import copy
import time
import datetime
from RF2 import dijkstra_path
from sw_LLA import load_location
from time import sleep
import sys
counter=2

_MAX = float('inf')
map= [[_MAX] * 48 for _ in range(48)]


def transP2T( plane, sat):  # (1,1)->9
    number = plane * 8 + sat
    return number


def transT2P(number):  # s12->[0,1]->1
    p = []
    p.append(int(number[1]) - 1)
    p.append(int(number[2]) - 1)
    t = transP2T(p[0], p[1])
    return t

def location_update(sat_list):


        for i in range(len(sat_list)):
            for j in range(len(sat_list[i])):
                locat_pre=load_location.query_data("sw",sat_list[i][j].ipAddress)
                load_location.alter_db("sw_prefix",[sat_list[i][j].ipAddress,locat_pre[1],locat_pre[2]])

                locat=load_location.readCSV("sw_LLA/"+'s' + str(i+1)+str(j+1)+".csv",counter)
                data=[sat_list[i][j].ipAddress,locat[0],locat[1]]
                #print("location change:",data)
                load_location.alter_db("sw",data)




def link_status_update(sat_list,sat_map,linksInfo):
    global counter
    global map
    map=sat_map
    # load_location.show_all_db("sw_sw_prefix")
    # for i in range(len(sat_list)):
    #     for j in range(len(sat_list[i])):
    #         data = [sat_list[i][j].ipAddress, str(0), str(0)]
    #         print(data)
    #         load_location.add_db("sw_prefix",data)
    while counter<115:
        time.sleep(5)
        # with open('/home/fxy/Workspace/P4/mininet/sw_LLA/update_logs.txt', 'w') as f:
        #     print >> f, ["update:",counter]
        location_update(sat_list)#update location
        for i in range(len(sat_list)-1):#update link
            for j in range(len(sat_list[i])):
                latitude=load_location.query_data("sw",sat_list[i][j].ipAddress)[1]
                latitude_pre=load_location.query_data("sw_prefix",sat_list[i][j].ipAddress)[1]
                if abs(latitude)>70:
                    if map[transP2T(i,j)][transP2T(i+1,j)]==1 and j!=0:
                        map[transP2T(i, j)][transP2T(i + 1, j)]=_MAX
                        map[transP2T(i + 1, j)][transP2T(i, j)]=_MAX
                    elif map[transP2T(i,j)][transP2T(i+1,j-1)]==1 and j!=0:
                        map[transP2T(i, j)][transP2T(i + 1, j-1)] = _MAX
                        map[transP2T(i + 1, j-1)][transP2T(i, j)]=_MAX
                    elif j==0:
                        if map[transP2T(i, j)][transP2T(i , j)+15]==1:
                            map[transP2T(i, j)][transP2T(i, j)+15] = _MAX
                            map[transP2T(i, j)+15][transP2T(i, j)] = _MAX
                        elif map[transP2T(i, j)][transP2T(i+1 , j)]==1:
                            map[transP2T(i, j)][transP2T(i + 1, j)] = _MAX
                            map[transP2T(i, j)][transP2T(i + 1, j)]= _MAX
                else:
                    if 0<abs(latitude)<70 and latitude_pre>latitude: #direct to south
                        if map[transP2T(i,j)][transP2T(i+1,j)]==_MAX :
                            map[transP2T(i, j)][transP2T(i + 1, j)] =1
                            map[transP2T(i + 1, j)][transP2T(i, j)] =1
                        if j==0:
                            if map[transP2T(i, j)][transP2T(i, j)+15] ==1:
                                map[transP2T(i, j)][transP2T(i, j)+15] =_MAX
                                map[transP2T(i, j)+15][transP2T(i, j)]=_MAX
                        else:
                            if map[transP2T(i, j)][transP2T(i, j) + 7] == 1:
                                map[transP2T(i, j)][transP2T(i, j) + 7] = _MAX
                                map[transP2T(i, j) + 7][transP2T(i, j)] = _MAX
                    elif 0<abs(latitude)<70 and latitude_pre<latitude:#direct to north
                        if map[transP2T(i,j)][transP2T(i,j)+7]==_MAX and j!=0:
                            map[transP2T(i, j)][transP2T(i,j)+7] =1
                            map[transP2T(i, j)+7][transP2T(i, j)]=1
                        if j==0:
                            if map[transP2T(i,j)][transP2T(i,j)+15]==_MAX:
                                map[transP2T(i, j)][transP2T(i,j)+15] =1
                                map[transP2T(i,j)+15][transP2T(i, j)]=1
                        else:
                            if map[transP2T(i, j)][transP2T(i, j) +8] == 1:
                                map[transP2T(i, j)][transP2T(i, j) + 8] = _MAX
                                map[transP2T(i, j) +8][transP2T(i, j)] = _MAX
        # for i in range(len(sat_map)):#update map
        #     for j in range(len(sat_map)):
        #         if j<i:
        #             sat_map[i][j]=sat_map[j][i]

        route_update(map,linksInfo)
        counter+=1

