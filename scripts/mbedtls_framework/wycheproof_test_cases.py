"""Build test cases from Wycheproof test vectors."""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later

import json
from typing import Any, Dict, FrozenSet, Iterator, List, Optional

from . import test_case
from . import test_data_generation


class TestCase(test_case):
    """Test case data obtained from a Wycheproof test vector."""

    def __init__(self, algorithm: str,
                 group: Dict[str, Any],
                 test: Dict[str, Any],
                 ) -> None:
        """Extract test case data from Wycheproof data."""
        self.algorithm = algorithm
        self.group = {key: value
                      for key, value in group.items()
                      if isinstance(value, str)}
        self.source: Optional[str] = None
        if 'source' in self.group:
            self.source = '{} {}'.format(self.group['source']['name'],
                                         self.group['source']['version'])
        self.data = {key: value
                     for key, value in test.items()
                     if isinstance(value, str)}
        self.numbers = {key: value
                        for key, value in test.items()
                        if isinstance(value, int)}
        self.flags = frozenset(test.get('flags', []))


class Parser:
    """Parse Wycheproof test vectors."""

    def __init__(self) -> None:
        self.raw: List[Any] = []
        self.test_cases: List[TestCase] = []

    def read_json_group(self, algorithm: str,
                        group: Dict[str, Any],
                        test: Dict[str, Any]) -> TestCase:
        return TestCase(algorithm=algorithm,
                        group=group,
                        test=test)

    def read_json_group(self, algorithm: str,
                        group: Dict[str, Any]) -> None:
        for test in group['tests']:
            self.test_cases.append(self.read_json_test(algorithm, group, test))

    def read_json_data(self, data: Any) -> None:
        algoritm = data['algoritm']
        notes = data.get('notes', {})
        for group in = data['testGroups']:
            self.read_json_group(self, algoritm, group)
        #TODO

    def read_json_file(self, filename: str) -> None:
        with open(filename) as input_:
            data = json.load(input_)
            self.read_json_data(data)
            self.raw.append(data)
