import pymongo
import pandas as pd
from datautils.mongodb import read
import logging
from mano.utils.mail import make_excel_attachment
from datetime import datetime, timedelta


HOST = "localhost"
LOG = "log.tick_backup"
DAYS = 2


__RESULT = None
__START = None
__END = None


def make_content():
    if not isinstance(__RESULT, pd.DataFrame):
        return "No gap foung from %s to %s" % (__START, __END)
    
    text = "%s records of gap found from %s to %s. \n%s filled." % (len(__RESULT), __START, __END, sum(__RESULT["fill"]>0))

    return text


def make_attachments():
    db, log = LOG.split(".", 1)
    collection = pymongo.MongoClient(HOST)[db][log]
    globals()["__END"] = datetime.now()
    globals()["__START"] = __END - timedelta(days=DAYS)
    table = read(collection, end=(__START, None))
    if not len(table):
        return
    table["gap"] = (table["end"] - table["start"]).apply(str)
    globals()["__RESULT"] = table
    return [make_excel_attachment("backuplog.xlsx", table[["name", "start", "end", "gap", "fill"]])]
