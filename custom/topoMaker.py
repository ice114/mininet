#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mininet.net import Mininet
from mininet.topo import Topo
#from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import RemoteController, OVSSwitch
from p4_mininet import P4Switch, P4Host
#from topoMaker import TopoMaker
import os
import copy
#import datetime 

class MakeSwitchTopo(Topo):
    """
    Mapping the topology in controller to Mininet
    """

    def __init__(self, sw_path, json_path, app_topo, **opts):
        """
        Make Mininet Host, Switch and Link entity

        :param sw_path: switch path (use bmv2's simple_switch target in this case)
        :param json_path: a compiled JSON file from P4 code
        :param app_topo: the Ctrl class instance to get informatin
        """
        Topo.__init__(self, **opts)

        self.switchSum = len(app_topo.switches)
        self.hostSum = len(app_topo.hosts)

        self.mn_switches = []
        self.mn_hosts = []
        for i in range(self.switchSum):
            self.mn_switches.append(self.addSwitch(app_topo.switches[i].name,
                                                   sw_path=sw_path,
                                                   json_path=json_path,
                                                   thrift_port=app_topo.switches[i].thriftPort,
                                                   pcap_dump=False))
        # self.mn_switches.append(self.addSwitch('s999',
        #                                        cls=OVSSwitch))
        for i in range(self.hostSum):
            if app_topo.hosts[i] != None:
                self.mn_hosts.append(self.addHost(app_topo.hosts[i].name,
                                                  ip=app_topo.hosts[i].ipAddress + "/24",
                                                  # ip="192.168.126." + str(i+10) + "/24",
                                                  mac=app_topo.hosts[i].macAddress))
            else:
                self.mn_hosts.append(None)
        for i in range(self.switchSum):
            for j in range(app_topo.switches[i].portSum):
                deviceNum = int(
                    app_topo.switches[i].ports[j].deviceName[1:])
                if app_topo.switches[i].ports[j].deviceName.startswith('s'):
                    if i < deviceNum:
                        self.addLink(
                            self.mn_switches[i], self.mn_switches[deviceNum])
                else:
                    self.addLink(
                        self.mn_switches[i], self.mn_hosts[deviceNum])


