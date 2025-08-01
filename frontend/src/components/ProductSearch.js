import React, { useState } from 'react';
import './ProductSearch.css';
import ProductDetail from './ProductDetail';

function ProductSearch({ onProductAdd }) {
  const [keyword, setKeyword] = useState(() => {
    // localStorage에서 검색 키워드 복원
    return localStorage.getItem('searchKeyword') || '';
  });
  const [searchResults, setSearchResults] = useState(() => {
    // localStorage에서 검색 결과 복원
    const savedResults = localStorage.getItem('searchResults');
    return savedResults ? JSON.parse(savedResults) : [];
  });
  const [isSearching, setIsSearching] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [compareResults, setCompareResults] = useState(() => {
    // localStorage에서 비교 결과 복원
    const savedCompareResults = localStorage.getItem('compareResults');
    return savedCompareResults ? JSON.parse(savedCompareResults) : null;
  });
  // ========== 네이버 쇼핑 상태 시작 ==========
  const [selectedSource, setSelectedSource] = useState(() => {
    // localStorage에서 선택된 소스 복원
    return localStorage.getItem('selectedSource') || 'SSG';
  });
  // ========== 네이버 쇼핑 상태 끝 ==========
  const [selectedProduct, setSelectedProduct] = useState(null);

  // ========== 무한 스크롤 상태 시작 ==========
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 0,
    totalResults: 0,
    hasNext: false,
    hasPrev: false
  });
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  // ========== 무한 스크롤 상태 끝 ==========

  // 검색 키워드 변경 시 localStorage에 저장
  const handleKeywordChange = (e) => {
    const newKeyword = e.target.value;
    setKeyword(newKeyword);
    localStorage.setItem('searchKeyword', newKeyword);
  };

  // 선택된 소스 변경 시 localStorage에 저장
  const handleSourceChange = (e) => {
    const newSource = e.target.value;
    setSelectedSource(newSource);
    localStorage.setItem('selectedSource', newSource);
  };

  // 검색 결과를 localStorage에 저장하는 함수
  const saveSearchResults = (results) => {
    setSearchResults(results);
    localStorage.setItem('searchResults', JSON.stringify(results));
  };

  // 비교 결과를 localStorage에 저장하는 함수
  const saveCompareResults = (results) => {
    setCompareResults(results);
    localStorage.setItem('compareResults', JSON.stringify(results));
  };

  // 검색 기록 초기화 함수
  const clearSearchHistory = () => {
    localStorage.removeItem('searchKeyword');
    localStorage.removeItem('searchResults');
    localStorage.removeItem('compareResults');
    setKeyword('');
    setSearchResults([]);
    setCompareResults(null);
  };

  // 중복 제거 함수
  const removeDuplicates = (products) => {
    const seen = new Set();
    const uniqueProducts = [];
    
    for (const product of products) {
      // URL과 이름으로 중복 체크
      const key = `${product.url || ''}-${product.name || ''}`;
      
      if (!seen.has(key) && product.name && product.name.trim().length > 5) {
        seen.add(key);
        uniqueProducts.push(product);
      }
    }
    
    console.log(`🔍 중복 제거: ${products.length}개 → ${uniqueProducts.length}개`);
    return uniqueProducts;
  };

  // ========== 무한 스크롤 처리 함수 시작 ==========
  const loadMoreProducts = () => {
    if (pagination.hasNext && !isLoadingMore) {
      handleEnhancedSearch(pagination.currentPage + 1, false);
    }
  };

  // 무한 스크롤 감지
  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollHeight - scrollTop <= clientHeight * 1.5) {
      loadMoreProducts();
    }
  };

  // 향상된 검색 함수
  const handleEnhancedSearch = async (page = 1, resetResults = true) => {
    if (!keyword.trim()) return;
    
    if (resetResults) {
      setIsSearching(true);
      setSearchResults([]);
    } else {
      setIsLoadingMore(true);
    }

    try {
      const params = new URLSearchParams({
        keyword: keyword,
        page: page,
        limit: 20
      });

      const response = await fetch(`/api/search/enhanced?${params.toString()}`);
      const data = await response.json();

      if (response.ok) {
        const uniqueProducts = removeDuplicates(data.products);
        
        if (resetResults) {
          setSearchResults(uniqueProducts);
          setPagination(data.pagination);
        } else {
          // 무한 스크롤: 기존 결과에 추가
          setSearchResults(prev => [...prev, ...uniqueProducts]);
          setPagination(data.pagination);
        }

        // 검색 키워드 저장
        localStorage.setItem('searchKeyword', keyword);
        console.log(`✅ 향상된 검색 완료: ${uniqueProducts.length}개 상품`);
      } else {
        console.error('향상된 검색 실패:', data.error);
        alert(data.error || '검색 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('향상된 검색 오류:', error);
      alert('검색 중 오류가 발생했습니다.');
    } finally {
      setIsSearching(false);
      setIsLoadingMore(false);
    }
  };
  // ========== 무한 스크롤 처리 함수 끝 ==========

  // ========== 네이버 쇼핑 검색 함수 시작 ==========
  const handleSearch = async () => {
    if (!keyword.trim()) return;
    
    // SSG인 경우 향상된 검색 사용
    if (selectedSource === 'SSG') {
      handleEnhancedSearch(1, true);
      return;
    }
    
    setIsSearching(true);
    try {
      // === 11번가 API 호출 추가 시작 ===
      let apiUrl;
      if (selectedSource === 'NAVER') {
        apiUrl = `/api/naver/search?keyword=${encodeURIComponent(keyword)}&limit=20`;
      } else if (selectedSource === '11ST') {
        apiUrl = `/api/11st/search?keyword=${encodeURIComponent(keyword)}&limit=20`;
      } else {
        apiUrl = `/api/search?keyword=${encodeURIComponent(keyword)}&limit=20`;
      }
      // === 11번가 API 호출 추가 끝 ===
      
      const response = await fetch(apiUrl);
      const data = await response.json();
      
      if (response.ok) {
        // 중복 제거 로직 추가
        const uniqueProducts = removeDuplicates(data.products);
        saveSearchResults(uniqueProducts);
        // 검색 키워드도 저장
        localStorage.setItem('searchKeyword', keyword);
        console.log(`✅ 검색 완료: ${uniqueProducts.length}개 상품`);
      } else {
        console.error('검색 실패:', data.error);
        alert(data.error || '검색 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('검색 오류:', error);
      alert('검색 중 오류가 발생했습니다.');
    } finally {
      setIsSearching(false);
    }
  };
  // ========== 네이버 쇼핑 검색 함수 끝 ==========

  // ========== 네이버 쇼핑 가격 비교 함수 시작 ==========
  const handleCompare = async () => {
    if (!keyword.trim()) return;
    
    setIsComparing(true);
    try {
      // === 11번가 가격 비교 API 호출 추가 시작 ===
      let apiUrl;
      if (selectedSource === 'NAVER') {
        apiUrl = `/api/naver/compare?keyword=${encodeURIComponent(keyword)}&limit=10`;
      } else if (selectedSource === '11ST') {
        // 11번가는 현재 가격 비교 API가 없으므로 검색 결과로 대체
        apiUrl = `/api/11st/search?keyword=${encodeURIComponent(keyword)}&limit=10`;
      } else {
        apiUrl = `/api/compare?keyword=${encodeURIComponent(keyword)}&limit=10`;
      }
      // === 11번가 가격 비교 API 호출 추가 끝 ===
      
      const response = await fetch(apiUrl);
      const data = await response.json();
      
      if (response.ok) {
        // === 11번가 응답 데이터 처리 추가 시작 ===
        if (selectedSource === '11ST') {
          // 11번가는 검색 결과를 가격 비교 형식으로 변환
          const uniqueProducts = removeDuplicates(data.products);
          const sortedProducts = uniqueProducts.sort((a, b) => a.price - b.price);
          saveCompareResults({
            products: sortedProducts,
            price_stats: {
              min_price: Math.min(...sortedProducts.map(p => p.price)),
              max_price: Math.max(...sortedProducts.map(p => p.price)),
              avg_price: Math.round(sortedProducts.reduce((sum, p) => sum + p.price, 0) / sortedProducts.length)
            }
          });
        } else {
          // 중복 제거 후 저장
          const uniqueProducts = removeDuplicates(data.products || []);
          saveCompareResults({
            ...data,
            products: uniqueProducts
          });
        }
        // === 11번가 응답 데이터 처리 추가 끝 ===
      } else {
        alert(data.error || '가격 비교 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('가격 비교 오류:', error);
      alert('가격 비교 중 오류가 발생했습니다.');
    } finally {
      setIsComparing(false);
    }
  };
  // ========== 네이버 쇼핑 가격 비교 함수 끝 ==========



  // ========== 네이버 쇼핑 상품 추가 함수 시작 ==========
  // const handleAddProduct = async (product) => {  // 기존 함수 주석 처리 시작
  //   try {
  //     const apiUrl = selectedSource === 'NAVER' 
  //       ? '/api/naver/products/add-from-search'
  //       : '/api/products/add-from-search';
  //     
  //     // 네이버 쇼핑의 경우 current_price 필드 사용
  //     const productData = selectedSource === 'NAVER' 
  //       ? { ...product, current_price: product.current_price || product.price }
  //       : product;
  //     
  //     const response = await fetch(apiUrl, {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify(productData),
  //     });
  //     
  //     const data = await response.json();
  //     
  //     if (response.ok) {
  //       alert(`${selectedSource} 상품이 추가되었습니다!`);
  //       if (onProductAdd) onProductAdd(data.product);
  //     } else {
  //       alert(data.error || '상품 추가 중 오류가 발생했습니다.');
  //     }
  //   } catch (error) {
  //     console.error('상품 추가 오류:', error);
  //     alert('상품 추가 중 오류가 발생했습니다.');
  //   }
  // };
  // 기존 함수 주석 처리 끝

  // === 가격 추적 상품 추가 함수 (이메일 없이 임시 저장) 시작 ===
  const handleAddProduct = async (product) => {
    try {
      const watchlistData = {
        product_name: product.name,
        product_url: product.url || '#',
        image_url: product.image_url,
        source: selectedSource,
        current_price: product.current_price || product.price,
        user_email: 'temp@temp.com' // 임시 이메일
      };

      console.log('🔍 전송할 데이터:', watchlistData);
      console.log('🔍 원본 상품 데이터:', product);

      const response = await fetch('/api/watchlist/temp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(watchlistData),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`${selectedSource} 상품이 임시 추적 목록에 추가되었습니다! 추적 목록 탭에서 이메일을 입력하면 알림을 받을 수 있습니다.`);
        if (onProductAdd) onProductAdd(data);
      } else {
        alert(data.error || '추적 목록 추가 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('추적 목록 추가 오류:', error);
      alert('추적 목록 추가 중 오류가 발생했습니다.');
    }
  };
  // === 가격 추적 상품 추가 함수 (이메일 없이 임시 저장) 끝 ===
  // ========== 네이버 쇼핑 상품 추가 함수 끝 ==========

  const handleProductClick = (product) => {
    setSelectedProduct(product);
  };

  const handleCloseDetail = () => {
    setSelectedProduct(null);
  };

  return (
    <div className="product-search">
      <div className="search-header">
        <h3>🔍 상품 검색</h3>
        <div className="search-controls">
          {/* ========== 네이버 쇼핑 UI 시작 ========== */}
          <div className="source-selector">
            <button 
              className={`source-btn ${selectedSource === 'SSG' ? 'active' : ''}`}
              onClick={() => handleSourceChange({ target: { value: 'SSG' } })}
            >
              🛒 SSG
            </button>
            <button 
              className={`source-btn ${selectedSource === 'NAVER' ? 'active' : ''}`}
              onClick={() => handleSourceChange({ target: { value: 'NAVER' } })}
            >
              🔍 네이버쇼핑
            </button>
            {/* === 11번가 탭 추가 시작 === */}
            <button 
              className={`source-btn ${selectedSource === '11ST' ? 'active' : ''}`}
              onClick={() => handleSourceChange({ target: { value: '11ST' } })}
            >
              🏪 11번가
            </button>
            {/* === 11번가 탭 추가 끝 === */}
          </div>
          {/* ========== 네이버 쇼핑 UI 끝 ========== */}
          <input
            type="text"
            value={keyword}
            onChange={handleKeywordChange}
            placeholder={
              // === 11번가 플레이스홀더 추가 시작 ===
              selectedSource === 'NAVER' ? '네이버쇼핑에서 검색할 상품명을 입력하세요' :
              selectedSource === '11ST' ? '11번가에서 검색할 상품명을 입력하세요' :
              'SSG에서 검색할 상품명을 입력하세요'
              // === 11번가 플레이스홀더 추가 끝 ===
            }
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={isSearching}>
            {isSearching ? '검색 중...' : `${selectedSource} 검색`}
          </button>
          <button onClick={handleCompare} disabled={isComparing}>
            {isComparing ? '비교 중...' : `${selectedSource} 가격 비교`}
          </button>
          <button 
            onClick={clearSearchHistory}
            className="clear-history-btn"
            title="검색 기록 초기화"
          >
            🗑️ 기록 초기화
          </button>
        </div>
      </div>

      {compareResults && (
        <div className="compare-results">
          <h4>💰 가격 비교 결과</h4>
          {compareResults.price_stats && (
            <div className="price-stats">
              <span>최저가: {compareResults.price_stats.min_price?.toLocaleString()}원</span>
              <span>최고가: {compareResults.price_stats.max_price?.toLocaleString()}원</span>
              <span>평균가: {compareResults.price_stats.avg_price?.toLocaleString()}원</span>
            </div>
          )}
        </div>
      )}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h4>검색 결과 ({searchResults.length}개)</h4>
          

          
          <div className="products-grid" onScroll={selectedSource === 'SSG' ? handleScroll : undefined}>
            {searchResults.map((product, index) => (
              <div key={index} className="product-card" onClick={() => handleProductClick(product)}>
                <img 
                  src={product.image_url} 
                  alt={product.name}
                  onError={(e) => {
                    // 이미지 로딩 실패 시 기본 이미지로 대체
                    e.target.src = `https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=${encodeURIComponent(product.name)}`;
                  }}
                />
                <div className="product-info">
                  <h5>{product.name}</h5>
                  {/* ========== 네이버 쇼핑 가격 표시 시작 ========== */}
                  <p className="price">
                    {(product.current_price || product.price)?.toLocaleString()}원
                  </p>
                  {/* ========== 네이버 쇼핑 가격 표시 끝 ========== */}
                  <p className="brand">{product.brand}</p>
                  <div className="product-actions">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAddProduct(product);
                      }}
                      className="add-btn"
                    >
                      추적 목록에 추가
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleProductClick(product);
                      }}
                      className="view-detail-btn"
                    >
                      상세보기
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {/* ========== 무한 스크롤 로딩 표시 시작 ========== */}
            {selectedSource === 'SSG' && isLoadingMore && (
              <div className="loading-more">
                <div className="loading-spinner"></div>
                <p>더 많은 상품을 불러오는 중...</p>
              </div>
            )}
            {/* ========== 무한 스크롤 로딩 표시 끝 ========== */}
          </div>
          
          {/* ========== 페이지네이션 정보 시작 ========== */}
          {selectedSource === 'SSG' && pagination.totalResults > 0 && (
            <div className="pagination-info">
              <p>
                총 {pagination.totalResults}개 중 {searchResults.length}개 표시
                {pagination.hasNext && (
                  <span className="scroll-hint"> (스크롤하여 더 보기)</span>
                )}
              </p>
            </div>
          )}
          {/* ========== 페이지네이션 정보 끝 ========== */}
        </div>
      )}

      {selectedProduct && (
        <ProductDetail
          product={selectedProduct}
          onClose={handleCloseDetail}
          onAddToTracking={handleAddProduct}
        />
      )}
    </div>
  );
}

export default ProductSearch;