import sys
from netaddr.ip import IPNetwork
# js_shell somehow garbles global import somewhere
globals()['IPNetwork'] = locals()['IPNetwork']

# config
hosts = ['10.102.221.172', '10.102.223.247']
# hosts = ['10.250.234.133', '10.250.123.223', '10.250.10.21']
letsencrypt_email = "kristof@vmlinuz.be"
recursive_resolvers = "8.8.8.8:53 1.1.1.1:53"
hwbase = '54:52:00:01:00:'

domain = "arakoon.org"

farmerszt = 'c7c8172af1f387a6'
mgmtzt = '1d71939404587f3c'


# setup nodes
# TODO : barf if error
trnodes = []
trcontainers = []
for i in hosts:
    trnodes.append(
        j.clients.zos.get(
            'traef%s' %
            hosts.index(i),
            data={
                'host': i}))

for i in trnodes:
    n = trnodes.index(i) + 1
    nic = [{'type': 'macvlan',
            'id': 'enp6s0',
            'hwaddr': hwbase + '%02d' % n,
            'name': 'public',
            'config': {'dhcp': True}},
           {'type': 'zerotier',
            'id': farmerszt},
           {'type': 'zerotier',
            'id': mgmtzt}]

    trcontainers.append(
        i.containers.create(
            'traefik-%s' % n,
            'https://hub.grid.tf/delandtj/traefik.flist',
            nics=nic, hostname='traefik-%s' % n,
            env={
                'ETCDCTL_API': '3'}))


# here we wait till they come up, might be interesting to give them a manual
# ip address, so it's easier... but that doesn't matter
# TODO try until mgmtzt interface got an ip

mgmtztiface = [x['portDeviceName'] for x in
               trcontainers[0].client.zerotier.list() if x['id'] == mgmtzt]

mgmtcontainerips = []
for i in trcontainers:
    # get ipv4 addr of mgmt interface in node (take the first one)
    ipv4 = [addr for addr in i.client.ip.addr.list(
        mgmtzt) if IPNetwork(addr).version == 4][0]
    mgmtcontainerips.append(str(IPNetwork(ipv4).ip))

# create files for /etc/etcd.conf, /etc/traefik.toml and /etc/coredns.conf
# etcd
listen_peer_urls = ", ".join(["http://%s:2380" % x for x in mgmtcontainerips])
listen_client_urls = ", ".join(
    ["http://%s:2379" % x for x in mgmtcontainerips])
initial_advertise_peer_urls = listen_peer_urls
advertise_client_urls = listen_client_urls

# Etcd config
etcdconfig = """
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
endpoints = ",".join(["%s:2379" % x for x in mgmtcontainerips])

traefikconfig = """
# /etc/traefik.toml
[web]
address = ":8080"
[etcd]
endpoint = {}
watch = true
prefix = "/traefik"
useapiv3 = true

[entryPoints]
  [entryPoints.http]
  address = ":80"
    [entryPoints.http.redirect]
      entryPoint = "https"
  [entryPoints.https]
  address = ":443"
    [entryPoints.https.tls]

""".format(endpoints)

# Coredns
dbfile = """
$TTL 86400
$ORIGIN arakoon.org.
@  1D  IN  SOA ns.{0}. hostmaster.{0}. (
            2002022401 ; serial
            3H ; refresh
            15 ; retry
            1w ; expire
            3h ; nxdomain ttl
           )
        IN  NS     ns1.{0}.
        IN  NS     ns2.{0}.

        IN  MX  30 aspmx5.googlemail.com.
        IN  MX  30 aspmx4.googlemail.com.
        IN  MX  20 alt1.aspmx.l.google.com.
        IN  MX  30 aspmx2.googlemail.com.
        IN  MX  30 aspmx3.googlemail.com.
        IN  MX  20 alt2.aspmx.l.google.com.
        IN  MX  10 aspmx.l.google.com.
""".format(domain)

basezone = """
# /etc/coredns.conf
. {{
    etcd {2} {{
        stubzones
        path /skydns
        endpoint {0}
        upstream {1}
    }}
    cache 160 skydns.local
    loadbalance
    proxy . {1}
}}

""".format(" ".join(["http://%s:2379" % x for x in mgmtcontainerips]),
           recursive_resolvers, domain)

# get configs over, restart services

for i in trcontainers:
    i.upload_content('/etc/traefik.toml', traefikconfig)
    i.upload_content('/etc/etcd.conf', etcdconfig)
    i.upload_content('/etc/coredns.conf', basezone)
    i.upload_content('/etc/db.zone.{}', dbfile)
    # kill them, CoreX will restart them
    pslist = [proc['pid'] for proc in i.client.process.list()
              if proc['name'] in['traefik', 'coredns', 'etcd']]
    for p in pslist:
        i.client.process.kill(p)
