from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI
from p4_mininet import P4Host
from p4runtime_switch import P4RuntimeSwitch

sw_path ='/home/fxy/Workspace/P4/mininet/simple_switch_grpc'
json_path ='/home/fxy/Workspace/P4/tutorials/exercises/source_routing/build/source_routing.json'

class MakeSatTopo(Topo):
    def __init__(self, OrbitNum, SatPerPlane, sw_path, json_path, **opts):
        Topo.__init__(self, **opts)
        self.sats = []
        self.name = []
        t_p = 9090
        d_id = 1
        for i in range(OrbitNum):
            a_plane = []
            names = []
            for j in range(SatPerPlane):
                sat = self.addSwitch('s-' + str(i + 1) + '-' + str(j + 1),
                                     sw_path=sw_path,
                                     json_path=json_path,
                                     thrift_port=t_p,
                                     device_id=d_id,
                                     pcap_dump=False)
                names.append('s-' + str(i + 1) + '-' + str(j + 1))
                a_plane.append(sat)
                # print('add '+'s-'+str(i+1)+'-'+str(j+1))
                self.addHost('h-' + str(i + 1) + '-' + str(j + 1))
                # print('add '+'h-'+str(i+1)+'-'+str(j+1))
                d_id += 1
                t_p += 1
            self.sats.append(a_plane)
            self.name.append(names)

        print(len(self.sats[0]))
        print(len(self.sats))
        print(len(self.name))
        for i in range(OrbitNum - 1):
            for j in range(SatPerPlane):
                print(i, j, i + 1, j)
                self.addLink(self.sats[i][j], self.sats[i + 1][j])
        for i in range(OrbitNum):  # 同轨sat环向相连
            for j in range(SatPerPlane - 1):
                self.addLink(self.sats[i][j], self.sats[i][j + 1])
            self.addLink(self.sats[i][0], self.sats[i][SatPerPlane - 1])


def PerSat():
    topo = MakeSatTopo(OrbitNum=6, SatPerPlane=8, sw_path=sw_path, json_path=json_path)
    print(topo.hosts())
    net = Mininet(topo, host=P4Host, switch=P4RuntimeSwitch, controller=None)
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':

    PerSat()
