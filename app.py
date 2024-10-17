import csv
from init import app, db 
from flask import Flask, render_template, url_for, flash, redirect, request, session, abort, make_response, jsonify
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
    Employee,
    fetch_report_data,
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
    #print(cards)  # Debugging: Print the cards to ensure they're populated
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
        return jsonify({'success': True})  # JSON response for success
        return redirect(url_for("home"))
    
    
    return render_template("submit.html", title="Visitor", form=form)

#Exit Page
@app.route("/exit", methods=['GET', 'POST'])
def exit():
    return redirect(url_for('exit_feedback'))

# Exit Feedback Page (replaces the old exit form)
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

        # Return JSON response for AJAX
        return jsonify({'success': True})

    return render_template("exit_feedback.html", title='Exit and Feedback', form=form)

@app.route("/visitors")
def display_visitors():
    all_visitors, existing_cards = display_details()
    return render_template("visitors.html", title="Visitor Records", visitors=all_visitors, cards=existing_cards)

# Employee Section
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
        
        # Flash message for OTP sent
        flash('OTP Sent Successfully', 'info')
        
        session['otp_submitted'] = True
        return render_template('employee.html', form=form, otp_form=otp_form, show_otp=True)

    # Step 2: OTP verification
    elif otp_form.validate_on_submit() and 'otp_submitted' in session:
        if otp_form.otp.data == session.get('otp'):
            flash('Email verified successfully!', 'success')
            
            # Capture the exact time when OTP is verified successfully (start time)
            session['start_time'] = datetime.now()

            session.pop('otp')
            session.pop('otp_submitted')
            return redirect(url_for('employee_card_details', email=session['email']))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('employee.html', form=form, otp_form=otp_form, show_otp=True)
    
    return render_template('employee.html', form=form, otp_form=otp_form, show_otp=False)

@app.route("/employee/card-details/<email>", methods=['GET', 'POST'])
def employee_card_details(email):
    form = EmployeeCardDetailsForm()
    
    if form.validate_on_submit():
        card_type = form.card_type.data
        start_date = datetime.today() # Automatically set start date
        print(type(start_date))
        end_date = form.end_date.data
        print(type(end_date))
        card_no = form.Card_no.data
        
        # Insert new employee record
        new_employee = Employee(
            employee_type=card_type,
            email=email,
            start_date=start_date,
            end_date=end_date,
            card_no=card_no
        )
        
        db.session.add(new_employee)
        db.session.commit()
        update_cards(form)
        flash(f'Card number {card_no} for {card_type} used from {start_date} to {end_date}.', 'success')
        return redirect(url_for('home'))  # Redirect after successful submission
    
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
    # SQLAlchemy query to fetch data from the visitors table
    visitors_query = db.session.query(
        visitors.name.label('identifier'),  # 'identifier' for name or email
        visitors.Card_no.label('card_no'),
        visitors.start_date,
        visitors.end_date,
        db.literal('Visitor').label('type')  # Add a 'type' column with value 'Visitor'
    ).all()
    
    # SQLAlchemy query to fetch data from the employees table
    employees_query = db.session.query(
        Employee.email.label('identifier'),  # 'identifier' for employee email
        Employee.card_no.label('card_no'),
        Employee.start_date,
        Employee.end_date,
        db.literal('Employee').label('type')  # Add a 'type' column with value 'Employee'
    ).all()

    # Combine both visitors and employees into a single list
    combined_data = visitors_query + employees_query

    # Render the combined data in the admin report
    return render_template("admin_report.html", report_data=combined_data)

@app.route("/admin/report/export")
@admin_required
def export_report_csv():
    # SQLAlchemy queries for visitors and employees
    visitors_query = db.session.query(
        visitors.name.label('identifier'),
        visitors.Card_no.label('card_no'),
        visitors.start_date,
        visitors.end_date,
        db.literal('Visitor').label('type')  # Add a 'type' column for visitors
    ).all()
    
    employees_query = db.session.query(
        Employee.email.label('identifier'),
        Employee.card_no.label('card_no'),
        Employee.start_date,
        Employee.end_date,
        db.literal('Employee').label('type')  # Add a 'type' column for employees
    ).all()

    # Combine the data
    combined_data = visitors_query + employees_query

    # Prepare CSV with the additional 'Type' column
    csv_data = []
    header = ['Name/Email', 'Card No', 'Start Date', 'End Date', 'Type']
    csv_data.append(header)

    # Add combined data (both visitors and employees) to the CSV
    for row in combined_data:
        csv_data.append([
            row.identifier,
            row.card_no,
            row.start_date.strftime("%Y-%m-%d %H:%M:%S") if row.start_date else '',
            row.end_date.strftime("%Y-%m-%d %H:%M:%S") if row.end_date else '',
            row.type  # Add the 'type' value
        ])
    
    # Create CSV response
    si = StringIO()
    writer = csv.writer(si)
    writer.writerows(csv_data)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/temp-report', methods=['GET'])
def temp_report():
    report_data = fetch_report_data()  # Fetch the combined report data
    
    # Temporary rendering of the report data
    return render_template('temp_report.html', report_data=report_data)

@app.route('/reporting', methods=['GET'])
def reporting():
    # SQLAlchemy query to fetch data from both visitors and employees tables
    visitors_query = db.session.query(
        visitors.name.label('identifier'),
        visitors.Card_no,
        visitors.start_date,  # Ensure this field exists in the visitors model
        visitors.end_date     # Ensure this field exists in the visitors model
    ).all()
    
    employees_query = db.session.query(
        Employee.email.label('identifier'),
        Employee.card_no,
        Employee.start_date,  # Ensure this field exists in the Employee model
        Employee.end_date     # Ensure this field exists in the Employee model
    ).all()
    
    # Combine both queries into one list
    report_data = visitors_query + employees_query

    return render_template('reporting.html', report_data=report_data)


if __name__ == "__main__":
    app.run(debug=True)



