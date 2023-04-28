from .models import Account, Note, Registry, Choice, Transaction, BRANCH_CUSTOMER, Credit_Card
from . import db

def get_account_number(registry_id):
    account = db.session.query(Account) \
    .join(BRANCH_CUSTOMER, BRANCH_CUSTOMER.ID == Account.CUST_ID) \
    .join(Registry, Registry.ID == BRANCH_CUSTOMER.ID) \
    .filter(Registry.ID == registry_id) \
    .first()
    if account:
        return account.ACCOUNTID
    else:
        return None
    
def get_credit_card_number(registry_id):
    credit_card = db.session.query(Credit_Card) \
    .join(BRANCH_CUSTOMER, BRANCH_CUSTOMER.ID == Credit_Card.CUST_ID) \
    .join(Registry, Registry.ID == BRANCH_CUSTOMER.ID) \
    .filter(Registry.ID == registry_id) \
    .first()
    if credit_card:
        return credit_card.CARDID
    else:
        return None