# --- Importaciones necesarias ---
import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from test_table;', ttl=1000)

for row in df.itertuples():
    st.write(f"{row.id} has a :{row.numero_usuario}:")
    st.write(f"{type(df)}:")