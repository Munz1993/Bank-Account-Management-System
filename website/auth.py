from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Registry, Branch, BRANCH_CUSTOMER
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Registry.query.filter_by(EMAILID=email).first()
        if user:
            if check_password_hash(user.PASSWORD, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        print('0')
        emailid = request.form.get('email')
        firstname = request.form.get('firstName')
        lastname = request.form.get('lastName')
        Cust_address_1 = request.form.get('CustAddress1')
        Cust_address_2 = request.form.get('CustAddress2')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        contact = request.form.get('contactno')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        print('1')
        user = Registry.query.filter_by(EMAILID=emailid).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(emailid) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstname) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(lastname) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(Cust_address_1) < 2:
            flash('Inappropriate Value for Address', category='error')
        elif len(zipcode) != 5:
            flash('Inappropriate Value for Zipcode', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 4:
            flash('Password must be at least 4 characters.', category='error')
        else:
            new_user = Registry(EMAILID=emailid, FIRSTNAME=firstname, LASTNAME=lastname, CUST_ADDRESS_1=Cust_address_1,
                                     CUST_ADDRESS_2= Cust_address_2, CITY=city, STATE=state, ZIP_CODE=zipcode,
                                     MOBILE_NUMBER = contact, PASSWORD=generate_password_hash(password1, method='sha256'))

            db.session.add(new_user)
            db.session.commit()
            
            #let's update the associative table between Registry and Branch i.e. BRANCH_CUSTOMER
            latest_cust = Registry.query.order_by(Registry.created_at.desc()).first()
            branch = Branch.query.filter_by(CITY=latest_cust.CITY).first()
            val=BRANCH_CUSTOMER(ID=latest_cust.ID, BRANCHID = branch.BRANCHCODE)
            db.session.add(val)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash('Profile created!', category='success')
            return redirect(url_for('views.home', branch_id=(branch.BRANCHCODE), cust_id=(latest_cust.ID)))
    return render_template("sign_up.html", user=current_user)