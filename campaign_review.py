"""
Banc Sabadell - Campaign Analysis
Reviewing marketing campaign performance
"""

import pandas as pd

print("Starting basic campaign analysis...")
print("=" * 40)

# Loading the campaign data from the kaggle csv file
print("Loading campaign data from CSV...")
campaign_data = pd.read_csv('data/bank_clean.csv', sep=';')

# ========== sql database integration with SQLiteP ==========
print("\n" + "=" * 40)
print("SQL DATABASE INTEGRATION")


import sqlite3

print("Creating SQL database for analysis...")
conn = sqlite3.connect('data/campaigns.db')

# Load CSV into SQLite
campaign_data.to_sql('campaign_results', conn, if_exists='replace', index=False)
print(f"• Database created successfully: data/campaigns.db")
print(f"• Table loaded: {len(campaign_data):,} records")

# Example basic SQL query
print("\nRunning SQL query for channel analysis:")
channel_query = """
SELECT 
    contact as marketing_channel,
    COUNT(*) as attempts,
    SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) as successes,
    ROUND(100.0 * SUM(CASE WHEN deposit = 'yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM campaign_results
GROUP BY contact
ORDER BY success_rate DESC;
"""

# Execute SQL and get results 
channel_results_sql = pd.read_sql_query(channel_query, conn)
print(channel_results_sql.to_string(index=False))

conn.close()
print("\n✓ SQL analysis complete")
print("=" * 40)

print(f"Total records successfulu loaded: {len(campaign_data):,}")
print(f"Data period: {campaign_data['month'].unique()}")

# Calculate campaign success rate using the SQL data extraction
print("\nCampaign success analysis:")
successful = (campaign_data['deposit'] == 'yes').sum()
total = len(campaign_data)
success_rate = (successful / total) * 100

print(f"   • Successful analysed campaigns: {successful:,}")
print(f"   • Total analysed campaigns: {total:,}")
print(f"   • Overall Success rate: {success_rate:.1f}%")

# Analyze performance by contact channel individually
print("\nChannel performance comparison:")

# here is the grouping data by contact method
# here using the lambda method to represent the anonymous function
channel_results = campaign_data.groupby('contact').agg(
    attempts=('deposit', 'count'),
    successes=('deposit', lambda x: (x == 'yes').sum())
)

# Calculate success rates individually
channel_results['success_rate'] = (channel_results['successes'] / channel_results['attempts'] * 100).round(1)

# displaying general results
for channel in ['cellular', 'telephone', 'unknown']:
    if channel in channel_results.index:
        stats = channel_results.loc[channel]
        print(f"   • {channel}: {stats['success_rate']}% success rate")
        print(f"     ({stats['successes']} successes out of {stats['attempts']} attempts)")

# identifiying the best and the worst performing channels (aproximation)
print("\nKey business insight:")
best_channel = channel_results['success_rate'].idxmax()
best_rate = channel_results['success_rate'].max()
worst_channel = channel_results['success_rate'].idxmin()
worst_rate = channel_results['success_rate'].min()

print(f"   • Best channel: {best_channel} ({best_rate}% success)")
print(f"   • Worst channel: {worst_channel} ({worst_rate}% success)")
print(f"   • Performance gap: {best_rate - worst_rate:.1f} percentage points")

#  recommendation based on the first results focused on Celular
print(f"\nRecommendation:")
print(f"   Consider reallocating some budget from {worst_channel}")
print(f"   to {best_channel} for better campaign results.")

# ========== CUSTOMER SEGMENTATION ==========
print("CUSTOMER VALUE SEGMENTATION")
print("=" * 40)

# create 3 cust segments based on the final balance 
campaign_data['customer_tier'] = pd.qcut(campaign_data['balance'], q=3, 
                                        labels=['Standard', 'Premium', 'Elite'])

# analysing each tier and comparing the sdeposit rate
print("\nCustomer segmentation by account balance:")
for tier in ['Standard', 'Premium', 'Elite']:
    tier_data = campaign_data[campaign_data['customer_tier'] == tier]
    tier_size = len(tier_data)
    tier_rate = (tier_data['deposit'] == 'yes').mean() * 100
    tier_avg_balance = tier_data['balance'].mean()
    
    print(f"\n{tier} Tier:")
    print(f"   • Customers: {tier_size:,}")
    print(f"   • Avg balance: ${tier_avg_balance:,.0f}")
    print(f"   • Success rate: {tier_rate:.1f}%")

print("\nSegmentation finding:")
print("Customer response varies by financial profile")
print("Suggests personalized campaign approaches")

#Business KPIs and return of investment (ROI)

print("BUSINESS IMPACT & ROI ESTIMATION")
print("=" * 40)

# assume average values for business calculation using tthe banks metrics
avg_deposit_amount = 1000  # Example: average deposit amount in €
contact_cost = {
    'cellular': 2.50,   # Cost per cellular contact
    'telephone': 8.00,   # Cost per phone call  
    'unknown': 0.50      # Cost per unknown contact
}

print("\nEstimated financial impact per channel:")

for channel in ['cellular', 'telephone', 'unknown']:
    channel_data = campaign_data[campaign_data['contact'] == channel]
    contacts = len(channel_data)
    conversions = (channel_data['deposit'] == 'yes').sum()
    success_rate = (conversions / contacts * 100)
    
    # Calculate revenue and cost aproximation
    revenue = conversions * avg_deposit_amount
    cost = contacts * contact_cost[channel]
    profit = revenue - cost
    roi = (profit / cost * 100) if cost > 0 else 0
    
    print(f"\n{channel.upper()} CHANNEL:")
    print(f"   • Contacts: {contacts:,}")
    print(f"   • Conversions: {conversions:,}")
    print(f"   • Success rate: {success_rate:.1f}%")
    print(f"   • Revenue: €{revenue:,.0f}")
    print(f"   • Cost: €{cost:,.0f}")
    print(f"   • Profit: €{profit:,.0f}")
    print(f"   • ROI: {roi:.1f}%")

# here is the best ROI channel
best_roi_channel = max(['cellular', 'telephone', 'unknown'], 
                      key=lambda x: ((campaign_data[campaign_data['contact'] == x]['deposit'] == 'yes').sum() * avg_deposit_amount - 
                                     len(campaign_data[campaign_data['contact'] == x]) * contact_cost[x]) / 
                                    (len(campaign_data[campaign_data['contact'] == x]) * contact_cost[x]) * 100)

print(f"\nKEY FINANCIAL INSIGHT:")
print(f"   • Highest ROI channel: {best_roi_channel}")
print(f"   • Recommendation: Prioritize {best_roi_channel} in budget allocation")
print(f"   • Expected impact: Improve overall campaign profitability")

# ROI focused on the insights (celular makes most sense to boost)
print("\nBUSINESS IMPACT ANALYSIS:")
cellular_cost = 0.10  # example cost per contact
cellular_revenue = 100  # example revenue per conversion
cellular_roi = (cellular_revenue * 0.543 - cellular_cost) / cellular_cost * 100

unknown_cost = 0.05
unknown_revenue = 100
unknown_roi = (unknown_revenue * 0.226 - unknown_cost) / unknown_cost * 100

print(f"• Estimated cellular channel ROI: {cellular_roi:.0f}%")
print(f"• Estimated unknown channel ROI: {unknown_roi:.0f}%")
print(f"• ROI improvement potential: {cellular_roi - unknown_roi:.0f}% points")
