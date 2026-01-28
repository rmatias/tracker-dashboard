import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config with custom theme
st.set_page_config(
    page_title="tracKer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for stunning visuals
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
        letter-spacing: -1px;
    }
    
    .sub-header {
        color: #8892b0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1e1e30 0%, #2a2a4a 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102,126,234,0.2);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #fff 0%, #a8b2d1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #8892b0;
        font-size: 0.95rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .delta-positive {
        background: rgba(0,255,136,0.15);
        color: #00ff88;
    }
    
    .delta-neutral {
        background: rgba(255,255,255,0.1);
        color: #8892b0;
    }
    
    /* Section headers */
    .section-header {
        color: #ccd6f6;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(102,126,234,0.3);
    }
    
    /* Podium styling */
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 1rem;
        padding: 2rem 0;
    }
    
    .podium-item {
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
        transition: transform 0.3s ease;
    }
    
    .podium-item:hover {
        transform: scale(1.05);
    }
    
    .gold {
        background: linear-gradient(145deg, #ffd700 0%, #b8860b 100%);
        min-height: 180px;
    }
    
    .silver {
        background: linear-gradient(145deg, #c0c0c0 0%, #808080 100%);
        min-height: 140px;
    }
    
    .bronze {
        background: linear-gradient(145deg, #cd7f32 0%, #8b4513 100%);
        min-height: 100px;
    }
    
    .podium-rank {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .podium-user {
        font-size: 0.9rem;
        font-weight: 600;
        word-break: break-all;
        max-width: 150px;
    }
    
    .podium-count {
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Data table styling */
    .dataframe {
        background: #1e1e30 !important;
        border-radius: 10px !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #1e1e30;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    /* Chart container */
    .chart-container {
        background: linear-gradient(145deg, #1e1e30 0%, #2a2a4a 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Status indicator */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff88;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0,255,136,0.4); }
        50% { opacity: 0.8; box-shadow: 0 0 0 10px rgba(0,255,136,0); }
    }
    
    /* User card */
    .user-card {
        background: linear-gradient(145deg, #1e1e30 0%, #2a2a4a 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1rem;
    }
    
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.5), transparent);
        margin: 2rem 0;
    }
    
    /* Info box */
    .info-box {
        background: rgba(102,126,234,0.1);
        border: 1px solid rgba(102,126,234,0.3);
        border-radius: 10px;
        padding: 1rem;
        color: #a8b2d1;
    }
    
    /* Animate on load */
    .animate-fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 tracKer Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header"><span class="status-online"></span>Live Data • Real-time Sensor Analytics</p>', unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )

conn = get_connection()

# Row 1: Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    users = pd.read_sql("SELECT COUNT(DISTINCT user_id) as count FROM sensor_readings", conn)
    user_count = users.iloc[0, 0]
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{user_count:,}</div>
        <div class="metric-label">Total Users</div>
        <div class="metric-delta delta-positive">● Active</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    passive = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'passive_%'", conn)
    passive_count = passive.iloc[0, 0]
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-icon">🌙</div>
        <div class="metric-value">{passive_count:,}</div>
        <div class="metric-label">Passive Chunks</div>
        <div class="metric-delta delta-neutral">Background</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    active = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'active_%'", conn)
    active_count = active.iloc[0, 0]
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div class="metric-icon">⚡</div>
        <div class="metric-value">{active_count:,}</div>
        <div class="metric-label">Active Chunks</div>
        <div class="metric-delta delta-positive">Recording</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Row 2: Top 3 Users with Podium
st.markdown('<h2 class="section-header">🏆 Top Contributors</h2>', unsafe_allow_html=True)

top_users = pd.read_sql("""
    SELECT user_id, COUNT(*) as total_uploads
    FROM sensor_readings
    GROUP BY user_id
    ORDER BY total_uploads DESC
    LIMIT 3
""", conn)

if len(top_users) >= 3:
    # Create podium layout
    podium_cols = st.columns([1, 1, 1, 1, 1])
    
    # Silver (2nd place) - left
    with podium_cols[1]:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 40px;">
            <div style="font-size: 3rem;">🥈</div>
            <div style="background: linear-gradient(145deg, #c0c0c0 0%, #808080 100%);
                        border-radius: 15px; padding: 1.5rem; margin-top: 1rem;
                        box-shadow: 0 8px 32px rgba(192,192,192,0.3);">
                <div style="font-size: 0.8rem; color: #1a1a2e; font-weight: 600; 
                            word-break: break-all; margin-bottom: 0.5rem;">
                    {top_users.iloc[1]['user_id'][:12]}...
                </div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #1a1a2e;">
                    {top_users.iloc[1]['total_uploads']:,}
                </div>
                <div style="font-size: 0.7rem; color: #333;">uploads</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gold (1st place) - center
    with podium_cols[2]:
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 4rem;">👑</div>
            <div style="background: linear-gradient(145deg, #ffd700 0%, #b8860b 100%);
                        border-radius: 15px; padding: 2rem; margin-top: 0.5rem;
                        box-shadow: 0 12px 40px rgba(255,215,0,0.4);">
                <div style="font-size: 0.9rem; color: #1a1a2e; font-weight: 600; 
                            word-break: break-all; margin-bottom: 0.5rem;">
                    {top_users.iloc[0]['user_id'][:12]}...
                </div>
                <div style="font-size: 2rem; font-weight: 700; color: #1a1a2e;">
                    {top_users.iloc[0]['total_uploads']:,}
                </div>
                <div style="font-size: 0.75rem; color: #333;">uploads</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bronze (3rd place) - right
    with podium_cols[3]:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 60px;">
            <div style="font-size: 2.5rem;">🥉</div>
            <div style="background: linear-gradient(145deg, #cd7f32 0%, #8b4513 100%);
                        border-radius: 15px; padding: 1.2rem; margin-top: 1rem;
                        box-shadow: 0 8px 32px rgba(205,127,50,0.3);">
                <div style="font-size: 0.75rem; color: #fff; font-weight: 600; 
                            word-break: break-all; margin-bottom: 0.5rem;">
                    {top_users.iloc[2]['user_id'][:12]}...
                </div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #fff;">
                    {top_users.iloc[2]['total_uploads']:,}
                </div>
                <div style="font-size: 0.65rem; color: #ddd;">uploads</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    top_users.index = ["1st", "2nd", "3rd"][:len(top_users)]
    st.dataframe(top_users, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Row 3: Chunks over time
st.markdown('<h2 class="section-header">📈 Activity Timeline</h2>', unsafe_allow_html=True)

timeline = pd.read_sql("""
    SELECT DATE(start_time) as date,
           SUM(CASE WHEN chunk_id LIKE 'active_%' THEN 1 ELSE 0 END) as active,
           SUM(CASE WHEN chunk_id LIKE 'passive_%' THEN 1 ELSE 0 END) as passive
    FROM sensor_readings
    WHERE start_time > NOW() - INTERVAL '30 days'
    GROUP BY date ORDER BY date
""", conn)

if not timeline.empty:
    # Create beautiful Plotly chart
    fig = go.Figure()
    
    # Add passive area
    fig.add_trace(go.Scatter(
        x=timeline['date'],
        y=timeline['passive'],
        name='Passive',
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        mode='lines',
        hovertemplate='<b>%{x}</b><br>Passive: %{y}<extra></extra>'
    ))
    
    # Add active area
    fig.add_trace(go.Scatter(
        x=timeline['date'],
        y=timeline['active'],
        name='Active',
        fill='tozeroy',
        fillcolor='rgba(118, 75, 162, 0.3)',
        line=dict(color='#764ba2', width=3),
        mode='lines',
        hovertemplate='<b>%{x}</b><br>Active: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#8892b0', family='Inter'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(size=11)
        ),
        hovermode='x unified',
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Summary stats below chart
    stat_cols = st.columns(4)
    with stat_cols[0]:
        total_chunks = timeline['active'].sum() + timeline['passive'].sum()
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.8rem; color: #8892b0;">Total (30 days)</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #ccd6f6;">{total_chunks:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[1]:
        avg_daily = total_chunks / max(len(timeline), 1)
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.8rem; color: #8892b0;">Daily Average</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #ccd6f6;">{avg_daily:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[2]:
        peak_day = timeline.loc[(timeline['active'] + timeline['passive']).idxmax(), 'date']
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.8rem; color: #8892b0;">Peak Day</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: #ccd6f6;">{peak_day}</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[3]:
        ratio = timeline['active'].sum() / max(timeline['passive'].sum(), 1)
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.8rem; color: #8892b0;">Active/Passive Ratio</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #ccd6f6;">{ratio:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-box" style="text-align: center; padding: 3rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
        <div style="font-size: 1.2rem; color: #ccd6f6;">No data in the last 30 days</div>
        <div style="font-size: 0.9rem; color: #8892b0; margin-top: 0.5rem;">
            Start collecting sensor data to see activity here
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Row 4: Filter by user
st.markdown('<h2 class="section-header">🔍 User Explorer</h2>', unsafe_allow_html=True)

user_ids = pd.read_sql("SELECT DISTINCT user_id FROM sensor_readings", conn)

# Create a nicer user selector
user_list = user_ids['user_id'].tolist()

col_select, col_info = st.columns([2, 1])

with col_select:
    selected_user = st.selectbox(
        "Select a user to view their activity",
        user_list,
        format_func=lambda x: f"👤 {x[:20]}..." if len(x) > 20 else f"👤 {x}"
    )

if selected_user:
    # User stats card
    user_stats = pd.read_sql("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN chunk_id LIKE 'active_%' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN chunk_id LIKE 'passive_%' THEN 1 ELSE 0 END) as passive,
            MIN(start_time) as first_upload,
            MAX(start_time) as last_upload
        FROM sensor_readings 
        WHERE user_id = %s
    """, conn, params=(selected_user,))
    
    with col_info:
        st.markdown(f"""
        <div class="user-card">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div class="user-avatar">{selected_user[0].upper()}</div>
                <div>
                    <div style="color: #ccd6f6; font-weight: 600;">Selected User</div>
                    <div style="color: #8892b0; font-size: 0.8rem;">{user_stats.iloc[0]['total']:,} total chunks</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # User activity breakdown
    user_metric_cols = st.columns(4)
    
    with user_metric_cols[0]:
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.75rem; color: #8892b0;">⚡ Active</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #764ba2;">{user_stats.iloc[0]['active']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with user_metric_cols[1]:
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.75rem; color: #8892b0;">🌙 Passive</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #667eea;">{user_stats.iloc[0]['passive']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with user_metric_cols[2]:
        first_date = user_stats.iloc[0]['first_upload']
        first_str = first_date.strftime('%b %d, %Y') if first_date else 'N/A'
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.75rem; color: #8892b0;">📅 First Upload</div>
            <div style="font-size: 1rem; font-weight: 600; color: #ccd6f6;">{first_str}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with user_metric_cols[3]:
        last_date = user_stats.iloc[0]['last_upload']
        last_str = last_date.strftime('%b %d, %Y') if last_date else 'N/A'
        st.markdown(f"""
        <div class="info-box">
            <div style="font-size: 0.75rem; color: #8892b0;">🕐 Last Upload</div>
            <div style="font-size: 1rem; font-weight: 600; color: #ccd6f6;">{last_str}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent chunks table with better styling
    user_chunks = pd.read_sql("""
        SELECT start_time, end_time, chunk_id
        FROM sensor_readings WHERE user_id = %s
        ORDER BY start_time DESC LIMIT 50
    """, conn, params=(selected_user,))
    
    # Format the dataframe
    if not user_chunks.empty:
        user_chunks['Type'] = user_chunks['chunk_id'].apply(
            lambda x: '⚡ Active' if x.startswith('active_') else '🌙 Passive'
        )
        user_chunks['Duration'] = (user_chunks['end_time'] - user_chunks['start_time']).apply(
            lambda x: f"{x.total_seconds():.0f}s" if pd.notna(x) else 'N/A'
        )
        user_chunks['start_time'] = user_chunks['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        user_chunks['end_time'] = user_chunks['end_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        display_df = user_chunks[['Type', 'start_time', 'end_time', 'Duration', 'chunk_id']].rename(columns={
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'chunk_id': 'Chunk ID'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            column_config={
                "Type": st.column_config.TextColumn(width="small"),
                "Duration": st.column_config.TextColumn(width="small"),
                "Start Time": st.column_config.TextColumn(width="medium"),
                "End Time": st.column_config.TextColumn(width="medium"),
                "Chunk ID": st.column_config.TextColumn(width="large"),
            }
        )

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #4a5568; font-size: 0.85rem; padding: 1rem;">
    <span style="color: #667eea;">●</span> tracKer Dashboard • Built with Streamlit
    <br><span style="font-size: 0.75rem;">Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</span>
</div>
""", unsafe_allow_html=True)
