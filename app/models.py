from datetime import datetime
from operator import index
from flask import current_app
from flask.helpers import url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from sqlalchemy.orm import backref
from app import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_admin.contrib.sqla import ModelView



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f"<Comment '{self.id}')>'"

class Like(db.Model):
    __tablename__ = "likes"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(35), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    about_me = db.Column(db.Text(), nullable=True)
    picture = db.Column(db.String(25), nullable=False, default='default.jpg')
    member_since = db.Column(db.DateTime, default = datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref="author", lazy=True)
    follower = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                cascade='all, delete-orphan')
    followed = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref="author", lazy='dynamic')
    likes = db.relationship('Like', foreign_keys=[Like.user_id], 
                backref=db.backref('user_liked', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')



    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id == None:
            self.role_id = 0
        
        if self.email == current_app.config["ADMIN_EMAIL"]:
            self.role_id = 3
        
        if self.role_id == 0:
            self.role_id = 1
        
  
    def __repr__(self):
        return f"<User '{self.username}', '{self.email})>'"

    def generate_confirmation_token(self, expiration=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm_token(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return None
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
        
    @staticmethod
    def verify_confirmation_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


    def has_role(self, role_id):
        return self.role_id & role_id == role_id

    def is_administrator(self):
        return self.role_id == 3

    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()
        

    def unfollow(self, user):
        f = self.follower.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
            
    def is_following(self, user):
        if user.id == None:
            return False
        return self.follower.filter_by(followed_id=user.id).first() is not None


    def is_followed_by(self, user):
        if user.id == None:
            return False
        return self.followed.filter_by(follower_id=user.id).first() is not None
class AnonymousUser(AnonymousUserMixin):

    def has_role(self, role):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser    

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref="post", lazy='dynamic')
    liked = db.relationship('Like', foreign_keys=[Like.post_id], 
                backref=db.backref('post_liked', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Post '{self.title}')>'"
    
    

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="user_role", lazy=True)

    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions == None:
            self.permissions = 0


    def add_permissions(self, perm):
        if not self.has_permissions(perm):
            self.permissions += perm

    def remove_permissions(self, perm):
        if self.has_permissions(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permissions(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permissions(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
    
    def __repr__(self):
        return f"Role <'{self.name}>'"


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 3

