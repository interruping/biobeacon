from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
# Create your models here.

class Department(models.Model):
    name = models.TextField(max_length=64, unique=True)

    def __str__(self):
        return str(self.pk)

def ImageUploadNameBind(instance, filename):
    ext = filename.split('.')[-1]
    if instance.pk:
        return 'profile_image/{}.{}'.format(instance.pk, ext)
    else:
        pass
     # do something if pk is not there yet


class ProfileImage(models.Model):
    user = models.OneToOneField(User, null=True)
    image = models.ImageField(upload_to=ImageUploadNameBind)

class ProfessorProfile(models.Model):
    user = models.OneToOneField(User)
    employee_id = models.IntegerField(unique=True)
    department =  models.ForeignKey(Department)
    absence_time_set = models.CharField(max_length=2, default=30)
    def __str__(self):
        return str(self.employee_id)


@python_2_unicode_compatible
class Lecture(models.Model):
    title = models.CharField(max_length=256, default='')
    lecturer = models.ForeignKey(ProfessorProfile)
    lecture_num = models.CharField(max_length=5, default='')

    def __str__(self):
        return self.title

class AttendanceRecord(models.Model):
    activate = models.BooleanField(default=False)
    activate_absence = models.BooleanField(default=False)
    start_time = models.DateTimeField(editable=True, null=True)
    end_time = models.DateTimeField(editable=True, null=True)
    absence_time = models.DateTimeField(editable=True, null=True)
    lecture = models.ForeignKey(Lecture)

class StudentProfile(models.Model):
    user = models.OneToOneField(User)
    student_id = models.IntegerField(unique=True)
    department = models.ForeignKey(Department)
    Crypt_rand_N = models.CharField(max_length=6, default='')


    def __str__(self):
        return str(self.student_id)

class LectureReceiveCard(models.Model):
    target_lecture = models.ForeignKey(Lecture)
    card_owner = models.ForeignKey(StudentProfile)

class AttendanceCard(models.Model):
    beacon_checker = models.BooleanField(default=False)
    check_time = models.DateTimeField(editable=False, null=True)
    check_start_time = models.DateTimeField(editable=True, null=True)
    checker = models.ForeignKey(StudentProfile)
    record_to = models.ForeignKey(AttendanceRecord)
    is_late_checker = models.BooleanField(default=False)
    is_reasonableabsent_checker = models.BooleanField(default=False)
    is_absent_checker = models.BooleanField(default=False)

class LectureUuidRecord(models.Model):
    time_difference = models.BooleanField(default=True)
    time_difference_check_flag = models.BooleanField(default=False)
    reachLimiter = models.CharField(max_length=2, default=4)
    default_uuid = models.CharField(max_length=15, default='4a4ece607eb011e')
    lecture_num = models.CharField(max_length=6, default='', primary_key=True)
    prime_num = models.CharField(max_length=10, default=99991)
    secret_key = models.CharField(max_length=10, default=54321)
    init_time = models.DateTimeField(editable=True, default=timezone.now, null=True)
    uuid_now = models.CharField(max_length=32, default='')
    uuid_pre = models.CharField(max_length=32, default='')
    uuid_next = models.CharField(max_length=32, default='')



