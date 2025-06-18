# Crawler Service

A robust web scraping service built with Playwright and FastAPI.

## Features

- Headless browser automation with Playwright
- RESTful API with FastAPI
- Async request handling
- Configurable scraping rules
- Data validation and transformation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the service:
```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Development

- Use `pytest` for running tests
- Follow PEP 8 style guide
- Use type hints for better code maintainability 