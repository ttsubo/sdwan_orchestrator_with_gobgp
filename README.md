What's sdwan_orchestrator_with_gobgp
==========
gobgpリソース管理用gohanツール一式です.

動作環境
==========
### gohan環境
Ubuntu Server版を推奨とします.

	$ cat /etc/lsb-release
	DISTRIB_ID=Ubuntu
	DISTRIB_RELEASE=14.04
	DISTRIB_CODENAME=trusty
	DISTRIB_DESCRIPTION="Ubuntu 14.04.4 LTS"

### keystone環境
keystone動作環境を準備します.
なお、keystone環境をセットアップするにあたっての環境パラメータは、以下を前提とし
ます.

	OS_TENANT_NAME=admin
	OS_AUTH_URL=http://192.168.195.156:5000/v2.0
	OS_USERNAME=admin
	OS_PASSWORD=secrete

インストール
==========
### keystoneクライアント環境を整備します.

(1) python-keystoneclientをインストールします

	$ sudo pip install python-keystoneclient

(2) keystoneクライアントを有効にします

	$ vi keystonerc_admin
	unset OS_SERVICE_TOKEN
	export OS_AUTH_URL=http://192.168.195.156:5000/v2.0
	export OS_USERNAME=admin
	export OS_PASSWORD=secrete
	export OS_TENANT_NAME=admin
	export OS_REGION_NAME=RegionOne

	$ source keystonerc_admin

(3) gohan用keystoneセットアップを行います

"admin"テナントのuuidを確認しておく

	$ keystone tenant-list
	+----------------------------------+----------+---------+
	|                id                |   name   | enabled |
	+----------------------------------+----------+---------+
	| 342863e5919743709dbfa58c83db9f46 |  admin   |   True  |
	| 4c2e62b829db4cdc914f6fd8feb3a046 |   demo   |   True  |
	| ef4c706ce7a849c1849f5fa4b9d849a4 | services |   True  |
	+----------------------------------+----------+---------+

"gohan"サービスを作成する

	$ keystone service-create --type gohan --name gohan --description Gohan
	+-------------+----------------------------------+
	|   Property  |              Value               |
	+-------------+----------------------------------+
	| description |              Gohan               |
	|   enabled   |               True               |
	|      id     | 3d99818e11bd4b12b43e20ea4f4c8432 |
	|     name    |              gohan               |
	|     type    |              gohan               |
	+-------------+----------------------------------+

"gohan"エンドポイントを作成する

	$ keystone endpoint-create --region RegionOne --service gohan --publicurl http://127.0.0.1:9998 --adminurl http://127.0.0.1:9998 --internalurl http://127.0.0.1:9998
	+-------------+----------------------------------+
	|   Property  |              Value               |
	+-------------+----------------------------------+
	|   adminurl  |      http://127.0.0.1:9998       |
	|      id     | 0085120a6c2147dc838c28a1e789d264 |
	| internalurl |      http://127.0.0.1:9998       |
	|  publicurl  |      http://127.0.0.1:9998       |
	|    region   |            RegionOne             |
	|  service_id | 3d99818e11bd4b12b43e20ea4f4c8432 |
	+-------------+----------------------------------+

"gohan"エンドポイントを確認しておく

	$ keystone endpoint-get --service gohan
	+-----------------+-----------------------+
	|     Property    |         Value         |
	+-----------------+-----------------------+
	| gohan.publicURL | http://127.0.0.1:9998 |
	+-----------------+-----------------------+


### gohan環境を整備します.

(1) golang環境を作成します
https://golang.org/doc/install を参考に、golang環境を構築します.

	$ cd $HOME
	$ wget --no-check-certificate https://storage.googleapis.com/golang/go1.5.3.linux-amd64.tar.gz
	$ sudo tar -C /usr/local -xzf go1.5.3.linux-amd64.tar.gz
	$ mkdir $HOME/golang
	$ vi .profile

	...(snip)
	export GOPATH=$HOME/golang
	export PATH=$GOPATH/bin:/usr/local/go/bin:$PATH

	$ source .profile
	$ go version
	go version go1.5.3 linux/amd64


