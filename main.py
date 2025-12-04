import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

FILE_PATH = 'weather_data.csv'
NEW_FILE_PATH = 'cleaned_weather_data.csv'
REPORT_PATH = 'analysis_report.txt'
PLOT_DIR = 'plots'

report_content = "--- Weather Data Analysis Report ---\n"
report_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
os.makedirs(PLOT_DIR, exist_ok=True)

print("--- Task 1: Loading and Inspection ---")
try:
    df = pd.read_csv(FILE_PATH)
except FileNotFoundError:
    print(f"Error: The file '{FILE_PATH}' was not found. Please ensure it is in the same directory.")
    exit()

print("\n[1.1] DataFrame Head (First 5 Rows):")
print(df.head())

print("\n[1.2] DataFrame Info (Structure and Data Types):")
df.info()
print("\n[1.3] DataFrame Describe (Statistical Summary of Numerical Columns):")
description = df.describe().to_markdown()
print(description)
report_content += "Statistical Summary of Numerical Columns (Raw Data):\n"
report_content += description + "\n\n"

print("\n--- Task 2: Data Cleaning and Processing ---")
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df_cleaned = df.copy() 
print("[2.1] 'Date' column converted to datetime and set as index.")

missing_before = df_cleaned.isnull().sum().to_frame(name='Missing Count')
print(f"\n[2.2] Missing values before cleaning:\n{missing_before.to_markdown(numalign='left', stralign='left')}")
report_content += f"Missing values before cleaning:\n{missing_before.to_markdown(numalign='left', stralign='left')}\n"

df_cleaned['Rainfall_mm'].fillna(0.0, inplace=True)
mean_humidity = df_cleaned['Humidity_perc'].mean()
df_cleaned['Humidity_perc'].fillna(mean_humidity, inplace=True)
print(f"  > Missing 'Rainfall_mm' imputed with 0.0.")
print(f"  > Missing 'Humidity_perc' imputed with mean ({mean_humidity:.2f}).")

num_duplicates = df_cleaned.duplicated().sum()
df_cleaned.drop_duplicates(inplace=True)

print(f"\n[2.3] Duplicate rows removed: {num_duplicates}")
report_content += f"Duplicate rows removed: {num_duplicates}\n\n"

print("\n[2.4] Cleaned DataFrame Info:")
df_cleaned.info()
report_content += "Cleaned DataFrame Summary:\n"
report_content += df_cleaned.describe().to_markdown() + "\n\n"


print("\n--- Task 3: Key Insights and Extremes ---")
report_content += "--- KEY INSIGHTS AND EXTREAME ---\n\n"

highest_temp = df_cleaned['Temperature_C'].idxmax()
lowest_temp = df_cleaned['Temperature_C'].idxmin()

highest_temp_data = df_cleaned.loc[highest_temp]
lowest_temp_data = df_cleaned.loc[lowest_temp]

print(f"\n[3.1] Overall Temperature Extremes:")
print(f"  Highest Temp: {highest_temp_data['Temperature_C']}°C on {highest_temp.strftime('%Y-%m-%d')} in {highest_temp_data['City']}")
print(f"  Lowest Temp: {lowest_temp_data['Temperature_C']}°C on {lowest_temp.strftime('%Y-%m-%d')} in {lowest_temp_data['City']}")

report_content += f"Overall Temperature Extremes:\n"
report_content += f"  Highest Temp: {highest_temp_data['Temperature_C']}°C on {highest_temp.strftime('%Y-%m-%d')} in {highest_temp_data['City']}\n"
report_content += f"  Lowest Temp: {lowest_temp_data['Temperature_C']}°C on {lowest_temp.strftime('%Y-%m-%d')} in {lowest_temp_data['City']}\n\n"

city_extremes = df_cleaned.groupby('City')['Temperature_C'].agg(['max', 'min', 'mean', 'std'])
print("\n[3.2] Temperature Extremes by City:")
print(city_extremes.to_markdown())
report_content += "Temperature Statistics by City:\n"
report_content += city_extremes.to_markdown() + "\n\n"

print("\n--- Task 4: Feature Engineering and Correlations ---")

correlation_matrix = df_cleaned[['Temperature_C', 'Rainfall_mm', 'Humidity_perc', 'WindSpeed_kmh']].corr()

print("\n[4.1] Correlation Matrix:")
print(correlation_matrix.to_markdown(floatfmt=".2f"))
report_content += "Correlation Matrix (Numerical Features):\n"
report_content += correlation_matrix.to_markdown(floatfmt=".2f") + "\n\n"


