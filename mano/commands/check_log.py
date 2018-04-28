from mano.utils import mail
from mano.utils.tools import logger, dict_output
from pymongo import MongoClient
from email.mime.application import MIMEApplication
from datetime import datetime
from io import BytesIO
import pandas as pd
from mano import conf
import logging


class ColReader(object):

    def __init__(self, name, date_key, date_format, index=None):
        self.name = name
        self.date_key = date_key
        self.date_format = date_format
        self.index = index

    def daily(self, db, date):
        dct = {self.date_key: self._get_date(date)}
        result = find_match(db[self.name], **dct)
        return self.decorate(result)

    def _get_date(self, date):
        if isinstance(self.date_format, str):
            return date.strftime(self.date_format)
        else:
            return date

    def range(self, db, start=None, end=None):
        ranges = {}
        if start:
            ranges["$gte"] = self._get_date(start)
        if end:
            ranges["$lte"] = self._get_date(end)
        filters = {self.date_key: ranges} if len(ranges) else None
        result = read(db[self.name], filters, {"_id": 0})

        return self.decorate(result)

    def decorate(self, result):
        if self.index:
            return result.set_index(self.index)
        else:
            return result


FORMATS = {
    "dailyIndicator": ColReader("dailyIndicator", "trade_date", "%Y%m%d", "trade_date"),
    "lb_daily": ColReader("lb_daily", "trade_date", "%Y%m%d", "trade_date"),
    "factor": ColReader("factor", "date", "%Y-%m-%d", "date"),
    "sinta": ColReader("sinta", "date", "%Y-%m-%d", ["date", "symbol"]),
    "future": ColReader("future_mi", "date", None, "date")
}


def get_db():
    return MongoClient(conf.URI)[conf.DB]


def read(collection, *args, **kwargs):
    return pd.DataFrame(list(collection.find(*args, **kwargs)))


def find_match(collection, **kwargs):
    return read(collection, kwargs, {"_id": 0})


def make_excel_attachment(data=None, name="temp.xlsx", **kwargs):
    bio = BytesIO()
    writer = pd.ExcelWriter(name)
    writer.book.filename = bio
    if isinstance(data, pd.DataFrame):
        data.to_excel(writer)
    for key, value in kwargs.items():
        value.to_excel(writer, sheet_name=key)
    writer.save()
    main, sub = mail.get_type(name)
    mime = MIMEApplication(bio.getvalue(), sub)
    mime["Content-Disposition"] = "attachment; filename={}".format(name)
    bio.close()
    writer.close()
    return mime


def send_daily(to=conf.RECEIVERS, tables=tuple(FORMATS.keys()), date=None):
    logging.warning("daily log | %s | %s | %s", date, to, tables)
    db = get_db()
    results = dict(iter_daily(db, tables, datetime.strptime(date, "%Y-%m-%d")))
    att = make_excel_attachment(name="daily_{}.xlsx".format(date), **results)
    smtp = mail.login_ssl(conf.HOST, conf.USER, conf.PASSWORD)
    return mail.send(smtp, "DataService daily check {}".format(date), to, attachments=[att])


def send_range(to=conf.RECEIVERS, tables=tuple(FORMATS.keys()), start=None, end=None):
    db = get_db()
    results = read_range(tables, db,
                         start=datetime.strptime(start, "%Y-%m-%d") if start else start,
                         end=datetime.strptime(end, "%Y-%m-%d") if end else end)
    att = make_excel_attachment(name="range({}~{}).xlsx".format(start, end), **results)
    smtp = mail.login_ssl(conf.HOST, conf.USER, conf.PASSWORD)
    mail.send(smtp, "DataService log range {} ~ {}".format(start, end), to, attachments=[att])


def iter_daily(db, tables, date):
    for name in tables:
        data = read_daily(name, date, db)
        if len(data.index):
            yield name, data
        else:
            logging.warning("log | %s | %s | empty", name, date)


@logger("daily", 0, 1, success="OK", default=lambda: pd.DataFrame())
def read_daily(name, date, db):
    reader = FORMATS[name]
    return reader.daily(db, date)


@logger("range", 0, "start", "end", success="OK", default=lambda: pd.DataFrame())
@dict_output(0)
def read_range(name, db, start=None, end=None):
    reader = FORMATS[name]
    return reader.range(db, start, end)


from functools import wraps


def kw_default(condition=lambda v: v is None, **kw):
    def wrapper(func):
        @wraps(func)
        def wrapped(**kwargs):
            for key, value in kw.items():
                if condition(kwargs.get(key, None)):
                    kwargs[key] = value
            return func(**kwargs)
        return wrapped
    return wrapper


import click


DATE = click.option("--date", "-d", default=datetime.today().strftime("%Y-%m-%d"))
NAMES = click.option("--name", "-n", multiple=True)
START = click.option("--start", "-s", default=None)
END = click.option("--end", "-e", default=None)
TO = click.argument("to", nargs=-1)


@click.command("daily")
@DATE
@TO
@NAMES
@kw_default(lambda v: len(v) == 0, to=conf.RECEIVERS, name=tuple(FORMATS.keys()))
def command_daily(to, name, date):
    send_daily(to, name, date)


@click.command("range")
@TO
@START
@END
@NAMES
@kw_default(lambda v: len(v) == 0, to=conf.RECEIVERS, name=tuple(FORMATS.keys()))
def command_range(to, name, start, end):
    send_range(to, name, start=start, end=end)


notice = click.Group("notice", {'range': command_range,
                                "daily": command_daily})


def send_test():
    conf.URI = "192.168.0.102"
    conf.USER = "cam@fxdayu.com"
    conf.PASSWORD = "Xinger520"
    conf.RECEIVERS = (conf.USER,)
