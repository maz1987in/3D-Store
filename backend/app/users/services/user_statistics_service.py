"""
User Statistics Service

Handles user analytics, statistics, and reporting operations.
"""

from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_

from app.utilities.db_utils import session_scope
from app.utilities.error_utils import handle_errors
from app.users.repository import UserRepository
from app.users.model import User, Role, Tracking


class UserStatisticsService:
    """Service for user statistics and analytics."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    @handle_errors("User")
    def get_users_statistics(self) -> tuple:
        """Get comprehensive user statistics."""
        # Use repository for statistics
        statistics = self.user_repo.get_user_statistics()
        return statistics, 200

    @handle_errors("User")
    def get_user_growth_analytics(self, days: int = 30) -> tuple:
        """Get user growth analytics for specified days."""
        # Use repository for growth analytics
        analytics = self.user_repo.get_user_growth_analytics(days)
        return analytics, 200

    @handle_errors("User")
    def get_user_engagement_metrics(self) -> tuple:
        """Get user engagement metrics."""
        # Use repository for engagement metrics
        metrics = self.user_repo.get_user_engagement_metrics()
        return metrics, 200
