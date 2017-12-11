
//var token = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InByb2Zlc3NvcjEiLCJvcmlnX2lhdCI6MTUxMDU1NTEwOSwidXNlcl9pZCI6MTcsImVtYWlsIjoicHJvZmVzc29yMUBkanUuYWMua3IiLCJleHAiOjE1MTA2MTUxMDl9.TwFWXxuA7aiqOMHTS0RZZwumS1KDdgmoafJOI69kNZQ";
var token;

var app = angular.module('BioBeaconApp', ['ngFileUpload']);

//localStorage.setItem('storedUserAuthData',"no_token");



app.controller('SaveLectureTime', function($scope, $http){

    $scope.formData = function (){
        var timeData = {
            "time_set": $scope.formData.e
        };

        $http.post("/attendance_check/api/profile/time_set/update/", timeData,
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

                if(response.data.result == 1)
                    $scope.loadProfile();

            },function(){

            })

    }

});


app.controller('localStorage', function($scope, $http){
    const loggedInfo = localStorage.getItem('storedUserAuthData');

    if (loggedInfo != null) {
        token = loggedInfo;
        $scope.completeLogin();
    }
});

app.controller('BioBeaconController', function($scope, $http){

    $scope.completeLogin = function (){
        $scope.LoginPage = false;
        $scope.VirtualClassPage = true;

    }

     $scope.completeLogout = function (){
        $scope.LoginPage = true;
        $scope.VirtualClassPage = false;
    }

});

app.controller('LogoutController', function($scope, $http){

    $scope.doLogout = function(){
            $scope.completeLogout();
            localStorage.removeItem('storedUserAuthData');
        }
});

app.controller('LoginController', function($scope, $http){

        if(localStorage.getItem('id') != 'null' && localStorage.getItem('pw') != 'null' &&localStorage.getItem('check') == 'true'){
            $scope.login_checkbox = true;
            $scope.login_username = localStorage.getItem('id');
            $scope.login_password = localStorage.getItem('pw');
        }

        else{
          $('#checkbox1').checked = false;
         }

$scope.doInfoCheck = function(){
var login_error;
 var userIdData ={
            "login_username" : $scope.login_username
            };

            $http.post("/attendance_check/api/user_register/info/check/", userIdData)
        .then(function(response){
        //success
             if(response.data.result ==1){
                    $scope.doLogin();

             } else{
                   login_error = "학생은 로그인이 불가합니다. 어플리케이션을 이용해주세요";
                   $("#no_login").html(login_error);
                   $("#login_error").appendTo('body').modal();
                }
        }, function(response){
            login_error = "회원이 아닙니다. 회원신청 바랍니다.";
            $("#no_login").html(login_error);
            $("#login_error").appendTo('body').modal();
            });
  };

    $scope.doLogin = function(){



        var userAuthData = {
            "username": $scope.login_username,
            "password": $scope.login_password
        };

        if(localStorage.getItem('check') == 'true'){
            $('#checkbox1').checked = true;

                if(localStorage.getItem('id') == null || localStorage.getItem('pw') == null){
                      localStorage.setItem('id',$scope.login_username);
                      localStorage.setItem('pw',$scope.login_password);
                }
                 else{
                      if($scope.login_username != localStorage.getItem('id')|| $scope.login_password != localStorage.getItem('pw') ){
                            if($scope.login_username != localStorage.getItem('id')){
                                       localStorage.setItem('id',$scope.login_username);
                            }
                            if($scope.login_password != localStorage.getItem('pw')){
                                       localStorage.setItem('pw',$scope.login_password);
                            }

                      }

                 }


        }

       else{
              localStorage.setItem('check','false');
              localStorage.setItem('id','');
              localStorage.setItem('pw','');
       }


                  $http.post("/attendance_check/api/user_auth/", userAuthData)
                  .then(function(response){
                   //success
                   token = "JWT " + response.data.token;
                   $scope.completeLogin();
                   $scope.login_username = "";
                   $scope.login_password = "";
                   localStorage.setItem('storedUserAuthData',token);

                    }, function (response){
                   //error
                 $("#registration-failed-modal").appendTo("body").modal();
                  });

    };
    $scope.checked_storage = function(state){
         if(state == true){
             localStorage.setItem('check','true');
         }
         else{
             localStorage.setItem('check','false');
         }
    };


});

