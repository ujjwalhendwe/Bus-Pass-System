from tracemalloc import start
from django.shortcuts import render
from django.http import HttpResponse
import MySQLdb.cursors
from datetime import datetime,time

import mysql.connector
from numpy import diff

connection=mysql.connector.connect(host="localhost",user="root",password="harsh",database="buspasssystem")
cursor=connection.cursor(buffered=True)

# Create your views here.
def register(request):
    return render(request,'register.html')

def signin(request):
    return render(request,'login.html')

def update(request):
    firstname=request.POST['firstname']
    lastname=request.POST['lastname']
    Userid=request.POST['Userid']
    password=request.POST['password']
    confirmpassword=request.POST['confirmpassword']
    phonenumber=int(request.POST['phonenumber'])
    email=request.POST['email']
    gender=request.POST['gender']
    dob=request.POST['dob']
    address=request.POST['address']

    cursor.execute("SELECT userid FROM user WHERE userid='{}'".format(Userid))
    validate=cursor.fetchall()

    if len(validate)==0 and password==confirmpassword:
        cursor.execute("""INSERT INTO user(userid,password,name,address,dob,phone,gender,email) VALUES('{}','{}','{}','{}','{}','{}','{}','{}')""".format(Userid,password,firstname+" "+lastname,address,dob,phonenumber,gender,email))
        connection.commit()
        return render(request,'login.html')
    elif len(validate)==0 and password!=confirmpassword:
        return render(request,'register.html',{'validpassword':"(Passwords do not match)"})
    if len(validate)>0:
        return render(request,'register.html',{'validuserid':"(User Id already present)"})

def login(request):
    cursor.execute("Select * from city")
    z=cursor.fetchall()
    Userid=request.GET['Userid']
    password=request.GET['password']
    cursor.execute("SELECT userid FROM user WHERE userid='{}'".format(Userid))
    validate1=cursor.fetchall()
    cursor.execute("SELECT userid FROM user WHERE userid='{}' and password='{}'".format(Userid,password))
    validate2=cursor.fetchall()
    if len(validate2)>0:
        return render(request,'home.html',{"stations":z})
    elif len(validate1)>0:
        return render(request,'login.html',{'validpassword':"(Incorrect password)"})
    else:
        return render(request,'login.html',{'validuserid':"(User Id is not present)"})

def showbus(request):
    startstation=(request.GET['Start']).split('-')[1]
    endstation=(request.GET['End']).split('-')[1]
    date=str(request.GET['Date'])
    cursor.execute("Select routeid from route where startcity='{}' and endcity='{}'".format(startstation,endstation))
    routeid=cursor.fetchall()
    cursor.execute("select * from bsp join bus join runningpath join seatavailability where runningpath.routeid='{}' and dateofjourney='{}' and bus.bspid=bsp.bspid and bus.busid=runningpath.busid and seatavailability.busid=bus.busid and seatavailability.routeid=runningpath.routeid".format(routeid[0][0],date))
    buses=cursor.fetchall()
    print(buses)
    return render(request,"buslist.html",{"buses":buses})

def track(request):
    cursor.execute("select busid from bus")
    buses=cursor.fetchall()
    return render(request,"track.html",{"bus":buses})

