import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
from src.utils import authenticate, load_logo

# Path to assets
BANNER_PATH = "StratAceBanner_Logo.png"
LOGO_PATH = "Campaign-Prioritizer_Logo.png"
BOTTOM_PATH = "StratAceBottom_Logo.png"

# Streamlit app
def main():

    # User session for login state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "tasks" not in st.session_state:
        st.session_state.tasks = []

    if not st.session_state.logged_in:
        st.image(BANNER_PATH,use_container_width=False)
        st.image(LOGO_PATH,width=225)
        st.title("Login to Prioritizer App")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.success("Login successful!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password.")
    else:
        # Display the logo on the main page
        st.image(BANNER_PATH,use_container_width=False)
        st.image(LOGO_PATH, width=225)
        # If logged in, display the App
        st.title("Prioritizer Tool")
        st.subheader("Create a prioritized list of precincts optimized for your campaign's strategy.")
        st.write("This is a product of Strategy Ace LLC")
        st.write("version: BETAv0.1")
        st.divider()

        # Dropdown for selecting the political party
        st.header("Select the Party to optimize for")
        party_choice = st.selectbox("Select Political Party for Favorability Score", ["Democrat","Republican", "NPA"])
        st.divider()

        st.header("Set Weights to Match Your Campaign's Strategy")
        st.write("Use the sliders below to adjust each parameter weight. Please note that the total for all weights needs to equal 1.0.")
        # Inputs for weights
        total_registered_weight = st.slider("Weight for Total Registered Voters", min_value=0.0, max_value=1.0, step=0.05)
        party_favorability_weight = st.slider("Weight for Party Favorability", min_value=0.0, max_value=1.0, step=0.05)
        swing_voters_weight = st.slider("Weight for Swing Voters", min_value=0.0, max_value=1.0, step=0.05)
        party_turnout_weight = st.slider("Weight for Party Turnout", min_value=0.0, max_value=1.0, step=0.05)

        # Calculate total weight
        total_weight = (total_registered_weight + party_favorability_weight +
                swing_voters_weight + party_turnout_weight)

        # Display total weight
        st.subheader(f"Current Total Weight: {total_weight:.2f}")
        if total_weight != 0.0 and total_weight != 1.0:
            st.warning("The sum of all weights must equal 1.0. Please adjust.")
        elif total_weight == 1.0:
            st.success("The sum of all weights is 1.0.")
        else:
            st.error("The sum of all weights must equal 1.0. Please adjust.")
        st.divider()

        # Select data source
        st.subheader("Select CSV File Source")
        data_source = st.radio("Choose the source of your CSV file:", ["Local file upload", "Google Drive path"])

        # Initialize DataFrame
        newdf = pd.DataFrame()
        origdf = None

        if data_source == "Local file upload":
            # File upload
            uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
            if uploaded_file is not None:
                origdf = pd.read_csv(uploaded_file)
        elif data_source == "Google Drive path":
            # Text input for Google Drive file path
            drive_path = st.text_input("Enter the full path to your CSV file in Google Drive:")
            if drive_path:
                if os.path.exists(drive_path):  # Check if the file exists
                    origdf = pd.read_csv(drive_path)
                else:
                    st.error("The specified path does not exist. Please check the path and try again.")

        # Perform scoring if a valid DataFrame has been loaded and weights sum to 1.0
        if origdf is not None and total_weight == 1.0:
            # Ensure required columns are present in the CSV file
            required_columns = ["PRECINCT", "TOTAL REGISTERED", "PCT DEM", "PCT REP", "PCT NPA", "PCT OTHER", "DEM TURNOUT", "REP TURNOUT", "NPA TURNOUT"]
            score_columns = ["TOTAL REGISTERED", "PCT DEM", "PCT REP", "PCT NPA", "PCT OTHER", "DEM TURNOUT", "REP TURNOUT", "NPA TURNOUT"]
            if all(col in origdf.columns for col in required_columns):

                # Normalize each parameter column to a range of 0-1
                scaler = MinMaxScaler()

                newdf[score_columns] = scaler.fit_transform(origdf[score_columns])

                # Set the party favorability column based on the selected party
                if party_choice == "Democrat":
                    favorability_column = "PCT DEM"
                    turnout_column = "DEM TURNOUT"
                    newdf["PARTY TOTAL"] = np.ceil((origdf["TOTAL REGISTERED"]*origdf["PCT DEM"]))
                elif party_choice == "Republican":
                    favorability_column = "PCT REP"
                    turnout_column = "REP TURNOUT"
                    newdf["PARTY TOTAL"] = np.ceil((origdf["TOTAL REGISTERED"]*origdf["PCT REP"]))
                elif party_choice == "NPA":
                    favorability_column = "PCT NPA"
                    turnout_column = "NPA TURNOUT"
                    newdf["PARTY TOTAL"] = np.ceil((origdf["TOTAL REGISTERED"]*origdf["PCT NPA"]))
                else:
                    st.error("Invalid party choice. Please select a valid party.")
                    return


                # Calculate weighted score for each precinct
                newdf['Score'] = (
                    total_registered_weight * newdf["TOTAL REGISTERED"] +
                    party_favorability_weight * newdf[favorability_column] +
                    swing_voters_weight * newdf["PCT NPA"] +
                    party_turnout_weight * newdf[turnout_column]
                )

                # Sort by score in descending order
                sorted_df = newdf.sort_values(by="Score", ascending=False)

                # Display sorted DataFrame
                st.divider()
                st.header("Prioritized Precincts List")
                numprecinct = st.number_input("How many Precincts would you like to focus on:",min_value=0, value=5)
                st.subheader(" ")
                st.write("Here is your full list of precincts in order from highest to lowest score:")
                st.write(sorted_df)
                st.write(f"Here are the stats for the top {numprecinct} Precincts:")
                PrioritRegNum = origdf["TOTAL REGISTERED"].head(numprecinct).sum()
                totalparty = newdf["PARTY TOTAL"].head(numprecinct).sum()
                st.metric("Total Registered Voters", PrioritRegNum)
                st.metric("Total Party Voters", totalparty)
                st.divider()

            else:
                st.error(f"The CSV file must contain the following columns: {required_columns}")
        else:
            st.info("Please upload or specify a valid CSV file and ensure the weights sum to 1.0.")

        
if __name__ == "__main__":
    main()
