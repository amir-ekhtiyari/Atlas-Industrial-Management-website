# راهنمای استقرار — www.atlas-aim.com

راهنمای تیم دپلوی برای راه‌اندازی وب‌سایت شرکت مدیریت صنعتی اطلس روی سرور.
پروژه آماده‌ی استقرار است؛ کافی است مراحل زیر انجام شود.

> **English summary:** Django 5.2 LTS. The live site runs on a cPanel host with MariaDB 10.6 (section 0).
> Alternative: Docker Compose with PostgreSQL behind Nginx/Gunicorn. Docker path: Docker Compose
> (`cp .env.production.example .env`, fill secrets, `docker compose up -d --build`,
> `docker compose exec web python manage.py createsuperuser`). The first start migrates the database,
> collects static files and loads all company content automatically. Point DNS for `atlas-aim.com` and
> `www.atlas-aim.com` to the server and enable HTTPS (section 4). A non-Docker setup is in section 6.

---

## ۰. سایت فعلی — هاست cPanel (ایران اسپید) با MariaDB

سایت زنده روی هاست cPanel با **Setup Python App** و دیتابیس **MariaDB 10.6** اجرا می‌شود
(PostgreSQL هاست قدیمی بود). DNS و ایمیل دامنه روی Morvahost است.

| مورد | مقدار |
|---|---|
| Django | 5.2 LTS (نسخه‌ی ۶ با MariaDB هاست سازگار نیست) |
| درایور دیتابیس | `mysqlclient` (در `requirements.txt`) |
| `.env` | `DB_ENGINE=mysql`، `DB_PORT=3306` — charset `utf8mb4` و حالت strict خودکار تنظیم می‌شوند |
| دیتابیس | `utf8mb4` با collation `utf8mb4_unicode_ci` (برای متن فارسی) |

به‌روزرسانی سایت روی همین هاست (در Terminal یا SSH، بعد از فعال کردن virtualenv):

```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt
```

دامنه‌ی `atlasaim.ir` (و `www.atlasaim.ir`) اگر به همین هاست اشاره کند، خودکار با ریدایرکت ۳۰۱ به
`https://www.atlas-aim.com` فرستاده می‌شود (متغیر `SITE_ALIAS_DOMAINS`).

بخش‌های ۱ تا ۶ برای راه‌اندازی روی سرور مجازی (VPS) با Docker یا بدون آن است.

## ۱. پیش‌نیازها

| مورد | توضیح |
|---|---|
| سرور | لینوکس (Ubuntu 22.04/24.04 پیشنهاد می‌شود)، حداقل ۱ گیگ رم، ۱۰ گیگ دیسک |
| روش پیشنهادی | **Docker** و **Docker Compose v2** |
| DNS | رکورد `A` برای `atlas-aim.com` و `www.atlas-aim.com` به IP سرور |
| پورت‌ها | ۸۰ و ۴۴۳ باز باشند |

دامنه‌ی اصلی سایت **`www.atlas-aim.com`** است؛ `atlas-aim.com` به‌طور خودکار به آن هدایت می‌شود.

## ۲. تنظیم متغیرهای محیطی

```bash
cp .env.production.example .env
nano .env
```

این مقادیر **حتماً** باید عوض شوند:

| متغیر | مقدار |
|---|---|
| `SECRET_KEY` | یک کلید تصادفی تازه — `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DB_PASSWORD` | یک رمز قوی برای دیتابیس |

> **مهم:** در مقادیر `.env` از کاراکتر `$` استفاده نکنید؛ Docker Compose آن را متغیر تفسیر می‌کند.
> کلیدی که با دستور بالا ساخته شود این کاراکتر را ندارد.

دامنه (`ALLOWED_HOSTS`، `CSRF_TRUSTED_ORIGINS`، `SITE_URL`) از پیش روی `atlas-aim.com` تنظیم شده است.
فایل `.env` هرگز نباید در گیت ثبت شود.

## ۳. راه‌اندازی با Docker (روش پیشنهادی)

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

در نخستین اجرا به‌طور خودکار انجام می‌شود:

1. ساخت جداول دیتابیس (`migrate`)
2. جمع‌آوری فایل‌های استاتیک (`collectstatic`)
3. بارگذاری کامل محتوای سایت — متن‌ها، محصولات، تصاویر، کاتالوگ‌ها، گواهی‌نامه‌ها و…

مرحله‌ی ۳ فقط روی دیتابیس خالی اجرا می‌شود؛ در راه‌اندازی‌های بعدی، ویرایش‌هایی که در پنل مدیریت
انجام شده بازنویسی **نمی‌شوند**.

| سرویس | نقش |
|---|---|
| `db` | PostgreSQL 16 (داده در volume به نام `postgres_data`) |
| `web` | Django + Gunicorn |
| `nginx` | پورت ۸۰، سرو مستقیم `/static/` و `/media/`، هدایت `atlas-aim.com` → `www` |

