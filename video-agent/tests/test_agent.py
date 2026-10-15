import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/"agent.py"
spec=importlib.util.spec_from_file_location("mathmagic_agent",MODULE)
agent=importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class MathMagicVideoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons=json.loads(agent.SPECS.read_text(encoding="utf-8"))

    def test_all_scenes_mathematically_correct(self):
        self.assertGreaterEqual(agent.validate(self.lessons),10)

    def test_bad_comparison_fails(self):
        with self.assertRaises(ValueError):
            agent.validate_scene(dict(kind="compare",a=[1,2],b=[1,4],relation="<",
                seconds=10,heading="Wrong",narration="Wrong"))

    def test_bad_arithmetic_fails(self):
        with self.assertRaises(ValueError):
            agent.validate_scene(dict(kind="operation",a=[1,2],b=[1,4],result=[2,4],
                op="+",seconds=10,heading="Wrong",narration="Wrong"))

    def test_zero_denominator_fails(self):
        with self.assertRaises(ValueError):
            agent.value([1,0])

    def test_unapproved_avatar_blocks_publishing(self):
        with tempfile.TemporaryDirectory() as folder:
            page=Path(folder)/"fractions.html"
            page.write_text('<section id="meaning"><div class="video-frame"><iframe src="old"></iframe></div></section>')
            manifest=Path(folder)/"manifest.json"
            manifest.write_text("{}")
            with self.assertRaisesRegex(ValueError,"Avatar approval required"):
                agent.publish(self.lessons,manifest,page)

    def test_preparation_produces_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            report=agent.build(self.lessons,Path(folder))
            self.assertEqual(len(report["lessons"]),5)
            self.assertTrue((Path(folder)/"equivalent"/"scene_01.svg").exists())
            self.assertTrue((Path(folder)/"qa-report.json").exists())

    def test_svg_escapes_comparison_symbols(self):
        scene=dict(kind="compare",a=[1,2],b=[1,4],relation=">",seconds=10,
                   heading="Test",narration="Test")
        svg=agent.draw_scene(scene,"Fractions")
        self.assertIn("&gt;",svg)
        self.assertIn("<svg",svg)


if __name__=="__main__":
    unittest.main()
