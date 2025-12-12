import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import re

# Page configuration
st.set_page_config(
    page_title="Web Usage Mining Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 40px rgba(0,212,255,0.3);
    }
    
    .sub-header {
        text-align: center;
        color: #a1a1aa;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.2) 0%, rgba(0,212,255,0.1) 100%);
        border: 1px solid rgba(124,58,237,0.3);
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0,212,255,0.5);
        box-shadow: 0 20px 40px rgba(0,212,255,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #00d4ff 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a1a1aa;
        margin-top: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 0.5rem;
        border-radius: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0.5rem;
        padding: 12px 24px;
        color: #a1a1aa;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(124,58,237,0.2);
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #00d4ff 100%);
        color: white;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .glass-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .prediction-item {
        background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(124,58,237,0.1) 100%);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 0.75rem;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .prediction-item:hover {
        border-color: rgba(0,212,255,0.5);
        transform: translateX(5px);
    }
    
    .stMultiSelect > div > div {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #00d4ff 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(124,58,237,0.4);
    }
    
    .sidebar .stMetric {
        background: rgba(255,255,255,0.05);
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #0f0f23 100%);
    }
    
    .stDataFrame {
        border-radius: 0.75rem;
        overflow: hidden;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    p, span, label {
        color: #e4e4e7 !important;
    }
    
    .stRadio > label {
        color: white !important;
    }
    
    .stSlider > label {
        color: white !important;
    }
    
    .footer-text {
        text-align: center;
        color: #71717a;
        padding: 2rem;
        font-size: 0.9rem;
    }
    
    .glow-text {
        text-shadow: 0 0 20px rgba(0,212,255,0.5);
    }
    
    /* Animated gradient background for header */
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .animated-header {
        background: linear-gradient(270deg, #00d4ff, #7c3aed, #f472b6, #00d4ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 8s ease infinite;
    }
</style>
""", unsafe_allow_html=True)

# ======================== DATA LOADING ========================

def parse_frozenset(frozenset_str):
    """Parse frozenset string from CSV back to Python set"""
    if pd.isna(frozenset_str):
        return frozenset()
    
    match = re.search(r"frozenset\(\{(.+?)\}\)", str(frozenset_str))
    if match:
        items_str = match.group(1)
        items = re.findall(r"'([^']+)'", items_str)
        return frozenset(items)
    return frozenset()


@st.cache_data
def load_precomputed_rules():
    """Load pre-computed rules from CSV files"""
    apriori_rules = pd.DataFrame()
    fp_rules = pd.DataFrame()
    
    try:
        apriori_rules = pd.read_csv('./Data/apriori/apriori_rules.csv')
        apriori_rules['antecedents'] = apriori_rules['antecedents'].apply(parse_frozenset)
        apriori_rules['consequents'] = apriori_rules['consequents'].apply(parse_frozenset)
    except FileNotFoundError:
        st.warning("apriori_rules.csv not found!")
    
    try:
        fp_rules = pd.read_csv('./Data/fp_growth/fp_rules.csv')
        fp_rules['antecedents'] = fp_rules['antecedents'].apply(parse_frozenset)
        fp_rules['consequents'] = fp_rules['consequents'].apply(parse_frozenset)
    except FileNotFoundError:
        st.warning("fp_rules.csv not found!")
    
    return apriori_rules, fp_rules


@st.cache_data
def get_all_paths(apriori_rules, fp_rules):
    """Extract all unique paths from rules"""
    all_paths = set()
    
    for df in [apriori_rules, fp_rules]:
        if len(df) > 0:
            for s in df['antecedents']:
                all_paths.update(s)
            for s in df['consequents']:
                all_paths.update(s)
    
    return sorted(list(all_paths))


def get_predictions(user_paths, rules_df, top_n=20):
    """Get page predictions based on user's browsing session"""
    if not user_paths or len(rules_df) == 0:
        return pd.DataFrame()
    
    user_set = set(user_paths)
    predictions = {}
    
    for _, rule in rules_df.iterrows():
        antecedents = rule['antecedents']
        consequents = rule['consequents']
        
        if antecedents and antecedents.issubset(user_set):
            score = rule['confidence'] * (1 + (rule['lift'] - 1) * 0.1)
            
            for page in consequents:
                if page not in user_set:
                    if page not in predictions or score > predictions[page]['score']:
                        predictions[page] = {
                            'score': score,
                            'confidence': rule['confidence'],
                            'lift': rule['lift'],
                            'support': rule['support'],
                            'based_on': ', '.join(sorted(antecedents))
                        }
    
    if not predictions:
        return pd.DataFrame()
    
    results = pd.DataFrame([
        {
            'Predicted Page': page,
            'Confidence': data['confidence'],
            'Lift': data['lift'],
            'Support': data['support'],
            'Score': data['score'],
            'Based On': data['based_on']
        }
        for page, data in predictions.items()
    ])
    
    return results.sort_values('Score', ascending=False).head(top_n)


# ======================== MAIN APP ========================

# Header with animation
st.markdown('<h1 class="main-header animated-header">🔍 Web Usage Mining Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Navigation Pattern Analysis with Association Rules</p>', unsafe_allow_html=True)

# Load pre-computed rules
with st.spinner("Loading pre-computed association rules..."):
    apriori_rules, fp_rules = load_precomputed_rules()
    all_paths = get_all_paths(apriori_rules, fp_rules)

if len(apriori_rules) == 0 and len(fp_rules) == 0:
    st.error("No rules loaded. Please ensure apriori_rules.csv and/or fp_rules.csv exist in the project directory.")
    st.stop()

# ======================== SIDEBAR ========================

st.sidebar.markdown("## 📊 Model Statistics")
st.sidebar.metric("Apriori Rules", f"{len(apriori_rules):,}")
st.sidebar.metric("FP-Growth Rules", f"{len(fp_rules):,}")
st.sidebar.metric("Unique Paths", f"{len(all_paths):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Settings")

max_rules_display = st.sidebar.slider(
    "Max Rules to Display",
    min_value=10,
    max_value=max(len(apriori_rules), len(fp_rules), 1000),
    value=min(500, max(len(apriori_rules), len(fp_rules))),
    step=10
)


# ======================== TABS ========================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Prediction", 
    "⚔️ Comparison", 
    "🔵 Apriori Rules", 
    "🟣 FP-Growth Rules"
])

# ======================== TAB 1: PREDICTION ========================

with tab1:
    st.markdown("## 🔮 Smart Page Prediction")
    st.markdown("Enter pages a user has visited to predict their next destination.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        algorithm = st.radio(
            "Select Algorithm",
            ["Apriori", "FP-Growth"],
            horizontal=True
        )
        
        rules_for_prediction = apriori_rules if algorithm == "Apriori" else fp_rules
        
        selected_paths = st.multiselect(
            "🔍 Select visited pages:",
            options=all_paths,
            placeholder="Start typing to search..."
        )
        
        st.markdown("**⚡ Quick Examples:**")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🚀 Apollo History", use_container_width=True):
                st.session_state['pred_example'] = ['/history/apollo']
        with col_b:
            if st.button("🛸 Shuttle Countdown", use_container_width=True):
                st.session_state['pred_example'] = ['/shuttle/countdown']
        with col_c:
            if st.button("🛰️ ELV Rockets", use_container_width=True):
                st.session_state['pred_example'] = ['/elv']
        
        if 'pred_example' in st.session_state:
            selected_paths = st.session_state['pred_example']
            del st.session_state['pred_example']
            st.rerun()
    
    with col2:
        top_n = st.slider(
            "Number of Predictions",
            min_value=5,
            max_value=50,
            value=15
        )
    
    if selected_paths:
        st.markdown("---")
        st.markdown("### 🎯 AI Predictions")
        
        predictions = get_predictions(selected_paths, rules_for_prediction, top_n)
        
        if len(predictions) > 0:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig = px.bar(
                    predictions,
                    x='Score',
                    y='Predicted Page',
                    orientation='h',
                    color='Confidence',
                    color_continuous_scale='Viridis',
                    title='<b>Top Predicted Pages</b>'
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title_font=dict(size=18, color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                display_df = predictions.copy()
                display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.1%}")
                display_df['Lift'] = display_df['Lift'].apply(lambda x: f"{x:.2f}")
                display_df['Score'] = display_df['Score'].apply(lambda x: f"{x:.3f}")
                
                st.dataframe(
                    display_df[['Predicted Page', 'Confidence', 'Lift', 'Score', 'Based On']],
                    use_container_width=True,
                    height=500,
                    hide_index=True
                )
            
            with st.expander("ℹ️ How predictions work"):
                st.markdown("""
                **Algorithm:** 
                1. Find all rules where your selected pages match the rule's antecedents
                2. Score predictions using: `Score = Confidence × (1 + 0.1 × (Lift - 1))`
                3. Rank by score, excluding pages you've already visited
                """)
        else:
            st.warning("🔍 No predictions found. Try selecting different pages.")
            st.info("💡 Try pages like `/history/apollo`, `/shuttle/countdown`, or `/elv`")
    else:
        st.info("👆 Select pages above to get AI-powered predictions")

# ======================== TAB 2: COMPARISON ========================

with tab2:
    st.markdown("## ⚔️ Algorithm Battle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔵 Apriori")
        if len(apriori_rules) > 0:
            st.metric("Total Rules", f"{len(apriori_rules):,}")
            st.metric("Avg Confidence", f"{apriori_rules['confidence'].mean():.3f}")
            st.metric("Avg Lift", f"{apriori_rules['lift'].mean():.3f}")
            st.metric("Max Lift", f"{apriori_rules['lift'].max():.3f}")
    
    with col2:
        st.markdown("### 🟣 FP-Growth")
        if len(fp_rules) > 0:
            st.metric("Total Rules", f"{len(fp_rules):,}")
            st.metric("Avg Confidence", f"{fp_rules['confidence'].mean():.3f}")
            st.metric("Avg Lift", f"{fp_rules['lift'].mean():.3f}")
            st.metric("Max Lift", f"{fp_rules['lift'].max():.3f}")
    
    st.markdown("---")
    
    # Comparison chart
    if len(apriori_rules) > 0 and len(fp_rules) > 0:
        comparison_data = pd.DataFrame({
            'Metric': ['Total Rules', 'Avg Confidence', 'Avg Lift', 'Max Lift'],
            'Apriori': [len(apriori_rules), apriori_rules['confidence'].mean(), apriori_rules['lift'].mean(), apriori_rules['lift'].max()],
            'FP-Growth': [len(fp_rules), fp_rules['confidence'].mean(), fp_rules['lift'].mean(), fp_rules['lift'].max()]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Apriori', x=comparison_data['Metric'], y=comparison_data['Apriori'], marker_color='#00d4ff'))
        fig.add_trace(go.Bar(name='FP-Growth', x=comparison_data['Metric'], y=comparison_data['FP-Growth'], marker_color='#7c3aed'))
        fig.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title='<b>Algorithm Comparison</b>',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🏆 Top Rules Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(apriori_rules) > 0:
            st.markdown("#### Apriori Top 10")
            top_apriori = apriori_rules.nlargest(10, 'lift')[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
            top_apriori['antecedents'] = top_apriori['antecedents'].apply(lambda x: ', '.join(sorted(x)))
            top_apriori['consequents'] = top_apriori['consequents'].apply(lambda x: ', '.join(sorted(x)))
            st.dataframe(top_apriori, use_container_width=True, hide_index=True)
    
    with col2:
        if len(fp_rules) > 0:
            st.markdown("#### FP-Growth Top 10")
            top_fp = fp_rules.nlargest(10, 'lift')[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
            top_fp['antecedents'] = top_fp['antecedents'].apply(lambda x: ', '.join(sorted(x)))
            top_fp['consequents'] = top_fp['consequents'].apply(lambda x: ', '.join(sorted(x)))
            st.dataframe(top_fp, use_container_width=True, hide_index=True)

# ======================== TAB 3: APRIORI RULES ========================

with tab3:
    st.markdown("## 🔵 Apriori Association Rules")
    
    if len(apriori_rules) > 0:
        st.markdown("### 📈 Support vs Confidence")
        plot_rules = apriori_rules.copy()
        plot_rules['antecedents_str'] = plot_rules['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        plot_rules['consequents_str'] = plot_rules['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        fig = px.scatter(
            plot_rules,
            x='support',
            y='confidence',
            size='lift',
            color='lift',
            hover_data=['antecedents_str', 'consequents_str'],
            color_continuous_scale='Viridis',
            title='<b>Rule Distribution</b>'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"### 📋 All Rules (showing {min(max_rules_display, len(apriori_rules)):,} of {len(apriori_rules):,})")
        rules_display = apriori_rules.head(max_rules_display).copy()
        rules_display['antecedents'] = rules_display['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        rules_display['consequents'] = rules_display['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        st.dataframe(
            rules_display[['antecedents', 'consequents', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No Apriori rules available.")

# ======================== TAB 4: FP-GROWTH RULES ========================

with tab4:
    st.markdown("## 🟣 FP-Growth Association Rules")
    
    if len(fp_rules) > 0:
        st.markdown("### 📈 Support vs Confidence")
        plot_rules_fp = fp_rules.copy()
        plot_rules_fp['antecedents_str'] = plot_rules_fp['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        plot_rules_fp['consequents_str'] = plot_rules_fp['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        fig = px.scatter(
            plot_rules_fp,
            x='support',
            y='confidence',
            size='lift',
            color='lift',
            hover_data=['antecedents_str', 'consequents_str'],
            color_continuous_scale='Plasma',
            title='<b>Rule Distribution</b>'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"### 📋 All Rules (showing {min(max_rules_display, len(fp_rules)):,} of {len(fp_rules):,})")
        rules_display_fp = fp_rules.head(max_rules_display).copy()
        rules_display_fp['antecedents'] = rules_display_fp['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        rules_display_fp['consequents'] = rules_display_fp['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        st.dataframe(
            rules_display_fp[['antecedents', 'consequents', 'support', 'confidence', 'lift']].sort_values('lift', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No FP-Growth rules available.")

# ======================== TAB 5: NETWORK GRAPH ========================



# Footer
st.markdown("---")
st.markdown("""
<div class="footer-text">
    <p>🔍 <strong>Web Usage Mining Dashboard</strong> | Powered by AI Association Rules</p>
    <p>📊 Data: NASA Web Server Logs | ⚡ Algorithms: Apriori & FP-Growth</p>
</div>
""", unsafe_allow_html=True)
