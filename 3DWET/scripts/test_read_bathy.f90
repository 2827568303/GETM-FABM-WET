program test_read_bathy
  use netcdf
  implicit none
  integer :: ncid, var_id, err
  integer :: nx, ny
  integer :: x_id, y_id
  real(kind=4), allocatable :: wrk2d(:,:)
  real(kind=8), allocatable :: wrk2d_dbl(:,:)
  character(len=256) :: fn = 'bathymetry.nc'
  integer :: var_type, natts, ndims
  integer, allocatable :: dimids(:)

  print *, "Testing NetCDF Fortran read of bathymetry.nc"
  print *, "============================================="

  err = nf90_open(fn, NF90_NOWRITE, ncid)
  if (err /= NF90_NOERR) then
    print *, "ERROR opening file: ", trim(nf90_strerror(err))
    stop
  end if

  err = nf90_inq_dimid(ncid, "x", x_id)
  err = nf90_inquire_dimension(ncid, x_id, len=nx)
  err = nf90_inq_dimid(ncid, "y", y_id)
  err = nf90_inquire_dimension(ncid, y_id, len=ny)
  print *, "Dimensions: x=", nx, " y=", ny

  err = nf90_inq_varid(ncid, "bathymetry", var_id)
  if (err /= NF90_NOERR) then
    print *, "ERROR getting bathymetry id: ", trim(nf90_strerror(err))
    stop
  end if

  ! Check variable type and dimensions
  err = nf90_inquire_variable(ncid, var_id, xtype=var_type, ndims=ndims)
  print *, "bathymetry: type=", var_type, " ndims=", ndims
  allocate(dimids(ndims))
  err = nf90_inquire_variable(ncid, var_id, dimids=dimids)
  print *, "  dimids=", dimids

  ! Read entire variable
  print *, ""
  print *, "Test: Read entire bathymetry variable (no start/count)"
  allocate(wrk2d_dbl(nx, ny))
  err = nf90_get_var(ncid, var_id, wrk2d_dbl)
  print *, "  err=", err, " (", trim(nf90_strerror(err)), ")"
  if (err == NF90_NOERR) then
    print *, "  min/max=", minval(wrk2d_dbl), maxval(wrk2d_dbl)
  end if
  deallocate(wrk2d_dbl)
  deallocate(dimids)

  err = nf90_close(ncid)
  print *, ""
  print *, "Done."
end program test_read_bathy
