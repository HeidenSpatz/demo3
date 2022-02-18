import streamlit as st
import pandas as pd
from gsheetsdb import connect

import geemap.foliumap as geemap
from geopy.geocoders import Nominatim 
#To avoid time out in API
from geopy.extra.rate_limiter import RateLimiter



#------------------
# config
st.set_page_config(page_title='Immo-FFM-Demo',
                #page_icon=":shark:",
                layout='wide')
                #menu_items: Get help, Report a Bug, About

st.title("hello 3")


# get data from google sheet
#------------------

# Share the connector across all users connected to the app
@st.experimental_singleton()
def get_connector():
    return connect()

# Time to live: the maximum number of seconds to keep an entry in the cache
TTL = 24 * 60 * 60

# Using `experimental_memo()` to memoize function executions
@st.experimental_memo(ttl=TTL)
def query_to_dataframe(_connector, query: str) -> pd.DataFrame:
    rows = _connector.execute(query, headers=1)
    dataframe = pd.DataFrame(list(rows))
    return dataframe

@st.experimental_memo(ttl=600)
def get_data(_connector, gsheets_url) -> pd.DataFrame:
    return query_to_dataframe(_connector, f'SELECT * FROM "{gsheets_url}"')


gsheet_connector = get_connector()
gsheets_url = st.secrets["gsheets"]["public_gsheets_url"]
data = get_data(gsheet_connector, gsheets_url)
df = pd.DataFrame(data)


# overiew
#------------------
st.header("Overview")
with st.expander("Click to see basic stats!"):
    st.write(df.describe())





#------------------
# get input
st.header("please enter address and parameters")
# street, housenumber, city, zip code
col1, col2, col3, col4 = st.columns([4, 1, 3, 2])

with col1:
    street = col1.text_input('Street')

with col2:
    housenr = col2.text_input('Nr.')

with col3:
    zip = st.text_input('Zip Code')
    
with col4:
    city = st.text_input('City')

st.write('address: ', street, " ", housenr, ", ", zip, " ", city)


geolocator = Nominatim(user_agent="my_user_agent")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)

address = street + " " + housenr + ", " + city + " " + zip



if len(address) > 5:
    
    location = geolocator.geocode(address)

    lat = location.latitude
    lon = location.longitude

    st.write(location.address)
    st.write(lat, lon)
    #st.write(f"Lat, Lon: {lat}, {lon}")
    #st.write(location.raw)
    popup = f"lat, lon: {lat}, {lon}"

    m = geemap.Map(center=[lat, lon], zoom=15)
    m.add_basemap("ROADMAP")
    m.add_marker(location=(lat, lon), popup=popup)    
    m.to_streamlit(height=600)
else:
    m = geemap.Map(center=[50.12978175, 8.693144895303579], zoom=15)
    m.to_streamlit(height=600)