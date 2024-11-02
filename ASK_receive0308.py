#!/usr/bin/env python
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers,get_if_addr,split_layers
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *
#from ASN_send0308 import send_back
from sw_LLA import load_location
location_dict={"10.0.1.4":[22,33]}
def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth2" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
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
def send_back(longitude,lagitude,dst_IP,src_IP):
    split_layers(IP, myAsk)
    # bind_layers(Ether, IP, type=0x1278)
    bind_layers(IP, DCS_Asn)
    iface = get_if2()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    for i in range(len(iface)):
        pkt = Ether(src=get_if_hwaddr(iface[i]), dst='ff:ff:ff:ff:ff:ff',type=0x1278)
        addr = socket.gethostbyname(src_IP)
        dst_h_info=load_location.query_data("h",dst_IP)
        pkt = pkt / IP(dst=addr) / DCS_Asn(longitude=longitude,lagitude=lagitude,dst_IP=dst_IP,d_longitude=trans2ten(dst_h_info[1]),d_lagitude=trans2ten(dst_h_info[2]))
        pkt.show2()
        sendp(pkt, iface=iface[i], verbose=False)
        print "dst_locate_info sending back"
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
    if myAsk in pkt:
        # split_layers(IP,myRegi)
        # split_layers(Ether, IP)
        #bind_layers(Ether, IP)
        # bind_layers(IP, myAsk)
        print "got a ask packet"
        my_ask = pkt.getlayer(myAsk)
        # longitude = my_ask.longitude
        # lagitude = my_ask.lagitude
        # d_ip = my_ask.dst_IP
        pkt.show2()
        sys.stdout.flush()
        #cancel_bind()
        #send_back(longitude, lagitude, d_ip)
    elif myRegi in pkt:
    #else:

        #split_layers(IP,myAsk)
        # split_layers(Ether, IP)
        #bind_layers(Ether, IP)
        #bind_layers(IP,myRegi)
        pkt.show2()
        sys.stdout.flush()
    # #    hexdump(pkt)
def cancel_bind():
    split_layers(IP, myAsk)
    #bind_layers(Ether, IP, type=0x1278)
    bind_layers(IP, DCS_Asn)
def stopSNIFF(pkt):
    if myAsk in pkt:
         pkt.show2()
         my_ask = pkt.getlayer(myAsk)
         longitude = my_ask.longitude
         lagitude = my_ask.lagitude
         d_ip = my_ask.dst_IP
         Ip=pkt.getlayer(IP)
         src_ip=Ip.src
         #split_layers(IP, myAsk)
         #split_layers(Ether, IP, type=0x1256)
         #bind_layers(Ether, IP, type=0x1278)
         #bind_layers(IP, DCS_Asn)
         send_back(longitude, lagitude, d_ip,src_ip)
         print "stopppppppppppppp"
         return True
    else:
        return  True
class myRegi(Packet):
    fields_desc =[
            IPField("u_srcIP",str(0)),
            BitField("longitude",11,16),
            BitField("lagitude",22,16),
            IPField("dst_satIP",str(0)),
           ]
def trans2ten(num):
    if abs(num)<2**15-1:
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
class myAsk(Packet):
    fields_desc = [
        IPField("u_srcIP", str(0)),
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        IPField("dst_satIP", str(0)),
    ]
class DCS_Asn(Packet):
    fields_desc = [
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        BitField("d_longitude", 22, 16),
        BitField("d_lagitude", 33, 16),
        IPField("dst_satIP", str(0)),
    ]

bind_layers(Ether, IP)
bind_layers(IP, myAsk)
#bind_layers(IP, myRegi)
def main():
    # bind_layers(Ether, IP)
    # bind_layers(IP, myAsk)
    # iface = 'h11-eth2'
    # print "sniffing on %s" % iface
    print("sniff on every interface")
    sys.stdout.flush()
    sniff(#iface=iface,
          prn=lambda x: handle_pkt(x),
          stop_filter=lambda x:stopSNIFF(x))
    # sniff(iface=iface,
    #       prn=lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()