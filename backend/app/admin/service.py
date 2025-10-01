## service layer of the API
import json
import os
import time
import redis
import sqlalchemy as sql
from flask import current_app
from app.utilities.common_utils import debug_return
from app.utilities.db_utils import get_session_with_retries
from config import BaseConfig, FileUploadConfig
from extensions import scheduler
from app.utilities.error_utils import handle_errors  # Import the decorator

class AdminService:
    def __init__(self):
        self.session = get_session_with_retries()

    @handle_errors("Job")
    def get_jobs(self):
        jobs = scheduler.get_jobs()
        jobs_list = []

        for job in jobs:
            job_dict = {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                # Add more fields as needed
            }
            jobs_list.append(job_dict)

        return jobs_list, 200
