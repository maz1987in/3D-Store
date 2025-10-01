from flask_cors import CORS, cross_origin
from flask import Blueprint, current_app, request, jsonify, abort, make_response, render_template
from app.security import permissions
from app.security.mail import send_email

mails = Blueprint('email', __name__)

@mails.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user.show.all'])
def send_email_template(self):
    try:
        #print(request.json)
        if not request.json or 'subject' not in request.json:
            abort(404)

        data = request.json
        html = render_template('email.html', message=data['message'])
        subject = data['subject']

        email = data['email'].split(';')
        if len(email) > 0:
            for e in email:
                send_email(e, subject, html)
            return jsonify({'status': 'OK', 'message': 'Email sent successfully!'}), 201
        return jsonify({'status': 'error', 'message': 'Email not sent!'}), 500
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'status': 'error', 'message': str(e)}), 500