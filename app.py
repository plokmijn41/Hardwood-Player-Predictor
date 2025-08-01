from flask import Flask, render_template, request
from predictor import run_prediction  # We’ll create this next

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        player_url = request.form.get("player_url")
        try:
            result = run_prediction(player_url)
        except Exception as e:
            result = {"error": f"An error occurred: {str(e)}"}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
