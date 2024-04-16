# Native libraries
import streamlit as st

# Local Modules
from data_api import (
    api_authenticate,
    get_list_of_states,
)

from interface import produce_main_interface

st.set_page_config(
    page_title="Vegellan App",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="collapsed",
    # menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
)

st.title("Welcome to Vegellan 🥬🔭!")

states = get_list_of_states()['body']

state_selector = st.sidebar.form("my_form")


st.session_state['state_selected'] = 'New_York'
st.session_state['api_key_input'] = None if "API_KEY" not in st.secrets else st.secrets['API_KEY']

#     st.session_state['state_selected'] = st.selectbox(
#         "Select your state",
#         states,
#         format_func=lambda x: " ".join(x.split("_")),
#         index=states.index('New_York'),
#     ) 

#     st.session_state['api_key_input'] = st.text_input(
#         "API Key",
#         type="password",
#         value= None if "API_KEY" not in st.secrets else st.secrets['API_KEY'],
#     )
    
#     st.subheader("Experimental")

#     st.session_state['show_all_restaurants'] = st.toggle("Show All Restaurants", value=False)

#     if st.session_state['show_all_restaurants']:
#         st.session_state['sampling_factor'] = st.slider("Sampling Factor", 0.0, 1.0, value=0.1)

#     st.session_state['state_select_submitted'] = st.form_submit_button("Submit")

# Check if API Key input authenticates
st.session_state["api_call_headers"] = {"X-API-Key": st.session_state['api_key_input']}
authenticate_check = api_authenticate(headers=st.session_state["api_call_headers"])

if authenticate_check['status'] == 'error':
    st.sidebar.error(f"API Error: {authenticate_check['message']}", icon="⚠️")
    st.session_state['authenticated'] = False
else:
    st.sidebar.success(f"API Success: {authenticate_check['body']}", icon="👍")
    st.session_state['authenticated'] = True

# Create a warning if state is not New York
if st.session_state['state_selected'] != 'New_York':
    st.warning(
        "WARNING: You have selected a different state aside from New York. Some visuals will not be produced due to interest of time.",
        icon="⚠️"
    )

if st.session_state['authenticated']:
    produce_main_interface()
else:
    st.error("API Key Error: Ensure that provided API key is correct.", icon="⚠️")

