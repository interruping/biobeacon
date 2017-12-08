#-*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response

from attendance_check.serializers import ( RegistrationSerializer,
                                           LectureCreateSerializer,
                                           LectureStartSerializer,
                                           LectureRequestAttendanceCheckSerializer,
                                           LectureReceiveApplySerializer,
                                           IdNumberCheckSerializer,
                                           IdCheckSerializer,
                                           InfoCheckSerializer,
                                           DeleteLectureSerializer,
                                           LectureListSerializer,
                                           ProfileTimeSetSerializer,
                                           ProfessorProfileSerializer,
                                           StudentProfileSerializer,
                                           LectureCreateUuidSerializer,
                                           LectureUuidSerializer,
                                           LectureCheckSerializer,
                                           LectureCheckedListViewSerializer,
                                           )

from django.utils import timezone
from .models import ( ProfessorProfile,
                      Lecture,
                      Department,
                      StudentProfile,
                      AttendanceRecord,
                      AttendanceCard,
                      LectureReceiveCard,
                      ProfileImage,
                      LectureUuidRecord,
                      )

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


from . import uuidcalc


import random
from django.utils import timezone
import datetime

from django.core.files import File
# Create your views here.

def mainView(request):

    return render(request, 'attendance_check/main.html')

def mainView(request):

    return render(request, 'attendance_check/main.html')

def loginView(request):

    return render(request, 'attendance_check/login.html')

def virtualClassView(request):

    return render(request, 'attendance_check/virtual_class.html')

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
                'username' : request.user.username,
                'email' : request.user.email,
                'user_type' : u'학생',
                'id' : sdt.student_id,
                'department' : sdt.department.name,
                'profile_image' : std_img.image.url,
            }

            return Response(result)


class LectureCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response("Lecture only can created by staff user.", status=status.HTTP_403_FORBIDDEN)

        serializer = LectureCreateSerializer(data=request.data)

        if serializer.is_valid():
            lecture = Lecture.objects.filter(title=serializer.validated_data['title'],
                                             lecture_num=serializer.validated_data['lecture_num'])

            if lecture:
                lectureL = lecture.reverse()[0]
                lecturer = ProfessorProfile.objects.get(user=request.user)

                # 강의명, 강의실 번호, 등록자(lecturer) 확인
                record = Lecture.objects.filter(title=lectureL, lecturer=lecturer)
                if record:
                    result = {
                        'failedModal': True,
                    }
                    return Response(result)

            professorProfile = ProfessorProfile.objects.get(user=request.user)
            lec = Lecture.objects.create(
                title=serializer.validated_data['title'],
                lecture_num=serializer.validated_data['lecture_num'],
                lecturer=professorProfile,
            )
            lec.save()

            return Response(serializer.data)
        else:
            result = {
            "result" : 1
            }
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(status=status.HTTP_400_BAD_REQUEST)

class LectureListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):

        if request.user.is_staff:
            prof = ProfessorProfile.objects.get(user=request.user)
            lecture_set = Lecture.objects.filter(lecturer=prof)

            lectures = []

            for lecture in lecture_set:
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




