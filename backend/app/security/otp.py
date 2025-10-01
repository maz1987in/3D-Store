import json
import jwt 
import datetime
from app.utilities.common_utils import get_random_digits_value, remove_leading_plus
from config import SecretKey
from flask import render_template_string, current_app, jsonify
from .mail import send_email
from app.templates_content.service import TemplatesContentService

SECRET_KEY = SecretKey().SECRET_KEY

def get_user_otp(data, phone,local):
	try:
		otp = get_random_digits_value(6)
		# send OTP by SMS => data[county_code], data[phone_number]
		# send email for testing
		#message = 'Please use OTP number ({0}) to complete the mobile verification, this OTP expires in 5 minutes.'.format(otp)
		#html = render_template('email.html', message=message)
		#subject = "Please Verify Your Mobile Number."
		#send_email(email, subject, html)
		template, status = TemplatesContentService().get_templates_contents_by_key('user_otp')

		#current_app.logger.error(type(template))
		
		if template is None:
			message = 'Please use OTP number ({0}) to complete the mobile verification, this OTP expires in 5 minutes.	الرجاء استخدام رقم OTP ({{0}}) لإكمال التحقق عبر الهاتف المحمول ، تنتهي صلاحية OTP هذا في 5 دقائق. مزاد عمان'.format(otp)
		else:
			message = render_template_string(template[0]['content'][local], otp=otp)
		mobile = remove_leading_plus(phone)
		#print(otp)
		#SMSNotificationService().send_sms(mobile, message)

		# generate token of OTP 
		token = jwt.encode({'mobile': mobile, 'otp': otp, 'exp' : datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=5)}, SECRET_KEY, "HS256")
		
		return token
	except Exception as e:
		current_app.logger.error(e)
		return None


def verify_OTP(data):
	phone_number = remove_leading_plus(data['phone_number'])
	OTP = data['otp']
	token = data['token']

	try:
		payload = jwt.decode(token, SECRET_KEY, "HS256")
	except Exception as e:
		current_app.logger.error(e)
		return False, phone_number
	
	#current_app.logger.error(payload)
	#current_app.logger.error('{0} - {1}'.format(phone_number,OTP))
	if phone_number == payload['mobile'] and OTP == payload['otp']:
		return True, phone_number
	#if int(phone_number) == int(payload['mobile']) and int(OTP) == int(payload['otp']):
	#	return True, phone_number
	
	return False, phone_number