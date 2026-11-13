"""Resumable read-only topic QA. Reuses existing tools; never renders, merges or publishes.
CI uses fresh gate executions and GitHub's re-run-failed-jobs mechanism. Local --resume
accepts only matching inputs/runtime and intact log evidence, never a release approval.
"""
import argparse
import concurrent.futures
import contextlib
import datetime as dt
import fcntl
import hashlib
from html.parser import HTMLParser
import json
import importlib.metadata
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
STAGES = ('inventory', 'curriculum', 'mathematics', 'media', 'progress', 'browser', 'accessibility', 'deployment')

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)

def load_profile(name):
    if not re.fullmatch(r'[a-z0-9-]+', name):
        raise ValueError('Invalid profile name')
    p = json.loads((ROOT / 'tools/production/profiles' / (name + '.json')).read_text())
    assert p['schema'] == 1 and p['production'] == 'VERIFY_EXISTING_ONLY'
    return p

def release(p):
    return json.loads((ROOT / p['release']).read_text())

def media_paths(p):
    paths = {p['release']}
    for row in release(p)['lessons']:
        paths.update(row[k] for k in ('src', 'captions', 'transcript', 'poster'))
        if row.get('original_release'):
            paths.add(row['original_release']['src'])
        if row.get('correction_evidence'):
            paths.add(row['correction_evidence'])
            register = json.loads((ROOT / 'docs/video-quality-audit-35.json').read_text())['records']
            proof = next(r for r in register if r['number'] == row['correction_record'])
            paths.add(proof['correction']['replacement']['script'])
    return paths

def fingerprint(p, stage):
    paths = set(p['rules']) | {'.gitignore', 'tools/production/requirements.txt', 'tools/production/pilot.py', 'tools/production/profiles/' + p['topic'] + '.json'}
    for pattern in p['inputs'][stage]:
        paths.update(str(f.relative_to(ROOT)) for f in ROOT.glob(pattern) if f.is_file())
        if not any(x in pattern for x in '*?['):
            paths.add(pattern)  # Missing declared inputs cannot disappear from the key.
    if stage in ('inventory', 'media', 'browser', 'accessibility', 'deployment'):
        paths.update(media_paths(p))
    mapping = {f: digest(ROOT / f) if (ROOT / f).is_file() else 'MISSING' for f in sorted(paths)}
    if stage == 'deployment': mapping['production_baseline_commit'] = os.environ.get('PILOT_DEPLOYMENT_BASE', '')
    return hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest()

def runtime():
    browser = next((shutil.which(x) for x in ['google-chrome', 'chromium'] if shutil.which(x)), None)
    try: sympy_version = importlib.metadata.version('sympy')
    except importlib.metadata.PackageNotFoundError: sympy_version = 'not installed'
    return {'python': sys.version.split()[0], 'system': platform.platform(), 'sympy': sympy_version,
            'browser': subprocess.check_output([browser, '--version'], text=True).strip() if browser else 'not installed',
            'node': subprocess.check_output(['node', '--version'], text=True).strip(),
            'ci': os.environ.get('CI', ''), 'browser_config': os.environ.get('PILOT_PLAYWRIGHT_CONFIG', 'playwright.config.js'),
            'browser_config_sha256': digest(Path(os.environ.get('PILOT_PLAYWRIGHT_CONFIG', ROOT / 'playwright.config.js')))}

def cache_valid(receipt, key, env, log):
    return (receipt.get('status') == 'PASS' and receipt.get('input_sha256') == key
            and receipt.get('runtime') == env and log.is_file()
            and receipt.get('log_sha256') == digest(log))

