# Cookiecutter Django REST API

A Cookiecutter template for creating production-ready Django REST API projects quickly.

This is a fork of [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django) that focuses exclusively on building REST APIs with Django REST Framework.

## Features

- Django REST Framework for API development
- JWT Authentication with dj-rest-auth
- Optional Social Authentication (Google, Facebook, Twitter, Apple)
- API Documentation with DRF Spectacular
- Arabic language support
- All the great features from Cookiecutter Django

## Usage

First, make sure you have cookiecutter installed:

```bash
pip install cookiecutter
```

Now you can generate a new Django REST API project:

```bash
cookiecutter gh:ayman-abdulhadi/cookiecutter-django-rest-api
```

You'll be prompted for some values. Provide them, then a Django REST API project will be created for you.

## Options

- `use_jwt_auth`: Whether to use JWT authentication with dj-rest-auth
- `use_social_auth`: Whether to include social authentication
- `social_auth_providers`: Which social authentication providers to include (Google, Facebook, Twitter, Apple, or All)
- `include_docs`: Whether to include Sphinx documentation setup

## Credits

This project is based on [Cookiecutter Django](https://github.com/cookiecutter/cookiecutter-django) by Daniel Roy Greenfeld and contributors.

## License

Same as Cookiecutter Django: BSD license
