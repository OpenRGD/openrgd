"""Malformed-input regressions; no provider, authority, hardware or network."""
from pathlib import Path
import tempfile
import unittest
from validate import ContractError, MAX_BYTES, read_json, validate

class ParserTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'input.json'
    def test_unhashable_discriminator(self):
        for value in [[],{},None,True,4]:
            with self.subTest(value=value),self.assertRaisesRegex(ContractError,'UNKNOWN_RECORD'):
                validate({'record_type':value})
    def test_nonobject_record(self):
        for value in [None,[],True,0,'private-input']:
            with self.subTest(value=value),self.assertRaisesRegex(ContractError,'UNKNOWN_RECORD'):validate(value)
    def test_duplicate_keys_fixed_code(self):
        self.path.write_text('{"private":1,"private":2}')
        with self.assertRaisesRegex(ContractError,'^DUPLICATE_KEY$'):read_json(self.path)
    def test_nonfinite_fixed_code(self):
        self.path.write_text('{"value":NaN}')
        with self.assertRaisesRegex(ContractError,'^NONFINITE$'):read_json(self.path)
    def test_huge_integer_fixed_code(self):
        self.path.write_text('{"value":'+('9'*10000)+'}')
        with self.assertRaisesRegex(ContractError,'^NUMBER_LIMIT$'):read_json(self.path)
    def test_size_fixed_code(self):
        self.path.write_bytes(b' '*(MAX_BYTES+1))
        with self.assertRaisesRegex(ContractError,'^SIZE_LIMIT$'):read_json(self.path)
    def test_invalid_utf8_fixed_code(self):
        self.path.write_bytes(b'\xff')
        with self.assertRaisesRegex(ContractError,'^JSON_READ_FAILED$'):read_json(self.path)

if __name__=='__main__':unittest.main(verbosity=2)
