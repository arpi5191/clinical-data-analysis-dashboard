import streamlit as st
import pandas as pd
import math
import statsmodels.formula.api as smf
from scipy.stats import ranksums
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import os
from google import genai
from google.genai import errors
import time

class CellDataDisplay:
    """
    Display and analyze immune cell data from melanoma PBMC samples.

    Provides interactive tables and charts for:
        - Cell population frequencies per sample
        - Cell population frequencies comparison of responders vs. non-responders
        - Subset summaries by project, response, and gender
    """

    def __init__(self, summary_file_path="output/cell_summary.csv", response_file_path="output/cell_response.csv",
                 samples_per_project_file_path="output/cell_project_summary.csv",
                 subjects_per_response_file_path="output/cell_response_summary.csv",
                 subjects_per_gender_file_path="output/cell_gender_summary.csv"):

        # Read all CSV files
        self.cell_summary_df = pd.read_csv(summary_file_path)
        self.cell_response_df = pd.read_csv(response_file_path)
        self.cell_project_summary_df = pd.read_csv(samples_per_project_file_path)
        self.cell_response_summary_df = pd.read_csv(subjects_per_response_file_path)
        self.cell_gender_summary_df = pd.read_csv(subjects_per_gender_file_path)

    def show_cell_population_summary(self):
        """
            Display an interactive table summarizing immune cell populations per sample.

            For each sample, the table shows:
                - subject: ID of the subject
                - total_count: total number of cells in the sample
                - population: immune cell type
                - count: number of cells of that type in the sample
                - percentage: relative frequency of the cell type within the sample (%)

            Users can filter the table using dropdowns for:
                - Sample
                - Cell population

            The table supports pagination to navigate large datasets.
        """

        # Set the dashboard title, subheader for Part II and markdown text to describe the visualization
        st.title("Clinical Trial Dashboard")
        st.subheader("Immune Cell Population Frequencies for Each Sample")
        st.markdown("""
                    <span style='font-size:20px'>
                    Explore the relative frequencies of immune cell populations across all samples.
                    Use the dropdown menus to filter by sample and/or cell type.
                    Use the "Previous Page" and "Next Page" buttons below to navigate through the table pages.
                    </span>
                    """, unsafe_allow_html=True)


        # Obtain the samples and population types that can be selected on the dashboard using the drop down menus
        samples = ["All"] + sorted(self.cell_summary_df["sample"].unique().tolist())
        populations = ["All"] + sorted(self.cell_summary_df["population"].unique().tolist())

        # Obtain the sample the user selected
        st.markdown("<div style='margin-top:10px; font-size:16px'>Select Sample</div>", unsafe_allow_html=True)
        selected_sample = st.selectbox("Select Sample", samples, label_visibility="collapsed")

        # Obtain the population the user selected
        st.markdown("<div style='margin-top:10px; font-size:16px'>Select Population</div>", unsafe_allow_html=True)
        selected_population = st.selectbox("Select Population", populations, label_visibility="collapsed")

        # Initialize session state to track the last selected filters
        if "last_filters" not in st.session_state:
            st.session_state.last_filters = (None, None)

        # If the currently selected sample or population has changed, reset the page number
        # and update the last selected filters in the session state
        if (selected_sample, selected_population) != st.session_state.last_filters:
            st.session_state.page_number = 0
            st.session_state.last_filters = (selected_sample, selected_population)

        # Filter dataframe based on the sample and population the user selected
        filtered_df = self.cell_summary_df.copy()
        if selected_sample != "All":
            filtered_df = filtered_df[filtered_df["sample"] == selected_sample]
        if selected_population != "All":
            filtered_df = filtered_df[filtered_df["population"] == selected_population]

        # Select a number of rows from the DataFrame to display on each page
        page_size = 10
        if "page_number" not in st.session_state:
            st.session_state.page_number = 0

        # Find the maximum number of pages that could be there in the table display
        max_pages = math.ceil(len(filtered_df) / page_size) - 1

        # Set the page numbers for the previous, current and next page
        prev_page, curr_page, next_page = st.columns([1, 2, 1])
        with prev_page:
            if st.button("Previous Page") and st.session_state.page_number > 0:
                st.session_state.page_number -= 1
        with next_page:
            if st.button("Next Page") and st.session_state.page_number < max_pages:
                st.session_state.page_number += 1

        # Set the start and end page indices
        start_idx = st.session_state.page_number * page_size
        end_idx = start_idx + page_size

        # Filter the DataFrame based on the start and end page index
        page_df = filtered_df.iloc[start_idx:end_idx]

        # Display the DataFrame
        st.dataframe(page_df, width='stretch')

        # Set the caption
        st.caption(f"Showing {start_idx + 1}–{min(end_idx, len(filtered_df))} of {len(filtered_df)} rows "
                   f"(Page {st.session_state.page_number + 1} of {max_pages + 1})")

    def analyze_response_statistics(self):
        """
        Display boxplots comparing relative frequencies of a selected immune cell
        population between responders and non-responders. Shows statistical significance.
        """

        # Set the dashboard title, subheader for Part III and markdown text to describe the visualization
        st.subheader("Response-Based Analysis of Immune Cell Populations")
        st.markdown("""
                    <span style='font-size:20px'>
                    Compare the relative frequencies of immune cell populations in PBMC samples from melanoma
                    patients receiving Miraclib treatment, highlighting differences between responders and non-responders.
                    Use the dropdown menu to select a cell type, check the boxes to filter specific response groups,
                    and hover over any boxplot to view detailed statistical information.
                    </span>
                    """, unsafe_allow_html=True)

        # Obtain the unique cell types and store the cell that the user selected
        cell_types = self.cell_response_df['population'].unique().tolist()

        # Obtain the cell type the user selected
        st.markdown("<div style='margin-top:10px; font-size:16px'>Select Cell Type</div>", unsafe_allow_html=True)
        selected_cell = st.selectbox("Select Cell Type", cell_types, label_visibility="collapsed")

        # Filter the DataFrame based on cell population
        cell_df = self.cell_response_df[self.cell_response_df['population'] == selected_cell]

        # Split the filtered DataFrame based on response
        yes_df = cell_df[cell_df['response'] == 'yes']['percentage']
        no_df = cell_df[cell_df['response'] == 'no']['percentage']

        # Count the number of unique responses per subject identify subjects with mixed responses
        response_counts = cell_df.groupby('subject')['response'].nunique()
        subjects_with_mixed_responses = response_counts[response_counts > 1]

        # Use the Wilcoxon rank-sum test if all subjects contain a single response type,
        # since it assumes independent samples.
        # If subjects have mixed responses, apply a Linear Mixed-Effects Model,
        # which can account for repeated measures within subjects.
        if len(subjects_with_mixed_responses) == 0:
            stat, p_value = ranksums(yes_df, no_df)
        else:
            model = smf.mixedlm("percentage ~ response", cell_df, groups=cell_df["subject"])
            result = model.fit()
            p_value = result.pvalues.get('response[T.yes]', None)

        # Find how significant the cell population differences are based on the p value
        if p_value is not None:
            if p_value < 0.001:
                significance = "Highly Significant"
            if p_value < 0.01:
                significance = "Very Significant"
            elif p_value < 0.05:
                significance = "Significant"
            elif p_value < 0.1:
                significance = "Not Significant"
            else:
                significance = "Very Not Significant"
        else:
            significance = "p-value could not be computed"

        # Display the statistical significance of the cell population difference above the boxplot
        st.markdown(f"""<span style='font-size:19px; font-weight:bold'>{significance} (p-value = {p_value:.4f})
                        </span>""", unsafe_allow_html=True)

        # Set the interactive boxplot using Plotly
        fig = px.box(
            cell_df,
            x="response",
            y="percentage",
            color="response",
            points=False,  # removes individual dots
            hover_data=["subject", "population", "percentage"],
            color_discrete_sequence=px.colors.qualitative.Set2,
            title=f"{selected_cell} Frequency by Response"
        )

        # Update the graph layout
        fig.update_layout(
            width = 600,
            height = 600,
            title=dict(
                text=f"{selected_cell} Frequency by Response",
                font=dict(size=21, color="black", family="Arial"),  # increase size here
                x=0.5,  # center the title
                xanchor='center'
            ),
            xaxis_title=dict(
                text="Response",
                font=dict(size=19, color="black", family="Arial")
            ),
            yaxis_title=dict(
                text="Percentage (%)",
                font=dict(size=19, color="black", family="Arial")
            ),
            xaxis=dict(
                tickfont=dict(size=17, color="black", family="Arial")
            ),
            yaxis=dict(
                tickfont=dict(size=17, color="black", family="Arial")
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(
                title=dict(
                    text=self.cell_response_df.columns[0],
                    font=dict(size=20, color="black", family="Arial")
                ),
                font=dict(size=18, color="black", family="Arial")
            )
        )

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def predict_response_with_llm_summary(self):

        # Set the subheader and markdown text to describe the predictive modeling and clinical summary
        # visualization
        st.subheader("Predicting Melanoma Patient Response to Miraclib")

        st.markdown("""
                    <span style='font-size:20px'>
                    This analysis will predict whether a melanoma patient treated with Miraclib responded \
                    to therapy or not based on the baseline cell counts below.
                    </span>
                    """, unsafe_allow_html=True)

        st.write("")

        # Transform the dataframe from a long format to a wide format for modeling.
        # This groups the data by patient, turning unique cell types into feature columns.
        features_df = self.cell_response_df.pivot(
            index=['subject', 'response'],  # Keep these as tracking/label rows (one row per subject)
            columns='population',           # Pivot unique cell types into individual column headers (features)
            values='total_population_count' # Populate the matrix cells with their respective percentage values
        ).reset_index()                     # Flatten the multi-index so 'subject' and 'response' become standard columns

        # Remove the lingering 'population' name from the columns axis metadata
        # to keep the DataFrame clean and easy to slice by column index later.
        features_df.columns.name = None

        # One-hot encode the categorical clinical response column (located at index 1).
        # drop_first=True avoids multicollinearity; the new binary column is appended to the far right.
        features_df = pd.get_dummies(features_df, columns=[features_df.columns[1]], drop_first=True)

        # Cast the final one-hot encoded boolean column to integer (0/1) in place
        # using assign to cleanly overwrite the column and prevent pandas dtype deprecation warnings.
        features_df = features_df.assign(**{features_df.columns[-1]: features_df.iloc[:, -1].astype(int)})

        # Separate features (X) from the target label (y).
        # Starts at index 1 to drop the patient 'subject' IDs, and goes up to (but excludes) the last column.
        # Targets strictly the newly engineered binary response column at the very end of the dataframe.
        X = features_df.iloc[:, 1:-1]
        y = features_df.iloc[:, -1]

        # Partition data into a 70/30 train/test split.
        # stratify=y preserves the exact class balance of responders across both subsets to prevent sampling bias.
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

        # Initialize XGBoost with conservative, regularized parameters tailored for noisy clinical datasets.
        model = XGBClassifier(
            n_estimators=300,      # Give the model plenty of iterations to learn subtle patterns
            learning_rate=0.02,    # Use a small step size to prevent overshooting the global minimum
            max_depth=1,           # Constrain trees to decision stumps to severely penalize feature interaction noise
            reg_lambda=4.0,        # Apply heavy L2 regularization to smooth out volatile biomarker variances
            subsample=0.8,         # Train on a random 80% subset of patient profiles per tree to boost variance generalization
            random_state=42        # Enforce deterministic results for reproducible metrics
        )

        # Fit the model to the training cohort
        model.fit(X_train, y_train)

        # Generate baseline metrics on the training pool to monitor for overfitting ceilings
        train_predictions = model.predict(X_train)
        train_accuracy = accuracy_score(y_train, train_predictions)
        # print(f"Training Accuracy: {train_accuracy:.4f}")

        # Evaluate generalization performance against completely unseen test patient profiles
        y_pred = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        # print(f"Test Accuracy: {test_accuracy:.4f}")

        # Initialize dictionaries to hold the stratification bounds for each cell population
        lower_thresholds = {}
        higher_thresholds = {}

        # Slices out the middle columns (skipping 'subject' ID at index 0 and the target column at the end)
        # This isolates only the numeric cell counts to prevent text-based math crashes
        numeric_cell_cols = features_df.columns[1:-1]

        for col_name in numeric_cell_cols:
            # Calculate the 33rd percentile (lower third boundary) and convert the
            # native NumPy float64 wrapper into a standard, clean Python float using .item()
            lower_thresholds[col_name] = features_df[col_name].quantile(0.33).item()

            # Calculate the 66th percentile (upper third boundary) and convert to a regular float
            higher_thresholds[col_name] = features_df[col_name].quantile(0.66).item()

        # Print the cleaned dictionaries to the terminal console logs for validation
        print("\n--- Safely Calculated Thresholds ---")
        print("33rd Percentile:", lower_thresholds)
        print("66th Percentile:", higher_thresholds)

        # Extract the 5 unique cell population feature columns from the dataframe
        # This skips the 'subject' ID at index 0 and the target variable column at the very end
        column_names = features_df.columns[1:-1]

        # Initialize an empty dictionary to store the user-submitted numbers
        captured_numbers = {}

        # Render a grouped form so all inputs are bundled and submitted together,
        # preventing premature reruns while the user is still filling in values
        with st.form(key="patient_input_form"):
            st.markdown("#### Enter Patient Cell Counts")
            # Dynamically build one text input per cell population column so the
            # form automatically adapts if the feature set changes
            for col_name in column_names:
                user_entry = st.text_input(label=col_name, value="0.0")
                # Safely parse the typed string to float; fall back to 0.0 on
                # empty or non-numeric input to avoid downstream type errors
                try:
                    captured_numbers[col_name] = float(user_entry)
                except ValueError:
                    captured_numbers[col_name] = 0.0
            # Bundles all inputs and triggers a single rerun on click
            submit_button = st.form_submit_button(label="Enter")

        # On submit, run prediction and persist results in session_state so they
        # survive subsequent reruns without needing the button to still be True
        if submit_button:
            # Wrap the input dict in a single-row DataFrame so column names and
            # order exactly match what the trained model expects
            input_df = pd.DataFrame([captured_numbers])
            # predict_proba returns [[prob_class_0, prob_class_1]]; index [0]
            # unwraps the outer list to give a flat [non-responder, responder] array
            probabilities = model.predict_proba(input_df)[0]
            response_probability = probabilities[1]
            # Threshold at 0.5: above means the model favours a positive response
            if response_probability >= 0.5:
                st.session_state.prediction_label = "Responder"
                st.session_state.confidence_score = response_probability
            else:
                st.session_state.prediction_label = "Non-Responder"
                # For non-responders, confidence is the probability of class 0
                st.session_state.confidence_score = probabilities[0]

        # Render results whenever they exist in session_state — this block runs on
        # every rerun so the output stays visible after subsequent interactions
        if "prediction_label" in st.session_state:
            st.markdown("#### Model Prediction Results")
            st.markdown(
                f'<span style="font-size:20px;">'
                f'Predicted Status: <strong>{st.session_state.prediction_label}</strong>'
                f'</span>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<span style="font-size:20px;">'
                f'Prediction Confidence: <strong>{st.session_state.confidence_score * 100:.2f}%</strong>'
                f'</span>',
                unsafe_allow_html=True
            )

            st.write("") # Extra spacer for clean UI formatting between cell types

            # --- Initialize the Gemini Client ---
            # The client automatically pulls your API key from the GEMINI_API_KEY environment variable.
            # Place this initialization near the top of your script.
            try:
                client = genai.Client()
            except Exception as e:
                # Fixed: Added missing double quote and removed the extra parenthesis
                st.error(f"Failed to initialize Gemini Client. Check your API key. Error: {e}")

            st.markdown("##### Feature Breakdown & Clinical Justifications")
            st.write("") # Quick breathing room spacer

            # Iterate through each isolated numeric cell column to stratify the patient's data
            for cell_type in numeric_cell_cols:

                # Retrieve the pre-calculated 33rd and 66th percentile boundaries for this specific cell
                # population
                lower_bound = lower_thresholds[cell_type]
                higher_bound = higher_thresholds[cell_type]

                # Grab the freshly captured patient input value for this cell type
                cell_count = captured_numbers[cell_type]

                # Initialize an empty string to hold our categorical evaluation tier
                level = ""

                # Classify the input relative to the core clinical cohort distribution
                if cell_count < lower_bound:
                    level = "low"
                elif cell_count > higher_bound:
                    level = "high"
                else:
                    # This catches all values falling cleanly between the lower and higher thresholds
                    level = "medium"

                # --- Display the Status Sentence on the Webpage ---
                # This handles the immediate visual output requested above the justification
                st.markdown(
                    f'<span style="font-size: 19px;">The patient\'s **{cell_type}** count is **{level}**.</span>',
                    unsafe_allow_html=True
                )

                # --- Construct the Hidden Prompt for Gemini ---
                # We keep the text inside triple quotes with the leading 'f' for variable interpolation
                prompt = f"""
                Context: You are analyzing baseline PBMC counts for a melanoma patient treated with Miraclib.
                The model has predicted this patient's status as: {st.session_state.prediction_label}.

                Current Feature: The patient's {cell_type} count is evaluated as {level}.

                Task: Provide a single-sentence clinical explanation or biological context justifying why
                having a {level} level of {cell_type} aligns with or characterizes a patient who is a
                {st.session_state.prediction_label} to this therapy. You MUST include the specific downstream
                consequence that caused this to happen.

                Constraint: Keep the response strictly to one clear sentence. Do not include conversational filler.
                """

                # --- Initialize the Gemini Client Safely ---
                # Fixed: Look up the variable by its configuration NAME, not its value string
                api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

                # Initialize client as None to establish its variable scope upfront.
                # This prevents downstream "referenced before assignment" runtime crashes if initialization
                # fails.
                client = None

                # Verify that a valid API key string was successfully extracted or assigned
                if api_key:
                    try:
                        # Instantiate the official Google GenAI Client explicitly passing the token string
                        client = genai.Client(api_key=api_key)
                    except Exception as e:
                        # Capture and display any authentication or connection errors on the web interface
                        st.error(f"Failed to initialize Gemini Client. Error: {e}")
                else:
                    # Fallback warning if the api_key variable is empty, alerting the user to fix their
                    # configurations
                    st.error("**Missing Gemini API Key!** Please export GEMINI_API_KEY in your terminal or add \
                              it to your environment configurations.")

                # Wrap the API call in a spinner so the webpage remains smooth while generating
                with st.spinner(f"Generating clinical insight for {cell_type}..."):
                    # Explicitly check if the client was successfully assigned above
                    if client is not None:
                        try:
                            # Call the generation model using the official v1 SDK format
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt,
                            )
                            # Extract the cleaned text result from the API response object
                            justification_text = response.text.strip()

                        # Handle specific exception scenarios arising during the API call lifecycle
                        except errors.APIError as api_err:
                            # Gracefully capture explicit upstream Google GenAI infrastructure or quota errors
                            justification_text = f"Unable to generate insight due to an API error: {api_err.message}"
                        except Exception as generic_err:
                            # Catch-all backup for unexpected runtime failures
                            justification_text = f"An unexpected error occurred: {str(generic_err)}"
                    else:
                        # Fallback assignment executed if the SDK client object was never instantiated
                        # successfully
                        justification_text = (
                            "Clinical interpretation unavailable: Gemini SDK client is uninitialized."
                        )

                # Display the resulting justification sentence right below the feature line
                st.markdown(
                    f'<span style="color: black; font-size: 18px;">💡 {justification_text}</span>',
                    unsafe_allow_html=True
                )

                st.write("") # Add vertical whitespace padding before moving to the next cell type

                # This prevents hitting Google's rate-limiting/burst-capacity thresholds.
                time.sleep(2)

    def explore_baseline_subsets(self):
        """
        Display interactive bar charts.

        This method visualizes subsets of melanoma PBMC baseline samples from
        patients treated with Miraclib. Three charts are displayed:
            1. Number of samples per project.
            2. Number of subjects who are responders vs. non-responders.
            3. Number of subjects by sex (male/female).
        """

        # Set the dashboard title, subheader for Part IV and markdown text to describe the visualization
        st.subheader("Data Subset Analysis")
        st.markdown("""
                    <span style='font-size:20px'>
                    Explore subsets of melanoma PBMC baseline samples from patients treated with Miraclib to understand
                    early treatment effects. Use the checkboxes below to select which summaries you’d like to display in the
                    bar charts. Hover over any bar to view the exact counts.
                    </span>
                    """, unsafe_allow_html=True)

        # Put all the dataframes and graph titles in a list
        dataframes = [(self.cell_project_summary_df, "Samples per Project"),
                      (self.cell_response_summary_df, "Subjects by Response"),
                      (self.cell_gender_summary_df, "Subjects by Gender")
                     ]

        # Iterate through each dataframe and graph title
        for df, title in dataframes:

            # Set the interactive boxplot using Plotly
            fig = px.bar(
                df,
                x=df.columns[0],
                y=df.columns[1],
                color=df.columns[0],
                color_continuous_scale="Viridis",
                title=title
            )

            # Update the graph layout
            fig.update_layout(
                width = 600,
                height = 600,
                title=dict(
                    text=title,
                    font=dict(size=21, color="black", family="Arial"),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis_title=dict(
                    text=df.columns[0].capitalize(),
                    font=dict(size=19, color="black", family="Arial")
                ),
                yaxis_title=dict(
                    text=df.columns[1].capitalize(),
                    font=dict(size=19, color="black", family="Arial")
                ),
                xaxis=dict(
                    tickfont=dict(size=17, color="black", family="Arial")
                ),
                yaxis=dict(
                    tickfont=dict(size=17, color="black", family="Arial")
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    title=dict(
                        text=df.columns[0],
                        font=dict(size=20, color="black", family="Arial")
                    ),
                    font=dict(size=18, color="black", family="Arial")
                )
            )

            # Display in streamlit
            st.plotly_chart(fig, use_container_width=True)

def main():
    # Create an instance of CellResponseAnalysis
    responder = CellDataDisplay()

    # Compute the cell population frequencies for each sample
    responder.show_cell_population_summary()

    # Compute the cell population frequencies for melanoma patients based on response
    responder.analyze_response_statistics()

    # Extract data, train Random Forest classifier, predict response via live inputs, and generate an LLM summary
    responder.predict_response_with_llm_summary()

    # Compute the following subsets for melanoma patients: number of samples in each project,
    # number of subjects with yes/no response, number of subjects who are M/F
    responder.explore_baseline_subsets()

if __name__ == "__main__":
    main()
