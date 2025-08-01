#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# === 가격 추적 핵심 로직 구현 시작 ===
"""
가격 추적 시스템 핵심 로직
- 3시간마다 가격 체크
- 최저가 갱신시 이메일 알림
- 가격 히스토리 저장
"""

# === 이메일 관련 import 제거 및 함수 내부로 이동 시작 ===
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta
import smtplib
# from email.mime.text import MimeText  # 함수 내부로 이동
# from email.mime.multipart import MimeMultipart  # 함수 내부로 이동
import os
from dotenv import load_dotenv
import logging
import time
import json
# === 이메일 관련 import 제거 및 함수 내부로 이동 끝 ===

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PriceTracker:
    """가격 추적 메인 클래스"""
    
    def __init__(self):
        # === 기존 데이터베이스와 통합 시작 ===
        # self.db_path = 'database/price_tracker.db'  # 기존 추적 전용 DB 주석 처리
        self.db_path = '../database/ssg_tracker.db'  # 기존 데이터베이스와 통합
        # === 기존 데이터베이스와 통합 끝 ===
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email_user = os.getenv('GMAIL_EMAIL')  # 환경변수명 수정
        self.email_password = os.getenv('GMAIL_APP_PASSWORD')  # 환경변수명 수정
        
    def init_database(self):
        """데이터베이스 초기화 - 기존 데이터베이스와 통합"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 테이블들이 이미 존재하므로 추가 테이블만 생성
        
        # 가격 히스토리 테이블 (기존 price_logs와 별도로 추적용)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # 가격 알림 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                alert_type TEXT NOT NULL,
                email_sent INTEGER DEFAULT 0,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 가격 추적 데이터베이스 초기화 완료")
    
    # === 기존 데이터베이스와 통합된 추적 목록 추가 기능으로 변경 시작 ===
    def add_to_watchlist(self, product_name, product_url, image_url, source, current_price, user_email, target_price=None):
        """기존 데이터베이스에 상품 추가 및 추적 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 상품 확인 (URL 기준)
            cursor.execute('SELECT id FROM products WHERE url = ?', (product_url,))
            existing_product = cursor.fetchone()
            
            if existing_product:
                product_id = existing_product[0]
                # 기존 상품의 현재 가격 업데이트
                cursor.execute('''
                    UPDATE products SET current_price = ?, updated_at = datetime('now', '+09:00')
                    WHERE id = ?
                ''', (current_price, product_id))
                logger.info(f"✅ 기존 상품 업데이트: {product_name} (ID: {product_id})")
            else:
                # 새 상품 추가
                cursor.execute('''
                    INSERT INTO products (name, current_price, url, image_url, brand, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+09:00'))
                ''', (product_name, current_price, product_url, image_url, '', source))
                product_id = cursor.lastrowid
                logger.info(f"✅ 새 상품 추가: {product_name} (ID: {product_id})")
            
            # 가격 로그 추가 (기존 price_logs 테이블)
            cursor.execute('''
                INSERT INTO price_logs (product_id, price, logged_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, current_price))
            
            # 가격 히스토리 추가 (추적용 price_history 테이블)
            cursor.execute('''
                INSERT INTO price_history (product_id, price, recorded_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, current_price))
            
            # 알림 설정 추가
            if target_price is None:
                target_price = int(current_price * 0.9)  # 기본 목표가: 현재 가격의 90%
            
            cursor.execute('''
                INSERT OR REPLACE INTO alerts (product_id, user_email, target_price, is_active)
                VALUES (?, ?, ?, 1)
            ''', (product_id, user_email, target_price))
            
            conn.commit()
            logger.info(f"✅ 추적 목록에 상품 추가: {product_name} (ID: {product_id})")
            return product_id
            
        except Exception as e:
            logger.error(f"❌ 추적 목록 추가 실패: {e}")
            return None
        finally:
            conn.close()
    # === 기존 데이터베이스와 통합된 추적 목록 추가 기능으로 변경 끝 ===
    
    def get_watchlist(self, user_email):
        """사용자의 추적 목록 조회 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.id,
                p.name as product_name,
                p.current_price,
                p.url as product_url,
                p.image_url,
                p.brand,
                p.source,
                p.created_at,
                a.target_price,
                a.is_active
            FROM products p
            JOIN alerts a ON p.id = a.product_id
            WHERE a.user_email = ? AND a.is_active = 1
            ORDER BY p.created_at DESC
        ''', (user_email,))
        
        results = cursor.fetchall()
        conn.close()
        
        watchlist = []
        for row in results:
            watchlist.append({
                'id': row[0],
                'product_name': row[1],
                'current_price': row[2],
                'product_url': row[3],
                'image_url': row[4],
                'brand': row[5],
                'source': row[6],
                'created_at': row[7],
                'target_price': row[8],
                'is_active': row[9]
            })
        
        return watchlist

    # === 임시 추적 목록 관리 메서드 시작 ===
    # === 기존 데이터베이스와 통합된 임시 추적 목록 추가 기능으로 변경 시작 ===
    def add_to_temp_watchlist(self, product_name, product_url, image_url, source, current_price, target_price=None):
        """임시 추적 목록에 상품 추가 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 상품 확인 (URL 기준)
            cursor.execute('SELECT id FROM products WHERE url = ?', (product_url,))
            existing_product = cursor.fetchone()
            
            if existing_product:
                product_id = existing_product[0]
                # 기존 상품의 현재 가격 업데이트
                cursor.execute('''
                    UPDATE products SET current_price = ?, updated_at = datetime('now', '+09:00')
                    WHERE id = ?
                ''', (current_price, product_id))
            else:
                # 새 상품 추가
                cursor.execute('''
                    INSERT INTO products (name, current_price, url, image_url, brand, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+09:00'))
                ''', (product_name, current_price, product_url, image_url, '', source))
                product_id = cursor.lastrowid
            
            # 가격 로그 추가 (기존 price_logs 테이블)
            cursor.execute('''
                INSERT INTO price_logs (product_id, price, logged_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, current_price))
            
            # 가격 히스토리 추가 (추적용 price_history 테이블)
            cursor.execute('''
                INSERT INTO price_history (product_id, price, recorded_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, current_price))
            
            # 임시 알림 설정 (is_active = 0으로 설정)
            if target_price is None:
                target_price = int(current_price * 0.9)
            
            cursor.execute('''
                INSERT OR REPLACE INTO alerts (product_id, user_email, target_price, is_active)
                VALUES (?, ?, ?, 0)
            ''', (product_id, 'temp@temp.com', target_price))
            
            conn.commit()
            logger.info(f"✅ 임시 추적 목록에 상품 추가: {product_name} (ID: {product_id})")
            return product_id
            
        except Exception as e:
            logger.error(f"❌ 임시 추적 목록 추가 실패: {e}")
            return None
        finally:
            conn.close()
    # === 기존 데이터베이스와 통합된 임시 추적 목록 추가 기능으로 변경 끝 ===

    def get_temp_watchlist(self):
        """임시 추적 목록 조회 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.id,
                p.name as product_name,
                p.current_price,
                p.url as product_url,
                p.image_url,
                p.brand,
                p.source,
                p.created_at,
                a.target_price
            FROM products p
            JOIN alerts a ON p.id = a.product_id
            WHERE a.user_email = 'temp@temp.com' AND a.is_active = 0
            ORDER BY p.created_at DESC
        ''', ())
        
        results = cursor.fetchall()
        conn.close()
        
        watchlist = []
        for row in results:
            watchlist.append({
                'id': row[0],
                'product_name': row[1],
                'current_price': row[2],
                'product_url': row[3],
                'image_url': row[4],
                'brand': row[5],
                'source': row[6],
                'created_at': row[7],
                'target_price': row[8]
            })
        
        return watchlist

    def activate_temp_watchlist(self, user_email):
        """임시 추적 목록을 실제 추적 목록으로 활성화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 임시 알림을 실제 사용자 이메일로 변경하고 활성화
            cursor.execute('''
                UPDATE alerts 
                SET user_email = ?, is_active = 1
                WHERE user_email = 'temp@temp.com' AND is_active = 0
            ''', (user_email,))
            
            activated_count = cursor.rowcount
            
            # 활성화된 상품들의 가격 히스토리 확인 및 보완
            if activated_count > 0:
                cursor.execute('''
                    SELECT DISTINCT product_id 
                    FROM alerts 
                    WHERE user_email = ? AND is_active = 1
                ''', (user_email,))
                
                activated_products = cursor.fetchall()
                
                for (product_id,) in activated_products:
                    # price_history에 데이터가 있는지 확인
                    cursor.execute('''
                        SELECT COUNT(*) FROM price_history WHERE product_id = ?
                    ''', (product_id,))
                    
                    history_count = cursor.fetchone()[0]
                    
                    # price_history에 데이터가 없으면 현재 가격으로 초기 데이터 추가
                    if history_count == 0:
                        cursor.execute('''
                            SELECT current_price FROM products WHERE id = ?
                        ''', (product_id,))
                        
                        current_price = cursor.fetchone()[0]
                        
                        if current_price:
                            cursor.execute('''
                                INSERT INTO price_history (product_id, price, recorded_at)
                                VALUES (?, ?, datetime('now', '+09:00'))
                            ''', (product_id, current_price))
                            
                            logger.info(f"✅ 상품 ID {product_id}의 초기 가격 히스토리 추가")
            
            conn.commit()
            
            logger.info(f"✅ {activated_count}개 상품이 추적 목록으로 활성화됨")
            return activated_count
            
        except Exception as e:
            logger.error(f"❌ 임시 목록 활성화 실패: {e}")
            return 0
        finally:
            conn.close()

    def remove_from_temp_watchlist(self, watch_id):
        """임시 추적 목록에서 상품 제거"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 해당 상품의 임시 알림 제거
            cursor.execute('''
                DELETE FROM alerts 
                WHERE product_id = ? AND user_email = 'temp@temp.com' AND is_active = 0
            ''', (watch_id,))
            
            conn.commit()
            logger.info(f"✅ 임시 추적 목록에서 상품 제거: ID {watch_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 임시 추적 목록 제거 실패: {e}")
            return False
        finally:
            conn.close()
    # === 임시 추적 목록 관리 메서드 끝 ===

    def get_price_history(self, watch_id, days=7):
        """가격 히스토리 조회 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # price_history 테이블에서 조회 (추적용)
        cursor.execute('''
            SELECT price, recorded_at
            FROM price_history 
            WHERE product_id = ? AND recorded_at >= datetime('now', '-{} days')
            ORDER BY recorded_at ASC
        '''.format(days), (watch_id,))
        
        results = cursor.fetchall()
        
        # price_history에 데이터가 없으면 price_logs에서 조회
        if not results:
            cursor.execute('''
                SELECT price, logged_at as recorded_at
                FROM price_logs 
                WHERE product_id = ? AND logged_at >= datetime('now', '-{} days')
                ORDER BY logged_at ASC
            '''.format(days), (watch_id,))
            results = cursor.fetchall()
        
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'price': row[0],
                'recorded_at': row[1]
            })
        
        return history
    
    def check_ssg_price(self, product_url):
        """SSG 상품 가격 체크"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(product_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SSG 가격 선택자 (실제 선택자로 수정 필요)
            price_element = soup.select_one('.ssg_price .blind')
            if price_element:
                price_text = price_element.get_text().strip()
                price = float(price_text.replace(',', '').replace('원', ''))
                return price
                
        except Exception as e:
            logger.error(f"❌ SSG 가격 체크 실패: {e}")
        
        return None
    
    def check_naver_price(self, product_url):
        """네이버 쇼핑 상품 가격 체크"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(product_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 네이버 쇼핑 가격 선택자 (실제 선택자로 수정 필요)
            price_element = soup.select_one('.price_num')
            if price_element:
                price_text = price_element.get_text().strip()
                price = float(price_text.replace(',', '').replace('원', ''))
                return price
                
        except Exception as e:
            logger.error(f"❌ 네이버 가격 체크 실패: {e}")
        
        return None
    
    def send_price_alert(self, user_email, product_name, old_price, new_price, product_url):
        """가격 알림 이메일 발송"""
        try:
            # === 이메일 관련 import를 함수 내부로 이동 시작 ===
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            # === 이메일 관련 import를 함수 내부로 이동 끝 ===
            
            if not self.email_user or not self.email_password:
                logger.error("❌ 이메일 설정이 없습니다")
                return False
            
            # 이메일 내용 구성
            subject = f"🔥 최저가 알림: {product_name}"
            
            html_body = f"""
            <html>
            <body>
                <h2>🎉 최저가 갱신 알림!</h2>
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h3>{product_name}</h3>
                    <p><strong>이전 가격:</strong> <span style="text-decoration: line-through; color: #999;">{old_price:,}원</span></p>
                    <p><strong>현재 가격:</strong> <span style="color: #e74c3c; font-size: 18px; font-weight: bold;">{new_price:,}원</span></p>
                    <p><strong>할인 금액:</strong> <span style="color: #27ae60; font-weight: bold;">{old_price - new_price:,}원 절약!</span></p>
                    <br>
                    <a href="{product_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">상품 보러가기</a>
                </div>
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    이 알림은 SSG 가격 추적기에서 자동으로 발송되었습니다.
                </p>
            </body>
            </html>
            """
            
            # 이메일 메시지 생성
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = user_email
            
            html_part = MimeText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ 가격 알림 이메일 발송 완료: {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 이메일 발송 실패: {e}")
            return False
    
    # === 기존 데이터베이스와 통합된 가격 체크 기능으로 변경 시작 ===
    def check_all_prices(self):
        """모든 추적 상품의 가격 체크 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 활성 추적 목록 조회 (기존 데이터베이스 구조 사용)
        cursor.execute('''
            SELECT 
                p.id, p.name, p.url, p.source, p.current_price, a.user_email
            FROM products p
            JOIN alerts a ON p.id = a.product_id
            WHERE a.is_active = 1
        ''')
        
        watchlist = cursor.fetchall()
        
        for item in watchlist:
            product_id, product_name, product_url, source, current_price, user_email = item
            
            # 소스별 가격 체크
            new_price = None
            if source == 'SSG':
                new_price = self.check_ssg_price(product_url)
            elif source == 'NAVER' or source == 'NaverShopping':
                new_price = self.check_naver_price(product_url)
            elif source == '11번가' or source == '11ST':
                new_price = self.check_11st_price(product_url)
            
            if new_price and new_price != current_price:
                # 가격 히스토리 저장 (추적용)
                cursor.execute('''
                    INSERT INTO price_history (product_id, price, recorded_at)
                    VALUES (?, ?, datetime('now', '+09:00'))
                ''', (product_id, new_price))
                
                # 가격 로그 저장 (기존 price_logs 테이블)
                cursor.execute('''
                    INSERT INTO price_logs (product_id, price, logged_at)
                    VALUES (?, ?, datetime('now', '+09:00'))
                ''', (product_id, new_price))
                
                # 최저가 갱신 체크
                cursor.execute('''
                    SELECT MIN(price) FROM price_history WHERE product_id = ?
                ''', (product_id,))
                
                min_price = cursor.fetchone()[0]
                
                if new_price <= min_price:
                    # 최저가 갱신 알림
                    alert_sent = self.send_price_alert(user_email, product_name, current_price, new_price, product_url)
                    
                    # 알림 로그 저장
                    cursor.execute('''
                        INSERT INTO price_alerts (product_id, old_price, new_price, alert_type, email_sent, sent_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (product_id, current_price, new_price, 'lowest_price', 1 if alert_sent else 0, datetime.now() if alert_sent else None))
                
                # 현재 가격 업데이트
                cursor.execute('''
                    UPDATE products SET current_price = ?, updated_at = datetime('now', '+09:00')
                    WHERE id = ?
                ''', (new_price, product_id))
                
                logger.info(f"📊 가격 업데이트: {product_name} ({source}) {current_price}원 → {new_price}원")
            
            # 요청 간격 (서버 부하 방지)
            time.sleep(2)
        
        conn.commit()
        conn.close()
        logger.info("✅ 전체 가격 체크 완료 (기존 데이터베이스 통합)")
    # === 기존 데이터베이스와 통합된 가격 체크 기능으로 변경 끝 ===
    
    def remove_from_watchlist(self, watch_id, user_email):
        """추적 목록에서 상품 제거 - 기존 데이터베이스 사용"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 해당 상품의 알림 설정 비활성화
            cursor.execute('''
                UPDATE alerts 
                SET is_active = 0
                WHERE product_id = ? AND user_email = ?
            ''', (watch_id, user_email))
            
            conn.commit()
            logger.info(f"✅ 추적 목록에서 상품 제거: ID {watch_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 추적 목록 제거 실패: {e}")
            return False
        finally:
            conn.close()

    # === 통합 쇼핑몰 지원 메서드 추가 시작 ===
    def _normalize_product_data(self, product_name, product_url, image_url, source, current_price):
        """상품 데이터 정규화"""
        return {
            'name': product_name.strip(),
            'url': product_url.strip(),
            'image_url': image_url.strip() if image_url else '',
            'source': source.upper().strip(),
            'price': float(current_price) if current_price else 0
        }

    def check_11st_price(self, product_url):
        """11번가 상품 가격 체크"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(product_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 11번가 가격 선택자 (실제 선택자로 수정 필요)
            price_element = soup.select_one('.price')
            if price_element:
                price_text = price_element.get_text().strip()
                price = float(price_text.replace(',', '').replace('원', ''))
                return price
                
        except Exception as e:
            logger.error(f"❌ 11번가 가격 체크 실패: {e}")
        
        return None
    # === 통합 쇼핑몰 지원 메서드 추가 끝 ===

# 가격 추적기 인스턴스 생성
price_tracker = PriceTracker()

# 데이터베이스 초기화
price_tracker.init_database()

if __name__ == "__main__":
    # 데이터베이스 초기화
    price_tracker.init_database()
    
    # 가격 체크 실행
    price_tracker.check_all_prices()
# === 가격 추적 핵심 로직 구현 끝 ===