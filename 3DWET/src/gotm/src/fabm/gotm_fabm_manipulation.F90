#ifdef _FABM_

#include "cppdefs.h"

!-----------------------------------------------------------------------
!BOP
!
! !MODULE: gotm_fabm_manipulation
!
! !INTERFACE:
   module gotm_fabm_manipulation
!
! !DESCRIPTION:
!
! !USES:
   use fabm, only: fabm_is_variable_used
   use fabm, only: type_bulk_variable_id,type_horizontal_variable_id,type_scalar_variable_id
   use fabm_types, only:rk
   use gotm_fabm, only:fabm_calc,model,cc
   use time, only: timestep,julianday,secondsofday,timestr
   use time, only: read_time_string,time_diff,in_time_interval
   implicit none

!  default: all is private.
   private
!
! !PUBLIC MEMBER FUNCTIONS:
   public init_gotm_fabm_manipulation, do_gotm_fabm_manipulations
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding
!
!EOP
!-----------------------------------------------------------------------
!
!  PRIVATE TYPES

   integer,parameter :: maxpathlen=256

!  Information on an observed variable
   type type_fabm_manipulation
      character(len=64)                       :: start = ''           ! When to start the manipulation
      character(len=64)                       :: stop = ''            ! When to stop the manipulation
      character(len=64)                       :: name = ''            ! Variable name to target for manipulation
      integer                                 :: action_type = 0      ! The specification of the action type (1 = instant multiplier, 2 = addition by rate)
      real(rk)                                :: action               ! The action value (multiplier if action_type = 1, or rate (e.g. g/sec) if action_type = 2)
      real(rk)                                :: threshold            ! only apply action if below this value - only used for action_type=2 for now
      logical                                 :: verbose = .true.
      integer                                 :: j1=0, s1=0, j2=0, s2=0
      integer                                 :: kstart, kstop
      integer                                 :: type_data = -1
      type (type_bulk_variable_id)            :: id                   ! FABM identifier of pelagic variable (not associated if variable is not pelagic)
      type (type_horizontal_variable_id)      :: horizontal_id        ! FABM identifier of horizontal variable (not associated if variable is not horizontal)
      ! type (type_scalar_variable_id)          :: scalar_id          ! FABM identifier of scalar variable (not associated if variable is not scalar)
      real(rk), pointer, dimension(:)         :: parray => null()     ! Pointer to data for specific array variable
      real(rk), pointer                       :: pscalar => null()    ! Pointer to data for specific scalar variable
      type (type_fabm_manipulation), pointer  :: next
   end type

!  PRIVATE DATA MEMBERS
   type (type_fabm_manipulation),pointer :: first_manipulation
!
!  PRIVATE PARAMETERS
   integer, parameter   :: type_unknown = 0, type_profile = 1, type_scalar = 2

!-----------------------------------------------------------------------

   contains

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: Initialize input
!
! !INTERFACE:
   subroutine init_gotm_fabm_manipulation(nlev,namlst,fname)
!
! !DESCRIPTION:
!  Initialize files with observations on FABM variables.
!
! !USES:
!
! !INPUT PARAMETERS:
   integer, intent(in)          :: nlev, namlst
   character(len=*), intent(in) :: fname
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding
!
! !LOCAL VARIABLES:
   logical                      :: file_exists
   character(len=64)            :: start, stop, name
   integer                      :: action_type
   real(rk)                     :: action
   real(rk)                     :: threshold
   integer                      :: kstart,kstop
   logical                      :: verbose
   type (type_fabm_manipulation), pointer :: c
   namelist /manipulation/ start,stop,name,action_type,action,threshold,kstart,kstop,verbose
   logical                      :: lake=.true.
   logical                      :: found
   integer                      :: i
!EOP
!-----------------------------------------------------------------------
!BOC
   LEVEL1 'init_gotm_fabm_manipulation'

!  If FABM is not used, return immediately.
   if (.not.fabm_calc) return

!  Initialize empty lists of manipulations.
   nullify(first_manipulation)

!  Open the file that contains zero, one or more namelists specifying manipulations.
   open(namlst,file=fname,action='read',status='old',err=98)
   do

!     Initialize namelist variables.
      start = ''
      stop = ''
      name = ''
      action_type = -1
      action = 0._rk
      threshold = 0._rk
      kstart = 1
      kstop = nlev
      verbose=.false.

!     Read the bio-manipulation namelists

      read(namlst,nml=manipulation,err=99,end=97)

      if (.not.associated(first_manipulation)) then
!        This is the first variable in the file: create it at the head of the list.
         allocate(first_manipulation)
         c => first_manipulation
      else
!        This is not the first variable in the file: append to previous variable.
         c => first_manipulation
         do while (associated(c%next))
            c => c%next
         end do
         allocate(c%next)
         c => c%next
      end if

      nullify(c%next)
      if (len_trim(start) == 19) then
         call read_time_string(start,c%j1,c%s1)
      end if
      c%start = start
      if (len_trim(stop) == 19) then
         call read_time_string(stop,c%j2,c%s2)
      end if
      c%stop = stop
      c%name = name
      c%action_type = action_type
      c%action = action
      c%threshold = threshold
      c%kstart = kstart
      c%kstop = kstop
      c%verbose = verbose
!      c%parray => model%get_data(model%get_bulk_variable_id(c%name))

!     First search in pelagic variables
      c%id = model%get_bulk_variable_id(c%name)
      if (fabm_is_variable_used(c%id)) then
         c%type_data = type_profile
         c%parray => model%get_data(c%id)
      end if

