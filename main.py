import os
import random
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from server import server_on
from datetime import datetime, timedelta
import pytz  # Import pytz for timezone conversion

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# Set Thailand timezone
THAILAND_TZ = pytz.timezone('Asia/Bangkok')

# Function to generate a random number for the links
def generate_random_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

# Function to generate URLs with random numbers attached
def generate_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/",
        "https://www.facebook.com/groups/289008456634964/",
        "https://www.facebook.com/groups/fivemthailandcommunity/"
        "https://www.facebook.com/groups/fivemofficiathailand/posts/"
    ]

    generated_links = []
    for link in links:
        random_number = generate_random_number()
        full_link = link + random_number
        generated_links.append(full_link)
    return generated_links

# Dictionary to track button press cooldowns for each user
cooldowns = {}

# Task to check and notify users when cooldown expires
@tasks.loop(minutes=1)
async def check_cooldown():
    current_time = discord.utils.utcnow().timestamp()
    for user_id, cooldown_time in list(cooldowns.items()):
        if cooldown_time <= current_time:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    # ส่งข้อความส่วนตัว (DM) แทนการส่งในห้องแชท
                    await user.send(f"คูลดาวน์ของคุณหมดแล้ว! คุณสามารถโปรโมทได้อีกครั้ง")
                except discord.Forbidden:
                    print(f"ไม่สามารถส่งข้อความส่วนตัวไปยัง {user.name} ได้")
            del cooldowns[user_id]  # ลบผู้ใช้จากคูลดาวน์ลิสต์


# Persistent View class with a button and custom_id for persistence
class MyPersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view, never times out

    @discord.ui.button(label="Generate URLs", style=discord.ButtonStyle.primary, custom_id="generate_urls_button")
    async def generate_urls_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        # Check if the user is on cooldown
        if user_id in cooldowns and cooldowns[user_id] > current_time:
            remaining_time = cooldowns[user_id] - current_time
            finish_time = datetime.utcnow() + timedelta(seconds=remaining_time)
            
            # Convert finish time to Thailand timezone
            finish_time_local = finish_time.replace(tzinfo=pytz.utc).astimezone(THAILAND_TZ)
            formatted_time = finish_time_local.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
            
            await interaction.response.send_message(
                f"กรุณารออีก {int(remaining_time // 60)} นาที คูลดาวน์จะหมดตอน {formatted_time} (เวลาไทย)", ephemeral=True
            )
            return

        # Generate URLs and send the result
        generated_links = generate_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"

        await interaction.response.send_message(result, ephemeral=True)

        # Set the cooldown for the user (2 hours = 7200 seconds)
        cooldowns[user_id] = current_time + 7200

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready')

    # Add the persistent view when the bot starts up
    bot.add_view(MyPersistentView())
    print("Persistent view added")

    # Start the cooldown checking task
    check_cooldown.start()

# Command to generate and send the embed with a button
@bot.command()
async def generate_embed(ctx):
    # Delete the user's command message
    await ctx.message.delete()

    embed = discord.Embed(
        title="สร้างลิงค์แชร์ Facebook",
        description="AONA TOWN",
        color=0x00ff00
    )

    # Send the message with the persistent button
    await ctx.send(embed=embed, view=MyPersistentView())

# Start the bot
server_on()
bot.run(os.getenv('TOKEN'))  # Use environment variable for token
