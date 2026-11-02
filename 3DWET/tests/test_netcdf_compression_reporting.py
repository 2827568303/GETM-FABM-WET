import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from netcdf_compression import format_compression_result


def test_success_report_includes_duration_sizes_and_percent_saved():
    report = format_compression_result({
        "status": "compressed",
        "original_bytes": 2 * 1024 * 1024,
        "compressed_bytes": 1024 * 1024,
        "elapsed_seconds": 12.345,
    })

    assert "压缩及逐值核验耗时 12.3 秒" in report
    assert "原始 2.0 MiB → 新文件 1.0 MiB" in report
    assert "实际节省 1048576 bytes（50.0%）" in report


def test_zero_byte_original_has_defined_non_dividing_report():
    report = format_compression_result({
        "status": "not_smaller",
        "original_bytes": 0,
        "compressed_bytes": 0,
        "elapsed_seconds": 0,
    })

    assert "原始 0.0 MiB；候选文件 0.0 MiB（核验后未采用）" in report
    assert "实际节省 0 bytes；比例不适用（原文件为 0）" in report


def test_failure_report_includes_elapsed_and_staged_size_when_available():
    report = format_compression_result({
        "status": "failed",
        "original_bytes": 1024 * 1024,
        "compressed_bytes": 512 * 1024,
        "elapsed_seconds": 4.25,
        "error": "verification mismatch",
    })

    assert "压缩/核验失败" in report
    assert "耗时 4.2 秒" in report
    assert "原始 1.0 MiB；候选文件 0.5 MiB（未验证并已清理）" in report
    assert "实际节省 0 bytes（0.0%）" in report
    assert "未替换原文件" in report


def test_failure_report_handles_no_staged_file_without_inventing_savings():
    report = format_compression_result({
        "status": "failed",
        "original_bytes": 0,
        "elapsed_seconds": 0.5,
        "error": "open failed",
    })

    assert "候选文件大小未知" in report
    assert "实际节省 0 bytes；比例不适用（原文件为 0）" in report


def test_not_smaller_report_uses_candidate_size_but_actual_savings_is_zero():
    report = format_compression_result({
        "status": "not_smaller",
        "original_bytes": 1024 * 1024,
        "compressed_bytes": 2 * 1024 * 1024,
        "elapsed_seconds": 7,
    })

    assert "候选文件 2.0 MiB（核验后未采用）" in report
    assert "实际节省 0 bytes（0.0%）" in report
    assert "未替换原文件" in report
    assert "体积增加" not in report


def test_skipped_report_does_not_claim_compression_savings():
    report = format_compression_result({
        "status": "skipped",
        "original_bytes": 1024 * 1024,
        "elapsed_seconds": 0.25,
        "error": "unsupported format",
    })

    assert "跳过压缩" in report
    assert "未替换原文件" in report
    assert "实际节省 0 bytes（0.0%）" in report
    assert "候选文件大小未知" not in report
