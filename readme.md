# Data Pusher Service

A Django-based service for receiving and forwarding data to configured destinations with rate limiting.

## Prerequisites

- Python 3.11+
- Redis server
- Virtualenv (recommended)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd data_pusher
```

### 2.Create and activate virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Running the Service

```bash
python manage.py runserver
```

#### Start Celery worker (in a separate terminal)

```bash
celery -A data_pusher worker --loglevel=info --pool=eventlet
```

#### Start Redis (if not running)

```bash
# On Linux/macOS (usually)
redis-server
# On Windows (if installed as service)
redis-cli ping
```

### Accessing the Service
#### API Documentation (Swagger): http://127.0.0.1:8000/swagger/

#### Admin Panel: http://127.0.0.1:8000/admin/

#### Login API: http://127.0.0.1:8000/api/auth/login/

#### Sample credentials:

```bash
Username: admin

Password: admin@123
```