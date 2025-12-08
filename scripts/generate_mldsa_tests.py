#!/usr/bin/env python3
"""Generate ML-DSA test cases.
"""

# Copyright The Mbed TLS Contributors
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later

import sys
from typing import Iterable, List, Optional

import dilithium_py.ml_dsa # pip install dilithium-py

from mbedtls_framework import test_case
from mbedtls_framework import test_data_generation

PURE = {
    #44: dilithium_py.ml_dsa.ML_DSA_44,
    #65: dilithium_py.ml_dsa.ML_DSA_65,
    87: dilithium_py.ml_dsa.ML_DSA_87,
}

HASH = {
    #44: dilithium_py.ml_dsa.HASH_ML_DSA_44_WITH_SHA512,
    #65: dilithium_py.ml_dsa.HASH_ML_DSA_65_WITH_SHA512,
    87: dilithium_py.ml_dsa.HASH_ML_DSA_87_WITH_SHA512,
}

SEEDS = [
    b'There was once upon a time a ...',
    b'\x00' * 32,
]

class Key:
    """An MLDSA key."""

    def __init__(self, kl: int, seed: bytes) -> None:
        self.kl = kl
        self.seed = seed
        self.public, self.secret = PURE[kl]._keygen_internal(seed)

    def sign_message(self, message: bytes, deterministic: bool) -> bytes:
        return PURE[self.kl].sign(self.secret, message,
                                  deterministic=deterministic)

KEYS = {kl: [Key(kl, seed) for seed in SEEDS]
        for kl in sorted(PURE.keys())}

MESSAGES = [
    (b'This is a test', ''),
    (b'', 'empty message'),
    (b'\x00', '"\\x00"'),
    (b'\x01', '"\\x01"'),
    (b'ACBDEFGHIJ' * 100, '1000B'),
]


class API:
    @classmethod
    def function(cls, func: str, kl: int) -> str:
        return NotImplementedError

    @classmethod
    def metadata_arguments(cls,
                           kl: int,
                           pair: bool,
                           deterministic: Optional[bool]) -> List[str]:
        return NotImplementedError

    @classmethod
    def final_arguments(cls) -> List[str]:
        return []

    @classmethod
    def secret_is_seed(cls) -> bool:
        return True


class PQCPAPI(API):
    @classmethod
    def function(cls, func: str, kl: int) -> str:
        return f'{func}_{kl}'

    @classmethod
    def metadata_arguments(cls,
                           _kl: int,
                           _pair: bool,
                           _deterministic: Optional[bool]) -> List[str]:
        return []

    @classmethod
    def secret_is_seed(cls) -> bool:
        return False


class DriverAPI(API):
    @classmethod
    def function(cls, func: str, _kl: int) -> str:
        return func

    @classmethod
    def metadata_arguments(cls,
                           kl: int,
                           pair: bool,
                           deterministic: Optional[bool]) -> List[str]:
        arguments = []
        arguments.append('PSA_KEY_TYPE_ML_DSA_KEY_PAIR' if pair else
                         'PSA_KEY_TYPE_ML_DSA_PUBLIC_KEY')
        arguments.append(str(kl))
        if deterministic is not None:
            arguments.append('PSA_ALG_DETERMINISTIC_ML_DSA' if deterministic else
                             'PSA_ALG_ML_DSA')
        return arguments

    @classmethod
    def final_arguments(cls) -> List[str]:
        return ['PSA_SUCCESS']


def one_mldsa_key_pair_from_seed(key: Key,
                                 descr: str) -> test_case.TestCase:
    tc = test_case.TestCase()
    tc.set_function(f'key_pair_from_seed_{key.kl}')
    tc.set_dependencies([f'TF_PSA_CRYPTO_PQCP_MLDSA_{key.kl}_ENABLED'])
    tc.set_arguments([
        test_case.hex_string(key.seed),
        test_case.hex_string(key.secret),
        test_case.hex_string(key.public),
    ])
    tc.set_description(f'MLDSA-{key.kl} key pair from seed {descr}')
    return tc

def gen_pqcp_key_management(kl: int) -> Iterable[test_case.TestCase]:
    for i, key in enumerate(KEYS[kl], 1):
        yield one_mldsa_key_pair_from_seed(key, f'key#{i}')

