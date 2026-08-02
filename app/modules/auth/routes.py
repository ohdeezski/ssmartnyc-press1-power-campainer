from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.modules.auth import auth_bp
from app.modules.auth.forms import LoginForm, RegistrationForm
from app.modules.auth.models import User


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("ui.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.status != "active":
                flash(
                    "This account has been suspended. Contact an administrator.",
                    "danger",
                )
                return render_template("auth/login.html", form=form)
            login_user(user, remember=form.remember.data)
            user.last_login_at = db.session.query(db.func.now()).scalar()
            db.session.commit()
            return redirect(url_for("ui.dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, name=form.name.data, role="viewer")
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)
