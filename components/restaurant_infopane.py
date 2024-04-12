import streamlit as st
import numpy as np
import pandas as pd

def generate_restaurant_infopane(st_main):

    # Show Selected Restaurants
    st_main.subheader(st.session_state["last_object_clicked_popup"], divider="green")

    desc_str = (
        st.session_state['resto_info']['description']
        if st.session_state['resto_info']['description'] is not None
        or st.session_state['resto_info']['description'] != 'None'
        or st.session_state['resto_info']['description'] != np.nan
        else "No description available."
    )

    st_main.markdown(f"**DESCRIPTION**: {desc_str}")

    st_main.markdown(f"**ADDRESS**: {st.session_state['resto_info']['address']}")

    st_main.caption("TAGS: " + ", ".join(st.session_state['resto_info']['category'].split(",")))
    st_main.caption("GMAP ID: " + st.session_state['resto_info']['gmap_id'])

    col1, col2, col3 = st_main.columns(3)

    col1.metric("Avg. Rating", f"{st.session_state['resto_info']['avg_rating']}")
    col2.metric("Reviews", f"{st.session_state['resto_info']['num_of_reviews']}")

    priciness_value = (
        'N/A' if st.session_state['resto_info']['price'] == 'None' or st.session_state['resto_info']['price'] is None
        else "💲" * len(st.session_state['resto_info']['price'])
    )

    col3.metric("Priciness", priciness_value)

    return col1, col2, col3