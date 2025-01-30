import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
from groq import Groq  # Ensure you have the Groq API key

# Load doctor dataset
df = pd.read_csv("doctors.csv")

# Initialize AI model
groq_client = Groq(api_key="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")  # Replace with your actual API key

st.markdown("""
    <style>
        /* Style the entire app */
        body {
            background-color: #f4f4f4;
font-family: Arial, sans-serif;G
        }

        /* Center the title and add logo */
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .title-container img {
            width: 50px; /* Adjust logo size */
            height: 50px;
        }

        .title-container h1 {
            font-size: 28px !important;
            font-weight: bold;
            color: #2C3E50;
        }

        /* Style the input text field */
        input[type="text"] {
            border-radius: 10px;
            border: 2px solid #3498db;
            padding: 10px;
            width: 100%;
        }

        /* Style the button */
        div.stButton > button {
            background-color: #3498db;
            color: white;
            font-size: 16px;
            padding: 10px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
        }

        div.stButton > button:hover {
            background-color: #2980b9;
        }

        /* Style the tables */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
        }

        /* Style success message */
        .stSuccess {
            font-size: 18px;
            font-weight: bold;
            color: green;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Display Title with Logo
st.markdown(
    """
    <div class="title-container">
        <img src="DIU logo.jpg">
        <h1>DIU Medical Assistance</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar: Emergency Contact & Available Doctors

st.sidebar.header("Email of DIU Medical Center")
st.sidebar.write(" **Email:** diumc@daffodilvarsity.edu.bd")

st.sidebar.header("🚑 Emergency Contact")
st.sidebar.write("📞 **Ambulance:** 01847334999")
st.sidebar.write("📞 **Medical Center Hotline Number:** 01847140120")


st.sidebar.header("🩺 Available Doctors")
available_doctors = df[df["Available"] == "Yes"][["Name", "Department", "Shift","Phone"]]
st.sidebar.dataframe(available_doctors)


def get_medical_advice(symptom):
    """Get medical advice using Groq's API"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": symptom}],
        temperature=0.7
    )
    return response.choices[0].message.content

def recommend_doctor(symptom):
    """Recommend a doctor based on the symptom"""
    symptom_mapping = {
        "heart": "Cardiologist",
        "chest pain": "Cardiologist",
        "heartattack": "Cardiologist",
        "teeth": "Dentist",
        "toothache": "Dentist",
        "gum": "Dentist",
        "back pain": "Physiotherapist",
        "muscle pain": "Physiotherapist",
        "pain": "Physiotherapist",
        "injury": "Physiotherapist",
        "body": "Physiotherapist",
        "bleeding": "Physiotherapist",
        "joint pain": "Physiotherapist",
        "brain": "Neurologist",
        "headache": "Neurologist",
        "brain tumors": "Neurologist",
        "seizures": "Neurologist",
        "stroke": "Neurologist",
        "memory loss": "Neurologist",
        "concussion": "Neurologist",
        "mental health": "Psychiatrist",
        "depression": "Psychiatrist",
        "anxiety": "Psychiatrist",
        "PTSD": "Psychiatrist",
        "schizophrenia": "Psychiatrist",
        "insomnia": "Psychiatrist",
        "hallucination": "Psychiatrist",
        "trauma": "Psychiatrist",
        "therapy": "Psychiatrist",
        "panic": "Psychiatrist",
        "children": "Pediatrician",
        "fever": "General Physician",
        "stomach": "General Physician",
        "digestion": "General Physician",
        "food": "General Physician",
        "digestion": "General Physician",
        "food poisioning": "General Physician",
        "cold": "General Physician",
        "breathing": "General Physician"
    }

    for key, department in symptom_mapping.items():
        if key in symptom.lower():
            doctors = df[df['Department'] == department]
            if not doctors.empty:
                return doctors

    # Default to General Physician if no match is found
    return df[df['Department'] == "General Physician"]

def send_email(to_email, doctor_name, doctor_email, doctor_phone, shift_time):
    sender_email = "rahman35-902@diu.edu.bd"
    app_password = "mijf occv voij pvfo"  # Use the generated App Password

    subject = "Appointment Confirmation"
    body = f"Your appointment with Dr. {doctor_name} is confirmed for {shift_time}.\n\n" \
           f"Doctor's Email: {doctor_email}\nDoctor's Phone: {doctor_phone}"

    message = f"Subject: {subject}\n\n{body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)  # Use App Password
        server.sendmail(sender_email, to_email, message)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error:", e)

st.title("AI Medical Hub")

symptom = st.text_input("Describe your symptoms:")

if symptom:
    advice = get_medical_advice(symptom)
    st.write("AI Advice:", advice)

    # Ask if the user wants a doctor recommendation
    want_recommendation = st.text_input("Would you like a doctor recommendation? (yes/no):")
    
    # Check if the user wants to proceed with the doctor recommendation
    if want_recommendation and "yes" in want_recommendation.lower():
        recommended_doctors = recommend_doctor(symptom)
        
        if isinstance(recommended_doctors, pd.DataFrame):
            st.write("Recommended Doctors:")
            st.dataframe(recommended_doctors)
            available_doctors = recommended_doctors[recommended_doctors["Available"] == "Yes"]
            
            if not available_doctors.empty:
                st.write("Available Doctors:")
                st.dataframe(available_doctors)

                doctor_choice = st.selectbox("Choose a doctor:", available_doctors["Name"])
                email = st.text_input("Enter your email:")
                
                if st.button("Confirm Appointment"):
                    doctor_info = available_doctors[available_doctors["Name"] == doctor_choice].iloc[0]
                    send_email(email, doctor_choice, doctor_info["Email"], doctor_info["Phone"], doctor_info["Shift"])
                    st.success(f"Appointment confirmed with {doctor_choice} at {doctor_info['Shift']}. "
                               f"Details sent to your email.")
            else:
                st.write("No available doctors at the moment.")
        else:
            st.write(recommended_doctors)