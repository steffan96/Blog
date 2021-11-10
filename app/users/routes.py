from flask.helpers import url_for
from flask_login.utils import login_user
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, logout_user, login_required, login_user
from app.users.forms import LoginForm, RegisterForm, UpdateAccount, RequestResetForm, ResetPasswordForm
from app.models import User, Post, Follow
from app import db, bcrypt
from app.users.utils import save_picture, send_confirmation_mail, reset_password_mail
from app.decorators import profile

users = Blueprint('users', __name__)




@users.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            #admin_user = User.query.filter_by(email='stefanmilicic@yahoo.com').first()
            #pic = admin_user.picture
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8', 'ignore')
            user = User(username = form.username.data, 
                    email = form.email.data,
                    password = hashed_pw)#, picture=pic)
            db.session.add(user)
            db.session.commit()            
            send_confirmation_mail(user)
            flash("Successfully registered!", 'success')
            return redirect(url_for('users.login'))
            
    return render_template('register.html', form=form)

@users.route('/login', methods=["GET", "POST"])
def login(): 
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
                flash("Login successful", 'success')
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash("Login unsuccessful. Please check your email and password", 'warning')
    return render_template('login.html', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('users.login'))

@users.route('/account', methods=["POST", "GET"])
@login_required
def account():
    
    count = 0# making sure that at least one element was changed so that the user can be directed to the home page with a flash message
    form = UpdateAccount()
    page = request.args.get('page', 1, type=int)
    
    
    pagin = Post.query.filter_by(user_id = current_user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    

    if form.username.data:
        current_user.username = form.username.data
        count+=1

    if form.email.data: 
        current_user.email = form.email.data
        count+=1

    if form.password.data and form.confirm_password.data:
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_pw
        count+=1

    if form.about_me.data:
        current_user.about_me = form.about_me.data
        count+=1
        
    if form.picture.data:
        picture_file = save_picture(form.picture.data)
        current_user.picture = picture_file
        count+=1

    
    if count > 0:
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('users.account'))
    image_file = url_for('static', filename='profile_pics/')# + current_user.picture)
    return render_template('account.html', form=form, image_file=image_file, page=page, pagin=pagin)

@users.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("Your have confirmed your account", 'success')
        return redirect(url_for('main.home'))
    if current_user.confirm_token(token):
        db.session.commit()
        flash("You have confirmed your account!", 'success')
        return redirect(url_for('main.home'))
    else:
        flash("The confirmation link is invalid or expired", 'warning')
    return render_template('unconfirmed.html')


@users.route('/user/<id>')
def user(id):
    if not current_user.confirmed:
        return render_template('unconfirmed.html')
    else:
        user = User.query.filter_by(id=id).first_or_404()
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc())
        pagin = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
        image_file = url_for('static', filename='profile_pics/' + user.picture)
        return render_template('user.html', user=user, image_file=image_file, page=page, pagin=pagin, posts=posts)

@users.route('/follow/<int:id>', methods=["POST", "GET"])
def follow(id):
    user = User.query.filter_by(id=id).first()
    image_file = url_for('static', filename='profile_picutres/' + user.picture)  
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc())
    pagin = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    if not current_user.is_following(user):
        f = Follow(follower=current_user, followed=user)
        db.session.add(f)
        db.session.commit()
    return render_template('user.html', user=user, image_file=image_file, page=page, pagin=pagin, posts=posts)
        
@users.route('/unfollow/<int:id>', methods=["POST", "GET"])
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    image_file = url_for('static', filename='profile_picutres/' + user.picture) 
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc())
    pagin = Post.query.filter_by(user_id = user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    f = current_user.follower.filter_by(followed_id=user.id).first()
    if f:
        db.session.delete(f)
        db.session.commit()
    return render_template('user.html', user=user, page=page, pagin=pagin, posts=posts, image_file=image_file)
    
@users.route('/is_following/<int:id1>/<int:id2>', methods=["POST", "GET"])     
def is_following(id1, id2):
    user1 = User.query.filter_by(id=id1).first()
    user2 = User.query.filter_by(id=id2).first()
    if user1 == None or user2 == None:
        return False
    return user1.follower.filter_by(followed_id=user2.id).first() is not None
    
@users.route('/is_followed_by/<int:id1>/<int:id2>', methods=["POST", "GET"])
def is_followed_by(id1, id2):
    user1 = User.query.filter_by(id=id1).first()
    user2 = User.query.filter_by(id=id2).first()
    if user1 == None or user2 == None:
        return False
    return user1.followed.filter_by(follower_id=user2.id).first() is not None



@users.route('/forgot_password', methods=["POST", "GET"])
def forgot_password():
    form = RequestResetForm()
    user = User.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit():
        
        reset_password_mail(user=user)
        flash("We have sent you an email. Please check your inbox to create a new password.", 'success')
        return redirect(url_for('users.login'))
    return render_template('forgot_password.html', form=form)

@users.route('/reset_password/<username>/<token>', methods=["POST", "GET"])
def reset_password(username, token):
    
    user = User.query.filter_by(username=username).first()
    if not user.confirm_token(token):
        flash('This is an invalid or expired token', 'warning')
        return redirect('users.forgot_password')
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated", 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', form=form)