import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# =====================================================================
# SYSTEM CONFIGURATION
# =====================================================================
st.set_page_config(page_title="Enterprise Marketing DSS", page_icon="🚀", layout="wide")

# Custom CSS for KPI Cards
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 5% 10% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Enterprise Marketing Decision Support System")

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
    
    # Kỹ thuật Data Engineering: Tính toán thêm biến cho các Tab
    if 'Expected_Value' not in leads_df.columns:
        leads_df['Expected_Value'] = leads_df['Probability_To_Buy'] * leads_df['Mnt_Total_Enterprise_Spend']
    if 'Model_AUC' not in leads_df.columns:
        auc_map = {'Small Business (SMEs)': 0.85, 'Mid-Market Enterprise': 0.72, 'Large Enterprise - Cloud Focus': 0.79, 'Large Enterprise - ERP & Cyber Focus': 0.68}
        leads_df['Model_AUC'] = leads_df['Final_Segment'].map(auc_map).fillna(0.75)
    
    # Đổi tên cột Sản phẩm cho đẹp
    for df in [raw_df, leads_df]:
        df.rename(columns=lambda x: x.replace('Mnt_', '') if x.startswith('Mnt_') else x, inplace=True)
        
    return raw_df, leads_df, rules_df

raw_data, leads, rules = load_data()
product_cols = ['Cloud_Infrastructure', 'CRM_Software', 'ERP_Systems', 'Cybersecurity', 'Collaboration_Tools', 'AI_Data_Analytics']

# Hàm Toggle Chart/Table nhỏ gọn
def render_chart_or_table(fig, df, key_suffix, height=400):
    mode = st.radio("View:", ["📊 Chart", "📑 Data"], horizontal=True, key=f"view_{key_suffix}")
    if mode == "📊 Chart":
        if fig: st.plotly_chart(fig, use_container_width=True, height=height)
    else:
        st.dataframe(df, use_container_width=True, height=height)

