import streamlit as st
import pandas as pd
import random
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Establish Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Configure page for a professional clinical study appearance
st.set_page_config(page_title="Pulse to Polyphony Study", page_icon="🎵", layout="centered")

st.title("Pulse to Polyphony: Auditory Perception Study")
st.markdown("""
Welcome to the perceptual usability study. Please listen to the following six generative audio tracks.
Your goal is to rate your intuitive perception of the physical health state represented by each soundscape.
Please wear headphones for the best experience.
""")

# Active Google Sheet Share links
RATINGS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1GQXZCd3BNJzetEhPUiaLnrEH36G2JWYwZK8OLRsorR0/edit?usp=sharing"
GROUPINGS_SHEET_URL = "https://docs.google.com/spreadsheets/d/1mtbvsnz42qFeml7Y62FMt9jQv_WtjdLeku95FwowrMo/edit?usp=sharing"

# Initialize session state to randomize and persist track order per participant
if 'participant_id' not in st.session_state:
    st.session_state.participant_id = datetime.now().strftime("%Y%m%d%H%M%S")

if 'audio_files' not in st.session_state:
    files = [
        {"file": "normal_1.wav", "state": "Baseline (Normal)"},
        {"file": "normal_2.wav", "state": "Baseline (Normal)"},
        {"file": "normal_3.wav", "state": "Baseline (Normal)"},
        {"file": "apnea_1.wav", "state": "Anomaly (Apnea)"},
        {"file": "apnea_2.wav", "state": "Anomaly (Apnea)"},
        {"file": "apnea_3.wav", "state": "Anomaly (Apnea)"}
    ]
    random.shuffle(files)
    st.session_state.audio_files = files

def survey_block(track_info, track_index):
    display_name = f"Audio Track {track_index + 1}"
    file_name = track_info["file"]
    true_state = track_info["state"]

    st.header(display_name)

    try:
        st.audio(file_name)
        
        # Likert Scales
        clarity = st.slider("Clarity: How clearly does this represent a distinct health state?", 1, 5, 3, key=f"c_{track_index}")
        stress = st.slider("Stress/Urgency: What level of urgency does this induce?", 1, 5, 3, key=f"s_{track_index}")
        reassure = st.slider("Reassurance: Does the background rhythm provide a sense of safety?", 1, 5, 3, key=f"r_{track_index}")
        mapping = st.slider("Intuitive Mapping: How naturally does this sound map to a medical event?", 1, 5, 3, key=f"m_{track_index}")
        
        comments = st.text_area("Think-aloud Comments (Optional):", key=f"t_{track_index}")
        
        if st.button(f"Submit Ratings for {display_name}", key=f"btn_{track_index}"):
            new_data = pd.DataFrame([[
                st.session_state.participant_id, display_name, true_state, 
                clarity, stress, reassure, mapping, comments
            ]], columns=["Participant_ID", "Track_Name", "True_State", "Clarity", "Stress_Urgency", "Reassurance", "Intuitive_Mapping", "Qualitative_Comments"])
            
            # Google Sheets Cloud Routing Logic
            existing_data = conn.read(spreadsheet=RATINGS_SHEET_URL)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(spreadsheet=RATINGS_SHEET_URL, data=updated_data)
            
            st.success(f"Response for {display_name} saved successfully to cloud!")
            
    except FileNotFoundError:
        st.error(f"Error: {file_name} not found in the directory.")
    st.divider()

# Render survey blocks
for i, track in enumerate(st.session_state.audio_files):
    survey_block(track, i)

# Final Grouping Section
st.header("Final Track Classification")
st.markdown("Based on what you heard, please group the tracks. Select the **three** tracks you believe represent the **Anomaly (Apnea)** state. The remaining tracks will automatically be categorized as Normal Baseline.")

track_names = [f"Audio Track {i+1}" for i in range(6)]
guessed_apnea = st.multiselect("Select the 3 Apnea tracks:", track_names, max_selections=3)

if st.button("Submit Final Classification"):
    if len(guessed_apnea) == 3:
        guessed_normal = [t for t in track_names if t not in guessed_apnea]
        grouping_data = pd.DataFrame([[
            st.session_state.participant_id,
            ", ".join(guessed_apnea),
            ", ".join(guessed_normal)
        ]], columns=["Participant_ID", "Guessed_Apnea_Tracks", "Guessed_Normal_Tracks"])
        
        # Google Sheets Cloud Routing Logic
        existing_group_data = conn.read(spreadsheet=GROUPINGS_SHEET_URL)
        updated_group_data = pd.concat([existing_group_data, grouping_data], ignore_index=True)
        conn.update(spreadsheet=GROUPINGS_SHEET_URL, data=updated_group_data)
        
        st.success("Classification submitted! Thank you for participating in the Pulse to Polyphony study.")
    else:
        st.warning("Please select exactly 3 tracks before submitting.")
