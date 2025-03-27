from langgraph.types import Command
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import streamlit as st
import asyncio
import uuid
import random

from agent_graph import travel_agent_graph

# Page configuration
st.set_page_config(
    page_title="Travel Planner Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .stChatMessage .content {
        padding: 0.5rem;
    }
    .stChatMessage .timestamp {
        font-size: 0.8rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

class UserContext(BaseModel):
    user_id: str
    preferred_airlines: List[str]
    hotel_amenities: List[str]
    budget_level: str

@st.cache_resource
def get_thread_id():
    return str(uuid.uuid4())

thread_id = get_thread_id()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4()),
        preferred_airlines=[],
        hotel_amenities=[],
        budget_level="mid-range"
    )

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to handle user input
def handle_user_message(user_input: str):
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    st.session_state.processing_message = user_input

# Function to invoke the agent graph
async def invoke_agent_graph(user_input: str):
    if not user_input:
        raise ValueError("User input is missing. Please provide a valid input.")

    config = {"configurable": {"thread_id": thread_id}}
    user_context = st.session_state.user_context

    # First message from user
    if len(st.session_state.chat_history) == 1:
        initial_state = {
            "user_input": user_input,
            "preferred_airlines": user_context.preferred_airlines,
            "hotel_amenities": user_context.hotel_amenities,
            "budget_level": user_context.budget_level
        }
        async for msg in travel_agent_graph.astream(initial_state, config, stream_mode="custom"):
            yield msg
    else:
        async for msg in travel_agent_graph.astream(Command(resume=user_input), config, stream_mode="custom"):
            yield msg

async def main():
    with st.sidebar:
        st.title("Travel Preferences")
        st.subheader("About You")
        traveler_name = st.text_input("Your Name", value="Traveler")

        st.subheader("Travel Preferences")
        preferred_airlines = st.multiselect(
            "Preferred Airlines",
            ["SkyWays", "OceanAir", "MountainJet", "Delta", "United", "American", "Southwest"],
            default=st.session_state.user_context.preferred_airlines
        )

        preferred_amenities = st.multiselect(
            "Must-have Hotel Amenities",
            ["WiFi", "Pool", "Gym", "Free Breakfast", "Restaurant", "Spa", "Parking"],
            default=st.session_state.user_context.hotel_amenities
        )

        budget_level = st.select_slider(
            "Budget Level",
            options=["budget", "mid-range", "luxury"],
            value=st.session_state.user_context.budget_level or "mid-range"
        )

        if st.button("Save Preferences"):
            st.session_state.user_context.preferred_airlines = preferred_airlines
            st.session_state.user_context.hotel_amenities = preferred_amenities
            st.session_state.user_context.budget_level = budget_level
            st.success("Preferences saved!")

        st.divider()

        if st.button("Start New Conversation"):
            st.session_state.chat_history = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.success("New conversation started!")

    # Display Example Queries
    example_queries = [
        "Plan a trip to Paris from New York, leaving on June 10 and returning on June 20. My hotel budget is $150 per night.",
        "Find me a flight to Tokyo from Los Angeles on April 15, returning on April 25, with a max hotel budget of $200 per night.",
        "I'm traveling from London to Rome on May 5 for 4 days. I prefer hotels with WiFi and free breakfast.",
        "Suggest a budget-friendly travel plan for a 7-day trip to Bali from Sydney."
    ]

    st.title("✈️ Travel Planner Assistant")
    st.caption("Give me the details for your trip and let me plan it for you!")

    # Show a random example query suggestion
    st.info(f"💡 Try: **{random.choice(example_queries)}**")

    # Expandable section for example queries
    with st.expander("Need help? Try these examples ⬇️"):
        for query in example_queries:
            if st.button(f"📌 {query[:30]}..."):
                handle_user_message(query)
                st.rerun()

    # Display Chat Messages
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}"):
                st.markdown(message["content"])
                st.caption(message["timestamp"])
        else:
            with st.chat_message("assistant", avatar="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent"):
                st.markdown(message["content"])
                st.caption(message["timestamp"])

    # User Input
    user_input = st.chat_input("Let's plan a trip...")
    if user_input:
        handle_user_message(user_input)
        st.rerun()

    # Processing User Input
    if st.session_state.processing_message:
        user_input = st.session_state.processing_message
        st.session_state.processing_message = None
        if not user_input:
            st.error("User input is missing. Please provide a valid input.")
            return

        with st.spinner("Thinking..."):
            try:
                response_content = ""

                with st.chat_message("assistant", avatar="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent"):
                    message_placeholder = st.empty()

                    async for chunk in invoke_agent_graph(user_input):
                        response_content += chunk
                        message_placeholder.markdown(response_content)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })

            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_message)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })

    st.divider()
    st.caption("Powered by Pydantic AI and LangGraph | Built with Streamlit")

if __name__ == "__main__":
    asyncio.run(main())
