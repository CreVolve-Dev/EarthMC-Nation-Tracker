import os
from urllib.parse import urlparse


def validate_database_url(url):
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")

    parsed = urlparse(url)
    if parsed.scheme != 'postgres':
        raise ValueError("DATABASE_URL must use postgres:// scheme")

    return parsed


DATABASE_URL = validate_database_url(os.getenv("DATABASE_URL"))

DATABASE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
              "user": DATABASE_URL.username,
              "password": DATABASE_URL.password,
              "host": DATABASE_URL.hostname,
              "port": DATABASE_URL.port,
              "database": DATABASE_URL.path[1:],

              "minsize": 5,
              "maxsize": 10,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.serverConfiguration", "models.nationData"],
            "default_connection": "default"
        }
    }
}