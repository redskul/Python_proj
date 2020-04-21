from hdbcli import dbapi

Connection = dbapi.connect(address='ussltcsnl1209.solutions.glbsnet.com', port=30015, user='system', password='cR42ket3rs')

print(Connection.isconnected())
