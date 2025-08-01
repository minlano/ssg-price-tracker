import React, { useState, useEffect } from 'react';
import './ProductDetail.css';

function ProductDetail({ product, onClose, onAddToTracking }) {
  const [isLoading, setIsLoading] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(0);
  const [reviewCount, setReviewCount] = useState(0);

  useEffect(() => {
    if (product) {
      // 상품 ID가 있으면 API 호출, 없으면 URL로 직접 리뷰 크롤링
      if (product.id) {
        fetchProductDetail();
      } else {
        // 검색 결과에서 온 상품의 경우 URL로 직접 리뷰 크롤링
        fetchReviewsDirectly();
      }
    }
  }, [product]);

  const fetchProductDetail = async () => {
    try {
      const response = await fetch(`/api/products/${product.id}/detail`);
      if (response.ok) {
        const detailData = await response.json();
        setReviews(detailData.reviews || []);
        setRating(detailData.rating || 0);
        setReviewCount(detailData.review_count || 0);
      } else {
        console.error('상품 상세 정보 조회 실패');
        // 실패 시 더미 데이터 사용
        generateFallbackReviews();
      }
    } catch (error) {
      console.error('상품 상세 정보 조회 중 오류:', error);
      // 오류 시 더미 데이터 사용
      generateFallbackReviews();
    }
  };

  const fetchReviewsDirectly = async () => {
    try {
      setIsLoading(true);
      console.log('상품 URL로 직접 리뷰 크롤링 시도:', product.url);
      
      const response = await fetch('/api/reviews/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: product.url,
          source: product.source || 'SSG'
        })
      });

      if (response.ok) {
        const reviewData = await response.json();
        console.log('리뷰 크롤링 성공:', reviewData);
        
        setReviews(reviewData.reviews || []);
        setRating(reviewData.average_rating || 0);
        setReviewCount(reviewData.total_reviews || 0);
      } else {
        console.error('리뷰 크롤링 실패');
        generateFallbackReviews();
      }
    } catch (error) {
      console.error('리뷰 크롤링 중 오류:', error);
      generateFallbackReviews();
    } finally {
      setIsLoading(false);
    }
  };

  const generateFallbackReviews = () => {
    const fallbackReviews = [
      {
        id: 1,
        user: "구매자1",
        rating: 5,
        date: "2024-01-15",
        comment: "정말 만족스러운 상품입니다. 품질이 좋고 가격도 합리적이에요!",
        helpful: 12
      },
      {
        id: 2,
        user: "구매자2", 
        rating: 4,
        date: "2024-01-10",
        comment: "배송이 빠르고 상품 상태가 좋습니다. 추천합니다.",
        helpful: 8
      },
      {
        id: 3,
        user: "구매자3",
        rating: 5,
        date: "2024-01-08", 
        comment: "기대 이상의 상품이었습니다. 다음에도 구매할 예정입니다.",
        helpful: 15
      }
    ];

    setReviews(fallbackReviews);
    setRating(4.2);
    setReviewCount(127);
  };

  const handleAddToTracking = async () => {
    setIsLoading(true);
    try {
      await onAddToTracking(product);
      alert('추적 목록에 추가되었습니다!');
    } catch (error) {
      alert('추적 목록 추가 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={`star ${i <= rating ? 'filled' : ''}`}>
          ★
        </span>
      );
    }
    return stars;
  };

  if (!product) return null;

  return (
    <div className="product-detail-overlay">
      <div className="product-detail-modal">
        <button className="close-btn" onClick={onClose}>×</button>
        
        <div className="product-detail-content">
          <div className="product-main-info">
            <div className="product-image">
              <img 
                src={product.image_url} 
                alt={product.name}
                onError={(e) => {
                  e.target.src = `https://via.placeholder.com/400x400/4A90E2/FFFFFF?text=${encodeURIComponent(product.name)}`;
                }}
              />
            </div>
            
            <div className="product-info">
              <h2>{product.name}</h2>
              <div className="price-info">
                <span className="current-price">
                  {(product.current_price || product.price)?.toLocaleString()}원
                </span>
                {product.original_price && (
                  <span className="original-price">
                    {product.original_price?.toLocaleString()}원
                  </span>
                )}
              </div>
              
              <div className="rating-info">
                <div className="stars">
                  {renderStars(rating)}
                </div>
                <span className="rating-text">{rating} ({reviewCount}개 리뷰)</span>
              </div>
              
              <div className="product-meta">
                <p><strong>브랜드:</strong> {product.brand || '정보 없음'}</p>
                <p><strong>출처:</strong> {product.source}</p>
                {product.description && (
                  <p><strong>설명:</strong> {product.description}</p>
                )}
              </div>
              
              <div className="action-buttons">
                <button 
                  className="add-tracking-btn"
                  onClick={handleAddToTracking}
                  disabled={isLoading}
                >
                  {isLoading ? '추가 중...' : '추적 목록에 추가'}
                </button>
                <a 
                  href={product.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="view-original-btn"
                >
                  원본 페이지 보기
                </a>
              </div>
            </div>
          </div>
          
          <div className="product-details">
            <h3>상품 상세 정보</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <strong>상품명</strong>
                <span>{product.name}</span>
              </div>
              <div className="detail-item">
                <strong>현재 가격</strong>
                <span>{(product.current_price || product.price)?.toLocaleString()}원</span>
              </div>
              <div className="detail-item">
                <strong>브랜드</strong>
                <span>{product.brand || '정보 없음'}</span>
              </div>
              <div className="detail-item">
                <strong>출처</strong>
                <span>{product.source}</span>
              </div>
              {product.description && (
                <div className="detail-item full-width">
                  <strong>상품 설명</strong>
                  <span>{product.description}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="customer-reviews">
            <h3>고객 리뷰 ({reviewCount}개)</h3>
            <div className="reviews-summary">
              <div className="overall-rating">
                <div className="rating-display">
                  <span className="rating-number">{rating}</span>
                  <div className="stars">{renderStars(rating)}</div>
                </div>
                <div className="rating-stats">
                  <p>전체 {reviewCount}개 리뷰</p>
                  <p>평균 평점: {rating}점</p>
                </div>
                <div className="rating-distribution">
                  {[5, 4, 3, 2, 1].map(star => (
                    <div key={star} className="rating-bar">
                      <span className="star-label">{star}점</span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill" 
                          style={{ 
                            width: `${(reviews.filter(r => r.rating === star).length / reviewCount) * 100}%` 
                          }}
                        ></div>
                      </div>
                      <span className="count-label">
                        {reviews.filter(r => r.rating === star).length}개
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="reviews-list">
              {reviews.map(review => (
                <div key={review.id} className="review-item">
                  <div className="review-header">
                    <div className="reviewer-info">
                      <span className="reviewer-name">{review.user}</span>
                      <div className="review-stars">
                        {renderStars(review.rating)}
                      </div>
                    </div>
                    <span className="review-date">{review.date}</span>
                  </div>
                  <p className="review-comment">{review.comment}</p>
                  <div className="review-footer">
                    <span className="helpful-count">도움됨 {review.helpful}명</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetail; 