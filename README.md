# Django Starter with Bootstrap 5, Font Awesome 6, Vite for packages

a personal Django starter template with:

- Django 5.2
- Bootstrap 5 via SCSS
- Font Awesome 6 Free via cdn (for now cuz i cba with webfonts 404)
- Vite for fast bundling (JS & SCSS)
- Static and media files set up (ready for production)
- Simple translation toggler (can delete or add django-modeltranslation on top of it for a complete solution)

---
** Note that it forces you to create a .env from the get go **
example of a .env file:
``
    EMAIL_HOST_USER="fake@fake.fake"
    DEFAULT_FROM_EMAIL="fake@fake.fake"
    EMAIL_HOST_PASSWORD="fake app password"
    EMAIL_PORT=587

    DJANGO_IS_PRODUCTION=False
    #can use python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
    DJANGO_SECRET_KEY="django-insecure-r01(sc^4!ugxu##tmb*q&5l!@o7tejc3#%50mh9nn6od3hss#c"
    DJANGO_ADMIN_EMAIL_1=""

    DB_TYPE='sqlite'
    DB_NAME=''
    DB_USER=''
    DB_PASSWORD=''
    #or "db" if django is ran inside docker else "host.docker.internal" or "localhost"
    DB_HOST=localhost
    DB_PORT=5432
``
## 📦 Install Dependencies

```bash
git clone "https://github.com/rynBenAmor/django-starter-bt5.git"
cd django-starter-bt5

npm install
npx vite build #this will auto create a BASE_DIR / 'static/'

python manage.py collectstatic --noinput --clear #optional
python manage.py migrate
python manage.py runserver
```
