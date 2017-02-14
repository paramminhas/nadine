from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404, HttpRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from nadine import email
from nadine.models.usage import CoworkingDay
from nadine.models.resource import Room
from nadine.utils.slack_api import SlackAPI

from interlink.forms import MailingListSubscriptionForm
from interlink.models import IncomingMail

from members.models import UserNotification
from members.views.core import is_active_member


@login_required
@user_passes_test(is_active_member, login_url='member_not_active')
def connect(request, username):
    message = ""
    target = get_object_or_404(User, username=username)
    user = request.user
    action = request.GET.get('action')
    if action and action == "send_info":
        email.send_contact_request(user, target)
        message = "Email Sent"
    context = {'target': target, 'user': user, 'page_message': message, 'settings': settings}
    return render(request, 'members/connect/connect.html', context)


@login_required
def notifications(request):
    notifications = UserNotification.objects.filter(notify_user=request.user, sent_date__isnull=True)
    return render(request, 'members/connect/notifications.html', {'notifications': notifications})


@login_required
def add_notification(request, username):
    target = get_object_or_404(User, username=username)
    if UserNotification.objects.filter(notify_user=request.user, target_user=target, sent_date__isnull=True).count() == 0:
        UserNotification.objects.create(notify_user=request.user, target_user=target)
    return HttpResponseRedirect(reverse('member:connect:notifications', kwargs={}))


@login_required
def delete_notification(request, username):
    target = get_object_or_404(User, username=username)
    for n in UserNotification.objects.filter(notify_user=request.user, target_user=target):
        n.delete()
    return HttpResponseRedirect(reverse('member:connect:notifications', kwargs={}))


@login_required
def chat(request):
    user = request.user
    return render(request, 'members/connect/chat.html', {'user': user})


@login_required
@user_passes_test(is_active_member, login_url='member_not_active')
def mail(request):
    user = request.user
    if request.method == 'POST':
        sub_form = MailingListSubscriptionForm(request.POST)
        if sub_form.is_valid():
            sub_form.save(user)
            return HttpResponseRedirect(reverse('member:connect:email_lists'))
    context = {'user': user,
               'mailing_list_subscription_form': MailingListSubscriptionForm(),
               'settings': settings
               }
    return render(request, 'members/connect/mail.html', context)


@login_required
@user_passes_test(is_active_member, login_url='member_not_active')
def mail_message(request, id):
    message = get_object_or_404(IncomingMail, id=id)
    return render(request, 'members/connect/mail_message.html', {'message': message, 'settings': settings})


@login_required
def slack_redirect(request):
    return HttpResponseRedirect(reverse('member:connect:slack', kwargs={'username': request.user.username}))


@login_required
def slack(request, username):
    user = get_object_or_404(User, username=username)
    if not user == request.user:
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('member:profile:view', kwargs={'username': request.user.username}))

    if request.method == 'POST':
        try:
            slack_api = SlackAPI()
            slack_api.invite_user(user)
            messages.add_message(request, messages.INFO, "Slack Invitation Sent.  Check your email for further instructions.")
        except Exception as e:
            messages.add_message(request, messages.ERROR, "Failed to send invitation: %s" % e)

    context = {'user': user,
               'team_url': settings.SLACK_TEAM_URL,
               'settings': settings
               }
    return render(request, 'members/connect/slack.html', context)


@csrf_exempt
def slack_bots(request):
    # Stupid chat bot
    try:
        text = request.POST.get("text")[7:]
        SlackAPI().post_message(text)
    except Exception as e:
        return JsonResponse({'text': str(e)})
    return JsonResponse({})


# Copyright 2017 Office Nomads LLC (http://www.officenomads.com/) Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
