import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
from st_keyup import st_keyup
 
st.write("""
# Welcome to Vegellan!
""")

# option = st.selectbox(
#     'Where are you located?',
#     ('New York', 'California', 'Texas'))

# st.write('You selected:', option)

restaurant_value = st_keyup("Please enter the name of the restaurant you would like to search for:")

#Temp values until we get the actual data
options = ['Restaurant 1', 'Restaurant 2', 'Restaurant 3', 'Restaurant 4', 'Restaurant 5']

filtered_options = [option for option in options if restaurant_value.lower() in option.lower()] if len(restaurant_value) >= 3 else []

if filtered_options:
    selected_option = st.selectbox("Select an option:", filtered_options)
    st.write(f"You selected: {selected_option}")
else:
    if len(restaurant_value) > 0:
        st.write("Please type more characters to see options...")

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [40.71, -74.0],
    columns=['lat', 'lon'])

st.map(df)

#the following will all be "on-click" after user clicks on a datapoint
st.write("General User Sentiment:")

st.write("Similar Restaurants:")
#Graph
# graph = nx.from_pandas_edgelist(edge_list, 'restaurant', 'similar_restaurant', True)
# Initiate PyVis network object
# net = Network(
#                    height='400px',
#                    width='100%',
#                    bgcolor='#222222',
#                    font_color='white'
#                   )

# # Take Networkx graph and translate it to a PyVis graph format
# net.from_nx(G)

# # Generate network with specific layout settings
# net.repulsion(
#                     node_distance=420,
#                     central_gravity=0.33,
#                     spring_length=110,
#                     spring_strength=0.10,
#                     damping=0.95
#                    )

st.write("Customer Rating Distribution:")
#Histogram
arr = np.random.normal(1, 1, size=100)
fig, ax = plt.subplots()
ax.hist(arr, bins=20)

st.pyplot(fig)
