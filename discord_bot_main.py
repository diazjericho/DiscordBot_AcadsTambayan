import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
from extensions.conversion import Conversion
import json

# Load the token from config.json
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    bot_token = config_data["token"]


# Initialize the bot with the required intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs for the logging channels
LOG_CHANNEL_ID = 1305895518391500850  # Replace with the main log channel ID
DURATION_CHANNEL_ID = 1306081482804301907  # Replace with the total time log channel ID

# Data tracking
user_join_times = {}  # Store join times for each user
call_start_time = None  # Start time of the call when the first user joins
call_active = False  # Flag to check if there's an active call


@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')


@bot.event
async def on_voice_state_update(member, before, after):
    global call_active, call_start_time
    timestamp = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    log_message = None

    # User joins a voice channel
    if before.channel is None and after.channel is not None:
        user_join_times[member.id] = datetime.now()  # Record join time
        log_message = f"[{timestamp}] - {member.mention} has joined **{after.channel.name}**."

        # Send individual duration log immediately
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(log_message)

        # If this is the first user joining, set the call start time
        if not call_active:
            call_active = True
            call_start_time = datetime.now()  # Start the call timer

    # User leaves a voice channel
    elif before.channel is not None and after.channel is None:
        # Calculate and log individual duration immediately
        if member.id in user_join_times:
            join_time = user_join_times.pop(member.id)
            duration = datetime.now() - join_time  # Calculate duration

            duration_str = Conversion.conversion_time(duration)

            # Determine leave reason based on activity
            if member.status == discord.Status.offline:
                log_message = (f"[{timestamp}] - {member.mention} has left **{before.channel.name}** and stayed for **{duration_str}**."
                               f"\n**Possible reason: Exited Discord application.**")
            else:
                spotify_activity = next(
                    (activity for activity in member.activities if isinstance(activity, discord.Spotify)), None)
                if spotify_activity:
                    song_title = spotify_activity.title
                    artist_name = spotify_activity.artist
                    log_message = (f"[{timestamp}] - {member.mention} has left **{before.channel.name}** and stayed for **{duration_str}**."
                                   f"\n**Possible reason: Listening to Spotify - '{song_title}' by {artist_name} or disconnected intentionally.**")
                else:
                    log_message = (f"[{timestamp}] - {member.mention} has left **{before.channel.name}** and stayed for **{duration_str}**."
                                   f"\n**Possible reason: Disconnected intentionally.**")

            # Send individual duration log immediately
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(log_message)

        # Check if all users have left after 5 seconds
        await check_empty_channel(before.channel)

    # User switches channels
    elif before.channel != after.channel:
        log_message = f"[{timestamp}] - {member.mention} has moved from {before.channel.name} to {after.channel.name}."
        user_join_times[member.id] = datetime.now()  # Reset join time


async def check_empty_channel(channel):
    await asyncio.sleep(2)  # Wait 2 seconds to confirm the channel is empty
    if len(channel.members) == 0:
        global call_active, call_start_time
        call_active = False
        end_timestamp = datetime.now() - timedelta(seconds=2)
        end_timestamp_final = end_timestamp.strftime("%m/%d/%Y %I:%M:%S %p")

        # Log the total call duration if there's time recorded
        if call_start_time:
            call_duration = datetime.now() - call_start_time
            # Subtract 2 seconds to account for async delays
            adjusted_duration = call_duration - timedelta(seconds=2)

            formatted_duration = Conversion.conversion_time(adjusted_duration)
            start_timestamp = call_start_time.strftime("%m/%d/%Y %I:%M:%S %p")

            # Send the total call time message
            duration_channel = bot.get_channel(DURATION_CHANNEL_ID)
            if duration_channel:
                await duration_channel.send(f"Time started: {start_timestamp}\n"
                                            f"Time ended: {end_timestamp_final}\n"
                                            f"Total call time: **{formatted_duration}**.")

        # Reset call_start_time for the next session
        call_start_time = None


# Run the bot with your token
bot.run(bot_token)