
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
from data_api import (
    # api_authenticate,
    # get_list_of_states,
    get_list_of_restaurants,
    # search_restaurant,
    reviews_histogram,
    get_restaurant_edges,
    get_sentiment,
)

def produce_main_interface(api_call_headers):
    # Proceed with listing of restaurants
    state_selected = st.session_state['state_selected']
    state_selected_beautified = " ".join(state_selected.split("_"))

    restaurant_list_request = get_list_of_restaurants(state_selected, 1.0, headers=api_call_headers)

    list_of_state_restaurants = pd.DataFrame(restaurant_list_request['body'])

    st.subheader(f"{len(list_of_state_restaurants)} vegan-friendly restaurants in {state_selected_beautified} identified!", divider="green")

    # pass search function to searchbox
    # user_text_input = st.text_input(
    #     "Enter the name of the restaurant you would like to look for:",
    # )

    main_col1, main_col2 = st.columns([0.7,0.3])

    st.session_state['toggle_heatmap'] = main_col1.toggle("Toggle Heatmap", value=True)

    # Initialize center and zoom level
    # st.session_state['map_center'] = list_of_state_restaurants[['latitude', 'longitude']].mean() if st.session_state.get('map_center') is None else st.session_state.get('map_center')
    # st.session_state['map_zoom_level'] = 7 if st.session_state.get('map_zoom_level') is None else st.session_state.get('map_zoom_level')

    # Map with markers
    m = folium.Map(
        location=list_of_state_restaurants[['latitude', 'longitude']].mean(),
        zoom_start=7,
    )

    fg = folium.FeatureGroup(name="Markers")

    if st.session_state['toggle_heatmap']:
        fg.add_child(
            HeatMap(list_of_state_restaurants[['latitude', 'longitude']].values.tolist())
        )
    else:

        if st.session_state['map_zoom_level'] < 10:
            main_col1.error("WARNING: Toggling off heatmap mode can only be done if you zoom enough.", icon="⚠️")
            st.session_state['toggle_heatmap'] = True
        else:

            if st.session_state.get('map_lat_bounds') is not None:
                filtered_restaurants = list_of_state_restaurants[
                    (
                        (list_of_state_restaurants.latitude.astype(float) >= st.session_state['map_lat_bounds'][0])
                        & (list_of_state_restaurants.latitude.astype(float) <= st.session_state['map_lat_bounds'][1])
                    ) & (
                        (list_of_state_restaurants.longitude.astype(float) >= st.session_state['map_long_bounds'][0])
                        & (list_of_state_restaurants.longitude.astype(float) <= st.session_state['map_long_bounds'][1])
                    )
                ].copy()

            else:
                filtered_restaurants = list_of_state_restaurants

            for idx, row in filtered_restaurants.iterrows():
                
                pin_color = 'green'
        
                fg.add_child(
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=row['name'],
                        tooltip=row['name'],
                        icon=folium.Icon(color=pin_color, icon='cutlery')
                    )
                )


    with main_col1:
        if st.session_state['toggle_heatmap']:
            st.info("Heatmap shows the density of vegan restaurants around the area. Red means more concentration in the area.", icon="💡")
        else:
            st.info("Click on a map pin to show its information and similarity graph.", icon="💡")
        result = st_folium(
            m,
            width=1_000,
            height=5_00,
            # zoom=st.session_state['map_zoom_level'],
            # center=st.session_state['map_center'],
            feature_group_to_add=fg,
        )

        st.session_state['map_zoom_level'] = result["zoom"]
        st.session_state['map_center'] = [result["center"]['lat'], result["center"]['lng']]
        
        # Save state of map bounds
        st.session_state['map_lat_bounds'] = [
            result["bounds"]["_southWest"]["lat"],
            result["bounds"]["_northEast"]["lat"],
        ]

        st.session_state['map_long_bounds'] = [
            result["bounds"]["_southWest"]["lng"],
            result["bounds"]["_northEast"]["lng"],
        ]    

    if result['last_object_clicked_popup'] is None:
        main_col2.subheader("👈 Select a restaurant pin on the map.", divider="green")
        main_col2.markdown("You might need to disable the Heatmap mode to display pins.")

    elif result['last_object_clicked_popup'] is not None:

        # Show Selected Restaurants
        main_col2.subheader(result['last_object_clicked_popup'], divider="green")

        resto_info = (
            list_of_state_restaurants
            [
                (list_of_state_restaurants.longitude.astype('float') == result['last_object_clicked']['lng'])
                & (list_of_state_restaurants.latitude.astype('float') == result['last_object_clicked']['lat'])
            ]
        )

        if len(resto_info) != 1:
            resto_info = resto_info.sample(1)

        resto_info = resto_info.to_dict(orient="records")[0]

        desc_str = (
            resto_info['description']
            if resto_info['description'] is not None
            or resto_info['description'] != 'None'
            or resto_info['description'] != np.nan
            else "No description available."
        )

        main_col2.markdown(f"**DESCRIPTION**: {desc_str}")

        main_col2.markdown(f"**ADDRESS**: {resto_info['address']}")

        main_col2.caption("TAGS: " + ", ".join(resto_info['category'].split(",")))
        main_col2.caption("GMAP_ID: " + resto_info['gmap_id'])

        col1, col2, col3 = main_col2.columns(3)

        col1.metric("Avg. Rating", f"{resto_info['avg_rating']}")
        col2.metric("Reviews", f"{resto_info['num_of_reviews']}")

        priciness_value = (
            'N/A' if resto_info['price'] == 'None' or resto_info['price'] is None
            else "💲" * len(resto_info['price'])
        )

        col3.metric("Priciness", priciness_value)

        sentiment_data = pd.DataFrame(get_sentiment(resto_info['gmap_id'], state_selected, headers=api_call_headers)['body'])

        # col1.dataframe(sentiment_data)
        if 'sentiment_count' not in sentiment_data.columns:
            col1.metric("Positive Reviews", f"N/A")
        else:
            sentiment_data['sentiment_ratio'] = sentiment_data['sentiment_count'] / sentiment_data['sentiment_count'].sum()

            sentiment_data = sentiment_data[sentiment_data['sentiment_label'] == 'POSITIVE']['sentiment_ratio'].values[0]
            
            if sentiment_data <= 0.6:
                sentiment_icon = "🔴"
            elif sentiment_data <= 0.8:
                sentiment_icon = "🟡"
            else:
                sentiment_icon = "🟢"     

            col1.metric(f"{sentiment_icon}Positive Reviews", f"{np.round(sentiment_data*100, 2)}%")

        st.session_state['resto_info'] = resto_info

        # b_col1, b_col2 = main_col2.columns(2)

        with st.spinner("Counting reviews..."):
            reviews_data = reviews_histogram(resto_info['gmap_id'], state_selected, headers=api_call_headers)

            main_col2.subheader("Reviews Distribution")

            if len(pd.DataFrame(reviews_data['body'])) == 0:
                main_col2.caption("No reviews found.")
            else:
                main_col2.bar_chart(pd.DataFrame(reviews_data['body']), x='rating', y='count')


        # Graph Node
        st.subheader("Cosine Similarity Graph")
        
        c_col1, c_col2 = st.columns([0.3,0.7])

        c_col1.info("Use your mouse wheel to zoom in and out. You can click and drag to move around the node graph area.", icon="💡")

        c_col2.markdown("Legend")
        node_graph_legend = pd.DataFrame({
            "Node Color":["🟡", "🟢", "🔴"],
            "Description":[
                "Chosen vegan-friendly establishment on the map",
                "Vegan-friendly establishments",
                "Ordinary establishments",
            ]
        })

        c_col2.dataframe(node_graph_legend, hide_index=True, width=500)

        degrees = c_col1.slider("Degrees", min_value=2, max_value=4, value=3)
        
        similarity_model = c_col1.selectbox(
            "Similarity Model",
            (
                "all-distilroberta-v1",
                "all-MiniLM-L6-v2",
                "all-MiniLM-L12-v2",
                "all-mpnet-base-v2",
            ),
            index=3,
        )

        restaurant_edges = pd.DataFrame(
            get_restaurant_edges(
                resto_info['gmap_id'],
                degrees=degrees,
                model=similarity_model,
                headers=api_call_headers,
            )['body']
        )

        threshold_midpoint = (
            (
                (1-restaurant_edges.cosine_distance.min())
                + (1-restaurant_edges.cosine_distance.max())
            )
            / 2
        )

        similarity_threshold = c_col1.slider(
            "Similarity Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.60,
        )

        restaurant_edges_filtered = restaurant_edges[(1-restaurant_edges.cosine_distance) >= similarity_threshold]
        # st.dataframe(restaurant_edges)
        
        nodes = []
        edges = []

        node_font = "12px arial white"

        # Attach Nodes
        nodes_df_a = restaurant_edges_filtered[['gmap_id_a', 'meta_name_a', 'meta_category_a']].drop_duplicates()
        nodes_df_a.columns = ['gmap_id', 'meta_name', 'meta_category']
        
        nodes_df_b = restaurant_edges_filtered[['gmap_id_b', 'meta_name_b', 'meta_category_b']].drop_duplicates()
        nodes_df_b.columns = ['gmap_id', 'meta_name', 'meta_category']

        nodes_df = pd.concat([nodes_df_a, nodes_df_b], axis=0)
        nodes_df = nodes_df.drop_duplicates()

        for source_id, source, meta_category in nodes_df[['gmap_id', 'meta_name', 'meta_category']].values:
            
            if resto_info['gmap_id'] == source_id:
                node_color = 'yellow'
                node_size = 15
            elif 'vegan' in meta_category.lower():
                node_color = 'green'
                node_size = 5
            else:
                node_color = 'red'
                node_size = 5

            nodes.append(
                Node(
                    id=source_id,
                    size=node_size,
                    label=source,
                    color=node_color,
                    shape="dot",
                    font=node_font,
                )
            )
        

        for gmap_id_a, gmap_id_b,  cosine_distance in restaurant_edges_filtered[['gmap_id_a', 'gmap_id_b', 'cosine_distance']].values:

            cossim_str = np.round((1-cosine_distance) * 100, 2)

            # if (source_id != gmap_id_b) and (source != meta_name_b):
                # nodes.append(
                #     Node(
                #         id=gmap_id_b,
                #         size=5,
                #         label=meta_name_b + f"({cossim_str}%)",
                #         color="green" if 'vegan' in meta_category_b.lower() else "red",
                #         shape="dot",
                #         font="node_font,
                #     )
                # )

            # Add cosine similarity
            edges.append(
                Edge(
                    source=gmap_id_a,
                    color="white",
                    target=gmap_id_b,
                    # value=1 - cosine_distance,
                    # label=1 - cosine_distance,
                    # widthConstraint=0.1,
                )
            )

        config = Config(
            width=1000,
            height=1000,
            directed=False,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=False,
            highlightColor="white"
        )

        with c_col2:
            return_value = agraph(
                nodes=nodes,
                edges=edges,
                config=config
            )

            st.write(return_value)
