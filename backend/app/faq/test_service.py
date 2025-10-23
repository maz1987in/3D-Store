"""
Unit tests for FAQ Service.

Tests all business logic in faq/service.py including:
- FAQ CRUD operations
- FAQ topic management
- Active/inactive filtering
- FAQ ordering within topics
- Translation handling
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
from app.faq.service import FaqService
from app.faq.model import Faq, FaqTopic
from app.common.error_handling import ResourceNotFoundError


class TestFaqService(BaseServiceTestCase):
    """Test cases for FaqService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = FaqService()
    
    # ========== FAQ Topic Tests ==========
    
    def test_create_faq_topic_success(self, db_session):
        """Test creating a FAQ topic successfully."""
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        
        result, status = self.service.create_faq_topic(topic_data)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify topic was created
        topic = db_session.query(FaqTopic).first()
        assert topic is not None
        assert topic.order == 1
        assert topic.is_active is True
    
    def test_get_faq_topics(self, db_session):
        """Test getting all FAQ topics."""
        # Create multiple topics
        for i in range(3):
            topic_data = {
                'name': json.dumps({'en': f'Topic {i}', 'ar': f'موضوع {i}'}),
                'order': i + 1,
                'is_active': True
            }
            self.service.create_faq_topic(topic_data)
        
        result, status = self.service.get_faq_topics()
        
        assert status == 200
        assert len(result) >= 3
    
    def test_update_faq_topic_success(self, db_session):
        """Test updating a FAQ topic."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'Original', 'ar': 'أصلي'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        
        topic = db_session.query(FaqTopic).first()
        
        # Update topic
        update_data = {
            'order': 2,
            'is_active': False
        }
        
        result, status = self.service.update_faq_topic(topic.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(topic)
        assert topic.order == 2
        assert topic.is_active is False
    
    def test_delete_faq_topic(self, db_session):
        """Test deleting a FAQ topic."""
        topic_data = {
            'name': json.dumps({'en': 'Delete Me', 'ar': 'احذفني'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        
        topic = db_session.query(FaqTopic).first()
        topic_id = topic.id
        
        result, status = self.service.delete_faq_topic(topic_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_topic = db_session.query(FaqTopic).filter_by(id=topic_id).first()
        assert deleted_topic is None
    
    # ========== FAQ CRUD Tests ==========
    
    def test_create_faq_success(self, db_session):
        """Test creating a FAQ successfully."""
        # Create topic first
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        faq_data = {
            'question': json.dumps({'en': 'What is 3D printing?', 'ar': 'ما هي الطباعة ثلاثية الأبعاد؟'}),
            'answer': json.dumps({'en': 'A process...', 'ar': 'عملية...'}),
            'faq_topic_id': topic.id,
            'order': 1,
            'is_active': True
        }
        
        result, status = self.service.create_faq(faq_data, None)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify FAQ was created
        faq = db_session.query(Faq).first()
        assert faq is not None
        assert faq.faq_topic_id == topic.id
        assert faq.order == 1
    
    def test_get_faqs_with_pagination(self, db_session):
        """Test getting FAQs with pagination."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        # Create multiple FAQs
        for i in range(12):
            faq_data = {
                'question': json.dumps({'en': f'Question {i}?', 'ar': f'سؤال {i}؟'}),
                'answer': json.dumps({'en': f'Answer {i}', 'ar': f'جواب {i}'}),
                'faq_topic_id': topic.id,
                'order': i + 1,
                'is_active': True
            }
            self.service.create_faq(faq_data, None)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_faqs(None, filter_obj)
        
        assert status == 200
        assert 'faqs' in result
        assert 'filters' in result
    
    def test_get_faq_by_id(self, db_session):
        """Test getting a specific FAQ by ID."""
        # Create topic and FAQ
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        faq_data = {
            'question': json.dumps({'en': 'Test Question?', 'ar': 'سؤال اختبار؟'}),
            'answer': json.dumps({'en': 'Test Answer', 'ar': 'جواب اختبار'}),
            'faq_topic_id': topic.id,
            'order': 1,
            'is_active': True
        }
        self.service.create_faq(faq_data, None)
        
        faq = db_session.query(Faq).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_faqs(faq.id, filter_obj)
        
        assert status == 200
        assert 'faqs' in result
    
    def test_update_faq_success(self, db_session):
        """Test updating a FAQ."""
        # Create topic and FAQ
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        faq_data = {
            'question': json.dumps({'en': 'Original?', 'ar': 'أصلي؟'}),
            'answer': json.dumps({'en': 'Original', 'ar': 'أصلي'}),
            'faq_topic_id': topic.id,
            'order': 1,
            'is_active': True
        }
        self.service.create_faq(faq_data, None)
        
        faq = db_session.query(Faq).first()
        
        # Update FAQ
        update_data = {
            'question': json.dumps({'en': 'Updated?', 'ar': 'محدث؟'}),
            'is_active': False
        }
        
        result, status = self.service.update_faq(faq.id, update_data)
        
        assert status == 200
        assert 'Updated' in result
    
    def test_delete_faq_success(self, db_session):
        """Test deleting a FAQ."""
        # Create topic and FAQ
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        faq_data = {
            'question': json.dumps({'en': 'Delete?', 'ar': 'حذف؟'}),
            'answer': json.dumps({'en': 'Delete', 'ar': 'حذف'}),
            'faq_topic_id': topic.id,
            'order': 1,
            'is_active': True
        }
        self.service.create_faq(faq_data, None)
        
        faq = db_session.query(Faq).first()
        faq_id = faq.id
        
        result, status = self.service.delete_faq(faq_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_faq = db_session.query(Faq).filter_by(id=faq_id).first()
        assert deleted_faq is None
    
    # ========== Ordering Tests ==========
    
    def test_faq_ordering_within_topic(self, db_session):
        """Test FAQ ordering within a topic."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        # Create FAQs with different orders
        for order in [3, 1, 2]:
            faq_data = {
                'question': json.dumps({'en': f'Q{order}?', 'ar': f'س{order}؟'}),
                'answer': json.dumps({'en': f'A{order}', 'ar': f'ج{order}'}),
                'faq_topic_id': topic.id,
                'order': order,
                'is_active': True
            }
            self.service.create_faq(faq_data, None)
        
        # Verify ordering
        faqs = db_session.query(Faq).filter(Faq.faq_topic_id == topic.id).order_by(Faq.order).all()
        assert len(faqs) == 3
        assert [f.order for f in faqs] == [1, 2, 3]
    
    def test_update_faq_order(self, db_session):
        """Test updating FAQ order."""
        # Create topic and FAQ
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        faq_data = {
            'question': json.dumps({'en': 'Question?', 'ar': 'سؤال؟'}),
            'answer': json.dumps({'en': 'Answer', 'ar': 'جواب'}),
            'faq_topic_id': topic.id,
            'order': 5,
            'is_active': True
        }
        self.service.create_faq(faq_data, None)
        
        faq = db_session.query(Faq).first()
        
        # Change order
        update_data = {'order': 10}
        self.service.update_faq(faq.id, update_data)
        
        db_session.refresh(faq)
        assert faq.order == 10
    
    # ========== Active/Inactive Filtering Tests ==========
    
    def test_filter_active_faqs(self, db_session):
        """Test filtering FAQs by active status."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        # Create mix of active and inactive FAQs
        for i in range(6):
            faq_data = {
                'question': json.dumps({'en': f'Q{i}?', 'ar': f'س{i}؟'}),
                'answer': json.dumps({'en': f'A{i}', 'ar': f'ج{i}'}),
                'faq_topic_id': topic.id,
                'order': i + 1,
                'is_active': i % 2 == 0  # Even indices active
            }
            self.service.create_faq(faq_data, None)
        
        # Get active FAQs
        active_faqs = db_session.query(Faq).filter(Faq.is_active == True).all()
        inactive_faqs = db_session.query(Faq).filter(Faq.is_active == False).all()
        
        assert len(active_faqs) == 3
        assert len(inactive_faqs) == 3
    
    # ========== Edge Cases Tests ==========
    
    def test_create_faq_without_topic(self, db_session):
        """Test creating FAQ without a topic."""
        faq_data = {
            'question': json.dumps({'en': 'Orphan?', 'ar': 'يتيم؟'}),
            'answer': json.dumps({'en': 'Orphan', 'ar': 'يتيم'}),
            'faq_topic_id': None,
            'order': 1,
            'is_active': True
        }
        
        # Should handle gracefully
        result, status = self.service.create_faq(faq_data, None)
        assert status in [201, 400]
    
    def test_create_faq_with_long_question_answer(self, db_session):
        """Test creating FAQ with very long question and answer."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        long_text = "A" * 5000  # Very long text
        
        faq_data = {
            'question': json.dumps({'en': long_text, 'ar': long_text}),
            'answer': json.dumps({'en': long_text, 'ar': long_text}),
            'faq_topic_id': topic.id,
            'order': 1,
            'is_active': True
        }
        
        result, status = self.service.create_faq(faq_data, None)
        assert status == 201
        
        faq = db_session.query(Faq).first()
        assert faq is not None
    
    def test_multiple_faqs_same_topic(self, db_session):
        """Test creating multiple FAQs for the same topic."""
        # Create topic
        topic_data = {
            'name': json.dumps({'en': 'General', 'ar': 'عام'}),
            'order': 1,
            'is_active': True
        }
        self.service.create_faq_topic(topic_data)
        topic = db_session.query(FaqTopic).first()
        
        # Create 5 FAQs for same topic
        for i in range(5):
            faq_data = {
                'question': json.dumps({'en': f'Q{i}?', 'ar': f'س{i}؟'}),
                'answer': json.dumps({'en': f'A{i}', 'ar': f'ج{i}'}),
                'faq_topic_id': topic.id,
                'order': i + 1,
                'is_active': True
            }
            result, status = self.service.create_faq(faq_data, None)
            assert status == 201
        
        # Verify all belong to same topic
        faqs = db_session.query(Faq).filter(Faq.faq_topic_id == topic.id).all()
        assert len(faqs) == 5
    
    def test_get_faqs_empty_database(self, db_session):
        """Test getting FAQs when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_faqs(None, filter_obj)
        
        assert status == 200
        assert 'faqs' in result
        assert len(result['faqs']) == 0
    
    # ========== Error Handling Tests ==========
    
    def test_create_faq_missing_required_fields(self, db_session):
        """Test creating FAQ with missing required fields."""
        incomplete_data = {
            'question': json.dumps({'en': 'Question?', 'ar': 'سؤال؟'})
            # Missing answer, topic_id, order
        }
        
        with pytest.raises(Exception):
            self.service.create_faq(incomplete_data, None)
    
    def test_get_faq_by_invalid_id(self, db_session):
        """Test getting FAQ with non-existent ID."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_faqs(non_existent_id, filter_obj)
    
    def test_update_faq_not_found(self, db_session):
        """Test updating a non-existent FAQ."""
        non_existent_id = uuid.uuid4()
        update_data = {'is_active': False}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_faq(non_existent_id, update_data)
    
    def test_delete_faq_not_found(self, db_session):
        """Test deleting a non-existent FAQ."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_faq(non_existent_id)
    
    def test_create_faq_with_invalid_topic(self, db_session):
        """Test creating FAQ with non-existent topic."""
        faq_data = {
            'question': json.dumps({'en': 'Question?', 'ar': 'سؤال؟'}),
            'answer': json.dumps({'en': 'Answer', 'ar': 'جواب'}),
            'faq_topic_id': uuid.uuid4(),  # Non-existent
            'order': 1,
            'is_active': True
        }
        
        with pytest.raises(Exception):  # Foreign key constraint
            self.service.create_faq(faq_data, None)

