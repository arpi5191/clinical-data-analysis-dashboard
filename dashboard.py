import streamlit as st
import pandas as pd
import math

class CellDataDisplay:
    """
    """

    def __init__(self, summary_file_path="cell_summary.csv"):
        self.cell_summary_df = pd.read_csv(summary_file_path)

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
        st.subheader("Part II: Cell Population Frequencies for Each Sample")
        st.markdown("""
        <span style='font-size:25px'>
        Cell Population Frequency Table
        </span>
        """, unsafe_allow_html=True)

        # Obtain the samples and population types that can be selected on the dashboard using the drop down menus
        samples = ["All"] + sorted(self.cell_summary_df["sample"].unique().tolist())
        populations = ["All"] + sorted(self.cell_summary_df["population"].unique().tolist())

        # Obtain the sample and population the user selected
        selected_sample = st.selectbox("Select Sample", samples)
        selected_population = st.selectbox("Select Population", populations)

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

        # Display the DataFrame and set the caption
        st.dataframe(page_df, use_container_width=True)
        st.caption(f"Showing {start_idx + 1}–{min(end_idx, len(filtered_df))} of {len(filtered_df)} rows "
                   f"(Page {st.session_state.page_number + 1} of {max_pages + 1})")

    def analyze_response_statistics(self):
        pass

    def explore_baseline_subsets(self):
        pass

def main():
    # Create an instance of CellResponseAnalysis
    responder = CellDataDisplay()

    # Compute the cell population frequencies for each sample
    responder.show_cell_population_summary()

if __name__ == "__main__":
    main()
