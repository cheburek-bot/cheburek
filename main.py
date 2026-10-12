import io
import os
import random
import re
from pathlib import Path

import discord
from dotenv import load_dotenv

from markov_chain import MarkovChain
from meme_generator import MemeGenerator

load_dotenv()

chain = MarkovChain()
meme_gen = MemeGenerator()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"🥟 Logged in as {bot.user}!")


@bot.event
async def on_message(ctx: discord.Message):
    if ctx.author.bot or not ctx.guild:
        return

    # Clean up and process the words

    clean_content = re.sub(
        r"https?:\/\/[^\s)\]]+",
        "",
        ctx.content,
    )
    clean_content = re.sub(r"<@!?\d+>", "", clean_content)
    clean_content = re.sub(r"\s+", " ", clean_content).strip()

    words = clean_content.split(" ")
    chain.process_words(words, ctx.guild.id)

    # Save image attachments

    image_dir = Path(f"./data/{ctx.guild.id}/images")
    image_dir.mkdir(parents=True, exist_ok=True)

    new_images = 0

    allowed_types = {"image/png", "image/jpeg", "image/webp"}

    for a in ctx.attachments:
        if a.content_type in allowed_types:
            await a.save(image_dir / str(a.id))
            new_images += 1

    if new_images > 0:
        print(f"🌅 {new_images} new image(s) from {ctx.author} ({ctx.guild.name})")

    # Reply when someone mentioned/replied to bot

    mentioned = bot.user in ctx.mentions

    replied = (
        ctx.reference is not None
        and isinstance(ctx.reference.resolved, discord.Message)
        and ctx.reference.resolved.author == bot.user
    )

    if mentioned or replied:
        try:
            message = chain.generate_message(random.randint(2, 12), ctx.guild.id)
            await ctx.reply(message)
        except Exception as e:
            print("Failed to reply a message:", e)
    else:
        # Try a chance to generate and send a message

        if random.random() < float(os.environ["MESSAGE_CHANCE"]):
            try:
                message = chain.generate_message(random.randint(2, 12), ctx.guild.id)
                await ctx.channel.send(message)
            except Exception as e:
                print("Failed to send message:", e)


class GenerateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🔁 Перегенерировать", style=discord.ButtonStyle.primary)
    async def regenerate(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if not interaction.guild_id:
            return

        await interaction.response.defer()

        message = chain.generate_message(random.randint(2, 12), interaction.guild_id)

        await interaction.edit_original_response(
            content=message, attachments=[], view=self
        )

    @discord.ui.button(label="👴 Жак Фреско", style=discord.ButtonStyle.secondary)
    async def fresco(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()

        if not interaction.message:
            return

        img = meme_gen.create_fresco(interaction.message.content)

        with io.BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)

            await interaction.followup.send(
                file=discord.File(fp=image_binary, filename="fresco.png"),
            )


@bot.command(
    description="Generate a message",
    description_localizations={"ru": "Сгенерировать сообщение"},
)
async def generate(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    if chain.get_words_count(interaction.guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    message = chain.generate_message(random.randint(2, 12), interaction.guild_id)

    await interaction.response.send_message(message, view=GenerateView())


@bot.command(
    description="Generate a Jacque Fresco meme",
    description_localizations={"ru": "Сгенерировать мем Жак Фреско"},
)
async def fresco(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    await interaction.response.defer()

    if chain.get_words_count(interaction.guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    message = chain.generate_message(random.randint(2, 8), interaction.guild_id)
    img = meme_gen.create_fresco(message)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        await interaction.respond(
            file=discord.File(fp=image_binary, filename="fresco.png")
        )


@bot.command(
    description="Generate a demotivator",
    description_localizations={"ru": "Сгенерировать демотиватор"},
)
async def demotivator(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    await interaction.response.defer()

    images_dir = Path(f"./data/{interaction.guild_id}/images")
    images_dir.mkdir(parents=True, exist_ok=True)

    images = os.listdir(images_dir)

    if len(images) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Изображений не найдено! Отправьте больше изображений и повторите попытку.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    if chain.get_words_count(interaction.guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    message = chain.generate_message(random.randint(2, 8), interaction.guild_id)
    image = f"./data/{interaction.guild_id}/images/{random.choice(images)}"

    img = meme_gen.create_demotivator(message, image)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        await interaction.respond(
            file=discord.File(fp=image_binary, filename="demotivator.png")
        )


@bot.command(
    description="Generate a meme",
    description_localizations={"ru": "Сгенерировать мем"},
)
async def meme(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    await interaction.response.defer()

    images_dir = Path(f"./data/{interaction.guild_id}/images")
    images_dir.mkdir(parents=True, exist_ok=True)

    images = os.listdir(images_dir)

    if len(images) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Изображений не найдено! Отправьте больше изображений и повторите попытку.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    if chain.get_words_count(interaction.guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    image = f"./data/{interaction.guild_id}/images/{random.choice(images)}"

    message1 = chain.generate_message(random.randint(2, 5), interaction.guild_id)
    message2 = chain.generate_message(random.randint(2, 5), interaction.guild_id)

    img = meme_gen.create_meme(message1, message2, image)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        await interaction.respond(
            file=discord.File(fp=image_binary, filename="meme.png")
        )


@bot.command(
    description="Display bot stats",
    description_localizations={"ru": "Показать статистику"},
)
async def stats(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    words = chain.get_words_count(interaction.guild_id)
    links = chain.get_links_count(interaction.guild_id)

    images_dir = Path(f"./data/{interaction.guild_id}/images")
    images_dir.mkdir(parents=True, exist_ok=True)

    images = len(os.listdir(images_dir))

    if interaction.guild:
        name = interaction.guild.name
    else:
        name = interaction.guild_id

    embed = discord.Embed(
        title=f"Статистика ({name})",
        description="Количество изученных данных",
        color=discord.Color.orange(),
    )

    embed.add_field(name="📖 Слова", value=f"{words} слов")
    embed.add_field(name="🔗 Связи", value=f"{links} связей")
    embed.add_field(name="🌅 Картинки", value=f"{images} картинок")

    await interaction.response.send_message(embed=embed)


bot.run(os.environ["TOKEN"])
