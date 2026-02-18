import sqlite3
import pandas as pd
import os

permissions:
  contents: write
  pages: write      # Required for deployment
  id-token: write   # Required for security

def generate_dashboard(db_path="signals.db"):
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM signals ORDER BY id DESC LIMIT 50", conn)
    conn.close()

    # Dynamic CSS for the Audit Log
    rows_html = ""
    for _, row in df.iterrows():
        status_color = "#4ade80" if row['status'] == "ELITE" else "#f87171"
        rows_html += f"""
        <tr>
            <td>{row['timestamp']}</td>
            <td><b>{row['symbol']}</b></td>
            <td style="color: {status_color}; font-weight: bold;">{row['status']}</td>
            <td>{row['reason']}</td>
            <td>{row['rsi']:.1f}</td>
            <td>{row['adx']:.1f}</td>
        </tr>
        """

    html_content = f"""
    <html>
    <head>
        <title>Bot Performance Audit</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: white; padding: 40px; }}
            .container {{ max-width: 1100px; margin: auto; }}
            h1 {{ color: #38bdf8; }}
            table {{ width: 100%; border-collapse: collapse; background: #1e293b; margin-top: 20px; border-radius: 8px; overflow: hidden; }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #334155; }}
            th {{ background: #334155; color: #38bdf8; text-transform: uppercase; font-size: 0.8em; }}
            tr:hover {{ background: #2d3748; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Trading Bot Audit Log</h1>
            <p>Showing the last 50 market scans and rejection reasons.</p>
            <table>
                <thead>
                    <tr>
                        <th>Time</th><th>Symbol</th><th>Status</th><th>Reason for Decision</th><th>RSI</th><th>ADX</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    with open("report.html", "w") as f:
        f.write(html_content)
    print("✅ Audit Dashboard generated: report.html")

if __name__ == "__main__":
    generate_dashboard()
