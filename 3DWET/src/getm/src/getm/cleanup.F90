#include "cppdefs.h"
!-----------------------------------------------------------------------
!BOP
!
! !ROUTINE:  clean_up - a wrapper to perform cleanup
!
! !INTERFACE:
   subroutine clean_up(dryrun,runtype,loop)
!
! !DESCRIPTION:
!  Calls the various model components clean up procedures. The called routines
!  should de-allocate memory close open files etc.
!  Some run-time statistics could also be put here.
!
! !USES:
   use input, only: clean_input
   use meteo, only: clean_meteo
   use m2d, only: clean_2d
#ifndef NO_3D
   use rivers, only: clean_rivers
   use m3d, only: clean_3d
#endif
   use register_all_variables, only: fm
   use output, only: clean_output
   use output_manager
   use kurt_parallel, only: clean_parallel
#ifdef _OPENMP
   use omp_lib, only: omp_pause_resource_all, omp_pause_hard
#endif
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   logical, intent(in)                 :: dryrun
   integer, intent(in)                 :: runtype
!
! !INPUT/OUTPUT PARAMETERS:
   integer, intent(inout)              :: loop
#ifdef _OPENMP
   integer                             :: pause_status
#endif
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding & Hans Burchard
!
!EOP
!-----------------------------------------------------------------------
!BOC
#ifdef DEBUG
   integer, save :: Ncall = 0
   Ncall = Ncall+1
   write(debug,*) 'clean_up() # ',Ncall
#endif

   STDERR LINE
   STDERR 'Cleaning up....'
   STDERR LINE

   call clean_meteo()

   call clean_2d()

#ifndef NO_3D
   call clean_rivers()
   call clean_3d()
#endif

   if( .not. dryrun ) then
      call clean_output(runtype,loop)
   end if
   call output_manager_clean()

   call fm%finalize()

   call clean_input()

   call clean_parallel()

#ifdef _OPENMP
   ! Release the OpenMP pool before the process exits. A static MinGW
   ! libgomp otherwise can wait forever while the runtime is torn down.
   pause_status = omp_pause_resource_all(omp_pause_hard)
#endif

#ifdef DEBUG
   write(debug,*) 'Leaving clean_up()'
   write(debug,*)
#endif

   return
   end subroutine clean_up
!EOC

!-----------------------------------------------------------------------
! Copyright (C) 2001 - Hans Burchard and Karsten Bolding               !
!-----------------------------------------------------------------------
