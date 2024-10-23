import json
import os
import requests
import streamlit as st
import pandas as pd
import base64

config = json.loads(open("config.json").read())
data_sources = {base64.a85decode(''.join([chr(ord(c) - 3) for c in key])).decode('utf-8'): base64.a85decode(''.join([chr(ord(c) - 3) for c in value])).decode('utf-8') for key, value in config["data_sources"].items()}

def download_jsons(force = False):
    # show loading progress with progress bar
    with sidebar_notification_container:
        with st.spinner('Downloading JSON files...'):
            for name, link in data_sources.items():
                if not os.path.exists(f"./downloads/{name}.json") or force:
                    print(f"Downloading {name}.json")
                    r = requests.get(link)
                    # create the downloads directory if it doesn't exist
                    os.makedirs("./downloads", exist_ok=True)
                    with open(f"./downloads/{name}.json", "wb") as f:
                        f.write(r.content)
                        st.toast(f"Downloaded {name}.json")
                else:
                    print(f"{name}.json already exists")

@st.cache_data
def get_data_df():
    dfs = []
    for name in data_sources.keys():
        a_df = pd.read_json(f"./downloads/{name}.json")
        dfs.append(a_df)
    pd_a = pd.concat(dfs)
    pd_a = pd.concat([pd_a["name"].reset_index(drop=True), pd.json_normalize(pd_a["downloads"])], axis=1)
    pd_a['uris'] = pd_a['uris'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    print("Data loaded")
    return pd_a

st.set_page_config(layout="wide")

sidebar_notification_container = None
dataframe_container = None
full_df = None
results_container = st.container()

with st.sidebar:
    menu_container = st.container()
    st.title('scrape-hydra')
    st.button('Redownload data', on_click=download_jsons, args=(True,))
    sidebar_notification_container = st.container()

download_jsons()
full_df = get_data_df()

with st.form("search_title"):
    st.title('Search')
    col1, col2, col3 = st.columns([3, 1, 2])
    with col1:
        title = st.text_input('title', value='')
    with col2:
        name = st.selectbox('releaser', ["*"] + full_df["name"].unique().tolist())
    with col3:
        st.form_submit_button('Search')

st.title('Results')
show_df = full_df
if title:
    show_df = show_df[show_df["title"].str.contains(title, case=False)]
if name != "*":
    show_df = show_df[show_df["name"] == name]

st.dataframe(show_df, use_container_width=True, height=800,
             column_config={
                 "uris": st.column_config.LinkColumn()
                 }
             )

