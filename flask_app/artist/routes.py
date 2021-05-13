from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import artist_client
from ..forms import SearchForm, JazzPostForm
from ..models import User, JazzPost
from ..utils import current_time


artists = Blueprint("artists", __name__, template_folder="templates")

@artists.route("/artists/<artist_id>", methods=["GET", "POST"])
def artist_detail(artist_id):
    try:
        result = artist_client.retrieve_artist_by_name(artist_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("main.index"))

    form = JazzPostForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        post = JazzPost(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            name=artist_id,
        )
        post.save()

        return redirect(request.path)

    posts = JazzPost.objects(name=artist_id)

    return render_template("artist_detail.html", form=form, artist=result, posts=posts)