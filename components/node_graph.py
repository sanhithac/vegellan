import numpy as np
import pandas as pd
import streamlit as st

from streamlit_agraph import agraph, Node, Edge, Config

def generate_node_graph(get_restaurant_edges_fxn):
    
    # Graph Node Visual
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

    degrees = c_col1.slider("Degrees", min_value=2, max_value=4, value=2)
    
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


    similarity_threshold = c_col1.slider(
        "Similarity Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.60,
    )

    restaurant_edges = pd.DataFrame(
        get_restaurant_edges_fxn(
            st.session_state['resto_info']['gmap_id'],
            degrees=degrees,
            model=similarity_model,
            headers=st.session_state["api_call_headers"],
        )['body']
    )

    # threshold_midpoint = (
    #     (
    #         (1-restaurant_edges.cosine_distance.min())
    #         + (1-restaurant_edges.cosine_distance.max())
    #     )
    #     / 2
    # )

    restaurant_edges_filtered = restaurant_edges[(1-restaurant_edges.cosine_distance) >= similarity_threshold]

    # Start building the node graph itself...
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
        
        if st.session_state['resto_info']['gmap_id'] == source_id:
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
        agraph(
            nodes=nodes,
            edges=edges,
            config=config
        )
