"""Compile actual GOTM RHS routines and verify current linked state plus flux units."""
import os
from pathlib import Path
import re
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('routine', ['rhs', 'ppdd'])
def test_current_column_state_is_linked_before_bottom_and_flux_units(tmp_path, routine):
    compiler = ROOT / 'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():
        pytest.skip('Portable Fortran compiler unavailable')
    source = (ROOT/'3DWET/src/gotm/src/fabm/gotm_fabm.F90').read_text()
    body = re.search(rf'(?is)\bsubroutine right_hand_side_{routine}\(.*?end subroutine right_hand_side_{routine}', source)[0]
    body = body.replace('REALTYPE', 'real(8)').replace('_ZERO_', '0d0')
    prefix = '''module probe
implicit none
integer,parameter :: rk=8
integer :: kmax_bot=2,active_bottom=1,calls=0,bottom_calls=0
logical :: no_surface=.false.
real(8) :: curh(2)=[2d0,4d0],Af(0:2)=[0d0,2d0,5d0],Vc(2)=[4d0,12d0]
real(8) :: bulk(2,1)
type variable
 integer :: unused
end type
type model_type
 type(variable) :: state_variables(1),bottom_state_variables(1),surface_state_variables(1)
 contains
 procedure :: set_bottom_index
end type
type(model_type) :: model
type observation
 real(8),pointer :: data=>null()
 real(8) :: relax_tau=1d20
end type
type(observation) :: cc_ben_obs(1)
type type_bottom_diagnostic
 real(8) :: column(2),local
 type(type_bottom_diagnostic),pointer :: next=>null()
end type
type(type_bottom_diagnostic),pointer :: first_bottom_diagnostic=>null()
interface fabm_do
 module procedure interior_rhs_stub,interior_ppdd_stub
end interface
interface fabm_do_bottom
 module procedure bottom_rhs,bottom_ppdd
end interface
contains
subroutine set_bottom_index(self,k)
 class(model_type) :: self
 integer :: k
 active_bottom=k
end subroutine
subroutine fabm_link_bulk_state_data(m,i,x)
 type(model_type) :: m
 integer :: i
 real(8) :: x(:)
 bulk(:,i)=x
end subroutine
subroutine fabm_link_bottom_state_data(m,i,x)
 type(model_type) :: m
 integer :: i
 real(8) :: x
end subroutine
subroutine fabm_link_surface_state_data(m,i,x)
 type(model_type) :: m
 integer :: i
 real(8) :: x
end subroutine
subroutine update_fabm_expressions(n)
 integer :: n
end subroutine
subroutine do_repair_state(n,label)
 integer :: n
 character(*) :: label
end subroutine
subroutine save_diagnostics()
end subroutine
subroutine interior_rhs_stub(m,a,b,r)
 type(model_type) :: m
 integer :: a,b
 real(8) :: r(:,:)
 if(bottom_calls/=2*(calls+1))stop 7
 calls=calls+1
 r=r+10d0
end subroutine
subroutine interior_ppdd_stub(m,a,b,p,d)
 type(model_type) :: m
 integer :: a,b
 real(8) :: p(:,:,:),d(:,:,:)
 if(bottom_calls/=calls+1)stop 7
 calls=calls+1
 p=p+10d0;d=d+20d0
end subroutine
subroutine bottom_rhs(m,p,b)
 type(model_type) :: m
 real(8) :: p(:),b(:)
 bottom_calls=bottom_calls+1
 p=p+4d0*bulk(active_bottom,1)
 b=b-4d0*bulk(active_bottom,1)
end subroutine
subroutine bottom_ppdd(m,p,d,n)
 type(model_type) :: m
 integer :: n
 real(8) :: p(:,:),d(:,:)
 bottom_calls=bottom_calls+1
 p(1,1)=p(1,1)+4d0*bulk(1,1)
 d(1,1)=d(1,1)+8d0*bulk(1,1)
 p(2,2)=p(2,2)+7d0
end subroutine
subroutine fabm_do_surface(m,p,b)
 type(model_type) :: m
 real(8) :: p(:),b(:)
 p=p+3d0;b=b+5d0
end subroutine
'''
    program = '''
end module
program test
use probe
implicit none
real(8) :: cc(0:2,3),r(0:2,3),p(0:2,3,3),d(0:2,3,3),x
integer :: stage
cc=0d0
do stage=1,3
 x=real(stage,8)
 cc(1,1)=x;cc(2,1)=2*x
'''
    if routine == 'rhs':
        program += '''call right_hand_side_rhs(stage==1,3,2,cc,r)
if(abs(r(1,1)-(10d0+2d0*x))>1d-12) stop 1
if(abs(r(2,1)-(10d0+2d0*x+0.75d0))>1d-12) stop 2
if(abs(r(1,2)+4d0*x)>1d-12) stop 3
if(abs(r(2,2)+8d0*x)>1d-12) stop 4
if(r(2,3)/=5d0.or.any(r(0,:)/=0d0)) stop 5
'''
    else:
        program += '''call right_hand_side_ppdd(stage==1,3,2,cc,p,d)
if(abs(p(1,1,1)-(10d0+2d0*x))>1d-12) stop 1
if(abs(d(1,1,1)-(20d0+4d0*x))>1d-12) stop 2
if(p(2,1,1)/=10d0.or.d(2,1,1)/=20d0) stop 3
if(p(1,2,2)/=7d0.or.any(p(0,:,:)/=0d0)) stop 4
'''
    program += f'''if(calls/=stage) stop 8
if(bottom_calls/={2 if routine == 'rhs' else 1}*stage) stop 6
end do
print *, 'CURRENT COLUMN AND UNITS PASS'
end program
'''
    path=tmp_path/'probe.f90';path.write_text(prefix+body+program)
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    exe=tmp_path/'probe.exe'
    compiled=subprocess.run([str(compiler),'-cpp','-ffree-line-length-none','-fcheck=all',str(path),'-o',str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert compiled.returncode==0,compiled.stdout+compiled.stderr
    result=subprocess.run([str(exe)],env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
