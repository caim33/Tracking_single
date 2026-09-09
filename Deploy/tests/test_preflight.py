"""Prerequisite checks must detect missing inputs and broken deployment bundles."""
from pathlib import Path
import subprocess
import sys
import numpy as np
from Deploy.preflight import check_setup, training_motion


def test_sim2sim_prerequisites_use_real_bundle_and_assets(bundle):
    results = check_setup('sim2sim', bundle=bundle)
    assert all(ok for _, ok, _ in results), results
    with (bundle/'motion.npz').open('ab') as stream:
        stream.write(b'tampered')
    results = check_setup('sim2sim', bundle=bundle)
    failure = next(row for row in results if row[0] == 'deployment bundle')
    assert not failure[1] and 'checksum' in failure[2]


def test_missing_bundle_has_nonzero_exit_and_actionable_report(tmp_path):
    result = subprocess.run([sys.executable, '-m', 'Deploy.preflight', '--stage', 'sim2sim'],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'PASS robot assets' in result.stdout, result.stdout
    assert 'FAIL deployment bundle' in result.stdout and 'Provide --bundle' in result.stdout


def test_training_motion_matches_retained_body_list(tmp_path, motion):
    path = tmp_path/'reference.npz'
    np.savez_compressed(path, **motion)
    assert '50 Hz' in training_motion(path)
    from pytest import raises
    motion['fps'] = np.asarray(30.0)
    np.savez_compressed(path, **motion)
    with raises(ValueError, match='50 Hz'):
        training_motion(path)


def test_only_demo_is_registered_and_all_internal_imports_exist():
    import ast
    root = Path(__file__).resolve().parents[2]
    wbc = root/'RL_envs/source/WBC'
    registry = wbc/'WBC/tasks/__init__.py'
    tree = ast.parse(registry.read_text(encoding='utf-8'))
    assert [alias.name for node in tree.body if isinstance(node, ast.ImportFrom)
            for alias in node.names] == ['dance_demo']
    configs = list((wbc/'WBC/tasks/manager_based/tracking_single/robots/g1_29dof').glob('*/tracking_env_cfg.py'))
    assert [p.parent.name for p in configs] == ['dance_demo']
    roots = {'WBC': wbc, 'GMR': root, 'Deploy': root}
    for path in [*wbc.rglob('*.py'), * (root/'Deploy').glob('*.py')]:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            modules = [node.module] if isinstance(node, ast.ImportFrom) and not node.level else (
                [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
            for module in modules:
                prefix = module.split('.')[0] if module else ''
                if prefix in roots:
                    target = roots[prefix].joinpath(*module.split('.'))
                    assert target.with_suffix('.py').is_file() or (target/'__init__.py').is_file(), (path, module)
