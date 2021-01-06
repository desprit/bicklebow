[![PyPI pyversions](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380)

Telegram bot that connects to your Tinkoff portoflio through the API, extracts open positions and allows you to create alerts on the market spikes.
To obtain TinkoffAPI token you have to be a client of Tinkoff Invest. More info [here](https://tinkoffcreditsystems.github.io/invest-openapi/)

![](https://github.com/desprit/bicklebow/blob/master/public/screenshots/mobile.jpg?raw=true | width=200)

# Installation (tested on Ubuntu 18.04)

First of all, make sure `python3.8` is installed. If not, follow [this article](https://linuxize.com/post/how-to-install-python-3-8-on-ubuntu-18-04/).

```sh
# Install PIP
sudo apt-get install python-pip
# Install virtualenv
sudo pip install virtualenv
# Create virtual environment
virtualenv -p python3.8 venv
# Activate it
source venv/bin/activate
# Install dependencies
pip install -r api/requirements.txt
# Initialize database
python api/src/database.py
```

Optionally create `.env` file in the root folder with the following content:

```sh
PYTHONPATH=PATH_TO_ROOT_FOLDER
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
