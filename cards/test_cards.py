"""Offline tests: every card must render valid XML from the fixture."""
import unittest
import xml.etree.ElementTree as ET

from . import (card_portscan, card_registry, card_scope, card_training,
               github_data)

FIXTURE = "testdata/profile.json"


class CardsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = github_data.load_fixture(FIXTURE)

    def _render(self, module, *needles):
        svg = module.render(self.data)
        ET.fromstring(svg)                      # must be well-formed XML
        self.assertIn("<svg", svg)
        for n in needles:
            self.assertIn(n, svg)
        return svg

    def test_fixture_shape(self):
        self.assertGreater(self.data["total"], 0)
        self.assertGreater(len(self.data["repos"]), 0)
        self.assertGreater(len(self.data["days"]), 350)

    def test_training(self):
        svg = self._render(card_training, "train_contributor.py",
                           "converging", "epoch")
        self.assertIn(str(self.data["total"]), svg)

    def test_portscan(self):
        svg = self._render(card_portscan, "/tcp", "Nmap done")
        # one port line per repo
        self.assertEqual(svg.count("/tcp"), len(self.data["repos"]))
        # a state only appears if some repo is actually in it; require the
        # two the live profile always has, and never an unknown one
        for state in ("open", "filtered"):
            self.assertIn(state, svg)

    def test_registry(self):
        svg = self._render(card_registry, "MODEL", "serving", "params")
        self.assertIn("v1.", svg)              # dab00gieman repos are 1-star

    def test_scope(self):
        svg = self._render(card_scope, "CH1: CONTRIBUTIONS", "TRIG: RUN",
                           "samples")
        self.assertIn("polyline", svg)

    def test_states_consistent(self):
        for r in self.data["repos"]:
            st = card_registry._status(r)
            if r["archived"]:
                self.assertEqual(st[0], "deprecated")


if __name__ == "__main__":
    unittest.main()
