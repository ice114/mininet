#!/usr/bin/env python

"""
Create a network and start sshd(8) on each host.

While something like rshd(8) would be lighter and faster,
(and perfectly adequate on an in-machine network)
the advantage of running sshd is that scripts can work
unchanged on mininet and hardware.

In addition to providing ssh access to hosts, this example
demonstrates:

- creating a convenience function to construct networks
- connecting the host network to the root namespace
- running server processes (sshd in this case) on hosts
"""

import sys  # 导入系统相关的参数和函数

# 导入Mininet相关的模块
from mininet.net import Mininet  # 用于创建和管理Mininet网络
from mininet.cli import CLI  # Mininet命令行接口
from mininet.log import lg, info  # Mininet日志系统，用于设置日志级别和输出信息
from mininet.node import Node  # 表示Mininet中的节点
from mininet.topolib import TreeTopo  # 用于创建树形拓扑结构
from mininet.util import waitListening  # 用于等待服务监听端口

# 定义创建树形网络的函数
def TreeNet( depth=1, fanout=2, **kwargs ):
    "Convenience function for creating tree networks."
    topo = TreeTopo( depth, fanout )  # 创建树形拓扑结构
    return Mininet( topo, waitConnected=True, **kwargs )  # 创建并返回Mininet网络对象

# 定义将网络连接到根命名空间的函数
def connectToRootNS( network, switch, ip, routes ):
    """Connect hosts to root namespace via switch. Starts network.
     network: Mininet() network object
     switch: switch to connect to root namespace
     ip: IP address for root namespace node
     routes: host networks to route to"""
    # 在根命名空间中创建一个节点，并将其链接到交换机0
    root = Node( 'root', inNamespace=False )
    intf = network.addLink( root, switch ).intf1
    root.setIP( ip, intf=intf )
    # 启动包含根命名空间链接的网络
    network.start()
    # 为根命名空间添加路由
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )

# 定义启动网络并运行sshd服务的函数
# pylint: disable=too-many-arguments
def sshd( network, cmd='/usr/sbin/sshd', opts='-D',
          ip='10.123.123.1/32', routes=None, switch=None ):
    """Start a network, connect it to root ns, and run sshd on all hosts.
     ip: root-eth0 IP address in root namespace (10.123.123.1/32)
     routes: Mininet host networks to route to (10.0/24)
     switch: Mininet switch to connect to root namespace (s1)"""
    if not switch:
        switch = network[ 's1' ]  # 如果没有指定交换机，则使用s1
    if not routes:
        routes = [ '10.0.0.0/24' ]  # 如果没有指定路由，则默认为10.0.0.0/24
    connectToRootNS( network, switch, ip, routes )  # 连接到根命名空间
    for host in network.hosts:
        host.cmd( cmd + ' ' + opts + '&' )  # 在所有主机上启动sshd服务
    info( "*** Waiting for ssh daemons to start\n" )
    for server in network.hosts:
        waitListening( server=server, port=22, timeout=5 )  # 等待SSH服务监听端口

    info( "\n*** Hosts are running sshd at the following addresses:\n" )
    for host in network.hosts:
        info( host.name, host.IP(), '\n' )  # 输出主机的SSH服务地址
    info( "\n*** Type 'exit' or control-D to shut down network\n" )
    CLI( network )  # 启动Mininet CLI
    for host in network.hosts:
        host.cmd( 'kill %' + cmd )  # 停止sshd服务
    network.stop()  # 停止网络

# 如果是主程序，则执行以下代码
if __name__ == '__main__':
    lg.setLogLevel( 'info')  # 设置日志级别为info
    net = TreeNet( depth=1, fanout=4 )  # 创建一个深度为1，分支数为4的树形网络
    # 从命令行获取sshd参数或使用默认参数
    # useDNS=no -u0 to avoid reverse DNS lookup timeout
    argvopts = ' '.join( sys.argv[ 1: ] ) if len( sys.argv ) > 1 else (
        '-D -o UseDNS=no -u0' )
    sshd( net, opts=argvopts )  # 启动网络并运行sshd服务