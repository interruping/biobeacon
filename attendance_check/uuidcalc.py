#-*- coding: utf-8 -*-

import hashlib
import time

now = time.localtime()


#난수의 개수
UUID_Rand= 60


#sorry......if else;;

#UUID계산용입니다

#(prime_num, secret_key, default_uuid, 강의실번호)
def UUID_calc_now(CryptF_X, CryptF_Scret, UUID_Static, UUID_LecNum):
    now = time.localtime()

    if (now.tm_min < 5):
        CryptF_i_time = (((now.tm_min / 10) - 1) % 6 + (
        now.tm_hour - 1) % 24 + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min < 10):
        CryptF_i_time = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min < 15):
        CryptF_i_time = (((now.tm_min / 10) - 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min > 55):
        CryptF_i_time = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min % 10 < 5):
        CryptF_i_time = (((now.tm_min / 10) - 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit
    else:
        CryptF_i_time = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand


    CryptF_N = pow(CryptF_Scret, CryptF_i_time)

    CryptF_Rand = (CryptF_N % CryptF_X) * 100000

    UUID_Front = UUID_Static + UUID_LecNum

    CryptF_Res_hex = int(UUID_Front, 16) - CryptF_Rand

    hashSHA = hashlib.sha256()

    hashSHA.update((str)(CryptF_Res_hex))

    SHA_CrypData = hashSHA.hexdigest()

    SHA_CrypData = SHA_CrypData + SHA_CrypData

    # 하루 지나면 잘못된 계산이 나옴 수정 가능하지만 사용엔 무리 없어서 보류
    CryptF_day_ran_lan = ((int)(now.tm_mday) + (int)(now.tm_mday) % 15 + (int)(now.tm_mon)) % 64

    ReplaceData_res = SHA_CrypData[CryptF_day_ran_lan:CryptF_day_ran_lan + 12]


    Decode_UUID = UUID_Front + ReplaceData_res

    return (Decode_UUID)


# (prime_num, secret_key, default_uuid, 강의실번호)
def UUID_calc_pre(CryptF_X, CryptF_Scret, UUID_Static, UUID_LecNum):
    now = time.localtime()

    if (now.tm_min < 5):
        CryptF_i_pretime = (((now.tm_min / 10) - 2) % 6 + (
        now.tm_hour - 1) % 24 + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min < 10):
        CryptF_i_pretime = (((now.tm_min / 10) - 1) % 6 + (
        now.tm_hour - 1) % 24 + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min < 15):
        CryptF_i_pretime = (((now.tm_min / 10) - 2) % 6 + (
        now.tm_hour - 1) % 24 + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min > 55):
        CryptF_i_pretime = ((( now.tm_min / 10) - 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min % 10 < 5):

        CryptF_i_pretime = (((now.tm_min / 10) - 2) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    else:

        CryptF_i_pretime = (((now.tm_min / 10) - 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand


    CryptF_N = pow(CryptF_Scret, CryptF_i_pretime)

    CryptF_Rand = (CryptF_N % CryptF_X) * 100000

    UUID_Front = UUID_Static + UUID_LecNum

    CryptF_Res_hex = int(UUID_Front, 16) - CryptF_Rand

    hashSHA = hashlib.sha256()

    hashSHA.update((str)(CryptF_Res_hex))

    SHA_CrypData = hashSHA.hexdigest()

    SHA_CrypData = SHA_CrypData + SHA_CrypData

    # 하루 지나면 잘못된 계산이 나옴 수정 가능하지만 사용엔 무리 없어서 보류
    CryptF_day_ran_lan = ((int)(now.tm_mday) + (int)(now.tm_mday) % 15 + (int)(now.tm_mon)) % 64

    ReplaceData_res = SHA_CrypData[CryptF_day_ran_lan:CryptF_day_ran_lan + 12]

    Decode_UUID = UUID_Front + ReplaceData_res

    return (Decode_UUID)


# (prime_num, secret_key, default_uuid, 강의실번호)
def UUID_calc_next(CryptF_X, CryptF_Scret, UUID_Static, UUID_LecNum):
    now = time.localtime()

    if (now.tm_min < 5):
        CryptF_i_nextime = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min < 10):
        CryptF_i_nextime = (((
                             now.tm_min / 10) + 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min < 15):
        CryptF_i_nextime = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    elif (now.tm_min > 55):
        CryptF_i_nextime = (((now.tm_min / 10) + 1) % 6 + (
        now.tm_hour + 1) % 24 + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand
        exit

    elif (now.tm_min % 10 < 5):

        CryptF_i_nextime = (now.tm_min / 10 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand

    else:

        CryptF_i_nextime = (((
                             now.tm_min / 10) + 1) % 6 + now.tm_hour + now.tm_year + now.tm_mon + now.tm_mday) % UUID_Rand


    CryptF_N = pow(CryptF_Scret, CryptF_i_nextime)

    CryptF_Rand = (CryptF_N % CryptF_X) * 100000

    UUID_Front = UUID_Static + UUID_LecNum

    CryptF_Res_hex = int(UUID_Front, 16) - CryptF_Rand

    hashSHA = hashlib.sha256()

    hashSHA.update((str)(CryptF_Res_hex))

    SHA_CrypData = hashSHA.hexdigest()

    SHA_CrypData = SHA_CrypData + SHA_CrypData

    # 하루 지나면 잘못된 계산이 나옴 수정 가능하지만 사용엔 무리 없어서 보류
    CryptF_day_ran_lan = ((int)(now.tm_mday) + (int)(now.tm_mday) % 15 + (int)(now.tm_mon)) % 64

    ReplaceData_res = SHA_CrypData[CryptF_day_ran_lan:CryptF_day_ran_lan + 12]

    Decode_UUID = UUID_Front + ReplaceData_res

    return (Decode_UUID)


#다음 uuid 갱싱시간 구하기
def addTime(mintime):
    timecach = (mintime+5) / 10

    nexttime = ((timecach)*10 - mintime)

    next_mintime = nexttime + mintime +5

    res_mintime = next_mintime - mintime

    return res_mintime

