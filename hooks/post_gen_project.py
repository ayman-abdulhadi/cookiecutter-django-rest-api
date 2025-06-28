"""
NOTE:
    This script is run after the project is generated.
    This script:
        1. Removes files depending on the user's input
"""
import json
import random
import shutil
import string
import os
import sys
from pathlib import Path

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

DEBUG_VALUE = "debug"

# Get the root project directory
PROJECT_DIRECTORY = Path.cwd().absolute()
DOCS_DIRECTORY = PROJECT_DIRECTORY / "docs"

def remove_open_source_files():
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        Path(file_name).unlink()


def remove_gplv3_files():
    file_names = ["COPYING"]
    for file_name in file_names:
        Path(file_name).unlink()


def remove_custom_user_manager_files():
    users_path = Path("{{cookiecutter.project_slug}}", "users")
    (users_path / "managers.py").unlink()
    (users_path / "tests" / "test_managers.py").unlink()


def remove_pycharm_files():
    idea_dir_path = Path(".idea")
    if idea_dir_path.exists():
        shutil.rmtree(idea_dir_path)

    docs_dir_path = Path("docs", "pycharm")
    if docs_dir_path.exists():
        shutil.rmtree(docs_dir_path)


def remove_docker_files():
    shutil.rmtree(".devcontainer")
    shutil.rmtree("compose")

    file_names = [
        "docker-compose.local.yml",
        "docker-compose.production.yml",
        ".dockerignore",
        "justfile",
    ]
    for file_name in file_names:
        Path(file_name).unlink()
    if "{{ cookiecutter.editor }}" == "PyCharm":
        file_names = ["docker_compose_up_django.xml", "docker_compose_up_docs.xml"]
        for file_name in file_names:
            Path(".idea", "runConfigurations", file_name).unlink()


def remove_nginx_docker_files():
    shutil.rmtree(Path("compose", "production", "nginx"))


def remove_utility_files():
    shutil.rmtree("utility")


def remove_heroku_files():
    file_names = ["Procfile", "requirements.txt"]
    for file_name in file_names:
        if file_name == "requirements.txt" and "{{ cookiecutter.ci_tool }}".lower() == "travis":
            # don't remove the file if we are using travisci but not using heroku
            continue
        Path(file_name).unlink()
    shutil.rmtree("bin")


def remove_sass_files():
    sass_path = Path("{{cookiecutter.project_slug}}", "static", "sass")
    if sass_path.exists():
        shutil.rmtree(sass_path)


def remove_gulp_files():
    file_names = ["gulpfile.mjs"]
    for file_name in file_names:
        if Path(file_name).exists():
            Path(file_name).unlink()


def remove_webpack_files():
    webpack_path = Path("webpack")
    if webpack_path.exists():
        shutil.rmtree(webpack_path)
    remove_vendors_js()


def remove_vendors_js():
    vendors_js_path = Path("{{ cookiecutter.project_slug }}", "static", "js", "vendors.js")
    if vendors_js_path.exists():
        vendors_js_path.unlink()


def remove_packagejson_file():
    file_names = ["package.json"]
    for file_name in file_names:
        if Path(file_name).exists():
            Path(file_name).unlink()


def update_package_json(remove_dev_deps=None, remove_keys=None, scripts=None):
    remove_dev_deps = remove_dev_deps or []
    remove_keys = remove_keys or []
    scripts = scripts or {}
    package_json = Path("package.json")
    content = json.loads(package_json.read_text())
    for package_name in remove_dev_deps:
        content["devDependencies"].pop(package_name)
    for key in remove_keys:
        content.pop(key)
    content["scripts"].update(scripts)
    updated_content = json.dumps(content, ensure_ascii=False, indent=2) + "\n"
    package_json.write_text(updated_content)


def handle_js_runner(choice, use_docker, use_async):
    if choice == "Gulp":
        update_package_json(
            remove_dev_deps=[
                "@babel/core",
                "@babel/preset-env",
                "babel-loader",
                "concurrently",
                "css-loader",
                "mini-css-extract-plugin",
                "postcss-loader",
                "postcss-preset-env",
                "sass-loader",
                "webpack",
                "webpack-bundle-tracker",
                "webpack-cli",
                "webpack-dev-server",
                "webpack-merge",
            ],
            remove_keys=["babel"],
            scripts={
                "dev": "gulp",
                "build": "gulp build",
            },
        )
        remove_webpack_files()
    elif choice == "Webpack":
        scripts = {
            "dev": "webpack serve --config webpack/dev.config.js",
            "build": "webpack --config webpack/prod.config.js",
        }
        remove_dev_deps = [
            "browser-sync",
            "cssnano",
            "gulp",
            "gulp-concat",
            "gulp-imagemin",
            "gulp-plumber",
            "gulp-postcss",
            "gulp-rename",
            "gulp-sass",
            "gulp-uglify-es",
        ]
        if not use_docker:
            dev_django_cmd = (
                "uvicorn config.asgi:application --reload" if use_async else "python manage.py runserver_plus"
            )
            scripts.update(
                {
                    "dev": "concurrently npm:dev:*",
                    "dev:webpack": "webpack serve --config webpack/dev.config.js",
                    "dev:django": dev_django_cmd,
                }
            )
        else:
            remove_dev_deps.append("concurrently")
        update_package_json(remove_dev_deps=remove_dev_deps, scripts=scripts)
        remove_gulp_files()


