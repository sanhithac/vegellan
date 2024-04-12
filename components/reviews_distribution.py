import streamlit as st
import numpy as np
import pandas as pd

def generate_reviews_distribution(reviews_histogram_data, st_main):
    
    with st.spinner("Counting reviews..."):

        st_main.subheader("Reviews Distribution")

        if len(pd.DataFrame(reviews_histogram_data)) == 0:
            st_main.caption("No reviews found.")
        else:
            st_main.bar_chart(
                pd.DataFrame(reviews_histogram_data),
                x='rating',
                y='count',
                height=180,
            )