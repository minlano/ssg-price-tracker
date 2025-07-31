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
        # === 추적 전용 데이터베이스로 변경 시작 ===
        # self.db_path = 'database/ssg_tracker.db'  # 기존 SSG 전용 DB 주석 처리
        self.db_path = 'database/price_tracker.db'  # 추적 전용 DB로 변경
        # === 추적 전용 데이터베이스로 변경 끝 ===
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 추적 목록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_url TEXT NOT NULL,
                image_url TEXT,
                source TEXT NOT NULL,
                current_price REAL NOT NULL,
                target_price REAL,
                user_email TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 가격 히스토리 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watch_id INTEGER NOT NULL,
                price REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (watch_id) REFERENCES watch_list (id)
            )
        ''')
        
        # 가격 알림 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watch_id INTEGER NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                alert_type TEXT NOT NULL,
                email_sent INTEGER DEFAULT 0,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (watch_id) REFERENCES watch_list (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ 가격 추적 데이터베이스 초기화 완료")
    
    # === 통합 추적 목록 추가 기능으로 변경 시작 ===
    def add_to_watchlist(self, product_name, product_url, image_url, source, current_price, user_email, target_price=None):
        """통합 추적 목록에 상품 추가 (모든 쇼핑몰 지원)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 상품 정보를 통합 형식으로 정규화
            normalized_data = self._normalize_product_data(
                product_name, product_url, image_url, source, current_price
            )
            
            cursor.execute('''
                INSERT INTO watch_list (product_name, product_url, image_url, source, current_price, user_email, target_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (normalized_data['name'], normalized_data['url'], normalized_data['image_url'], 
                  normalized_data['source'], normalized_data['price'], user_email, target_price))
            
            watch_id = cursor.lastrowid
            
            # 초기 가격 히스토리 저장
            cursor.execute('''
                INSERT INTO price_history (watch_id, price)
                VALUES (?, ?)
            ''', (watch_id, normalized_data['price']))
            
            conn.commit()
            logger.info(f"✅ 통합 추적 목록에 상품 추가: {normalized_data['name']} ({normalized_data['source']})")
            return watch_id
            
        except Exception as e:
            logger.error(f"❌ 통합 추적 목록 추가 실패: {e}")
            return None
        finally:
            conn.close()
    # === 통합 추적 목록 추가 기능으로 변경 끝 ===
    
    def get_watchlist(self, user_email):
        """사용자의 추적 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, product_name, product_url, image_url, source, current_price, target_price, created_at
            FROM watch_list 
            WHERE user_email = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 30
        ''', (user_email,))
        
        results = cursor.fetchall()
        conn.close()
        
        watchlist = []
        for row in results:
            watchlist.append({
                'id': row[0],
                'product_name': row[1],
                'product_url': row[2],
                'image_url': row[3],
                'source': row[4],
                'current_price': row[5],
                'target_price': row[6],
                'created_at': row[7]
            })
        
        return watchlist

    # === 임시 추적 목록 관리 메서드 시작 ===
    # === 통합 임시 추적 목록 추가 기능으로 변경 시작 ===
    def add_to_temp_watchlist(self, product_name, product_url, image_url, source, current_price, target_price=None):
        """통합 임시 추적 목록에 상품 추가 (모든 쇼핑몰 지원)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 상품 정보를 통합 형식으로 정규화
            normalized_data = self._normalize_product_data(
                product_name, product_url, image_url, source, current_price
            )
            
            cursor.execute('''
                INSERT INTO watch_list (product_name, product_url, image_url, source, current_price, user_email, target_price, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (normalized_data['name'], normalized_data['url'], normalized_data['image_url'], 
                  normalized_data['source'], normalized_data['price'], 'temp@temp.com', target_price, 0))
            
            watch_id = cursor.lastrowid
            
            # 초기 가격 히스토리는 활성화될 때 저장
            conn.commit()
            logger.info(f"✅ 통합 임시 추적 목록에 상품 추가: {normalized_data['name']} ({normalized_data['source']})")
            return watch_id
            
        except Exception as e:
            logger.error(f"❌ 통합 임시 추적 목록 추가 실패: {e}")
            return None
        finally:
            conn.close()
    # === 통합 임시 추적 목록 추가 기능으로 변경 끝 ===

    def get_temp_watchlist(self):
        """임시 추적 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, product_name, product_url, image_url, source, current_price, target_price, created_at
            FROM watch_list 
            WHERE user_email = 'temp@temp.com' AND is_active = 0
            ORDER BY created_at DESC
            LIMIT 30
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        temp_watchlist = []
        for row in results:
            temp_watchlist.append({
                'id': row[0],
                'product_name': row[1],
                'product_url': row[2],
                'image_url': row[3],
                'source': row[4],
                'current_price': row[5],
                'target_price': row[6],
                'created_at': row[7]
            })
        
        return temp_watchlist

    def activate_temp_watchlist(self, user_email):
        """임시 추적 목록을 실제 추적 목록으로 활성화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 임시 추적 목록 조회
            cursor.execute('''
                SELECT id, current_price FROM watch_list 
                WHERE user_email = 'temp@temp.com' AND is_active = 0
            ''')
            
            temp_items = cursor.fetchall()
            
            if not temp_items:
                return 0
            
            # 임시 목록을 실제 목록으로 활성화
            cursor.execute('''
                UPDATE watch_list 
                SET user_email = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE user_email = 'temp@temp.com' AND is_active = 0
            ''', (user_email,))
            
            # 각 상품의 초기 가격 히스토리 저장
            for watch_id, current_price in temp_items:
                cursor.execute('''
                    INSERT INTO price_history (watch_id, price)
                    VALUES (?, ?)
                ''', (watch_id, current_price))
            
            activated_count = len(temp_items)
            conn.commit()
            
            logger.info(f"✅ {activated_count}개 상품이 활성화됨: {user_email}")
            return activated_count
            
        except Exception as e:
            logger.error(f"❌ 추적 목록 활성화 실패: {e}")
            return 0
        finally:
            conn.close()

    # === 임시 추적 목록 삭제 메서드 추가 시작 ===
    def remove_from_temp_watchlist(self, watch_id):
        """임시 추적 목록에서 상품 제거"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 임시 목록에서 해당 상품 삭제
            cursor.execute('''
                DELETE FROM watch_list 
                WHERE id = ? AND user_email = 'temp@temp.com' AND is_active = 0
            ''', (watch_id,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                logger.info(f"✅ 임시 추적 목록에서 제거: ID {watch_id}")
                return True
            else:
                logger.warning(f"⚠️ 임시 추적 목록에서 제거할 상품을 찾을 수 없음: ID {watch_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 임시 추적 목록 제거 실패: {e}")
            return False
        finally:
            conn.close()
    # === 임시 추적 목록 삭제 메서드 추가 끝 ===
    
    # === 임시 추적 목록 관리 메서드 끝 ===
    
    def get_price_history(self, watch_id, days=7):
        """가격 히스토리 조회 (최근 7일)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, recorded_at
            FROM price_history 
            WHERE watch_id = ? AND recorded_at >= datetime('now', '-{} days')
            ORDER BY recorded_at ASC
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
    
    # === 통합 가격 체크 기능으로 변경 시작 ===
    def check_all_prices(self):
        """모든 추적 상품의 가격 체크 (모든 쇼핑몰 지원)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 활성 추적 목록 조회
        cursor.execute('''
            SELECT id, product_name, product_url, source, current_price, user_email
            FROM watch_list 
            WHERE is_active = 1
        ''')
        
        watchlist = cursor.fetchall()
        
        for item in watchlist:
            watch_id, product_name, product_url, source, current_price, user_email = item
            
            # 소스별 가격 체크
            new_price = None
            if source == 'SSG':
                new_price = self.check_ssg_price(product_url)
            elif source == 'NAVER' or source == 'NaverShopping':
                new_price = self.check_naver_price(product_url)
            elif source == '11번가' or source == '11ST':
                new_price = self.check_11st_price(product_url)
            
            if new_price and new_price != current_price:
                # 가격 히스토리 저장
                cursor.execute('''
                    INSERT INTO price_history (watch_id, price)
                    VALUES (?, ?)
                ''', (watch_id, new_price))
                
                # 최저가 갱신 체크
                cursor.execute('''
                    SELECT MIN(price) FROM price_history WHERE watch_id = ?
                ''', (watch_id,))
                
                min_price = cursor.fetchone()[0]
                
                if new_price <= min_price:
                    # 최저가 갱신 알림
                    alert_sent = self.send_price_alert(user_email, product_name, current_price, new_price, product_url)
                    
                    # 알림 로그 저장
                    cursor.execute('''
                        INSERT INTO price_alerts (watch_id, old_price, new_price, alert_type, email_sent, sent_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (watch_id, current_price, new_price, 'lowest_price', 1 if alert_sent else 0, datetime.now() if alert_sent else None))
                
                # 현재 가격 업데이트
                cursor.execute('''
                    UPDATE watch_list SET current_price = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_price, watch_id))
                
                logger.info(f"📊 가격 업데이트: {product_name} ({source}) {current_price}원 → {new_price}원")
            
            # 요청 간격 (서버 부하 방지)
            time.sleep(2)
        
        conn.commit()
        conn.close()
        logger.info("✅ 전체 가격 체크 완료 (모든 쇼핑몰)")
    # === 통합 가격 체크 기능으로 변경 끝 ===
    
    def remove_from_watchlist(self, watch_id, user_email):
        """추적 목록에서 상품 제거"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE watch_list SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_email = ?
        ''', (watch_id, user_email))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ 추적 목록에서 제거: ID {watch_id}")

    # === 통합 쇼핑몰 지원 메서드 추가 시작 ===
    def _normalize_product_data(self, product_name, product_url, image_url, source, current_price):
        """쇼핑몰별 상품 데이터를 통합 형식으로 정규화"""
        try:
            # 상품명 정리 (HTML 태그 제거, 길이 제한)
            clean_name = product_name[:200] if product_name else "상품명 없음"
            
            # URL 정리
            clean_url = product_url if product_url and product_url != '#' else ''
            
            # 이미지 URL 정리
            clean_image_url = image_url if image_url else ''
            
            # 소스명 통일
            source_mapping = {
                'SSG': 'SSG',
                'NAVER': 'NaverShopping',
                'NaverShopping': 'NaverShopping',
                '11번가': '11ST',
                '11ST': '11ST'
            }
            clean_source = source_mapping.get(source, source)
            
            # 가격 정리 (정수형으로 변환)
            clean_price = int(current_price) if current_price and current_price > 0 else 0
            
            return {
                'name': clean_name,
                'url': clean_url,
                'image_url': clean_image_url,
                'source': clean_source,
                'price': clean_price
            }
            
        except Exception as e:
            logger.error(f"❌ 상품 데이터 정규화 실패: {e}")
            return {
                'name': str(product_name)[:200] if product_name else "상품명 없음",
                'url': str(product_url) if product_url else '',
                'image_url': str(image_url) if image_url else '',
                'source': str(source),
                'price': int(current_price) if current_price and current_price > 0 else 0
            }

    def check_11st_price(self, product_url):
        """11번가 상품 가격 체크"""
        try:
            # 11번가는 현재 API 기반이므로 실제 가격 체크 제한적
            # 샘플 구현 (실제로는 11번가 API 호출 필요)
            logger.info(f"11번가 가격 체크 시도: {product_url}")
            
            # 실제 구현시에는 11번가 API를 통해 가격 조회
            # 현재는 제한적 지원으로 None 반환
            return None
            
        except Exception as e:
            logger.error(f"❌ 11번가 가격 체크 실패: {e}")
            return None
    # === 통합 쇼핑몰 지원 메서드 추가 끝 ===

# 전역 인스턴스
price_tracker = PriceTracker()

if __name__ == "__main__":
    # 데이터베이스 초기화
    price_tracker.init_database()
    
    # 가격 체크 실행
    price_tracker.check_all_prices()
# === 가격 추적 핵심 로직 구현 끝 ===