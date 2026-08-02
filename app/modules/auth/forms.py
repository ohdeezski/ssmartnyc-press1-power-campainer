from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# check_deliverability=False keeps syntax validation but skips the DNS MX
# lookup, which otherwise rejects internal domains (*.local, *.internal) and
# adds network latency plus a hard dependency on DNS during login.
_email = Email(check_deliverability=False)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), _email])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField("Email", validators=[DataRequired(), _email])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")
