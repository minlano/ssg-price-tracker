# 🚀 SSG 가격 추적 시스템 - 팀 협업 가이드

## 👥 팀원별 담당 파일 영역

### 🔹 팀원 A (Backend API) - feature/api
**전담 파일 (충돌 없음)**
```
backend/
├── api/
│   ├── advanced_search.py     # 새로 생성
│   ├── product_compare.py     # 새로 생성
│   ├── price_prediction.py    # 새로 생성
│   └── bulk_alerts.py         # 새로 생성
├── utils/
│   ├── validators.py          # 새로 생성
│   └── cache.py              # 새로 생성
└── tests/
    └── test_api.py           # 새로 생성
```

**공유 파일 (주의 필요)**
- `backend/app.py` - 새 라우트 추가만
- `backend/requirements.txt` - 패키지 추가

### 🔹 팀원 B (Frontend) - feature/frontend  
**전담 파일 (충돌 없음)**
```
frontend/src/
├── components/
│   ├── AdvancedSearch.js      # 새로 생성
│   ├── ProductCompare.js      # 새로 생성
│   ├── AlertDashboard.js      # 새로 생성
│   └── MobileLayout.js        # 새로 생성
├── hooks/
│   ├── useAdvancedSearch.js   # 새로 생성
│   └── useProductCompare.js   # 새로 생성
├── styles/
│   ├── advanced-search.css    # 새로 생성
│   └── mobile.css            # 새로 생성
└── utils/
    └── formatters.js         # 새로 생성
```

**공유 파일 (주의 필요)**
- `frontend/src/App.js` - 새 컴포넌트 추가만
- `frontend/package.json` - 패키지 추가

### 🔹 팀원 C (크롤링/알림) - feature/crawler
**전담 파일 (충돌 없음)**
```
backend/
├── crawlers/
│   ├── coupang_crawler.py     # 새로 생성
│   ├── gmarket_crawler.py     # 새로 생성
│   └── multi_site_manager.py  # 새로 생성
├── notifications/
│   ├── slack_notifier.py      # 새로 생성
│   ├── kakao_notifier.py      # 새로 생성
│   └── smart_alerts.py        # 새로 생성
└── tests/
    └── test_crawlers.py       # 새로 생성
```

**공유 파일 (주의 필요)**
- `backend/crawler.py` - 기존 함수 개선만
- `backend/notification.py` - 새 함수 추가만

### 🔹 팀원 D (DevOps/통합) - feature/integration
**전담 파일 (충돌 없음)**
```
프로젝트 루트/
├── docker/
│   ├── Dockerfile.backend     # 새로 생성
│   ├── Dockerfile.frontend    # 새로 생성
│   └── docker-compose.yml     # 새로 생성
├── .github/
│   └── workflows/
│       └── deploy.yml         # 새로 생성
├── monitoring/
│   ├── prometheus.yml         # 새로 생성
│   └── grafana-dashboard.json # 새로 생성
└── scripts/
    ├── setup.sh              # 새로 생성
    └── deploy.sh             # 새로 생성
```

**공유 파일 (주의 필요)**
- `backend/database.py` - PostgreSQL 마이그레이션
- `.gitignore` - 새 항목 추가

## 🔄 안전한 협업 워크플로우

### 1단계: 브랜치 생성 및 초기 설정
```bash
# 메인 브랜치에서 최신 코드 받기
git checkout main
git pull origin main

# 각자 브랜치 생성
git checkout -b feature/api          # 팀원 A
git checkout -b feature/frontend     # 팀원 B
git checkout -b feature/crawler      # 팀원 C
git checkout -b feature/integration  # 팀원 D

# 초기 폴더 구조 생성 (충돌 방지)
mkdir -p backend/api backend/utils backend/tests     # 팀원 A
mkdir -p frontend/src/components/advanced            # 팀원 B
mkdir -p backend/crawlers backend/notifications      # 팀원 C
mkdir -p docker .github/workflows monitoring         # 팀원 D
```

### 2단계: 개발 중 동기화 (1시간마다)
```bash
# 다른 팀원 변경사항 가져오기
git checkout main
git pull origin main
git checkout feature/your-branch
git rebase main  # 또는 git merge main

# 충돌 발생 시 해결 후
git add .
git rebase --continue
```