app.controller('RegisterController',['$scope', '$http', 'Upload', function ($scope, $http, Upload){

 var username_flag = false;
  var id_flag= false;

    $scope.doCheckId = function (){

        var userAuthData = {
            "reg_username": $scope.reg_username
        };

        $http.post("/attendance_check/api/user_register/id/check/", userAuthData)
            .then(function(response){

               if(response.data.result == '1'){
                     if(username_flag == true){
                            username_flag = false;
                            $('[data-toggle="popover"]').popover({placement: 'top', content: "중복된 아이디 입니다."}).popover("show");
                     }
               }
                else{
                     if(username_flag == false){
                           $('[data-toggle="popover"]').popover('hide');
                           username_flag = true;
                     }
                }

        }, function (response){

        });

     };



    $scope.doCheckIdNumber = function (){

        var userAuthNumData = {
            "organization_id": $scope.organization_id
        };

        $http.post("/attendance_check/api/user_register/id/NumberCheck/", userAuthNumData)
        .then(function(response){

            if(response.data.result == '1'){
                if(id_flag == true){
                        id_flag = false;
                        $('[data-toggle="popover1"]').popover({placement: 'top', content: "중복된 학번/사번 입니다."}).popover("show");
                }
            }
            else{
                if(id_flag == false){
                    $('[data-toggle="popover1"]').popover('hide');
                    id_flag = true;
                 }
            }
        }, function (response){

        });

     };

    $http.get("/attendance_check/api/department/list/")
    .then(function (response) {

       $scope.departments = response.data.departments;
       $scope.selectedDepartment = '0';

    }, function (response) {

    })

    $scope.doRegister = function () {

        var regist_form = {
            "first_name" : $scope.reg_firstname,
            "last_name" : $scope.reg_lastname,
            "username" : $scope.reg_username,
            "email" : $scope.email,
            "password" : $scope.reg_password,
            "confirm-password" : $scope.reg_password_confirm,
            "is_staff" : $scope.user_type,
            "id" : $scope.organization_id,
            "department" : $scope.selectedDepartment,
            "profile_image_id" : $scope.image_id,
        };

        if($scope.reg_firstname ==""){
            $scope.reg_firstname = null;
            }

        if($scope.reg_lastname ==""){
            $scope.reg_lastname = null;
            }

        if($scope.reg_username ==""){
            $scope.reg_username = null;
            }
        if($scope.email == ""){
            $scope.email = null;
            }
        if($scope.reg_password == ""){
            $scope.reg_password = null;
            }
        if($scope.reg_password_confirm == ""){
            $scope.reg_password_confirm = null;
            }
        if($scope.organization_id == ""){
            $scope.organization_id = null;
            }

       if($scope.reg_username !=null && $scope.email != null && $scope.reg_firstname != null&& $scope.reg_lastname !=null && $scope.reg_password != null && $scope.reg_password_confirm != null && $scope.organization_id !=null && $scope.selectedDepartment != '0' ){
            if($scope.reg_password == $scope.reg_password_confirm){
                if($scope.profile_image  != null){
                   $http.put("/attendance_check/api/user_register/", regist_form)
                     .then(function(response){
                      $scope.reg_firstname = '';
                      $scope.reg_lastname = '';
                      $scope.reg_username = '';
                      $scope.email = '';
                      $scope.reg_password = '';
                      $scope.reg_password_confirm = '';
                      $scope.user_type = 'true';
                      $scope.organization_id = '';
                      $scope.selectedDepartment = '0';

                      $('#registration-complete-modal').css("z-index", "99999");
                      $('#registration-complete-modal').appendTo("body").modal();

                   },  function(response) {

                         });
                 }
                 else{
                        var subject_error='';
                        var hole_error ="사진을 첨부해주세요.";
                        $('#sub_error_code').html(subject_error);
                        $('#error_code').html(hole_error);
                        $("#error_dialog").appendTo('body').modal();
                  }
            }
            else {
                   var hole_error ="비밀번호 확인이 일치하지 않습니다.";
                    $('#error_code').html(hole_error);
                    $("#error_dialog").appendTo('body').modal();

            }
       } else {
            var hole_error= "";
            var subject_error="";
            var count = 0;

            if( $scope.reg_firstname == null ||
                $scope.reg_lastname == null ||
                $scope.reg_username == null ||
                $scope.email == null ||
                $scope.reg_password == null ||
                $scope.reg_password_confirm == null ||
                 $scope.organization_id == null) {

                if($scope.reg_lastname ==null){
                    hole_error +="성";
                    count=1;
                    }

                 if($scope.reg_firstname==null){
                    if(count==1){
                       hole_error +=",";
                       }
                    else{
                        count =1;
                        }
                    hole_error +="이름";
                 }

                if($scope.reg_username ==null){
                    if(count ==1){
                       hole_error +=",";
                       }
                     else{
                        count =1;
                        }
                    hole_error +="아이디";
                  }

                if($scope.email == null){
                  if(count ==1){
                    hole_error +=",";
                  } else {
                    count=1;
                  }
                  hole_error +="메일";
                }
                if($scope.reg_password == null){
                    if(count ==1){
                        hole_error +=",";
                    } else {
                        count=1;
                    }
                    hole_error +="비밀번호";
                }
                if($scope.reg_password_confirm == null){
                    if(count ==1){
                        hole_error +=",";
                    } else {
                        count=1;
                    }
                    hole_error += "비밀번호 확인"
                }
                if($scope.organization_id == null){
                    if(count ==1){
                        hole_error +=",";
                    } else {
                        count=1;
                    }
                    hole_error += "학번"
                }
                hole_error +="의 값이 올바르지 않습니다. ";
            }

            if($scope.selectedDepartment == '0'){
                subject_error += "학과를 선택하십시오.";
            }


            $('#error_code').html(hole_error);
            $("#sub_error_code").html(subject_error);
            $("#error_dialog").appendTo('body').modal();

        }
    };

    $scope.submitImage = function () {
      if ( $scope.profile_image) {
        $scope.upload($scope.profile_image);
      }
    };




    $('#upload_progress_container').css({'display':'none'});

    $scope.upload = function( file ) {
        $('#upload_progress_container').css({'display':'block'});
        Upload.upload({
            url: '/attendance_check/api/profile/image/upload/',
            data: {'file': file}
        }).then(function (resp) {
            $('#uploaded_image').attr('src', resp.data.uploaded_url);
            $('#image_confirm').collapse();
            $scope.image_id = resp.data.image_id;
        }, function (resp) {

        }, function (evt) {
            var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
            $("#upload_progress").css({'width':progressPercentage + '%'});
            $("#upload_progress").html(progressPercentage + '%');

            if ( progressPercentage >= 100) {
                setTimeout(function(){
                    $('#upload_progress_container').css({'display':'none'});
                }, 700);

            }
        });

    };
}]);