print("\n--- Task 5: Time-based Analysis and Aggregation ---")
df_cleaned['MonthName'] = df_cleaned.index.strftime('%B')

monthly_avg_temp = df_cleaned.groupby('MonthName').agg({
    'Temperature_C': 'mean',
    'Rainfall_mm': 'sum',
    'Humidity_perc': 'mean'
}).sort_values(by='Temperature_C')


print("\n[5.1] Aggregation by Month Name (Sorted by Avg Temp):")
print(monthly_avg_temp.to_markdown(floatfmt=".2f"))
report_content += "Aggregation by Month Name (Sorted by Avg Temp):\n"
report_content += monthly_avg_temp.to_markdown(floatfmt=".2f") + "\n\n"


def get_season(date):
    month = date.month
    if 3 <= month <= 5:
        return 'Spring'
    elif 6 <= month <= 8:
        return 'Summer'
    elif 9 <= month <= 10:
        return 'Autumn'
    else:
        return 'Winter'

df_cleaned['Season'] = df_cleaned.index.to_series().apply(get_season)

seasonal_stats = df_cleaned.groupby('Season').agg({
    'Temperature_C': ['mean', 'std'],
    'Rainfall_mm': 'sum',
    'Humidity_perc': 'mean'
})
season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
seasonal_stats = seasonal_stats.loc[season_order]

print("\n[5.2] Seasonal Aggregate Statistics (using groupby):")
print(seasonal_stats.to_markdown(floatfmt=".2f"))
report_content += "Seasonal Aggregate Statistics:\n"
report_content += seasonal_stats.to_markdown(floatfmt=".2f") + "\n\n"



print("\n--- Task 6: Export and Storytelling ---")

df_cleaned.to_csv(NEW_FILE_PATH, index=True)
print(f"[6.1] Cleaned data exported to '{NEW_FILE_PATH}'.")

try:
    with open(REPORT_PATH, 'w') as f:
        f.write(report_content)
    print(f"[6.2] Analysis report successfully generated and saved to '{REPORT_PATH}'.")
    report_content += f"Analysis report successfully generated and saved to '{REPORT_PATH}'.\n"
except Exception as e:
    print(f"Error writing analysis report: {e}")
    report_content += f"ERROR: Failed to write report file. {e}\n"


plt.figure(figsize=(12, 6))
plt.plot(df_cleaned.index, df_cleaned['Temperature_C'], label='Temperature (°C)')
plt.plot(df_cleaned.index, df_cleaned['WindSpeed_kmh'], label='Wind Speed (km/h)')
plt.title('Time Series of Temperature and Wind Speed')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plot_path = os.path.join(PLOT_DIR, 'temp_windspeed_timeseries.png')
plt.savefig(plot_path)
plt.close()
print(f"[6.3] Time Series Plot saved to '{plot_path}'.")
report_content += f"[6.3] Time Series Plot saved to '{plot_path}'.\n"

plt.figure(figsize=(8, 6))
plt.hist(df_cleaned['Humidity_perc'], bins=15, edgecolor='black', color='skyblue')
plt.title('Distribution of Humidity Percentage')
plt.xlabel('Humidity (%)')
plt.ylabel('Frequency (Days)')
plt.grid(axis='y', alpha=0.75)
plot_path = os.path.join(PLOT_DIR, 'humidity_histogram.png')
plt.savefig(plot_path)
plt.close()
print(f"[6.4] Humidity Histogram Plot saved to '{plot_path}'.")
report_content += f"[6.4] Humidity Histogram Plot saved to '{plot_path}'.\n"

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 6)
plt.figure()
plt.plot(df_cleaned.index, df_cleaned['Temperature_C'], label='Daily Temperature (°C)', color='orangered', linewidth=1.5)
plt.title('Daily Temperature Trends Over Time')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'daily_temperature_trend.png'))
print(f"[4.1] Saved Line Chart to {PLOT_DIR}/daily_temperature_trend.png")
plt.close()

monthly_rainfall = df_cleaned['Rainfall_mm'].resample('M').sum()
monthly_labels = monthly_rainfall.index.strftime('%Y-%b')
plt.figure()
monthly_rainfall.plot(kind='bar', color='darkblue')
plt.title('Monthly Total Rainfall (mm)')
plt.xlabel('Month')
plt.ylabel('Rainfall (mm)')
plt.xticks(ticks=range(len(monthly_labels)), labels=monthly_labels, rotation=45, ha='right')
plt.grid(axis='y', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'monthly_rainfall_bar.png'))
print(f"[4.2] Saved Bar Chart to {PLOT_DIR}/monthly_rainfall_bar.png")
plt.close()

print("\n--- Analysis Complete ---")