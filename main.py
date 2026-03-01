from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import random
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="."), name="static")

THREAT_DATA = {
    "Heat Wave": "Intense solar radiation. Direct temperature spike of +12°C.",
    "Permafrost Thaw": "Frozen soil melting. Releases trapped methane, increasing heat pressure.",
    "Glacial Collapse": "Massive ice loss. Reduces planetary Albedo, speeding up baseline warming.",
    "Methane Burp": "Sudden release of sub-sea gas. Causes rapid, unpredictable heating.",
    "Solar Flare": "Extreme UV burst. Damages high-tech cooling infrastructure.",
    "Wind Storm": "Hot desert winds. Disrupts urban ventilation and windmills."
}

TOOL_CONFIG = {
    "windmill": {
        "cost": 50, "cooling": 0.2, 
        "name": "Kinetic Wind Turbine",
        "desc": "Converts wind energy into clean power. West placement is optimal."
    },
    "mist_tower": {
        "cost": 150, "cooling": 1.5, 
        "name": "Evaporative Mist Tower",
        "desc": "Uses high-pressure nozzles to mimic 'Flash Evaporation'."
    },
    "wind_corridor": {
        "cost": 200, "cooling": 2.0, 
        "name": "Cryo-Wind Corridor",
        "desc": "Uses the Venturi Effect to flush hot air out of urban pockets."
    },
    "solar_sail": {
        "cost": 300, "cooling": 3.5, 
        "name": "Orbital Albedo Sail",
        "desc": "Increases planet's Albedo by bouncing radiation back into space."
    },
    "thermal_vent": {
        "cost": 600, "cooling": 8.0, 
        "name": "Stratospheric Aerosol Injector",
        "desc": "Releases reflective particles to create a temporary shield."
    },
    "white_roof": {
        "cost": 25, "cooling": 0.8, 
        "name": "Titanium White Coating",
        "desc": "Reflects up to 80% of sunlight, mitigating Heat Island effects."
    }
}

FACTS = [
    "Placing cooling tech upwind allows convective heat transfer across the city.",
    "Grouping units reduces surface area but increases the Urban Heat Island effect.",
    "The Albedo Effect: White roofs reflect the majority of solar radiation.",
    "Methane is roughly 28 times more potent than CO2 at trapping heat."
]

def generate_initial_city():
    buildings = []
    
    def is_valid_pos(x, y, existing_buildings):
        for b in existing_buildings:
            dist = ((b['x'] - x)**2 + (b['y'] - y)**2)**0.5
            if dist < 8:
                return False
        return True

    # Generate 20 Houses (East/Right)
    attempts = 0
    while len(buildings) < 20 and attempts < 500:
        x, y = random.uniform(55, 90), random.uniform(10, 90)
        if is_valid_pos(x, y, buildings):
            buildings.append({"type": "house", "x": x, "y": y, "is_white": False})
        attempts += 1
    
    # Generate 20 Windmills (West/Left)
    attempts = 0
    while len([b for b in buildings if b["type"] == "windmill"]) < 20 and attempts < 500:
        x, y = random.uniform(10, 45), random.uniform(10, 90)
        if is_valid_pos(x, y, buildings):
            buildings.append({"type": "windmill", "x": x, "y": y})
        attempts += 1
        
    return buildings

# Global Game State
game_state = {
    "city_temp": 35.0,
    "credits": 500, 
    "next_disaster": "Heat Wave",
    "threat_desc": THREAT_DATA["Heat Wave"],
    "time_until_hit": 100,
    "disaster_count": 0,
    "buildings": generate_initial_city(),
    "heat_pressure": 2.2,
    "game_over": False,
    "grace_period_active": False,
    "disaster_triggered": False,
    "days_survived": 0,
    "fact": "Sensors active. Upwind cooling strategy recommended."
}

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/tool_info/{tool_id}")
def get_tool_info(tool_id: str):
    return TOOL_CONFIG.get(tool_id, {"name": "Unknown", "desc": "No data available."})

@app.post("/toggle_grace")
def toggle_grace(data: dict):
    game_state["grace_period_active"] = data.get("active", False)
    return {"status": "success", "grace_active": game_state["grace_period_active"]}

@app.post("/reset")
def reset_game():
    global game_state
    game_state.update({
        "city_temp": 35.0, "credits": 500, "disaster_count": 0,
        "buildings": generate_initial_city(), "heat_pressure": 2.2,
        "game_over": False, "grace_period_active": False, "days_survived": 0,
        "next_disaster": "Heat Wave",
        "threat_desc": THREAT_DATA["Heat Wave"],
        "fact": "Core stabilized. Re-deploying organized grid."
    })
    return game_state

