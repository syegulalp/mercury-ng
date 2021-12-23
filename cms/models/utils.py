import datetime
import regex as re
import urllib

DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H",
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S.%f",
)

DATE_FORMAT = DATE_FORMATS[0]

from cms.settings import SALT

import html
import pathlib
import os, sys
import hashlib
import smtplib
from email.message import EmailMessage

unsafe = lambda x: html.escape(x, True)


def fullpath(path_obj: pathlib.Path) -> pathlib.Path:
    if path_obj.exists():
        return path_obj.resolve()
    else:
        return pathlib.Path(os.getcwd(), path_obj).resolve()


def str_to_date(string: str) -> str:
    for format in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(string.strip(), format)
        except ValueError:
            continue
    raise ValueError(f"No valid time format found for {string}")


def date_to_str(dt: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.strftime(dt, DATE_FORMAT)


def next_month(dt: datetime.datetime) -> datetime.datetime:
    year = dt.year
    month = dt.month + 1
    if month == 13:
        month = 1
        year += 1
    return datetime.datetime(year=year, month=month, day=1)


def previous_month(dt: datetime.datetime, last_day=True) -> datetime.datetime:
    if last_day:
        return datetime.datetime(
            year=dt.year, month=dt.month, day=1
        ) + datetime.timedelta(seconds=-1)
    year = dt.year
    month = dt.month - 1
    if month == 0:
        month == 12
        year -= 1
    return datetime.datetime(year=year, month=month, day=1)


def remove_accents(input_str: str) -> str:
    import unicodedata

    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


basename_subs = (
    (r"[ \./]", r"-"),
    (r"<[^>]*>", r""),
    (r"[^a-z0-9\-]*", r""),
    (r"\-\-", r"-"),
)


def create_basename(basename: str) -> str:

    basename = remove_accents(basename)

    try:
        basename = basename.casefold()
    except Exception:
        basename = basename.lower()

    for pattern, replacement in basename_subs:
        basename = re.sub(pattern, replacement, basename)

    basename = urllib.parse.quote_plus(basename)

    return basename

    # TODO: enforce some maximum length limit? or should that be the responsibility of the caller?


def hash_password(password: str) -> str:
    hashed_pwd = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), SALT, 100000)
    return hashed_pwd


# def verify_password(password, hash):


def send_email(results: str):

    msg = EmailMessage()
    msg.set_content("\n".join(results))

    msg["Subject"] = f"Job runner"
    msg["From"] = "admin@infinimata.com"
    msg["To"] = "serdar@infinimata.com"

    # Send the message via our own SMTP server.
    try:
        s = smtplib.SMTP("localhost")
        s.send_message(msg)
        s.quit()
    except Exception as e:
        print("Email error: ", e, file=sys.stderr)


strip = re.compile("<[^>]*>")


def tagstrip(input: str):
    output = input
    for f in strip.finditer(input):
        output = output.replace(f[0], "")
    output = output.lstrip()
    return output
