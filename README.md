# mkit-idv-next

Voucher Management System with IDV Integration.

## Running the Project

### Option 1: Docker (Recommended)

Requires Docker and Docker Compose.

1. Build and run:

    ```bash
    docker-compose up --build
    ```

2. Open [http://localhost:9914](http://localhost:9914)

### Option 2: Manual Setup

**Frontend:**

1. Navigate to `frontend` directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Build CSS (Watch mode for development):

    ```bash
    npm run build
    # OR for watch mode:
    npm run watch
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

- **Frontend**: HTML/JS + TailwindCSS (Served by FastAPI)
- **Backend**: FastAPI + SQLAlchemy (Async)
