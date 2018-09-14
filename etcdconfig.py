import sys
from netaddr.ip import IPNetwork
# js_shell somehow garbles global import somewhere
globals()['IPNetwork'] = locals()['IPNetwork']

# config
nodes = ['192.168.64.240']
hosts = ['10.250.234.133','10.250.123.223','10.250.10.21']
letsencrypt_email = "kristof@vmlinuz.be"
recursive_resolvers = "8.8.8.8:53 1.1.1.1:53"
mgmtnic = 'ztrf24x2zy'

# etcd
listen_peer_urls = ", ".join(["http://%s:2380" % x for x in nodes ])
listen_client_urls = ", ".join(["http://%s:2379" % x for x in nodes ])
initial_advertise_peer_urls = listen_peer_urls
advertise_client_urls = listen_client_urls

etcdconfig  = """
# /etc/etcd.conf
name: '{0}'
data-dir: '{1}'
listen-peer-urls: {2}
listen-client-urls: {3}
initial-advertise-peer-urls: {4}
advertise-client-urls: {5}
""".format('proxy-etcd',
        '/etcd-data',
        listen_peer_urls,
        listen_client_urls,
        initial_advertise_peer_urls,
        advertise_client_urls)

# traefik
endpoints = ",".join(["%s:2379"%x for x in nodes])
traefikconfig = """
# /etc/traefik.toml
[etcd]
endpoint = {}
watch = true
prefix = "/traefik"

[acme]
email = "{}"
storageFile = "/etc/acme.json"
entryPoint = "https"

""".format(endpoints,letsencrypt_email)

# Coredns
dnsformat = ", ".join([ "%s:53" %x for x in nodes ])

basezone = """
# /etc/coredns.conf
. {{
    etcd . {{
        stubzones
        path /skydns
        endpoint {0}
        upstream {1}
    }}
    cache 160 skydns.local
    loadbalance
    proxy . {1}
}}

""".format(" ".join(["http://%s:2379"%x for x in nodes]),recursive_resolvers)


print(etcdconfig)
print(traefikconfig)
print(basezone)

trnodes = []
trcontainers = []
for i in hosts:
    trnodes.append(j.clients.zos.get('traef%s'%hosts.index(i),data={'host': i}))

for i in trnodes:
    n = trnodes.index(i) + 1
    nic =  [{'type':'macvlan','id':'enp6s0','hwaddr':'52:54:01:12:00:%02d'%n,'name':'public','config':{'dhcp':True}},
            {'type': 'zerotier', 'id': 'c7c8172af1f387a6'},
            {'type': 'zerotier', 'id': '1d71939404587f3c'}]
    trcontainers.append(i.containers.create('traefik-%s'%n, 'https://hub.grid.tf/delandtj/traefik.flist', nics=nic,hostname='traefik-%s'%n, env={'ETCDCTL_API':'3'}))

for i in trcontainers:
    # get ipv4 addr of mgmt interface in node







# we only work for 3 machines, so copy-pasta
traef1 = j.clients.zos.get('traef1',data={'host':hosts[0]})
traef2 = j.clients.zos.get('traef2',data={'host':hosts[1]})
traef2 = j.clients.zos.get('traef3',data={'host':hosts[3]})

trcont1_nics = [{'type':'macvlan','id':'enp6s0','hwaddr':'52:54:01:12:00:01','name':'public','config':{'dhcp':True}},{'type': 'zerotier', 'id': 'c7c8172af1f387a6'},{'type': 'zerotier', 'id': '1d71939404587f3c'}]
trcont2_nics = [{'type':'macvlan','id':'enp6s0','hwaddr':'52:54:01:12:00:02','name':'public','config':{'dhcp':True}},{'type': 'zerotier', 'id': 'c7c8172af1f387a6'},{'type': 'zerotier', 'id': '1d71939404587f3c'}]
trcont3_nics = [{'type':'macvlan','id':'enp6s0','hwaddr':'52:54:01:12:00:03','name':'public','config':{'dhcp':True}},{'type': 'zerotier', 'id': 'c7c8172af1f387a6'},{'type': 'zerotier', 'id': '1d71939404587f3c'}]

trcont1 = traef1.containers.create('traefik-1','https://hub.grid.tf/delandtj/traefik.flist',nics=trcont1_nics,hostname='traefik1',env={'ETCDCTL_API':'3'})
trcont2 = traef1.containers.create('traefik-2','https://hub.grid.tf/delandtj/traefik.flist',nics=trcont2_nics,hostname='traefik2',env={'ETCDCTL_API':'3'})
trcont3 = traef1.containers.create('traefik-3','https://hub.grid.tf/delandtj/traefik.flist',nics=trcont2_nics,hostname='traefik3',env={'ETCDCTL_API':'3'})

# Ok, now get ip addrs of sysadmin interface of containers
#
mgmtip1 = [ addr for addr in trcont1.client.ip.addr.list(mgmtnic) if IPNetwork(addr).version == 4 ][0]
mgmtip2 = [ addr for addr in trcont2.client.ip.addr.list(mgmtnic) if IPNetwork(addr).version == 4 ][0]
mgmtip3 = [ addr for addr in trcont3.client.ip.addr.list(mgmtnic) if IPNetwork(addr).version == 4 ][0]



