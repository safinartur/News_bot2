# Backend (Django)
Create and activate venv, then:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

API:
- `GET /api/posts/?page=1&tag=obshchestvo`
- `GET /api/posts/<slug>/`
- `POST /api/posts/` with `X-API-KEY: $API_SHARED_KEY` (multipart form ok, field names: title, body, tag_slugs[], cover(optional), source_url(optional))
- `GET /api/tags/`
