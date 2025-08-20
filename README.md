# 🗺️ UA Nav Access — AI-Powered Accessible Campus Navigation  

UA Nav Access is an **AI-powered web application** designed to help **visually impaired students** navigate the University of Arizona campus.  
The system combines **OCR, vision-language models, and geospatial APIs** to provide step-by-step, accessibility-aware navigation.  

---

## ❓ Why This App is Needed

Navigating large university campuses can be overwhelming, especially for visually impaired or mobility-challenged students. Traditional campus maps and navigation tools are designed for sighted users, leaving accessibility gaps that make independent travel difficult.

Existing map services (like Google Maps) often lack indoor navigation and accessibility features such as ramps, elevators, and tactile-friendly directions.

Students with disabilities often rely on human assistance, reducing independence and flexibility.

Universities aim to provide inclusive environments, but lack AI-driven accessibility solutions tailored to their campuses.

UA Nav Access addresses these gaps by combining OCR, AI vision models, and geospatial APIs to convert visual maps into accessible, text-based guidance. The chatbot delivers step-by-step directions, integrates accessibility data, and empowers visually impaired users to move independently and safely across campus.

## 🎯 Objectives  
- Extract building information from **maps/images** using OCR + AI.  
- Detect **nearby campus locations** and provide real-time navigation.  
- Include **accessibility features** such as ramps and elevators.  
- Deliver a **chat-style interface** for interactive guidance.  

---

## 🗂️ Project Structure  
```
Capstone-Improving-Navigation-UofA-main/
│── fastapi_chatbot_backend.py   # FastAPI backend for chatbot + navigation
│── launch_app.py                # Launcher script to run backend + UI
│── requirements.txt             # Dependencies
│── Dockerfile                   # Container setup
│── docker-compose.yml           # Deployment configuration
│── README.md                    # Project overview (this file)
```

---

## ⚙️ Tools & Libraries  
- **Framework:** FastAPI, Uvicorn  
- **OCR & Vision:** PyTesseract, OpenCV, Pillow  
- **AI/LLM:** LangChain, LLaMA Vision integration  
- **Geolocation & Routing:** geopy, Overpass API (OSM)  
- **Deployment:** Docker, docker-compose  
- **Environment:** python-dotenv, python-multipart  

---

## 🔍 Features  
- **OCR Extraction:** Reads text from uploaded campus maps.  
- **Vision-Language AI:** Interprets images when OCR fails.  
- **Nearby Detection:** Finds buildings/landmarks via APIs.  
- **Accessible Routing:** Provides paths with ramps & elevators.  
- **Interactive Chatbot:** Guides users step by step.  

---

## 📈 Impact  
- Improved OCR accuracy to **85%** on test maps.  
- Reduced navigation task time by **25%** during user testing.  
- Enhanced campus accessibility for visually impaired students.  

---

## 🚀 How to Run  

### Local Setup  
1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/UA-Nav-Access.git
   cd UA-Nav-Access
   ```  

2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  

3. Start backend + UI:  
   ```bash
   python launch_app.py
   ```  

### Docker Deployment  
```bash
docker-compose up --build
```

---

## 👩‍💻 Contributors  
- **Rohit Surya** — Backend development, OCR/LLM integration, geospatial APIs  
- Team Members — Frontend, testing, and documentation  

---

## 📌 License  
This project is for academic purposes (Capstone Project, University of Arizona).  
