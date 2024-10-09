import csv
from init import app, db 
from flask import Flask, render_template, url_for, flash, redirect, request, session, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import random
from flask_migrate import Migrate
from io import StringIO

migrate = Migrate(app, db)

from forms import (
    EmployeeEmailForm,
    EmployeeCardDetailsForm,
    ExitFeedbackForm,
    OTPForm,
    visitorform,
    exitform,
    Feedbackform,
)
from data import (
    visitors,
    card,
    update_cards,
    update_card_status,
    get_unused_cards,
    get_used_cards,
    change_status,
    display_details,
    Feedback,
)

# Configure Flask app
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitordata.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hashclg@gmail.com'
app.config['MAIL_PASSWORD'] = 'terypydbgjvaprjb'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)  # Increase this as needed

mail = Mail(app)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

#Visitors Page
@app.route("/submit", methods=['GET', 'POST'])
def submit():
    form = visitorform()
    cards = get_unused_cards()
    print(cards)  # Debugging: Print the cards to ensure they're populated
    form.Card_no.choices = cards
    form.Card_no.choices = get_unused_cards() 
  
    if form.validate_on_submit() and form.Card_no.data:
        purpose = form.other_purpose.data if form.purpose.data == 'Other' else form.purpose.data
        selected_card = form.Card_no.data
        update_card_status(selected_card, "used")  
        new_visitor = visitors(
            name=form.name.data,
            contact_number=form.contact_number.data,
            meeting_person=form.meeting_person.data,
            purpose=purpose,
            Card_no=form.Card_no.data,
            card_type='some_value',  # Pass a value for card_type here
            start_date=datetime.utcnow(),  # Set a value for start_date
            end_date=datetime.utcnow() + timedelta(hours=4)

        )
        db.session.add(new_visitor)
        db.session.commit()
        update_cards(form)
        flash(f'Visitor {form.name.data} with card number {form.Card_no.data} has entered.', 'success')
        flash('Thank you for your request! Welcome to Fusion.')
        return redirect(url_for("home"))
    
    return render_template("submit.html", title="Visitor", form=form)

#Exit Page
@app.route("/exit", methods=['GET', 'POST'])
def exit():
    form = exitform()
    form.Card_no.choices = get_used_cards()  # Update choices initially
    if form.validate_on_submit() and form.Card_no.data:
        change_status(form)
        flash('Thank you for visiting Fusion. Have a great day!')
        return redirect(url_for('feedbackpage'))
    
    return render_template("exit.html", title='Exit Page', form=form)


@app.route("/exit-feedback", methods=['GET', 'POST'])
def exit_feedback():
    form = ExitFeedbackForm()

    if form.validate_on_submit():
        # Handle form submission
        card_no = form.Card_no.data
        professionalism = form.professionalism.data
        hospitality = form.hospitality.data
        hygiene = form.hygiene.data
        feedback_text = form.feedback_text.data

        # Update the card status to 'free' (exit functionality)
        change_status(form)

        # Save the feedback (if any ratings are provided)
        if professionalism or hospitality or hygiene or feedback_text:
            new_feedback = Feedback(
                category1=professionalism,
                category2=hospitality,
                category3=hygiene,
                feedback_text=feedback_text  # Add feedback text if needed
            )
            db.session.add(new_feedback)
            db.session.commit()

        flash('Thank you for your feedback and visit!', 'success')
        return redirect(url_for('home'))

    return render_template("exit_feedback.html", title='Exit and Feedback', form=form)


@app.route("/visitors")
def display_visitors():
    all_visitors, existing_cards = display_details()
    return render_template("visitors.html", title="Visitor Records", visitors=all_visitors, cards=existing_cards)

