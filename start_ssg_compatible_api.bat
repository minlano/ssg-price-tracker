@echo off
echo ========================================
echo SSG 호환 11번가 API 서버 시작
echo ========================================

cd backend

echo 데이터베이스 초기화 중...
python database.py

echo.
echo SSG 호환 API 서버 시작 중...
echo 서버 주소: http://localhost:5000
echo.
echo 🚀 11번가 실제 API와 연동된 SSG 호환 서버
echo.
echo 사용 가능한 API (SSG 호환):
echo - 상품 검색: /api/search?keyword=스마트폰
echo - 상품 목록: /api/products
echo - 대시보드: /api/dashboard
echo - 가격 비교: /api/compare?keyword=노트북
echo - 알림 설정: /api/alerts
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo ========================================

cd api
python main.py

pause