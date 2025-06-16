import os

DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_CONFIG = {
  "connections": {
    "default": f"{DATABASE_URL}"
  },
  "apps": {
    "models": {
      "models": ["models.serverConfiguration", "models.nationData"],
      "default_connection": "default"
    }
  }
}