import streamlit as st
import json

sample_prompt_result = """result = {
                    "owners": [
                        "TRANSPORT RESEARCH & EDUCATION CENTRE, KUMASI (TRECK)"
                    ],
                    "plot_number": "15B",
                    "date": "02/02/2022",
                    "area": "1.78",
                    "metric": "Acres",
                    "scale": "1:2500",
                    "locality": "Research Hills",
                    "district": "OFORIKROM",
                    "region": "ASHANTI",
                    "other_location_details": None,
                    "surveyors_name": "DR. A. ARKO-ADJEI",
                    "surveyors_location": "P. O. BOX UP 1703 KNUST-KUMASI",
                    "surveyors_reg_number": "316",
                    "regional_number": None,
                    "reference_number": None,
                    "site_plan_data": {
                        "plan_data": {
                        "from": [
                            "KNUST.TREK.10/2021/1",
                            "KNUST.TREK.10/2021/2",
                            "KNUST.TREK.10/2021/3",
                            "KNUST.TREK.10/2021/4",
                            "KNUST.TREK.10/2021/5",
                            "KNUST.CEPB.10/2021/2",
                            "KNUST.CEPB.10/2021/3",
                            "SGA.CORS 2020 3"
                        ],
                        "x_coords": [
                            "724125.686",
                            "724103.844",
                            "724089.960",
                            "724057.009",
                            "724197.311",
                            "724330.685",
                            "724294.927",
                            "732285.928"

                        ],
                        "y_coords": [
                            "695158.748",
                            "695149.339",
                            "695129.526",
                            "694842.085",
                            "694820.230",
                            "695135.853",
                            "694811.094",
                            "673148.096"
                        ],
                        "bearing": [],
                        "distance": [],
                        "to": []
                        },
                        "north_easterns": {
                        "norths": [
                            "694500",
                            "695500"
                        ],
                        "easterns": [
                            "723500",
                            "724500"
                        ]
                        }
                    }
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
