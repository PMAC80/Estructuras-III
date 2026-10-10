from flask import render_template
from config import connex_app
from models import Person

app = connex_app.app
connex_app.add_api("swagger.yml")

@app.route("/")
def home():
    people = Person.query.all()
    return render_template("home.html", people=people)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)