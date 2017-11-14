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

class ProfessorProfile(models.Model):
    user = models.OneToOneField(User)
    employee_id = models.IntegerField(unique=True)
    department =  models.ForeignKey(Department)

    def __str__(self):
        return str(self.employee_id)


@python_2_unicode_compatible
class Lecture(models.Model):
    title = models.CharField(max_length=256, default='')
    lecturer = models.ForeignKey(ProfessorProfile)

    def __str__(self):
        return self.title



class AttendanceRecord(models.Model):
    activate = models.BooleanField(default=False)
    start_time = models.DateTimeField(editable=False)
    end_time = models.DateTimeField(editable=False)
    lecture = models.ForeignKey(Lecture)

class StudentProfile(models.Model):
    user = models.OneToOneField(User)
    student_id = models.IntegerField(unique=True)
    Lectures = models.ManyToManyField(Lecture)
    department = models.ForeignKey(Department)

    def __str__(self):
        return str(self.student_id)

class LectureReceiveCard(models.Model):
    target_lecture = models.ForeignKey(Lecture)
    card_owner = models.ForeignKey(StudentProfile)

class AttendanceCard(models.Model):
    check_time = models.DateTimeField(editable=False)
    checker = models.ForeignKey(StudentProfile)
    record_to = models.ForeignKey(AttendanceRecord)
    is_late_checker = models.BooleanField(default=False)




