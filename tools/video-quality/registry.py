"""Versioned topic media registry. Registration is distinct from release approval.

Dependency-free validation of the JSON Schema keywords used by schema.json;
unknown schema keywords fail closed. All paths are repository-relative local files.
Unchanged means exact baseline bytes AND every encoded audio/video packet, never
an approval of inherited speech, teaching quality or an unpublished candidate.
"""
import argparse
from array import array
from collections import Counter
from datetime import date
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
INDEX = 'video-agent/media-registry/registry.json'
SCHEMA = 'video-agent/media-registry/schema.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path, root=ROOT):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value, 'Duplicate JSON key: ' + key
            value[key] = item
        return value
    return json.loads((root / path).read_text(), object_pairs_hook=unique)


def validate_schema(value, schema, definitions, at='$'):
    supported = {'$schema', '$defs', '$ref', 'type', 'const', 'enum', 'properties',
                 'required', 'additionalProperties', 'items', 'minItems', 'uniqueItems',
                 'minimum', 'minLength', 'pattern', 'minProperties'}
    assert not set(schema) - supported, 'Unsupported schema keyword'
    if '$ref' in schema:
        ref = schema['$ref']; assert ref.startswith('#/$defs/')
        return validate_schema(value, definitions[ref.split('/')[-1]], definitions, at)
    if 'const' in schema:
        assert type(value) is type(schema['const']) and value == schema['const'], at + ': schema version/constant'
    if 'enum' in schema:
        assert value in schema['enum'], at + ': invalid enum'
    kind = schema.get('type')
    if kind:
        types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
        valid = type(value) in (int, float) if kind == 'number' else type(value) is types[kind]
        assert valid, at + ': expected ' + kind
    if isinstance(value, dict):
        assert set(schema.get('required', [])) <= value.keys(), at + ': missing required field'
        assert len(value) >= schema.get('minProperties', 0), at + ': empty object'
        props = schema.get('properties', {}); extra = schema.get('additionalProperties', True)
        for key, item in value.items():
            if key in props: validate_schema(item, props[key], definitions, at + '.' + key)
            elif extra is False: raise AssertionError(at + ': unexpected field ' + key)
            elif isinstance(extra, dict): validate_schema(item, extra, definitions, at + '.' + key)
    elif isinstance(value, list):
        assert len(value) >= schema.get('minItems', 0), at + ': missing items'
        if schema.get('uniqueItems'):
            assert len({json.dumps(x, sort_keys=True) for x in value}) == len(value), at + ': duplicate items'
        for n, item in enumerate(value): validate_schema(item, schema.get('items', {}), definitions, f'{at}[{n}]')
    elif isinstance(value, str):
        assert len(value) >= schema.get('minLength', 0), at + ': empty string'
        if 'pattern' in schema: assert re.search(schema['pattern'], value), at + ': invalid string'
    elif type(value) in (int, float) and 'minimum' in schema:
        assert value >= schema['minimum'], at + ': below minimum'


def schema_check(value, name, root=ROOT):
    definitions = read(SCHEMA, root)['$defs']
    validate_schema(value, definitions[name], definitions)


def local(path, root=ROOT):
    p = PurePosixPath(path)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in path and str(p) == path, 'Unsafe registry path: ' + path
    target = root / path
    assert target.resolve().is_relative_to(root.resolve()) and target.is_file(), 'Missing or escaped media/evidence: ' + path
    return target


def file_check(item, root=ROOT):
    p = local(item['path'], root)
    assert p.stat().st_size == item['bytes'] and digest(p.read_bytes()) == item['sha256'], 'Altered checksum: ' + item['path']
    return p


def packet_fingerprint(path):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_packets', '-show_entries',
        'packet=codec_type,data_hash', '-show_data_hash', 'sha256', '-of', 'json', str(path)]))
    result = {}
    for kind in ('video', 'audio'):
        hashes = [p['data_hash'] for p in data['packets'] if p['codec_type'] == kind]
        assert hashes, 'Missing ' + kind + ' packets'
        result[kind] = {'count': len(hashes), 'sha256': digest(('\n'.join(hashes)+'\n').encode())}
    return result


