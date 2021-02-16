start:
	python3 main.py

load:
	source envs/local.env

shell:
	pipenv shell

install:
	pipenv install

requirements:
	pip install -r requirements.txt

envs:
	mkdir -p envs && echo "export DISCORD_TOKEN=\"YOUR_DISCORD_TOKEN\"\nexport DISCORD_GUILD=\"YOUR_DISCORD_GUILD\"\nexport REDDIT_USER=\"YOUR_REDDIT_USER\"\nexport REDDIT_PASSWORD=\"YOUR_REDDIT_PASSWORD\"\nexport CLIENT_ID=\"YOUR_CLIENT_ID\"\nexport CLIENT_SECRET=\"YOUR_CLIENT_SECRET\"\nexport ADMIN_ROLE_ID=\"YOUR_ADMIN_ROLE_ID\"\nexport CHANNEL_TO_POST_ID=\"YOUR_CHANNEL_TO_POST_ID\"\nexport CHANNEL_LOGS_ID=\"YOUR_CHANNEL_LOGS_ID\"\n" >> envs/local.env