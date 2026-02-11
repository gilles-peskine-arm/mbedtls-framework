"""Generate test cases from Whycheproof test data.
"""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#

import json
import os
import re
import sys
from typing import FrozenSet, List, Optional, Set

from . import psa_test_case

def main():
    with open(sys.argv[1]) as json_input:
        json_data = json.load(json_input)
    algorithm =  json_data['algorithm']
    notes =  json_data['notes']
    groups = json_data['testGroups']
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()