def remove_prettier_pre_commit():
    pre_commit_yaml = Path(".pre-commit-config.yaml")
    content = pre_commit_yaml.read_text().splitlines()

    removing = False
    new_lines = []
    for line in content:
        if removing and "- repo:" in line:
            removing = False
        if "mirrors-prettier" in line:
            removing = True
        if not removing:
            new_lines.append(line)

    pre_commit_yaml.write_text("\n".join(new_lines))


def remove_celery_files():
    file_paths = [
        Path("config", "celery_app.py"),
        Path("{{ cookiecutter.project_slug }}", "users", "tasks.py"),
        Path("{{ cookiecutter.project_slug }}", "users", "tests", "test_tasks.py"),
    ]
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def remove_async_files():
    file_paths = [
        Path("config", "asgi.py"),
        Path("config", "websocket.py"),
    ]
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink()


def remove_dottravisyml_file():
    Path(".travis.yml").unlink()


def remove_dotgitlabciyml_file():
    Path(".gitlab-ci.yml").unlink()


def remove_dotgithub_folder():
    shutil.rmtree(".github")


def remove_dotdrone_file():
    Path(".drone.yml").unlink()


def generate_random_string(length, using_digits=False, using_ascii_letters=False, using_punctuation=False):
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', "\\", "$"}
        suitable = all_punctuation.difference(unsuitable)
        symbols += "".join(suitable)
    return "".join([random.choice(symbols) for _ in range(length)])


def set_flag(file_path: Path, flag, value=None, formatted=None, *args, **kwargs):
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your "
                "system. Please, make sure to manually {} later.".format(flag)
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string

    with file_path.open("r+") as f:
        file_contents = f.read().replace(flag, value)
        f.seek(0)
        f.write(file_contents)
        f.truncate()

    return value


