
//var token = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InByb2Zlc3NvcjEiLCJvcmlnX2lhdCI6MTUxMDU1NTEwOSwidXNlcl9pZCI6MTcsImVtYWlsIjoicHJvZmVzc29yMUBkanUuYWMua3IiLCJleHAiOjE1MTA2MTUxMDl9.TwFWXxuA7aiqOMHTS0RZZwumS1KDdgmoafJOI69kNZQ";
var token;

var app = angular.module('BioBeaconApp', ['ngFileUpload']);

//localStorage.setItem('storedUserAuthData',"no_token");

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

    $scope.doLogin = function(){

        var userAuthData = {
            "username": $scope.login_username,
            "password": $scope.login_password
        };

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

});

app.controller('RegisterController',['$scope', '$http', 'Upload', function ($scope, $http, Upload){

    $http.get("/attendance_check/api/department/list/")
    .then(function (response) {

       $scope.departments = response.data.departments;
       $scope.selectedDepartment = '0';

    }, function (response) {

    })

    $scope.doRegister = function () {

        var regist_form = {
            "username" : $scope.reg_username,
            "email" : $scope.email,
            "password" : $scope.reg_password,
            "confirm-password" : $scope.reg_password_confirm,
            "is_staff" : $scope.user_type,
            "id" : $scope.organization_id,
            "department" : $scope.selectedDepartment,
            "profile_image_id" : $scope.image_id,
        };

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

       if($scope.reg_username !=null && $scope.email != null && $scope.reg_password != null && $scope.reg_password_confirm != null && $scope.organization_id !=null && $scope.selectedDepartment != '0' ){
            if($scope.reg_password == $scope.reg_password_confirm){
                if($scope.profile_image  != null){
                   $http.put("/attendance_check/api/user_register/", regist_form)
                     .then(function(response){
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

            if( $scope.reg_username == null ||
                $scope.email == null ||
                $scope.reg_password == null ||
                $scope.reg_password_confirm == null ||
                 $scope.organization_id == null) {

                if($scope.reg_username ==null){
                  hole_error +="아이디";
                  count=1;
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
            data: {file: file, 'username': $scope.username}
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

            $scope.username = response.data.username;
            $scope.department = response.data.department;
            $scope.id = response.data.id;
            $scope.email = response.data.email;
            $scope.user_type = response.data.user_type;
            $scope.profile_image = response.data.profile_image;

        }, function (response){

        });
    };


});

app.controller('LectureController', function($scope, $http){

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
            $scope.loadLectureList();

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

    $scope.updateSelectedLecture = function () {
        $http.post('/attendance_check/api/lecture/apply/list/', {"lecture": $scope.seletedLecture},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){
            myDataView.clearAll();
            var students = response.data.students;

            for ( index in students ) {
                student = students[index];
                myDataView
                .add({id: student.id,
                ImgSRC: student.profile_image,
                Name: student.name,
                IdNum: student.student_id,
                PanelStatus: waitStatus,
                AttendanceCheckStatus: waitText });
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
        $http.post('/attendance_check/api/lecture/apply/start/', {"id": $scope.seletedLecture, "minute" : $scope.selectedTimeMin},
        {
            headers: {
                'Authorization' : token
            }

        }).then(function(response){

        },function(response){
        });
    };



    var timeInterval;
    $scope.realTimeReset = function () {
        if ($scope.realTime=!null)
            $interval.cancel(timeInterval);
        $scope.realTime = $scope.selectedTimeMin * 60;
        $scope.strColon = " : ";
            timeInterval = $interval(function () {
                $scope.realTime = $scope.realTime -1;
                $scope.realTimeMin = parseInt($scope.realTime/60);
                $scope.realTimeSec = $scope.realTime%60;

        }, 1000,[$scope.selectedTimeMin*60]);
    };


    $scope.selectedTime = {
    1 : {str : "1분", int : 1},
    3 : {str : "3분", int : 3},
    5 : {str : "5분", int : 5},
    10 :{str : "10분", int : 10}
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
};

function onEnterSubmit(){
     var keyCode = window.event.keyCode;
     document.getElementById("login-submit").click();
}

function activeMyInfo() {
    localStorage.setItem('chulCheckActived',"20132308");
}
function activeChulCheck() {
    localStorage.setItem('chulCheckActived',"20132307");
}
function chulcheckJS() {
    const chulCheckInfo = localStorage.getItem('chulCheckActived');

    if (chulCheckInfo == "20132307") {
        $(document).ready(function(){
            $('#chul2').tab('show');
        });
    }
    else if (myInfoInfo == "20132308") {
        $(document).ready(function(){
            $('#chul1').tab('show');
        });
    }
}