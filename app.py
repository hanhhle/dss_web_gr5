import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# =====================================================================
# SYSTEM CONFIGURATION
# =====================================================================
st.set_page_config(page_title="DSS Enterprise Dashboard", page_icon="🚀", layout="wide")

# Custom CSS to make KPIs look like Power BI cards
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 5% 10% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Enterprise Marketing Decision Support System")
st.markdown("*A Unified 4-Phase Decision Support Environment based on Simon's Decision-Making Model*")

# =====================================================================
# DATA LOADING ENGINE
# =====================================================================
@st.cache_data
def load_data():
    raw_file = 'Two_Stage_Clustered_B2B_Data.csv'
    leads_file = 'MASTER_Hot_Leads_All_Campaigns.csv'
    rules_file = 'MASTER_Cross_Sell_Rules_All_Campaigns.xlsx'
    
    if not os.path.exists(raw_file) or not os.path.exists(leads_file) or not os.path.exists(rules_file):
        st.error("⚠️ Error: Core data files are missing! Please ensure all .csv and .xlsx files are in the same folder.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
    raw_df = pd.read_csv(raw_file)
    leads_df = pd.read_csv(leads_file)
    rules_df = pd.read_excel(rules_file)
    return raw_df, leads_df, rules_df

raw_data, leads, rules = load_data()

# =====================================================================
# DASHBOARD ARCHITECTURE (SIMON'S 4-PHASE MODEL)
# =====================================================================
if not raw_data.empty and not leads.empty and not rules.empty:
    
    # Define 4 Tabs representing the 4 Phases
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 1. Market Overview (Intelligence)", 
        "🎯 2. Campaign Decision (Design)", 
        "⚖️ 3. Campaign Comparison (Choice)", 
        "🛒 4. Cross-Sell Strategy (Implementation)"
    ])

    # -----------------------------------------------------------------
    # TAB 1: INTELLIGENCE PHASE
    # -----------------------------------------------------------------
    with tab1:
        st.info("**Decision Contribution (Intelligence Phase):** Understand customer structure, spending behavior, and market opportunities before campaign planning begins. It establishes the informational foundation required for subsequent campaign design and resource allocation.")
        
        st.markdown("### 🔍 Interactive Market Filters")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            seg_options = ["All Segments"] + list(raw_data['Final_Segment'].unique())
            t1_seg = st.selectbox("Filter by Customer Segment:", seg_options, key="t1_seg")
        with f_col2:
            camp_options = ["All Campaigns", "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
            t1_camp = st.selectbox("Filter by Historical Campaign Participation:", camp_options, key="t1_camp")
            
        # Cross-filtering logic
        df_t1 = raw_data.copy()
        if t1_seg != "All Segments": df_t1 = df_t1[df_t1['Final_Segment'] == t1_seg]
        if t1_camp != "All Campaigns": df_t1 = df_t1[df_t1[t1_camp] == 1]

        if not df_t1.empty:
            # KPI Cards
            st.markdown("#### 📊 High-level Market KPIs")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Companies", f"{len(df_t1):,}")
            kpi2.metric("Avg. IT Budget", f"${df_t1['IT_Budget_USD'].mean():,.0f}")
            kpi3.metric("Avg. Enterprise Spend", f"${df_t1['Mnt_Total_Enterprise_Spend'].mean():,.0f}")
            kpi4.metric("Avg. Tech Readiness", f"{df_t1['Tech_Readiness_Level'].mean():.1f}/10")
            
            st.markdown("---")
            
            # Visualizations Row 1
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.markdown("**Customer Distribution Chart**")
                dist_df = df_t1['Final_Segment'].value_counts().reset_index()
                dist_df.columns = ['Segment', 'Count']
                fig_pie = px.pie(dist_df, values='Count', names='Segment', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with r1c2:
                st.markdown("**Product Category Analysis (Spending Patterns)**")
                prod_cols = ['Mnt_Cloud_Infrastructure', 'Mnt_CRM_Software', 'Mnt_ERP_Systems', 'Mnt_Cybersecurity', 'Mnt_Collaboration_Tools', 'Mnt_AI_Data_Analytics']
                prod_means = df_t1[prod_cols].mean().reset_index()
                prod_means.columns = ['Product', 'Avg Spend']
                prod_means['Product'] = prod_means['Product'].str.replace('Mnt_', '')
                fig_bar = px.bar(prod_means, x='Avg Spend', y='Product', orientation='h', color='Avg Spend', color_continuous_scale='Viridis')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Visualizations Row 2
            r2c1, r2c2 = st.columns([1.5, 1])
            with r2c1:
                st.markdown("**Customer Segmentation Scatter Plot**")
                fig_scatter = px.scatter(df_t1, x='IT_Budget_USD', y='Mnt_Total_Enterprise_Spend', color='Final_Segment', 
                                         hover_data=['Partnership_Years'], opacity=0.7, color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig_scatter, use_container_width=True)
            with r2c2:
                st.markdown("**Spending Summary Table**")
                sum_tb = df_t1.groupby('Final_Segment')[['IT_Budget_USD', 'Mnt_Total_Enterprise_Spend']].mean().reset_index()
                sum_tb.columns = ['Segment', 'Avg Budget ($)', 'Avg Spend ($)']
                st.dataframe(sum_tb.style.format({"Avg Budget ($)": "{:,.0f}", "Avg Spend ($)": "{:,.0f}"}), use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # TAB 2: DESIGN PHASE
    # -----------------------------------------------------------------
    with tab2:
        st.success("**Decision Contribution (Design Phase):** Identify customers with high conversion potential and evaluate the business value of marketing campaigns. Helps focus marketing efforts on customers with the highest likelihood of conversion.")
        
        st.markdown("### 🎯 Predictive Lead Targeting")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            t2_camp = st.selectbox("Select Target Campaign:", leads['Campaign'].unique(), key="t2_camp")
        with d_col2:
            t2_seg_opts = ["All Segments"] + list(leads[leads['Campaign'] == t2_camp]['Final_Segment'].unique())
            t2_seg = st.selectbox("Select Target Segment:", t2_seg_opts, key="t2_seg")

        df_t2 = leads[leads['Campaign'] == t2_camp]
        if t2_seg != "All Segments": df_t2 = df_t2[df_t2['Final_Segment'] == t2_seg]

        if not df_t2.empty:
            st.markdown("#### 📊 Predictive Opportunity KPIs")
            kpi_d1, kpi_d2, kpi_d3 = st.columns(3)
            kpi_d1.metric("Qualified Hot Leads", f"{len(df_t2):,} Companies")
            kpi_d2.metric("Total Targetable IT Budget", f"${df_t2['IT_Budget_USD'].sum():,.0f}")
            kpi_d3.metric("Average Win Probability", f"{df_t2['Probability_To_Buy'].mean()*100:.1f}%")
            
            st.markdown("---")
            
            r3c1, r3c2 = st.columns([1, 1.2])
            with r3c1:
                st.markdown("**Expected Value vs. Model Performance**")
                fig_val = px.scatter(df_t2, x='Probability_To_Buy', y='IT_Budget_USD', color='Final_Segment', size='Mnt_Total_Enterprise_Spend',
                                     hover_data=['Company_ID'], title="Risk vs Reward Analysis")
                st.plotly_chart(fig_val, use_container_width=True)
            with r3c2:
                st.markdown("**Model Validation: Probability Distribution**")
                fig_hist = px.histogram(df_t2, x='Probability_To_Buy', nbins=15, color='Final_Segment', marginal="box")
                st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown("**Hot Lead Detail Table (Ready for Telesales)**")
            st.dataframe(df_t2[['Company_ID', 'Final_Segment', 'Probability_To_Buy', 'IT_Budget_USD', 'Mnt_Total_Enterprise_Spend']].sort_values(by='Probability_To_Buy', ascending=False), use_container_width=True)
            st.download_button("📥 Export Hot Leads to Operational Workflow (CSV)", data=df_t2.to_csv(index=False).encode('utf-8'), file_name=f"HotLeads_{t2_camp}.csv", mime="text/csv")
        else:
            st.warning("No predictive leads available for this combination.")

    # -----------------------------------------------------------------
    # TAB 3: CHOICE PHASE (Campaign Comparison)
    # -----------------------------------------------------------------
    with tab3:
        st.warning("**Decision Contribution (Choice Phase):** Compare alternative marketing campaigns and determine how organizational resources should be allocated. Assess trade-offs systematically to select the optimal campaign strategy.")
        
        st.markdown("### ⚖️ Campaign Strategic Alternatives")
        
        # Aggregate data at Campaign Level
        camp_summary = leads.groupby('Campaign').agg(
            Lead_Volume=('Company_ID', 'count'),
            Avg_Probability=('Probability_To_Buy', 'mean'),
            Total_Projected_Budget=('IT_Budget_USD', 'sum')
        ).reset_index()

        st.markdown("#### 📊 Portfolio Evaluation KPIs")
        kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
        best_vol = camp_summary.loc[camp_summary['Lead_Volume'].idxmax()]
        best_val = camp_summary.loc[camp_summary['Total_Projected_Budget'].idxmax()]
        best_prob = camp_summary.loc[camp_summary['Avg_Probability'].idxmax()]
        
        kpi_c1.metric("Largest Scale Campaign", best_vol['Campaign'], f"{best_vol['Lead_Volume']} Leads")
        kpi_c2.metric("Highest Value Campaign", best_val['Campaign'], f"${best_val['Total_Projected_Budget']:,.0f}")
        kpi_c3.metric("Safest Campaign (Highest Prob)", best_prob['Campaign'], f"{best_prob['Avg_Probability']*100:.1f}%")
        
        st.markdown("---")

        r4c1, r4c2 = st.columns(2)
        with r4c1:
            st.markdown("**Campaign Positioning Matrix (Trade-off Analysis)**")
            fig_matrix = px.scatter(camp_summary, x='Avg_Probability', y='Lead_Volume', size='Total_Projected_Budget', 
                                    color='Campaign', text='Campaign', title="Scale vs Reliability (Bubble size = Budget)")
            fig_matrix.update_traces(textposition='top center')
            st.plotly_chart(fig_matrix, use_container_width=True)
            
        with r4c2:
            st.markdown("**Segment Contribution Analysis**")
            seg_contrib = leads.groupby(['Campaign', 'Final_Segment']).size().reset_index(name='Lead_Count')
            fig_stack = px.bar(seg_contrib, x='Campaign', y='Lead_Count', color='Final_Segment', title="Lead Volume Breakdown by Segment")
            st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown("**Consolidated Campaign Summary Table**")
        st.dataframe(camp_summary.style.format({"Avg_Probability": "{:.2%}", "Total_Projected_Budget": "${:,.0f}"}), use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # TAB 4: IMPLEMENTATION PHASE (Cross-Selling Strategy)
    # -----------------------------------------------------------------
    with tab4:
        st.error("**Decision Contribution (Implementation Phase):** Assist sales personnel in identifying appropriate products to recommend during customer interactions. Transforms mathematical association rules into intuitive recommendation pathways.")
        
        st.markdown("### 🛒 Smart Recommendation Engine")
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            t4_camp = st.selectbox("Operating Campaign Context:", rules['Campaign'].unique(), key="t4_camp")
        with i_col2:
            t4_seg_opts = ["All Segments"] + list(rules[rules['Campaign'] == t4_camp]['Segment'].unique())
            t4_seg = st.selectbox("Customer Segment Context:", t4_seg_opts, key="t4_seg")

        df_t4 = rules[rules['Campaign'] == t4_camp]
        if t4_seg != "All Segments": df_t4 = df_t4[df_t4['Segment'] == t4_seg]

        prod_universe = ['Cloud_Infrastructure', 'CRM_Software', 'ERP_Systems', 'Cybersecurity', 'Collaboration_Tools', 'AI_Data_Analytics']
        owned_prods = st.multiselect("Select Products the Customer Already Owns (Recommendation Pathway Trigger):", prod_universe)

        if owned_prods:
            def is_strict_subset(ant_str):
                return set([i.strip() for i in str(ant_str).split(',')]).issubset(set(owned_prods))
            df_t4 = df_t4[df_t4['Khách Đã Mua'].apply(is_strict_subset)]

        if not df_t4.empty:
            st.markdown("#### 📊 Rule Performance KPIs")
            kpi_i1, kpi_i2, kpi_i3 = st.columns(3)
            kpi_i1.metric("Available Recommendation Paths", len(df_t4))
            kpi_i2.metric("Maximum Revenue Lift", f"{df_t4['Lift'].max():.2f}x")
            kpi_i3.metric("Highest Success Confidence", f"{df_t4['Confidence'].max()*100:.1f}%")
            
            st.markdown("---")

            r5c1, r5c2 = st.columns([1, 1.2])
            with r5c1:
                st.markdown("**Lift Ranking Chart (Top 10)**")
                top_rules = df_t4.sort_values(by='Lift', ascending=False).head(10).copy()
                top_rules['Pathway'] = top_rules['Khách Đã Mua'] + " ➔ " + top_rules['Gợi Ý Bán Chéo']
                fig_lift = px.bar(top_rules, x='Lift', y='Pathway', orientation='h', color='Confidence', title="Top Priority Recommendations")
                fig_lift.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_lift, use_container_width=True)
                
            with r5c2:
                st.markdown("**Support vs. Confidence Chart (Reliability Evaluation)**")
                # Assuming 'Support' column exists. If not, fallback gracefully.
                if 'Support' in df_t4.columns:
                    fig_sup = px.scatter(df_t4, x='Confidence', y='Lift', size='Support', color='Segment', hover_data=['Khách Đã Mua', 'Gợi Ý Bán Chéo'], title="Rule Strength Distribution")
                else:
                    fig_sup = px.scatter(df_t4, x='Confidence', y='Lift', color='Segment', hover_data=['Khách Đã Mua', 'Gợi Ý Bán Chéo'], title="Rule Strength Distribution")
                st.plotly_chart(fig_sup, use_container_width=True)

            st.markdown("**Executable Cross-Sell Strategy Matrix**")
            st.dataframe(df_t4[['Segment', 'Khách Đã Mua', 'Gợi Ý Bán Chéo', 'Confidence', 'Lift']].sort_values(by='Lift', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("No cross-sell rules match your strict ownership criteria. Try adjusting the product selection or filters.")

else:
    st.error("Dashboard failed to load due to missing data. Ensure the Machine Learning pipeline has generated all required CSV and Excel files.")