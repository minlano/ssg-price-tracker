import React, { useState, useEffect } from 'react';
import './ProductList.css';

function ProductList({ refreshTrigger }) {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [alertForm, setAlertForm] = useState({ email: '', targetPrice: '' });

  useEffect(() => {
    fetchProducts();
  }, [refreshTrigger]);

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/products');
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
      }
    } catch (error) {
      console.error('상품 목록 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPriceHistory = async (productId) => {
    try {
      const response = await fetch(`/api/products/${productId}/prices`);
      if (response.ok) {
        const data = await response.json();
        setPriceHistory(data);
      }
    } catch (error) {
      console.error('가격 이력 조회 오류:', error);
    }
  };

  const handleProductClick = (product) => {
    setSelectedProduct(product);
    fetchPriceHistory(product.id);
  };

  const handleCreateAlert = async (e) => {
    e.preventDefault();
    if (!selectedProduct || !alertForm.email || !alertForm.targetPrice) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    try {
      const response = await fetch('/api/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: selectedProduct.id,
          email: alertForm.email,
          target_price: parseInt(alertForm.targetPrice),
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        alert('알림이 설정되었습니다!');
        setAlertForm({ email: '', targetPrice: '' });
      } else {
        alert(data.error || '알림 설정 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('알림 설정 오류:', error);
      alert('알림 설정 중 오류가 발생했습니다.');
    }
  };

  if (isLoading) {
    return <div className="loading">상품 목록을 불러오는 중...</div>;
  }

  return (
    <div className="product-list">
      <h3>📦 추적 중인 상품 ({products.length}개)</h3>
      
      {products.length === 0 ? (
        <div className="empty-state">
          <p>추적 중인 상품이 없습니다.</p>
          <p>위의 검색 기능을 사용해서 상품을 추가해보세요!</p>
        </div>
      ) : (
        <div className="products-container">
          <div className="products-grid">
            {products.map((product) => (
              <div 
                key={product.id} 
                className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}
                onClick={() => handleProductClick(product)}
              >
                {product.image_url && (
                  <img src={product.image_url} alt={product.name} />
                )}
                <div className="product-info">
                  <h5>{product.name}</h5>
                  <p className="price">{product.current_price?.toLocaleString()}원</p>
                  <p className="date">
                    등록일: {new Date(product.created_at).toLocaleDateString()}
                  </p>
                  <a 
                    href={product.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="view-link"
                  >
                    상품 보기
                  </a>
                </div>
              </div>
            ))}
          </div>

          {selectedProduct && (
            <div className="product-detail">
              <h4>📊 {selectedProduct.name} 상세 정보</h4>
              
              <div className="detail-sections">
                <div className="price-history-section">
                  <h5>가격 변동 이력</h5>
                  {priceHistory.length > 0 ? (
                    <div className="price-history">
                      {priceHistory.map((entry, index) => (
                        <div key={index} className="price-entry">
                          <span className="price">{entry.price.toLocaleString()}원</span>
                          <span className="date">
                            {new Date(entry.logged_at).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>가격 이력이 없습니다.</p>
                  )}
                </div>

                <div className="alert-section">
                  <h5>🔔 가격 알림 설정</h5>
                  <form onSubmit={handleCreateAlert} className="alert-form">
                    <input
                      type="email"
                      placeholder="이메일 주소"
                      value={alertForm.email}
                      onChange={(e) => setAlertForm({...alertForm, email: e.target.value})}
                      required
                    />
                    <input
                      type="number"
                      placeholder="목표 가격 (원)"
                      value={alertForm.targetPrice}
                      onChange={(e) => setAlertForm({...alertForm, targetPrice: e.target.value})}
                      required
                    />
                    <button type="submit">알림 설정</button>
                  </form>
                  <p className="alert-info">
                    상품 가격이 목표 가격 이하로 떨어지면 이메일로 알림을 보내드립니다.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ProductList;