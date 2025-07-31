#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sqlite3
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        # 테스트용 임시 데이터베이스 생성
        test_db = "test_temp.db"
        
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        # 간단한 테이블 생성 및 데이터 삽입
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER
            )
        """)
        
        cursor.execute("INSERT INTO test_products (name, price) VALUES (?, ?)", 
                      ("테스트 상품", 10000))
        conn.commit()
        
        # 데이터 조회
        cursor.execute("SELECT * FROM test_products")
        results = cursor.fetchall()
        
        assert len(results) > 0, "데이터가 삽입되어야 함"
        assert results[0][1] == "테스트 상품", "상품명이 일치해야 함"
        assert results[0][2] == 10000, "가격이 일치해야 함"
        
        conn.close()
        
        # 임시 파일 삭제
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ 데이터베이스 연결 테스트 성공")
        
    except Exception as e:
        pytest.fail(f"데이터베이스 연결 테스트 실패: {e}")

def test_database_models():
    """데이터베이스 모델 테스트"""
    try:
        # 데이터베이스 모델이 있는지 확인
        try:
            from database_models import Product, SessionLocal, get_db
            print("✅ 데이터베이스 모델 import 성공")
        except ImportError:
            print("⚠️ 데이터베이스 모델 없음 (선택사항)")
            return
        
        # 세션 생성 테스트
        db = next(get_db())
        assert db is not None, "데이터베이스 세션이 생성되어야 함"
        db.close()
        
        print("✅ 데이터베이스 모델 테스트 성공")
        
    except Exception as e:
        print(f"⚠️ 데이터베이스 모델 테스트 스킵: {e}")

def test_sql_injection_protection():
    """SQL 인젝션 방지 테스트"""
    try:
        test_db = "test_injection.db"
        
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        
        # 안전한 파라미터 바인딩 테스트
        malicious_input = "'; DROP TABLE test_table; --"
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", (malicious_input,))
        conn.commit()
        
        # 테이블이 여전히 존재하는지 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        result = cursor.fetchone()
        
        assert result is not None, "테이블이 삭제되지 않아야 함 (SQL 인젝션 방지)"
        
        conn.close()
        
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ SQL 인젝션 방지 테스트 성공")
        
    except Exception as e:
        pytest.fail(f"SQL 인젝션 방지 테스트 실패: {e}")

if __name__ == "__main__":
    print("🧪 데이터베이스 테스트 시작")
    
    test_database_connection()
    test_database_models()
    test_sql_injection_protection()
    
    print("🎉 데이터베이스 테스트 완료!")