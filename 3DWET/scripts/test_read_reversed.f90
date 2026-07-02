program test_read_reversed
  use netcdf
  implicit none
  integer :: ncid, var_id, err
  integer :: nx, ny, nt
  integer :: lon_id, lat_id, time_id
  real(kind=4), allocatable :: wrk_normal(:,:,:)      ! (nx, ny, nt) - C order
  real(kind=4), allocatable :: wrk_reversed(:,:,:)    ! (nt, ny, nx) - Fortran reversed
  real(kind=4), allocatable :: wrk2d_normal(:,:)      ! (nx, ny)
  real(kind=4), allocatable :: wrk2d_reversed(:,:)    ! (ny, nx)
  integer :: start(3), edges(3)
  character(len=256) :: fn = 'test_nc3.nc'

  print *, 'Testing dimension order hypothesis'
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

  ! Test A: Normal order (nx, ny, nt) - entire variable
  allocate(wrk_normal(nx, ny, nt))
  err = nf90_get_var(ncid, var_id, wrk_normal)
  print *, 'Test A (normal nx,ny,nt): err=', err

  ! Test B: Reversed order (nt, ny, nx) - entire variable
  allocate(wrk_reversed(nt, ny, nx))
  err = nf90_get_var(ncid, var_id, wrk_reversed)
  print *, 'Test B (reversed nt,ny,nx): err=', err
  if (err .eq. NF90_NOERR) then
    print *, '  REVERSED ORDER WORKS!'
    print *, '  min/max=', minval(wrk_reversed), maxval(wrk_reversed)
  end if

  ! Test C: 2D slice with normal order start/edges, reversed array
  start = (/1, 1, 1/)
  edges = (/nx, ny, 1/)
  deallocate(wrk2d_normal, wrk2d_reversed)
  allocate(wrk2d_normal(nx, ny))
  err = nf90_get_var(ncid, var_id, wrk2d_normal, start, edges)
  print *, 'Test C (2D normal array, normal start/edges): err=', err

  ! Test D: 2D slice with reversed start/edges, reversed array
  ! If Fortran reverses, then start/edges should also be reversed:
  ! start = (time, lat, lon) = (1, 1, 1)
  ! edges = (time, lat, lon) = (1, ny, nx)
  start = (/1, 1, 1/)
  edges = (/1, ny, nx/)
  allocate(wrk2d_reversed(ny, nx))
  err = nf90_get_var(ncid, var_id, wrk2d_reversed, start, edges)
  print *, 'Test D (2D reversed array, reversed start/edges): err=', err
  if (err .eq. NF90_NOERR) then
    print *, '  REVERSED 2D WORKS!'
    print *, '  min/max=', minval(wrk2d_reversed), maxval(wrk2d_reversed)
  end if

  ! Test E: 2D slice with normal array but reversed start/edges
  start = (/1, 1, 1/)
  edges = (/1, ny, nx/)
  err = nf90_get_var(ncid, var_id, wrk2d_normal, start, edges)
  print *, 'Test E (2D normal array, reversed start/edges): err=', err

  err = nf90_close(ncid)
  print *, 'Done.'
end program