(2) etcd環境を作成します
https://github.com/coreos/etcd/releases を参考に、etcd環境を構築します.

	$ cd $HOME
	$ wget --no-check-certificate https://github.com/coreos/etcd/releases/download/v2.3.2/etcd-v2.3.2-linux-amd64.tar.gz
	$ sudo tar -C /usr/local -xzf etcd-v2.3.2-linux-amd64.tar.gz

	$ vi .profile
	...(snip)
	export PATH=$GOPATH/bin:/usr/local/go/bin:/usr/local/etcd-v2.3.2-linux-amd64:$PATH

	$ source .profile

(3) その他オープンソースをインストールします

	$ sudo apt-get update
	$ sudo apt-get install git
	$ sudo apt-get install gcc
	$ sudo apt-get install make
	$ sudo apt-get install python-pip
	$ sudo apt-get install python-dev

(4) "sdwan_orchestrator_with_gobgp"リポジトリをダウンロードします

	$ git clone git@bitbucket.org:ttsubo/sdwan_orchestrator_with_gobgp.git
	$ cd sdwan_orchestrator_with_gobgp
	$ sudo pip install -r pip-requires.txt

(5) 必要に応じて、"gohan.yaml"ファイルを編集します

	$ cd $HOME/sdwan_orchestrator_with_gobgp/gohan
	$ vi gohan.yaml

	database:
	    type: "sqlite3"
	    connection: "./gobgp.db"
	schemas:
	    - "./etc/gohan.json"
	    - "./etc/gohan_extension.yaml"
	    - "./gobgp_schema.yaml"
	    - "./gobgp_extensions.yaml"
	address: ":9998"
	tls:
	    enabled: false
	document_root: "/etc/gohan/"
	etcd:
	    - "http://127.0.0.1:2379"
	keystone:
	    use_keystone: true
	    fake: false
	    auth_url: "http://192.168.195.156:5000/v2.0"
	    user_name: "admin"
	    tenant_name: "admin"
	    password: "secrete"
	cors: "*"
	logging:
	    stderr:
	        enabled: true
	        level: INFO
	    file:
	        enabled: true
	        level: INFO
	        filename: ./gohan.log

(6) gohan環境用の検索パスを追加しておきます

	$ vi .profile
	...(snip)
	export PATH=$HOME/sdwan_orchestrator_with_gobgp/gohan/bin:$GOPATH/bin:/usr/local/go/bin:/usr/local/etcd-v2.3.2-linux-amd64:$PATH 

	$ source .profile


(7) gobgp_workerからgobgpコマンドが起動できるようにgobgp環境を作成します

	$ go get github.com/osrg/gobgp/gobgp


### GoBGP環境を整備します.

(1) gobgpdを動作させたいLinux環境に、gobgpをインストールします

	$ go get github.com/osrg/gobgp/gobgpd
	$ go get github.com/osrg/gobgp/gobgp

(2) gobgpdを起動する際に、常に、"FIB manipulation"を有効にさせる必要があるので、つぎの個別patchファイルを作成して、パッチ適用します(コピー＆ペーストする際には、タブ文字が欠損しないよう注意が必要)

	$ vi sdwan_orchestrator_with_gobgp.patch

	---------------------------------------------------------
	diff --git a/gobgpd/main.go b/gobgpd/main.go
	index 8dddfa5..df1334a 100644
	--- a/gobgpd/main.go
	+++ b/gobgpd/main.go
	@@ -191,6 +191,14 @@ func main() {
 		m.Serve()
 	} else if opts.ConfigFile != "" {
 		go config.ReadConfigfileServe(opts.ConfigFile, opts.ConfigType, configCh)
	+	} else if opts.ConfigFile == "" {
	+		newConfig := config.BgpConfigSet{}
	+		newConfig.Zebra.Config.Enabled = true
	+		newConfig.Zebra.Config.Url = "unix:/var/run/quagga/zserv.api"
	+		log.Info("### Zebra.Config: ", newConfig.Zebra.Config)
	+		if err := bgpServer.SetZebraConfig(newConfig.Zebra); err != nil {
	+			log.Fatalf("failed to set zebra config: %s", err)
	+		}
	 	}
 
	 	var c *config.BgpConfigSet = nil
	diff --git a/server/server.go b/server/server.go
	index 539c408..4d3a281 100644
	--- a/server/server.go
	+++ b/server/server.go
	@@ -1576,13 +1576,13 @@ func (server *BgpServer) handleGrpc(grpcReq *GrpcRequest) []*SenderMsg {
	 		return []*Peer{peer}, err
	 	}
 
	-	if server.bgpConfig.Global.Config.As == 0 && grpcReq.RequestType != REQ_START_SERVER {
	-		grpcReq.ResponseCh <- &GrpcResponse{
	-			ResponseErr: fmt.Errorf("bgpd main loop is not started yet"),
	-		}
	-		close(grpcReq.ResponseCh)
	-		return nil
	-	}
	+//	if server.bgpConfig.Global.Config.As == 0 && grpcReq.RequestType != REQ_START_SERVER {
	+//		grpcReq.ResponseCh <- &GrpcResponse{
	+//			ResponseErr: fmt.Errorf("bgpd main loop is not started yet"),
	+//		}
	+//		close(grpcReq.ResponseCh)
	+//		return nil
	+//	}
 
 		var err error
	---------------------------------------------------------


	$ cp sdwan_orchestrator_with_gobgp.patch $GOPATH/src/github.com/osrg/gobgp/
	$ cd $GOPATH/src/github.com/osrg/gobgp
	$ git apply sdwan_orchestrator_with_gobgp.patch
	$ cd $GOPATH/src/github.com/osrg/gobgp/gobgpd
	$ go install


