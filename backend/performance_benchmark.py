#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
크롤링 성능 벤치마크 테스트
- 각 기능별 사용 전후 정확한 수치 비교
- 실제 성능 개선 효과 측정
"""

import time
import statistics
from typing import List, Dict
from crawler import search_ssg_products_legacy, search_ssg_products
from cache_manager import cache_manager
from concurrent.futures import ThreadPoolExecutor
import threading

class PerformanceBenchmark:
    """성능 벤치마크 테스트"""
    
    def __init__(self):
        self.results = {}
        self.test_keywords = ["아이폰", "나이키", "라면", "노트북", "삼성"]
        
    def measure_execution_time(self, func, *args, **kwargs) -> Dict:
        """함수 실행 시간 정확히 측정"""
        times = []
        results = []
        
        # 5회 반복 측정하여 평균값 계산
        for i in range(5):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            times.append(execution_time)
            results.append(result)
            
            print(f"  테스트 {i+1}/5: {execution_time:.3f}초, {len(result)}개 상품")
            
            # 테스트 간 간격
            time.sleep(0.5)
        
        return {
            'times': times,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'results': results,
            'avg_products': statistics.mean([len(r) for r in results])
        }
    
    def test_sync_vs_async_crawler(self) -> Dict:
        """1. 동기 vs 비동기 크롤러 성능 비교"""
        print("\n" + "="*80)
        print("🔍 테스트 1: 동기 vs 비동기 크롤러 성능 비교")
        print("="*80)
        
        keyword = "아이폰"
        limit = 5
        
        # 캐시 초기화
        cache_manager.clear_cache()
        
        print(f"\n🐌 동기 크롤러 테스트 (키워드: {keyword}, 개수: {limit})")
        print("-" * 50)
        sync_results = self.measure_execution_time(
            search_ssg_products_legacy, keyword, limit=limit
        )
        
        # 캐시 초기화
        cache_manager.clear_cache()
        
        print(f"\n🚀 비동기 크롤러 테스트 (키워드: {keyword}, 개수: {limit})")
        print("-" * 50)
        async_results = self.measure_execution_time(
            search_ssg_products, keyword, limit=limit
        )
        
        # 성능 개선 계산
        improvement = ((sync_results['avg_time'] - async_results['avg_time']) / sync_results['avg_time']) * 100
        speed_ratio = sync_results['avg_time'] / async_results['avg_time']
        
        result = {
            'sync_avg_time': sync_results['avg_time'],
            'async_avg_time': async_results['avg_time'],
            'improvement_percent': improvement,
            'speed_ratio': speed_ratio,
            'sync_std_dev': sync_results['std_dev'],
            'async_std_dev': async_results['std_dev']
        }
        
        print(f"\n📊 결과:")
        print(f"   동기 크롤러 평균: {sync_results['avg_time']:.3f}초 (±{sync_results['std_dev']:.3f})")
        print(f"   비동기 크롤러 평균: {async_results['avg_time']:.3f}초 (±{async_results['std_dev']:.3f})")
        print(f"   성능 개선: {improvement:.1f}%")
        print(f"   속도 비율: {speed_ratio:.2f}x")
        
        return result
    
    def test_cache_performance(self) -> Dict:
        """2. 캐시 시스템 성능 테스트"""
        print("\n" + "="*80)
        print("💾 테스트 2: 캐시 시스템 성능 비교")
        print("="*80)
        
        keyword = "나이키"
        limit = 5
        
        # 캐시 초기화
        cache_manager.clear_cache()
        
        print(f"\n1️⃣ 첫 번째 검색 (캐시 없음) - 키워드: {keyword}")
        print("-" * 50)
        first_search = self.measure_execution_time(
            search_ssg_products, keyword, limit=limit
        )
        
        print(f"\n2️⃣ 두 번째 검색 (캐시 있음) - 키워드: {keyword}")
        print("-" * 50)
        cached_search = self.measure_execution_time(
            search_ssg_products, keyword, limit=limit
        )
        
        # 캐시 효율성 계산
        cache_improvement = ((first_search['avg_time'] - cached_search['avg_time']) / first_search['avg_time']) * 100
        cache_speed_ratio = first_search['avg_time'] / cached_search['avg_time'] if cached_search['avg_time'] > 0 else float('inf')
        
        result = {
            'first_search_time': first_search['avg_time'],
            'cached_search_time': cached_search['avg_time'],
            'cache_improvement_percent': cache_improvement,
            'cache_speed_ratio': cache_speed_ratio,
            'first_std_dev': first_search['std_dev'],
            'cached_std_dev': cached_search['std_dev']
        }
        
        print(f"\n📊 결과:")
        print(f"   첫 검색 평균: {first_search['avg_time']:.3f}초 (±{first_search['std_dev']:.3f})")
        print(f"   캐시 검색 평균: {cached_search['avg_time']:.3f}초 (±{cached_search['std_dev']:.3f})")
        print(f"   캐시 개선: {cache_improvement:.1f}%")
        print(f"   캐시 속도: {cache_speed_ratio:.0f}x" if cache_speed_ratio != float('inf') else "   캐시 속도: 무한대")
        
        return result
    
    def test_parallel_processing(self) -> Dict:
        """3. 병렬 처리 성능 테스트"""
        print("\n" + "="*80)
        print("🔥 테스트 3: 순차 vs 병렬 처리 성능 비교")
        print("="*80)
        
        keywords = ["아이폰", "삼성", "나이키"]
        limit = 3
        
        # 캐시 초기화
        cache_manager.clear_cache()
        
        print(f"\n1️⃣ 순차 처리 테스트 - 키워드: {keywords}")
        print("-" * 50)
        
        def sequential_search():
            results = []
            for keyword in keywords:
                result = search_ssg_products(keyword, limit=limit)
                results.extend(result)
            return results
        
        sequential_results = self.measure_execution_time(sequential_search)
        
        # 캐시 초기화
        cache_manager.clear_cache()
        
        print(f"\n2️⃣ 병렬 처리 테스트 - 키워드: {keywords}")
        print("-" * 50)
        
        def parallel_search():
            results = []
            with ThreadPoolExecutor(max_workers=len(keywords)) as executor:
                futures = [executor.submit(search_ssg_products, keyword, limit=limit) for keyword in keywords]
                for future in futures:
                    results.extend(future.result())
            return results
        
        parallel_results = self.measure_execution_time(parallel_search)
        
        # 병렬 처리 효율성 계산
        parallel_improvement = ((sequential_results['avg_time'] - parallel_results['avg_time']) / sequential_results['avg_time']) * 100
        parallel_speed_ratio = sequential_results['avg_time'] / parallel_results['avg_time']
        
        result = {
            'sequential_time': sequential_results['avg_time'],
            'parallel_time': parallel_results['avg_time'],
            'parallel_improvement_percent': parallel_improvement,
            'parallel_speed_ratio': parallel_speed_ratio,
            'sequential_std_dev': sequential_results['std_dev'],
            'parallel_std_dev': parallel_results['std_dev']
        }
        
        print(f"\n📊 결과:")
        print(f"   순차 처리 평균: {sequential_results['avg_time']:.3f}초 (±{sequential_results['std_dev']:.3f})")
        print(f"   병렬 처리 평균: {parallel_results['avg_time']:.3f}초 (±{parallel_results['std_dev']:.3f})")
        print(f"   병렬 개선: {parallel_improvement:.1f}%")
        print(f"   병렬 속도: {parallel_speed_ratio:.2f}x")
        
        return result
    
    def test_product_name_quality(self) -> Dict:
        """4. 상품명 품질 개선 테스트"""
        print("\n" + "="*80)
        print("📊 테스트 4: 상품명 품질 개선 비교")
        print("="*80)
        
        keywords = ["라면", "운동화", "화장품"]
        
        legacy_quality = []
        improved_quality = []
        
        for keyword in keywords:
            print(f"\n🔍 키워드: {keyword}")
            print("-" * 30)
            
            # 캐시 초기화
            cache_manager.clear_cache()
            
            # 기존 크롤러 테스트
            legacy_products = search_ssg_products_legacy(keyword, limit=5)
            legacy_generic = sum(1 for p in legacy_products if f"{keyword} 관련 상품" in p['name'])
            legacy_quality_rate = ((len(legacy_products) - legacy_generic) / len(legacy_products)) * 100 if legacy_products else 0
            legacy_quality.append(legacy_quality_rate)
            
            print(f"   기존 크롤러: {len(legacy_products)}개 중 {len(legacy_products) - legacy_generic}개 정확 ({legacy_quality_rate:.1f}%)")
            
            # 캐시 초기화
            cache_manager.clear_cache()
            
            # 개선된 크롤러 테스트
            improved_products = search_ssg_products(keyword, limit=5)
            improved_generic = sum(1 for p in improved_products if f"{keyword} 관련 상품" in p['name'])
            improved_quality_rate = ((len(improved_products) - improved_generic) / len(improved_products)) * 100 if improved_products else 0
            improved_quality.append(improved_quality_rate)
            
            print(f"   개선된 크롤러: {len(improved_products)}개 중 {len(improved_products) - improved_generic}개 정확 ({improved_quality_rate:.1f}%)")
        
        avg_legacy_quality = statistics.mean(legacy_quality)
        avg_improved_quality = statistics.mean(improved_quality)
        quality_improvement = avg_improved_quality - avg_legacy_quality
        
        result = {
            'legacy_quality_avg': avg_legacy_quality,
            'improved_quality_avg': avg_improved_quality,
            'quality_improvement': quality_improvement,
            'legacy_quality_details': legacy_quality,
            'improved_quality_details': improved_quality
        }
        
        print(f"\n📊 전체 결과:")
        print(f"   기존 크롤러 평균 품질: {avg_legacy_quality:.1f}%")
        print(f"   개선된 크롤러 평균 품질: {avg_improved_quality:.1f}%")
        print(f"   품질 개선: +{quality_improvement:.1f}%p")
        
        return result
    
    def test_memory_efficiency(self) -> Dict:
        """5. 메모리 효율성 테스트"""
        print("\n" + "="*80)
        print("🧠 테스트 5: 메모리 효율성 분석")
        print("="*80)
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # 초기 메모리 사용량
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            print(f"초기 메모리 사용량: {initial_memory:.1f} MB")
            
            # 여러 검색 수행
            keywords = ["아이폰", "삼성", "나이키", "라면", "노트북"] * 2  # 10회 검색
            
            memory_usage = [initial_memory]
            
            for i, keyword in enumerate(keywords):
                search_ssg_products(keyword, limit=3)
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_usage.append(current_memory)
                
                if (i + 1) % 2 == 0:
                    print(f"   {i+1}회 검색 후: {current_memory:.1f} MB (+{current_memory-initial_memory:.1f} MB)")
            
            final_memory = memory_usage[-1]
            max_memory = max(memory_usage)
            memory_increase = final_memory - initial_memory
            
            result = {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'max_memory_mb': max_memory,
                'memory_increase_mb': memory_increase,
                'memory_efficiency': 'Excellent' if memory_increase < 50 else 'Good' if memory_increase < 100 else 'Fair'
            }
            
            print(f"\n📊 메모리 효율성 결과:")
            print(f"   최종 메모리: {final_memory:.1f} MB")
            print(f"   최대 메모리: {max_memory:.1f} MB")
            print(f"   메모리 증가: {memory_increase:.1f} MB")
            print(f"   효율성 평가: {result['memory_efficiency']}")
            
            return result
            
        except ImportError:
            print("⚠️ psutil 라이브러리가 필요합니다")
            return {'error': 'psutil not available'}
    
    def generate_comprehensive_report(self) -> str:
        """종합 성능 보고서 생성"""
        print("\n" + "="*80)
        print("📋 종합 성능 벤치마크 실행")
        print("="*80)
        
        # 모든 테스트 실행
        sync_async_result = self.test_sync_vs_async_crawler()
        cache_result = self.test_cache_performance()
        parallel_result = self.test_parallel_processing()
        quality_result = self.test_product_name_quality()
        memory_result = self.test_memory_efficiency()
        
        # 보고서 생성
        report = []
        report.append("\n" + "🎯 최종 성능 벤치마크 보고서")
        report.append("=" * 80)
        
        # 1. 비동기 처리 효과
        report.append(f"\n🚀 1. 비동기 처리 효과:")
        report.append(f"   • 동기 크롤러: {sync_async_result['sync_avg_time']:.3f}초")
        report.append(f"   • 비동기 크롤러: {sync_async_result['async_avg_time']:.3f}초")
        report.append(f"   • 성능 개선: {sync_async_result['improvement_percent']:.1f}%")
        report.append(f"   • 속도 향상: {sync_async_result['speed_ratio']:.2f}배")
        
        # 2. 캐시 시스템 효과
        report.append(f"\n💾 2. 캐시 시스템 효과:")
        report.append(f"   • 첫 검색: {cache_result['first_search_time']:.3f}초")
        report.append(f"   • 캐시 검색: {cache_result['cached_search_time']:.3f}초")
        report.append(f"   • 캐시 개선: {cache_result['cache_improvement_percent']:.1f}%")
        if cache_result['cache_speed_ratio'] != float('inf'):
            report.append(f"   • 캐시 속도: {cache_result['cache_speed_ratio']:.0f}배")
        else:
            report.append(f"   • 캐시 속도: 무한대 (즉시 응답)")
        
        # 3. 병렬 처리 효과
        report.append(f"\n🔥 3. 병렬 처리 효과:")
        report.append(f"   • 순차 처리: {parallel_result['sequential_time']:.3f}초")
        report.append(f"   • 병렬 처리: {parallel_result['parallel_time']:.3f}초")
        report.append(f"   • 병렬 개선: {parallel_result['parallel_improvement_percent']:.1f}%")
        report.append(f"   • 병렬 속도: {parallel_result['parallel_speed_ratio']:.2f}배")
        
        # 4. 상품명 품질 개선
        report.append(f"\n📊 4. 상품명 품질 개선:")
        report.append(f"   • 기존 품질: {quality_result['legacy_quality_avg']:.1f}%")
        report.append(f"   • 개선된 품질: {quality_result['improved_quality_avg']:.1f}%")
        report.append(f"   • 품질 향상: +{quality_result['quality_improvement']:.1f}%p")
        
        # 5. 메모리 효율성
        if 'error' not in memory_result:
            report.append(f"\n🧠 5. 메모리 효율성:")
            report.append(f"   • 메모리 증가: {memory_result['memory_increase_mb']:.1f} MB")
            report.append(f"   • 효율성 평가: {memory_result['memory_efficiency']}")
        
        # 전체 결론
        report.append(f"\n🏆 전체 성능 개선 요약:")
        report.append(f"   • 🥇 캐시 시스템: {cache_result['cache_improvement_percent']:.0f}% 개선 (가장 효과적)")
        report.append(f"   • 🥈 병렬 처리: {parallel_result['parallel_improvement_percent']:.0f}% 개선")
        report.append(f"   • 🥉 상품명 품질: +{quality_result['quality_improvement']:.0f}%p 향상")
        report.append(f"   • 🏅 비동기 처리: {sync_async_result['improvement_percent']:.0f}% 개선")
        
        # 실제 사용자 경험 개선
        total_improvement = (
            sync_async_result['improvement_percent'] +
            cache_result['cache_improvement_percent'] +
            parallel_result['parallel_improvement_percent']
        ) / 3
        
        report.append(f"\n💡 실제 사용자 경험:")
        report.append(f"   • 평균 성능 개선: {total_improvement:.0f}%")
        report.append(f"   • 첫 검색: ~{sync_async_result['async_avg_time']:.1f}초")
        report.append(f"   • 캐시된 검색: ~{cache_result['cached_search_time']:.3f}초 (거의 즉시)")
        report.append(f"   • 다중 검색: 병렬 처리로 {parallel_result['parallel_speed_ratio']:.1f}배 빠름")
        report.append(f"   • 상품명 정확도: {quality_result['improved_quality_avg']:.0f}%")
        
        return "\n".join(report)

def main():
    """메인 벤치마크 실행"""
    print("🔬 SSG 크롤러 성능 벤치마크 시작")
    print(f"시작 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    benchmark = PerformanceBenchmark()
    report = benchmark.generate_comprehensive_report()
    
    print(report)
    
    print(f"\n⏱️ 벤치마크 완료 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊 모든 성능 테스트가 완료되었습니다!")

if __name__ == "__main__":
    main()