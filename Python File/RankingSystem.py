import pandas as pd
import numpy as np
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
# Load the dataset
df = pd.read_csv("D:/TRADES_CopyTr_90D_ROI.csv")  # Update path if needed
# Ensure 'Trade_History' column is read as a string and parsed correctly
def safe_eval(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except (ValueError, SyntaxError):
        return None

df['Trade_History'] = df['Trade_History'].apply(safe_eval)
# Drop rows with invalid Trade_History
df = df.dropna(subset=['Trade_History']).reset_index(drop=True)
# Helper function to flatten the 'Trade_History'
def extract_trade_data(trade_history, port_id):
    trades = []
    for trade in trade_history:
        trade_data = trade.copy()
        trade_data['Port_IDs'] = port_id
        trades.append(trade_data)
    return trades
# Flatten trade data
all_trades = []
for _, row in df.iterrows():
    if isinstance(row['Trade_History'], list):
        all_trades.extend(extract_trade_data(row['Trade_History'], row['Port_IDs']))

df_trades = pd.DataFrame(all_trades)
# Step 1: Calculate PnL
df_trades['PnL'] = df_trades['realizedProfit']
# Step 2: Calculate ROI
df_trades['Investment'] = df_trades['quantity'] * df_trades['price']
df_trades['ROI'] = (df_trades['PnL'] / df_trades['Investment']).replace([np.inf, -np.inf], np.nan) * 100
# Step 3: Calculate Sharpe Ratio
sharpe_ratios = {}
for port_id, group in df_trades.groupby('Port_IDs'):
    mean_returns = group['PnL'].mean()
    std_dev_returns = group['PnL'].std()
    sharpe_ratios[port_id] = (mean_returns / std_dev_returns) if std_dev_returns != 0 else np.nan
# Step 4: Calculate Maximum Drawdown (MDD)
df_trades['cumulative_profit'] = df_trades.groupby('Port_IDs')['PnL'].cumsum()
df_trades['peak'] = df_trades.groupby('Port_IDs')['cumulative_profit'].cummax()
df_trades['drawdown'] = ((df_trades['cumulative_profit'] - df_trades['peak']) / df_trades['peak']).replace([np.inf, -np.inf], np.nan)
max_drawdowns = df_trades.groupby('Port_IDs')['drawdown'].min()
# Step 5: Calculate Win Rate and Win Positions
df_trades['Win'] = df_trades['PnL'] > 0
win_positions = df_trades.groupby('Port_IDs')['Win'].sum()
total_positions = df_trades.groupby('Port_IDs').size()
win_rates = (win_positions / total_positions).round(2)
# Step 6: Combine metrics for ranking
metrics = pd.DataFrame({
    'Port_IDs': win_positions.index,
    'Total_PnL': df_trades.groupby('Port_IDs')['PnL'].sum().round(3),
    'Total_ROI': df_trades.groupby('Port_IDs')['ROI'].mean().round(2),
    'Sharpe_Ratio': pd.Series(sharpe_ratios),
    'Max_Drawdown': max_drawdowns.round(2),
    'Win_Rate': win_rates,
    'Total_Positions': total_positions,
    'Win_Positions': win_positions
}).reset_index(drop=True)
# Weighted Scoring System
weights = {
    'Total_ROI': 0.3,
    'Total_PnL': 0.25,
    'Sharpe_Ratio': 0.2,
    'Win_Rate': 0.15,
    'Max_Drawdown': -0.1
}

for metric, weight in weights.items():
    metrics[metric + '_Score'] = metrics[metric] * weight

metrics['Rank_Score'] = metrics[[metric + '_Score' for metric in weights]].sum(axis=1)
# Rank accounts
metrics = metrics.sort_values(by='Rank_Score', ascending=False)
# Save metrics to CSV
output_file = 'D:/final_account_ranking.csv'
metrics.to_csv(output_file, index=False)
# Visualization
plt.figure(figsize=(18, 10))
sns.barplot(x=metrics['Port_IDs'].head(20), y=metrics['Rank_Score'].head(20), palette="viridis")
plt.title('Top 20 Accounts by Rank Score')
plt.xlabel('Port_IDs')
plt.ylabel('Rank Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Top 20 Accounts
top_20_accounts = metrics.head(20)
print(top_20_accounts)