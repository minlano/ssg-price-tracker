#!/usr/bin/env python3
"""
이메일 전송 서비스
Gmail SMTP를 사용하여 가격 알림 및 환영 이메일을 전송합니다.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

class EmailService:
    def __init__(self):
        self.gmail_email = os.getenv('GMAIL_EMAIL')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, html_content, text_content=None):
        """이메일 전송"""
        try:
            if not self.gmail_email or not self.gmail_password:
                self.logger.error("Gmail 설정이 없습니다. .env 파일을 확인해주세요.")
                return False
            
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 내용 추가
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 텍스트 내용 추가 (있는 경우)
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_email, self.gmail_password)
                server.send_message(msg)
            
            self.logger.info(f"이메일 전송 성공: {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"이메일 전송 실패: {e}")
            return False
    
    def send_welcome_email(self, user_email, activated_count):
        """환영 이메일 전송"""
        subject = "🎉 SSG 가격 추적 시스템 환영합니다!"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .highlight {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-item {{ text-align: center; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 SSG 가격 추적 시스템</h1>
                    <p>가격 변동 알림 서비스에 가입하신 것을 환영합니다!</p>
                </div>
                
                <div class="content">
                    <h2>안녕하세요! 👋</h2>
                    <p>SSG 가격 추적 시스템에 성공적으로 가입하셨습니다.</p>
                    
                    <div class="highlight">
                        <h3>📊 현재 추적 현황</h3>
                        <div class="stats">
                            <div class="stat-item">
                                <div class="stat-number">{activated_count}</div>
                                <div>추적 상품</div>
                            </div>
                        </div>
                    </div>
                    
                    <h3>🔔 알림 서비스</h3>
                    <ul>
                        <li>추적 중인 상품의 가격이 변동되면 즉시 알림을 받으실 수 있습니다.</li>
                        <li>목표 가격에 도달하면 특별 알림을 받으실 수 있습니다.</li>
                        <li>주기적으로 가격 변동 리포트를 받으실 수 있습니다.</li>
                    </ul>
                    
                    <h3>📈 주요 기능</h3>
                    <ul>
                        <li><strong>실시간 가격 추적:</strong> SSG.COM 상품의 가격 변동을 실시간으로 모니터링</li>
                        <li><strong>가격 차트:</strong> 상품별 가격 변동 이력을 차트로 확인</li>
                        <li><strong>알림 설정:</strong> 원하는 가격에 도달하면 이메일 알림</li>
                        <li><strong>다중 소스:</strong> SSG, 네이버 쇼핑, 11번가 등 다양한 쇼핑몰 지원</li>
                    </ul>
                    
                    <div class="highlight">
                        <h3>💡 사용 팁</h3>
                        <p>더 많은 상품을 추적하고 싶으시다면 상품 검색에서 관심 있는 상품을 찾아 추적 목록에 추가해보세요!</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>감사합니다! 🛒</p>
                    <p><small>이 이메일은 SSG 가격 추적 시스템에서 자동으로 발송되었습니다.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
SSG 가격 추적 시스템 환영합니다!

안녕하세요! SSG 가격 추적 시스템에 성공적으로 가입하셨습니다.

📊 현재 추적 현황
- 추적 상품: {activated_count}개

🔔 알림 서비스
- 추적 중인 상품의 가격이 변동되면 즉시 알림을 받으실 수 있습니다.
- 목표 가격에 도달하면 특별 알림을 받으실 수 있습니다.
- 주기적으로 가격 변동 리포트를 받으실 수 있습니다.

📈 주요 기능
- 실시간 가격 추적: SSG.COM 상품의 가격 변동을 실시간으로 모니터링
- 가격 차트: 상품별 가격 변동 이력을 차트로 확인
- 알림 설정: 원하는 가격에 도달하면 이메일 알림
- 다중 소스: SSG, 네이버 쇼핑, 11번가 등 다양한 쇼핑몰 지원

💡 사용 팁
더 많은 상품을 추적하고 싶으시다면 상품 검색에서 관심 있는 상품을 찾아 추적 목록에 추가해보세요!

감사합니다! 🛒
        """
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_price_alert_email(self, user_email, product_name, old_price, new_price, product_url, change_percentage):
        """가격 변동 알림 이메일 전송"""
        subject = f"💰 가격 변동 알림: {product_name}"
        
        # 가격 변동 방향에 따른 이모지
        if new_price < old_price:
            trend_emoji = "📉"
            trend_text = "가격 하락"
            color = "#4caf50"  # 녹색
        elif new_price > old_price:
            trend_emoji = "📈"
            trend_text = "가격 상승"
            color = "#f44336"  # 빨간색
        else:
            trend_emoji = "➡️"
            trend_text = "가격 유지"
            color = "#2196f3"  # 파란색
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .price-change {{ background: {color}; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
                .price-details {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .price-item {{ text-align: center; }}
                .price-number {{ font-size: 24px; font-weight: bold; }}
                .old-price {{ text-decoration: line-through; color: #666; }}
                .new-price {{ color: {color}; }}
                .product-link {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{trend_emoji} 가격 변동 알림</h1>
                    <p>추적 중인 상품의 가격이 변동되었습니다!</p>
                </div>
                
                <div class="content">
                    <h2>{product_name}</h2>
                    
                    <div class="price-change">
                        <h3>{trend_emoji} {trend_text}</h3>
                        <p>변동률: {change_percentage:.1f}%</p>
                    </div>
                    
                    <div class="price-details">
                        <div class="price-item">
                            <div class="price-number old-price">{old_price:,}원</div>
                            <div>이전 가격</div>
                        </div>
                        <div class="price-item">
                            <div class="price-number new-price">{new_price:,}원</div>
                            <div>현재 가격</div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{product_url}" class="product-link" target="_blank">
                            🔗 상품 확인하기
                        </a>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>💡 추천</h3>
                        <p>가격이 하락했다면 구매 타이밍일 수 있습니다!</p>
                        <p>가격이 상승했다면 다른 상품과 비교해보세요.</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>SSG 가격 추적 시스템</p>
                    <p><small>이 알림은 자동으로 발송되었습니다.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
가격 변동 알림

상품: {product_name}
변동: {trend_emoji} {trend_text}
변동률: {change_percentage:.1f}%

이전 가격: {old_price:,}원
현재 가격: {new_price:,}원

상품 확인: {product_url}

💡 추천
가격이 하락했다면 구매 타이밍일 수 있습니다!
가격이 상승했다면 다른 상품과 비교해보세요.

SSG 가격 추적 시스템
        """
        
        return self.send_email(user_email, subject, html_content, text_content)

# 전역 이메일 서비스 인스턴스
email_service = EmailService() 