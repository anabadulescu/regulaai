# RegulaAI Privacy Policy

Last updated: [Current Date]

## Introduction

Welcome to RegulaAI. We are committed to protecting your privacy and ensuring you have a positive experience on our website and when using our services. This Privacy Policy explains how we collect, use, and protect your personal data in compliance with the General Data Protection Regulation (GDPR).

## Who We Are

RegulaAI is a service that helps businesses ensure GDPR compliance for their websites. We are the data controller for the personal data we collect and process.

## What Personal Data We Collect

We collect the following types of personal data:

1. **Contact Information**
   - Email address (when you join our waitlist or contact us)

2. **Website Data**
   - Domain URLs that you submit for scanning
   - Cookie information collected during website scans
   - Technical information about the websites being scanned

## How We Collect Your Data

We collect your personal data when you:
- Join our waitlist
- Submit a website for scanning
- Contact us for support
- Use our services

## Why We Process Your Data

We process your personal data for the following purposes:

1. **To Provide Our Services**
   - To scan websites for GDPR compliance
   - To generate compliance reports
   - To maintain and improve our services

2. **To Communicate With You**
   - To send you updates about our services
   - To respond to your inquiries
   - To send you important notifications

3. **To Improve Our Services**
   - To analyze usage patterns
   - To develop new features
   - To enhance security

## Legal Basis for Processing

We process your personal data based on the following legal grounds:

1. **Contractual Necessity**
   - When you use our services, we need to process your data to fulfill our contractual obligations

2. **Legitimate Interests**
   - To improve our services
   - To ensure the security of our platform
   - To prevent fraud

3. **Consent**
   - When you explicitly agree to receive marketing communications
   - When you join our waitlist

## How Long We Keep Your Data

We retain your personal data for as long as necessary to:
- Provide our services
- Fulfill the purposes outlined in this policy
- Comply with legal obligations

## Your Rights

Under GDPR, you have the following rights:

1. **Right to Access**
   - You can request a copy of your personal data

2. **Right to Rectification**
   - You can ask us to correct inaccurate data

3. **Right to Erasure**
   - You can request deletion of your personal data

4. **Right to Restrict Processing**
   - You can ask us to limit how we use your data

5. **Right to Data Portability**
   - You can request a copy of your data in a machine-readable format

6. **Right to Object**
   - You can object to our processing of your data

7. **Right to Withdraw Consent**
   - You can withdraw your consent at any time

## Data Security

We implement appropriate technical and organizational measures to protect your personal data, including:
- Encryption of data in transit and at rest
- Regular security assessments
- Access controls and authentication
- Secure data storage

## International Data Transfers

We may transfer your personal data outside the European Economic Area (EEA). When we do, we ensure appropriate safeguards are in place through:
- Standard contractual clauses
- Adequacy decisions
- Binding corporate rules

## Contact Us

If you have any questions about this Privacy Policy or our data practices, please contact us at:
- Email: privacy@regulaai.com
- Address: [Your Company Address]

## Changes to This Policy

We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date. 

# Stage 1: Build with Poetry
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps for Playwright and Poetry
RUN apt-get update && apt-get install -y curl git && \
    pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main

# Install Playwright and download browsers
RUN pip install playwright && playwright install --with-deps

COPY . .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# System deps for Playwright
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy installed packages and app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Expose FastAPI port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]

version: '3.8'

services:
  crawler:
    build: .
    container_name: crawler-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/regulaai
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 5

  db:
    image: postgres:15
    container_name: regulaai-db
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: regulaai
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    container_name: regulaai-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@regulaai.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
    name: regulaai_pgdata 