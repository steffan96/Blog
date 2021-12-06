import os
from functools import wraps

from flask import abort
from flask_login import current_user


def permission_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required():
    return current_user.has_role(3)


import cProfile
import io
import pstats


def profile(fnc):
    @wraps(fnc)
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        return retval

    return inner
