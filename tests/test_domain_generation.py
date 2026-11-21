import unittest
from pathlib import Path

from main import build_variations, load_config
from modules.generator import DomainVariationGenerator


class DomainGenerationTests(unittest.TestCase):
    def test_config_targets_are_a_list_of_domains(self):
        config_path = Path(__file__).resolve().parents[1] / "config.yaml"

        self.assertEqual(load_config(config_path)["targets"], ["tesla.com"])

    def test_string_target_is_not_split_into_characters(self):
        candidates = build_variations("example.com", ["net"], 8)

        self.assertTrue(candidates)
        self.assertEqual(set(candidates.values()), {"example.com"})
        self.assertTrue(all("." in candidate for candidate in candidates))
        self.assertNotIn("e", candidates)

    def test_generator_yields_only_complete_domain_names(self):
        candidates = list(DomainVariationGenerator(["net"]).generate("example.com"))

        self.assertIn("example.com", candidates)
        self.assertTrue(all("." in candidate for candidate in candidates))


if __name__ == "__main__":
    unittest.main()
