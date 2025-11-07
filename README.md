# AI Agent Swagger Platform

A comprehensive platform for creating and managing AI agents from Swagger/OpenAPI specifications. This system automatically generates LLM-powered agents that can interact with your APIs through natural language.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Technology Stack](#technology-stack)
- [License](#license)

## 🎯 Overview

The AI Agent Swagger Platform bridges the gap between OpenAPI specifications and Large Language Models (LLMs). It automatically transforms your API documentation into intelligent agents that can understand natural language requests and execute API calls accordingly.

### Key Concepts

- **Swagger/OpenAPI Integration**: Upload your API specifications to automatically generate function definitions
- **AI Agent Generation**: Create LLM-powered agents that understand and interact with your APIs
- **Function Customization**: Enable/disable specific endpoints and add custom descriptions to help the LLM better understand your API
- **Multi-Provider Support**: Compatible with OpenAI, Anthropic, Mistral, and local LLMs via Ollama

## ✨ Features

### Core Functionality

- **Swagger Document Management**
  - Upload Swagger/OpenAPI files (JSON/YAML)
  - Automatic endpoint parsing and analysis
  - Version tracking and metadata management
  - Support for OpenAPI 2.0 and 3.0

- **AI Agent Creation**
  - Automatic system prompt generation from API documentation
  - Function calling definitions for LLM integration
  - Configurable LLM providers and models
  - Temperature and token limit controls

- **Endpoint Customization**
  - Enable/disable specific API functions per agent
  - Add custom descriptions to improve LLM understanding
  - Visual function editor with real-time preview
  - Batch save and regenerate functionality

- **User Management**
  - Secure JWT-based authentication
  - User-specific API key management (OpenAI, Anthropic)
  - Role-based access control
  - Refresh token support (30-min access, 7-day refresh)

### Advanced Features

- **Agent Regeneration**: Update agents when Swagger specs or customizations change
- **Real-time Function Filtering**: Only enabled functions are available to the LLM
- **Custom Descriptions**: Override default API descriptions with LLM-optimized explanations
- **Multi-Agent Support**: Create multiple agents from the same API with different configurations

## 🏗️ Architecture

The platform follows a modern microservices architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  - Dashboard UI                                             │
│  - Agent Manager                                            │
│  - Function Editor                                          │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (Routers)                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │           Business Logic (Services)                  │   │
│  │  - Swagger Parser                                    │   │
│  │  - Agent Generator                                   │   │ 
│  │  - LLM Integration                                   │   │
│  └──────────────────┬───────────────────────────────────┘   │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │         Data Layer (SQLAlchemy ORM)                  │   │
│  └──────────────────┬───────────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                PostgreSQL Database                          │
│  - Users & Authentication                                   │
│  - Swagger Documents                                        │
│  - Agents & Functions                                       │
│  - Endpoint Customizations                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User uploads Swagger file** → Backend parses and stores in DB
2. **User creates agent** → System generates system prompt and function definitions
3. **User customizes functions** → Modifications stored per Swagger document
4. **User regenerates agent** → Functions filtered by `is_enabled`, custom descriptions applied
5. **LLM receives only enabled functions** with optimized descriptions

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.11+ (for local development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TomSft15/ai-agent-swagger.git
cd AI_Agent_Swagger
```

2. **Configure environment variables**

Backend `.env`:
```bash
cd Backend
cp .env.example .env
# Edit .env with your configuration:
# - DATABASE_URL
# - SECRET_KEY
# - OPENAI_API_KEY (optional)
# - ANTHROPIC_API_KEY (optional)
```

3. **Start with Docker Compose**
```bash
cd Backend
docker compose up -d
```

4. **Access the application**
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/v1/docs

### First Steps

1. **Login** with default credentials:
   - Email: `admin@example.com`
   - Password: Check `Backend/.env` for `SUPERADMIN_PWD`

2. **Add your LLM API keys** in Manage Keys page

3. **Upload a Swagger file** from your API

4. **Create an agent** by selecting the uploaded Swagger document

5. **Customize functions** (optional):
   - View the Swagger document
   - Enable/disable specific endpoints
   - Add custom descriptions for better LLM understanding
   - Click "Save & Regenerate Agents"

6. **Start chatting** with your agent!

## 📁 Project Structure

```
AI_Agent_Swagger/
├── Backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints/routers
│   │   │   └── endpoints/  # Route handlers
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   │       ├── agent_generator.py
│   │       ├── agent_service.py
│   │       ├── swagger_parser.py
│   │       └── llm_service.py
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── requirements.txt
│   └── README.md           # Backend documentation
│
├── Frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   │   └── FunctionEditor.jsx
│   │   ├── pages/         # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AgentManager.jsx
│   │   │   ├── AgentEdit.jsx
│   │   │   ├── SwaggerView.jsx
│   │   │   └── ManageKeys.jsx
│   │   ├── services/      # API service layer
│   │   │   └── api.js
│   │   └── App.jsx        # Main application component
│   ├── package.json
│   └── README.md          # Frontend documentation
│
└── README.md              # This file
```

## 📚 Documentation

Detailed documentation is available for each component:

- **[Backend Documentation](./Backend/README.md)**: API endpoints, database schema, services
- **[Frontend Documentation](./Frontend/README.md)**: Components, state management, routing

### API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with refresh tokens
- **API Parsing**: PyYAML, JSON
- **LLM Integration**: OpenAI, Anthropic, Ollama

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Fetch API with auto-refresh
- **Icons**: Lucide React
- **Styling**: CSS Modules

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Database**: PostgreSQL with Alpine

## 🔐 Security Features

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- API key encryption in database
- CORS configuration
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

## 🧪 Development

### Backend Development

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

### Frontend Development

```bash
cd Frontend
npm install
npm run dev
```

### Database Initialization

```bash
cd Backend
python -m app.db.init_db
```

This will:
- Create all database tables
- Run necessary migrations
- Create a default superuser

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change ports in `docker-compose.yaml`
   - Default: Backend (5000), Frontend (5173), PostgreSQL (5432)

2. **Database connection failed**
   - Ensure PostgreSQL container is running: `docker compose ps`
   - Check `DATABASE_URL` in `.env`
   - Verify PostgreSQL is healthy: `docker compose logs db`

3. **LLM API errors**
   - Verify API keys in Manage Keys page
   - Check LLM provider status
   - Review token limits and quotas

4. **Frontend cannot reach backend**
   - Check CORS settings in `Backend/app/core/config.py`
   - Verify `VITE_API_URL` in Frontend `.env`

5. **Token refresh issues**
   - Clear browser localStorage
   - Re-login to get new tokens
   - Check token expiration settings in backend `.env`

## 📖 Key Features Explained

### Function Customization Workflow

1. Upload a Swagger document
2. Navigate to the Swagger view page
3. Use the Function Editor to:
   - Toggle functions on/off (disabled functions won't be available to LLM)
   - Edit descriptions to make them more LLM-friendly
   - Changes are kept in local state (not saved yet)
4. Click "Save & Regenerate Agents" to:
   - Save all customizations to database
   - Automatically regenerate all agents using this Swagger
   - Apply the new function list and descriptions

### Agent Regeneration

When you regenerate an agent:
- The system fetches the latest Swagger document
- Filters endpoints based on `is_enabled` flag
- Applies custom descriptions where available
- Generates new system prompt and function definitions
- Updates the agent in the database

This ensures agents always reflect the current state of customizations.

## 🔄 Workflow Example

```
1. Upload Petstore Swagger (30 endpoints)
   ↓
2. Create "Customer Support Agent"
   ↓
3. Customize functions:
   - Disable: deletePet, updatePet (read-only agent)
   - Custom description for getPets: "Use this to show available pets to customers"
   ↓
4. Save & Regenerate
   ↓
5. Agent now has only 28 functions with optimized descriptions
   ↓
6. LLM can only call enabled functions
```

## 📝 License

This project is licensed under the MIT License.

## 📧 Support

For questions and support, please open an issue on GitHub.

---

**Made with ❤️ using FastAPI and React**
