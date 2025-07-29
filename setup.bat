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
    npm install
    if %errorLevel% == 0 (
        echo ✅ Frontend 패키지 설치 완료
    ) else (
        echo ❌ Frontend 패키지 설치 실패
        pause
        exit /b 1
    )
) else (
    echo ❌ package.json 파일을 찾을 수 없습니다.
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