class LectureStartView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response("Lecture only can started by staff user.", status=status.HTTP_403_FORBIDDEN)

        serializer = LectureStartSerializer(data=request.data)
        if serializer.is_valid():
            lecture = Lecture.objects.get(pk=serializer.validated_data['id'])

            # 해당 강의의 활성화 여부 찾기
            record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
            #해당 강의의 활성화유무 판단 활성화되면
            if record:
                record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                if (record.end_time<timezone.now()):
                    record.activate = False
                    record.save()

            #해당 강의의 활성화 여부 재검색
            record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
            # 활성화된 강좌가 있으면
            if record:
                record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                record.end_time=timezone.now() + datetime.timedelta(seconds = serializer.validated_data['second'])

            #활성화된 강좌가 없으면
            else:
                lecturer = ProfessorProfile.objects.get(user = request.user)
                record = AttendanceRecord.objects.create(
                    activate = True,
                    start_time = timezone.now(),
                    end_time = timezone.now()  + datetime.timedelta(seconds = serializer.validated_data['second']),
                    lecture = lecture,
                    absence_time=timezone.now() + datetime.timedelta(minutes=(int)(lecturer.absence_time_set))
                )

            record.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LectureStopView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response("Lecture only can stopped by staff user.", status=status.HTTP_403_FORBIDDEN)

        serializer = LectureStartSerializer(data=request.data)
        if serializer.is_valid():
            lecture = Lecture.objects.get(pk=serializer.validated_data['id'])
            record = AttendanceRecord.objects.get(lecture=lecture)
            record.activate = False
            record.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LectureRequestAttendaneCheck(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        serializer = LectureRequestAttendanceCheckSerializer(data=request.data)

        if request.user.is_staff:

            if serializer.is_valid():


                student = StudentProfile.objects.get(user=User.objects.get(pk=serializer.validated_data['user']))



                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])

                is_received = LectureReceiveCard.objects.get(card_owner=student, target_lecture=lecture)

                if not is_received:
                    return Response("You are not received this Lecture.", status=status.HTTP_403_FORBIDDEN)

                record = lecture.attendancerecord_set.get(activate=True)

                if not record:
                    return Response("Not Exist Activate Lecture.", status=status.HTTP_403_FORBIDDEN)

                allow_seconds = ( record.start_time - record.end_time ).seconds

                is_late = False
                if  (record.end_time - timezone.now()).seconds < allow_seconds :
                    is_late = False
                else :
                    is_late = True

                override_check = AttendanceCard.objects.get(checker=student, record_to=record)
                if override_check:
                    return Response("Already checked in this Lecture.", status=status.HTTP_403_FORBIDDEN)

                card = AttendanceCard.objects.create(
                    check_time = datetime.datetime.now(),
                    checker = student,
                    record_to = record,
                    is_late_checker =  is_late
                )
                card.save()

                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:

            if serializer.is_valid():

                student = StudentProfile.objects.get(user=request.user)

                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])

                is_received = LectureReceiveCard.objects.filter(card_owner=student, target_lecture=lecture)

                if not is_received.exists():
                    return Response("You are not received this Lecture.", status=status.HTTP_403_FORBIDDEN)

                record_set = lecture.attendancerecord_set.filter(activate=True)

                if not record_set.exists():
                    return Response("Not Exist Activate Lecture.", status=status.HTTP_403_FORBIDDEN)

                record = record_set.first()
                allow_seconds = (record.start_time - record.end_time).seconds

                is_late = False
                if (record.end_time - timezone.now()).seconds < allow_seconds:
                    is_late = False
                else:
                    is_late = True

                override_check = AttendanceCard.objects.filter(checker=student, record_to=record)
                if override_check.exists():
                    return Response("Already checked in this Lecture.", status=status.HTTP_403_FORBIDDEN)

                card = AttendanceCard.objects.create(
                    check_time=datetime.datetime.now(),
                    checker=student,
                    record_to=record,
                    is_late_checker=is_late
                )
                card.save()

                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LectureRecordStatusView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        if request.user.is_staff:
            prof = ProfessorProfile.objects.get(user=request.user)
            lecture = Lecture.objects.get(lecturer=prof)
            record = AttendanceRecord.objects.get(activate=True, lecture=lecture)
            cards = record.attendancecard_set.values()

            return Response(cards)
        else:
            return Response("Lecture Record Status can read by staff user.", status=status.HTTP_403_FORBIDDEN)

class LectureDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):

        serializer = DeleteLectureSerializer(data=request.data)

        if serializer.is_valid():
            id = serializer.validated_data['id']

            if request.user.is_staff:
                prof = Lecture.objects.get(pk=id)
                prof.delete()
                result = {
                    "result": 1
                }
            return Response(result)

        else:
            return Response("Lecture Error.", status=status.HTTP_403_FORBIDDEN)



class ProfileTimeSetView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):

        serializer = ProfileTimeSetSerializer(data=request.data)

        if serializer.is_valid():
            time_set = serializer.validated_data['time_set']

            if request.user.is_staff:
                prof = ProfessorProfile.objects.get(user=request.user)
                prof.absence_time_set = time_set
                prof.save()

                result = {
                    "result": 1
                }
            return Response(result)

        else:
            return Response("Lecture Error.", status=status.HTTP_403_FORBIDDEN)



