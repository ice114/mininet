#!/usr/bin/env python
import argparse
import datetime
import sys
from sw_LLA import load_location
from threading import Thread
import socket
import random
import struct
import argparse
import  time
from sw_LLA import load_location
from threading import Thread
data_count_send=0
data_count_rec=0
time_start=0
time_asn=0
time_data_start=0
time_data_end=0
ap_b_long=0
ap_b_lati=0
import distance_calc
from time import sleep
from distance_calc import find_shortest_path
from sw_LLA import load_location
from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump,bind_layers,get_if_addr,sniff
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *
hosts=[[1,'10.0.7.7'],[2,'10.0.8.8']]
gws=[[1,[116,40]],[2,[75, 39]]]
def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface
def update_sat_gw_locat():
    while True:
        data=load_location.query_data('sw','192.168.3.3')
        # print(data)
        # print(data[0])
        long=data[1]
        lati=data[2]
        gws[1][1][0]=long
        gws[1][1][1]=lati
        # print(gws[1])
        sleep(5)

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
bind_layers(Ether,myTunnel,type=0x1213)
bind_layers(Ether,IP,type=0x800)
bind_layers(Ether,IP,type=0x801)
bind_layers(myTunnel, IP)


def search_vni(s_ip):
    for i in range(len(hosts)):
        if hosts[i][1]==s_ip:
            vni=hosts[i][0]
            return vni
def search_gw(vni):
        if vni==1:
            gw_ip="10.0."+str(vni+8)+"."+str(vni+8)
            return gws[0][1][0],gws[0][1][1],gw_ip
        if vni==2:
            gw_ip="192.168.3.3"
            return gws[1][1][0],gws[1][1][1],gw_ip

def add_tunnel_and_fw(pkt):
    d_ip=pkt.getlayer(IP).dst
    d_vni=search_vni(d_ip)
    d_long,d_lati,d_gw_ip=search_gw(d_vni)
    gw_type=d_gw_ip.split('.')
    print(gw_type)
    if(int(gw_type[0])==192):
        print("d_gw is sat")
        bind_layers(Ether, myTunnel, type=0x1212)
        bind_layers(myTunnel, IP)
        iface = get_if()
        my_ip = get_if_addr('eth0')
        # print("my ip = "+my_ip)
        s_vni=search_vni(pkt.getlayer(IP).src)
        my_long,my_lati,s_ip=search_gw(s_vni)
        my_name=load_location.query_data("gw", my_ip)[0]
        # print(my_name)
        accept_sat = distance_calc.find_shortest_path(trans2ten(int(my_long)), trans2ten(int(my_lati)))[-3:]
        sat_num = accept_sat.split('.')
        print("the accept sat is s"+str(sat_num))
        send_iface = (int(sat_num[0]) - 1) * 8 + int(sat_num[1]) + 1
        # print(send_iface)
        addr = socket.gethostbyname('10.0.255.255')
        new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4626)
        new_pkt = new_pkt / myTunnel(t_src=my_ip,t_dst=d_gw_ip,VNI=d_vni,s_long=my_long,s_lati=my_lati,d_long=d_long,d_lati=d_lati,sat=3)
        o_IP=pkt[IP]
        new_pkt = new_pkt / o_IP
        new_pkt.show2()
        sendp(new_pkt, iface=str(iface), verbose=False)

def clean_tunnel_and_fw(pkt):
    iface = get_if()
    print("iface = "+ iface)
    new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x0801)
    new_pkt=new_pkt/pkt[IP]
    # new_pkt.show2()
    sendp(new_pkt, iface=iface, verbose=False)




def handle_pkt(pkt):
    # print("sniffing")
    global  data_count_rec,ap_b_lati,ap_b_long,time_data_end
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    rec_time=pkt.time
    ether=pkt.getlayer(Ether)

    if ether.type==0x0800:
        IPinfo = pkt.getlayer(IP)
        s_ip=IPinfo.src
        d_ip=IPinfo.dst
        add_tunnel_and_fw(pkt)
    elif pkt[Ether].type==4627:
        pkt.show2()
        clean_tunnel_and_fw(pkt)


def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)

def main1():
    print("loading vxlan")
    print("loading vmgw table")
    print("gateway_sniffing")
    # thread_for_update = Thread(target=update_sat_gw_locat(), daemon=True)
    # thread_for_update.start()
    sys.stdout.flush()
    sniff(  # iface=iface,
        prn=lambda x: handle_pkt(x))
if __name__ == '__main__':

    main1()