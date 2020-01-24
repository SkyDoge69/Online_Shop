import json
import uuid

from flask import Flask
from flask import request
from flask import render_template

from model.ad import Ad
from model.user import User
from errors import register_error_handlers

from security.basic_authentication import generate_password_hash
from security.basic_authentication import init_basic_auth

#zakomentirah vsi4ko s auth da vidq
#export FLASK_APP=app.py && flask run


app = Flask(__name__)
auth = init_basic_auth()
register_error_handlers(app)


@app.route("/api/ads", methods = ["POST"])
def create_ad():
    ad_data = request.get_json(force=True, silent=True)
    if ad_data == None:
        return "Bad request", 400
    ad = Ad(ad_data["title"], ad_data["content"], ad_data["price"], ad_data["release_date"], ad_data["is_active"], ad_data["buyer"])
    ad.save()
    return json.dumps(ad.to_dict()), 201


@app.route("/api/ads", methods = ["GET"])
def list_ads():
    result = {"result": []}
    for ad in Ad.all():
        result["result"].append(ad.to_dict())
    return json.dumps(result)


@app.route("/api/ads/<ad_id>", methods = ["GET"])
def get_ad(ad_id):
    return json.dumps(Ad.find(ad_id).to_dict())


@app.route("/api/ads/<ad_id>", methods = ["DELETE"])
def delete_ad(ad_id):
    ad = Ad.find(ad_id)
    ad.delete(ad_id)
    return ""


@app.route("/api/ads/<ad_id>", methods = ["PATCH"])
def update_ad(ad_id):
    ad_data = request.get_json(force=True, silent=True)
    if ad_data == None:
        return "Bad request", 400

    ad = Ad.find(ad_id)
    if "title" in ad_data:
        ad.title = ad_data["title"]
    if "content" in ad_data:
        ad.content = ad_data["content"]
    if "price" in ad_data:
        ad.price = ad_data["price"]
    if "release_date" in ad_data:
        ad.release_date = ad_data["release_date"]
    if "is_active" in ad_data:
        ad.is_active = ad_data["is_active"]
    if "buyer" in ad_data:
        ad.buyer = ad_data["buyer"]
    return json.dumps(ad.save().to_dict())


@app.route("/api/users", methods = ["POST"])
def create_user():
    user_data = request.get_json(force=True, silent=True)
    if user_data == None:
        return "Bad request", 400
    hashed_password = generate_password_hash(user_data["password"])
    user = User(user_data["username"], hashed_password, user_data["name"], user_data["adress"], user_data["mobile_number"])
    user.save()
    return json.dumps(user.to_dict()), 201


@app.route("/", methods = ["GET"])
@auth.login_required
def ads():
    return render_template("index.html")


@app.route("/ads/<ad_id>", methods = ["GET"])
def view_ad(ad_id):
    return render_template("ad.html", ad=Ad.find(ad_id))



