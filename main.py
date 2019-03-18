from flask import Flask, request, render_template
import Engine

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=['post'])
def home_form_post():
    text = request.form['text']
    engine = Engine.Engine()
    top = engine.get_recommendations(text, 5)
    if top == []:
        return render_template(
            'submitted_form.html',
            name='Film not found', rec1=' ', rec2=' ', rec3=' ', rec4=' ', rec5=' ')
    else:
        return render_template(
            'submitted_form.html',
               name=text, rec1 = top[0], rec2 = top[1], rec3 = top[2], rec4 = top[3], rec5 = top[4])

if __name__ == "__main__":
    app.run(debug=True)
