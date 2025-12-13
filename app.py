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
    """Load pre-computed rules from CSV files (Apriori, FP-Growth, ECLAT)"""
    apriori_rules = pd.DataFrame()
    fp_rules = pd.DataFrame()
    eclat_rules = pd.DataFrame()
    
    try:
        apriori_rules = pd.read_csv('./Data/apriori/apriori_rules.csv')
        if 'antecedents' in apriori_rules.columns:
            apriori_rules['antecedents'] = apriori_rules['antecedents'].apply(parse_frozenset)
        if 'consequents' in apriori_rules.columns:
            apriori_rules['consequents'] = apriori_rules['consequents'].apply(parse_frozenset)
    except FileNotFoundError:
        st.warning("apriori_rules.csv not found!")
    except Exception as e:
        st.error(f"Error loading apriori rules: {e}")
    
    try:
        fp_rules = pd.read_csv('./Data/fp_growth/fp_rules.csv')
        if 'antecedents' in fp_rules.columns:
            fp_rules['antecedents'] = fp_rules['antecedents'].apply(parse_frozenset)
        if 'consequents' in fp_rules.columns:
            fp_rules['consequents'] = fp_rules['consequents'].apply(parse_frozenset)
    except FileNotFoundError:
        st.warning("fp_rules.csv not found!")
    except Exception as e:
        st.error(f"Error loading fp-growth rules: {e}")
    
    try:
        eclat_rules = pd.read_csv('./Data/ECLAT/ECLAT_rules.csv')
        if 'antecedents' in eclat_rules.columns:
            eclat_rules['antecedents'] = eclat_rules['antecedents'].apply(parse_frozenset)
        if 'consequents' in eclat_rules.columns:
            eclat_rules['consequents'] = eclat_rules['consequents'].apply(parse_frozenset)
    except FileNotFoundError:
        st.warning("ECLAT_rules.csv not found in Data/ECLAT/")
    except Exception as e:
        st.error(f"Error loading ECLAT rules: {e}")
    
    return apriori_rules, fp_rules, eclat_rules


@st.cache_data
def get_all_paths(apriori_rules, fp_rules, eclat_rules):
    """Extract all unique paths from rules"""
    all_paths = set()
    for df in [apriori_rules, fp_rules, eclat_rules]:
        if (df is not None) and (len(df) > 0):
            for s in df['antecedents']:
                all_paths.update(s)
            for s in df['consequents']:
                all_paths.update(s)
    return sorted(list(all_paths))


# get_predictions remains the same logic and works for any rule dataframe

def get_predictions(user_paths, rules_df, top_n=20):
    """Get page predictions based on user's browsing session"""
    if not user_paths or rules_df is None or len(rules_df) == 0:
        return pd.DataFrame()
    
    user_set = set(user_paths)
    predictions = {}
    
    for _, rule in rules_df.iterrows():
        antecedents = rule.get('antecedents', frozenset())
        consequents = rule.get('consequents', frozenset())
        # skip malformed rows
        if not antecedents or not isinstance(antecedents, (set, frozenset)):
            continue
        if not consequents or not isinstance(consequents, (set, frozenset)):
            continue
        
        if antecedents and antecedents.issubset(user_set):
            # build a score that prefers higher confidence and slightly rewards lift
            confidence = float(rule.get('confidence', 0))
            lift = float(rule.get('lift', 1))
            support = float(rule.get('support', 0))
            score = confidence * (1 + (lift - 1) * 0.1)
            
            for page in consequents:
                if page not in user_set:
                    if page not in predictions or score > predictions[page]['score']:
                        predictions[page] = {
                            'score': score,
                            'confidence': confidence,
                            'lift': lift,
                            'support': support,
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
    apriori_rules, fp_rules, eclat_rules = load_precomputed_rules()
    all_paths = get_all_paths(apriori_rules, fp_rules, eclat_rules)

if len(apriori_rules) == 0 and len(fp_rules) == 0 and len(eclat_rules) == 0:
    st.error("No rules loaded. Please ensure apriori_rules.csv, fp_rules.csv and/or ECLAT_rules.csv exist in the project directory under Data/")
    st.stop()

# ======================== SIDEBAR ========================

st.sidebar.markdown("## 📊 Model Statistics")
st.sidebar.metric("Apriori Rules", f"{len(apriori_rules):,}")
st.sidebar.metric("FP-Growth Rules", f"{len(fp_rules):,}")
st.sidebar.metric("ECLAT Rules", f"{len(eclat_rules):,}")
st.sidebar.metric("Unique Paths", f"{len(all_paths):,}")

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Settings")

max_possible = max(len(apriori_rules), len(fp_rules), len(eclat_rules), 1)
max_rules_display = st.sidebar.slider(
    "Max Rules to Display",
    min_value=10,
    max_value=max(max_possible, 1000),
    value=min(500, max(max_possible, 10)),
    step=10
)


# ======================== TABS ========================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔮 Prediction", 
    "⚔️ Comparison", 
    "📊 Apriori Rules", 
    "🌳 FP-Growth Rules",
    "⚡ ECLAT Rules",
    "🕸️ Network Graph"
])

