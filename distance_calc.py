from math import  sin,cos,tan,atan,degrees,radians,sqrt,pow,acos,pi
from sw_LLA import load_location
import  sqlite3
h = 1450
R = 6371



def yangjiao_calc(sat_long,sat_lati,u_long,u_lati):
    c=cos(abs(radians(u_long)-radians(sat_long)))*cos(radians(u_lati))*cos(radians(sat_lati))\
      +sin(radians(u_lati))*sin(radians(sat_lati))

    beta=atan((c-R/(R+h))/(sqrt(1-c*c)))
    #print(beta)
    return beta

def distance_calc(sat_long,sat_lati,u_long,u_lati):
    beta=yangjiao_calc(sat_long,sat_lati,u_long,u_lati)
    d=sqrt(pow(R,2)+pow(R+h,2)-2*R*(R+h)*cos(acos(R/(R+h)*cos(beta))-beta))
    return d

def find_shortest_path(u_long,u_lati):
    distance_list=[]
    cur_1 = load_location.open_db("sw")[1]
    cur_1.execute("select ip,long,lati from sw_location")
    for row in cur_1:
        #print(row)
        dst=distance_calc(row[1],row[2],u_long,u_lati)
        distance_list.append([row[0],dst])
    sorted_list=sorted(distance_list,key=lambda x:x[1])
    # for i in range(len(sorted_list)):
    #     print(sorted_list[i])
    # print(sorted_list[0][0])
    return sorted_list[0][0]
def find_nearest_sat_for_hosts():
    list=[]
    cur_1 = load_location.open_db("h")[1]
    cur_1.execute("select ip,long,lati from h_location")
    for row in cur_1:
        print(row)
        nearest_sat=find_shortest_path(row[1],row[2])
        list.append([row[0],nearest_sat])
    for i in range(len(list)):
        print(list[i])
if __name__ == '__main__':
    print("the nearest satellite to beijing gound station(116,40):",find_shortest_path(116,40)) #beijing  ground station
    print("the nearest satellite to beijing haikou(110,20):", find_shortest_path(110, 20) )#haikou
    print("the nearest satellite to beijing washingtonDC(-77,39):", find_shortest_path(-77, 39))#washingtonDC
    find_shortest_path(11,48)
