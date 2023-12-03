import random

def generate_otp(length=6):
    digits = "0123456789"
    otp = ""

    for _ in range(length):
        otp += random.choice(digits)
    return otp

import requests


def send_otp_via_sms():
    api_key = "d56dd1b2-6aa9-11ee-addf-0200cd936042"
    phone_number = "917075333315"
    sms_request_id = "tryksl"
    otp_value = "1234"
    otp_template_name = "SmsOtp"

    # API endpoint for sending OTP
    url = f'https://2factor.in/API/V1/{api_key}/SMS/{phone_number}/{otp_value}/{otp_template_name}'

    # Make the API request
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        result = response.json()
        if result["Status"] == "Success":
            print("OTP Sent Successfully")
            # You can also retrieve the unique SMS request id for future verification
            sms_request_id = result["Details"]
            print(f"SMS Request ID: {sms_request_id}")
        else:
            print(f"Failed to send OTP. Details: {result['Details']}")
    else:
        print(f"Failed to send OTP. Status Code: {response.status_code}")
        print(response.text)


