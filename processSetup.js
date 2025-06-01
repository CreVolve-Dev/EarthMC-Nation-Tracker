const path = require('path');
const fs = require('fs');

const venvPython = path.resolve(__dirname, 'bot', 'bot-venv', 'bin', 'python3');

const config = {
  apps : [{
    name   : "earthmc-nation-tracker",
    script : "main.py",
    cwd    : "./bot/",
    interpreter : venvPython,
    env    : {
       BOT_TOKEN: "Insert your token here"
    }
  }]
};

fs.writeFileSync('pm2.config.js', 'module.exports = ' + JSON.stringify(config, null, 2));
console.log('PM2 config generated');