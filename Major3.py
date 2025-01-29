import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configure your Gemini API key
genai.configure(api_key="AIzaSyCELeb5yW-sNM1k7NtrBKj8vBbB9PDS9wE")

# Load the groundwater data from CSV
file_path = "C:/Users/akhil/Downloads/District_Statewise_Well.csv"  # Update with your file path

# Try loading the CSV data
try:
    data = pd.read_csv(file_path)
    st.success("Data loaded successfully!")
except FileNotFoundError:
    st.error(f"File not found: {file_path}. Please check the file path.")
    st.stop()
except pd.errors.ParserError:
    st.error("Error parsing the CSV file. Please ensure the file is correctly formatted.")
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

# Store conversation history
conversation_history = []

# Define a function to fetch groundwater details based on location
def get_groundwater_data(state, district):
    location_data = data[(data['Name of State'] == state) & (data['Name of District'] == district)]
    if not location_data.empty:
        return location_data.to_dict(orient='records')[0]
    else:
        return None

# Define a function to generate a response with context
def generate_response(user_query, context):
    # Append the user query to the conversation history
    conversation_history.append(f"User: {user_query}")
    conversation_history.append(f"Context: {context}")

    # Prepare the full conversation history as context for the AI
    conversation_history_text = "\n".join(conversation_history)

    # Generate response from Gemini AI using the full conversation context
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(conversation_history_text)
    chatbot_reply = response.text

    # Append chatbot response to the conversation history
    conversation_history.append(f"Chatbot: {chatbot_reply}")

    return chatbot_reply

# Function to handle the user's query
def handle_query(query, location_data):
    if location_data:
        # Build context with more columns for varied responses
        if "recharge from rainfall" in query.lower():
            context = f"Recharge from rainfall During Monsoon Season: {location_data['Recharge from rainfall During Monsoon Season']} million cubic meters"
        elif "ground water extraction" in query.lower():
            context = f"Current Annual Ground Water Extraction For Irrigation: {location_data['Current Annual Ground Water Extraction For Irrigation']} million cubic meters"
        elif "stage of extraction" in query.lower():
            context = f"Stage of Ground Water Extraction: {location_data['Stage of Ground Water Extraction (%)']}%"
        elif "total annual recharge" in query.lower():
            context = f"Total Annual Ground Water Recharge: {location_data['Total Annual Ground Water Recharge']} million cubic meters."
        elif "natural discharges" in query.lower():
            context = f"Total Natural Discharges: {location_data['Total Natural Discharges']} million cubic meters."
        elif "annual extractable resources" in query.lower():
            context = f"Annual Extractable Ground Water Resource: {location_data['Annual Extractable Ground Water Resource']} million cubic meters."
        elif "domestic and industrial extraction" in query.lower():
            context = f"Current Annual Ground Water Extraction For Domestic & Industrial Use: {location_data['Current Annual Ground Water Extraction For Domestic & Industrial Use']} million cubic meters."
        elif "total extraction" in query.lower():
            context = f"Total Current Annual Ground Water Extraction: {location_data['Total Current Annual Ground Water Extraction']} million cubic meters."
        elif "gw allocation for domestic use" in query.lower():
            context = f"Annual GW Allocation for Domestic Use as on 2025: {location_data['Annual GW Allocation for Domestic Use as on 2025']} million cubic meters."
        elif "net ground water availability" in query.lower():
            context = f"Net Ground Water Availability for future use: {location_data['Net Ground Water Availability for future use']} million cubic meters."
        elif "noc" in query.lower():
            context = "Check Eligibility: Verify if your activity and area require an NOC under CGWA or state guidelines. Gather Documents: Land ownership proof, Groundwater impact assessment report, Rainwater harvesting/recharge plan, Water use details."
        else:
            context = f"Total Annual Ground Water Recharge: {location_data['Total Annual Ground Water Recharge']} million cubic meters."

        # Generate the chatbot response using the context
        response = generate_response(query, context)
        return response
    else:
        return "Sorry, no data found for the specified location."

# Streamlit app
st.title("Groundwater Information Chatbot")
st.write("Enter your location to get started and ask questions about groundwater.")

# State and district input (using session_state to keep values)
if 'state' not in st.session_state:
    st.session_state.state = ''
if 'district' not in st.session_state:
    st.session_state.district = ''

# User input for location
st.session_state.state = st.text_input("Enter your State:", value=st.session_state.state)
st.session_state.district = st.text_input("Enter your District:", value=st.session_state.district)

# Handle the location query and query processing after fetching data
if st.session_state.state and st.session_state.district:
    # Fetch groundwater data for the location
    location_data = get_groundwater_data(st.session_state.state, st.session_state.district)
    
    if location_data:
        st.success(f"Data found for {st.session_state.district}, {st.session_state.state}. You can now enter your query.")
        
        # User query input
        query = st.text_input("Enter your query:")
        
        # If the "Send" button is clicked, process the query
        if st.button("Send") and query:
            # Get response from the chatbot based on location data
            answer = handle_query(query, location_data)
            st.write(f"Chatbot response: {answer}")
    else:
        st.error("No data found for the specified location. Please check the input.")
else:
    st.info("Please enter both State and District.")
