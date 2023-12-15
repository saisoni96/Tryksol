import random
import requests

def generate_otp(length=6):
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp


def send_otp_via_sms(phone,otp):
    API_KEY = "d56dd1b2-6aa9-11ee-addf-0200cd936042"
    PHONE_NUMBER = "+91"+str(phone)
    SENDER_ID = "trykso"
    VAR1_VALUE = otp
    TEMPLATE_NAME = "Registration_OTP"

    # API endpoint for sending OTP
    url = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey={API_KEY}&to={PHONE_NUMBER}&from={SENDER_ID}&templatename={TEMPLATE_NAME}&var1={VAR1_VALUE}'
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result["Status"] == "Success":
            return True
        else:
            return False
