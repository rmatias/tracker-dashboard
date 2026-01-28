import streamlit as st                                                                                                                                                            
import psycopg2                                                                                                                                                                   
import pandas as pd                                                                                                                                                               
                                                                                                                                                                                  
st.set_page_config(page_title="tracKer Dashboard", layout="wide")                                                                                                                 
st.title("tracKer Dashboard")                                                                                                                                                     
                                                                                                                                                                                  
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
    st.metric("Total Users", users.iloc[0, 0])                                                                                                                                    
                                                                                                                                                                                  
with col2:                                                                                                                                                                        
    passive = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'passive_%'", conn)                                                                  
    st.metric("Passive Chunks", passive.iloc[0, 0])                                                                                                                               
                                                                                                                                                                                  
with col3:                                                                                                                                                                        
    active = pd.read_sql("SELECT COUNT(*) as count FROM sensor_readings WHERE chunk_id LIKE 'active_%'", conn)                                                                    
    st.metric("Active Chunks", active.iloc[0, 0])                                                                                                                                 
                                                                                                                                                                                  
# Row 2: Top 3 Users                                                                                                                                                              
st.subheader("Top 3 Users by Uploads")                                                                                                                                            
top_users = pd.read_sql("""                                                                                                                                                       
    SELECT user_id, COUNT(*) as total_uploads                                                                                                                                     
    FROM sensor_readings                                                                                                                                                          
    GROUP BY user_id                                                                                                                                                              
    ORDER BY total_uploads DESC                                                                                                                                                   
    LIMIT 3                                                                                                                                                                       
""", conn)                                                                                                                                                                        
top_users.index = ["1st", "2nd", "3rd"][:len(top_users)]                                                                                                                          
st.dataframe(top_users, use_container_width=True)                                                                                                                                 
                                                                                                                                                                                  
# Row 3: Chunks over time                                                                                                                                                         
st.subheader("Chunks Uploaded Over Time")                                                                                                                                         
timeline = pd.read_sql("""                                                                                                                                                        
    SELECT DATE(start_time) as date,                                                                                                                                              
           SUM(CASE WHEN chunk_id LIKE 'active_%' THEN 1 ELSE 0 END) as active,                                                                                                   
           SUM(CASE WHEN chunk_id LIKE 'passive_%' THEN 1 ELSE 0 END) as passive                                                                                                  
    FROM sensor_readings                                                                                                                                                          
    WHERE start_time > NOW() - INTERVAL '30 days'                                                                                                                                 
    GROUP BY date ORDER BY date                                                                                                                                                   
""", conn)                                                                                                                                                                        
if not timeline.empty:                                                                                                                                                            
    st.line_chart(timeline.set_index('date'))                                                                                                                                     
else:                                                                                                                                                                             
    st.info("No data in the last 30 days")                                                                                                                                        
                                                                                                                                                                                  
# Row 4: Filter by user                                                                                                                                                           
st.subheader("Filter by User")                                                                                                                                                    
user_ids = pd.read_sql("SELECT DISTINCT user_id FROM sensor_readings", conn)                                                                                                      
selected_user = st.selectbox("Select User", user_ids['user_id'].tolist())                                                                                                         
                                                                                                                                                                                  
if selected_user:                                                                                                                                                                 
    user_chunks = pd.read_sql("""                                                                                                                                                 
        SELECT start_time, end_time, chunk_id                                                                                                                                     
        FROM sensor_readings WHERE user_id = %s                                                                                                                                   
        ORDER BY start_time DESC LIMIT 50                                                                                                                                         
    """, conn, params=(selected_user,))                                                                                                                                           
    st.dataframe(user_chunks, use_container_width=True)