# ======================== TAB 1: PREDICTION ========================

with tab1:
    st.markdown("##  Smart Page Prediction")
    st.markdown("Enter pages a user has visited to predict their next destination.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        algorithm = st.radio(
            "Select Algorithm",
            ["Apriori", "FP-Growth", "ECLAT"],
            horizontal=True
        )
        
        rules_for_prediction = apriori_rules if algorithm == "Apriori" else (fp_rules if algorithm == "FP-Growth" else (eclat_rules if algorithm == "ECLAT" else None))
        
        selected_paths = st.multiselect(
            "🔍 Select visited pages:",
            options=all_paths,
            placeholder="Start typing to search..."
        )
        
      
    
    with col2:
        top_n = st.slider(
            "Number of Predictions",
            min_value=5,
            max_value=50,
            value=15
        )
    
    if selected_paths:
        st.markdown("---")
        st.markdown("###  AI Predictions")
        
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
    st.markdown("##  Algorithm Battle")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("###  Apriori")
        if len(apriori_rules) > 0:
            st.metric("Total Rules", f"{len(apriori_rules):,}")
            st.metric("Avg Confidence", f"{apriori_rules['confidence'].mean():.3f}")
            st.metric("Avg Lift", f"{apriori_rules['lift'].mean():.3f}")
            st.metric("Max Lift", f"{apriori_rules['lift'].max():.3f}")
    
    with col2:
        st.markdown("###  FP-Growth")
        if len(fp_rules) > 0:
            st.metric("Total Rules", f"{len(fp_rules):,}")
            st.metric("Avg Confidence", f"{fp_rules['confidence'].mean():.3f}")
            st.metric("Avg Lift", f"{fp_rules['lift'].mean():.3f}")
            st.metric("Max Lift", f"{fp_rules['lift'].max():.3f}")
    
    with col3:
        st.markdown("###  ECLAT")
        if len(eclat_rules) > 0:
            st.metric("Total Rules", f"{len(eclat_rules):,}")
            st.metric("Avg Confidence", f"{eclat_rules['confidence'].mean():.3f}")
            st.metric("Avg Lift", f"{eclat_rules['lift'].mean():.3f}")
            st.metric("Max Lift", f"{eclat_rules['lift'].max():.3f}")
    
    st.markdown("---")
    
    # Comparison chart
    if len(apriori_rules) > 0 and len(fp_rules) > 0 and len(eclat_rules) > 0:
        comparison_data = pd.DataFrame({
            'Metric': ['Total Rules', 'Avg Confidence', 'Avg Lift', 'Max Lift'],
            'Apriori': [len(apriori_rules), apriori_rules['confidence'].mean(), apriori_rules['lift'].mean(), apriori_rules['lift'].max()],
            'FP-Growth': [len(fp_rules), fp_rules['confidence'].mean(), fp_rules['lift'].mean(), fp_rules['lift'].max()],
            'ECLAT': [len(eclat_rules), eclat_rules['confidence'].mean(), eclat_rules['lift'].mean(), eclat_rules['lift'].max()],
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Apriori', x=comparison_data['Metric'], y=comparison_data['Apriori']))
        fig.add_trace(go.Bar(name='FP-Growth', x=comparison_data['Metric'], y=comparison_data['FP-Growth']))
        fig.add_trace(go.Bar(name='ECLAT', x=comparison_data['Metric'], y=comparison_data['ECLAT']))
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
    
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        if len(eclat_rules) > 0:
            st.markdown("#### ECLAT Top 10")
            top_eclat = eclat_rules.nlargest(10, 'lift')[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
            top_eclat['antecedents'] = top_eclat['antecedents'].apply(lambda x: ', '.join(sorted(x)))
            top_eclat['consequents'] = top_eclat['consequents'].apply(lambda x: ', '.join(sorted(x)))
            st.dataframe(top_eclat, use_container_width=True, hide_index=True)
    

# ======================== TAB 3: APRIORI RULES ========================

with tab3:
    st.markdown("##  Apriori Association Rules")
    
    if len(apriori_rules) > 0:
        st.markdown("###  Support vs Confidence")
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
        
        st.markdown(f"###  All Rules (showing {min(max_rules_display, len(apriori_rules)):,} of {len(apriori_rules):,})")
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
    st.markdown("## FP-Growth Association Rules")
    
    if len(fp_rules) > 0:
        st.markdown("###  Support vs Confidence")
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
        
        st.markdown(f"###  All Rules (showing {min(max_rules_display, len(fp_rules)):,} of {len(fp_rules):,})")
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

# ======================== TAB 5: ECLAT RULES ========================

with tab5:
    st.markdown("##  ECLAT Association Rules")
    
    if len(eclat_rules) > 0:
        st.markdown("###  Support vs Confidence")
        plot_rules_eclat = eclat_rules.copy()
        # only add string columns if antecedents/consequents exist
        if 'antecedents' in plot_rules_eclat.columns:
            plot_rules_eclat['antecedents_str'] = plot_rules_eclat['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        if 'consequents' in plot_rules_eclat.columns:
            plot_rules_eclat['consequents_str'] = plot_rules_eclat['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        # some ECLAT exports may not include confidence/lift; guard against missing columns
        x_col = 'support' if 'support' in plot_rules_eclat.columns else (plot_rules_eclat.columns[0] if len(plot_rules_eclat.columns)>0 else None)
        y_col = 'confidence' if 'confidence' in plot_rules_eclat.columns else (plot_rules_eclat.columns[0] if len(plot_rules_eclat.columns)>0 else None)
        size_col = 'lift' if 'lift' in plot_rules_eclat.columns else None
        color_col = 'lift' if 'lift' in plot_rules_eclat.columns else None
        
        # Create scatter only if we have at least x and y
        if x_col and y_col:
            fig = px.scatter(
                plot_rules_eclat,
                x=x_col,
                y=y_col,
                size=size_col,
                color=color_col,
                hover_data=[c for c in ['antecedents_str', 'consequents_str'] if c in plot_rules_eclat.columns],
                title='<b>Rule Distribution</b>'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"###  All Rules (showing {min(max_rules_display, len(eclat_rules)):,} of {len(eclat_rules):,})")
        rules_display_eclat = eclat_rules.head(max_rules_display).copy()
        if 'antecedents' in rules_display_eclat.columns:
            rules_display_eclat['antecedents'] = rules_display_eclat['antecedents'].apply(lambda x: ', '.join(sorted(x)))
        if 'consequents' in rules_display_eclat.columns:
            rules_display_eclat['consequents'] = rules_display_eclat['consequents'].apply(lambda x: ', '.join(sorted(x)))
        
        # show common columns only
        columns_to_show = [c for c in ['antecedents', 'consequents', 'support', 'confidence', 'lift'] if c in rules_display_eclat.columns]
        st.dataframe(
            rules_display_eclat[columns_to_show].sort_values('lift', ascending=False) if 'lift' in rules_display_eclat.columns else rules_display_eclat[columns_to_show],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No ECLAT rules available. Put ECLAT_rules.csv in Data/ECLAT/")

# ======================== TAB 6: NETWORK GRAPH ========================

with tab6:
    st.markdown("## 🕸️ Association Rules Network Graph")
    st.markdown("Visualize how pages are connected based on association rules.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        network_algo = st.selectbox(
            "Select Algorithm",
            ["Apriori", "FP-Growth", "ECLAT"],
            key="network_algo"
        )
    
    with col2:
        min_lift_filter = st.slider(
            "Minimum Lift",
            min_value=1.0,
            max_value=50.0,
            value=5.0,
            step=0.5,
            key="min_lift_network"
        )
    
    with col3:
        max_nodes = st.slider(
            "Max Nodes",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            key="max_nodes"
        )
    
    # Select rules based on algorithm
    if network_algo == "Apriori":
        rules_for_network = apriori_rules
    elif network_algo == "FP-Growth":
        rules_for_network = fp_rules
    else:
        rules_for_network = eclat_rules
    
    if len(rules_for_network) > 0 and 'lift' in rules_for_network.columns:
        # Filter rules by lift
        filtered_rules = rules_for_network[rules_for_network['lift'] >= min_lift_filter].copy()
        
        if len(filtered_rules) > 0:
            # Build network graph
            G = nx.DiGraph()
            
            # Add edges from rules
            edge_weights = {}
            for _, rule in filtered_rules.iterrows():
                antecedents = rule.get('antecedents', frozenset())
                consequents = rule.get('consequents', frozenset())
                lift = float(rule.get('lift', 1))
                confidence = float(rule.get('confidence', 0))
                
                if antecedents and consequents:
                    for ant in antecedents:
                        for cons in consequents:
                            if (ant, cons) not in edge_weights or edge_weights[(ant, cons)] < lift:
                                edge_weights[(ant, cons)] = lift
                                G.add_edge(ant, cons, weight=lift, confidence=confidence)
            
            # Limit nodes to max_nodes (keep highest degree nodes)
            if len(G.nodes()) > max_nodes:
                node_degrees = dict(G.degree())
                top_nodes = sorted(node_degrees.keys(), key=lambda x: node_degrees[x], reverse=True)[:max_nodes]
                G = G.subgraph(top_nodes).copy()
            
            if len(G.nodes()) > 0:
                # Create layout
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
                
                # Create edge traces
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                edge_trace = go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='rgba(125, 125, 125, 0.5)'),
                    hoverinfo='none',
                    mode='lines'
                )
                
                # Create node traces
                node_x = [pos[node][0] for node in G.nodes()]
                node_y = [pos[node][1] for node in G.nodes()]
                node_degrees = [G.degree(node) for node in G.nodes()]
                
                # Shorten node labels for display
                node_labels = [n.split('/')[-1] if '/' in n else n for n in G.nodes()]
                node_full_labels = list(G.nodes())
                
                node_trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    hoverinfo='text',
                    text=node_labels,
                    textposition='top center',
                    textfont=dict(size=10, color='white'),
                    hovertext=[f"{full}<br>Connections: {deg}" for full, deg in zip(node_full_labels, node_degrees)],
                    marker=dict(
                        showscale=True,
                        colorscale='Viridis',
                        size=[10 + deg * 3 for deg in node_degrees],
                        color=node_degrees,
                        colorbar=dict(
                            thickness=15,
                            title='Connections',
                            xanchor='left',
                            titleside='right'
                        ),
                        line=dict(width=2, color='white')
                    )
                )
                
                # Create figure
                fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f'<b>Page Network ({network_algo})</b><br>Lift ≥ {min_lift_filter}',
                        titlefont=dict(size=16, color='white'),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=60),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=600
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nodes (Pages)", len(G.nodes()))
                with col2:
                    st.metric("Edges (Rules)", len(G.edges()))
                with col3:
                    st.metric("Avg Connections", f"{sum(node_degrees)/len(node_degrees):.1f}")
                
                with st.expander("ℹ️ How to read this graph"):
                    st.markdown("""
                    **Graph Elements:**
                    - **Nodes** = Web pages
                    - **Edges** = Association rules (arrow direction shows: if A then B)
                    - **Node size** = Number of connections (more connected = bigger)
                    - **Node color** = Number of connections (darker = more connected)
                    
                    **Filters:**
                    - **Minimum Lift**: Only show rules with lift above this value (stronger associations)
                    - **Max Nodes**: Limit display to top N most connected pages
                    """)
            else:
                st.warning("No nodes in the graph after filtering. Try lowering the minimum lift.")
        else:
            st.warning(f"No rules found with lift ≥ {min_lift_filter}. Try lowering the minimum lift.")
    else:
        st.warning("No rules available for network visualization.")