class TopoMaker(object):
    """
    Make topology in Mininet
    """

    def __init__(self, switchPath, jsonPath, topoObj):
        """
        Initial topology maker

        :param sw_path: switch path (use bmv2's simple_switch target in this case)
        :param json_path: a compiled JSON file from P4 code
        :param topoObj: the Ctrl class instance to get informatin
        """
        self.topo = MakeSwitchTopo(switchPath, jsonPath, topoObj)
        self.topoObj = topoObj



    def genMnTopo2(self):
        """
        Launch Mininet topology and add some commands (like disable IPv6, open INT sender/packet client/INT parser) to host and switch & start OVS and ryu controller
        """
        #setLogLevel('debug')
        self.net = Mininet(topo=self.topo,
                           host=P4Host,
                           switch=P4Switch,
                           controller=None)
        controller_list = []
        # c = self.net.addController('mycontroller', controller=RemoteController, ip='192.168.126.129')
        c = self.net.addController('mycontroller', controller=RemoteController,ip = '127.0.0.1')
        print('hahahah mycontroller is started')
        controller_list.append(c)
        # self.net.switches[self.topo.switchSum].start(controller_list)
        #ovs = self.net.addSwitch('s999', cls=OVSSwitch)

        #hostIpList = [
            #host.ipAddress for host in self.topoObj.hosts if host is not None]

        #j = 0
        #for i in range(self.topo.hostSum):
            #if self.topo.mn_hosts[i] != None:
                #self.net.addLink(self.net.hosts[j], ovs)
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.all.disable_ipv6=1")
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.default.disable_ipv6=1")
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
                #name = self.topoObj.hosts[i].name
                #ipAddr = self.topoObj.hosts[i].ovsIpAddress
                #action = 'ip a a ' + ipAddr + '/24 dev ' + name + '-eth1'
                #self.net.hosts[j].cmd(action)
                #self.net.hosts[j].cmd('ifconfig')
                #j = j + 1

        #ovs.start(controller_list)

        self.net.start()
        
        num_hosts = 0
        for host in self.topoObj.hosts:
            if host != None:
                num_hosts +=1
        
        for n in xrange(num_hosts):
            h = self.net.get('h%d' % n)
            for host in self.topoObj.hosts:
                if host != None :
                    if str(host.name) != str(h):
                        h.setARP(host.ipAddress, host.macAddress)
            h.describe()
        print('--------------------------------------------------------')
        
        m=0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:
                packetReceiver = ' python ~/P4/gml-p41/multireceiveudp.py ' + '&'
                self.net.hosts[m].cmd(packetReceiver)
                m += 1
        
        hostList = [host.ipAddress for host in self.topoObj.hosts if host is not None]
        print('hostList = ',hostList)
        k=0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:
                hostListDelSelf = copy.deepcopy(hostList)
                hostListDelSelf.remove(self.topoObj.hosts[i].ipAddress)
                hostListStr = ' '.join(hostListDelSelf)
                packetSender = ' python ~/P4/gml-p41/multisendudp2.py ' + hostListStr + '&'
                print('oooooookkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                #print('k = %d.'%k)
                #print('hostListStr = ', hostListStr)
                self.net.hosts[k].cmd(packetSender)
                k += 1
                
        #print(threading.active_count())
                #print(k)
        #hostList = ['10.0.0.101','10.0.0.102']
        #hostListStr = ' '.join(hostList)
        #packetSender = ' python ~/P4/mlv2/send.py ' + hostListStr + '&'
        #self.net.hosts[0].cmd(packetSender)
        #packetSender0 = ' python ~/P4/mlv2/send_socket.py ' + '&'
        #self.net.hosts[0].cmd(packetSender0)
        #packetSender1 = ' python ~/P4/mlv2/send1.py ' + '&'
        #self.net.hosts[1].cmd(packetSender1)
        #packetSender2 = ' python ~/P4/mlv2/send2.py ' + '&'
        #self.net.hosts[2].cmd(packetSender2)
        #os.popen('ovs-vsctl add-port s999 ens38')
        # os.system('sh ~/P4_DC/SQControl.sh')
        
        #j = 0
        #for i in range(self.topo.hostSum):
            #if self.topo.mn_hosts[i] != None:

                #packetSender = ' python ~/P4/mlv1/send.py ' + \
                    #str(i) + ' &'
                #self.net.hosts[j].cmd(packetSender)

                #hostIpListDelSelf = copy.deepcopy(hostIpList)
                #hostIpListDelSelf.remove(self.topoObj.hosts[i].ipAddress)
                #hostIpListStr = ' '.join(hostIpListDelSelf)
                #packetClient = ' python ~/P4_DC/packet/packetClient.py ' + hostIpListStr + ' &'
                #self.net.hosts[j].cmd(packetClient)

                # intReceiver = '~/P4_DC/packet/receiveint > packet/logs/intParser' + \
                #     str(i) + '.txt &'

                #intReceiver = '~/P4_DC/packet/receiveint ' + \
                    #str(i) + ' >/dev/null &'
                #self.net.hosts[j].cmd(intReceiver)
                #j = j + 1
            
        # cmdd = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[10].ipAddress + ' &'
        # self.net.hosts[0].cmd(cmdd)

        # cmdd1 = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[0].ipAddress +' '+self.topoObj.hosts[1].ipAddress + ' &'
        # cmdd2 = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[2].ipAddress +' '+self.topoObj.hosts[3].ipAddress + ' &'
        # self.net.hosts[0].cmd(cmdd2)
        # self.net.hosts[1].cmd(cmdd2)
        # self.net.hosts[2].cmd(cmdd1)
        # self.net.hosts[3].cmd(cmdd1)

        # cli = CLI(self.net, script='actions.txt')

        #start CLI
        # cli = CLI(self.net)

        # for hostId, host in enumerate(self.topoObj.hosts):
        #     if host:
        #         ipAddr = host.ovsIpAddress
        #         name = host.name
        #         action = name + ' ip a a ' + ipAddr + '/24 dev ' + name + '-eth1'
        #         print(action)
        #         cli.default(action)
        #         cli.default(name + ' ifconfig')
        #         cli.default(
        #             name + ' python2 ~/P4_DC/packet/packetTrans.py ' + str(hostId) + ' & >> trans' + str(hostId) + '.log')
        #         # name + ' python2 ~/P4_DC/packet/packetTrans.py ' + str(hostId))
        #         # name + ' python2 ~/P4_DC/packet/packetTrans.py a b c')


    def genMnTopo(self):
        """
        Launch Mininet topology and add some commands (like disable IPv6, open INT sender/packet client/INT parser) to host and switch & start OVS and ryu controller
        """
        #setLogLevel('debug')
        self.net = Mininet(topo=self.topo,
                           host=P4Host,
                           switch=P4Switch,
                           controller=None)
        controller_list = []
        # c = self.net.addController('mycontroller', controller=RemoteController, ip='192.168.126.129')
        c = self.net.addController('mycontroller', controller=RemoteController,ip = '127.0.0.1')
        print('hahahah mycontroller is started')
        controller_list.append(c)
        # self.net.switches[self.topo.switchSum].start(controller_list)
        #ovs = self.net.addSwitch('s999', cls=OVSSwitch)

        #hostIpList = [
            #host.ipAddress for host in self.topoObj.hosts if host is not None]

        #j = 0
        #for i in range(self.topo.hostSum):
            #if self.topo.mn_hosts[i] != None:
                #self.net.addLink(self.net.hosts[j], ovs)
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.all.disable_ipv6=1")
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.default.disable_ipv6=1")
                #self.net.hosts[j].cmd(
                 #   "sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
                #name = self.topoObj.hosts[i].name
                #ipAddr = self.topoObj.hosts[i].ovsIpAddress
                #action = 'ip a a ' + ipAddr + '/24 dev ' + name + '-eth1'
                #self.net.hosts[j].cmd(action)
                #self.net.hosts[j].cmd('ifconfig')
                #j = j + 1

        #ovs.start(controller_list)

        self.net.start()
        
        num_hosts = 0
        for host in self.topoObj.hosts:
            if host != None:
                num_hosts +=1
        
        for n in xrange(num_hosts):
            h = self.net.get('h%d' % n)
            for host in self.topoObj.hosts:
                if host != None :
                    if str(host.name) != str(h):
                        h.setARP(host.ipAddress, host.macAddress)
            h.describe()
        print('--------------------------------------------------------')
        
        m=0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:
                packetReceiver = ' python ~/P4/gml-p41/multireceiveudp.py ' + '&'
                self.net.hosts[m].cmd(packetReceiver)
                m += 1
        
        hostList = [host.ipAddress for host in self.topoObj.hosts if host is not None]
        print('hostList = ',hostList)
        k=0
        for i in range(self.topo.hostSum):
            if self.topo.mn_hosts[i] != None:
                hostListDelSelf = copy.deepcopy(hostList)
                hostListDelSelf.remove(self.topoObj.hosts[i].ipAddress)
                hostListStr = ' '.join(hostListDelSelf)
                packetSender = ' python ~/P4/gml-p41/multisendudp.py ' + hostListStr + '&'
                #print('k = %d.'%k)
                #print('hostListStr = ', hostListStr)
                self.net.hosts[k].cmd(packetSender)
                k += 1
                
        #print(threading.active_count())
                #print(k)
        #hostList = ['10.0.0.101','10.0.0.102']
        #hostListStr = ' '.join(hostList)
        #packetSender = ' python ~/P4/mlv2/send.py ' + hostListStr + '&'
        #self.net.hosts[0].cmd(packetSender)
        #packetSender0 = ' python ~/P4/mlv2/send_socket.py ' + '&'
        #self.net.hosts[0].cmd(packetSender0)
        #packetSender1 = ' python ~/P4/mlv2/send1.py ' + '&'
        #self.net.hosts[1].cmd(packetSender1)
        #packetSender2 = ' python ~/P4/mlv2/send2.py ' + '&'
        #self.net.hosts[2].cmd(packetSender2)
        #os.popen('ovs-vsctl add-port s999 ens38')
        # os.system('sh ~/P4_DC/SQControl.sh')
        
        #j = 0
        #for i in range(self.topo.hostSum):
            #if self.topo.mn_hosts[i] != None:

                #packetSender = ' python ~/P4/mlv1/send.py ' + \
                    #str(i) + ' &'
                #self.net.hosts[j].cmd(packetSender)

                #hostIpListDelSelf = copy.deepcopy(hostIpList)
                #hostIpListDelSelf.remove(self.topoObj.hosts[i].ipAddress)
                #hostIpListStr = ' '.join(hostIpListDelSelf)
                #packetClient = ' python ~/P4_DC/packet/packetClient.py ' + hostIpListStr + ' &'
                #self.net.hosts[j].cmd(packetClient)

                # intReceiver = '~/P4_DC/packet/receiveint > packet/logs/intParser' + \
                #     str(i) + '.txt &'

                #intReceiver = '~/P4_DC/packet/receiveint ' + \
                    #str(i) + ' >/dev/null &'
                #self.net.hosts[j].cmd(intReceiver)
                #j = j + 1
            
        # cmdd = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[10].ipAddress + ' &'
        # self.net.hosts[0].cmd(cmdd)

        # cmdd1 = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[0].ipAddress +' '+self.topoObj.hosts[1].ipAddress + ' &'
        # cmdd2 = ' python ~/P4_DC/packet/packetClient.py ' + self.topoObj.hosts[2].ipAddress +' '+self.topoObj.hosts[3].ipAddress + ' &'
        # self.net.hosts[0].cmd(cmdd2)
        # self.net.hosts[1].cmd(cmdd2)
        # self.net.hosts[2].cmd(cmdd1)
        # self.net.hosts[3].cmd(cmdd1)

        # cli = CLI(self.net, script='actions.txt')

        #start CLI
        # cli = CLI(self.net)

        # for hostId, host in enumerate(self.topoObj.hosts):
        #     if host:
        #         ipAddr = host.ovsIpAddress
        #         name = host.name
        #         action = name + ' ip a a ' + ipAddr + '/24 dev ' + name + '-eth1'
        #         print(action)
        #         cli.default(action)
        #         cli.default(name + ' ifconfig')
        #         cli.default(
        #             name + ' python2 ~/P4_DC/packet/packetTrans.py ' + str(hostId) + ' & >> trans' + str(hostId) + '.log')
        #         # name + ' python2 ~/P4_DC/packet/packetTrans.py ' + str(hostId))
        #         # name + ' python2 ~/P4_DC/packet/packetTrans.py a b c')

    def getCLI(self):
        """
        Open Mininet CLI
        """
        CLI(self.net)

    def stopMnTopo(self):
        """
        Stop Mininet envirnoment
        """
        self.net.stop()

    def cleanMn(self):
        """
        Clean all mininet trace
        """
        os.system('sudo mn -c')
        os.system(
            'ryu-manager /usr/local/lib/python2.7/dist-packages/ryu/app/simple_switch.py 2>/dev/null >/dev/null &')
        pass


if __name__ == '__main__':
    # cannot test without ctlr.py
    print('hello world')
    pass
