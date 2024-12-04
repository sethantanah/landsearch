import streamlit as st
import json

sample_prompt_result = """{
                            "owners": ["MRS NAA AYELEY BROWN"],
                            "plot_number": None,
                            "date": "22-09-2021",
                            "area": "0.16",
                            "metric": "Acres",
                            "scale": "1:2500",
                            "locality": "KATAMANSO",
                            "district": "K.K.M.A",
                            "region": "GREATER ACCRA",
                            "other_location_details": "Shewn Edged Pink",
                            "surveyors_name": "EDWIN ADDO-TAWIAH",
                            "surveyors_location": None,
                            "surveyors_reg_number": "388",
                            "regional_number": None,
                            "reference_number": None,
                            "site_plan_data": {
                                "plan_data": {
                                    "from": [
                                        "SGGA. F0258/21/1",
                                        "SGGA. F0258/21/2",
                                        "SGGA. F0258/21/3",
                                        "SGGA. F0258/21/4",
                                        "SGGA. EX/TD/19/2",
                                    ],
                                    "x_coords": [
                                        "402081.98",
                                        "402173.48",
                                        "402202.49",
                                        "402110.97",
                                        "358320.50",
                                    ],
                                    "y_coords": [
                                        "1227948.15",
                                        "1227904.04",
                                        "1227967.77",
                                        "1228010.97",
                                        "1260681.89",
                                    ],
                                    "bearing": ["334°16'", "065°31'", "154°44'", "245°13′", "323°12"],
                                    "distance": ["101.6", "70.0", "101.2", "69.2", "54,649.5"],
                                    "to": [
                                        "SGGA. F0258/21/2",
                                        "SGGA. F0258/21/3",
                                        "SGGA. F0258/21/4",
                                        "SGGA. F0258/21/4",
                                        "SGGA. F0258/21/1",
                                    ],
                                    "ref": [True, True, True, True, False],
                                },
                                "north_easterns": {
                                    "norths": ["402500", "402000", "401500"],
                                    "easterns": ["1227500", "1228000", "1228500"],
                                },
                            },
                        }
                """
# Sample input data
data = [
    {
        "plot_info": {
            "plot_number": None,
            "area": 0.16,
            "metric": "Acres",
            "locality": "KATAMANSO",
            "district": "K.K.M.A",
            "region": "GREATER ACCRA",
            "owners": ["MRS NAA AYELEY BROWN"],
            "date": "22-09-2021",
            "scale": "1:2500",
            "other_location_details": "- Shewn Edged Pink -",
            "surveyors_name": "EDWIN ADDO-TAWIAH",
            "surveyors_location": None,
            "surveyors_reg_number": "388",
            "regional_number": None,
            "reference_number": None,
        },
        "survey_points": [
            {
                "point_name": "SGGA. F0258/21/1",
                "original_coords": {
                    "x": 724125.686,
                    "y": 695158.748,
                    "ref_point": False,
                },
                "converted_coords": {
                    "latitude": 5.777300184321659,
                    "longitude": -0.09704742419819078,
                    "ref_point": False,
                },
                "next_point": {
                    "name": "SGGA. F0258/21/2",
                    "bearing": "334°16'",
                    "bearing_decimal": 334.26666666666665,
                    "distance": [101.6],
                },
            },
            {
                "point_name": "SGGA. F0258/21/2",
                "original_coords": {
                    "x": 724103.844,
                    "y": 695149.339,
                    "ref_point": False,
                },
                "converted_coords": {
                    "latitude": 5.777552603198304,
                    "longitude": -0.097168428017529,
                    "ref_point": False,
                },
                "next_point": {
                    "name": "SGGA. F0258/21/3",
                    "bearing": "065°31'",
                    "bearing_decimal": 65.51666666666667,
                    "distance": [70],
                },
            },
            {
                "point_name": "SGGA. F0258/21/3",
                "original_coords": {
                    "x": 724089.960,
                    "y": 695129.526,
                    "ref_point": False,
                },
                "converted_coords": {
                    "latitude": 5.777632292682959,
                    "longitude": -0.0969928984380644,
                    "ref_point": False,
                },
                "next_point": {
                    "name": "SGGA. F0258/21/4",
                    "bearing": "154°44'",
                    "bearing_decimal": 154.73333333333332,
                    "distance": [101.2],
                },
            },
            {
                "point_name": "SGGA. F0258/21/4",
                "original_coords": {
                    "x": 724057.009,
                    "y": 694842.085,
                    "ref_point": False,
                },
                "converted_coords": {
                    "latitude": 5.77737982262644,
                    "longitude": -0.09687439935416571,
                    "ref_point": False,
                },
                "next_point": {
                    "name": "SGGA. F0258/21/4",
                    "bearing": "245°13′",
                    "bearing_decimal": 245.21666666666667,
                    "distance": [69.2],
                },
            },
            {
                "point_name": "SGGA. EX/TD/19/2",
                "original_coords": {"x": 358320.5, "y": 1260681.89, "ref_point": False},
                "converted_coords": {
                    "latitude": 5.656521316006493,
                    "longitude": -0.00716395661312132,
                    "ref_point": False,
                },
                "next_point": {
                    "name": "SGGA. F0258/21/1",
                    "bearing": "323°12",
                    "bearing_decimal": 323.2,
                    "distance": [54],
                },
            },
        ],
        "boundary_points": [
            {
                "point": "Boundary_1",
                "northing": 402500,
                "easting": 1227500,
                "latitude": 5.77845444,
                "longitude": -0.09827904,
            },
            {
                "point": "Boundary_2",
                "northing": 402000,
                "easting": 1228000,
                "latitude": 5.77707397,
                "longitude": -0.09690508,
            },
            {
                "point": "Boundary_3",
                "northing": 401500,
                "easting": 1228500,
                "latitude": 5.7756935,
                "longitude": -0.09553112,
            },
        ],
        "point_list": [
            {
                "latitude": 5.777300184321659,
                "longitude": -0.09704742419819078,
                "ref_point": False,
            },
            {
                "latitude": 5.777632292682959,
                "longitude": -0.0969928984380644,
                "ref_point": False,
            },
            {
                "latitude": 5.77737982262644,
                "longitude": -0.09687439935416571,
                "ref_point": False,
            },
            {
                "latitude": 5.656521316006493,
                "longitude": -0.00716395661312132,
                "ref_point": False,
            },
            {
                "latitude": 5.777552603198304,
                "longitude": -0.097168428017529,
                "ref_point": False,
            },
        ],
    }
]


st.session_state["processed_docs"] = data
