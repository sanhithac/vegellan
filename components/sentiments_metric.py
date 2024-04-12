import streamlit as st
import numpy as np
import pandas as pd

def generate_sentiments_metric(sentiments_data, st_main):

    sentiment_data = pd.DataFrame(sentiments_data)

    if 'sentiment_count' not in sentiment_data.columns:
        st_main.metric("Positive Reviews", f"N/A")
    else:
        sentiment_data['sentiment_ratio'] = sentiment_data['sentiment_count'] / sentiment_data['sentiment_count'].sum()

        sentiment_data = sentiment_data[sentiment_data['sentiment_label'] == 'POSITIVE']['sentiment_ratio'].values[0]
        
        if sentiment_data <= 0.6:
            sentiment_icon = "🔴"
        elif sentiment_data <= 0.8:
            sentiment_icon = "🟡"
        else:
            sentiment_icon = "🟢"     

        st_main.metric(f"{sentiment_icon}Positive Reviews", f"{np.round(sentiment_data*100, 2)}%")