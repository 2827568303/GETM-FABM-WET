   ! Included inside getm_fabm; not an independent compilation unit.
   subroutine ensure_temporal_memory()
      class(type_expression), pointer :: expression
      integer :: n,q,nz,ns
      if (allocated(temporal_memory)) return
      n=0
      expression=>model%root%first_expression
      do while(associated(expression))
         select type(expression)
         class is(type_bulk_temporal_mean)
            n=n+1
         class is(type_horizontal_temporal_mean)
            n=n+1
         end select
         expression=>expression%next
      end do
      allocate(temporal_memory(n))
      q=0
      expression=>model%root%first_expression
      do while(associated(expression))
         nz=0
         select type(expression)
         class is(type_bulk_temporal_mean)
            nz=size(expression%history,1);ns=expression%n+3
         class is(type_horizontal_temporal_mean)
            nz=1;ns=expression%n+3
         end select
         if(nz>0)then
            q=q+1
            temporal_memory(q)%expression=>expression
            allocate(temporal_memory(q)%history(imin:imax,jmin:jmax,nz,ns))
            allocate(temporal_memory(q)%last_time(imin:imax,jmin:jmax),temporal_memory(q)%next_time(imin:imax,jmin:jmax))
            allocate(temporal_memory(q)%oldest(imin:imax,jmin:jmax),temporal_memory(q)%valid(imin:imax,jmin:jmax))
            temporal_memory(q)%history=0
            temporal_memory(q)%last_time=0
            temporal_memory(q)%next_time=0
            temporal_memory(q)%oldest=-1
            temporal_memory(q)%valid=0
         end if
         expression=>expression%next
      end do
      call ensure_diagnostic_memory()
   end subroutine ensure_temporal_memory

   subroutine restore_temporal_memory(i,j)
      integer,intent(in) :: i,j
      integer :: q
      REALTYPE,pointer :: data(:)
      call ensure_temporal_memory()
      do q=1,size(temporal_memory)
         select type(expression=>temporal_memory(q)%expression)
         class is(type_bulk_temporal_mean)
            expression%history=temporal_memory(q)%history(i,j,:,:)
            expression%last_time=temporal_memory(q)%last_time(i,j)
            expression%next_save_time=temporal_memory(q)%next_time(i,j)
            expression%ioldest=temporal_memory(q)%oldest(i,j)
            expression%valid=temporal_memory(q)%valid(i,j)==1
         class is(type_horizontal_temporal_mean)
            expression%history=temporal_memory(q)%history(i,j,1,:)
            expression%last_time=temporal_memory(q)%last_time(i,j)
            expression%next_save_time=temporal_memory(q)%next_time(i,j)
            expression%ioldest=temporal_memory(q)%oldest(i,j)
         end select
      end do
      do q=1,size(diagnostic_memory_indices)
         data=>fabm_get_bulk_diagnostic_data(model,diagnostic_memory_indices(q))
         data=diagnostic_memory(i,j,:,q)
      end do
   end subroutine restore_temporal_memory

   subroutine store_temporal_memory(i,j)
      integer,intent(in) :: i,j
      integer :: q
      REALTYPE,pointer :: data(:)
      do q=1,size(temporal_memory)
         select type(expression=>temporal_memory(q)%expression)
         class is(type_bulk_temporal_mean)
            temporal_memory(q)%history(i,j,:,:)=expression%history
            temporal_memory(q)%last_time(i,j)=expression%last_time
            temporal_memory(q)%next_time(i,j)=expression%next_save_time
            temporal_memory(q)%oldest(i,j)=expression%ioldest
            temporal_memory(q)%valid(i,j)=merge(1,0,expression%valid)
         class is(type_horizontal_temporal_mean)
            temporal_memory(q)%history(i,j,1,:)=expression%history
            temporal_memory(q)%last_time(i,j)=expression%last_time
            temporal_memory(q)%next_time(i,j)=expression%next_save_time
            temporal_memory(q)%oldest(i,j)=expression%ioldest
         end select
      end do
      do q=1,size(diagnostic_memory_indices)
         data=>fabm_get_bulk_diagnostic_data(model,diagnostic_memory_indices(q))
         diagnostic_memory(i,j,:,q)=data
      end do
   end subroutine store_temporal_memory

   subroutine ensure_diagnostic_memory()
      integer :: q,n,index
      if(allocated(diagnostic_memory_indices))return
      n=0
      do index=1,size(model%diagnostic_variables)
         if(model%diagnostic_variables(index)%properties%get_logical('column_memory',default=.false.))n=n+1
      end do
      allocate(diagnostic_memory_indices(n),diagnostic_memory(imin:imax,jmin:jmax,kmax,n))
      q=0
      do index=1,size(model%diagnostic_variables)
         if(.not.model%diagnostic_variables(index)%properties%get_logical('column_memory',default=.false.))cycle
         if(model%diagnostic_variables(index)%save_index<=0) &
            call getm_error('FABM column memory','Stateful diagnostic must have saved data')
         q=q+1;diagnostic_memory_indices(q)=index
         diagnostic_memory(:,:,:,q)=model%diagnostic_variables(index)%properties%get_real('column_memory_initial',default=0.0d0)
      end do
   end subroutine ensure_diagnostic_memory
