import subprocess
import json
import pathlib


def test_run_adapters_harness_creates_report(tmp_path):
    """Run the adapters harness and assert the JSON report is produced."""
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    harness = repo_root / 'scripts' / 'run_adapters_test.sh'
    assert harness.exists(), f"Harness not found: {harness}"

    # Run the harness
    subprocess.check_call(['chmod', '+x', str(harness)])
    subprocess.check_call([str(harness)])

    report = repo_root / 'data' / 'modules_import_report_detailed.json'
    assert report.exists(), 'Expected report file not generated'

    # Minimal content checks
    with open(report, 'r', encoding='utf-8') as fh:
        j = json.load(fh)
    assert 'adapters' in j, 'Report missing adapters key'
