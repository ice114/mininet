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


def trans2ten(num):
    if abs(num<2**15-1):
        return num
    else:
        return -(((num & 0xffff) ^ 0xffff) + 1)
def handle_pkt(pkt):
     if myRegi in pkt or myAsk in pkt or myData in pkt or DCS_Asn in pkt or replyData in pkt:
         info = pkt.getlayer(Ether)
         rec_time=pkt.time
         type = info.type
         if type == 0x1234:

             # pkt.show2()
             regi_info = pkt.getlayer(myRegi)
             direction = regi_info.direction
             bind_layers(Ether, myRegi, type=0x1234)
             if direction == 0:
                 print("got a regi packet from ground:", time.clock())

                 u_srcIP = regi_info.u_srcIP
                 longitude = regi_info.longitude
                 lagitude = regi_info.lagitude
                 DCS_locat = load_location.query_data("h", "10.0.7.7")[1:]
                 dst_satIP = find_shortest_path(trans2ten(int(DCS_locat[0])), trans2ten(int(DCS_locat[1])))
                 send_regi_forward_btw_sats(u_srcIP, longitude, lagitude, dst_satIP)
                 print(time.time())
                 # split_layers(myRegi, IP)
                 # split_layers(SourceRoute, myRegi)
                 # split_layers(SourceRoute, SourceRoute, bos=0)
                 # split_layers(Ether, SourceRoute, type=0x1111)
                 print
                 "stopppppppppppppp"
                 # return True
             elif direction == 2:
                 print("got a regi packet from sat:", time.clock())
                 u_srcIP = regi_info.u_srcIP
                 longitude = regi_info.longitude
                 lagitude = regi_info.lagitude
                 DCS_locat = load_location.query_data("h", "10.0.7.7")[1:]
                 dst_satIP = find_shortest_path(trans2ten(int(DCS_locat[0])), trans2ten(int(DCS_locat[1])))
                 regi_forward_to_ground(u_srcIP, longitude, lagitude, dst_satIP)
                 print("send to DCS:", time.clock())

                 # split_layers(SourceRoute, myRegi, bos=0x1234)
                 # split_layers(Ether, SourceRoute, type=0x1111)
         elif type == 0x1256:

             ask_info = pkt.getlayer(myAsk)
             direction = ask_info.direction

             if direction == 0:
                 print("got a ask packet from ground", time.clock())
                 print("got a ask packet from ground", datetime.datetime.now())
                 u_srcIP = ask_info.u_srcIP
                 longitude = ask_info.longitude
                 lagitude = ask_info.lagitude
                 dst_IP = ask_info.dst_IP
                 DCS_locat = load_location.query_data("h", "10.0.7.7")[1:]
                 dst_satIP = find_shortest_path(trans2ten(int(DCS_locat[0])), trans2ten(int(DCS_locat[1])))
                 time_clear1 = time.time()
                 send_ask_forward_btw_sats(u_srcIP, longitude, lagitude, dst_satIP, dst_IP)
                 time_clear2 = time.time()
                 delta_time = time_clear2 - time_clear1
                 # Note = open('sw_LLA/time_log.txt', mode='a')
                 # Note.writelines(["-",str(delta_time), '   '])
                 # Note.close()
                 # split_layers(myAsk, IP)
                 # split_layers(SourceRoute, myAsk)
                 # split_layers(SourceRoute, SourceRoute, bos=0)
                 # split_layers(Ether, SourceRoute, type=0x1111)
                 print("send btw sats:", time.clock)
                 print("send btw sats:", datetime.datetime.now())
                 print
                 "stopppppppppppppp"
                 # return True
             elif direction == 2:
                 print("got a ask packet from sat", time.clock())
                 print("got a ask packet from sat", datetime.datetime.now())
                 u_srcIP = ask_info.u_srcIP
                 longitude = ask_info.longitude
                 lagitude = ask_info.lagitude
                 dst_IP = ask_info.dst_IP
                 DCS_locat = load_location.query_data("h", "10.0.7.7")[1:]
                 dst_satIP = find_shortest_path(trans2ten(int(DCS_locat[0])), trans2ten(int(DCS_locat[1])))
                 time_clear1 = time.time()
                 ask_forward_to_ground(u_srcIP, longitude, lagitude, dst_satIP, dst_IP)
                 time_clear2 = time.time()
                 delta_time = time_clear2 - time_clear1
                 # Note = open('sw_LLA/time_log.txt', mode='a')
                 # Note.writelines(["-", str(delta_time), '   '])
                 # Note.close()
                 # split_layers(SourceRoute, myAsk, bos=0x1256)
                 # split_layers(Ether, SourceRoute, type=0x1111)
                 print("send to DCS:", time.clock())
                 print("send to DCS:", datetime.datetime.now())
         elif type == 0x1278:
             ans_info = pkt.getlayer(DCS_Asn)
             direction = ans_info.direction
             if direction == 0:
                 print("got a ans packet from ground:", time.clock())
                 print("got a ans packet from ground:", datetime.datetime.now())
                 time_clear1 = time.time()
                 dst_satIP = find_shortest_path(trans2ten(int(ans_info.longitude)), trans2ten(int(ans_info.lagitude)))
                 send_ans_forward_btw_sats(ans_info, dst_satIP)
                 time_clear2 = time.time()
                 delta_time = time_clear2 - time_clear1
                 # Note = open('sw_LLA/time_log.txt', mode='a')
                 # Note.writelines(["-", str(delta_time), '   '])
                 # Note.close()
                 print("send btw sats:", time.clock())
                 print("send btw sats:", datetime.datetime.now())
             elif direction == 2:
                 print("got a ans packet from sat:", time.clock)
                 print("got a ans packet from sat:", datetime.datetime.now())
                 time_clear1 = time.time()
                 ans_forward_to_ground(ans_info)
                 time_clear2 = time.time()
                 delta_time = time_clear2 - time_clear1
                 # Note = open('sw_LLA/time_log.txt', mode='a')
                 # Note.writelines(["-", str(delta_time), '   '])
                 # Note.close()
                 print("send to ground:", time.clock())
                 print("send to ground:", datetime.datetime.now())
         elif type == 0x1299:
             data_info = pkt.getlayer(myData)
             direction = data_info.direction
             pkt.show2()
             if direction == 0:
                 print("got a data packet from ground:", rec_time)
                 print("got a data packet from ground:", time.time())
                 print("got a data packet from ground:", datetime.datetime.now())

                 dst_satIP = find_shortest_path(trans2ten(int(data_info.d_longitude)),
                                                trans2ten(int(data_info.d_lagitude)))
                 print(dst_satIP)
                 time_clear1 = time.time()
                 rec_data_from_ground = time.time()
                 Note = open('sat_log/2_sw_rec_data.txt', mode='a')
                 Note.writelines([str(int(round(rec_time*10000,2))), "\n"])
                 Note.close()
                 before_send=time.time()
                 send_time_3=send_data_forward_btw_sats(data_info, dst_satIP)
                 # del_1=timeit.timeit(stmt=send_data_forward_btw_sats,number=1)
                 after_send=time.time()
                 Note = open('sat_log/del_1.txt', mode='a')
                 Note.writelines([str(after_send-before_send), "\n"])
                 Note.close()
                 print("first del:",after_send-before_send)
                 print("send btw sats:", time.time())
                 print("send btw sats:", datetime.datetime.now())
                 Note = open('sat_log/3_sw_fw_data.txt', mode='a')
                 Note.writelines([str(int(round(send_time_3))), "\n"])
                 Note.close()
             elif direction == 2:
                 print("got a data packet from sat:", rec_time)
                 print("got a data packet from sat:", time.time())
                 print("got a data packet from sat:", datetime.datetime.now())
                 sw_rec_data_from_sats_4 = time.time()
                 Note = open('sat_log/4_sw_rec_data.txt', mode='a')
                 Note.writelines([str(int(round(rec_time*10000,2))), "\n"])
                 Note.close()
                 before_send=time.time()
                 send_time_5=data_forward_to_ground(data_info)
                 after_send=time.time()
                 Note = open('sat_log/del_2.txt', mode='a')
                 Note.writelines([str(after_send-before_send), "\n"])
                 Note.close()
                 print("del 2:",after_send-before_send)
                 print("send to ground:", time.time())
                 print("send to ground:", datetime.datetime.now())
                 Note = open('sat_log/5_sw_fw_data.txt', mode='a')
                 Note.writelines([str(int(round(send_time_5))), "\n"])
                 Note.close()
         elif type == 0x1300:
             data_info = pkt.getlayer(replyData)
             direction = data_info.direction
             pkt.show2()
             if direction == 0:
                 print("got a rdata packet from ground:", rec_time)
                 print("got a data packet from ground:", time.time())
                 print("got a data packet from ground:", datetime.datetime.now())

                 dst_satIP = find_shortest_path(trans2ten(int(data_info.d_longitude)),
                                                trans2ten(int(data_info.d_lagitude)))
                 rec_data_from_ground_8 = time.time()
                 Note = open('sat_log/8_sw_rec_data.txt', mode='a')

                 Note.writelines([str(int(round(rec_time*10000))), "\n"])

                 Note.close()
                 before_send=time.time()
                 send_time_9=send_rdata_forward_btw_sats(data_info, dst_satIP)

                 after_send=time.time()
                 Note = open('sat_log/del_3.txt', mode='a')

                 Note.writelines([str(after_send-before_send), "\n"])

                 Note.close()
                 print("del 3:",after_send-before_send)
                 print("send btw sats:",time.time())
                 print("send btw sats:", datetime.datetime.now())
                 Note = open('sat_log/9_sw_fw_data.txt', mode='a')
                 Note.writelines([str(int(round(send_time_9))), "\n"])
                 Note.close()
             elif direction == 2:
                 sw_rec_data_from_sats_10 = time.time()
                 Note = open('sat_log/10_sw_rec_data.txt', mode='a')
                 Note.writelines([str(int(round(rec_time*10000))), "\n"])
                 Note.close()
                 print("got a rdata packet from sat:", rec_time)
                 print("got a data packet from sat:", time.time())
                 print("got a data packet from sat:", datetime.datetime.now())
                 time_clear1 = time.time()
                 before_send = time.time()
                 send_time_11=rdata_forward_to_ground(data_info)
                 after_send = time.time()
                 Note = open('sat_log/del_4.txt', mode='a')

                 Note.writelines([str(after_send - before_send), "\n"])

                 Note.close()
                 print("del 4:", after_send - before_send)
                 print(time.time())
                 print("send to ground:", time.time())
                 print("send to ground:", datetime.datetime.now())
                 Note = open('sat_log/11_sw_fw_data.txt', mode='a')
                 Note.writelines([str(int(round(send_time_11))), "\n"])
                 Note.close()
     sys.stdout.flush()

class myRegi(Packet):
    fields_desc =[
            BitField("direction", 0, 16),
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
class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 16),
                   BitField("port", 0, 16)]
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

bind_layers(Ether, SourceRoute, type=0x1111)
bind_layers(SourceRoute, SourceRoute, bos=0)

bind_layers(SourceRoute, myRegi,bos=0x1234)
bind_layers(SourceRoute, myAsk,bos=0x1256)
bind_layers(SourceRoute, DCS_Asn,bos=0x1278)
bind_layers(SourceRoute, myData,bos=0x1299)
bind_layers(SourceRoute, replyData,bos=0x1300)

bind_layers(myRegi, IP)
bind_layers(myAsk,IP)
bind_layers(DCS_Asn,IP)
bind_layers(myData,IP)
bind_layers(replyData,IP)
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