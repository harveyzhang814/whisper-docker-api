# Whisper Translation Server

A real-time speech-to-text service using OpenAI's Whisper model, optimized for Apple Silicon (ARM64) and containerized with Docker.

## Features

- 🎙️ Real-time audio transcription using OpenAI Whisper
- 🐳 Containerized deployment with Docker
- 🚀 FastAPI server with streaming support
- 🔌 Easy integration with input methods
- 💻 Optimized for Apple Silicon (M-series) processors
- 🌐 RESTful API for audio transcription
- 📱 Real-time microphone input support
- 🔧 Configurable audio settings

## System Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Docker Desktop for Apple Silicon
- Python 3.10 or higher
- ffmpeg (installed automatically in Docker)

## Project Structure

```
whisper-translation/
├── docker_api/                # All Docker API related files and configs
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env.docker.example   # Docker API environment variable template
│   ├── .env.docker.local     # Docker API environment variable for deployment
│   └── src/                  # API server source code (entry: app.py)
├── config/                   # Shared config files
├── docs/
├── sample/
├── src/                      # Client and other backend code
├── tests/
├── .env.local                # Global env (not used by Docker API)
├── .env.example
└── ...
```

## Quick Start (Docker API)

### 1. 配置环境变量

在 `docker_api/` 目录下，复制并编辑环境变量文件：
```bash
cp docker_api/.env.docker.example docker_api/.env.docker.local
# 按需修改 docker_api/.env.docker.local
```

### 2. 构建并部署 API 服务

在项目根目录下运行：
```bash
docker-compose -f docker_api/docker-compose.yml up --build -d
```
- 推荐只用 compose 管理服务，无需手动 docker build。
- 镜像和服务会自动构建并启动。

### 3. 查看服务日志
```bash
docker-compose -f docker_api/docker-compose.yml logs -f
```

### 4. 测试 API
```bash
curl http://localhost:8090/health
```
应返回：
```json
{"status": "healthy", "model": "base"}
```

## 环境变量管理说明
- Docker API 服务环境变量独立于主项目，全部在 `docker_api/.env.docker.local` 和 `.env.docker.example` 中维护。
- 不再使用根目录下的 `.env.local` 或 `.env.example` 进行 Docker API 配置。

## 其他说明
- 如需修改 API 代码，请在 `docker_api/src/` 下编辑。
- 如需自定义 Dockerfile 或 compose 配置，请在 `docker_api/` 下操作。
- 停止服务：
  ```bash
  docker-compose -f docker_api/docker-compose.yml down
  ```

## 旧版/客户端开发
- 客户端和其他后端代码仍在 `src/` 目录下，环境变量管理不变。

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Docker](https://www.docker.com/) 