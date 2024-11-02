# 从 Mininet 导入必要的模块
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Node
from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch

import argparse  # 处理命令行参数
import os  # 处理文件和目录操作
from time import sleep  # 时间相关操作

# 获取当前工作目录
cwd = os.getcwd()
# 日志目录
log_dir = "/home/fxy/Workspace/P4/mininet"
# 默认日志目录
default_logs = os.path.join(cwd, 'logs')

# 设置命令行参数解析器
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

# 解析命令行参数
args = parser.parse_args()

# 定义一个单交换机拓扑类
class SingleSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n, **opts):
        # 初始化拓扑和默认选项
        Topo.__init__(self, **opts)
        sw_list = []  # 存储交换机列表
        sw_list2 = []  # 存储第二组交换机
        h_list = []  # 存储主机列表
        
        # 创建交换机和主机
        for s in range(n):
            # 添加交换机
            switch = self.addSwitch('s'+str(s+1),
                                    sw_path=sw_path,
                                    json_path=json_path,
                                    thrift_port=thrift_port+s,
                                    pcap_dump=pcap_dump)
            # 将交换机分组
            if s < 3:
                sw_list.append(switch)  # 第一组交换机
            else:
                sw_list2.append(switch)  # 第二组交换机
            
            # 添加主机
            host = self.addHost('h%d' % (s + 1),
                                ip="10.0.0.%d/24" % (s + 1),
                                mac='08:00:00:00:00:%02x' % (s+1))
            h_list.append(host)  # 将主机添加到列表
            # 连接主机与交换机
            self.addLink(host, switch)
        
        # 为前3个交换机和后面的交换机添加连接
        for i in range(3):
            for j in range(3):
                self.addLink(sw_list[i], sw_list2[j])

# 将平面编号与卫星编号转换为一个数字
def T2P(number):
    p = number // 8  # 计算平面编号
    n = number % 8  # 计算卫星编号
    return p, n

# 将平面和卫星编号转换为一个数字
def transP2T(plane, sat):  # (1,1)->9
    number = plane * 8 + sat  # 计算唯一编号
    return number

