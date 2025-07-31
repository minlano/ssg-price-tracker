#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis 라이브러리가 없습니다. 메모리 캐시를 사용합니다.")

class CacheManager:
    """Redis 캐시 매니저"""
    
    def __init__(self):
        self.memory_cache = {}
        
        if REDIS_AVAILABLE:
            # Redis 연결 설정
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # 연결 테스트
                self.redis_client.ping()
                self.redis_available = True
                print("✅ Redis 연결 성공")
            except Exception as e:
                print(f"⚠️ Redis 연결 실패: {e}")
                print("📝 메모리 캐시로 대체합니다.")
                self.redis_available = False
        else:
            self.redis_available = False
            print("📝 메모리 캐시를 사용합니다.")
    
    def _generate_cache_key(self, keyword: str, limit: int = 20) -> str:
        """캐시 키 생성"""
        cache_string = f"search:{keyword}:{limit}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_results(self, keyword: str, limit: int = 20) -> Optional[List[Dict]]:
        """캐시된 검색 결과 조회"""
        cache_key = self._generate_cache_key(keyword, limit)
        
        try:
            if self.redis_available:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    result = json.loads(cached_data)
                    print(f"🎯 캐시 히트: {keyword} ({len(result)}개 상품)")
                    return result
            else:
                # 메모리 캐시 사용
                if cache_key in self.memory_cache:
                    cache_entry = self.memory_cache[cache_key]
                    if datetime.now() < cache_entry['expires_at']:
                        print(f"🎯 메모리 캐시 히트: {keyword} ({len(cache_entry['data'])}개 상품)")
                        return cache_entry['data']
                    else:
                        # 만료된 캐시 삭제
                        del self.memory_cache[cache_key]
        except Exception as e:
            print(f"⚠️ 캐시 조회 오류: {e}")
        
        return None
    
    def cache_results(self, keyword: str, results: List[Dict], limit: int = 20, ttl: int = 3600):
        """검색 결과 캐시 저장"""
        cache_key = self._generate_cache_key(keyword, limit)
        
        try:
            if self.redis_available:
                # Redis에 저장 (TTL: 1시간)
                self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(results, ensure_ascii=False)
                )
                print(f"💾 Redis 캐시 저장: {keyword} ({len(results)}개 상품, TTL: {ttl}초)")
            else:
                # 메모리 캐시에 저장
                self.memory_cache[cache_key] = {
                    'data': results,
                    'expires_at': datetime.now() + timedelta(seconds=ttl)
                }
                print(f"💾 메모리 캐시 저장: {keyword} ({len(results)}개 상품)")
                
                # 메모리 캐시 크기 제한 (최대 100개)
                if len(self.memory_cache) > 100:
                    # 가장 오래된 항목 삭제
                    oldest_key = min(self.memory_cache.keys(), 
                                   key=lambda k: self.memory_cache[k]['expires_at'])
                    del self.memory_cache[oldest_key]
        except Exception as e:
            print(f"⚠️ 캐시 저장 오류: {e}")
    
    def clear_cache(self, pattern: str = "search:*"):
        """캐시 삭제"""
        try:
            if self.redis_available:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    print(f"🗑️ Redis 캐시 삭제: {len(keys)}개 키")
            else:
                # 메모리 캐시 삭제
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith("search:")]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                print(f"🗑️ 메모리 캐시 삭제: {len(keys_to_delete)}개 키")
        except Exception as e:
            print(f"⚠️ 캐시 삭제 오류: {e}")
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 조회"""
        try:
            if self.redis_available:
                info = self.redis_client.info()
                return {
                    'type': 'Redis',
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                }
            else:
                return {
                    'type': 'Memory',
                    'cached_items': len(self.memory_cache),
                    'memory_usage': f"{len(str(self.memory_cache))} bytes"
                }
        except Exception as e:
            return {'error': str(e)}

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()