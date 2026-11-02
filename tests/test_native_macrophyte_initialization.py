"""Compile the actual cold-initialization mirror helper with checked arrays."""
import os
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '3DWET/src/getm/src/3d/getm_fabm.F90'


@pytest.mark.parametrize('instance,sediment_suffix', [
    ('macrophytes', ''), ('zoobenthos', ''), ('bivalves', ''),
    ('POM', 'S'), ('DOM', 'S'), ('humus', 'S'),
    ('cyanobacteria', 'S'), ('diatoms', 'S'), ('greens', 'S')])
def test_native_bottom_mirrors_match_spatial_benthic_states_only(tmp_path, instance, sediment_suffix):
    text = SOURCE.read_text(encoding='utf-8')
    match = re.search(r'(?is)\bsubroutine initialize_wet_benthic_mirrors\(\).*?end subroutine initialize_wet_benthic_mirrors', text)
    assert match, 'Cold initialization must reconcile WET PV and spatial benthic states'
    compiler = ROOT / 'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():
        pytest.skip('Portable native Fortran compiler is unavailable')
    probe = tmp_path / 'mirror.f90'
    probe.write_text('''module probe
implicit none
integer,parameter :: imin=1,imax=3,jmin=1,jmax=2,kmax=3
type variable
 character(len=80) :: name
end type
type model_type
 type(variable) :: state_variables(6),bottom_state_variables(5)
end type
type(model_type) :: model
integer :: az(3,2)
real(8) :: fabm_pel(3,2,0:3,6),fabm_ben(3,2,5)
contains
''' + match[0] + '''
end module
program test
use probe
implicit none
integer :: q,n,i,j
integer :: pi(4)=[4,3,5,2],bi(4)=[2,4,1,3]
model%state_variables(1)%name='foreign_sDS_PV'
model%state_variables(2)%name='macrophytes_sC_PV'
model%state_variables(3)%name='macrophytes_sN_PV'
model%state_variables(4)%name='macrophytes_sD_PV'
model%state_variables(5)%name='macrophytes_sP_PV'
model%state_variables(6)%name='unrelated'
model%bottom_state_variables(1)%name='macrophytes_sP'
model%bottom_state_variables(2)%name='macrophytes_sD'
model%bottom_state_variables(3)%name='macrophytes_sC'
model%bottom_state_variables(4)%name='macrophytes_sN'
model%bottom_state_variables(5)%name='foreign_sDS'
az=1;az(3,2)=0
fabm_pel=-900d0
fabm_ben=77d0
do q=1,4
 fabm_ben(:,:,bi(q))=real(q,8)*0.125d0
 fabm_ben(1,1,bi(q))=0d0
end do
call initialize_wet_benthic_mirrors()
do q=1,4
 do j=1,2
  do i=1,3
   if(az(i,j)>=1)then
    if(fabm_pel(i,j,1,pi(q))/=fabm_ben(i,j,bi(q))) stop 1
   else
    if(fabm_pel(i,j,1,pi(q))/=-900d0) stop 2
   endif
  enddo
 enddo
enddo
if(any(fabm_pel(:,:,0,:)/=-900d0))stop 3
if(any(fabm_pel(:,:,2:3,:)/=-900d0))stop 4
if(any(fabm_pel(:,:,:,1)/=-900d0))stop 5
if(any(fabm_pel(:,:,:,6)/=-900d0))stop 6
! Missing canonical variables are a no-op, never an index-0 write.
model%state_variables%name='foreign'
fabm_pel=-901d0
call initialize_wet_benthic_mirrors()
if(any(fabm_pel/=-901d0))stop 7
print *, 'PASS bottom mirrors: shuffled D/N/P/C, exact zeros, dry/upper/foreign unchanged'
end program
''', encoding='utf-8')
    probe_text = probe.read_text(encoding='utf-8')
    for element in 'DNPC':
        probe_text = probe_text.replace("'macrophytes_s" + element + "_PV'", "'" + instance + '_s' + element + sediment_suffix + "_PV'")
        probe_text = probe_text.replace("'macrophytes_s" + element + "'", "'" + instance + '_s' + element + sediment_suffix + "'")
    probe.write_text(probe_text, encoding='utf-8')
    executable = tmp_path / 'mirror.exe'
    env = dict(os.environ, PATH=str(compiler.parent) + os.pathsep + os.environ['PATH'])
    compiled = subprocess.run([str(compiler), '-O0', '-fcheck=all', '-ffree-line-length-none',
                               str(probe), '-o', str(executable)], cwd=tmp_path, env=env,
                              capture_output=True, text=True)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    result = subprocess.run([str(executable)], cwd=tmp_path, env=env, capture_output=True,
                            text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS bottom mirrors' in result.stdout


def test_mirror_initialization_is_scoped_to_initial_load_before_halos():
    text = SOURCE.read_text(encoding='utf-8')
    init = text[text.index('subroutine init_getm_fabm_fields('):text.index('end subroutine init_getm_fabm_fields')]
    cold = init[init.index('case(1,2)'):init.index('case default')]
    assert 'call initialize_wet_benthic_mirrors()' in cold
    assert cold.index('call initialize_wet_benthic_mirrors()') > cold.index('call get_2d_field(')
    assert 'call initialize_wet_benthic_mirrors()' not in init[init.index('case(0)'):init.index('case(1,2)')]