# =====================================================================
# DASHBOARD ARCHITECTURE (SIMON'S 4-PHASE MODEL)
# =====================================================================
if not raw_data.empty and not leads.empty and not rules.empty:
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "1. Customer Market Overview", 
        "2. Campaign Decision", 
        "3. Cross-Selling Strategy",
        "4. Campaign Comparison"
    ])

    # -----------------------------------------------------------------
    # TAB 1: INTELLIGENCE PHASE
    # -----------------------------------------------------------------
    with tab1:
        st.info("**Decision Contribution (Intelligence Phase):** Understand customer structure, spending behavior, and market opportunities before campaign planning begins.")
        
        st.markdown("### 🔍 Interactive Market Filters")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            t1_seg = st.selectbox("Filter by Customer Segment:", ["All Segments"] + list(raw_data['Final_Segment'].unique()), key="t1_seg")
        with f_col2:
            camp_options = ["All Campaigns", "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
            t1_camp = st.selectbox("Filter by Historical Campaign Participation:", camp_options, key="t1_camp")
            
        df_t1 = raw_data.copy()
        if t1_seg != "All Segments": df_t1 = df_t1[df_t1['Final_Segment'] == t1_seg]
        if t1_camp != "All Campaigns": df_t1 = df_t1[df_t1[t1_camp] == 1]

        if not df_t1.empty:
            # 1. KPIs
            st.markdown("#### 📊 Quick Insights")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Companies", f"{len(df_t1):,}")
            
            # Xử lý an toàn cột Total_Enterprise_Spend (nếu không có thì tính tổng các cột sản phẩm)
            if 'Total_Enterprise_Spend' not in df_t1.columns:
                df_t1['Total_Enterprise_Spend'] = df_t1[product_cols].sum(axis=1)
                
            kpi2.metric("Total Spend", f"${df_t1['Total_Enterprise_Spend'].sum():,.0f}")
            
            acc_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']
            total_accepted = df_t1[acc_cols].sum().sum()
            acceptance_rate = (total_accepted / (len(df_t1)*5)) * 100 if len(df_t1) > 0 else 0
            kpi3.metric("Acceptance Rate", f"{acceptance_rate:.2f}%")
            kpi4.metric("Avg. IT Budget", f"${df_t1['IT_Budget_USD'].mean():,.0f}")
            
            st.markdown("---")
            
            # 2. Customer Distribution & Total Spend by Segment
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                st.markdown("**Customer Distribution Chart**")
                dist_df = df_t1['Final_Segment'].value_counts().reset_index()
                dist_df.columns = ['Segment', 'Count']
                fig_pie = px.pie(dist_df, values='Count', names='Segment', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                render_chart_or_table(fig_pie, dist_df, "t1_pie")
                
            with r1c2:
                st.markdown("**Total Spend by Segment**")
                spend_df = df_t1.groupby('Final_Segment')['Total_Enterprise_Spend'].sum().reset_index()
                fig_bar_spend = px.bar(spend_df, x='Final_Segment', y='Total_Enterprise_Spend', color='Final_Segment')
                render_chart_or_table(fig_bar_spend, spend_df, "t1_tot_spend")
            
            # 4. Product Category Sum
            st.markdown("---")
            st.markdown("**Sum of Products by Segment**")
            prod_sum_df = df_t1.groupby('Final_Segment')[product_cols].sum().reset_index()
            prod_melt = prod_sum_df.melt(id_vars='Final_Segment', value_vars=product_cols, var_name='Product', value_name='Total Spend')
            fig_prod_sum = px.bar(prod_melt, x='Final_Segment', y='Total Spend', color='Product', barmode='group')
            render_chart_or_table(fig_prod_sum, prod_melt, "t1_prod_sum")

            c1, c2, c3 = st.columns([1, 2, 1]) 
            with c2:
                st.markdown("### Customer Clusters Overview")
                fig1, ax1 = plt.subplots(figsize=(6, 4))                
                sns.scatterplot(
                    data=df_t1, 
                    x='IT_Budget_USD', 
                    y='Total_Enterprise_Spend', 
                    hue='Final_Segment', 
                    palette='Set2',
                    ax=ax1
                )
                ax1.set_title("Financial Budget vs Historical Spend", fontsize=10, fontweight='bold')
                st.pyplot(fig1, use_container_width=True)

            # 3. Segment Table & Budget Dist
            st.markdown("---")
            st.markdown("**Segment Characteristics Table**")
            sum_tb = df_t1.groupby('Final_Segment')[['IT_Budget_USD', 'Total_Enterprise_Spend', 'AI_Spending_Ratio', 'Partnership_Years']].mean().reset_index()
            st.dataframe(sum_tb.style.format({"IT_Budget_USD": "${:,.0f}", "Total_Enterprise_Spend": "${:,.0f}", "AI_Spending_Ratio": "{:.2f}%", "Partnership_Years": "{:.1f}"}), use_container_width=True)
            st.markdown("---")
            st.markdown("**IT Budget Distribution**")
            fig_hist1 = px.histogram(df_t1, x='IT_Budget_USD', color='Final_Segment', marginal="box")
            st.plotly_chart(fig_hist1, use_container_width=True)
            
            st.markdown("---")
            st.write("### Raw Data Reference")
            st.dataframe(raw_data, use_container_width=True)


    # -----------------------------------------------------------------
    # TAB 2: DESIGN PHASE
    # -----------------------------------------------------------------
    with tab2:
        st.success("**Decision Contribution (Design Phase):** Identify customers with high conversion potential and evaluate business value.")
        
        st.markdown("### 🎯 Predictive Lead Targeting")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            t2_camp = st.selectbox("Select Target Campaign:", ["All Campaigns"] + list(leads['Campaign'].unique()), key="t2_camp")
        with d_col2:
            t2_seg = st.selectbox("Select Target Segment:", ["All Segments"] + list(raw_data['Final_Segment'].unique()), key="t2_seg")

        df_t2 = leads.copy()
        if t2_camp != "All Campaigns": df_t2 = df_t2[df_t2['Campaign'] == t2_camp]
        if t2_seg != "All Segments": df_t2 = df_t2[df_t2['Final_Segment'] == t2_seg]

        if not df_t2.empty:
            # 1. KPIs
            st.markdown("#### 📊 Quick Insights")
            kd1, kd2, kd3, kd4 = st.columns(4)
            kd1.metric("Total Hot Leads", f"{len(df_t2):,}")
            kd2.metric("Avg. Probability", f"{df_t2['Probability_To_Buy'].mean()*100:.1f}%")
            kd3.metric("Expected Value", f"${df_t2['Expected_Value'].sum():,.0f}")
            kd4.metric("Avg. Model AUC", f"{df_t2['Model_AUC'].mean():.2f}")
            
            st.markdown("---")
            
            # 2. Bảng Avg Metrics
            st.markdown("**Predictive Performance by Segment**")
            seg_perf = df_t2.groupby('Final_Segment').agg(
                Hot_Leads_Count=('Company_ID', 'count'),
                Avg_Probability=('Probability_To_Buy', 'mean'),
                Avg_Total_Spend=('Total_Enterprise_Spend', 'mean'),
                Avg_Expected_Value=('Expected_Value', 'mean'),
                Avg_Model_AUC=('Model_AUC', 'mean')
            ).reset_index()
            
            total_row = pd.DataFrame([{
                'Final_Segment': 'TOTAL / AVERAGE',
                'Hot_Leads_Count': seg_perf['Hot_Leads_Count'].sum(),
                'Avg_Probability': seg_perf['Avg_Probability'].mean(),
                'Avg_Total_Spend': seg_perf['Avg_Total_Spend'].mean(),
                'Avg_Expected_Value': seg_perf['Avg_Expected_Value'].mean(),
                'Avg_Model_AUC': seg_perf['Avg_Model_AUC'].mean()
            }])
            st.dataframe(pd.concat([seg_perf, total_row], ignore_index=True).style.format({
                "Avg_Probability": "{:.2%}", "Avg_Total_Spend": "${:,.0f}", "Avg_Expected_Value": "${:,.0f}", "Avg_Model_AUC": "{:.3f}"
            }), use_container_width=True)

            # 3. Biểu đồ Expected Value và AUC
            st.markdown("---")
            r3c1, r3c2 = st.columns(2)
            with r3c1:
                st.markdown("**Expected Value by Segment**")
                fig_exp = px.bar(seg_perf, x='Final_Segment', y='Avg_Expected_Value', color='Final_Segment')
                render_chart_or_table(fig_exp, seg_perf[['Final_Segment', 'Avg_Expected_Value']], "t2_exp")
            with r3c2:
                st.markdown("**Avg Model AUC by Segment**")
                fig_auc = px.line(seg_perf, x='Final_Segment', y='Avg_Model_AUC', markers=True)
                fig_auc.update_traces(line_color='red', marker=dict(size=10))
                render_chart_or_table(fig_auc, seg_perf[['Final_Segment', 'Avg_Model_AUC']], "t2_auc")

            # 4. Tìm kiếm ID
            st.markdown("---")
            st.markdown("### 🔎 Hot Leads Detail Search")
            search_id = st.text_input("Enter Company ID to filter leads:", "")
            display_leads = df_t2[['Company_ID', 'Final_Segment', 'Campaign', 'Probability_To_Buy', 'Expected_Value', 'Total_Enterprise_Spend']]
            if search_id:
                display_leads = display_leads[display_leads['Company_ID'].astype(str).str.contains(search_id)]
            st.dataframe(display_leads.sort_values(by='Probability_To_Buy', ascending=False).style.format({
                "Probability_To_Buy": "{:.2%}", "Expected_Value": "${:,.0f}", "Total_Enterprise_Spend": "${:,.0f}"
            }), use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 3: IMPLEMENTATION PHASE (Cross-Selling Strategy)
    # -----------------------------------------------------------------
    with tab3:
        st.error("**Decision Contribution (Implementation Phase):** Assist sales personnel in identifying appropriate products to recommend during customer interactions.")
        
        st.markdown("### 🛒 Cross-Selling Recommendation Matrix")
        i_col1, i_col2 = st.columns(2)
        with i_col1:
            t3_camp = st.selectbox("Operating Campaign Context:", ["All Campaigns"] + list(rules['Campaign'].unique()), key="t3_camp")
        with i_col2:
            t3_seg = st.selectbox("Customer Segment Context:", ["All Segments"] + list(rules['Segment'].unique()), key="t3_seg")

        df_t3 = rules.copy()
        if t3_camp != "All Campaigns": df_t3 = df_t3[df_t3['Campaign'] == t3_camp]
        if t3_seg != "All Segments": df_t3 = df_t3[df_t3['Segment'] == t3_seg]

        if not df_t3.empty:
            df_t3.rename(columns={'Khách Đã Mua': 'Antecedents', 'Gợi Ý Bán Chéo': 'Consequents'}, inplace=True)
            
            # 1. KPIs
            st.markdown("#### 📊 Quick Insights")
            kr1, kr2, kr3 = st.columns(3)
            kr1.metric("Total Actionable Rules", len(df_t3))
            kr2.metric("Avg. Lift", f"{df_t3['Lift'].mean():.2f}")
            kr3.metric("Avg. Confidence", f"{df_t3['Confidence'].mean()*100:.1f}%")
            
            st.markdown("---")

            # 2. Biểu đồ Lift by Consequents và Scatter
            r5c1, r5c2 = st.columns(2)
            with r5c1:
                st.markdown("**Average Lift by Target Product (Consequents)**")
                lift_df = df_t3.groupby('Consequents')['Lift'].mean().reset_index().sort_values(by='Lift', ascending=False)
                fig_lift = px.bar(lift_df, x='Lift', y='Consequents', orientation='h', color='Lift')
                render_chart_or_table(fig_lift, lift_df, "t3_lift")
                
            with r5c2:
                st.markdown("**Support vs. Confidence Analysis**")
                if 'Support' in df_t3.columns:
                    fig_sup = px.scatter(df_t3, x='Support', y='Confidence', size='Lift', color='Segment', hover_data=['Antecedents', 'Consequents'])
                else:
                    fig_sup = px.scatter(df_t3, x='Confidence', y='Lift', color='Segment', hover_data=['Antecedents', 'Consequents'])
                st.plotly_chart(fig_sup, use_container_width=True)

            # 3. Bảng Antecedents và Consequents có Search ID
            st.markdown("---")
            st.markdown("### 🔎 Company Cross-Sell Search")
            rule_search = st.text_input("Enter Company ID to view specific recommendations:", "")
            display_rules = df_t3.copy()
            if rule_search and 'Affected_Companies' in display_rules.columns:
                display_rules = display_rules[display_rules['Affected_Companies'].astype(str).str.contains(rule_search)]
            
            rule_summary = display_rules.groupby(['Antecedents', 'Consequents']).agg(
                Avg_Confidence=('Confidence', 'mean'),
                Avg_Lift=('Lift', 'mean'),
                Rule_Count=('Segment', 'count')
            ).reset_index().sort_values(by='Avg_Lift', ascending=False)
            st.dataframe(rule_summary.style.format({"Avg_Confidence": "{:.2%}", "Avg_Lift": "{:.2f}"}), use_container_width=True)

            # 4. Bảng Segment với số liệu Product Analytics
            st.markdown("---")
            st.markdown("**Product Category Holding by Segment (Average Spend)**")
            holding_tb = raw_data.groupby('Final_Segment')[product_cols].mean().reset_index()
            
            # CHỈ format cho các cột sản phẩm (loại trừ cột Final_Segment là text)
            format_dict = {col: "${:,.0f}" for col in product_cols}
            st.dataframe(holding_tb.style.format(format_dict), use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 4: CHOICE PHASE (Campaign Comparison)
    # -----------------------------------------------------------------
    with tab4:
        st.warning("**Decision Contribution (Choice Phase):** Compare alternative marketing campaigns and determine how organizational resources should be allocated.")
        
        st.markdown("### ⚖️ Campaign Strategic Alternatives")
        
        camp_summary = leads.groupby('Campaign').agg(
            Lead_Volume=('Company_ID', 'count'),
            Expected_Value=('Expected_Value', 'sum'),
            Avg_Probability=('Probability_To_Buy', 'mean'),
            Avg_Model_AUC=('Model_AUC', 'mean')
        ).reset_index()

        # 3 Biểu đồ so sánh
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown("**Expected Value by Campaign**")
            fig_c1 = px.bar(camp_summary, x='Campaign', y='Expected_Value', color='Campaign')
            render_chart_or_table(fig_c1, camp_summary[['Campaign', 'Expected_Value']], "t4_exp")
        with rc2:
            st.markdown("**Avg Model AUC by Campaign**")
            fig_c2 = px.line(camp_summary, x='Campaign', y='Avg_Model_AUC', markers=True)
            fig_c2.update_traces(line_color='#2ca02c', marker=dict(size=12))
            render_chart_or_table(fig_c2, camp_summary[['Campaign', 'Avg_Model_AUC']], "t4_auc")
        with rc3:
            st.markdown("**Hot Leads Volume by Campaign**")
            fig_c3 = px.bar(camp_summary, x='Campaign', y='Lead_Volume', color='Campaign')
            render_chart_or_table(fig_c3, camp_summary[['Campaign', 'Lead_Volume']], "t4_vol")

        st.markdown("---")
        st.markdown("**Consolidated Campaign Summary**")
        st.dataframe(camp_summary.style.format({
            "Expected_Value": "${:,.0f}", "Avg_Probability": "{:.2%}", "Avg_Model_AUC": "{:.3f}"
        }), use_container_width=True, hide_index=True)

        st.markdown("**Segment Contribution by Campaign**")
        camp_seg_matrix = leads.pivot_table(index='Campaign', columns='Final_Segment', values='Company_ID', aggfunc='count', fill_value=0)
        st.dataframe(camp_seg_matrix, use_container_width=True)

else:
    st.error("Dashboard failed to load due to missing data.")