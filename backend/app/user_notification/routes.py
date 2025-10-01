from flask_cors import CORS, cross_origin
from flask import Blueprint, request, jsonify, abort, make_response, g

from app.security import roles, permissions
from app.common import filters

from .service import UserNotificationService

__uri__ = 'user_notifications'
__blueprint__ = 'user_notifications'

user_notifications = Blueprint(__uri__, __name__)

service = UserNotificationService()

@user_notifications.route('/', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user_notification.show.all'])
@filters.filters
def get_all_user_notifications(filter, self):
    return jsonify(service.getUserNotifications(None,filter))

@user_notifications.route('/<id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user_notification.show.all'])
def get_user_notification(self, id):
    user_notifications = service.getUserNotifications(id, None)
    return jsonify(user_notifications)


@user_notifications.route('/', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user_notification.add'])
def add_user_notification(self):
    if not request.json or not 'user_id' in request.json:
        abort(404)    
    message, status = service.create_userNotification(request.json)
    return jsonify({'msg': message}), status

@user_notifications.route('/<id>', methods=['PATCH'])
#@cross_origin()
@permissions.has_permission(['user_notification.edit'])
def update_user_notification(self,id):
    message, status = service.updateUserNotification(id, request.json)
    return jsonify({'msg': message}), status


@user_notifications.route('/<id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['user_notification.delete'])
def delete_user_notification(self, id):
    message, status = service.delete_userNotification(id)
    return jsonify({'msg': message}), status



@user_notifications.route('/user/<user_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user_notification.show.my'])
@filters.filters
def get_user_notification_by_user_id(filter, self, user_id):
    user_notifications = service.getUserNotificationsByUserId(user_id,filter)
    return jsonify(user_notifications)

@user_notifications.route('/user/<user_id>', methods=['DELETE'])
#@cross_origin()
@permissions.has_permission(['user_notification.delete.my'])
def delete_user_notification_by_user_id(self, user_id):
    message, status = service.deleteAllUserNotificationByUserId(user_id)
    return jsonify({'msg': message}), status

@user_notifications.route('/user/count/<user_id>', methods=['GET'])
#@cross_origin()
@permissions.has_permission(['user_notification.show.my'])
def get_unread_count_user_notification_by_user_id(self, user_id):
    message, status = service.getUnreadCountUserNotificationsByUserId(user_id)
    return jsonify({'msg': message}), status

@user_notifications.route('/read/<id>', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user_notification.edit.my'])
def read_user_notification(self, id):
    message, status = service.readUserNotification(id)
    return jsonify({'msg': message}), status

@user_notifications.route('/read/all/<user_id>', methods=['POST'])
#@cross_origin()
@permissions.has_permission(['user_notification.edit.my'])
def read_all_user_notification_by_user_id(self, user_id):
    message, status = service.readAllUserNotificationByUserId(user_id)
    return jsonify({'msg': message}), status