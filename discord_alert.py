import logging
from discord import Embed, SyncWebhook

class DiscordAlerter:
    def __init__(self, webhook_url):
        """
        Initializes the synchronous webhook.
        If the URL is missing, it will log a warning.
        """
        self.webhook = None
        if webhook_url:
            try:
                self.webhook = SyncWebhook.from_url(webhook_url)
            except Exception as e:
                logging.error(f"Failed to initialize Discord Webhook: {e}")
        else:
            logging.warning("No DISCORD_WEBHOOK_URL provided. Alerts are disabled.")

    def send_new_signal(self, signal, entry, sl, tp):
        """Formats and sends a high-visibility trading signal embed."""
        if not self.webhook:
            return

        try:
            # Color 0x00ff00 is Green for 'New Signal'
            embed = Embed(title="🚀 New Signal Detected", color=0x00ff00)
            embed.add_field(name="Ticker", value=signal.get('ticker', 'Unknown'), inline=True)
            embed.add_field(name="Side", value=signal.get('side', 'N/A').upper(), inline=True)
            embed.add_field(name="Type", value=signal.get('type', 'N/A'), inline=True)
            embed.add_field(name="Entry", value=f"{entry:.4f}", inline=True)
            embed.add_field(name="SL", value=f"{sl:.4f}", inline=True)
            embed.add_field(name="TP", value=f"{tp:.4f}", inline=True)
            
            confidence = signal.get('confidence', 0)
            embed.add_field(name="Confidence", value=f"{confidence*100:.0f}%", inline=False)
            
            self.webhook.send(embed=embed)
        except Exception as e:
            logging.error(f"Discord send_new_signal failed: {e}")

    def send_update(self, message):
        """Sends a standard notification for trade updates or closures."""
        if not self.webhook:
            return

        try:
            # Color 0x3498db is Blue for 'Update'
            embed = Embed(title="🔔 Signal Update", description=message, color=0x3498db)
            self.webhook.send(embed=embed)
        except Exception as e:
            logging.error(f"Discord send_update failed: {e}")