app.controller('ProfileController', function($scope, $http){


    $scope.loadProfile = function () {
        $http.get('/attendance_check/api/profile', {
            headers: {
                'Authorization' : token
            }
        }).then(function(response){
            $scope.lastname =response.data.last_name;
            $scope.firstname = response.data.first_name;
            $scope.username = response.data.username;
            $scope.department = response.data.department;
            $scope.id = response.data.id;
            $scope.email = response.data.email;
            $scope.user_type = response.data.user_type;
            $scope.profile_image = response.data.profile_image;
            $scope.time_set = response.data.time_set;

        }, function (response){

        });
    };


});

app.controller('LectureController', function($scope, $http){

    $scope.deleteLecture = function(num){
        $http.post('/attendance_check/api/lecture/delete/',{"id": num}, {
            headers: {
                'Authorization' : token
            }
        }).then(function(response){
                $scope.loadLectureList();

        },function(response){
             $("#lecture-failed-modal").appendTo("body").modal();
        });

    };

    $scope.loadLectureList = function () {
        $http.get('/attendance_check/api/lecture/list/', {
            headers: {
                'Authorization' : token
            }
        }).then(function(response){
            lecture_list = response.data.lectures;
            $scope.lectures = [];
            for ( index in lecture_list ) {
                $scope.lectures.push(lecture_list[index]);
            }

        }, function (response){
        });
    };

    $scope.registNewLecture = function () {
        $http.post('/attendance_check/api/lecture/create/', {"title": $scope.newLectureTitle, "lecture_num": $scope.newLectureNum},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            if(response.data.result == 1){
            alert("잘못된 입력입니다.");
            }
            $scope.loadLectureList();

            var checkCompare = response.data.failedModal
            if (checkCompare) {
                $("#lecture-failed-modal").appendTo("body").modal();
            }
        }, function (response){
        });
    };

    $scope.createUuidTable = function () {
        $http.post('/attendance_check/api/lecture/createUuid/', {"lecture_num": $scope.newLectureNum},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

        }, function (response){
        });
    };
});

