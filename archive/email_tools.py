import smtplib
from email.mime.text import MIMEText
from email.message import Message


def alert(subject, message):
    msg = MIMEText(message)

    msg['Subject']  = subject
    msg['From']     = 'adam.thornton@cern.ch'
    msg['To']       = 'adam.thornton@cern.ch'

    s = smtplib.SMTP('cernmx.cern.ch')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
