@echo off
echo ========================================
echo SSG 가격 추적 시스템 - 전체 시작
echo ========================================

echo Backend 서버 시작 중...
start "Backend Server" cmd /k "cd backend && pip install -r requirements.txt && python database.py && python app.py"

echo 3초 대기 후 Frontend 시작...
timeout /t 3 /nobreak > nul

echo Frontend 서버 시작 중...
start "Frontend Server" cmd /k "cd frontend && npm install && npm start"

echo.
echo ========================================
echo 서버 시작 완료!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo 브라우저에서 http://localhost:3000 을 열어주세요.
echo 종료하려면 각 창에서 Ctrl+C를 누르세요.
echo.

pause