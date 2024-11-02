# -*- coding:utf-8 -*-

class Port(object):
    """
    描述交换机端口的类

    包含端口号和包含该端口的设备名称
    """

    def __init__(self, portNum, deviceName):
        self.portNum = portNum  # 端口号
        self.deviceName = deviceName  # 设备名称


class DetailedLink(object):
    def __init__(self, sw1, sw2, p1, p2):
        """
        DetailedLink类用于描述两个交换机之间的详细连接信息。
        sw1, sw2: 两个交换机的实例
        p1, p2: 分别是两个交换机的端口
        """
        self.sw1 = sw1
        self.sw2 = sw2
        self.p1 = p1
        self.p2 = p2


class Table(object):
    """
    描述交换机中的流表项的类

    包含名称、动作、键和值
    """
    def __init__(self, name, action, key, value):
        self.name = name  # 流表项名称
        self.action = action  # 动作
        self.key = key  # 键
        self.value = value  # 值


class Device(object):
    """
    描述网络中的设备的基类

    包含名称、端口列表和端口数量
    """

    def __init__(self, name):
        self.name = name  # 设备名称
        self.ports = []  # 端口列表
        self.portSum = 0  # 端口数量
        self.locat = [0, 0]  # 设备位置

    def addLink(self, deviceName):
        """
        添加一个连接到设备
        deviceName: 连接的设备名称
        """
        self.portSum = self.portSum + 1
        port = Port(self.portSum, deviceName)
        self.ports.append(port)

    def addLink1(self, deviceName, portName):
        """
        添加一个指定端口名的连接到设备
        deviceName: 连接的设备名称
        portName: 指定的端口名称
        """
        self.portSum += 1
        port = Port(portName, deviceName)
        self.ports.append(port)


class Switch(Device):
    """
    描述网络中的交换机的类（继承自Device类）

    包含流表、Thrift端口和Thrift运行时
    有两个动作：添加流表和清除流表
    """

    def __init__(self, name, thriftPort, ip, locat, runtime=None):
        super(Switch, self).__init__(name)
        self.name = name
        self.ipAddress = ip
        self.tables = []
        self.thriftPort = thriftPort
        self.runtime = runtime
        self.locat[0] = locat[0]
        self.locat[1] = locat[1]

    def addTable(self, name, action, key, value):
        """
        添加一个流表项
        name: 流表项名称
        action: 动作
        key: 键
        value: 值
        """
        self.tables.append(Table(name, action, key, value))

    def clearTable(self):
        """
        清除所有流表项
        """
        self.tables = []


class Host(Device):
    """
    描述网络中的主机的类（继承自Device类）

    包含MAC地址、IP地址和OpenVSwitch IP地址
    """

    def __init__(self, name, locat, mac='', ip='', ovsIp=''):
        super(Host, self).__init__(name)
        self.name = name
        self.macAddress = mac  # MAC地址
        self.ipAddress = ip  # IP地址
        self.ovsIpAddress = ovsIp  # OpenVSwitch IP地址
        self.locat[0] = locat[0]
        self.locat[1] = locat[1]


# 如果是主程序，则执行以下代码
if __name__ == '__main__':
    device = Host('hahah')  # 创建一个主机实例
    print(device.name)  # 打印主机的名称