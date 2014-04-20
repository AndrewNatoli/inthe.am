import time
from urlparse import urljoin

from behave import given, when, then, step
from selenium.common.exceptions import (
    StaleElementReferenceException,
)

from django.conf import settings
from django.contrib.auth.models import User


@step(u'the user accesses the url "{url}"')
def user_accesses_the_url(context, url):
    full_url = urljoin(context.config.server_url, url)
    context.browser.visit(full_url)
    context.browser.execute_script(
        u"window.localStorage.setItem('disable_ticket_stream', 'yes');"
    )
    time.sleep(2)


@given(u'the user is logged-in')
def user_is_logged_in(context):
    context.execute_steps(u'''
        when the user accesses the url "/"
        and the user accesses the url "/login/google-oauth2/"
        and the user enters his credentials if necessary
        and the user accepts the terms and conditions
    ''')


@step(u'the user accepts the terms and conditions')
def user_accepts_terms_and_conditions(context):
    time.sleep(1)
    page_h2 = context.browser.find_by_tag('h2')
    if page_h2.first.text == "Terms and Conditions of Use of Inthe.AM":
        context.browser.find_by_id("accept-terms").first.click()


@given(u'the test account user does not exist')
def test_account_user_does_not_exist(context):
    count = User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).count()
    assert count == 0, "Test account user does appear to exist."


@step(u'the user waits for {num} seconds')
def wait_for_a_bit(context, num):
    time.sleep(int(num))


@when(u'the user clicks the link "{anchor_text}"')
def clicks_link(context, anchor_text):
    matches = context.browser.find_link_by_partial_text(anchor_text)
    for match in matches:
        try:
            if match.visible:
                match.click()
                return
        except StaleElementReferenceException:
            pass
    assert False, "Of %s anchors with text %s, none were clickable." % (
        len(matches),
        anchor_text,
    )


@when(u'the user enters the text "{text}" into the field named "{field}"')
def user_enters_text_into_field(context, text, field):
    context.browser.find_by_name(field).type(text)


@when(u'the user clicks the button labeled "{label}"')
def user_clicks_button_labeled(context, label):
    for button in context.browser.find_by_tag("button"):
        if button.visible and button.text == label:
            button.click()
            return
    assert False, "No button with label %s could be clicked" % label


@when(u'the user enters his credentials if necessary')
def user_enters_credentials(context):
    login_form = context.browser.find_by_id('Email')
    if login_form:
        context.browser.find_by_id('Email').type(
            settings.TESTING_LOGIN_USER
        )
        context.browser.find_by_id('Passwd').type(
            settings.TESTING_LOGIN_PASSWORD
        )
        context.browser.find_by_id('signIn').first.click()

    needs_approval = context.browser.find_by_id('submit_approve_access')
    if needs_approval:
        time.sleep(2)
        needs_approval.first.click()


@then(u'a new account will be created using the test e-mail address')
def testing_account_created(context):
    count = User.objects.filter(
        email=settings.TESTING_LOGIN_USER
    ).count()
    assert count == 1, "Test account user does not exist."


@step(u'the page contains the heading "{heading}"')
def page_contains_heading(context, heading):
    all_headings = []
    for tag in ['h1', 'h2', 'h3']:
        these_headings = [e.text for e in context.browser.find_by_tag(tag)]
        if heading in these_headings:
            return
        all_headings.extend(these_headings)
    assert False, \
        "Page should contain '%s', has '%s'" % (
            heading, all_headings
        )
