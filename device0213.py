

class Device(object):
    def __init__(self,name):
        self.name = name
        self.ports =[]
        self.portSum =0

class Switch(Device):
    def __init__(self, planeNum=0, satNum=0,thrift_port=9090,device_id=0):
        self.satNum = satNum
        self.planeNum = planeNum
        name='s'+str(planeNum)+'-'+str(satNum)
        self.name= name
        self.thrift_port=thrift_port
        self.device_id=device_id
        self.ip=genIPforSwitch(planeNum,satNum)
        self.locat=[]
class Host(Device):
    def __init__(self,planeNum=0, satNum=0):
        self.satNum = satNum
        self.planeNum = planeNum
        name = 'h' + str(planeNum) + '-' + str(satNum)
        self.name = name
        self.ip=genIPforHost(planeNum,satNum)
        self.mac=genMACforHost(planeNum,satNum)
def genIPforHost(i,j):
    preIp='10.0.'
    ip=preIp+str(i)+'.'+str(j)
    return ip
def genIPforSwitch(i,j):
    preIp = '127.0.'
    ip = preIp + str(i) + '.' + str(j)
    return ip
def genMACforHost(i,j):
    preMAC='00:10:00:00:00:'
    mac=preMAC+str(i)+str(j)
    return mac

if __name__=='__main__':
    switches=[]
    hosts=[]
    for i in range(6):
        for j in range(8):
            switch1=Switch(i,j,9090+i*10+j,0+i*10+j)
            switches.append(switch1)
            host1=Host(i,j)
            hosts.append(host1)
    for i in range(len(switches)):
        print(switches[i].name,switches[i].thrift_port,switches[i].device_id,switches[i].thrift_port,switches[i].ip)