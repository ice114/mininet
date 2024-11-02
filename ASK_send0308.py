#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump,bind_layers,get_if_addr,split_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *
from sw_LLA import load_location
def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "h22" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth42 interface"
        exit(1)
    return iface
def get_if2(): #broadcast interface list
    ifs = get_if_list()
    iface = get_if_list() # "h1-eth0"
    # print(len(get_if_list()))
    # for i in range(len(get_if_list())):
    #     print(get_if_list()[i])
    # print(get_if_list())
    # for i in range(len(get_if_list())):
    #         if "h22" in get_if_list()[i] or "eth0" in get_if_list()[i]:
    #             iface.append(get_if_list()[i])
    if not len(iface):
            print
            "Cannot find interface"
            exit(1)
    return iface
class myRegi(Packet):
    fields_desc =[
            IPField("u_srcIP",str(0)),
            BitField("longitude",11,16),
            BitField("lagitude",22,16),
            IPField("dst_satIP",str(0)),

           ]
# class m_type(Packet):
#     fields_desc = [
#         BitField("acc_state",0,16)
#     ]
class myAsk(Packet):
    fields_desc = [
        IPField("u_srcIP", str(0)),
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        IPField("dst_satIP", str(0)),
    ]
# bind_layers(m_type,Ether,acc_state=0)
# bind_layers(Ether,IP,type=0x1256)
# bind_layers(IP,myAsk)

def main():
    if len(sys.argv)<3:
        print "please check the dst_ip of package!"
        exit(1)
    type=sys.argv[1]
    dst_ip=sys.argv[2]
    iface = get_if2()
    # if type == "ask":
    #     src_ip=get_if_addr('eth0')
    #     print src_ip
    #     src_addr=socket.gethostbyname(src_ip)
    #     long=load_location.query_data("h",src_ip)[1]
    #     lati=load_location.query_data("h",src_ip)[2]
    #     print  src_addr
    #     addr = socket.gethostbyname("10.0.1.1")
    #     print addr
    #     print "broadcast send a ASK_packet"
    #     pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    #     pkt = pkt/IP(dst=addr)/ myAsk(u_srcIP=src_addr,longitude=long, lagitude=lati,dst_IP=dst_ip)
    #     pkt.show2()
    #     sendp(pkt, iface=iface, verbose=False)
    count=0
    if type=="ask":
        bind_layers(Ether, IP, type=0x1256)
        bind_layers(IP, myAsk)
        for i in range(len(iface)):
            src_ip = get_if_addr('eth0')
            print
            src_ip
            src_addr = socket.gethostbyname(src_ip)
            long = load_location.query_data("h", src_ip)[1]
            lati = load_location.query_data("h", src_ip)[2]
            print src_addr
            addr = socket.gethostbyname("10.0.1.1")
            print addr
            print
            "broadcast send a ASK_packet"
            pkt = Ether(src=get_if_hwaddr(iface[i]), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt / IP(dst=addr) / myAsk(u_srcIP=src_addr, longitude=long, lagitude=lati, dst_IP=dst_ip)
            #pkt.show2()
            sendp(pkt, iface=iface[i], verbose=False)
            #print(count)
            count+=1
    elif type=='regi':
        if len(sys.argv) < 4:
            print
            "please check the type of package!"
            exit(1)
        split_layers(IP, myAsk)
        bind_layers(Ether,IP,type=0x1234)
        bind_layers(IP,myRegi)
        # bind_layers(Ether, myRegi, type=0x1234)
        # bind_layers(myRegi, IP, regi_state=0)
        longitude=sys.argv[2]
        latitude=sys.argv[3]
        for i in range(len(iface)):
            src_ip = get_if_addr('eth0')
            print
            src_ip
            src_addr = socket.gethostbyname(src_ip)
            print
            src_addr
            addr = socket.gethostbyname('10.0.1.1')
            print
            addr
            print
            "broadcast send a regi_packet"
            pkt = Ether(src=get_if_hwaddr(iface[i]), dst='ff:ff:ff:ff:ff:ff')
            pkt = pkt / IP(dst=addr) / myRegi( u_srcIP=src_addr, longitude=int(longitude), lagitude=int(latitude))
            pkt.show2()
            sendp(pkt, iface=iface[i], verbose=False)
    else:
        print "errrrrrr"
        exit(1)
    print(count)
if __name__ == '__main__':
    main()