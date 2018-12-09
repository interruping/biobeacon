#-*- coding: utf-8 -*-
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response

from attendance_check.serializers import ( RegistrationSerializer,
                                           LectureRequestSerializer,)

from attendance_check.models import ( ProfessorProfile,
                                      Lecture,
                                      Department,
                                      StudentProfile,
                                      LectureReceiveCard,
                                      ProfileImage,
                                      )


from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

import random

# Create your views here.
def Create_rand_N():
    N = random.randint(1, 99999)
    while (N % 99991 == 0):
        N = random.randint(1, 99999)
    return N


class RegistrationView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = RegistrationSerializer(data=request.data)
        Crypt_rand_N = Create_rand_N()
        if serializer.is_valid():
            newUser = User.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=make_password(serializer.validated_data['password']),
                is_staff=serializer.validated_data['is_staff'],
            )
            newUser.save()
            if serializer.validated_data['is_staff']:
                newProf = ProfessorProfile.objects.create(
                    user=newUser,
                    employee_id=serializer.validated_data['id'],
                    department=Department.objects.get(pk=serializer.validated_data['department']),
                )
                newProf.save()

                profile_img = ProfileImage.objects.get(pk=serializer.validated_data['profile_image_id'])
                profile_img.user = newUser
                profile_img.save()


            else :
                newStudentProfile = StudentProfile.objects.create(
                    user=newUser,
                    student_id=serializer.validated_data['id'],
                    department=Department.objects.get(pk=serializer.validated_data['department']),
                    Crypt_rand_N=Crypt_rand_N,
                )
                newStudentProfile.save()

                profile_img = ProfileImage.objects.get(pk=serializer.validated_data['profile_image_id'])
                profile_img.user = newUser
                profile_img.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):

        if request.user.is_staff:
            prof = ProfessorProfile.objects.get(user=request.user)
            prof_img = ProfileImage.objects.get(user=request.user)
            result = {
                'last_name' : request.user.last_name,
                'first_name': request.user.first_name,
                'username' : request.user.username,
                'email' : request.user.email,
                'user_type' : u'교수',
                'id' : prof.employee_id,
                'department' : prof.department.name,
                'profile_image' : prof_img.image.url,
                'time_set' : prof.absence_time_set,
            }


            return Response(result)
        else:
            sdt = StudentProfile.objects.get(user=request.user)
            std_img = ProfileImage.objects.get(user=request.user)
            result = {
                'last_name' : request.user.last_name,
                'first_name': request.user.first_name,
                'username' : request.user.username,
                'email' : request.user.email,
                'user_type' : u'학생',
                'id' : sdt.student_id,
                'department' : sdt.department.name,
                'profile_image' : std_img.image.url,
            }

            return Response(result)


class DepartmentListView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        departments = { "departments" : Department.objects.values() }


        return Response(departments)


class ProfileImageUploadView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        profile_image = ProfileImage()

        profile_image.save()
        profile_image.image = request.FILES['file']
        profile_image.save()

        return Response({
            'uploaded_url': profile_image.image.url,
            'image_id' : profile_image.pk})


class LectureRequestView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        serializer = LectureRequestSerializer(data=request.data)

        if serializer.is_valid():

            std = StudentProfile.objects.get(user=request.user)
            reqList = Lecture.objects.get(pk=serializer.validated_data['id'])

            record = LectureReceiveCard.objects.filter(target_lecture=reqList, card_owner=std)
            if record:
                result = {
                    'fail': True,
                }
                return Response(result, status=status.HTTP_403_FORBIDDEN)

            std = StudentProfile.objects.get(user=request.user)
            reqList = Lecture.objects.get(pk=serializer.validated_data['id'])

            lec = LectureReceiveCard.objects.create(
                target_lecture=reqList,
                card_owner=std,
            )
            lec.save()
            return Response({"result": True},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        std = StudentProfile.objects.get(user=request.user)

        return Response({"StudentPK": std.pk})