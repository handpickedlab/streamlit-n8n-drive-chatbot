import streamlit as st
import requests
import uuid  # Import uuid module for generating unique session IDs


# Configuration
development = True  # Switch between development and production
url = "http://localhost:5678" # Change to appropriate URL if deployed live

# Determine webhook base path
if development:
    webhook_base = f"{url}/webhook-test"
else:
    webhook_base = f"{url}/webhook"

st.title("n8n Chatbot")

# Initialize session state
if 'initialized' not in st.session_state:
    # Generate a unique session_id
    st.session_state['session_id'] = str(uuid.uuid4())
    
    # Call the init-chatbot webhook
    try:
        response = requests.post(
            f"{webhook_base}/init-chatbot",
            json={}
        )
        response.raise_for_status()  # Raise an error for bad status codes
        init_data = response.json()
        
        # Store the welcome message
        st.session_state['welcome_message'] = init_data.get('welcomeMessage', 'Welcome!')
        
        # Store the assistant_id
        assistant_id = init_data.get('assistant_id')
        if assistant_id:
            st.session_state['assistant_id'] = assistant_id
        else:
            st.error("Initialization failed: 'assistant_id' not returned.")
            st.stop()
        
        # Initialize messages list
        st.session_state['messages'] = []
        st.session_state['initialized'] = True
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to initialize the chatbot: {e}")
        st.stop()

# Display the welcome message
st.write(st.session_state['welcome_message'])

# Chatbot interface
user_input = st.text_input("You:")

if st.button("Send"):
    if user_input:
        # Display user message
        st.session_state['messages'].append({"user": user_input})
        
        # Retrieve assistant_id and session_id from session state
        assistant_id = st.session_state.get('assistant_id')
        session_id = st.session_state.get('session_id')
        if not assistant_id or not session_id:
            st.error("Session ID or Assistant ID is missing. Please refresh the page to reinitialize the chatbot.")
            st.stop()
        
        # Send message to n8n chatbot webhook
        try:
            response = requests.post(
                f"{webhook_base}/chat",
                json={
                    "message": user_input,
                    "assistant_id": assistant_id,
                    "session_id": session_id
                }
            )
            response.raise_for_status()
            reply = response.json().get("output", "")
            # Display bot reply
            st.session_state['messages'].append({"bot": reply})
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the chatbot: {e}")

# Display chat history
for msg in st.session_state['messages']:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    elif "bot" in msg:
        st.markdown(f"**Bot:** {msg['bot']}")
