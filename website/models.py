from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Sequence, text

class Note(db.Model):
    __tablename__ = 'NOTE'
    ID = db.Column(db.Numeric(6),Sequence('auto_increment'), primary_key=True)
    DATA = db.Column(db.String(128))
    DATE_CREATED = db.Column(db.DateTime(timezone=True), default=func.now())
    USER_ID = db.Column(db.Numeric(6), db.ForeignKey('REGISTRY.ID'))

class Branch(db.Model):
    __tablename__ = 'BRANCH'
    BRANCHCODE = db.Column(db.Numeric(4), primary_key=True)
    BRANCHNAME = db.Column(db.String(50), nullable=False)
    ADDRESS = db.Column(db.String(200), nullable=False)
    CITY = db.Column(db.String(50), nullable=False)
    STATE = db.Column(db.String(50), nullable = False)
    ZIP_CODE = db.Column(db.Numeric(5), nullable=False)

#make an associative entity between Registration and Branch to transform many to many relationship
# association table
class BRANCH_CUSTOMER(db.Model):
    __tablename__ = 'BRANCH_CUSTOMER'
    ID = db.Column(db.Integer, db.ForeignKey('REGISTRY.ID'), primary_key=True)
    BRANCHID = db.Column(db.Numeric(4), db.ForeignKey('BRANCH.BRANCHCODE'), primary_key=True)

