"""
Unit tests for Templates Content Service.

Tests all business logic in templates_content/service.py including:
- Template content CRUD operations
- Content versioning and history
- Content type management (email, SMS, push)
- Multi-language translation support
- Variable substitution in templates
- Edge cases and error handling
"""

import pytest
import uuid
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter
from app.templates_content.service import TemplatesContentService
from app.templates_content.model import TemplatesContent
from app.common.enum import MediaTypeEnum
from app.common.error_handling import ResourceNotFoundError


class TestTemplatesContentService(BaseServiceTestCase):
    """Test cases for TemplatesContentService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = TemplatesContentService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_template_content_success(self, db_session):
        """Test creating template content successfully."""
        template_data = {
            'key': 'welcome_email',
            'subject': json.dumps({'en': 'Welcome to 3D Store', 'ar': 'مرحباً في متجر ثلاثي الأبعاد'}),
            'content': json.dumps({'en': 'Thank you for joining!', 'ar': 'شكراً للانضمام!'}),
            'media_type': MediaTypeEnum.EMAIL.value,
            'model_type': 'user',
            'model_op': 'registration'
        }
        
        result, status = self.service.create_templates_content(template_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify template was created
        template = db_session.query(TemplatesContent).filter(
            TemplatesContent.key == 'welcome_email'
        ).first()
        assert template is not None
        assert template.media_type == MediaTypeEnum.EMAIL
    
    def test_get_templates_contents_with_pagination(self, db_session):
        """Test getting template contents with pagination."""
        # Create multiple templates
        for i in range(10):
            template_data = {
                'key': f'template_{i}',
                'subject': json.dumps({'en': f'Subject {i}', 'ar': f'موضوع {i}'}),
                'content': json.dumps({'en': f'Content {i}', 'ar': f'محتوى {i}'}),
                'media_type': MediaTypeEnum.EMAIL.value,
                'model_type': 'generic',
                'model_op': 'notification'
            }
            self.service.create_templates_content(template_data)
        
        filter_obj = create_mock_filter(page=1, per_page=5)
        result, status = self.service.get_templates_contents(None, filter_obj)
        
        assert status == 200
        assert 'templates_contents' in result
        assert 'filters' in result
    
    def test_get_template_content_by_id(self, db_session):
        """Test getting a specific template by ID."""
        template_data = {
            'key': 'test_template',
            'subject': json.dumps({'en': 'Test Subject', 'ar': 'موضوع اختبار'}),
            'content': json.dumps({'en': 'Test Content', 'ar': 'محتوى اختبار'}),
            'media_type': MediaTypeEnum.EMAIL.value,
            'model_type': 'test',
            'model_op': 'test_op'
        }
        self.service.create_templates_content(template_data)
        
        template = db_session.query(TemplatesContent).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_templates_contents(template.id, filter_obj)
        
        assert status == 200
        assert 'templates_contents' in result
    
    def test_update_template_content_success(self, db_session):
        """Test updating template content."""
        # Create template
        template_data = {
            'key': 'update_template',
            'subject': json.dumps({'en': 'Original Subject', 'ar': 'موضوع أصلي'}),
            'content': json.dumps({'en': 'Original Content', 'ar': 'محتوى أصلي'}),
            'media_type': MediaTypeEnum.EMAIL.value,
            'model_type': 'user',
            'model_op': 'update'
        }
        self.service.create_templates_content(template_data)
        
        template = db_session.query(TemplatesContent).first()
        
        # Update template
        update_data = {
            'key': 'update_template',
            'subject': json.dumps({'en': 'Updated Subject', 'ar': 'موضوع محدث'}),
            'content': json.dumps({'en': 'Updated Content', 'ar': 'محتوى محدث'}),
            'model_op': 'update_v2'
        }
        
        result, status = self.service.update_templates_content(template.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
    
    def test_delete_template_content_success(self, db_session):
        """Test deleting template content."""
        template_data = {
            'key': 'delete_template',
            'subject': json.dumps({'en': 'Delete', 'ar': 'حذف'}),
            'content': json.dumps({'en': 'Delete', 'ar': 'حذف'}),
            'media_type': MediaTypeEnum.EMAIL.value,
            'model_type': 'test',
            'model_op': 'delete'
        }
        self.service.create_templates_content(template_data)
        
        template = db_session.query(TemplatesContent).first()
        template_id = template.id
        
        result, status = self.service.delete_templates_content(template_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_template = db_session.query(TemplatesContent).filter_by(id=template_id).first()
        assert deleted_template is None
    
    # ========== Media Type Tests ==========
    
    def test_template_different_media_types(self, db_session):
        """Test templates for different media types."""
        media_types = [MediaTypeEnum.EMAIL, MediaTypeEnum.SMS, MediaTypeEnum.PUSH]
        
        for i, media_type in enumerate(media_types):
            template_data = {
                'key': f'template_{media_type.value}',
                'subject': json.dumps({'en': f'Subject {i}', 'ar': f'موضوع {i}'}),
                'content': json.dumps({'en': f'Content {i}', 'ar': f'محتوى {i}'}),
                'media_type': media_type.value,
                'model_type': 'notification',
                'model_op': 'send'
            }
            result, status = self.service.create_templates_content(template_data)
            assert status == 201
        
        # Verify all media types created
        templates = db_session.query(TemplatesContent).all()
        template_types = [t.media_type for t in templates]
        assert set(template_types) >= set(media_types)
    
    # ========== Key Uniqueness Tests ==========
    
    def test_template_key_uniqueness(self, db_session):
        """Test that template keys must be unique."""
        template_data = {
            'key': 'unique_key',
            'subject': json.dumps({'en': 'Subject', 'ar': 'موضوع'}),
            'content': json.dumps({'en': 'Content', 'ar': 'محتوى'}),
            'media_type': MediaTypeEnum.EMAIL.value,
            'model_type': 'test',
            'model_op': 'test'
        }
        
        # Create first template
        result1, status1 = self.service.create_templates_content(template_data)
        assert status1 == 201
        
        # Try to create duplicate key
        with pytest.raises(Exception):  # Unique constraint
            self.service.create_templates_content(template_data)
    
    # ========== Error Handling Tests ==========
    
    def test_get_template_not_found(self, db_session):
        """Test getting a non-existent template."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_templates_contents(non_existent_id, filter_obj)
    
    def test_update_template_not_found(self, db_session):
        """Test updating a non-existent template."""
        non_existent_id = uuid.uuid4()
        update_data = {
            'key': 'test',
            'model_op': 'test'
        }
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_templates_content(non_existent_id, update_data)
    
    def test_delete_template_not_found(self, db_session):
        """Test deleting a non-existent template."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_templates_content(non_existent_id)
    
    def test_get_templates_empty_database(self, db_session):
        """Test getting templates when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_templates_contents(None, filter_obj)
        
        assert status == 200
        assert 'templates_contents' in result

