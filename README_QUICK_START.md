# 🚀 SSG 가격 추적 시스템 - 빠른 시작 가이드

## 📋 사전 요구사항
- Python 3.7+ 설치
- Node.js 14+ 설치
- Git 설치 (선택사항)

## ⚡ 1분 만에 시작하기

### 방법 1: 자동 실행 스크립트 (Windows)
```bash
# 전체 시스템 시작 (Backend + Frontend)
start_all.bat

# 또는 개별 실행
start_backend.bat    # Backend만 실행
start_frontend.bat   # Frontend만 실행
```

### 방법 2: 빠른 테스트 스크립트
```bash
python quick_test.py
```

### 방법 3: 수동 실행
```bash
# 1. Backend 실행
cd backend
pip install -r requirements.txt
python database.py
python app.py

# 2. 새 터미널에서 Frontend 실행
cd frontend
npm install
npm start
```

## 🎯 실행 후 확인사항

### ✅ 서버 상태 확인
- Backend API: http://localhost:5000/api/products
- Frontend 웹: http://localhost:3000

### ✅ 기본 테스트 시나리오
1. **상품 추가**: 상품 관리 탭에서 SSG URL 입력
   ```
   예시 URL: https://www.ssg.com/item/itemView.ssg?itemId=1000000000001
   ```

2. **대시보드 확인**: 등록된 상품의 가격 차트 확인

3. **알림 설정**: 목표 가격 설정하여 이메일 알림 등록

## 🔧 문제 해결

### Backend 실행 오류
```bash
# Python 패키지 재설치
pip install --upgrade -r requirements.txt

# 데이터베이스 재초기화
python database.py
```

### Frontend 실행 오류
```bash
# Node 모듈 재설치
rm -rf node_modules package-lock.json
npm install

# 캐시 클리어
npm start -- --reset-cache
```

### 포트 충돌 오류
- Backend 포트 변경: `app.py`에서 `port=5000`로 수정
- Frontend 포트 변경: `package.json`에서 `"start": "PORT=3001 react-scripts start"`

## 📱 주요 기능 사용법

### 1. 상품 등록
- 상품 관리 탭 → SSG 상품 URL 입력 → 상품 추가

### 2. 가격 차트 보기
- 대시보드 탭 → 상품 선택 → 가격 변동 차트 확인

### 3. 알림 설정
- 알림 설정 탭 → 상품 선택 → 이메일 + 목표가격 입력

## 🎉 데모 데이터

시스템에는 테스트용 샘플 데이터가 포함되어 있습니다:
- 테스트 상품 1: 50,000원
- 테스트 상품 2: 75,000원
- 샘플 가격 이력 데이터

## 📞 지원

문제가 발생하면:
1. `quick_test.py` 실행하여 환경 확인
2. 브라우저 개발자 도구에서 네트워크 오류 확인
3. Backend 터미널에서 오류 로그 확인

---

**🎯 목표**: 9시간 해커톤에서 완전히 동작하는 가격 추적 시스템 구축!