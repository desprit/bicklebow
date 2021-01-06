# Installation (tested on Ubuntu 18.04)

```sh
# Create virtual environment
virtualenv --no-site-packages -p python3.7 venv
# Activate it
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

Optionally create `.env` file in the root folder with the following content:

```sh
PYTHONPATH=/home/desprit/projects/desprit-media/bicklebow
ENVIRONMENT=testing
BOT_TOKEN=TOKEN_OBTAINED_FROM_BOT_FATHER
SERVER_IP=IP_ADDRESS_OF_YOUR_SERVER (only needed when using webhooks)
```

If you want to launch your bot on a remote server, consider using Telegram webhooks. More info on how to setup Nginx and create certificate in this [Medium article](https://medium.com/jj-innovative-results/how-to-create-a-simple-telegram-bot-in-python-using-nginx-and-gcp-926f1b0fb16f).

# Usage

```sh
# Run bot
python api/src/bot.py
```

Now connect to your bot though telegam, type `/start` to start conversation.

```sh
# Check triggers
python api/src/triggers.py USER_ID
```
