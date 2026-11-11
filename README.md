# thearaperson — FlyStudio-inspired portfolio

A complete Django 5.2 application with an original editorial visual design: ivory and ink, acid-yellow accents, expressive typography, custom procedural artwork, and responsive multi-page navigation. It uses Bootstrap 5’s grid, Google Fonts, Phosphor Icons, GSAP + ScrollTrigger, Lenis, Swiper, and a native accessible dialog lightbox.

The application is runnable without cloud credentials using SQLite and local media. Configure the supplied environment variables to use Supabase PostgreSQL and S3-compatible Storage. No live Supabase account was connected during development.

## 1. Directory structure and installation

```text
flystudio/
├── manage.py
├── requirements.txt             # Supported dependency ranges
├── requirements.lock.txt        # Exact versions verified in this environment
├── .env.example
├── Dockerfile / .dockerignore
├── Procfile
├── config/
│   ├── settings.py              # Environment, database, storage, security
│   ├── urls.py                  # Admin, application URLs, error handlers
│   └── wsgi.py
├── portfolio/
│   ├── models.py                # Profile, Project, ProjectImage, BlogPost,
│   │                            # ContactMessage, ContactThrottle
│   ├── forms.py                 # Contact validation
│   ├── views.py                 # CBVs, sanitized Markdown, AJAX API
│   ├── urls.py
│   ├── admin.py
│   ├── context_processors.py
│   ├── tests.py
│   ├── migrations/0001_initial.py
│   └── management/commands/seed_demo.py
├── templates/
│   ├── base.html
│   ├── 403.html / 404.html
│   └── portfolio/
│       ├── index.html
│       ├── project_list.html / project_detail.html
│       ├── blog_list.html / post_detail.html
│       ├── about.html / contact.html
│       ├── contact_section.html / contact_form.html
│       ├── artwork.html / project_card.html / post_card.html
│       └── pagination.html / cta.html
└── static/
    ├── css/style.css
    ├── js/main.js
    └── images/favicon.svg
```

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.lock.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/.

The seed command is optional and idempotent: it preserves existing records and edits. Alex Morgan, all clients, artwork, experience numbers, and projects are fictional demonstration content. Replace the homepage’s descriptive copy and statistics in `index.html`, the branding in `base.html`, and the profile in Admin before launch. `hello@example.com` is a placeholder. No social or project links point to invented live accounts; add your own valid links in Admin.

## 2. Supabase and Django configuration

### PostgreSQL

1. Create a Supabase project and copy its **session pooler** PostgreSQL URI from **Connect**. A session pooler is a convenient option on IPv4-only hosts. Use the connection details and region shown in your own dashboard.
2. Set `DATABASE_URL` in your deployment secret manager or local `.env`. URL-encode reserved characters in the password; never put database credentials in frontend JavaScript.
3. Run `python manage.py migrate` against that database. Run `createsuperuser` there, too. Seed the cloud database only if you intentionally want demo content.

```dotenv
DATABASE_URL=postgresql://postgres.PROJECT_REF:ENCODED_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require
```

`config/settings.py` uses `dj_database_url.parse`, TLS in production, `conn_max_age=0`, and disabled server-side cursors for pooler compatibility. The Django ORM writes contact submissions directly to Supabase PostgreSQL; no browser Supabase key is needed.

Django owns authentication and authorization for Admin and private messages. Keep contact data out of public Supabase Data API access: preferably use a dedicated unexposed database schema or remove this app’s tables from exposed API schemas. If they remain in an exposed schema, enable RLS and revoke access for the `anon` and `authenticated` roles. Do not add public read policies for messages, sessions, users, or throttle records. Django’s server-side database role must retain the permissions needed for migrations and queries. This project does not use Supabase Auth.

### Storage

1. Create a bucket named `portfolio` under Supabase Storage. A private bucket works: Django generates time-limited signed S3 URLs when rendering images and résumé links.
2. Enable/configure Supabase S3 compatibility and generate a dedicated S3 access-key/secret pair in the Storage settings. These are **S3 credentials**, not the publishable/anon key.
3. Copy the exact S3 endpoint and region from your dashboard into the variables below. The example host may differ from the endpoint shown for your project.

