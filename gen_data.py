import json
from datetime import datetime, timedelta
import random

def generate_mock_data(num_plots=10):
    """Generate mock land registry data"""
    
    # Sample locations in Ghana with approximate coordinates
    locations = [
        {"name": "Accra", "base_lat": 5.556, "base_lon": -0.1969},
        {"name": "Kumasi", "base_lat": 6.6885, "base_lon": -1.6244},
        {"name": "Tamale", "base_lat": 9.4075, "base_lon": -0.8533},
        {"name": "Cape Coast", "base_lat": 5.1315, "base_lon": -1.2795},
        {"name": "Tema", "base_lat": 5.6698, "base_lon": -0.0167}
    ]
    
    # Sample owner names and streets
    first_names = ["Kwame", "Ama", "Kofi", "Efua", "Kwesi", "Abena", "Yaw", "Akua", "Kojo", "Esi"]
    last_names = ["Mensah", "Owusu", "Addo", "Sarpong", "Osei", "Boateng", "Asante", "Appiah", "Amoah", "Wiredu"]
    streets = ["High Street", "Market Road", "Independence Ave", "Liberation Road", "Beach Road", 
               "Castle Road", "Ring Road", "Harbor Road", "University Road", "Airport Road"]
    
    # Land types
    land_types = ["Residential", "Commercial", "Industrial", "Agricultural", "Mixed Use"]
    
    plots = []
    
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_plots):
        # Select random location
        location = random.choice(locations)
        
        # Generate random coordinates near the base location
        lat_offset = random.uniform(-0.01, 0.01)
        lon_offset = random.uniform(-0.01, 0.01)
        base_lat = location["base_lat"] + lat_offset
        base_lon = location["base_lon"] + lon_offset
        
        # Create plot points with slight variations
        points = []
        plot_size = random.uniform(300, 1000)  # Size in square meters
        point_offsets = [
            (0, 0),
            (random.uniform(0.001, 0.002), 0),
            (random.uniform(0.001, 0.002), random.uniform(0.001, 0.002)),
            (0, random.uniform(0.001, 0.002))
        ]
        
        for offset in point_offsets:
            points.append({
                "latitude": base_lat + offset[0],
                "longitude": base_lon + offset[1]
            })
        
        # Generate random owners (1-2 owners per plot)
        num_owners = random.randint(1, 2)
        owners = []
        for _ in range(num_owners):
            owners.append({
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "address": f"{random.randint(1, 999)} {random.choice(streets)}, {location['name']}, Ghana"
            })
        
        # Generate random dates
        instrument_date = start_date + timedelta(days=random.randint(0, 365))
        survey_date = instrument_date - timedelta(days=random.randint(30, 90))
        
        # Calculate distances between points
        distances = []
        for j in range(len(points)):
            next_point = (j + 1) % len(points)
            distance = random.uniform(35, 50)  # Random distance in meters
            distances.append({
                "start_point": j + 1,
                "end_point": next_point + 1,
                "distance": round(distance, 1)
            })
        
        plot = {
            "land_data": {
                "date_of_instrument": instrument_date.strftime("%Y-%m-%d"),
                "title_of_document": "Land Title Certificate",
                "owners": owners,
                "plot_id": f"GH{location['name'][:2].upper()}{str(i+1).zfill(4)}",
                "size": round(plot_size, 1),
                "type": random.choice(land_types),
                "location": location["name"],
                "site_plan": {
                    "gps_processed_data_summary": {
                        "point_list": points
                    },
                    "bearing_distances": distances,
                    "plan_data": "Details of boundary and corner points",
                    "area_computation": round(plot_size, 1),
                    "licensed_surveyor_number": f"LS{random.randint(100000, 999999)}",
                    "date_of_letter": survey_date.strftime("%Y-%m-%d"),
                    "regional_number": f"GR{random.randint(10000, 99999)}"
                }
            }
        }
        
        plots.append(plot)
    
    return {"plots": plots}

# Generate mock data
mock_data = generate_mock_data(20)  # Generate 20 plots

# Save to file
with open("mock_land_registry_data.json", "w") as f:
    json.dump(mock_data, f, indent=2)

# Print sample data
print(json.dumps(mock_data["plots"][0], indent=2))