def one_mldsa_public_key_from_seed(key: Key,
                                   descr: str) -> test_case.TestCase:
    tc = test_case.TestCase()
    tc.set_function('export_public_key')
    tc.set_dependencies([f'TF_PSA_CRYPTO_PQCP_MLDSA_{key.kl}_ENABLED'])
    tc.set_arguments([
        'PSA_KEY_TYPE_ML_DSA_KEY_PAIR',
        str(key.kl),
        test_case.hex_string(key.seed),
        test_case.hex_string(key.public),
        'PSA_SUCCESS',
    ])
    tc.set_description(f'MLDSA-{key.kl} export public key from seed {descr}')
    return tc

def gen_driver_key_management(kl: int) -> Iterable[test_case.TestCase]:
    for i, key in enumerate(KEYS[kl], 1):
        yield one_mldsa_public_key_from_seed(key, f'key#{i}')

def one_mldsa_sign_deterministic_pure(api: API,
                                      key: Key,
                                      message: bytes,
                                      descr: str) -> test_case.TestCase:
    signature = key.sign_message(message, deterministic=True)
    tc = test_case.TestCase()
    tc.set_function(api.function('sign_deterministic_pure', key.kl))
    tc.set_dependencies([f'TF_PSA_CRYPTO_PQCP_MLDSA_{key.kl}_ENABLED'])
    tc.set_arguments(api.metadata_arguments(key.kl, True, True) + [
        test_case.hex_string(key.seed if api.secret_is_seed() else key.secret),
        test_case.hex_string(message),
        test_case.hex_string(signature),
    ] + api.final_arguments())
    tc.set_description(f'MLDSA-{key.kl} sign deterministic {descr}')
    return tc

def one_mldsa_verify_pure(api: API,
                          key: Key,
                          message: bytes,
                          deterministic: bool,
                          descr: str) -> test_case.TestCase:
    signature = key.sign_message(message, deterministic=True)
    tc = test_case.TestCase()
    tc.set_function(api.function('verify_pure', key.kl))
    tc.set_dependencies([f'TF_PSA_CRYPTO_PQCP_MLDSA_{key.kl}_ENABLED'])
    tc.set_arguments(api.metadata_arguments(key.kl, False, True) + [
        test_case.hex_string(key.public),
        test_case.hex_string(message),
        test_case.hex_string(signature),
    ] + api.final_arguments())
    tc.set_description(f'MLDSA-{key.kl} verify {"deterministic" if deterministic else "randomized"} {descr}')
    return tc

def gen_mldsa_pure(api: API, kl: int) -> Iterable[test_case.TestCase]:
    for i, key in enumerate(KEYS[kl], 1):
        yield one_mldsa_sign_deterministic_pure(api, key, MESSAGES[0][0],
                                                f'key#{i}')
    for message, descr in MESSAGES[1:]:
        yield one_mldsa_sign_deterministic_pure(api, KEYS[kl][0], message,
                                                f'key#1 {descr}')
    for i, key in enumerate(KEYS[kl], 1):
        yield one_mldsa_verify_pure(api, key, MESSAGES[0][0], True,
                                    f'key#{i}')
    for message, descr in MESSAGES[1:]:
        yield one_mldsa_verify_pure(api, KEYS[kl][0], message,
                                    True, f'key#1 {descr}')
    for i, key in enumerate(KEYS[kl], 1):
        yield one_mldsa_verify_pure(api, key, MESSAGES[0][0], False,
                                    f'key#{i}')
    for message, descr in MESSAGES[1:]:
        yield one_mldsa_verify_pure(api, KEYS[kl][0], message,
                                    False, f'key#1 {descr}')

def gen_pqcp_mldsa_all() -> Iterable[test_case.TestCase]:
    api = PQCPAPI()
    for kl in sorted(KEYS.keys()):
        yield from gen_pqcp_key_management(kl)
        yield from gen_mldsa_pure(api, kl)

def gen_driver_mldsa_all() -> Iterable[test_case.TestCase]:
    api = DriverAPI()
    for kl in sorted(KEYS.keys()):
        yield from gen_driver_key_management(kl)
        yield from gen_mldsa_pure(api, kl)

class MLDSATestGenerator(test_data_generation.TestGenerator):
    """Generate test cases for ML-DSA."""

    def __init__(self, settings) -> None:
        self.targets = {
            'test_suite_pqcp_mldsa.dilithium_py': gen_pqcp_mldsa_all,
        }
        self.targets = {
            'test_suite_psa_crypto_mldsa.dilithium_py': gen_driver_mldsa_all,
        }
        super().__init__(settings)


if __name__ == '__main__':
    test_data_generation.main(sys.argv[1:], __doc__, MLDSATestGenerator)