class LessonHTML(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.sections = {}; self.current = None; self.depth = 0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section':
            if not self.depth and re.fullmatch(r'lesson\d+', a.get('id', '')):
                self.current = self.sections.setdefault(a['id'], {'video': [], 'text': [], 'li': 0})
            self.depth += 1
        if self.current:
            if tag == 'source': self.current['video'].append(a.get('src'))
            if tag == 'li': self.current['li'] += 1
    def handle_endtag(self, tag):
        if tag == 'section':
            self.depth -= 1
            if not self.depth: self.current = None
    def handle_data(self, data):
        if self.current: self.current['text'].append(data)

def inventory(p):
    """Audit both Measurement topics without converting unrelated gaps into pilot approval."""
    result = []; scope_blockers = []
    for page in p['audit_pages']:
        text = (ROOT / page).read_text()
        scope_rule = p.get('audit_scope_rules', {}).get(page)
        if scope_rule:
            source = (ROOT / scope_rule['assessment']).read_text()
            sequence = re.search(r'const sequence=\[([\d,\s]+)\]', source)
            assert sequence, 'Core assessment sequence requires an explicit scope review'
            included = set(map(int, re.findall(r'\d+', sequence[1]))) & set(scope_rule['extension_kinds'])
            if included: scope_blockers.append({'page': page, **scope_rule, 'core_extension_kinds': sorted(included), 'status': 'BLOCKED'})
        sections = LessonHTML(text).sections
        for section, body in sections.items():
            src = body['video'][0] if len(body['video']) == 1 else None
            # Inspect the actual player, not a filename-based assumption.
            block = re.search(r'<section\b[^>]*id="' + section + r'".*?</section>', text, re.S)
            tracks = re.findall(r'<track\b[^>]*src="([^"]+)"', block[0])
            issues = []
            if not src or not (ROOT / src).is_file(): issues.append('Missing or ambiguous MP4')
            if not tracks: issues.append('Missing captions')
            if 'transcript' not in block[0].lower(): issues.append('Missing transcript')
            for track in tracks:
                if not (ROOT / track).is_file(): issues.append('Missing caption asset: ' + track)
            metadata = {}
            if src and (ROOT / src).is_file():
                metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
                    'stream=codec_name,codec_type,width,height,r_frame_rate:format=duration', '-of', 'json', str(ROOT / src)]))
            result.append({'page': page, 'lesson': section, 'src': src, 'metadata': metadata,
                           'sha256': digest(ROOT / src) if src and (ROOT / src).is_file() else None,
                           'issues': issues, 'scope': 'PILOT' if page == p['page'] else 'AUDIT_ONLY'})
    accessibility = {}
    if p.get('audit_accessibility_manifest'):
        sys.path.insert(0, str(ROOT / 'tools/video-quality'))
        from time_angles_accessibility import verify
        accessibility = verify()
    scoped = [r for r in result if r['scope'] == 'PILOT']
    assert len(scoped) == p['lesson_count'] and all(not r['issues'] for r in scoped), 'Pilot asset inventory incomplete'
    return {'accessibility_recovery': accessibility, 'placements': result, 'curriculum_scope_blockers': scope_blockers, 'audit_only_defects': sum(bool(r['issues']) for r in result if r['scope'] == 'AUDIT_ONLY')}

def curriculum(p):
    text = (ROOT / p['page']).read_text()
    sections = LessonHTML(text).sections
    assert len(sections) == p['lesson_count']
    rows = []
    for row in p['curriculum']:
        assert re.fullmatch(r'AC9M5(?:N|A|M|SP|ST|P)\d{2}', row['code']) and row['source'].startswith('https://www.scootle.edu.au/')
        joined = ' '.join(' '.join(sections[s]['text']) for s in row['sections']).lower()
        assert all(token.lower() in joined for token in row['evidence']), row['code'] + ': missing instructional evidence'
        assert (ROOT / row['assessment']).is_file()
        rows.append({'code': row['code'], 'source': row['source'], 'lessons': row['sections'],
                     'assessment_oracle': row['assessment'], 'status': 'MAPPED_IMPLEMENTATION'})
    for name, body in sections.items():
        words = ' '.join(body['text']).lower()
        assert 'learning goal' in words and 'success criteria' in words and body['li'] >= 3, name
        assert len(body['video']) == 1, name
    return {'mappings': rows, 'limit': 'Structural/assessment evidence; practical learner performance and semantic human review remain separate.'}

def media(p):
    sys.path.insert(0, str(ROOT / 'tools/video-quality'))
    from contract import load, branded, assert_scoped_correction_release
    cfg = load()
    register = json.loads((ROOT / 'docs/video-quality-audit-35.json').read_text())['records']
    batch = release(p); report = []
    assert batch['voice']['name'] == cfg['approved_voice']['voice']
    assert batch['voice']['speaker_id'] == cfg['approved_voice']['speaker_id']
    for row in batch['lessons']:
        f = ROOT / row['src']; assert digest(f) == row['sha256'] and f.stat().st_size == row['bytes']
        proof = next(r for r in register if r['number'] == row['correction_record'])
        assert_scoped_correction_release([proof])
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(f)]))
        v = next(s for s in info['streams'] if s['codec_type'] == 'video')
        a = next(s for s in info['streams'] if s['codec_type'] == 'audio')
        assert (v['width'], v['height'], v['codec_name'], v['pix_fmt'], a['codec_name']) == (1920, 1080, 'h264', 'yuv420p', 'aac')
        assert abs(float(info['format']['duration']) - row['duration']) < .1
        for field in ('captions', 'transcript'):
            assert not branded((ROOT / row[field]).read_text())
        report.append({'src': row['src'], 'sha256': row['sha256'], 'probe': 'PASS',
                       'decode_audio_frames_evidence': row['correction_evidence'],
                       'evidence_reused_only_after_exact_byte_and_sidecar_validation': True,
                       'perceptual_status': 'UNVERIFIED'})
    return {'files': report, 'policy': p['legacy_media_policy']}

