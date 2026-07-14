
# Django + Supabase backend, authenticated via Firebase

## How the pieces fit together

- **Firebase Auth** (already working in Next.js) stays the single source of truth
  for login/signup/password reset. Django never touches passwords.
- On every API call, your Next.js app sends the current user's Firebase **ID
  token** as `Authorization: Bearer <token>`.
- Django verifies that token server-side with the **Firebase Admin SDK**
  (`accounts/authentication.py`), then maps the token's `uid` to a local
  `Profile` row.
- That `Profile` row — plus `Clinic` and `ClinicMembership` — live in your
  **Supabase Postgres** database via the normal Django ORM. Supabase here is
  just a managed Postgres instance; you are not using Supabase Auth.

## 1. Get your Firebase service account key

Firebase Console → Project Settings → Service Accounts → **Generate new
private key**. Download the JSON. In production, mount it as a secret file
(don't commit it, don't bake it into your image) and point
`FIREBASE_CREDENTIALS_PATH` at that path.

## 2. Get your Supabase connection string

Supabase Dashboard → Project Settings → Database → Connection string (URI).
Use the **Session pooler** (or a direct connection), not the **Transaction
pooler**, unless you also set `DISABLE_SERVER_SIDE_CURSORS = True` in
settings — transaction-mode pgbouncer doesn't support Django's named
prepared statements / server-side cursors.

## 3. Local setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real values
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

## 4. API surface this ships with

| Method           | Path                   | Purpose                                                                      |
| ---------------- | ---------------------- | ---------------------------------------------------------------------------- |
| GET              | `/api/profile/me/`   | Fetch the caller's own profile (auto-created on first authenticated request) |
| PATCH/PUT        | `/api/profile/me/`   | Update first/last name, username, phone, avatar                              |
| GET/POST         | `/api/clinics/`      | List / create clinics                                                        |
| GET/PATCH/DELETE | `/api/clinics/{id}/` | Retrieve / update / delete a clinic                                          |

`ClinicMembership` (who works where, and their role) is nested read-only under
a profile's `clinic_memberships` for now — add dedicated endpoints for
creating/editing memberships once you decide who's allowed to add staff to a
clinic (see "Before going to production" below).

## 5. Calling it from Next.js

Send the Firebase ID token on every request:

```ts
import { getAuth } from "firebase/auth";

async function apiFetch(path: string, options: RequestInit = {}) {
  const user = getAuth().currentUser;
  const token = user ? await user.getIdToken() : null;

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}

// e.g. fetch/update the current user's profile
const res = await apiFetch("/api/profile/me/");
const profile = await res.json();
```

`getIdToken()` automatically refreshes an expiring token, so you don't need
to manage refresh logic yourself.

## 6. Before going to production

- **Lock down `ClinicViewSet`**: right now any authenticated Firebase user can
  create/edit any clinic. Add a permission class that checks the caller's
  `ClinicMembership.role` (e.g. only `owner`/`admin` can edit; anyone can
  read).
- **Rate limiting**: add `django-ratelimit` or throttle classes in DRF
  (`DEFAULT_THROTTLE_CLASSES`) — Firebase token verification is a network
  call per request unless you enable Firebase's local JWKS caching (the
  Admin SDK does this automatically, so this is mostly fine out of the box).
- **Logging/monitoring**: wire up Sentry or similar; set `DEBUG=False` and
  never expose stack traces.
- **Migrations**: run `migrate` as a release step in your deploy pipeline,
  not manually on the running instance.
- **CORS**: keep `CORS_ALLOWED_ORIGINS` to your real frontend domain(s) only.
- **Static files**: `collectstatic` is wired up via WhiteNoise for the admin
  site; run `python manage.py collectstatic` in your build step.
- **Process**: run with `gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000`
  behind a reverse proxy (or your platform's equivalent), not `runserver`.

## 7. Project layout

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py      # env-driven, production-hardened when DEBUG=False
│   ├── urls.py
│   └── wsgi.py
└── accounts/
    ├── models.py         # Profile, Clinic, ClinicMembership
    ├── authentication.py # Firebase ID token verification -> Profile
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── admin.py
```