# 定义一个卫星交换机拓扑类
class MakeSatSwitchTopo(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, designedTopo, **opts):
        Topo.__init__(self, **opts)  # 初始化拓扑
        self.nums = designedTopo.total  # 拓扑中总的设备数量
        self.host_list = []  # 主机列表
        self.host_name = []  # 主机名称列表
        self.switch_list = []  # 交换机列表
        self.switch_name = []  # 交换机名称列表
        self.gw_list = []  # 网关列表
        self.gw_name = []  # 网关名称列表
        self.gw_h = []  # 网关主机列表
        self.switch_h_list = []  # 交换机主机列表
        self.switch_h_name = []  # 交换机主机名称列表
        self.linkMap = designedTopo.linkMap  # 拓扑的链接信息
        self.link_h2s = []  # 主机到交换机的链接
        self.link_s2s = []  # 交换机到交换机的链接
        self.host_num = 0  # 主机计数
        mode = args.mode  # 当前模式

        # 创建卫星交换机和主机
        for i in range(len(designedTopo.satSwitches)):
            tp_sws = []  # 当前卫星交换机列表
            tp_names = []  # 当前卫星交换机名称列表
            tp_hs = []  # 当前主机列表
            tp_names_h = []  # 当前主机名称列表
            
            for j in range(len(designedTopo.satSwitches[i])):
                # 添加卫星交换机
                sw = self.addSwitch(designedTopo.satSwitches[i][j].name,
                                    sw_path=sw_path,
                                    json_path=json_path,
                                    thrift_port=designedTopo.satSwitches[i][j].thriftPort,
                                    pcap_dump=pcap_dump)
                
                # 添加主机
                h = self.addHost(name=designedTopo.hostLinkToSwitches[i][j].name,
                                 ip=designedTopo.hostLinkToSwitches[i][j].ipAddress,
                                 mac=designedTopo.hostLinkToSwitches[i][j].macAddress)
                
                # 将交换机和主机添加到临时列表
                tp_sws.append(sw)
                tp_names.append(designedTopo.satSwitches[i][j].name)
                tp_hs.append(h)
                tp_names_h.append(designedTopo.hostLinkToSwitches[i][j].name)
                
                # 连接交换机和主机
                self.addLink(sw, h, 0, 0)
                
            # 将当前组的交换机和主机添加到主列表
            self.switch_list.append(tp_sws)
            self.switch_name.append(tp_names)
            self.switch_h_list.append(tp_hs)
            self.switch_h_name.append(tp_names_h)

        # 添加地面终端主机
        for i in range(len(designedTopo.groud_ending_host)):
            print("host:", len(designedTopo.groud_ending_host))
            tp_hs = []  # 当前终端主机列表
            tp_hnames = []  # 当前终端主机名称列表
            
            # 添加终端主机
            print(designedTopo.groud_ending_host[i].name,
                  designedTopo.groud_ending_host[i].ipAddress,
                  designedTopo.groud_ending_host[i].macAddress)
            h = self.addHost(name=designedTopo.groud_ending_host[i].name,
                             ip=designedTopo.groud_ending_host[i].ipAddress,
                             mac=designedTopo.groud_ending_host[i].macAddress)
            self.host_num += 1  # 主机计数增加
            
            # 将终端主机添加到主列表
            self.host_list.append(h)
            self.host_name.append(designedTopo.groud_ending_host[i].name)

        # 添加地面网关
        for i in range(len(designedTopo.ground_gw)):
            print("gw:", len(designedTopo.ground_gw))
            sw = self.addSwitch(designedTopo.ground_gw[i].name,
                                sw_path=sw_path,
                                json_path=json_path,
                                thrift_port=designedTopo.ground_gw[i].thriftPort,
                                pcap_dump=pcap_dump)
            self.gw_list.append(sw)  # 将网关交换机添加到列表
            self.gw_name.append(designedTopo.ground_gw[i].name)

        # 添加网关主机
        for i in range(len(designedTopo.gw_host)):
            h = self.addHost(name=designedTopo.gw_host[i].name,
                             ip=designedTopo.gw_host[i].ipAddress,
                             mac=designedTopo.gw_host[i].macAddress)
            self.gw_h.append(h)  # 将网关主机添加到列表

        # 定义一个详细链接类，用于存储交换机间的连接信息
        class DetailedLink(object):
            def __init__(self, sw1, sw2, p1, p2):
                self.sw1 = sw1  # 第一个交换机
                self.sw2 = sw2  # 第二个交换机
                self.p1 = p1  # 第一个交换机的端口
                self.p2 = p2  # 第二个交换机的端口

        # 连接网关与终端主机
        for i in range(len(self.host_list)):
            self.addLink(self.gw_list[i], self.host_list[i], 1, 1)

        # 连接网关与其他交换机和主机
        for i in range(len(self.gw_list)):
            gw_port = 2  # 网关的起始端口
            self.addLink(self.gw_list[i], self.gw_h[i], 0, 0)  # 连接网关与网关主机
            
            # 连接网关与卫星交换机
            for j in range(len(self.switch_list)):
                for k in range(len(self.switch_list[j])):
                    self.addLink(self.gw_list[i], self.switch_list[j][k], gw_port, i + 2)
                    gw_port += 1  # 网关端口递增

        # 添加交换机之间的连接
        for i in range(len(designedTopo.linksInfo)):
            l = DetailedLink(self.findSwitch(designedTopo.linksInfo[i].sw1),
                             self.findSwitch(designedTopo.linksInfo[i].sw2),
                             designedTopo.linksInfo[i].p1,
                             designedTopo.linksInfo[i].p2)
            self.link_s2s.append(l)  # 将链接信息添加到列表
        
        # 将交换机之间的连接添加到拓扑中
        for i in range(len(self.link_s2s)):
            self.addLink(self.link_s2s[i].sw1, self.link_s2s[i].sw2, self.link_s2s[i].p1, self.link_s2s[i].p2)

    # 根据主机名查找主机
    def findHost(self, name):
        for i in range(len(self.host_list)):
            if self.host_name[i] == name:
                return self.host_list[i]  # 返回对应的主机对象

    # 根据交换机名查找交换机
    def findSwitch(self, name):
        for i in range(len(self.switch_list)):
            for j in range(len(self.switch_list[i])):
                if self.switch_name[i][j] == name:
                    return self.switch_list[i][j]  # 返回对应的交换机对象

# 主函数
def main():
    setLogLevel('info')  # 设置日志级别为信息
    num_hosts = args.num_hosts  # 获取主机数量
    mode = args.mode  # 获取模式
    # 创建拓扑实例
    topo = SingleSwitchTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            num_hosts)

    # 创建 Mininet 网络实例
    net = Mininet(topo=topo,
                  host=P4Host,
                  switch=P4RuntimeSwitch,
                  controller=None)  # 不使用控制器
    net.start()  # 启动网络

    print("Ready !")  # 网络已准备好
    CLI(net)  # 启动 Mininet CLI
    net.stop()  # 停止网络

# 如果此脚本是主程序，则运行主函数
if __name__ == '__main__':
    setLogLevel('info')  # 设置日志级别为信息
    main()  # 执行主函数