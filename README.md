# LLM Chat Application

A modern, full-stack LLM chat application with multi-provider support, tool calling capabilities, and streaming responses.

## Features

- **Multi-Provider Support**: OpenAI, LlamaCpp (OpenAI-compatible API), and custom providers
- **Streaming Responses**: Real-time SSE (Server-Sent Events) streaming
- **Tool Calling**: Built-in web search and database query tools with security controls
- **Session Management**: Persistent chat sessions with configurable parameters
- **Modern Frontend**: React + TypeScript + TailwindCSS

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MyAgent
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Generate encryption key and update `.env`:
   ```bash
   python -c "import os; print(os.urandom(32).hex())"
   # Copy the output to ENCRYPTION_KEY in .env
   ```

4. Start all services:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

### Local Development

#### Backend Setup

1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export DATABASE_URL="postgresql+asyncpg://llmchat:llmchat_secret@localhost:5432/llmchat"
   export SECRET_KEY="your-secret-key"
   export ENCRYPTION_KEY="your-64-char-hex-encryption-key"
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

#### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set environment variables:
   ```bash
   export VITE_API_BASE_URL="http://localhost:8001"
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://llmchat:llmchat_secret@postgres:5432/llmchat` |
| `SECRET_KEY` | Application secret key for sessions | Required |
| `ENCRYPTION_KEY` | 64-char hex key for API key encryption | Required |
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000,http://localhost:5173` |
| `POSTGRES_USER` | PostgreSQL username | `llmchat` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `llmchat_secret` |
| `POSTGRES_DB` | PostgreSQL database name | `llmchat` |

### Provider Configuration

1. Navigate to Settings in the application
2. Add a new provider (OpenAI, LlamaCpp, or Custom)
3. Enter the API endpoint and API key
4. Test the connection
5. Set as default provider if desired

### Tool Configuration

Tools can be enabled per session:
- **Web Search**: Search the web using DuckDuckGo (30s timeout)
- **Database Query**: Read-only SQL queries with table whitelist (10s timeout, 100 row limit)

## API Endpoints

### Sessions

- `POST /api/sessions` - Create a new session
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session

### Messages

- `GET /api/sessions/{id}/messages` - Get session messages
- `POST /api/sessions/{id}/messages` - Add message

### Chat

- `POST /api/chat` - Send chat message (SSE streaming)

### Providers

- `GET /api/providers` - List providers
- `POST /api/providers` - Create provider
- `PUT /api/providers/{id}` - Update provider
- `DELETE /api/providers/{id}` - Delete provider
- `GET /api/providers/{id}/models` - List available models

### Configuration

- `GET /api/config` - Get global configuration
- `PUT /api/config` - Update global configuration

## Deployment

### Production Docker Compose

```yaml
version: '3.8'
services:
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_BASE_URL: https://api.yourdomain.com
    ports:
      - "80:80"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@postgres:5432/llm_chat
      SECRET_KEY: ${SECRET_KEY}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
      DEBUG: "false"
      CORS_ORIGINS: https://yourdomain.com
    ports:
      - "8001:8001"

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: llm_chat
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

### Kubernetes

Refer to `k8s/` directory for Kubernetes deployment manifests.

### Security Considerations

1. **Change default credentials**: Update `POSTGRES_PASSWORD` and `SECRET_KEY`
2. **Generate secure encryption key**: Use `python -c "import os; print(os.urandom(32).hex())"`
3. **Enable HTTPS**: Use reverse proxy (nginx, Traefik) with SSL certificates
4. **Restrict CORS**: Set `CORS_ORIGINS` to your actual domain
5. **API Keys**: Provider API keys are encrypted at rest using Fernet encryption

## Testing

### Backend Tests

```bash
cd backend
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │     │    Backend      │     │   PostgreSQL    │
│  React + Vite   │────▶│  FastAPI        │────▶│   Database      │
│  TypeScript     │     │  Python 3.11    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  LLM Providers  │
                        │  OpenAI/Custom  │
                        └─────────────────┘
```

## License

MIT License
