import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "app"))
from calibration_storage import migrate_missing_files, load_json_with_seed


def test_migrates_legacy_calibration_files_only_when_destination_is_missing(tmp_path):
    legacy = tmp_path / "legacy"
    current = tmp_path / "D-state"
    legacy.mkdir()
    current.mkdir()
    (legacy / "calibration_points.json").write_text('[{"id":"legacy-point"}]', encoding="utf-8")
    (legacy / "auto_calib_config.json").write_text('{"method":"parsac"}', encoding="utf-8")
    (current / "auto_calib_config.json").write_text('{"method":"scipy"}', encoding="utf-8")

    migrated = migrate_missing_files(legacy, current, (
        "calibration_points.json", "auto_calib_config.json", "calibration_data.json"))

    assert migrated == ["calibration_points.json"]
    assert json.loads((current / "calibration_points.json").read_text(encoding="utf-8")) == [
        {"id": "legacy-point"}]
    assert json.loads((current / "auto_calib_config.json").read_text(encoding="utf-8")) == {
        "method": "scipy"}
    assert not (current / "calibration_data.json").exists()
    assert (legacy / "calibration_points.json").exists()


def test_calibration_json_load_falls_back_to_read_only_seed(tmp_path):
    user_data = tmp_path / "D-state" / "calibration_points.json"
    seed_data = tmp_path / "app-data" / "calibration_points.json"
    seed_data.parent.mkdir()
    seed_data.write_text('[{"id":"packaged-default"}]', encoding="utf-8")

    assert load_json_with_seed(user_data, seed_data, []) == [{"id": "packaged-default"}]
    user_data.parent.mkdir()
    user_data.write_text('[{"id":"user-edit"}]', encoding="utf-8")
    assert load_json_with_seed(user_data, seed_data, []) == [{"id": "user-edit"}]


def test_calibration_json_missing_everywhere_returns_default(tmp_path):
    assert load_json_with_seed(tmp_path / "D" / "absent.json",
                               tmp_path / "app" / "absent.json", {}) == {}
