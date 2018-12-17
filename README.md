#  BioBeacon 출석체크 시스템

 [iBeacon](https://ko.wikipedia.org/wiki/%EC%95%84%EC%9D%B4%EB%B9%84%EC%BD%98)을 사용한 자동화 출석 체크 시스템. 기존 iBeacon만 사용한 시스템과 달리 생체인식(지문 or 얼굴인식)을 도입하여, 대리 출석과 부정 출석을 방지함.

## 주요기능
- 강좌 개설 및 수강 신청.
- 회원가입
- [안드로이드 전용 앱](https://github.com/interruping/biobeacon-client-android) 사용.
- Beacon과 지문 or 얼굴인식을 사용하여 출석 인증.

## 시연 예시
![biobeacontest](https://user-images.githubusercontent.com/29074678/50104888-873b9d80-026e-11e9-9277-37a95ab5ba7e.gif)

##  Requirments
- Django==1.11.17
- djangorestframework==3.9.0
- djangorestframework-jwt==1.11.0
- Pillow==5.3.0
- PyJWT==1.7.1
- pytz==2018.7

## License

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 사항은  [LICENSE](https://raw.githubusercontent.com/interruping/biobeacon/Develop/LICENSE.txt)파일을 참조하세요.

