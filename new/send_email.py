import logging
import smtplib, ssl
import os
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse
from os.path import basename

import yaml

from logger import gen_log

# Make email address valid and set email public
# See https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address

logger = gen_log("test")
# Parse command line arguments
parser = argparse.ArgumentParser()

parser.add_argument('-t', '--to', dest='to_email', help='the email receiver')
parser.add_argument('-r', '--result', dest='result', help='the result yml file')
parser.add_argument('-g', '--github_repo', dest='repository', help='github repository')
parser.add_argument('-a', '--attachment', dest='attachment', action='append', help='the files to attach')
parser.add_argument('-l', '--link', dest='link', help='the link to the workflow')


# Parse the command-line arguments
args = parser.parse_args()

# the email address to send the email
server = 'smtp.outlook.com'
port = 587
username = 'Cyrusiris@outlook.com'
password = 'Daohaomei77'

# Email settings
to_email = ''
from_email = username
email_subject = 'Github Action Result'
email_body = 'test'
msg = MIMEMultipart()

# Access the options
if args.to_email:
    logger.info(f'Send email to: {args.to_email}')
    to_email = args.to_email
else:
    logger.error("No email specified")

# Access the log file and concatenate it to the email body
# find log file that is in the same directory as this script
# for file in os.listdir(os.path.dirname(os.path.abspath(__file__))):
#     if file.endswith(".log"):
#         # print(file)
#         pass

# Attach file args.result
with open(args.result, "rb") as attachment:
    part = MIMEApplication(
        attachment.read(),
        Name=basename(args.result)
    )

    # Set subject
    data = yaml.safe_load(open(args.result))
    # Count failure tests
    failed_tests = 0
    passed_tests = 0
    for command in data:
        if command["result"] == "Passed":
            passed_tests += 1
        else:
            failed_tests += 1
    if failed_tests > 0:
        email_subject = f'Failed {failed_tests} tests for {args.repository}'
    else:
        email_subject = f'Passed all tests for {args.repository}'
    attachment.close()
part['Content-Disposition'] = 'attachment; filename="%s"' % basename(args.result)
msg.attach(part)

# Attach files
if args.attachment:
    for file in args.attachment:
        with open(file, "rb") as attachment:
            part = MIMEApplication(
                attachment.read(),
                Name=basename(file)
            )
            attachment.close()
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
        msg.attach(part)


# Create the email message
# Set body
msg.attach(MIMEText(f"Workflow link {args.link}"))
msg['Subject'] = email_subject
msg['From'] = from_email
msg['To'] = to_email

# Send the email using the SMTP server
with smtplib.SMTP(server, port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

print("Email sent successfully!")