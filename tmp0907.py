from copy import deepcopy
from mininet.examples import  sshd
import datetime
from device import Switch, Host,Device,DetailedLink
#from switchRuntime import SwitchRuntime
from TopoMaker0907 import MakeSatSwitchTopo
from RF2 import dijkstra_path,startwith
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
from threading import Thread
from location_update import link_status_update
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
        self.groud_ending_host=[]
        self.ground_gw=[]
        self.linksInfo=[] #link:sw1-p1 to sw2-p2
        self.linksInfo_h2s=[] #link host 2 switch
        self.linkMap=[[_MAX] * self.total for _ in range(self.total)]
        self.actual_map=[[_MAX] * self.total for _ in range(self.total)]
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
    def transP2T(self,plane,sat): #(1,1)->9
        number=plane*8+sat
        return number
    def transT2P(self,number):#s12->[0,1]->1
        p=[]
        p.append(int(number[1])-1)
        p.append(int(number[2])-1)
        t=self.transP2T(p[0],p[1])
        return t
    def genDevices(self):
        print("111111")
        # sat_switches and their hosts(a sat_switche + its host = a sat)
        for i in range(self.planeNum):
            tp_a_plane_sw=[]
            tp_a_plane_h=[]
            for j in range(self.satPerplane):
                thriftPort = 9090+10*i+j
                tp_a_plane_sw.append(
                    Switch('s' + str(i+1)+str(j+1), thriftPort=thriftPort,ip=self.genIPforSwitch(i+1,j+1),
                           locat=load_location.readCSV("sw_LLA/"+'s' + str(i+1)+str(j+1)+".csv",1))
                )
                tp_a_plane_h.append(
                    Host('h'+ str(i+1)+str(j+1),mac=self.genMac(i+1,j+1),ip=self.genIPforSwitch(i+1,j+1),locat=load_location.readCSV("sw_LLA/"+'s' + str(i+1)+str(j+1)+".csv",1))
                )
            self.satSwitches.append(tp_a_plane_sw)
            self.hostLinkToSwitches.append(tp_a_plane_h)



        self.groud_ending_host.append(
            Host('u1', mac=self.genMac(7,7),ip=self.genIpforHost(7,7),locat=[116,40]))  #beijing  ground station
        self.groud_ending_host.append(
            Host('u2', mac=self.genMac(8, 8), ip=self.genIpforHost(8, 8), locat=[75, 39])) #wuqia
        thriftPort = 9090 + 10 * 9 + 9
        self.ground_gw.append( Switch('g1', thriftPort=thriftPort,ip=self.genIPforSwitch(9,9),
                           locat=[118,50]))
        thriftPort = 9090 + 10 * 10 + 10
        self.ground_gw.append(Switch('g2', thriftPort=thriftPort, ip=self.genIPforSwitch(10, 10),
                                     locat=[80, 40]))
    def log_addr(self):
        print("2222222")
        for i in range(len(self.satSwitches)):
            tmp_addr=[]
            for j in range(len(self.satSwitches[i])):
                #self.sat_log[i][j]="/logs/%d.log" % self.satSwitches[i][j].name
                tmp_addr.append("/logs/"+self.satSwitches[i][j].name+".log")
            self.sat_log.append(tmp_addr)
    def genLink(self):
        print("3333333333333")
        # s11 link s21 in port2  s21 link s11 in port3 (s11,s21,2,3)(s11,s18,4,5)
        for i in range(self.planeNum - 1):
            for j in range(self.satPerplane):
                self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][j].name, 2)
                self.satSwitches[i + 1][j].addLink1(self.satSwitches[i][j].name, 3)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i + 1][j].name,
                                                           2,
                                                           3))
                # self.switches[i][j].addLink(self.switches[i+1][j])
                # self.switches[i+1][j].addLink(self.switches[i][j])
        for i in range(self.planeNum-1):
            for j in range(self.satPerplane):
                if j!=0:
                    self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][j-1].name, 4)
                    self.satSwitches[i + 1][j-1].addLink1(self.satSwitches[i][j].name, 5)
                    self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                               self.satSwitches[i + 1][j-1].name,
                                                               4,
                                                               5))
                else:
                    self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][self.satPerplane-1].name, 4)
                    self.satSwitches[i + 1][self.satPerplane-1].addLink1(self.satSwitches[i][j].name, 5)
                    self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                               self.satSwitches[i + 1][self.satPerplane-1].name,
                                                               4,
                                                               5))
        # s11 link s12 in port6 s12 link s11 in port7
        for i in range(self.planeNum):
            for j in range(self.satPerplane - 1):
                self.satSwitches[i][j].addLink1(self.satSwitches[i][j + 1].name, 6)
                self.satSwitches[i][j + 1].addLink1(self.satSwitches[i][j].name, 7)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i][j + 1].name,
                                                           6,
                                                           7))
            self.satSwitches[i][0].addLink1(self.satSwitches[i][self.satPerplane - 1].name, 7)
            self.satSwitches[i][self.satPerplane - 1].addLink1(self.satSwitches[i][0].name, 6)
            self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][0].name,
                                                       self.satSwitches[i][self.satPerplane - 1].name,
                                                       7,
                                                       6))



        #broadcast wireless
        # for i in range(self.planeNum):
        #     for j in range(self.satPerplane):
        #         for k in range(len(self.groud_ending_host)):
        #             host_port=6
        #             self.groud_ending_host[k].addLink(self.satSwitches[i][j].name)
        #             self.satSwitches[i][j].addLink(self.groud_ending_host[k].name)
        #             self.linksInfo_h2s.append(self.genLinkInDetail(self.groud_ending_host[k].name,
        #                                                            self.satSwitches[i][j].name,
        #                                                            self.groud_ending_host[k].portSum,
        #                                                            host_port))
        #             host_port+=1

        for k in range(len(self.ground_gw)):
            sat_port = 8+k
            host_port=0
            for i in range(self.planeNum):
                for j in range(self.satPerplane):
                    self.ground_gw[k].addLink(self.satSwitches[i][j].name)
                    self.satSwitches[i][j].addLink(self.ground_gw[k].name)
                    self.linksInfo_h2s.append(self.genLinkInDetail(self.ground_gw[k].name,
                                                                   self.satSwitches[i][j].name,
                                                                   host_port,
                                                                   sat_port))
                    host_port += 1
        for i in range(len(self.groud_ending_host)):
            self.groud_ending_host[i].addLink(self.ground_gw[i].name)
            self.ground_gw[i].addLink(self.groud_ending_host[i].name)

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
        self.actual_map=deepcopy(self.linkMap)
        for i in range(self.planeNum):
            for j in range(self.satPerplane):
                next_locat = load_location.readCSV("sw_LLA/" + 's' + str(i + 1) + str(j + 1) + ".csv", 2)[1]
                if abs(self.hostLinkToSwitches[i][j].locat[1])>70:
                    for k in self.satSwitches[i][j].ports:
                        if k.portNum == 4 or k.portNum == 2:
                            self.actual_map[self.transP2T(i, j)][self.transT2P(k.deviceName)] = _MAX
                            self.actual_map[self.transT2P(k.deviceName)][self.transP2T(i, j)] = _MAX
                elif self.hostLinkToSwitches[i][j].locat[1] < next_locat:
                    # for k in self.hostLinkToSwitches[i][j].ports:
                    for k in self.satSwitches[i][j].ports:
                        # if k[0]==4:
                        if k.portNum == 4:
                            self.actual_map[self.transP2T(i,j)][self.transT2P(k.deviceName)]=_MAX
                            self.actual_map[self.transT2P(k.deviceName)][self.transP2T(i,j)]=_MAX
                elif self.hostLinkToSwitches[i][j].locat[1] > next_locat:
                    # for k in self.hostLinkToSwitches[i][j].ports:
                    for k in self.satSwitches[i][j].ports:
                        # if k[0]==2:
                        if k.portNum==2:
                            self.actual_map[self.transP2T(i,j)][self.transT2P(k.deviceName)]=_MAX
                            self.actual_map[self.transT2P(k.deviceName)][self.transP2T(i,j)]=_MAX
        # print(self.actual_map)
        for i in range(self.total):
            # len, road = startwith(i, self.actual_map)
            # print(road)
            for j in range(self.total):
                if i==j:
                    self.roads_nodesTran[i][j]=_MAX
                else:
                    tp_matrix=dijkstra_path(self.actual_map,i)
                    road=tp_matrix.find_shortestPath(j)
                    self.roads_nodesTran[i][j]=road
                    # road_l=road[str(j)]
                    # road_l.append(j)
                    # self.roads_nodesTran[i][j] =road_l
                    # print(self.roads_nodesTran[i][j])
        # for i in range(self.total):
        #     for j in range(self.total):
        #         print(self.roads_nodesTran[i][j])
        #         print(self.roads_nodesTran[j][i])
        # for i in range(len(self.roads_nodesTran)):
        #     for j in range(len(self.roads_nodesTran[i])):
        #         print(self.roads_nodesTran[i][j])
        hopsnum = []
        for i in range(len(self.roads_nodesTran)):
            for j in range(len(self.roads_nodesTran[i])):
                if self.roads_nodesTran[i][j]!=_MAX:
                    hopsnum.append(len(self.roads_nodesTran[i][j]) - 1)
        hopsnum.sort(reverse=True)
        Note = open('sat_log/max_hops.txt', mode='a')
        Note.writelines([str(datetime.datetime.now()), "max hop:", str(hopsnum[1]), '\n'])
        Note.close()
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
                elif i==j:
                    tp_portTran.append(1)
                self.roads_portTran[i][j]=tp_portTran

        for i in range(len(self.roads_portTran)):
            for j in range(len(self.roads_portTran[j])):
                if len(self.roads_portTran[i][j])!=0:
                    data=[str([i,j]),str(self.roads_portTran[i][j])]
                    load_location.add_db("SR",data)
                    if i!=j:
                        Note = open('sat_log/hops_num.txt', mode='a')
                        Note.writelines([str(len(self.roads_portTran[i][j])+1), '\n'])
                        Note.close()
        # for i in range(len(self.roads_nodesTran)):
        #    print(self.roads_portTran[i])
    def genLocatDict(self):
        print("666666666")
        LocatDict=dict()
        for i in range(len(self.hostLinkToSwitches)):
            for j in range(len(self.hostLinkToSwitches[i])):
                load_location.add_db("sw_prefix",[self.hostLinkToSwitches[i][j].ipAddress,"0","0"])

        for i in range(len(self.hostLinkToSwitches)):
            for j in range(len(self.hostLinkToSwitches[i])):
                print(self.hostLinkToSwitches[i][j].ipAddress,self.hostLinkToSwitches[i][j].locat[1],self.hostLinkToSwitches[i][j].locat[0])
        for i in range(len(self.hostLinkToSwitches)):
            for j in range(len(self.hostLinkToSwitches[i])):

                # LocatDict[self.hostLinkToSwitches[i][j].ipAddress]=self.hostLinkToSwitches[i][j].locat
                LocatDict[self.hostLinkToSwitches[i][j].ipAddress]=self.hostLinkToSwitches[i][j].locat
                data=[self.hostLinkToSwitches[i][j].ipAddress,self.hostLinkToSwitches[i][j].locat[0],self.hostLinkToSwitches[i][j].locat[1]]
                print(data)
                load_location.add_db("sw",data)
        for i in range(len(self.groud_ending_host)):
            LocatDict[self.groud_ending_host[i].ipAddress]=self.groud_ending_host[i].locat
            data=[self.groud_ending_host[i].ipAddress,self.groud_ending_host[i].locat[0],self.groud_ending_host[i].locat[1],self.groud_ending_host[i].name]
            load_location.add_db("h",data)
        return LocatDict
    def genLocatDict2(self):
        LocatDict = dict()
        for i in range(len(self.hostLinkToSwitches)):
            #for j in range(len(self.hostLinkToSwitches[i])):
                # LocatDict[self.hostLinkToSwitches[i][j].ipAddress]=self.hostLinkToSwitches[i][j].locat
                LocatDict[self.hostLinkToSwitches[i].ipAddress] = self.hostLinkToSwitches[i].locat
                data = [self.hostLinkToSwitches[i].ipAddress, self.hostLinkToSwitches[i].locat[1],
                        self.hostLinkToSwitches[i].locat[0],self.hostLinkToSwitches[i].name]

                load_location.add_db("h", data)
        for i in range(len(self.satSwitches)):
            for j in range(len(self.satSwitches[i])):
                # LocatDict[self.satSwitches[i][j].ipAddress]=self.satSwitches[i][j].locat
                LocatDict[self.satSwitches[i][j].ipAddress] = self.satSwitches[i][j].locat
                data = [self.satSwitches[i][j].ipAddress, self.satSwitches[i][j].locat[1],
                        self.satSwitches[i][j].locat[0]]
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
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # for i in topo.links(withInfo=True,withKeys=True):
        #     print(i)
        print(topo.hosts(sort=False))

        net=Mininet(topo=topo,
                    host=P4Host,
                    switch=P4RuntimeSwitch
                    )


        net.start()

        # argvopts ='-D -o UseDNS=no -u0'
        # sshd.sshd(net, opts=argvopts)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # sats=[]
        # #
        # for i in range(6):
        #     for j in range(8):
        #         name='h'+str(i+1)+str(j+1)
        #         host=net.get(name)
        #         sats.append(host)
        # ground=net.get('u1')
        # self.houtai(sats,ground)
        #
        # thread_for_houtai = Thread(target=self.houtai, args=(sats,ground), daemon=True)
        # thread_for_houtai.start()

        thread_for_update = Thread(target=link_status_update,
                                   args=(self.hostLinkToSwitches, self.linkMap, self.linksInfo), daemon=True)
        thread_for_update.start()
        # for i in topo.hosts:
        #     if 'h' in i.name:
        #         i.cmd('./sw_recieve_regi0324.py')
        #     elif 'u1' in i.name:
        #         i.cmd('./ground.py')
        print("Ready !")

        CLI(net,script='program.txt')

        CLI(net)



        net.stop()
    def houtai(self,sats,ground):
        for i in range(len(sats)):
                sats[i].cmd('sudo sh test.sh')

        #ground.cmd('sudo python ground.py')
    def start(self):
        self.genDevices()
        self.log_addr()
        self.genLink()
        # #self.printLinks()
        # #self.printPorts(0,0)
        # self.genLinkMap()
        # self.route_fouding()
        # self.locatDict=self.genLocatDict()
        self.makeTopo()




if __name__ == '__main__':
    app=ctrlSat(6,8)
    app.start()

    #app.printHostInf()
