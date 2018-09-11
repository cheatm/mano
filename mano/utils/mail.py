import smtplib
from email.message import EmailMessage
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.application import MIMEApplication
import mimetypes
from mano.utils.tools import logger
from io import BytesIO
import pandas as pd


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


def make_excel_attachment(name="temp.xlsx", data=None, **kwargs):
    bio = BytesIO()
    writer = pd.ExcelWriter(name)
    writer.book.filename = bio
    if isinstance(data, pd.DataFrame):
        data.to_excel(writer)
    for key, value in kwargs.items():
        value.to_excel(writer, sheet_name=key)
    writer.save()
    main, sub = get_type(name)
    mime = MIMEApplication(bio.getvalue(), sub)
    mime["Content-Disposition"] = "attachment; filename={}".format(name)
    bio.close()
    writer.close()
    return mime


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


def main():
    message = make_msg("cam@fxdayu.com", "cam@fxdayu.com", "test", content="this is a test")
    print(message)

if __name__ == '__main__':
    main()