Quick Start
===========
gohanによるリソース管理に連動して、GoBGPのコンフィグ設定が自動的に行われます。

### ネットワーク構成図


	                                               < AS65000 >                 < AS65001 >                  < AS65001 >                  < 650002 >
	                   +————————+                  +--------+                  +---------+                  +---------+                  +--------+                  +-----+
	              .201 |        | .1          .101 |        | .1   e-BGP    .2 |         | .1   i-BGP    .2 |         | .1   e-BGP   .2  |        | .1           .2  |     |
	 +----------------+| VyOS-3 | +--------------+ | VyOS-1 | +--------------+ | GoBGP-1 | +--------------+ | GoBGP-3 | +--------------+ | VyOS-4 |+----------------+| pc1 |
	  192.168.100.0/24 |        |  192.168.3.0/24  |        |  192.168.0.0/24  |         |   172.16.0.0/24  |         |  192.168.2.0/24  |        | 192.168.101.0/24 |     |
	                   +------—-+         +        +--------+                  +---------+                  +---------+                  +--------+                  +-----+
	                                      |                                                                   .2 +
	                                      |                                                                      |
	                                     Vrrp                                                                    |
	                             (VIP: 192.168.3.100)                                                            |
	                                      |                                                                      |
	                                      |         +--------+                  +---------+                      |
	                                      |    .102 |        | .1   e-BGP    .2 |         | .1      i-BGP        |
	                                      +-------+ | VyOS-2 | +--------------+ | GoBGP-2 | +--------------------+
	                                                |        |  192.168.1.0/24  |         |      172.16.1.0/24
	                                                +--------+                  +---------+
	                                                < AS65000 >                 < AS65001 >


### gobgpdを起動します.

(1) コンフィグファイルを指定せずに、gobgpdを起動しておきます

	$ cd $GOPATH/bin
	$ sudo ./gobgpd
	{"level":"info","msg":"gobgpd started","time":"2016-06-11T06:20:46+09:00"}
	{"level":"info","msg":"### Zebra.Config: {true unix:/var/run/quagga/zserv.api []}","time":"2016-06-11T06:20:46+09:00"}


### gobgp_workerを起動します.

