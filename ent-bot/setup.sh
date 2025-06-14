#!/bin/bash

set -e
echo "Beginning Setup Process"

if command -v python3 >/dev/null 2>&1 && command -v pip3 >/dev/null 2>&1; then
  echo "Python3 and pip3 are already installed. Skipping installation."
else
  echo "Installing Python3 and related packages..."
  sudo apt update
  sudo apt install -y python3 python3-pip python3-venv
fi

if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm are already installed. Skipping installation."
else
  echo "Installing Node.js and PM2..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt install -y nodejs
fi

if command -v pm2 >/dev/null 2>&1; then
  echo "PM2 is already installed. Skipping installation."
else
  echo "Installing PM2..."
  sudo npm install -g pm2 --silent
fi

read -rp "Enter your bot's token: " BOTTOKEN
read -rp "Enter your MySQL Database URL: " MYSQL_URL

python3 -m venv bot-venv
source bot-venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
deactivate

cat > pm2.config.js <<EOF
module.exports = {
  apps: [
    {
      name: "earthmc-nation-tracker",
      script: "main.py",
      cwd: "./",
      interpreter: "$(pwd)/bot-venv/bin/python3",
      env: {
        BOT_TOKEN: "${BOTTOKEN}"
      }
    }
  ]
};
EOF

cat > databaseConfig.json <<EOF
{
  "connections": {
    "default": "${MYSQL_URL}"
  },
  "apps": {
    "models": {
      "models": ["models.serverConfiguration", "models.nationData"],
      "default_connection": "default"
    }
  }
}
EOF
