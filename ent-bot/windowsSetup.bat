@echo off
setlocal enabledelayedexpansion
echo Beginning Setup Process

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Python is already installed. Skipping installation.
) else (
    echo Please install Python 3 manually from https://www.python.org/downloads/
    pause
    exit /b 1
)

where pip >nul 2>nul
if %ERRORLEVEL%==0 (
    echo pip is already installed. Skipping installation.
) else (
    echo pip not found. Installing pip...
    python -m ensurepip
)

where node >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Node.js is already installed. Skipping installation.
) else (
    echo Please install Node.js manually from https://nodejs.org/
    pause
    exit /b 1
)

where pm2 >nul 2>nul
if %ERRORLEVEL%==0 (
    echo PM2 is already installed. Skipping installation.
) else (
    echo Installing PM2...
    npm install -g pm2 --silent
)

set /p BOTTOKEN=Enter your bot's token:
set /p MYSQL_URL=Enter your MySQL Database URL:

python -m venv bot-venv
call bot-venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

call bot-venv\Scripts\deactivate.bat

set "VENV_PATH=%cd%\bot-venv\Scripts\python.exe"
> pm2.config.js (
    echo module.exports = {
    echo   apps: [
    echo     {
    echo       name: "earthmc-nation-tracker",
    echo       script: "main.py",
    echo       cwd: "./ent-bot/",
    echo       interpreter: "%VENV_PATH:\=\\%",
    echo       env: {
    echo         BOT_TOKEN: "%BOTTOKEN%"
    echo       }
    echo     }
    echo   ]
    echo };
)

> databaseConfig.json (
    echo {
    echo   "connections": {
    echo     "default": "%MYSQL_URL%"
    echo   },
    echo   "apps": {
    echo     "models": {
    echo       "models": ["models.serverConfiguration", "models.nationData"],
    echo       "default_connection": "default"
    echo     }
    echo   }
    echo }
)
