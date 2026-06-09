import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Set page configuration
st.set_page_config(page_title="DSS Marketing Dashboard", layout="wide")
st.title("🚀 Enterprise Marketing Decision Support System")

# =====================================================================
# DATA LOADING WITH CACHING
# =====================================================================
@st.cache_data
def load_data():
    raw_file = 'Two_Stage_Clustered_B2B_Data.csv'
    leads_file = 'MASTER_Hot_Leads_All_Campaigns.csv'
    rules_file = 'MASTER_Cross_Sell_Rules_All_Campaigns.xlsx'
    
    if not os.path.exists(raw_file) or not os.path.exists(leads_file) or not os.path.exists(rules_file):
        st.error("Error: Core data files are missing! Please ensure all .csv and .xlsx files are in the same folder.")
        return None, None, None
        
    raw_df = pd.read_csv(raw_file)
    leads_df = pd.read_csv(leads_file)
    rules_df = pd.read_excel(rules_file)
    return raw_df, leads_df, rules_df

raw_data, leads, rules = load_data()

# =====================================================================
# STREAMLIT UI WITH FLEXIBLE TABS
# =====================================================================
if raw_data is not None and leads is not None and rules is not None:
    
    tab1, tab2, tab3 = st.tabs(["📊 Customer Segmentation", "🎯 Prediction & Targeted Sales", "🛒 Recommended Strategy"])

    # -----------------------------------------------------------------
    # TAB 1: CUSTOMER SEGMENTATION (K-MEANS)
    # -----------------------------------------------------------------
    with tab1:
        st.subheader("Customer Segmentation Analysis (K-Means)")
        
        # Bổ sung theo Yêu cầu 1: Show số lượng doanh nghiệp mỗi cụm
        col1_a, col1_b = st.columns([1, 1.5])
        
        with col1_a:
            st.write("### Segment Size (Number of Companies)")
            seg_counts = raw_data['Final_Segment'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Company Count']
            
            # Hiển thị bảng số liệu và biểu đồ cột đếm số lượng
            st.dataframe(seg_counts, use_container_width=True)
            st.bar_chart(seg_counts.set_index('Segment'), color="#4CAF50")
            
        with col1_b:
            st.write("### Customer Clusters Overview")
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            sns.scatterplot(
                data=raw_data, 
                x='IT_Budget_USD', 
                y='Mnt_Total_Enterprise_Spend', 
                hue='Final_Segment', 
                palette='Set2',
                ax=ax1
            )
            ax1.set_title("Financial Budget vs Historical Spend", fontsize=11, fontweight='bold')
            st.pyplot(fig1, use_container_width=True)
            
        st.markdown("---")
        st.write("### Raw Data Reference")
        st.dataframe(raw_data, use_container_width=True)

    # -----------------------------------------------------------------
    # TAB 2: PREDICTION & TARGETED SALES (DECISION TREE)
    # -----------------------------------------------------------------
    with tab2:
        st.subheader("Targeted Sales Engine (Decision Tree Phasing)")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            campaign_filter = st.selectbox("Select Target Campaign:", leads['Campaign'].unique(), key="dt_camp")
        with col_f2:
            # Thêm tùy chọn "All Segments" để nhìn được bao quát
            available_segs = ["All Segments"] + list(leads[leads['Campaign'] == campaign_filter]['Final_Segment'].unique())
            segment_filter = st.selectbox("Select Target Segment:", available_segs, key="dt_seg")

        # Logic bộ lọc
        if segment_filter != "All Segments":
            filtered_leads = leads[(leads['Campaign'] == campaign_filter) & (leads['Final_Segment'] == segment_filter)]
        else:
            filtered_leads = leads[leads['Campaign'] == campaign_filter]

        col_view1, col_view2 = st.columns([1.2, 1])
        
        with col_view1:
            st.write(f"### Targeted Hot Leads List")
            st.dataframe(
                filtered_leads[['Company_ID', 'Final_Segment', 'Probability_To_Buy', 'IT_Budget_USD', 'Mnt_Total_Enterprise_Spend']], 
                use_container_width=True
            )
            csv_data = filtered_leads.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Hot Leads CSV for Telesales", 
                data=csv_data, 
                file_name=f"hot_leads.csv", 
                mime="text/csv"
            )
            
        with col_view2:
            st.write("### Probability to Buy Distribution")
            if not filtered_leads.empty:
                fig2, ax2 = plt.subplots(figsize=(6, 3.5))
                sns.histplot(data=filtered_leads, x='Probability_To_Buy', bins=10, kde=True, ax=ax2, color='royalblue')
                st.pyplot(fig2, use_container_width=True)
            
            # Bổ sung theo Yêu cầu 2: Budget Distribution of Hot Leads
            st.write("### Budget Distribution of Hot Leads")
            if not filtered_leads.empty:
                if segment_filter == "All Segments":
                    # Nếu chọn All, vẽ biểu đồ so sánh ngân sách trung bình giữa các cụm
                    budget_dist = filtered_leads.groupby('Final_Segment')['IT_Budget_USD'].mean()
                    st.bar_chart(budget_dist, color="#FF9800")
                else:
                    # Nếu chọn 1 cụm cụ thể, vẽ biểu đồ Histogram phân phối ngân sách của riêng cụm đó
                    fig3, ax3 = plt.subplots(figsize=(6, 3.5))
                    sns.histplot(data=filtered_leads, x='IT_Budget_USD', bins=10, ax=ax3, color='seagreen')
                    st.pyplot(fig3, use_container_width=True)
            else:
                st.info("No leads available to visualize.")

    # -----------------------------------------------------------------
    # TAB 3: RECOMMENDED STRATEGY (APRIORI CROSS-SELL)
    # -----------------------------------------------------------------
    with tab3:
        st.subheader("Interactive Cross-Sell Recommendation Matrix (Apriori)")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rule_campaign = st.selectbox("Select Campaign Context:", rules['Campaign'].unique(), key="ap_camp")
        with col_r2:
            # Đồng bộ thêm "All Segments" cho Tab 3
            available_rule_segs = ["All Segments"] + list(rules[rules['Campaign'] == rule_campaign]['Segment'].unique())
            rule_segment = st.selectbox("Select Segment Context:", available_rule_segs, key="ap_seg")

        if rule_segment != "All Segments":
            context_rules = rules[(rules['Campaign'] == rule_campaign) & (rules['Segment'] == rule_segment)]
        else:
            context_rules = rules[rules['Campaign'] == rule_campaign]

        product_universe = ['Cloud_Infrastructure', 'CRM_Software', 'ERP_Systems', 'Cybersecurity', 'Collaboration_Tools', 'AI_Data_Analytics']
        selected_owned_products = st.multiselect("What does this specific customer already own? (Prerequisites)", product_universe)

        if selected_owned_products:
            def check_strict_subset(antecedent_str):
                items_in_rule = [item.strip() for item in str(antecedent_str).split(',')]
                return set(items_in_rule).issubset(set(selected_owned_products))
            
            final_filtered_rules = context_rules[context_rules['Khách Đã Mua'].apply(check_strict_subset)]
        else:
            final_filtered_rules = context_rules

        if not final_filtered_rules.empty:
            st.write("### Top Cross-Sell Combinations (Ranked by Lift)")
            top_rules = final_filtered_rules.sort_values(by='Lift', ascending=False).head(5).copy()
            top_rules['Rule_Path'] = top_rules['Khách Đã Mua'] + " ➔ " + top_rules['Gợi Ý Bán Chéo']
            st.bar_chart(top_rules.set_index('Rule_Path')['Lift'], color="#E91E63")

            st.write("### Executable Cross-Sell Strategy Matrix")
            st.dataframe(
                final_filtered_rules[['Segment', 'Khách Đã Mua', 'Gợi Ý Bán Chéo', 'Confidence', 'Lift']], 
                use_container_width=True
            )
        else:
            st.warning("No cross-sell rules match your strict ownership criteria for this segment. Try expanding the product checkboxes.")

else:
    st.error("Dashboard could not initialize. Please verify data pipeline generation steps.")