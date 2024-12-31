import streamlit as st
from datetime import date
from Travel_Itinerary import get_itinerary

# Setting page configuration
st.set_page_config(page_title="Travel Itinerary", page_icon="✈")

# Session state for initialization
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = ""

# Title
st.title("**Hi, I am Your Travel Planner...**")
# Subheading
st.subheader("Plan Your Next Trip With Me..")

# Collect user inputs through the sidebar
st.sidebar.title("Enter Your Travel Details:")
Departure = st.sidebar.text_input("Source", "Paris")
Destination = st.sidebar.text_input("Destination", "New York")
Date = st.sidebar.date_input("Travel Start Date", min_value=date.today())
Date = Date.strftime("%Y-%m-%d")
Duration = st.sidebar.slider("Duration", min_value=1, max_value=90)
Budget = st.sidebar.number_input("Budget", min_value=1000, max_value=1000000, step=100)
Currency = st.sidebar.selectbox("Currency", ["INR", "USD", "EUR", "GBP", "JPY", "AUD", "CNY", "MXN", "BRL"])
Food_Preferences = st.sidebar.text_input("Food Preferences", "Local Cuisine")
Activity = st.sidebar.text_input("Activities", "Adventure")
Hotel = st.sidebar.selectbox("Hotel Preference", ["Luxury", "Mid_Budget", "Low_Budget"])

# Button to trigger itinerary generation
if st.sidebar.button("Generate Itinerary"):
    # Call the function to generate itinerary
    itinerary = get_itinerary(Departure, Destination, Date, Duration, Budget, Currency, Food_Preferences, Activity, Hotel)

    # Store itinerary in session state
    st.session_state.itinerary = itinerary

    # Display generated itinerary
    st.subheader("Your Travel Itinerary:🛬🛫")
    st.write(itinerary)

    # Button to download itinerary as a text file
    st.download_button(
        label="Download Itinerary",
        data=itinerary,
        file_name="travel_itinerary.txt",
        mime="text/plain"
    )
