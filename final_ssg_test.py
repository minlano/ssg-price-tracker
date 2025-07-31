#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from crawler import search_ssg_products, crawl_ssg_product
from review_crawler import crawl_product_reviews, get_review_statistics

def test_complete_ssg_system():
    """완전한 SSG 시스템 테스트"""
    print("🚀 완전한 SSG 크롤링 시스템 테스트")
    print("=" * 80)
    
    # 1. 상품 검색 테스트
    print("\n📦 1단계: 상품 검색")
    print("-" * 50)
    
    keyword = "노트북"
    print(f"🔍 검색 키워드: '{keyword}'")
    
    try:
        products = search_ssg_products(keyword, limit=3)
        
        if products:
            print(f"✅ {len(products)}개 상품 검색 성공!")
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. 상품명: {product['name'][:60]}...")
                print(f"   가격: {product['price']:,}원" if product['price'] > 0 else "   가격: 정보 없음")
                print(f"   브랜드: {product['brand']}")
                print(f"   URL: {product['url'][:70]}...")
                print(f"   이미지: {'✅' if product['image_url'] else '❌'}")
            
            # 첫 번째 상품으로 상세 테스트 진행
            test_product = products[0]
            
        else:
            print("❌ 상품 검색 실패")
            return
            
    except Exception as e:
        print(f"❌ 상품 검색 오류: {e}")
        return
    
    # 2. 상품 상세 정보 테스트
    print(f"\n📋 2단계: 상품 상세 정보")
    print("-" * 50)
    
    try:
        product_detail = crawl_ssg_product(test_product['url'])
        
        if product_detail:
            print("✅ 상품 상세 정보 추출 성공!")
            print(f"   상품명: {product_detail['name'][:80]}...")
            print(f"   가격: {product_detail['price']:,}원" if product_detail['price'] > 0 else "   가격: 정보 없음")
            print(f"   이미지: {'✅' if product_detail['image_url'] else '❌'}")
        else:
            print("❌ 상품 상세 정보 추출 실패")
            
    except Exception as e:
        print(f"❌ 상품 상세 정보 오류: {e}")
    
    # 3. 리뷰 크롤링 테스트 (핵심!)
    print(f"\n⭐ 3단계: 리뷰 크롤링 (핵심 기능)")
    print("-" * 50)
    
    try:
        reviews = crawl_product_reviews(test_product['url'], 'SSG')
        
        if reviews:
            print(f"🎉 {len(reviews)}개 리뷰 크롤링 성공!")
            
            # 리뷰 통계
            stats = get_review_statistics(reviews)
            print(f"\n📊 리뷰 통계:")
            print(f"   총 리뷰 수: {stats['total_reviews']}개")
            print(f"   평균 평점: {stats['average_rating']}/5.0")
            
            # 실제 리뷰 내용 확인
            print(f"\n📝 실제 리뷰 내용:")
            for i, review in enumerate(reviews[:3], 1):
                print(f"\n{i}. 사용자: {review['user']}")
                print(f"   평점: {'⭐' * review['rating']} ({review['rating']}/5)")
                print(f"   날짜: {review['date']}")
                print(f"   내용: {review['comment'][:120]}...")
                print(f"   도움됨: {review['helpful']}명")
                
                # 실제 리뷰인지 확인
                if len(review['comment']) > 50 and '구매자' not in review['comment']:
                    print(f"   ✅ 실제 사용자 리뷰!")
                else:
                    print(f"   ⚠️ 생성된 리뷰")
        else:
            print("❌ 리뷰 크롤링 실패")
            
    except Exception as e:
        print(f"❌ 리뷰 크롤링 오류: {e}")
    
    # 4. 종합 평가
    print(f"\n🏆 4단계: 종합 평가")
    print("-" * 50)
    
    success_count = 0
    total_tests = 3
    
    if products:
        success_count += 1
        print("✅ 상품 검색: 성공")
    else:
        print("❌ 상품 검색: 실패")
    
    if 'product_detail' in locals() and product_detail:
        success_count += 1
        print("✅ 상품 상세: 성공")
    else:
        print("❌ 상품 상세: 실패")
    
    if reviews:
        success_count += 1
        print("✅ 리뷰 크롤링: 성공")
    else:
        print("❌ 리뷰 크롤링: 실패")
    
    success_rate = (success_count / total_tests) * 100
    print(f"\n🎯 전체 성공률: {success_rate:.1f}% ({success_count}/{total_tests})")
    
    if success_rate >= 100:
        print("🎉 완벽한 SSG 크롤링 시스템!")
    elif success_rate >= 66:
        print("👍 우수한 SSG 크롤링 시스템!")
    elif success_rate >= 33:
        print("⚠️ 개선이 필요한 시스템")
    else:
        print("❌ 시스템 점검 필요")

def test_multiple_products():
    """여러 상품 테스트"""
    print("\n" + "=" * 80)
    print("🔄 다양한 상품 테스트")
    print("=" * 80)
    
    test_keywords = ["아이폰", "삼성 갤럭시", "베이직북"]
    
    for keyword in test_keywords:
        print(f"\n🔍 '{keyword}' 테스트")
        print("-" * 30)
        
        try:
            products = search_ssg_products(keyword, limit=1)
            
            if products:
                product = products[0]
                print(f"✅ 상품: {product['name'][:50]}...")
                print(f"   가격: {product['price']:,}원")
                
                # 간단한 리뷰 테스트
                reviews = crawl_product_reviews(product['url'], 'SSG')
                if reviews:
                    print(f"   리뷰: {len(reviews)}개 (평균 {sum(r['rating'] for r in reviews)/len(reviews):.1f}점)")
                else:
                    print(f"   리뷰: 추출 실패")
            else:
                print(f"❌ '{keyword}' 검색 실패")
                
        except Exception as e:
            print(f"❌ '{keyword}' 테스트 오류: {e}")

def main():
    """메인 테스트 함수"""
    # 1. 완전한 시스템 테스트
    test_complete_ssg_system()
    
    # 2. 다양한 상품 테스트
    test_multiple_products()
    
    print("\n" + "=" * 80)
    print("🎊 SSG 크롤링 시스템 테스트 완료!")
    print("=" * 80)

if __name__ == "__main__":
    main()