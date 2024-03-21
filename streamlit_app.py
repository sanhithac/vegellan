import streamlit as st
import pandas as pd
import numpy as np
 
st.write("""
# Welcome to Vegellan!
""")

option = st.selectbox(
    'Where are you located?',
    ('New York', 'California', 'Texas'))

st.write('You selected:', option)

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(df)

#the following will all be "on-click" after user clicks on a datapoint
st.write("General User Sentiment:")

st.write("Similar Restaurants:")
#Graph

st.write("Customer Rating Distribution:")
#Histogram
