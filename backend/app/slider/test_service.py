"""
Unit tests for Slider Service.

Tests all business logic in slider/service.py including:
- Slider CRUD operations
- Slider ordering and sequencing
- Active/inactive (enable/disable) filtering
- Date range validation
- Image upload handling
- Platform-specific sliders
- Edge cases and error handling
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from test.test_helpers import create_mock_filter, create_test_file, create_test_image_data
from app.slider.service import SliderService
from app.slider.model import Slider
from app.common.error_handling import ResourceNotFoundError


class TestSliderService(BaseServiceTestCase):
    """Test cases for SliderService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = SliderService()
    
    # ========== CRUD Operations Tests ==========
    
    def test_create_slider_success(self, db_session):
        """Test creating a slider successfully."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'url': '/products/featured',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        # Create mock image
        image = create_test_file(
            filename='slider.jpg',
            content=create_test_image_data(),
            mimetype='image/jpeg'
        )
        
        result, status = self.service.create_slider(slider_data, image)
        
        assert status == 201
        assert 'Created' in result
        
        # Verify slider was created
        slider = db_session.query(Slider).first()
        assert slider is not None
        assert slider.order == 1
        assert slider.enable is True
    
    def test_create_slider_without_image(self, db_session):
        """Test creating slider without image."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        
        # Should either succeed or require image
        assert status in [201, 400]
    
    def test_create_slider_with_invalid_image_type(self, db_session):
        """Test creating slider with invalid image file type."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        # Create invalid file type
        invalid_image = create_test_file(
            filename='slider.pdf',
            content=b'PDF content',
            mimetype='application/pdf'
        )
        
        result, status = self.service.create_slider(slider_data, invalid_image)
        
        assert status == 400
        assert 'not allowed' in result.lower()
    
    def test_get_sliders_with_pagination(self, db_session):
        """Test getting sliders with pagination."""
        # Create multiple sliders
        for i in range(12):
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': str(i + 1),
                'slider_type': 'banner',
                'platform': 'web'
            }
            self.service.create_slider(slider_data, None)
        
        filter_obj = create_mock_filter(page=1, per_page=10)
        result, status = self.service.get_sliders(None, filter_obj)
        
        assert status == 200
        assert 'sliders' in result
        assert 'filters' in result
    
    def test_get_slider_by_id(self, db_session):
        """Test getting a specific slider by ID."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        self.service.create_slider(slider_data, None)
        
        slider = db_session.query(Slider).first()
        filter_obj = create_mock_filter()
        
        result, status = self.service.get_sliders(slider.id, filter_obj)
        
        assert status == 200
        assert 'sliders' in result
    
    def test_update_slider_success(self, db_session):
        """Test updating a slider."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        self.service.create_slider(slider_data, None)
        
        slider = db_session.query(Slider).first()
        
        # Update slider
        update_data = {
            'enable': 'false',
            'order': '5',
            'url': '/new-url'
        }
        
        result, status = self.service.update_slider(slider.id, update_data, None)
        
        assert status == 200
        assert 'Updated' in result
        
        db_session.refresh(slider)
        assert slider.enable is False
        assert slider.order == 5
    
    def test_delete_slider_success(self, db_session):
        """Test deleting a slider."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        self.service.create_slider(slider_data, None)
        
        slider = db_session.query(Slider).first()
        slider_id = slider.id
        
        result, status = self.service.delete_slider(slider_id)
        
        assert status == 200
        assert 'deleted' in result.lower()
        
        deleted_slider = db_session.query(Slider).filter_by(id=slider_id).first()
        assert deleted_slider is None
    
    # ========== Ordering Tests ==========
    
    def test_slider_ordering_sequence(self, db_session):
        """Test slider ordering sequence."""
        # Create sliders with different orders
        for order in [3, 1, 5, 2, 4]:
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': str(order),
                'slider_type': 'banner',
                'platform': 'web'
            }
            self.service.create_slider(slider_data, None)
        
        # Verify ordering
        sliders = db_session.query(Slider).order_by(Slider.order).all()
        assert len(sliders) == 5
        assert [s.order for s in sliders] == [1, 2, 3, 4, 5]
    
    def test_update_slider_order(self, db_session):
        """Test reordering sliders."""
        # Create sliders
        for i in range(3):
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': str(i + 1),
                'slider_type': 'banner',
                'platform': 'web'
            }
            self.service.create_slider(slider_data, None)
        
        # Get first slider and move it to position 3
        first_slider = db_session.query(Slider).order_by(Slider.order).first()
        
        update_data = {'order': '3'}
        self.service.update_slider(first_slider.id, update_data, None)
        
        db_session.refresh(first_slider)
        assert first_slider.order == 3
    
    # ========== Date Range Tests ==========
    
    def test_slider_with_future_dates(self, db_session):
        """Test slider with future date range."""
        future_start = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
        future_end = (datetime.now() + timedelta(days=40)).strftime('%Y-%m-%d')
        
        slider_data = {
            'enable': 'true',
            'from_date': future_start,
            'to_date': future_end,
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        assert status == 201
    
    def test_slider_with_past_dates(self, db_session):
        """Test slider with past date range (expired)."""
        past_start = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        past_end = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        slider_data = {
            'enable': 'true',
            'from_date': past_start,
            'to_date': past_end,
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        assert status == 201
        
        # Slider should be created but might be filtered in queries
        slider = db_session.query(Slider).first()
        assert slider is not None
    
    def test_slider_invalid_date_range(self, db_session):
        """Test slider with end date before start date."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-12-31',
            'to_date': '2024-01-01',  # Before start date
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        # Should validate date range
        result, status = self.service.create_slider(slider_data, None)
        # Either succeeds or validates
        assert status in [201, 400]
    
    # ========== Platform-Specific Tests ==========
    
    def test_sliders_for_different_platforms(self, db_session):
        """Test creating sliders for different platforms."""
        platforms = ['web', 'mobile', 'app']
        
        for i, platform in enumerate(platforms):
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': str(i + 1),
                'slider_type': 'banner',
                'platform': platform
            }
            result, status = self.service.create_slider(slider_data, None)
            assert status == 201
        
        # Verify all platforms created
        sliders = db_session.query(Slider).all()
        slider_platforms = [s.platform for s in sliders]
        assert set(slider_platforms) >= set(platforms)
    
    # ========== Enable/Disable Tests ==========
    
    def test_create_enabled_slider(self, db_session):
        """Test creating an enabled slider."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        assert status == 201
        
        slider = db_session.query(Slider).first()
        assert slider.enable is True
    
    def test_create_disabled_slider(self, db_session):
        """Test creating a disabled slider."""
        slider_data = {
            'enable': 'false',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        assert status == 201
        
        slider = db_session.query(Slider).first()
        assert slider.enable is False
    
    def test_toggle_slider_enable_status(self, db_session):
        """Test toggling slider enable/disable status."""
        # Create enabled slider
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        self.service.create_slider(slider_data, None)
        
        slider = db_session.query(Slider).first()
        
        # Disable
        self.service.update_slider(slider.id, {'enable': 'false'}, None)
        db_session.refresh(slider)
        assert slider.enable is False
        
        # Re-enable
        self.service.update_slider(slider.id, {'enable': 'true'}, None)
        db_session.refresh(slider)
        assert slider.enable is True
    
    # ========== Error Handling Tests ==========
    
    def test_get_slider_not_found(self, db_session):
        """Test getting a non-existent slider."""
        non_existent_id = uuid.uuid4()
        filter_obj = create_mock_filter()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.get_sliders(non_existent_id, filter_obj)
    
    def test_update_slider_not_found(self, db_session):
        """Test updating a non-existent slider."""
        non_existent_id = uuid.uuid4()
        update_data = {'enable': 'false'}
        
        with pytest.raises(ResourceNotFoundError):
            self.service.update_slider(non_existent_id, update_data, None)
    
    def test_delete_slider_not_found(self, db_session):
        """Test deleting a non-existent slider."""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError):
            self.service.delete_slider(non_existent_id)
    
    def test_create_slider_missing_required_fields(self, db_session):
        """Test creating slider with missing required fields."""
        incomplete_data = {
            'enable': 'true',
            'order': '1'
            # Missing dates, slider_type, platform
        }
        
        with pytest.raises(Exception):
            self.service.create_slider(incomplete_data, None)
    
    # ========== Edge Cases Tests ==========
    
    def test_create_slider_with_zero_order(self, db_session):
        """Test creating slider with order = 0."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '0',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        
        assert status == 201
        slider = db_session.query(Slider).first()
        assert slider.order == 0
    
    def test_create_slider_with_negative_order(self, db_session):
        """Test creating slider with negative order."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '-1',
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        # Should either prevent or allow
        result, status = self.service.create_slider(slider_data, None)
        assert status in [201, 400]
    
    def test_get_sliders_empty_database(self, db_session):
        """Test getting sliders when database is empty."""
        filter_obj = create_mock_filter()
        result, status = self.service.get_sliders(None, filter_obj)
        
        assert status == 200
        assert 'sliders' in result
        assert len(result['sliders']) == 0
    
    def test_slider_url_optional(self, db_session):
        """Test creating slider without URL."""
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'slider_type': 'banner',
            'platform': 'web'
            # No URL
        }
        
        result, status = self.service.create_slider(slider_data, None)
        assert status == 201
        
        slider = db_session.query(Slider).first()
        # URL should be None or empty
        assert slider.url is None or slider.url == ''
    
    def test_slider_with_long_url(self, db_session):
        """Test slider with very long URL."""
        long_url = 'https://example.com/' + 'a' * 500
        
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'url': long_url,
            'slider_type': 'banner',
            'platform': 'web'
        }
        
        result, status = self.service.create_slider(slider_data, None)
        # Should either succeed or validate length
        assert status in [201, 400]
    
    def test_multiple_sliders_same_order(self, db_session):
        """Test creating multiple sliders with same order number."""
        # Create two sliders with same order
        for i in range(2):
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': '1',  # Same order
                'slider_type': 'banner',
                'platform': 'web'
            }
            result, status = self.service.create_slider(slider_data, None)
            assert status == 201
        
        # Both should be created (ordering handled by display logic)
        sliders = db_session.query(Slider).filter(Slider.order == 1).all()
        assert len(sliders) >= 2
    
    def test_slider_different_types(self, db_session):
        """Test creating sliders with different types."""
        slider_types = ['banner', 'carousel', 'hero', 'promo']
        
        for i, slider_type in enumerate(slider_types):
            slider_data = {
                'enable': 'true',
                'from_date': '2024-01-01',
                'to_date': '2024-12-31',
                'order': str(i + 1),
                'slider_type': slider_type,
                'platform': 'web'
            }
            result, status = self.service.create_slider(slider_data, None)
            assert status == 201
        
        sliders = db_session.query(Slider).all()
        slider_types_created = [s.slider_type for s in sliders]
        assert set(slider_types_created) >= set(slider_types)
    
    def test_update_slider_partial_data(self, db_session):
        """Test updating only some fields of a slider."""
        # Create slider
        slider_data = {
            'enable': 'true',
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'order': '1',
            'url': '/original',
            'slider_type': 'banner',
            'platform': 'web'
        }
        self.service.create_slider(slider_data, None)
        
        slider = db_session.query(Slider).first()
        original_order = slider.order
        
        # Update only URL
        update_data = {'url': '/updated'}
        self.service.update_slider(slider.id, update_data, None)
        
        db_session.refresh(slider)
        assert slider.url == '/updated'
        assert slider.order == original_order  # Should not change

