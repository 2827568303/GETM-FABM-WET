"""Exercise actual adapter storage against distinct column histories."""
import os
from pathlib import Path
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('checkpoint', ['none','roundtrip','legacy','identity','period','ring','nonfinite','fill','diagnostic_fill','diagnostic_identity'])
def test_temporal_memory_is_column_local_and_preserves_output_pointers(tmp_path,checkpoint):
    compiler=ROOT/'build/native-toolchain/ucrt64/bin/gfortran.exe'
    if not compiler.exists():pytest.skip('Fortran compiler unavailable')
    folder=ROOT/'3DWET/src/getm/src/3d'
    prefix='''module probe
use netcdf
implicit none
integer,parameter :: imin=1,imax=2,jmin=1,jmax=1,kmax=3
type property_dictionary
 logical :: persistent=.false.
 contains
 procedure :: get_logical,get_real
end type
type diagnostic_info
 type(property_dictionary) :: properties
 integer :: save_index=1
 character(len=80) :: name='vegetation_onset'
end type
type type_expression
 class(type_expression),pointer :: next=>null()
 character(len=80) :: output_name='test_expression'
end type
type,extends(type_expression) :: type_bulk_temporal_mean
 real(8),allocatable :: history(:,:)
 real(8) :: last_time,next_save_time
 real(8) :: period=86400d0,missing_value=0d0
 integer :: n=2,ioldest=-1
 logical :: valid=.false.
end type
type,extends(type_expression) :: type_horizontal_temporal_mean
 real(8),allocatable :: history(:)
 real(8) :: last_time,next_save_time
 real(8) :: period=86400d0
 integer :: n=2,ioldest=-1
end type
type root_type
 class(type_expression),pointer :: first_expression=>null()
end type
type model_type
 type(root_type) :: root
 type(diagnostic_info) :: diagnostic_variables(2)
end type
type(model_type) :: model
real(8),target :: diagnostic_values(3,2)
'''
    types=(folder/'fabm_temporal_memory_types.h').read_text().replace('REALTYPE','real(8)')
    routines=(folder/'fabm_temporal_memory.h').read_text().replace('REALTYPE','real(8)')
    routines+=(folder/'fabm_temporal_restart.h').read_text().replace('REALTYPE','real(8)')
    routines+='''
logical function get_logical(self,name,default)
 class(property_dictionary) :: self
 character(*) :: name
 logical :: default
 get_logical=self%persistent
end function
real(8) function get_real(self,name,default)
 class(property_dictionary) :: self
 character(*) :: name
 real(8) :: default
 get_real=default
 if(name=='column_memory_initial')get_real=-1d0
end function
function fabm_get_bulk_diagnostic_data(self,index) result(data)
 type(model_type) :: self
 integer :: index
 real(8),pointer :: data(:)
 data=>diagnostic_values(:,index)
end function
subroutine getm_error(routine,message)
 character(*) :: routine,message
 print *, routine,message
 stop 77
end subroutine
'''
    program='''
end module
program test
use probe
use, intrinsic :: ieee_arithmetic, only: ieee_value,ieee_quiet_nan
implicit none
type(type_bulk_temporal_mean),target :: bulk
type(type_horizontal_temporal_mean),target :: horizontal
real(8),pointer :: output(:)
integer :: i,pass,ncid,xdim,ydim,varid
allocate(bulk%history(3,5),horizontal%history(5))
model%diagnostic_variables(2)%properties%persistent=.true.
diagnostic_values=-999d0
model%root%first_expression=>bulk;bulk%next=>horizontal
bulk%history=0;horizontal%history=0
output=>bulk%history(:,5)
call ensure_temporal_memory()
do i=1,2
 call restore_temporal_memory(i,1)
 if(bulk%ioldest/=-1.or.bulk%valid.or.horizontal%ioldest/=-1)stop 1
 if(any(bulk%history/=0).or.any(horizontal%history/=0))stop 2
 if(any(diagnostic_values(:,2)/=-1d0))stop 9
 diagnostic_values(:,2)=1000d0*i
 bulk%history=100d0*i;horizontal%history=10d0*i
 bulk%last_time=86400d0+i;bulk%next_save_time=90000d0+i
 bulk%ioldest=i;bulk%valid=i==2
 horizontal%last_time=86400d0+2*i;horizontal%next_save_time=90000d0+2*i
 horizontal%ioldest=3-i
 call store_temporal_memory(i,1)
end do
do pass=1,3
 do i=2,1,-1
  call restore_temporal_memory(i,1)
  if(any(bulk%history/=100d0*i).or.any(horizontal%history/=10d0*i))stop 3
  if(any(diagnostic_values(:,2)/=1000d0*i))stop 10
  if(any(output/=100d0*i))stop 4
  if(bulk%ioldest/=i.or.(bulk%valid.neqv.(i==2)))stop 5
  if(bulk%last_time/=86400d0+i.or.bulk%next_save_time/=90000d0+i)stop 6
  if(horizontal%ioldest/=3-i.or.horizontal%last_time/=86400d0+2*i)stop 7
  if(horizontal%next_save_time/=90000d0+2*i)stop 8
 end do
end do
print *, 'COLUMN MEMORY PASS'
end program
'''
    if checkpoint!='none':
        tamper=''
        if checkpoint=='legacy':tamper="call memory_netcdf_check(nf90_del_att(ncid,nf90_global,'fabm_memory_version'))"
        if checkpoint=='identity':tamper="call memory_netcdf_check(nf90_inq_varid(ncid,'fabm_memory_0001_history',varid))\ncall memory_netcdf_check(nf90_put_att(ncid,varid,'expression','wrong_expression'))"
        if checkpoint=='period':tamper="call memory_netcdf_check(nf90_inq_varid(ncid,'fabm_memory_0001_history',varid))\ncall memory_netcdf_check(nf90_put_att(ncid,varid,'period',12d0))"
        if checkpoint=='diagnostic_identity':tamper="call memory_netcdf_check(nf90_inq_varid(ncid,'fabm_diagnostic_memory',varid))\ncall memory_netcdf_check(nf90_put_att(ncid,varid,'name_0001','wrong_onset'))"
        # Ring and nonfinite corruption are written by the actual serializer.
        corrupt=''
        if checkpoint=='ring':corrupt='temporal_memory(1)%oldest(1,1)=0'
        if checkpoint=='nonfinite':corrupt='temporal_memory(1)%history(1,1,1,1)=ieee_value(0d0,ieee_quiet_nan)'
        if checkpoint=='fill':corrupt='temporal_memory(1)%history(1,1,1,1)=nf90_fill_double'
        if checkpoint=='diagnostic_fill':corrupt='diagnostic_memory(1,1,1,1)=nf90_fill_double'
        io=f'''
{corrupt}
call memory_netcdf_check(nf90_create('memory.nc',nf90_clobber,ncid))
call memory_netcdf_check(nf90_def_dim(ncid,'xax',2,xdim))
call memory_netcdf_check(nf90_def_dim(ncid,'yax',1,ydim))
call define_temporal_memory(ncid,xdim,ydim)
{tamper}
call memory_netcdf_check(nf90_enddef(ncid))
call write_temporal_memory(ncid,1,1)
call memory_netcdf_check(nf90_close(ncid))
do i=1,size(temporal_memory)
 temporal_memory(i)%history=-333d0
 temporal_memory(i)%last_time=0;temporal_memory(i)%next_time=0
 temporal_memory(i)%oldest=-1;temporal_memory(i)%valid=0
end do
diagnostic_memory=-222d0
call memory_netcdf_check(nf90_open('memory.nc',nf90_nowrite,ncid))
call read_temporal_memory(ncid,1,1,2,1,1,1)
call memory_netcdf_check(nf90_close(ncid))
'''
        program=program.replace('do pass=1,3',io+'\ndo pass=1,3')
    path=tmp_path/'memory.f90';path.write_text(prefix+types+'\ncontains\n'+routines+program)
    env=dict(os.environ,PATH=str(compiler.parent)+os.pathsep+os.environ['PATH'])
    exe=tmp_path/'memory.exe'
    runtime=ROOT/'3DWET/bin/runtime'
    env['PATH']=str(runtime)+os.pathsep+env['PATH']
    built=subprocess.run([str(compiler),'-I'+str(compiler.parent.parent/'include'),'-ffree-line-length-none','-fcheck=all',str(path),str(runtime/'libnetcdff-7.dll'),str(runtime/'libnetcdf.dll'),'-o',str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert built.returncode==0,built.stderr
    ran=subprocess.run([str(exe)],cwd=tmp_path,env=env,capture_output=True,text=True)
    if checkpoint not in ('none','roundtrip'):
        assert ran.returncode==77,ran.stdout+ran.stderr
        assert 'FABM temporal checkpoint' in ran.stdout
    else:
        assert ran.returncode==0,ran.stdout+ran.stderr
