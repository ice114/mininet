# 导入必要的库和模块
from copy import deepcopy  # 用于创建对象的深拷贝
import sys  # 系统相关的参数和函数
import subprocess  # 用于执行外部命令
from mininet.examples import sshd  # Mininet中用于启动ssh服务的模块
import datetime  # 用于处理日期和时间
from device import Switch, Host, Device, DetailedLink  # 自定义的设备类
# from switchRuntime import SwitchRuntime  # 可能用于处理交换机运行时的模块（被注释掉了）
from TopoMaker0907 import MakeSatSwitchTopo  # 用于创建卫星交换拓扑的模块
from RF2 import dijkstra_path, startwith  # 用于Dijkstra最短路径算法和启动函数
from mininet.net import Mininet  # Mininet网络创建和管理的模块
from mininet.topo import Topo  # Mininet拓扑创建的模块
from mininet.log import setLogLevel, info  # Mininet日志设置和信息输出的模块
from mininet.cli import CLI  # Mininet命令行接口
import os  # 操作系统接口
from p4_mininet import P4Switch, P4Host  # P4语言相关的Mininet模块
from p4runtime_switch import P4RuntimeSwitch  # P4运行时交换机模块
import argparse  # 用于解析命令行参数
import sqlite3  # SQLite数据库连接和操作的模块
from sw_LLA import load_location  # 用于加载交换机位置信息的模块
from time import sleep  # 用于暂停执行的函数
from threading import Thread  # 用于创建线程的模块
from location_update import link_status_update  # 用于更新链路状态的模块

# 获取当前工作目录和默认日志、pcap文件存储路径
cwd = os.getcwd()
default_logs = os.path.join(cwd, 'logs')
default_pcaps = os.path.join(cwd, 'pcaps')

# 创建命令行参数解析器
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
                    action='store_true', required=False, default=False)
parser.add_argument('--log-dir', type=str, required=False, default=default_logs)
# .add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)

# 解析命令行参数
args = parser.parse_args()

