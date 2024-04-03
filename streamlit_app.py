import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network
from rapidfuzz import process, fuzz
import folium
from streamlit_folium import folium_static

# Load restaurant data
restaurant_data = pd.read_parquet('restaurants.parquet')
restaurant_list = restaurant_data["meta_name"].drop_duplicates()

not_found_message = "No restaurant of that name found, please try entering the name again."

def fuzzy_search(user_input, choices, message, threshold=70):
    fuzzy_match = process.extractOne(user_input, choices, scorer=fuzz.WRatio)
    if fuzzy_match and fuzzy_match[1] > threshold:
        return fuzzy_match[0]
    else:
        return message

st.write("# Welcome to Vegellan!")

user_input = st.text_input("Enter the name of the restaurant you would like to look for:")

plot_data = restaurant_data[['meta_name', 'meta_latitude', 'meta_longitude']].copy()

# Initial map settings
initial_location = [41.71, -74.0060]
initial_zoom = 6

if user_input:
    restaurant = fuzzy_search(user_input, restaurant_list, not_found_message)
    if restaurant != not_found_message:
        st.write("Restaurant selected:", restaurant)
        selected_restaurant = plot_data[plot_data['meta_name'] == restaurant]
        if not selected_restaurant.empty:
            selected_lat = selected_restaurant.iloc[0]['meta_latitude']
            selected_lon = selected_restaurant.iloc[0]['meta_longitude']

            initial_location = [selected_lat, selected_lon]
            initial_zoom = 15

m = folium.Map(
    location=initial_location,
    zoom_start=initial_zoom,
    tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap contributors, © CARTO'
    )


for idx, row in plot_data.iterrows():
    folium.Marker(
        location=[row['meta_latitude'], row['meta_longitude']],
        popup=row['meta_name'],
        icon=folium.Icon(color='cadetBlue', icon='cutlery')
    ).add_to(m)


folium_static(m)

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
