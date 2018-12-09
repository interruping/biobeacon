#-*- coding: utf-8 -*-
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response

from attendance_check.serializers import (
                                           LectureRequestAttendanceCheckSerializer,
                                           IdNumberCheckSerializer,
                                           IdCheckSerializer,
                                           InfoCheckSerializer,
                                           LectureBeaconCheckSerializer,)


from attendance_check.models import ( ProfessorProfile,
                                      Lecture,
                                      StudentProfile,
                                      AttendanceRecord,
                                      AttendanceCard,
                                      LectureReceiveCard,
                                      LectureUuidRecord,
                                      )

from django.contrib.auth.models import User

from attendance_check import uuidcalc

from django.utils import timezone
import datetime


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


class LectureBeaconCheck(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user:
            serializer = LectureBeaconCheckSerializer(data = request.data)
            if serializer.is_valid():
                #해당 강의
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])

                # 요청한 강의의 uuid
                lectureUuid = LectureUuidRecord.objects.get(lecture_num=lecture.lecture_num)


                if (lectureUuid.reachLimiter < serializer.validated_data['reach']):
                    return Response("Beacon is too far", status=status.HTTP_403_FORBIDDEN)#비콘과의 거리가 멀음


                # 해당 강좌의 결석플래그 상태 조정
                recordLate = AttendanceRecord.objects.filter(lecture=lecture, activate_absence=False)
                if recordLate:
                    for list in recordLate:
                        if list.absence_time < timezone.now():
                            list.activate_absence = True
                            list.save()

                # 해당 강의의 활성화 여부 찾기
                record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)

                # 해당 강의의 활성화유무 판단 활성화되면
                if record:
                    record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                    # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                    if (record.end_time < timezone.now()):
                        record.activate = False
                        record.save()







                # 지정한 강의실 UUID 갱신기간이 넘어가면 수행
                if lectureUuid.init_time <= timezone.now():
                    secret_key = (int)(lectureUuid.secret_key)
                    prime_num = (int)(lectureUuid.prime_num)

                    # UUID값을 계산하여 저장 now현재 pre이전 next다음
                    # UUID_calc(prime_num, secret_key, default_uuid, 강의실번호)
                    lectureUuid.uuid_now = (uuidcalc.UUID_calc_now(prime_num, secret_key, lectureUuid.default_uuid,
                                                                   lecture.lecture_num))
                    lectureUuid.uuid_pre = (uuidcalc.UUID_calc_pre(prime_num, secret_key, lectureUuid.default_uuid,
                                                                   lecture.lecture_num))
                    lectureUuid.uuid_next = (
                    uuidcalc.UUID_calc_next(prime_num, secret_key, lectureUuid.default_uuid,
                                            lecture.lecture_num))
                    # 다음 uuid값이 변경해야할 값을 저장
                    lectureUuid.init_time = timezone.now() + datetime.timedelta(
                        minutes=uuidcalc.addTime(timezone.now().minute)) - datetime.timedelta(
                        seconds=timezone.now().second)
                    lectureUuid.save()

                if AttendanceRecord.objects.filter(lecture=lecture).last():
                    activateRecord = AttendanceRecord.objects.filter(lecture=lecture).last()
                    activateRecord = AttendanceRecord.objects.get(pk = activateRecord.pk)
                # 해당 강좌가 결석 플레그가 있으면
                if activateRecord.activate_absence == True:
                    userInfo = User.objects.get(username=request.user)
                    userprofile = StudentProfile.objects.get(user=userInfo)
                    userLectureCard = AttendanceCard.objects.filter(checker=userprofile, record_to = activateRecord)

                    if not userLectureCard:
                        card = AttendanceCard.objects.create(
                            checker=userprofile,
                            record_to=activateRecord,
                            check_time=timezone.now(),
                            check_start_time=activateRecord.start_time,
                            is_late_checker=True,
                            is_reasonableabsent_checker=False,
                            is_absent_checker=True
                        )
                        card.save()
                        return Response("Completed absence",status = status.HTTP_200_OK)#결석 완료


                #활성화되고 결석플래그가 없는 강좌가 있으면
                elif  activateRecord.activate==True:
                    if lectureUuid.uuid_now == serializer.validated_data['lectureUuid']:
                        userInfo = User.objects.get(username=request.user)
                        userprofile = StudentProfile.objects.get(user=userInfo)
                        userLectureCard = AttendanceCard.objects.filter(checker=userprofile, record_to = activateRecord)



                        #시차 차이에 의한 UUID값의 허용 중단플래그 설정
                        if (((timezone.now() > lectureUuid.init_time - datetime.timedelta(minutes=1)) or (
                        timezone.now() < lectureUuid.init_time - datetime.timedelta(minutes=9)))):
                            if lectureUuid.time_difference_check_flag == True:
                                lectureUuid.time_difference_check_flag = False
                                lectureUuid.time_difference = False
                        else:
                            lectureUuid.time_difference_check_flag = False
                            lectureUuid.time_difference = True
                        lectureUuid.save()


                        #학생 출결이 이미 있으면
                        if userLectureCard:
                            userLectureCard = AttendanceCard.objects.get(checker=userprofile,record_to=activateRecord)
                            userLectureCard.beacon_checker = True
                            userLectureCard.is_late_checker = False
                            userLectureCard.is_reasonableabsent_checker = False
                            userLectureCard.is_absent_checker = False
                            userLectureCard.save()
                        # 없으면 생성
                        else:
                            card = AttendanceCard.objects.create(
                                checker=userprofile,
                                record_to=activateRecord,
                                check_time=timezone.now(),
                                check_start_time=activateRecord.start_time,
                                beacon_checker = True,
                            )
                            card.save()

                        return Response("Completed attendance", status=status.HTTP_200_OK)#출석 완료
                    else:
                        if (((timezone.now() > lectureUuid.init_time - datetime.timedelta(minutes=1)) or (timezone.now() < lectureUuid.init_time - datetime.timedelta(minutes=9))) and (lectureUuid.time_difference == True)):
                            userInfo = User.objects.get(username=request.user)
                            userprofile = StudentProfile.objects.get(user=userInfo)
                            userLectureCard = AttendanceCard.objects.filter(checker=userprofile,record_to=activateRecord)

                            #이전, 다음 UUID와 일치하는지
                            if lectureUuid.uuid_pre == serializer.validated_data['lectureUuid'] or lectureUuid.uuid_next == serializer.validated_data['lectureUuid']:
                                lectureUuid.time_difference_check_flag = True
                                lectureUuid.save()
                                # 학생 출결이 이미 있으면
                                if userLectureCard:
                                    userLectureCard = AttendanceCard.objects.get(checker=userprofile,record_to=activateRecord)
                                    userLectureCard.beacon_checker = True
                                    userLectureCard.is_late_checker = False
                                    userLectureCard.is_reasonableabsent_checker = False
                                    userLectureCard.is_absent_checker = False
                                    userLectureCard.save()
                                    return Response("Completed attendance", status=status.HTTP_200_OK)

                                # 없으면 생성
                                else:

                                    card = AttendanceCard.objects.create(
                                        checker=userprofile,
                                        record_to=activateRecord,
                                        check_time=timezone.now(),
                                        check_start_time=activateRecord.start_time,
                                        beacon_checker = True
                                    )
                                    card.save()
                                    return Response("Completed attendance", status=status.HTTP_200_OK)

                        return Response("UUID values ​​do not match", status=status.HTTP_403_FORBIDDEN)#UUID값이 일치하지 않음


                #강좌의 인증시간이 끝나 지각처리를 받을 때
                elif activateRecord.activate==False:
                    if lectureUuid.uuid_now == serializer.validated_data['lectureUuid']:
                        userInfo = User.objects.get(username=request.user)
                        userprofile = StudentProfile.objects.get(user=userInfo)
                        userLectureCard = AttendanceCard.objects.filter(checker=userprofile,record_to=activateRecord)



                        # 시차 차이에 의한 UUID값의 허용 중단플래그 설정
                        if (((timezone.now() > lectureUuid.init_time - datetime.timedelta(minutes=1)) or (
                                    timezone.now() < lectureUuid.init_time - datetime.timedelta(minutes=9)))):
                            if lectureUuid.time_difference_check_flag == True:
                                lectureUuid.time_difference_check_flag = False
                                lectureUuid.time_difference = False
                        else:
                            lectureUuid.time_difference_check_flag = False
                            lectureUuid.time_difference = True
                        lectureUuid.save()

                        # 학생 기록이 없으면
                        if not userLectureCard:
                            card = AttendanceCard.objects.create(
                                beacon_checker = True,
                                checker=userprofile,
                                record_to=activateRecord,
                                check_time=timezone.now(),
                                check_start_time=activateRecord.start_time,
                                is_late_checker=True,
                                is_reasonableabsent_checker=False,
                                is_absent_checker=False
                            )
                            card.save()
                            return Response("Completed late", status=status.HTTP_200_OK)#지각 완료

                        # 학생 출결이 이미 있으면 결석 > 지각
                        elif userLectureCard.last().is_absent_checker== True:
                            userLectureCard = AttendanceCard.objects.get(checker=userprofile,record_to=activateRecord)
                            userLectureCard.beacon_checker = True
                            userLectureCard.is_late_checker = True
                            userLectureCard.is_reasonableabsent_checker = False
                            userLectureCard.is_absent_checker = False
                            userLectureCard.save()
                            return Response("Completed late", status=status.HTTP_200_OK)

                    else:
                        if (((timezone.now() > lectureUuid.init_time - datetime.timedelta(minutes=1)) or (timezone.now() < lectureUuid.init_time - datetime.timedelta(minutes=9))) and (lectureUuid.time_difference == True)):

                            userInfo = User.objects.get(username=request.user)
                            userprofile = StudentProfile.objects.get(user=userInfo)
                            userLectureCard = AttendanceCard.objects.filter(checker=userprofile,record_to=activateRecord)

                            #이전, 다음 UUID와 일치
                            if lectureUuid.uuid_pre == serializer.validated_data['lectureUuid'] or lectureUuid.uuid_next == serializer.validated_data['lectureUuid']:
                                lectureUuid.time_difference_check_flag = True
                                activateRecord.save()
                                # 학생 기록이 없으면
                                if not userLectureCard:
                                    card = AttendanceCard.objects.create(
                                        beacon_checker = True,
                                        checker=userprofile,
                                        record_to=activateRecord,
                                        check_time=timezone.now(),
                                        check_start_time=activateRecord.start_time,
                                        is_late_checker=True,
                                        is_reasonableabsent_checker=False,
                                        is_absent_checker=False
                                    )
                                    card.save()
                                    return Response("Completed late", status=status.HTTP_200_OK)

                                # 학생 출결이 이미 있으면 결석 > 지각
                                elif userLectureCard.last().is_absent_checker == True:
                                    userLectureCard = AttendanceCard.objects.get(checker=userprofile, record_to=activateRecord)
                                    userLectureCard.beacon_checker = True
                                    userLectureCard.is_late_checker = True
                                    userLectureCard.is_reasonableabsent_checker = False
                                    userLectureCard.is_absent_checker = False
                                    userLectureCard.save()
                                    return Response("Completed late", status=status.HTTP_200_OK)


                        return Response("UUID values ​​do not match", status=status.HTTP_403_FORBIDDEN)
                return Response("Activate lecture is not found", status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Unknown User request", status=status.HTTP_403_FORBIDDEN)