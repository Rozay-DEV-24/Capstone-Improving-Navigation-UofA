# ImprovingNavigationUA
Improving Navigation and Accessibility for Visually Impaired People at the University of Arizona 
Built with a FastAPI backend and an HTML/JavaScript frontend, the system enables users to upload images or type building names to receive:

🔍 OCR-based address recognition from campus signage

🧠 Vision-language model fallback (Gemma or LLaMA-3.2) for scene understanding

📍 Nearby building detection using OpenStreetMap or GIS APIs

🧭 Accessible route generation (ramps, elevators) using OSM and UArizona routing APIs

💬 Chat-style interaction with screen-reader friendly UI and ARIA attributes

The project integrates multimodal AI, geospatial APIs, and accessibility datasets to ensure inclusive navigation experiences.

//Install Dependencies
pip install -r requirements.txt

//Debugging
To run the background : uvicorn fastapi_chatbot_backend:app --reload

Then, Double click frontend homepage.html file.

//To run backend and frontend in one go
python launch_app.py

//docker image
docker compose up --build [http://localhost:8000/]

//delete broken docker [ While Rebuilding ]
docker compose down --volumes
