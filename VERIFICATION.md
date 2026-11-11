# Verification record

Built and checked on November 11, 2026 with Python 3.12 and Django 5.2.19.

- `python manage.py check`: passed, no issues.
- `python manage.py migrate --noinput`: all migrations applied successfully to a local SQLite database.
- `python manage.py seed_demo`: completed; idempotence and edit preservation are covered by a test.
- `python manage.py test`: 18 tests passed.
- `python manage.py makemigrations --check --dry-run`: no model changes detected.
- `python manage.py collectstatic --noinput`: completed with compressed and hashed static assets.
- `node --check static/js/main.js`: passed.
- `python manage.py check --deploy`: no issues with production-mode environment settings, a verification secret, and a placeholder PostgreSQL URI. This check did not establish a live PostgreSQL connection.

The test suite renders the public templates, exercises the JSON contact endpoint and CSRF middleware, and checks data visibility and sanitization. It does not execute browser JavaScript or verify visual layout.

## Not verified in this environment

Browser and device QA could not run: the required managed-browser control tool (`cua_repl.js`) was unavailable. No desktop/mobile screenshot or interaction result is claimed. Verify fullscreen-menu animation/focus, pinned horizontal scrolling, reduced-motion behavior, light/dark persistence, the AJAX submission UX, and real uploaded Swiper/lightbox galleries in a browser before launch.

No Supabase credentials were configured. PostgreSQL TLS/pooler connectivity, Storage bucket permissions, S3 uploads and signed URLs need to be checked against your own project. External CDN delivery and production-domain HTTPS/proxy configuration also remain deployment checks.

No public deployment was made. The source targets a Python/WSGI or Docker host; Cloudflare Workers/Sites cannot directly run this Django application.

The source archive excludes the local SQLite preview database, collected static files, caches, uploaded media, and secrets. Run the README installation commands to recreate a clean demo.