var waitStatus = "default";
var absentStatus = "danger";
var lateStatus = "warning";
var reasonableAbsentStatus = "success";
var checkCompleteStatus = "primary"
var waitText = "출석대기 중";
var absentText = "결석";
var lateText = "지각";
var reasonableAbsentText = "공결";
var checkCompleteText = "출석";

app.controller('LectureAttendanceCheckController', function($scope, $http, $interval){
    $scope.select_entire_control = "0";
    $scope.seletedLecture = "0";

    currentSpecificControl = 0;
    myDataView.attachEvent("onMouseMove", function (id, ev, html){

        if ( currentSpecificControl != id ){
            $('#specificControl_'+ currentSpecificControl).popover('hide');
            currentSpecificControl = id;

        }

        myDataView.unselectAll();

        $('#specificControl_'+ id).popover({
        html : true,
        content: function() {
          var content = $(this).attr("data-popover-content");
          return $(content).children(".popover-body").html();
        },
        title: function() {
          var title = $(this).attr("data-popover-content");
          return $(title).children(".popover-heading").html();
        }});
        $('#specificControl_'+ id).popover('show');
        return true;
    });

    myDataView.attachEvent("onMouseOut", function (ev){
        var id = currentSpecificControl;
        $('#specificControl_'+ id).popover('hide');
        return true;
    });


     $scope.loadLectureList = function () {
        $http.get('/attendance_check/api/lecture/list/', {
            headers: {
                'Authorization' : token
            }
        }).then(function(response){
            lecture_list = response.data.lectures;
            $scope.lectures = [];
            for ( index in lecture_list ) {
                $scope.lectures.push(lecture_list[index]);
            }

        }, function (response){
        });
    };

    $scope.updateSelectedLecture = function () {
        $http.post('/attendance_check/api/lecture/apply/list/', {"lecture": $scope.seletedLecture},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            $scope.realTimeReset(response.data.wait_time);
            if (response.data.lecture_time_record)
                $scope.lectureTimeRecord = "기록날짜:"+response.data.lecture_time_record;
            else
                $scope.lectureTimeRecord = "출석을 시작하지 않으셨습니다."
            myDataView.clearAll();
            var students = response.data.students;

            for ( index in students ) {
                student = students[index];
                myDataView
                .add({id: student.id,
                ImgSRC: student.profile_image,
                Name: student.name,
                IdNum: student.student_id,
                PanelStatus: student.std_status,
                AttendanceCheckStatus: student.std_text});
            }

        }, function(response){


        });

    };

    $scope.updateEntireControl = function() {
        var count = myDataView.dataCount();

        for ( var index = 0; index < count; index++ ) {
            var id = myDataView.idByIndex(index);

            var value = Number($scope.select_entire_control);

            switch ( value ) {
            case 0:
                break;
            case 1:
                myDataView.set(id, {
                    id: id,
                    ImgSRC: myDataView.get(id).ImgSRC,
                    Name:  myDataView.get(id).Name,
                    IdNum:  myDataView.get(id).IdNum,
                    PanelStatus : absentStatus,
                    AttendanceCheckStatus : absentText
                });
                break;
            case 2:
                myDataView.set(id, {
                    id: id,
                    ImgSRC: myDataView.get(id).ImgSRC,
                    Name:  myDataView.get(id).Name,
                    IdNum:  myDataView.get(id).IdNum,
                    PanelStatus : lateStatus,
                    AttendanceCheckStatus : lateText
                });
                break;
            case 3:
                myDataView.set(id, {
                    id: id,
                    ImgSRC: myDataView.get(id).ImgSRC,
                    Name:  myDataView.get(id).Name,
                    IdNum:  myDataView.get(id).IdNum,
                    PanelStatus : reasonableAbsentStatus,
                    AttendanceCheckStatus : reasonableAbsentText
                });
                break;
            case 4:
                myDataView.set(id, {
                    id: id,
                    ImgSRC: myDataView.get(id).ImgSRC,
                    Name:  myDataView.get(id).Name,
                    IdNum:  myDataView.get(id).IdNum,
                    PanelStatus : checkCompleteStatus,
                    AttendanceCheckStatus : checkCompleteText
                    });
                break;

            }


        }
    };
    $scope.startLecture = function () {
        $http.post('/attendance_check/api/lecture/apply/start/', {"id": $scope.seletedLecture, "second" : $scope.selectedTimeMin},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            $scope.updateSelectedLecture()
        },function(response){
        });
    };

    $scope.checkUUID = function () {
        $http.post('/attendance_check/api/lecture/apply/checkUUID/', {"id": $scope.seletedLecture},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

        }, function (response){

        });
    };


    var timeInterval;
    $scope.realTimeReset = function (timeset) {
        if ($scope.realTime=!null)
            $interval.cancel(timeInterval);
        $scope.realTime = timeset;
        $scope.strColon = " : ";
        if (timeset<=1){
            $scope.realTimeMin = 0;
            $scope.realTimeSec = 0;
        }

        else{
            timeInterval = $interval(function () {
                $scope.realTime = $scope.realTime -1;
                $scope.realTimeMin = parseInt($scope.realTime/60);
                $scope.realTimeSec = $scope.realTime%60;

        }, 1000,[timeset]);
        }
    };


    var ainterval;

    $scope.stopRealCheck = function() {
            $interval.cancel(ainterval);
    }


    $scope.continueRealCheck = function() {
            $scope.realTimeCheck();
    }


    $scope.realTimeCheck = function () {

        $interval.cancel(ainterval);

        ainterval = $interval(function () {




                $http.post('/attendance_check/api/lecture/apply/list/', {"lecture": $scope.seletedLecture},
                {
                    headers: { 'Authorization' : token }

                }).then(function(response){

                        var students = response.data.students;

                        for ( index in students ) {
                            student = students[index];
                            myDataView
                            .update(student.id,
                            {id: student.id,
                            ImgSRC: student.profile_image,
                            Name: student.name,
                            IdNum: student.student_id,
                            PanelStatus: student.std_status,
                            AttendanceCheckStatus: student.std_text});
                        }

                    }, function(response){


                    });




        }, 1000,[$scope.realTime]);

    };



    $scope.selectedTime = {
    0 : {str : "없음", int : 1},
    1 : {str : "1분", int : 60},
    2 : {str : "3분", int : 180},
    3 : {str : "5분", int : 300},
    4 :{str : "10분", int : 600}
    }



});


