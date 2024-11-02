#!/usr/bin/env python
import sys
import time
import datetime
import timeit
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
avr_cal_time=0
count=0

hosts=[[1,'10.0.7.7'],[2,'10.0.8.8']]
gws=[[1,[116,40]],[2,[75, 39]]]

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
def transP2T(plane,sat): #(1,1)->9
        number=plane*8+sat
        return number

# def stopSNIFF(pkt):


def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)

def clean_tunnel_and_fw(pkt):
    iface = get_if()
    print("iface = "+ iface)
    new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)
    new_pkt = new_pkt / SourceRoute(bos=0x0800, port=3)
    new_pkt=new_pkt/pkt[IP]

    new_pkt.show2()
    sendp(new_pkt, iface=iface, verbose=False)

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
    if (int(gw_type[0]) == 10):
        print("d_gw is on the ground")
        bind_layers(Ether, myTunnel, type=0x1212)
        bind_layers(myTunnel, IP)
        iface = get_if()
        my_ip = get_if_addr('eth0')
        # print("my ip = "+my_ip)
        s_vni = search_vni(pkt.getlayer(IP).src)
        my_long, my_lati, s_ip = search_gw(s_vni)
        my_name = load_location.query_data("gw", my_ip)[0]
        # print(my_name)
        accept_sat = distance_calc.find_shortest_path(trans2ten(int(my_long)), trans2ten(int(my_lati)))[-3:]
        sat_num = accept_sat.split('.')
        print("the accept sat is s" + str(sat_num))
        send_iface = (int(sat_num[0]) - 1) * 8 + int(sat_num[1]) + 1
        # print(send_iface)
        addr = socket.gethostbyname('10.0.255.255')
        new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4626)
        new_pkt = new_pkt / myTunnel(t_src=my_ip, t_dst=d_gw_ip, VNI=d_vni, s_long=my_long, s_lati=my_lati,
                                     d_long=d_long, d_lati=d_lati, sat=3)
        o_IP = pkt[IP]
        new_pkt = new_pkt / o_IP
        new_pkt.show2()
        # sendp(new_pkt, iface=str(iface), verbose=False)
        sat_fw(new_pkt)

