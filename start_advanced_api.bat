@echo off
echo ========================================
echo Flask API 고도화 서버 시작
echo ========================================

cd backend

echo 데이터베이스 초기화 중...
python database.py

echo.
echo API 서버 시작 중...
echo 서버 주소: http://localhost:5001
echo.
echo 사용 가능한 API:
echo - 고급 검색: /api/search/advanced
echo - 상품 비교: /api/compare/products  
echo - 데이터 분석: /api/data/analytics
echo - 11번가 검색: /api/11st/search
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo ========================================

cd api
python main.py

pause