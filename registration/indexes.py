
# for use when you are using django non-rel which needs
# a little help to be able to execute some 'complex' queries.

from django.contrib.auth.models import User
from dbindexer.api import register_index

register_index(User, {
    'username': 'iexact',
    'email': 'iexact',
    })