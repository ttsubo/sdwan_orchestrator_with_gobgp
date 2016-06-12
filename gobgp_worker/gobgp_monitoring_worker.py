import etcd
import json
import sys
import copy
import eventlet
from fabric.api import local, hide

host = '127.0.0.1'
port = 4001
GoBGPs = {'GoBGP-1': '192.168.200.103', 'GoBGP-2': '192.168.200.104', 'GoBGP-3': '192.168.200.105'}

result_queue = eventlet.queue.Queue()
neighbors = []

class NeighborTable(object):
    def __init__(self, host_name, neighbor_addr, uuid):
        self.host_name = host_name
        self.neighbor_addr = neighbor_addr
        self.uuid = uuid

    def get_all(self):
        return self.host_name, self.neighbor_addr, self.uuid


class Monitor(object):
    def __init__(self, host_name, mgmt_addr):
        self.host_name = host_name
        self.mgmt_addr = mgmt_addr
        self.old_results = {}

    def start(self):
        self._thread = eventlet.spawn(self._monitor_neighbor)

    def wait(self):
        self._thread.wait()

    def _monitor_neighbor(self):
        with hide('running', 'stdout'):
            while True:
                eventlet.sleep(1)
                try:
                    results = {}
                    cmd = 'gobgp -j neighbor -u {0}'.format(self.mgmt_addr)
                    output = local(cmd, capture=True)
                    ret = json.loads(output)
                    for i in range(len(ret)):
                        addr = ret[i]['conf']['remote_ip']
                        state = ret[i]['info']['bgp_state']
                        results[addr] = state
                    change_result_list = self._extract_change_state(results)
                    if change_result_list != []:
                        result_queue.put(change_result_list)
                except:
                    continue


    def _extract_change_state(self, new_results):
        change_result = {}
        change_result_list = []
        buf = {}
        # new neighbor
        for target_addr in set(new_results) - set(self.old_results):
            new_state = new_results[target_addr]
            change_result['host_name'] = self.host_name
            change_result['neighbor_addr'] = target_addr
            change_result['state'] = new_state
            buf = copy.deepcopy(change_result)
            change_result_list.append(buf)
        # exiting neighbor
        for target_addr in set(new_results) & set(self.old_results):
            new_state = new_results[target_addr]
            old_state = self.old_results[target_addr]
            if new_state != old_state:
                change_result['host_name'] = self.host_name
                change_result['neighbor_addr'] = target_addr
                change_result['state'] = new_state
                buf = copy.deepcopy(change_result)
                change_result_list.append(buf)
        self.old_results = copy.deepcopy(new_results)
        return change_result_list


class EtcdConsumer(Monitor):
    def __init__(self, host, port, resource):
        self.host = host
        self.port = port
        self.resource = resource
        self.uuids = {}
        self.url = "/config/v2.0/" + resource + "s/"
        self.old_configs = {}

    def start(self):
        self._thread = eventlet.spawn(self._monitoring_loop)
        self._thread = eventlet.spawn(self._consume_loop)

    def wait(self):
        self._thread.wait()

    def _monitoring_loop(self):
        while True:
            eventlet.sleep(1)
            if not result_queue.empty():
                change_result_list = result_queue.get()
                for change_result in change_result_list:
                    host_name = change_result['host_name']
                    neighbor_addr = change_result['neighbor_addr']
                    state = change_result['state']
                    if state == "BGP_FSM_ESTABLISHED":
                        status = 'UP'
                    elif state == "BGP_FSM_IDLE" or state == "BGP_FSM_ACTIVE":
                        status = 'DOWN'
                    while True:
                        eventlet.sleep(1)
                        uuid = self._search_uuid(host_name, neighbor_addr)
                        if uuid:
                            print "### Detect: ", host_name, neighbor_addr, uuid, status
                            self._writeState(uuid, self.resource, status)
                            break
                        else:
                            print ("### retry search uuid")

    def _writeState(self, uuid, resource, status):
        res = {}
        res['version'] = self.uuids[uuid]
        res[resource] = status

        client = etcd.Client(self.host, self.port)
        url_monitoring = "/monitoring/v2.0/" + resource + "s/"

        client.write(url_monitoring + uuid, json.dumps(res))
        print ("### writeState: resource:[%s], id:[%s], value:[%s]"% (resource, uuid, res))

    def _search_uuid(self, host_name, neighbor_addr):
        for neighbor in neighbors:
            host, addr, uuid = neighbor.get_all()
            if host_name == host and neighbor_addr == addr:
                return uuid

    def _consume_loop(self):
        new_configs = {}
        while True:
            eventlet.sleep(5)
            client = etcd.Client(self.host, self.port)
            try:
                new_configs = self._readConfig(client)
                target_configs_list = self._detect_target_configs(new_configs)
                for target_config in target_configs_list:
                    uuid = target_config['id']
                    body = target_config['body']
                    version = body['version']
                    self._regist_neighbor(uuid, body)
                    self.uuids[uuid] = version
            except etcd.EtcdKeyNotFound:
                continue

    def _regist_neighbor(self, uuid, body):
        host_name = body['host_name']
        neighbor_addr = body['neighbor_addr']
        new_neighbor = NeighborTable(host_name, neighbor_addr, uuid)
        neighbors.append(new_neighbor)

    def _readConfig(self, client):
        read_configs = {}
        id = ""
        reqs = client.get(self.url)
        for req in reqs.children:
            if req.value:
                buf = json.loads(req.value)
                body = json.loads(buf['body'])
                id = body['id']
                body['version'] = buf['version']
                read_configs[id] = body
        return read_configs

    def _detect_target_configs(self, new_configs):
        target_configs = {}
        target_configs_list = []
        buf = {}

        # new config
        for target_id in set(new_configs) - set(self.old_configs):
            new_config_body = new_configs[target_id]
            target_configs['id'] = target_id
            target_configs['body'] = new_config_body
            buf = copy.deepcopy(target_configs)
            target_configs_list.append(buf)
        # update config
        for target_id in set(new_configs) & set(self.old_configs):
            new_config_body = new_configs[target_id]
            old_config_body = self.old_configs[target_id]
            if new_config_body['version'] != old_config_body['version']:
                target_configs['id'] = target_id
                target_configs['body'] = new_config_body
                buf = copy.deepcopy(target_configs)
                target_configs_list.append(buf)
        self.old_configs = copy.deepcopy(new_configs)
        return target_configs_list


if __name__ == '__main__':
    workers = []

    etcd_worker = EtcdConsumer(host, port, 'neighbor')
    workers.append(etcd_worker)

    for host_name, mgmt_addr in GoBGPs.items():
        monitor_worker = Monitor(host_name, mgmt_addr)
        workers.append(monitor_worker)

    [worker.start() for worker in workers]
    [worker.wait() for worker in workers]

