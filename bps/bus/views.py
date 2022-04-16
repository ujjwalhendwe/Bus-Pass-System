from email import message
from operator import index
import re
from tracemalloc import start
from django.shortcuts import redirect, render
from django.http import HttpResponse
import MySQLdb.cursors
from datetime import datetime,time
from django.contrib import messages
import time
from django.core.files.storage import FileSystemStorage

import mysql.connector
from numpy import diff


#connection=mysql.connector.connect(host="localhost",user="root",password="harsh",database="buspasssystem")

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

    if not request.user.is_authenticated:
        messages.info(request, 'Login before booking tickets')
        return redirect('/')

    user=str(request.user)   

    cursor.execute(''' select userid from user where userid=%s''',(user,))
    log=cursor.fetchone()

    if log == None:
        cursor.execute(''' insert into user(userid,name) values(%s,%s)''',(request.user.get_username(),request.user.get_full_name()))
        connection.commit()
        cursor.execute('''insert into wallet(userid,walletbalance) values(%s,%s)''',(request.user.get_username(),0))
        connection.commit()

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
        temp2.append(d)
        temp3=tuple(temp2)
        temp1[index]=temp3

    buses=tuple(temp1)    
    print(buses)

    return render(request,"buslist.html",{"buses":buses})


def seat(request):

    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']

    cursor.execute(''' select bookedseats from seatavailability where routeid=%s and busid=%s and dateofjourney=%s''',(routeid,busid,date))
    info1=cursor.fetchone()
    info=info1[0]
    seats=[]

    n=0

    if info != None:
       n=len(info)

    print(n)

    for i in range(n):
        if(info[i]=='_'):
            temp=info[i-1]+info[i]+info[i+1]
            seats.append(temp)

    print(seats)

    return render(request, "seat.html", {"seats":seats,"routeid":routeid,"busid":busid,"date":date})


def payment(request):
    seats=request.POST['seats']
    price=request.POST['price']
    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']
    pricef=int(price)
    pricef=pricef+100
    print(seats)

    cursor.execute(''' select walletbalance from wallet where userid=%s''',(request.user.get_username(),))
    balance=cursor.fetchall()

    check=False

    if balance[0][0] > pricef:
        check=True

    return render(request, "payment.html",{"seats":seats, "price":price, "pricef":pricef,"routeid":routeid,"busid":busid,"date":date, "balance":balance[0][0], "check":check})

def passenger(request):
    pricef=request.POST['pricef']
    seat=request.POST['seats']
    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']

    n=len(seat)
    n=n+1
    n=n/4
    n=int(n)

    temp=[]
    j=1

    for i in range(len(seat)):
       if seat[i]=='_':
           st=seat[i-1]+seat[i]+seat[i+1]
           temp1=[j,st]
           temp.append(tuple(temp1))
           j=j+1

    seats=tuple(temp)
    print(seats)       

    return render(request,"passenger.html",{"seats":seats,"pricef":pricef, "price":pricef,"routeid":routeid,"busid":busid,"date":date})


def topup(request):
    user=request.user.get_username()
    seats=request.POST['seats']
    price=request.POST['price']
    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']
    pricef=request.POST['pricef']
    topup=request.POST['topup']

    print(type(request.user.get_username()))
    cursor.execute(''' select walletbalance from wallet where userid=%s''',(request.user.get_username(),))
    balance=cursor.fetchall()

    new=balance[0][0]+int(topup)

    cursor.execute(''' update wallet set walletbalance =%s where userid=%s''',(new,request.user.get_username(),))
    connection.commit()

    cursor.execute(''' select walletbalance from wallet where userid=%s''',(request.user.get_username(),))
    balance=cursor.fetchall()

    check=False

    if balance[0][0] > int(pricef):
        check=True

    return render(request,'payment.html',{"seats":seats,"pricef":pricef, "price":price,"routeid":routeid,"busid":busid,"date":date,"balance":balance[0][0],"check":check})

