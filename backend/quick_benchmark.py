#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
빠른 성능 벤치마크 - 핵심 지표만 측정
"""

import time
import statistics
from crawler import search_ssg_products_legacy, search_ssg_products
from cache_manager import cache_manager
from concurrent.futures import ThreadPoolExecutor

def measure_time(func, *args, **kwargs):
    """실행 시간 측정 (3회 평균)"""
    times = []
    for _ in range(3):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        times.append(end - start)
        time.sleep(0.5)  # 간격
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'result_count': len(result) if result else 0
    }

def main():
    print("🔬 SSG 크롤러 성능 벤치마크 (핵심 지표)")
    print("=" * 60)
    
    keyword = "아이폰"
    limit = 5
    
    # 1. 동기 vs 비동기 크롤러
    print(f"\n1️⃣ 동기 vs 비동기 크롤러 비교 (키워드: {keyword})")
    print("-" * 40)
    
    cache_manager.clear_cache()
    sync_result = measure_time(search_ssg_products_legacy, keyword, limit=limit)
    print(f"🐌 동기 크롤러: {sync_result['avg_time']:.3f}초 (평균)")
    
    cache_manager.clear_cache()
    async_result = measure_time(search_ssg_products, keyword, limit=limit)
    print(f"🚀 비동기 크롤러: {async_result['avg_time']:.3f}초 (평균)")
    
    sync_improvement = ((sync_result['avg_time'] - async_result['avg_time']) / sync_result['avg_time']) * 100
    print(f"📈 비동기 개선: {sync_improvement:.1f}% ({sync_result['avg_time']/async_result['avg_time']:.1f}배)")
    
    # 2. 캐시 효과
    print(f"\n2️⃣ 캐시 시스템 효과 (키워드: {keyword})")
    print("-" * 40)
    
    cache_manager.clear_cache()
    first_search = measure_time(search_ssg_products, keyword, limit=limit)
    print(f"💾 첫 검색: {first_search['avg_time']:.3f}초")
    
    cached_search = measure_time(search_ssg_products, keyword, limit=limit)
    print(f"⚡ 캐시 검색: {cached_search['avg_time']:.3f}초")
    
    cache_improvement = ((first_search['avg_time'] - cached_search['avg_time']) / first_search['avg_time']) * 100
    cache_speedup = first_search['avg_time'] / cached_search['avg_time'] if cached_search['avg_time'] > 0 else float('inf')
    print(f"📈 캐시 개선: {cache_improvement:.1f}% ({cache_speedup:.0f}배)" if cache_speedup != float('inf') else f"📈 캐시 개선: {cache_improvement:.1f}% (무한대)")
    
    # 3. 병렬 처리 효과
    print(f"\n3️⃣ 병렬 처리 효과 (키워드: ['아이폰', '삼성', '나이키'])")
    print("-" * 40)
    
    keywords = ["아이폰", "삼성", "나이키"]
    
    # 순차 처리
    cache_manager.clear_cache()
    def sequential():
        results = []
        for kw in keywords:
            results.extend(search_ssg_products(kw, limit=3))
        return results
    
    seq_result = measure_time(sequential)
    print(f"🔄 순차 처리: {seq_result['avg_time']:.3f}초")
    
    # 병렬 처리
    cache_manager.clear_cache()
    def parallel():
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(search_ssg_products, kw, limit=3) for kw in keywords]
            for future in futures:
                results.extend(future.result())
        return results
    
    par_result = measure_time(parallel)
    print(f"⚡ 병렬 처리: {par_result['avg_time']:.3f}초")
    
    parallel_improvement = ((seq_result['avg_time'] - par_result['avg_time']) / seq_result['avg_time']) * 100
    print(f"📈 병렬 개선: {parallel_improvement:.1f}% ({seq_result['avg_time']/par_result['avg_time']:.1f}배)")
    
    # 4. 상품명 품질
    print(f"\n4️⃣ 상품명 품질 비교 (키워드: 라면)")
    print("-" * 40)
    
    cache_manager.clear_cache()
    legacy_products = search_ssg_products_legacy("라면", limit=5)
    legacy_generic = sum(1 for p in legacy_products if "라면 관련 상품" in p['name'])
    legacy_quality = ((len(legacy_products) - legacy_generic) / len(legacy_products)) * 100 if legacy_products else 0
    
    cache_manager.clear_cache()
    improved_products = search_ssg_products("라면", limit=5)
    improved_generic = sum(1 for p in improved_products if "라면 관련 상품" in p['name'])
    improved_quality = ((len(improved_products) - improved_generic) / len(improved_products)) * 100 if improved_products else 0
    
    print(f"🐌 기존 크롤러: {legacy_quality:.1f}% 정확도")
    print(f"🚀 개선된 크롤러: {improved_quality:.1f}% 정확도")
    print(f"📈 품질 개선: +{improved_quality - legacy_quality:.1f}%p")
    
    # 종합 결과
    print(f"\n" + "="*60)
    print("🏆 종합 성능 개선 결과")
    print("="*60)
    print(f"🥇 캐시 시스템: {cache_improvement:.0f}% 개선 (가장 효과적)")
    print(f"🥈 병렬 처리: {parallel_improvement:.0f}% 개선")
    print(f"🥉 상품명 품질: +{improved_quality - legacy_quality:.0f}%p 향상")
    print(f"🏅 비동기 처리: {sync_improvement:.0f}% 개선")
    
    print(f"\n💡 실제 사용자 경험:")
    print(f"   • 첫 검색: ~{async_result['avg_time']:.1f}초")
    print(f"   • 캐시된 검색: ~{cached_search['avg_time']:.3f}초")
    print(f"   • 상품명 정확도: {improved_quality:.0f}%")
    print(f"   • 다중 검색: {seq_result['avg_time']/par_result['avg_time']:.1f}배 빠름")

if __name__ == "__main__":
    main()