def route_update(sat_map,linksInfo):
    actual_map=copy.deepcopy(sat_map)

    roads_nodesTran = [[_MAX] * 48 for _ in range(48)]  # route founding result with nodes
    roads_portTran = [[_MAX] * 48 for _ in range(48)]  # route founding result with nodes
    for i in range(48):
        for j in range(48):
            if i == j:
                roads_nodesTran[i][j] = _MAX
            else:
                tp_matrix = dijkstra_path(actual_map, i)
                road = tp_matrix.find_shortestPath(j)
                # value, road = Dijkstra(self.total, len(self.linksInfo), self.linkMap, i, j)
                roads_nodesTran[i][j] = road
    # for i in range(len(self.roads_nodesTran)):
    #    print(self.roads_nodesTran[i])
    hopsnum = []
    for i in range(len(roads_nodesTran)):
        for j in range(len(roads_nodesTran[i])):
            if roads_nodesTran[i][j] != _MAX:
                hopsnum.append(len(roads_nodesTran[i][j]) - 1)
    hopsnum.sort(reverse=True)
    # Note = open('sw_LLA/max_hops.txt', mode='a')
    # Note.writelines([str(datetime.datetime.now()), "max hop:", str(hopsnum[1]), '\n'])
    # Note.close()
    for i in range(len(roads_nodesTran)):
        for j in range(len(roads_nodesTran[i])):
            tp_portTran = []
            if i != j:
                for k in range(len(roads_nodesTran[i][j])):
                    if k == len(roads_nodesTran[i][j]) - 1:
                        tp_portTran.append(1)
                    else:
                        ln = roads_nodesTran[i][j][k]
                        rn = roads_nodesTran[i][j][k + 1]
                        for l in range(len(linksInfo)):
                            # print(self.linksInfo[l].sw1)
                            # print(self.transT2P(self.linksInfo[l].sw1),self.transT2P(self.linksInfo[l].sw2))
                            if transT2P(linksInfo[l].sw1) == ln and transT2P(
                                    linksInfo[l].sw2) == rn:
                                tp_portTran.append(linksInfo[l].p1)
                                break
                            elif transT2P(linksInfo[l].sw2) == ln and transT2P(
                                    linksInfo[l].sw1) == rn:
                                tp_portTran.append(linksInfo[l].p2)
                                break
            elif i==j:
                tp_portTran.append(1)
            roads_portTran[i][j] = tp_portTran

    for i in range(len(roads_portTran)):
        for j in range(len(roads_portTran[j])):
            if len(roads_portTran[i][j]) != 0:
                data = [str([i, j]), str(roads_portTran[i][j])]
                load_location.alter_db("SR", data)

    # for i in range(len(self.roads_nodesTran)):
    #    print(self.roads_portTran[i])















































    sleep(60)




