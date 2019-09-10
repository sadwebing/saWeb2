from django.shortcuts               import render
from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponse
from django.views.decorators.csrf   import csrf_exempt, csrf_protect
from saWeb2                         import settings
import json, logging, requests, re

logger = logging.getLogger('django')

# Create your views here.
@csrf_exempt
def Index(request):
    title = u'默认页面'
    global username, role, clientip
    username = request.user.username
    try:
        role = request.user.userprofile.role
    except:
        role = 'none'
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        clientip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        clientip = request.META['REMOTE_ADDR']
    logger.info('%s is requesting %s' %(clientip, request.get_full_path()))

    # return HttpResponse(json.dumps({
    #           "code": 0
    #           ,"msg": "登入成功"
    #           ,"data": {
    #             "csrftoken": "c262e61cd13ad99fc650e6908c7e5e65b63d2f32185ecfed6b801ee3fbdd5c0a"
    #           }
    #         })
    #     )

    return render(
        request,
        'home.html',
    )