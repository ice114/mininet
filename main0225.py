
from device import Switch, Host,Device,DetailedLink
#from switchRuntime import SwitchRuntime
from TopoMaker0224 import MakeSatSwitchTopo
from RF2 import dijkstra_path
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os
from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch
import argparse
import sqlite3
from sw_LLA import load_location
from time import sleep
cwd = os.getcwd()
default_logs = os.path.join(cwd, 'logs')
default_pcaps = os.path.join(cwd, 'pcaps')
parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=False ,default= "simple_switch_grpc")
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=6)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)
parser.add_argument('--quiet', help='Suppress log messages.',
                    action='store_true', required=True, default=True)
parser.add_argument('--log-dir', type=str, required=False, default=default_logs)
#.add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)
args = parser.parse_args()
_MAX = float('inf')
class ctrlSat(object):
    def __init__(self,planeNum,satPerPlane):
        self.planeNum=planeNum
        self.satPerplane=satPerPlane
        self.total = self.planeNum * self.satPerplane
        self.satSwitches =[]
        self.sat_log=[]
        self.locatDict=dict
        self.hostLinkToSwitches=[]
        self.linksInfo=[] #link:sw1-p1 to sw2-p2
        self.linksInfo_h2s=[] #link host 2 switch
        self.linkMap=[[_MAX] * self.total for _ in range(self.total)]
        self.portMap=[[_MAX] * self.total for _ in range(self.total)]
        self.roads_nodesTran=[[_MAX] * self.total for _ in range(self.total)] #route founding result with nodes
        self.roads_portTran=[[_MAX] * self.total for _ in range(self.total)] #route founding result with ports
    def genMac(self, plane,sat):
        mac = '08:00:00:00:0'+str(plane)+':0'+str(sat)
        return mac
    def genIpforHost(self, plane,sat):

        ip='10.0.'+str(plane)+'.'+str(sat)
        return ip

    def genIPforSwitch(self,plane,sat):
        ip='192.168.'+str(plane)+'.'+str(sat)
        return ip
    def log_addr(self):
        print("2222222")
        for i in range(len(self.satSwitches)):
            tmp_addr=[]
            for j in range(len(self.satSwitches[i])):
                #self.sat_log[i][j]="/logs/%d.log" % self.satSwitches[i][j].name
                tmp_addr.append("/logs/"+self.satSwitches[i][j].name+".log")
            self.sat_log.append(tmp_addr)
    def genDevices(self):
        print("111111")
        for i in range(self.planeNum):
            tp_a_plane_sw=[]
            tp_a_plane_h=[]
            for j in range(self.satPerplane):
                thriftPort = 9090+10*i+j
                tp_a_plane_sw.append(
                    Switch('s' + str(i+1)+str(j+1), thriftPort=thriftPort,ip=self.genIPforSwitch(i+1,j+1),
                           locat=load_location.readCSV("sw_LLA/"+'s' + str(i+1)+str(j+1)+".csv",1))
                )
                # locat = load_location.readCSV("sw_LLA/" + 's' + str(i + 1) + str(j + 1) + ".csv", 1)
                # location_data=['s' + str(i+1)+str(j+1),locat[0],locat[1]]
                # load_location.add_db(location_data)
                tp_a_plane_h.append(
                    Host('h'+ str(i+1)+str(j+1),mac=self.genMac(i+1,j+1),ip=self.genIpforHost(i+1,j+1),locat=[i,j])
                )
                # location_data_h=['h'+ str(i+1)+str(j+1),i,j]
                # load_location.add_db(location_data_h)
            self.satSwitches.append(tp_a_plane_sw)
            self.hostLinkToSwitches.append(tp_a_plane_h)
    def printHostInf(self):
        for i in range(len(self.hostLinkToSwitches)):
            for j in range(len(self.hostLinkToSwitches[i])):
                print(self.hostLinkToSwitches[i][j].name, self.hostLinkToSwitches[i][j].macAddress,
                     self.hostLinkToSwitches[i][j].ipAddress)
    def genLinkInDetail(self,sw1,sw2,p1,p2):
        a_link=DetailedLink(sw1,sw2,p1,p2)
        return  a_link
    def printLinks(self):
        print('Number of links:', len(self.linksInfo))
        for i in range(len(self.linksInfo)):
            print(self.linksInfo[i].sw1, self.linksInfo[i].sw2, self.linksInfo[i].p1, self.linksInfo[i].p2)
    def printPorts(self,i,j):
        for s in range(len(self.satSwitches[i][j].ports)):
            print(self.satSwitches[i][j].ports[s].portNum,self.satSwitches[i][j].ports[s].deviceName)
    def genLink(self):
        print("3333333333333")
        for i in range(self.planeNum):
            for j in range(self.satPerplane):
                self.hostLinkToSwitches[i][j].addLink(self.satSwitches[i][j].name)
                self.satSwitches[i][j].addLink(self.hostLinkToSwitches[i][j].name)
                self.linksInfo_h2s.append(self.genLinkInDetail(self.hostLinkToSwitches[i][j].name,
                                                           self.satSwitches[i][j].name,
                                                           self.hostLinkToSwitches[i][j].portSum,
                                                           self.satSwitches[i][j].portSum))
        for i in range(self.planeNum-1):
            for j in range(self.satPerplane):
                self.satSwitches[i][j].addLink(self.satSwitches[i + 1][j].name)
                self.satSwitches[i + 1][j].addLink(self.satSwitches[i][j].name)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i + 1][j].name,
                                                           self.satSwitches[i][j].portSum,
                                                           self.satSwitches[i + 1][j].portSum))
                #self.switches[i][j].addLink(self.switches[i+1][j])
                #self.switches[i+1][j].addLink(self.switches[i][j])
        for i in range(self.planeNum):
            for j in range(self.satPerplane-1):
                self.satSwitches[i][j].addLink(self.satSwitches[i][j+1].name)
                self.satSwitches[i][j+1].addLink(self.satSwitches[i][j].name)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i][j+1].name,
                                                           self.satSwitches[i][j].portSum,
                                                           self.satSwitches[i][j+1].portSum))
            self.satSwitches[i][0].addLink(self.satSwitches[i][self.satPerplane-1].name)
            self.satSwitches[i][self.satPerplane-1].addLink(self.satSwitches[i][0].name)
            self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][0].name,
                                                       self.satSwitches[i][self.satPerplane-1].name,
                                                       self.satSwitches[i][0].portSum,
                                                       self.satSwitches[i][self.satPerplane-1].portSum))
    def genLink2(self):
        for i in range(self.planeNum):
            for j in range(self.satPerplane):
                self.hostLinkToSwitches[i][j].addLink(self.satSwitches[i][j].name)
                self.satSwitches[i][j].addLink(self.hostLinkToSwitches[i][j].name)
                self.linksInfo_h2s.append(self.genLinkInDetail(self.hostLinkToSwitches[i][j],
                                                           self.satSwitches[i][j],
                                                           self.hostLinkToSwitches[i][j].portSum,
                                                           self.satSwitches[i][j].portSum))
        for i in range(self.planeNum-1):
            for j in range(self.satPerplane):
                self.satSwitches[i][j].addLink(self.satSwitches[i + 1][j].name)
                self.satSwitches[i + 1][j].addLink(self.satSwitches[i][j].name)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j],
                                                           self.satSwitches[i + 1][j],
                                                           self.satSwitches[i][j].portSum,
                                                           self.satSwitches[i + 1][j].portSum))
                #self.switches[i][j].addLink(self.switches[i+1][j])
                #self.switches[i+1][j].addLink(self.switches[i][j])
        for i in range(self.planeNum):
            for j in range(self.satPerplane-1):
                self.satSwitches[i][j].addLink(self.satSwitches[i][j+1].name)
                self.satSwitches[i][j+1].addLink(self.satSwitches[i][j].name)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j],
                                                           self.satSwitches[i][j+1],
                                                           self.satSwitches[i][j].portSum,
                                                           self.satSwitches[i][j+1].portSum))
            self.satSwitches[i][0].addLink(self.satSwitches[i][self.satPerplane-1].name)
            self.satSwitches[i][self.satPerplane-1].addLink(self.satSwitches[i][0].name)
            self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][0],
                                                       self.satSwitches[i][self.satPerplane-1],
                                                       self.satSwitches[i][0].portSum,
                                                       self.satSwitches[i][self.satPerplane-1].portSum))
    def transP2T(self,plane,sat): #(1,1)->9
        number=plane*8+sat
        return number
    def transT2P(self,number):#s12->[0,1]->1
        p=[]
        p.append(int(number[1])-1)
        p.append(int(number[2])-1)
        t=self.transP2T(p[0],p[1])
        return t
    def genLinkMap(self):
        print("4444444444")
        for i in range(self.total):
            self.linkMap[i][i]=0
            self.portMap[i][i]=0
        for i in range(len(self.linksInfo)):
            sw1=self.transT2P(self.linksInfo[i].sw1)
            sw2 = self.transT2P(self.linksInfo[i].sw2)
            #print(sw1,sw2)
            self.linkMap[sw1][sw2]=1
            self.linkMap[sw2][sw1]=1
            self.portMap[sw1][sw2]=self.linksInfo[i].p1
            self.portMap[sw2][sw1]=self.linksInfo[i].p2
        #for i in range(len(self.portMap)):
        #    print(self.portMap[i])
    def route_fouding(self):
        print("55555555555")
        for i in range(self.total):
            for j in range(self.total):
                if i==j:
                    self.roads_nodesTran[i][j]=_MAX
                else:
                    tp_matrix=dijkstra_path(self.linkMap,i)
                    road=tp_matrix.find_shortestPath(j)
                    #value, road = Dijkstra(self.total, len(self.linksInfo), self.linkMap, i, j)
                    self.roads_nodesTran[i][j] = road
        #for i in range(len(self.roads_nodesTran)):
        #    print(self.roads_nodesTran[i])

        for i in range(len(self.roads_nodesTran)):
            for j in range(len(self.roads_nodesTran[i])):
                tp_portTran=[]
                if i != j:
                    for k in range(len(self.roads_nodesTran[i][j])):
                        if k==len(self.roads_nodesTran[i][j])-1 :
                            tp_portTran.append(1)
                        else:
                            ln=self.roads_nodesTran[i][j][k]
                            rn=self.roads_nodesTran[i][j][k+1]
                            for l in range(len(self.linksInfo)):
                                #print(self.linksInfo[l].sw1)
                                #print(self.transT2P(self.linksInfo[l].sw1),self.transT2P(self.linksInfo[l].sw2))
                                if self.transT2P(self.linksInfo[l].sw1)==ln and self.transT2P(self.linksInfo[l].sw2)==rn:
                                    tp_portTran.append(self.linksInfo[l].p1)
                                    break
                                elif self.transT2P(self.linksInfo[l].sw2)==ln and self.transT2P(self.linksInfo[l].sw1)==rn:
                                    tp_portTran.append(self.linksInfo[l].p2)
                                    break
                self.roads_portTran[i][j]=tp_portTran



        #for i in range(len(self.roads_nodesTran)):
        #    print(self.roads_portTran[i])
    def genLocatDict(self):
        print("666666666")
        LocatDict=dict()
        for i in range(len(self.hostLinkToSwitches)):
            for j in range(len(self.hostLinkToSwitches[i])):
                # LocatDict[self.hostLinkToSwitches[i][j].ipAddress]=self.hostLinkToSwitches[i][j].locat
                LocatDict[self.hostLinkToSwitches[i][j].ipAddress]=self.hostLinkToSwitches[i][j].locat
                data=[self.hostLinkToSwitches[i][j].ipAddress,self.hostLinkToSwitches[i][j].locat[1],self.hostLinkToSwitches[i][j].locat[0]]
                load_location.add_db("h",data)
        for i in range(len(self.satSwitches)):
            for j in range(len(self.satSwitches[i])):
                # LocatDict[self.satSwitches[i][j].ipAddress]=self.satSwitches[i][j].locat
                LocatDict[self.satSwitches[i][j].ipAddress] =self.satSwitches[i][j].locat
                data=[self.satSwitches[i][j].ipAddress,self.satSwitches[i][j].locat[1],self.satSwitches[i][j].locat[0]]
                load_location.add_db("sw", data)
        return LocatDict

    def makeTopo(self):
        print("777777777777")
        mode = args.mode
        setLogLevel('info')
        topo = MakeSatSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            self)
        # defaultSwitchClass = P4RuntimeSwitch(
        #     sw_path=args.behavioral_exe,
        #     json_path=args.json,
        #     log_console=True,
        #     pcap_dump=args.pcap_dump)

        net=Mininet(topo=topo,
                    host=P4Host,
                    switch=P4RuntimeSwitch,
                    controller=None)
        net.start()
        # sw_mac = ["00:aa:bb:00:00:%02x" % n for n in range(self.total)]
        # sw_addr = ["10.0.%d.1" % n for n in range(self.total)]
        #
        # for i in range(len(self.hostLinkToSwitches)):
        #     for j in range(len(self.hostLinkToSwitches[i])):
        #         h = net.get(self.hostLinkToSwitches[i][j].name)
        #         if mode == "l2":
        #             h.setDefaultRoute("dev eth0")
        #         else:
        #             h.setARP(sw_addr[self.transP2T(i,j)], sw_mac[self.transP2T(i,j)])
        #             h.setDefaultRoute("dev eth0 via %s" % sw_addr[self.transP2T(i,j)])
        # for i in range(len(self.hostLinkToSwitches)):
        #     for j in range(len(self.hostLinkToSwitches[i])):
        #         h = net.get(self.hostLinkToSwitches[i][j].name)
        #         h.describe()
        # sleep(1)
        print("Ready !")
        CLI(net)
        net.stop()

    def start(self):
        self.genDevices()
        self.log_addr()
        self.genLink()
        #self.printLinks()
        #self.printPorts(0,0)
        self.genLinkMap()
        self.route_fouding()
        self.locatDict=self.genLocatDict()
        self.makeTopo()
if __name__ == '__main__':
    app=ctrlSat(6,8)
    app.start()

    #app.printHostInf()
