#!/usr/bin/env python
import argparse
import datetime
import sys
import socket
import random
import struct
import argparse
import  time
data_count_send=0
data_count_rec=0
time_start=0
time_asn=0
time_data_start=0
time_data_end=0
import distance_calc
from distance_calc import find_shortest_path
from sw_LLA import load_location
from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump,bind_layers,get_if_addr,sniff
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *
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

class myRegi(Packet):
    fields_desc =[
            BitField("direction",0,16),
            IPField("u_srcIP",str(0)),
            BitField("longitude",11,16),
            BitField("lagitude",22,16),
            IPField("dst_satIP",str(0)),

           ]
class myAsk(Packet):
    fields_desc = [
        BitField("direction", 0, 16),
        IPField("u_srcIP", str(0)),
        BitField("longitude", 11, 16),
        BitField("lagitude", 22, 16),
        IPField("dst_IP", str(0)),
        IPField("dst_satIP", str(0)),
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
class myData(Packet):
    fields_desc = [
        BitField("direction", 0, 16),
        BitField("d_longitude", 22, 16),
        BitField("d_lagitude", 33, 16),
        IPField("dst_satIP", str(0)),
    ]
bind_layers(Ether,myAsk,type=0x1256)
bind_layers(Ether, myRegi,type=0x1234)
bind_layers(Ether,DCS_Asn,type=0x1278)
bind_layers(Ether,myData,type=0x1299)


bind_layers(myRegi, IP)
bind_layers(myAsk,IP)
bind_layers(DCS_Asn,IP)
bind_layers(myData,IP)
def send_data(d_longitude,d_lagitude):
    iface = get_if()
    bind_layers(Ether, myData, type=0x1299)
    bind_layers(myData, IP)
    src_ip = get_if_addr('eth0')
    print
    src_ip

    src_addr = socket.gethostbyname(src_ip)
    self_locat = load_location.query_data("h", src_addr)
    print(self_locat)
    accept_sat = distance_calc.find_shortest_path(trans2ten(int(self_locat[1])), trans2ten(int(self_locat[2])))[-3:]
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
    print(send_iface)
    print
    src_addr
    addr = socket.gethostbyname('10.0.255.255')
    print
    addr
    print("broadcast send a DATA_packet:",time.clock())

    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4761)
    pkt = pkt / myData(direction=0,d_longitude=d_longitude,d_lagitude=d_lagitude)
    pkt = pkt / IP(dst=addr)
    #pkt.show2()
    sendp(pkt, iface=str(send_iface), verbose=False)

def handle_pkt(pkt):


    # if myRegi in pkt:
    #     print
    #     "got a regi packet"
    #     pkt.show2()
    #     sys.stdout.flush()
    # if myAsk in pkt:
    #     print
    #     "got a ask packet"
    #     pkt.show2()
    #     sys.stdout.flush()
    if DCS_Asn in pkt:
            time_asn=time.clock()
            print("ask-asn:",time_asn-time_start,"s")
            print("got a DCS packet:",time.clock())
            print("got a DCS packet:",datetime.datetime.now())
            #pkt.show2()
            info=pkt.getlayer(DCS_Asn)
            sys.stdout.flush()
            print(trans2ten(int(info.d_longitude)),trans2ten(int(info.d_lagitude)))
            send_data(trans2ten(int(info.d_longitude)),trans2ten(int(info.d_lagitude)))
            time_data_start=time.clock()
            print("Send a data pkt:",time.time())
            print("Send a data pkt:",datetime.datetime.now())
    if myData in pkt:
            time_end=time.time()
            time_data_end=time.clock()
            Note = open('sw_LLA/time_log.txt', mode='a')

            Note.writelines(["end: ",str(time_end),"\n"])

            Note.close()
            data_count_rec += 1
            print(time_data_end)
            print("got a data packet:",time.clock(),time.time())

            print("got a data packet:", datetime.datetime.now())
            #pkt.show2()
            print("data_package couting:",data_count_rec)

            sys.stdout.flush()

def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
def main():
    global data_count_send
    global data_count_rec
    global  time_start,time_asn,time_data_start,time_data_end
    print "11111111111111111111"
    if len(sys.argv)<2:
        bind_layers(Ether, myRegi, type=0x1234)
        bind_layers(myRegi, IP)
        bind_layers(Ether, myAsk, type=0x1256)
        bind_layers(myAsk, IP)
        sys.stdout.flush()
        sniff(  # iface=iface,
            prn=lambda x: handle_pkt(x))
    else:

        type=sys.argv[1]
        iface = get_if()
        print "222222222222222222222"
        if type == "regi":
            bind_layers(Ether, myRegi, type=0x1234)
            bind_layers(myRegi, IP)
            src_ip=get_if_addr('eth0')
            print src_ip

            src_addr=socket.gethostbyname(src_ip)
            self_locat = load_location.query_data("h", src_addr)
            print(self_locat)
            accept_sat=distance_calc.find_shortest_path(trans2ten(int(self_locat[1])),trans2ten(int(self_locat[2])))[-3:]
            sat_num=accept_sat.split('.')
            # for i in sat_num:
            #     print(i)
            if sat_num[0]=='1':
                if sat_num[1]=='1':
                    send_iface = 'eth' + str(int(sat_num[1]) - 1)
                else:
                    send_iface = self_locat[0] + '-eth' + str(int(sat_num[1]) - 1)

            else:
                send_iface = self_locat[0] +'-eth' + str((int(sat_num[0]) - 1) * 8+int(sat_num[1]) - 1)
            print(send_iface)
            print  src_addr
            addr = socket.gethostbyname('10.0.255.255')
            print addr
            print "broadcast send a regi_packet"
            pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff',type=4660)
            pkt = pkt / myRegi(u_srcIP=src_addr,longitude=self_locat[1], lagitude=self_locat[2])
            pkt = pkt / IP(dst=addr)
            pkt.show2()



            sendp(pkt, iface=str(send_iface), verbose=False)

        elif type=="ask":
            bind_layers(Ether, myAsk, type=0x1256)
            bind_layers(myAsk, IP)
            src_ip = get_if_addr('eth0')
            print
            src_ip

            src_addr = socket.gethostbyname(src_ip)
            self_locat = load_location.query_data("h", src_addr)
            print(self_locat)
            accept_sat = distance_calc.find_shortest_path(trans2ten(int(self_locat[1])), trans2ten(int(self_locat[2])))[-3:]
            sat_num = accept_sat.split('.')
            dst_ip=sys.argv[2]

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
            print

            pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=4694)
            pkt = pkt / myAsk(direction=0,u_srcIP=src_addr, longitude=self_locat[1], lagitude=self_locat[2],dst_IP=dst_ip)
            pkt = pkt / IP(dst=addr)
            #pkt.show2()
            sendp(pkt, iface=str(send_iface), verbose=False)
            time_start = time.clock()
            time_start1 = time.time()
            print("broadcast send a ask_packet:", time.time(),time.clock())
            print("send ask:", time_start1)
            print("send ask:",datetime.datetime.now() )
            Note = open('sw_LLA/time_log.txt', mode='a')
            Note.writelines(["start: ",str(time.time()), "   "])
            Note.close()
            sniff(  # iface=iface,
                prn=lambda x: handle_pkt(x))

        else:
            print "errrrrrr"
            exit(1)

if __name__ == '__main__':
    main()