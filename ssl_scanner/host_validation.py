import re
import re
from netaddr.core import AddrFormatError
from netaddr import IPNetwork

# <name> from https://tools.ietf.org/html/rfc952#page-5
ALLOWED_NAME = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)

# from https://tools.ietf.org/html/rfc3696#section-2
ALL_NUMERIC = re.compile(r"[0-9]+$")

# Lifted from https://stackoverflow.com/a/33214423
# Modified to extract compilation of regexes


def is_valid_hostname(hostnameport):
    if hostnameport.count(':') != 1:
        # expect port to be baked into hostname
        return False
    hostname = hostnameport.split(':')[0]
    try:
        # not used but will throw if it is an invalid input
        IPNetwork(hostname)
        return True
    except AddrFormatError:

        if hostname[-1] == ".":
            # strip exactly one dot from the right, if present
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        # the TLD must be not all-numeric
        if ALL_NUMERIC.match(labels[-1]):
            return False

        return all(ALLOWED_NAME.match(label) for label in labels)