def execute(p, stage, work):
    (work / 'scratch').mkdir(exist_ok=True)
    for recipe in p['commands'][stage]:
        argv = [sys.executable if s == 'python' else s.replace('{work}', str(work)) for s in recipe]
        if stage in ('browser', 'accessibility') and os.environ.get('PILOT_PLAYWRIGHT_CONFIG'):
            argv += ['--config', os.environ['PILOT_PLAYWRIGHT_CONFIG']]
        print('COMMAND', json.dumps(argv), flush=True)
        subprocess.run(argv, cwd=ROOT, check=True, stdout=sys.stdout, stderr=sys.stderr)  # No shell, hidden retries or ignored failures.
    return {'commands_passed': len(p['commands'][stage])}

def deployment(p):
    baseline = os.environ.get('PILOT_DEPLOYMENT_BASE', '')
    assert not baseline or re.fullmatch(r'[0-9a-f]{40}', baseline), 'Invalid production baseline commit'
    def committed_bytes(path):
        return subprocess.check_output(['git', 'show', baseline + ':' + path], cwd=ROOT) if baseline else (ROOT / path).read_bytes()
    batch = json.loads(committed_bytes(p['release']))
    files = set(p['site_assets'])
    for row in batch['lessons']:
        files.update(row[k] for k in ('src', 'captions', 'transcript', 'poster'))
    expected_hashes = {f: hashlib.sha256(committed_bytes(f)).hexdigest() for f in files}
    candidate_differences = [f for f in files if not (ROOT / f).is_file() or digest(ROOT / f) != expected_hashes[f]]
    def check(path):
        expected = expected_hashes[path]
        h = hashlib.sha256(); size = 0
        req = urllib.request.Request(p['site'] + path, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=45) as response:
            assert response.status == 200, path
            for chunk in iter(lambda: response.read(1024 * 1024), b''):
                h.update(chunk); size += len(chunk)
        assert h.hexdigest() == expected, 'Published bytes differ: ' + path
        return {'url': p['site'] + path, 'bytes': size, 'sha256': expected}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(check, sorted(files)))
    return {'verified': rows, 'production_baseline_commit': baseline or 'working-tree assets',
            'unpublished_candidate_files': candidate_differences if baseline else [],
            'scope': 'Production baseline bytes only on PRs; NOT deployment of the candidate or live Firebase verification.'}

def run_stage(p, stage, work, resume=False):
    key = fingerprint(p, stage); env = runtime(); target = work / (stage + '.json'); log = work / (stage + '.log')
    old = json.loads(target.read_text()) if target.exists() else {}
    if resume and not os.environ.get('CI') and stage != 'deployment' and cache_valid(old, key, env, log):
        print(stage + ': REUSED verified local checkpoint'); return old
    attempts = old.get('attempts', 0) if old.get('input_sha256') == key else 0
    failures = old.get('consecutive_failures', attempts if old.get('status') == 'FAIL' else 0) if old.get('input_sha256') == key else 0
    if resume and failures >= 2:
        raise RuntimeError(stage + ': two unchanged failures; diagnose and change inputs before retrying')
    receipt = {'stage': stage, 'status': 'RUNNING', 'input_sha256': key, 'runtime': env, 'attempts': attempts + 1,
               'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'worktree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
               'run_id': os.environ.get('GITHUB_RUN_ID'), 'started': dt.datetime.now(dt.timezone.utc).isoformat()}
    write_json(target, receipt)  # Durable before dispatch; interrupted work is never a PASS.
    started = time.monotonic()
    with log.open('w') as out, contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            handlers = {'inventory': inventory, 'curriculum': curriculum, 'media': media, 'deployment': deployment}
            receipt['evidence'] = handlers[stage](p) if stage in handlers else execute(p, stage, work)
            receipt['status'] = 'PASS'
        except Exception as e:
            receipt.update(status='FAIL', error=str(e)); print(type(e).__name__ + ': ' + str(e))
    receipt['consecutive_failures'] = failures + 1 if receipt['status'] == 'FAIL' else 0
    receipt['seconds'] = round(time.monotonic() - started, 2); receipt['log_sha256'] = digest(log)
    write_json(target, receipt)
    print(stage + ': ' + receipt['status'] + (' — ' + receipt.get('error', '') if receipt['status'] != 'PASS' else ''))
    return receipt

