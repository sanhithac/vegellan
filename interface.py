
# Native libraries
import random
import streamlit as st
import pandas as pd
import numpy as np

# Imaging Libraries
from PIL import Image
from matplotlib import pyplot as plt
from rapidfuzz import process, fuzz

# Folium Libraries
import folium
from folium.plugins import HeatMap

# Streamlit 3rd Party Components
from streamlit_folium import st_folium
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_searchbox import st_searchbox

# Local Modules
from components import (
    generate_interactive_map,
    generate_restaurant_infopane,
    generate_sentiments_metric,
    generate_reviews_distribution,
    generate_node_graph,
)

# Local Modules
from data_api import (
    # api_authenticate,
    # get_list_of_states,
    get_list_of_restaurants,
    # search_restaurant,
    reviews_histogram,
    get_restaurant_edges,
    get_sentiment,
)

def produce_main_interface():
    
    # Proceed with listing of restaurants
    state_selected = st.session_state['state_selected']
    state_selected_beautified = " ".join(state_selected.split("_"))

    # Generate List of Restaurants
    restaurant_list_request = get_list_of_restaurants(
        state_selected,
        sampling_factor=1.0,
        vegan_only=True,
        non_vegan_only=False,
        headers=st.session_state["api_call_headers"],
    )

    if st.session_state['show_all_restaurants']:

        non_vegan_list_request = get_list_of_restaurants(
            state_selected,
            sampling_factor=1.0 if 'sampling_factor' not in st.session_state else st.session_state['sampling_factor'],
            vegan_only=False,
            non_vegan_only=True,
            headers=st.session_state["api_call_headers"],
        )

        list_of_state_restaurants = pd.concat(
            [
                pd.DataFrame(restaurant_list_request["body"]),
                pd.DataFrame(non_vegan_list_request["body"]),
            ],
            axis=0,
        )

    else:

        list_of_state_restaurants = pd.DataFrame(restaurant_list_request['body'])

    st.subheader(f"{len(restaurant_list_request['body'])} vegan-friendly restaurants in {state_selected_beautified} identified!", divider="green")

    # pass search function to searchbox
    # user_text_input = st.text_input(
    #     "Enter the name of the restaurant you would like to look for:",

    # )

    main_col1, main_col2 = st.columns([0.7,0.3])

    ###### Interactive Map
    generate_interactive_map(main_col1, list_of_state_restaurants)

    if st.session_state["last_object_clicked_popup"] is None:
        main_col2.subheader("👈 Select a restaurant pin on the map.", divider="green")
        main_col2.markdown("You might need to disable the Heatmap mode to display pins.")

    elif st.session_state["last_object_clicked_popup"] is not None:

        ###### Restaurant Infopane
        st.session_state['resto_info'] = (
            list_of_state_restaurants
            [
                (list_of_state_restaurants.longitude.astype('float') == st.session_state['last_object_clicked']['lng'])
                & (list_of_state_restaurants.latitude.astype('float') == st.session_state['last_object_clicked']['lat'])
            ]
        )

        if len(st.session_state['resto_info']) != 1:
            st.session_state['resto_info'] = st.session_state['resto_info'].sample(1).to_dict(orient="records")[0]
        else:
            st.session_state['resto_info'] = st.session_state['resto_info'].to_dict(orient="records")[0]

        col1, col2, col3 = generate_restaurant_infopane(main_col2)

        b_col1, b_col2 = main_col2.columns([0.3, 0.7])

        ###### Sentiments Metric
        sentiments_data = get_sentiment(
            st.session_state['resto_info']['gmap_id'],
            st.session_state['state_selected'],
            headers=st.session_state["api_call_headers"]
        )['body']

        generate_sentiments_metric(sentiments_data, b_col1)

        ###### Reviews Histogram
        reviews_histogram_data = reviews_histogram(
            st.session_state['resto_info']['gmap_id'],
            st.session_state['state_selected'],
            headers=st.session_state["api_call_headers"]
        )['body']

        generate_reviews_distribution(reviews_histogram_data, b_col2)

        ###### Graph Node Visual
        generate_node_graph(get_restaurant_edges)

