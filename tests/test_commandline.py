import io
import re

from passcheck.commandline import main


def test_main():
    output = io.StringIO()
    main(['correct&horsebatterystaple'], output)
    assert re.match((
        '\n'
        'Entropy: 68 bits\n'
        'Number of bytes: 26\n'
        'Pattern detected: cracklib dictionary | symbols | cracklib dictionary | cracklib dictionary | cracklib dictionary\n'  # noqa
        'Number of possible passwords: 2.501218e+20\n'
        'Brute force (1000 guesses/second): 7,931,309,416 years\n'
        'Brute force (1e09 guesses/second): 7,931 years\n'
        'Brute force (1e12 guesses/second): 7 years\n'
        'Time to process: [0-9.]+ seconds\n'
    ), output.getvalue())
