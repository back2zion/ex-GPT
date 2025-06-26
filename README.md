# ex-GPT Demo

🤖 **Open Source RAG-powered AI Assistant**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![RAGFlow](https://img.shields.io/badge/RAG-RAGFlow-green.svg)](https://github.com/infiniflow/ragflow)

## 🎯 Overview

ex-GPT is a fully **open-source AI assistant** powered by RAGFlow, designed for document analysis, question answering, and intelligent conversation. This project demonstrates how to build a production-ready RAG system using only open-source components.

### ✨ Key Features

- 🔓 **100% Open Source**: No proprietary APIs or closed-source dependencies
- 🏠 **Self-Hosted**: Complete control over your data and models
- 🔄 **Dual RAG Support**: Choose between RAGFlow and DSRAG engines
- 🖥️ **Modern UI**: Clean, responsive interface optimized for all devices
- 📚 **Document Processing**: Support for PDF, DOCX, HWP, and more
- 🚀 **Easy Deployment**: One-click setup with Docker
- 💾 **CPU/GPU Support**: Works with or without GPU acceleration

## 🚀 Quick Start

### Option 1: CPU-Only Testing (No GPU Required)

Perfect for testing the UI and basic functionality:

```bash
# Windows
.\start_cpu_test.bat

# Linux/Mac
chmod +x start_cpu_test.sh
./start_cpu_test.sh
```

Then open: http://localhost:5001

### Option 2: Full Setup with RAGFlow

1. **Start RAGFlow**:
   ```bash
   # Windows
   .\start_ragflow.bat
   
   # Linux/Mac
   docker-compose -f docker-compose-ragflow.yaml up -d
   ```

2. **Configure RAGFlow**:
   - Open: http://localhost:8080
   - Create account and API key
   - Create a chat assistant

3. **Setup Environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your RAGFlow credentials
   ```

4. **Start ex-GPT**:
   ```bash
   python server.py
   ```

5. **Access**: http://localhost:5001

## 📋 System Requirements

### Minimum (CPU Testing)
- Python 3.8+
- 4GB RAM
- 2GB disk space

### Recommended (Full Setup)
- Python 3.8+
- 16GB RAM
- 20GB disk space
- GPU (optional, for better performance)

## 🛠️ Installation

### Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Or using Poetry
poetry install
```

### Docker Setup
```bash
# RAGFlow + Database
docker-compose -f docker-compose-ragflow.yaml up -d

# Optional: GPU-accelerated LLM
docker-compose -f docker-compose-gpu-alternatives.yaml up -d
```

## 📁 Project Structure

```
ex-gpt-demo/
├── 📄 README.md                    # This file
├── 🚀 Quick Start Scripts
│   ├── start_cpu_test.bat/.sh      # CPU-only testing
│   ├── start_ragflow.bat           # RAGFlow server
│   └── start_services.bat/.sh      # Full system startup
├── 🐍 Backend
│   ├── server.py                   # Main Flask server
│   ├── test_server.py              # CPU testing server
│   └── src/                        # Source modules
├── 🎨 Frontend
│   ├── index.html                  # Main UI
│   ├── css/style.css               # Styling
│   └── js/main.js                  # JavaScript
├── 🐳 Docker
│   ├── docker-compose-ragflow.yaml # RAGFlow setup
│   └── docker-compose-*.yaml       # Various configurations
├── 📚 Documentation
│   ├── OPENSOURCE_LLM_SETUP.md     # LLM setup guide
│   ├── RAGFLOW_INTEGRATION_GUIDE.md# RAGFlow guide
│   └── README_CPU_TEST.md          # CPU testing guide
└── 📋 Configuration
    ├── .env.template               # Environment template
    ├── requirements.txt            # Python dependencies
    └── pyproject.toml             # Poetry configuration
```

## 🔧 Configuration

### Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
# RAGFlow Configuration
RAGFLOW_HOST=http://localhost:8080
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_ASSISTANT_ID=your_assistant_id_here

# LLM Configuration (Optional)
VLLM_BASE_URL=http://localhost:8000
OLLAMA_BASE_URL=http://localhost:11434

# Server Configuration
FLASK_PORT=5001
FLASK_DEBUG=false
```

## 🎮 Usage

### Basic Chat
1. Open http://localhost:5001
2. Select RAG engine (RAGFlow/DSRAG)
3. Type your question
4. Get AI-powered responses

### Document Upload
1. Click upload button
2. Select PDF, DOCX, or HWP files
3. Wait for processing
4. Ask questions about the documents

### RAG Engine Selection
- **RAGFlow**: Full-featured, production-ready
- **DSRAG**: Lightweight alternative

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose files
2. **Memory issues**: Reduce model size or use CPU mode
3. **Docker problems**: Check Docker Desktop is running
4. **Package errors**: Use virtual environment

### Getting Help

- 📖 Check documentation in project folder
- 🐛 Report issues on GitHub
- 💡 See example configurations

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## � License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [RAGFlow](https://github.com/infiniflow/ragflow) - Open source RAG engine
- [vLLM](https://github.com/vllm-project/vllm) - High-performance LLM serving
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Qdrant](https://qdrant.tech/) - Vector database

## � Support

- 🌟 Star this repo if you find it helpful
- 🐛 Report bugs via GitHub Issues
- 💬 Join discussions in GitHub Discussions

---

**Made with ❤️ for the open source community**
