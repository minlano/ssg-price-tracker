// === 가격 추적 목록 컴포넌트 시작 ===
import React, { useState, useEffect, useCallback } from 'react';
import PriceChart from './PriceChart';
import './WatchList.css';

function WatchList() {
  // === 탭 상태 관리 시작 ===
  const [activeTab, setActiveTab] = useState('temp'); // 'temp' 또는 'tracking'
  // === 탭 상태 관리 끝 ===

  // === 임시 추적 목록 상태 관리 시작 ===
  const [watchlist, setWatchlist] = useState([]);
  const [tempWatchlist, setTempWatchlist] = useState([]);
  const [userEmail, setUserEmail] = useState(() => {
    // localStorage에서 이메일 복원
    const savedEmail = localStorage.getItem('userEmail');
    console.log('🔍 저장된 이메일:', savedEmail);
    return savedEmail || '';
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSending, setIsEmailSending] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showChart, setShowChart] = useState(false);

  const [selectedItems, setSelectedItems] = useState(new Set());
  const [isEmailActivated, setIsEmailActivated] = useState(() => {
    // localStorage에서 활성화 상태 복원
    return localStorage.getItem('isEmailActivated') === 'true';
  });
  // === 임시 추적 목록 상태 관리 끝 ===

  // === 임시 추적 목록 조회 시작 ===
  const fetchTempWatchlist = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/watchlist/temp');
      const data = await response.json();
      
      console.log('🔍 임시 추적 목록 응답:', data);
      
      if (response.ok) {
        setTempWatchlist(data.watchlist);
        console.log('✅ 임시 추적 목록 설정됨:', data.watchlist.length, '개');
      } else {
        console.error('임시 추적 목록 조회 실패:', data.error);
      }
    } catch (error) {
      console.error('임시 추적 목록 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // === 가격 추적 목록 조회 시작 ===
  const fetchTrackingWatchlist = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/watchlist/tracking?user_email=${encodeURIComponent(userEmail)}`);
      const data = await response.json();
      
      console.log('🔍 가격 추적 목록 응답:', data);
      
      if (response.ok) {
        setWatchlist(data.watchlist);
        console.log('✅ 가격 추적 목록 설정됨:', data.watchlist.length, '개');
      } else {
        console.error('가격 추적 목록 조회 실패:', data.error);
      }
    } catch (error) {
      console.error('가격 추적 목록 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 이메일 변경 시 localStorage에 저장
  const handleEmailChange = (e) => {
    const email = e.target.value;
    setUserEmail(email);
    localStorage.setItem('userEmail', email);
  };

  // 체크박스 선택/해제
  const handleItemSelect = (itemId) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  // 전체 선택/해제
  const handleSelectAll = () => {
    if (selectedItems.size === tempWatchlist.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(tempWatchlist.map(item => item.id)));
    }
  };



  // 가격 추적 이메일 전송
  const sendPriceTrackingEmail = async () => {
    if (!userEmail.trim()) {
      alert('이메일 주소를 입력해주세요.');
      return;
    }

    // 선택된 상품들 확인
    const selectedProducts = tempWatchlist.filter(item => selectedItems.has(item.id));
    if (selectedProducts.length === 0) {
      alert('전송할 상품을 선택해주세요.');
      return;
    }

    setIsEmailSending(true);
    try {
      console.log('🔍 이메일 전송 시작');
      console.log('🔍 요청 URL:', '/api/email/send-tracking');
      console.log('🔍 사용자 이메일:', userEmail);
      console.log('🔍 선택된 상품:', selectedProducts);
      
            // 선택된 상품들을 alert 테이블에 저장
      try {
        const response = await fetch('/api/email/send-tracking', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_email: userEmail,
            selected_products: selectedProducts
          })
        });
        
        if (!response.ok) {
          console.error('가격 추적 설정 실패');
        } else {
          const data = await response.json();
          console.log('가격 추적 설정 완료:', data);
        }
      } catch (error) {
        console.error('가격 추적 설정 오류:', error);
      }
      
      // 서버 요청 없이 바로 처리
      
      // 가격 추적 목록 새로고침
      console.log('🔍 가격 추적 목록 새로고침 시작');
      await fetchTrackingWatchlist();
      console.log('🔍 가격 추적 목록 새로고침 완료');
      
      // 임시 목록도 새로고침 (제거된 항목들이 사라지도록)
      console.log('🔍 임시 목록 새로고침 시작');
      await fetchTempWatchlist();
      console.log('🔍 임시 목록 새로고침 완료');
      
      console.log('🔍 탭을 tracking으로 변경');
      setActiveTab('tracking');
      setSelectedItems(new Set());
      
      // 마지막에 alert 표시
      setTimeout(() => {
        alert('기능 구현중입니다!');
      }, 100);
    } catch (error) {
      console.error('이메일 전송 오류:', error);
      alert('이메일 전송 중 오류가 발생했습니다.');
    } finally {
      setIsEmailSending(false);
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
        fetchTrackingWatchlist(); // 목록 새로고침
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

  // 실제 추적 목록 조회
  const fetchWatchlist = useCallback(async () => {
    if (!userEmail.trim()) return;
    
    setIsLoading(true);
    try {
      console.log('🔍 추적 목록 조회 시도:', userEmail);
      const response = await fetch(`/api/watchlist?user_email=${encodeURIComponent(userEmail)}`);
      const data = await response.json();
      
      console.log('🔍 추적 목록 응답:', data);
      
      if (response.ok) {
        setWatchlist(data.watchlist);
        // 추적 목록이 있으면 활성화 상태로 설정
        if (data.watchlist.length > 0) {
          setIsEmailActivated(true);
          localStorage.setItem('isEmailActivated', 'true');
          console.log('✅ 추적 목록 설정됨:', data.watchlist.length, '개');
        } else {
          console.log('📭 추적 목록이 비어있음');
        }
      } else {
        console.error('추적 목록 조회 실패:', data.error);
        // 오류가 발생해도 알림은 표시하지 않음 (자동 조회이므로)
      }
    } catch (error) {
      console.error('추적 목록 조회 오류:', error);
      alert('추적 목록 조회 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [userEmail]);

  // 자동 이메일 감지 함수
  const detectAutoEmail = async () => {
    try {
      const response = await fetch('/api/auto-email');
      const data = await response.json();
      
      if (response.ok && data.found && data.email) {
        console.log('🔍 자동 이메일 감지됨:', data.email);
        setUserEmail(data.email);
        localStorage.setItem('userEmail', data.email);
        return data.email;
      }
    } catch (error) {
      console.error('자동 이메일 감지 오류:', error);
    }
    return null;
  };

  // === 컴포넌트 마운트시 데이터 로드 시작 ===
  React.useEffect(() => {
    fetchTempWatchlist();
    fetchTrackingWatchlist();
    
    // 자동 이메일 감지 및 설정
    const setupAutoEmail = async () => {
      // localStorage에 이메일이 없으면 자동 감지
      const savedEmail = localStorage.getItem('userEmail');
      if (!savedEmail) {
        const detectedEmail = await detectAutoEmail();
        if (detectedEmail) {
          console.log('✅ 자동 이메일 설정됨:', detectedEmail);
        }
      }
    };
    
    setupAutoEmail();
    
    // 초기 탭 설정: 항상 임시 추적 탭으로 시작
    setActiveTab('temp');
    
    // 디버깅: 데이터베이스에 있는 이메일 확인
    console.log('🔍 현재 이메일 상태:', {
      userEmail,
      isEmailActivated,
      localStorageEmail: localStorage.getItem('userEmail')
    });
  }, []); // 컴포넌트 마운트시 한 번만 실행

  // 이메일이 변경될 때마다 추적 목록 조회 (자동 조회 비활성화)
  // React.useEffect(() => {
  //   if (userEmail.trim()) {
  //     console.log('🔍 이메일 변경됨, 추적 목록 조회 시도:', userEmail);
  //     fetchWatchlist();
  //   } else {
  //     // 이메일이 없으면 가격 추적 목록 초기화
  //     setWatchlist([]);
  //   }
  // }, [userEmail, fetchWatchlist]);

  // 디버깅용 상태 로그
  React.useEffect(() => {
    console.log('🔍 WatchList 상태:', {
      isEmailActivated,
      userEmail,
      tempWatchlistLength: tempWatchlist.length,
      watchlistLength: watchlist.length,
      isLoading
    });
  }, [isEmailActivated, userEmail, tempWatchlist.length, watchlist.length, isLoading]);
  // === 컴포넌트 마운트시 데이터 로드 끝 ===

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h2>📋 추적 목록</h2>
        
        {/* === 탭 네비게이션 시작 === */}
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'temp' ? 'active' : ''}`}
            onClick={() => setActiveTab('temp')}
          >
            ⏳ 임시 추적 목록 ({tempWatchlist.length})
          </button>
          <button 
            className={`tab-button ${activeTab === 'tracking' ? 'active' : ''}`}
            onClick={() => setActiveTab('tracking')}
          >
            📧 가격 추적 목록 ({watchlist.length})
          </button>
        </div>

        <div className="email-input-section">
          <input
            type="email"
            value={userEmail}
            onChange={handleEmailChange}
            placeholder="이메일 주소를 입력하세요"
            className="email-input"
          />
          <button onClick={sendPriceTrackingEmail} disabled={isEmailSending || !userEmail.trim()}>
                          {isEmailSending ? '전송 중...' : '📧 가격 추적 이메일 전송'}
          </button>
          <button onClick={manualPriceCheck} className="price-check-btn">
            🔄 가격 체크
          </button>
        </div>
      </div>

      {/* === 탭 내용 시작 === */}
      
      {/* 임시 추적 목록 탭 */}
      {activeTab === 'temp' && (
        <div className="tab-content">
          {tempWatchlist.length > 0 ? (
            <div className="temp-watchlist-section">
              <div className="temp-watchlist-header">
                                  <h3>⏳ 임시 추적 목록 ({tempWatchlist.length}개)</h3>
                  <p>체크박스로 선택하고 이메일을 전송하면 가격 추적이 시작됩니다.</p>
                  <div className="selection-controls">
                    <label>
                      <input
                        type="checkbox"
                        checked={selectedItems.size === tempWatchlist.length && tempWatchlist.length > 0}
                        onChange={handleSelectAll}
                      />
                      전체 선택
                    </label>
                    <span className="selected-count">
                      {selectedItems.size}개 선택됨
                    </span>
                  </div>
                
              </div>
              <div className="watchlist-grid">
                {tempWatchlist.map((item) => (
                  <div key={item.id} className="watchlist-card temp-card">
                    <div className="item-checkbox">
                      <input
                        type="checkbox"
                        checked={selectedItems.has(item.id)}
                        onChange={() => handleItemSelect(item.id)}
                      />
                    </div>
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
                      <div className="temp-action-buttons">
                        <button 
                          onClick={() => removeFromTempWatchlist(item.id)}
                          className="temp-remove-btn"
                        >
                          🗑️ 제거
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="empty-watchlist">
              <p>📭 임시 추적 목록이 비어있습니다.</p>
              <p>상품 검색에서 관심 있는 상품을 추가해보세요!</p>
            </div>
          )}
        </div>
      )}

      {/* 가격 추적 목록 탭 */}
      {activeTab === 'tracking' && (
        <div className="tab-content">
          {watchlist.length > 0 ? (
            <>
              <div className="watchlist-stats">
                <span>총 {watchlist.length}개 상품 추적 중</span>
                <span>최대 30개까지 추적 가능</span>
              </div>
              <div className="watchlist-grid">
                {watchlist.map((item) => (
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
                      <div className="email-info">
                        <span className="email-badge">
                          📧 {item.user_email}
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
            </>
          ) : (
            <div className="empty-watchlist">
              <p>📭 가격 추적 목록이 비어있습니다.</p>
              <p>임시 추적 목록에서 상품을 추가하고 이메일을 전송해보세요!</p>
            </div>
          )}
        </div>
      )}
      
      {/* === 탭 내용 끝 === */}

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