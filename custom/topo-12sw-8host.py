"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        layer1Switch1 = self.addSwitch( 's1' )
        layer1Switch2 = self.addSwitch( 's2' )
        layer1Switch3 = self.addSwitch( 's3' )
        layer1Switch4 = self.addSwitch( 's4' )
        layer2Switch1 = self.addSwitch( 's5' )
        layer2Switch2 = self.addSwitch( 's6' )
        layer2Switch3 = self.addSwitch( 's7' )
        layer2Switch4 = self.addSwitch( 's8' )
        layer3Switch1 = self.addSwitch( 's9' )
        layer3Switch2 = self.addSwitch( 's10' )
        layer3Switch3 = self.addSwitch( 's11' )
        layer3Switch4 = self.addSwitch( 's12' )

        s9Host1 = self.addHost( 'h1', ip='10.0.0.1')
        s9Host2 = self.addHost( 'h2', ip='10.0.0.2')
        s10Host1 = self.addHost( 'h3', ip='10.0.0.3')
        s10Host2 = self.addHost( 'h4', ip='10.0.0.4')
        s11Host1 = self.addHost( 'h5', ip='10.0.0.5')
        s11Host2 = self.addHost( 'h6', ip='10.0.0.6')
        s12Host1 = self.addHost( 'h7', ip='10.0.0.7')
        s12Host2 = self.addHost( 'h8', ip='10.0.0.8')
       
        

        # Add links
        self.addLink( layer1Switch1, layer2Switch1 )
        self.addLink( layer1Switch1, layer2Switch3 )
        self.addLink( layer1Switch2, layer2Switch1 )
        self.addLink( layer1Switch2, layer2Switch3 )
        self.addLink( layer1Switch3, layer2Switch2 )
        self.addLink( layer1Switch3, layer2Switch4 )
        self.addLink( layer1Switch4, layer2Switch2 )
        self.addLink( layer1Switch4, layer2Switch4 )

        self.addLink( layer2Switch1, layer3Switch1 )
        self.addLink( layer2Switch1, layer3Switch2 )
        self.addLink( layer2Switch2, layer3Switch1 )
        self.addLink( layer2Switch2, layer3Switch2 )
        self.addLink( layer2Switch3, layer3Switch3 )
        self.addLink( layer2Switch3, layer3Switch4 )
        self.addLink( layer2Switch4, layer3Switch3 )
        self.addLink( layer2Switch4, layer3Switch4 )

        self.addLink( layer3Switch1, s9Host1 )
        self.addLink( layer3Switch1, s9Host2 )
        self.addLink( layer3Switch2, s10Host1 )
        self.addLink( layer3Switch2, s10Host2 )
        self.addLink( layer3Switch3, s11Host1 )
        self.addLink( layer3Switch3, s11Host2 )
        self.addLink( layer3Switch4, s12Host1 )
        self.addLink( layer3Switch4, s12Host2 )


topos = { 'mytopo': ( lambda: MyTopo() ) }
