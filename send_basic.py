#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import time

from scapy.all import sendp, send, get_if_list, get_if_hwaddr,get_if_addr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

from scapy.fields import *
from scapy.packet import bind_layers


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

class myTunnel(Packet):
    fields_desc =[

            IPField("t_src",str(0)),
            IPField("t_dst", str(0)),
            BitField("VNI", 0, 8),
            BitField("s_long", 0, 8),
            BitField("s_lati",0,8),
            BitField("d_long", 0, 8),
            BitField("d_lati", 0, 8),
            BitField("sat", 0, 8),

           ]

bind_layers(Ether,myTunnel,type=0x1212)
bind_layers(myTunnel,IP)
def main():

    if len(sys.argv)<3:
        print 'pass 2 arguments: <destination> "<message>"'
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()
    my_ip = get_if_addr('eth0')
    print "sending on interface %s to %s" % (iface, str(addr))

    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x0800)
    # pkt = pkt / myTunnel(t_src='10.0.9.9', t_dst='10.0.10.10', VNI=2, s_long=11, s_lati=11, d_long=11,
    #                              d_lati=11, sat=0)
    pkt = pkt /IP(src=my_ip,dst=addr) / UDP(dport=4321, sport=1234) / sys.argv[2]
    pkt.show2()


    sendp(pkt, iface=iface, verbose=False)
    print(time.time())

if __name__ == '__main__':
    main()