### 3단계: 공유 파일 수정 시 소통
```bash
# 공유 파일 수정 전 팀원들에게 알림
# Slack/Discord: "app.py 수정 시작합니다 (라우트 추가)"

# 수정 완료 후 즉시 푸시
git add backend/app.py
git commit -m "feat: add advanced search route"
git push origin feature/api

# 팀원들에게 알림
# "app.py 수정 완료, 충돌 방지를 위해 rebase 해주세요"
```

## 🚨 충돌 방지 규칙

### Rule 1: 공유 파일 수정 시 사전 공지
```
공유 파일: app.py, package.json, requirements.txt, database.py
→ 수정 전 팀원들에게 알림 필수!
```

### Rule 2: 작은 단위로 자주 커밋
```bash
# ❌ 나쁜 예: 4시간 작업 후 한 번에 커밋
git commit -m "feat: add all advanced features"

# ✅ 좋은 예: 30분마다 작은 단위 커밋
git commit -m "feat: add price range filter API"
git commit -m "feat: add brand filter validation"
git commit -m "feat: add advanced search tests"
```

### Rule 3: 함수/클래스 단위로 분리
```python
# ❌ 나쁜 예: 기존 함수 수정
def search_ssg_products(keyword):
    # 기존 코드 대폭 수정
    
# ✅ 좋은 예: 새 함수 추가
def advanced_search_products(filters):
    # 새로운 기능은 새 함수로
    return search_ssg_products(filters.keyword)
```

## 🔧 병합 전 체크리스트

### 각 팀원이 병합 전 확인사항
```bash
# 1. 최신 main 브랜치와 동기화
git checkout main && git pull origin main
git checkout feature/your-branch && git rebase main

# 2. 테스트 실행
npm test                    # Frontend
python -m pytest          # Backend
python crawler.py          # 크롤러 테스트

# 3. 린트 검사
npm run lint               # Frontend
flake8 backend/           # Backend

# 4. 빌드 테스트
npm run build             # Frontend
python -m py_compile backend/*.py  # Backend
```

### 통합 담당자 (팀원 D)의 병합 순서
```bash
# 1. 안전한 순서로 병합
git merge feature/integration  # 인프라 먼저
git merge feature/api         # API 두 번째  
git merge feature/crawler     # 크롤러 세 번째
git merge feature/frontend    # Frontend 마지막

# 2. 각 병합 후 테스트
npm start & python app.py     # 서버 실행 테스트
curl localhost:5000/api/search?keyword=test  # API 테스트
```

## 🆘 충돌 발생 시 해결 방법

### 1. 파일 충돌 해결
```bash
# 충돌 발생 시
git status  # 충돌 파일 확인

# 충돌 파일 열어서 수동 해결
# <<<<<<< HEAD
# 내 변경사항
# =======  
# 다른 사람 변경사항
# >>>>>>> feature/other-branch

# 해결 후
git add 충돌파일.py
git commit -m "resolve: merge conflict in 충돌파일.py"
```

### 2. 패키지 의존성 충돌
```bash
# requirements.txt 충돌 시
# 1. 두 버전 모두 설치 테스트
pip install package1 package2

# 2. 호환성 확인 후 병합
# 3. 전체 팀원에게 새 패키지 설치 안내
```

## 📞 실시간 소통 채널

### Slack/Discord 채널 구성
```
#general - 전체 공지
#git-updates - Git 푸시/병합 알림  
#api-team - 팀원 A 전용
#frontend-team - 팀원 B 전용
#crawler-team - 팀원 C 전용
#devops-team - 팀원 D 전용
```

### 중요 알림 템플릿
```
🚨 공유 파일 수정 시작
파일: backend/app.py
작업자: 팀원 A
예상 시간: 30분
내용: 고급 검색 API 라우트 추가

✅ 공유 파일 수정 완료  
파일: backend/app.py
변경사항: /api/advanced-search 라우트 추가
다음 작업자: 충돌 방지를 위해 rebase 해주세요
```

이렇게 하면 4명이 동시에 작업해도 충돌 없이 안전하게 병합할 수 있어요! 🎉