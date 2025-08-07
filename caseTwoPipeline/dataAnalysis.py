import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Load historical data (replace paths if needed; auth_codes not used but loaded for completeness)
df_trans = pd.read_csv('transactions.csv')
df_auth = pd.read_csv('transactions_auth_codes.csv')

df_trans['timestamp'] = pd.to_datetime(df_trans['timestamp'])
df_auth['timestamp'] = pd.to_datetime(df_auth['timestamp'])

# Query to organize the data: Pivot to get counts per status per timestamp
df_pivot = df_trans.pivot_table(index='timestamp', columns='status', values='count', fill_value=0)

# Graphic to view data (historical; call plot_data() to show)
def plot_data():
    df_pivot.plot(figsize=(12, 6))
    plt.title('Transaction Counts by Status Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Count')
    plt.legend(title='Status')
    plt.show()

# Uncomment to plot historical data
# plot_data()

# Model: Compute historical stats (mean/std) for anomaly detection
bad_statuses = ['failed', 'reversed', 'denied']
stats = df_trans[df_trans['status'].isin(bad_statuses)].groupby('status')['count'].agg(['mean', 'std']).fillna(0)

# Anomaly check function (combination of rule-based and score-based)
def is_anomaly(status, count):
    if status not in bad_statuses:
        return False
    if status not in stats.index:
        return count > 0  # If no historical data, alert on any positive count
    mean = stats.loc[status, 'mean']
    std = stats.loc[status, 'std']
    threshold = mean + 3 * std
    return count > threshold

# System to report anomalies automatically (print for now; extend to email/Slack)
def report_anomaly(status, count, timestamp):
    message = f"ALERT: High number of '{status}' transactions detected at {timestamp}! Count: {count} (above normal threshold)."
    print(message)
    # Example extension: send email or notification
    # import smtplib  # Add email logic here if needed

# Endpoint: Receives transaction data, checks for anomaly, returns recommendation
@app.route('/alert', methods=['POST'])
def check_alert():
    data = request.json
    timestamp = data.get('timestamp', datetime.now().isoformat())
    status = data['status']
    count = data['count']
    
    if is_anomaly(status, count):
        report_anomaly(status, count, timestamp)
        return jsonify({"recommendation": "alert"})
    return jsonify({"recommendation": "no alert"})

if __name__ == '__main__':
    app.run(debug=True)