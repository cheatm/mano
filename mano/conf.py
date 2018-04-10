import os


HOST = os.environ.get("SERVER_HOST", "smtp.exmail.qq.com:465")
USER = os.environ.get("USER", "")
PASSWORD = os.environ.get("PASSWORD", "")
SUBJECT = os.environ.get("DEFAULT_SUBJECT", "")
URI = os.environ.get("MONGODB_URI", "localhost:27017")
DB = os.environ.get("DB_NAME", "log")
DIR = os.environ.get("CONF_DIF", "/conf")


def get_receivers():
    path = os.path.join(DIR, "receivers")
    if os.path.exists(path):
        with open(os.path.join(DIR, "receivers")) as f:
            return tuple(f.readlines())
    else:
        return ()


RECEIVERS = get_receivers()


DICT = {
    "SERVER_HOST": HOST,
    "USER": USER,
    "PASSWORD": PASSWORD,
    "DEFAULT_SUBJECT": SUBJECT,
    "MONGODB_URI": URI,
    "DB_NAME": DB,
    "CONF_DIF": DIR
}
