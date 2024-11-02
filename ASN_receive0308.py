#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers,get_if_addr,split_layers
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]
def handle_pkt(pkt):

    if DCS_Asn in pkt:
        print "got a asn packet"
        pkt.show2()
        sys.stdout.flush()
        answer=pkt.getlayer(DCS_Asn)
        longitude=answer.d_longitude
        latitude=answer.d_lagitude
        print("answer:",trans2ten(int(longitude)),trans2ten(int(latitude)))
        #print("answer:",bin(longitude)&0xffff)
def trans2ten(num):
    if abs(num)<2**15-1:
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
class DCS_Asn(Packet):
    fields_desc = [
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        BitField("d_longitude", 22, 16),
        BitField("d_lagitude", 33, 16),
        IPField("dst_satIP", str(0)),
    ]
bind_layers(Ether,IP)
bind_layers(IP,DCS_Asn)
def main():
    iface = 'h22-eth42'
    #print "sniffing on %s" % iface
    print("sniff on all interfaces")
    sys.stdout.flush()

    sniff(iface=iface,
          prn=lambda x: handle_pkt(x))


if __name__ == '__main__':
    main()