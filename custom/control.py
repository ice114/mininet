#!/usr/bin/env python
# -*- coding:utf-8 -*-

from device import Switch, Host,Device
#from routeFinding import RouteFinding
from switchRuntime import SwitchRuntime
from topoMaker import TopoMaker


import copy
import time
import datetime
from collections import Counter
_ = float('inf')

class Ctrl(object):
    def __init__(self, switchGraph, hostList, qdepth, qrate):
        self.switchGraph = copy.deepcopy(switchGraph)
        self.graph = switchGraph
        self.vertexNum = len(switchGraph)
        self.hostList = hostList
        self.hostNum = Counter(self.hostList)[1]
        self.switchList = [1] * self.vertexNum
        self.hosts = []
        self.switches = []
	self.links_ports_map = []
        self.kind_of_switches = [] 
        self.linkCounter_sw2sw = [] 
        self.linkCounter_sw2h = [] 
        self.portSum_sw=[0]*self.vertexNum
        self.portSum_h=[0]*self.vertexNum
    def linksConvePorts(self):
        for i in range(len(self.graph)):
            for j in range(i+1,len(self.graph)):
                if self.graph[i][j] == 1:
                    self.links_ports_map.append([i,j])
        return None
    def genDevice(self):
        for i in range(self.vertexNum):
            thriftPort = 9090 + i
            
            if self.hostList[i] == 1:
                self.switches.append(
                Switch('s' + str(i), thriftPort, SwitchRuntime(thriftPort=thriftPort),'Leaf'))
                self.hosts.append(
                    Host('h' + str(i), self.genMac(i), self.genIp(i), True))
                self.kind_of_switches.append((i,'Leaf'))
            else:
                self.switches.append(
                Switch('s' + str(i), thriftPort, SwitchRuntime(thriftPort=thriftPort),'Spine'))
                self.hosts.append(None)
                self.kind_of_switches.append((i,'Spine'))
    def genLinks(self):

        for i in range(self.vertexNum):
            for j in range(i + 1, self.vertexNum):
                if self.graph[i][j] != _:
                    self.switches[i].addLink('s' + str(j))
                    self.switches[j].addLink('s' + str(i))
                    self.linkCounter_sw2sw.append((i,j,self.kind_of_switches[j][1]))
                    self.portSum_sw[i]+=1
                    self.linkCounter_sw2sw.append((j,i,self.kind_of_switches[i][1]))
                    self.portSum_sw[j]+=1
        for i in range(self.vertexNum):
            if self.hostList[i] == 1:
                self.hosts[i].addLink('s' + str(i))###这里感觉有问题！数组无函数
                self.switches[i].addLink('h' + str(i))
                self.linkCounter_sw2h.append((i,self.genIp(i)))
                self.portSum_sw[i]+=1
                self.portSum_h[i]+=1
    def genMac(self, id):

        macPrefix = '00:01:00:00:00:'
        hexId = hex(id)[2:].upper()
        if len(hexId) == 1:
            hexId = '0' + hexId
        mac = macPrefix + hexId
        return mac

    def genIp(self, id, isOvs=False):

        if isOvs:
            ipPrefix = '192.168.8.'
        else:
            ipPrefix = '10.0.0.'
        ip = ipPrefix + str(id + 100)
        return ip

    def makeTopo(self):

        switchPath = 'simple_switch'
        jsonPath = './basic.json'
        self.topoMaker = TopoMaker(switchPath, jsonPath, self)
        self.topoMaker.cleanMn()
        self.topoMaker.genMnTopo()
        for i, switch in enumerate(self.switches):
            switch.runtime.makeThriftLink(self.qdepth, self.qrate)


    def start(self):
        self.linksConvePorts()
        self.genDevice()
        self.genLinks()
        self.makeTopo()

if __name__ == '__main__':
    graphOfSwitch = [          #小规模实验拓扑4x4s-l结构
        [0, _, _, _, 1, 1, 1, 1],
        [_, 0, _, _, 1, 1, 1, 1],
        [_, _, 0, _, 1, 1, 1, 1],
        [_, _, _, 0, 1, 1, 1, 1],
        [1, 1, 1, _, 0, _, _, _],
        [1, 1, 1, _, _, 0, _, _],
        [1, 1, 1, _, _, _, 0, _],
        [1, 1, 1, _, _, _, _, 0],
    ]
    hostList = [0, 0, 0, 0, 1, 1, 1, 1]
    app = Ctrl(graphOfSwitch, hostList,4000,2000)
    app.start()
