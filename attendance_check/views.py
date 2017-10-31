from django.shortcuts import render

# Create your views here.

def login_view(request):

    return render(request, 'attendance_check/login.html')

def virtual_class_view(request):

    return render(request, 'attendance_check/virtual_class.html')