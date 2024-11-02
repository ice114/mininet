from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import  Node
from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch

import argparse
import os
from time import sleep
cwd = os.getcwd()
log_dir = "/home/fxy/Workspace/P4/mininet"
default_logs = os.path.join(cwd, 'logs')
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

args = parser.parse_args()

class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        sw_list = []
        sw_list2 =[]
        h_list =[]
        for s in range(n):
            switch = self.addSwitch('s'+str(s+1),
                                    sw_path=sw_path,
                                    json_path=json_path,
                                    thrift_port=thrift_port+s,
                                    pcap_dump=pcap_dump)
            if s<3:
                sw_list.append(switch)
            else:
                sw_list2.append(switch)
            host = self.addHost('h%d' % (s + 1),
                                ip="10.0.0.%d/24" % (s + 1),
                                mac='08:00:00:00:00:%02x' % (s+1))
            h_list.append(host)
            self.addLink(host, switch)
        for i in range(3):
            for j in range(3):
                self.addLink(sw_list[i],sw_list2[j])
def T2P(number):
    p=number//8
    n=number%8
    return p,n
def transP2T(plane,sat): #(1,1)->9
    number=plane*8+sat
    return number
class MakeSatSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump,designedTopo, **opts):
        Topo.__init__(self, **opts)
        self.nums=designedTopo.total
        self.host_list=[]
        self.host_name = []
        self.switch_list=[]
        self.switch_name=[]
        self.switch_h_list=[]
        self.switch_h_name=[]
        self.linkMap=designedTopo.linkMap
        self.link_h2s=[]
        self.link_s2s=[]
        self.host_num=0
        mode = args.mode

        for i in range(len(designedTopo.satSwitches)):
            tp_sws=[]
            tp_names=[]
            tp_hs = []
            tp_names_h = []
            for j in range(len(designedTopo.satSwitches[i])):
                sw=self.addSwitch(designedTopo.satSwitches[i][j].name,
                                sw_path=sw_path,
                               json_path=json_path,
                               thrift_port=designedTopo.satSwitches[i][j].thriftPort,
                               pcap_dump=pcap_dump,
                                  log_file="%s/%s.log" % (log_dir, designedTopo.satSwitches[i][j].name)
                                )
                h = self.addHost(name=designedTopo.hostLinkToSwitches[i][j].name,
                                 ip=designedTopo.hostLinkToSwitches[i][j].ipAddress,
                                 mac=designedTopo.hostLinkToSwitches[i][j].macAddress)
                # print(designedTopo.satSwitches[i][j].name,designedTopo.satSwitches[i][j].ipAddress,)
                tp_sws.append(sw)
                tp_names.append(designedTopo.satSwitches[i][j].name)
                tp_hs.append(h)
                tp_names_h.append(designedTopo.hostLinkToSwitches[i][j].name)
                self.addLink(sw,h)
            self.switch_list.append(tp_sws)
            self.switch_name.append(tp_names)
            self.switch_h_list.append(tp_hs)
            self.switch_h_name.append(tp_names_h)


        for i in range(len(designedTopo.groud_ending_host)):
            tp_hs=[]
            tp_hnames=[]
            #for j in range(len(designedTopo.hostLinkToSwitches[i])):
            print(designedTopo.groud_ending_host[i].name,designedTopo.groud_ending_host[i].ipAddress,designedTopo.groud_ending_host[i].macAddress)
            h=self.addHost(name=designedTopo.groud_ending_host[i].name,
                            ip=designedTopo.groud_ending_host[i].ipAddress,
                            mac=designedTopo.groud_ending_host[i].macAddress)
            self.host_num+=1
            #tp_hnames.append(designedTopo.hostLinkToSwitches[i].name)

            self.host_list.append(h)
            self.host_name.append(designedTopo.groud_ending_host[i].name)

        class DetailedLink(object):
            def __init__(self, sw1, sw2, p1, p2):
                self.sw1 = sw1
                self.sw2 = sw2
                self.p1 = p1
                self.p2 = p2

        for i in range(len(designedTopo.linksInfo)):
            l=DetailedLink(self.findSwitch(designedTopo.linksInfo[i].sw1),
                           self.findSwitch(designedTopo.linksInfo[i].sw2),
                           designedTopo.linksInfo[i].p1,
                           designedTopo.linksInfo[i].p2)
            self.link_s2s.append(l)
        for i in range(len(self.link_s2s)):
            self.addLink(self.link_s2s[i].sw1,self.link_s2s[i].sw2,self.link_s2s[i].p1,self.link_s2s[i].p2)

        # for i in range(len(self.host_list)):
        #     for j in range(len(self.switch_list)):
        #         for k in range(len(self.switch_list[j])):
        #             self.addLink(self.host_list[i],self.switch_list[j][k])
        #
        for i in range(len(designedTopo.linksInfo_h2s)):
            l=DetailedLink(self.findHost(designedTopo.linksInfo_h2s[i].sw1),
                           self.findSwitch(designedTopo.linksInfo_h2s[i].sw2),
                           designedTopo.linksInfo_h2s[i].p1,
                           designedTopo.linksInfo_h2s[i].p2)
            self.link_h2s.append(l)

        for i in range(len(self.link_h2s)):
            self.addLink(self.link_h2s[i].sw1,self.link_h2s[i].sw2,self.link_h2s[i].p1,self.link_h2s[i].p2)


    def findHost(self,name):
        for i in range(len(self.host_list)):
            #for j in range(len(self.host_list[i])):
                if self.host_name[i]==name:
                    return self.host_list[i]
    def findSwitch(self, name):
        for i in range(len(self.switch_list)):
            for j in range(len(self.switch_list[i])):
                if self.switch_name[i][j]==name:
                    return self.switch_list[i][j]





def main():
    setLogLevel('info')
    num_hosts = args.num_hosts
    mode = args.mode
    topo = SingleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            num_hosts)

    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4RuntimeSwitch,
                  controller = None)
    net.start()
    # sw_mac = ["00:aa:bb:00:00:%02x" % n for n in range(num_hosts)]
    # sw_addr = ["10.0.%d.1" % n for n in range(num_hosts)]
    # for n in range(num_hosts):
    #     h = net.get('h%d' % (n + 1))
    #     if mode == "l2":
    #         h.setDefaultRoute("dev eth0")
    #     else:
    #         h.setARP(sw_addr[n], sw_mac[n])
    #         h.setDefaultRoute("dev eth0 via %s" % sw_addr[n])
    # for n in range(num_hosts):
    #     h = net.get('h%d' % (n + 1))
    #     h.describe()
    # sleep(1)
    print("Ready !")
    CLI( net )
    #net.configLinkStatus("h11","s11",'down')
    net.stop()
def main1():
    print("111")
if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
