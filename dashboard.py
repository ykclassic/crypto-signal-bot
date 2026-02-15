import sqlite3
import pandas as pd
import os

def generate_dashboard(db_path="signals.db"):
    if not os.path.exists(db_path):
        print("❌ Database not found. Run the bot first!")
        return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM signals", conn)
    conn.close()

    if df.empty:
        print("ℹ️ Database is empty. No stats to show.")
        return

    # Calculate Stats
    total_scans = len(df)
    elite_signals = len(df[df['is_aligned'] == 1])
    win_count = len(df[df['status'] == 'CLOSED_TP'])
    loss_count = len(df[df['status'] == 'CLOSED_SL'])
    
    # Simple Win Rate Calculation
    total_closed = win_count + loss_count
    win_rate = (win_count / total_closed * 100) if total_closed > 0 else 0

    html_content = f"""
    <html>
    <head>
        <title>Crypto Bot Dashboard</title>
        <style>
            body {{ font-family: sans-serif; background: #121212; color: white; padding: 40px; }}
            .card-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ background: #1e1e1e; padding: 20px; border-radius: 10px; flex: 1; text-align: center; border: 1px solid #333; }}
            .value {{ font-size: 2em; font-weight: bold; color: #00ff88; }}
            table {{ width: 100%; border-collapse: collapse; background: #1e1e1e; }}
            th, td {{ padding: 12px; border-bottom: 1px solid #333; text-align: left; }}
            th {{ background: #252525; }}
            .status-tp {{ color: #00ff88; font-weight: bold; }}
            .status-sl {{ color: #ff4444; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>🚀 Crypto Signal Intelligence Dashboard</h1>
        <div class="card-container">
            <div class="card"><div class="label">Total Scans</div><div class="value">{total_scans}</div></div>
            <div class="card"><div class="label">Elite Signals</div><div class="value">{elite_signals}</div></div>
            <div class="card"><div class="label">Win Rate</div><div class="value">{win_rate:.1f}%</div></div>
            <div class="card"><div class="label">Active Trades</div><div class="value">{len(df[df['status'] == 'OPEN'])}</div></div>
        </div>
        <h2>Latest Signals</h2>
        {df.tail(10).to_html(index=False, classes='table')}
    </body>
    </html>
    """
    
    with open("report.html", "w") as f:
        f.write(html_content)
    print("✅ Dashboard generated: report.html")

if __name__ == "__main__":
    generate_dashboard()