(1) etcdを起動しておきます

	$ etcd
	2016-06-11 06:30:27.485294 I | etcdmain: etcd Version: 2.3.2
	2016-06-11 06:30:27.485574 I | etcdmain: Git SHA: ce63f10
	2016-06-11 06:30:27.485770 I | etcdmain: Go Version: go1.6.2
	2016-06-11 06:30:27.485837 I | etcdmain: Go OS/Arch: linux/amd64
	2016-06-11 06:30:27.485892 I | etcdmain: setting maximum number of CPUs to 2, total number of available CPUs is 2
	2016-06-11 06:30:27.486210 W | etcdmain: no data-dir provided, using default data-dir ./default.etcd
	2016-06-11 06:30:27.486594 I | etcdmain: listening for peers on http://localhost:2380
	2016-06-11 06:30:27.486790 I | etcdmain: listening for peers on http://localhost:7001
	2016-06-11 06:30:27.486991 I | etcdmain: listening for client requests on http://localhost:2379
	2016-06-11 06:30:27.487278 I | etcdmain: listening for client requests on http://localhost:4001
	2016-06-11 06:30:27.487605 I | etcdserver: name = default
	2016-06-11 06:30:27.487748 I | etcdserver: data dir = default.etcd
	2016-06-11 06:30:27.487906 I | etcdserver: member dir = default.etcd/member
	2016-06-11 06:30:27.487960 I | etcdserver: heartbeat = 100ms
	2016-06-11 06:30:27.488175 I | etcdserver: election = 1000ms
	2016-06-11 06:30:27.488307 I | etcdserver: snapshot count = 10000
	2016-06-11 06:30:27.488431 I | etcdserver: advertise client URLs = http://localhost:2379,http://localhost:4001
	2016-06-11 06:30:27.488572 I | etcdserver: initial advertise peer URLs = http://localhost:2380,http://localhost:7001
	2016-06-11 06:30:27.488864 I | etcdserver: initial cluster = default=http://localhost:2380,default=http://localhost:7001
	2016-06-11 06:30:27.491120 I | etcdserver: starting member ce2a822cea30bfca in cluster 7e27652122e8b2ae
	2016-06-11 06:30:27.491365 I | raft: ce2a822cea30bfca became follower at term 0
	2016-06-11 06:30:27.491523 I | raft: newRaft ce2a822cea30bfca [peers: [], term: 0, commit: 0, applied: 0, lastindex: 0, lastterm: 0]
	2016-06-11 06:30:27.491583 I | raft: ce2a822cea30bfca became follower at term 1
	2016-06-11 06:30:27.491987 I | etcdserver: starting server... [version: 2.3.2, cluster version: to_be_decided]
	2016-06-11 06:30:27.493144 N | etcdserver: added local member ce2a822cea30bfca [http://localhost:2380 http://localhost:7001] to cluster 7e27652122e8b2ae
	2016-06-11 06:30:27.893465 I | raft: ce2a822cea30bfca is starting a new election at term 1
	2016-06-11 06:30:27.893604 I | raft: ce2a822cea30bfca became candidate at term 2
	2016-06-11 06:30:27.893615 I | raft: ce2a822cea30bfca received vote from ce2a822cea30bfca at term 2
	2016-06-11 06:30:27.893647 I | raft: ce2a822cea30bfca became leader at term 2
	2016-06-11 06:30:27.893672 I | raft: raft.node: ce2a822cea30bfca elected leader ce2a822cea30bfca at term 2
	2016-06-11 06:30:27.894329 I | etcdserver: published {Name:default ClientURLs:[http://localhost:2379 http://localhost:4001]} to cluster 7e27652122e8b2ae
	2016-06-11 06:30:27.894394 I | etcdserver: setting up the initial cluster version to 2.3
	2016-06-11 06:30:27.895839 N | etcdserver: set the initial cluster version to 2.3


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
	06:36:58.896 gohan.server INFO  Keystone backend server configured
	06:36:59.084 gohan.server INFO  etcd servers: [http://127.0.0.1:2379]
	06:36:59.084 gohan.server INFO  Enabling CORS for *
	06:36:59.085 gohan.server WARNING  cors for * have security issue
	06:36:59.085 gohan.server INFO  Static file serving from /etc/gohan/
	06:36:59.100 gohan.server INFO  Gohan no jikan desuyo (It's time for dinner!) 
	06:36:59.100 gohan.server INFO  Starting Gohan Server...

	

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
	| id        | 4cbcbbc0-7eaa-4d22-9ae5-ebb3353ad61d |
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
	| GoBGP-1   | 4cbcbbc0-7eaa-4d22-9ae5-ebb3353ad61d |    65001 | 192.168.200.103 | 10.0.1.1  | ACTIVE |
	| GoBGP-3   | 783fccd0-264f-470b-b095-c0c56a55e201 |    65001 | 192.168.200.105 | 10.0.1.3  | ACTIVE |
	| GoBGP-2   | c0983775-292b-4477-9696-bec407193e60 |    65001 | 192.168.200.104 | 10.0.1.2  | ACTIVE |
	+-----------+--------------------------------------+----------+-----------------+-----------+--------+


(3) gohanクライアントからBGP隣接情報を登録して、GoBGPdにneighborを設定します

	$ gohan client neighbor create --host_name GoBGP-1 --neighbor_addr 192.168.0.1 --peer_as 65000 --mgmt_addr 192.168.200.103
	+---------------+--------------------------------------+
	|   PROPERTY    |                VALUE                 |
	+---------------+--------------------------------------+
	| host_name     | GoBGP-1                              |
	| id            | c41bb5e8-c404-47a0-8ad9-2ff8e4282c6c |
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
	| GoBGP-2   | 434467d1-7b38-401d-9176-4f9f627ef8c5 | 192.168.200.104 | 192.168.1.1   |   65000 | UP     |
	| GoBGP-3   | 7049a5f4-16f9-47c1-8036-2ed57a2dc8cd | 192.168.200.105 | 172.16.0.1    |   65001 | UP     |
	| GoBGP-3   | 834da2a5-db04-40c6-99f2-e147adfd83ab | 192.168.200.105 | 192.168.2.2   |   65002 | UP     |
	| GoBGP-2   | 87990905-5dd7-4a48-9727-1cb87d48c65f | 192.168.200.104 | 172.16.1.2    |   65001 | UP     |
	| GoBGP-1   | 8e40c67e-6af7-45d6-adbe-52740902be0c | 192.168.200.103 | 172.16.0.2    |   65001 | UP     |
	| GoBGP-1   | c41bb5e8-c404-47a0-8ad9-2ff8e4282c6c | 192.168.200.103 | 192.168.0.1   |   65000 | UP     |
	| GoBGP-3   | ecf8f312-3701-471d-9f34-152a07e2cec6 | 192.168.200.105 | 172.16.1.1    |   65001 | UP     |
	+-----------+--------------------------------------+-----------------+---------------+---------+--------+

	GoBGPd側でBGP Peer開設できると、"STATUS: UP"となります



(4) GoBGP-3側でのCLIにて、BGPテーブルを確認しておきます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  192.168.100.0/24    192.168.0.1          65000                00:01:22   [{Origin: ?} {Med: 0} {LocalPref: 100}]
	*   192.168.100.0/24    192.168.1.1          65000                00:00:56   [{Origin: ?} {Med: 0} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:00:38   [{Origin: i} {Med: 1}]

    このままでは、192.168.100.0/24の経路に対するnext-hopへの到達性が無いため、BGPで学習した経路がルーティングテーブルに注入されません
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
	| id                | 82787751-43d1-42bc-8dac-6ed57323e14d |
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
	| export          | 172.16.1.1     | Existing | GoBGP-3   | 5175b7f0-cedf-46c8-bc11-ce5425fec3e2 | 192.168.200.105 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.0.2     | New      | GoBGP-1   | 82787751-43d1-42bc-8dac-6ed57323e14d | 192.168.200.103 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.0.1     | New      | GoBGP-3   | a1186223-8ef7-4660-a749-b2e181057c81 | 192.168.200.105 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	| export          | 172.16.1.2     | New      | GoBGP-2   | a8d60cef-5a53-4a0e-8613-31fc171e5d46 | 192.168.200.104 | policy1     | accept            | next-hop self    | statement1     | ACTIVE |
	+-----------------+----------------+----------+-----------+--------------------------------------+-----------------+-------------+-------------------+------------------+----------------+--------+


(6) 再度、GoBGP-3側でのCLIにて、BGPテーブルを確認してみます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  192.168.100.0/24    172.16.0.1           65000                00:07:02   [{Origin: i} {Med: 0} {LocalPref: 100}]
	*   192.168.100.0/24    172.16.1.1           65000                00:00:18   [{Origin: i} {Med: 0} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:00:38   [{Origin: i} {Med: 1}]

    期待通りに、next-hopが変更できました!!


(7) VyOS-4側でのBGPテーブルを確認してみます

	vyos@VyOS-4:~$ show ip bgp
	BGP table version is 0, local router ID is 10.0.0.4
	Status codes: s suppressed, d damped, h history, * valid, > best, i - internal,
	              r RIB-failure, S Stale, R Removed
	Origin codes: i - IGP, e - EGP, ? - incomplete

	   Network          Next Hop            Metric LocPrf Weight Path
	*> 192.168.100.0    192.168.2.1                            0 65001 65000 i
	*> 192.168.101.0    0.0.0.0                  1         32768 i

	Total number of prefixes 2

	期待通りに、192.168.100.0/24をBGPテーブルで保持できました!!


(8) エンドエンドでping通信確認してみます

	tsubo@pc1:~$ route -n
	Kernel IP routing table
	Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
	0.0.0.0         192.168.101.1   0.0.0.0         UG    0      0        0 eth1
	192.168.101.0   0.0.0.0         255.255.255.0   U     0      0        0 eth1

	tsubo@pc1:~$ ping 192.168.100.201 -I 192.168.101.2
	PING 192.168.100.201 (192.168.100.201) from 192.168.101.2 : 56(84) bytes of data.
	64 bytes from 192.168.100.201: icmp_seq=1 ttl=60 time=1.57 ms
	64 bytes from 192.168.100.201: icmp_seq=2 ttl=60 time=2.29 ms
	64 bytes from 192.168.100.201: icmp_seq=3 ttl=60 time=1.28 ms
	64 bytes from 192.168.100.201: icmp_seq=4 ttl=60 time=2.17 ms
	64 bytes from 192.168.100.201: icmp_seq=5 ttl=60 time=2.15 ms
	^C
	--- 192.168.100.201 ping statistics ---
	5 packets transmitted, 5 received, 0% packet loss, time 4010ms
	rtt min/avg/max/mdev = 1.284/1.897/2.290/0.396 ms

	期待通りに、ping通信できました!!


### GoBGPでの経路迂回を試してみます

(1) まず、GoBGP-3側でのCLIにて、BGPテーブルを確認しておきます

	$ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  192.168.100.0/24    172.16.0.1           65000                00:07:02   [{Origin: i} {Med: 0} {LocalPref: 100}]
	*   192.168.100.0/24    172.16.1.1           65000                00:00:18   [{Origin: i} {Med: 0} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:00:38   [{Origin: i} {Med: 1}]


(2) エンドエンドでtraceroute通信確認しておきます

	tsubo@pc1:~$ traceroute 192.168.100.201
	traceroute to 192.168.100.201 (192.168.100.201), 30 hops max, 60 byte packets
	 1  192.168.101.1 (192.168.101.1)  0.212 ms  0.132 ms  0.089 ms
	 2  192.168.2.1 (192.168.2.1)  0.397 ms  0.422 ms  0.383 ms
	 3  172.16.0.1 (172.16.0.1)  1.112 ms  1.066 ms  1.126 ms
	 4  * * *
	 5  192.168.100.201 (192.168.100.201)  1.911 ms  1.933 ms  1.981 ms


(3) VyOS-1を停止してみます

	vyos@VyOS-1:~$ sudo halt

	vyos@VyOS-1:~$ Broadcast message from root@VyOS-1 (pts/0) (Fri Jun 11 07:25:21 2016):

	The system is going down for system halt NOW!


(4) 再度、GoBGP-3側でのCLIにて、BGPテーブルを確認してみます

        $ gobgp global rib
	    Network             Next Hop             AS_PATH              Age        Attrs
	*>  192.168.100.0/24    172.16.1.1           65000                00:04:17   [{Origin: i} {Med: 0} {LocalPref: 100}]
	*>  192.168.101.0/24    192.168.2.2          65002                00:11:25   [{Origin: i} {Med: 1}]

	期待通りに、next-hopが変更されました!!


(5) 再度、エンドエンドでtraceroute通信確認してみます

	tsubo@pc1:~$ traceroute 192.168.100.201
	traceroute to 192.168.100.201 (192.168.100.201), 30 hops max, 60 byte packets
	 1  192.168.101.1 (192.168.101.1)  0.255 ms  0.255 ms  0.200 ms
	 2  192.168.2.1 (192.168.2.1)  1.117 ms  1.051 ms  0.962 ms
	 3  172.16.1.1 (172.16.1.1)  0.910 ms  0.914 ms  0.852 ms
	 4  * * *
	 5  192.168.100.201 (192.168.100.201)  3.082 ms  3.042 ms  2.994 ms

	期待通りに、ホップ経路が変更されました!!

