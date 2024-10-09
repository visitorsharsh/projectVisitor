from init import db, app
from datetime import datetime, timedelta

card_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

class visitors(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    contact_number = db.Column(db.String(10), nullable=True)  # Allows NULL values
    meeting_person = db.Column(db.String(50), nullable=True)  # Allows NULL values
    purpose = db.Column(db.String(50), nullable=True)  # Allows NULL values
    date_visited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow() + timedelta(hours=5, minutes=30))
    date_left = db.Column(db.DateTime)
    Card_no = db.Column(db.Integer, nullable=False)
    card_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"visitors('{self.name}','{self.purpose}',{self.Card_no})"

class card(db.Model):
    Card_no = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=True)  # Optional for employees
    department = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    date_joined = db.Column(db.DateTime, nullable=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category1 = db.Column(db.Integer, nullable=False)
    category2 = db.Column(db.Integer, nullable=False)
    category3 = db.Column(db.Integer, nullable=False)

# Initializing all cards from 1 to 10 as free
card_numbers = {i: 'free' for i in range(1, 11)}

def get_unused_cards():
    """ Return a list of unused cards for the dropdown. """
    return [(str(k), str(k)) for k, v in card_numbers.items() if v == 'free']

def get_used_cards():
    """ Return a list of used cards for display or exit. """
    return [(str(k), str(k)) for k, v in card_numbers.items() if v == 'used']

def update_card_status(card_no, status):
    card_in_db = card.query.filter_by(Card_no=card_no).first()
    if card_in_db:
        card_in_db.status = (status == 'used')
        db.session.commit()

# Functions for card management
def put_cards(card_numbers):
    with app.app_context():
        for card_number in card_numbers:
            existing_card = card.query.filter_by(Card_no=card_number).first()
            if not existing_card:
                new_card = card(Card_no=card_number)
                db.session.add(new_card)
        db.session.commit()

def update_cards(form):
    with app.app_context():
        new_card = card.query.filter_by(Card_no=form.Card_no.data).first()
        new_card.status = True
        db.session.commit()
        return "Update successful!"

def get_cards():
    with app.app_context():
        cards = card.query.all()
        c_list = [i.Card_no for i in cards]
    print(c_list)
    return c_list

def display_details():
    with app.app_context():
        all_visitors = visitors.query.all()
        return all_visitors, display_card()

def display_card():
    with app.app_context():
        cards_in_use = card.query.filter_by(status=True).all()
        return cards_in_use

def get_used_cards():
    with app.app_context():
        cards = card.query.filter_by(status=True).all()
        return [(i.Card_no, str(i.Card_no)) for i in cards]

def get_unused_cards():
    with app.app_context():
        cards = card.query.filter_by(status=False).limit(10)
        return [(i.Card_no, str(i.Card_no)) for i in cards]

def change_status(form):
    with app.app_context():
        card_in_use = card.query.filter_by(Card_no=form.Card_no.data).first()
        card_in_use.status = False
        db.session.commit()

        card_number = form.Card_no.data
        exit_datetime = datetime.utcnow()  # Current time for exit

        visitor = visitors.query.filter_by(Card_no=card_number, date_left=None).first()
        if visitor:
            visitor.date_left = exit_datetime  # Record exit time
            # Optional: You can log the exit time separately if needed
            db.session.commit()
            return "Exit time noted!"
        return "Visitor not found!"