class Players(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.sections = []; self.video = 0; self.sources = []; self.players = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section': self.sections.append(a.get('id', ''))
        if tag == 'video':
            self.video += 1
            section = next((s for s in reversed(self.sections) if s), '')
            self.players.append({'section':section,'attrs':a,'sources':[],'tracks':[]})
            if a.get('src'):
                self.sources.append((section,a['src']));self.players[-1]['sources'].append(a['src'])
        if tag == 'source' and self.video:
            section = next((s for s in reversed(self.sections) if s), '')
            self.sources.append((section, a.get('src', '')))
            self.players[-1]['sources'].append(a.get('src',''))
        if tag == 'track' and self.video and a.get('kind') in ('captions','subtitles'):
            self.players[-1]['tracks'].append(a.get('src',''))

    def handle_endtag(self, tag):
        if tag == 'section' and self.sections: self.sections.pop()
        if tag == 'video': self.video -= 1


def baseline_file(item, commit, root=ROOT):
    data = subprocess.check_output(['git', 'show', commit+':'+item['path']], cwd=root)
    assert digest(data) == item['sha256'] and len(data) == item['bytes'], 'Unchanged record differs from preservation baseline: ' + item['path']


def legacy_inventory(records, index=None, root=ROOT):
    index = index or read(INDEX, root)
    expected = {(t['id'], n) for t in index['topics'] for n in t['legacy_numbers']}
    actual = [(r['topic'], r['number']) for r in records]
    assert len(set(actual)) == len(actual) and set(actual) == expected, 'Missing/unexpected legacy inventory record'
    return len(expected)


def tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text.lower())


def subject(row):
    return {k: v['sha256'] for k, v in row['assets'].items()}


def media_integrity(path):
    """Independent decode of newly approved bytes; never trusts receipt booleans."""
    atoms = []; size = path.stat().st_size
    with path.open('rb') as f:
        while f.tell() < size:
            header = f.read(8); assert len(header) == 8, 'Invalid MP4 atom'
            length, kind = struct.unpack('>I4s', header); header_size = 8
            if length == 1:
                length = struct.unpack('>Q', f.read(8))[0]; header_size = 16
            atoms.append(kind)
            if length == 0: break
            assert length >= header_size and f.tell()+length-header_size <= size, 'Invalid MP4 size'
            f.seek(length-header_size, 1)
    assert b'moov' in atoms and b'mdat' in atoms and atoms.index(b'moov') < atoms.index(b'mdat'), 'MP4 lacks faststart'
    decoded = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],capture_output=True,check=True)
    assert not decoded.stderr.strip(), 'Media decode errors'
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','48000','-f','f32le','-'])
    samples = array('f'); samples.frombytes(raw)
    if sys.byteorder != 'little': samples.byteswap()
    assert len(samples) >= 48000, 'Missing audio'
    rms = (sum(x*x for x in samples)/len(samples))**.5
    clipped = sum(abs(x)>=.999 for x in samples)/len(samples)
    from contract import load
    limits = load()['technical']
    assert rms >= limits['audio_rms_min'] and clipped < limits['clipping_fraction_max'], 'Decoded audio integrity limits'


