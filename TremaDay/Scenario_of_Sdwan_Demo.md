sdwan_orchestrator_with_gobgp Demo in Trema Day
===========
gohanによるリソース管理に連動して、GoBGPのコンフィグ設定が自動的に行われます。

### ネットワーク構成図


	                                               < AS65000 >                 < AS65001 >                  < AS65001 >                  < 650002 >
	                   +————————+                  +--------+                  +---------+                  +---------+                  +--------+                  +-----+
	              .201 |        | .1          .101 |        | .1   e-BGP    .2 |         | .1   i-BGP    .2 |         | .1   e-BGP   .2  |        | .1           .2  |     |
	 +----------------+|Quagga-1| +--------------+ | SRX-1  | +--------------+ | GoBGP-1 | +--------------+ | GoBGP-3 | +--------------+ |Quagga-2|+----------------+| pc1 |
	  192.168.100.0/24 |        |  192.168.3.0/24  |        |  192.168.0.0/24  |         |   172.16.0.0/24  |         |  192.168.2.0/24  |        | 192.168.101.0/24 |     |
	                   +------—-+         +        +--------+                  +---------+                  +---------+                  +--------+                  +-----+
	                                      |                                                                   .2 +
	                                      |                                                                      |
	                                     Vrrp                                                                    |
	                             (VIP: 192.168.3.100)                                                            |
	                                      |                                                                      |
	                                      |         +--------+                  +---------+                      |
	                                      |    .102 |        | .1   e-BGP    .2 |         | .1      i-BGP        |
	                                      +-------+ | SRX-2  | +--------------+ | GoBGP-2 | +--------------------+
	                                                |        |  192.168.1.0/24  |         |      172.16.1.0/24
	                                                +--------+                  +---------+
	                                                < AS65000 >                 < AS65001 >


### gobgpdを起動します.

(1) コンフィグファイルを指定せずに、gobgpdを起動しておきます

	$ cd $GOPATH/bin
	$ sudo ./gobgpd
	{"level":"info","msg":"gobgpd started","time":"2016-06-11T08:33:45+09:00"}


### gobgp_workerを起動します.