@app.post("/build")
def build_item(data: dict):
    if game_state["game_over"]: return {"status": "error"}
    
    t_type = data["type"]
    if t_type == "windmill" and data["x"] > 50:
        return {"status": "error", "message": "Optimal wind is in the West (Left)!"}
    
    for b in game_state["buildings"]:
        dist = ((b['x'] - data['x'])**2 + (b['y'] - data['y'])**2)**0.5
        if dist < 6: return {"status": "error", "message": "Site occupied!"}
    
    cost = TOOL_CONFIG[t_type]["cost"]
    if game_state["credits"] >= cost:
        game_state["credits"] -= cost
        game_state["buildings"].append(data)
        return {"status": "success"}
    return {"status": "error", "message": "Insufficient Credits"}

@app.post("/upgrade_house")
def upgrade_house(data: dict):
    idx = data["index"]
    cost = TOOL_CONFIG["white_roof"]["cost"]
    
    if game_state["credits"] >= cost:
        # 1. Deduct the credits
        game_state["credits"] -= cost
        
        # 2. Apply the "White Roof" status to the building
        game_state["buildings"][idx]["is_white"] = True
        
        # 3. DIRECT TEMPERATURE REDUCTION
        # This subtracts 3 degrees immediately upon clicking
        game_state["city_temp"] -= 3.0
        
        # 4. Optional: Prevent temperature from going below a "frozen" floor (e.g., -50°C)
        if game_state["city_temp"] < -50.0:
            game_state["city_temp"] = -50.0
            
        return {"status": "success", "new_temp": game_state["city_temp"]}
    
    return {"status": "error", "message": "Insufficient Credits"}
@app.post("/weather_tick")
def weather_tick():
    if game_state["game_over"]: return game_state

    
    
    # 1. Calculate Cooling Power
    total_cooling = sum(0.6 if b.get("is_white") else TOOL_CONFIG.get(b["type"], {"cooling":0})["cooling"] for b in game_state["buildings"])
    
    # Windward Bonus: 10% boost per properly placed windmill
    west_windmills = [b for b in game_state["buildings"] if b["type"] == "windmill" and b["x"] < 50]
    total_cooling += (len(west_windmills) * 0.1) 

    # 2. Update Resources
    game_state["credits"] += 20 + (game_state["days_survived"] // 10)
    game_state["days_survived"] += 1 
    
    # 3. Physics Simulation
    temp_change = (game_state["heat_pressure"] - (total_cooling * 0.1))
    game_state["city_temp"] += max(-0.5, temp_change) 
    
    # 4. Check Defeat Condition (Respecting Grace Period)
    
    if game_state["city_temp"] >= 80.0 and not game_state["grace_period_active"]:
        game_state["game_over"] = True
    
    #game_state["game_over"] = False
    
    # 5. Disaster Management
    game_state["disaster_triggered"] = False
    game_state["time_until_hit"] -= 5

    

    for b in game_state["buildings"]:
        if b.get("is_white") == True:
            # We give white roofs a specific cooling value
            temp_change = (game_state["heat_pressure"] - (total_cooling * 1))
        else:
            # Otherwise, use the standard cooling for that building type
            total_cooling += TOOL_CONFIG.get(b["type"], {"cooling": 0})["cooling"]
    
    if game_state["time_until_hit"] <= 0:
        game_state["disaster_triggered"] = True
        game_state["disaster_count"] += 1
        game_state["heat_pressure"] += 0.25 # Difficulty spike
        game_state["fact"] = random.choice(FACTS)
        
        # Execute Disaster Effects
        if game_state["next_disaster"] == "Heat Wave": 
            game_state["city_temp"] += 10.0
        
        # Structure Damage
        targets = [i for i, b in enumerate(game_state["buildings"]) if b["type"] not in ["house"]]
        if targets:
            to_destroy = random.sample(targets, min(len(targets), 4))
            for index in sorted(to_destroy, reverse=True): 
                game_state["buildings"].pop(index)
        
        # Cycle to next threat
        game_state["time_until_hit"] = 100
        game_state["next_disaster"] = random.choice(list(THREAT_DATA.keys()))
        game_state["threat_desc"] = THREAT_DATA[game_state["next_disaster"]]
        
    return game_state