def set_django_secret_key(file_path: Path):
    django_secret_key = set_flag(
        file_path,
        "!!!SET DJANGO_SECRET_KEY!!!",
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_secret_key


def set_django_admin_url(file_path: Path):
    django_admin_url = set_flag(
        file_path,
        "!!!SET DJANGO_ADMIN_URL!!!",
        formatted="{}/",
        length=32,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_admin_url


def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)


def generate_postgres_user(debug=False):
    return DEBUG_VALUE if debug else generate_random_user()


def set_postgres_user(file_path, value):
    postgres_user = set_flag(file_path, "!!!SET POSTGRES_USER!!!", value=value)
    return postgres_user


def set_postgres_password(file_path, value=None):
    postgres_password = set_flag(
        file_path,
        "!!!SET POSTGRES_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return postgres_password


def set_celery_flower_user(file_path, value):
    celery_flower_user = set_flag(file_path, "!!!SET CELERY_FLOWER_USER!!!", value=value)
    return celery_flower_user


def set_celery_flower_password(file_path, value=None):
    celery_flower_password = set_flag(
        file_path,
        "!!!SET CELERY_FLOWER_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return celery_flower_password


def append_to_gitignore_file(ignored_line):
    with Path(".gitignore").open("a") as gitignore_file:
        gitignore_file.write(ignored_line)
        gitignore_file.write("\n")


def set_flags_in_envs(postgres_user, celery_flower_user, debug=False):
    local_django_envs_path = Path(".envs", ".local", ".django")
    production_django_envs_path = Path(".envs", ".production", ".django")
    local_postgres_envs_path = Path(".envs", ".local", ".postgres")
    production_postgres_envs_path = Path(".envs", ".production", ".postgres")

    set_django_secret_key(production_django_envs_path)
    set_django_admin_url(production_django_envs_path)

    set_postgres_user(local_postgres_envs_path, value=postgres_user)
    set_postgres_password(local_postgres_envs_path, value=DEBUG_VALUE if debug else None)
    set_postgres_user(production_postgres_envs_path, value=postgres_user)
    set_postgres_password(production_postgres_envs_path, value=DEBUG_VALUE if debug else None)

    set_celery_flower_user(local_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(local_django_envs_path, value=DEBUG_VALUE if debug else None)
    set_celery_flower_user(production_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(production_django_envs_path, value=DEBUG_VALUE if debug else None)


def set_flags_in_settings_files():
    set_django_secret_key(Path("config", "settings", "local.py"))
    set_django_secret_key(Path("config", "settings", "test.py"))


def remove_envs_and_associated_files():
    shutil.rmtree(".envs")
    Path("merge_production_dotenvs_in_dotenv.py").unlink()
    shutil.rmtree("tests")


def remove_celery_compose_dirs():
    shutil.rmtree(Path("compose", "local", "django", "celery"))
    shutil.rmtree(Path("compose", "production", "django", "celery"))


def remove_node_dockerfile():
    node_docker_path = Path("compose", "local", "node")
    if node_docker_path.exists():
        shutil.rmtree(node_docker_path)


def remove_aws_dockerfile():
    aws_docker_path = Path("compose", "production", "aws")
    if aws_docker_path.exists():
        shutil.rmtree(aws_docker_path)


def remove_drf_starter_files():
    """This function is now a no-op since we're making the entire app API-focused"""
    # We don't want to remove API files anymore
    pass


def remove_docs():
    """Remove documentation directory if include_docs is 'n'"""
    if "{{ cookiecutter.include_docs }}" == "n":
        if os.path.exists(DOCS_DIRECTORY):
            shutil.rmtree(DOCS_DIRECTORY)
        
        # Remove .readthedocs.yml file
        readthedocs_file = PROJECT_DIRECTORY / ".readthedocs.yml"
        if os.path.exists(readthedocs_file):
            os.remove(readthedocs_file)

        # Remove docker-compose.docs.yml file if it exists
        docker_docs_file = PROJECT_DIRECTORY / "docker-compose.docs.yml"
        if os.path.exists(docker_docs_file):
            os.remove(docker_docs_file)
            
        # Remove compose/local/docs folder if it exists
        compose_docs_dir = PROJECT_DIRECTORY / "compose" / "local" / "docs"
        if os.path.exists(compose_docs_dir):
            shutil.rmtree(compose_docs_dir)


def remove_frontend_related_files():
    """Remove frontend-related files and directories"""
    # Remove template directories
    templates_dir = Path("{{cookiecutter.project_slug}}", "templates")
    if templates_dir.exists():
        shutil.rmtree(templates_dir)
    
    # Remove static files directory - not needed for API-only
    static_dir = Path("{{cookiecutter.project_slug}}", "static")
    if static_dir.exists():
        shutil.rmtree(static_dir)
    
    # Clean up users app to be API-focused
    users_dir = Path("{{cookiecutter.project_slug}}", "users")
    if users_dir.exists():
        # Remove frontend-related files
        frontend_files = [
            "views.py",
            "urls.py",
            "context_processors.py",
            "adapters.py"
        ]
        for file_name in frontend_files:
            file_path = users_dir / file_name
            if file_path.exists():
                file_path.unlink()
        
        # Remove frontend-related test files
        tests_dir = users_dir / "tests"
        if tests_dir.exists():
            frontend_test_files = [
                "test_forms.py",
                "test_views.py",
                "test_urls.py",
                "test_admin.py"
            ]
            for file_name in frontend_test_files:
                file_path = tests_dir / file_name
                if file_path.exists():
                    file_path.unlink()
        
        # Remove the api directory - we'll move its contents to the main app
        api_dir = users_dir / "api"
        if api_dir.exists():
            shutil.rmtree(api_dir)
            
        # Create serializers.py
        serializers_content = """from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        {% if cookiecutter.username_type == "email" %}
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:users:detail", "lookup_field": "pk"},
        }
        {% else %}
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:users:detail", "lookup_field": "username"},
        }
        {% endif %}
"""
        (users_dir / "serializers.py").write_text(serializers_content)
            
        # Create views.py
        views_content = """from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import User
from .serializers import UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    {% if cookiecutter.username_type == "email" %}
    lookup_field = "pk"
    {% else %}
    lookup_field = "username"
    {% endif %}

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
"""
        (users_dir / "views.py").write_text(views_content)
        
        # Create urls.py
        urls_content = """from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings

from .views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("", UserViewSet)

app_name = "users"
urlpatterns = router.urls
"""
        (users_dir / "urls.py").write_text(urls_content)


def handle_language_files():
    """Replace Portuguese with Arabic language files"""
    locale_dir = Path("{{cookiecutter.project_slug}}", "locale")
    if locale_dir.exists():
        # Remove Portuguese locale
        pt_br_dir = locale_dir / "pt_BR"
        if pt_br_dir.exists():
            shutil.rmtree(pt_br_dir)
        
        # Remove French locale
        fr_fr_dir = locale_dir / "fr_FR"
        if fr_fr_dir.exists():
            shutil.rmtree(fr_fr_dir)
        
        # Make sure Arabic locale directory exists
        ar_dir = locale_dir / "ar"
        if not ar_dir.exists():
            ar_dir.mkdir(parents=True, exist_ok=True)
            ar_lc_dir = ar_dir / "LC_MESSAGES"
            ar_lc_dir.mkdir(parents=True, exist_ok=True)
    
    # Also check for locale files in the root directory
    root_locale_dir = Path("locale")
    if root_locale_dir.exists():
        # Remove Portuguese locale
        root_pt_br_dir = root_locale_dir / "pt_BR"
        if root_pt_br_dir.exists():
            shutil.rmtree(root_pt_br_dir)
        
        # Remove French locale
        root_fr_fr_dir = root_locale_dir / "fr_FR"
        if root_fr_fr_dir.exists():
            shutil.rmtree(root_fr_fr_dir)


def main():
    debug = "{{ cookiecutter.debug }}".lower() == "y"

    set_flags_in_envs(
        DEBUG_VALUE if debug else generate_random_user(),
        DEBUG_VALUE if debug else generate_random_user(),
        debug=debug,
    )
    set_flags_in_settings_files()

    if "{{ cookiecutter.open_source_license }}" == "Not open source":
        remove_open_source_files()
    if "{{ cookiecutter.open_source_license}}" != "GPLv3":
        remove_gplv3_files()

    if "{{ cookiecutter.username_type }}" == "username":
        remove_custom_user_manager_files()

    if "{{ cookiecutter.editor }}" != "PyCharm":
        remove_pycharm_files()

    if "{{ cookiecutter.use_docker }}".lower() == "y":
        remove_utility_files()
        if "{{ cookiecutter.cloud_provider }}".lower() != "none":
            remove_nginx_docker_files()
    else:
        remove_docker_files()

    if "{{ cookiecutter.use_docker }}".lower() == "y" and "{{ cookiecutter.cloud_provider}}" != "AWS":
        remove_aws_dockerfile()

    if "{{ cookiecutter.use_heroku }}".lower() == "n":
        remove_heroku_files()

    if "{{ cookiecutter.use_docker }}".lower() == "n" and "{{ cookiecutter.use_heroku }}".lower() == "n":
        if "{{ cookiecutter.keep_local_envs_in_vcs }}".lower() == "y":
            print(
                INFO + ".env(s) are only utilized when Docker Compose and/or "
                "Heroku support is enabled so keeping them does not make sense "
                "given your current setup." + TERMINATOR
            )
        remove_envs_and_associated_files()
    else:
        append_to_gitignore_file(".env")
        append_to_gitignore_file(".envs/*")
        if "{{ cookiecutter.keep_local_envs_in_vcs }}".lower() == "y":
            append_to_gitignore_file("!.envs/.local/")

    # Always remove frontend-related files
    remove_sass_files()
    remove_gulp_files()
    remove_webpack_files()
    remove_packagejson_file()
    remove_prettier_pre_commit()
    remove_frontend_related_files()
    
    if "{{ cookiecutter.use_docker }}".lower() == "y":
        remove_node_dockerfile()

    if "{{ cookiecutter.cloud_provider }}" == "None" and "{{ cookiecutter.use_docker }}".lower() == "n":
        print(
            WARNING + "You chose to not use any cloud providers nor Docker, "
            "media files won't be served in production." + TERMINATOR
        )

    if "{{ cookiecutter.use_celery }}".lower() == "n":
        remove_celery_files()
        if "{{ cookiecutter.use_docker }}".lower() == "y":
            remove_celery_compose_dirs()

    if "{{ cookiecutter.ci_tool }}" != "Travis":
        remove_dottravisyml_file()

    if "{{ cookiecutter.ci_tool }}" != "Gitlab":
        remove_dotgitlabciyml_file()

    if "{{ cookiecutter.ci_tool }}" != "Github":
        remove_dotgithub_folder()

    if "{{ cookiecutter.ci_tool }}" != "Drone":
        remove_dotdrone_file()

    if "{{ cookiecutter.use_drf }}".lower() == "n":
        remove_drf_starter_files()

    if "{{ cookiecutter.use_async }}".lower() == "n":
        remove_async_files()

    # Handle language files - replace Portuguese with Arabic
    handle_language_files()

    remove_docs()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()
