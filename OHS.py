import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
# Set the page configuration. This must be the first Streamlit command.
st.set_page_config(
    page_title="OHS Hazard Reporting App",
    page_icon="⚠️",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- FILE PATHS & CONSTANTS ---
# Define paths for data storage. This makes the code cleaner and easier to manage.
LOGO_PATH = 'fmf_logo.png' # IMPORTANT: Replace with the actual path to your company logo.
UPLOADS_DIR = 'uploads'
REPORTS_CSV = 'hazard_reports.csv'

# --- HELPER FUNCTIONS ---

def initialize_storage():
    """
    Creates the necessary directory for uploads and the CSV file for reports
    if they don't already exist. This prevents errors on the first run.
    """
    # Create the directory for uploaded images
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

    # Create the CSV file with headers if it doesn't exist
    if not os.path.exists(REPORTS_CSV):
        df = pd.DataFrame(columns=[
            'ReportID', 'Timestamp', 'EmployeeID', 'Entity',
            'SpecificArea', 'Urgency', 'Description', 'ImagePath'
        ])
        df.to_csv(REPORTS_CSV, index=False)

def save_report(report_data):
    """
    Appends a new hazard report to the central CSV file.
    Args:
        report_data (dict): A dictionary containing the hazard report details.
    """
    try:
        # Convert dictionary to a DataFrame
        df = pd.DataFrame([report_data])
        # Append to the CSV file without writing the header again
        df.to_csv(REPORTS_CSV, mode='a', header=False, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving report: {e}")
        return False

def save_image(uploaded_file, report_id):
    """
    Saves the uploaded image to the 'uploads' directory with a unique filename.
    Args:
        uploaded_file: The file object from st.file_uploader.
        report_id (str): The unique ID of the report to link the image.
    Returns:
        str: The path to the saved image, or None if no file was uploaded.
    """
    if uploaded_file is not None:
        # Get the file extension (e.g., .png, .jpg)
        file_extension = os.path.splitext(uploaded_file.name)[1]
        # Create a unique filename to prevent overwrites
        image_filename = f"{report_id}{file_extension}"
        image_path = os.path.join(UPLOADS_DIR, image_filename)

        # Write the file to the uploads directory
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return image_path
    return None

# --- MAIN APPLICATION LOGIC ---

def main():
    """
    The main function that runs the Streamlit application.
    """
    # Run initialization to ensure storage is ready
    initialize_storage()

    # --- HEADER ---
    # Display the company logo if it exists, otherwise show a placeholder.
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=200)
    else:
        st.warning(f"Logo not found at '{LOGO_PATH}'. Please update the path.")

    st.title("OHS Hazard Reporting App")
    st.markdown("Use this form to report any potential hazards or safety concerns you observe.")

    # --- REPORTING FORM ---
    # Using st.form ensures all widgets are submitted at once.
    with st.form("hazard_report_form", clear_on_submit=True):
        st.header("Report Details")

        # Input fields for the report
        employee_id = st.text_input("Your Employee ID (Optional)", help="Providing your ID helps us follow up if needed.")
        
        entity = st.selectbox(
            "Location / Entity",
            ["BCF (Biscuit Company)", "Flour Mill", "Feed Mill", "Corporate Office", "Warehouse", "Other"],
            index=0
        )

        specific_area = st.text_input("Specific Area / Machine", placeholder="e.g., Line 3 Wrapper, Silo 5, Loading Bay", max_chars=100)
        
        description = st.text_area(
            "Hazard Description",
            placeholder="Please describe the hazard in detail. What did you see? What is the potential danger?",
            height=150
        )
        
        urgency = st.selectbox(
            "Urgency Level",
            ["🔴 Immediate Danger - Stop Work Required", "🟡 Needs Attention - Potential for Harm", "🟢 General Improvement / Observation"],
            index=1
        )
        
        uploaded_photo = st.file_uploader(
            "Upload a Photo (Recommended)",
            type=['png', 'jpg', 'jpeg']
        )

        # Submit button for the form
        submitted = st.form_submit_button("Submit Hazard Report")

    # --- FORM SUBMISSION LOGIC ---
    # This block runs only when the user clicks the submit button.
    if submitted:
        # Basic validation: ensure critical fields are filled.
        if not description or not specific_area:
            st.error("Please fill in both the 'Specific Area' and 'Hazard Description' fields.")
        else:
            # Generate a unique report ID using the current timestamp
            timestamp = datetime.now()
            report_id = timestamp.strftime("HAZ%Y%m%d-%H%M%S")

            # Save the uploaded image and get its path
            image_path = save_image(uploaded_photo, report_id)

            # Compile all data into a dictionary
            report_data = {
                'ReportID': report_id,
                'Timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'EmployeeID': employee_id if employee_id else 'Anonymous',
                'Entity': entity,
                'SpecificArea': specific_area,
                'Urgency': urgency.split(' ')[0], # Extracts just the color/symbol
                'Description': description,
                'ImagePath': image_path if image_path else 'N/A'
            }

            # Attempt to save the report data to the CSV
            if save_report(report_data):
                st.success(f"✅ Thank you! Your report has been submitted successfully.")
                st.info(f"Your Report ID is: **{report_id}**")
                st.balloons()
            else:
                st.error("Failed to save the report. Please contact the OHS department directly.")


# --- SCRIPT EXECUTION ---
if __name__ == "__main__":
    main()
