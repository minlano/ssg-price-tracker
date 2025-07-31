#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
시스템 초기화 스크립트
- 데이터베이스 테이블 생성
- Redis 연결 테스트
- 비동기 크롤러 테스트
"""

import os
import sys
import asyncio
from database_models import init_database
from cache_manager import cache_manager

def test_redis_connection():
    """Redis 연결 테스트"""
    print("\n🔍 Redis 연결 테스트...")
    try:
        stats = cache_manager.get_cache_stats()
        print(f"✅ Redis 상태: {stats}")
        
        # 테스트 데이터 저장/조회
        test_data = [{'name': 'test', 'price': 1000}]
        cache_manager.cache_results('test_keyword', test_data, 5, 60)
        
        cached = cache_manager.get_cached_results('test_keyword', 5)
        if cached:
            print("✅ 캐시 저장/조회 테스트 성공")
        else:
            print("⚠️ 캐시 조회 실패")
            
        # 테스트 데이터 삭제
        cache_manager.clear_cache('search:*')
        
    except Exception as e:
        print(f"❌ Redis 테스트 실패: {e}")

def test_database():
    """데이터베이스 테스트"""
    print("\n🔍 데이터베이스 테스트...")
    try:
        from database_models import SessionLocal, Product
        from datetime import datetime
        
        db = SessionLocal()
        
        # 테스트 상품 추가
        test_product = Product(
            name="테스트 상품",
            price=10000,
            url="https://test.com",
            brand="테스트 브랜드",
            keyword="테스트"
        )
        
        db.add(test_product)
        db.commit()
        
        # 조회 테스트
        products = db.query(Product).filter(Product.keyword == "테스트").all()
        if products:
            print(f"✅ 데이터베이스 저장/조회 테스트 성공 ({len(products)}개 상품)")
        else:
            print("⚠️ 데이터베이스 조회 실패")
        
        # 테스트 데이터 삭제
        db.query(Product).filter(Product.keyword == "테스트").delete()
        db.commit()
        db.close()
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")

async def test_async_crawler():
    """비동기 크롤러 테스트"""
    print("\n🔍 비동기 크롤러 테스트...")
    try:
        from async_crawler import search_products_async
        
        # 간단한 검색 테스트
        results = await search_products_async("테스트", limit=2)
        
        if results:
            print(f"✅ 비동기 크롤러 테스트 성공 ({len(results)}개 상품)")
            for i, product in enumerate(results, 1):
                print(f"   {i}. {product['name'][:30]}...")
        else:
            print("⚠️ 비동기 크롤러 결과 없음")
            
    except Exception as e:
        print(f"❌ 비동기 크롤러 테스트 실패: {e}")

def main():
    """메인 초기화 함수"""
    print("🚀 SSG 가격 추적기 시스템 초기화 시작")
    print("=" * 60)
    
    # 1. 데이터베이스 초기화
    print("\n📊 데이터베이스 초기화...")
    try:
        init_database()
        test_database()
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
    
    # 2. Redis 연결 테스트
    test_redis_connection()
    
    # 3. 비동기 크롤러 테스트
    print("\n🕷️ 비동기 크롤러 테스트...")
    try:
        asyncio.run(test_async_crawler())
    except Exception as e:
        print(f"❌ 비동기 크롤러 테스트 실패: {e}")
    
    # 4. 통합 테스트
    print("\n🔧 통합 테스트...")
    try:
        from crawler import search_ssg_products
        
        print("기본 검색 함수 테스트...")
        results = search_ssg_products("아이폰", limit=2)
        
        if results:
            print(f"✅ 통합 테스트 성공 ({len(results)}개 상품)")
            for i, product in enumerate(results, 1):
                print(f"   {i}. {product['name'][:40]}...")
                print(f"      가격: {product['price']:,}원" if product['price'] > 0 else "      가격: 정보 없음")
        else:
            print("⚠️ 통합 테스트 결과 없음")
            
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 시스템 초기화 완료!")
    print("\n📋 시스템 구성 요소:")
    print("   - 🗄️ SQLite 데이터베이스 (상품 정보 저장)")
    print("   - 🚀 Redis 캐시 (검색 결과 캐싱)")
    print("   - ⚡ 비동기 크롤러 (고속 병렬 처리)")
    print("   - 🔄 자동 폴백 시스템 (안정성 보장)")
    
    print("\n💡 사용법:")
    print("   from crawler import search_ssg_products")
    print("   results = search_ssg_products('검색어', limit=10)")

if __name__ == "__main__":
    main()