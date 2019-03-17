from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=['post'])
def home_form_post():
    text = request.form['text']

    return render_template(
        'submitted_form.html',
        name=text, rec1 = 'Rec1', rec2 = 'Rec2', rec3 = 'Rec3', rec4 = 'Rec4', rec5 = 'Rec5')

if __name__ == "__main__":
    app.run(debug=True)
