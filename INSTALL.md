# 🚀 SSG 가격 추적 시스템 - 설치 가이드

## 📋 시스템 요구사항

### 필수 소프트웨어
- **Python 3.8+** - [다운로드](https://python.org/downloads)
- **Node.js 16+** - [다운로드](https://nodejs.org)
- **Git** - [다운로드](https://git-scm.com)

### 권장 사양
- **RAM**: 4GB 이상
- **저장공간**: 1GB 이상
- **인터넷 연결**: 크롤링을 위한 안정적인 연결

## ⚡ 빠른 설치 (권장)

### Windows
```bash
# 1. 프로젝트 클론
git clone https://github.com/your-username/ssg-price-tracker.git
cd ssg-price-tracker

# 2. 자동 설치 실행 (관리자 권한 필요)
setup.bat
```

### macOS/Linux
```bash
# 1. 프로젝트 클론
git clone https://github.com/your-username/ssg-price-tracker.git
cd ssg-price-tracker

# 2. 자동 설치 실행
chmod +x setup.sh
./setup.sh
```

## 🔧 수동 설치

### 1단계: 프로젝트 클론
```bash
git clone https://github.com/your-username/ssg-price-tracker.git
cd ssg-price-tracker
```

### 2단계: Backend 설정
```bash
cd backend

# Python 패키지 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python database.py

# 크롤러 테스트
python crawler.py
```

### 3단계: Frontend 설정
```bash
cd ../frontend

# Node.js 패키지 설치
npm install

# 빌드 테스트
npm run build
```

### 4단계: 실행
```bash
# Backend 실행 (터미널 1)
cd backend
python app.py

# Frontend 실행 (터미널 2)
cd frontend
npm start
```

## 🌐 접속 확인

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/products

## 🔍 문제 해결

### Python 관련 오류
```bash
# Python 버전 확인
python --version

# pip 업그레이드
python -m pip install --upgrade pip

# 가상환경 사용 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Node.js 관련 오류
```bash
# Node.js 버전 확인
node --version
npm --version

# npm 캐시 클리어
npm cache clean --force

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install
```

### 포트 충돌 오류
```bash
# 포트 사용 확인
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Mac/Linux

# 다른 포트 사용
# Backend: app.py에서 port=5001로 변경
# Frontend: package.json에서 PORT=3001 설정
```

### 크롤링 오류
```bash
# 인터넷 연결 확인
ping google.com

# 방화벽/보안 프로그램 확인
# User-Agent 차단 가능성 확인
```

## 🐳 Docker 설치 (고급)

```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up --build

# 접속 주소
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

## 📱 모바일 테스트

```bash
# 로컬 네트워크에서 접속
# Windows: ipconfig
# Mac/Linux: ifconfig

# 예시: http://192.168.1.100:3000
```

## 🔐 보안 설정 (프로덕션)

```bash
# 환경변수 설정
cp .env.example .env
# .env 파일에서 비밀키 설정

# HTTPS 설정
# SSL 인증서 설치 필요
```

## 📞 지원

### 자주 묻는 질문
1. **Q**: Python이 인식되지 않아요
   **A**: PATH 환경변수에 Python이 추가되었는지 확인하세요

2. **Q**: npm install이 실패해요
   **A**: Node.js 버전을 16 이상으로 업그레이드하세요

3. **Q**: 크롤링이 안 돼요
   **A**: 인터넷 연결과 방화벽 설정을 확인하세요

### 문의 채널
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discord**: 실시간 지원 (해커톤 기간)
- **Email**: support@ssg-tracker.com

## 🎯 다음 단계

설치가 완료되면:
1. **README.md** - 프로젝트 전체 개요
2. **README_QUICK_START.md** - 사용법 가이드  
3. **TEAM_WORKFLOW.md** - 개발 참여 방법

---

**🎉 설치 완료 후 "아이폰"으로 검색해보세요!**