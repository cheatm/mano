import logging
from functools import wraps
import traceback


def logger(tag, *keys, success=None, default=lambda: None):
    formatter = "%s | %s" % (tag, " | ".join(["%s"]*(len(keys)+1)))

    def select(*args, **kwargs):
        for key in keys:
            if isinstance(key, int):
                yield args[key]
            else:
                yield kwargs.get(key, None)

    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            show = list(select(*args, **kwargs))
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                show.append(traceback.format_exc())
                logging.error(formatter, *show)
                return default()
            else:
                if success is None:
                    show.append(result)
                else:
                    show.append(success)
                logging.warning(formatter, *show)
                return result
        return wrapped
    return wrapper


def dict_output(key):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return dict(iter_out(func, key, *args, **kwargs))
        return wrapped
    return wrapper


def iter_out(func, key, *args, **kwargs):
    if isinstance(key, int):
        keys = args[key]
        arguments = list(args)
        for k in keys:
            arguments[key] = k
            try:
                yield k, func(*arguments, **kwargs)
            except Exception as e:
                logging.error("%s | %s", k, e)
    else:
        keys = kwargs[key]
        for k in keys:
            kwargs[key] = k
            try:
                yield k, func(*args, **kwargs)
            except Exception as e:
                logging.error("%s | %s", k, e)