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

location_dict={"10.0.4.4":[22,33]}
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


class DCS_Asn(Packet):
    fields_desc = [
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        BitField("d_longitude", 22, 16),
        BitField("d_lagitude", 33, 16),
        IPField("dst_satIP", str(0)),
    ]
# class m_type(Packet):
#     fields_desc = [
#         BitField("acc_state",0,16)
#     ]




def send_back(longitude,lagitude,dst_IP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    addr = socket.gethostbyname("10.0.255.255")
    pkt = pkt / IP(dst=addr) / DCS_Asn(longitude=longitude,lagitude=lagitude,dst_IP=dst_IP,d_longitude=location_dict[dst_IP][0],d_lagitude=location_dict[dst_IP][1])
    #pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
    print "dst_locate_info sending back"
def main():
    bind_layers(Ether, IP,type=0x1278)
    bind_layers(IP, DCS_Asn)
    iface = get_if()
    src_ip=get_if_addr('eth0')
    print src_ip
    src_addr=socket.gethostbyname(src_ip)
    print  src_addr
    addr = socket.gethostbyname("10.0.1.3")
    print addr
    print "broadcast send a ASN_packet"
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt/IP(dst=addr)/DCS_Asn(longitude=11,lagitude=22,dst_IP='10.0.4.4')
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    # print location_dict["10.0.4.4"][1]
    main()