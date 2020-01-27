import json
import uuid

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify

from model.ad import Ad
from model.user import User
from errors import register_error_handlers

from security.basic_authentication import generate_password_hash
from security.basic_authentication import init_basic_auth
from werkzeug.security import generate_password_hash, check_password_hash


# export FLASK_APP=app.py && flask run


app = Flask(__name__)
auth = init_basic_auth()
register_error_handlers(app)

user_ad_comp = False


@app.route("/api/ads", methods=["POST"])
def create_ad():
    ad_data = request.get_json(force=True, silent=True)
    if ad_data == None:
        return "Bad request", 400
    ad = Ad(ad_data["title"], ad_data["content"], ad_data["price"], ad_data["release_date"],
            ad_data["is_active"], ad_data["buyer"], ad_data["creator_id"])
    ad.save()
    return jsonify(ad.to_dict()), 201


@app.route("/api/ads", methods=["GET"])
def list_ads():
    result = {"result": []}
    for ad in Ad.all():
        result["result"].append(ad.to_dict())
    return jsonify(result)


@app.route("/api/ads/<ad_id>", methods=["GET"])
def get_ad(ad_id):
    return jsonify(Ad.find(ad_id).to_dict())


@app.route("/api/ads/<ad_id>", methods=["DELETE"])
@auth.login_required
def delete_ad(ad_id):
    current_user = User.find_by_email(auth.username())
    ad = Ad.find(ad_id)
    if current_user.id == ad.creator_id:
        ad = Ad.find(ad_id)
        ad.delete(ad_id)
        return "The ad was deleted", 200
    else:
        return "Permission denied", 401


@app.route("/api/ads/<ad_id>", methods=["PATCH"])
@auth.login_required
def update_ad(ad_id):
    current_user = User.find_by_email(auth.username())
    ad = Ad.find(ad_id)

    if current_user.id == ad.creator_id:
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
            ad.buyer_id = ad_data["buyer"]
        return jsonify(ad.save().to_dict()), 201

    else:
        return "Permission denied", 401


@app.route("/api/users", methods=["POST"])
def create_user():
    user_data = request.get_json(force=True, silent=True)
    if user_data == None:
        return "Bad request", 401
    hashed_password = generate_password_hash(user_data["password"])
    user = User(user_data["email"], hashed_password, user_data["name"],
                user_data["adress"], user_data["mobile_number"])
    user.save()
    return jsonify(user.to_dict()), 201


@app.route("/api/users/<user_id>", methods=["GET"])
@auth.login_required
def get_user(user_id):
    return jsonify(User.find(user_id).to_dict())


@app.route("/api/users", methods=["GET"])
def list_users():
    result = {"result": []}
    for user in User.all():
        result["result"].append(user.to_dict())
    return jsonify(result), 201


@app.route("/api/users/<user_id>", methods=["PATCH"])
def update_user(user_id):
    user_data = request.get_json(force=True, silent=True)
    if user_data == None:
        return "Bad request", 401

    user = User.find(user_id)
    if "name" in user_data:
        user.name = user_data["name"]
    if "adress" in user_data:
        user.adress = user_data["adress"]
    if "mobile_number" in user_data:
        user.mobile_number = user_data["mobile_number"]
    return jsonify(user.save().to_dict()), 201


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.find(user_id)
    user.delete(user_id)
    return ""


@app.route("/", methods=["GET"])
@auth.login_required
def ads():
    return render_template("index.html")


@app.route("/ads/<ad_id>", methods=["GET"])
def view_ad(ad_id):
    return render_template("ad.html", ad=Ad.find(ad_id))


@app.route("/api/ads/<user_id>/<ad_id>", methods=["PATCH"])
def buy_ad(user_id, ad_id):
    ad = Ad.find(ad_id)
    user = User.find(user_id)
    ad.is_active = 0
    ad.buyer_id = user.name
    return jsonify(ad.save().to_dict())


@app.route("/api/users/sold/<user_id>", methods=["GET"])
def sold_ads(user_id):
    return jsonify([ad.to_dict() for ad in Ad.all() if (ad.creator_id == int(user_id) and not ad.is_active)])
