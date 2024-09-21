import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE
from email.encoders import encode_base64
import os

from .ai import summarize_with_bare_api
from configs import ACCOUNT, MAIL_SERVER, CC, TO, CSV_DIR, logger

def send_email(results, subject=None, include_cc=False, attached_file=None):

    body = get_message(subject, results)
    mime_text = MIMEText(body, 'html')

    if body:
        mimemsg = MIMEMultipart()
        mimemsg['From'] = 'SECURITY CENTER' + '<' + ACCOUNT['email'] + '>'
        mimemsg['To'] = TO
        if include_cc and CC is not None:
            mimemsg['Cc'] = CC
        mimemsg['Subject'] = subject
        mimemsg.attach(mime_text)
        part = None 
        attached_file_path = CSV_DIR +'/'+ attached_file
        if attached_file and os.path.isfile(attached_file_path):
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attached_file_path,'rb').read())
            encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename={}'.format(attached_file))
            mimemsg.attach(part)
        try:
            connection = smtplib.SMTP(host=MAIL_SERVER['host'], port=MAIL_SERVER['port'])
            connection.ehlo('mylowercasehost')
            connection.starttls()
            connection.ehlo('mylowercasehost')
            if MAIL_SERVER['host'] == 'smtp.office365.com':
                connection.login(ACCOUNT['email'], ACCOUNT['password'])
            connection.send_message(mimemsg)
            connection.quit()
            return True
        except Exception as e:
            logger.error(e)
            return False
    else:
        return False 

def get_message(subject, results):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Threat Intelligence</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .vertical-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .vertical-table th, .vertical-table td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            .vertical-table th {
                background-color: #f2f2f2;
            }
            .vertical-table td {
                vertical-align: top;
            }
        </style>
    </head>
    <body>
    """

    html += f"""
        <table class="vertical-table">
            <caption style="font-size: 15px; font-weight: bold; color: #333; text-align: center; margin-bottom: 10px;">{subject}</caption>
            <thead>
                <tr>
                    <th style="text-align: center;">No</th>
                    <th style="text-align: center;">Name</th>
                    <th style="text-align: center;">Adversary</th>
                    <th style="text-align: center;">Description</th>
                    <th style="text-align: center;">Reference</th>
                </tr>
            </thead>
            <tbody>
    """

    for i, result in enumerate(results):
        #if i > 0:
        #    break
        # modified = result['modified'].split('.')[0]+'z'
        summarized_description = summarize_with_bare_api(result['description'])
        if result['references']:
            reference = result['references'][0]
        else:
            reference = ''
        
        html += f"""
            <tr>
                <td style="text-align: center;">{i + 1}</td>
                <td>{result['name']}</td>
                <td>{result['adversary']}</td>
                <td>{summarized_description}</td>
                <td><a href={reference}>{reference}</a></td>
            </tr>
        """
    html += '''
            </tbody>
        </table>
    </body>
    </html>
    '''

    return html 
    