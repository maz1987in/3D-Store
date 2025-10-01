from datetime import datetime, timezone
import json
import time
from app.utilities.scheduler_utils import lock_task
from database import engine
from sqlalchemy.pool import Pool
from extensions import scheduler
from flask import current_app
from extensions import cache



#@lock_task('lock_for_once_day_job')
#@scheduler.task('cron', id='sqlalchemy_stats_job', minute='5',max_instances=1, name='sqlalchemy_stats_job')
#@scheduler.task('interval', id='items_hour_job', seconds=60*60,max_instances=1)
def sqlalchemy_stats_job():
    #print('items_hour_task')
    try:
        with scheduler.app.app_context():
            stats = {}
            """
            # Get the SQLAlchemy connection pool status
            connection_pool = engine.pool
            stats["pool_size"] = connection_pool.size()
            stats["checked_out"] = connection_pool.checkedout()
            stats["idle"] = connection_pool.checkedin()
            # Get the number of active sessions
            stats["active_sessions"] = engine.pool._all_external()

            current_time = time.time()
            # Store the statistics in Redis with a timestamp and set an expiration
            timestamp = int(current_time)
            redis_key = f"sqlalchemy_stats_{timestamp}"
            cache.set(redis_key, json.dumps(stats), timeout=60*60*24)
            #redis_client.setex(redis_key, interval_duration, json.dumps(stats))
            """
            

    except Exception as e:
        print(e)
        raise
    #finally:
    #    if Session.is_active:
    #        Session.close()
    #    Session.remove()