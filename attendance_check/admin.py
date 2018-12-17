from django.contrib import admin
from attendance_check.models import (Lecture,
                                     AttendanceRecord,
                                     AttendanceCard,
                                     ProfessorProfile,
                                     StudentProfile,
                                     LectureReceiveCard,
                                     Department,
                                     ProfileImage,
                                     Beacon
                                     )

# Register your models here.
admin.site.register(Lecture)
admin.site.register(ProfessorProfile)
admin.site.register(StudentProfile)
admin.site.register(Department)
admin.site.register(AttendanceRecord)
admin.site.register(AttendanceCard)
admin.site.register(LectureReceiveCard)
admin.site.register(ProfileImage)
admin.site.register(Beacon)