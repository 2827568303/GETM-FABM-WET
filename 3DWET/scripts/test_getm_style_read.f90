program test_getm_style_read
  use netcdf
  implicit none
  integer :: ncid, var_id, err
  integer :: nx, ny, nt
  integer :: lon_id, lat_id, time_id
  integer :: iextr, jextr
  real(kind=4), allocatable :: wrk(:,:)      ! GETM style: wrk(iextr, jextr)
  integer :: start(3), edges(3)
  integer :: indx
  character(len=256) :: fn = 'test_reversed.nc'

  print *, 'Testing GETM-style read on (time, lat, lon) variable'
  print *, '======================================================'

  err = nf90_open(fn, NF90_NOWRITE, ncid)
  if (err .ne. NF90_NOERR) then
    print *, 'OPEN failed: ', trim(nf90_strerror(err))
    stop
  end if

  ! GETM finds dimensions by NAME (not position)
  err = nf90_inq_dimid(ncid, "lon", lon_id)
  err = nf90_inquire_dimension(ncid, lon_id, len=iextr)  ! iextr = lon len
  err = nf90_inq_dimid(ncid, "lat", lat_id)
  err = nf90_inquire_dimension(ncid, lat_id, len=jextr)  ! jextr = lat len
  err = nf90_inq_dimid(ncid, "time", time_id)
  err = nf90_inquire_dimension(ncid, time_id, len=nt)
  print *, 'iextr(lon)=', iextr, ' jextr(lat)=', jextr, ' nt(time)=', nt

  err = nf90_inq_varid(ncid, "u10", var_id)

  ! GETM allocates wrk(iextr, jextr) = wrk(lon, lat)
  allocate(wrk(iextr, jextr))

  ! GETM sets start/edges exactly like this:
  start(1) = 1; start(2) = 1
  edges(1) = iextr; edges(2) = jextr
  edges(3) = 1

  ! Test reading time step 1 (indx=1)
  indx = 1
  start(3) = indx
  err = nf90_get_var(ncid, var_id, wrk, start, edges)
  print *, 'Time step 1: err=', err
  if (err .eq. NF90_NOERR) then
    print *, '  SUCCESS! min/max=', minval(wrk), maxval(wrk)
    print *, '  Expected: 0.0 / 0.0 (t=0 * 0.1)'
  end if

  ! Test reading time step 15 (indx=15)
  indx = 15
  start(3) = indx
  err = nf90_get_var(ncid, var_id, wrk, start, edges)
  print *, 'Time step 15: err=', err
  if (err .eq. NF90_NOERR) then
    print *, '  SUCCESS! min/max=', minval(wrk), maxval(wrk)
    print *, '  Expected: 1.4 / 1.4 (t=14 * 0.1)'
  end if

  ! Test reading time step 31 (indx=31, last)
  indx = 31
  start(3) = indx
  err = nf90_get_var(ncid, var_id, wrk, start, edges)
  print *, 'Time step 31: err=', err
  if (err .eq. NF90_NOERR) then
    print *, '  SUCCESS! min/max=', minval(wrk), maxval(wrk)
    print *, '  Expected: 3.0 / 3.0 (t=30 * 0.1)'
  end if

  err = nf90_close(ncid)
  print *, 'Done.'
end program
