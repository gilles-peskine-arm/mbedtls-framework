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

from .data_models.wycheproof import mldsa_verify_schema

def main():
    with open(sys.argv[1]) as json_input:
        json_data = json_input.read()
    data = mldsa_verify_schema.Model.model_validate_json(json_data)
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()
