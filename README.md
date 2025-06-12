# Django Starter with Bootstrap 5, Font Awesome 6, Vite for Packages

A personal Django starter template with:

- Django 5.2
- The essentials of an Auth workflow
- Bootstrap 5 via SCSS
- Font Awesome 6 Free via CDN (for now, because I can't be bothered with webfonts 404)
- Vite for fast bundling (JS & SCSS)
- Static and media files set up (ready for production)
- Simple translation toggler (can delete or add django-modeltranslation on top of it for a complete solution)
- Extra utility filters/components/widgets/functions/payment methods... (most things are centralized in accounts app)
- Used some django 3rd party packages (django-htmlmin, django-ratelimit...)

---

**Note:** You must create a `.env` file from the start.

<details>
<summary>Example <code>.env</code> file</summary>

```env
EMAIL_HOST_USER="fake@fake.fake"
DEFAULT_FROM_EMAIL="fake@fake.fake"
EMAIL_HOST_PASSWORD="fake app password"
EMAIL_PORT=587

DJANGO_IS_PRODUCTION=False
# You can use: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DJANGO_SECRET_KEY="django-insecure-r01(sc^4!ugxu##tmb*q&5l!@o7tejc3#%50mh9nn6od3hss#c"
DJANGO_ADMIN_EMAIL_1=""

DB_TYPE='sqlite'
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
# Use "db" if Django is run inside Docker, else "host.docker.internal" or "localhost"
DB_HOST=localhost
DB_PORT=5432

FLOUCI_APP_SECRET=''
FLOUCI_APP_TOKEN=''

PAYMEE_API_KEY=''

```
</details>

## 📦 Install Dependencies

```bash
git clone "https://github.com/rynBenAmor/django-starter-bt5.git"
cd django-starter-bt5

npm install
npx vite build # this will auto create a BASE_DIR / 'static/'

python manage.py collectstatic --noinput --clear # optional
python manage.py migrate
python manage.py runserver
```