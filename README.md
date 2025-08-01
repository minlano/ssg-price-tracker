# SSG Price Tracker

SSG.com 상품 가격 추적 및 리뷰 크롤링 시스템

## 📁 프로젝트 구조

```
ssg-price-tracker/
├── 📁 backend/                    # 백엔드 서버
│   ├── 📁 api/                   # API 모듈
│   │   ├── advanced_search.py    # 고급 검색 API
│   │   ├── config.py             # API 설정
│   │   ├── data_processing.py    # 데이터 처리 API
│   │   ├── eleventh_street_api.py # 11번가 API 연동
│   │   ├── main.py               # API 메인
│   │   ├── product_comparison.py # 상품 비교 API
│   │   └── README.md             # API 문서
│   ├── 📁 crawlers/              # 크롤러 모듈
│   │   └── naver_shopping_crawler.py # 네이버 쇼핑 크롤러
│   ├── app.py                    # 메인 Flask 애플리케이션
│   ├── async_crawler.py          # 비동기 크롤러
│   ├── cache_manager.py          # 캐시 관리
│   ├── crawler.py                # 메인 크롤러
│   ├── database.py               # 데이터베이스 연결
│   ├── database_models.py        # 데이터베이스 모델
│   ├── models.py                 # 데이터 모델
│   ├── notification.py           # 알림 시스템
│   ├── price_tracker.py          # 가격 추적 시스템
│   ├── review_crawler.py         # 리뷰 크롤러
│   ├── scheduler.py              # 스케줄러
│   └── requirements.txt          # Python 의존성
├── 📁 database/                  # 데이터베이스
│   ├── init.sql                  # 데이터베이스 초기화 스크립트
│   └── ssg_tracker.db           # 메인 데이터베이스
├── 📁 frontend/                  # 프론트엔드 (React)
│   ├── 📁 public/               # 정적 파일
│   │   └── index.html           # 메인 HTML
│   ├── 📁 src/                  # 소스 코드
│   │   ├── 📁 components/       # React 컴포넌트
│   │   │   ├── Dashboard.js     # 대시보드
│   │   │   ├── PriceChart.js    # 가격 차트
│   │   │   ├── ProductDetail.js # 상품 상세
│   │   │   ├── ProductList.js   # 상품 목록
│   │   │   ├── ProductSearch.js # 상품 검색
│   │   │   └── WatchList.js     # 추적 목록
│   │   ├── App.js               # 메인 앱 컴포넌트
│   │   ├── index.js             # 앱 진입점
│   │   └── index.css            # 전역 스타일
│   ├── package.json             # Node.js 의존성
│   └── package-lock.json        # 의존성 잠금 파일
├── 📁 docker/                   # Docker 설정
│   └── README.md                # Docker 문서
├── start_all.bat                # 전체 서비스 시작 (Windows)
├── start_backend.bat            # 백엔드 시작 (Windows)
├── start_frontend.bat           # 프론트엔드 시작 (Windows)
├── setup.bat                    # 환경 설정 (Windows)
├── setup.sh                     # 환경 설정 (Linux/Mac)
└── README.md                    # 프로젝트 문서
```

## 🚀 주요 기능

### 1. 가격 추적 시스템
- **실시간 가격 모니터링**: SSG.com 상품 가격을 3시간마다 자동 체크
- **가격 히스토리**: 상품별 가격 변동 이력 저장 및 차트 표시
- **알림 시스템**: 가격 변동 시 이메일 알림 발송
- **추적 목록 관리**: 사용자별 상품 추적 목록 관리

### 2. 리뷰 크롤링 시스템
- **실제 리뷰 수집**: SSG.com에서 실제 사용자 리뷰 크롤링
- **평점 분석**: 상품별 평균 평점 및 리뷰 통계
- **API 기반 크롤링**: SSG 리뷰 API를 통한 안정적인 데이터 수집

### 3. 상품 검색 및 비교
- **통합 검색**: SSG, 네이버 쇼핑, 11번가 상품 검색
- **상품 비교**: 여러 상품의 가격 및 리뷰 비교
- **가성비 분석**: 최적 상품 추천 시스템

### 4. 웹 인터페이스
- **반응형 디자인**: 모바일/데스크톱 최적화
- **실시간 차트**: 가격 변동 차트 및 통계
- **사용자 친화적 UI**: 직관적인 상품 관리 인터페이스
- **상태 지속성**: 페이지 새로고침 후에도 검색 기록과 추적 목록 유지
- **향상된 대시보드**: 상세한 통계 정보와 분포 차트 제공

## 🛠️ 기술 스택

### 백엔드
- **Python 3.10+**: 메인 프로그래밍 언어
- **Flask**: 웹 프레임워크
- **SQLite**: 데이터베이스
- **BeautifulSoup**: 웹 크롤링
- **Requests**: HTTP 클라이언트
- **Selenium**: 동적 웹페이지 크롤링

### 프론트엔드
- **React 18**: 사용자 인터페이스
- **Recharts**: 데이터 시각화
- **CSS3**: 스타일링

### 인프라
- **Docker**: 컨테이너화
- **Git**: 버전 관리

## 📦 설치 및 실행

### 1. 환경 설정
```bash
# 환경 변수 설정
cp env.example .env
# .env 파일을 편집하여 필요한 설정을 변경하세요

# Windows
setup.bat

# Linux/Mac
./setup.sh
```

### 2. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 설정을 추가하세요:

```bash
# 서버 설정
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# 데이터베이스 설정
DATABASE_PATH=ssg_products.db

# 크롤링 설정
CRAWLING_INTERVAL=10800
CRAWLING_TIMEOUT=30

# 이메일 설정 (선택사항)
EMAIL_NOTIFICATIONS_ENABLED=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. 서비스 시작
```bash
# 전체 서비스 시작 (Windows)
start_all.bat

# 개별 서비스 시작
start_backend.bat    # 백엔드만
start_frontend.bat   # 프론트엔드만
```

### 3. 수동 실행
```bash
# 백엔드
cd backend
python app.py

# 프론트엔드
cd frontend
npm start
```

## 🔧 API 엔드포인트

### 상품 관리
- `GET /api/search` - 상품 검색
- `GET /api/products/all` - 전체 상품 목록
- `GET /api/products/{id}/detail` - 상품 상세 정보
- `POST /api/products/add-from-search` - 검색 결과에서 상품 추가

### 추적 목록
- `GET /api/watchlist` - 사용자 추적 목록
- `POST /api/watchlist` - 추적 목록에 상품 추가
- `DELETE /api/watchlist/{id}` - 추적 목록에서 상품 제거

### 가격 추적
- `GET /api/price-history/{id}` - 가격 히스토리
- `POST /api/price-check` - 수동 가격 체크

### 리뷰 크롤링
- `POST /api/reviews/crawl` - 상품 리뷰 크롤링

## 📊 데이터베이스 스키마

### 주요 테이블
- `products`: 상품 정보
- `price_logs`: 가격 이력
- `price_history`: 추적용 가격 히스토리
- `alerts`: 알림 설정
- `watch_list`: 추적 목록

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**SSG Price Tracker** - 스마트한 가격 추적 시스템 🚀