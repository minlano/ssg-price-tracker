@echo off
echo ========================================
echo 🚀 GitHub에 프로젝트 업로드
echo ========================================
echo.

echo 📋 GitHub 저장소 URL을 입력하세요:
echo 예시: https://github.com/your-username/ssg-price-tracker.git
set /p REPO_URL="GitHub 저장소 URL: "

if "%REPO_URL%"=="" (
    echo ❌ URL이 입력되지 않았습니다.
    pause
    exit /b 1
)

echo.
echo 🔗 GitHub 저장소와 연결 중...
git remote add origin %REPO_URL%

echo.
echo 📤 GitHub에 업로드 중...
git push -u origin main

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo 🎉 업로드 완료!
    echo ========================================
    echo.
    echo 🌐 저장소 주소: %REPO_URL%
    echo 📚 README: %REPO_URL%/blob/main/README.md
    echo 🚀 릴리즈: %REPO_URL%/releases
    echo.
    echo 👥 팀원들에게 다음 명령어로 클론하라고 알려주세요:
    echo git clone %REPO_URL%
    echo cd ssg-price-tracker
    echo setup.bat
    echo.
) else (
    echo.
    echo ❌ 업로드 실패
    echo 💡 GitHub 저장소가 올바르게 생성되었는지 확인하세요
    echo 💡 인터넷 연결을 확인하세요
    echo 💡 GitHub 로그인 상태를 확인하세요
)

pause