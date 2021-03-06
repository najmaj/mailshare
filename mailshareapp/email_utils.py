# License: https://github.com/RobFisher/mailshare/blob/master/LICENSE

import models
import search
from plaintext import plaintext2html
from lxml.html.clean import Cleaner
import lxml.html.defs
import re
from django.conf import settings

outlook_otags = re.compile('</*o:p>')

def sanitise_html(body):
    """Given the text of a HTML email, return HTML suitable for rendering on a web page."""
    # Discussion of sanitising HTML here:
    # http://stackoverflow.com/questions/699468/python-html-sanitizer-scrubber-filter

    # remove empty paragraphs from Outlook emails that look like <o:p>
    # or </o:p>. These were causing large line breaks between
    # paragaphs because lxml replaces them with <p></p>.
    body=outlook_otags.sub('', body)

    # Outlook emails contain span elements with style attributes. Add
    # style to the set of safe attributes allowed.
    outlook_safe_attrs = set(lxml.html.defs.safe_attrs)
    outlook_safe_attrs.add('style')
    lxml.html.defs.safe_attrs = frozenset(outlook_safe_attrs)
    cleaner = Cleaner(style=False)
    return cleaner.clean_html(body)


def mail_body_html(mail):
    """Given a mailshareapp.models.Mail object, returns the body formatted as HTML."""
    # For now assume all email bodies are HTML or plain text
    if mail.content_type == 'text/html':
        return sanitise_html(mail.body)
    else:
        return plaintext2html(mail.body)


def contact_to_html(contact, search_object=None):
    """Given a mailshareapp.models.Contact object, return a string representing it in HTML."""
    sender_search = search.get_contact_id_search(contact.id)
    if search_object:
        sender_search = search_object.add_and(sender_search)
    result = '<a href="' + sender_search.get_url_path()
    if contact.name != '':
        result += '" title="' + contact.address + '">' + contact.name + '</a>'
    else:
        result += '">' + contact.address + '</a>'
    return result


def contacts_queryset_to_html(contacts, search_object):
    """Given a QuerySet of contacts, return a string representing them in HTML."""
    if len(contacts) == 0:
        return ''
    result = contact_to_html(contacts[0], search_object)
    for contact in contacts[1:]:
        result += ', '
        result += contact_to_html(contact, search_object)
    return result


def mail_permalink_html(mail):
    """Generate permalink to a mail in HTML."""
    mail_search = search.get_mail_id_search(mail.id)
    result = '<a href="' + mail_search.get_url_path()
    result += '">permalink</a>'
    return result


def strip_subject_prefixes(subject):
    """Returns the specified mail subject string stripped of replying and forwarding prefixes."""
    prefixes = ['re', 'fw', 'fwd']
    subject_lower = subject.lower()
    for prefix in prefixes:
        if subject_lower.startswith(prefix + ' ') or subject_lower.startswith(prefix + ':'):
            subject = subject[len(prefix)+1:].strip()
            # recurse because subjects often have multiple "re: Re: Fwd: re:" prefixes
            subject = strip_subject_prefixes(subject)
            break
    return subject


def mail_thread_link_html(mail):
    """Generate a link to the mail's thread in HTML."""
    result = 'thread'
    subject = strip_subject_prefixes(mail.subject)
    if len(subject) > 3:
        subject_search = search.get_subject_ends_with_search(subject)
        result = '<a href="' + subject_search.get_url_path()
        result += '">thread</a>'
    return result


def mail_delete_html(mail):
    """Generate delete link for a mail in HTML."""
    result = '<a href="#" onclick="fetch_delete_mail(' + str(mail.id) + '); return false;">delete</a>'
    return result


def mail_contacts_bar_html(mail, search_object):
    """Given a mailshareapp.models.Mail object, generate the contacts bar in HTML."""
    result = '<div class="recipients"><p style="float:left;">From: '
    result += contact_to_html(mail.sender, search_object) + '</p><p style="float:right;">'
    if settings.MAILSHARE_ENABLE_DELETE:
        result += mail_delete_html(mail) + ' | '
    result += mail_thread_link_html(mail) + ' | '
    result += mail_permalink_html(mail) + '</p><div style="clear:both;"></div>'
    result += 'To: '
    result += contacts_queryset_to_html(mail.to.all(), search_object)
    result += '<br />Cc: '
    result += contacts_queryset_to_html(mail.cc.all(), search_object)
    result += '</p></div>'
    return result
