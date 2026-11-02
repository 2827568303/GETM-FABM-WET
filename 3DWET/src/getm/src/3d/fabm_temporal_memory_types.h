   type type_column_temporal_memory
      class(type_expression), pointer :: expression => null()
      REALTYPE, allocatable :: history(:,:,:,:),last_time(:,:),next_time(:,:)
      integer, allocatable :: oldest(:,:),valid(:,:)
   end type
   type(type_column_temporal_memory), allocatable :: temporal_memory(:)
   integer, allocatable :: diagnostic_memory_indices(:)
   REALTYPE, allocatable :: diagnostic_memory(:,:,:,:)
