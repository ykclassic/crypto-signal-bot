import discord
from discord import Embed, SyncWebhook

class DiscordAlerter:
    def __init__(self, webhook_url):
        self.webhook = SyncWebhook.from_url(webhook_url)

    def send_new_signal(self, signal, entry, sl, tp):
        embed = Embed(title="🚀 New Signal Detected", color=0x00ff00)
        embed.add_field(name="Ticker", value=signal['ticker'], inline=True)
        embed.add_field(name="Side", value=signal['side'], inline=True)
        embed.add_field(name="Type", value=signal['type'], inline=True)
        embed.add_field(name="Entry", value=f"{entry:.4f}", inline=True)
        embed.add_field(name="SL", value=f"{sl:.4f}", inline=True)
        embed.add_field(name="TP", value=f"{tp:.4f}", inline=True)
        embed.add_field(name="Confidence", value=f"{signal['confidence']*100:.0f}%", inline=False)
        self.webhook.send(embed=embed)

    def send_update(self, message):
        embed = Embed(title="🔔 Signal Update", description=message, color=0x3498db)
        self.webhook.send(embed=embed)
