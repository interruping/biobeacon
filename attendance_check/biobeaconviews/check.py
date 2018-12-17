#-*- coding: utf-8 -*-
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response

from attendance_check.serializers import (IdNumberCheckSerializer,
                                           IdCheckSerializer,
                                           InfoCheckSerializer,
                                           )


from attendance_check.models import ( ProfessorProfile,
                                      Lecture,
                                      StudentProfile,
                                      AttendanceRecord,
                                      LectureReceiveCard,
                                      )

from django.contrib.auth.models import User
from django.utils import timezone


class IdCheckView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):

        serializer = IdCheckSerializer(data=request.data)

        if serializer.is_valid():
            reg_username = serializer.validated_data['reg_username']
            user = User.objects.filter(username=reg_username)

            if user.exists():
                result = {
                    "result": 1
                }
                return Response(result)
            return Response(user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IdNumberCheckView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):

        serializer = IdNumberCheckSerializer(data=request.data)

        if serializer.is_valid():
            organization_id = serializer.validated_data['organization_id']
            employee_user = ProfessorProfile.objects.filter(employee_id=organization_id)
            student_user = StudentProfile.objects.filter(student_id=organization_id)

            if employee_user.exists():
                result = {
                    "result": 1
                }
                return Response(result)
            if student_user.exists():
                result = {
                    "result": 1
                }
                return Response(result)
            return Response(employee_user)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class InfoCheckView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):

        serializer = InfoCheckSerializer(data=request.data)

        if serializer.is_valid():
            login_username = serializer.validated_data['login_username']
            user = User.objects.filter(username=login_username).last()

            if user:
                if user.is_staff:
                    result = {
                        "result": 1
                    }
                    return Response(result)
                else:
                    result = {
                        "result": 2
                    }
                    return Response(result)

            else:
                return Response({'error': 'user not exist'}, status=status.HTTP_404_NOT_FOUND)


class LectureListCheckedView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):

        if request.user.is_staff:
            prof = ProfessorProfile.objects.get(user=request.user)
            lecture_set = Lecture.objects.filter(lecturer=prof)

            lectures = []

            for lecture in lecture_set:
                if AttendanceRecord.objects.filter(lecture = lecture):
                    lectures.append({
                        "id": lecture.pk,
                        "title": lecture.title,
                        "lecture_num": lecture.lecture_num
                    })

            result = {"lectures": lectures}
            return Response(result)
        else:

            lectures = { "lectures" : Lecture.objects.values()}

            return Response(lectures)


class LectureFastestView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        if request.user:
            userInfo = User.objects.get(username = request.user)
            userprofile = StudentProfile.objects.get(user = userInfo)
            userLectureCard = LectureReceiveCard.objects.filter(card_owner=userprofile)
            if userLectureCard:
                listcach = []

                for card in userLectureCard:
                    record = AttendanceRecord.objects.filter(lecture=card.target_lecture, activate=True)
                    if record:
                        if (record.last().end_time < timezone.now()):
                            record.last().activate = False
                            record.last().save()

                    record = AttendanceRecord.objects.filter(lecture=card.target_lecture, activate=True)
                    if record:

                        cardList = {
                            "lecture_id" : card.target_lecture.pk,
                            "lecture_title" : card.target_lecture.title,
                            "lecture_num" : card.target_lecture.lecture_num
                       }
                        listcach.append(cardList)

                return Response(listcach)

            else:
                return Response("You don't have lecture", status=status.HTTP_403_FORBIDDEN)
        else:
            return Response("Unknown User request", status=status.HTTP_403_FORBIDDEN)









