# Campus Starter Portal – Cloud Integrated Student Onboarding System

A Django + DRF onboarding portal for new students, with frontend templates and cloud-ready backend integration.

## What this project includes

- Student registration and profile storage
- External ID card API integration
- Classmate restaurant recommendation API integration
- Public country API integration
- Async-ready welcome-pack trigger using **AWS SQS** (consumer can be AWS Lambda)
- Bootstrap dashboard UI

## Tech stack

- Backend: Django, Django REST Framework, Django ORM
- Database: SQLite (dev), PostgreSQL-ready config
- Frontend: HTML, CSS, Bootstrap 5, JavaScript Fetch API
- Queue/Event: AWS SQS
- Worker idea: AWS Lambda consuming SQS messages

---

## Step-by-step tutorial: build this from scratch

### 1) Create project and app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
django-admin startproject campus_portal .
python manage.py startapp onboarding
```

### 2) Configure settings

In `campus_portal/settings.py`:

- Add `rest_framework` and `onboarding` in `INSTALLED_APPS`
- Use `.env` variables for secrets and service URLs
- Keep SQLite default, and enable PostgreSQL when `DB_ENGINE=postgres`
- Add SQS settings:
  - `AWS_REGION`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `WELCOME_PACK_QUEUE_URL`

### 3) Create student model and migrate

Model fields used:

- first_name, last_name, email, phone
- home_country, campus_city, course
- card_id

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4) Create service layer

Create `onboarding/services.py` for external API calls:

- `IDCardService.generate_card(...)`
- `RestaurantService.get_recommendations(...)`
- `CountryInfoService.fetch_country_info(...)`

This keeps view logic clean and scalable.

### 5) Create SQS producer service

Create `onboarding/aws_queue.py` with `WelcomePackQueueService.enqueue(...)`:

- Build SQS message payload
- Send with `boto3.client('sqs').send_message(...)`
- Return `queued`, `message_id`, and a helpful note

### 6) Add API endpoints

Create endpoints in `onboarding/views.py` and map in `onboarding/urls.py`:

- `POST /api/register-student`
- `POST /api/get-restaurants`
- `GET /api/country-info`
- `GET /api/student/<id>`
- `POST /api/generate-welcome-pack` (pushes message to SQS)

### 7) Build frontend pages

- `register.html`: onboarding form
- `dashboard.html`: profile + country info + restaurant cards + guidance section
- `register.js`: submit form and redirect
- `dashboard.js`: load student data and country info, query restaurants

### 8) Connect Lambda to SQS (trigger)

In AWS:

1. Create an SQS queue
2. Create Lambda function (Python runtime)
3. Add SQS trigger to Lambda (select your queue)
4. Set Lambda IAM permissions for SQS, logs, and any DB/API access needed

Example Lambda handler skeleton:

```python
import json

def lambda_handler(event, context):
    for record in event["Records"]:
        payload = json.loads(record["body"])
        student_id = payload["student_id"]
        # fetch student profile, country info, restaurant suggestions
        # combine into welcome pack JSON and store/send as needed
    return {"statusCode": 200, "body": "Processed"}
```

### 9) Run locally

```bash
cp .env.example .env
python manage.py runserver
```

---

## API documentation (share with classmates)

### POST `/api/register-student`
Registers a student and stores `card_id` returned by ID service.

### POST `/api/get-restaurants`
Input: `student_id`, `cuisine`, `budget`.
Returns restaurant suggestions for student campus city.

### GET `/api/country-info?country=India`
Returns currency, symbol, timezone, calling code, flag, and region.

### GET `/api/student/<id>`
Returns student profile.

### POST `/api/generate-welcome-pack`
Pushes a welcome-pack generation event to SQS.

Example request:

```json
{ "student_id": 1 }
```

Example response:

```json
{
  "message": "Welcome pack event sent.",
  "student_id": 1,
  "queued": true,
  "message_id": "abc-123",
  "note": "Message pushed to SQS. Lambda consumer can now generate the welcome pack."
}
```

---


## Architecture Diagram

```mermaid
flowchart LR
    A[Student Browser
Bootstrap + JS] -->|POST /api/register-student| B[Django REST API
(onboarding/views.py)]
    A -->|GET /dashboard + API calls| B

    B --> C[(SQLite Dev DB
PostgreSQL in AWS)]
    B -->|Generate ID Card| D[ID Card Service API
(Your own service)]
    B -->|Restaurant Suggestions| E[Classmate Restaurant API]
    B -->|Country/Currency Info| F[Public Country API
(restcountries)]

    B -->|POST /api/generate-welcome-pack| G[AWS SQS Queue]
    G -->|Event trigger| H[AWS Lambda Consumer]
    H -->|Compose Welcome Pack| D
    H -->|Compose Welcome Pack| E
    H -->|Compose Welcome Pack| F

    subgraph Cloud Ready Design
      B
      G
      H
      C
    end
```

### How to read this diagram

1. The student uses the web frontend (registration + dashboard).
2. Django REST API handles validation, persistence, and external API orchestration.
3. Core student data is stored in SQLite during development, and can switch to PostgreSQL for AWS deployment.
4. The API integrates 3 required web services:
   - Your own ID card API
   - Classmate restaurant API
   - Public country information API
5. For scalability, welcome-pack generation is event-driven:
   - Django publishes an event to SQS
   - Lambda consumes the queue event and performs heavier aggregation work asynchronously.

## AWS deployment readiness

- Environment variables already used
- PostgreSQL-ready database settings included
- `STATIC_ROOT` set for `collectstatic`
- SQS queue integration included
- Lambda trigger approach documented (no auto deployment performed)
