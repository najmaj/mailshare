# License: https://github.com/RobFisher/mailshare/blob/master/LICENSE

import email
import datetime
import warnings
import poll_imap_email
from mailshare.mailshareapp.models import Mail, Contact

def get_plain_body(message):
    """Search all the MIME parts of the email.message.Message and return the plain text body."""
    plain_part = None
    for part in message.walk():
        # for now we assume the first "text/plain" part is what we want
        if part.get_content_type() == 'text/plain':
            plain_part = part
            # we've found it. Get out of here!
            break

        # settle for the first non-multipart payload in case there is no text/plain,
        # but keep looking
        if plain_part == None and not part.is_multipart():
            plain_part = part

    # decode any Base64 and convert to utf-8 if needed
    plain_part_payload = ''
    if plain_part:
        plain_part_payload = plain_part.get_payload(decode=True)
        charset = plain_part.get_content_charset()
        if charset != None and charset != 'utf-8':
            plain_part_payload = plain_part_payload.decode(charset).encode('utf-8')

    return plain_part_payload


def get_or_add_contact(name, address):
    """
    Looks up the email address in the Contact table. If the address does not exist in the table
    it is added. In both cases the matching Contact object is returned.

    Email addresses are considered to be case insensitive for now. While not strictly true,
    this seems more useful than the alternative.
    """
    contact_list = Contact.objects.filter(address__iexact=address)
    result = None
    if len(contact_list) == 0:
        contact = Contact(name=name, address=address)
        contact.save()
        result = contact
    else:
        result = contact_list[0]
    return result


def add_contacts_to_mail(address_field, address_headers):
    """
    Parse out email addresses and add them to the Mail table.
    address_field: a ManyToManyField linked to the Contact table
    address_header: headers retrieved with email.email.Message.get_all
    """
    if address_headers != None:
        addresses = email.utils.getaddresses(address_headers)
        for (name, address) in addresses:
            contact = get_or_add_contact(name, address)
            address_field.add(contact)


def datetime_from_email_date(email_date):
    """
    Returns a Python datetime object suitable for storing in the database given
    the email Date header string. These should comply with this specification:
    http://cr.yp.to/immhf/date.html
    """
    d = email.utils.parsedate_tz(email_date)
    dt = datetime.datetime(*d[0:6])

    # now we need to subtract the time zone offset to get a UTC time
    tz_offset = datetime.timedelta(seconds=d[9])
    dt = dt - tz_offset
    return dt


def add_message_to_database(message):
    """Add the message to the database if it is unique according to its Message-ID field."""
    message_id = message.get('Message-ID')
    matching_messages = Mail.objects.filter(message_id__exact=message_id)
    if len(matching_messages) == 0:
        m = Mail()
        m.sender = get_or_add_contact(*email.utils.parseaddr(message.get('from')))
        m.subject = message.get('Subject')
        m.date = datetime_from_email_date(message.get('Date'))
        m.message_id = message.get('Message-ID')
        m.thread_index = message.get('Thread-Index')
        if m.thread_index == None:
            m.thread_index = ''
        m.body = get_plain_body(message)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            m.save()
        add_contacts_to_mail(m.to, message.get_all('to'))
        add_contacts_to_mail(m.cc, message.get_all('cc'))


def print_message_headers(message):
    """Given an email.message.Message object, print out some interesting headers."""
    print "To: " + message.get('To')
    print "From: " + message.get('From')
    print "Subject: " + message.get('Subject')
    print "Date: " + message.get('Date')

mail_file_name = 'mailfile'

def quick_test(from_file=False):
    messages = None
    if from_file:
        mail_file = open(mail_file_name, 'r')
        messages = poll_imap_email.read_messages(mail_file)
    else:
        mail_file = open(mail_file_name, 'a')
        messages = poll_imap_email.fetch_messages(10, mail_file)
    for message in messages:
        add_message_to_database(message)

def test_email(n):
    """Test the nth email in the file."""
    mail_file = open(mail_file_name, 'r')
    messages = poll_imap_email.read_messages(mail_file)
    print_message_headers(messages[n])
    body = get_plain_body(messages[n])
    print body

if __name__ == '__main__':
    messages = poll_imap_email.fetch_messages()
    for message in messages:
        print_message_headers(message)
        plain_body = get_plain_body(message)
        print("-----")
        print(plain_body)
        print("-----")
        print("")
