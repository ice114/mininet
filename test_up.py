import imp
from time import sleep
from sw_LLA import load_location
gws=[[1,[116,40]],[2,[75, 39]]]
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

update_sat_gw_locat()