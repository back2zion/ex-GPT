const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// Ollama 연동 (실제 구현시)
async function callOllama(prompt) {
    // 실제로는 axios로 Ollama API 호출
    return "AI 응답 예시: " + prompt;
}

// API 엔드포인트
app.post('/api/search', async (req, res) => {
    const { query } = req.body;
    
    // 데모용 응답
    const responses = {
        "터널": "터널 안전 관리 지침에 따르면, 2025년부터 IoT 센서 설치가 의무화되었습니다.",
        "점검": "정기 점검 주기가 6개월에서 3개월로 단축되었습니다.",
        default: "한국도로공사 규정에 따른 답변입니다."
    };
    
    const answer = responses[query] || responses.default;
    res.json({ answer });
});

app.post('/api/chat', async (req, res) => {
    const { message } = req.body;
    res.json({ response: `"${message}"에 대한 AI 답변입니다.` });
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`서버가 포트 ${PORT}에서 실행 중입니다.`);
});