def report(p, work):
    rows = {}; blocked = []
    for stage in STAGES:
        target = work / (stage + '.json'); log = work / (stage + '.log')
        row = json.loads(target.read_text()) if target.exists() else {'status': 'NOT_RUN'}
        if row.get('input_sha256') != fingerprint(p, stage): row = {**row, 'status': 'STALE'} if target.exists() else row
        if row.get('status') == 'PASS' and (not log.is_file() or row.get('log_sha256') != digest(log)):
            row = {**row, 'status': 'INVALID_EVIDENCE'}
        if (os.environ.get('GITHUB_ACTIONS') == 'true' and row.get('status') == 'PASS'
                and (row.get('run_id') != os.environ.get('GITHUB_RUN_ID')
                     or row.get('source_commit') != os.environ.get('GITHUB_SHA')
                     or row.get('worktree_dirty') is not False)):
            row = {**row, 'status': 'INVALID_CI_CONTEXT'}
        rows[stage] = row
    manual_path = ROOT / p['manual_evidence']
    manual = json.loads(manual_path.read_text()) if manual_path.exists() else {}
    hashes = {r['src']: r['sha256'] for r in release(p)['lessons']}
    for requirement in p['manual_requirements']:
        e = manual.get(requirement, {})
        valid = e.get('status') == 'PASS' and all(e.get(k) for k in ('reviewer', 'date', 'evidence_url')) and e.get('evidence_url', '').startswith('https://')
        if requirement == 'exact_video_listening_and_viewing': valid = valid and e.get('video_sha256') == hashes
        elif requirement == 'time_angles_exact_video_caption_listening_and_viewing':
            audit = json.loads((ROOT / p['audit_accessibility_manifest']).read_text())
            expected = {r['video']: r['assets'][r['video']] for r in audit['lessons']}
            valid = valid and e.get('video_sha256') == expected and e.get('input_sha256') == fingerprint(p, 'inventory')
        elif requirement.startswith(('live_firebase', 'live_firestore', 'deployed_firestore')):
            valid = valid and e.get('input_sha256') == fingerprint(p, 'progress')
        elif requirement == 'physical_safari_ios': valid = valid and e.get('input_sha256') == fingerprint(p, 'browser')
        if not valid: blocked.append(requirement)
    pending_deployment = rows['deployment'].get('evidence', {}).get('unpublished_candidate_files', [])
    audit = rows['inventory'].get('evidence', {})
    audit_blocked = bool(audit.get('audit_only_defects') or audit.get('curriculum_scope_blockers') or audit.get('accessibility_recovery', {}).get('blocked_lessons'))
    ready = not audit_blocked and all(r.get('status') == 'PASS' for r in rows.values()) and not blocked and not pending_deployment
    value = {'topic': p['topic'], 'stages': rows, 'manual_checks_unverified': blocked, 'unpublished_candidate_files': pending_deployment, 'audit_content_blocked': audit_blocked, 'time_angles_accessibility': audit.get('accessibility_recovery', {}), 'release_ready': ready,
             'scope': 'Verification pilot only; no render, publish, merge, security-rule deployment or recurring automation.'}
    write_json(work / 'report.json', value)
    lines = ['# Measurement production pilot', '', '| Gate | Result |', '|---|---|']
    lines += ['| ' + s + ' | ' + r['status'] + ' |' for s, r in rows.items()]
    lines += ['', '**Release: ' + ('READY' if ready else 'BLOCKED') + '**', '', 'External checks unverified: ' + ', '.join(blocked),
              '', 'Time and Angles placements with missing accessibility assets (audit only): ' + str(rows['inventory'].get('evidence', {}).get('audit_only_defects', 'UNVERIFIED')) + '. See inventory.json.',
              '', 'Time and Angles recovered caption sets integrated: ' + str(audit.get('accessibility_recovery', {}).get('integrated_caption_sets', 'UNVERIFIED')) + '/5; blocked lessons: ' + str(audit.get('accessibility_recovery', {}).get('blocked_lessons', 'UNVERIFIED')),
              '', 'Audit-only curriculum scope blockers: ' + str(len(rows['inventory'].get('evidence', {}).get('curriculum_scope_blockers', []))),
              '', 'Unpublished candidate files: ' + ', '.join(pending_deployment),
              '', 'No content or video generation/deployment is performed by this workflow.']
    (work / 'report.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'report'])
    parser.add_argument('--profile', default='measurement')
    parser.add_argument('--stages', nargs='+', choices=STAGES, default=list(STAGES))
    parser.add_argument('--work-dir', type=Path)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--require-ready', action='store_true')
    args = parser.parse_args(); p = load_profile(args.profile); work = (args.work_dir or ROOT / 'work/production-pilot' / p['topic']).resolve(); work.mkdir(parents=True, exist_ok=True)
    with (work / '.lock').open('w') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: parser.error('A pilot is already using this checkpoint; no duplicate execution started.')
        if args.action == 'run':
            failed = False
            for stage in args.stages:
                try: failed |= run_stage(p, stage, work, args.resume)['status'] != 'PASS'
                except Exception as e: print(str(e), file=sys.stderr); failed = True
            if failed: return 1
        else:
            result = report(p, work)
            if args.require_ready and not result['release_ready']: return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
