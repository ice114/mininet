#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *
from sw_LLA import load_location
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
     if myRegi in pkt:
        print "got a regi packet"
        pkt.show2()
        # regi_info=pkt.getlayer(myRegi)
        # print regi_info.u_srcIP
        #load_location.alter_db("h",[regi_info.u_srcIP,regi_info.longitude,regi_info.lagitude])
    #    hexdump(pkt)
        sys.stdout.flush()
     if myAsk in pkt:
         print
         "got a ask packet"
         pkt.show2()
         # regi_info=pkt.getlayer(myRegi)
         # print regi_info.u_srcIP
         # load_location.alter_db("h",[regi_info.u_srcIP,regi_info.longitude,regi_info.lagitude])
         #    hexdump(pkt)
         sys.stdout.flush()

class myAsk(Packet):
    fields_desc = [
        BitField("direction", 0, 16),
        IPField("u_srcIP", str(0)),
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        IPField("dst_satIP", str(0)),
    ]
class myRegi(Packet):
    fields_desc =[
            BitField("direction", 0, 16),
            IPField("u_srcIP",str(0)),
            BitField("longitude",11,16),
            BitField("lagitude",22,16),
            IPField("dst_satIP",str(0)),

           ]

bind_layers(Ether, myRegi,type=0x1234)
bind_layers(myRegi, IP)
bind_layers(Ether,myAsk,type=0x1256)
bind_layers(myAsk,IP)
def main():
    # iface = 'eth0'
    # print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(#iface=iface,
          prn=lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()