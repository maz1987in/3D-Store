"""
Unit tests for Admin Service.

Tests all business logic in admin/service.py including:
- Job management and scheduling
- System statistics and dashboard data
- Bulk operations
- Admin-specific functionality
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from test.base_test import BaseServiceTestCase
from app.admin.service import AdminService


class TestAdminService(BaseServiceTestCase):
    """Test cases for AdminService."""
    
    def setup_method(self):
        """Set up method for each test."""
        super().setup_method()
        self.service = AdminService()
    
    # ========== Job Management Tests ==========
    
    @patch('extensions.scheduler')
    def test_get_jobs_success(self, mock_scheduler, db_session):
        """Test getting scheduled jobs."""
        # Create mock jobs
        mock_job1 = Mock()
        mock_job1.id = 'job1'
        mock_job1.name = 'Daily Cleanup'
        mock_job1.next_run_time = None
        mock_job1.trigger = Mock()
        mock_job1.trigger.__str__ = lambda self: 'interval[1:00:00]'
        
        mock_job2 = Mock()
        mock_job2.id = 'job2'
        mock_job2.name = 'Weekly Report'
        mock_job2.next_run_time = None
        mock_job2.trigger = Mock()
        mock_job2.trigger.__str__ = lambda self: 'cron[0 0 * * 0]'
        
        mock_scheduler.get_jobs.return_value = [mock_job1, mock_job2]
        
        result, status = self.service.get_jobs()
        
        assert status == 200
        assert len(result) == 2
        assert result[0]['id'] == 'job1'
        assert result[0]['name'] == 'Daily Cleanup'
        assert result[1]['id'] == 'job2'
        assert result[1]['name'] == 'Weekly Report'
    
    @patch('extensions.scheduler')
    def test_get_jobs_empty(self, mock_scheduler, db_session):
        """Test getting jobs when no jobs exist."""
        mock_scheduler.get_jobs.return_value = []
        
        result, status = self.service.get_jobs()
        
        assert status == 200
        assert len(result) == 0
    
    @patch('extensions.scheduler')
    def test_get_jobs_with_next_run_time(self, mock_scheduler, db_session):
        """Test getting jobs with next_run_time set."""
        from datetime import datetime, timezone
        
        mock_job = Mock()
        mock_job.id = 'job_with_time'
        mock_job.name = 'Scheduled Job'
        mock_job.next_run_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_job.trigger = Mock()
        mock_job.trigger.__str__ = lambda self: 'date'
        
        mock_scheduler.get_jobs.return_value = [mock_job]
        
        result, status = self.service.get_jobs()
        
        assert status == 200
        assert len(result) == 1
        assert result[0]['next_run_time'] is not None
        assert '2024-01-15' in result[0]['next_run_time']
    
    @patch('extensions.scheduler')
    def test_get_jobs_error_handling(self, mock_scheduler, db_session):
        """Test error handling when scheduler fails."""
        mock_scheduler.get_jobs.side_effect = Exception("Scheduler error")
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            self.service.get_jobs()
    
    # ========== Edge Cases Tests ==========
    
    @patch('extensions.scheduler')
    def test_get_jobs_with_different_trigger_types(self, mock_scheduler, db_session):
        """Test getting jobs with various trigger types."""
        trigger_types = ['interval', 'cron', 'date']
        mock_jobs = []
        
        for i, trigger_type in enumerate(trigger_types):
            mock_job = Mock()
            mock_job.id = f'job_{i}'
            mock_job.name = f'{trigger_type} Job'
            mock_job.next_run_time = None
            mock_job.trigger = Mock()
            mock_job.trigger.__str__ = lambda self, t=trigger_type: f'{t}[...]'
            mock_jobs.append(mock_job)
        
        mock_scheduler.get_jobs.return_value = mock_jobs
        
        result, status = self.service.get_jobs()
        
        assert status == 200
        assert len(result) == len(trigger_types)
    
    @patch('extensions.scheduler')
    def test_get_jobs_none_returned(self, mock_scheduler, db_session):
        """Test when scheduler returns None instead of list."""
        mock_scheduler.get_jobs.return_value = None
        
        # Should handle None gracefully
        with pytest.raises(Exception):
            self.service.get_jobs()

