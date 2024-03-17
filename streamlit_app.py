import streamlit as st
import pandas as pd
 
st.write("""
# Welcome to Vegellan!
""")

option = st.selectbox(
    'Where are you located?',
    ('New York', 'California', 'Texas'))

st.write('You selected:', option)
