import discord
import datetime
import humanize
import pkg_resources
from lavalink import node
from tabulate import tabulate
from redbot.core import commands
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS, menu
from redbot.core.utils.chat_formatting import (
    box,
)

async def parse_llnode_stat(stats: node.NodeStats, stat_name: str):
    stat = getattr(stats, stat_name)
    if isinstance(stat, int) and stat_name.startswith("memory_"):
        stat = humanize.naturalsize(stat, binary=True)
    if stat_name == "uptime":
        stat = chat.humanize_timedelta(seconds=stat / 1000)
    if "load" in stat_name:
        stat = f"{round(stat*100, 2)} %"
    return stat

class Utility(commands.Cog):
    """Random utility will be in this cog."""

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.has_permissions(embed_links=True)
    @commands.group(invoke_without_command=True)
    async def statsinfo(self,ctx):
        """This shows some botstats."""
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        latency = self.bot.latency * 1000
        version = pkg_resources.get_distribution('discord.py').version
        servers = str(len(self.bot.guilds))
        users = str(len(self.bot.users))
        emb = discord.Embed(title=f"Botstats of {self.bot.user.name}:", color=discord.Color.green())
        emb.add_field(name="Ping:", value=chat.box(str(round(latency)) + " ms"))
        emb.add_field(name="Servers:", value=chat.box(servers))
        emb.add_field(name='Members:', inline=False, value=chat.box(f'{total_members} total\n{total_unique} unique'))
        emb.add_field(name='Channels:', value=chat.box(f'{text + voice} total\n{text} text\n{voice} voice'))
        emb.set_footer(text=f'discord.py v{version}')
        emb.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=emb)

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.has_permissions(embed_links=True)
    @statsinfo.command(hidden=True)
    async def t(self,ctx):
        """Shows some more stats."""
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        shards = [f"Shard {shard + 1}/{self.bot.shard_count}: {round(pingt * 1000)}ms\n" for shard, pingt in self.bot.latencies]
        latency = self.bot.latency * 1000
        version = pkg_resources.get_distribution('discord.py').version
        servers = str(len(self.bot.guilds))
        users = str(len(self.bot.users))
        emb = discord.Embed(title=f"Botstats of {self.bot.user.name}:", color=discord.Color.green())
        emb.add_field(name="Ping:", value=chat.box(str(round(latency)) + " ms"))
        emb.add_field(name="Servers:", value=chat.box(servers))
        emb.add_field(name='Members:', inline=False, value=chat.box(f'{total_members} total\n{total_unique} unique'))
        emb.add_field(name='Channels:', inline=False, value=chat.box(f'{text + voice} total\n{text} text\n{voice} voice'))
        emb.add_field(name="Shards:", value=box("".join(shards)))
        emb.set_footer(text=f'discord.py v{version}')
        emb.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=emb)

    @commands.command()
    @commands.is_owner()
    async def llnodestats(self, ctx):
        """Lavalink nodestats"""
        nodes = node.get_nodes_stats()
        if not nodes:
            await ctx.send(chat.info("This cog requires the Audio cog to be loaded to show nodestats."))
            return
        stats = [stat for stat in dir(nodes[0]) if not stat.startswith("_")]
        tabs = []
        for i, n in enumerate(nodes, start=1):
            tabs.append(
                f"Node {i}/{len(nodes)}\n"
                + chat.box(
                    tabulate(
                        [
                            (
                                stat.replace("_", " ").title(),
                                await parse_llnode_stat(n, stat),
                            )
                            for stat in stats
                        ],
                    ),
                    "ml",
                )
            )
        await menu(ctx, tabs, DEFAULT_CONTROLS)