function doCheck() {
    var id = currentSpecificControl;
    myDataView.set(id, {
        id: id,
        ImgSRC: myDataView.get(id).ImgSRC,
        Name:  myDataView.get(id).Name,
        IdNum:  myDataView.get(id).IdNum,
        PanelStatus : checkCompleteStatus,
        AttendanceCheckStatus : checkCompleteText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"check");
    };


};

function doAbsent() {
    var id = currentSpecificControl;
    myDataView.set(id, {
        id: id,
        ImgSRC: myDataView.get(id).ImgSRC,
        Name:  myDataView.get(id).Name,
        IdNum:  myDataView.get(id).IdNum,
        PanelStatus : absentStatus,
        AttendanceCheckStatus : absentText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"absent");
    };
};

function doReasonableAbsent() {
    var id = currentSpecificControl;
    myDataView.set(id, {
        id: id,
        ImgSRC: myDataView.get(id).ImgSRC,
        Name:  myDataView.get(id).Name,
        IdNum:  myDataView.get(id).IdNum,
        PanelStatus : reasonableAbsentStatus,
        AttendanceCheckStatus : reasonableAbsentText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"reasonableAbsent");
    };
};

function doLate() {
    var id = currentSpecificControl;
    myDataView.set(id, {
        id: id,
        ImgSRC: myDataView.get(id).ImgSRC,
        Name:  myDataView.get(id).Name,
        IdNum:  myDataView.get(id).IdNum,
        PanelStatus : lateStatus,
        AttendanceCheckStatus : lateText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"late");
    };
};



function onEnterSubmit(sw){
    if( sw == true){
     var keyCode = window.event.keyCode;
     document.getElementById("login-submit").click();
  }
}
function onEnter(){
        if(window.event.keyCode == 13)
        document.getElementById("login-submit").click();
}

function activeMyInfo() {
    localStorage.setItem('chulCheckActived',"20132308");
}
function activeChulCheck() {
    localStorage.setItem('chulCheckActived',"20132307");
}
function activeChulCheckList() {
    localStorage.setItem('chulCheckActived',"20132309");
}

