import os
import logging

def get_config():
    config = {
        'BITGET_API_KEY': os.getenv('BITGET_API_KEY'),
        'BITGET_SECRET': os.getenv('BITGET_SECRET'),
        'BITGET_PASSWORD': os.getenv('BITGET_PASSWORD'),
        'GATEIO_API_KEY': os.getenv('GATEIO_API_KEY'),
        'GATEIO_SECRET': os.getenv('GATEIO_SECRET'),
        'DISCORD_WEBHOOK_URL': os.getenv('DISCORD_WEBHOOK_URL'),
    }
    
    # Check if critical keys are missing
    missing = [k for k, v in config.items() if not v]
    if missing:
        logging.error(f"❌ Missing Secrets in GitHub: {', '.join(missing)}")
        
    return config
