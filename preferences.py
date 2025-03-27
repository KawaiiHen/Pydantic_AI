import streamlit as st
import json
import os

PREFERENCES_FILE = "user_preferences.json"

# Load preferences from file
def load_preferences():
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, "r") as file:
            return json.load(file)
    return {
        "preferred_airlines": [],
        "hotel_amenities": [],
        "budget_level": "mid-range"
    }

# Save preferences to file
def save_preferences(preferences):
    with open(PREFERENCES_FILE, "w") as file:
        json.dump(preferences, file)

# Reset preferences
def reset_preferences():
    os.remove(PREFERENCES_FILE) if os.path.exists(PREFERENCES_FILE) else None
    return {
        "preferred_airlines": [],
        "hotel_amenities": [],
        "budget_level": "mid-range"
    }

# Streamlit Page
st.set_page_config(page_title="Manage Preferences", page_icon="⚙️")

st.title("⚙️ Manage Your Preferences")

# Load existing preferences
preferences = load_preferences()

# Form to update preferences
with st.form("preferences_form"):
    st.subheader("Update Your Preferences")
    
    preferred_airlines = st.multiselect(
        "Preferred Airlines",
        ["SkyWays", "OceanAir", "MountainJet", "Delta", "United", "American", "Southwest"],
        default=preferences["preferred_airlines"]
    )

    hotel_amenities = st.multiselect(
        "Hotel Amenities",
        ["WiFi", "Pool", "Gym", "Free Breakfast", "Restaurant", "Spa", "Parking"],
        default=preferences["hotel_amenities"]
    )

    budget_level = st.select_slider(
        "Budget Level",
        options=["budget", "mid-range", "luxury"],
        value=preferences["budget_level"]
    )

    if st.form_submit_button("Save Preferences"):
        preferences["preferred_airlines"] = preferred_airlines
        preferences["hotel_amenities"] = hotel_amenities
        preferences["budget_level"] = budget_level
        save_preferences(preferences)
        st.success("Preferences saved!")

st.divider()

# Reset preferences
if st.button("Reset Preferences"):
    preferences = reset_preferences()
    save_preferences(preferences)
    st.success("Preferences reset!")

st.divider()
st.caption("Navigate back to the main chatbot to see updates.")
