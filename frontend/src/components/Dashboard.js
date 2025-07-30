import React, { useState, useEffect } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    // 30초마다 대시보드 데이터 새로고침
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
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
      <h3>📊 대시보드</h3>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-content">
            <h4>등록된 상품</h4>
            <p className="stat-number">{dashboardData.total_products}</p>
            <span className="stat-label">개</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div className="stat-content">
            <h4>활성 알림</h4>
            <p className="stat-number">{dashboardData.active_alerts}</p>
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
      </div>

      {dashboardData.recent_changes && dashboardData.recent_changes.length > 0 && (
        <div className="recent-changes">
          <h4>📈 최근 가격 변동</h4>
          <div className="changes-list">
            {dashboardData.recent_changes.slice(0, 8).map((change, index) => (
              <div key={index} className="change-item">
                <div className="change-info">
                  <span className="product-name">{change.name}</span>
                  <span className="change-price">{change.price.toLocaleString()}원</span>
                </div>
                <div className="change-date">
                  {new Date(change.logged_at).toLocaleDateString('ko-KR', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
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