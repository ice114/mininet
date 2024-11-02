#!/usr/bin/env python
import argparse
import datetime
import sys
import socket
import random
import struct
import argparse
import  time
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
class replyData(Packet):
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
bind_layers(Ether,replyData,type=0x1300)

bind_layers(myRegi, IP)
bind_layers(myAsk,IP)
bind_layers(DCS_Asn,IP)
bind_layers(myData,IP)
bind_layers(replyData,IP)
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
def handle_pkt(pkt):
    # print("sniffing")
    global  data_count_rec,ap_b_lati,ap_b_long,time_data_end
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    rec_time=pkt.time
    if IP in pkt:
        IPinfo=pkt.getlayer(IP)
        if IPinfo.src!=src_ip:
            if DCS_Asn in pkt:
                    time_asn=time.clock()
                    # print("ask-asn:",time_asn-time_start,"s")
                    # print("got a DCS packet:",time.clock())
                    # print("got a DCS packet:",datetime.datetime.now())
                    pkt.show2()
                    info=pkt.getlayer(DCS_Asn)
                    sys.stdout.flush()
                    # print(trans2ten(int(info.d_longitude)),trans2ten(int(info.d_lagitude)))
                    ap_b_long=trans2ten(int(info.d_longitude))
                    ap_b_lati=trans2ten(int(info.d_lagitude))
                    print("update locat!!:",ap_b_lati,ap_b_long)
                    Note = open('sat_log/ask_rec.txt', mode='a')
                    Note.writelines([str(time.time()), "\n"])
                    Note.close()
                    # print('update reciever location:',ap_b_long,ap_b_lati)
                    # print(ap_b_long,ap_b_lati)
                    #send_data(trans2ten(int(info.d_longitude)),trans2ten(int(info.d_lagitude)))
                    # time_data_start=time.clock()
                    # print("Send a data pkt:",time.time())
                    # print("Send a data pkt:",datetime.datetime.now())
            if replyData in pkt:
                    time_data_end=time.time()
                    time_end=time.time()
                    # if data_count_rec!=0:
                    Note = open('sat_log/12_rec_data.txt', mode='a')

                    Note.writelines([str(int(round(rec_time*10000,2))),"\n"])

                    Note.close()
                    data_count_rec += 1
                    # print(time_data_end)
                    # print("got a data packet:",time.clock(),time.time())

                    print("got a data packet:", datetime.datetime.now())
                    # pkt.show2()
                    print("data_rec couting:",data_count_rec)
                    # if data_count_rec<5:
                    #     send_data1()
                    sys.stdout.flush()

def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
def main():
    print("main process")
    global  time_start,time_asn,time_data_start,time_data_end
    for i in range(len(sys.argv)):
        print(sys.argv[i])
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
            print "ask porcess:"
            dst_ip = sys.argv[2]

            print "dst:",dst_ip
            data = Thread(target=send_data)
            data.start()
            ask=Thread(target=send_ask,args=(iface,dst_ip))
            ask.start()
            #send_ask(iface,dst_ip)

            #send_data(ap_b_long,ap_b_lati)
            sniff(  # iface=iface,
                prn=lambda x: handle_pkt(x))

        else:
            print "errrrrrr"
            exit(1)
def main1():
    print("main process")
    global time_start, time_asn, time_data_start, time_data_end
    iface = get_if()
    dst_ip="10.0.9.9"
    src_ip = get_if_addr('eth0')
    src_addr = socket.gethostbyname(src_ip)
    addr = socket.gethostbyname('10.0.255.255')
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    # pkt = pkt / myRegi(u_srcIP=src_addr, longitude=000, lagitude=1111)
    pkt = pkt / IP(dst=addr)
    pkt.show2()
    bg=time.time()
    sendp(pkt, iface='eth0', verbose=False)
    sendp(pkt, iface='eth0', verbose=False)
    sendp(pkt, iface='eth0', verbose=False)
    sendp(pkt, iface='eth0', verbose=False)
    end=time.time()
    Note = open('sat_log/sendp_time.txt', mode='a')
    Note.writelines([str(end-bg), "\n"])
    Note.close()

    ask = Thread(target=send_ask, args=(iface, dst_ip))
    ask.daemon = True
    ask.start()
    time.sleep(1)
    data = Thread(target=send_data1)
    data.daemon = True
    data.start()
    sniff(  # iface=iface,
        prn=lambda x: handle_pkt(x))
if __name__ == '__main__':
    main1()