from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     validators)
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import (DataRequired, EqualTo, Length, Regexp,
                                ValidationError)

from app.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Enter your username", validators=[DataRequired(), Length(1, 64)]
    )
    email = EmailField(
        "Enter your email", [validators.DataRequired(), validators.Email()]
    )
    password = PasswordField(
        "Enter your password",
        validators=[
            DataRequired(),
            Length(min=6),
            EqualTo("confirm_password", message="Passwords need to match"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm your password",
        validators=[DataRequired(), EqualTo("password", message=" ")],
    )
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("This user already exist")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError("This email is already in use")


class LoginForm(FlaskForm):
    email = EmailField("Enter email", [validators.DataRequired(), validators.Email()])
    password = PasswordField(
        "Enter password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must contain at least 6 characters"),
        ],
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class UpdateAccount(FlaskForm):
    username = StringField(
        "Change username",
    )
    email = EmailField(
        "Change email",
        validators=[Regexp("[^@]+@[^@]+\.[^@]+", message="email not valid")],
    )
    password = PasswordField(
        "Change password",
        validators=[
            Length(min=6),
            EqualTo("confirm_password", message="Passwords need to match"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password", validators=[Length(min=6), EqualTo("password")]
    )
    picture = FileField(
        "Upload profile picture", validators=[FileAllowed(["jpg", "png"])]
    )
    about_me = TextAreaField("Tell us something about you", validators=[Length(0, 600)])
    submit = SubmitField("Submit")
    # posts = StringField('')


class RequestResetForm(FlaskForm):
    email = EmailField(
        "Have you forgot your password?",
        [validators.DataRequired(), validators.Email()],
    )
    submit = SubmitField("Submit")

    def validate_email(self, email):
        user = User.query.filter_by(email=self.email)
        if not user:
            raise ValidationError(
                "There is no account with this email address. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "Enter new password",
        validators=[
            Length(min=6),
            EqualTo("confirm_password", message="Passwords need to match"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[Length(min=6), EqualTo("new_password", message=" ")],
    )
    submit = SubmitField("Submit")
