# mkit-idv-next

Voucher Management System with IDV Integration.

## Running the Project

### Option 1: Docker (Prod-like)

Requires Docker and Docker Compose.

1. Build and run:

    ```bash
    docker compose up --build
    ```

2. Open [http://localhost:9914](http://localhost:9914)

Notes:

- Includes `redis` and `orchestrator` services for transaction orchestration runtime.

### Option 2: Docker Development (Backend + Vite)

1. Build and run:

    ```bash
    docker compose -f docker-compose.dev.yml up --build
    ```

2. Open frontend dev server at [http://localhost:5173](http://localhost:5173)
3. API remains available at [http://localhost:9914](http://localhost:9914)
4. `redis` and `orchestrator` are started automatically in compose.

### Option 3: Manual Setup

**Frontend:**

1. Navigate to `frontend` directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Run dev server:

    ```bash
    npm run dev
    ```

**Backend:**

1. Navigate to root or `backend` directory.
2. Create/Activate Virtual Environment (Python 3.12+):

    ```bash
    # Windows
    backend\.venv\Scripts\Activate
    # Linux/Mac
    source backend/.venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -e backend
    ```

4. Run Server:

    ```bash
    uvicorn backend.app.main:app --port 9914 --reload
    ```

5. Open [http://localhost:9914](http://localhost:9914)

## Architecture

- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui
- **Backend**: FastAPI + SQLAlchemy (Async)
