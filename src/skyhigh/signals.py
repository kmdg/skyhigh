'''
Created on 10 Jan 2013

@author: euan
'''
from django.dispatch import Signal

user_requested_evaluation = Signal(providing_args=['user', 'request'])
user_requested_partnership = Signal(providing_args=['user', 'request'])