بررسی: `http://www.atlas-aim.com/` سایت فارسی و `/admin/` پنل مدیریت را باز می‌کند.

### اگر سرور به pypi.org دسترسی ندارد

اگر هنگام build خطای SSL یا `No matching distribution` دیدید، از یک mirror استفاده کنید:

```bash
PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple docker compose build
docker compose up -d
```

## ۴. HTTPS

سایت برای کار روی HTTPS پیکربندی شده است (`SECURE_SSL_REDIRECT=True`). یکی از این دو حالت:

**الف) CDN یا load balancer جلوی سرور (مثلاً ابر آروان / Cloudflare)** — گواهی را آن‌جا فعال کنید و
ترافیک را به پورت ۸۰ سرور بفرستید. nginx سرآیند `X-Forwarded-Proto` را به Django می‌رساند. کار دیگری لازم نیست.

**ب) گواهی Let's Encrypt روی همین سرور:**

```bash
docker compose stop nginx
sudo certbot certonly --standalone -d atlas-aim.com -d www.atlas-aim.com
```

سپس در `docker-compose.yml` پورت `443` و volume `/etc/letsencrypt` را از کامنت درآورید، در
`deploy/nginx/atlas.conf` بلوک `listen 443` و خط `return 301 https://...` را فعال کنید و:

```bash
docker compose up -d
```

> برای آزمایش موقت روی HTTP، **پیش از** نصب گواهی، `SECURE_SSL_REDIRECT=False` بگذارید و پس از
> فعال شدن HTTPS آن را به `True` برگردانید (در حالت HTTP ورود به پنل مدیریت ممکن نیست).
> `SECURE_HSTS_SECONDS` با ۳۶۰۰ شروع می‌شود؛ پس از اطمینان از HTTPS می‌توان آن را به `31536000` رساند.

## ۵. نگهداری

| کار | دستور |
|---|---|
| به‌روزرسانی کد | `git pull && docker compose up -d --build` |
| مشاهده‌ی لاگ | `docker compose logs -f web` |
| پشتیبان دیتابیس | `docker compose exec db pg_dump -U atlas atlas > backup.sql` |
| پشتیبان فایل‌های آپلودی | `docker run --rm -v atlas_media_files:/m -v $PWD:/b alpine tar czf /b/media.tgz -C /m .` |
| بارگذاری دوباره‌ی محتوای اولیه* | `docker compose exec web python manage.py load_client_content` |

\* این دستور متن‌ها و اطلاعات شرکت را به نسخه‌ی اولیه برمی‌گرداند؛ فقط در صورت نیاز اجرا شود.

نام volume ها با نام پوشه‌ی پروژه شروع می‌شود (`docker volume ls`).

## ۶. استقرار بدون Docker

```bash
sudo apt install python3.12-venv postgresql nginx certbot python3-certbot-nginx
sudo useradd --system --home /srv/atlas atlas
# کد پروژه در /srv/atlas
cd /srv/atlas
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.production.example .env        # DB_HOST=localhost
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py load_client_content
.venv/bin/python manage.py createsuperuser
sudo chown -R atlas:www-data /srv/atlas

sudo cp deploy/atlas-gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now atlas-gunicorn

sudo cp deploy/nginx/atlas-aim.com.host.conf /etc/nginx/sites-available/atlas-aim.com
sudo ln -s /etc/nginx/sites-available/atlas-aim.com /etc/nginx/sites-enabled/
sudo certbot --nginx -d atlas-aim.com -d www.atlas-aim.com
sudo nginx -t && sudo systemctl reload nginx
```

پیش از اجرای certbot، دیتابیس و کاربر PostgreSQL را مطابق `.env` بسازید:

```bash
sudo -u postgres psql -c "CREATE USER atlas WITH PASSWORD '...';"
sudo -u postgres psql -c "CREATE DATABASE atlas OWNER atlas;"
```

## ۷. فهرست فایل‌های استقرار

| فایل | کاربرد |
|---|---|
| `Dockerfile` | ایمیج Django + Gunicorn (کاربر غیر root) |
| `docker-compose.yml` | سرویس‌های db، web و nginx |
| `docker/entrypoint.sh` | انتظار برای دیتابیس، migrate، collectstatic، بارگذاری محتوا |
| `deploy/nginx/atlas.conf` + `atlas-locations.inc` | nginx داخل Docker |
| `deploy/nginx/atlas-aim.com.host.conf` | nginx روی خود سرور، با SSL (بدون Docker) |
| `deploy/atlas-gunicorn.service` | سرویس systemd برای Gunicorn (بدون Docker) |
| `.env.production.example` | نمونه‌ی متغیرهای محیطی تولید |
| `content/client/` | تصاویر، کاتالوگ‌ها و فایل‌های کارفرما که در نخستین اجرا بارگذاری می‌شوند |
