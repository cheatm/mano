import pymongo
import pandas as pd
from datautils.mongodb import read
import logging

FIELDS = ["datetime", "open", "low", "close", "high"]

PAIRS = {
    "BTC": ["tBTCUSD", "BTCUSDT"],
    "ETH": ["tETHUSD", "ETHUSDT"],
    "EOS": ["tEOSUSD", "EOSUSDT"],
    "LTC": ["tLTCUSD", "LTCUSDT"],
    "BCH": ["tBCHUSD", "BCCUSDT"],
    "ETC": ["tETCUSD", "ETCUSDT"]
}

BITFINEX_SYMBOLS = ["tBTCUSD", "tETHUSD", "tEOSUSD", "tBCHUSD", "tETCUSD", "tLTCUSD"]
BINANCE_SYMBOLS = ["ETHUSDT", "BTCUSDT", "LTCUSDT", "ETCUSDT", "BCCUSDT", "EOSUSDT"]

HOST = "localhost"
MIN1DB = "VnTrader_1Min_Db"
LOGDB = "log"
START = None
END = None


def run(uri, log_db, data_db):
    client = pymongo.MongoClient(uri)
    log = pymongo.MongoClient(uri)[log_db]


def read_bitfinex_log(db, symbols, start, end):
    results = {}
    fields = ["start", "end", "contract", "date", "count", "inserted"]
    data = read(db["bitfinex"], fields=fields, contract=symbols, date=(start, end))
    data = data.sort_values(["date", "contract"])
    for name, table in data.groupby(data["contract"]):
        results[name] = table.groupby(table["date"])[["count", "inserted"]].sum()
    return data[fields], results


def read_binance_log(db, symbols, start, end):
    results = {}
    fields = ["start", "end", "symbol", "date", "count", "inserted"]
    data = read(db["binance"], fields=fields, symbol=symbols, date=(start, end)).sort_values(["date", "symbol"])
    for name, table in data.groupby(data["symbol"]):
        results[name] = table.groupby(table["date"])[["count", "inserted"]].sum()
    return data[fields], results


def sumlog(db, start, end):
    binance_all, binance = read_binance_log(db, BINANCE_SYMBOLS, start, end)
    write_log("binance_%s~%s.xlsx" % (start, end), binance_all, binance)
    bitfinex_all, bitfinex = read_bitfinex_log(db, BITFINEX_SYMBOLS, start, end)
    write_log("bitfinex_%s~%s.xlsx" % (start, end), bitfinex_all, bitfinex)


def make_log(db, start, end):
    binance_all, binance = read_binance_log(db, BINANCE_SYMBOLS, start, end)
    binance["data"] = binance_all
    bitfinex_all, bitfinex = read_bitfinex_log(db, BITFINEX_SYMBOLS, start, end)
    bitfinex["data"] = bitfinex_all
    return {
        "binance_%s~%s.xlsx" % (start, end): binance,
        "bitfinex_%s~%s.xlsx" % (start, end): bitfinex
    }



def write_log(name, main, others):
    writer = pd.ExcelWriter(name)
    main.to_excel(writer, sheet_name="all", index=False)
    for name, table in others.items():
        table.to_excel(writer, sheet_name=name)
    writer.close()


def compare(frame1, frame2):
    assert isinstance(frame1, pd.DataFrame)
    assert isinstance(frame2, pd.DataFrame)
    return ((frame2 - frame1)/frame1)


def diff(col1, col2, date):
    f1 = read(col1, "datetime", FIELDS, **{"date": date})
    f2 = read(col2, "datetime", FIELDS, **{"date": date})
    return compare(f1, f2)


def analysis(frame, date):
    result = pd.DataFrame({"mean": frame.mean(skipna=True), "std": frame.std(skipna=True)})
    result["date"] = date
    result.index.name = "tag"
    return result.reset_index()[["date", "tag", "mean", "std"]]


def merge(db, symbol1, symbol2, start, end):
    col1 = db[symbol1]
    col2 = db[symbol2]
    results = []
    for date in dates(start, end):
        try:
            frame = diff(col1, col2, date)
            results.append(analysis(frame, date))
        except Exception as e:
            logging.error("merge | %s | %s | %s | %s", symbol1, symbol2, date, e)
        else:
            logging.warning("merge | %s | %s | %s | ok", symbol1, symbol2, date)
    if len(results):
        return pd.concat(results, ignore_index=True).set_index(["date", "tag"])
    else:
        return pd.DataFrame()


def make_merge(db, start, end):
    frames = {}
    for name, pair in PAIRS.items():
        bitfinex, binance = pair 
        frames[name] = merge(db, binance+":binance", bitfinex+":bitfinex", start, end)
    return {"compare_%s~%s.xlsx" % (start, end): frames}


def save_merge(db, start, end):
    filename = "compare_%s~%s.xlsx" % (start, end)
    writer = pd.ExcelWriter(filename)
    for name, pair in PAIRS.items():
        bitfinex, binance = pair 
        result = merge(db, binance+":binance", bitfinex+":bitfinex", start, end)
        result.to_excel(writer, sheet_name=name)
    writer.close()


def dates(start, end):
    for date in pd.date_range(start, end):
        yield date.strftime("%Y%m%d")


from datetime import datetime, timedelta


def last_week():
    today = datetime.today()
    return today - timedelta(days=today.weekday()+7)


def last_weekend():
    return last_week() + timedelta(days=6)


def date_range():
    return (
        START if START else last_week().strftime("%Y-%m-%d"),
        END if END else last_weekend().strftime("%Y-%m-%d")
    )


def make_attachments():
    from mano.utils.mail import make_excel_attachment
    attachments = []
    start, end = date_range()
    client = pymongo.MongoClient(HOST)
    for name, frames in make_log(client[LOGDB], start, end).items():
        attachments.append(make_excel_attachment(name, **frames))
    for name, frames in make_merge(client[MIN1DB], start, end).items():
        attachments.append(make_excel_attachment(name, **frames))
    return attachments


def make_content():
    return ""
    

def clean():
    client = pymongo.MongoClient("192.168.0.104")
    db = client["VnTrader_1Min_Db"]
    for symbol in BINANCE_SYMBOLS:
        col = db[symbol+":binance"]
        for doc in col.find({"date": "20180209"}, {"datetime": 1}):
            dt = doc["datetime"].replace(second=0, microsecond=0)
            col.update_one({"_id": doc["_id"]}, {"$set": {"datetime": dt}})
            print(dt)

