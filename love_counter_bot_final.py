import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

SAVE_FILE = "love_data.json"

# Load or initialize data
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
        love_count = data.get("count", 0)
        leaderboard = data.get("leaderboard", {})
        auto_daily = data.get("auto_daily", False)
        last_auto = data.get("last_auto", None)
else:
    love_count = 547
    leaderboard = {}
    auto_daily = False
    last_auto = None

def save_data():
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "count": love_count,
            "leaderboard": leaderboard,
            "auto_daily": auto_daily,
            "last_auto": last_auto
        }, f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_love_increase.start()

@bot.command()
async def love(ctx):
    global love_count

    button = discord.ui.Button(label="❤️ Add +1 Love", style=discord.ButtonStyle.primary)

    async def button_callback(interaction):
        global love_count
        user_id = str(interaction.user.id)
        love_count += 1
        leaderboard[user_id] = leaderboard.get(user_id, 0) + 1
        save_data()
        await interaction.response.edit_message(
            content=f"**Love Counter: {love_count} ❤️**\nLast added by: {interaction.user.mention}",
            view=view
        )

    button.callback = button_callback

    view = discord.ui.View()
    view.add_item(button)

    await ctx.send(f"**Love Counter: {love_count} ❤️**\nClick the button to add more love!", view=view)

@bot.command()
async def toggleauto(ctx):
    global auto_daily
    auto_daily = not auto_daily
    save_data()
    status = "activated ✅" if auto_daily else "deactivated ❌"
    await ctx.send(f"Daily auto-love increase is now **{status}**.")

@tasks.loop(hours=24)
async def daily_love_increase():
    global love_count, last_auto
    if auto_daily:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if last_auto != today:
            love_count += 1
            last_auto = today
            save_data()
            print(f"Auto-increased love to {love_count} on {today}")

@bot.command()
async def loveboard(ctx):
    if not leaderboard:
        await ctx.send("No love contributions yet! 💔")
        return
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    desc = ""
    for i, (uid, count) in enumerate(sorted_lb[:10], 1):
        user = await bot.fetch_user(int(uid))
        desc += f"{i}. {user.mention} — **{count}** ❤️\n"
    embed = discord.Embed(title="🏆 Love Leaderboard", description=desc, color=0xFF69B4)
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN_HERE")