class LectureReceiveApplyView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            serializer = LectureReceiveApplySerializer(data = request.data)

            if serializer.is_valid():
                student = StudentProfile.objects.get(user=request.user)
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                receive_card = LectureReceiveCard.objects.create(
                    target_lecture = lecture,
                    card_owner = student
                )
                receive_card.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply can only student", status=status.HTTP_403_FORBIDDEN)

class LectureReceiveApplyListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureReceiveApplySerializer(data = request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                cards = LectureReceiveCard.objects.filter(target_lecture=lecture)

                ######
                # 해당 강의의 활성화 여부 찾기
                record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                # 해당 강의의 활성화유무 판단 활성화되면
                if record:
                    record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                    # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                    if (record.end_time < timezone.now()):
                        record.activate = False
                        record.save()
                ######

                #활성 강의 남은시간 계산
                activate_lec_card = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                wait_time = 1
                if activate_lec_card:
                    lec_card = activate_lec_card.last()
                    wait_time = (lec_card.end_time.minute*60+lec_card.end_time.second) - (timezone.now().minute*60+timezone.now().second)
                    if wait_time<0:
                        wait_time = 1
                #


                student_infos = []
                selectLecture = AttendanceRecord.objects.filter(lecture=lecture)
                check_start_time = ''
                if selectLecture:
                    check_start_time = selectLecture.last().start_time
                for card in cards:
                    std_text = ''
                    try :
                        std_card = AttendanceCard.objects.get(checker = card.card_owner, record_to=selectLecture.last())
                    except:
                        std_text = "출석대기 중"
                        std_status = 'default'

                    if std_text == '':
                        if std_card.is_reasonableabsent_checker == True:
                            std_text = '공결'
                            std_status = 'success'

                        elif std_card.is_late_checker == True:
                            std_text = '지각'
                            std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            std_text = '출석'
                            std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.username,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text.decode('utf-8')),
                        "std_status":(std_status)
                    }
                    student_infos.append(student_info)

                result = {
                    "wait_time" : wait_time,
                    "students" : student_infos
                }
                return Response(result)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply List only can read by student", status=status.HTTP_403_FORBIDDEN)


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

def Create_rand_N():
    N = random.randint(1, 99999)
    while (N % 99991 == 0):
        N = random.randint(1, 99999)
    return N


#강의생성 시 해당 강의실의 uuid데이터베이스 테이블이 없으면 생성함
class LectureCreateuuidView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = LectureCreateUuidSerializer(data=request.data)
        if serializer.is_valid():
            lectureuuidtest = LectureUuidRecord.objects.filter(lecture_num = serializer.validated_data['lecture_num'])
            if not lectureuuidtest:
                record = LectureUuidRecord.objects.create(
                    lecture_num=serializer.validated_data['lecture_num']
                )
                record.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#UUID갱신 확인
