#-*- coding: utf-8 -*-
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response

from attendance_check.serializers import ( LectureCreateSerializer,
                                           LectureStartSerializer,
                                           LectureReceiveApplySerializer,
                                           DeleteLectureSerializer,
                                           ProfileTimeSetSerializer,
                                           LectureCreateUuidSerializer,
                                           LectureUuidSerializer,
                                           LectureCheckSerializer,
                                           LectureRequestSerializer,
                                           LectureCheckedListViewSerializer,
                                           LectureBeaconReachSetSerializer)

from attendance_check.models import ( ProfessorProfile,
                                      Lecture,
                                      StudentProfile,
                                      AttendanceRecord,
                                      AttendanceCard,
                                      LectureReceiveCard,
                                      ProfileImage,
                                      LectureUuidRecord,
                                      )
from attendance_check import uuidcalc
from django.utils import timezone
import datetime


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

class LectureStartView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if not request.user.is_staff:
            return Response("Lecture only can started by staff user.", status=status.HTTP_403_FORBIDDEN)

        serializer = LectureStartSerializer(data=request.data)
        if serializer.is_valid():
            lecture = Lecture.objects.get(pk=serializer.validated_data['id'])

            # 해당 강좌의 결석플래그 상태 조정
            recordLate = AttendanceRecord.objects.filter(lecture=lecture, activate_absence=False)
            if recordLate:
                for list in recordLate:
                    if list.absence_time < timezone.now():
                        list.activate_absence = True
                        list.save()

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

            selectLecture = AttendanceRecord.objects.filter(lecture=lecture)
            check_start_time_record = ((str)(selectLecture.last().start_time))[0:16]

            result = {
                "serializer.data": serializer.data,
                "check_start_time_record": check_start_time_record
            }

            return Response(result)
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


#강의기록 내역 불러오기
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
                            if (std_card.beacon_checker == True):
                                std_text = '지각(B)'
                                std_status = 'warning'
                            else:
                                std_text = '지각'
                                std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            if (std_card.beacon_checker == True):
                                std_text = '출석(B)'
                                std_status = 'primary'
                            else:
                                std_text = '출석'
                                std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.last_name+card.card_owner.user.first_name,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text),
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


class LectureAvailableList(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):
        availableList = Lecture.objects.all()

        results = []
        for list in availableList:
            result = {
                 "lectureList": list.title,
                 "id": list.pk,
            }
            results.append(result)
        return Response(results)

class LectureRequestList (APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request):

        std = StudentProfile.objects.get(user=request.user)
        reqLectureList = LectureReceiveCard.objects.filter(card_owner=std)

        results = []
        for list in reqLectureList:
            result = {
                "lecture":list.target_lecture.title,
                "pk": list.target_lecture.id,
            }
            results.append(result)

        return Response({"result": results})


class LectureBeaconReachSet(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureBeaconReachSetSerializer(data=request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk = serializer.validated_data['lecture'])
                uuidRecord = LectureUuidRecord.objects.get(lecture_num=lecture.lecture_num)
                uuidRecord.reachLimiter = serializer.validated_data['value']
                uuidRecord.save()

                result = {
                    "reachLimiter": uuidRecord.reachLimiter,
                    "lecture_num": lecture.lecture_num,
                }
                return Response(result, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("Beacon reach only can set by student", status=status.HTTP_403_FORBIDDEN)

class LectureBeaconReachView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureReceiveApplySerializer(data=request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk = serializer.validated_data['lecture'])
                uuidRecord = LectureUuidRecord.objects.get(lecture_num=lecture.lecture_num)


                result = {
                    "reachLimiter": uuidRecord.reachLimiter,
                    "lecture_num" : lecture.lecture_num,
                }
                return Response(result, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("Beacon reach view only can set by student", status=status.HTTP_403_FORBIDDEN)

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
            else:
                return Response({"StoredLecture": 1})

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
                # 해당 강좌의 결석플래그 상태 조정
                recordLate = AttendanceRecord.objects.filter(lecture=lecture, activate_absence=False)
                if recordLate:
                    for list in recordLate:
                        if list.absence_time < timezone.now():
                            list.activate_absence = True
                            list.save()

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
                            if (std_card.beacon_checker == True):
                                std_text = '지각(B)'
                                std_status = 'warning'
                            else:
                                std_text = '지각'
                                std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            if (std_card.beacon_checker == True):
                                std_text = '출석(B)'
                                std_status = 'primary'
                            else:
                                std_text = '출석'
                                std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.last_name+card.card_owner.user.first_name,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text),
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


class LectureReceiveApplyListView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):
        if request.user.is_staff:
            serializer = LectureReceiveApplySerializer(data = request.data)
            if serializer.is_valid():
                lecture = Lecture.objects.get(pk=serializer.validated_data['lecture'])
                cards = LectureReceiveCard.objects.filter(target_lecture=lecture)

                # 해당 강좌의 결석플래그 상태 조정
                recordLate = AttendanceRecord.objects.filter(lecture=lecture, activate_absence=False)
                if recordLate:
                    for list in recordLate:
                        if list.absence_time < timezone.now():
                            list.activate_absence = True
                            list.save()
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
                    wait_time = (lec_card.end_time.hour*3600+lec_card.end_time.minute*60+lec_card.end_time.second) - (timezone.now().hour*3600+timezone.now().minute*60+timezone.now().second)
                    if wait_time<0:
                        wait_time = 1



                student_infos = []
                selectLecture = AttendanceRecord.objects.filter(lecture=lecture)
                check_start_time_record = ''
                if selectLecture:
                    check_start_time_record = ((str)(selectLecture.last().start_time))[0:16]
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
                            if (std_card.beacon_checker == True):
                                std_text = '지각(B)'
                                std_status = 'warning'
                            else:
                                std_text = '지각'
                                std_status = 'warning'

                        elif std_card.is_absent_checker == True:
                            std_text = '결석'
                            std_status = 'danger'

                        else:
                            if (std_card.beacon_checker == True):
                                std_text = '출석(B)'
                                std_status = 'primary'
                            else:
                                std_text = '출석'
                                std_status = 'primary'

                    student_info = {
                        "student_id" : card.card_owner.student_id,
                        "id" : card.card_owner.pk,
                        "name" : card.card_owner.user.last_name+card.card_owner.user.first_name,
                        "profile_image": (ProfileImage.objects.get(user=card.card_owner.user)).image.url,
                        "std_text": (std_text),
                        "std_status":(std_status)
                    }


                    student_infos.append(student_info)

                result = {
                    "wait_time" : wait_time,
                    "students" : student_infos,
                    "lecture_time_record" : check_start_time_record
                }
                return Response(result)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Lecture Receive Apply List only can read by student", status=status.HTTP_403_FORBIDDEN)