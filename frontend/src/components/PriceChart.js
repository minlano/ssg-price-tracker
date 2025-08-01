// === 가격 차트 컴포넌트 시작 ===
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

function PriceChart({ watchId }) {
  const [priceHistory, setPriceHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [days, setDays] = useState(7);

  // 가격 히스토리 조회
  const fetchPriceHistory = async () => {
    setIsLoading(true);
    try {
      // watchId가 실제로는 product_id임
      const response = await fetch(`/api/price-history/${watchId}?days=${days}`);
      const data = await response.json();
      
      if (response.ok) {
        // 차트용 데이터 포맷팅
        const formattedData = data.price_history.map(item => ({
          date: new Date(item.recorded_at).toLocaleDateString('ko-KR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit'
          }),
          price: item.price,
          fullDate: item.recorded_at
        }));
        
        setPriceHistory(formattedData);
      } else {
        console.error('가격 히스토리 조회 실패:', data.error);
      }
    } catch (error) {
      console.error('가격 히스토리 조회 오류:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (watchId) {
      fetchPriceHistory();
    }
  }, [watchId, days]);

  // 가격 변동 통계 계산
  const getStats = () => {
    if (priceHistory.length === 0) return null;
    
    const prices = priceHistory.map(item => item.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const currentPrice = prices[prices.length - 1];
    const firstPrice = prices[0];
    const priceChange = currentPrice - firstPrice;
    const priceChangePercent = ((priceChange / firstPrice) * 100).toFixed(1);
    
    return {
      minPrice,
      maxPrice,
      currentPrice,
      priceChange,
      priceChangePercent,
      dataPoints: prices.length
    };
  };

  const stats = getStats();

  // 커스텀 툴팁
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          <p className="tooltip-price">
            가격: {payload[0].value?.toLocaleString()}원
          </p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return <div className="chart-loading">📊 차트 로딩 중...</div>;
  }

  if (priceHistory.length === 0) {
    return (
      <div className="chart-empty">
        <p>📈 가격 데이터가 없습니다.</p>
        <p>상품이 추적된 후 시간이 지나면 가격 변동 차트를 볼 수 있습니다.</p>
        <p>💡 가격 데이터는 1시간마다 자동으로 수집되며, 수동으로도 체크할 수 있습니다.</p>
        <p>🔄 "가격 체크" 버튼을 눌러 최신 가격을 확인해보세요!</p>
      </div>
    );
  }

  return (
    <div className="price-chart-container">
      {/* 기간 선택 */}
      <div className="chart-controls">
        <label>조회 기간:</label>
        <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
          <option value={3}>3일</option>
          <option value={7}>7일</option>
          <option value={14}>14일</option>
        </select>
      </div>

      {/* 가격 통계 */}
      {stats && (
        <div className="price-stats">
          <div className="stat-item">
            <span className="stat-label">현재가</span>
            <span className="stat-value current">
              {stats.currentPrice?.toLocaleString()}원
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">최저가</span>
            <span className="stat-value min">
              {stats.minPrice?.toLocaleString()}원
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">최고가</span>
            <span className="stat-value max">
              {stats.maxPrice?.toLocaleString()}원
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">변동</span>
            <span className={`stat-value change ${stats.priceChange >= 0 ? 'positive' : 'negative'}`}>
              {stats.priceChange >= 0 ? '+' : ''}{stats.priceChange?.toLocaleString()}원
              ({stats.priceChangePercent}%)
            </span>
          </div>
        </div>
      )}

      {/* 가격 차트 */}
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={priceHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#666"
              fontSize={12}
            />
            <YAxis 
              stroke="#666"
              fontSize={12}
              tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#2196F3" 
              strokeWidth={2}
              dot={{ fill: '#2196F3', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#2196F3', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-info">
        <p>📊 총 {stats?.dataPoints}개의 가격 데이터 포인트</p>
        <p>🔄 3시간마다 자동으로 가격이 업데이트됩니다</p>
      </div>
    </div>
  );
}

export default PriceChart;
// === 가격 차트 컴포넌트 끝 ===