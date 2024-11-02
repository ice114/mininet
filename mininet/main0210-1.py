# 这是一个示例 Python 脚本。
# !/usr/bin/env python
# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import os
import threading

from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI
from p4_mininet import P4Host
from p4runtime_switch import P4RuntimeSwitch


# from para import *
# from topo_update import sat_linkstatus_update
# from sat_brd import sat_broadcast
# command="sudo mn -c"
# os.system("gnome-terminal -e 'bash -c \"%s; exec bash\"'"%command)


class MakeSatTopo(Topo):
    def __init__(self, orbit_num, sat_per_orbit, sw_path, json_path, **opts):
        Topo.__init__(self, **opts)  # 拓扑初始化

        self.Sat_sws = []
        self.Sat_location = []
        self.Sat_graph = []
        self.Sat_dict = {}
        self.Sat_map = {}

        device_id = 1
        thrift_port = 9090

        for i in range(orbit_num):
            self.Sat_sws.append([])
            self.Sat_location.append([])
            for j in range(sat_per_orbit):
                sat = self.addSwitch('o%d_s%d' % (i + 1, j + 1),
                                     sw_path=sw_path,
                                     json_path=json_path,
                                     thrift_port=thrift_port,
                                     device_id=device_id,
                                     pcap_dump=False)
                h = self.addHost('s%d%d' % (i + 1, j + 1))

                self.Sat_sws[i].append(sat)
                self.Sat_location[i].append(0)
                self.Sat_dict[sat] = device_id
                self.Sat_map[sat] = 0

                device_id += 1
                thrift_port += 1
        for i in range(orbit_num - 1):
            for j in range(sat_per_orbit):  # 异轨同标号sat相连（0轨和5轨不连，反向缝）
                self.addLink(self.Sat_sws[i][j], self.Sat_sws[i + 1][j])
        for i in range(orbit_num):  # 同轨sat环向相连
            for j in range(sat_per_orbit - 1):
                self.addLink(self.Sat_sws[i][j], self.Sat_sws[i][j + 1])
            self.addLink(self.Sat_sws[i][0], self.Sat_sws[i][sat_per_orbit - 1])

        for i in range(orbit_num):  # （轨道，sat标号）对应satID ----（0，0）：0，   （4，5）：20
            for j in range(sat_per_orbit):
                self.Sat_dict[(i, j)] = i * orbit_num + j * sat_per_orbit


class TopoMaker(object):
    def __init__(self, sw_path, json_path, **opts):
        def gen_topo3():
            topo = testtopo(sw_path=sw_path, json_path=json_path)
            net = Mininet(topo=topo,
                          host=P4Host,
                          switch=P4RuntimeSwitch,
                          controller=None)
            net.start()
            CLI(net)
            net.stop()


class testtopo(Topo):
    def __init__(self, **opts):
        Topo.__init__(self, **opts)

        a = self.addSwitch('s1')
        b = self.addSwitch('s2')
        c = self.addHost('h1')
        d = self.addHost('h2')
        self.addLink(a, b)
        self.addLink(a, c)
        self.addLink(b, d)


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


def gen_topo():
    def __init__(self, orbit_num, sat_per_orbit, sw_path, json_path):
        orbit_num = 6
        sat_per_orbit = 8
        self.topo = MakeSatTopo(orbit_num,
                                sat_per_orbit,
                                sw_path,
                                json_path)

        net = Mininet(topo=self.topo,
                      host=P4Host,
                      switch=P4RuntimeSwitch,
                      controller=None)

        link_info = self.topo.links(sort=True, withKeys=True, withInfo=True)
        print(link_info)
        net.start()
        CLI(net)
        net.stop()


def gen_topo2():
    orbit_num = 6
    sat_per_orbit = 8
    topo = MakeSatTopo(orbit_num, sat_per_orbit, sw_path, json_path)

    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4RuntimeSwitch,
                  controller=None)

    link_info = topo.links(sort=True, withKeys=True, withInfo=True)
    print(link_info)
    net.start()
    CLI(net)
    net.stop()


def gen_topo3():
    topo = testtopo()
    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4RuntimeSwitch,
                  controller=None)
    net.start()
    CLI(net)
    net.stop()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')
    os.system("sudo mn -c")
    gen_topo3()
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
