from flask import current_app
from functools import wraps
from config import SchedulerConfig
""" 
def run_task_with_lock(task, lock_name):
        if scheduler_redis_client() is not None:
            lock = scheduler_redis_client().lock(lock_name, timeout=600)
            have_lock = lock.acquire(blocking=False)
        else:
            have_lock = True

        if have_lock:
            try:
                task()
            finally:
                if scheduler_redis_client() is not None:
                    lock.release()
"""
def lock_task(lock_name):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    rd_client = SchedulerConfig.SCHEDULER_REDUIS_CLIENT
                    #print("lock_name: ", lock_name)
                    #print("scheduler_redis_client(): ", SchedulerConfig.scheduler_redis_client())
                    #print("scheduler_redis_client(): ", SchedulerConfig().scheduler_redis_client())
                    #current_app.logger.error("lock_name: " + lock_name)
                    if rd_client is not None:
                        #print("scheduler_redis_client() is not None")
                        #current_app.logger.error("scheduler_redis_client() is not None")
                        lock = rd_client.lock(lock_name, timeout=600)
                        have_lock = lock.acquire(blocking=False)
                    else:
                        #print("scheduler_redis_client() is None")
                        #current_app.logger.error("scheduler_redis_client() is None")
                        have_lock = True

                    if have_lock:
                        try:
                            return f(*args, **kwargs)
                        finally:
                            if rd_client is not None:
                                lock.release()
                except Exception as e:
                    print("lock_task Exception: ", e)
                    #current_app.logger.error("lock_task Exception: " + e)
                    raise e
            return decorated_function
        return decorator