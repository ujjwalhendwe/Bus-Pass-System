from tracemalloc import start
from django.shortcuts import render
from django.http import HttpResponse
import MySQLdb.cursors

import mysql.connector

connection=mysql.connector.connect(host="localhost",user="hello",password="Google123",database="Buspasssystem")
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
    date=request.GET['Date']
    cursor.execute("Select routeid from route where startcity='{}' and endcity='{}'".format(startstation,endstation))
    routeid=cursor.fetchall()
    cursor.execute("select * from bsp join bus join runningpath join seatavailability where runningpath.routeid='{}' and dateofjourney='{}' and bus.bspid=bsp.bspid and bus.busid=runningpath.busid and seatavailability.busid=bus.busid and seatavailability.routeid=runningpath.routeid".format(routeid[0][0],date))
    buses=cursor.fetchall()
    print(buses)
    return render(request,"buslist.html",{"buses":buses})