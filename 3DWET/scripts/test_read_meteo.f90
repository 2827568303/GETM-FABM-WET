program test_read_meteo
  use netcdf
  implicit none
  integer :: ncid, u10_id, err
  integer :: start(3), edges(3)
  integer :: nx, ny, nt
  integer :: lon_id, lat_id, time_id
  real(kind=4), allocatable :: wrk2d(:,:)
  real(kind=4), allocatable :: wrk3d(:,:,:)
  character(len=256) :: fn = 'meteo.nc'

  print *, "Testing NetCDF Fortran read of meteo.nc"
  print *, "========================================"

  err = nf90_open(fn, NF90_NOWRITE, ncid)
  if (err /= NF90_NOERR) then
    print *, "ERROR opening file: ", trim(nf90_strerror(err))
    stop
  end if

  ! Get dimension IDs and lengths
  err = nf90_inq_dimid(ncid, "lon", lon_id)
  err = nf90_inquire_dimension(ncid, lon_id, len=nx)
  err = nf90_inq_dimid(ncid, "lat", lat_id)
  err = nf90_inquire_dimension(ncid, lat_id, len=ny)
  err = nf90_inq_dimid(ncid, "time", time_id)
  err = nf90_inquire_dimension(ncid, time_id, len=nt)

  print *, "Dimensions: lon=", nx, " lat=", ny, " time=", nt

  ! Get variable ID
  err = nf90_inq_varid(ncid, "u10", u10_id)
  if (err /= NF90_NOERR) then
    print *, "ERROR getting u10 id: ", trim(nf90_strerror(err))
    stop
  end if

  ! Test 1: 2D array with 3D start/edges (GETM style)
  print *, ""
  print *, "Test 1: 2D wrk with 3D start/edges (GETM style)"
  allocate(wrk2d(nx, ny))
  start = (/1, 1, 1/)
  edges = (/nx, ny, 1/)
  print *, "  start=", start
  print *, "  edges=", edges
  print *, "  shape(wrk2d)=", shape(wrk2d)
  err = nf90_get_var(ncid, u10_id, wrk2d, start, edges)
  print *, "  err=", err, " (", trim(nf90_strerror(err)), ")"
  if (err == NF90_NOERR) then
    print *, "  min/max=", minval(wrk2d), maxval(wrk2d)
  end if
  deallocate(wrk2d)

  ! Test 2: 3D array with 3D start/edges
  print *, ""
  print *, "Test 2: 3D wrk3d with 3D start/edges"
  allocate(wrk3d(nx, ny, 1))
  start = (/1, 1, 1/)
  edges = (/nx, ny, 1/)
  print *, "  start=", start
  print *, "  edges=", edges
  print *, "  shape(wrk3d)=", shape(wrk3d)
  err = nf90_get_var(ncid, u10_id, wrk3d, start, edges)
  print *, "  err=", err, " (", trim(nf90_strerror(err)), ")"
  if (err == NF90_NOERR) then
    print *, "  min/max=", minval(wrk3d), maxval(wrk3d)
  end if
  deallocate(wrk3d)

  ! Test 3: 3D array with keyword arguments
  print *, ""
  print *, "Test 3: 3D wrk3d with keyword start=/count="
  allocate(wrk3d(nx, ny, 1))
  err = nf90_get_var(ncid, u10_id, wrk3d, start=(/1,1,1/), count=(/nx,ny,1/))
  print *, "  err=", err, " (", trim(nf90_strerror(err)), ")"
  if (err == NF90_NOERR) then
    print *, "  min/max=", minval(wrk3d), maxval(wrk3d)
  end if
  deallocate(wrk3d)

  ! Test 4: Read entire variable
  print *, ""
  print *, "Test 4: Read entire variable (no start/count)"
  allocate(wrk3d(nx, ny, nt))
  err = nf90_get_var(ncid, u10_id, wrk3d)
  print *, "  err=", err, " (", trim(nf90_strerror(err)), ")"
  if (err == NF90_NOERR) then
    print *, "  min/max=", minval(wrk3d), maxval(wrk3d)
  end if
  deallocate(wrk3d)

  err = nf90_close(ncid)
  print *, ""
  print *, "Done."
end program test_read_meteo