# 定义一个很大的数，用于比较和循环
_MAX = sys.maxsize
class ctrlSat(object):
    def __init__(self, planeNum, satPerPlane):
        """
        初始化控卫星类。
        
        :param planeNum: 卫星平面的数量
        :param satPerPlane: 每个平面上的卫星数量
        """
        self.planeNum = planeNum  # 卫星平面的数量
        self.satPerplane = satPerPlane  # 每个平面上的卫星数量
        self.total = self.planeNum * self.satPerplane  # 总卫星数量
        self.satSwitches = []  # 存储卫星交换机的列表
        self.sat_log = []  # 存储卫星交换机日志的列表
        self.locatDict = dict  # 存储位置信息的字典
        self.hostLinkToSwitches = []  # 存储主机连接到交换机的列表
        self.groud_ending_host = []  # 存储地面终端主机的列表
        self.ground_gw = []  # 存储地面网关的列表
        self.gw_host = []  # 存储地面网关主机的列表
        self.linksInfo = []  # 存储链路信息，格式为sw1-p1 to sw2-p2
        self.linksInfo_h2s = []  # 存储主机到交换机的链路信息
        self.linkMap = [[_MAX] * self.total for _ in range(self.total)]  # 存储链路映射
        self.actual_map = [[_MAX] * self.total for _ in range(self.total)]  # 存储实际链路映射
        self.portMap = [[_MAX] * self.total for _ in range(self.total)]  # 存储端口映射
        self.roads_nodesTran = [[[_MAX]] * self.total for _ in range(self.total)]  # 存储路由结果与节点
        self.roads_portTran = [[[_MAX]] * self.total for _ in range(self.total)]  # 存储路由结果与端口

    def genMac(self, plane, sat):
        """
        生成主机的MAC地址。
        
        :param plane: 平面编号
        :param sat: 卫星编号
        :return: 生成的MAC地址
        """
        mac = '08:00:00:00:0' + str(plane) + ':0' + str(sat)
        return mac

    def genIpforHost(self, plane, sat):
        """
        生成主机的IP地址。
        
        :param plane: 平面编号
        :param sat: 卫星编号
        :return: 生成的IP地址
        """
        ip = '10.0.' + str(plane) + '.' + str(sat)
        return ip

    def genIPforSwitch(self, plane, sat):
        """
        生成交换机的IP地址。
        
        :param plane: 平面编号
        :param sat: 卫星编号
        :return: 生成的IP地址
        """
        ip = '192.168.' + str(plane) + '.' + str(sat)
        return ip

    def log_addr(self):
        """
        生成日志地址。
        """
        print("2222222")
        for i in range(len(self.satSwitches)):
            tmp_addr = []
            for j in range(len(self.satSwitches[i])):
                tmp_addr.append("/logs/" + self.satSwitches[i][j].name + ".log")
            self.sat_log.append(tmp_addr)

    def genDevices(self):
        """
        生成设备。
        """
        print("111111")
        for i in range(self.planeNum):
            tp_a_plane_sw = []
            tp_a_plane_h = []
            for j in range(self.satPerplane):
                thriftPort = 9090 + 10 * i + j
                tp_a_plane_sw.append(
                    Switch('s' + str(i + 1) + str(j + 1), thriftPort=thriftPort, ip=self.genIPforSwitch(i + 1, j + 1),
                           locat=load_location.readCSV("sw_LLA/" + 's' + str(i + 1) + str(j + 1) + ".csv", 1))
                ) # 交换机的信息，S11，第一个平面的第一个卫星
                tp_a_plane_h.append(
                    Host('h' + str(i + 1) + str(j + 1), mac=self.genMac(i + 1, j + 1), ip=self.genIPforSwitch(i + 1, j + 1),
                         locat=load_location.readCSV("sw_LLA/" + 's' + str(i + 1) + str(j + 1) + ".csv", 1))
                ) # 主机的信息，h11，第一个平面的第一个卫星
            self.satSwitches.append(tp_a_plane_sw)
            self.hostLinkToSwitches.append(tp_a_plane_h)

       
        thriftPort = 9090 + 10 * 9 + 9  # 这一行代码似乎是孤立的，可能是用于生成某个特定的thriftPort
        self.ground_gw.append(
            Switch('g1'  , thriftPort=thriftPort, ip=self.genIPforSwitch(9, 9),
                   locat=[117,41])
        )#第一个地面网关，g1 端口号为9090+90+9
        self.gw_host.append(
            Host('gw1', mac=self.genMac(9,9),ip=self.genIpforHost(9,9),locat=[117,41]))#第一个地面主机gw1
        thriftPort = 9090 + 10 * 10 + 10
        self.ground_gw.append(
            Switch('g2' , thriftPort=thriftPort, ip=self.genIPforSwitch(10, 10),
                   locat=[76, 40])
        )#第二个地面网关，g2 端口号为9090+100+10
        self.gw_host.append(
            Host('gw2', mac=self.genMac(10, 10), ip=self.genIpforHost(10, 10), locat=[76, 40]))#第二个地面主机gw2
        # print("00000000000000000000000")
        # print(len(self.hostLinkToSwitches))
        # print(len(self.hostLinkToSwitches[0]))
        # for i in range(len(self.hostLinkToSwitches)):
        #     for j in range(len(self.hostLinkToSwitches[i])):
        #         print(self.hostLinkToSwitches[i][j].name,self.hostLinkToSwitches[i][j].ipAddress)
        # print("00000000000000000000000")
        self.groud_ending_host.append(
            Host('u1', mac=self.genMac(7,7),ip=self.genIpforHost(7,7),locat=[116,40]))  #beijing  ground station  地面终止站
        self.groud_ending_host.append(
            Host('u2', mac=self.genMac(8, 8), ip=self.genIpforHost(8, 8), locat=[75, 39])) #wuqia

    def printHostInf(self):
        for i in range(len(self.hostLinkToSwitches)): #每个平面
            for j in range(len(self.hostLinkToSwitches[i])): #每个平面上的卫星
                print(self.hostLinkToSwitches[i][j].name, self.hostLinkToSwitches[i][j].macAddress,
                     self.hostLinkToSwitches[i][j].ipAddress) #打印相关信息
    def genLinkInDetail(self,sw1,sw2,p1,p2): #两个交换机之间的详细信息
        a_link=DetailedLink(sw1,sw2,p1,p2)
        return  a_link
    def printLinks(self):
        print('Number of links:', len(self.linksInfo))  #打印总的链路数
        for i in range(len(self.linksInfo)):
            print(self.linksInfo[i].sw1, self.linksInfo[i].sw2, self.linksInfo[i].p1, self.linksInfo[i].p2)  #打印每个链路的信息
    def printPorts(self,i,j):
        for s in range(len(self.satSwitches[i][j].ports)):
            print(self.satSwitches[i][j].ports[s].portNum,self.satSwitches[i][j].ports[s].deviceName) #打印每个交换机的每个端口详情(端口号和拥有端口的设备名称)
    def genLink(self):
        print("3333333333333")

        # s11 link s21 in port4  s21 link s11 in port5 (s11,s21,2,3)(s11,s18,4,5)
        for i in range(self.planeNum - 1):
            for j in range(self.satPerplane):
                self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][j].name, 4) #该交换机的4号端口链接下一个平面的交换机
                self.satSwitches[i + 1][j].addLink1(self.satSwitches[i][j].name, 5) #下一个平面交换机的5号端口链接该交换机
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i + 1][j].name,
                                                           4,
                                                           5))
                # self.switches[i][j].addLink(self.switches[i+1][j])
                # self.switches[i+1][j].addLink(self.switches[i][j])
            
        # s12 link s21 in port6 s21 link s12 in port7
        # s13 link s22 in port6 s22 link s13 in port7
        for i in range(self.planeNum-1):
            for j in range(self.satPerplane):
                if j!=0:
                    self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][j-1].name, 6)
                    self.satSwitches[i + 1][j-1].addLink1(self.satSwitches[i][j].name, 7)
                    self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                               self.satSwitches[i + 1][j-1].name,
                                                               6,
                                                               7))
                else:
                    self.satSwitches[i][j].addLink1(self.satSwitches[i + 1][self.satPerplane-1].name, 6)
                    self.satSwitches[i + 1][self.satPerplane-1].addLink1(self.satSwitches[i][j].name, 7)
                    self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                               self.satSwitches[i + 1][self.satPerplane-1].name,
                                                               6,
                                                               7))
        # s11 link s12 in port8 s12 link s11 in port9
        for i in range(self.planeNum):
            for j in range(self.satPerplane - 1):
                self.satSwitches[i][j].addLink1(self.satSwitches[i][j + 1].name, 8)
                self.satSwitches[i][j + 1].addLink1(self.satSwitches[i][j].name, 9)
                self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][j].name,
                                                           self.satSwitches[i][j + 1].name,
                                                           8,
                                                           9))
            self.satSwitches[i][0].addLink1(self.satSwitches[i][self.satPerplane - 1].name, 9)
            self.satSwitches[i][self.satPerplane - 1].addLink1(self.satSwitches[i][0].name, 8)
            self.linksInfo.append(self.genLinkInDetail(self.satSwitches[i][0].name,
                                                       self.satSwitches[i][self.satPerplane - 1].name,
                                                       9,
                                                       8))



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


    def transP2T(self,plane,sat): #(1,1)->9
        number=plane*8+sat  
        return number
    def transT2P(self,number):#s12->[0,1]->1 #s11 0 #s13 2 #s23 
        p=[]
        p.append(int(number[1])-1)
        p.append(int(number[2])-1)
        t=self.transP2T(p[0],p[1])
        return t
    def genLinkMap(self):
        print("4444444444")
        for i in range(self.total):
            self.linkMap[i][i]=0 #先0
            self.portMap[i][i]=0 
        for i in range(len(self.linksInfo)):
            sw1=self.transT2P(self.linksInfo[i].sw1)
            sw2 = self.transT2P(self.linksInfo[i].sw2)
            #print(sw1,sw2)
            self.linkMap[sw1][sw2]=1 #意味两个交换机相连
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
                        if k.portNum == 4 or k.portNum == 6:
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
                    self.roads_nodesTran[i][j]=[_MAX]
                else:
                    tp_matrix=dijkstra_path(self.actual_map,i)
                    road=tp_matrix.find_shortestPath(j) # i到j的最短跳数
                    self.roads_nodesTran[i][j]=road
                    # road_l=road[str(j)]
                    # road_l.append(j)
                    # self.roads_nodesTran[i][j] =road_l
                    # print(self.roads_nodesTran[i][j])
        for i in range(len(self.roads_nodesTran)):
            for j in range(len(self.roads_nodesTran[i])):
                print(self.roads_nodesTran[i][j])
        hopsnum = []
        for i in range(len(self.roads_nodesTran)):
            for j in range(len(self.roads_nodesTran[i])):
                if self.roads_nodesTran[i][j]!=[_MAX]:
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
                            # tp_portTran.append(1)
                            continue
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
                    continue
                    # tp_portTran.append(1)
                self.roads_portTran[i][j]=tp_portTran

        for i in range(len(self.roads_portTran)):
            for j in range(len(self.roads_portTran[i])):
                if self.roads_portTran[i][j] != [_MAX]:
                # if len(self.roads_portTran[i][j])!=0:
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

        for i in range(len(self.gw_host)):
            LocatDict[self.gw_host[i].ipAddress] = self.gw_host[i].locat
            data = [self.gw_host[i].ipAddress, self.gw_host[i].locat[0],
                    self.gw_host[i].locat[1], self.gw_host[i].name]
            load_location.add_db("gw", data)
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
        print(topo.switches(sort=False))

        net=Mininet(topo=topo,
                    host=P4Host,
                    switch=P4RuntimeSwitch
                    )


        net.start()
        # for sw in net.switches:
        #     sw.cmd('tail -f /log/%s.log > %s.log &'%(sw.name,sw.name))
        # argvopts ='-D -o UseDNS=no -u0'
        # sshd.sshd(net, opts=argvopts)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        self.genFlowtable()
        subprocess.call("sh load_flow_table_for_sw.sh",shell=True)
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



        CLI(net,script='program2.txt')

        CLI(net)



        net.stop()
        os.remove('load_flow_table_for_sw.sh')
        os.remove('location.db')
        # os.removedirs('sat_log')
    def genFlowtable(self):
        with open('load_flow_table_for_sw.sh','a') as file:
            for i in range(len(self.satSwitches)):
                for j in range(len(self.satSwitches[i])):
                    cmd="simple_switch_CLI --thrift-port "+str(self.satSwitches[i][j].thriftPort)+" < flow_table/tunnel_table.txt \n"
                    cmd1 = "simple_switch_CLI --thrift-port " + str(self.satSwitches[i][j].thriftPort) + " < flow_table/ipv4_table.txt \n"
                    file.writelines(cmd)
                    file.writelines(cmd1)
            for i in range(len(self.ground_gw)):
                cmd = "simple_switch_CLI --thrift-port " + str(self.ground_gw[i].thriftPort) + " < flow_table/tunnel_table.txt \n"
                cmd1 = "simple_switch_CLI --thrift-port " + str(self.ground_gw[i].thriftPort) + " < flow_table/ipv4_table.txt \n"
                file.writelines(cmd)
                file.writelines(cmd1)

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
