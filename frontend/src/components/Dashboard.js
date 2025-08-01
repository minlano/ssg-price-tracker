import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard');
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('대시보드 데이터 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="loading">대시보드 데이터를 불러오는 중...</div>;
  }

  if (!dashboardData) {
    return <div className="error">대시보드 데이터를 불러올 수 없습니다.</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h3>📊 대시보드</h3>
      </div>
      
      {/* 기본 통계 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h4>등록된 상품</h4>
            <p className="stat-number">{dashboardData.total_products || 0}</p>
            <span className="stat-label">개</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div className="stat-content">
            <h4>활성 알림</h4>
            <p className="stat-number">{dashboardData.active_alerts || 0}</p>
            <span className="stat-label">개</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <h4>최근 변동</h4>
            <p className="stat-number">{dashboardData.recent_changes?.length || 0}</p>
            <span className="stat-label">건</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h4>평균 가격</h4>
            <p className="stat-number">{dashboardData.average_price?.toLocaleString() || 0}</p>
            <span className="stat-label">원</span>
          </div>
        </div>
      </div>

      {/* 최근 추가된 상품 */}
      {dashboardData.recent_products && dashboardData.recent_products.length > 0 && (
        <div className="products-section">
          <h4>🆕 최근 추가된 상품</h4>
          <div className="products-grid">
            {dashboardData.recent_products.slice(0, 5).map((product, index) => (
              <div key={index} className="product-card">
                <div className="product-info">
                  <h5>{product.name}</h5>
                  <p className="product-price">{product.price?.toLocaleString()}원</p>
                  <p className="product-brand">{product.brand} • {product.source}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="dashboard-actions">
        <button onClick={fetchDashboardData} className="refresh-btn">
          🔄 새로고침
        </button>
      </div>
    </div>
  );
}

export default Dashboard;