   ! Included inside getm_fabm; not an independent compilation unit.
   subroutine memory_netcdf_check(status)
      use netcdf
      integer,intent(in) :: status
      if(status/=nf90_noerr)then
         call getm_error('FABM temporal checkpoint',trim(nf90_strerror(status)))
         stop 'FABM temporal checkpoint is missing or incompatible'
      end if
   end subroutine memory_netcdf_check

   function temporal_prefix(q) result(prefix)
      integer,intent(in) :: q
      character(len=32) :: prefix
      write(prefix,'(a,i4.4)') 'fabm_memory_',q
   end function temporal_prefix

   subroutine define_temporal_memory(ncid,xdim,ydim)
      use netcdf
      integer,intent(in) :: ncid,xdim,ydim
      integer :: q,zdim,sdim,varid,n,kind
      REALTYPE :: period,missing
      character(len=32) :: prefix
      call ensure_temporal_memory()
      call memory_netcdf_check(nf90_put_att(ncid,nf90_global,'fabm_memory_version',2))
      call memory_netcdf_check(nf90_put_att(ncid,nf90_global,'fabm_memory_timebase','GETM Julian-day seconds'))
      call memory_netcdf_check(nf90_put_att(ncid,nf90_global,'fabm_memory_count',size(temporal_memory)))
      do q=1,size(temporal_memory)
         prefix=temporal_prefix(q)
         select type(expression=>temporal_memory(q)%expression)
         class is(type_bulk_temporal_mean)
            kind=1;n=expression%n;period=expression%period;missing=expression%missing_value
         class is(type_horizontal_temporal_mean)
            kind=2;n=expression%n;period=expression%period;missing=0
         end select
         call memory_netcdf_check(nf90_def_dim(ncid,trim(prefix)//'_levels',size(temporal_memory(q)%history,3),zdim))
         call memory_netcdf_check(nf90_def_dim(ncid,trim(prefix)//'_slots',n+3,sdim))
         call memory_netcdf_check(nf90_def_var(ncid,trim(prefix)//'_history',nf90_double,(/xdim,ydim,zdim,sdim/),varid))
         call memory_netcdf_check(nf90_put_att(ncid,varid,'expression',temporal_memory(q)%expression%output_name))
         call memory_netcdf_check(nf90_put_att(ncid,varid,'kind',kind))
         call memory_netcdf_check(nf90_put_att(ncid,varid,'n',n))
         call memory_netcdf_check(nf90_put_att(ncid,varid,'period',period))
         call memory_netcdf_check(nf90_put_att(ncid,varid,'expression_missing_value',missing))
         call memory_netcdf_check(nf90_def_var(ncid,trim(prefix)//'_last',nf90_double,(/xdim,ydim/),varid))
         call memory_netcdf_check(nf90_def_var(ncid,trim(prefix)//'_next',nf90_double,(/xdim,ydim/),varid))
         call memory_netcdf_check(nf90_def_var(ncid,trim(prefix)//'_oldest',nf90_int,(/xdim,ydim/),varid))
         call memory_netcdf_check(nf90_def_var(ncid,trim(prefix)//'_valid',nf90_int,(/xdim,ydim/),varid))
      end do
      call define_diagnostic_memory(ncid,xdim,ydim)
   end subroutine define_temporal_memory

   subroutine write_temporal_memory(ncid,file_i,file_j)
      use netcdf
      integer,intent(in) :: ncid,file_i,file_j
      integer :: q,varid,xy(2),counts(4)
      character(len=32) :: prefix
      xy=(/file_i,file_j/)
      do q=1,size(temporal_memory)
         prefix=temporal_prefix(q)
         counts=shape(temporal_memory(q)%history)
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_history',varid))
         call memory_netcdf_check(nf90_put_var(ncid,varid,temporal_memory(q)%history,start=(/xy,1,1/),count=counts))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_last',varid))
         call memory_netcdf_check(nf90_put_var(ncid,varid,temporal_memory(q)%last_time,start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_next',varid))
         call memory_netcdf_check(nf90_put_var(ncid,varid,temporal_memory(q)%next_time,start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_oldest',varid))
         call memory_netcdf_check(nf90_put_var(ncid,varid,temporal_memory(q)%oldest,start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_valid',varid))
         call memory_netcdf_check(nf90_put_var(ncid,varid,temporal_memory(q)%valid,start=xy,count=counts(1:2)))
      end do
      call write_diagnostic_memory(ncid,file_i,file_j)
   end subroutine write_temporal_memory

   subroutine read_temporal_memory(ncid,local_i,local_j,nx,ny,file_i,file_j)
      use netcdf
      use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
      integer,intent(in) :: ncid,local_i,local_j,nx,ny,file_i,file_j
      integer :: q,varid,version,count,n,kind,expected_kind,xy(2),counts(4),i,j
      REALTYPE :: period,expected_period,missing,expected_missing
      character(len=256) :: identity,timebase
      character(len=32) :: prefix
      call ensure_temporal_memory()
      if(size(temporal_memory)==0.and.size(diagnostic_memory_indices)==0)return
      ! Legacy checkpoints cannot reproduce a warmed-up temporal mean.
      call memory_netcdf_check(nf90_get_att(ncid,nf90_global,'fabm_memory_version',version))
      call memory_netcdf_check(nf90_get_att(ncid,nf90_global,'fabm_memory_count',count))
      call memory_netcdf_check(nf90_get_att(ncid,nf90_global,'fabm_memory_timebase',timebase))
      if(version/=2.or.count/=size(temporal_memory).or.trim(timebase)/='GETM Julian-day seconds') &
         call memory_netcdf_check(nf90_einval)
      xy=(/file_i,file_j/)
      do q=1,size(temporal_memory)
         prefix=temporal_prefix(q)
         counts=shape(temporal_memory(q)%history);counts(1:2)=(/nx,ny/)
         select type(expression=>temporal_memory(q)%expression)
         class is(type_bulk_temporal_mean)
            expected_kind=1;n=expression%n;expected_period=expression%period;expected_missing=expression%missing_value
         class is(type_horizontal_temporal_mean)
            expected_kind=2;n=expression%n;expected_period=expression%period;expected_missing=0
         end select
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_history',varid))
         call memory_netcdf_check(nf90_get_att(ncid,varid,'expression',identity))
         call memory_netcdf_check(nf90_get_att(ncid,varid,'kind',kind))
         call memory_netcdf_check(nf90_get_att(ncid,varid,'period',period))
         call memory_netcdf_check(nf90_get_att(ncid,varid,'expression_missing_value',missing))
         call memory_netcdf_check(nf90_get_att(ncid,varid,'n',count))
         if(trim(identity)/=trim(temporal_memory(q)%expression%output_name).or.kind/=expected_kind.or. &
            count/=n.or.period/=expected_period.or.missing/=expected_missing)call memory_netcdf_check(nf90_einval)
         call memory_netcdf_check(nf90_get_var(ncid,varid,temporal_memory(q)%history(local_i:local_i+nx-1,local_j:local_j+ny-1,:,:), &
                                             start=(/xy,1,1/),count=counts))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_last',varid))
         call memory_netcdf_check(nf90_get_var(ncid,varid,temporal_memory(q)%last_time(local_i:local_i+nx-1,local_j:local_j+ny-1),start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_next',varid))
         call memory_netcdf_check(nf90_get_var(ncid,varid,temporal_memory(q)%next_time(local_i:local_i+nx-1,local_j:local_j+ny-1),start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_oldest',varid))
         call memory_netcdf_check(nf90_get_var(ncid,varid,temporal_memory(q)%oldest(local_i:local_i+nx-1,local_j:local_j+ny-1),start=xy,count=counts(1:2)))
         call memory_netcdf_check(nf90_inq_varid(ncid,trim(prefix)//'_valid',varid))
         call memory_netcdf_check(nf90_get_var(ncid,varid,temporal_memory(q)%valid(local_i:local_i+nx-1,local_j:local_j+ny-1),start=xy,count=counts(1:2)))
         if(.not.all(ieee_is_finite(temporal_memory(q)%history)).or. &
            .not.all(ieee_is_finite(temporal_memory(q)%last_time)).or. &
            .not.all(ieee_is_finite(temporal_memory(q)%next_time)))call memory_netcdf_check(nf90_einval)
         if(any(temporal_memory(q)%history==nf90_fill_double).or. &
            any(temporal_memory(q)%last_time==nf90_fill_double).or. &
            any(temporal_memory(q)%next_time==nf90_fill_double))call memory_netcdf_check(nf90_einval)
         do j=local_j,local_j+ny-1
            do i=local_i,local_i+nx-1
               if(temporal_memory(q)%oldest(i,j)/=-1.and. &
                  (temporal_memory(q)%oldest(i,j)<1.or.temporal_memory(q)%oldest(i,j)>n))call memory_netcdf_check(nf90_einval)
               if(temporal_memory(q)%valid(i,j)<0.or.temporal_memory(q)%valid(i,j)>1)call memory_netcdf_check(nf90_einval)
               if(temporal_memory(q)%oldest(i,j)>0.and.temporal_memory(q)%next_time(i,j)<=temporal_memory(q)%last_time(i,j)) &
                  call memory_netcdf_check(nf90_einval)
            end do
         end do
      end do
      call read_diagnostic_memory(ncid,local_i,local_j,nx,ny,file_i,file_j)
   end subroutine read_temporal_memory

   subroutine define_diagnostic_memory(ncid,xdim,ydim)
      use netcdf
      integer,intent(in) :: ncid,xdim,ydim
      integer :: zdim,ndim,varid,q,index
      character(len=32) :: label
      call memory_netcdf_check(nf90_put_att(ncid,nf90_global,'fabm_diagnostic_memory_count',size(diagnostic_memory_indices)))
      if(size(diagnostic_memory_indices)==0)return
      call memory_netcdf_check(nf90_def_dim(ncid,'fabm_diagnostic_memory_levels',kmax,zdim))
      call memory_netcdf_check(nf90_def_dim(ncid,'fabm_diagnostic_memory_fields',size(diagnostic_memory_indices),ndim))
      call memory_netcdf_check(nf90_def_var(ncid,'fabm_diagnostic_memory',nf90_double,(/xdim,ydim,zdim,ndim/),varid))
      do q=1,size(diagnostic_memory_indices)
         index=diagnostic_memory_indices(q)
         write(label,'(a,i4.4)')'name_',q
         call memory_netcdf_check(nf90_put_att(ncid,varid,trim(label),model%diagnostic_variables(index)%name))
      end do
   end subroutine define_diagnostic_memory

   subroutine write_diagnostic_memory(ncid,file_i,file_j)
      use netcdf
      integer,intent(in) :: ncid,file_i,file_j
      integer :: varid
      if(size(diagnostic_memory_indices)==0)return
      call memory_netcdf_check(nf90_inq_varid(ncid,'fabm_diagnostic_memory',varid))
      call memory_netcdf_check(nf90_put_var(ncid,varid,diagnostic_memory,start=(/file_i,file_j,1,1/),count=shape(diagnostic_memory)))
   end subroutine write_diagnostic_memory

   subroutine read_diagnostic_memory(ncid,local_i,local_j,nx,ny,file_i,file_j)
      use netcdf
      use,intrinsic :: ieee_arithmetic,only:ieee_is_finite
      integer,intent(in) :: ncid,local_i,local_j,nx,ny,file_i,file_j
      integer :: count,varid,q,index
      REALTYPE :: minimum,maximum
      character(len=32) :: label
      character(len=256) :: identity
      call memory_netcdf_check(nf90_get_att(ncid,nf90_global,'fabm_diagnostic_memory_count',count))
      if(count/=size(diagnostic_memory_indices))call memory_netcdf_check(nf90_einval)
      if(count==0)return
      call memory_netcdf_check(nf90_inq_varid(ncid,'fabm_diagnostic_memory',varid))
      do q=1,count
         index=diagnostic_memory_indices(q)
         write(label,'(a,i4.4)')'name_',q
         call memory_netcdf_check(nf90_get_att(ncid,varid,trim(label),identity))
         if(trim(identity)/=trim(model%diagnostic_variables(index)%name))call memory_netcdf_check(nf90_einval)
      end do
      call memory_netcdf_check(nf90_get_var(ncid,varid,diagnostic_memory(local_i:local_i+nx-1,local_j:local_j+ny-1,:,:), &
         start=(/file_i,file_j,1,1/),count=(/nx,ny,kmax,count/)))
      if(.not.all(ieee_is_finite(diagnostic_memory)).or.any(diagnostic_memory==nf90_fill_double))call memory_netcdf_check(nf90_einval)
      do q=1,count
         index=diagnostic_memory_indices(q)
         minimum=model%diagnostic_variables(index)%properties%get_real('column_memory_minimum',default=-huge(1.0d0))
         maximum=model%diagnostic_variables(index)%properties%get_real('column_memory_maximum',default=huge(1.0d0))
         if(any(diagnostic_memory(:,:,:,q)<minimum).or.any(diagnostic_memory(:,:,:,q)>maximum))call memory_netcdf_check(nf90_einval)
      end do
   end subroutine read_diagnostic_memory
