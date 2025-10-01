from datetime import datetime, timezone
from app.utilities.scheduler_utils import lock_task
from app.utilities.db_utils import get_session_with_retries
from extensions import scheduler
from .service import PaymentTransactionsService
from flask import current_app


#class ItemsTask:
#@scheduler.task('cron', id='payments_job', minute='*/5',max_instances=1)
@lock_task('lock_for_payments_job')
@scheduler.task('interval', id='payments_job', seconds=60*5,max_instances=1, name='check_all_pending_payment_transaction')
def payments_task():
    
    try:
        with scheduler.app.app_context():
            payment_service = PaymentTransactionsService()
            #print('payments_job')
            payment_service.check_all_pending_payment_transaction()
    except Exception as e:
        print(e)
        raise
    finally:
        if get_session_with_retries().is_active:
            get_session_with_retries().close()
        #Session.remove()