#!/usr/bin/env python
import argparse
import datetime
import sys
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
        print "Cannot find eth0 interface"
        exit(1)
    return iface

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

def send_data():
    iface=get_if()
    counter=0
    while counter<5:
        global data_count_send,time_data_start

        if(ap_b_long!=0 and ap_b_lati!=0):
            bind_layers(Ether, myData, type=0x1299)
            bind_layers(myData, IP)
            src_ip = get_if_addr('eth0')

            src_addr = socket.gethostbyname(src_ip)
            self_locat = load_location.query_data("h", src_addr)
            # print(self_locat)
            accept_sat = distance_calc.find_shortest_path(trans2ten(int(self_locat[1])), trans2ten(int(self_locat[2])))[-3:]
            Note1 = open('sat_log/sender_accept_sat.txt', mode='a')

            Note1.writelines([accept_sat, "\n"])

            Note1.close()
            sat_num = accept_sat.split('.')
            # for i in sat_num:
            #     print(i)
            if sat_num[0] == '1':
                if sat_num[1] == '1':
                    send_iface = 'eth' + str(int(sat_num[1]) - 1)
                else:
                    send_iface = self_locat[0] + '-eth' + str(int(sat_num[1]) - 1)

            else:
                send_iface = self_locat[0] + '-eth' + str((int(sat_num[0]) - 1) * 8 + int(sat_num[1]) - 1)
            # print(send_iface)
            addr = socket.gethostbyname('10.0.255.255')


            pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4761)
            pkt = pkt / myData(direction=0,d_longitude=ap_b_long,d_lagitude=ap_b_lati)
            pkt = pkt / IP(dst=addr)
            # pkt.show2()
            sendp(pkt, iface=str(send_iface), verbose=False)
            time_data_start=time.time()
            Note = open('sat_log/1_send_data.txt', mode='a')

            Note.writelines([str(time_data_start), "\n"])

            Note.close()
            print("broadcast send a DATA_packet:", datetime.datetime.now())
            data_count_send+=1
            print("counting sended data packet: ",data_count_send)
            time.sleep(1)
            counter+=1
def send_data1():
    print('99999999999999999999999999999999999999999999999999')
    iface = get_if()
    # time.sleep(5)
    global data_count_send, time_data_start
    counter=0
    while True:
        if (ap_b_long != 0 and ap_b_lati != 0):
            time.sleep(1)
            bind_layers(Ether, myData, type=0x1299)
            bind_layers(myData, IP)
            src_ip = get_if_addr('eth0')

            src_addr = socket.gethostbyname(src_ip)
            self_locat = load_location.query_data("h", src_addr)
            # print(self_locat)
            accept_sat = distance_calc.find_shortest_path(trans2ten(int(self_locat[1])), trans2ten(int(self_locat[2])))[
                         -3:]
            Note1 = open('sat_log/sender_accept_sat.txt', mode='a')

            Note1.writelines([accept_sat, "\n"])

            Note1.close()
            sat_num = accept_sat.split('.')
            # for i in sat_num:
            #     print(i)
            if sat_num[0] == '1':
                if sat_num[1] == '1':
                    send_iface = 'eth' + str(int(sat_num[1]) - 1)
                else:
                    send_iface = self_locat[0] + '-eth' + str(int(sat_num[1]) - 1)

            else:
                send_iface = self_locat[0] + '-eth' + str((int(sat_num[0]) - 1) * 8 + int(sat_num[1]) - 1)
            # print(send_iface)
            addr = socket.gethostbyname('10.0.255.255')

            pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4761)
            pkt = pkt / myData(direction=0, d_longitude=ap_b_long, d_lagitude=ap_b_lati)
            pkt = pkt / IP(dst=addr)
            pkt.show2()
            bf_send=time.time()*10000
            sendp(pkt, iface=str(send_iface), verbose=False)
            time_data_start = time.time()*10000
            print("after send:",time_data_start)
            Note = open('sat_log/1_send_data.txt', mode='a')

            Note.writelines([str(int(round((time_data_start+bf_send)/2,2))), "\n"])

            Note.close()
            print("broadcast send a DATA_packet:", datetime.datetime.now())
            data_count_send += 1
            print("counting sended data packet: ", data_count_send)

            counter+=1

def send_ask(iface,dst_ip):
    counter=0

    while counter<5:
        bind_layers(Ether, myAsk, type=0x1256)
        bind_layers(myAsk, IP)
        src_ip = get_if_addr('eth0')
        src_addr = socket.gethostbyname(src_ip)
        # print(src_addr)
        self_locat = load_location.query_data("h", src_addr)
        # print(self_locat)
        accept_sat = distance_calc.find_shortest_path(trans2ten(int(self_locat[1])), trans2ten(int(self_locat[2])))[-3:]
        sat_num = accept_sat.split('.')
        Note1 = open('sat_log/sender_accept_sat.txt', mode='a')

        Note1.writelines([accept_sat, "\n"])

        Note1.close()
        # for i in sat_num:
        #     print(i)
        if sat_num[0] == '1':
            if sat_num[1] == '1':
                send_iface = 'eth' + str(int(sat_num[1]) - 1)
            else:
                send_iface = self_locat[0] + '-eth' + str(int(sat_num[1]) - 1)

        else:
            send_iface = self_locat[0] + '-eth' + str((int(sat_num[0]) - 1) * 8 + int(sat_num[1]) - 1)
        # print(send_iface)
        addr = socket.gethostbyname('10.0.255.255')
        pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4694)
        pkt = pkt / myAsk(direction=0, u_srcIP=src_addr, longitude=self_locat[1], lagitude=self_locat[2], dst_IP=dst_ip)
        pkt = pkt / IP(dst=addr)
        pkt.show2()
        sendp(pkt, iface=str(send_iface), verbose=False)
        time_start = time.clock()
        time_start1 = time.time()
        # print("broadcast send a ask_packet:", time.time(), time.clock())
        # print("send ask:", time_start1)
        # print("send ask:", datetime.datetime.now())
        Note = open('sat_log/ask_send.txt', mode='a')
        Note.writelines([str(time.time()), "\n"])
        Note.close()
        time.sleep(5)
        counter+=1
        # sniff(  # iface=iface,
        #     prn=lambda x: handle_pkt(x))
        # send_data1()

def search_vni(s_ip):
    for i in range(len(hosts)):
        if hosts[i][1]==s_ip:
            vni=hosts[i][0]
            return vni
def search_gw(vni):
    for i in range(len(gws)):
        if vni==gws[i][0]:
            gw_ip="10.0."+str(vni+8)+"."+str(vni+8)
            return gws[i][1][0],gws[i][1][1],gw_ip

def add_tunnel_and_fw(pkt):
    d_ip=pkt.getlayer(IP).dst
    d_vni=search_vni(d_ip)
    d_long,d_lati,d_gw_ip=search_gw(d_vni)
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
    new_pkt = new_pkt / myTunnel(t_src=my_ip,t_dst=d_gw_ip,VNI=d_vni,s_long=my_long,s_lati=my_lati,d_long=d_long,d_lati=d_lati,sat=send_iface)
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
    sys.stdout.flush()
    sniff(  # iface=iface,
        prn=lambda x: handle_pkt(x))
if __name__ == '__main__':
    main1()