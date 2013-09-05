'''
Created on 16 Jan 2013

@author: euan
'''
from django.core.management.base import BaseCommand
from django.contrib.auth import models as auth_models

from unobase.blog import models as blog_models
from unobase.forum import models as forum_models

#==============================================================================
class Command(BaseCommand):
    """
    Initial base setup
    """
    #--------------------------------------------------------------------------
    def handle(self, *args, **options):
        # Blogs
        blog_models.Blog.objects.create(title='Corporate Blog')
        blog_models.Blog.objects.create(title='Engineering Blog')

        # Forum
        forum_models.Forum.objects.create(title='Support')

        permissions = auth_models.Permission.objects.filter(codename='can_moderate')
        group = auth_models.Group.objects.create(name='Forum Moderators')

        for permission in permissions:
            group.permissions.add(permission)