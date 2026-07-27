# ROMSITES

Studio site for ROMSITES LLC — full-stack web design, development, SEO, and maintenance services.
Doubles as a live portfolio with client testimonials.

**Live site:** https://romsites.onrender.com/

## Tech Stack
- Django 4.2, SQLite
- WhiteNoise (static file serving/compression)
- Statically compiled utility CSS (see "Styling" below — no Tailwind CDN/build step required)
- Render (hosting)

## Required environment variables (production)
| Variable | Required | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | **Yes** | The app will refuse to start without this when `DJANGO_DEBUG=False`. `render.yaml` already generates this automatically (`generateValue: true`) — nothing to do if deploying via the Render Blueprint. |
| `DJANGO_DEBUG` | No (defaults to `False`) | Only set to `True` for local development |
| `DJANGO_ALLOWED_HOSTS` | No (defaults to `romsites.onrender.com,localhost,127.0.0.1`) | Comma-separated list; update if the domain changes |

## Running locally
```bash
pip install -r requirements.txt
DJANGO_DEBUG=True python manage.py migrate
DJANGO_DEBUG=True python manage.py runserver
```

## Deploying (Render)
`render.yaml` defines a single Django web service. Previously this file also declared a second,
unused Node/Express service pointing at leftover React/Vite scaffolding that was never the real
site — that's been removed. If you're using Render's Blueprint feature, just point it at this repo
and it will build/deploy the Django service correctly.

## Styling
This project ships a statically compiled CSS file (`static/css/compiled-tailwind.css`) generated to
cover exactly the utility classes the templates use — there is **no Tailwind CDN `<script>`** and no
build step required to deploy. If you add new utility classes to a template, that stylesheet needs
to be regenerated/extended to include them, or the new classes won't render.

## Reviews & moderation
Reviews are stored in the `Review` database model (previously they were written to a JSON file on
disk, which doesn't survive a restart on Render's ephemeral filesystem — see "What changed" below).
Public submissions go into a pending queue (`is_approved=False`) and aren't shown on the public
Portfolio page until a staff user approves them from `/portfolio` (while logged in) or the Django
admin.

## What changed in this refactor (see full audit for details)
- **Reviews moved from `data/reviews.json` to the database.** The old approach silently lost every
  submitted review on the next deploy/restart because Render's free-tier filesystem is ephemeral.
  The existing 3 reviews were migrated in as approved seed data so nothing was lost.
- **`render.yaml` no longer deploys a second, wrong service.**
- Removed the hardcoded insecure `SECRET_KEY` fallback, fixed `DEBUG` defaulting to `True`, and
  replaced `ALLOWED_HOSTS = ['*']` with an explicit host list.
- Added honeypot + timing-check spam protection to the review form (previously anyone could submit
  unlimited unmoderated reviews), plus safe rating parsing (a malformed `rating` value used to
  crash the request with an unhandled exception).
- Fixed the delete-review page leaking review content to anonymous visitors on page load — it now
  checks admin status before rendering anything, not just before the delete action.
- Fixed a large number of invalid Tailwind color classes scattered across nearly every page
  (e.g. `slate-350`, `slate-850`, `indigo-550` — numbers that don't exist in Tailwind's default
  palette and silently render as unstyled).
- Added SEO essentials: unique page titles/descriptions, Open Graph/Twitter tags, canonical URLs,
  favicon, `robots.txt`, and `sitemap.xml` (previously all pages shared one generic title with no
  other metadata at all).
- Removed the dead Node/Vite/Express/Gemini scaffold (`package.json`, `server.ts`,
  `export-static.js`, `metadata.json`, `.env.example` referencing an unused Gemini key) that isn't
  part of the deployed Django app.

## Known open items
- The review submission form is still built as a raw HTML string embedded in `views.py` rather than
  a Django Form or template partial. It works correctly (CSRF token is present in the surrounding
  template), but converting it to a proper Django Form would be cleaner and safer long-term.
