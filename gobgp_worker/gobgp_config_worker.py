import etcd
import json
import sys
import copy
import eventlet
from fabric.api import local

host = '127.0.0.1'
port = 4001


class EtcdConsumer(object):
    def __init__(self, host, port, resource, func):
        self.host = host
        self.port = port
        self.resource = resource
        self.url = "/config/v2.0/" + resource + "s/"
        self.func = func
        self.old_configs = {}

    def start(self):
        self._thread = eventlet.spawn(self._consume_loop)

    def wait(self):
        self._thread.wait()

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
                    result = self.func(body)
                    if result == True:
                        self._writeState(client, uuid, version, self.resource, "ACTIVE")
                    elif result == False:
                        self._writeState(client, uuid, version, self.resource, "FAILED")
            except etcd.EtcdKeyNotFound:
                continue

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

    def _writeState(self, client, uuid, version, resource, result):
        res = {}
        state_mon = {}
        state = {}
        res['version'] = version
        res['error'] = ""
        url_state = "/state/v2.0/" + resource + "s/"

        state[resource] = result
        state_mon['state_monitoring'] = state
        res['state'] = state_mon
        client.write(url_state + uuid, json.dumps(res))
        print ("### writeState: resource:[%s], id:[%s], value:[%s]"% (resource, uuid, res))




def activateGlobalConfig(body):
    host_name = body['host_name']
    mgmt_addr = body['mgmt_addr']
    router_id = body['router_id']
    local_as = body['local_as']
    status = body['status']
    try:
        ret = gobgpCli_for_globalConfig(local_as, router_id, mgmt_addr, status)
        result = True if ret == "" else False
    except:
        result = False
    return result

def activateBgpNeighbor(body):
    host_name = body['host_name']
    mgmt_addr = body['mgmt_addr']
    neighbor_addr = body['neighbor_addr']
    peer_as = body['peer_as']
    status = body['status']
    try:
        ret = gobgpCli_for_addNeighbor(neighbor_addr, peer_as, mgmt_addr, status)
        result = True if ret == "" else False
    except:
        result = False
    return result

def activateBgpPolicy(body):
    host_name = body['host_name']
    mgmt_addr = body['mgmt_addr']
    policy_name = body['policy_name']
    statement_name = body['statement_name']
    statement_action = body['statement_action']
    route_disposition = body['route_disposition']
    apply_direction = body['apply_direction']
    apply_neighbor = body['apply_neighbor']
    exist = body['exist']
    status = body['status']
    try:
        ret = gobgpCli_for_addPolicy(policy_name, statement_name, statement_action, route_disposition, apply_direction, apply_neighbor, mgmt_addr, exist, status)
        result = True if ret == "" else False
    except:
        result = False
    return result

def gobgpCli_for_globalConfig(local_as, router_id, mgmt_addr, status):
    if status == "PENDING_CREATE":
        cmd = 'gobgp -j global as {0} router-id {1} -u {2}'.format(local_as, router_id, mgmt_addr)
    elif status == "PENDING_DELETE":
        cmd = 'gobgp -j global del all -u {0}'.format(mgmt_addr)
    ret = local(cmd, capture=True)
    return ret

def gobgpCli_for_addNeighbor(neighbor_addr, peer_as, mgmt_addr, status):
    if status == "PENDING_CREATE":
        cmd = 'gobgp -j neighbor add {0} as {1} -u {2}'.format(neighbor_addr, peer_as, mgmt_addr)
    elif status == "PENDING_DELETE":
        cmd = 'gobgp -j neighbor del {0} as {1} -u {2}'.format(neighbor_addr, peer_as, mgmt_addr)
    ret = local(cmd, capture=True)
    return ret

def gobgpCli_for_addPolicy(policy_name, statement_name, statement_action, route_disposition, apply_direction, apply_neighbor, mgmt_addr, exist, status):
    if status == "PENDING_CREATE":
        if exist == "New":
            cmd1 = 'gobgp -j policy statement add {0} -u {1}'.format(statement_name, mgmt_addr)
            cmd2 = 'gobgp -j policy statement {0} add action {1} -u {2}'.format(statement_name, statement_action, mgmt_addr)
            cmd3 = 'gobgp -j policy statement {0} add action {1} -u {2}'.format(statement_name, route_disposition, mgmt_addr)
            cmd4 = 'gobgp -j policy add {0} {1} -u {2}'.format(policy_name, statement_name, mgmt_addr)
            cmd5 = 'gobgp -j global policy {0} add {1} -u {2}'.format(apply_direction, policy_name, mgmt_addr)
            cmd6 = 'gobgp -j neighbor {0} softresetout -u {1}'.format(apply_neighbor, mgmt_addr)
        elif exist == "Existing":
            cmd7 = 'gobgp -j neighbor {0} softresetout -u {1}'.format(apply_neighbor, mgmt_addr)
    elif status == "PENDING_DELETE":
        if exist == "New":
            cmd1 = 'gobgp -j global policy {0} del {1} -u {2}'.format(apply_direction, policy_name, mgmt_addr)
            cmd2 = 'gobgp -j neighbor {0} softresetout -u {1}'.format(apply_neighbor, mgmt_addr)
            cmd3 = 'gobgp -j policy del {0} {1} -u {2}'.format(policy_name, statement_name, mgmt_addr)
            cmd4 = 'gobgp -j policy statement {0} del action {1} -u {2}'.format(statement_name, route_disposition, mgmt_addr)
            cmd5 = 'gobgp -j policy statement {0} del action {1} -u {2}'.format(statement_name, statement_action, mgmt_addr)
            cmd6 = 'gobgp -j policy statement del {0} -u {1}'.format(statement_name, mgmt_addr)
        elif exist == "Existing":
            cmd7 = 'gobgp -j neighbor {0} softresetout -u {1}'.format(apply_neighbor, mgmt_addr)

    if exist == "New":
        ret1 = local(cmd1, capture=True)
        ret2 = local(cmd2, capture=True)
        ret3 = local(cmd3, capture=True)
        ret4 = local(cmd4, capture=True)
        ret5 = local(cmd5, capture=True)
        ret6 = local(cmd6, capture=True)
        if (ret1 == "") and (ret2 =="") and (ret3 == "") and (ret4 == "") and (ret5 == "") and (ret6 == ""):
            ret = ""
        else:
            ret = "failed"
    elif exist == "Existing":
        ret7 = local(cmd7, capture=True)
        if (ret7 == ""):
            ret = ""
    return ret


if __name__ == '__main__':
    resources = {}
    workers = []
    resources['router'] = activateGlobalConfig
    resources['neighbor'] = activateBgpNeighbor
    resources['policyinfo'] = activateBgpPolicy

    for resource, func in resources.items():
        worker = EtcdConsumer(host, port, resource, func)
        workers.append(worker)

    [worker.start() for worker in workers]
    [worker.wait() for worker in workers]
