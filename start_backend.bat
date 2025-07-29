@echo off
echo ========================================
echo SSG 가격 추적 시스템 - Backend 시작
echo ========================================

cd backend

echo Python 패키지 설치 중...
pip install -r requirements.txt

echo.
echo 데이터베이스 초기화 중...
python database.py

echo.
echo Flask 서버 시작 중...
echo Backend 서버: http://localhost:5000
echo.
python app.py

pause