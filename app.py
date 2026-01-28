import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="tracKer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kinetikos Health color palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: #f8f9fa;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        padding: 1.5rem 0 2rem 0;
    }
    
    .main-header span {
        color: #E8913A;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .metric-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .podium-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
    }
    
    .gold-border { border-top: 4px solid #E8913A; }
    .silver-border { border-top: 4px solid #9ca3af; }
    .bronze-border { border-top: 4px solid #b87333; }
    
    .rank-badge {
        font-size: 1.75rem;
        margin-bottom: 0.5rem;
    }
    
    .user-id {
        font-size: 0.8rem;
        color: #6c757d;
        word-break: break-all;
        margin: 0.5rem 0;
    }
    
    .upload-count {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
    }
    
    .upload-label {
        font-size: 0.7rem;
        color: #9ca3af;
    }
    
    .stat-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e9ecef;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .stat-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    .empty-state {
        background: white;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
    }
    
    .empty-icon { font-size: 2.5rem; margin-bottom: 1rem; }
    .empty-title { font-size: 1rem; color: #2d3748; font-weight: 600; }
    .empty-desc { font-size: 0.85rem; color: #6c757d; }
    
    /* Orange accent for active elements */
    .accent-orange { color: #E8913A; }
    .accent-slate { color: #3d4f5f; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style the selectbox */
    .stSelectbox label { color: #2d3748; font-weight: 500; }
    
    /* Make chart lines thicker */
    .stLineChart svg path {
        stroke-width: 3px !important;
    }
</style>
""", unsafe_allow_html=True)

# Header (no subtitle)
st.markdown('<h1 class="main-header"><span>tracKer</span> Dashboard</h1>', unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{users.iloc[0, 0]:,}</div>
        <div class="metric-label">Total Users</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    passive = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'passive_%'", conn)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📱</div>
        <div class="metric-value">{passive.iloc[0, 0]:,}</div>
        <div class="metric-label">Passive Chunks</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    active = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'active_%'", conn)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🚶</div>
        <div class="metric-value">{active.iloc[0, 0]:,}</div>
        <div class="metric-label">Active Chunks</div>
    </div>
    """, unsafe_allow_html=True)

# Row 2: Top 3 Users
st.markdown('<div class="section-title">Top 3 Users by Uploads</div>', unsafe_allow_html=True)

top_users = pd.read_sql("""
    SELECT user_id, COUNT(*) as total_uploads
    FROM sensor_readings
    GROUP BY user_id
    ORDER BY total_uploads DESC
    LIMIT 3
""", conn)

if len(top_users) >= 1:
    podium_cols = st.columns(3)
    
    medals = ["🥇", "🥈", "🥉"]
    borders = ["gold-border", "silver-border", "bronze-border"]
    
    for i, col in enumerate(podium_cols):
        with col:
            if i < len(top_users):
                user = top_users.iloc[i]
                user_display = user['user_id'][:16] + "..." if len(str(user['user_id'])) > 16 else user['user_id']
                st.markdown(f"""
                <div class="podium-card {borders[i]}">
                    <div class="rank-badge">{medals[i]}</div>
                    <div class="user-id">{user_display}</div>
                    <div class="upload-count">{user['total_uploads']:,}</div>
                    <div class="upload-label">uploads</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="podium-card {borders[i]}">
                    <div class="rank-badge">{medals[i]}</div>
                    <div class="user-id">—</div>
                    <div class="upload-count">0</div>
                    <div class="upload-label">uploads</div>
                </div>
                """, unsafe_allow_html=True)
else:
    top_users.index = ["1st", "2nd", "3rd"][:len(top_users)]
    st.dataframe(top_users, use_container_width=True)

# Row 3: Chunks over time
st.markdown('<div class="section-title">Chunks Uploaded Over Time</div>', unsafe_allow_html=True)

timeline = pd.read_sql("""
    SELECT DATE(start_time) as date,
           SUM(CASE WHEN chunk_id LIKE 'active_%' THEN 1 ELSE 0 END) as active,
           SUM(CASE WHEN chunk_id LIKE 'passive_%' THEN 1 ELSE 0 END) as passive
    FROM sensor_readings
    WHERE start_time > NOW() - INTERVAL '30 days'
    GROUP BY date ORDER BY date
""", conn)

if not timeline.empty:
    chart_data = timeline.set_index('date')[['active', 'passive']]
    st.line_chart(chart_data, color=["#E8913A", "#3d4f5f"], height=280)
    
    # Stats row
    stat_cols = st.columns(4)
    total_chunks = int(timeline['active'].sum() + timeline['passive'].sum())
    avg_daily = total_chunks / max(len(timeline), 1)
    
    with stat_cols[0]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total (30d)</div>
            <div class="stat-value">{total_chunks:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[1]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Daily Avg</div>
            <div class="stat-value">{avg_daily:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[2]:
        peak_idx = (timeline['active'] + timeline['passive']).idxmax()
        peak_day = str(timeline.loc[peak_idx, 'date'])
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Peak Day</div>
            <div class="stat-value" style="font-size: 1rem;">{peak_day}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[3]:
        passive_sum = timeline['passive'].sum()
        ratio = timeline['active'].sum() / passive_sum if passive_sum > 0 else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Active/Passive</div>
            <div class="stat-value">{ratio:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-title">No data in the last 30 days</div>
        <div class="empty-desc">Start collecting sensor data to see activity here</div>
    </div>
    """, unsafe_allow_html=True)

# Row 4: Filter by user
st.markdown('<div class="section-title">Filter by User</div>', unsafe_allow_html=True)

user_ids = pd.read_sql("SELECT DISTINCT user_id FROM sensor_readings", conn)
user_list = user_ids['user_id'].tolist()

if user_list:
    selected_user = st.selectbox(
        "Select User",
        user_list,
        format_func=lambda x: f"{x[:30]}..." if len(str(x)) > 30 else x
    )
    
    if selected_user:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN chunk_id LIKE 'active_%%' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN chunk_id LIKE 'passive_%%' THEN 1 ELSE 0 END) as passive,
                MIN(start_time) as first_upload,
                MAX(start_time) as last_upload
            FROM sensor_readings 
            WHERE user_id = %s
        """, (selected_user,))
        stats_row = cursor.fetchone()
        cursor.close()
        
        user_stat_cols = st.columns(4)
        with user_stat_cols[0]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Total Chunks</div>
                <div class="stat-value">{stats_row[0]:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with user_stat_cols[1]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">🚶 Active</div>
                <div class="stat-value accent-orange">{stats_row[1]:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with user_stat_cols[2]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">📱 Passive</div>
                <div class="stat-value accent-slate">{stats_row[2]:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with user_stat_cols[3]:
            last_upload = stats_row[4].strftime('%Y-%m-%d') if stats_row[4] else 'N/A'
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Last Upload</div>
                <div class="stat-value" style="font-size: 1rem;">{last_upload}</div>
            </div>
            """, unsafe_allow_html=True)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT start_time, end_time, chunk_id
            FROM sensor_readings WHERE user_id = %s
            ORDER BY start_time DESC LIMIT 50
        """, (selected_user,))
        rows = cursor.fetchall()
        cursor.close()
        
        if rows:
            user_chunks = pd.DataFrame(rows, columns=['start_time', 'end_time', 'chunk_id'])
            user_chunks['Type'] = user_chunks['chunk_id'].apply(
                lambda x: '🚶 Active' if str(x).startswith('active_') else '📱 Passive'
            )
            user_chunks['Duration'] = (pd.to_datetime(user_chunks['end_time']) - pd.to_datetime(user_chunks['start_time'])).apply(
                lambda x: f"{int(x.total_seconds() // 60)} min" if pd.notna(x) else 'N/A'
            )
            user_chunks['start_time'] = pd.to_datetime(user_chunks['start_time']).dt.strftime('%Y-%m-%d %H:%M')
            user_chunks['end_time'] = pd.to_datetime(user_chunks['end_time']).dt.strftime('%Y-%m-%d %H:%M')
            
            display_df = user_chunks[['Type', 'start_time', 'end_time', 'Duration']].rename(columns={
                'start_time': 'Start',
                'end_time': 'End'
            })
            
            st.dataframe(display_df, use_container_width=True, height=300)
else:
    st.info("No users found in the database yet.")

# Footer
st.markdown(f"""
<div style="text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 2rem 0 1rem 0;">
    tracKer Dashboard • {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)
