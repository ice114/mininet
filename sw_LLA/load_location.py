#!/usr/bin/env python

import csv
import sys
import time
import sqlite3
def open_db(type):
    if type=="sw":
        db = sqlite3.connect('location.db')
        db.execute("create table if not exists sw_location(ip primary key,long,lati)")
        cur = db.cursor()
        return db, cur
    elif type=="h":
        db = sqlite3.connect('location.db')
        db.execute("create table if not exists h_location(ip primary key,long,lati,name)")
        cur = db.cursor()
        return db, cur
    elif type=="gw":
        db = sqlite3.connect('location.db')
        db.execute("create table if not exists gw_location(ip primary key,long,lati,name)")
        cur = db.cursor()
        return db, cur
    elif type=="sw_prefix":
        db = sqlite3.connect('location.db')
        db.execute("create table if not exists sw_location_pre(ip primary key,long,lati)")
        cur = db.cursor()
        return db, cur
    elif type=="SR":
        db = sqlite3.connect('location.db')
        db.execute("create table if not exists SR_result(sNd primary key,result)")
        cur = db.cursor()
        return db, cur
    else:
        print("error type")
        exit(1)
def open_gw_db(name,type):
    gw_db="gw"+name+".db"
    db = sqlite3.connect(gw_db)
    if type=="vxlan":
        db.execute("create table if not exists vxlan(primary key(VNI,DIP),islocal,nexthop)")
        cur = db.cursor()
        return db, cur
    elif type=="vmgw":
        db.execute("create table if not exists vmgw(primary key(VNI,VMIP),long,lati,gw)")
        cur = db.cursor()
def add_db(type,data):
    print("******adding data******")
    cur_1=open_db(type)
    if type=="sw":
        cur_1[1].execute("insert or ignore into sw_location(ip,long,lati) values(?,?,?)",(data[0],data[1],data[2]))
        cur_1[0].commit()
        print(data)
        print("******add data successfully******")
    elif type=="h":
        cur_1[1].execute("insert or ignore into h_location(ip,long,lati,name) values(?,?,?,?)", (data[0], data[1], data[2],data[3]))
        cur_1[0].commit()
        print(data)
        print("******add data successfully******")
    elif type=="gw":
        cur_1[1].execute("insert or ignore into gw_location(ip,long,lati,name) values(?,?,?,?)", (data[0], data[1], data[2],data[3]))
        cur_1[0].commit()
        print(data)
        print("******add data successfully******")
    elif type=="vxlan":
        cur_1[1].execute("insert or ignore into vxlan(VNI,DIP,islocal,name) values(?,?,?,?)",
                         (data[0], data[1], data[2], data[3]))
        cur_1[0].commit()
        print(data)
        print("******add data successfully******")
    elif type == "sw_prefix":
        cur_1[1].execute("insert or ignore into sw_location_pre(ip,long,lati) values(?,?,?)", (data[0], data[1], data[2]))
        cur_1[0].commit()
        # print(data)
        # print("******add data successfully******")
    elif type == "SR":
        cur_1[1].execute("insert or ignore into SR_result(sNd,result) values(?,?)", (data[0], data[1]))
        cur_1[0].commit()
        print(data)
        print("******add data successfully******")
        

def add_gw_db(name,type,data):
    print("******adding gw data******")
    cur_1 = open_gw_db(name,type)
    if type == "vxlan":
        cur_1[1].execute("insert into vxlan(VNI,DIP,islocal,nexthop) values(?,?,?,?)", (data[0], data[1], data[2],data[3]))
        cur_1[0].commit()
        print(data)
        print("******add vxlan data successfully******")
    if type == "vmgw":
        cur_1[1].execute("insert into vmnc(VNI,VMIP,long,lati,gw) values(?,?,?,?,?)", (data[0], data[1], data[2],data[3],data[4].data[5]))
        cur_1[0].commit()
        print(data)
        print("******add vmgw data successfully******")

def delete_db(type,d_ip):
    print("******deleting data******")
    cur_1=open_db(type)
    if type == "sw":
        cur_1[1].execute("delete from sw_location where ip =?",(d_ip,))
        cur_1[0].commit()
        print("******delete data successfully******")
        show_all_db()
        cur_1[1].close()
    elif type=="h":
        cur_1[1].execute("delete from h_location where ip =?", (d_ip,))
        cur_1[0].commit()
        print("******delete data successfully******")
        show_all_db()
        cur_1[1].close()
    elif type=="gw":
        cur_1[1].execute("delete from gw_location where ip =?", (d_ip,))
        cur_1[0].commit()
        print("******delete data successfully******")
        show_all_db()
        cur_1[1].close()
    elif type == "sw_prefix":
        cur_1[1].execute("delete from sw_location_pre where ip =?", (d_ip,))
        cur_1[0].commit()
        print("******delete data successfully******")
        show_all_db()
        cur_1[1].close()
    elif type == "SR":
        cur_1[1].execute("delete from SR_result where sNd =?", (d_ip,))
        cur_1[0].commit()
        print("******delete data successfully******")
        show_all_db()
        cur_1[1].close()


def show_all_db(type):
    print("******all data******")
    cur_1=open_db(type)[1]
    if type == "sw":
        cur_1.execute("select ip,long,lati from sw_location")
        for row in cur_1:
            print(row)
    elif type=="h":
        cur_1.execute("select ip,long,lati,name from h_location")
        for row in cur_1:
            print(row)
    elif type=="gw":
        cur_1.execute("select ip,long,lati,name from gw_location")
        for row in cur_1:
            print(row)
    elif type == "sw_prefix":
        cur_1.execute("select ip,long,lati from sw_location_pre")
        for row in cur_1:
            print(row)
    elif type == "SR":
        cur_1.execute("select sNd,result from SR_result")
        for row in cur_1:
            print(row)


