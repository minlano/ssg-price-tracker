#!/usr/bin/env python3
"""
가격 모니터링 및 알림 시스템
추적 중인 상품의 가격을 주기적으로 체크하고 변동 시 이메일 알림을 전송합니다.
"""

import time
import threading
from datetime import datetime, timedelta
import logging
from database import get_db_connection
from email_service import email_service
# from crawler import SSGCrawler  # SSGCrawler 클래스가 없으므로 주석 처리

class PriceMonitor:
    def __init__(self):
        self.is_running = False
        self.monitor_thread = None
        self.check_interval = 3600  # 1시간마다 체크
        self.price_change_threshold = 0.05  # 5% 이상 변동 시 알림
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 크롤러 초기화 (임시로 None으로 설정)
        self.crawler = None
    
    def start_monitoring(self):
        """가격 모니터링 시작"""
        if self.is_running:
            self.logger.info("가격 모니터링이 이미 실행 중입니다.")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("가격 모니터링을 시작했습니다.")
    
    def stop_monitoring(self):
        """가격 모니터링 중지"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("가격 모니터링을 중지했습니다.")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                self._check_all_tracked_products()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 후 재시도
    
    def _check_all_tracked_products(self):
        """모든 추적 상품의 가격을 체크"""
        try:
            conn = get_db_connection()
            
            # 활성화된 알림이 있는 상품들을 조회
            cursor = conn.execute('''
                SELECT 
                    p.id, p.name, p.url, p.current_price, p.source,
                    a.user_email, a.target_price, a.is_active
                FROM products p
                JOIN alerts a ON p.id = a.product_id
                WHERE a.is_active = 1
            ''')
            
            tracked_products = cursor.fetchall()
            conn.close()
            
            self.logger.info(f"추적 상품 {len(tracked_products)}개 가격 체크 시작")
            
            for product in tracked_products:
                try:
                    self._check_single_product(product)
                    time.sleep(2)  # 크롤링 간격 조절
                except Exception as e:
                    self.logger.error(f"상품 {product['name']} 체크 실패: {e}")
                    continue
            
            self.logger.info("모든 추적 상품 가격 체크 완료")
            
        except Exception as e:
            self.logger.error(f"가격 체크 오류: {e}")
    
    def _check_single_product(self, product):
        """단일 상품 가격 체크"""
        try:
            # 현재 가격 크롤링
            current_price = self._crawl_current_price(product['url'], product['source'])
            
            if current_price is None:
                self.logger.warning(f"상품 {product['name']} 가격 크롤링 실패")
                return
            
            old_price = product['current_price']
            
            # 가격 변동 확인
            if current_price != old_price:
                self.logger.info(f"가격 변동 감지: {product['name']} - {old_price:,}원 → {current_price:,}원")
                
                # 데이터베이스 업데이트
                self._update_product_price(product['id'], current_price)
                
                # 가격 변동 알림 전송
                self._send_price_alert(product, old_price, current_price)
                
                # 목표가 도달 확인
                if current_price <= product['target_price']:
                    self._send_target_price_alert(product, current_price)
            
        except Exception as e:
            self.logger.error(f"상품 {product['name']} 체크 중 오류: {e}")
    
    def _crawl_current_price(self, url, source):
        """현재 가격 크롤링"""
        try:
            if source.upper() == 'SSG':
                return self.crawler.get_product_price(url)
            else:
                # 다른 소스는 기본 크롤러 사용
                return self.crawler.get_product_price(url)
        except Exception as e:
            self.logger.error(f"가격 크롤링 실패: {e}")
            return None
    
    def _update_product_price(self, product_id, new_price):
        """상품 가격 업데이트"""
        try:
            conn = get_db_connection()
            
            # products 테이블 업데이트
            conn.execute('''
                UPDATE products 
                SET current_price = ?, updated_at = datetime('now', '+09:00')
                WHERE id = ?
            ''', (new_price, product_id))
            
            # price_logs 테이블에 로그 추가
            conn.execute('''
                INSERT INTO price_logs (product_id, price, logged_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, new_price))
            
            # price_history 테이블에 기록 추가
            conn.execute('''
                INSERT INTO price_history (product_id, price, recorded_at)
                VALUES (?, ?, datetime('now', '+09:00'))
            ''', (product_id, new_price))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"상품 {product_id} 가격 업데이트 완료: {new_price:,}원")
            
        except Exception as e:
            self.logger.error(f"가격 업데이트 실패: {e}")
    
    def _send_price_alert(self, product, old_price, new_price):
        """가격 변동 알림 전송"""
        try:
            change_percentage = ((new_price - old_price) / old_price) * 100
            
            # 변동률이 임계값을 넘을 때만 알림
            if abs(change_percentage) >= (self.price_change_threshold * 100):
                email_service.send_price_alert_email(
                    user_email=product['user_email'],
                    product_name=product['name'],
                    old_price=old_price,
                    new_price=new_price,
                    product_url=product['url'],
                    change_percentage=change_percentage
                )
                self.logger.info(f"가격 변동 알림 전송: {product['name']}")
            
        except Exception as e:
            self.logger.error(f"가격 알림 전송 실패: {e}")
    
    def _send_target_price_alert(self, product, current_price):
        """목표가 도달 알림 전송"""
        try:
            subject = f"🎯 목표가 도달: {product['name']}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
                             color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .target-reached {{ background: #4caf50; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; }}
                    .price-info {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .price-item {{ text-align: center; }}
                    .price-number {{ font-size: 24px; font-weight: bold; }}
                    .current-price {{ color: #4caf50; }}
                    .target-price {{ color: #666; }}
                    .product-link {{ background: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 목표가 도달!</h1>
                        <p>설정하신 목표가에 도달했습니다!</p>
                    </div>
                    
                    <div class="content">
                        <h2>{product['name']}</h2>
                        
                        <div class="target-reached">
                            <h3>🎉 목표가 달성!</h3>
                            <p>원하시던 가격에 도달했습니다!</p>
                        </div>
                        
                        <div class="price-info">
                            <div class="price-item">
                                <div class="price-number current-price">{current_price:,}원</div>
                                <div>현재 가격</div>
                            </div>
                            <div class="price-item">
                                <div class="price-number target-price">{product['target_price']:,}원</div>
                                <div>목표 가격</div>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{product['url']}" class="product-link" target="_blank">
                                🔗 상품 구매하기
                            </a>
                        </div>
                        
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3>💡 구매 추천</h3>
                            <p>목표가에 도달했으니 구매 타이밍입니다!</p>
                            <p>다른 상품과 비교해보시고 구매를 결정하세요.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email_service.send_email(
                to_email=product['user_email'],
                subject=subject,
                html_content=html_content
            )
            
            self.logger.info(f"목표가 도달 알림 전송: {product['name']}")
            
        except Exception as e:
            self.logger.error(f"목표가 알림 전송 실패: {e}")
    
    def manual_price_check(self):
        """수동 가격 체크"""
        try:
            self.logger.info("수동 가격 체크 시작")
            self._check_all_tracked_products()
            self.logger.info("수동 가격 체크 완료")
            return True
        except Exception as e:
            self.logger.error(f"수동 가격 체크 실패: {e}")
            return False

# 전역 가격 모니터 인스턴스
price_monitor = PriceMonitor() 