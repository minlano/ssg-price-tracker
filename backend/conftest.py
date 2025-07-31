#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os

# pytest 설정 파일

def pytest_configure(config):
    """pytest 설정"""
    # 현재 디렉토리를 Python 경로에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

@pytest.fixture(scope="session")
def test_data():
    """테스트용 데이터"""
    return {
        'test_keyword': '노트북',
        'test_url': 'https://www.ssg.com/item/itemView.ssg?itemId=1000671133675&siteNo=6004&salestrNo=6005',
        'expected_fields': ['name', 'price', 'url', 'source']
    }

@pytest.fixture
def mock_product():
    """테스트용 모의 상품 데이터"""
    return {
        'name': '테스트 노트북',
        'price': 500000,
        'url': 'https://www.ssg.com/item/itemView.ssg?itemId=test',
        'image_url': 'https://example.com/image.jpg',
        'brand': '테스트 브랜드',
        'source': 'SSG'
    }

@pytest.fixture
def mock_reviews():
    """테스트용 모의 리뷰 데이터"""
    return [
        {
            'id': 1,
            'user': 'test_user1',
            'rating': 5,
            'date': '2025-01-01',
            'comment': '좋은 상품입니다.',
            'helpful': 10
        },
        {
            'id': 2,
            'user': 'test_user2',
            'rating': 4,
            'date': '2025-01-02',
            'comment': '만족스럽습니다.',
            'helpful': 5
        }
    ]