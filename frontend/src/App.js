import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import ProductSearch from './components/ProductSearch';
import ProductList from './components/ProductList';
// === 가격 추적 컴포넌트 import 시작 ===
import WatchList from './components/WatchList';
// === 가격 추적 컴포넌트 import 끝 ===

function App() {
  const [backendStatus, setBackendStatus] = useState('확인 중...');
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('/api/dashboard');
      if (response.ok) {
        setBackendStatus('✅ 연결됨');
        setIsConnected(true);
      } else {
        setBackendStatus('❌ 연결 실패');
        setIsConnected(false);
      }
    } catch (error) {
      console.error('백엔드 연결 오류:', error);
      setBackendStatus('❌ 연결 실패 - 백엔드 서버를 확인해주세요');
      setIsConnected(false);
    }
  };

  const handleProductAdd = () => {
    // 상품이 추가되면 목록을 새로고침
    setRefreshTrigger(prev => prev + 1);
  };

  const renderContent = () => {
    if (!isConnected) {
      return (
        <div className="error-section">
          <h3>⚠️ 백엔드 서버 연결 필요</h3>
          <p>백엔드 서버를 시작하려면:</p>
          <div className="code-block">
            <code>start_backend.bat</code>
          </div>
          <p>또는</p>
          <div className="code-block">
            <code>cd backend && python app.py</code>
          </div>
          <button onClick={checkBackendConnection} className="retry-btn">
            🔄 다시 연결 시도
          </button>
        </div>
      );
    }

    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'search':
        return <ProductSearch onProductAdd={handleProductAdd} />;
      // case 'products':  // 기존 코드 주석 처리
      //   return <ProductList refreshTrigger={refreshTrigger} />;
      // === 가격 추적 목록 탭 추가 시작 ===
      case 'products':
        return <WatchList />;
      // === 가격 추적 목록 탭 추가 끝 ===
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🛒 SSG 가격 추적 시스템</h1>
          <p>SSG.COM 상품 가격을 추적하고 알림을 받아보세요!</p>
          
          <div className="status-bar">
            <span className="status-item">
              백엔드 연결: {backendStatus}
            </span>
          </div>

          {isConnected && (
            <nav className="tab-navigation">
              <button 
                className={activeTab === 'dashboard' ? 'active' : ''}
                onClick={() => setActiveTab('dashboard')}
              >
                📊 대시보드
              </button>
              <button 
                className={activeTab === 'search' ? 'active' : ''}
                onClick={() => setActiveTab('search')}
              >
                🔍 상품 검색
              </button>
              <button 
                className={activeTab === 'products' ? 'active' : ''}
                onClick={() => setActiveTab('products')}
              >
                📦 추적 목록
              </button>
            </nav>
          )}
        </div>
      </header>

      <main className="App-main">
        {renderContent()}
      </main>

      <footer className="App-footer">
        <p>SSG 가격 추적 시스템 v1.0 | 실시간 가격 모니터링</p>
      </footer>
    </div>
  );
}

export default App;