from typing import Type

import streamlit as st

# Folium Libraries
import folium
from folium.plugins import HeatMap

# 3rd-Party Libraries
from streamlit_folium import st_folium

def generate_interactive_map(
        main_st,
        list_of_state_restaurants,
):

    '''This function generates the main interactive map of Vegellan.

    Parameters:
    main_st (streamlit submodule | Streamlit Column object): streamlit object to be called where the visuals will be called on.
    list_of_state_restaurants (pd.DataFrame): Dataframe containing the list of restaurant information.
    '''

    st.session_state['toggle_heatmap'] = main_st.toggle("Toggle Heatmap", value=True)

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
            main_st.error("WARNING: Toggling off heatmap mode can only be done if you zoom enough.", icon="⚠️")
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


    with main_st:
        if st.session_state['toggle_heatmap']:
            st.info("Heatmap shows the density of vegan restaurants around the area. Red means more concentration in the area.", icon="💡")
        else:
            st.info("Click on a map pin to show its information and similarity graph.", icon="💡")

        result = st_folium(
            m,
            width=1_000,
            height=4_00,
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

        st.session_state["last_object_clicked_popup"] = result['last_object_clicked_popup']
        st.session_state["last_object_clicked"] = result['last_object_clicked']