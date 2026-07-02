program test_read_nc3
  use netcdf
  implicit none
  integer :: ncid, var_id, err
  integer :: nx, ny, nt
  integer :: lon_id, lat_id, time_id
  real(kind=4), allocatable :: wrk3d(:,:,:)
  real(kind=4), allocatable :: wrk2d(:,:)
  integer :: start(3), edges(3)
  character(len=256) :: fn = 'test_nc3.nc'

  print *, 'Testing NETCDF3_CLASSIC 3D read'
  print *, '==================================='

  err = nf90_open(fn, NF90_NOWRITE, ncid)
  if (err .ne. NF90_NOERR) then
    print *, 'OPEN failed: ', trim(nf90_strerror(err))
    stop
  end if

  err = nf90_inq_dimid(ncid, "lon", lon_id)
  err = nf90_inquire_dimension(ncid, lon_id, len=nx)
  err = nf90_inq_dimid(ncid, "lat", lat_id)
  err = nf90_inquire_dimension(ncid, lat_id, len=ny)
  err = nf90_inq_dimid(ncid, "time", time_id)
  err = nf90_inquire_dimension(ncid, time_id, len=nt)
  print *, 'Dimensions: lon=', nx, ' lat=', ny, ' time=', nt

  err = nf90_inq_varid(ncid, "u10", var_id)
  if (err .ne. NF90_NOERR) then
    print *, 'INQ_VARID failed: ', trim(nf90_strerror(err))
    stop
  end if

  ! Test 1: 2D slice with 3D start/edges (GETM style)
  allocate(wrk2d(nx, ny))
  start = (/1, 1, 1/)
  edges = (/nx, ny, 1/)
  err = nf90_get_var(ncid, var_id, wrk2d, start, edges)
  print *, 'Test 1 (2D slice, GETM style): err=', err
  if (err .eq. NF90_NOERR) print *, '  min/max=', minval(wrk2d), maxval(wrk2d)

  ! Test 2: 3D array with 3D start/edges
  deallocate(wrk2d)
  allocate(wrk3d(nx, ny, 1))
  err = nf90_get_var(ncid, var_id, wrk3d, start, edges)
  print *, 'Test 2 (3D slice): err=', err
  if (err .eq. NF90_NOERR) print *, '  min/max=', minval(wrk3d), maxval(wrk3d)

  ! Test 3: Read entire variable
  deallocate(wrk3d)
  allocate(wrk3d(nx, ny, nt))
  err = nf90_get_var(ncid, var_id, wrk3d)
  print *, 'Test 3 (entire variable): err=', err
  if (err .eq. NF90_NOERR) print *, '  min/max=', minval(wrk3d), maxval(wrk3d)

  err = nf90_close(ncid)
  print *, 'Done.'
end program
