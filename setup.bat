@echo off
chcp 65001 > nul
echo.
echo ========================================
echo 🚀 SSG 가격 추적 시스템 - 자동 설치
echo ========================================
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 관리자 권한으로 실행 중
) else (
    echo ⚠️  관리자 권한이 필요합니다. 우클릭 후 "관리자 권한으로 실행"을 선택해주세요.
    pause
    exit /b 1
)

echo.
echo 📋 시스템 요구사항 확인 중...

:: Python 설치 확인
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python 설치됨
    python --version
) else (
    echo ❌ Python이 설치되지 않았습니다.
    echo 📥 Python 3.8+ 설치가 필요합니다: https://python.org/downloads
    pause
    exit /b 1
)

:: Node.js 설치 확인
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Node.js 설치됨
    node --version
) else (
    echo ❌ Node.js가 설치되지 않았습니다.
    echo 📥 Node.js 16+ 설치가 필요합니다: https://nodejs.org
    pause
    exit /b 1
)

:: npm 설치 확인
npm --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ npm 설치됨
    npm --version
) else (
    echo ❌ npm이 설치되지 않았습니다.
    pause
    exit /b 1
)

echo.
echo 🔧 프로젝트 설정 시작...

:: Backend 설정
echo.
echo 📦 Backend 패키지 설치 중...
cd backend
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo ✅ Backend 패키지 설치 완료
    ) else (
        echo ❌ Backend 패키지 설치 실패
        pause
        exit /b 1
    )
) else (
    echo ❌ requirements.txt 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

:: 데이터베이스 초기화
echo.
echo 🗄️ 데이터베이스 초기화 중...
python database.py
if %errorLevel% == 0 (
    echo ✅ 데이터베이스 초기화 완료
) else (
    echo ❌ 데이터베이스 초기화 실패
    pause
    exit /b 1
)

:: Frontend 설정
echo.
echo 📦 Frontend 패키지 설치 중...
cd ..\frontend
if exist package.json (
    echo ✅ package.json 파일 발견
) else (
    echo 📝 package.json 파일이 없습니다. React 앱용으로 생성 중...
    (
        echo {
        echo   "name": "ssg-price-tracker-frontend",
        echo   "version": "1.0.0",
        echo   "description": "SSG 가격 추적 시스템 프론트엔드",
        echo   "private": true,
        echo   "dependencies": {
        echo     "@testing-library/jest-dom": "^5.16.4",
        echo     "@testing-library/react": "^13.3.0",
        echo     "@testing-library/user-event": "^13.5.0",
        echo     "react": "^18.2.0",
        echo     "react-dom": "^18.2.0",
        echo     "react-scripts": "5.0.1",
        echo     "web-vitals": "^2.1.4",
        echo     "axios": "^1.4.0",
        echo     "react-router-dom": "^6.3.0"
        echo   },
        echo   "scripts": {
        echo     "start": "react-scripts start",
        echo     "build": "react-scripts build",
        echo     "test": "react-scripts test",
        echo     "eject": "react-scripts eject"
        echo   },
        echo   "eslintConfig": {
        echo     "extends": [
        echo       "react-app",
        echo       "react-app/jest"
        echo     ]
        echo   },
        echo   "browserslist": {
        echo     "production": [
        echo       "^>0.2%%",
        echo       "not dead",
        echo       "not op_mini all"
        echo     ],
        echo     "development": [
        echo       "last 1 chrome version",
        echo       "last 1 firefox version",
        echo       "last 1 safari version"
        echo     ]
        echo   },
        echo   "proxy": "http://localhost:5000"
        echo }
    ) > package.json
    echo ✅ package.json 파일 생성 완료
)

:: React 앱 기본 파일들 생성
echo 📁 React 앱 기본 구조 생성 중...

:: public 폴더 및 index.html 생성
if not exist public mkdir public
if not exist public\index.html (
    (
        echo ^<!DOCTYPE html^>
        echo ^<html lang="ko"^>
        echo   ^<head^>
        echo     ^<meta charset="utf-8" /^>
        echo     ^<link rel="icon" href="%%PUBLIC_URL%%/favicon.ico" /^>
        echo     ^<meta name="viewport" content="width=device-width, initial-scale=1" /^>
        echo     ^<meta name="theme-color" content="#000000" /^>
        echo     ^<meta
        echo       name="description"
        echo       content="SSG 가격 추적 시스템"
        echo     /^>
        echo     ^<title^>SSG 가격 추적 시스템^</title^>
        echo   ^</head^>
        echo   ^<body^>
        echo     ^<noscript^>JavaScript를 활성화해야 이 앱을 실행할 수 있습니다.^</noscript^>
        echo     ^<div id="root"^>^</div^>
        echo   ^</body^>
        echo ^</html^>
    ) > public\index.html
    echo ✅ public/index.html 생성 완료
)

:: src 폴더 및 기본 파일들 생성
if not exist src mkdir src
if not exist src\index.js (
    (
        echo import React from 'react';
        echo import ReactDOM from 'react-dom/client';
        echo import './index.css';
        echo import App from './App';
        echo.
        echo const root = ReactDOM.createRoot^(document.getElementById^('root'^)^);
        echo root.render^(
        echo   ^<React.StrictMode^>
        echo     ^<App /^>
        echo   ^</React.StrictMode^>
        echo ^);
    ) > src\index.js
    echo ✅ src/index.js 생성 완료
)

if not exist src\App.js (
    (
        echo import React from 'react';
        echo import './App.css';
        echo.
        echo function App^(^) {
        echo   return ^(
        echo     ^<div className="App"^>
        echo       ^<header className="App-header"^>
        echo         ^<h1^>🛒 SSG 가격 추적 시스템^</h1^>
        echo         ^<p^>
        echo           SSG.COM 상품 가격을 추적하고 알림을 받아보세요!
        echo         ^</p^>
        echo         ^<div className="App-content"^>
        echo           ^<p^>시스템이 성공적으로 실행되었습니다.^</p^>
        echo           ^<p^>백엔드 연결 상태를 확인 중...^</p^>
        echo         ^</div^>
        echo       ^</header^>
        echo     ^</div^>
        echo   ^);
        echo }
        echo.
        echo export default App;
    ) > src\App.js
    echo ✅ src/App.js 생성 완료
)

if not exist src\index.css (
    (
        echo body {
        echo   margin: 0;
        echo   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
        echo     'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
        echo     sans-serif;
        echo   -webkit-font-smoothing: antialiased;
        echo   -moz-osx-font-smoothing: grayscale;
        echo }
        echo.
        echo code {
        echo   font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
        echo     monospace;
        echo }
    ) > src\index.css
    echo ✅ src/index.css 생성 완료
)

if not exist src\App.css (
    (
        echo .App {
        echo   text-align: center;
        echo }
        echo.
        echo .App-header {
        echo   background-color: #282c34;
        echo   padding: 20px;
        echo   color: white;
        echo   min-height: 100vh;
        echo   display: flex;
        echo   flex-direction: column;
        echo   align-items: center;
        echo   justify-content: center;
        echo   font-size: calc^(10px + 2vmin^);
        echo }
        echo.
        echo .App-content {
        echo   margin-top: 20px;
        echo   font-size: 18px;
        echo }
        echo.
        echo .App-content p {
        echo   margin: 10px 0;
        echo }
    ) > src\App.css
    echo ✅ src/App.css 생성 완료
)

npm install
if %errorLevel% == 0 (
    echo ✅ Frontend 패키지 설치 완료
) else (
    echo ❌ Frontend 패키지 설치 실패
    pause
    exit /b 1
)

cd ..

:: 크롤러 테스트
echo.
echo 🕷️ 크롤러 기능 테스트 중...
cd backend
python -c "from crawler import search_ssg_products; print('크롤러 테스트:', len(search_ssg_products('테스트', limit=1)) > 0)"
if %errorLevel% == 0 (
    echo ✅ 크롤러 테스트 통과
) else (
    echo ⚠️ 크롤러 테스트 실패 (인터넷 연결 확인 필요)
)

cd ..

:: 설치 완료
echo.
echo ========================================
echo 🎉 설치 완료!
echo ========================================
echo.
echo 📍 실행 방법:
echo   1. 전체 시스템 시작: start_all.bat
echo   2. Backend만 시작:   start_backend.bat  
echo   3. Frontend만 시작:  start_frontend.bat
echo.
echo 🌐 접속 주소:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:5000
echo.
echo 📚 문서:
echo   README.md - 프로젝트 개요
echo   README_QUICK_START.md - 빠른 시작 가이드
echo   TEAM_WORKFLOW.md - 팀 협업 가이드
echo.

:: 자동 실행 여부 확인
set /p choice="지금 바로 시스템을 시작하시겠습니까? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 시스템 시작 중...
    start_all.bat
) else (
    echo.
    echo 👋 설치가 완료되었습니다. 언제든지 start_all.bat을 실행하세요!
)

pause