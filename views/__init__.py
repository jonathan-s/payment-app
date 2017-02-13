from flask.views import View
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

class BaseView(View):

    def __init__(self, template_name):
        self.template_name = template_name

    def provide_context(self):
        raise NotImplementedError

    def render_template(self, context={}):
        return render_template(self.template_name, **context)

    def dispatch_request(self, **kwargs):
        self.parameters = kwargs
        if request.method == 'POST':
            result = self.post()
            if result:
                return self.render_template(context=result)
            return redirect(url_for('payment'))

        context = self.provide_context()
        if context.get('status', 200) == 404:
            self.template_name = '404.html'

        return self.render_template(context=context), context.get('status')