function chulcheckJS() {
    const chulCheckInfo = localStorage.getItem('chulCheckActived');

    if (chulCheckInfo == "20132307") {
        $(document).ready(function(){
            $('#chul2').tab('show');
        });
    }
    else if (chulCheckInfo == "20132308") {
        $(document).ready(function(){
            $('#chul1').tab('show');
        });
    }
    else if(chulCheckInfo == "20132309") {
        $(document).ready(function(){
            $('#chul3').tab('show');
        });
    }
}


app.controller('specificControlController', function($scope, $http){

    $scope.ng_doCheck = function (std_id, status_flag) {
        $http.post('/attendance_check/api/lecture/apply/check/status/', {"std_id": std_id,"lec_id": $scope.seletedLecture,"status_flag": status_flag},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            if (response.data.StoredLecture) {
                $("#lecture-stored-modal").appendTo("body").modal();
                $interval.cancel(ainterval);
            }
        }, function (response){
        });

    };


});
















/*****************************************************************************************/
/******************************강의기록 페이지 ***********************************************/


app.controller('LectureAttendanceCheckController_list', function($scope, $http, $interval){
    $scope.select_entire_control = "0";
    $scope.seletedLecture = "0";

    currentSpecificControl = 0;
    myDataViewList.attachEvent("onMouseMove", function (id, ev, html){

        if ( currentSpecificControl != id ){
            $('#specificControl_list_'+ currentSpecificControl).popover('hide');
            currentSpecificControl = id;

        }

        myDataViewList.unselectAll();

        $('#specificControl_list_'+ id).popover({
        html : true,
        content: function() {
          var content = $(this).attr("data-popover-content");
          return $(content).children(".popover-body").html();
        },
        title: function() {
          var title = $(this).attr("data-popover-content");
          return $(title).children(".popover-heading").html();
        }});
        $('#specificControl_list_'+ id).popover('show');
        // your code here
        return true;
    });



     $scope.loadLectureList = function () {
        $http.get('/attendance_check/api/lecture/list/', {
            headers: {
                'Authorization' : token
            }
        }).then(function(response){
            lecture_list = response.data.lectures;
            $scope.lectures = [];
            for ( index in lecture_list ) {
                $scope.lectures.push(lecture_list[index]);
            }

        }, function (response){
        });
    };


    $scope.updateSelectedLectureTitle = function () {
        $http.post('/attendance_check/api/lecture/list/search/', {"lecture": $scope.seletedLecture},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            $scope.realTimeReset(response.data.wait_time);
            myDataViewList.clearAll();
            var students = response.data.students;

            for ( index in students ) {
                student = students[index];

                if (student.std_status=='default'){
                myDataViewList
                .add({id: student.id,
                ImgSRC: student.profile_image,
                Name: student.name,
                IdNum: student.student_id,
                PanelStatus: absentStatus,
                AttendanceCheckStatus: absentText});
                }


                else{
                myDataViewList
                .add({id: student.id,
                ImgSRC: student.profile_image,
                Name: student.name,
                IdNum: student.student_id,
                PanelStatus: student.std_status,
                AttendanceCheckStatus: student.std_text});
                }
            }

            lecturesTime = response.data.lecturesTime;
            $scope.timeLectures = [];
            for ( index in lecturesTime){
                {
                    $scope.timeLectures.push(lecturesTime[index]);
                }

            }
         });



    };


    $scope.checkedListView = function () {
        $http.post('/attendance_check/api/lecture/list/checked/view/', {"lecture": $scope.seletedLecture, "time": $scope.seletedLectureTime},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            $scope.realTimeReset(response.data.wait_time);
            myDataViewList.clearAll();
            var students = response.data.students;

            for ( index in students ) {
                student = students[index];
                myDataViewList
                .add({id: student.id,
                ImgSRC: student.profile_image,
                Name: student.name,
                IdNum: student.student_id,
                PanelStatus: student.std_status,
                AttendanceCheckStatus: student.std_text});
            }
        }, function(response){
       });
    };



    $scope.updateEntireControl = function() {
        var count = myDataViewList.dataCount();

        for ( var index = 0; index < count; index++ ) {
            var id = myDataViewList.idByIndex(index);

            var value = Number($scope.select_entire_control);

            switch ( value ) {
            case 0:
                break;
            case 1:
                myDataViewList.set(id, {
                    id: id,
                    ImgSRC: myDataViewList.get(id).ImgSRC,
                    Name:  myDataViewList.get(id).Name,
                    IdNum:  myDataViewList.get(id).IdNum,
                    PanelStatus : absentStatus,
                    AttendanceCheckStatus : absentText
                });
                break;
            case 2:
                myDataViewList.set(id, {
                    id: id,
                    ImgSRC: myDataViewList.get(id).ImgSRC,
                    Name:  myDataViewList.get(id).Name,
                    IdNum:  myDataViewList.get(id).IdNum,
                    PanelStatus : lateStatus,
                    AttendanceCheckStatus : lateText
                });
                break;
            case 3:
                myDataViewList.set(id, {
                    id: id,
                    ImgSRC: myDataViewList.get(id).ImgSRC,
                    Name:  myDataViewList.get(id).Name,
                    IdNum:  myDataViewList.get(id).IdNum,
                    PanelStatus : reasonableAbsentStatus,
                    AttendanceCheckStatus : reasonableAbsentText
                });
                break;
            case 4:
                myDataViewList.set(id, {
                    id: id,
                    ImgSRC: myDataViewList.get(id).ImgSRC,
                    Name:  myDataViewList.get(id).Name,
                    IdNum:  myDataViewList.get(id).IdNum,
                    PanelStatus : checkCompleteStatus,
                    AttendanceCheckStatus : checkCompleteText
                    });
                break;

            }


        }
    };

    $scope.checkUUID = function () {
        $http.post('/attendance_check/api/lecture/apply/checkUUID/', {"id": $scope.seletedLecture},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

        }, function (response){

        });
    };


    var timeInterval;
    $scope.realTimeReset = function (timeset) {
        if ($scope.realTime=!null)
            $interval.cancel(timeInterval);
        $scope.realTime = timeset;
        $scope.strColon = " : ";
        if (timeset<=1){
            $scope.realTimeMin = 0;
            $scope.realTimeSec = 0;
        }

        else{
            timeInterval = $interval(function () {
                $scope.realTime = $scope.realTime -1;
                $scope.realTimeMin = parseInt($scope.realTime/60);
                $scope.realTimeSec = $scope.realTime%60;

        }, 1000,[timeset]);
        }
    };

    $scope.selectedTime = {
    0 : {str : "없음", int : 1},
    1 : {str : "1분", int : 60},
    3 : {str : "3분", int : 180},
    5 : {str : "5분", int : 300},
    10 :{str : "10분", int : 600}
    }

});


