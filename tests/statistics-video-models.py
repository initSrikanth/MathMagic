"""Independent exact checks of the authored Statistics video examples."""
from collections import Counter
import unittest,json,sys,importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'video-agent/production-v2'))
sp=importlib.util.spec_from_file_location('statistics_drawing',root/'video-agent/statistics/graphics.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
class StatisticsModels(unittest.TestCase):
 def test_snack_sort_and_total(self):
  expected=Counter(s.lower() for s in ['Apple','Banana','apple','Pear','Apple','Banana']);m=g.model_for(2,5);self.assertEqual(m['counts'],[expected[s.lower()] for s in m['labels']]);self.assertEqual(sum(m['counts']),6)
 def test_books_and_mode(self):
  m=g.model_for(3,3);raw=[0,1,2,2,2,3,4];self.assertEqual(m['counts'],[raw.count(i) for i in range(5)]);self.assertEqual(max(Counter(raw),key=Counter(raw).get),2)
 def test_same_mode_different_shapes(self):
  a=[1,2,5,2,1];b=[0,0,5,4,2];self.assertEqual(sum(a),11);self.assertEqual(sum(b),11);self.assertEqual(a.index(max(a)),b.index(max(b)));self.assertNotEqual(a,b)
 def test_line_changes(self):
  m=g.model_for(4,3);a=m['a'];self.assertEqual([a[i+1]-a[i] for i in range(3)],[10,0,20]);self.assertEqual(a[-1]-g.model_for(4,7)['b'][-1],10)
 def test_theme_lead_is_not_majority(self):
  m=g.model_for(5,7);self.assertEqual(sum(m['counts']),10);self.assertEqual(m['labels'][m['counts'].index(max(m['counts']))],'Animals');self.assertLess(max(m['counts'])*2,sum(m['counts']))
 def test_missing_responses(self):
  m=g.model_for(5,9);self.assertEqual(sum(m['counts']),8);self.assertEqual(24-sum(m['counts']),16)
 def test_prediction_cards_do_not_reveal_sorted_frequencies(self):
  self.assertEqual(g.model_for(2,4)['kind'],'cards');self.assertNotIn('counts',g.model_for(2,4))
 def test_all_scripts_brand_free_with_criteria(self):
  for i in range(1,6):
   s=json.loads((root/f'video-agent/statistics/scripts/lesson{i}.json').read_text());self.assertTrue(s['beats'][1]['text'].startswith('Today we are learning'));self.assertEqual(len(s['beats'][2]['board']),3);self.assertNotIn('mathmagic',' '.join(b['text'] for b in s['beats']).lower())
if __name__=='__main__':unittest.main()
