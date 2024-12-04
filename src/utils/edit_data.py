import streamlit as st
import json

from modules.compute_coordinates import ComputeCoordinates
from utils.map_utils import MapUtils
from streamlit_folium import st_folium
from utils.convert_string_to_float import to_float


def edit_data(data):
    # Variables to control pagination
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    # Pagination Logic
    def navigate(direction):
        """Navigates through pages based on direction."""
        if direction == "next" and st.session_state.current_page < len(data) - 1:
            st.session_state.current_page += 1
        elif direction == "prev" and st.session_state.current_page > 0:
            st.session_state.current_page -= 1

    # Display Current Page Data
    current_data = data[st.session_state.current_page]
    with st.sidebar:
        st.subheader(
            f"Editing Data for Page {st.session_state.current_page + 1} of {len(data)}"
        )

    # Pagination Controls
    with st.sidebar:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous", on_click=navigate, args=("prev",)):
                pass

        with col2:
            if st.button("Next", on_click=navigate, args=("next",)):
                pass

    edit_data_func(current_data, st.session_state.current_page)


def edit_data_func(data, index: int = 0):
    # Display title
    # st.title("Plot Data Editor")

    # Plot Information Section
    st.subheader("Edit Plot Information")
    cols = st.columns(3)
    # Group 1: General Info
    with cols[0]:
        data["plot_info"]["plot_number"] = st.text_input(
            "Plot Number", data["plot_info"]["plot_number"] or ""
        )
        data["plot_info"]["area"] = st.number_input(
            "Area", value=data["plot_info"]["area"]
        )
        data["plot_info"]["metric"] = st.text_input(
            "Metric", data["plot_info"]["metric"]
        )
        data["plot_info"]["date"] = st.text_input("Date", data["plot_info"]["date"])

    # Group 2: Location Details
    with cols[1]:
        data["plot_info"]["locality"] = st.text_input(
            "Locality", data["plot_info"]["locality"]
        )
        data["plot_info"]["district"] = st.text_input(
            "District", data["plot_info"]["district"]
        )
        data["plot_info"]["region"] = st.text_input(
            "Region", data["plot_info"]["region"]
        )

    # Group 3: Ownership & Surveyor Info
    with cols[2]:
        data["plot_info"]["owners"] = st.text_area(
            "Owners (comma-separated)",
            ", ".join(data["plot_info"]["owners"]),
        ).split(", ")
        data["plot_info"]["surveyors_name"] = st.text_input(
            "Surveyor's Name", data["plot_info"]["surveyors_name"]
        )
        data["plot_info"]["surveyors_location"] = st.text_input(
            "Surveyor's Location", data["plot_info"]["surveyors_location"] or ""
        )
        data["plot_info"]["surveyors_reg_number"] = st.text_input(
            "Surveyor's Registration Number",
            data["plot_info"]["surveyors_reg_number"],
        )

    # Survey Points Section
    st.subheader("Edit Survey Points")
    for i, point in enumerate(data["survey_points"]):
        st.markdown(f"**Survey Point {i+1}: {point['point_name']}**")
        cols = st.columns(3)
        with cols[0]:
            point["point_name"] = st.text_input(
                f"Point Name {i+1}", point["point_name"]
            )
        with cols[1]:
            point["original_coords"]["x"] = st.number_input(
                f"X Coordinate {i+1}", value=point["original_coords"]["x"]
            )
        with cols[2]:
            point["original_coords"]["y"] = st.number_input(
                f"Y Coordinate {i+1}", value=point["original_coords"]["y"]
            )

    # Boundary Points Section
    st.subheader("Edit Boundary Points")
    for i, boundary in enumerate(data["boundary_points"]):
        st.markdown(f"**Boundary Point {i+1}: {boundary['point']}**")
        cols = st.columns(2)
        with cols[0]:
            boundary["northing"] = st.number_input(
                f"Northing {i+1}", value=boundary["northing"]
            )
        with cols[1]:
            boundary["easting"] = st.number_input(
                f"Easting {i+1}", value=boundary["easting"]
            )

    # Save Functionality
    # if st.button("Save Changes"):
    compute_corrdinates = ComputeCoordinates()
    new_data = compute_corrdinates.process_data(data)
    st.session_state["processed_docs"][index] = new_data

    with st.expander(label="Updated Data", expanded=False):
        markdown_content = format_to_markdown(data)
        st.markdown(markdown_content)

    plot_data(data=[data])


