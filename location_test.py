#!/usr/bin/env python
import sys
import struct
import distance_calc
from distance_calc import find_shortest_path
from sw_LLA import load_location
from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers,get_if_addr,split_layers
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *
from sw_LLA import load_location
import distance_calc
from time import sleep




def start():
    src_ip = get_if_addr('eth0')
    while True:
        a=load_location.query_data("sw",src_ip)
        print(a)
        print(a[0],a[1],a[2])
        b=distance_calc.find_shortest_path(116,40)
        print(b)
        sleep(30)



def test():
    print("1111111111111")




if __name__ == '__main__':
    test()