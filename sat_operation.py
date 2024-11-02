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
h_dict={str([116,40]):1,str([75, 39]):2,str([122, 30]):3}

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
def send_regi_forward_btw_sats(u_srcIP,longitude,lagitude,dst_satIP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    src_num=transP2T(int(src_addr[-3])-1,int(src_addr[-1])-1)
    dst_num=transP2T(int(dst_satIP[-3])-1,int(dst_satIP[-1])-1)
    sort=str([src_num,dst_num])
    print(sort)
    route=load_location.query_data("SR",sort)[1][1:-1].split(', ')
    print(route)
    addr = socket.gethostbyname('10.0.255.255')
    # split_layers(myRegi, IP)
    # split_layers(Ether, myRegi,type=0x1234)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, SourceRoute, bos=0)
    # bind_layers(SourceRoute, myRegi)
    # bind_layers(myRegi, IP)
    i=0
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)

    for p in route:
        try:
            pkt = pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1234
    pkt = pkt / myRegi(direction=1,u_srcIP=u_srcIP, longitude=longitude, lagitude=lagitude,dst_satIP=dst_satIP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def send_ask_forward_btw_sats(u_srcIP,longitude,lagitude,dst_satIP,dst_IP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    src_num=transP2T(int(src_addr[-3])-1,int(src_addr[-1])-1)
    dst_num=transP2T(int(dst_satIP[-3])-1,int(dst_satIP[-1])-1)
    sort=str([src_num,dst_num])
    print(sort)
    route=load_location.query_data("SR",sort)[1][1:-1].split(', ')
    print(route)
    addr = socket.gethostbyname('10.0.255.255')
    # split_layers(myAsk, IP)
    # split_layers(Ether, myAsk,type=0x1256)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, SourceRoute, bos=0)
    # bind_layers(SourceRoute, myAsk)
    # bind_layers(myAsk, IP)
    i=0
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)

    for p in route:
        try:
            pkt = pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1256
    pkt = pkt / myAsk(direction=1,u_srcIP=u_srcIP, longitude=longitude, lagitude=lagitude,dst_satIP=dst_satIP,dst_IP=dst_IP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def send_ans_forward_btw_sats(ans_info,dst_satIP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    src_num = transP2T(int(src_addr[-3]) - 1, int(src_addr[-1]) - 1)
    dst_num = transP2T(int(dst_satIP[-3]) - 1, int(dst_satIP[-1]) - 1)
    sort = str([src_num, dst_num])
    print(sort)
    route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
    print(route)
    addr = socket.gethostbyname('10.0.255.255')
    # split_layers(myAsk, IP)
    # split_layers(Ether, myAsk,type=0x1256)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, SourceRoute, bos=0)
    # bind_layers(SourceRoute, myAsk)
    # bind_layers(myAsk, IP)
    i = 0
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)

    for p in route:
        try:
            pkt = pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1278
    pkt = pkt / DCS_Asn(direction=1, longitude=ans_info.longitude, lagitude=ans_info.lagitude, dst_IP=ans_info.dst_IP,
                      d_longitude=ans_info.d_longitude,d_lagitude=ans_info.d_lagitude)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def send_data_forward_btw_sats(data_info,dst_satIP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    src_num = transP2T(int(src_addr[-3]) - 1, int(src_addr[-1]) - 1)
    dst_num = transP2T(int(dst_satIP[-3]) - 1, int(dst_satIP[-1]) - 1)
    sort = str([src_num, dst_num])
    print(sort)
    route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
    print(route)
    Note1 = open('sat_log/route_length.txt', mode='a')
    Note1.writelines([str(route), "\n"])
    Note1.close()
    addr = socket.gethostbyname('10.0.255.255')
    # split_layers(myAsk, IP)
    # split_layers(Ether, myAsk,type=0x1256)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, SourceRoute, bos=0)
    # bind_layers(SourceRoute, myAsk)
    # bind_layers(myAsk, IP)
    i = 0
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)

    for p in route:
        try:
            pkt = pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1299
    pkt = pkt / myData(direction=1,d_longitude=data_info.d_longitude,d_lagitude=data_info.d_lagitude,dst_satIP=dst_satIP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    bf=time.time()*10000
    sendp(pkt, iface=iface, verbose=False)
    af=time.time()*10000
    send_data_btw_sats_3 = (bf+af)/2
    return send_data_btw_sats_3
def send_rdata_forward_btw_sats(data_info,dst_satIP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    src_num = transP2T(int(src_addr[-3]) - 1, int(src_addr[-1]) - 1)
    dst_num = transP2T(int(dst_satIP[-3]) - 1, int(dst_satIP[-1]) - 1)
    sort = str([src_num, dst_num])
    print(sort)
    route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
    print(route)
    Note1 = open('sat_log/route_length.txt', mode='a')
    Note1.writelines([str(route), "\n"])
    Note1.close()
    addr = socket.gethostbyname('10.0.255.255')
    # split_layers(myAsk, IP)
    # split_layers(Ether, myAsk,type=0x1256)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, SourceRoute, bos=0)
    # bind_layers(SourceRoute, myAsk)
    # bind_layers(myAsk, IP)
    i = 0
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)

    for p in route:
        try:
            pkt = pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1300
    pkt = pkt / replyData(direction=1,d_longitude=data_info.d_longitude,d_lagitude=data_info.d_lagitude,dst_satIP=dst_satIP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    bf=time.time()*10000
    sendp(pkt, iface=iface, verbose=False)
    af=time.time()*10000
    send_data_btw_sats_9 = (af+bf)/2
    return send_data_btw_sats_9


def regi_forward_to_ground(u_srcIP,longitude,lagitude,dst_satIP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    addr = socket.gethostbyname('10.0.255.255')
    src_addr = socket.gethostbyname(src_ip)
    # split_layers(myRegi, IP)
    # split_layers(Ether, myRegi, type=0x1234)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, myRegi,bos=0x1234)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)
    pkt = pkt / SourceRoute(bos=0x1234, port=8)
    pkt = pkt / myRegi(direction=1, u_srcIP=u_srcIP, longitude=longitude, lagitude=lagitude, dst_satIP=dst_satIP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def ask_forward_to_ground(u_srcIP,longitude,lagitude,dst_satIP,dst_IP):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    addr = socket.gethostbyname('10.0.255.255')
    src_addr = socket.gethostbyname(src_ip)
    # split_layers(myRegi, IP)
    # split_layers(Ether, myRegi, type=0x1234)
    # bind_layers(Ether, SourceRoute, type=0x1111)
    # bind_layers(SourceRoute, myAsk,bos=0x1256)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)
    pkt = pkt / SourceRoute(bos=0x1256, port=8)
    pkt = pkt / myAsk(direction=1, u_srcIP=u_srcIP, longitude=longitude, lagitude=lagitude, dst_satIP=dst_satIP,dst_IP=dst_IP)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def ans_forward_to_ground(ans_info):
    iface = get_if()
    src_ip = get_if_addr('eth0')
    addr = socket.gethostbyname('10.0.255.255')
    src_addr = socket.gethostbyname(src_ip)
    host_name=load_location.query_data1("h",[trans2ten(int(ans_info.longitude)),trans2ten(int(ans_info.lagitude))])[0]
    # print(host_name)
    port=int(host_name[1])+7
    # print(port)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)
    pkt = pkt / SourceRoute(bos=0x1278, port=port)
    pkt = pkt / DCS_Asn(direction=1, longitude=ans_info.longitude, lagitude=ans_info.lagitude,dst_IP=ans_info.dst_IP, dst_satIP=ans_info.dst_satIP,
                      d_longitude=ans_info.d_longitude,d_lagitude=ans_info.d_lagitude)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
def data_forward_to_ground(data_info):
    global avr_cal_time,count
    cal_start=time.time()
    iface = get_if()
    src_ip = get_if_addr('eth0')
    addr = socket.gethostbyname('10.0.255.255')
    src_addr = socket.gethostbyname(src_ip)
    # host_name=load_location.query_data1("h",[trans2ten(int(data_info.d_longitude)),trans2ten(int(data_info.d_lagitude))])[0]
    host_name=h_dict.get(str([trans2ten(int(data_info.d_longitude)),trans2ten(int(data_info.d_lagitude))]))
    # print(host_name)
    #port=int(host_name[1])+7
    port=host_name+7
    # print(port)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)
    pkt = pkt / SourceRoute(bos=0x1299, port=port)
    pkt = pkt / myData(direction=1, dst_satIP=data_info.dst_satIP,
                      d_longitude=data_info.d_longitude,d_lagitude=data_info.d_lagitude)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    bf=time.time()*10000
    sendp(pkt, iface=iface, verbose=False)
    af=time.time()*10000
    send_data_to_ground_5 = (bf+af)/2
    return send_data_to_ground_5

def rdata_forward_to_ground(data_info):
    global avr_cal_time,count
    cal_start=time.time()
    iface = get_if()
    src_ip = get_if_addr('eth0')
    addr = socket.gethostbyname('10.0.255.255')
    src_addr = socket.gethostbyname(src_ip)
    # host_name=load_location.query_data1("h",[trans2ten(int(data_info.d_longitude)),trans2ten(int(data_info.d_lagitude))])[0]
    host_name=h_dict.get(str([trans2ten(int(data_info.d_longitude)),trans2ten(int(data_info.d_lagitude))]))
    # print(host_name)
    #port=int(host_name[1])+7
    port=host_name+7
    # print(port)
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x1111)
    pkt = pkt / SourceRoute(bos=0x1300, port=port)
    pkt = pkt / replyData(direction=1, dst_satIP=data_info.dst_satIP,
                      d_longitude=data_info.d_longitude,d_lagitude=data_info.d_lagitude)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    bf=time.time()*10000
    sendp(pkt, iface=iface, verbose=False)
    af=time.time()*10000
    send_data_to_ground_11 =(bf+af)/2
    return send_data_to_ground_11

# def stopSNIFF(pkt):
def send_pkt_btw_sats(pkt,d_sat):
    iface = get_if()
    my_ip = get_if_addr('eth0')
    my_name = socket.gethostbyname(my_ip)
    src_num = transP2T(int(my_name[-3]) - 1, int(my_name[-1]) - 1)
    dst_num = transP2T(int(d_sat[-3]) - 1, int(d_sat[-1]) - 1)
    sort = str([src_num, dst_num])
    print(sort)
    route = load_location.query_data("SR", sort)[1][1:-1].split(', ')
    print(route)
    i = 0
    new_pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4369)

    for p in route:
        try:
            new_pkt = new_pkt / SourceRoute(bos=0, port=int(p))
            i = i + 1
        except ValueError:
            pass
    if pkt.haslayer(SourceRoute):
        pkt.getlayer(SourceRoute, i).bos = 0x1234
    new_pkt = new_pkt / pkt[myTunnel]/pkt[IP]
    pkt.show2()
    sendp(new_pkt, iface=iface, verbose=False)

def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
def handle_pkt(pkt):
     if pkt[Ether].type==0x1234:
         Tunnel_info = pkt.getlayer(myTunnel)

         bind_layers(Ether, myTunnel, type=0x1234)
         d_long,d_lati = Tunnel_info.d_long,Tunnel_info.d_lati
         dst_satIP = find_shortest_path(trans2ten(int(d_long)), trans2ten(int(d_lati)))
         send_pkt_btw_sats(pkt,dst_satIP)


     sys.stdout.flush()


class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 16),
                   BitField("port", 0, 16)]


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

bind_layers(Ether,myTunnel,type=0x1234)
bind_layers(Ether, SourceRoute, type=0x1111)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, myTunnel,bos=0x1234)
bind_layers(myTunnel, IP)

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