def book(request):

    name=request.POST.getlist('name')
    age=request.POST.getlist('age')
    seats=request.POST['seats']
    routeid=request.POST['routeid']
    busid=request.POST['busid']
    date=request.POST['date']
    pricef=request.POST['pricef']

    bookingid=int(time.time()*1000000)

    cursor.execute(''' select bookedseats from seatavailability where busid=%s and routeid=%s and dateofjourney=%s ''',(busid,routeid,date))
    bs=cursor.fetchone()
    bseats=bs[0]

    if bseats== None:
        bseats=""
        
    seat=""

    for index,s in enumerate(seats):
        if s=='_':
           seat=seat+seats[index-1]+s+seats[index+1]+" "
           bseats=bseats+seats[index-1]+s+seats[index+1]+" "

    cursor.execute('''insert into ticket(bookingid,userid,busid,routeid,dateofjourney,seats,price,transactionid,status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(bookingid,request.user.get_username(),busid,routeid,date,bseats,pricef,bookingid,"CNF"))
    connection.commit()

    for index,n in enumerate(name):
        pid=int(time.time()*1000000+index+1)
        cursor.execute(''' insert into passengerdetails(passengerid,bookingid,userid,name,age) value(%s,%s,%s,%s,%s)''',(pid,bookingid,request.user.get_username(),n,age[index]))
        connection.commit()

    cursor.execute(''' update seatavailability set bookedseats=%s  where busid=%s and routeid=%s and dateofjourney=%s ''',(bseats,busid,routeid,date))    
    connection.commit()


    cursor.execute(''' select startcity, endcity from route where routeid=%s''',(routeid,))
    details=cursor.fetchone()

    cursor.execute(''' select cityname from city where cityid=%s''',(details[0],))
    startcity=cursor.fetchone()[0]

    cursor.execute(''' select cityname from city where cityid=%s''',(details[1],))
    endcity=cursor.fetchone()[0]

    npass=len(name)

    cursor.execute(''' select bspid, registrationno from bus where busid=%s''',(busid,))
    details=cursor.fetchone()

    bspid=details[0]
    bregno=details[1]

    cursor.execute(''' select name,phone from bsp where bspid=%s''',(bspid,))
    details=cursor.fetchone()

    bspname=details[0]
    phone=details[1]

    cursor.execute(''' select walletbalance from wallet where userid=%s''',(request.user.get_username(),))
    balance=cursor.fetchone()[0]

    fbalance=int(balance)-int(pricef)

    cursor.execute(''' update wallet set walletbalance=%s where userid=%s''',(fbalance,request.user.get_username()))
    connection.commit()

    return render(request,'ticket.html',{"bookingid":bookingid,"startcity":startcity,"endcity":endcity,"npass":npass,"seat":seat,"bregno":bregno,"bspname":bspname,"phone":phone,"pricef":pricef,"date":date,"name":name})


def profile(request):

    user=request.user.get_username()

    cursor.execute(''' select userid from user where userid=%s''',(user,))
    log=cursor.fetchone()

    if log == None:
        cursor.execute(''' insert into user(userid,name) values(%s,%s)''',(request.user.get_username(),request.user.get_full_name()))
        connection.commit()
        cursor.execute('''insert into wallet(userid,walletbalance) values(%s,%s)''',(request.user.get_username(),0))
        connection.commit()

    userid=request.user.get_username()
    cursor.execute('''select * from user where userid=%s''',(userid,))
    details=cursor.fetchall()
    print(details)
    return render(request,"profile.html",{'details':details})

def editprofile(request):

    user=request.user.get_username()

    cursor.execute(''' select userid from user where userid=%s''',(user,))
    log=cursor.fetchone()

    if log == None:
        cursor.execute(''' insert into user(userid,name) values(%s,%s)''',(request.user.get_username(),request.user.get_full_name()))
        connection.commit()
        cursor.execute('''insert into wallet(userid,walletbalance) values(%s,%s)''',(request.user.get_username(),0))
        connection.commit()

    userid=request.user.get_username()
    cursor.execute('''select * from user where userid=%s''',(userid,))
    details=cursor.fetchall()
    date=str(details[0][4])
    return render(request,"editprofile.html",{'details':details,"date":date})

def edit(request):
    name=request.POST['name']
    phone=request.POST['phone']
    gender=request.POST['gender']
    dob=request.POST['dob']
    address=request.POST['address']
    userid=request.user.get_username()
    cursor.execute("update user set name='{}', phone='{}',gender='{}',dob='{}',address='{}' where userid='{}'".format(name,phone,gender,dob,address,userid))
    connection.commit()
    cursor.execute("select * from user where userid='{}'".format(userid))
    details=cursor.fetchall()
    return render(request,"profile.html",{"details":details})    

def history(request):
    userid=request.user.get_username()
    cursor.execute("select * from ticket where userid='{}'".format(userid))
    ticket=cursor.fetchall()
    if(len(ticket)>0):
        cursor.execute("select distinct(dateofjourney) from ticket where userid='{}'".format(userid))
        dates=cursor.fetchall()
        prevdetails=[]
        newdetails=[]
        c=datetime.now()
        date=c.strftime("%Y:%m:%d")
        date_format = "%Y:%m:%d"
        a = datetime.strptime(date, date_format)
        for i in dates:
            date1=str(i[0]).replace("-",":")
            b = datetime.strptime(date1, date_format)
            delta=b-a
            delta=delta.days
            if (delta>=0):
                cursor.execute("select bookingid,startcity,endcity,dateofjourney,seats,status from ticket join route where userid='{}' and dateofjourney='{}' and route.routeid=ticket.routeid".format(userid,i[0]))
                y=cursor.fetchall()
                newdetails.append(y)
            else:
                cursor.execute("select bookingid,startcity,endcity,dateofjourney,seats,status from ticket join route where userid='{}' and dateofjourney='{}' and route.routeid=ticket.routeid".format(userid,i[0]))
                y=cursor.fetchall()
                prevdetails.append(y)
        #print(type(prevdetails[0][0]))
        #print(prevdetails)

        return render(request,"history.html",{"prevdetails":prevdetails,'newdetails':newdetails}) 
    return render(request,"history.html") 

def rating(request):
    return render(request,"rating.html") 

def cancel(request,Ticketno):
    cursor.execute("select status from ticket where bookingid='{}'".format(Ticketno))
    status=cursor.fetchall()
    if(len(status)>0):
        if(status[0][0]=="CNF"):
            cursor.execute("update ticket set status='CXL' where bookingid='{}'".format(Ticketno))
            connection.commit()
    userid=request.user.get_username()
    cursor.execute("select * from ticket where userid='{}'".format(userid))
    ticket=cursor.fetchall()
    if(len(ticket)>0):
        cursor.execute("select distinct(dateofjourney) from ticket where userid='{}'".format(userid))
        dates=cursor.fetchall()
        prevdetails=[]
        newdetails=[]
        c=datetime.now()
        date=c.strftime("%Y:%m:%d")
        date_format = "%Y:%m:%d"
        a = datetime.strptime(date, date_format)
        for i in dates:
            date1=str(i[0]).replace("-",":")
            b = datetime.strptime(date1, date_format)
            delta=b-a
            delta=delta.days
            if (delta>=0):
                cursor.execute("select bookingid,startcity,endcity,dateofjourney,seats,status from ticket join route where userid='{}' and dateofjourney='{}' and route.routeid=ticket.routeid".format(userid,i[0]))
                y=cursor.fetchall()
                newdetails.append(y)
            else:
                cursor.execute("select bookingid,startcity,endcity,dateofjourney,seats,status from ticket join route where userid='{}' and dateofjourney='{}' and route.routeid=ticket.routeid".format(userid,i[0]))
                y=cursor.fetchall()
                prevdetails.append(y)
    return render(request,"history.html",{"prevdetails":prevdetails,'newdetails':newdetails}) 
def buspass(request):
    return render(request,"pass.html")

def passcheck(request):

    if not request.user.is_authenticated:
        messages.info(request, 'Login before booking tickets')
        return redirect('/')

    user=str(request.user)   

    cursor.execute(''' select userid from user where userid=%s''',(user,))
    log=cursor.fetchone()

    if log == None:
        cursor.execute(''' insert into user(userid,name) values(%s,%s)''',(request.user.get_username(),request.user.get_full_name()))
        connection.commit()
        cursor.execute('''insert into wallet(userid,walletbalance) values(%s,%s)''',(request.user.get_username(),0))
        connection.commit()
    userid=request.user.get_username()
    name=request.POST['Name']
    fathername=request.POST['FatherName']
    aadharno=request.POST['Aadharno']
    aadhar=request.FILES['Aadhar']
    city=request.POST['CityId']
    student=request.POST['student']
    handicap=request.POST['handicap']
    senior=request.POST['senior']
    fs=FileSystemStorage()
    file1=fs.save(name+"-"+aadhar.name,aadhar)
    x=""
    y=""
    z=""
    if(student=="Yes"):
        studentid=request.FILES['studentid']
        x=name+"-"+studentid.name
        file2=fs.save(name+"-"+studentid.name,studentid)
    if(handicap=="Yes"):
        handicapcertificate=request.FILES['handicapcertificate']
        y=name+"-"+handicapcertificate.name
        file3=fs.save(name+"-"+handicapcertificate.name,handicapcertificate)
    if(senior=="Yes"):
        seniorcitizencertificate=request.FILES['seniorcitizencertificate']
        z=name+"-"+seniorcitizencertificate.name
        file4=fs.save(name+"-"+seniorcitizencertificate.name,seniorcitizencertificate)
    cursor.execute("insert into citybuspass(name,fathername,userid,cityid,aadharno,aadharpath,documentpath) values('{}','{}','{}','{}','{}','{}','{}')".format(name,fathername,userid,city,aadharno,name+"-"+aadhar.name,x+"  "+y+"  "+z))
    connection.commit()
    cursor.execute("select * from citybuspass where userid='{}'".format(userid))
    details=cursor.fetchall()
    c=datetime.now()
    date=c.strftime("%Y:%m:%d")
    date_format = "%Y:%m:%d"
    a = datetime.strptime(date, date_format)
    return render(request,"softcopy.html",{"details":details,"date":date})

def contact(request):
    return render(request,"contact.html")    