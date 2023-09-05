import praw
import os
import discord
import random as r
import json
from urllib.request import urlopen

DC_TOKEN = os.environ['TOKEN']

# Initialise PRAW with account information
reddit = praw.Reddit(
    client_id = os.environ['reddit_client_id'],
    client_secret = os.environ['reddit_client_secret'],
    user_agent = os.environ['reddit_user_agent'],
    check_for_async=False
)

# Function to make an embed with the best posts of a given subreddit
# Subreddit - What subreddit
# posts_lim - How many posts to choose from
# comments_lim - How many comments to display

def getbestpost(subreddit, posts_lim, comments_lim):
  # Get some top posts from a subreddit to choose from
  submissions = list(reddit.subreddit(subreddit).hot(limit=posts_lim))
  sub = subreddit.lower()
  # Get a random post from the chosen top posts
  # Skip NSFW Posts
  i = submissions[r.randint(0, posts_lim-1)]
  if i.over_18:
    embed = discord.Embed(title="No NSFW posts for ya 😏 child 😏", color=0xFF0000)
    print ("NSFW Post, skipping...")
    return embed
  print("Post: " + i.title) # Title of the post

  # Sort comments from best
  i.comment_sort = "best"

  # Get comments to display
  i.comment_limit = comments_lim

  # Create embed with the OP's name on subreddit, with a link to the original post on reddit
  embed = discord.Embed(title=i.title, description = "**" + i.selftext + "**" , url="https://www.reddit.com"+i.permalink, color=0xff4500)
  # u/AUTHOR on SUBREDDIT, with the sub's icon.
  embed.set_author(name= "u/" + str(i.author) + " on r/" + subreddit + ":", icon_url=reddit.subreddit(subreddit).icon_img)

  # Images in the post
  # Read the post JSON
  json_url = "https://www.reddit.com"+i.permalink+".json"
  json_data = urlopen(json_url).read().decode('utf-8')
  post_json = json.loads(json_data)

  # Get image or gif embed, if any.
  try:
    # Parse the json for the image link
    img_link = (post_json[0]["data"]["children"][0]["data"]["url_overridden_by_dest"])
    print ("Image url: " + img_link)
    embed.set_image(url=img_link)
  except KeyError as err:
    print ("No media embed found, continuing...")
  
  # Loop through the list of comments and add a field to our embed
  for topcomment in i.comments:
    if isinstance(topcomment, praw.models.MoreComments):
      continue
    print("- " + topcomment.body)

    # Prevent adding messages longer than max discord embed field length
    if len(topcomment.body) < 1024:
      embed.add_field(name=str("u/" + str(topcomment.author)),
                    value=topcomment.body,
                    inline=False)
    else:
      embed.add_field(name=str("u/" + str(topcomment.author)),
                    value="*`comment too long to display`*",
                    inline=False)
        
  # Return the embed
  return embed


class MyClient(discord.Client):

  async def on_ready(self):
    print(f'Logged in as {self.user} (ID: {self.user.id})')
    print('------')

  async def on_message(self, message):
    # we do not want the bot to reply to itself
    if message.author.id == self.user.id:
      return

    if message.content.startswith('!reddit '):
      subreddit = message.content.removeprefix("!reddit ")

      await message.reply(embed = getbestpost(subreddit, 20 , 5), mention_author=True)


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DC_TOKEN)
