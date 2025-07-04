![Logo](https://i.imgur.com/0ih5Uv0.png)

EMC Nation Tracker (ENT) is a disnake bot focused around making it easier for EarthMC players to track what happens within their nations. It aims to better integrate EarthMC with Discord by showing things such as citizens joining and leaving your nation, who is online, and keeping track of who in your Discord is verified as a citizen.
### Invite the Bot to Your Server:

Invite the bot here: https://discord.com/oauth2/authorize?client_id=1376977555546050650
## Features

- See current relationships with other nations with /information relations  
![information](https://i.imgur.com/uisBvzW.gif)
- Get notified on when people leave and join your nation in a dedicated notifications channel  
![notification](https://i.imgur.com/RNzrVak.png)
- Ensure the integrity of your citizens by verifying them on your Discord automatically  
![verify](https://i.imgur.com/I5I1kyR.gif)
- See who is online at any time by having an Online Players embed in your Discord  
![embed](https://i.imgur.com/TdJrgZV.png)
## Commands

Information:
- /configuration settings -> See the current settings for your server such as your notifications channel and who you are tracking.
- /configure nation -> Sets the default nation for your server which is needed for some commands
- /information relations -> Check to see the enemies and allies of a particular nation

Notifications:
- /notification channel -> Set the channel in which notifications will appear for nations you track
- /notification status -> Enable/Disable notifications for your server
- /notifications add -> Add a nation to track in your notifications
- /notifications remove -> Remove a nation from tracking

Online Players Embeds:
- /embed add -> Create a new embed message in the current channel which will then turn into the Online Player Embed after some time (Cannot have more than one nation at a time)
- /embed remove -> Destroy the current Online Embed making it no longer update

Verifications:
- /verify add -> Link a Discord user and a Minecraft user together on your server
- /verify remove -> Unlink a Discord and Minecraft user
- /verify check -> See what Minecraft username a Discord user is linked to
- /verify configure -> Turn a verification setting on/off
## Installation

### DROPLET OR VM:
Clone the repository in your desired directory:
```bash
git clone https://github.com/CreVolve-Dev/EarthMC-Nation-Tracker.git
cd EarthMC-Nation-Tracker
```

Run the setup script for your operating system:
```bash
# Mac or Linux
./setup.sh

# Windows
./windowsSetup.bat
```

By default, the bot is running on PM2 so you can use PM2 commands:
```bash
pm2 start earthmc-nation-tracker # Start the bot

pm2 stop earthmc-nation-tracker # Stop the bot

pm2 restart earthmc-nation-tracker # Restart the bot

pm2 logs earthmc-nation-tracker # See the bot logs
```

### APP PLATFORM:
Use this repository as your model to deploy and set the working directory:
```bash
https://github.com/CreVolve-Dev/EarthMC-Nation-Tracker.git
/ent-bot # Working Directory
```

Set your environment variables:
```bash
# Get your bot's token in the Discord Application Portal
BOT_TOKEN="BOT TOKEN HERE"

# MUST be a MySQL url: mysql://username:password@cool-database-host.com:port/database-name
DATABASE_URL="DATABASE URL HERE" 
```

Set the build and run commands:
```bash
# Build Command:
./setup.sh

# Run Command:
python3 ./main.py
```
## Contributing

Thank you for wanting to contribute to this project!  
For major changes to the bot open an issue first then talk about what you want changed.

For smaller things such as bug fixes or tweaks:
- Fork the Repo
- Apply your changes
- Test your changes thoroughly
- Send a merge request

PLEASE: Test your changes before sending in merge requests. I don't want to spend hours debugging your code...
## Roadmap

- ~~Add a feature to verifications to automatically check the API to see whether a user is actually a member of a nation~~ - Done
- ~~Add a way to set a "default nation" for a server so when you don't specify a target it is automatically assumed~~ - Done
- ~~Add more notification events such as towns leaving or joining and other nations changing their relationship with you~~ - Done
- Allow multiple OnlineEmbeds as well as letting you choose which channel and whether they are enabled/disabled - In Progress
## Authors

- [@CreVolve](https://github.com/CreVolve-Dev) - Lead Developer
