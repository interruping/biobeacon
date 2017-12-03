from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Lecture, ProfessorProfile, StudentProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'is_staff')
    def create(self, validated_data):
        user = User.objects.create(
            email= validated_data['email'],
            username= validated_data['username'],
            password=make_password(self.validated_data['password']),
            is_staff= validated_data['is_staff']
        )
        user.save()
        return user
class RegistrationSerializer(serializers.Serializer):
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
    lecture_num = serializers.CharField(max_length=5)

class LectureCreateUuidSerializer(serializers.Serializer):
    lecture_num = serializers.CharField(max_length=5)

class LectureStartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    minute = serializers.IntegerField()

class LectureRequestAttendanceCheckSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    lecture = serializers.IntegerField()

class LectureReceiveApplySerializer(serializers.Serializer):
    lecture = serializers.IntegerField()
