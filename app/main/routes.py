from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user
from flask_login.utils import login_required
from flask_sqlalchemy import get_debug_queries

from app import db
from app.main.forms import CommentForm, PostForm
from app.models import Comment, Follow, Like, Post, User

main = Blueprint("main", __name__)


@main.route("/", methods=["POST", "GET"])
@main.route("/home", methods=["POST", "GET"])
@login_required
def home():
    if not current_user.confirmed:
        return render_template("unconfirmed.html")
    else:

        page = request.args.get("page", 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(
            page=page, per_page=4
        )
        return render_template("home.html", posts=posts, Like=Like)


@main.route("/post/<int:id>", methods=["POST", "GET"])
@login_required
def post(id):
    post = Post.query.filter_by(id=id).first()
    user = User.query.filter_by(id=post.user_id).first()
    form = CommentForm()
    comments = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.timestamp.desc())
        .all()
    )
    page = request.args.get("page", 1, type=int)
    pagin = Comment.query.filter_by(post_id=post.id).paginate(page=page, per_page=4)
    if form.validate_on_submit():  # adding comments
        comment = Comment(
            body=form.body.data, post=post, author=current_user._get_current_object()
        )
        db.session.add(comment)
        db.session.commit()
        flash("New comment added", "success")
        if (
            pagin.total % 4 + 1 == 1
        ):  # code that will redirect user to a last comment's page after posting a comment
            pages_num = pagin.pages + 1
        else:
            pages_num = pagin.pages
        return redirect(url_for(".post", id=post.id, page=pages_num))
    return render_template(
        "post.html",
        post=post,
        user=user,
        form=form,
        comments=comments,
        page=page,
        pagin=pagin,
    )


@main.route("/newpost", methods=["POST", "GET"])
@login_required
def newpost():
    if not current_user.confirmed:
        return render_template("unconfirmed.html")
    else:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(
                title=form.title.data, content=form.content.data, author=current_user
            )
            db.session.add(post)
            db.session.commit()
            flash("New post added", "success")
            return redirect(url_for(".home"))
    return render_template("new_post.html", form=form)


@main.route("/delete_post/<int:id>", methods=["POST", "GET"])
@login_required
def delete_post(id):

    f = Post.query.filter_by(id=id).first()
    db.session.delete(f)
    db.session.commit()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    flash("Post deleted", "success")
    return render_template("home.html", posts=posts, Like=Like)


@main.route("/delete_comment/<int:id>/<int:post_id>", methods=["POST", "GET"])
@login_required
def delete_comment(id, post_id):
    f = Comment.query.filter_by(id=id).first()
    db.session.delete(f)
    db.session.commit()
    flash("Comment deleted", "success")

    return redirect(url_for(".post", id=post_id))


@main.route("/edit_post/<int:id>", methods=["POST", "GET"])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully", "success")
        return redirect(url_for("main.home"))
    form.title.data = post.title
    form.content.data = post.content
    return render_template("edit_post.html", post=post, form=form)


@main.route("/edit_comment", methods=["POST", "GET"])
@login_required
def edit_comment():
    pass


@main.route("/following/<int:id>", methods=["POST", "GET"])
def following(id):
    if not current_user.confirmed:
        return render_template("unconfirmed.html")
    else:
        user = User.query.filter_by(id=id).first()
        page = request.args.get("page", 1, type=int)
        posts = (
            Post.query.join(Follow, Follow.followed_id == Post.user_id)
            .filter(Follow.follower_id == user.id)
            .paginate(page=page, per_page=4)
        )
        return render_template("following.html", posts=posts, page=page)


@main.route("/like/<int:id>", methods=["POST", "GET"])
@login_required
def like(id):
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    f = current_user.likes.filter_by(post_id=id).first()
    if not f:
        like = Like(user_id=current_user.id, post_id=id)
        db.session.add(like)
        db.session.commit()
        return redirect(url_for(".home"))


@main.route("/unlike/<int:id>", methods=["POST", "GET"])
@login_required
def unlike(id):
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    post = Post.query.filter_by(id=id).first()
    f = current_user.likes.filter_by(post_id=post.id).first()
    if f:
        db.session.delete(f)
        db.session.commit()
    return render_template("home.html", posts=posts, Like=Like)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["FLASK_SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(
                "Slow query: {}\nParameters: {}\n Duration: {}\n Context: {}\n".format(
                    query.statement, query.parameters, query.duration, query.context
                )
            )
    return response
