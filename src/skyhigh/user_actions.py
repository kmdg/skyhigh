__author__ = 'michael'

from django.utils import timezone

from django.contrib.auth.models import User

import models
import constants

from skyhigh.api import product as skyhigh_product_api
from skyhigh.api import marketo_api as skyhigh_marketo_api
from skyhigh.api import service_cloud_api as skyhigh_service_cloud_api

def action_new_profile_registration(user):
    skyhigh_marketo_api.sync_new_profile_registration.delay(user.id)

def action_profile_update(user):
    skyhigh_marketo_api.sync_profile_update.delay(user.id)
    skyhigh_product_api.update_profile(user)

def action_login(user):
    action = constants.ACTIVITY_LOGIN

    user.profile.login_count += 1
    user.profile.save()

    if (timezone.now() - user.last_login).days >= 1:
        user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

def action_logout(user):
    action = constants.ACTIVITY_LOGOUT

    if (timezone.now() - user.last_login).days >= 1:
        user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

def action_blog_entry_comment(user, blog_entry):
    action = constants.ACTIVITY_ACTION_BLOG_ENTRY_COMMENT

    if blog_entry.created_by != user:
        user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

def action_product_evaluation_request(user, from_new_profile=False):
    action = constants.ACTIVITY_ACTION_EVALUATION_REQUEST

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

    if not from_new_profile:
        skyhigh_marketo_api.sync_product_evaluation_request.delay(user.id)

def action_product_evaluation_request_approved(user):
    action = constants.ACTIVITY_ACTION_EVALUATION_REQUEST_APPROVED

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)
    
    skyhigh_product_api.create_evaluation_account(user)

def action_partnership_request(user):
    action = constants.ACTIVITY_ACTION_PARTNERSHIP_REQUEST

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

    skyhigh_marketo_api.sync_partnership_request.delay(user.id)

def action_partnership_request_approved(user):
    action = constants.ACTIVITY_ACTION_PARTNERSHIP_REQUEST_APPROVED

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

def action_contact_message_sent(user):
    action = constants.ACTIVITY_ACTION_CONTACT_MESSAGE_SENT

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

    skyhigh_marketo_api.sync_contact_message_sent.delay(user.id)


def action_contact_message_read(user):
    action = constants.ACTIVITY_ACTION_CONTACT_MESSAGE_READ

    models.UserActivity.track(user, action)

def action_contact_message_responded(user):
    action = constants.ACTIVITY_ACTION_CONTACT_MESSAGE_RESPONDED

    models.UserActivity.track(user, action)

def action_support_case_submitted(case):
    action = constants.ACTIVITY_ACTION_SUPPORT_CASE_SUBMITTED

    user = case.created_by

    user.profile.update_marketo_score(action)

    models.UserActivity.track(user, action)

    skyhigh_service_cloud_api.sync_case.delay(case.id)
    
def action_deal_request_submitted(user):
    skyhigh_marketo_api.sync_deal_request_submitted.delay(user.id)