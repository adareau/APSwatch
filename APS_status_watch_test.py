#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
File    : getpaper_tests
Author  : A. Dareau

Comments: tests for getpaper
"""
#%% Imports

import requests

import os
import ConfigParser
import smtplib
import time
from email.mime.text import MIMEText

from bs4 import BeautifulSoup

#%% Settings
URL = 'https://authors.aps.org/Submissions/status'
ARCHIVE_FOLDER = os.path.join('stored')
CONF_FILE = os.path.join('.', 'papers.conf')
MAIL_CONF_FILE = os.path.join('.', 'mail.conf')
#%% Functions

def send_alert(paper, content):
    global MAIL_CONF_FILE
    cfg = ConfigParser.ConfigParser()
    cfg.read(MAIL_CONF_FILE)
    # Get settings
    if cfg.has_section('email account'):
        smtp_server = cfg.get('email account','smtp_server')
        smtp_port = int(cfg.get('email account','smtp_port'))
        smtp_user = cfg.get('email account','smtp_user')
        smtp_password = cfg.get('email account','smtp_password')
        addr_from = cfg.get('email account','smtp_from')
        send_to = cfg.get('email account','send_to')
        s = smtplib.SMTP(smtp_server,smtp_port)
    else:
        #sys.exit('bad conf file')
        print("bad conf file : no message sent !")
        return

    html = """\
            <html>
              <head></head>
              <body>
                <p>Bonjour,<br><br>

                   Voila le nouveau statut :<br>
                   <hr>
                   %s
                   <hr><br><br>
                   Adishatz, Fragosatpi
                </p>
              </body>
            </html>
            """
    msg_txt ='Bonjour,\n\n'
    msg_txt += ' Voila le nouveau statut : \n\n'
    msg_txt += content
    msg_txt += '\n\n Adishatz, Fragosatpi'

    modif_time = time.strftime("%d/%m/%Y %H:%M")
    subject = '[APS status] %s was modified on %s ' % (paper, modif_time)

    # Construct message
    msg = MIMEText(html % content, 'html')
    msg['To'] = send_to
    msg['From'] = addr_from
    msg['Subject'] = subject

    # Send mail
    print("about to send mail...")
    s.ehlo()
    s.starttls()
    s.login(smtp_user,smtp_password)
    s.sendmail(addr_from, send_to, msg.as_string())
    s.quit()

    print("Mail sent successfully")


def check_status(code, author):
    global URL, ARCHIVE_FOLDER

    data = {'accode':code, 'author':author}

    file_name = data['accode'] + '_' + data['author'] + '.html'
    file_path = os.path.join(ARCHIVE_FOLDER, file_name)

    # get new event list
    r = requests.get(URL, params = data)
    if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')

            attrs = {'class':'listing_table'}
            event_list = soup.find('table', attrs=attrs)
            if event_list is None:
                event_list = 'Error: table not found'
            else:
                event_list = str(event_list)
    else:
        event_list = 'Error : %i'%r.status_code

    # old event
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            old_event_list = file.read()
    else:
        old_event_list = ''

    # compare
    if old_event_list == event_list:
        print('  + No change')
    else:
        print('  + Change !!!')
        with open(file_path, 'w+') as file:
            pass
            #file.write(event_list)
        paper = data['accode'] + ' ' + data['author']
        send_alert(paper, event_list)

def check_all():
    global CONF_FILE
    cp = ConfigParser.ConfigParser()
    cp.read(CONF_FILE)
    for paper in cp.sections():
        print('#### Checking %s paper status' % paper)
        code = cp.get(paper, 'code')
        author = cp.get(paper, 'author')
        check_status(code, author)

#send_alert('paper', 'conten')

cp = check_all()
#check_status('LW15644', 'Dareau')