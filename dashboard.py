import streamlit as st
import pandas as pd
import math
import statsmodels.formula.api as smf
from scipy.stats import ranksums
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

class CellDataDisplay:
    """
    """

    def __init__(self, summary_file_path="cell_summary.csv", response_file_path = "cell_response.csv"):
        # Read all CSV files
        self.cell_summary_df = pd.read_csv(summary_file_path)
        self.cell_response_df = pd.read_csv(response_file_path)

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
        st.subheader("Part II: Immune Cell Population Frequencies for Each Sample")
        st.markdown("""
        <span style='font-size:20px'>
        Explore the relative frequencies of each immune cell population across all samples.
        Use the dropdown menus to filter by sample or cell type.
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
        st.subheader("Part III: Response-Based Analysis of Immune Cell Populations")
        st.markdown("""
        <span style='font-size:20px'>
        Compare the relative frequencies of immune cell populations between responders and non-responders.
        Select a cell type from the dropdown to view its distribution, along with statistical significance.
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

        # Interactive boxplot using Plotly
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

        # Improve layout aesthetics
        fig.update_layout(
            title_font=dict(size=20, family="Arial", color="black"),
            title_x=0.0,
            xaxis_title="Response",
            yaxis_title="Percentage (%)",
            xaxis=dict(
                title_font=dict(size=18, family="Arial", color="black"),
                tickfont=dict(size=16, family="Arial", color="black")
            ),
            yaxis=dict(
                title_font=dict(size=18, family="Arial", color="black"),
                tickfont=dict(size=14, family="Arial", color="black")
            ),
            hoverlabel=dict(font_size=14),
            plot_bgcolor="white",
            width=800,
            height=600,
        )

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def explore_baseline_subsets(self):
        pass

def main():
    # Create an instance of CellResponseAnalysis
    responder = CellDataDisplay()

    # Compute the cell population frequencies for each sample
    responder.show_cell_population_summary()

    # Compute the cell population frequencies for melanoma patients based on response
    responder.analyze_response_statistics()

if __name__ == "__main__":
    main()
