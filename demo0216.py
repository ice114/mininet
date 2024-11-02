from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from p4_mininet import P4Switch, P4Host
from p4runtime_switch import P4RuntimeSwitch

import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=6)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

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



def main():
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
    sw_mac = ["00:aa:bb:00:00:%02x" % n for n in range(num_hosts)]
    sw_addr = ["10.0.%d.1" % n for n in range(num_hosts)]
    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        if mode == "l2":
            h.setDefaultRoute("dev eth0")
        else:
            h.setARP(sw_addr[n], sw_mac[n])
            h.setDefaultRoute("dev eth0 via %s" % sw_addr[n])
    for n in range(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()
    sleep(1)
    print("Ready !")
    CLI( net )
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
