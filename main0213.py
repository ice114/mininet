from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI
from p4_mininet import P4Host
from p4runtime_switch import P4RuntimeSwitch
import  device0213
sw_path ='/home/fxy/Workspace/P4/mininet/simple_switch_grpc'
json_path ='/home/fxy/Workspace/P4/tutorials/exercises/basic/build/basic.json'

class MakeSatTopo(Topo):
    def __init__(self, OrbitNum, SatPerPlane, sw_path, json_path, **opts):
        Topo.__init__(self, **opts)
        self.sats = []
        self.sat_host =[]
        self.name = []
        switches = []
        hosts = []
        for i in range(OrbitNum):
            switches_tp=[]
            hosts_tp=[]
            for j in range(SatPerPlane):
                switch1 = device0213.Switch(i+1, j+1, 9033 + i * 10 + j, 0 + i * 10 + j)
                switches_tp.append(switch1)
                host1 = device0213.Host(i+1, j+1)
                hosts_tp.append(host1)
            switches.append(switches_tp)
            hosts.append(hosts_tp)

        print(len(hosts))
        for i in range(len(switches)):
            a_plane = []
            a_plane_host=[]
            names = []
            for j in range(len(switches[i])):
                sat = self.addSwitch(switches[i][j].name,
                                     ip=switches[i][j].ip,
                                     sw_path=sw_path,
                                     json_path=json_path,
                                     thrift_port=switches[i][j].thrift_port,
                                     device_id=switches[i][j].device_id,
                                     pcap_dump=False)
                names.append('s-' + str(i + 1) + '-' + str(j + 1))
                a_plane.append(sat)
                #print(hosts[i][j].name)
                # print('add '+'s-'+str(i+1)+'-'+str(j+1))
                #self.addHost(hosts[i][j].name,
                #             ip=hosts[i][j].ip,
                #             mac=hosts[i][j].mac)
                #print(hosts[i][j].name, hosts[i][j].ip, hosts[i][j].mac)
                # print('add '+'h-'+str(i+1)+'-'+str(j+1))
            self.sats.append(a_plane)
            self.name.append(names)


        for i in range(OrbitNum - 1):
            for j in range(SatPerPlane):
                #print(i, j,'-', i + 1, j)
                self.addLink(self.sats[i][j], self.sats[i + 1][j])
        for i in range(OrbitNum):
            for j in range(SatPerPlane - 1):
                #print(i, j, '-', i , j+1)
                self.addLink(self.sats[i][j], self.sats[i][j + 1])
            self.addLink(self.sats[i][0], self.sats[i][SatPerPlane - 1])

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
def PerSat():
    tp = MakeSatTopo(OrbitNum=6, SatPerPlane=8, sw_path =sw_path, json_path=json_path)
    #print(len(tp.sat_host))
    #print (len(tp.hosts[0]))
    net1 = Mininet(tp, host=P4Host, switch=P4RuntimeSwitch)
    net1.start()
    CLI(net1)
    net1.stop()


if __name__ == '__main__':

    PerSat()
   # a =genIPforHost(1,2)
   # print(a)
    #b = genMACforHost(1,2)
    #print(b)