def format_to_markdown(data):
    def format_to_markdown_grid(data):
        """
        Formats the selected edited data into a Markdown table-based grid.

        Args:
            data (dict): The edited data dictionary.
        Returns:
            str: A Markdown-formatted string with tables.
        """
        markdown = []

        # Plot Information Table
        markdown.append("## Plot Information\n")
        plot_info = data.get("plot_info", {})
        markdown.append("| Field                     | Value                        |")
        markdown.append("|---------------------------|------------------------------|")
        markdown.append(
            f"| Plot Number               | {plot_info.get('plot_number', 'N/A')} |"
        )
        markdown.append(
            f"| Area                      | {plot_info.get('area', 'N/A')} {plot_info.get('metric', 'N/A')} |"
        )
        markdown.append(
            f"| Locality                  | {plot_info.get('locality', 'N/A')} |"
        )
        markdown.append(
            f"| District                  | {plot_info.get('district', 'N/A')} |"
        )
        markdown.append(
            f"| Region                    | {plot_info.get('region', 'N/A')} |"
        )
        markdown.append(
            f"| Owners                    | {', '.join(plot_info.get('owners', []))} |"
        )
        markdown.append(
            f"| Date                      | {plot_info.get('date', 'N/A')} |"
        )
        markdown.append(
            f"| Scale                     | {plot_info.get('scale', 'N/A')} |"
        )
        markdown.append(
            f"| Other Location Details    | {plot_info.get('other_location_details', 'N/A')} |"
        )
        markdown.append(
            f"| Surveyor's Name           | {plot_info.get('surveyors_name', 'N/A')} |"
        )
        markdown.append(
            f"| Surveyor's Location       | {plot_info.get('surveyors_location', 'N/A')} |"
        )
        markdown.append(
            f"| Surveyor's Registration Number | {plot_info.get('surveyors_reg_number', 'N/A')} |\n"
        )

        # Survey Points Table
        markdown.append("## Survey Points\n")
        markdown.append(
            "| Point Name               | X Coordinate   | Y Coordinate   |"
        )
        markdown.append(
            "|--------------------------|----------------|----------------|"
        )
        for point in data.get("survey_points", []):
            original_coords = point.get("original_coords", {})
            markdown.append(
                f"| {point.get('point_name', 'N/A')} "
                f"| {original_coords.get('x', 'N/A')} "
                f"| {original_coords.get('y', 'N/A')} |"
            )

        # Boundary Points Table
        markdown.append("\n## Boundary Points\n")
        markdown.append(
            "| Point Name               | Northing       | Easting        | Latitude       | Longitude       |"
        )
        markdown.append(
            "|--------------------------|----------------|----------------|----------------|-----------------|"
        )
        for boundary in data.get("boundary_points", []):
            markdown.append(
                f"| {boundary.get('point', 'N/A')} "
                f"| {boundary.get('northing', 'N/A')} "
                f"| {boundary.get('easting', 'N/A')} "
                f"| {boundary.get('latitude', 'N/A')} "
                f"| {boundary.get('longitude', 'N/A')} |"
            )

        return "\n".join(markdown)

    return format_to_markdown_grid(data)


def plot_data(data):
    if data:
        m = MapUtils(data)
        m = m.create_map()

        if m:
            # Display Folium map
            output = st_folium(m, width=None, height=600)
