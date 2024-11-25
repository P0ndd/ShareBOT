import os
import random
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from server import server_on
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import asyncio


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# Set Thailand timezone
THAILAND_TZ = pytz.timezone('Asia/Bangkok')

# Function to generate a random number for the links
def generate_random_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

# Function to generate URLs with random numbers attached
def generate_aonatown_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/",
        "https://www.facebook.com/groups/289008456634964/",
        "https://www.facebook.com/groups/fivemthailandcommunity/",
    ]
    generated_links = [link + generate_random_number() for link in links]
    return generated_links

def generate_sevencity_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/posts/",
        "https://www.facebook.com/groups/289008456634964/posts/",
        "https://www.facebook.com/groups/255834148328219/posts/",
        "https://www.facebook.com/groups/fivemthailandcommunity/posts/",
        "https://www.facebook.com/groups/686633655307229/posts/"
    ]
    generated_links = [f"{link}{generate_random_number()}/" for link in links]
    return generated_links

# Dictionary to track button press cooldowns for each user
cooldowns = defaultdict(lambda: [0, 0])  # Default cooldowns for AONATOWN and SEVEN CITY

# Task to check and notify users when cooldown expires
@tasks.loop(minutes=1)
async def check_cooldown():
    current_time = discord.utils.utcnow().timestamp()
    for user_id, cooldowns_data in list(cooldowns.items()):
        try:
            aonatown_cooldown, sevencity_cooldown = cooldowns_data
            user = await bot.fetch_user(user_id)

            if aonatown_cooldown <= current_time and aonatown_cooldown != 0:
                if user:
                    await user.send(f"คูลดาวน์ของปุ่ม AONATOWN ของคุณหมดแล้ว! คุณสามารถกดปุ่มนี้ได้อีกครั้ง")
                cooldowns[user_id][0] = 0  # Reset AONATOWN cooldown

            if sevencity_cooldown <= current_time and sevencity_cooldown != 0:
                if user:
                    await user.send(f"คูลดาวน์ของปุ่ม SEVEN CITY ของคุณหมดแล้ว! คุณสามารถกดปุ่มนี้ได้อีกครั้ง")
                cooldowns[user_id][1] = 0  # Reset SEVEN CITY cooldown

        except discord.Forbidden:
            print(f"Unable to notify user ID {user_id}. They might have disabled DMs.")
        except Exception as e:
            print(f"Unexpected error for user ID {user_id}: {e}")

# Function to count users who interacted with the bot
def count_users():
    return len(cooldowns)

# Function to get users currently in cooldown
async def get_users_in_cooldown():
    current_time = discord.utils.utcnow().timestamp()
    users_in_cooldown = []
    for user_id, (aonatown_cd, sevencity_cd) in cooldowns.items():
        if aonatown_cd > current_time or sevencity_cd > current_time:
            try:
                user = await bot.fetch_user(user_id)
                if user:
                    users_in_cooldown.append(user.name)  # Use user.display_name for nickname
            except discord.NotFound:
                users_in_cooldown.append(f"Unknown User ({user_id})")
            except discord.Forbidden:
                users_in_cooldown.append(f"Private User ({user_id})")
            except Exception as e:
                users_in_cooldown.append(f"Error Fetching User ({user_id}): {e}")
    return users_in_cooldown

# Persistent View class with buttons and custom_id for persistence
class MyPersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view, never times out

    @discord.ui.button(label="AONA TOWN", style=discord.ButtonStyle.primary, custom_id="aonatown_button")
    async def aonatown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        if cooldowns[user_id][0] > current_time:
            remaining_time = cooldowns[user_id][0] - current_time
            finish_time = datetime.utcnow() + timedelta(seconds=remaining_time)
            finish_time_local = finish_time.replace(tzinfo=pytz.utc).astimezone(THAILAND_TZ)
            formatted_time = finish_time_local.strftime("%I:%M:%S %p")

            await interaction.response.send_message(
                f"Please wait another {int(remaining_time // 60)} minutes. Your AONATOWN cooldown will expire at {formatted_time} (Thailand time)",
                ephemeral=True
            )
            return

        generated_links = generate_aonatown_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"
        await interaction.response.send_message(result, ephemeral=True)

        cooldowns[user_id][0] = current_time + 7200  # 2 hours cooldown

    @discord.ui.button(label="SEVEN CITY", style=discord.ButtonStyle.primary, custom_id="sevencity_button")
    async def sevencity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        if cooldowns[user_id][1] > current_time:
            remaining_time = cooldowns[user_id][1] - current_time
            finish_time = datetime.utcnow() + timedelta(seconds=remaining_time)
            finish_time_local = finish_time.replace(tzinfo=pytz.utc).astimezone(THAILAND_TZ)
            formatted_time = finish_time_local.strftime("%I:%M:%S %p")

            await interaction.response.send_message(
                f"Please wait another {int(remaining_time // 60)} minutes. Your SEVEN CITY cooldown will expire at {formatted_time} (Thailand time)",
                ephemeral=True
            )
            return

        generated_links = generate_sevencity_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"
        await interaction.response.send_message(result, ephemeral=True)

        cooldowns[user_id][1] = current_time + 3600  # 1 hour cooldown

    @discord.ui.button(label="Total Users", style=discord.ButtonStyle.secondary, custom_id="total_users_button")
    async def total_users_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_users = count_users()
        await interaction.response.send_message(f"Total users who interacted with the bot: {total_users}", ephemeral=True)

    @discord.ui.button(label="Users in Cooldown", style=discord.ButtonStyle.secondary, custom_id="users_in_cooldown_button")
    async def users_in_cooldown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        users_in_cooldown = await get_users_in_cooldown()
        if users_in_cooldown:
            user_list = "\n".join(users_in_cooldown)
            await interaction.response.send_message(
                f"Users currently in cooldown:\n```\n{user_list}\n```", ephemeral=True
            )
        else:
            await interaction.response.send_message("No users are currently in cooldown.", ephemeral=True)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready')

    bot.add_view(MyPersistentView())
    print("Persistent view added")

    check_cooldown.start()

    for user_id in cooldowns.keys():
        try:
            user = await bot.fetch_user(user_id)
            if user:
                await user.send("บอทกลับมาออนไลน์แล้ว คุณสามารถใช้งานได้ตามปกติ 🎉")
            await asyncio.sleep(1)  # Avoid hitting rate limits
        except discord.Forbidden:
            print(f"Unable to send private message to user ID {user_id}.")
        except Exception as e:
            print(f"Unexpected error while notifying user ID {user_id}: {e}")

# Command to generate and send the embed with buttons
@bot.command()
async def generate_embed(ctx):
    try:
        await ctx.message.delete()

        embed = discord.Embed(
            title="สร้างลิงค์แชร์ Facebook",
            color=0x00ff00
        )
        embed.add_field(name="AONA TOWN", value="Get your AONA TOWN links", inline=False)
        embed.add_field(name="SEVEN CITY", value="Get your SEVEN CITY links", inline=False)
        embed.add_field(name="Info", value="Check total users and cooldowns", inline=False)

        await ctx.send(embed=embed, view=MyPersistentView())
    except Exception as e:
        print(f"Error in generate_embed command: {e}")

# Start the bot
server_on()
bot.run(os.getenv('TOKEN'))
