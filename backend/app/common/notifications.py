from flask import render_template_string, current_app, jsonify
from app.common.enum import MediaTypeEnum
from app.security.mail import send_email
from app.templates_content.service import TemplatesContentService
from app.utilities.error_utils import handle_errors  # Import the decorator


@handle_errors("Notification")
def item_approve_offline_payment(data, send=True):
    user = data['user']
    item = data['item']
    local = 'ar'
    if user['language']:
        local = user['language'] if isinstance(user['language'], str) else user['language'].value
    message = None

    templates, status = TemplatesContentService().get_templates_contents_by_key_default('approve_offline_pay', item['owner_id'])  # or item['owner_id']
    for template in templates:
        if status != 200 or template is None:
            message = 'Item {{item.title.en}} has been successfully paid at {{item.total}} OMR'.format(**item)
        else:
            message = render_template_string(template['content'][local], item=item, user=user)

        if send:
            #if template['media_type'] == MediaTypeEnum.SMS.value:
                #    SMSNotificationService().send_sms(str(user['phone']), message)
                #elif template['media_type'] == MediaTypeEnum.EMAIL.value:
                    # send email for testing
            send_email(user['email'], template['subject'][local], message)

    return message


@handle_errors("Notification")
def item_reject_offline_payment(data, send=True):
    user = data['user']
    item = data['item']
    local = 'ar'
    if user['language']:
        local = user['language'] if isinstance(user['language'], str) else user['language'].value

    message = None

    templates, status = TemplatesContentService().get_templates_contents_by_key_default('reject_offline_pay', item['owner_id'])  # or item['owner_id']

    for template in templates:
        if status != 200 or template is None:
            message = 'The payment of Item {{item.title.en}} has been rejected.'.format(**item)
        else:
            message = render_template_string(template['content'][local], item=item, user=user)

        if send:
            #if template['media_type'] == MediaTypeEnum.SMS.value:
                #    SMSNotificationService().send_sms(str(user['phone']), message)
                #elif template['media_type'] == MediaTypeEnum.EMAIL.value:
                    # send email for testing
            send_email(user['email'], template['subject'][local], message)

    return message