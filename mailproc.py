#!/usr/bin/env python2

from __future__ import print_function

import subprocess
import mailbox
import email
import imp
import pwd
import sys
import os
import re

USERNAME = pwd.getpwuid(os.getuid()).pw_name
USERRC = os.path.expanduser('~/.mailprocrc')
MAILBOX = '/var/mail/%s' % USERNAME


def default_process(mbox, message):
    mbox.lock()
    mbox.add(message)
    mbox.flush()

def load_user_rc():
    try:
        with open(USERRC, 'rb') as f:
            code = compile(f.read(), USERRC, 'exec')

    except:
        return default_process

    else:
        def run(mbox, message):

            RECIPES = []
            def recipe(test=lambda m: True):
                def decorator(func):
                    RECIPES.append((test, func))
                    return func
                return decorator

            exec code in {
                    # main objects
                    'message': message,
                    'mbox': mbox,

                    # helpers
                    'default_process': default_process,
                    'mkdir_p': mkdir_p,
                    'recipe': recipe,

                    # useful modules
                    're': re,
                    'os': os,
                    'sys': sys,
                    'subprocess': subprocess,
                    }

            if RECIPES:
                RECIPES.append((lambda m: True, default_process))
                for recipe in RECIPES:
                    if recipe[0](message):
                        if recipe[1](mbox, message) is not False:
                            break

        return run


def mkdir_p(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise

if __name__ == '__main__':
    message = email.message_from_file(sys.stdin)
    mbox = mailbox.mbox(MAILBOX)
    userrc = load_user_rc()
    userrc(mbox, message)
