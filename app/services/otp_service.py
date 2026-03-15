from twilio.rest import Client
import os
from dotenv import load_dotenv
import random;

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
verify_sid = os.getenv('TWILIO_SERVICES_SID')


client = Client(account_sid, auth_token)
async def send_otp(phone):
    otp=generate_otp()
    print(otp)
    # phone = f"+91{phone}"
    # verification = await client.verify.v2.services(verify_sid) \
    #     .verifications \
    #     .create(to=phone, channel="sms")
    return otp


def generate_otp():
    otp=  random.randint(1000,9999)
    return otp