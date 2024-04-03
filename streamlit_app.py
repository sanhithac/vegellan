import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
from rapidfuzz import process, fuzz
import pydeck as pdk

# Replace this dataframe with a call to the actual database
restaurant_data = pd.read_parquet('restaurants.parquet')
restaurant_list = restaurant_data["meta_name"].drop_duplicates()

not_found_message = "No restaurant of that name found, please try entering the name again."

def fuzzy_search(user_input, choices, message, threshold=70):
    """
    Search for the best match for the user input in the list of choices using fuzzy matching.
    If the match score is below the threshold, return the message.
    """
    fuzzy_match = process.extractOne(user_input, choices, scorer=fuzz.WRatio)
    if fuzzy_match and fuzzy_match[1] > threshold:
        return fuzzy_match[0]
    else:
        return message

st.write("""
# Welcome to Vegellan!
""")

user_input = st.text_input("Enter the name of the restaurant you would like to look for:")

plot_data = restaurant_data[['meta_name', 'meta_latitude', 'meta_longitude']].copy()

# Initial view state that hovers over New York
initial_zoom = 7
initial_lat = 41.21
initial_lon = -74.00
initial_radius = 1000

view_state = pdk.ViewState(
    latitude=initial_lat,
    longitude=initial_lon,
    zoom=initial_zoom,
    bearing=0,
    pitch=0
)

if user_input:
    restaurant = fuzzy_search(user_input, restaurant_list, not_found_message)
    if restaurant == not_found_message:
        st.write(restaurant)
    else:
        st.write("Restaurant selected:", restaurant)
        
        selected_restaurant = plot_data[plot_data['meta_name'] == restaurant]
        if not selected_restaurant.empty:
            selected_lat = selected_restaurant.iloc[0]['meta_latitude']
            selected_lon = selected_restaurant.iloc[0]['meta_longitude']
            
            view_state.latitude = selected_lat
            view_state.longitude = selected_lon
            view_state.zoom = 14
            zoomed_radius = 50

layer = pdk.Layer(
    'ScatterplotLayer',
    data=plot_data,
    get_position=['meta_longitude', 'meta_latitude'],
    get_radius=initial_radius if view_state.zoom == initial_zoom else zoomed_radius,
    get_fill_color=[255, 50, 0],
    pickable=True
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{meta_name}"}
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
