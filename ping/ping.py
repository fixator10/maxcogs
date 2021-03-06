import time
import random
import discord

from redbot.core import checks, Config, commands
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.chat_formatting import (
    box,
)

old_ping = None

QUOTES = [
    "Seven billion people in the world trying to fit in.",
    "Dreams don’t work unless you do.",
    "The purpose of our lives is to be happy",
    "Money and success don’t change people",
]

class Ping(commands.Cog):
    """Reply with latency of bot"""

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return
    
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        global old_ping
        if old_ping:
            try:
                self.bot.remove_command("ping")
            except:
                pass
            self.bot.add_command(old_ping)

    @commands.has_permissions(embed_links=True)
    @commands.group(invoke_without_command=True)
    async def ping(self, ctx):
        """Reply with latency of bot."""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Pong !", color=discord.Color.red())
        emb.add_field(
            name="Discord WS:", value=chat.box(str(round(latency)) + " ms"),
        )
        emb.add_field(name="Message:", value=chat.box("…"))
        emb.add_field(name="Typing:", value=chat.box("…"))
        # Thanks preda and fixator.
        if len(self.bot.latencies) > 1:
            # The chances of this in near future is almost 0, but who knows, what future will bring to us?
            shards = [
                f"Shard {shard + 1}/{self.bot.shard_count}: {round(pingt * 1000)}ms"
                for shard, pingt in self.bot.latencies
            ]
            emb.add_field(name="Shards:", value=chat.box("\n".join(shards)))
        emb.set_footer(text=random.choice(QUOTES).format(author=ctx.author))

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000
        emb.colour = await ctx.embed_color()
        emb.set_field_at(
            1,
            name="Message:",
            value=chat.box(
                str(int((message.created_at - ctx.message.created_at).total_seconds() * 1000))
                + " ms"
            ),
        )
        emb.set_field_at(2, name="Typing:", value=chat.box(str(round(ping)) + " ms"))

        await message.edit(embed=emb)

    @commands.has_permissions(embed_links=True)
    @ping.command(hidden=True)
    async def t(self, ctx,):
        """Reply with more latency."""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Please wait..", color=discord.Color.red())
        emb.add_field(name="Discord WS:", value=box(str(round(latency)) + " ms"))
        emb.add_field(name="Typing", value=box("calculating" + " ms"))
        emb.add_field(name="Message", value=chat.box("…"))

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000

        #French people aren't that bad. At least preda is nice, to add shards option.
        shards = [f"Shard {shard + 1}/{self.bot.shard_count}: {round(pingt * 1000)}ms\n" for shard, pingt in self.bot.latencies]
        emb.add_field(name="Shards:", value=box("".join(shards)))
        emb.title = "Pong !"
        emb.color = discord.Color.green()
        emb.set_field_at(1, name="Message:", value=chat.box(str(int((message.created_at - ctx.message.created_at).total_seconds() * 1000)) + " ms"))
        emb.set_field_at(2, name="Typing:", value=chat.box(str(round(ping)) + " ms"))
        await message.edit(embed=emb)

def setup(bot):
    ping = Ping(bot)
    global old_ping
    old_ping = bot.get_command("ping")
    if old_ping:
        bot.remove_command(old_ping.name)
    bot.add_cog(ping)
