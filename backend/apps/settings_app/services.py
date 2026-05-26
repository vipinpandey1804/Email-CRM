import smtplib
from email.mime.text import MIMEText


def test_smtp_connection(host: str, port: int, username: str, password: str,
                         use_tls: bool, use_ssl: bool, to_email: str) -> dict:
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
        if use_tls and not use_ssl:
            server.starttls()
        if username:
            server.login(username, password)
        msg = MIMEText('<p>SMTP test from Maven Emailer.</p>', 'html')
        msg['Subject'] = 'Maven Emailer — SMTP Test'
        msg['From'] = username or 'noreply@maven.com'
        msg['To'] = to_email
        server.sendmail(username or 'noreply@maven.com', [to_email], msg.as_string())
        server.quit()
        return {'success': True, 'message': 'Test email sent successfully'}
    except smtplib.SMTPException as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        return {'success': False, 'message': f'Connection failed: {e}'}
