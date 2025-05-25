# {{cookiecutter.project_name}}

{{ cookiecutter.description }}

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django%20REST%20API-ff69b4.svg?logo=cookiecutter)](https://github.com/yourusername/cookiecutter-django-rest-api/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

{%- if cookiecutter.open_source_license != "Not open source" %}

License: {{cookiecutter.open_source_license}}
{%- endif %}

## API-First Django Project

This project is built as an API-first Django application using Django REST Framework. It's designed to serve as a backend for modern frontend frameworks or mobile applications.

## Features

- Django REST Framework for API development
{%- if cookiecutter.use_jwt_auth == 'y' %}
- JWT Authentication with dj-rest-auth
{%- endif %}
{%- if cookiecutter.use_social_auth == 'y' %}
- Social Authentication ({% if cookiecutter.social_auth_providers == 'Google' %}Google{% elif cookiecutter.social_auth_providers == 'Facebook' %}Facebook{% elif cookiecutter.social_auth_providers == 'Twitter' %}Twitter{% elif cookiecutter.social_auth_providers == 'Apple' %}Apple{% elif cookiecutter.social_auth_providers == 'All' %}Google, Facebook, Twitter, Apple{% endif %})
{%- endif %}
- API Documentation with DRF Spectacular
{%- if cookiecutter.use_celery == "y" %}
- Celery for background tasks
{%- endif %}
{%- if cookiecutter.use_sentry == "y" %}
- Sentry integration for error tracking
{%- endif %}

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## API Endpoints

{%- if cookiecutter.use_jwt_auth == 'y' %}
### Authentication Endpoints

- `/api/auth/login/` - Log in and obtain JWT token
- `/api/auth/logout/` - Log out and invalidate JWT token
- `/api/auth/token/refresh/` - Refresh JWT token
- `/api/auth/user/` - Retrieve/update the current user
- `/api/auth/password/change/` - Change user password
- `/api/auth/password/reset/` - Reset user password
- `/api/auth/registration/` - Register a new user

{%- if cookiecutter.use_social_auth == 'y' %}
### Social Authentication Endpoints

{%- if cookiecutter.social_auth_providers == 'Google' or cookiecutter.social_auth_providers == 'All' %}
- `/api/auth/google/` - Authenticate with Google
{%- endif %}
{%- if cookiecutter.social_auth_providers == 'Facebook' or cookiecutter.social_auth_providers == 'All' %}
- `/api/auth/facebook/` - Authenticate with Facebook
{%- endif %}
{%- if cookiecutter.social_auth_providers == 'Twitter' or cookiecutter.social_auth_providers == 'All' %}
- `/api/auth/twitter/` - Authenticate with Twitter
{%- endif %}
{%- if cookiecutter.social_auth_providers == 'Apple' or cookiecutter.social_auth_providers == 'All' %}
- `/api/auth/apple/` - Authenticate with Apple
{%- endif %}
{%- endif %}
{%- endif %}

### API Documentation

- `/api/docs/` - Swagger UI for API documentation
- `/api/schema/` - OpenAPI schema

## Basic Commands

### Setting Up Your Users

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

### Type checks

Running type checks with mypy:

    $ mypy {{cookiecutter.project_slug}}

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

{%- if cookiecutter.use_celery == "y" %}

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd {{cookiecutter.project_slug}}
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd {{cookiecutter.project_slug}}
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd {{cookiecutter.project_slug}}
celery -A config.celery_app worker -B -l info
```

{%- endif %}
{%- if cookiecutter.use_mailpit == "y" %}

### Email Server

{%- if cookiecutter.use_docker == "y" %}

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.
Please check [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`
{%- else %}

In development, it is often nice to be able to see emails that are being sent from your application. If you choose to use [Mailpit](https://github.com/axllent/mailpit) when generating the project a local SMTP server with a web interface will be available.

1.  [Download the latest Mailpit release](https://github.com/axllent/mailpit/releases) for your OS.

2.  Copy the binary file to the project root.

3.  Make it executable:

        $ chmod +x mailpit

4.  Spin up another terminal window and start it there:

        ./mailpit

5.  Check out <http://127.0.0.1:8025/> to see how it goes.

Now you have your own mail server running locally, ready to receive whatever you send it.

{%- endif %}

{%- endif %}
{%- if cookiecutter.use_sentry == "y" %}

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.
{%- endif %}

## Deployment

The following details how to deploy this application.
{%- if cookiecutter.use_heroku.lower() == "y" %}

### Heroku

See detailed [cookiecutter-django Heroku documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-on-heroku.html).

{%- endif %}
{%- if cookiecutter.use_docker.lower() == "y" %}

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).

{%- endif %}
