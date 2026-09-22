from database.models import SecurityLog
from extensions import db


def log_security_event(user_id, action, ip_address):
    """
    Save a security event to the database.
    """

    log = SecurityLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address
    )

    db.session.add(log)
    db.session.commit()