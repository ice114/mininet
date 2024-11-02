#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump,bind_layers,get_if_addr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *
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

class myRegi(Packet):
    fields_desc =[
            BitField("regi_state",0,16),
            IPField("u_srcIP",str(0)),
            BitField("longitude",11,16),
            BitField("lagitude",22,16),
            IPField("dst_satIP",str(0)),

           ]

bind_layers(Ether, myRegi,type=0x1234)
bind_layers(myRegi, IP)

def main():
    print "11111111111111111111"
    if len(sys.argv)<2:
        print "please check the type of package!"
        exit(1)
    type=sys.argv[1]
    iface = get_if()
    print "222222222222222222222"
    if type == "broadcast":
        src_ip=get_if_addr('eth0')
        print src_ip
        src_addr=socket.gethostbyname(src_ip)
        print  src_addr
        addr = socket.gethostbyname('10.0.255.255')
        print addr
        print "broadcast send a regi_packet"
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / myRegi(regi_state=0,u_srcIP=src_addr,longitude=11, lagitude=22)
        pkt = pkt / IP(dst=addr) / UDP(dport=4321, sport=1234)
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)
    else:
        print "errrrrrr"
        exit(1)

if __name__ == '__main__':
    main()