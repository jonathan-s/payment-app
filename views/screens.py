from flask import redirect, url_for, flash, request
from wtforms import Form
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired
from peewee import DoesNotExist

from models.models import Account, TransferException, Transaction
from views import BaseView


class AccountView(BaseView):

    def provide_context(self):
        try:
            _id = self.parameters.get('id')
            account = Account.objects.get_account(_id)
            txns = Transaction.objects.transactions_for_account(_id)
            context = {'transactions': txns, 'account': account}
        except DoesNotExist:
            context = {'status': 404}
        return context


class AccountListView(BaseView):

    def provide_context(self):
        accounts = Account.objects.get_accounts()
        return {'accounts': accounts}


class PaymentForm(Form):
    from_account = SelectField('From Account', coerce=int, validators=[DataRequired()])
    to_account = SelectField('To Account', coerce=int, validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField()


class PaymentView(BaseView):

    methods = ['GET', 'POST']
    paymentform = PaymentForm()

    def provide_context(self):
        accounts = Account.objects.get_accounts()
        self.paymentform.from_account.choices = [(a.id, a.name) for a in accounts]
        self.paymentform.to_account.choices = [(a.id, a.name) for a in accounts]

        return {'form': self.paymentform}

    def post(self):
        self.paymentform.process(request.form)
        if self.paymentform.validate():
            amount = self.paymentform.amount.data
            try:
                Account.objects.transfer(from_id=self.paymentform.from_account.data,
                                         to_id=self.paymentform.to_account.data,
                                         amount=amount)
                flash('You transferred the sum {}'.format(amount))
            except TransferException as exc:
                return {'error': exc.message, 'form': self.paymentform}




class IndexView(BaseView):

    def provide_context(self):
        return {}