```dotenv
USE_SUPABASE_STORAGE=true
SUPABASE_S3_ENDPOINT_URL=https://PROJECT_REF.storage.supabase.co/storage/v1/s3
SUPABASE_S3_ACCESS_KEY_ID=YOUR_S3_ACCESS_KEY
SUPABASE_S3_SECRET_ACCESS_KEY=YOUR_S3_SECRET
SUPABASE_STORAGE_BUCKET=portfolio
SUPABASE_S3_REGION_NAME=YOUR_PROJECT_REGION
```

`django-storages` uses S3 v4 signatures, path addressing, signed URLs, unique upload names, and no object ACL override. Uploads flow through authenticated Django Admin. Configure upload size/type restrictions on the bucket according to your media needs. Static CSS/JS stays with the application and is served by WhiteNoise. Disabling `USE_SUPABASE_STORAGE` uses `media/` locally; Django serves local media only with `DEBUG=true`.

The S3 secret and database password stay exclusively on the server. Do not commit `.env` or copy it into an image. Changing storage backends does not transfer existing media: copy old objects separately and preserve their stored paths.

## 3. Models, views, URLs, and Admin

- **Profile:** editable identity, bio, tagline, avatar, PDF résumé, location, contact email, social-link JSON, and availability. Admin allows one profile. HTTPS social links render automatically.
- **Project:** unique slug, summary, Markdown case study, client, role, comma-separated technology tags, optional live URL and cover, featured flag, category, year, and ordering. A `ProjectImage` relation supports gallery images, captions, and ordering. Procedural CSS artwork provides a polished fallback until you upload covers.
- **BlogPost:** unique slug, excerpt, Markdown content, optional cover, date, tags, and an explicit published flag. Drafts and future posts are excluded from both lists and direct detail URLs.
- **ContactMessage:** sender details, subject, budget, message, timestamp, and read state. Admin supports search, filters, and bulk mark-as-read.
- **ContactThrottle:** internal hashed-IP counters shared by all workers. It is intentionally not exposed in Admin.

| URL | View / behavior |
| --- | --- |
| `/` | Home ListView, featured projects and latest published posts |
| `/work/` | Project ListView, category query filter and pagination |
| `/work/<slug>/` | Project DetailView, sanitized case study and gallery |
| `/about/` | About TemplateView |
| `/journal/` | Published BlogPost ListView and pagination |
| `/journal/<slug>/` | Published BlogPost DetailView |
| `/contact/` | Contact TemplateView with CSRF cookie |
| `/api/contact/` | CSRF-protected POST JSON endpoint |
| `/admin/` | Authenticated Django Admin |

Markdown supports headings, lists, links, fenced code, and tables. Rendered HTML is sanitized with Bleach before it is marked safe. Raw scripts, event handlers, unsafe protocols, and embedded media markup are excluded. Use dedicated image fields for media. Django’s default form widgets are used for content editing; a WYSIWYG editor is not bundled.

## 4. Base template and frontend behavior

`base.html` contains pinned CDN links for Bootstrap grid 5.3.3, Phosphor Icons 2.1.1, GSAP/ScrollTrigger 3.12.7, Lenis 1.3.1, and Swiper 11.2.6. It loads DM Sans and Manrope from Google Fonts. Bootstrap’s JavaScript bundle is unnecessary for the custom menu and native dialog.

Theme selection is applied in the head before painting, stored in `localStorage`, and initially respects the operating-system theme. The fullscreen navigation animates with GSAP, traps keyboard focus, closes with Escape, and returns focus to its trigger. Regular page links and anchor sections provide both multi-page navigation and a smooth single-page journey.

`main.js` connects Lenis to the GSAP ticker and ScrollTrigger, animates hero elements, scrolls the featured work horizontally on large screens, pins the About label, and stacks service cards. Touch screens use native horizontal scrolling. Reduced-motion visitors receive the full content without the animations or smooth scrolling. CDN failure leaves content and navigation visible; custom menu and form logic do not require GSAP. Swiper enhances uploaded galleries, while native `dialog` provides image previews. No haptic permission or vibration is required.

CSS artwork is locally rendered, original, and needs no external image licensing. Uploads override it automatically. Static design values, demo statistics, the Brooklyn clock, and brand labels live in the templates/JS; content records live in the database.

## 5. AJAX contact flow

