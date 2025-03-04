import streamlit as st
import re
import random
import string
from datetime import datetime, timedelta

# Initialize session state for theme selection
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True  # Default to dark mode

# Apply theme colors based on toggle state
def apply_theme():
    return {
        "bg_color": "#121212",  # Dark background
        "text_color": "#ffffff",  # White text
        "input_bg": "#1e1e1e",  # Dark input field
        "input_text": "#ffffff",  # White input text
        "button_bg": "#333",  # Dark button
        "button_text": "#ffffff",  # White button text
        "sidebar_bg": "#1e1e1e",  # Dark sidebar background
        "sidebar_text": "#ffffff",  # White sidebar text
    }

theme = apply_theme()

# Custom CSS to apply theme
theme_css = f"""
    <style>
        body {{
            background-color: {theme["bg_color"]};
            color: {theme["text_color"]};
        }}
        .stTextInput > div > div > input, .stDateInput > div > div > input {{
            background-color: {theme["input_bg"]};
            color: {theme["input_text"]};
            border-radius: 5px;
        }}
        .stButton > button {{
            background-color: {theme["button_bg"]};
            color: {theme["button_text"]};
            border-radius: 5px;
            padding: 10px;
            border: none;
        }}
        .stSidebar {{
            background-color: {theme["sidebar_bg"]} !important;
        }}
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar span {{
            color: {theme["sidebar_text"]} !important;
        }}
    </style>
"""

st.markdown(theme_css, unsafe_allow_html=True)

# List of common weak passwords to reject
BLACKLISTED_PASSWORDS = {"password", "123456", "qwerty", "password123", "admin", "letmein"}

# Function to check password strength
def check_password_strength(password):
    score = 0
    feedback = []

    # Blacklist check
    if password.lower() in BLACKLISTED_PASSWORDS:
        return "Very Weak", 0, ["Your password is too common. Choose a stronger one."]

    # Custom scoring weights
    length_weight = 2 if len(password) >= 12 else 1
    case_weight = 2 if re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) else 1
    digit_weight = 1 if re.search(r'\d', password) else 0
    special_char_weight = 2 if re.search(r'[!@#$%^&*]', password) else 0

    score = length_weight + case_weight + digit_weight + special_char_weight

    # Provide feedback
    if length_weight == 1:
        feedback.append("Use at least 12 characters for a stronger password.")
    if case_weight == 1:
        feedback.append("Include both uppercase and lowercase letters.")
    if digit_weight == 0:
        feedback.append("Include at least one number.")
    if special_char_weight == 0:
        feedback.append("Use at least one special character (!@#$%^&*).")

    # Determine password strength
    if score <= 2:
        return "Weak", score, feedback
    elif 3 <= score <= 5:
        return "Moderate", score, feedback
    elif score >= 6:
        return "Strong", score, []

# Function to generate a strong password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

# Password Expiration Checker
def check_password_expiry(last_updated):
    expiration_days = 90  # Password expires after 90 days
    expiry_date = last_updated + timedelta(days=expiration_days)
    days_left = (expiry_date - datetime.now()).days

    if days_left <= 0:
        return f"⚠️ Your password has expired! Please change it immediately.", "danger"
    elif days_left <= 10:
        return f"⚠️ Your password will expire in {days_left} days. Consider updating it soon.", "warning"
    else:
        return f"✅ Your password is secure. {days_left} days left before expiration.", "success"

# Streamlit UI
st.title("🔒 Password Strength Meter")

# User Input
password = st.text_input("Enter your password:", type="password")

if password:
    strength, score, feedback = check_password_strength(password)
    st.write(f"**Password Strength:** {strength} (Score: {score}/7)")

    # Corrected Feedback Display Logic
    if strength == "Very Weak" or strength == "Weak":
        st.error("Your password is weak! Consider these improvements:")
        for suggestion in feedback:
            st.write(f"- {suggestion}")
    elif strength == "Moderate":
        st.warning("Your password is okay, but could be stronger.")
        for suggestion in feedback:
            st.write(f"- {suggestion}")
    elif strength == "Strong":
        st.success("Great job! Your password is strong. 💪")

# Password Generator
if st.button("Generate a Strong Password"):
    strong_password = generate_password()
    st.write(f"🔑 **Suggested Password:** `{strong_password}`")

# Password Expiration Checker
st.sidebar.header("⏳ Password Expiration Checker")
last_updated = st.sidebar.date_input("📅 Select Last Password Update Date:", datetime.now())

if last_updated:
    expiry_message, status = check_password_expiry(datetime.combine(last_updated, datetime.min.time()))
    
    if status == "danger":
        st.sidebar.error(expiry_message)
    elif status == "warning":
        st.sidebar.warning(expiry_message)
    else:
        st.sidebar.success(expiry_message)
