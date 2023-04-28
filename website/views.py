from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Account, Note, Registry, Choice, Transaction, CustomerLimit, Card_Type, Credit_Card, Loan
from .function import get_account_number, get_credit_card_number
from .forms import ChoiceForm
from . import db
import json
from sqlalchemy.sql import func
from sqlalchemy import text

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = ChoiceForm()
    form.choices.choices = [(str(choice.id), choice.name) for choice in Choice.query.all()]
    if request.method == 'POST':
        if form.validate():
            choice_id = form.choices.data            
            choice = Choice.query.filter_by(id=choice_id).first()
            branch_id = request.form.get('branch_id')
            cust_id = request.form.get('cust_id')
            note = request.form.get('note')

            if len(note) < 1:
                flash('Note is Empty!', category='error') 
            else:
                new_note = Note(DATA=note, USER_ID=current_user.ID)  #providing the schema for the note 
                db.session.add(new_note) #adding the note to the database 
                db.session.commit()
            return redirect(url_for('views.choice_page',  choice_id=choice.id, branch_id=branch_id, cust_id=cust_id))
    return render_template('home.html', form=form, user=current_user)

@views.route('/choice/<int:choice_id>', methods=['GET', 'POST'])
@login_required
def choice_page(choice_id):
    form = ChoiceForm()
    form.choices.choices = [(str(choice.id), choice.name) for choice in Choice.query.all()]
    choice = Choice.query.filter_by(id=choice_id).first()
    branch_id = request.args.get('branch_id')
    cust_id = request.args.get('cust_id')
    if choice.id==1:
        if request.method == 'POST':
            cust_id = current_user.ID
            registry = Registry.query.get(cust_id)
            branches = registry.branch
            
            branch_ids = [branch.BRANCHCODE for branch in branches]
            branch_id=branch_ids[0]
            account_type = request.form.get('account_type')
            balance = request.form.get('initial_deposit')
            #setting the condition for one account holding per person
            user = Account.query.filter_by(CUST_ID=cust_id).first()
            if user:
                account_id = get_account_number(cust_id)
                flash(f"Account already found with ID {account_id}", "error")
            else:
                new_account = Account(BRANCHID =int(branch_id), CUST_ID =int(cust_id), ACCOUNTTYPE_ID=int(account_type), BALANCE=int(balance), UPDATED_ON=func.now())
                db.session.add(new_account)
                db.session.commit()
                flash('Account created!', category='success')
            return render_template('home.html', branch_id=int(branch_id), cust_id=int(cust_id), form=form, user=current_user)
        return render_template('account.html', choice_id=choice_id, form=form, user=current_user)
    
    elif choice.id==2:
        
        if request.method == 'POST':
            #let's figure out values of cust_ID and branch_id from existing data
            cust_id = current_user.ID
            registry = Registry.query.get(cust_id)
            branches = registry.branch
            branch_ids = [branch.BRANCHCODE for branch in branches]
            branch_id=branch_ids[0]
            
            cardtype = request.form.get('card-type')
            #let's get the value of limit assigned
            result = db.session.query(Card_Type, CustomerLimit.LIMIT_AMOUNT)\
                  .join(CustomerLimit, Card_Type.LIMIT_ID == CustomerLimit.LIMIT_ID)\
                  .filter(Card_Type.CARDTYPE_ID == cardtype)\
                  .first()
            _, limit_available = result
            #setting the condition for one credit holding per person
            credit = Credit_Card.query.filter_by(CUST_ID=cust_id).first()
            if credit:
                flash(f"Credit Card already issued",'error')
            else:
                new_card = Credit_Card(BRANCHID =int(branch_id), CUST_ID =int(cust_id), CARDTYPE_ID=int(cardtype), LIMIT_AVAILABLE=int(limit_available))
                db.session.add(new_card)
                db.session.commit()
                flash('Credit Card Issued!', category='success')
                print('3')
            return render_template('home.html', branch_id=int(branch_id), cust_id=int(cust_id), form=form, user=current_user)
        return render_template('credit_card.html', choice_id=choice_id, form=form, user=current_user)

    elif choice.id==3:
        if request.method == 'POST':
             #refer to functions.py for following functions
            account_id =get_account_number(current_user.ID)
            loan = Loan.query.filter_by(ACCOUNT_ID=account_id).first()
            if loan:
                flash(f"Loan already granted",'error')
            else:
                income = request.form.get('income')
                credit_score = request.form.get('credit_score')
                loan_amount = request.form.get('loan_amount')
                X = int(request.form.get('period'))
                due_date = datetime.utcnow() + relativedelta(years=X)
                #keeping the borrower's account ready for the transfer
                account= Account.query.filter_by(ACCOUNTID=account_id).first()
            
                #setting the eligiblity condition @ annual_income of 60k and credit_score of 700
                if (int(credit_score) >= 700 and int(income) >= 60000):
                    new_loan = Loan(ACCOUNT_ID = account_id, AMOUNT = int(loan_amount), OUTSTANDING = int(loan_amount), DUE_DATE = due_date, ANNUAL_INCOME = int(income), CREDIT_SCORE = int(credit_score)) 
                    #transfer the loan amount to borrower's account
                    account.BALANCE = account.BALANCE + int(loan_amount)
                    db.session.add(new_loan)
                    db.session.commit()
                    flash('Loan Approved!', category='success')
                else:
                    flash('Not Eligible for Loan', category='error')
                return render_template('home.html', form=form, user=current_user)
        return render_template('loan.html', choice_id=choice_id, user=current_user)

    elif choice.id==4:
        if request.method == 'POST':
            if request.form.get('category')=='account':
                amount = request.form.get('amount')
                description = request.form.get('description')
                #refer to functions.py for following functions
                account_id =get_account_number(current_user.ID)
                account = Account.query.filter_by(ACCOUNTID=account_id).first()
                if (account.BALANCE >= int(amount)):
                    new_transaction = Transaction(AMOUNT=int(amount),ACCOUNT_ID=account_id, TRANSACTION_DATE = func.now(), DESCRIPTION = description) 
                    account.BALANCE = account.BALANCE - int(amount)
                    db.session.add(new_transaction)
                    db.session.commit()
                    flash('Transaction successful!', category='success')
                else:
                    flash('Insufficient Funds', category='error')
            elif request.form.get('category')=='credit_card':
                amount = request.form.get('amount')
                description = request.form.get('description')
                #refer to functions.py for following functions
                card_id =get_credit_card_number(current_user.ID)
                card = Credit_Card.query.filter_by(CARDID=card_id).first()
                if (card.LIMIT_AVAILABLE >= int(amount)):
                    new_transaction = Transaction(AMOUNT=int(amount), CREDIT_CARD_ID=card_id, TRANSACTION_DATE = func.now(), DESCRIPTION = description) 
                    card.LIMIT_AVAILABLE = card.LIMIT_AVAILABLE - int(amount)
                    db.session.add(new_transaction)
                    db.session.commit()
                    flash('Transaction successful!', category='success')
                else:
                    flash('Insufficient Funds', category='error')
            return render_template('home.html', form=form, user=current_user)
        return render_template('transaction.html', choice=choice, user=current_user)
    elif choice.id==5:
        # Retrieve a complete transaction data for a given customerd
        account = Account.query.filter_by(CUST_ID=current_user.ID).first()
        transactions = Transaction.query.filter_by(ACCOUNT_ID=account.ACCOUNTID).all()
        
        # Pass the account balance and credit card limit to the template
        return render_template('delete_transactions.html', transactions=transactions,choice_id=choice_id, user=current_user)
    elif choice.id==6:
        # Retrieve account and credit card information for the customer
        account = Account.query.filter_by(CUST_ID=current_user.ID).first()
        credit_card = Credit_Card.query.filter_by(CUST_ID=current_user.ID).first()
        loan = Loan.query.filter_by(ACCOUNT_ID=account.ACCOUNTID).first()

        # Pass the account balance and credit card limit to the template
        return render_template('balances.html', account_balance=account.BALANCE,
                           credit_card_limit=credit_card.LIMIT_AVAILABLE, 
                           loan_outstanding = loan.OUTSTANDING, choice_id=choice_id, user=current_user)
        
@views.route('/delete_transaction', methods=['POST'])
@login_required
def delete_transaction():
    print('0')
    transactionID=request.form.get('transactionID')
    instance=Transaction.query.filter_by(TRANSACTIONID=transactionID).first()
    print('1')
    db.session.delete(instance)
    db.session.commit()
    print('2')
    account = Account.query.filter_by(CUST_ID=current_user.ID).first()
    transactions = Transaction.query.filter_by(ACCOUNT_ID=account.ACCOUNTID).all()
    return render_template('delete_transactions.html', transactions=transactions,choice_id=6, user=current_user)