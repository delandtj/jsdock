iyo = j.clients.itsyouonline.get()
jwt = iyo.jwt_get(refreshable=True,scope='user:memberof:threefold.sysadmin')
cl = j.clients.zos.get('node1', data={'host' : '172.29.51.96'})
cl.client.config.data_set('password_', jwt)
cl.client.config.data
cl.containers.list()
j.tools.configmanager.path
