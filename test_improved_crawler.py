#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from crawler import search_ssg_products, crawl_ssg_product
from review_crawler import crawl_product_reviews, get_review_statistics

def test_ssg_search():
    """개선된 SSG 검색 테스트"""
    print("=" * 60)
    print("🔍 개선된 SSG 검색 테스트")
    print("=" * 60)
    
    keywords = ["아이폰", "삼성 갤럭시", "노트북"]
    
    for keyword in keywords:
        print(f"\n🔎 '{keyword}' 검색 중...")
        print("-" * 40)
        
        try:
            products = search_ssg_products(keyword, limit=3)
            
            if products:
                print(f"✅ {len(products)}개 상품 발견!")
                
                for i, product in enumerate(products, 1):
                    print(f"\n{i}. 상품명: {product['name']}")
                    print(f"   가격: {product['price']:,}원" if product['price'] > 0 else "   가격: 정보 없음")
                    print(f"   브랜드: {product['brand']}")
                    print(f"   URL: {product['url'][:80]}...")
                    print(f"   이미지: {'있음' if product['image_url'] else '없음'}")
            else:
                print("❌ 검색 결과가 없습니다.")
                
        except Exception as e:
            print(f"❌ 검색 오류: {e}")

def test_ssg_product_detail():
    """SSG 상품 상세 정보 테스트"""
    print("\n" + "=" * 60)
    print("📦 SSG 상품 상세 정보 테스트")
    print("=" * 60)
    
    # 먼저 검색으로 실제 상품 URL 가져오기
    print("🔎 테스트용 상품 검색 중...")
    products = search_ssg_products("아이폰", limit=1)
    
    if products and products[0]['url']:
        test_url = products[0]['url']
        print(f"📱 테스트 URL: {test_url}")
        
        try:
            product_info = crawl_ssg_product(test_url)
            
            if product_info:
                print("✅ 상품 상세 정보 추출 성공!")
                print(f"   상품명: {product_info['name']}")
                print(f"   가격: {product_info['price']:,}원" if product_info['price'] > 0 else "   가격: 정보 없음")
                print(f"   이미지: {'있음' if product_info['image_url'] else '없음'}")
            else:
                print("❌ 상품 상세 정보 추출 실패")
                
        except Exception as e:
            print(f"❌ 상품 상세 정보 오류: {e}")
    else:
        print("⚠️ 테스트할 상품 URL을 찾을 수 없습니다.")

def test_ssg_reviews():
    """SSG 리뷰 크롤링 테스트"""
    print("\n" + "=" * 60)
    print("⭐ SSG 리뷰 크롤링 테스트")
    print("=" * 60)
    
    # 먼저 검색으로 실제 상품 URL 가져오기
    print("🔎 테스트용 상품 검색 중...")
    products = search_ssg_products("삼성", limit=1)
    
    if products and products[0]['url']:
        test_url = products[0]['url']
        print(f"📱 테스트 URL: {test_url}")
        
        try:
            reviews = crawl_product_reviews(test_url, 'SSG')
            
            if reviews:
                print(f"✅ {len(reviews)}개 리뷰 추출 성공!")
                
                # 리뷰 통계
                stats = get_review_statistics(reviews)
                print(f"\n📊 리뷰 통계:")
                print(f"   총 리뷰 수: {stats['total_reviews']}개")
                print(f"   평균 평점: {stats['average_rating']}/5.0")
                
                # 개별 리뷰 출력
                print(f"\n📝 리뷰 목록:")
                for i, review in enumerate(reviews[:3], 1):
                    print(f"\n{i}. 사용자: {review['user']}")
                    print(f"   평점: {'⭐' * review['rating']} ({review['rating']}/5)")
                    print(f"   날짜: {review['date']}")
                    print(f"   내용: {review['comment'][:100]}...")
                    print(f"   도움됨: {review['helpful']}명")
            else:
                print("❌ 리뷰 추출 실패")
                
        except Exception as e:
            print(f"❌ 리뷰 크롤링 오류: {e}")
    else:
        print("⚠️ 테스트할 상품 URL을 찾을 수 없습니다.")

def main():
    """메인 테스트 함수"""
    print("🚀 개선된 SSG 크롤러 테스트 시작")
    
    # 1. 검색 테스트
    test_ssg_search()
    
    # 2. 상품 상세 정보 테스트
    test_ssg_product_detail()
    
    # 3. 리뷰 크롤링 테스트
    test_ssg_reviews()
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()