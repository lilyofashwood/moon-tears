import unittest
import moon_tears as mt


class MoonTearsTests(unittest.TestCase):
    def test_ascii_full_domain(self):
        message = ''.join(map(chr, range(128)))
        self.assertEqual(mt.decode(mt.encode('a' * 400, message)), message)

    def test_unicode_exact(self):
        message = '\ufeff𝔩̸ 👾\n é \x00'
        self.assertEqual(mt.decode(mt.encode('rain ' * 100, message, 'utf8_4'), 'utf8_4'), message)

    def test_bad_domains(self):
        for digits, mode in (([5,5,5], 'ascii3'), ([5,5,5,5], 'utf8_4'), ([1], 'ascii3')):
            with self.assertRaises(ValueError): mt.digits_to_payload(digits, mode)

    def test_bad_stacks_and_colliding_carriers(self):
        with self.assertRaises(ValueError): mt.decode('a' + mt.MOON_TEAR_MARKS[0] * 8)
        with self.assertRaises(ValueError): mt.encode('ḁ' * 20, 'lily')

    def test_capacity(self):
        with self.assertRaises(ValueError): mt.encode('a', 'lily')

    def test_historical_specimen(self):
        from pathlib import Path
        specimen = Path('historical/demo_honeysuckle_encoded.txt').read_text()
        self.assertEqual(mt.decode(specimen), 'honeysuckle')
