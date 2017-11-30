
//var token = "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InByb2Zlc3NvcjEiLCJvcmlnX2lhdCI6MTUxMDU1NTEwOSwidXNlcl9pZCI6MTcsImVtYWlsIjoicHJvZmVzc29yMUBkanUuYWMua3IiLCJleHAiOjE1MTA2MTUxMDl9.TwFWXxuA7aiqOMHTS0RZZwumS1KDdgmoafJOI69kNZQ";
var token;

var app = angular.module('BioBeaconApp', []);
app.controller('BioBeaconController', function($scope, $http){



    $scope.completeLogin = function (){
        $scope.LoginPage = false;
        $scope.VirtualClassPage = true;

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

        }, function (response){
        //error
            alert(response);
        });

    };

});

app.controller('RegisterController', function ($scope, $http){

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
            "department" : $scope.selectedDepartment
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

                }, function(response) {

                });
            }
            else {
                   var hole_error ="비밀번호 확인 일치하지 않습니다.";
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

});

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

app.controller('LectureAttendanceCheckController', function($scope, $http){
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
            for ( index in students ){
                student = students[index];
                myDataView.add({id: student.id, ImgSRC: "/static/attendance_check/img/default_profile.jpg", Content: student.student_id});
            }



        }, function(response){


        });


    };
});