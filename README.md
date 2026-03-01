# Frostbyte Project Documentation

## Project Description
Frostbyte is a FastAPI-based climate simulation. It calculates temperature changes based on urban development and cooling infrastructure.

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation and Setup
1. Clone the repository:
   git clone https://github.com/Famousmaster206/Frostbyte.git

2. Install dependencies:
   pip install -r requirements.txt

3. Start the application:
   python -m uvicorn main:app --reload

4. Access the application:
   Open a web browser and navigate to http://127.0.0.1:8000

## Current Mechanics
- Windmills: Provide passive cooling based on coordinates.
- Houses: Generate baseline heat pressure.
- White Roofs: Instant temperature reduction of 3.0 units upon upgrade.
- Game Over: Currently disabled (Sandbox Mode).
