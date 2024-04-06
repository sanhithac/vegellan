import random
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from rapidfuzz import process, fuzz
import folium
from streamlit_folium import st_folium
from streamlit_agraph import agraph, Node, Edge, Config

# Load restaurant data
restaurant_data = pd.read_parquet('restaurants.parquet')
restaurant_list = restaurant_data["meta_name"].str.lower().drop_duplicates()

not_found_message = "No restaurant of that name found, please try entering the name again."

def fuzzy_search(user_input, choices, message, threshold=70):
    user_input_lower = user_input.lower()
    fuzzy_match = process.extractOne(user_input_lower, choices, scorer=fuzz.WRatio)
    if fuzzy_match and fuzzy_match[1] > threshold:
        return fuzzy_match[0]
    else:
        return message

st.write("# Welcome to Vegellan!")

user_text_input = st.text_input("Enter the name of the restaurant you would like to look for:")

plot_data = restaurant_data[['meta_name', 'meta_latitude', 'meta_longitude', 'sentiment_label', 'meta_address']].copy()

#sentiment aggregation
plot_data['sentiment_label'] = np.where(plot_data['sentiment_label'] == 'POSITIVE', 1, plot_data['sentiment_label'])
plot_data['sentiment_label'] = np.where(plot_data['sentiment_label'] == 'NEGATIVE', 0, plot_data['sentiment_label'])

grouped = plot_data.groupby(['meta_name', 'meta_address'])
sentiment_data = grouped.mean().reset_index()

#ratings aggregation
ratings_data = restaurant_data[['meta_name', 'meta_address', 'rating']].copy()
ratings_grouped = ratings_data.groupby(['meta_name', 'meta_address'])
avg_ratings = ratings_grouped.mean().reset_index()

# Initial map settings
initial_location = plot_data[['meta_latitude', 'meta_longitude']].mean()
initial_zoom = 7
selected_restaurant_name = None

if user_text_input:
    restaurant = fuzzy_search(user_text_input, restaurant_list, not_found_message)
    if restaurant != not_found_message:
        selected_restaurant = plot_data[plot_data['meta_name'].str.lower() == restaurant]
        if not selected_restaurant.empty:
            selected_restaurant_name = selected_restaurant.iloc[0]['meta_name']
            selected_lat = selected_restaurant.iloc[0]['meta_latitude']
            selected_lon = selected_restaurant.iloc[0]['meta_longitude']

            initial_location = [selected_lat, selected_lon]
            initial_zoom = 15
    else:
        st.write(not_found_message)

#Map with markers
m = folium.Map(
    location=initial_location,
    zoom_start=initial_zoom,
    )

for idx, row in plot_data.iterrows():
    folium.Marker(
        location=[row['meta_latitude'], row['meta_longitude']],
        popup=row['meta_name'],
        tooltip=row['meta_name'],
        icon=folium.Icon(color='red', icon='cutlery')
    ).add_to(m)

result = st_folium(m, width=725)

if result['last_object_clicked_popup'] is not None:
    selected_restaurant_name = result['last_object_clicked_popup']

#on search/click of map marker
if selected_restaurant_name is not None:
    st.write("You selected the restaurant: ", selected_restaurant_name)

    sentiment_value = sentiment_data.loc[sentiment_data['meta_name'] == selected_restaurant_name, 'sentiment_label']
    if (sentiment_value > .5).bool():
        sentiment = 'Positive'
    else:
        sentiment = 'Negative'
    st.write("General User Sentiment: ", sentiment)

    address = sentiment_data.loc[sentiment_data['meta_name'] == selected_restaurant_name, 'meta_address']
    st.write("Address: ", address.values[0])

    rating = avg_ratings.loc[avg_ratings['meta_name'] == selected_restaurant_name, 'rating']
    st.write("Average Rating: ", rating.values[0])

    #Histogram of ratings
    ratings_rest = ratings_data.loc[ratings_data['meta_name'] == selected_restaurant_name]
    arr = ratings_rest['rating']
    # commutes.plot.hist(grid=True, bins=20, rwidth=0.9,
    #                    color='#607c8e')
    plt.title('Rating Distribution')
    plt.xlabel('Ratings')
    plt.ylabel('Num Ratings')
    # plt.grid(axis='y', alpha=0.75)
    # plt.rcParams['figure.figsize'] = [2, 3]
    fig, ax = plt.subplots(figsize=(4,3))
    ax.hist(arr, bins=5, range=[1,5], histtype='bar', align='right')
    fig.savefig("histogram.png")
    image = Image.open('histogram.png')
    st.image(image, width=300)
    #without streamlit
    # size, scale = 1000, 10
    # ratings_rest = ratings_data.loc[ratings_data['meta_name'] == selected_restaurant_name]
    # commutes = ratings_rest['rating']
    #
    # commutes.plot.hist(grid=True, bins=20, rwidth=0.9,
    #                    color='#607c8e')
    # plt.title('Rating Distribution')
    # plt.xlabel('Ratings')
    # plt.ylabel('Num Ratings')
    # plt.grid(axis='y', alpha=0.75)

#dummy data for graph:
source = []  # empty list
target = []  # different empty list
node_list = restaurant_list

for i in node_list:
    for j in node_list:
        if i < j:
            source.append(i)
            target.append(j)

loop_data = pd.DataFrame({'source': source, 'target': target})

st.write("Similar Restaurants:")

#agraph
if selected_restaurant_name is not None:
    edge_data_similar = (loop_data.loc[(loop_data['source']==selected_restaurant_name.lower()) | (loop_data['target']==selected_restaurant_name.lower())])

    nodes = []
    edges = []

    source = selected_restaurant_name.lower()
    target = pd.concat([edge_data_similar['source'], edge_data_similar['target']])
    nodes_all = target.drop_duplicates()

    node_data = list(set(nodes_all))
    nodes.append( Node(id=source,
                       size=15,
                       label=source,
                       color="red",
                       shape="dot",)
                )
    for i in range(0, len(node_data)):
        if(node_data[i]!=source):
            nodes.append( Node(id=node_data[i],
                           size=5,
                           label=node_data[i],
                           title = (random.uniform(0, 1)),
                           color="green",
                           shape="dot",)
                    ) # includes **kwargs
            edges.append( Edge(source=source,
                           color="black",
                           target=node_data[i],
                           # **kwargs
                           )
                    )

    config = Config(width=750,
                    height=950,
                    directed=False,
                    physics=True,
                    hierarchical=True,
                    # **kwargs
                    )

    return_value = agraph(nodes=nodes,
                          edges=edges,
                          config=config)


