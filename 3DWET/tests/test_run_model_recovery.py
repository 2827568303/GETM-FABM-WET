import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'workflow' / '4_run' / 'run_model.py'
SPEC = importlib.util.spec_from_file_location('run_model_under_test', MODULE_PATH)
run_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_model)


def _cdf1_time_file(path, values, trailing=b''):
    def name_bytes(name):
        raw = name.encode('ascii')
        return struct.pack('>I', len(raw)) + raw + b'\0' * (-len(raw) % 4)

    header = bytearray(b'CDF\x01' + struct.pack('>I', 0))
    header += struct.pack('>II', 10, 1) + name_bytes('time') + struct.pack('>I', 0)
    header += struct.pack('>II', 0, 0)  # global attributes
    header += struct.pack('>II', 11, 1) + name_bytes('time')
    header += struct.pack('>I', 1) + struct.pack('>I', 0)  # one unlimited dimension
    header += struct.pack('>II', 0, 0)  # variable attributes
    header += struct.pack('>II', 6, 8)  # NC_DOUBLE, one 8-byte value per record
    begin_offset = len(header)
    header += struct.pack('>I', begin_offset + 4)
    path.write_bytes(header + b''.join(struct.pack('>d', value) for value in values) + trailing)
    return bytes(header)


class RunModelRecoveryTests(unittest.TestCase):
    def test_zero_exit_with_meteo_eof_without_complete_healthy_outputs_fails(self):
        class Process:
            stdout = iter(['FATAL ERROR: Reached eof in: meteo_input.txt\n'])

            @staticmethod
            def wait():
                return 0

        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp)
            exe = case / 'getm_cartesian'
            exe.write_bytes(b'placeholder')
            (case / 'getm.inp').write_text("runid = 'TESTLAKE'\nstop = '2020-01-02 00:00:00'\n")
            with patch.object(run_model, 'MODEL_EXE', str(exe)), \
                    patch.object(run_model.subprocess, 'Popen', return_value=Process()):
                self.assertFalse(run_model.run_model(case, no_validate=True))
            log = (case / 'run.log').read_text()
            self.assertIn('FATAL ERROR: Reached eof in: meteo_input.txt', log)
            self.assertIn('EXIT_CODE:0', log)

    def test_numrecs_is_restored_from_complete_physical_records_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp)
            (case / 'getm.inp').write_text(
                "runid = 'TESTLAKE'\n"
                "start = '2000-01-01 00:00:00'\n"
                "stop = '2099-01-01 00:00:00'\n"
                "timestep = 1\n"
            )
            files = {
                'TESTLAKE.2d.nc': ([10., 20.], b'partial'),
                'TESTLAKE.3d.nc': ([30., 40., 50.], b''),
                'output.nc': ([60.], b''),
            }
            original_payloads = {}
            header_lengths = {}
            for filename, (values, trailing) in files.items():
                path = case / filename
                header = _cdf1_time_file(path, values, trailing)
                header_lengths[filename] = len(header)
                original_payloads[filename] = path.read_bytes()[len(header):]

            run_model._auto_patch_numrecs(case, 'TESTLAKE')

            expected = {'TESTLAKE.2d.nc': 2, 'TESTLAKE.3d.nc': 3, 'output.nc': 1}
            for filename, count in expected.items():
                path = case / filename
                with path.open('rb') as f:
                    f.seek(4)
                    self.assertEqual(struct.unpack('>I', f.read(4))[0], count)
                self.assertEqual(path.read_bytes()[header_lengths[filename]:], original_payloads[filename])


if __name__ == '__main__':
    unittest.main()
