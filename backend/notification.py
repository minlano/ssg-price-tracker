import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import get_db_connection
import threading
import time

# 이메일 설정 (실제 사용시 환경변수로 관리)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@gmail.com'  # 실제 이메일로 변경
EMAIL_PASSWORD = 'your-app-password'    # Gmail 앱 비밀번호

def send_email(to_email, subject, body):
    """이메일 발송"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        
        print(f"이메일 발송 완료: {to_email}")
        return True
        
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return False

def check_price_alerts():
    """가격 알림 체크"""
    conn = get_db_connection()
    
    # 활성 알림 조회
    alerts = conn.execute('''
        SELECT a.*, p.name, p.current_price, p.url
        FROM alerts a
        JOIN products p ON a.product_id = p.id
        WHERE a.is_active = 1
    ''').fetchall()
    
    for alert in alerts:
        if alert['current_price'] <= alert['target_price']:
            # 목표 가격 도달 시 이메일 발송
            subject = f"[SSG 가격 알림] {alert['name']} 목표 가격 도달!"
            
            body = f"""
            <html>
            <body>
                <h2>가격 알림</h2>
                <p><strong>상품명:</strong> {alert['name']}</p>
                <p><strong>현재 가격:</strong> {alert['current_price']:,}원</p>
                <p><strong>목표 가격:</strong> {alert['target_price']:,}원</p>
                <p><strong>상품 링크:</strong> <a href="{alert['url']}">바로가기</a></p>
                <p>지금 바로 확인해보세요!</p>
            </body>
            </html>
            """
            
            if send_email(alert['user_email'], subject, body):
                # 알림 비활성화 (중복 발송 방지)
                conn.execute(
                    'UPDATE alerts SET is_active = 0 WHERE id = ?',
                    (alert['id'],)
                )
                conn.commit()
    
    conn.close()

def start_notification_scheduler():
    """알림 스케줄러 시작"""
    def scheduler():
        while True:
            try:
                check_price_alerts()
                time.sleep(300)  # 5분마다 체크
            except Exception as e:
                print(f"스케줄러 오류: {e}")
                time.sleep(60)  # 오류 시 1분 후 재시도
    
    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    print("알림 스케줄러가 시작되었습니다.")

if __name__ == '__main__':
    # 테스트 이메일 발송
    test_email = "test@example.com"
    send_email(test_email, "테스트", "알림 시스템 테스트입니다.")