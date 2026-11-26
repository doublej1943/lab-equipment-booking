from contextlib import contextmanager

from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError, TimeoutError as PoolTimeout
from .extensions import db


class BusinessError(Exception):
    pass


class Invalid(BusinessError):
    pass


class Forbidden(BusinessError):
    pass


class Missing(BusinessError):
    pass


class Conflict(BusinessError):
    pass


class Occupied(Conflict):
    pass


class UnknownCommit(BusinessError):
    def __init__(self, message, recovery, booking_id=None):
        super().__init__(message)
        self.recovery = recovery
        self.booking_id = booking_id


def temporary_failure(error):
    if isinstance(error, PoolTimeout):
        return True
    code = getattr(getattr(error, "orig", None), "sqlstate", None) or ""
    return isinstance(error, OperationalError) or code.startswith(("08", "40", "53")) or code in {"55P03", "57014"}


@contextmanager
def write_transaction(unknown_message, *, recovery="devices.catalog", booking_id=None, unique_name=None, make_conflict=None):
    committing = False
    try:
        yield
        db.session.flush()
        committing = True
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        cause = error.orig
        if (unique_name and getattr(cause, "sqlstate", None) == "23505"
                and getattr(cause.diag, "constraint_name", None) == unique_name):
            raise make_conflict() from None
        raise
    except DBAPIError as error:
        code = getattr(error.orig, "sqlstate", None) or ""
        uncertain = committing and (error.connection_invalidated or not code or code.startswith("08")
                                    or code in {"40003", "57P01", "57P02"})
        db.session.rollback()
        if uncertain:
            raise UnknownCommit(unknown_message, recovery, booking_id) from None
        raise
    except Exception:
        db.session.rollback()
        raise