app.controller('specificControlController_list', function($scope, $http){

    $scope.ng_doCheck = function (std_id, status_flag) {
        $http.post('/attendance_check/api/lecture/apply/check/status/', {"std_id": std_id,"lec_id": $scope.seletedLecture,"status_flag": status_flag},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

        }, function (response){
        });

    };


});



function doCheckList() {
    var id = currentSpecificControl;
    myDataViewList.set(id, {
        id: id,
        ImgSRC: myDataViewList.get(id).ImgSRC,
        Name:  myDataViewList.get(id).Name,
        IdNum:  myDataViewList.get(id).IdNum,
        PanelStatus : checkCompleteStatus,
        AttendanceCheckStatus : checkCompleteText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"check");
    };


};

function doAbsentList() {
    var id = currentSpecificControl;
    myDataViewList.set(id, {
        id: id,
        ImgSRC: myDataViewList.get(id).ImgSRC,
        Name:  myDataViewList.get(id).Name,
        IdNum:  myDataViewList.get(id).IdNum,
        PanelStatus : absentStatus,
        AttendanceCheckStatus : absentText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"absent");
    };
};

function doReasonableAbsentList() {
    var id = currentSpecificControl;
    myDataViewList.set(id, {
        id: id,
        ImgSRC: myDataViewList.get(id).ImgSRC,
        Name:  myDataViewList.get(id).Name,
        IdNum:  myDataViewList.get(id).IdNum,
        PanelStatus : reasonableAbsentStatus,
        AttendanceCheckStatus : reasonableAbsentText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"reasonableAbsent");
    };
};

function doLateList() {
    var id = currentSpecificControl;
    myDataViewList.set(id, {
        id: id,
        ImgSRC: myDataViewList.get(id).ImgSRC,
        Name:  myDataViewList.get(id).Name,
        IdNum:  myDataViewList.get(id).IdNum,
        PanelStatus : lateStatus,
        AttendanceCheckStatus : lateText
    });

    {
    angular.element(document.getElementById('specificControl')).scope().ng_doCheck(currentSpecificControl,"late");
    };
};