class LectureCheckUUID(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = LectureUuidSerializer(data=request.data)
        if serializer.is_valid():
            try:
                #강의실 번호에따른 강의실 UUID데이터베이스 가져옴
                lecture = Lecture.objects.get(id = serializer.validated_data['id'])
                lectureuuid = LectureUuidRecord.objects.get(lecture_num=lecture.lecture_num)

                #지정한 강의실 UUID 갱신기간이 넘어가면 수행
                if lectureuuid.init_time <= timezone.now():
                    secret_key = (int)(lectureuuid.secret_key)
                    prime_num = (int)(lectureuuid.prime_num)

                    # UUID값을 계산하여 저장 now현재 pre이전 next다음
                    # UUID_calc(prime_num, secret_key, default_uuid, 강의실번호)
                    lectureuuid.uuid_now =  (uuidcalc.UUID_calc_now(prime_num, secret_key, lectureuuid.default_uuid,
                                                  lecture.lecture_num))
                    lectureuuid.uuid_pre =  (uuidcalc.UUID_calc_pre(prime_num, secret_key, lectureuuid.default_uuid,
                                                  lecture.lecture_num))
                    lectureuuid.uuid_next =  (uuidcalc.UUID_calc_next(prime_num, secret_key, lectureuuid.default_uuid,
                                                  lecture.lecture_num))
                    #다음 uuid값이 변경해야할 값을 저장
                    lectureuuid.init_time = timezone.now() + datetime.timedelta(minutes=uuidcalc.addTime(timezone.now().minute)) - datetime.timedelta(seconds=timezone.now().second)
                    lectureuuid.save()

            except:
                return Response()



            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 출석체크값 저장
class LectureStuCheck(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = LectureCheckSerializer(data=request.data)
        if serializer.is_valid():
            stu_num = StudentProfile.objects.get(pk = serializer.validated_data['std_id'])#체크한 학번
            lecture = Lecture.objects.get(pk = serializer.validated_data['lec_id'])#선택강의


            if AttendanceRecord.objects.filter(lecture = lecture):#최신 활성 강의기록
                attendanceRecord = AttendanceRecord.objects.filter(lecture=lecture).last()

            # 강의 활성화가 있으면
            if attendanceRecord:
                #학생의 출석카드가 만들어진 경우 ex)출석 대기상태가 아닌 결석,지각,공결 등의 상태일경우 해당
                if AttendanceCard.objects.filter(checker = stu_num, check_start_time = attendanceRecord.start_time):
                    attendanceCard = AttendanceCard.objects.get(checker = stu_num, record_to = attendanceRecord)

                #학생의 출석체크가 이루어지지 않은 출석 대기상태
                else:
                    createCard = AttendanceCard.objects.create(
                        checker = stu_num,
                        record_to = attendanceRecord,
                        check_time = timezone.now(),
                        check_start_time = attendanceRecord.start_time,
                    )
                    createCard.save()
                    attendanceCard = AttendanceCard.objects.get(checker=stu_num, record_to = attendanceRecord)

                #출석
                if serializer.validated_data['status_flag']=='check':
                    attendanceCard.is_late_checker = False
                    attendanceCard.is_reasonableabsent_checker = False
                    attendanceCard.is_absent_checker = False


                #지각
                elif serializer.validated_data['status_flag']=='late':
                    attendanceCard.is_late_checker = True
                    attendanceCard.is_reasonableabsent_checker = False
                    attendanceCard.is_absent_checker = False

                #공결
                elif serializer.validated_data['status_flag'] == 'reasonableAbsent':
                    attendanceCard.is_late_checker = False
                    attendanceCard.is_reasonableabsent_checker = True
                    attendanceCard.is_absent_checker = False

                #결석
                else:
                    attendanceCard.is_late_checker = False
                    attendanceCard.is_reasonableabsent_checker = False
                    attendanceCard.is_absent_checker = True

                attendanceCard.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LectureListSearch(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureReceiveApplySerializer(data = request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                cards = LectureReceiveCard.objects.filter(target_lecture=lecture)

                ######
                # 해당 강의의 활성화 여부 찾기
                record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                # 해당 강의의 활성화유무 판단 활성화되면
                if record:
                    record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                    # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                    if (record.end_time < timezone.now()):
                        record.activate = False
                        record.save()
                ######

                #활성 강의 남은시간 계산
                activate_lec_card = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                wait_time = 1
                if activate_lec_card:
                    lec_card = activate_lec_card.last()
                    wait_time = (lec_card.end_time.minute*60+lec_card.end_time.second) - (timezone.now().minute*60+timezone.now().second)
                    if wait_time<0:
                        wait_time = 1


                #db에서 학생 출결상태 출력
                student_infos = []
                selectLecture = AttendanceRecord.objects.filter(lecture=lecture)
                check_start_time = ''
                if selectLecture:
                    check_start_time = selectLecture.last().start_time
                for card in cards:
                    std_text = ''
                    try :
                        std_card = AttendanceCard.objects.get(checker = card.card_owner, check_start_time=check_start_time)
                    except:
                        std_text = "출석대기 중"
                        std_status = 'default'

                    if std_text == '':
                        if std_card.is_reasonableabsent_checker == True:
                            std_text = '공결'
                            std_status = 'success'

                        elif std_card.is_late_checker == True:
                            std_text = '지각'
                            std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            std_text = '출석'
                            std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.username,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text.decode('utf-8')),
                        "std_status":(std_status)
                    }
                    student_infos.append(student_info)
                #강의 날짜별로 정리
                if selectLecture:
                    lecturesTime = []
                    num = 1
                    for lecture in selectLecture:
                        lecturesTime.append({
                                "date": (str)(lecture.start_time)[0:16],
                                "id": lecture.pk,
                                "num": num
                            })

                        num+=1



                # 결과값
                result = {
                    "wait_time" : wait_time,
                    "students" : student_infos,
                    "lecturesTime": lecturesTime
                }
                return Response(result)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply List only can read by student", status=status.HTTP_403_FORBIDDEN)



class LectureCheckedSearchView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureCheckedListViewSerializer(data = request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                cards = LectureReceiveCard.objects.filter(target_lecture=lecture)

                ######
                # 해당 강의의 활성화 여부 찾기
                record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                # 해당 강의의 활성화유무 판단 활성화되면
                if record:
                    record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                    # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                    if (record.end_time < timezone.now()):
                        record.activate = False
                        record.save()
                ######

                #활성 강의 남은시간 계산
                activate_lec_card = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                wait_time = 1
                if activate_lec_card:
                    lec_card = activate_lec_card.last()
                    wait_time = (lec_card.end_time.minute*60+lec_card.end_time.second) - (timezone.now().minute*60+timezone.now().second)
                    if wait_time<0:
                        wait_time = 1


                #db에서 학생 출결상태 출력
                student_infos = []
                selectLecture = AttendanceRecord.objects.get(pk=serializer.validated_data['time'])
                for card in cards:
                    std_text = ''
                    try :
                        std_card = AttendanceCard.objects.get(checker = card.card_owner, record_to=selectLecture)
                    except:
                        std_text = "결석"
                        std_status = 'danger'

                    if std_text == '':
                        if std_card.is_reasonableabsent_checker == True:
                            std_text = '공결'
                            std_status = 'success'

                        elif std_card.is_late_checker == True:
                            std_text = '지각'
                            std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            std_text = '출석'
                            std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.username,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text.decode('utf-8')),
                        "std_status":(std_status)
                    }
                    student_infos.append(student_info)



                # 결과값
                result = {
                    "wait_time" : wait_time,
                    "students" : student_infos
                }
                return Response(result)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply List only can read by student", status=status.HTTP_403_FORBIDDEN)




class LectureBeaconCheck(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user:
            serializer = LectureCheckedListViewSerializer(data = request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                cards = LectureReceiveCard.objects.filter(target_lecture=lecture)

                ######
                # 해당 강의의 활성화 여부 찾기
                record = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                # 해당 강의의 활성화유무 판단 활성화되면
                if record:
                    record = AttendanceRecord.objects.get(lecture=lecture, activate=True)
                    # 해당강의의 시작시간과 종료시간을 보고 활성화 변경
                    if (record.end_time < timezone.now()):
                        record.activate = False
                        record.save()
                ######

                #활성 강의 남은시간 계산
                activate_lec_card = AttendanceRecord.objects.filter(lecture=lecture, activate=True)
                wait_time = 1
                if activate_lec_card:
                    lec_card = activate_lec_card.last()
                    wait_time = (lec_card.end_time.minute*60+lec_card.end_time.second) - (timezone.now().minute*60+timezone.now().second)
                    if wait_time<0:
                        wait_time = 1


                #db에서 학생 출결상태 출력
                student_infos = []
                selectLecture = AttendanceRecord.objects.get(pk=serializer.validated_data['time'])
                for card in cards:
                    std_text = ''
                    try :
                        std_card = AttendanceCard.objects.get(checker = card.card_owner, record_to=selectLecture)
                    except:
                        std_text = "결석"
                        std_status = 'danger'

                    if std_text == '':
                        if std_card.is_reasonableabsent_checker == True:
                            std_text = '공결'
                            std_status = 'success'

                        elif std_card.is_late_checker == True:
                            std_text = '지각'
                            std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            std_text = '출석'
                            std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.username,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text.decode('utf-8')),
                        "std_status":(std_status)
                    }
                    student_infos.append(student_info)



                # 결과값
                result = {
                    "wait_time" : wait_time,
                    "students" : student_infos
                }
                return Response(result)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply List only can read by student", status=status.HTTP_403_FORBIDDEN)

