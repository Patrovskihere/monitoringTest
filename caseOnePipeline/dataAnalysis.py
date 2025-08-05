import pandas as pd  # Import Pandas

# Load your local CSVs (use your paths)
df1 = pd.read_csv('/home/patrick/Prog/monitoringTest/caseOnePipeline/checkout_1.csv')
df1['dataset'] = 'checkout_1'  # Add label
df2 = pd.read_csv('/home/patrick/Prog/monitoringTest/caseOnePipeline/checkout_2.csv')
df2['dataset'] = 'checkout_2'

# Combine into one DataFrame
df = pd.concat([df1, df2], ignore_index=True)

# Add columns for analysis
df['deviation_from_avg'] = df['today'] - df['avg_last_month']  # How much off from monthly avg
df['ratio_to_avg'] = df['today'] / df['avg_last_month']  # Ratio for spikes/drops

# Flag anomalies (custom rules: drops <50% or spikes >200% if avg >10, plus zeros in peaks)
df['is_anomaly'] = False
df.loc[(df['ratio_to_avg'] < 0.5) & (df['avg_last_month'] > 10), 'is_anomaly'] = True
df.loc[(df['ratio_to_avg'] > 2) & (df['avg_last_month'] > 10), 'is_anomaly'] = True
df.loc[(df['today'] == 0) & (df['avg_last_month'] > 10), 'is_anomaly'] = True

# Show flagged anomalies (time, today, avg, ratio, dataset)
print(df[df['is_anomaly']][['time', 'today', 'avg_last_month', 'ratio_to_avg', 'dataset', 'is_anomaly']])