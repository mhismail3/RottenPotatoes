from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=['post'])
def home_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text
if __name__ == "__main__":
    app.run(debug=True)
