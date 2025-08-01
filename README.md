# Hardwood Player Predictor

This tool predicts a basketball player's skill ratings at age 22 based on their current and initial values from [onlinecollegebasketball.org](http://onlinecollegebasketball.org).

**Live App:** https://your-app-name.onrender.com  
(Replace with your actual Render URL)

## How It Works

- Paste a player URL like `http://onlinecollegebasketball.org/player/224284`
- The app scrapes:
  - Initial skill values (from age 14)
  - Current skill values
  - Potential rating
- It predicts skill growth up to age 22
- Applies an SI (Skill Index) cap: `SI Cap = Potential × 15.5`
- Displays predicted skill ratings (max 20, rounded down)

## To Run Locally

1. Clone the repo:
git clone https://github.com/plokmijn41/Hardwood-Player-Predictor.git
cd Hardwood-Player-Predictor


2. Install requirements:
pip install -r requirements.txt


3. Run the app:
python app.py


4. Open your browser to:  
`http://localhost:5000`

## Files

- `app.py` - Flask web app
- `predictor.py` - Scraper and prediction logic
- `templates/index.html` - Web interface
- `requirements.txt` - Dependencies

## Built With

- Python + Flask
- LXML (web scraping)
- Render (deployment)

---

Created by Dayton Emerson
