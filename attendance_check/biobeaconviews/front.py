#-*- coding: utf-8 -*-
from django.shortcuts import render
# Create your views here.

def mainView(request):

    return render(request, 'attendance_check/main.html')

def mainView(request):

    return render(request, 'attendance_check/main.html')

def loginView(request):

    return render(request, 'attendance_check/login.html')

def virtualClassView(request):

    return render(request, 'attendance_check/virtual_class.html')