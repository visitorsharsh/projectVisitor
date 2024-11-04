from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, SubmitField, IntegerField,SelectField, RadioField, HiddenField, validators, EmailField, DateField
from wtforms.validators import DataRequired, Optional,Length, NumberRange,InputRequired,Email, Length, Regexp
from data import card, card_numbers, get_used_cards, get_unused_cards
from datetime import datetime

class visitorform(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50)])
    contact_number = StringField('Contact Number', 
                                 [validators.DataRequired(), 
                                  validators.Length(min=12, max=12), 
                                  Regexp(r'^\d{3}-\d{4}-\d{3}$', message="Invalid contact number.")])
    meeting_person = StringField('Meeting Person', 
                                 [validators.DataRequired(), validators.Length(min=3)])
    purpose = SelectField('Purpose', choices=[
        ('Internship', 'Internship'),
        ('Friends and Family', 'Friends and Family'),
        ('Interview', 'Interview'),
        ('Industry Friends', 'Industry Friends'),
        ('Employee', 'Employee'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    other_purpose = StringField('Other Purpose')
    #Card_no = SelectField('Card No', choices=[(str(i), str(i)) for i in range(1, 11)], validators=[DataRequired()])
    #Card_no = SelectField('Card No', choices=[('1', 'Card 1'), ('2', 'Card 2')], validate_choice=False)
    Card_no = SelectField('Card No', choices=[],  validate_choice=False)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(visitorform, self).__init__(*args, **kwargs)
        self.Card_no.choices = get_unused_cards()

class exitform(FlaskForm):
    Card_no = SelectField(coerce = int, choices=get_used_cards() , validate_choice=False)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(exitform, self).__init__(*args, **kwargs)
        self.Card_no.choices = get_used_cards() 

class Feedbackform(FlaskForm):
    category1 = IntegerField('Service_Rating')
    category2 = IntegerField('Quality_Rating')
    category3 = IntegerField('Support_Rating')
    submit = SubmitField('Submit')

class IntroForm(FlaskForm):
    entry = SubmitField('Entry')
    exit = SubmitField('Exit')
    value = HiddenField()
    def set_value(self, button_pressed):
        if button_pressed == 'entry':
            self.value.data = 1
        elif button_pressed == 'exit':
            self.value.data = 2

# class EmployeeForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
#     email = EmailField('Email', validators=[DataRequired(), Email()])
#     otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
#     #Card_no = SelectField('Card No', choices=[(str(i), str(i)) for i in range(1, 11)], validators=[DataRequired()])
#     submit = SubmitField('Submit')

class EmployeeEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Verify Email')

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Submit OTP')

class EmployeeCardDetailsForm(FlaskForm):
    # SelectField for card type with predefined choices
    card_type = SelectField('Employee Type', choices=[('FII', 'FII'), ('Other Region', 'Other Region')], validators=[DataRequired()])
    
    # Removed start_date field since it will be set by the system's exact time after OTP verification
    # end_date should remain as it needs to be selected by the user
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    
    # Card_no choices are dynamically populated from get_unused_cards()
    Card_no = SelectField('Card No', choices=[], validators=[DataRequired()])
    
    submit = SubmitField('Submit Details')
    
    def __init__(self, *args, **kwargs):
        super(EmployeeCardDetailsForm, self).__init__(*args, **kwargs)
        # Populate Card_no choices dynamically from the available card pool
        self.Card_no.choices = get_unused_cards()

class ExitFeedbackForm(FlaskForm):
    # Card No dropdown, required
    Card_no = SelectField('Card No', choices=[], validators=[DataRequired()])
    card_holder_name = StringField('Card Holder', render_kw={'readonly': True})  # Read-only field for the name
    # Rating fields for feedback (optional)
    professionalism = RadioField('Professionalism', choices=[('1', '★'), ('2', '★★'), ('3', '★★★'), ('4', '★★★★'), ('5', '★★★★★')], validators=[Optional()])
    hospitality = RadioField('Hospitality', choices=[('1', '★'), ('2', '★★'), ('3', '★★★'), ('4', '★★★★'), ('5', '★★★★★')], validators=[Optional()])
    hygiene = RadioField('Hygiene', choices=[('1', '★'), ('2', '★★'), ('3', '★★★'), ('4', '★★★★'), ('5', '★★★★★')], validators=[Optional()])

    # Optional feedback text area
    feedback_text = TextAreaField('Feedback', validators=[Optional()])

    # Submit button
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ExitFeedbackForm, self).__init__(*args, **kwargs)
        # Populate Card_no choices dynamically
        #self.Card_no.choices = get_used_cards()
        self.Card_no.choices = [('', 'Select Card No')] + get_used_cards()