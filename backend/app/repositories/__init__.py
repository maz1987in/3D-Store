# Repository package for data access layer
from .base import BaseRepository

# Note: Individual repositories should be imported directly from their modules
# to avoid circular imports. For example:
# from app.users.repository import UserRepository

__all__ = [
    'BaseRepository'
]