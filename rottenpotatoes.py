from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
    return "Welcome to Rotten Potatoes! Best movie recommender on the web!"
if __name__ == "__main__":
    app.run(debug=True)