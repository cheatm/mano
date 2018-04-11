import smtplib
from email.message import EmailMessage
from email.mime.nonmultipart import MIMENonMultipart
import mimetypes
from mano.utils.tools import logger


def make_msg(_from, _to, subject, attachments=None, content=""):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = _from
    msg["To"] = _to
    msg.set_content(content)
    msg.make_mixed()
    if attachments is not None:
        for atc in attachments:
            add_attachment(msg, atc)
    return msg


def add_attachment(msg, attachment):
    if isinstance(attachment, MIMENonMultipart):
        msg.attach(attachment)
    elif isinstance(attachment, str):
        with open(attachment, "rb") as fp:
            main, sub = get_type(attachment)
            msg.add_attachment(fp.read(), maintype=main, subtype=sub, filename=attachment)


def get_type(filename):
    mtype, encoding = mimetypes.guess_type(filename)
    return mtype.split('/', 1)


@logger("login", 0, 1, success="success")
def login_ssl(host, user, password):
    smtp = smtplib.SMTP_SSL(host)
    smtp.login(user, password)
    return smtp


@logger("send mail", 1, 2, success="success")
def send(smtp, subject, _to, attachments=None, _from=None, content=""):
    if isinstance(smtp, smtplib.SMTP):
        if _from is None:
            _from = smtp.user
        message = make_msg(_from, _to, subject, attachments, content=content)
        smtp.send_message(message)
        return message
    else:
        raise TypeError("Type of smtp should be smtplib.SMTP")
