#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from crawler import crawl_ssg_product
from review_crawler import crawl_product_reviews, get_review_statistics

def test_specific_ssg_product():
    """제공된 실제 SSG 상품으로 테스트"""
    print("=" * 60)
    print("🔍 실제 SSG 상품 테스트")
    print("=" * 60)
    
    # 제공된 실제 노트북 상품 URL
    test_url = "https://www.ssg.com/item/itemView.ssg?itemId=1000671133675&siteNo=6004&salestrNo=6005"
    
    print(f"📱 테스트 상품: {test_url}")
    print(f"📝 예상 상품명: 베이직스 베이직북16 윈도우11 사무용 가성비 노트북")
    
    # 1. 상품 상세 정보 테스트
    print("\n" + "-" * 40)
    print("📦 상품 상세 정보 추출")
    print("-" * 40)
    
    try:
        product_info = crawl_ssg_product(test_url)
        
        if product_info:
            print("✅ 상품 상세 정보 추출 성공!")
            print(f"   상품명: {product_info['name']}")
            print(f"   가격: {product_info['price']:,}원" if product_info['price'] > 0 else "   가격: 정보 없음")
            print(f"   URL: {product_info['url']}")
            print(f"   이미지: {'있음' if product_info['image_url'] else '없음'}")
        else:
            print("❌ 상품 상세 정보 추출 실패")
            
    except Exception as e:
        print(f"❌ 상품 상세 정보 오류: {e}")
    
    # 2. 리뷰 크롤링 테스트
    print("\n" + "-" * 40)
    print("⭐ 리뷰 크롤링 테스트")
    print("-" * 40)
    
    try:
        reviews = crawl_product_reviews(test_url, 'SSG')
        
        if reviews:
            print(f"✅ {len(reviews)}개 리뷰 추출!")
            
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

def test_search_with_specific_keyword():
    """실제 상품명으로 검색 테스트"""
    print("\n" + "=" * 60)
    print("🔎 실제 상품명으로 검색 테스트")
    print("=" * 60)
    
    from crawler import search_ssg_products
    
    keywords = ["베이직북16", "베이직스 노트북", "윈도우11 노트북"]
    
    for keyword in keywords:
        print(f"\n🔍 '{keyword}' 검색 중...")
        print("-" * 30)
        
        try:
            products = search_ssg_products(keyword, limit=2)
            
            if products:
                print(f"✅ {len(products)}개 상품 발견!")
                
                for i, product in enumerate(products, 1):
                    print(f"\n{i}. 상품명: {product['name'][:80]}...")
                    print(f"   가격: {product['price']:,}원" if product['price'] > 0 else "   가격: 정보 없음")
                    print(f"   브랜드: {product['brand']}")
                    print(f"   URL: {product['url'][:80]}...")
            else:
                print("❌ 검색 결과가 없습니다.")
                
        except Exception as e:
            print(f"❌ 검색 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 실제 SSG 상품 테스트 시작")
    
    # 1. 특정 상품 테스트
    test_specific_ssg_product()
    
    # 2. 검색 테스트
    test_search_with_specific_keyword()
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()