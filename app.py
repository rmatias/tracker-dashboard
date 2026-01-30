import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="tracKer Dashboard",
    page_icon="🚶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Password protection
def check_password():
    """Returns True if the user entered the correct password."""
    
    walking_k_small = '''<svg style="display:inline-block;width:24px;height:32px;vertical-align:middle;margin:0 -2px;" viewBox="0 0 40 52" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="6" r="5" fill="#E8913A"/>
        <line x1="20" y1="11" x2="20" y2="35" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
        <line x1="20" y1="18" x2="32" y2="8" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
        <line x1="20" y1="18" x2="10" y2="24" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
        <line x1="20" y1="35" x2="32" y2="50" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
        <line x1="20" y1="35" x2="8" y2="50" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
    </svg>'''
    
    def password_entered():
        if st.session_state["password"] == st.secrets["DASHBOARD_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show password input
        st.markdown("""
        <style>
            .stApp { background: #f8f9fa; }
            [data-testid="stMainBlockContainer"] {
                max-width: 400px;
                margin: 15vh auto;
                padding: 2rem;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .password-title {
                font-size: 1.5rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.5rem;
                text-align: center;
            }
            .password-hint {
                color: #6c757d;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="password-title">trac{walking_k_small}er Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="password-hint">Enter password to continue</div>', unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.markdown("""
        <style>
            .stApp { background: #f8f9fa; }
            [data-testid="stMainBlockContainer"] {
                max-width: 400px;
                margin: 15vh auto;
                padding: 2rem;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .password-title {
                font-size: 1.5rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.5rem;
                text-align: center;
            }
            .password-hint {
                color: #6c757d;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="password-title">trac{walking_k_small}er Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="password-hint">Enter password to continue</div>', unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        st.error("Wrong password. Try again!")
        return False
    
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# Kinetikos Health color palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: #f8f9fa;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #2d3748;
        text-align: center;
        padding: 1.5rem 0 2rem 0;
    }
    
    .walking-k {
        display: inline-block;
        width: 44px;
        height: 58px;
        vertical-align: middle;
        margin: 0 -2px;
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
    
    /* Disable zoom/scroll on charts */
    .stLineChart, .stBarChart, .stAreaChart {
        pointer-events: none;
    }
    .stLineChart canvas, .stBarChart canvas, .stAreaChart canvas {
        pointer-events: none;
    }
    
    /* Hide Y-axis on charts */
    svg g[aria-roledescription="axis"][aria-label*="y" i],
    svg g[aria-roledescription="axis"][aria-label*="Y"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Header (no subtitle)
walking_k_svg = '''<svg class="walking-k" viewBox="0 0 40 52" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="6" r="5" fill="#E8913A"/>
    <line x1="20" y1="11" x2="20" y2="35" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="18" x2="32" y2="8" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="18" x2="10" y2="24" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="35" x2="32" y2="50" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="35" x2="8" y2="50" stroke="#E8913A" stroke-width="4" stroke-linecap="round"/>
</svg>'''

st.markdown(f'<h1 class="main-header">trac{walking_k_svg}er Dashboard</h1>', unsafe_allow_html=True)

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

# Excluded test users
EXCLUDED_USERS = ["3D8E238E-CADD-4380-9340-DBFE379E8654"]
EXCLUDE_CLAUSE = f"user_id NOT IN ({','.join([repr(u) for u in EXCLUDED_USERS])})"

# Row 1: Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    users = pd.read_sql(f"SELECT COUNT(DISTINCT user_id) as count FROM sensor_readings WHERE {EXCLUDE_CLAUSE}", conn)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-value">{users.iloc[0, 0]:,}</div>
        <div class="metric-label">Total Users</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    passive = pd.read_sql(f"""
        SELECT COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))/60), 0) as total_minutes 
        FROM sensor_readings 
        WHERE chunk_id LIKE 'passive_%' AND {EXCLUDE_CLAUSE}
    """, conn)
    total_mins = int(passive.iloc[0, 0])
    hours = total_mins // 60
    mins = total_mins % 60
    time_display = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">📱</div>
        <div class="metric-value">{time_display}</div>
        <div class="metric-label">Passive Time</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    active = pd.read_sql(f"""
        SELECT COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))/60), 0) as total_minutes 
        FROM sensor_readings 
        WHERE chunk_id LIKE 'active_%' AND {EXCLUDE_CLAUSE}
    """, conn)
    total_mins = int(active.iloc[0, 0])
    hours = total_mins // 60
    mins = total_mins % 60
    time_display = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">🚶</div>
        <div class="metric-value">{time_display}</div>
        <div class="metric-label">Active Time</div>
    </div>
    """, unsafe_allow_html=True)

# Row 2: Top 3 Users
st.markdown('<div class="section-title">Top 3 Users by Recording Time</div>', unsafe_allow_html=True)

top_users = pd.read_sql(f"""
    SELECT user_id, 
           COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))/60), 0) as total_minutes
    FROM sensor_readings
    WHERE {EXCLUDE_CLAUSE}
    GROUP BY user_id
    ORDER BY total_minutes DESC
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
                total_mins = int(user['total_minutes'])
                hours = total_mins // 60
                mins = total_mins % 60
                time_display = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
                st.markdown(f"""
                <div class="podium-card {borders[i]}">
                    <div class="rank-badge">{medals[i]}</div>
                    <div class="user-id">{user_display}</div>
                    <div class="upload-count">{time_display}</div>
                    <div class="upload-label">recorded</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="podium-card {borders[i]}">
                    <div class="rank-badge">{medals[i]}</div>
                    <div class="user-id">—</div>
                    <div class="upload-count">0m</div>
                    <div class="upload-label">recorded</div>
                </div>
                """, unsafe_allow_html=True)
else:
    top_users.index = ["1st", "2nd", "3rd"][:len(top_users)]
    st.dataframe(top_users, use_container_width=True)

# Row 3: Daily Activity Signature (hourly bins)
st.markdown('<div class="section-title">Our Daily Activity Signature</div>', unsafe_allow_html=True)

# Fetch all chunks for hourly distribution
chunks_for_hourly = pd.read_sql(f"""
    SELECT start_time, end_time
    FROM sensor_readings
    WHERE {EXCLUDE_CLAUSE} AND start_time IS NOT NULL AND end_time IS NOT NULL
""", conn)

if not chunks_for_hourly.empty:
    # Initialize 24 hour bins
    hourly_bins = [0.0] * 24
    
    # Calculate proportional minutes for each chunk
    for _, row in chunks_for_hourly.iterrows():
        start = row['start_time']
        end = row['end_time']
        
        if pd.isna(start) or pd.isna(end) or end <= start:
            continue
        
        # Iterate through each hour the chunk touches
        current = start.replace(minute=0, second=0, microsecond=0)
        while current < end:
            hour = current.hour
            bin_start = current
            bin_end = current + pd.Timedelta(hours=1)
            
            # Calculate overlap
            overlap_start = max(start, bin_start)
            overlap_end = min(end, bin_end)
            
            if overlap_end > overlap_start:
                overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                hourly_bins[hour] += overlap_minutes
            
            current = bin_end
    
    # Create DataFrame for chart - only 6am to 11pm (hours 6-23)
    hour_labels = ['6am', '7am', '8am', '9am', '10am', '11am', '12pm', 
                   '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', 
                   '8pm', '9pm', '10pm', '11pm']
    filtered_bins = hourly_bins[6:24]  # Hours 6-23
    
    hourly_df = pd.DataFrame({
        'Minutes': filtered_bins
    }, index=hour_labels)
    
    # Display bar chart
    st.bar_chart(hourly_df, color="#E8913A", height=280, use_container_width=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-title">No data available</div>
        <div class="empty-desc">Start collecting sensor data to see daily patterns</div>
    </div>
    """, unsafe_allow_html=True)

# Row 4: Recording time over time
st.markdown('<div class="section-title">Recording Time Over Time</div>', unsafe_allow_html=True)

timeline = pd.read_sql(f"""
    SELECT DATE(start_time) as date,
           COALESCE(SUM(CASE WHEN chunk_id LIKE 'active_%' THEN EXTRACT(EPOCH FROM (end_time - start_time))/60 ELSE 0 END), 0) as active,
           COALESCE(SUM(CASE WHEN chunk_id LIKE 'passive_%' THEN EXTRACT(EPOCH FROM (end_time - start_time))/60 ELSE 0 END), 0) as passive
    FROM sensor_readings
    WHERE start_time > NOW() - INTERVAL '30 days' AND {EXCLUDE_CLAUSE}
    GROUP BY date ORDER BY date
""", conn)

if not timeline.empty:
    chart_data = timeline.set_index('date')[['active', 'passive']]
    st.line_chart(chart_data, color=["#E8913A", "#3d4f5f"], height=280)
    
    # Stats row
    stat_cols = st.columns(4)
    total_mins = int(timeline['active'].sum() + timeline['passive'].sum())
    total_hours = total_mins // 60
    total_remaining_mins = total_mins % 60
    total_display = f"{total_hours}h {total_remaining_mins}m" if total_hours > 0 else f"{total_mins}m"
    
    avg_daily_mins = total_mins / max(len(timeline), 1)
    avg_hours = int(avg_daily_mins) // 60
    avg_mins = int(avg_daily_mins) % 60
    avg_display = f"{avg_hours}h {avg_mins}m" if avg_hours > 0 else f"{int(avg_daily_mins)}m"
    
    with stat_cols[0]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total (30d)</div>
            <div class="stat-value">{total_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_cols[1]:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Daily Avg</div>
            <div class="stat-value">{avg_display}</div>
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

user_ids = pd.read_sql(f"SELECT DISTINCT user_id FROM sensor_readings WHERE {EXCLUDE_CLAUSE}", conn)
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
                COALESCE(SUM(EXTRACT(EPOCH FROM (end_time - start_time))/60), 0) as total_minutes,
                COALESCE(SUM(CASE WHEN chunk_id LIKE 'active_%%' THEN EXTRACT(EPOCH FROM (end_time - start_time))/60 ELSE 0 END), 0) as active_minutes,
                COALESCE(SUM(CASE WHEN chunk_id LIKE 'passive_%%' THEN EXTRACT(EPOCH FROM (end_time - start_time))/60 ELSE 0 END), 0) as passive_minutes,
                MIN(start_time) as first_upload,
                MAX(start_time) as last_upload
            FROM sensor_readings 
            WHERE user_id = %s
        """, (selected_user,))
        stats_row = cursor.fetchone()
        cursor.close()
        
        # Format durations
        def format_duration(mins):
            mins = int(mins)
            hours = mins // 60
            remaining = mins % 60
            return f"{hours}h {remaining}m" if hours > 0 else f"{mins}m"
        
        user_stat_cols = st.columns(4)
        with user_stat_cols[0]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">Total Time</div>
                <div class="stat-value">{format_duration(stats_row[0])}</div>
            </div>
            """, unsafe_allow_html=True)
        with user_stat_cols[1]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">🚶 Active</div>
                <div class="stat-value accent-orange">{format_duration(stats_row[1])}</div>
            </div>
            """, unsafe_allow_html=True)
        with user_stat_cols[2]:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-label">📱 Passive</div>
                <div class="stat-value accent-slate">{format_duration(stats_row[2])}</div>
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
            
            st.dataframe(display_df, use_container_width=True, height=300, hide_index=True)
else:
    st.info("No users found in the database yet.")

# Footer
walking_k_footer = '''<svg style="display:inline-block;width:12px;height:16px;vertical-align:middle;margin:0 -1px;" viewBox="0 0 40 52" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="6" r="5" fill="#9ca3af"/>
    <line x1="20" y1="11" x2="20" y2="35" stroke="#9ca3af" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="18" x2="32" y2="8" stroke="#9ca3af" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="18" x2="10" y2="24" stroke="#9ca3af" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="35" x2="32" y2="50" stroke="#9ca3af" stroke-width="4" stroke-linecap="round"/>
    <line x1="20" y1="35" x2="8" y2="50" stroke="#9ca3af" stroke-width="4" stroke-linecap="round"/>
</svg>'''

st.markdown(f"""
<div style="text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 2rem 0 1rem 0;">
    trac{walking_k_footer}er Dashboard • {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)
