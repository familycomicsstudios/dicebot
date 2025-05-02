import discord
from discord import app_commands
import random
import re
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class RollType(discord.Enum):
    NORMAL = "normal"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"

@tree.command(name="roll", description="Roll dice in the format xdy+z (e.g., 2d6+3)")
@app_commands.describe(
    expression="Dice like 2d6+3 or just d20",
    mode="Roll with advantage or disadvantage?"
)
@app_commands.choices(mode=[
    app_commands.Choice(name="Normal", value="normal"),
    app_commands.Choice(name="Advantage", value="advantage"),
    app_commands.Choice(name="Disadvantage", value="disadvantage"),
])
async def roll(interaction: discord.Interaction, expression: str, mode: app_commands.Choice[str] = None):
    # Allow shorthand like "d20" to mean "1d20"
    expression = expression.replace(" ", "")
    if expression.startswith("d") and expression[1:].isdigit():
        expression = "1" + expression

    match = re.fullmatch(r"(\d+)d(\d+)([+-]\d+)?", expression)
    if not match:
        await interaction.response.send_message("❌ Invalid format. Use xdy+z like 2d6+3 or d20.")
        return


    num_dice = int(match[1])
    sides = int(match[2])
    modifier = int(match[3]) if match[3] else 0
    mode_value = mode.value if mode else "normal"

    if num_dice <= 0 or sides <= 0 or num_dice > 100:
        await interaction.response.send_message("❌ Use reasonable values (1-100 dice, sides > 0).")
        return

    def do_roll():
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        return rolls, sum(rolls) + modifier

    if mode_value == "advantage":
        roll1, total1 = do_roll()
        roll2, total2 = do_roll()
        chosen = (roll1, total1) if total1 >= total2 else (roll2, total2)
        result = f"🎲 You rolled with **Advantage**: {expression}\n"
        result += f"First roll: {roll1} => {sum(roll1)}\n"
        result += f"Second roll: {roll2} => {sum(roll2)}\n"
        result += f"**Chosen total: {chosen[1]}**"
    elif mode_value == "disadvantage":
        roll1, total1 = do_roll()
        roll2, total2 = do_roll()
        chosen = (roll1, total1) if total1 <= total2 else (roll2, total2)
        result = f"🎲 You rolled with **Disadvantage**: {expression}\n"
        result += f"First roll: {roll1} => {sum(roll1)}\n"
        result += f"Second roll: {roll2} => {sum(roll2)}\n"
        result += f"**Chosen total: {chosen[1]}**"
    else:
        rolls, total = do_roll()
        result = f"🎲 You rolled: {expression}\n"
        result += f"Rolls: {rolls} => {sum(rolls)}"
        if modifier:
            result += f" {'+' if modifier > 0 else '-'} {abs(modifier)}"
        result += f"\n**Total: {total}**"

    await interaction.response.send_message(result)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Game(name="D&D"))
    print(f"Bot is ready. Logged in as {client.user}")


# Replace with your bot's token
client.run(TOKEN)
