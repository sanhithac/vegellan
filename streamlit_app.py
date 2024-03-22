import streamlit as st
import pandas as pd
import numpy as np
# import networkx as nx
# from pyvis.network import Network
 
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
#graph = nx.from_pandas_edgelist(edge_list, 'restaurant', 'similar_restaurant', True)
# # Initiate PyVis network object
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
histogram = pd.DataFrame([1,2,3], columns=["a", "b", "c"])

st.bar_chart(histogram)
