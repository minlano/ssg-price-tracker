import React, { useState } from 'react';
import './ProductSearch.css';

function ProductSearch({ onProductAdd }) {
  const [keyword, setKeyword] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [compareResults, setCompareResults] = useState(null);
  // ========== 네이버 쇼핑 상태 시작 ==========
  const [selectedSource, setSelectedSource] = useState('SSG'); // 'SSG' 또는 'NAVER'
  // ========== 네이버 쇼핑 상태 끝 ==========

  // ========== 네이버 쇼핑 검색 함수 시작 ==========
  const handleSearch = async () => {
    if (!keyword.trim()) return;
    
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
        setSearchResults(data.products);
      } else {
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
          const sortedProducts = data.products.sort((a, b) => a.price - b.price);
          setCompareResults({
            products: sortedProducts,
            price_stats: {
              min_price: Math.min(...sortedProducts.map(p => p.price)),
              max_price: Math.max(...sortedProducts.map(p => p.price)),
              avg_price: Math.round(sortedProducts.reduce((sum, p) => sum + p.price, 0) / sortedProducts.length)
            }
          });
        } else {
          setCompareResults(data);
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

  return (
    <div className="product-search">
      <div className="search-header">
        <h3>🔍 상품 검색</h3>
        <div className="search-controls">
          {/* ========== 네이버 쇼핑 UI 시작 ========== */}
          <div className="source-selector">
            <button 
              className={`source-btn ${selectedSource === 'SSG' ? 'active' : ''}`}
              onClick={() => setSelectedSource('SSG')}
            >
              🛒 SSG
            </button>
            <button 
              className={`source-btn ${selectedSource === 'NAVER' ? 'active' : ''}`}
              onClick={() => setSelectedSource('NAVER')}
            >
              🔍 네이버쇼핑
            </button>
            {/* === 11번가 탭 추가 시작 === */}
            <button 
              className={`source-btn ${selectedSource === '11ST' ? 'active' : ''}`}
              onClick={() => setSelectedSource('11ST')}
            >
              🏪 11번가
            </button>
            {/* === 11번가 탭 추가 끝 === */}
          </div>
          {/* ========== 네이버 쇼핑 UI 끝 ========== */}
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
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
          <div className="products-grid">
            {searchResults.map((product, index) => (
              <div key={index} className="product-card">
                {product.image_url && (
                  <img src={product.image_url} alt={product.name} />
                )}
                <div className="product-info">
                  <h5>{product.name}</h5>
                  {/* ========== 네이버 쇼핑 가격 표시 시작 ========== */}
                  <p className="price">
                    {(product.current_price || product.price)?.toLocaleString()}원
                  </p>
                  {/* ========== 네이버 쇼핑 가격 표시 끝 ========== */}
                  <p className="brand">{product.brand}</p>
                  <button 
                    onClick={() => handleAddProduct(product)}
                    className="add-btn"
                  >
                    추적 목록에 추가
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductSearch;