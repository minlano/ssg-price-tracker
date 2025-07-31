#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def recreate_databases():
    """데이터베이스와 테이블을 다시 생성"""
    print("🔄 데이터베이스 재생성 시작")
    
    # 1. database 폴더의 데이터베이스들 생성
    database_files = [
        'database/ssg_tracker.db',
        'database/naver_shopping_tracker.db'
    ]
    
    # 2. 루트 폴더의 ssg_products.db도 생성 (기존 파일이 있으면 데이터만 삭제)
    root_db = 'ssg_products.db'
    
    # SQL 스크립트 읽기
    with open('database/init.sql', 'r', encoding='utf-8') as f:
        init_sql = f.read()
    
    # 각 데이터베이스 생성/초기화
    all_dbs = database_files + [root_db]
    
    for db_path in all_dbs:
        try:
            print(f"📁 {db_path} 처리 중...")
            
            # 데이터베이스 연결
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 기존 데이터 삭제 (테이블은 유지)
            try:
                cursor.execute("DELETE FROM alerts")
                cursor.execute("DELETE FROM price_logs") 
                cursor.execute("DELETE FROM products")
                print(f"   ✅ 기존 데이터 삭제 완료")
            except sqlite3.OperationalError:
                print(f"   ⚠️ 기존 테이블 없음 (새로 생성)")
            
            # 테이블 생성 및 초기 데이터 삽입
            cursor.executescript(init_sql)
            conn.commit()
            
            # 테이블 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   ✅ 테이블 생성 완료: {[table[0] for table in tables]}")
            
            # 데이터 개수 확인
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            print(f"   📊 상품 데이터: {product_count}개")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ {db_path} 처리 실패: {e}")
    
    print("🎉 데이터베이스 재생성 완료!")

def test_database():
    """데이터베이스 연결 테스트"""
    print("\n🔍 데이터베이스 연결 테스트")
    
    test_dbs = ['ssg_products.db', 'database/ssg_tracker.db']
    
    for db_path in test_dbs:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 테이블 목록 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"✅ {db_path}: {len(tables)}개 테이블")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count}개 레코드")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ {db_path} 테스트 실패: {e}")

if __name__ == "__main__":
    recreate_databases()
    test_database()