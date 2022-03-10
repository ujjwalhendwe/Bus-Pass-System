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
    Userid=request.GET['Userid']
    password=request.GET['password']
    cursor.execute("SELECT userid FROM user WHERE userid='{}'".format(Userid))
    validate1=cursor.fetchall()
    cursor.execute("SELECT userid FROM user WHERE userid='{}' and password='{}'".format(Userid,password))
    validate2=cursor.fetchall()
    if len(validate2)>0:
        return render(request,'index.html')
    elif len(validate1)>0:
        return render(request,'login.html',{'validpassword':"(Incorrect password)"})
    else:
        return render(request,'login.html',{'validuserid':"(User Id is not present)"})