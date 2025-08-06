import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Load CSVs
df1 = pd.read_csv('checkout_1.csv')
df1['dataset'] = 'checkout_1'
df2 = pd.read_csv('checkout_2.csv')
df2['dataset'] = 'checkout_2'
df = pd.concat([df1, df2], ignore_index=True)

# Extract hour as integer for sorting
df['hour'] = df['time'].str.replace('h', '').astype(int)

# Create SQLite connection and load data
conn = sqlite3.connect(':memory:')  # In-memory database
df.to_sql('checkouts', conn, index=False, if_exists='replace')

# SQL query for anomalies
query = """
SELECT 
    time,
    today,
    avg_last_month,
    today / (avg_last_month + 0.1) AS ratio_to_avg,
    dataset,
    hour,
    CASE 
        WHEN (today / (avg_last_month + 0.1) < 0.5 AND avg_last_month > 10) 
        OR (today / (avg_last_month + 0.1) > 2 AND avg_last_month > 10) 
        OR (today = 0 AND avg_last_month > 10) 
        THEN 1 
        ELSE 0 
    END AS is_anomaly
FROM checkouts
WHERE is_anomaly = 1
ORDER BY dataset, hour;
"""
anomalies = pd.read_sql_query(query, conn)

# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Plot for checkout_1
df1_sorted = df[df['dataset'] == 'checkout_1'].sort_values('hour')
ax1.plot(df1_sorted['hour'], df1_sorted['today'], label='Today', marker='o')
ax1.plot(df1_sorted['hour'], df1_sorted['avg_last_month'], label='Avg Last Month', linestyle='--')
anomalies_1 = anomalies[anomalies['dataset'] == 'checkout_1']
ax1.scatter(anomalies_1['hour'], anomalies_1['today'], color='red', s=100, label='Anomalies', zorder=5)
ax1.set_title('Checkout 1: Today vs. Avg Last Month')
ax1.set_ylabel('Checkouts')
ax1.legend()
ax1.grid(True)

# Plot for checkout_2
df2_sorted = df[df['dataset'] == 'checkout_2'].sort_values('hour')
ax2.plot(df2_sorted['hour'], df2_sorted['today'], label='Today', marker='o')
ax2.plot(df2_sorted['hour'], df2_sorted['avg_last_month'], label='Avg Last Month', linestyle='--')
anomalies_2 = anomalies[anomalies['dataset'] == 'checkout_2']
ax2.scatter(anomalies_2['hour'], anomalies_2['today'], color='red', s=100, label='Anomalies', zorder=5)
ax2.set_title('Checkout 2: Today vs. Avg Last Month')
ax2.set_xlabel('Hour of Day')
ax2.set_ylabel('Checkouts')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('anomaly_plot.png')
plt.show()

# Close connection
conn.close()

# Print anomalies for reference
print(anomalies[['time', 'today', 'avg_last_month', 'ratio_to_avg', 'dataset', 'is_anomaly']])
