from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
Bootstrap5(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # Note that this goes inside the cafe class above
    # If we use the below to convert the data into a dict, we can return all of the data without doing it line by line
    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/cafes')
def cafes():
    # with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
    #     csv_data = csv.reader(csv_file, delimiter=',')
    #     list_of_rows = []
    #     for row in csv_data:
    #         print(row)
    #         list_of_rows.append(row)
    #     print(list_of_rows[0])
    list_of_rows = "null"
    return render_template('cafes.html', cafes=list_of_rows)


@app.route('/add', methods=['POST', 'GET'])
def add_cafe():
    form = "form"
    # form = CafeForm()
    # if form.validate_on_submit():
    #     print("True")
    #     cafe = form.cafe.data
    #     location = form.location.data
    #     open_time = form.open_time.data
    #     close_time = form.close_time.data
    #     coffee = form.coffee.data
    #     wifi = form.wifi.data
    #     power = form.power.data
    #     cafe_data = open("cafe-data.csv", "a", encoding="utf-8")
    #     cafe_data.write(f"\n{cafe}, {location}, {open_time}, {close_time}, {coffee}, {wifi}, {power}")
    #     cafe_data.close()
    #     with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
    #         csv_data = csv.reader(csv_file, delimiter=',')
    #         list_of_rows = []
    #         for row in csv_data:
    #             print(row)
    #             list_of_rows.append(row)
    #         print(list_of_rows[0])
    #     return render_template('cafes.html', cafes=list_of_rows)
    return render_template('add.html', form=form)


# ALL BELOW ARE FOR API CALLS
@app.route("/random")
def find_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    list_of_cafes = []
    for cafe in all_cafes:
        list_of_cafes.append(cafe.to_dict())
    return jsonify(list_of_cafes)


@app.route('/search')
def search_cafes():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        # Note that the keys we will use in Postman are the strings EG. "loc" instead of "location"
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        #404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == "TopSecretAPIKey":
        cafe = db.get_or_404(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted cafe from database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found."}), 404
    else:
        return jsonify(error={"Forbidden": "Invalid API Key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
