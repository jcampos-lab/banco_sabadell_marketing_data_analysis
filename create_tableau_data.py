"""
Create Excel summaries for Tableau visualization
"""

import pandas as pd
import sqlite3

print("Creating Excel summaries for Tableau...")

# Connect to your SQLite database
conn = sqlite3.connect('sql_practice/bank_data.db')

# 1. Channel Performance Summary
print("1. Creating channel performance summary...")
channel_query = """
SELECT 
    contact as channel,
    COUNT(*) as total_contacts,
    SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) as conversions,
    ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate,
    ROUND(AVG(duration), 2) as avg_duration
FROM campaigns
GROUP BY contact;
"""
channel_df = pd.read_sql_query(channel_query, conn)

# 2. Customer Segmentation Summary
print("2. Creating customer segmentation summary...")
segment_query = """
SELECT 
    job,
    COUNT(*) as customers,
    ROUND(AVG(balance), 2) as avg_balance,
    ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
FROM campaigns
GROUP BY job
HAVING COUNT(*) > 100
ORDER BY conversion_rate DESC;
"""
segment_df = pd.read_sql_query(segment_query, conn)

# 3. Monthly Performance Summary
print("3. Creating monthly performance summary...")
monthly_query = """
SELECT 
    month,
    COUNT(*) as campaigns,
    ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate,
    ROUND(AVG(balance), 2) as avg_balance
FROM campaigns
GROUP BY month
ORDER BY 
    CASE month
        WHEN 'jan' THEN 1 WHEN 'feb' THEN 2 WHEN 'mar' THEN 3
        WHEN 'apr' THEN 4 WHEN 'may' THEN 5 WHEN 'jun' THEN 6
        WHEN 'jul' THEN 7 WHEN 'aug' THEN 8 WHEN 'sep' THEN 9
        WHEN 'oct' THEN 10 WHEN 'nov' THEN 11 WHEN 'dec' THEN 12
    END;
"""
monthly_df = pd.read_sql_query(monthly_query, conn)

# Save to Excel with multiple sheets
output_path = 'tableau_data.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    channel_df.to_excel(writer, sheet_name='Channel_Performance', index=False)
    segment_df.to_excel(writer, sheet_name='Customer_Segments', index=False)
    monthly_df.to_excel(writer, sheet_name='Monthly_Trends', index=False)
    # Also save raw sample for deeper analysis
    raw_sample = pd.read_sql_query("SELECT * FROM campaigns LIMIT 1000;", conn)
    raw_sample.to_excel(writer, sheet_name='Raw_Sample', index=False)

conn.close()

print(f"\n✅ Excel file created: {output_path}")
print("Sheets created:")
print("  1. Channel_Performance - Marketing channel analysis")
print("  2. Customer_Segments - Job-based segmentation")
print("  3. Monthly_Trends - Time-based performance")
print("  4. Raw_Sample - Sample data for exploration")

print("\nOpen this file in Tableau Public for visualization!")