def release_record(row, topic, root=ROOT, *, integrity=True):
    """Only newly approved replacements/new media use this policy.

    Historical unchanged records retain all prior, separate contract gates.
    A status field or technical checksum is never human approval.
    """
    from contract import load, branded
    from narration_release import parse_vtt
    if row['policy'] == 'unchanged': return
    assert row['status'] == 'approved', row['id'] + ': PENDING_HUMAN_APPROVAL'
    schema_check(row, 'record', root)
    for asset in row['assets'].values(): file_check(asset, root)
    approval = row['human_approval']
    assert approval['status'] == 'approved', 'Explicit human approval required'
    for key in ('reviewer', 'reviewed_at', 'reference'):
        assert approval.get(key, '').strip(), 'Incomplete human approval: ' + key
    date.fromisoformat(approval['reviewed_at'])
    for key in ('full_audio_listened', 'full_video_viewed', 'script_approved', 'all_flags_reviewed'):
        assert approval.get(key) is True, 'Incomplete human approval: ' + key
    assert approval.get('subject') == subject(row), 'Human approval bound to different bytes'
    assets = row['assets']; assert 'verification' in assets, 'Incomplete verification evidence'
    evidence = read(assets['verification']['path'], root); schema_check(evidence, 'verification', root)
    assert evidence['subject'] == {k: v for k, v in subject(row).items() if k != 'verification'}, 'Verification bound to different bytes'
    file_check(evidence['verifier'], root)
    assert evidence['verifier']['path'] != assets['producer']['path'], 'Integrity verifier must be independent of producer'
    assert evidence['verifier']['sha256'] != assets['producer']['sha256'], 'Integrity verifier cannot be a renamed producer'
    assert all(v == 'PASS' for v in evidence['checks'].values()), 'Incomplete independent verification'
    assert len({f['id'] for f in evidence['flags']}) == len(evidence['flags']), 'Duplicate evidence flag ID'
    assert all(f['status'] == 'reviewed' for f in evidence['flags']), 'Unresolved media flags'
    cfg = load(); m = evidence['metrics']
    assert m['audio_rms'] >= cfg['technical']['audio_rms_min'] and m['clipping_fraction'] < cfg['technical']['clipping_fraction_max'], 'Audio integrity limits'
    if row['policy'] == 'new': assert not cfg['production_hold']['active'], 'New media production/release hold remains active'
    script = read(assets['script']['path'], root); schema_check(script, 'script', root)
    assert script['topic'] == topic, 'Wrong script topic'
    expected_voice = {k:cfg['approved_voice'][k] for k in ('speaker_id','model_sha256','voices_sha256')}
    expected_voice['name'] = cfg['approved_voice']['voice']
    assert script['voice'] == expected_voice, 'Unapproved voice configuration'
    assert cfg['approved_voice']['enhanced_enthusiasm_approval'] is not None, 'Existing full-release voice calibration approval remains required'
    alignment = read(assets['alignment']['path'], root)
    text = local(assets['transcript']['path'], root).read_text()
    captions = local(assets['captions']['path'], root).read_text()
    assert not any(branded(s) for s in (script['text'], script['title'], text, captions)), 'Prohibited branding'
    assert tokens(script['text']) == tokens(text) == tokens(' '.join(u['text'] for u in alignment['utterances'])), 'Approved script/audio/transcript mismatch'
    assert alignment['video_sha256'] == assets['video']['sha256'], 'Alignment belongs to different media'
    assert alignment['captions_sha256'] == assets['captions']['sha256'] and alignment['transcript_sha256'] == assets['transcript']['sha256'], 'Alignment sidecars changed'
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(local(assets['video']['path'], root))]))
    v = next(s for s in probe['streams'] if s['codec_type']=='video'); a = next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],a['codec_name']) == ('h264',1920,1080,'yuv420p','aac'), 'Invalid replacement encoding'
    duration = float(probe['format']['duration']); cues = parse_vtt(local(assets['captions']['path'], root))
    assert cues and all(0 <= c['start'] < c['end'] <= duration+.03 for c in cues), 'Caption timing outside media'
    assert all(a['end'] <= b['start'] for a,b in zip(cues,cues[1:])), 'Overlapping captions'
    assert tokens(' '.join(' '.join(c['lines']) for c in cues)) == tokens(text), 'Caption coverage mismatch'
    if integrity: media_integrity(local(assets['video']['path'], root))


