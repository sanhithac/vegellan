import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
from rapidfuzz import process, fuzz
import pydeck as pdk

# Replace this dataframe with the real data from our database
restaurant_data = pd.DataFrame({
    'name': ["Chipotle Mexican Grill", "McDonald's", "Starbucks", "Subway", "Taco Bell", "Wendy's"],
    'lat': [40.71, 40.72, 40.73, 40.74, 40.75, 40.76],
    'lon': [-74.00, -74.01, -74.02, -74.03, -74.04, -74.05]
})
not_found_message = "No restaurant of that name found, please try entering the name again."

def fuzzy_search(user_input, choices, message, threshold=70):
    """
    Search for the best match for the user input in the list of choices using fuzzy matching.
    If the match score is below the threshold, return the message.
    """
    # WW ratio is a weighted ratio of the two strings, might need to switch to QRatio
    # if performance is a concern
    fuzzy_match = process.extractOne(user_input, choices, scorer=fuzz.WRatio)
    if fuzzy_match and fuzzy_match[1] > threshold:
        return fuzzy_match[0]
    else:
        return message

st.write("""
# Welcome to Vegellan!
""")

user_input = st.text_input("Enter the name of the restaurant you would like to look for:")

if user_input:
    restaurant = fuzzy_search(user_input, restaurant_data['name'].to_list(), not_found_message)
    if restaurant == not_found_message:
        st.write(restaurant)
    else:
        st.write("Restaurant selected:", restaurant)

layer = pdk.Layer(
    'ScatterplotLayer',
    data=restaurant_data,
    get_position='[lon, lat]',
    get_radius=100,
    get_fill_color=[255, 140, 0],
    pickable=True
)

view_state = pdk.ViewState(
    latitude=40.71,
    longitude=-74.00,
    zoom=11,
    bearing=0,
    pitch=0
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"}
)

st.pydeck_chart(r)

# df = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [40.71, -74.0],
#     columns=['lat', 'lon'])

# st.map(df)

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
