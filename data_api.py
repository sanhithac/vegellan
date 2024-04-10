import os
import logging
import requests
import streamlit as st

# Resolve BASE_URL/VEGELLAN_API_URL value:
# Get it first from st.secrets if it exists,
# then look for it in the environment variables.
# This will have a default value of `http://localhost:8000`
# if not provided
if st.secrets["VEGELLAN_API_URL"] is None:
    BASE_URL = os.environ.get("VEGELLAN_API_URL", "http://localhost:8000")
else:
    BASE_URL = st.secrets["VEGELLAN_API_URL"]

logger = logging.getLogger(__name__)

@st.cache_data
def api_authenticate(headers=None):
    try:
        response = requests.get(
            f"{BASE_URL}/authenticate",
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text

        return {"status":"error", "message": error_msg}

    if response.status_code != 200:
        return {"status":"error", "message": f"{response.status_code} error. Check your API Key."}

    return {
        "status": "success",
        "body": "Authentication successful!",
    }

@st.cache_data
def get_list_of_states(headers=None):

    try:
        response = requests.get(
            f"{BASE_URL}/restaurant/states",
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text

        return {"status":"error", "message": error_msg}

    return {
        "status": "success",
        "body": response.json(),
    }

@st.cache_data
def get_list_of_restaurants(state, sampling_factor, headers=None):

    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/{state}/{sampling_factor}",
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text
        return {"status":"error", "message": error_msg}
    
    return {
        "status": "success",
        "body": response.json(),
    }

@st.cache_data
def search_restaurant(search_term, top_results, state, headers=None):

    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/{state}/search",
            headers=headers,
            params={
                "search_input": search_term,
                "top_results": top_results,
            },
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text
        return {"status":"error", "message": error_msg}
    
    return {
        "status": "success",
        "body": response.json(),
    }

@st.cache_data
def reviews_histogram(gmap_id, state, headers=None):
    try:
        response = requests.get(
            f"{BASE_URL}/restaurant/reviews_histogram/{state}/{gmap_id}",
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text
        return {"status":"error", "message": error_msg}
    
    return {
        "status": "success",
        "body": response.json(),
    }


@st.cache_data
def get_restaurant_edges(gmap_id, degrees=2, model="all-mpnet-base-v2", headers=None):

    try:
        response = requests.get(
            f"{BASE_URL}/restaurant/{gmap_id}/nodes",
            headers=headers,
            params={
                "model":model,
                "degrees":degrees,
            }
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text
        return {"status":"error", "message": error_msg}
    
    return {
        "status": "success",
        "body": response.json(),
    }

@st.cache_data
def get_sentiment(gmap_id, state, headers=None):

    try:
        response = requests.get(
            f"{BASE_URL}/sentiments/{state}/{gmap_id}",
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        error_msg = e.response.text
        return {"status":"error", "message": error_msg}
    
    return {
        "status": "success",
        "body": response.json(),
    }
