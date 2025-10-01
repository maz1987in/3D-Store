import time
from sqlalchemy.exc import OperationalError
from database import Session
from contextlib import contextmanager

def get_session_with_retries(retries=3, wait=2):
    """
    Tries to establish a new session with retries in case of a database disconnect.
    """
    for attempt in range(retries):
        try:
            return Session()
        except OperationalError as e:
            if attempt < retries - 1:
                time.sleep(wait)  # Wait before retrying
            else:
                raise e  # Raise error after all retries fail

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Automatically handles commit, rollback, and session closure.
    """
    session = get_session_with_retries()
    #print("Session started")
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        #print("Session closed")
