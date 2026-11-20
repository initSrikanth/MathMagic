"""Regression checks for the actual Statistics timing/model adapter, no synthesis."""
import sys,json,copy,unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('statistics_produce',ROOT/'video-agent/statistics/produce.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
class TimingModels(unittest.TestCase):
 def test_equal_frequency_model_matches_spoken_example(self):
  l=p.prepare(3);c=next(c for c in l['beats'] if 'same frequency' in c['text']);self.assertEqual(c['statistics_model']['counts'],[2]*5);self.assertNotIn('Ties',c['board'][0])
 def test_extra_book_response_updates_distribution(self):
  c=next(c for c in p.prepare(3)['beats'] if 'one extra pupil' in c['text']);self.assertEqual(c['statistics_model']['counts'],[1,1,3,1,2])
 def test_ordered_categories_use_relevant_cards(self):
  c=next(c for c in p.prepare(2)['beats'] if 'interest rating' in c['text']);self.assertEqual(c['statistics_model']['labels'],['Low','Medium','High'])
 def test_result_waits_for_actual_words_across_sentence_boundary(self):
  base={'parent_index':5,'role':'answer','board_events':[{'text':'3 + 2 + 1 = 6','at':4.65,'reason':'old sentence fallback'}],'statistics_model':{'kind':'table','labels':['Apple'],'counts':[3]},'text':'Check the votes.'}
  a=dict(copy.deepcopy(base),start=0,end=5,words=[{'word':'apple','start':1}]);b=dict(copy.deepcopy(base),start=5,end=12,words=[{'word':'six','start':10}]);t=p.measured_events({}, {'cues':[a,b]})
  for c in t['cues']:self.assertAlmostEqual(c['board_events'][0]['at'],10.1)
 def test_tool_example_result_is_not_an_immediate_question_reveal(self):
  base={'parent_index':9,'role':'question','board_events':[{'text':'24 − 8 = 16','at':0,'reason':'old immediate question context'}],'statistics_model':{'kind':'table','labels':['Art'],'counts':[4]},'text':'Check the missing replies.'}
  a=dict(copy.deepcopy(base),start=0,end=5,words=[{'word':'check','start':1}]);b=dict(copy.deepcopy(base),start=5,end=12,words=[{'word':'sixteen','start':10}]);t=p.measured_events({}, {'cues':[a,b]})
  self.assertTrue(all(c['board_events'][0]['at']>a['end'] for c in t['cues']))
 def test_comparison_uses_one_nonoverlapping_heading(self):
  from unittest.mock import patch
  p.g.CACHE.clear();c={'parent_index':7,'role':'answer','start':0,'statistics_model':{'kind':'compare'},'board_events':[]}
  with patch.object(p.g,'panel',wraps=p.g.panel) as draw_heading:p.g.picture({'id':'heading-regression','title':'Compare the classes'},c,None,0,0,[])
  self.assertEqual(draw_heading.call_count,1)
 def test_preparation_preserves_source_and_tracks_timing_recipe(self):
  f=ROOT/'video-agent/statistics/scripts/lesson1.json';before=f.read_bytes();l=p.prepare(1);self.assertEqual(f.read_bytes(),before);self.assertEqual(l['timing_recipe'],'parent-word-events-v2');self.assertEqual(l['statistics_renderer_sha256'],p.sha(p.__file__))
if __name__=='__main__':unittest.main()
