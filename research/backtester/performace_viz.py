import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns


def plot_performance(db_path="data/hft_nifty.db"):
    conn = sqlite3.connect(db_path)
    trades = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()

    if trades.empty:
        print("No trades found in database.")
        return

    trades['timestamp'] = pd.to_datetime(trades['timestamp'])
    trades['cum_pnl'] = trades['pnl'].cumsum()

    sns.set(style="darkgrid")
    plt.figure(figsize=(12, 6))

    # Cumulative PnL Curve
    plt.subplot(2, 1, 1)
    plt.plot(trades['timestamp'], trades['cum_pnl'], label='Cumulative PnL', color='green')
    plt.title('NIFTY ORB Strategy: Cumulative Equity Curve')
    plt.ylabel('PnL (INR)')
    plt.legend()

    # PnL Distribution
    plt.subplot(2, 1, 2)
    sns.histplot(trades['pnl'], kde=True, color='blue', bins=20)
    plt.title('Trade PnL Distribution')
    plt.xlabel('PnL per Trade')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_performance()