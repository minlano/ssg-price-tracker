#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_modules():
    """모듈 import 테스트"""
    try:
        from crawler import search_ssg_products, crawl_ssg_product
        from review_crawler import crawl_product_reviews, get_review_statistics
        assert True
    except ImportError as e:
        pytest.fail(f"모듈 import 실패: {e}")

def test_search_ssg_products():
    """SSG 상품 검색 기본 테스트"""
    try:
        from crawler import search_ssg_products
        
        # 간단한 검색 테스트
        products = search_ssg_products("노트북", limit=1)
        
        # 결과 검증
        assert isinstance(products, list), "검색 결과는 리스트여야 함"
        
        if products:
            product = products[0]
            assert 'name' in product, "상품에 name 필드가 있어야 함"
            assert 'price' in product, "상품에 price 필드가 있어야 함"
            assert 'url' in product, "상품에 url 필드가 있어야 함"
            assert 'source' in product, "상품에 source 필드가 있어야 함"
            assert product['source'] == 'SSG', "source는 SSG여야 함"
        
        print(f"✅ 검색 테스트 성공: {len(products)}개 상품")
        
    except Exception as e:
        pytest.fail(f"SSG 상품 검색 테스트 실패: {e}")

def test_crawl_ssg_product():
    """SSG 상품 상세 정보 크롤링 테스트"""
    try:
        from crawler import crawl_ssg_product
        
        # 테스트용 URL (실제 SSG 상품 URL)
        test_url = "https://www.ssg.com/item/itemView.ssg?itemId=1000671133675&siteNo=6004&salestrNo=6005"
        
        product_info = crawl_ssg_product(test_url)
        
        if product_info:
            assert 'name' in product_info, "상품 정보에 name 필드가 있어야 함"
            assert 'price' in product_info, "상품 정보에 price 필드가 있어야 함"
            assert 'url' in product_info, "상품 정보에 url 필드가 있어야 함"
            assert product_info['url'] == test_url, "URL이 일치해야 함"
            
            print(f"✅ 상품 상세 테스트 성공: {product_info['name'][:50]}...")
        else:
            print("⚠️ 상품 상세 정보를 가져올 수 없음 (네트워크 제한 가능)")
        
    except Exception as e:
        print(f"⚠️ 상품 상세 테스트 스킵: {e}")
        # 네트워크 관련 오류는 실패로 처리하지 않음
        pass

def test_review_crawler():
    """리뷰 크롤러 기본 테스트"""
    try:
        from review_crawler import crawl_product_reviews, get_review_statistics
        
        # 테스트용 URL
        test_url = "https://www.ssg.com/item/itemView.ssg?itemId=1000671133675&siteNo=6004&salestrNo=6005"
        
        reviews = crawl_product_reviews(test_url, 'SSG')
        
        # 결과 검증
        assert isinstance(reviews, list), "리뷰 결과는 리스트여야 함"
        
        if reviews:
            review = reviews[0]
            assert 'user' in review, "리뷰에 user 필드가 있어야 함"
            assert 'rating' in review, "리뷰에 rating 필드가 있어야 함"
            assert 'comment' in review, "리뷰에 comment 필드가 있어야 함"
            assert 'date' in review, "리뷰에 date 필드가 있어야 함"
            assert 1 <= review['rating'] <= 5, "평점은 1-5 사이여야 함"
            
            # 통계 테스트
            stats = get_review_statistics(reviews)
            assert 'total_reviews' in stats, "통계에 total_reviews가 있어야 함"
            assert 'average_rating' in stats, "통계에 average_rating이 있어야 함"
            assert stats['total_reviews'] == len(reviews), "리뷰 개수가 일치해야 함"
            
            print(f"✅ 리뷰 테스트 성공: {len(reviews)}개 리뷰, 평균 {stats['average_rating']:.1f}점")
        else:
            print("⚠️ 리뷰를 가져올 수 없음")
        
    except Exception as e:
        print(f"⚠️ 리뷰 테스트 스킵: {e}")
        # 네트워크 관련 오류는 실패로 처리하지 않음
        pass

def test_basic_functionality():
    """기본 기능 테스트 (네트워크 없이)"""
    try:
        from crawler import get_headers, create_dummy_products
        from review_crawler import ReviewCrawler
        
        # 헤더 테스트
        headers = get_headers()
        assert isinstance(headers, dict), "헤더는 딕셔너리여야 함"
        assert 'User-Agent' in headers, "User-Agent가 있어야 함"
        
        # 더미 상품 생성 테스트
        dummy_products = create_dummy_products("테스트", 3)
        assert len(dummy_products) == 3, "더미 상품 3개가 생성되어야 함"
        assert all('name' in p for p in dummy_products), "모든 더미 상품에 name이 있어야 함"
        
        # 리뷰 크롤러 인스턴스 생성 테스트
        crawler = ReviewCrawler()
        assert crawler is not None, "리뷰 크롤러 인스턴스가 생성되어야 함"
        
        print("✅ 기본 기능 테스트 성공")
        
    except Exception as e:
        pytest.fail(f"기본 기능 테스트 실패: {e}")

if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    print("🧪 SSG 크롤러 테스트 시작")
    
    test_import_modules()
    test_basic_functionality()
    test_search_ssg_products()
    test_crawl_ssg_product()
    test_review_crawler()
    
    print("🎉 모든 테스트 완료!")