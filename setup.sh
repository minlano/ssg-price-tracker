#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "🚀 SSG 가격 추적 시스템 - 자동 설치"
echo "========================================"
echo -e "${NC}"

# 함수 정의
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 설치됨${NC}"
        $1 --version
        return 0
    else
        echo -e "${RED}❌ $1이 설치되지 않았습니다.${NC}"
        return 1
    fi
}

install_python_packages() {
    echo -e "${YELLOW}📦 Backend 패키지 설치 중...${NC}"
    cd backend
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Backend 패키지 설치 완료${NC}"
        else
            echo -e "${RED}❌ Backend 패키지 설치 실패${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다.${NC}"
        exit 1
    fi
    cd ..
}

install_node_packages() {
    echo -e "${YELLOW}📦 Frontend 패키지 설치 중...${NC}"
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Frontend 패키지 설치 완료${NC}"
        else
            echo -e "${RED}❌ Frontend 패키지 설치 실패${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ package.json 파일을 찾을 수 없습니다.${NC}"
        exit 1
    fi
    cd ..
}

# 시스템 요구사항 확인
echo -e "${YELLOW}📋 시스템 요구사항 확인 중...${NC}"

# Python 확인
if ! check_command python3; then
    if ! check_command python; then
        echo -e "${RED}📥 Python 3.8+ 설치가 필요합니다: https://python.org/downloads${NC}"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Node.js 확인
if ! check_command node; then
    echo -e "${RED}📥 Node.js 16+ 설치가 필요합니다: https://nodejs.org${NC}"
    exit 1
fi

# npm 확인
if ! check_command npm; then
    echo -e "${RED}❌ npm이 설치되지 않았습니다.${NC}"
    exit 1
fi

# 프로젝트 설정 시작
echo -e "${BLUE}🔧 프로젝트 설정 시작...${NC}"

# Backend 패키지 설치
install_python_packages

# 데이터베이스 초기화
echo -e "${YELLOW}🗄️ 데이터베이스 초기화 중...${NC}"
cd backend
$PYTHON_CMD database.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
else
    echo -e "${RED}❌ 데이터베이스 초기화 실패${NC}"
    exit 1
fi
cd ..

# Frontend 패키지 설치
install_node_packages

# 크롤러 테스트
echo -e "${YELLOW}🕷️ 크롤러 기능 테스트 중...${NC}"
cd backend
$PYTHON_CMD -c "from crawler import search_ssg_products; print('크롤러 테스트:', len(search_ssg_products('테스트', limit=1)) > 0)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 크롤러 테스트 통과${NC}"
else
    echo -e "${YELLOW}⚠️ 크롤러 테스트 실패 (인터넷 연결 확인 필요)${NC}"
fi
cd ..

# 실행 스크립트 권한 부여
chmod +x *.sh 2>/dev/null

# 설치 완료
echo -e "${GREEN}"
echo "========================================"
echo "🎉 설치 완료!"
echo "========================================"
echo -e "${NC}"

echo -e "${BLUE}📍 실행 방법:${NC}"
echo "  1. Backend 시작:  cd backend && python3 app.py"
echo "  2. Frontend 시작: cd frontend && npm start"
echo ""
echo -e "${BLUE}🌐 접속 주소:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:5000"
echo ""
echo -e "${BLUE}📚 문서:${NC}"
echo "  README.md - 프로젝트 개요"
echo "  README_QUICK_START.md - 빠른 시작 가이드"
echo "  TEAM_WORKFLOW.md - 팀 협업 가이드"
echo ""

# 자동 실행 여부 확인
read -p "지금 바로 Backend 서버를 시작하시겠습니까? (y/n): " choice
case "$choice" in 
  y|Y ) 
    echo -e "${GREEN}🚀 Backend 서버 시작 중...${NC}"
    cd backend
    $PYTHON_CMD app.py &
    echo -e "${YELLOW}Frontend는 새 터미널에서 'cd frontend && npm start'를 실행하세요.${NC}"
    ;;
  * ) 
    echo -e "${GREEN}👋 설치가 완료되었습니다!${NC}"
    ;;
esac