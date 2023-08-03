import random

def generate_otp(length=6):
    digits = "0123456789"
    otp = ""

    for _ in range(length):
        otp += random.choice(digits)
    return otp