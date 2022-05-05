# Some utility functions in no particular order
# Note: None of these functions use arcpy - to facilitate testing without mocks

import logging
import os
import smtplib
import uuid
from collections import OrderedDict
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# Optional: add logging
# At this point there is no logging inside utility functions because I
# can't image what I'd want to log here - but the call to get logger is
# included in case I change my mind
log = logging.getLogger(__name__)


class SlicableOrderedDict(OrderedDict):
    """Create an ordered dictionary with option to slice like a list.

    Example
    --------
    .. code-block:: python

        pets = {3: 'turtles', 15: 'goldfish', 1: 'parrot', 5: 'mice'}
        ordered_pets = SlicableOrderedDict(
            sorted({key: val for key, val in pets.items()}.items(), reverse=True)
        )
        # Give me the 2 top-selling pets!
        ordered_pets[:2]

    See Also
    --------
    Source: https://stackoverflow.com/questions/30975339

    """

    def __getitem__(self, k):
        if not isinstance(k, slice):
            return OrderedDict.__getitem__(self, k)
        x = SlicableOrderedDict()
        for idx, key in enumerate(self.keys()):
            if k.start <= idx < k.stop:
                x[key] = self[key]
        return x


def acres_to_sq_miles(in_acres):
    """Convert acres to square miles.

    Parameters
    ----------
    in_acres: int
        Acres

    Returns
    -------
    float

    """
    return in_acres*0.0015625


def better_strftime(in_item, formatting="%m/%d/%Y"):
    """
    Improve strftime by guarding against non-datetime in_items.

    Parameters
    ----------
    in_item: any type
        Input to attempt time-formatting on
    formatting: str
        Datetime formatting style

    Returns
    -------
    Same type as ``in_item``
        Formatted (or not) in_item

    """
    try:
        return in_item.strftime(formatting)
    except AttributeError:
        return in_item


def create_temp_file(gdb_path):
    """Create a temp file name in the given path.

    Parameters
    ----------
    gdb_path: str
        path to geodatabase where feature class will be written.

    Returns
    -------
    str
        String corresponding to full path of gdb joined to a junk fc name.
    """
    junk_name = 't{}'.format(uuid.uuid4().hex[:10])
    return os.path.join(gdb_path, junk_name)


def ft_to_miles(linear_feet):
    """Convert linear feet to miles.

    Parameters
    ----------
    linear_feet: int
        Linear feet

    Returns
    -------
    float
    """
    return linear_feet*0.00018939


def join_args(args):
    """
    Join the entries of an iterable into a string.

    Example
    -------
    .. code-block:: python

    cat_names = ["Cleo", "Fluffy", "Jinxy"]
    join_args(cat_names)
    # result "Cleo', 'Fluffy', 'Jinxy"


    Parameters
    ----------
    args: iterable
        Elements to be joined

    Returns
    -------
    str
    """
    return "', '".join([str(x) for x in args])


def remove_bracket(in_str):
    """Remove angled bracket(s) from string.

    Parameters
    ----------
    in_str: str
        Input string to remove brackets from

    Returns
    -------
    str
        New string without brackets. If input not type string, function returns None.

    """
    try:
        return in_str.replace('<', '').replace('>', '')
    except AttributeError:
        pass


def send_mail(mail_server, fro, to, subject, text, files=[]):
    """Send an email.

    Parameters
    ----------
    fro: str
        Sender's email address
    to: list
        List of recipients
    subject: str
        Subject line
    text: str
        Body of email
    files: (str, optional)
        Files to attach to email. Defaults to None.

    Returns
    -------
    None
        Sends email (side effect)
    """
    assert type(to) == list
    assert type(files) == list
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)
    # serverName = "mail.dnr.wa.gov"
    # smtp = smtplib.SMTP(serverName)
    smtp = smtplib.SMTP(mail_server)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()



