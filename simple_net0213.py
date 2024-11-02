"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from p4_mininet import P4Host
from p4runtime_switch import P4RuntimeSwitch

sw_path ='/home/fxy/Workspace/P4/mininet/simple_switch_grpc'
json_path ='/home/fxy/Workspace/P4/tutorials/exercises/p4runtime/build/advanced_tunnel.json'
class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        s1 = self.addSwitch( 's1' )


        # Add links
        self.addLink( h1, s1 )
        self.addLink(h2,s1)


topo = MyTopo()
net1 = Mininet(topo, host=P4Host, switch=P4RuntimeSwitch)
net1.start()
CLI(net1)
net1.stop()