!     If variable was not found, search variables defined on horizontal slice of model domain (e.g., benthos)
      if (.not.fabm_is_variable_used(c%id)) then
         c%horizontal_id = model%get_horizontal_variable_id(c%name)
         if (fabm_is_variable_used(c%horizontal_id)) then
            if (lake) then
#if 0
               c%parray => model%get_data(c%horizontal_id)
#else
               found = .false.
               do i=1,size(model%bottom_state_variables)
                  if(trim(c%name) == trim(model%bottom_state_variables(i)%name)) found = .true.
                  if (found) exit
               end do
               if (found) then
                  c%parray => cc(1:,size(model%state_variables)+i)
                  if (c%verbose) then
                     LEVEL2 trim(c%name),size(model%state_variables),i 
!                     write(*,*) c%parray 
                  end if
                  c%type_data = type_profile
               end if
#endif
            else
               c%pscalar => model%get_data(c%horizontal_id)
               c%type_data = type_scalar
            end if
!            stop
         end if
      end if

#if 0
!        If variable still was not found, search scalar [non-spatial] variables.
         if (.not.(fabm_is_variable_used(c%id).or.fabm_is_variable_used(c%horizontal_id))) then
            c%scalar_id = fabm_get_scalar_variable_id(model,variables(i))
            c%type_data = type_scalar
         end if

!        If variable still was not found, test whether its name matches the name of a pelagic variable,
!        followed by an underscore, and the name of an stream. In that case, the input variable specifies the
!        time-varying concentration of the pelagic variable in the stream.
         if
         (.not.(fabm_is_variable_used(c%id).or.fabm_is_variable_used(c%horizontal_id).or.fabm_is_variable_used(c%scalar_id))) then
            curstream => first_stream
            do while (associated(curstream))
               vl = len_trim(variables(i))
               ifl = len_trim(curstream%name)
               if (variables(i)(vl-ifl+1:vl)==curstream%name) then
                  c%id = fabm_get_bulk_variable_id(model,variables(i)(:vl-ifl-1))
                  variabletype = type_scalar
                  if (fabm_is_variable_used(c%id)) c%stream => curstream
               end if
               curstream => curstream%next
            end do
         end if

#endif
!     Report an error if the variable was still not found.
!      if (.not.(fabm_is_variable_used(c%id).or.fabm_is_variable_used(c%horizontal_id).or.fabm_is_variable_used(c%scalar_id))) then
      if (.not.(fabm_is_variable_used(c%id).or.fabm_is_variable_used(c%horizontal_id))) then
         FATAL 'Variable '//trim(c%name)//', referenced in namelist manipulation &
               &in '//trim(fname)//', was not found in model.'
         stop 'gotm_fabm_manipulation:init_gotm_fabm_manipulation'
      end if

   end do
!  Close the namelist file
97 close(namlst)

98 LEVEL2 'done'

   return

99 FATAL 'Error reading namelist "manipulation" from '//trim(fname)
   stop 'gotm_fabm_manipulation:init_gotm_fabm_manipulation'

   end subroutine init_gotm_fabm_manipulation
!EOC

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: Do bio manipulation
!
! !INTERFACE:
   subroutine do_gotm_fabm_manipulations(Vc,dt)
!
! !DESCRIPTION:
!  loop over all manipulations
!  check action
!  check times
!  apply action
!
! !USES:
!
! !INPUT PARAMETERS:
   REALTYPE, intent(in)          :: Vc(:)
   REALTYPE, intent(in)          :: dt
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding
!
! !LOCAL VARIABLES:
   type (type_fabm_manipulation), pointer :: c
   REALTYPE :: sumV
   REALTYPE, allocatable :: weights(:)
!EOP
!-----------------------------------------------------------------------
!BOC
!  If FABM is not used, return immediately.
   if (.not.fabm_calc) return

   c => first_manipulation
   do while (associated(c))
      select case (c%action_type)
      case(1)
         if (abs(time_diff(c%j1,c%s1,julianday,secondsofday)) .lt. timestep) then
            if (c%verbose) then
               LEVEL2 'Manipulation: ',trim(c%start),' ',c%type_data
            end if
            select case(c%type_data)
            case(type_profile)
               c%parray(c%kstart:c%kstop) = c%action*c%parray(c%kstart:c%kstop)
            case(type_scalar)
               c%pscalar = c%action*c%pscalar
            end select
         end if
      case(2)
         if (in_time_interval(c%j1,c%s1,julianday,secondsofday,c%j2,c%s2)) then
            if (c%verbose) then
               LEVEL2 'In interval: ',trim(c%start),' - ',trim(c%stop),' ',c%type_data
            end if
            select case(c%type_data)
            case(type_profile)
               if (minval(c%parray(c%kstart:c%kstop)) .lt. c%threshold) then
                  sumV = sum(Vc(c%kstart:c%kstop))
                  c%parray(c%kstart:c%kstop) = c%parray(c%kstart:c%kstop)+c%action*dt/sumV
               end if
            case(type_scalar)
               c%pscalar = c%pscalar+c%action*dt
            end select
         end if
      end select
      c => c%next
   end do
   end subroutine do_gotm_fabm_manipulations
!EOC

!-----------------------------------------------------------------------

   end module gotm_fabm_manipulation

#endif

!-----------------------------------------------------------------------
! Copyright by the GOTM-team under the GNU Public License - www.gnu.org
!----------------------------------------------------------------------

