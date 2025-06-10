# Alt Data Dashboard

A modern, interactive SaaS web application for unified analytics and visualization of public and alternative data.

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── database/ # Database configuration
│   └── requirements.txt
└── frontend/         # Next.js frontend
    ├── src/
    │   ├── app/      # Next.js app directory
    │   ├── components/ # Reusable components
    │   ├── hooks/    # Custom React hooks
    │   └── styles/   # Global styles
    └── package.json
```

## Prerequisites

- Node.js (v18 or higher)
- Python 3.10+
- PostgreSQL 14+
- Redis

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/alt_data
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Features

- Modern dashboard with customizable widgets
- Unified analytics across multiple data sources
- Real-time data visualization
- User authentication and authorization
- Rate-limited API integrations
- Responsive and accessible UI
- Multi-language support (Vietnamese/English)

## Development

### Environment Variables

Create a `.env` file in both backend and frontend directories with the required configuration.

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
