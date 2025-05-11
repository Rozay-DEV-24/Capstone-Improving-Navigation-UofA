# ImprovingNavigationUA
Improving Navigation and Accessibility for Visually Impaired People at the University of Arizona 

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