class Registry(db.Model, UserMixin):
    __tablename__ = 'REGISTRY'
    ID = db.Column(db.Integer, Sequence('AUTO_INCREMENT_USERID'), primary_key=True)
    EMAILID = db.Column(db.String(100), unique=True)
    PASSWORD = db.Column(db.String(128), nullable=False)
    FIRSTNAME = db.Column(db.String(50), nullable=False)
    LASTNAME = db.Column(db.String(50), nullable=False)
    CUST_ADDRESS_1 = db.Column(db.String(100), nullable=False) 
    CUST_ADDRESS_2 = db.Column(db.String(100), nullable=True) 
    CITY = db.Column(db.String(50),nullable = False)
    STATE = db.Column(db.String(50), nullable = False)
    ZIP_CODE = db.Column(db.String(5), nullable = False)
    MOBILE_NUMBER = db.Column(db.String(15), nullable = False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    #defining relationship with notes
    notes = db.relationship('Note')
    #defining relationship with associative table
    branch = db.relationship('Branch', secondary='BRANCH_CUSTOMER',
                             primaryjoin='Registry.ID == BRANCH_CUSTOMER.ID',
                             secondaryjoin='Branch.BRANCHCODE == BRANCH_CUSTOMER.BRANCHID',
                             backref='customers')
    def get_id(self):
        return str(self.ID)

    

class Choice(db.Model):
    __tablename__ = 'CHOICE'
    id = db.Column(db.Numeric(1), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    page_url = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Choice(name='{self.name}', page='{self.page}')"
    
class CustomerLimit(db.Model):
    __tablename__ = 'CUSTOMERLIMIT'
    LIMIT_ID = db.Column(db.Numeric(3), nullable=False, primary_key=True)
    LIMIT_AMOUNT = db.Column(db.Numeric(6), nullable=False)
    CREDIT_LIMT = db.relationship('Card_Type', backref='credit_limit')


class Account_Type(db.Model):
    __tablename__ = 'ACCOUNT_TYPE'
    ACCOUNTTYPE_ID = db.Column(db.Numeric(3), nullable=False, primary_key=True)
    LIMIT_ID = db.Column(db.Numeric(3), db.ForeignKey('CUSTOMERLIMIT.LIMIT_ID'), nullable=False)
    ACCOUNTTYPE_NAME = db.Column(db.String(30), nullable=False)
    OVERDRAFT_ALLOWED = db.Column(db.Numeric(1), nullable=False)


class Account(db.Model):
    __tablename__ = 'ACCOUNT'
    ACCOUNTID = db.Column(db.Integer, Sequence('ACCOUNT_SEQ'), primary_key=True, nullable=False) 
    BRANCHID = db.Column(db.Numeric(4), db.ForeignKey('BRANCH_CUSTOMER.BRANCHID'), nullable=False)     
    CUST_ID = db.Column(db.Integer, db.ForeignKey('BRANCH_CUSTOMER.ID'), nullable=False)
    ACCOUNTTYPE_ID = db.Column(db.Numeric(3), db.ForeignKey('ACCOUNT_TYPE.ACCOUNTTYPE_ID'), nullable=False)
    BALANCE = db.Column(db.Numeric(9), nullable=False)
    UPDATED_ON = db.Column(db.Date, nullable=True)
    CREATED_ON = db.Column(db.DateTime(timezone=True), default=func.now())

    ACCOUNTTYPES=db.relationship('Account_Type', backref = 'no_of_accounts')
    branch_customer_val = db.relationship('BRANCH_CUSTOMER', backref=db.backref('account', uselist=False), 
                                      primaryjoin='and_(Account.CUST_ID==BRANCH_CUSTOMER.ID, '
                                                  'Account.BRANCHID==BRANCH_CUSTOMER.BRANCHID)')
    def get_id(self):
        return str(self.ACCOUNTID)

class Transaction(db.Model):
    __tablename__='TRANSACTION'
    TRANSACTIONID = db.Column(db.Integer, Sequence('ACCOUNT_SEQ'), primary_key=True, nullable=False) 
    ACCOUNT_ID = db.Column(db.Numeric(6,0), db.ForeignKey('ACCOUNT.ACCOUNTID'), nullable=True)
    CREDIT_CARD_ID =  db.Column(db.Numeric(6,0), db.ForeignKey('CREDIT_CARD.CARDID'), nullable=True)
    LOANID = db.Column(db.Numeric(6,0), db.ForeignKey('LOAN.LOANID'), nullable=True)
    AMOUNT = db.Column(db.Numeric(6,0), nullable=False)
    TRANSACTION_DATE = db.Column(db.Date, nullable=False)   
    DESCRIPTION = db.Column(db.String(200), nullable=True)
    with_account = db.relationship('Account', backref = 'account_trans')
    def get_id(self):
        return str(self.TRANSACTIONID)
    
class Card_Type(db.Model):
    __tablename__ = 'CARD_TYPE'
    CARDTYPE_ID = db.Column(db.Numeric(3), nullable=False, primary_key=True)
    LIMIT_ID = db.Column(db.Numeric(3,0),db.ForeignKey('CUSTOMERLIMIT.LIMIT_ID'), nullable=False) 
    CARDTYPE_NAME = db.Column(db.String(30), nullable=False)
    OVERDRAFT_ALLOWED = db.Column(db.Numeric(1,0), nullable = False)


class Credit_Card(db.Model):
    __tablename__ = 'CREDIT_CARD'
    CARDID = db.Column(db.Integer, Sequence('ACCOUNT_SEQ'), primary_key=True, nullable=False) 
    BRANCHID = db.Column(db.Numeric(4,0), db.ForeignKey('BRANCH_CUSTOMER.BRANCHID'), nullable=False)     
    CUST_ID = db.Column(db.Integer, db.ForeignKey('BRANCH_CUSTOMER.ID'), nullable=False)
    CARDTYPE_ID = db.Column(db.Numeric(3,0), db.ForeignKey('CARD_TYPE.CARDTYPE_ID'), nullable=False)
    LIMIT_AVAILABLE = db.Column(db.Numeric(6,0), nullable=False)
    ISSUE_DATE = db.Column(db.DateTime(timezone=True), default=func.now())
    #expires five years later
    EXPIRY_DATE = db.Column(db.DateTime(timezone=True), default= func.now() + text("INTERVAL '5' YEAR"))
    CVV = db.Column(db.Numeric(3,0,),Sequence('CVV'),nullable=False)

    CARDTYPES=db.relationship('Card_Type', backref = 'no_of_cards')
    card_customer_val = db.relationship('BRANCH_CUSTOMER', backref=db.backref('Credit_Card', uselist=False), 
                                      primaryjoin='and_(Credit_Card.CUST_ID==BRANCH_CUSTOMER.ID, '
                                                  'Credit_Card.BRANCHID==BRANCH_CUSTOMER.BRANCHID)')
    def get_id(self):
        return str(self.CARDID)
    
class Loan(db.Model):
    __tablename__ = 'LOAN'
    LOANID = db.Column(db.Numeric(6,0), Sequence('ACCOUNT_SEQ'), primary_key=True, nullable=False) 
    ACCOUNT_ID = db.Column(db.Numeric(6,0), db.ForeignKey('ACCOUNT.ACCOUNTID'), nullable=False)
    AMOUNT = db.Column(db.Numeric(9,0), nullable=False)
    OUTSTANDING = db.Column(db.Numeric(9,0), nullable=False)
    DISBURSEMENT_DATE = db.Column(db.DateTime(timezone=True), default=func.now())
    DUE_DATE = db.Column(db.Date, nullable=False)
    ANNUAL_INCOME = db.Column(db.Numeric(9,0), nullable=False)
    CREDIT_SCORE = db.Column(db.Numeric(5,2), nullable = False)
    account = db.relationship('Account', backref='related_account')
    def get_id(self):
        return str(self.LOANID)
