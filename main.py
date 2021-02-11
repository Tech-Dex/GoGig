#! usr/bin/env python3
import asyncpraw
import pprint
import time
import discord
import os
import sys
import asyncio

reddit = asyncpraw.Reddit(client_id=f'{os.getenv("CLIENT_ID")}',
                          client_secret=f'{os.getenv("CLIENT_SECRET")}',
                          user_agent='Reddit Job Finder Discord Bot',
                          username=f'{os.getenv("REDDIT_USER")}',
                          password=f'{os.getenv("REDDIT_PASSWORD")}')

pp = pprint.PrettyPrinter(indent=4)
name_subreddit_list = ['forhire', 'jobbit', 'freelance_forhire', 'RemoteJobs']
sent_submission_id_list = list()
keyword_job_list = ['dev', 'junior', 'mid', 'intermediate', 'senior', 'software',
                    'backend', 'frontend', 'fullstack', 'web',
                    'java', 'python', 'javascript', 'typescript', 'node', 'nodejs', 'deno', 'denojs',
                    'angular', 'react', 'vue', 'django', 'flask', 'fastapi', 'spring', 'boot']

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == DISCORD_GUILD:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
            )
        else:
            sys.exit("The bot is not linked to the Guild you declared")


def build_discord_embed_message(submission):
    description = submission.selftext
    if len(description) > 2048:
        description = submission.selftext[:2044] + '...'
    embed = discord.Embed(title=f'{submission.title}',
                          color=discord.Colour(0x82de09),
                          url=f'https://www.reddit.com{submission.permalink}',
                          description=f'{description}',
                          )
    embed.set_image(url=f'')
    embed.set_thumbnail(url=f'')
    embed.set_author(name=f'{submission.author.name}')
    embed.set_footer(text=f'Subreddit {submission.subreddit_name_prefixed} '
                          f'| {time.strftime("%a %b %d, %Y at %H:%M:%S", time.gmtime(submission.created_utc))}')
    try:
        embed.set_thumbnail(url=f'{submission.preview["images"][0]["source"]["url"]}')
    except AttributeError:
        pass
    embed.add_field(name=f'👍', value=f'{submission.ups}', inline=True)
    embed.add_field(name=f'👎', value=f'{submission.downs}', inline=True)
    embed.add_field(name=f'💬', value=f'{submission.num_comments}', inline=True)

    return embed


async def send_discord_message(submission):
    channel = client.get_channel(736319558285131788)

    await channel.send(embed=build_discord_embed_message(submission))
    # print(f'Link : https://www.reddit.com{submission.permalink}')


async def search_subreddits():
    await client.wait_until_ready()
    while True:
        for subreddit_name in name_subreddit_list:
            subreddit = await reddit.subreddit(subreddit_name)
            async for submission in subreddit.new(limit=10):
                for keyword_job in keyword_job_list:
                    if (keyword_job in submission.permalink or keyword_job in submission.selftext) \
                            and submission.link_flair_text == 'Hiring' \
                            and submission.id not in sent_submission_id_list:
                        await send_discord_message(submission)
                        sent_submission_id_list.append(submission.id)
        await asyncio.sleep(10)


client.loop.create_task(search_subreddits())
client.run(DISCORD_TOKEN)