def trackbus(request):
    busid=request.GET['busid']
    date=request.GET['date']
    cursor.execute("select * from seatavailability where busid='{}' and dateofjourney='{}'".format(busid,date))
    running=cursor.fetchall()
    if (len(running)<=0):
        return render(request,"track.html",{'info':"Bus is not running on this day"})
    date1=date.replace("-",":")
    c=datetime.now()
    time=c.strftime("%H:%M:%S")
    date2=c.strftime("%Y:%m:%d")
    date_format = "%Y:%m:%d"
    a = datetime.strptime(date1, date_format)
    b = datetime.strptime(date2, date_format)
    delta=b-a
    diff=delta.days
    cursor.execute("select max(enddayno) from runningpath where busid='{}'".format(busid))
    endday=cursor.fetchall()[0][0]
    cursor.execute("select max(endstopnumber) from runningpath where busid='{}'".format(busid))
    endstop=cursor.fetchall()[0][0]
    cursor.execute("select endtime from runningpath where busid='{}' and endstopnumber='{}'".format(busid,endstop))
    endtime=cursor.fetchall()[0][0]
    if diff<0:
        return render(request,"track.html",{'info':"Bus didn't start its journey"})
    if diff>endday:
        return render(request,"track.html",{'info':"Bus completed its journey"})
    if(diff<=endday and time>=str(endtime)):
        cursor.execute("select * from runningpath where busid='{}' and endstopnumber='{}'".format(busid,endstop))
        complete=cursor.fetchall()
        if(len(complete)<=0):
            return render(request,"track.html",{'info':"Bus completed its journey"})
    cursor.execute("select starttime from runningpath where busid='{}' and startstopnumber=1".format(busid))
    start=cursor.fetchall()[0][0]
    if (diff==0 and time<str(start)):
        return render(request,"track.html",{'info':"Bus didn't start its journey"})
    cursor.execute("select * from runningpath where busid='{}'and starttime<'{}' and endtime>'{}' and endstopnumber-startstopnumber=1".format(busid,time,time))
    route=cursor.fetchall()
    depttime=route[0][2]
    arrivaltime=route[0][5]
    routeid=route[0][1]
    cursor.execute("select * from route where routeid='{}'".format(routeid))
    path=cursor.fetchall()
    deptstation=path[0][1]
    arrivalstation=path[0][2]
    details=[depttime,deptstation,arrivaltime,arrivalstation]
    if (len(details)>0):
        return render(request,"track.html",{'details':details})
    cursor.execute("select * from runningpath where busid='{}'and starttime='{}' and endstopnumber-startstopnumber=1".format(busid,time))
    route=cursor.fetchall()
    routeid=route[0][1]
    cursor.execute("select * from route where routeid='{}'".format(routeid))
    path=cursor.fetchall()
    deptstation=path[0][1]
    details=[deptstation]
    if (len(details)>0):
        return render(request,"track.html",{'details1':details})


def home(request):
    cursor.execute("select cityid, cityname from city")
    city=cursor.fetchall()
    return render(request,'home.html',{"city":city});        


def buslist(request):
    dep=request.POST['dep']
    arr=request.POST['arr']
    date=str(request.POST['date'])

    cursor.execute(''' select routeid from route where startcity =%s and endcity=%s''',(dep,arr))
    route=cursor.fetchall()
    routeid=route[0]

    cursor.execute(''' select busid from runningpath where routeid=%s''',routeid)
    buslist=cursor.fetchall()

    cursor.execute('''select * from bsp join bus join runningpath join seatavailability where runningpath.routeid=%s and dateofjourney='{}' and bus.bspid=bsp.bspid and bus.busid=runningpath.busid and seatavailability.busid=bus.busid and seatavailability.routeid=runningpath.routeid'''.format(date),(routeid))
    busess=cursor.fetchall()

    temp1=list(busess)

    for index,bus in enumerate(temp1):
        temp2=list(bus)
        d=str(temp2[27])
        #temp2[27]=str(temp2[27])
        temp2.append(d)
        print(type(temp2[31]))
        temp3=tuple(temp2)
        temp1[index]=temp3

    buses=tuple(temp1)    

    return render(request,"buslist.html",{"buses":buses})


def seat(request):

    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']

    cursor.execute(''' select bookedseats from seatavailability where routeid=%s and busid=%s and dateofjourney=%s''',(routeid,busid,date))
    info1=cursor.fetchone()
    info=info1[0]
    seats=[]
    n=len(info)
    print(n)

    for i in range(n):
        if(info[i]=='_'):
            temp=info[i-1]+info[i]+info[i+1]
            seats.append(temp)

    print(seats)

    return render(request, "seat.html", {"seats":seats})


def payment(request):
    seats=request.POST['seats']
    price=request.POST['price']
    pricef=int(price)
    pricef=pricef+100
    print(seats)

    return render(request, "payment.html",{"seats":seats, "price":price, "pricef":pricef})

