"""The actual extinction callback must use current state, not cached shading."""
import os,re,subprocess
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def test_extinction_recomputes_current_vegetation_fraction(tmp_path):
    compiler=ROOT/'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():pytest.skip('Fortran compiler unavailable')
    source=(ROOT/'3DWET/src/wet/src/macrophytes.F90').read_bytes().decode('utf-8',errors='replace')
    body=re.search(r'(?is)subroutine get_light_extinction\(.*?end subroutine get_light_extinction',source)[0]
    body=body.replace('_DECLARE_ARGUMENTS_GET_EXTINCTION_','real(rk),intent(in) :: env(6)\n real(rk),intent(inout) :: extinction').replace('_ARGUMENTS_GET_EXTINCTION_','env,extinction')
    body=re.sub(r'_GET(?:_GLOBAL|_HORIZONTAL)?_\(self%(\w+),(\w+)\)',r'\2=env(self%\1)',body)
    body=body.replace('_LOOP_BEGIN_','').replace('_LOOP_END_','')
    body=re.sub(r'_SET_EXTINCTION_\((.*?)\)',r'extinction=extinction+(\1)',body)
    prefix='''module probe
implicit none
integer,parameter :: rk=8
integer :: calls=0
type type_wet_macrophytes
 integer :: id_aDSubVeg_PV_in=1,id_uTm=2,id_Day=3,id_lat=4,id_sDVeg_PV=5,id_aDayInitVeg=6
 real(rk) :: cExtSpVeg=0.0035d0
 contains
 procedure :: calc_veg_fractions
end type
contains
subroutine calc_veg_fractions(self,Day,sDVeg,uTm,lat,aDSubVeg,aCovVeg,afCovSurfVeg,aDayInitVeg,aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg)
 class(type_wet_macrophytes),intent(in) :: self
 real(rk),intent(in) :: Day,sDVeg,uTm,lat
 real(rk),intent(inout) :: aDayInitVeg
 real(rk),intent(out) :: aDSubVeg,aCovVeg,afCovSurfVeg,aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg
 calls=calls+1
 if(Day/=22d0.or.uTm/=18d0.or.lat/=33d0.or.aDayInitVeg/=-1d0)stop 3
 aDSubVeg=0.4d0*sDVeg
 aCovVeg=0;afCovSurfVeg=0;aDShootVeg=0;aDRootVeg=0;aDEmergVeg=0;aDFloatVeg=0
 bfShootVeg=0;bfRootVeg=0;bfSubVeg=0
end subroutine
'''
    program='''end module
program test
use probe
implicit none
type(type_wet_macrophytes) :: model
real(rk) :: env(6),extinction
integer :: i
env=[999d0,18d0,22d0,33d0,10d0,-1d0]
do i=1,3
 env(1)=999d0*i;env(5)=10d0*i;extinction=0
 call get_light_extinction(model,env,extinction)
 if(abs(extinction-0.0035d0*0.4d0*env(5))>1d-14)stop 1
 if(calls/=i)stop 2
end do
end program
'''
    path=tmp_path/'extinction.f90';path.write_text(prefix+body+'\n'+program,encoding='utf-8')
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    exe=tmp_path/'extinction.exe'
    built=subprocess.run([str(compiler),'-ffree-line-length-none','-fcheck=all',str(path),'-o',str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert built.returncode==0,built.stderr
    ran=subprocess.run([str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert ran.returncode==0,ran.stdout+ran.stderr


def test_vegetation_onset_missing_value_is_not_the_valid_no_onset_code(tmp_path):
    compiler=ROOT/'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():pytest.skip('Fortran compiler unavailable')
    source=(ROOT/'3DWET/src/wet/src/macrophytes.F90').read_bytes().decode('utf-8',errors='replace')
    body=re.search(r'(?is)subroutine calc_veg_fractions\(.*?end subroutine calc_veg_fractions',source)[0]
    prefix='''module probe
implicit none
integer,parameter :: rk=8
real(rk),parameter :: Pi=3.141592653589793d0,NearZero=1d-20
type type_wet_macrophytes
 real(rk) :: cCovSpVeg=0.001d0,cDCarrVeg=1000d0,cDLayerVeg=100d0
 real(rk) :: cDaySumVegMin=90d0,cDayWinVeg=300d0,cLengAllo=30d0,cTmInitVeg=10d0
 real(rk) :: fEmergVeg=0.1d0,fFloatVeg=0.1d0,fRootVegSum=0.3d0,fRootVegWin=0.8d0
end type
contains
'''
    program='''
end module
program test
use probe
use, intrinsic :: ieee_arithmetic,only:ieee_is_finite
implicit none
type(type_wet_macrophytes),target :: model
real(rk) :: days(4)=[22d0,120d0,200d0,320d0],a(3),b(3),onset_a,onset_b,root_fraction
integer :: i
model%cDayWinVeg=350d0
onset_a=-1d0
call calc_veg_fractions(model,1d0,10d0,18d0,33d0,a(1),a(2),a(3),onset_a)
onset_a=120d0
call calc_veg_fractions(model,120d0,10d0,18d0,33d0,a(1),a(2),a(3),onset_a,bfRootVeg=root_fraction)
if(abs(root_fraction-model%fRootVegWin)>1d-14)stop 2
model%cDayWinVeg=300d0
do i=1,4
 onset_a=-1d0;onset_b=-2d20
 call calc_veg_fractions(model,days(i),10d0,18d0,33d0,a(1),a(2),a(3),onset_a)
 call calc_veg_fractions(model,days(i),10d0,18d0,33d0,b(1),b(2),b(3),onset_b)
 if(any(a/=b).or.onset_a/=onset_b.or..not.all(ieee_is_finite(b)))stop 1
end do
end program
'''
    path=tmp_path/'onset.f90';path.write_text(prefix+body+program,encoding='utf-8')
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    exe=tmp_path/'onset.exe'
    built=subprocess.run([str(compiler),'-ffree-line-length-none','-fcheck=all',str(path),'-o',str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert built.returncode==0,built.stderr
    ran=subprocess.run([str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert ran.returncode==0,ran.stdout+ran.stderr
