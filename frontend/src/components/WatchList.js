// === 가격 추적 목록 컴포넌트 시작 ===
import React, { useState, useEffect } from 'react';
import PriceChart from './PriceChart';
import './WatchList.css';

function WatchList() {
  // === 임시 추적 목록 상태 관리 시작 ===
  const [watchlist, setWatchlist] = useState([]);
  const [tempWatchlist, setTempWatchlist] = useState([]);
  const [userEmail, setUserEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showChart, setShowChart] = useState(false);
  const [isEmailActivated, setIsEmailActivated] = useState(false);
  // === 임시 추적 목록 상태 관리 끝 ===

  // === 임시 추적 목록 조회 시작 ===
  const fetchTempWatchlist = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/watchlist/temp');
      const data = await response.json();
      
      if (response.ok) {
        setTempWatchlist(data.watchlist);
      } else {
        console.error('임시 추적 목록 조회 실패:', data.error);
      }
    } catch (error) {
      console.error('임시 추적 목록 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 실제 추적 목록 조회
  const fetchWatchlist = async () => {
    if (!userEmail.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/watchlist?user_email=${encodeURIComponent(userEmail)}`);
      const data = await response.json();
      
      if (response.ok) {
        setWatchlist(data.watchlist);
        setIsEmailActivated(true);
      } else {
        alert(data.error || '추적 목록 조회 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('추적 목록 조회 오류:', error);
      alert('추적 목록 조회 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 임시 추적 목록을 실제 추적 목록으로 활성화
  const activateWatchlist = async () => {
    if (!userEmail.trim()) {
      alert('이메일 주소를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/watchlist/activate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_email: userEmail }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`${data.activated_count}개 상품이 활성화되었습니다! 이제 가격 알림을 받을 수 있습니다.`);
        setIsEmailActivated(true);
        fetchWatchlist();
        setTempWatchlist([]);
      } else {
        alert(data.error || '추적 목록 활성화 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('추적 목록 활성화 오류:', error);
      alert('추적 목록 활성화 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // === 임시 추적 목록 삭제 함수 추가 시작 ===
  const removeFromTempWatchlist = async (watchId) => {
    if (!window.confirm('이 상품을 임시 추적 목록에서 제거하시겠습니까?')) return;
    
    try {
      const response = await fetch(`/api/watchlist/temp/${watchId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('임시 추적 목록에서 제거되었습니다.');
        fetchTempWatchlist(); // 임시 목록 새로고침
      } else {
        alert(data.error || '제거 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('임시 목록 제거 오류:', error);
      alert('제거 중 오류가 발생했습니다.');
    }
  };
  // === 임시 추적 목록 삭제 함수 추가 끝 ===
  
  // === 임시 추적 목록 조회 끝 ===

  // 추적 목록에서 제거
  const removeFromWatchlist = async (watchId) => {
    if (!window.confirm('이 상품을 추적 목록에서 제거하시겠습니까?')) return;
    
    try {
      const response = await fetch(`/api/watchlist/${watchId}?user_email=${encodeURIComponent(userEmail)}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('추적 목록에서 제거되었습니다.');
        fetchWatchlist(); // 목록 새로고침
      } else {
        alert(data.error || '제거 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('제거 오류:', error);
      alert('제거 중 오류가 발생했습니다.');
    }
  };

  // 가격 차트 보기
  const showPriceChart = (product) => {
    setSelectedProduct(product);
    setShowChart(true);
  };

  // 수동 가격 체크
  const manualPriceCheck = async () => {
    try {
      const response = await fetch('/api/price-check', {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('가격 체크가 완료되었습니다. 잠시 후 목록을 새로고침해주세요.');
      } else {
        alert(data.error || '가격 체크 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error('가격 체크 오류:', error);
      alert('가격 체크 중 오류가 발생했습니다.');
    }
  };

  // === 컴포넌트 마운트시 임시 목록 로드 시작 ===
  React.useEffect(() => {
    fetchTempWatchlist();
  }, []);
  // === 컴포넌트 마운트시 임시 목록 로드 끝 ===

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h2>📋 가격 추적 목록</h2>
        <div className="email-input-section">
          <input
            type="email"
            value={userEmail}
            onChange={(e) => setUserEmail(e.target.value)}
            placeholder="이메일 주소를 입력하세요"
            className="email-input"
          />
          {!isEmailActivated ? (
            <button onClick={activateWatchlist} disabled={isLoading}>
              {isLoading ? '활성화 중...' : '추적 활성화'}
            </button>
          ) : (
            <button onClick={fetchWatchlist} disabled={isLoading}>
              {isLoading ? '조회 중...' : '목록 새로고침'}
            </button>
          )}
          <button onClick={manualPriceCheck} className="price-check-btn">
            🔄 가격 체크
          </button>
        </div>
      </div>

      {/* === 임시 추적 목록 표시 시작 === */}
      {!isEmailActivated && tempWatchlist.length > 0 && (
        <div className="temp-watchlist-section">
          <div className="temp-watchlist-header">
            <h3>⏳ 임시 추적 목록 ({tempWatchlist.length}개)</h3>
            <p>이메일을 입력하고 "추적 활성화"를 클릭하면 가격 알림을 받을 수 있습니다.</p>
          </div>
          <div className="watchlist-grid">
            {tempWatchlist.map((item) => (
              <div key={item.id} className="watchlist-card temp-card">
                {item.image_url && (
                  <img src={item.image_url} alt={item.product_name} className="product-image" />
                )}
                <div className="product-details">
                  <h4>{item.product_name}</h4>
                  <div className="price-info">
                    <span className="current-price">
                      현재가: {item.current_price?.toLocaleString()}원
                    </span>
                  </div>
                  <div className="source-info">
                    <span className={`source-badge ${item.source.toLowerCase()}`}>
                      {item.source}
                    </span>
                    <span className="temp-status">임시 저장됨</span>
                  </div>
                  {/* === 임시 추적 목록 삭제 버튼 추가 시작 === */}
                  <div className="temp-action-buttons">
                    <button 
                      onClick={() => removeFromTempWatchlist(item.id)}
                      className="temp-remove-btn"
                    >
                      🗑️ 제거
                    </button>
                  </div>
                  {/* === 임시 추적 목록 삭제 버튼 추가 끝 === */}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {/* === 임시 추적 목록 표시 끝 === */}

      {/* === 활성화된 추적 목록 표시 시작 === */}
      {isEmailActivated && watchlist.length > 0 && (
        <div className="watchlist-stats">
          <span>총 {watchlist.length}개 상품 추적 중</span>
          <span>최대 30개까지 추적 가능</span>
        </div>
      )}

      {isEmailActivated && watchlist.length === 0 && !isLoading && (
        <div className="empty-watchlist">
          <p>📭 활성화된 추적 상품이 없습니다.</p>
          <p>상품 검색에서 관심 있는 상품을 추적 목록에 추가해보세요!</p>
        </div>
      )}

      {!isEmailActivated && tempWatchlist.length === 0 && !isLoading && (
        <div className="empty-watchlist">
          <p>📭 추적 중인 상품이 없습니다.</p>
          <p>상품 검색에서 관심 있는 상품을 추적 목록에 추가해보세요!</p>
        </div>
      )}

      <div className="watchlist-grid">
        {isEmailActivated && watchlist.map((item) => (
          // === 활성화된 추적 목록 표시 끝 ===
          <div key={item.id} className="watchlist-card">
            {item.image_url && (
              <img src={item.image_url} alt={item.product_name} className="product-image" />
            )}
            <div className="product-details">
              <h4>{item.product_name}</h4>
              <div className="price-info">
                <span className="current-price">
                  현재가: {item.current_price?.toLocaleString()}원
                </span>
                {item.target_price && (
                  <span className="target-price">
                    목표가: {item.target_price?.toLocaleString()}원
                  </span>
                )}
              </div>
              <div className="source-info">
                <span className={`source-badge ${item.source.toLowerCase()}`}>
                  {item.source}
                </span>
                <span className="created-date">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="action-buttons">
                <button 
                  onClick={() => showPriceChart(item)}
                  className="chart-btn"
                >
                  📊 가격 차트
                </button>
                <button 
                  onClick={() => removeFromWatchlist(item.id)}
                  className="remove-btn"
                >
                  🗑️ 제거
                </button>
                {item.product_url !== '#' && (
                  <a 
                    href={item.product_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="visit-btn"
                  >
                    🔗 상품 보기
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 가격 차트 모달 */}
      {showChart && selectedProduct && (
        <div className="chart-modal">
          <div className="chart-modal-content">
            <div className="chart-modal-header">
              <h3>📊 {selectedProduct.product_name} 가격 변동</h3>
              <button 
                onClick={() => setShowChart(false)}
                className="close-btn"
              >
                ✕
              </button>
            </div>
            <PriceChart watchId={selectedProduct.id} />
          </div>
        </div>
      )}
    </div>
  );
}

export default WatchList;
// === 가격 추적 목록 컴포넌트 끝 ===