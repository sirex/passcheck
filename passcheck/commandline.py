import argparse
import binascii
import getpass
import math
import os
import os.path
import random
import time

from passcheck.passcheck import get_default_passcheck
from passcheck.formatting import format_number, format_seconds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', nargs='?')
    parser.add_argument('--debug', action='store_true', default=False, help="Turn on debug mode.")
    parser.add_argument('-q', dest='verbosity', action='append_const', const=-1, help="Be more quiet.")
    parser.add_argument('-v', dest='verbosity', action='append_const', const=1, help="Be more verbose.")
    parser.add_argument('-p', dest='askpass', action='store_true', help=(
        "Ask for password interactively without showing what was entered."
    ))
    parser.add_argument('-x', dest='unhexlify', action='store_true', help=(
        "Decode provided password from hex serialisation."
    ))

    args = parser.parse_args()

    verbosity = sum(args.verbosity or []) + 1

    if args.askpass:
        password = getpass.getpass()
    elif args.password:
        password = args.password.encode()
        if args.unhexlify:
            password = binascii.unhexlify(password)
    else:
        password = os.urandom(random.randint(8, 32))
        print("Password (hex): %s" % repr(password).lstrip('b'))

    start_time = time.time()

    results = get_default_passcheck(debug=args.debug).check(password)

    entropy = 0
    combinations = 1

    print()

    for r in results:
        entropy += r.entropy
        combinations *= r.combinations
        if verbosity > 1:
            print('- Fragment: %s' % repr(r.value.bytes).lstrip('b'))
            print('  Entropy: %d bits' % math.ceil(r.entropy))
            print('  Number of bytes: %d' % len(r.value.bytes))
            print('  Pattern detected: %s' % r.pattern)
            print('  Number of possible passwords: %s' % format_number(r.combinations))
            print('  Brute force (1000 guesses/second): %s' % format_seconds(r.combinations / 1000))
            print('  Brute force (1e09 guesses/second): %s' % format_seconds(r.combinations / 1e09))
            print('  Brute force (1e12 guesses/second): %s' % format_seconds(r.combinations / 1e12))
            print()

    print('Entropy: %d bits' % math.ceil(entropy))
    if verbosity > 0:
        print('Number of bytes: %d' % len(password))
        print('Pattern detected: %s' % ' | '.join(str(r.pattern) for r in results))
        print('Number of possible passwords: %s' % format_number(combinations))
        print('Brute force (1000 guesses/second): %s' % format_seconds(combinations / 1000))
        print('Brute force (1e09 guesses/second): %s' % format_seconds(combinations / 1e09))
        print('Brute force (1e12 guesses/second): %s' % format_seconds(combinations / 1e12))
        print('Time to process: %.06f seconds' % (time.time() - start_time))
