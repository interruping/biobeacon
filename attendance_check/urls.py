"""biobeacon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from .views import (
                    mainView,
                    loginView,
                    virtualClassView,
                    RegistrationView,
                    InfoCheckView,
                    IdCheckView,
                    IdNumberCheckView,
                    LectureDeleteView,
                    LectureCreateView,
                    LectureStartView,
                    LectureListView,
                    LectureRequestAttendaneCheck,
                    LectureRecordStatusView,
                    LectureReceiveApplyView,
                    LectureReceiveApplyListView,
                    ProfileView,
                    ProfileTimeSetView,
                    DepartmentListView,
                    ProfileImageUploadView,
                    LectureCreateuuidView,
                    LectureCheckUUID,
                    LectureAvailableList,
                    LectureRequestList,
                    LectureRequestView,
                    LectureStuCheck,
                    LectureListSearch,
                    LectureCheckedSearchView,
                    StudentView,
                    LectureFastestView)


from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token

urlpatterns = [
    url(r'^main/$', mainView, name='main'),
    url(r'^login/$', loginView, name='login'),
    # url(r'^main/$', login_view, name='main'),
    url(r'^virtual_class/$', virtualClassView, name='virtual_class'),
    url(r'^$', RedirectView.as_view(url='attendance_check/main/')),


    url(r'^api/user_register/$', RegistrationView.as_view()),
    url(r'^api/user_register/info/check/$', InfoCheckView.as_view()),
    url(r'^api/user_register/id/check/$', IdCheckView.as_view()),
    url(r'^api/user_register/id/NumberCheck/$', IdNumberCheckView.as_view()),
    url(r'^api/user_auth/$', obtain_jwt_token),
    url(r'^api/user_auth/refresh/$', refresh_jwt_token),
    url(r'^api/user_auth/verify/$', verify_jwt_token),

    url(r'^api/profile/$', ProfileView.as_view()),

    url(r'^api/profile/image/upload/$', ProfileImageUploadView.as_view()),
    url(r'^api/profile/time_set/update/$', ProfileTimeSetView.as_view()),

    url(r'^api/department/list/$', DepartmentListView.as_view()),

    url(r'^api/lecture/list/$', LectureListView.as_view()),
    url(r'^api/lecture/create/$', LectureCreateView.as_view()),
    url(r'^api/lecture/delete/$', LectureDeleteView.as_view()),
    url(r'^api/lecture/createUuid/$', LectureCreateuuidView.as_view()),
    url(r'^api/lecture/start/$', LectureStartView.as_view()),
    url(r'^api/lecture/check/$', LectureRequestAttendaneCheck.as_view()),
    url(r'^api/lecture/status/$', LectureRecordStatusView.as_view()),
    url(r'^api/lecture/apply/$', LectureReceiveApplyView.as_view()),
    url(r'^api/lecture/apply/list/$', LectureReceiveApplyListView.as_view()),
    url(r'^api/lecture/apply/start/$', LectureStartView.as_view()),
    url(r'^api/lecture/apply/checkUUID/$', LectureCheckUUID.as_view()),
    url(r'^api/lecture/available/list/$', LectureAvailableList.as_view()),
    url(r'^api/lecture/request/list/$', LectureRequestList.as_view()),
    url(r'^api/lecture/apply/check/status/$', LectureStuCheck.as_view()),
    url(r'^api/lecture/list/search/$', LectureListSearch.as_view()),
    url(r'^api/lecture/list/checked/view/$', LectureCheckedSearchView.as_view()),
    url(r'^api/lecture/request/view/$', LectureRequestView.as_view()),
    url(r'^api/student/view/$', StudentView.as_view()),
    url(r'^api/lecture/fastest/view/$', LectureFastestView.as_view()),

    # url(r'^api/lecture/stop/$', LectureStopView.as_view()),
    # url(r'^api/lecture/check/$', LectureStopView.as_view()),
]