def alter_db(type,data):
    #print("******editing data******")
    cur_1=open_db(type)
    if type=="sw":
        dataa=(data[1],data[2],data[0])
        cmd="update sw_location set long = ? ,lati = ? where ip = ?"
        #print(cmd)
        #cur_1[1].execute("update book set long=?,lati=?where ip ="+data[0],(data[1],data[2]))
        cur_1[1].execute(cmd,dataa)
        cur_1[0].commit()
        # show_all_db(type)
        cur_1[1].close()
    elif type=="h":
        dataa = (data[1], data[2], data[0])
        cmd = "update h_location set long = ? ,lati = ? where ip = ?"
        # print(cmd)
        # cur_1[1].execute("update book set long=?,lati=?where ip ="+data[0],(data[1],data[2]))
        cur_1[1].execute(cmd, dataa)
        cur_1[0].commit()
        # show_all_db(type)
        cur_1[1].close()
    elif type=="gw":
        dataa = (data[1], data[2], data[0])
        cmd = "update gw_location set long = ? ,lati = ? where ip = ?"
        # print(cmd)
        # cur_1[1].execute("update book set long=?,lati=?where ip ="+data[0],(data[1],data[2]))
        cur_1[1].execute(cmd, dataa)
        cur_1[0].commit()
        # show_all_db(type)
        cur_1[1].close()
    elif type == "sw_prefix":
        dataa = (data[1], data[2], data[0])
        cmd = "update sw_location_pre set long = ? ,lati = ? where ip = ?"
        # print(cmd)
        # cur_1[1].execute("update book set long=?,lati=?where ip ="+data[0],(data[1],data[2]))
        cur_1[1].execute(cmd, dataa)
        cur_1[0].commit()
        # show_all_db(type)
        cur_1[1].close()
    elif type == "SR":
        dataa=(data[1],data[0])
        cmd="update SR_result set result = ? where sNd = ?"
        cur_1[1].execute(cmd, dataa)
        cur_1[0].commit()
        # show_all_db(type)
        cur_1[1].close()
        # print("alter SR of ",data[0])

def query_data(type,data):
    #print("******sorting data******")
    if type=="sw":
        # print(data)
        cur_1=open_db(type)
        cmd="SELECT * FROM sw_location WHERE ip = ?"
        # print(cmd)
        cur_1[1].execute(cmd,(data,))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()
    elif type=="h":
        cur_1 = open_db(type)
        cur_1[1].execute("select name,long,lati from h_location where ip =?" ,(data,))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()
    elif type=="gw":
        cur_1 = open_db(type)
        cur_1[1].execute("select name,long,lati from gw_location where ip =?" ,(data,))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()
    elif type == "sw_prefix":
        # print(data)
        cur_1 = open_db(type)
        cmd = "SELECT * FROM sw_location_pre WHERE ip = ?"
        # print(cmd)
        cur_1[1].execute(cmd, (data,))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()
    elif type == "SR":
        # print(data)
        cur_1 = open_db(type)
        cmd = "SELECT * FROM SR_result WHERE sNd = ?"
        #print(cmd)
        cur_1[1].execute(cmd, (data,))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()

def query_data1(type,data):
    if type=="h":
        cur_1 = open_db(type)
        cur_1[1].execute("select name from h_location where long =? and lati= ?" ,(data[0],data[1]))
        # print("******sorting result******")
        for row in cur_1[1]:
            # print(row)
            return row
        cur_1[1].close()
def drop_all_tables():
    conn = sqlite3.connect('location.db')
    cursor = conn.execute("DROP TABLE")
    cursor.close()

def readCSV(filename,index):
    with open(filename) as f:
        reader=csv.reader(f)
        head_row=next(reader)
        #print(head_row)
        while index>0:
            f_row=next(reader)
            index-=1
       #print(round(float(f_row[1])),round(float(f_row[2])))
    return [round(float(f_row[2])),round(float(f_row[1]))]

def analyze():
    cur_1=open_db('SR')[1]
    cur_1.execute("select sNd,result from SR_result")
    for row in cur_1:
        row1=row[1][1:-4].split(', ')
        t=0
        for i in range(len(row1)):
            if row1[i]=='9' or row1[i]=='8':
                t+=16.6
            elif row1[i]=='4' or row1[i]=='5' or row1[i]=='6' or row1[i]=='7':
                t+=5.6
        # src=int(row[0][1:-1].split(',')[0])
        # dst=int(row[0][1:-1].split(',')[1])
        # if abs(src-dst)>7:
        #     print(row[0],row1,t)
        #     Note = open('../sat_log/dif_orbit.txt', mode='a')
        #     Note.writelines([str(round(t,2)), '\n'])
        #     Note.close()
        Note = open('../sat_log/total.txt', mode='a')
        Note.writelines([str(round(t, 2)), '\n'])
        Note.close()

if __name__ == '__main__':
    #readCSV('sw_LLA/s11.csv',4)
    read=readCSV('s11.csv',3)
    data =['168.0.1.2',read[0],read[1]]
    #add_db(data)
    #show_all_db("sw")
    #show_all_db("h")
    #delete_db('168.0.1.2')
    #alter_db(data)

    # ll=[1,2]
    # rr=[6,1]
    # data1=[str(ll),str(rr)]
    # #add_db("SR",data1)
    # #show_all_db("sw_prefix")
    # show_all_db("SR")
    # analyze()
    # #alter_db("SR",[])
    a=query_data("gw",'10.0.9.9')[0]
    print(a)
    # query_data1('SR',str([]))