def load_registry(root=ROOT):
    from contract import load
    index = read(INDEX, root); schema_check(index, 'index', root)
    policy = load()['media_registry']
    assert policy['path'] == INDEX and policy['schema_version'] == index['schema_version'], 'Unsupported registry policy version/path'
    assert digest((root/SCHEMA).read_bytes()) == policy['schema_sha256'], 'Registry schema changed without versioned policy'
    assert index['preservation_commit'] == policy['preservation_commit'], 'Preservation baseline changed'
    topics = {}; all_rows = {}; files = {}; active = []
    for item in index['preserved']:
        file_check(item, root); baseline_file(item, index['preservation_commit'], root)
    for t in index['topics']:
        assert t['id'] not in topics, 'Duplicate topic ID'
        assert t['page'] not in [x['page'] for x in topics.values()], 'Duplicate topic page'
        file_check(t['manifest'], root)
        manifest = read(t['manifest']['path'], root); schema_check(manifest, 'topic', root)
        assert manifest['topic'] == t['id'], 'Manifest topic mismatch'
        rows = manifest['records']; ids = [r['id'] for r in rows]
        assert len(set(ids)) == len(ids), 'Duplicate record ID'
        assert set(ids) == set(t['inventory']), 'Missing/unexpected declared media record'
        assert set(policy['preserved_inventory'].get(t['id'], [])) <= set(ids), 'Preserved inventory removed'
        topic_rows = {r['id']: r for r in rows}
        for row in rows:
            assert row['id'] not in all_rows, 'Duplicate global record ID'
            all_rows[row['id']] = row
            for asset in row['assets'].values(): file_check(asset, root)
            path = row['assets']['video']['path']
            assert path not in files, 'Duplicate media path'
            files[path] = row['id']
            assert packet_fingerprint(root/path) == row['packets'], 'Encoded packet identity changed: ' + path
            if row['policy'] == 'unchanged':
                assert row['id'] in policy['preserved_inventory'].get(t['id'], []), 'Undeclared unchanged-media grandfathering'
                assert row['status'] == 'retained' and 'human_approval' not in row and 'replaces' not in row, 'Unchanged is preservation, not new approval'
                for asset in row['assets'].values(): baseline_file(asset, index['preservation_commit'], root)
            else:
                assert row['status'] in ('pending','approved') and 'human_approval' in row, 'Replacement/new policy requires explicit review state'
                assert row['human_approval']['status'] == row['status'], 'Review status mismatch'
                required = {'video','captions','transcript','poster','script','alignment','producer'}
                assert required <= row['assets'].keys(), 'Incomplete proposed media assets'
                if row['policy'] == 'replacement':
                    assert row.get('replaces') in topic_rows and row['replaces'] != row['id'], 'Missing original replacement record'
                    assert topic_rows[row['replaces']]['policy'] == 'unchanged', 'Replacement must preserve baseline original'
                else: assert 'replaces' not in row, 'New media cannot masquerade as replacement'
                script = read(row['assets']['script']['path'], root); schema_check(script, 'script', root)
                assert script['topic'] == t['id'], 'Wrong script topic'
                if 'verification' in row['assets']:
                    evidence = read(row['assets']['verification']['path'], root); schema_check(evidence, 'verification', root)
                    assert len({f['id'] for f in evidence['flags']}) == len(evidence['flags']), 'Duplicate evidence flag ID'
                    assert evidence['subject'] == {k:v for k,v in subject(row).items() if k!='verification'}, 'Verification bound to different bytes'
                    file_check(evidence['verifier'], root)
                if row['status'] == 'approved': release_record(row, t['id'], root, integrity=False)
        expected = []
        for placement in manifest['placements']:
            assert placement['record'] in topic_rows, 'Placement references missing record'
            row = topic_rows[placement['record']]
            expected.append((placement['section'], row['assets']['video']['path']))
            active.append((t['id'], row))
        assert len(expected) == len(set(expected)), 'Duplicate placement'
        players = Players(local(t['page'], root).read_text())
        assert Counter(expected) == Counter(players.sources), 'Missing/unexpected player in ' + t['page']
        for placement in manifest['placements']:
            row = topic_rows[placement['record']]
            match = [p for p in players.players if p['section']==placement['section'] and row['assets']['video']['path'] in p['sources']]
            assert len(match)==1 and len(match[0]['sources'])==1, 'Ambiguous registered player'
            if 'captions' in row['assets']:
                assert row['assets']['captions']['path'] in match[0]['tracks'], 'Missing/mismatched registered caption track'
            if row['policy']!='unchanged':
                a = match[0]['attrs']
                assert 'controls' in a and 'playsinline' in a and a.get('preload')=='metadata', 'Accessible native controls required'
                assert a.get('poster') == row['assets']['poster']['path'], 'Replacement poster mismatch'
        topics[t['id']] = t
    assert set(policy['preserved_inventory']) <= topics.keys(), 'Preserved topic removed'
    preserved = {r['id']:r for r in all_rows.values() if r['policy']=='unchanged'}
    assert digest(json.dumps(preserved,sort_keys=True,separators=(',',':')).encode()) == policy['preserved_records_sha256'], 'Preserved record bindings changed'
    return {'index': index, 'topics': topics, 'records': all_rows, 'files': files, 'active': active}


