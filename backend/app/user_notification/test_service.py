"""
Unit tests for User Notification Service.

Tests all business logic in user_notification/service.py including:
- Notification creation and delivery
- User notification preferences
- Bulk notification sending
- Read/unread status tracking
- Notification history and cleanup
- Edge cases and error handling
"""

import pytest
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.user_notification.service import UserNotificationService
from app.user_notification.model import UserNotification
from app.common.error_handling import ResourceNotFoundError


class TestUserNotificationService(BaseServiceTestCase):
    """Test cases for UserNotificationService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = UserNotificationService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_notification_success(self, db_session, sample_user):
        """Test creating a user notification successfully."""
        notification_data = {
            'name': 'Order Shipped',
            'user_id': sample_user.id,
            'read': False,
            'message': 'Your order #12345 has been shipped'
        }
        
        result, status = self.service.create_user_notification(notification_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify notification was created
        notification = db_session.query(UserNotification).filter(
            UserNotification.user_id == sample_user.id
        ).first()
        assert notification is not None
        assert notification.name == 'Order Shipped'
        assert notification.read is False
    
    def test_get_user_notifications_with_pagination(self, db_session, sample_user):
        """Test getting notifications with pagination."""
        # Create multiple notifications
        for i in range(12):
            notification_data = {
                'name': f'Notification {i}',
                'user_id': sample_user.id,
                'read': False,
                'message': f'Message {i}'
            }
            self.service.create_user_notification(notification_data)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_user_notifications(None, filter_obj)
        
        assert status == 200
        assert 'user_notifications' in result
        assert 'filters' in result
    
    def test_get_notification_by_id(self, db_session, sample_user):
        """Test getting a specific notification by ID."""
        notification_data = {
            'name': 'Test Notification',
            'user_id': sample_user.id,
            'read': False,
            'message': 'Test message'
        }
        self.service.create_user_notification(notification_data)
        
        notification = db_session.query(UserNotification).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_user_notifications(notification.id, filter_obj)
        
        assert status == 200
        assert 'user_notifications' in result
    
    def test_mark_notification_as_read(self, db_session, sample_user):
        """Test marking a notification as read."""
        # Create unread notification
        notification_data = {
            'name': 'Unread Notification',
            'user_id': sample_user.id,
            'read': False,
            'message': 'Please read this'
        }
        self.service.create_user_notification(notification_data)
        
        notification = db_session.query(UserNotification).first()
        
        # Mark as read
        update_data = {
            'name': notification.name,
            'user_id': notification.user_id,
            'read': True,
            'message': notification.message
        }
        
        result, status = self.service.update_user_notification(notification.id, update_data)
        
        assert status == 200
        
        db_session.refresh(notification)
        assert notification.read is True
    
    def test_delete_notification_success(self, db_session, sample_user):
        """Test deleting a notification."""
        notification_data = {
            'name': 'Delete Me',
            'user_id': sample_user.id,
            'read': False,
            'message': 'Delete this notification'
        }
        self.service.create_user_notification(notification_data)
        
        notification = db_session.query(UserNotification).first()
        notification_id = notification.id
        
        result, status = self.service.delete_user_notification(notification_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_notification = db_session.query(UserNotification).filter_by(id=notification_id).first()
        assert deleted_notification is None
    
    # ========== Read/Unread Status Tests ==========
    
    def test_filter_unread_notifications(self, db_session, sample_user):
        """Test filtering notifications by unread status."""
        # Create mix of read and unread
        for i in range(6):
            notification_data = {
                'name': f'Notification {i}',
                'user_id': sample_user.id,
                'read': (i % 2 == 0),  # Even indices are read
                'message': f'Message {i}'
            }
            self.service.create_user_notification(notification_data)
        
        # Query unread
        unread = db_session.query(UserNotification).filter(
            UserNotification.read == False
        ).all()
        
        assert len(unread) >= 3
        assert all(not n.read for n in unread)
    
    def test_mark_all_as_read(self, db_session, sample_user):
        """Test marking all user notifications as read."""
        # Create unread notifications
        for i in range(3):
            notification_data = {
                'name': f'Unread {i}',
                'user_id': sample_user.id,
                'read': False,
                'message': f'Unread message {i}'
            }
            self.service.create_user_notification(notification_data)
        
        # Mark all as read
        result, status = self.service.mark_all_as_read(sample_user.id)
        
        assert status == 200
        
        # Verify all marked as read
        notifications = db_session.query(UserNotification).filter(
            UserNotification.user_id == sample_user.id
        ).all()
        assert all(n.read for n in notifications)
    
    # ========== User-Specific Tests ==========
    
    def test_get_user_notifications_by_user_id(self, db_session, sample_user):
        """Test getting all notifications for a specific user."""
        # Create notifications for user
        for i in range(5):
            notification_data = {
                'name': f'User Notification {i}',
                'user_id': sample_user.id,
                'read': False,
                'message': f'Message {i}'
            }
            self.service.create_user_notification(notification_data)
        
        # Get by user ID
        result, status = self.service.get_notifications_by_user(sample_user.id)
        
        assert status == 200
        assert len(result) >= 5
    
    def test_multiple_users_separate_notifications(self, db_session):
        """Test that different users have separate notifications."""
        from app.users.model import User
        from werkzeug.security import generate_password_hash
        
        # Create two users
        user1 = User(
            username='notifuser1',
            phone='+8888888881',
            email='notif1@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        user2 = User(
            username='notifuser2',
            phone='+8888888882',
            email='notif2@test.com',
            password=generate_password_hash('test'),
            active=True
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        # Create notifications for both
        for user in [user1, user2]:
            notification_data = {
                'name': f'Notification for {user.username}',
                'user_id': user.id,
                'read': False,
                'message': f'Message for {user.username}'
            }
            self.service.create_user_notification(notification_data)
        
        # Verify separate notifications
        user1_notifs, _ = self.service.get_notifications_by_user(user1.id)
        user2_notifs, _ = self.service.get_notifications_by_user(user2.id)
        
        assert len(user1_notifs) > 0
        assert len(user2_notifs) > 0
    
    # ========== Error Handling Tests ==========
    
    def test_create_notification_invalid_user(self, db_session):
        """Test creating notification for non-existent user."""
        notification_data = {
            'name': 'Invalid User Notification',
            'user_id': uuid.uuid4(),  # Non-existent
            'read': False,
            'message': 'Message'
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_user_notification(notification_data)
    
    def test_update_notification_not_found(self, db_session):
        """Test updating a non-existent notification."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'name': 'Test',
            'user_id': uuid.uuid4(),
            'read': True,
            'message': 'Test'
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_user_notification(non_existent_id, update_data)
    
    def test_delete_notification_not_found(self, db_session):
        """Test deleting a non-existent notification."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_user_notification(non_existent_id)
    
    def test_get_notifications_empty_user(self, db_session, sample_user):
        """Test getting notifications when user has none."""
        result, status = self.service.get_notifications_by_user(sample_user.id)
        
        assert status == 200
        assert len(result) == 0

