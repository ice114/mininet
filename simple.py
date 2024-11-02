from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
net = Mininet(link=TCLink)

# Creating nodes in the network.

c0 = net.addController()

h0 = net.addHost('h0', ip='192.168.1.1/24', defaultRoute="via 192.168.1.2")

s0 = net.addSwitch('s0')
s1 = net.addSwitch('s1')

h1 = net.addHost('h1', ip='192.168.1.2/24', defaultRoute="via 192.168.1.1")

# Creating links between nodes in network
net.addLink(s1, s0,delay='5ms')
net.addLink(h0, s0,delay='5ms')

net.addLink(h1, s1,delay='5ms')

# Configuration of IP addresses in interfaces
#
# h0.setIP(, 24)
#
# h1.setIP('192.168.1.2', 24)

net.start()
CLI(net)

net.stop()
