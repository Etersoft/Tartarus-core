
"""Console dialog primitives.

This module provides several simple functions to interact with user
on terminal.
"""

import getpass

def _is_yes(ans, default=True):
    r"""Check if user answered positively."""
    if len(ans) == 0:
        return default
    ans = ans.lower()
    return ans == 'y' or ans == 'yes'


def yesno(prompt, default=True):
    r"""Ask yes-or-no question.

    Returns a boolean value: whether user answered yes.
    """
    if default:
        prompt2 = " [Y/n] "
    else:
        prompt2 = " [y/N] "

    return _is_yes(raw_input(prompt + prompt2), default)


def ask(prompt, default=None):
    r"""Ask user for a string."""
    if default:
        prompt += " (ENTER will select '%s') " % default
    prompt += ': '
    s = raw_input(prompt)
    if len(s) == 0:
        return default
    return s


def password(prompt, prompt1="Password: ",
                 prompt2="Re-enter password: ", min_len=8):
    """Prompt user for a new password.

    User is asked to type password twice.
    """
    print prompt
    while True:
        ans1 = getpass.getpass(prompt1)
        if len(ans1) < min_len:
            print 'Password too short! Please type at least %s symbols.' % min_len
            continue
        ans2 = getpass.getpass(prompt2)
        if ans1 == ans2:
            return ans1
        else:
            print "Sorry, passwords do not match. Try again."


def choice(prompt, choices, default_num=0,
               prompt2='Enter your choice'):
    """Ask user to choose one of several items."""
    print prompt
    for n, v in enumerate(choices):
        print "%s. %s" % (n+1, v)
    prompt2 += " (ENTER will select '%s'): " % choices[default_num]
    while True:
        ans = raw_input(prompt2).lower()
        if len(ans) == 0:
            return choices[default_num]
        if ans in ['c', 'cancel']:
            return None
        try:
            res = int(ans) - 1
        except ValueError:
            if ans in choices:
                return ans
            continue
        try:
            return choices[res]
        except IndexError:
            print "Choice must be between 1 and %s" % len(choices)
        # and ask again

def force(prompt):
    """Ask whether user wants to force some action or cancel the operation"""
    print prompt
    while True:
        ans = raw_input('[F]orce/[C]ancel: ').lower()
        if ans in ['f', 'force']:
            return True
        if ans in ['c', 'cancel']:
            return False
        #ask again