The form sends same-origin JSON with the hidden Django CSRF token as `X-CSRFToken`. It disables repeated clicks while pending, reports field errors with `aria-invalid` and descriptions, keeps entered values on errors, and resets after success. Network interruptions and 15-second timeouts produce visible feedback. A timeout can occur after a server write, so its message explicitly warns that the original submission might have arrived.

```json
{
  "name": "Jamie Taylor",
  "email": "jamie@example.com",
  "subject": "A new website",
  "budget": "$5,000 – $10,000",
  "message": "I would love to discuss a new portfolio website with you.",
  "website": ""
}
```

| Status | Meaning |
| --- | --- |
| `201` | Persisted successfully; `ok: true` and a message |
| `400` | Invalid JSON or fields; field validation includes `errors` |
| `403` | CSRF failure; refresh and retry |
| `405` | POST required |
| `415` | JSON content type required |
| `429` | Hourly rate limit; `Retry-After: 3600` |
| `503` | Database persistence failed; no false success |

Default limit: five valid submissions per IP per hour. Invalid forms do not consume the quota. A filled honeypot returns a neutral success without saving a message. IPs are HMAC-hashed with the application secret. PostgreSQL row locks and transactions coordinate the quota across workers. SQLite is intended for development, not concurrent production traffic.

The app reads `REMOTE_ADDR`, not client-supplied forwarded IP headers. Configure your trusted reverse proxy/application server to set the real client address safely; otherwise requests behind a shared proxy share the quota. For a high-traffic public site, apply infrastructure request limits too. Delete stale `ContactThrottle` rows periodically according to your retention policy; old rows are reset on reuse. Messages are saved for Admin review; email notifications are not configured.

## Production deployment

Deploy on a Python/Docker host with HTTPS and PostgreSQL network access. This Django application does not run directly in Cloudflare Workers/Sites.

1. Set `DEBUG=false`, generate a unique random `SECRET_KEY` of at least 50 characters, and set `DATABASE_URL` and the storage credentials through deployment secrets.
2. Set exact domain names in `ALLOWED_HOSTS`, and HTTPS origins in `CSRF_TRUSTED_ORIGINS`.
3. Behind a trusted TLS-terminating proxy that strips incoming forwarded-protocol headers, set `TRUST_PROXY_HEADERS=true`. Leave HTTPS redirect enabled. Confirm real-client-IP handling for rate limits.
4. Install locked dependencies, run `python manage.py migrate` as a release task, and run `python manage.py collectstatic --noinput`.
5. Run `python manage.py check --deploy`, create a production superuser, and launch `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -` behind the HTTPS proxy.
6. Replace demo copy, verify a contact submission in Admin, upload and open media from Storage, and test on desktop and mobile before launch. Back up the database and media and monitor server error logs.

Example production environment (use real values in your host’s secret manager):

```dotenv
DEBUG=false
SECRET_KEY=GENERATE_A_RANDOM_SECRET_OF_AT_LEAST_50_CHARACTERS
ALLOWED_HOSTS=portfolio.example.com
CSRF_TRUSTED_ORIGINS=https://portfolio.example.com
DATABASE_URL=YOUR_SUPABASE_POSTGRES_CONNECTION_URI
USE_SUPABASE_STORAGE=true
TRUST_PROXY_HEADERS=true
```

A Dockerfile and Procfile are supplied. Build with `docker build -t portfolio .`, then supply production environment values at runtime. The Docker image collects static files during its build with development defaults; all production runtime settings come from environment variables. Run migrations separately from web worker startup. The container runs as an unprivileged user. Supabase stores uploads in production, so the container does not require persistent local media.

To preview the custom error page locally, temporarily use `DEBUG=false` with a valid production-style configuration, or rely on the included test that renders it with production error handling. Django intentionally shows its technical 404 page when `DEBUG=true`.

## Verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
node --check static/js/main.js
```

The 18 included tests cover rendered routes, category filtering, draft/future post privacy, custom 404 behavior, sanitization, demo seeding, empty content, contact persistence, CSRF rejection, field/JSON validation, the honeypot, rate limits, forwarded-IP spoofing, and transactional rollback on database failure. Tests run against the configured backend’s test database; keep production credentials out of test environments.

See `VERIFICATION.md` for this build’s actual results and remaining deployment checks. Browser/device QA and real Supabase upload/connection checks require the corresponding runtime and credentials; they are not implied by passing server-side tests.