def sat_fw(pkt):
    iface = get_if()
    my_ip = get_if_addr('eth0')
    Tunnel_info = pkt.getlayer(myTunnel)
    d_ip=Tunnel_info.t_dst
    d_gw=d_ip.split('.')
    if int(d_gw[0])==192:
        print("pkt needs to trans to sat gw")
        # d_long = Tunnel_info.d_long
        # d_lati = Tunnel_info.d_lati
        #
        # d_accept_sat = distance_calc.find_shortest_path(trans2ten(int(d_long)), trans2ten(int(d_lati)))[-3:]
        # d_sat = d_accept_sat.split('.')
        print("the d_accept sat is s" + d_gw[2]+d_gw[3])

        src_num = transP2T(int(my_ip[-3]) - 1, int(my_ip[-1]) - 1)
        dst_num = transP2T(int(d_gw[2]) - 1, int(d_gw[3]) - 1)
        if src_num==dst_num:
            new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)
            # new_pkt = new_pkt / SourceRoute(bos=0x1213, port=int(Tunnel_info.VNI+1))
            new_pkt = new_pkt / SourceRoute(bos=0x1213, port=0)
            new_pkt=new_pkt/pkt[myTunnel]
            sendp(new_pkt, iface=iface, verbose=False)
        else:
            sort = str([src_num, dst_num])
            print(sort)
            route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
            print(route)
            addr = socket.gethostbyname('10.0.255.255')
            # split_layers(myRegi, IP)
            # split_layers(Ether, myRegi,type=0x1234)
            # bind_layers(Ether, SourceRoute, type=0x1111)
            # bind_layers(SourceRoute, SourceRoute, bos=0)
            # bind_layers(SourceRoute, myRegi)
            # bind_layers(myRegi, IP)
            i = 0
            new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)

            for p in route:
                try:
                    new_pkt = new_pkt / SourceRoute(bos=0, port=int(p))
                    i = i + 1
                except ValueError:
                    pass
            # if pkt.haslayer(SourceRoute):
            #     pkt.getlayer(SourceRoute, i).bos = 0x1212
            # new_pkt = new_pkt / SourceRoute(bos=0x1213, port=int(Tunnel_info.VNI+1))
            new_pkt = new_pkt / SourceRoute(bos=0x1213, port=0)
            new_pkt = new_pkt / pkt[myTunnel]
            new_pkt.show2()
            print("send pkt with SR")
            sendp(new_pkt, iface=iface, verbose=False)
    elif int(d_gw[0])==10:
        print("pkt needs to trans to ground gw")
        d_long = Tunnel_info.d_long
        d_lati = Tunnel_info.d_lati

        d_accept_sat = distance_calc.find_shortest_path(trans2ten(int(d_long)), trans2ten(int(d_lati)))[-3:]
        d_sat = d_accept_sat.split('.')
        print("the d_accept sat is s" + str(d_sat))

        src_num = transP2T(int(my_ip[-3]) - 1, int(my_ip[-1]) - 1)
        dst_num = transP2T(int(d_accept_sat[-3]) - 1, int(d_accept_sat[-1]) - 1)
        if src_num == dst_num:
            new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)
            new_pkt = new_pkt / SourceRoute(bos=0x1213, port=int(Tunnel_info.VNI) + 1)
            new_pkt = new_pkt / pkt[myTunnel]
            sendp(new_pkt, iface=iface, verbose=False)
        else:
            sort = str([src_num, dst_num])
            print(sort)
            route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
            print(route)
            addr = socket.gethostbyname('10.0.255.255')
            # split_layers(myRegi, IP)
            # split_layers(Ether, myRegi,type=0x1234)
            # bind_layers(Ether, SourceRoute, type=0x1111)
            # bind_layers(SourceRoute, SourceRoute, bos=0)
            # bind_layers(SourceRoute, myRegi)
            # bind_layers(myRegi, IP)
            i = 0
            new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)

            for p in route:
                try:
                    new_pkt = new_pkt / SourceRoute(bos=0, port=int(p))
                    i = i + 1
                except ValueError:
                    pass
            # if pkt.haslayer(SourceRoute):
            #     pkt.getlayer(SourceRoute, i).bos = 0x1212
            new_pkt = new_pkt / SourceRoute(bos=0x1213, port=int(Tunnel_info.VNI + 1))
            new_pkt = new_pkt / pkt[myTunnel]
            new_pkt.show2()
            print("send pkt with SR")
            sendp(new_pkt, iface=iface, verbose=False)
def handle_pkt(pkt):
    print("get a pkt")
    # pkt.show2()
    ether = pkt.getlayer(Ether)
    if ether.type==0x0800:
        add_tunnel_and_fw(pkt)
    elif ether.type == 0x1212:
        print("get a tunnel packet")
        sat_fw(pkt)
    elif ether.type ==0x1213:
        clean_tunnel_and_fw(pkt)
    sys.stdout.flush()

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
class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 16),
                   BitField("port", 0, 16)]

bind_layers(Ether,myTunnel,type=0x1212)
bind_layers(Ether,myTunnel,type=0x1213)
bind_layers(Ether,IP,type=0x800)
bind_layers(Ether,IP,type=0x801)
bind_layers(myTunnel, IP)


bind_layers(Ether, SourceRoute, type=0x1111)
bind_layers(SourceRoute, SourceRoute, bos=0)

bind_layers(SourceRoute, myTunnel,bos=0x1213)

def main():
    # iface = 'eth0'
    # print "sniffing on %s" % iface
    print("sniffing")
    # sys.stdout.flush()
    # sniff(#iface=iface,
    #       prn=lambda x: handle_pkt(x),
    #       stop_filter=lambda x:stopSNIFF(x))
    sniff(prn=lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()