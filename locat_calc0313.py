import time
from math import pi,sin,cos,tan,degrees,atan,radians,asin





def fomula1(delta_time):
    sita=2*pi/6900*delta_time
    jiaoju=degrees(sita)
    if 360>jiaoju>180:
        jiaoju=0-(jiaoju-180)
    print("jiaoju=",jiaoju)
    omega_e=7.292*(10**(-5))
    jd=0
    wd=0

    if -180<=jiaoju<-90:
        jd=atan(cos(radians(86))*tan(sita))-omega_e*delta_time-180
    elif -90<=jiaoju<90:
        jd = atan(cos(radians(86)) * tan(sita))-omega_e*delta_time
    elif 90<=jiaoju<180:
        jd=atan(cos(radians(86)) * tan(sita))-omega_e*delta_time+180
    wd=asin(sin(radians(86))*sin(sita))
    print(jd,wd)
    if jd<-180:
        print("11111")
        jd=180+(jd+180)
    elif jd>180:
        print("22222")
        jd=-180+(jd-180)
    print("jd11=",jd,"wd11=",wd)
    return jd,wd

def fomula2(i,j,time):
    jd11,wd11=fomula1(time)
    delta_omega=2*pi/6
    jdi1=jd11+i*delta_omega
    if jdi1>180:
        jdi1-=360
    print("jdi1=",jdi1)
    jd1j=0
    if jdi1>=0:
        jiaoju=(2*pi/6900*time+2*j*(2*pi/8))%360
        print("jiaoju=",jiaoju)
        if(cos(radians(jiaoju))*cos(2*pi/6900*time))<0:
            print(cos(radians(jiaoju))*cos(2*pi/6900*time),'<0')
            jd1j=jdi1-180
            print(jd1j)
        else:
            print(cos(radians(jiaoju)) * cos(2 * pi / 6900 * time),'>=0')
            jd1j=jdi1
            print(jd1j)
    else:
        jiaoju = (2 * pi / 6900 * time + 2 * j * (2 * pi / 8)) % 360
        print("jiaoju=", jiaoju)
        if (cos(radians(jiaoju)) * cos(2 * pi / 6900 * time)) < 0:
            print(cos(radians(jiaoju)) * cos(2 * pi / 6900 * time), '<0')
            jd1j = jdi1 + 180
            print(jd1j)
        else:
            print(cos(radians(jiaoju)) * cos(2 * pi / 6900 * time), '>=0')
            jd1j = jdi1
            print(jd1j)
    jdij=jdi1+jd1j
    if jdij<-180:
        jdij=180+(jdij+180)
    elif jdij>180:
        jd=-180-(jdij-180)
    return jdij

def underSatLocat(planeNum,delta_time):

















if __name__ == '__main__':
    jd=fomula2(0,4,0)
    print(jd)