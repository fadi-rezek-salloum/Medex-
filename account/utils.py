import os

from common.utils.send_activation_email import Activision
from django.template.loader import render_to_string
from django.utils.html import strip_tags

FRONTEND_URL = os.environ.get("FRONTEND_URL", "localhost:5173")


def send_activation_email(link, template, subject, to):
    absolute_url = FRONTEND_URL + link

    html_message = render_to_string(
        template, {"absolute_url": absolute_url, "website_link": FRONTEND_URL}
    )
    plain_message = strip_tags(html_message)

    try:
        Activision.send_email(
            subject=subject, plain_message=plain_message, html_message=html_message, email_to=to
        )
    except Exception as e:
        # Handle email sending errors
        print(f"Error sending activation email: {e}")
