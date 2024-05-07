import asyncio
import getpass
import re

from validate_email import validate_email

from codej.dirs import settings
from codej.auth.attri import groups, USER_PATTERN
from codej.auth.pg import check_address, check_username, create_user

USERNAME = 'Enter your username: '
MESSAGE = '''Username must be from 3 to 16 symbols
(latin letters, russian letters including `ё`,
numbers, dots, hyphens, underscores)
and start with any letter, latin or russian.
'''
EMAIL = 'Enter your email address: '
PASSWORD = 'Enter your password: '


def get_username():
    pattern = re.compile(USER_PATTERN)
    username = input(USERNAME)
    while True:
        if not pattern.match(username):
            print(MESSAGE)
            username = input(USERNAME)
            continue
        if asyncio.run(check_username(settings, username)):
            print('This name is already registered. Try again.\n')
            username = input(USERNAME)
            continue
        return username


def get_email():
    address = input(EMAIL)
    while True:
        if not validate_email(address):
            print('This is not a valid email address.\n')
            address = input(EMAIL)
            continue
        if asyncio.run(check_address(settings, address)):
            print('This email address cannot be registered. Try another.\n')
            address = input(EMAIL)
            continue
        return address


def get_passwd():
    phrase = getpass.getpass(PASSWORD)
    while True:
        confirm = getpass.getpass('Confirm the password: ')
        if confirm != phrase:
            print('Passwords must match!\n')
            phrase = getpass.getpass(PASSWORD)
            continue
        return phrase


if __name__ == '__main__':
    asyncio.run(create_user(
        settings, get_username(), get_email(), get_passwd(), groups.root))
