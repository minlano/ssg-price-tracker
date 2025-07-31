#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Product(Base):
    """상품 정보 모델"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    price = Column(Float, nullable=True)
    url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    brand = Column(String(100), nullable=True)
    source = Column(String(50), nullable=False, default='SSG')
    keyword = Column(String(100), nullable=False)  # 검색 키워드
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 인덱스 생성 (검색 성능 향상)
    __table_args__ = (
        Index('idx_keyword', 'keyword'),
        Index('idx_brand', 'brand'),
        Index('idx_price', 'price'),
        Index('idx_created_at', 'created_at'),
        Index('idx_keyword_brand', 'keyword', 'brand'),
    )

# === 가격 추적 기능을 위한 테이블 추가 시작 ===
class WatchList(Base):
    """상품 추적 목록 모델"""
    __tablename__ = 'watch_list'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(500), nullable=False)
    product_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    source = Column(String(50), nullable=False)  # SSG, NAVER, 11ST
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)  # 목표 가격 (이 가격 이하로 떨어지면 알림)
    user_email = Column(String(200), nullable=False)
    is_active = Column(Integer, default=1)  # 1: 활성, 0: 비활성
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_email', 'user_email'),
        Index('idx_source', 'source'),
        Index('idx_is_active', 'is_active'),
        Index('idx_created_at_watch', 'created_at'),
    )

class PriceHistory(Base):
    """가격 변동 히스토리 모델"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    watch_id = Column(Integer, nullable=False)  # WatchList의 id 참조
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_watch_id', 'watch_id'),
        Index('idx_recorded_at', 'recorded_at'),
        Index('idx_watch_recorded', 'watch_id', 'recorded_at'),
    )

class PriceAlert(Base):
    """가격 알림 로그 모델"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    watch_id = Column(Integer, nullable=False)  # WatchList의 id 참조
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'lowest_price', 'target_price'
    email_sent = Column(Integer, default=0)  # 0: 미발송, 1: 발송완료
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_watch_id_alert', 'watch_id'),
        Index('idx_alert_type', 'alert_type'),
        Index('idx_email_sent', 'email_sent'),
        Index('idx_created_at_alert', 'created_at'),
    )
# === 가격 추적 기능을 위한 테이블 추가 끝 ===

class SearchCache(Base):
    """검색 캐시 모델"""
    __tablename__ = 'search_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False)
    cache_key = Column(String(200), nullable=False, unique=True)
    result_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_cache_key', 'cache_key'),
        Index('idx_keyword_cache', 'keyword'),
        Index('idx_expires_at', 'expires_at'),
    )

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./ssg_products.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """테이블 생성"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """데이터베이스 초기화"""
    create_tables()
    print("✅ 데이터베이스 테이블이 생성되었습니다.")

if __name__ == "__main__":
    init_database()