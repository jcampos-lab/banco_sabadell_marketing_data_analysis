"""
Simple SQL Practice for Banc Sabadell
"""

import pandas as pd
import sqlite3

print("SQL PRACTICE - BANC SABADELL")
print("=" * 50)

# 1. Load data from CSV
print("\n1. Loading data...")
df = pd.read_csv('../data/bank_clean.csv', sep=';')
print(f"   Records: {len(df):,}")

# 2. Create SQL database
print("\n2. Creating SQL database...")
conn = sqlite3.connect('bank_data.db')
df.to_sql('campaigns', conn, if_exists='replace', index=False)
print("   Database: bank_data.db")

# 3. Run simple queries
print("\n3. Running SQL queries:")

# Query 1: Basic SELECT
print("\n   Query 1: First 5 customers")
result1 = pd.read_sql_query("SELECT age, job, balance FROM campaigns LIMIT 5;", conn)
print(result1.to_string(index=False))

# Query 2: COUNT
print("\n   Query 2: Total customers")
result2 = pd.read_sql_query("SELECT COUNT(*) as total FROM campaigns;", conn)
print(result2.to_string(index=False))

# Query 3: WHERE clause
print("\n   Query 3: High balance customers (>5000)")
result3 = pd.read_sql_query("""
    SELECT age, job, balance 
    FROM campaigns 
    WHERE balance > 5000 
    ORDER BY balance DESC 
    LIMIT 5;
""", conn)
print(result3.to_string(index=False))

# Query 4: GROUP BY with aggregation
print("\n   Query 4: Average balance by job")
result4 = pd.read_sql_query("""
    SELECT 
        job,
        COUNT(*) as count,
        ROUND(AVG(balance), 2) as avg_balance,
        MIN(balance) as min_balance,
        MAX(balance) as max_balance
    FROM campaigns
    GROUP BY job
    ORDER BY avg_balance DESC;
""", conn)
print(result4.to_string(index=False))

# Query 5: CASE statement for segmentation
print("\n   Query 5: Customer segmentation by balance")
result5 = pd.read_sql_query("""
    SELECT 
        CASE 
            WHEN balance < 0 THEN 'Negative'
            WHEN balance BETWEEN 0 AND 1000 THEN 'Low'
            WHEN balance BETWEEN 1000 AND 5000 THEN 'Medium'
            ELSE 'High'
        END as segment,
        COUNT(*) as customers,
        ROUND(AVG(CASE WHEN deposit = 'yes' THEN 1.0 ELSE 0.0 END) * 100, 2) as conversion_rate
    FROM campaigns
    GROUP BY segment
    ORDER BY conversion_rate DESC;
""", conn)
print(result5.to_string(index=False))

# Query 6: Channel performance (Post-mortem analysis)
print("\n   Query 6: Channel performance - Post-mortem analysis")
result6 = pd.read_sql_query("""
    SELECT 
        contact as channel,
        COUNT(*) as total_contacts,
        SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) as conversions,
        ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate,
        ROUND(AVG(duration), 2) as avg_engagement_seconds
    FROM campaigns
    GROUP BY contact
    ORDER BY conversion_rate DESC;
""", conn)
print(result6.to_string(index=False))

# Query 7: Customer value segments (CLV proxy)
print("\n   Query 7: Customer value segmentation")
result7 = pd.read_sql_query("""
    SELECT 
        CASE 
            WHEN balance > 10000 THEN 'Premium'
            WHEN balance BETWEEN 5000 AND 10000 THEN 'High Value'
            WHEN balance BETWEEN 1000 AND 5000 THEN 'Medium Value'
            ELSE 'Standard'
        END as value_tier,
        COUNT(*) as customers,
        ROUND(AVG(balance), 2) as avg_balance,
        ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate,
        ROUND(AVG(CASE WHEN deposit = 'yes' THEN duration ELSE 0 END), 2) as avg_success_duration
    FROM campaigns
    GROUP BY value_tier
    ORDER BY avg_balance DESC;
""", conn)
print(result7.to_string(index=False))

# Query 8: Campaign saturation analysis
print("\n   Query 8: Campaign contact frequency analysis")
result8 = pd.read_sql_query("""
    WITH contact_frequency AS (
        SELECT 
            campaign,
            COUNT(*) as contact_count,
            AVG(previous) as avg_previous_contacts
        FROM campaigns
        GROUP BY campaign
    )
    SELECT 
        CASE 
            WHEN contact_count > 10 THEN 'High Frequency'
            WHEN contact_count BETWEEN 5 AND 10 THEN 'Medium Frequency'
            ELSE 'Low Frequency'
        END as frequency_level,
        COUNT(*) as campaigns_count,
        ROUND(AVG(contact_count), 2) as avg_contacts,
        ROUND(AVG(avg_previous_contacts), 2) as avg_previous_contacts,
        ROUND(100.0 * SUM(CASE WHEN contact_count > 10 THEN 1 ELSE 0 END) / COUNT(*), 2) as high_freq_percentage
    FROM contact_frequency
    GROUP BY frequency_level
    ORDER BY campaigns_count DESC;
""", conn)
print(result8.to_string(index=False))

# Query 9: Monthly performance trends
print("\n   Query 9: Monthly performance trends")
result9 = pd.read_sql_query("""
    SELECT 
        month,
        COUNT(*) as monthly_campaigns,
        ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as monthly_conversion_rate,
        ROUND(AVG(duration), 2) as avg_engagement,
        ROUND(AVG(balance), 2) as avg_customer_balance
    FROM campaigns
    GROUP BY month
    ORDER BY 
        CASE month
            WHEN 'jan' THEN 1
            WHEN 'feb' THEN 2
            WHEN 'mar' THEN 3
            WHEN 'apr' THEN 4
            WHEN 'may' THEN 5
            WHEN 'jun' THEN 6
            WHEN 'jul' THEN 7
            WHEN 'aug' THEN 8
            WHEN 'sep' THEN 9
            WHEN 'oct' THEN 10
            WHEN 'nov' THEN 11
            WHEN 'dec' THEN 12
        END;
""", conn)
print(result9.to_string(index=False))

# Query 10: Propensity model (simple version)
print("\n   Query 10: Customer propensity indicators")
result10 = pd.read_sql_query("""
    SELECT 
        job,
        education,
        COUNT(*) as sample_size,
        ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as historical_conversion_rate,
        ROUND(AVG(balance), 2) as avg_balance,
        ROUND(AVG(age), 1) as avg_age,
        CASE 
            WHEN 100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*) > 60 THEN 'High Propensity'
            WHEN 100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*) > 40 THEN 'Medium Propensity'
            ELSE 'Low Propensity'
        END as propensity_level
    FROM campaigns
    WHERE job IN ('management', 'technician', 'admin.', 'blue-collar')
    GROUP BY job, education
    HAVING COUNT(*) > 30
    ORDER BY historical_conversion_rate DESC
    LIMIT 10;
""", conn)
print(result10.to_string(index=False))

# Close database connection
conn.close()

print("\n" + "=" * 50)
print("SQL PRACTICE COMPLETE")