def check_history(registry, base, root=ROOT):
    """Append-only registrations; updating checksums cannot reapprove old bytes."""
    exists = subprocess.run(['git','cat-file','-e',base+':'+INDEX],cwd=root,capture_output=True).returncode == 0
    if not exists: return set()  # Initial migration is pinned to the preservation commit.
    old = json.loads(subprocess.check_output(['git','show',base+':'+INDEX],cwd=root))
    assert old['preservation_commit'] == registry['index']['preservation_commit'], 'Preservation baseline changed'
    old_contract = json.loads(subprocess.check_output(['git','show',base+':video-agent/video-production-contract.json'],cwd=root))
    assert old_contract['media_registry'] == __import__('contract').load()['media_registry'], 'Registry trust anchor changed'
    assert old['preserved'] == registry['index']['preserved'], 'Preserved evidence removed or changed'
    trusted = set()
    for t in old['topics']:
        assert t['id'] in registry['topics'], 'Registered topic removed'
        assert set(t['inventory']) <= set(registry['topics'][t['id']]['inventory']), 'Registered inventory removed'
        assert registry['topics'][t['id']]['page'] == t['page'], 'Registered topic page changed'
        m = json.loads(subprocess.check_output(['git','show',base+':'+t['manifest']['path']],cwd=root))
        current_manifest = read(registry['topics'][t['id']]['manifest']['path'], root)
        for placement in m['placements']:
            if placement not in current_manifest['placements']:
                replacements = [p for p in current_manifest['placements'] if p['section']==placement['section']
                                and registry['records'][p['record']].get('replaces')==placement['record']]
                assert len(replacements) == 1, 'Registered player removed without explicit replacement'
        for row in m['records']:
            current = registry['records'][row['id']]
            for key in ('policy','assets','packets','replaces','legacy'):
                if key=='assets' and row['status']=='pending':
                    # Complete a pending review with a NEW evidence artifact, not
                    # a silent rewrite of media, script, captions or old evidence.
                    before={k:v for k,v in row[key].items() if k!='verification'}
                    after={k:v for k,v in current[key].items() if k!='verification'}
                    assert before==after, 'Immutable pending media changed; add a new revision ID'
                    if 'verification' in row[key]:
                        file_check(row[key]['verification'],root)
                        assert 'verification' in current[key], 'Prior verification evidence removed'
                        before_flags={f['id'] for f in read(row[key]['verification']['path'],root)['flags']}
                        after_flags={f['id'] for f in read(current[key]['verification']['path'],root)['flags']}
                        assert before_flags <= after_flags, 'Known review flags removed'
                        if row[key]['verification']!=current[key].get('verification'):
                            assert row[key]['verification']['path']!=current[key].get('verification',{}).get('path'), 'Preserve prior verification artifact'
                else:
                    assert current.get(key) == row.get(key), 'Immutable registered media changed; add a new revision ID'
            if row['status'] in ('retained','approved'):
                assert current == row, 'Existing preservation/approval changed'
                if row['status'] == 'approved': trusted.add(row['id'])
    return trusted


def assert_releasable(registry, changed=(), root=ROOT, *, trusted=()):
    changed = set(changed)
    def media_file(path):
        if Path(path).suffix.lower() in ('.mp4','.m4v','.webm','.mov','.avi','.mkv','.mpeg','.mpg','.ts','.mts'): return True
        p = root/path
        if not p.is_file(): return False
        with p.open('rb') as f: head = f.read(12)
        return head[4:8] == b'ftyp' or head.startswith(b'\x1aE\xdf\xa3') or (head.startswith(b'RIFF') and head[8:12]==b'AVI ')
    unknown = [p for p in changed if p not in registry['files'] and media_file(p)]
    assert not unknown, 'Unregistered media: ' + repr(unknown)
    registered_pages = {t['page'] for t in registry['topics'].values()}
    for path in changed:
        if path.endswith('.html') and (root/path).is_file() and Players((root/path).read_text()).sources:
            assert path in registered_pages, 'Unregistered topic player page: ' + path
    selected = {row['id']: (topic,row) for topic,row in registry['active']}
    for path in changed & registry['files'].keys():
        row = registry['records'][registry['files'][path]]
        topic = next(t['id'] for t in registry['topics'].values() if row['id'] in t['inventory'])
        selected[row['id']] = (topic,row)
    for topic,row in selected.values(): release_record(row, topic, root, integrity=row['id'] not in trusted)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.parse_args()
    registry = load_registry()
    print(json.dumps({'schema_version':1,'topics':len(registry['topics']),'records':len(registry['records']),
                      'pending':[r['id'] for r in registry['records'].values() if r['status']=='pending'],
                      'registration':'PASS','release_checked':False},indent=2))
