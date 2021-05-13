from flask import Blueprint, render_template, url_for, redirect, request, flash, send_file
from flask_login import current_user

# local
from . import bcrypt, map_client, artist_client
from .forms import (
    SearchForm,
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
)

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()
    map_name = "basic_map.html"

    if form.validate_on_submit():
        return redirect(url_for("main.query_results", query=form.search_query.data))

    return render_template("index.html", form=form, map=map_name)


@main.route("/heatmap", methods=["GET", "POST"])
def heatmap():
    form = SearchForm()
    map_name = "heat_map.html"

    return render_template("index.html", form=form, map=map_name)


@main.route('/map/<map_name>')
def show_map(map_name):
    map_route = './map/' + map_name
    return send_file(map_route)


@main.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = artist_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("main.index"))

    return render_template("query.html", results=results)
