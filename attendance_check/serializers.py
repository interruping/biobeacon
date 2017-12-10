from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Lecture, ProfessorProfile, StudentProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('last_name','first_name','username', 'password', 'email', 'is_staff')
    def create(self, validated_data):
        user = User.objects.create(
            last_name=validated_data['last_name'],
            first_name = validated_data['first_name'],
            email= validated_data['email'],
            username= validated_data['username'],
            password=make_password(self.validated_data['password']),
            is_staff= validated_data['is_staff']
        )
        user.save()
        return user
class RegistrationSerializer(serializers.Serializer):
    last_name = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=512)
    email = serializers.EmailField()
    is_staff = serializers.BooleanField(default=False)
    id = serializers.IntegerField()
    department = serializers.IntegerField()
    profile_image_id = serializers.IntegerField()

class ProfessorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorProfile
        fields = ('user', 'employee_id', 'department')


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('user', 'student_id', 'department', 'Lectures')


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ('title', 'lecturer_num')

    def create(self, validated_data):

        return validated_data
class LectureListSerializer(serializers.Serializer):
    lecturer = serializers.IntegerField()

class LectureCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    lecture_num = serializers.CharField(min_length=5, max_length=5)

class IdCheckSerializer(serializers.Serializer):
    reg_username = serializers.CharField(max_length=128)

class IdNumberCheckSerializer(serializers.Serializer):
    organization_id = serializers.IntegerField()

class InfoCheckSerializer(serializers.Serializer):
    login_username = serializers.CharField(max_length=128)

class LectureCreateUuidSerializer(serializers.Serializer):
    lecture_num = serializers.CharField(max_length=5)


class LectureStartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    second = serializers.IntegerField()

class LectureUuidSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class LectureRequestAttendanceCheckSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    lecture = serializers.IntegerField()

class LectureReceiveApplySerializer(serializers.Serializer):
    lecture = serializers.IntegerField()


class LectureCheckSerializer(serializers.Serializer):
    status_flag = serializers.CharField(max_length=18)
    std_id = serializers.IntegerField()
    lec_id = serializers.IntegerField()


class LectureCheckedListViewSerializer(serializers.Serializer):
    lecture = serializers.IntegerField()
    time = serializers.CharField(max_length=17)

class LectureBeaconCheckSerializer(serializers.Serializer):
    lecture = serializers.IntegerField()
    uuid_now = serializers.CharField(max_length=32, default='')


class DeleteLectureSerializer(serializers.Serializer):
    id = serializers.CharField()


class ProfileTimeSetSerializer(serializers.Serializer):
    time_set = serializers.CharField()

class LectureRequestSerializer(serializers.Serializer):
    id = serializers.CharField()