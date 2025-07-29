# 🛒 SSG 가격 추적 시스템

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000.svg)](https://flask.palletsprojects.com)

4인 팀 9시간 해커톤 프로젝트 - SSG 쇼핑몰 상품 가격 추적 및 알림 시스템

## ⚡ 빠른 시작

### 🚀 원클릭 설치 (권장)

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-username/ssg-price-tracker.git
cd ssg-price-tracker

# 2. 환경 체크 (선택사항)
python check_system.py

# 3. 자동 설치 및 실행
setup.bat        # Windows
./setup.sh       # macOS/Linux
```

### 🎯 즉시 테스트
설치 완료 후 브라우저에서 http://localhost:3000 접속하여 **"아이폰"** 검색해보세요!

## 🌟 주요 기능

### ✨ 새로운 기능 (v2.0)
- 🔍 **실시간 상품 검색**: 키워드로 SSG 상품 검색
- 💰 **가격 비교**: 동일 카테고리 상품 가격 순위 비교
- 📊 **가격 통계**: 최저가, 최고가, 평균가 분석
- 🎯 **원클릭 추가**: 검색 결과에서 바로 추적 목록 등록

### 🎨 기존 기능
- 📈 **가격 차트**: Chart.js 기반 가격 변동 시각화
- 🔔 **스마트 알림**: 목표 가격 도달 시 이메일 알림
- 📱 **반응형 UI**: 모바일/데스크톱 완벽 지원
- ⚡ **실시간 크롤링**: SSG 상품 정보 자동 수집

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend │    │   SQLite DB     │
│   (Port 3000)    │◄──►│   (Port 5000)   │◄──►│   (Local File)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│  SSG Crawler    │──────────────┘
                        │  (BeautifulSoup)│
                        └─────────────────┘
```

## 📁 프로젝트 구조

```
ssg-price-tracker/
├── 🚀 setup.bat/setup.sh          # 원클릭 설치 스크립트
├── 🔍 check_system.py             # 환경 체크 도구
├── 📚 INSTALL.md                  # 상세 설치 가이드
├── 👥 TEAM_WORKFLOW.md            # 팀 협업 가이드
│
├── 📂 backend/                    # Flask API 서버
│   ├── 🌐 app.py                  # 메인 서버 (7개 API 엔드포인트)
│   ├── 🕷️ crawler.py              # SSG 크롤러 (검색 + 가격비교)
│   ├── 🗄️ database.py             # SQLite DB 관리
│   ├── 📧 notification.py         # 이메일 알림 시스템
│   ├── ⏰ scheduler.py            # 가격 모니터링 스케줄러
│   └── 📦 requirements.txt        # Python 의존성
│
├── 📂 frontend/                   # React 웹 앱
│   ├── src/
│   │   ├── 🏠 App.js              # 메인 앱 (4개 탭)
│   │   ├── 🔍 ProductSearch.js    # 상품 검색 & 가격 비교
│   │   ├── 📊 Dashboard.js        # 대시보드 & 차트
│   │   ├── 📦 ProductList.js      # 상품 관리
│   │   └── 🔔 AlertForm.js        # 알림 설정
│   └── 📦 package.json            # Node.js 의존성
│
├── 📂 database/                   # 데이터베이스
│   └── 🗄️ init.sql               # DB 스키마 & 샘플 데이터
│
└── 📂 docker/                     # 컨테이너화 (팀원 D 작업 영역)
    └── 📋 README.md
```

## 🎯 API 엔드포인트

### 🆕 검색 & 비교 API
```http
GET  /api/search?keyword=아이폰&limit=20     # 상품 검색
GET  /api/compare?keyword=무선이어폰&limit=10  # 가격 비교
POST /api/products/add-from-search          # 검색 결과에서 상품 추가
```

### 📊 기존 API
```http
GET  /api/products                          # 상품 목록
POST /api/products                          # 상품 추가 (URL 방식)
GET  /api/products/{id}/prices              # 가격 이력
POST /api/alerts                            # 알림 설정
GET  /api/dashboard                         # 대시보드 데이터
```

## 👥 팀 협업 가이드

### 🔀 브랜치 전략
```bash
main                    # 배포용 메인 브랜치
├── feature/api         # 팀원 A: Backend API 개발
├── feature/frontend    # 팀원 B: React 컴포넌트 개발  
├── feature/crawler     # 팀원 C: 크롤링 & 알림 시스템
└── feature/integration # 팀원 D: DevOps & 통합
```

### ⏰ 9시간 타임라인
- **1-2시간**: 환경 설정 & 브랜치 생성
- **2-6시간**: 병렬 개발 (각자 담당 영역)
- **6-8시간**: 브랜치 병합 & 통합 테스트
- **8-9시간**: 버그 수정 & 데모 준비

### 📋 팀원별 역할
| 팀원 | 담당 영역 | 주요 작업 |
|------|----------|----------|
| **A** | Backend API | 고급 검색, 상품 비교, 가격 예측 API |
| **B** | Frontend UI | 고급 검색 컴포넌트, 모바일 최적화 |
| **C** | 크롤링/알림 | 다중 쇼핑몰 크롤러, 스마트 알림 |
| **D** | DevOps/통합 | Docker, CI/CD, 모니터링 시스템 |

## 🔧 기술 스택

### Backend
- **Python 3.8+** - 메인 언어
- **Flask 2.3+** - 웹 프레임워크
- **SQLite** - 데이터베이스
- **BeautifulSoup4** - 웹 크롤링
- **Requests** - HTTP 클라이언트

### Frontend  
- **React 18+** - UI 프레임워크
- **Chart.js** - 데이터 시각화
- **Bootstrap 5** - CSS 프레임워크
- **Axios** - API 클라이언트

### DevOps
- **Docker** - 컨테이너화
- **GitHub Actions** - CI/CD
- **Nginx** - 리버스 프록시

## 🎮 사용법

### 1. 🔍 상품 검색
```
1. "🔍 상품 검색" 탭 클릭
2. 검색어 입력 (예: "아이폰 15")
3. "일반 검색" 또는 "가격 비교" 선택
4. 결과에서 "추적 추가" 버튼으로 등록
```

### 2. 📊 가격 모니터링
```
1. "📊 대시보드" 탭에서 등록된 상품 확인
2. 상품 선택하여 가격 변동 차트 확인
3. 가격 트렌드 분석
```

### 3. 🔔 알림 설정
```
1. "🔔 알림 설정" 탭 클릭
2. 상품 선택 & 목표 가격 입력
3. 이메일 주소 입력
4. 가격 하락 시 자동 알림 수신
```

## 🎯 데모 시나리오

### 시나리오 1: 아이폰 가격 비교 쇼핑
```
1. 검색어: "아이폰 15"
2. 가격 비교 모드로 여러 모델 비교
3. 최저가 상품을 추적 목록에 추가
4. 목표 가격 설정하여 알림 등록
5. 가격 하락 시 이메일 알림 수신
```

### 시나리오 2: 노트북 장기 모니터링
```
1. 검색어: "게이밍 노트북"  
2. 관심 있는 여러 제품을 추적 목록에 추가
3. 대시보드에서 가격 변동 차트 확인
4. 가격 트렌드 분석 후 구매 타이밍 결정
```

## 🚨 문제 해결

### 자주 발생하는 문제
```bash
# Python 관련
python --version          # 3.8+ 확인
pip install --upgrade pip # pip 업그레이드

# Node.js 관련  
node --version            # 16+ 확인
npm cache clean --force   # 캐시 클리어

# 크롤링 관련
ping www.ssg.com         # 네트워크 연결 확인
```

### 포트 충돌 해결
```bash
# 포트 사용 확인
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Mac/Linux

# 다른 포트 사용
# Backend: app.py에서 port=5001
# Frontend: package.json에서 PORT=3001
```

## 📈 로드맵

### v2.1 (다음 버전)
- [ ] 쿠팡, G마켓 크롤링 추가
- [ ] 슬랙, 카카오톡 알림 지원
- [ ] 가격 예측 AI 모델
- [ ] 모바일 앱 (React Native)

### v3.0 (장기 계획)
- [ ] 마이크로서비스 아키텍처
- [ ] 실시간 WebSocket 알림
- [ ] 사용자 인증 시스템
- [ ] 클라우드 배포 (AWS/GCP)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원 & 문의

- 📧 **Email**: support@ssg-tracker.com
- 💬 **Discord**: [해커톤 서버](https://discord.gg/hackathon)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/ssg-price-tracker/issues)
- 📚 **Wiki**: [프로젝트 위키](https://github.com/your-username/ssg-price-tracker/wiki)

---

<div align="center">

**🎉 해커톤에서 완전히 동작하는 가격 추적 시스템을 만들어보세요!**

Made with ❤️ by 4-Person Hackathon Team

</div>