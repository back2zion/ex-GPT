#!/bin/bash

echo ""
echo "========================================"
echo "   ex-GPT CPU 테스트 모드 시작"
echo "========================================"
echo ""

echo "[1/3] Python 버전 확인..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Python3이 설치되지 않았습니다. Python 3.8 이상을 설치해주세요."
    exit 1
fi

echo ""
echo "[2/3] 필요한 패키지 설치..."
pip3 install flask flask-cors requests
if [ $? -ne 0 ]; then
    echo "패키지 설치에 실패했습니다."
    exit 1
fi

echo ""
echo "[3/3] ex-GPT 테스트 서버 시작..."
echo ""
echo "▶ 웹 브라우저에서 http://localhost:5001 을 열어주세요."
echo "▶ 서버를 종료하려면 Ctrl+C를 누르세요."
echo ""

python3 test_server.py
