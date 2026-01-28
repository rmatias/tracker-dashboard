import streamlit as st                                                                                                                                                            
import psycopg2                                                                                                                                                                   
import pandas as pd                                                                                                                                                               
                                                                                                                                                                                  
st.set_page_config(page_title="tracKer Dashboard", layout="wide")                                                                                                                 
st.title("📊 tracKer Dashboard")                                                                                                                                                  
                                                                                                                                                                                  
@st.cache_resource                                                                                                                                                                
def get_connection():                                                                                                                                                             
    return psycopg2.connect(st.secrets["DATABASE_URL"])                                                                                                                           
                                                                                                                                                                                  
conn = get_connection()                                                                                                                                                           
                                                                                                                                                                                  
# Row 1: Key Metrics                                                                                                                                                              
col1, col2, col3 = st.columns(3)                                                                                                                                                  
                                                                                                                                                                                  
with col1:                                                                                                                                                                        
    users = pd.read_sql("SELECT COUNT(DISTINCT user_id) as count FROM chunks", conn)                                                                                              
    st.metric("Total Users", users.iloc[0, 0])                                                                                                                                    
                                                                                                                                                                                  
with col2:                                                                                                                                                                        
    passive = pd.read_sql("SELECT COUNT(*) as count FROM chunks WHERE is_active = false", conn)                                                                                   
    st.metric("Passive Chunks", passive.iloc[0, 0])                                                                                                                               
                                                                                                                                                                                  
with col3:                                                                                                                                                                        
    active = pd.read_sql("SELECT COUNT(*) as count FROM chunks WHERE is_active = true", conn)                                                                                     
    st.metric("Active Chunks", active.iloc[0, 0])                                                                                                                                 
                                                                                                                                                                                  
# Row 2: Latest uploads                                                                                                                                                           
st.subheader("Latest Upload per User")                                                                                                                                            
latest = pd.read_sql("""                                                                                                                                                          
    SELECT user_id, MAX(created_at) as latest_upload                                                                                                                              
    FROM chunks GROUP BY user_id ORDER BY latest_upload DESC                                                                                                                      
""", conn)                                                                                                                                                                        
st.dataframe(latest, use_container_width=True)                                                                                                                                    
                                                                                                                                                                                  
# Row 3: Chunks over time                                                                                                                                                         
st.subheader("Chunks Uploaded Over Time")                                                                                                                                         
timeline = pd.read_sql("""                                                                                                                                                        
    SELECT DATE(created_at) as date,                                                                                                                                              
           SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,                                                                                                                  
           SUM(CASE WHEN NOT is_active THEN 1 ELSE 0 END) as passive                                                                                                              
    FROM chunks                                                                                                                                                                   
    WHERE created_at > NOW() - INTERVAL '30 days'                                                                                                                                 
    GROUP BY date ORDER BY date                                                                                                                                                   
""", conn)                                                                                                                                                                        
st.line_chart(timeline.set_index('date'))                                                                                                                                         
                                                                                                                                                                                  
# Row 4: Filter by user                                                                                                                                                           
st.subheader("Filter by User")                                                                                                                                                    
user_ids = pd.read_sql("SELECT DISTINCT user_id FROM chunks", conn)                                                                                                               
selected_user = st.selectbox("Select User", user_ids['user_id'].tolist())                                                                                                         
                                                                                                                                                                                  
if selected_user:                                                                                                                                                                 
    user_chunks = pd.read_sql(f"""                                                                                                                                                
        SELECT created_at, is_active, duration_seconds                                                                                                                            
        FROM chunks WHERE user_id = %s                                                                                                                                            
        ORDER BY created_at DESC LIMIT 50                                                                                                                                         
    """, conn, params=(selected_user,))                                                                                                                                           
    st.dataframe(user_chunks, use_container_width=True)                                                                                                                           
                                                          
