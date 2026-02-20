import sqlite3
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_dashboard(db_path="signals.db"):
    if not os.path.exists(db_path):
        logging.warning(f"❌ Database not found at {db_path}. Skipping dashboard generation.")
        return

    try:
        # Connect and fetch latest 50 logs
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM signals ORDER BY id DESC LIMIT 50"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            logging.info("📭 Database is empty. Nothing to display on dashboard.")
            return

        # Generate HTML Rows dynamically
        rows_html = ""
        for _, row in df.iterrows():
            # Color logic for Status
            status = str(row['status']).upper()
            status_color = "#4ade80" if status == "ELITE" else "#f87171"
            
            # Formatting the reason for readability
            reason = row['reason'] if row['reason'] else "No data"
            
            rows_html += f"""
            <tr>
                <td>{row['timestamp']}</td>
                <td><strong>{row['symbol']}</strong></td>
                <td style="color: {status_color}; font-weight: bold;">{status}</td>
                <td>{reason}</td>
                <td>{row['rsi']:.1f}</td>
                <td>{row['adx']:.1f}</td>
                <td>{row['regime_1h']}</td>
            </tr>
            """

        # Full HTML Template with CSS
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Elite Crypto Bot | Audit Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f1f5f9; padding: 20px; line-height: 1.6; }}
                .container {{ max-width: 1200px; margin: auto; }}
                header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 30px; }}
                h1 {{ color: #38bdf8; margin: 0; font-size: 24px; }}
                .status-tag {{ background: #1e293b; padding: 5px 15px; border-radius: 20px; font-size: 14px; border: 1px solid #334155; }}
                table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
                th {{ background: #334155; color: #38bdf8; text-align: left; padding: 15px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
                td {{ padding: 15px; border-bottom: 1px solid #334155; font-size: 14px; }}
                tr:last-child td {{ border-bottom: none; }}
                tr:hover {{ background: #2d3748; transition: 0.2s; }}
                .metric {{ font-family: 'Courier New', monospace; color: #94a3b8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🛡️ Trading Bot Audit Log</h1>
                    <div class="status-tag">Status: Live Monitoring</div>
                </header>
                
                <table>
                    <thead>
                        <tr>
                            <th>Time (UTC)</th>
                            <th>Pair</th>
                            <th>Verdict</th>
                            <th>Reasoning</th>
                            <th>RSI</th>
                            <th>ADX</th>
                            <th>1H Trend</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <p style="text-align: center; color: #64748b; font-size: 12px; margin-top: 30px;">
                    Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
                </p>
            </div>
        </body>
        </html>
        """

        with open("report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logging.info("✅ Dashboard generated successfully: report.html")

    except Exception as e:
        logging.error(f"❌ Failed to generate dashboard: {e}")

if __name__ == "__main__":
    # Use the DB_PATH environment variable if available
    target_db = os.getenv('DB_PATH', 'signals.db')
    generate_dashboard(target_db)
