import yaml
from mano.utils import mail
import logging


mailhost = "smtp.exmail.qq.com:465"
user = ""
password = ""
to = []


def make_content():
    return ""


def make_attachments():
    return None



def send_mail(to, subject, filename, params):
    variables = {}
    with open(filename) as f:
        exec(f.read(), variables, variables)
    variables.update(params)
    attachments = variables.get("make_attachments", make_attachments)()
    content = variables.get("make_content", make_content)()
    
    smtp = mail.login_ssl(mailhost, user, password)
    mail.send(smtp, subject, to, attachments, content=content)


def load(filename):
    return yaml.load(open(filename))


from datetime import datetime

def check_time(now, rule):
    minute, hour, day, month, week = rule.split(' ')
    for t, r in [(now.minute, minute), (now.hour, hour), (now.day, day), (now.month, month), (now.isoweekday(), week)]:
        if not match(t, r):
            return False
    return True


def match(time, rule):
    if rule == "*":
        return True
    for t in split(rule):
        if t == time:
            return True
    return False


def split(t):
    if "-" in t:
        start, end = t.split("-")
        return range(int(start), int(end)+1)
    else:
        return map(int, t.split(","))


def run(filename):
    now = datetime.now()
    conf = load(filename)
    globals().update(conf.get("from", {}))
    globals()["to"] = conf.get("to", [])
    for name, config in conf["services"].items():
        rule = config.get("time", "* * * * *")
        try:
            do = check_time(now, rule)
        except Exception as e:
            logging.error("check time | %s | %s | %s", name, rule, e)
            continue
        if do:
            
            try:
                send_mail(
                    config.get("to", to),
                    config.get("subject", name),
                    config["filename"],
                    config.get("params", {})
                )
            except Exception as e:
                logging.error("send mail | %s | %s", name, e)
            else:
                logging.warning("send mail | %s | success", name)


if __name__ == '__main__':
    import sys
    try:
        filename = sys.argv[1]
    except:
        filename = "conf/works.yml"
    
    run(sys.argv[1])