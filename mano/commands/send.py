from mano.utils import mail
from mano import conf


def send(to, subject=conf.SUBJECT, content="", attachments=None,
         host=conf.HOST, user=conf.USER, password=conf.PASSWORD):
    smtp = mail.login_ssl(host, user, password)
    if attachments is not None:
        attachments = attachments.split(",")
    else:
        attachments = ()
    mail.send(smtp, subject, to, content=content, attachments=attachments)