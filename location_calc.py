from math import cos,tan,sin,acos,asin,atan,pi,radians,degrees




def yshwdzb_1(locat):
    fi=acos(cos(radians(locat[0]))*cos(radians(locat[1])))
    return degrees(fi)

def wdfys_2(jdys):
    jd=atan(tan(radians(jdys))*sin(radians(0)))
    wd=asin(sin(radians(jdys))*cos(radians(0)))

    #return jd,wd
    return round(degrees(jd),2),round(degrees(wd),2)
def underSatLocat(planeNum,satNum,delta_time):
    omega_e=7.27*(10**(-5)) #弧度/s
    #jiaoju=(radians(22.5)*(planeNum-1)+2*pi/6900*delta_time+2*(satNum-1)*2*pi/8)%360  #是弧度
    #jiaoju=((2*pi/6900)*delta_time+2*(satNum-1)*2*pi/8)%(2*pi)        #是弧度
    jiaoju=(2*pi/6900*delta_time)+(satNum-1)*(2*pi/8)-(pi/8)*(planeNum-1)
    longitude_rad=(2*pi)/6*(planeNum-1)+atan(cos(radians(90))*tan(jiaoju))-omega_e*delta_time
    longitude_deg=degrees(longitude_rad)
    if -180<=degrees(jiaoju)<-90:
        longitude_deg+=-180
    elif 90<=degrees(jiaoju)<180:
        longitude_deg+=180
    lagitude=degrees(asin(sin(jiaoju)*sin(radians(90))))
    return longitude_deg,lagitude
def main():

    very_first_LEO = [0, 0]#dongjingwei+,beiweiwei+  -151.682
    very_first_LEO_yshwd = yshwdzb_1(very_first_LEO)
    print(very_first_LEO_yshwd)
    very_first_LEO_ysjd, very_first_LEO_yswd = wdfys_2(very_first_LEO_yshwd)
    #print(very_first_LEO_ysjd, very_first_LEO_yswd)
    a_plane = []
    a_plane_yshwd=[]
    # for i in range(8):
    #     delta=i*45
    #     wd_after_ys=yshwdzb_1([very_first_LEO[0],very_first_LEO[1]+delta])
    #     jd,wd=wdfys_2(wd_after_ys)
    #     a_plane.append([round(jd,2),round(wd,2)])
    for i in range(6):
        tmp_plane=[]
        very_first_sat=[very_first_LEO[0]+60*i,very_first_LEO[1]-22.5*i]
        print(very_first_sat)
        for j in range(8):
            delta=j*45
            wd_after_ys=yshwdzb_1([very_first_sat[0],very_first_sat[1]+delta])
            jd,wd=wdfys_2(wd_after_ys)
            tmp_plane.append([jd,wd])
        a_plane.append(tmp_plane)
    for i in range(len(a_plane)):
        print(a_plane[i])
def findUnderSatLocat():
    undersatDict=dict()
    for i in range(1,7):
        for j in range(1,9):
            l1,l2=underSatLocat(i,j,0)
            undersatDict["s"+str(i)+str(j)]=[l1,l2]
    for key,value in undersatDict.items():
        print(key,value)
def findEachSatLocat():
    s11=[0,0]
    s11_fi=yshwdzb_1(s11)
if __name__ == '__main__':
    main()

