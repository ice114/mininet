#!/usr/bin/env python
import sys
import datetime
import struct
from sw_LLA import  load_location
import distance_calc
from distance_calc import find_shortest_path
from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers,get_if_addr
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *
from sw_LLA import load_location
import  time
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
        regi_info=pkt.getlayer(myRegi)
        print regi_info.u_srcIP

        load_location.alter_db("h",[regi_info.u_srcIP,regi_info.longitude,regi_info.lagitude])
    #    hexdump(pkt)
        sys.stdout.flush()
     if myAsk in pkt:

         print("got a ask packet",time.time())
         print("got a ask packet", datetime.datetime.now())

         pkt.show2()
         ask_info=pkt.getlayer(myAsk)
         print ask_info.dst_IP
         dst_locat=load_location.query_data("h",str(ask_info.dst_IP))[1:]

         Asn_forward(dst_locat,ask_info)
         print(time.time)

         #    hexdump(pkt)
         sys.stdout.flush()

def Asn_forward(dst_locat,ask_info):
    iface = get_if()
    bind_layers(Ether, myAsk, type=0x1278)
    bind_layers(myAsk, IP)
    src_ip = get_if_addr('eth0')
    print
    src_ip

    src_addr = socket.gethostbyname(src_ip)
    self_locat = load_location.query_data("h", src_addr)
    print(self_locat)
    accept_sat = distance_calc.find_shortest_path(int(self_locat[1]), int(self_locat[2]))[-3:]
    sat_num = accept_sat.split('.')
    dst_ip = ask_info.dst_IP

    # for i in sat_num:
    #     print(i)
    if sat_num[0] == '1':
        if sat_num[1] == '1':
            send_iface = 'eth' + str(int(sat_num[1]) - 1)
        else:
            send_iface = self_locat[0] + '-eth' + str(int(sat_num[1]) - 1)

    else:
        send_iface = self_locat[0] + '-eth' + str((int(sat_num[0]) - 1) * 8 + int(sat_num[1]) - 1)
    print(send_iface)
    print
    src_addr
    addr = socket.gethostbyname('10.0.255.255')
    print
    addr


    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4728)
    pkt = pkt / DCS_Asn(direction=0,longitude=ask_info.longitude, lagitude=ask_info.lagitude, dst_IP=dst_ip,d_longitude=dst_locat[0],d_lagitude=dst_locat[1])
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=str(send_iface), verbose=False)
    print("broadcast send a Asn_packet:", time.time())
    print("broadcast send a Asn_packet:", datetime.datetime.now())

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
class DCS_Asn(Packet):
    fields_desc = [
        BitField("direction", 0, 16),
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        BitField("d_longitude", 22, 16),
        BitField("d_lagitude", 33, 16),
        IPField("dst_satIP", str(0)),
    ]
bind_layers(Ether, myRegi,type=0x1234)
bind_layers(myRegi, IP)
bind_layers(Ether,myAsk,type=0x1256)
bind_layers(myAsk,IP)
bind_layers(Ether,DCS_Asn,type=0x1278)
bind_layers(DCS_Asn,IP)
def main():
    # iface = 'eth0'
    # print "sniffing on %s" % iface
    print("ground_sniffing")
    sys.stdout.flush()
    sniff(#iface=iface,
          prn=lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()