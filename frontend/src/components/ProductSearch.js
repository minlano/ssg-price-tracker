import React, { useState } from 'react';
import './ProductSearch.css';

function ProductSearch({ onProductAdd }) {
  const [keyword, setKeyword] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [compareResults, setCompareResults] = useState(null);

  const handleSearch = async () => {
    if (!keyword.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}&limit=20`);
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

  const handleCompare = async () => {
    if (!keyword.trim()) return;
    
    setIsComparing(true);
    try {
      const response = await fetch(`/api/compare?keyword=${encodeURIComponent(keyword)}&limit=10`);
      const data = await response.json();
      
      if (response.ok) {
        setCompareResults(data);
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



  const handleAddProduct = async (product) => {
    try {
      const response = await fetch('/api/products/add-from-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(product),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('상품이 추가되었습니다!');
        if (onProductAdd) onProductAdd(data.product);
      } else {
        alert(data.error || '상품 추가 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('상품 추가 오류:', error);
      alert('상품 추가 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="product-search">
      <div className="search-header">
        <h3>🔍 상품 검색</h3>
        <div className="search-controls">
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="검색할 상품명을 입력하세요"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={isSearching}>
            {isSearching ? '검색 중...' : '검색'}
          </button>
          <button onClick={handleCompare} disabled={isComparing}>
            {isComparing ? '비교 중...' : '가격 비교'}
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
                  <p className="price">{product.price?.toLocaleString()}원</p>
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