#Feedback Page
@app.route("/feedback", methods=['GET', 'POST'])
def feedbackpage():
    form = Feedbackform()
    if form.validate_on_submit():
        feedback = Feedback(
            category1=request.form['service_rating'],
            category2=request.form['quality_rating'],
            category3=request.form['support_rating'],
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template("feedback.html", form=form)

#Employee Section
@app.route("/employee", methods=['GET', 'POST'])
def employee():
    form = EmployeeEmailForm()
    otp_form = OTPForm()

    # Step 1: Email verification and OTP generation
    if form.validate_on_submit() and 'otp_submitted' not in session:
        otp = str(random.randint(100000, 999999))  # Generate OTP
        session['otp'] = otp
        session['email'] = form.email.data
        msg = Message('Your OTP Code', sender='your-email@gmail.com', recipients=[form.email.data])
        msg.body = f'Your OTP code is {otp}'
        mail.send(msg)
        flash(f'OTP has been sent to {form.email.data}. Please enter the OTP to verify your email.', 'info')
        session['otp_submitted'] = True
        return render_template('employee.html', form=form, otp_form=otp_form, show_otp=True)

    # Step 2: OTP verification
    elif otp_form.validate_on_submit() and 'otp_submitted' in session:
        if otp_form.otp.data == session.get('otp'):
            flash('Email verified successfully!', 'success')
            session.pop('otp')
            session.pop('otp_submitted')
            return redirect(url_for('employee_card_details', email=session['email']))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('employee.html', form=form, otp_form=otp_form, show_otp=True)
    
    # Initial load or email submission without OTP request yet
    return render_template('employee.html', form=form, otp_form=otp_form, show_otp=False)

@app.route("/employee/card-details/<email>", methods=['GET', 'POST'])
def employee_card_details(email):
    form = EmployeeCardDetailsForm()
    
    if form.validate_on_submit():
        card_type = form.card_type.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        card_no = form.Card_no.data
        
        # Insert new visitor, allowing nullable fields
        new_record = visitors(
            name=email,  # Email is used as name
            contact_number=None,  # Set to None if not provided
            meeting_person=None,  # Set to None if not provided
            purpose=None,  # Set to None if not provided
            date_visited=start_date,
            date_left=None,  # Assuming the visitor hasn't left yet
            Card_no=card_no,
            card_type=card_type,
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        flash(f'Card number {card_no} for {card_type} used from {start_date} to {end_date}.', 'success')
        return redirect(url_for('home'))
    
    return render_template('employee_card_details.html', form=form, email=email)

#Admin Page
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('email') != 'hashclg@gmail.com':  # Replace with the actual admin email
            abort(403)  # Forbidden access if email is not admin
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    form = EmployeeEmailForm()  # Assuming you want to use email form already defined
    otp_form = OTPForm()

    if form.validate_on_submit() and 'otp_submitted' not in session:
        if form.email.data == 'hashclg@gmail.com':  # Restrict login to only this email
            otp = str(random.randint(100000, 999999))  # Generate OTP
            session['otp'] = otp
            session['email'] = form.email.data
            msg = Message('Your OTP Code', sender='your-email@gmail.com', recipients=[form.email.data])
            msg.body = f'Your OTP code is {otp}'
            mail.send(msg)
            flash(f'OTP sent to {form.email.data}. Please enter it to verify.', 'info')
            session['otp_submitted'] = True
            return render_template('admin_login.html', form=form, otp_form=otp_form, show_otp=True)

    elif otp_form.validate_on_submit() and 'otp_submitted' in session:
        if otp_form.otp.data == session.get('otp'):
            flash('Login successful!', 'success')
            session.pop('otp')
            session.pop('otp_submitted')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('admin_login.html', form=form, otp_form=otp_form, show_otp=True)

    return render_template('admin_login.html', form=form, otp_form=otp_form, show_otp=False)

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/report")
@admin_required
def admin_report():
    all_visitors, _ = display_details()  # Assuming display_details() returns a list of visitors

    return render_template("admin_report.html", visitors=all_visitors)

@app.route("/admin/report/export")
@admin_required
def export_report_csv():
    all_visitors, _ = display_details()
    
    # Prepare CSV
    csv_data = []
    header = ['Name', 'Contact Number', 'Meeting Person', 'Purpose', 'Card No', 'Date Visited', 'Date Left']
    csv_data.append(header)

    for visitor in all_visitors:
        row = [
            visitor.name,
            visitor.contact_number,
            visitor.meeting_person,
            visitor.purpose,
            visitor.Card_no,
            visitor.date_visited.strftime("%Y-%m-%d %H:%M:%S") if visitor.date_visited else '',
            visitor.date_left.strftime("%Y-%m-%d %H:%M:%S") if visitor.date_left else ''
        ]
        csv_data.append(row)

    # Create response
    si = StringIO()
    writer = csv.writer(si)
    writer.writerows(csv_data)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=visitor_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == "__main__":
    app.run(debug=True)