(1) etcdを起動しておきます

	$ etcd
	2016-06-12 07:56:36.287792 I | etcdmain: etcd Version: 2.3.2
	2016-06-12 07:56:36.287880 I | etcdmain: Git SHA: ce63f10
	2016-06-12 07:56:36.287884 I | etcdmain: Go Version: go1.6.2
	2016-06-12 07:56:36.287888 I | etcdmain: Go OS/Arch: darwin/amd64
	2016-06-12 07:56:36.287893 I | etcdmain: setting maximum number of CPUs to 8, total number of available CPUs is 8
	2016-06-12 07:56:36.287900 W | etcdmain: no data-dir provided, using default data-dir ./default.etcd
	2016-06-12 07:56:36.288161 I | etcdmain: listening for peers on http://localhost:2380
	2016-06-12 07:56:36.288257 I | etcdmain: listening for peers on http://localhost:7001
	2016-06-12 07:56:36.288369 I | etcdmain: listening for client requests on http://localhost:2379
	2016-06-12 07:56:36.288463 I | etcdmain: listening for client requests on http://localhost:4001
	2016-06-12 07:56:36.288745 I | etcdserver: name = default
	2016-06-12 07:56:36.288754 I | etcdserver: data dir = default.etcd
	2016-06-12 07:56:36.288758 I | etcdserver: member dir = default.etcd/member
	2016-06-12 07:56:36.288761 I | etcdserver: heartbeat = 100ms
	2016-06-12 07:56:36.288764 I | etcdserver: election = 1000ms
	2016-06-12 07:56:36.288767 I | etcdserver: snapshot count = 10000
	2016-06-12 07:56:36.288778 I | etcdserver: advertise client URLs = http://localhost:2379,http://localhost:4001
	2016-06-12 07:56:36.288783 I | etcdserver: initial advertise peer URLs = http://localhost:2380,http://localhost:7001
	2016-06-12 07:56:36.288799 I | etcdserver: initial cluster = default=http://localhost:2380,default=http://localhost:7001
	2016-06-12 07:56:36.290813 I | etcdserver: starting member ce2a822cea30bfca in cluster 7e27652122e8b2ae
	2016-06-12 07:56:36.290869 I | raft: ce2a822cea30bfca became follower at term 0
	2016-06-12 07:56:36.290890 I | raft: newRaft ce2a822cea30bfca [peers: [], term: 0, commit: 0, applied: 0, lastindex: 0, lastterm: 0]
	2016-06-12 07:56:36.290894 I | raft: ce2a822cea30bfca became follower at term 1
	2016-06-12 07:56:36.291138 I | etcdserver: starting server... [version: 2.3.2, cluster version: to_be_decided]
	2016-06-12 07:56:36.291344 E | etcdserver: cannot monitor file descriptor usage (cannot get FDUsage on darwin)
	2016-06-12 07:56:36.291692 N | etcdserver: added local member ce2a822cea30bfca [http://localhost:2380 http://localhost:7001] to cluster 7e27652122e8b2ae
	2016-06-12 07:56:36.691477 I | raft: ce2a822cea30bfca is starting a new election at term 1
	2016-06-12 07:56:36.691604 I | raft: ce2a822cea30bfca became candidate at term 2
	2016-06-12 07:56:36.691618 I | raft: ce2a822cea30bfca received vote from ce2a822cea30bfca at term 2
	2016-06-12 07:56:36.691649 I | raft: ce2a822cea30bfca became leader at term 2
	2016-06-12 07:56:36.691664 I | raft: raft.node: ce2a822cea30bfca elected leader ce2a822cea30bfca at term 2
	2016-06-12 07:56:36.692042 I | etcdserver: setting up the initial cluster version to 2.3
	2016-06-12 07:56:36.693880 N | etcdserver: set the initial cluster version to 2.3
	2016-06-12 07:56:36.693992 I | etcdserver: published {Name:default ClientURLs:[http://localhost:2379 http://localhost:4001]} to cluster 7e27652122e8b2ae


(2) gobgp_config_workerを起動します

	$ cd $HOME/sdwan_orchestrator_with_gobgp/gobgp_worker
	$ python gobgp_config_worker.py


(3) さらに、gobgp_monitoring_worker.pyも起動します(事前に、GoBGPs変数に、host_name, mgmt_addrを適切に設定しておくこと)
	
	$ cd $HOME/sdwan_orchestrator_with_gobgp/gobgp_worker
	$ vi gobgp_monitoring_worker.py

	  1 import etcd
	  2 import json
	  3 import sys
	  4 import copy
	  5 import eventlet
	  6 from fabric.api import local, hide
	  7 
	  8 host = '127.0.0.1'
	  9 port = 4001
	 10 GoBGPs = {'GoBGP-1': '192.168.200.103', 'GoBGP-2': '192.168.200.104', 'GoBGP-3': '192.168.200.105'}
	 11 


	$ python gobgp_monitoring_worker.py



### gohanサーバを起動します.

(1) gohanサーバを起動します

	$ cd $HOME/sdwan_orchestrator_with_gobgp/gohan
	$ ./start_gohan.sh

	...(snip)
	08:46:25.170 gohan.server INFO  Keystone backend server configured
	08:46:25.326 gohan.server INFO  etcd servers: [http://127.0.0.1:2379]
	08:46:25.327 gohan.server INFO  Enabling CORS for *
	08:46:25.327 gohan.server WARNING  cors for * have security issue
	08:46:25.327 gohan.server INFO  Static file serving from /etc/gohan/
	08:46:25.341 gohan.server INFO  Gohan no jikan desuyo (It's time for dinner!) 
	08:46:25.341 gohan.server INFO  Starting Gohan Server...

	

### gohanクライアントからリソース情報を登録します.

(1) gohanクライアント動作環境を有効にします

	$ source keystonerc_admin 
	$ cd $HOME/sdwan_orchestrator_with_gobgp/gohan
	$ source gohan_cli.rc

(2) gohanクライアントからルータ情報を登録して、GoBGPdにGlobalConfigを設定します

	$ gohan client router create --host_name GoBGP-1 --router_id 10.0.1.1 --local_as 65001 --mgmt_addr 192.168.200.103
	+-----------+--------------------------------------+
	| PROPERTY  |                VALUE                 |
	+-----------+--------------------------------------+
	| host_name | GoBGP-1                              |
	| id        | 0483728d-546a-47d7-99ce-6734aa853c1e |
	| local_as  |                                65001 |
	| mgmt_addr | 192.168.200.103                      |
	| router_id | 10.0.1.1                             |
	| status    | PENDING_CREATE                       |
	+-----------+--------------------------------------+

	$ gohan client router create --host_name GoBGP-2 --router_id 10.0.1.2 --local_as 65001 --mgmt_addr 192.168.200.104
	$ gohan client router create --host_name GoBGP-3 --router_id 10.0.1.3 --local_as 65001 --mgmt_addr 192.168.200.105
	$ gohan client router list
	+-----------+--------------------------------------+----------+-----------------+-----------+--------+
	| HOST NAME |                  ID                  | LOCAL AS |    MGMT ADDR    | ROUTER ID | STATUS |
	+-----------+--------------------------------------+----------+-----------------+-----------+--------+
	| GoBGP-1   | 0483728d-546a-47d7-99ce-6734aa853c1e |    65001 | 192.168.200.103 | 10.0.1.1  | ACTIVE |
	| GoBGP-3   | 23071b3e-868d-4877-b671-0af34a2a835f |    65001 | 192.168.200.105 | 10.0.1.3  | ACTIVE |
	| GoBGP-2   | 6a67cb08-8cbb-4f80-ae55-73097f4c8a4a |    65001 | 192.168.200.104 | 10.0.1.2  | ACTIVE |
	+-----------+--------------------------------------+----------+-----------------+-----------+--------+


(3) gohanクライアントからBGP隣接情報を登録して、GoBGPdにneighborを設定します

	$ gohan client neighbor create --host_name GoBGP-1 --neighbor_addr 192.168.0.1 --peer_as 65000 --mgmt_addr 192.168.200.103
	+---------------+--------------------------------------+
	|   PROPERTY    |                VALUE                 |
	+---------------+--------------------------------------+
	| host_name     | GoBGP-1                              |
	| id            | bc402892-b43b-43b6-8975-9e6dfbace901 |
	| mgmt_addr     | 192.168.200.103                      |
	| neighbor_addr | 192.168.0.1                          |
	| peer_as       |                                65000 |
	| status        | PENDING_CREATE                       |
	+---------------+--------------------------------------+

	$ gohan client neighbor create --host_name GoBGP-1 --neighbor_addr 172.16.0.2 --peer_as 65001 --mgmt_addr 192.168.200.103
	$ gohan client neighbor create --host_name GoBGP-2 --neighbor_addr 192.168.1.1 --peer_as 65000 --mgmt_addr 192.168.200.104
	$ gohan client neighbor create --host_name GoBGP-2 --neighbor_addr 172.16.1.2 --peer_as 65001 --mgmt_addr 192.168.200.104
	$ gohan client neighbor create --host_name GoBGP-3 --neighbor_addr 172.16.0.1 --peer_as 65001 --mgmt_addr 192.168.200.105
	$ gohan client neighbor create --host_name GoBGP-3 --neighbor_addr 172.16.1.1 --peer_as 65001 --mgmt_addr 192.168.200.105
	$ gohan client neighbor create --host_name GoBGP-3 --neighbor_addr 192.168.2.2 --peer_as 65002 --mgmt_addr 192.168.200.105

	$ gohan client neighbor list
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| HOST NAME |                  ID                  |    MGMT ADDR    | NEIGHBOR ADDR | PEER AS | STATUS |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| GoBGP-2   | 91f8e478-d3cc-459c-adf4-3f6cc4f2ba03 | 192.168.200.104 | 192.168.1.1   |   65000 | UP     |
	| GoBGP-2   | 97432008-6e58-416a-a976-d79aacc66849 | 192.168.200.104 | 172.16.1.2    |   65001 | UP     |
	| GoBGP-1   | bc402892-b43b-43b6-8975-9e6dfbace901 | 192.168.200.103 | 192.168.0.1   |   65000 | UP     |
	| GoBGP-1   | c99176e8-2676-4781-9782-15d5b22aba02 | 192.168.200.103 | 172.16.0.2    |   65001 | UP     |
	| GoBGP-3   | e101709a-2934-4c95-8b3a-dcafc00ebb60 | 192.168.200.105 | 192.168.2.2   |   65002 | UP     |
	| GoBGP-3   | f253a80d-d644-4f56-8b87-f7409d44f92e | 192.168.200.105 | 172.16.1.1    |   65001 | UP     |
	| GoBGP-3   | f43abcc7-b593-44d2-a673-6b1208d977ad | 192.168.200.105 | 172.16.0.1    |   65001 | UP     |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+

	GoBGPd側でBGP Peer開設できると、"STATUS: UP"となります



(4) GoBGP-3側でのCLIにて、BGPテーブルを確認しておきます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attr
	*>  0.0.0.0/0           192.168.0.1          65000                00:00:43   [{Origin: i} {LocalPref: 100}]
	*   0.0.0.0/0           192.168.1.1          65000                00:00:43   [{Origin: i} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:00:21   [{Origin: i} {Med: 0}]

    このままでは、0.0.0.0/24の経路に対するnext-hopへの到達性が無いため、BGPで学習した経路がルーティングテーブルに注入されません
    そこで、next-hopへの到達性を可能とするpolicyを設定します


(5) gohanクライアントからポリシー情報を登録して、GoBGPdにPolicyを設定します

	$ gohan client policyinfo create --host_name GoBGP-1 --mgmt_addr 192.168.200.103 --policy_name policy1 --statement_name statement1 --statement_action "next-hop self" --route_disposition accept --apply_direction export --apply_neighbor 172.16.0.2 --exist New
	+-------------------+--------------------------------------+
	|     PROPERTY      |                VALUE                 |
	+-------------------+--------------------------------------+
	| apply_direction   | export                               |
	| apply_neighbor    | 172.16.0.2                           |
	| exist             | New                                  |
	| host_name         | GoBGP-1                              |
	| id                | 7759ddb4-340e-41b7-94ac-6f3c64cee6ae |
	| mgmt_addr         | 192.168.200.103                      |
	| policy_name       | policy1                              |
	| route_disposition | accept                               |
	| statement_action  | next-hop self                        |
	| statement_name    | statement1                           |
	| status            | PENDING_CREATE                       |
	+-------------------+--------------------------------------+

	$ gohan client policyinfo create --host_name GoBGP-2 --mgmt_addr 192.168.200.104 --policy_name policy1 --statement_name statement1 --statement_action "next-hop self" --route_disposition accept --apply_direction export --apply_neighbor 172.16.1.2 --exist New
	$ gohan client policyinfo create --host_name GoBGP-3 --mgmt_addr 192.168.200.105 --policy_name policy1 --statement_name statement1 --statement_action "next-hop self" --route_disposition accept --apply_direction export --apply_neighbor 172.16.0.1 --exist New
	$ gohan client policyinfo create --host_name GoBGP-3 --mgmt_addr 192.168.200.105 --policy_name policy1 --statement_name statement1 --statement_action "next-hop self" --route_disposition accept --apply_direction export --apply_neighbor 172.16.1.1 --exist Existing

	$ gohan client policyinfo list
	+-----------------+----------------+----------+-----------+--------------------------------------+-----------------+-------------+-------------------+------------------+----------------+--------+
	| APPLY DIRECTION | APPLY NEIGHBOR |  EXIST   | HOST NAME |                  ID                  |    MGMT ADDR    | POLICY NAME | ROUTE DISPOSITION | STATEMENT ACTION | STATEMENT NAME | STATUS |
	+-----------------+----------------+----------+-----------+--------------------------------------+-----------------+-------------+-------------------+------------------+----------------+--------+
	| export          | 172.16.0.2     | New      | GoBGP-1   | 08485d14-84d7-4c63-b3ce-75755219b411 | 192.168.200.103 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.1.1     | Existing | GoBGP-3   | 38676bc8-8386-4a7e-b116-56b83c110f18 | 192.168.200.105 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.0.1     | New      | GoBGP-3   | 7e488b4d-d5f2-4570-83d7-e7023b0dd417 | 192.168.200.105 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.1.2     | New      | GoBGP-2   | c751303d-c2c4-4a63-be24-814c6bd728c9 | 192.168.200.104 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	+-----------------+----------------+----------+-----------+--------------------------------------+-----------------+-------------+-------------------+------------------+----------------+--------+


(6) 再度、GoBGP-3側でのCLIにて、BGPテーブルを確認してみます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  0.0.0.0/0           172.16.0.1           65000                00:01:46   [{Origin: i} {LocalPref: 100}]
	*   0.0.0.0/0           172.16.1.1           65000                00:00:30   [{Origin: i} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:01:24   [{Origin: i} {Med: 0}]

	期待通りに、next-hopが変更できました!!


(7) Quagga-2側でのBGPテーブルを確認してみます

	Quagga-2# show ip bgp
	BGP table version is 0, local router ID is 10.0.0.4
	Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
	              r RIB-failure, S Stale, R Removed
	Origin codes: i - IGP, e - EGP, ? - incomplete

	   Network          Next Hop            Metric LocPrf Weight Path
	*> 0.0.0.0          192.168.2.1                            0 65001 65000 i
	*> 192.168.101.0    0.0.0.0                  0         32768 i


	期待通りに、192.168.100.0/24をBGPテーブルで保持できました!!


(8) エンドエンドでping通信確認してみます

	$ ping 192.168.100.1
	PING 192.168.100.1 (192.168.100.1): 56 data bytes
	64 bytes from 192.168.100.1: icmp_seq=0 ttl=250 time=1.572 ms
	64 bytes from 192.168.100.1: icmp_seq=1 ttl=250 time=1.598 ms
	64 bytes from 192.168.100.1: icmp_seq=2 ttl=250 time=1.566 ms
	64 bytes from 192.168.100.1: icmp_seq=3 ttl=250 time=1.602 ms
	64 bytes from 192.168.100.1: icmp_seq=4 ttl=250 time=1.639 ms
	^C
	--- 192.168.100.1 ping statistics ---
	5 packets transmitted, 5 packets received, 0.0% packet loss
	round-trip min/avg/max/stddev = 1.566/1.595/1.639/0.026 ms

	期待通りに、ping通信できました!!


### GoBGPでの経路迂回を試してみます

(1) まず、GoBGP-3側でのCLIにて、BGPテーブルを確認しておきます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  0.0.0.0/0           172.16.0.1           65000                00:01:46   [{Origin: i} {LocalPref: 100}]
	*   0.0.0.0/0           172.16.1.1           65000                00:00:30   [{Origin: i} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:01:24   [{Origin: i} {Med: 0}]


(2) Gohanクライアントより、neighborリソースのSTATUSを確認しておきます

	$ gohan client neighbor list
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| HOST NAME |                  ID                  |    MGMT ADDR    | NEIGHBOR ADDR | PEER AS | STATUS |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| GoBGP-2   | 91f8e478-d3cc-459c-adf4-3f6cc4f2ba03 | 192.168.200.104 | 192.168.1.1   |   65000 | UP     |
	| GoBGP-2   | 97432008-6e58-416a-a976-d79aacc66849 | 192.168.200.104 | 172.16.1.2    |   65001 | UP     |
	| GoBGP-1   | bc402892-b43b-43b6-8975-9e6dfbace901 | 192.168.200.103 | 192.168.0.1   |   65000 | UP     |
	| GoBGP-1   | c99176e8-2676-4781-9782-15d5b22aba02 | 192.168.200.103 | 172.16.0.2    |   65001 | UP     |
	| GoBGP-3   | e101709a-2934-4c95-8b3a-dcafc00ebb60 | 192.168.200.105 | 192.168.2.2   |   65002 | UP     |
	| GoBGP-3   | f253a80d-d644-4f56-8b87-f7409d44f92e | 192.168.200.105 | 172.16.1.1    |   65001 | UP     |
	| GoBGP-3   | f43abcc7-b593-44d2-a673-6b1208d977ad | 192.168.200.105 | 172.16.0.1    |   65001 | UP     |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+


(3) SRX-1を停止してみます

	root@SRX-1> request system halt 
	Halt the system ? [yes,no] (no) yes 

	Shutdown NOW!
	[pid 1542]



(4) 再度、GoBGP-3側でのCLIにて、BGPテーブルを確認してみます

        $ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  0.0.0.0/0           172.16.1.1           65000                00:02:12   [{Origin: i} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:03:06   [{Origin: i} {Med: 0}]

	期待通りに、next-hopが変更されました!!


(5) 再度、Gohanクライアントより、neighborリソースのSTATUSを確認してみます

	$ gohan client neighbor list
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| HOST NAME |                  ID                  |    MGMT ADDR    | NEIGHBOR ADDR | PEER AS | STATUS |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+
	| GoBGP-2   | 91f8e478-d3cc-459c-adf4-3f6cc4f2ba03 | 192.168.200.104 | 192.168.1.1   |   65000 | UP     |
	| GoBGP-2   | 97432008-6e58-416a-a976-d79aacc66849 | 192.168.200.104 | 172.16.1.2    |   65001 | UP     |
	| GoBGP-1   | bc402892-b43b-43b6-8975-9e6dfbace901 | 192.168.200.103 | 192.168.0.1   |   65000 | DOWN   |
	| GoBGP-1   | c99176e8-2676-4781-9782-15d5b22aba02 | 192.168.200.103 | 172.16.0.2    |   65001 | UP     |
	| GoBGP-3   | e101709a-2934-4c95-8b3a-dcafc00ebb60 | 192.168.200.105 | 192.168.2.2   |   65002 | UP     |
	| GoBGP-3   | f253a80d-d644-4f56-8b87-f7409d44f92e | 192.168.200.105 | 172.16.1.1    |   65001 | UP     |
	| GoBGP-3   | f43abcc7-b593-44d2-a673-6b1208d977ad | 192.168.200.105 | 172.16.0.1    |   65001 | UP     |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+

	期待通りに、GoBGP1 <-> SRX-1間のBGP Peerダウンを検出することができました!!


(6) 再度、エンドエンドでping通信確認してみます

	$ ping 192.168.100.1
	PING 192.168.100.1 (192.168.100.1): 56 data bytes
	64 bytes from 192.168.100.1: icmp_seq=0 ttl=250 time=1.755 ms
	64 bytes from 192.168.100.1: icmp_seq=1 ttl=250 time=1.696 ms
	64 bytes from 192.168.100.1: icmp_seq=2 ttl=250 time=1.697 ms
	64 bytes from 192.168.100.1: icmp_seq=3 ttl=250 time=1.781 ms
	64 bytes from 192.168.100.1: icmp_seq=4 ttl=250 time=1.701 ms
	^C
	--- 192.168.100.1 ping statistics ---
	5 packets transmitted, 5 packets received, 0.0% packet loss
	round-trip min/avg/max/stddev = 1.696/1.726/1.781/0.035 ms


	期待通りに、ping通信できました!!

