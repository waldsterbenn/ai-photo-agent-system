# Agent Management System

This repository contains a multi-service application built using Docker Compose. It includes three main components:

- **Backend**: A Flask API service that provides a REST API and communicates with the AI Agents service. See [`backend/app.py`](c:\src\agent-container-sandbox\agent-management-system\backend\app.py).
- **AI Agents**: A Flask API service that handles task execution. See [`ai_agents/app.py`](c:\src\agent-container-sandbox\agent-management-system\ai_agents\app.py) and [`ai_agents/agent_manager.py`](c:\src\agent-container-sandbox\agent-management-system\ai_agents\agent_manager.py).
- **Frontend**: A Vue 3 application built with Vite that interacts with the backend API. See [`frontend/src/App.vue`](c:\src\agent-container-sandbox\agent-management-system\frontend\src\App.vue) and [`frontend/src/config/backend_conf.ts`](c:\src\agent-container-sandbox\agent-management-system\frontend\src\config\backend_conf.ts).

## Project Structure

```
agent-management-system/
├── docker-compose.yml
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── ai_agents/
│   ├── app.py
│   ├── agent_manager.py
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── Dockerfile
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.vue
        ├── main.ts
        ├── components/
        │   └── Main.vue
        ├── config/
        │   └── backend_conf.ts
        └── router/
            └── index.ts
```

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose must be installed on your system.

### Running the Application

1. **Build and Start Containers**

   From the project root, run:

   ```sh
   docker-compose up --build
   ```
