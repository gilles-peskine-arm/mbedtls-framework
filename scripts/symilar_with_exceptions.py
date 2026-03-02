#!/usr/bin/env python3
"""Check for duplicate code across Python files, allowing for exceptions.
"""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later

from typing import Dict, Iterable, Iterator, Set, Tuple
import unittest.mock

from pylint.checkers.similar import Similar, LineSet, Run #type: ignore

class SimilarWithExceptions(Similar):
    """Allow some file pairs to have duplicate code."""

    PAIRS_ALLOWING_DUPLICATION: Iterable[Tuple[str, str]] = [
        # Normally we don't want code duplication across files.
        # This includes duplication between files in the framework repository
        # and files in a consuming branch. (Also between TF-PSA-Crypto and
        # Mbed TLS, but we don't check that at the time of writing.)
        #
        # However, sometimes, we want exceptions. The reason this exception
        # mechanism was added was to support migration of code to the
        # framework, for which there is a transition period where the same
        # code is already present in the framework and not yet removed from
        # its originating repository.
        #
        # Add exceptions here. Note that the path needs to be what pylint
        # or symliar sees on its command line.
        ('framework/scripts/mbedtls_framework/interface_checks.py',
         'scripts/abi_check.py'),
        ('framework/scripts/make_generated_files.py',
         'scripts/make_generated_files.py'),
        ('framework/scripts/code_size_compare.py',
         'scripts/code_size_compare.py'),
        ('framework/scripts/ecp_comb_table.py',
         'scripts/ecp_comb_table.py'),
        ('framework/scripts/audit-validity-dates.py',
         'tests/scripts/audit-validity-dates.py'),
        ('framework/scripts/generate_server9_bad_saltlen.py',
         'tests/scripts/generate_server9_bad_saltlen.py'),
        ('framework/scripts/psa_collect_statuses.py',
         'tests/scripts/psa_collect_statuses.py'),
        ('framework/scripts/run_demos.py',
         'tests/scripts/run_demos.py'),
        ('framework/scripts/test_config_script.py',
         'tests/scripts/test_config_script.py'),
    ]

    def __init__(self, *args, **kwargs) -> None:
        """pylint.checkers.similar.Similar() with an exception mechanism.

        The class attribute PAIRS_ALLOWING_DUPLICATION contains a list of
        pairs of file names. Code in the first file is allowed to duplicate
        code in the second file and vice versa.
        """
        super().__init__(*args, **kwargs)
        self.files_allowing_duplication: Dict[str, Set[str]] = {}
        for path1, path2 in self.PAIRS_ALLOWING_DUPLICATION:
            self.files_allowing_duplication.setdefault(path1, set())
            self.files_allowing_duplication[path1].add(path2)
            self.files_allowing_duplication.setdefault(path2, set())
            self.files_allowing_duplication[path2].add(path1)

    def duplication_allowed(self, path1: str, path2: str) -> bool:
        """Whether code in path2 is allowed to duplicate code in path1."""
        if path1 in self.files_allowing_duplication:
            if path2 in self.files_allowing_duplication[path1]:
                return True
        return False

    def _find_common(self, lineset1: LineSet, lineset2: LineSet) \
            -> Iterator[Tuple[int, LineSet, int, LineSet, int]]:
        if not self.duplication_allowed(lineset1.name, lineset2.name):
            yield from super()._find_common(lineset1, lineset2)

def main() -> None:
    with unittest.mock.patch('pylint.checkers.similar.Similar',
                             new=SimilarWithExceptions):
        Run()

if __name__ == '__main__':
    main()
