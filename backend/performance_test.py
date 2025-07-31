#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
성능 테스트 스크립트
- 동기 vs 비동기 크롤러 성능 비교
- 캐시 성능 테스트
- 데이터베이스 성능 테스트
"""

import time
import asyncio
from typing import List, Dict
from crawler import search_ssg_products_legacy, search_ssg_products
from cache_manager import cache_manager

async def performance_comparison():
    """동기 vs 비동기 성능 비교"""
    print("🏁 성능 비교 테스트 시작")
    print("=" * 80)
    
    test_keywords = ["아이폰", "나이키", "라면", "노트북"]
    limit = 5
    
    # 캐시 초기화
    cache_manager.clear_cache()
    
    total_sync_time = 0
    total_async_time = 0
    
    for keyword in test_keywords:
        print(f"\n🔍 테스트 키워드: '{keyword}'")
        print("-" * 50)
        
        # 1. 동기 크롤러 테스트
        print("🐌 동기 크롤러 테스트...")
        start_time = time.time()
        
        try:
            sync_results = search_ssg_products_legacy(keyword, limit=limit)
            sync_time = time.time() - start_time
            total_sync_time += sync_time
            
            print(f"   ✅ 완료: {sync_time:.2f}초, {len(sync_results)}개 상품")
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            sync_time = 0
        
        # 잠시 대기 (서버 부하 방지)
        await asyncio.sleep(1)
        
        # 2. 비동기 크롤러 테스트 (캐시 초기화 후)
        cache_manager.clear_cache(f"search:*{keyword}*")
        
        print("🚀 비동기 크롤러 테스트...")
        start_time = time.time()
        
        try:
            async_results = search_ssg_products(keyword, limit=limit)
            async_time = time.time() - start_time
            total_async_time += async_time
            
            print(f"   ✅ 완료: {async_time:.2f}초, {len(async_results)}개 상품")
            
            # 성능 개선 비율 계산
            if sync_time > 0:
                improvement = ((sync_time - async_time) / sync_time) * 100
                print(f"   📈 성능 개선: {improvement:.1f}%")
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            async_time = 0
        
        # 3. 캐시 테스트 (두 번째 요청)
        print("💾 캐시 테스트...")
        start_time = time.time()
        
        try:
            cached_results = search_ssg_products(keyword, limit=limit)
            cache_time = time.time() - start_time
            
            print(f"   ✅ 캐시 조회: {cache_time:.2f}초, {len(cached_results)}개 상품")
            
            if async_time > 0:
                cache_improvement = ((async_time - cache_time) / async_time) * 100
                print(f"   ⚡ 캐시 개선: {cache_improvement:.1f}%")
                
        except Exception as e:
            print(f"   ❌ 캐시 오류: {e}")
    
    # 전체 결과 요약
    print("\n" + "=" * 80)
    print("📊 전체 성능 테스트 결과")
    print("-" * 80)
    print(f"🐌 동기 크롤러 총 시간: {total_sync_time:.2f}초")
    print(f"🚀 비동기 크롤러 총 시간: {total_async_time:.2f}초")
    
    if total_sync_time > 0 and total_async_time > 0:
        overall_improvement = ((total_sync_time - total_async_time) / total_sync_time) * 100
        speed_ratio = total_sync_time / total_async_time
        print(f"📈 전체 성능 개선: {overall_improvement:.1f}%")
        print(f"⚡ 속도 비율: {speed_ratio:.1f}x 빠름")
    
    # 캐시 통계
    cache_stats = cache_manager.get_cache_stats()
    print(f"\n💾 캐시 통계: {cache_stats}")

async def stress_test():
    """스트레스 테스트"""
    print("\n🔥 스트레스 테스트 시작")
    print("=" * 80)
    
    keywords = ["아이폰", "삼성", "나이키", "아디다스", "라면"]
    concurrent_requests = 5
    
    print(f"동시 요청 수: {concurrent_requests}")
    print(f"테스트 키워드: {keywords}")
    
    start_time = time.time()
    
    # 동시 요청 실행
    tasks = []
    for keyword in keywords:
        task = asyncio.create_task(test_single_search(keyword))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # 결과 분석
    successful_requests = 0
    total_products = 0
    
    for i, result in enumerate(results):
        if isinstance(result, list):
            successful_requests += 1
            total_products += len(result)
            print(f"✅ {keywords[i]}: {len(result)}개 상품")
        else:
            print(f"❌ {keywords[i]}: {result}")
    
    print(f"\n📊 스트레스 테스트 결과:")
    print(f"   - 총 소요 시간: {total_time:.2f}초")
    print(f"   - 성공한 요청: {successful_requests}/{len(keywords)}")
    print(f"   - 총 상품 수: {total_products}개")
    print(f"   - 평균 처리 시간: {total_time/len(keywords):.2f}초/요청")
    print(f"   - 처리량: {total_products/total_time:.1f}개 상품/초")

async def test_single_search(keyword: str) -> List[Dict]:
    """단일 검색 테스트"""
    try:
        return search_ssg_products(keyword, limit=3)
    except Exception as e:
        return f"오류: {e}"

def memory_usage_test():
    """메모리 사용량 테스트"""
    print("\n🧠 메모리 사용량 테스트")
    print("=" * 80)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 초기 메모리 사용량
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"초기 메모리 사용량: {initial_memory:.1f} MB")
        
        # 여러 검색 수행
        keywords = ["아이폰", "삼성", "나이키", "라면", "노트북"] * 3
        
        for i, keyword in enumerate(keywords):
            search_ssg_products(keyword, limit=5)
            
            if (i + 1) % 5 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"{i+1}회 검색 후 메모리: {current_memory:.1f} MB (+{current_memory-initial_memory:.1f} MB)")
        
        # 최종 메모리 사용량
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"\n최종 메모리 사용량: {final_memory:.1f} MB")
        print(f"메모리 증가량: {memory_increase:.1f} MB")
        
        if memory_increase < 50:  # 50MB 이하
            print("✅ 메모리 사용량 양호")
        else:
            print("⚠️ 메모리 사용량 높음")
            
    except ImportError:
        print("⚠️ psutil 라이브러리가 필요합니다: pip install psutil")
    except Exception as e:
        print(f"❌ 메모리 테스트 오류: {e}")

async def main():
    """메인 테스트 함수"""
    print("🚀 SSG 크롤러 성능 테스트 시작")
    print("현재 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 1. 성능 비교 테스트
    await performance_comparison()
    
    # 2. 스트레스 테스트
    await stress_test()
    
    # 3. 메모리 사용량 테스트
    memory_usage_test()
    
    print("\n🎉 모든 성능 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())