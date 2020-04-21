import pyhdb
import os

import pyhdb

#from hdbcli import dbapi
host='ussltcsnl1209.solutions.glbsnet.com'
connection = pyhdb.connect(host='ussltcsnl1209.solutions.glbsnet.com',port='30015',user='system',password='cR42ket3rs')
print(str(connection.isconnected())+"conection is established to" +host)

cursor=connection.cursor()

statement=cursor.execute('select * from m_databases')
ans=cursor.fetchone()
print(ans)

time=datetime.datetime.now()
print(time)

try:
    prefix=time
    statement1=cursor.execute('backup data using file'+prefix)
    os.chdir("/usr/sap/HNN/HDB00/ussltcsnl1209/trace")
    file=open("backup.log","rt")
    contents=file.read()
    mylines=[]
    with open('backup.log','rt') as file:
        for mylines in file:
            mylines.append(mylines.rstrip("\n"))
#locate for error
     index=0
     prev=0
     str=mylines[0]
     substring="error"
     while index <len(str):

        index=str.find(substring,index)
        if index == -1:
        break
    print(""*(index - prev) + "error" ,end='')
        prev=index + len(substring)
        index = len(substring) +1
print(str)

except:
    print("back up scheduled")



