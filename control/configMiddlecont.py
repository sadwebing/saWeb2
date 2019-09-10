#-_- coding: utf-8 -_-
from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
import json, logging, requests, re

logger = logging.getLogger('django')

choices_s = (
        (1, '启用'), 
        (0, '禁用'),
    )