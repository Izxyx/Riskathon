# --- Importaciones necesarias ---
import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from test_table;', ttl=600)

for row in df.itertuples():
    st.write(f"{row.id} has a :{row.numero_registro}:")

print(df)