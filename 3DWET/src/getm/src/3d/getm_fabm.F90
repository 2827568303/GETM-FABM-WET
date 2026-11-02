#ifdef _FABM_
#include "cppdefs.h"
#ifndef _FABM_API_VERSION_
#include "fabm_version.h"
#endif
!-----------------------------------------------------------------------
!BOP
!
! !MODULE: getm_fabm()
!
! !INTERFACE:
   module getm_fabm
!
! !DESCRIPTION:
!
! !USES:
   use parameters, only: rho_0
   use domain, only: imin,imax,jmin,jmax,kmax
   use domain, only: ilg,ihg,jlg,jhg,ill,ihl,jll,jhl
   use domain, only: az,latc,lonc
   use domain, only: H
!KB   use get_field, only: get_2d_field,get_3d_field
   use variables_3d, only: uu,vv,ww,hun,hvn,ho,hn
   use variables_3d, only: fabm_pel,fabm_ben,fabm_diag,fabm_diag_hz
   use variables_3d, only: nuh,T,S,rho,a,g1,g2,taub,dt
   use advection_3d, only: print_adv_settings_3d,do_advection_3d
   use variables_2d, only: D
   use meteo, only: swr,u10,v10,evap,precip,tcc
   use time, only: month,yearday,secondsofday,timestr,julianday
   use halo_zones, only: update_3d_halo,wait_halo,D_TAG,H_TAG
   use exceptions
! JORN_FABM
#ifdef _NEW_GOTM_
#ifdef _GOTM_FABM_NML_
   use gotm_fabm, only: configure_gotm_fabm_from_nml
#else
   use gotm_fabm, only: configure_gotm_fabm
#endif
   use gotm_fabm, only: gotm_fabm_create_model
#endif
   use gotm_fabm, only: init_gotm_fabm,start_gotm_fabm,set_env_gotm_fabm,do_gotm_fabm
   use gotm_fabm, only: gotm_fabm_calc=>fabm_calc, model, cc_col=>cc, cc_diag_col=>cc_diag, cc_diag_hz_col=>cc_diag_hz, cc_transport, save_instant_diagnostics

#ifndef _OLD_FABM_
   use fabm_v0_compatibility, only: type_horizontal_variable_id, fabm_is_variable_used
   use fabm, only: status_start_done
#else
   use fabm, only: type_horizontal_variable_id, fabm_is_variable_used
#endif
   use fabm_types,only: output_instantaneous, output_none, output_time_integrated, &
      output_time_step_averaged, output_time_step_integrated, type_bulk_standard_variable
   use fabm_driver, only: host_save_diagnostics
!$ use omp_lib
   use fabm, only: fabm_link_scalar_data, fabm_get_scalar_variable_id, type_scalar_variable_id
   use fabm_standard_variables, only: standard_variables
   use fabm, only: fabm_get_bulk_diagnostic_data
   use fabm_types, only: type_expression
   use fabm_expressions, only: type_bulk_temporal_mean,type_horizontal_temporal_mean

   IMPLICIT NONE
   private
!
! !PUBLIC DATA MEMBERS:
   public fabm_pel, fabm_ben, fabm_diag, fabm_diag_hz
   public init_getm_fabm_fields
   public init_getm_fabm, do_getm_fabm, model, output_none
   public register_fabm_variables
   public define_temporal_memory, read_temporal_memory, write_temporal_memory
   integer, public :: fabm_init_method=0
   integer, allocatable :: diag_keep(:), diag_hz_keep(:)
   integer :: n_diag_keep=0, n_diag_hz_keep=0
   logical :: diag_keep_ready=.false.
   character(len=PATH_MAX)   :: fabm_init_file
   integer                   :: fabm_init_format, fabm_field_no
   logical, public :: fabm_calc
!
! !PRIVATE DATA MEMBERS:
   integer         :: fabm_adv_split=0
   integer         :: fabm_adv_hor=1
   integer         :: fabm_adv_ver=1
   REALTYPE        :: fabm_AH=-_ONE_
   type (type_horizontal_variable_id) :: id_bottom_depth_below_geoid,id_bottom_depth
   REALTYPE, allocatable :: bot_pel_conv_col(:)
#include "fabm_temporal_memory_types.h"

   type type_input_variable
      integer                              :: ncid  = -1
      integer                              :: varid = -1
      class (type_input_variable), pointer :: next => null()
   end type

   type,extends(type_input_variable) :: type_horizontal_input_variable
      REALTYPE, allocatable, dimension(:,:) :: data
      type (type_horizontal_variable_id)    :: id
   end type

   class (type_input_variable), pointer, save :: first_input_variable => null()

   integer         :: old_month=-1
!
! !REVISION HISTORY:
!  Original author(s): Hans Burchard & Karsten Bolding
!
!EOP
!-----------------------------------------------------------------------

interface
   subroutine inquire_file(fn,ncid,varids,varnames)
      character(len=*), intent(in)        :: fn
      integer, intent(inout)              :: ncid
      integer, allocatable, intent(inout) :: varids(:)
      character(len=50), allocatable, intent(out) :: varnames(:)
   end subroutine inquire_file

!KB - only until a proper input_manager has been made
   subroutine get_2d_field_ncdf_by_id(ncid,varid,il,ih,jl,jh,n,field)
      integer, intent(in)                 :: ncid,varid
      integer, intent(in)                 :: il,ih,jl,jh,n
      REALTYPE, intent(out)               :: field(:,:)
   end subroutine get_2d_field_ncdf_by_id

! Temporary interface (should be read from module):
   subroutine get_2d_field(fn,varname,il,ih,jl,jh,break_on_missing,f)
      character(len=*),intent(in)   :: fn,varname
      integer, intent(in)           :: il,ih,jl,jh
      logical, intent(in)           :: break_on_missing
      REALTYPE, intent(out)         :: f(:,:)
   end subroutine get_2d_field
end interface

   contains
#include "fabm_temporal_memory.h"
#include "fabm_temporal_restart.h"

   subroutine initialize_wet_benthic_mirrors()
      integer :: i,j,x,y,element,instance
      character(len=32), parameter :: instances(9) = &
         [character(len=32) :: 'macrophytes','zoobenthos','bivalves', &
                               'POM','DOM','humus','cyanobacteria','diatoms','greens']
      character(len=1), parameter :: elements(4) = ['D','N','P','C']
      character(len=48) :: pel_name,bottom_name

      do instance=1,size(instances)
         do element=1,size(elements)
            if (instance<=3) then
               pel_name=trim(instances(instance))//'_s'//elements(element)//'_PV'
               bottom_name=trim(instances(instance))//'_s'//elements(element)
            else
               pel_name=trim(instances(instance))//'_s'//elements(element)//'S_PV'
               bottom_name=trim(instances(instance))//'_s'//elements(element)//'S'
            end if
            do i=1,size(model%state_variables)
               if (trim(model%state_variables(i)%name)/=trim(pel_name)) cycle
               do j=1,size(model%bottom_state_variables)
                  if (trim(model%bottom_state_variables(j)%name)/=trim(bottom_name)) cycle
                  do y=jmin,jmax
                     do x=imin,imax
                        if (az(x,y)>=1) fabm_pel(x,y,1,i)=fabm_ben(x,y,j)
                     end do
                  end do
                  exit
               end do
               exit
            end do
         end do
      end do
   end subroutine initialize_wet_benthic_mirrors

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: init_getm_fabm
!
! !INTERFACE:
   subroutine init_getm_fabm(nml_file,hotstart)
!
! !DESCRIPTION:
!  Reads the namelist and makes calls to the init functions of the
!  various model components.
!
! !USES:
   use advection, only: J7
#ifndef _GOTM_FABM_NML_
   use yaml_settings
#endif
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   character(len=*), intent(in)   :: nml_file
   logical,intent(in)             :: hotstart
!
! !REVISION HISTORY:
!  See the log for the module
!
!  !LOCAL VARIABLES
   integer, parameter        :: unit_fabm=63
   integer                   :: rc
   integer                   :: i,j,n
   character(len=PATH_MAX)   :: fabm_surface_flux_file=""
   integer                   :: ncid
   integer, allocatable      :: varids(:)
   character(len=50), allocatable :: varnames(:)
#ifndef _GOTM_FABM_NML_
   type (type_settings), pointer, save :: settings_gotm_fabm => null()
   class (type_settings), pointer      :: branch
#endif

   namelist /getm_fabm_nml/ fabm_init_method, &
                           fabm_init_file,fabm_init_format,fabm_field_no, &
                           fabm_surface_flux_file, &
                           fabm_adv_split,fabm_adv_hor,fabm_adv_ver,fabm_AH
!EOP
!-------------------------------------------------------------------------
!BOC
   LEVEL2 'init_getm_fabm()'

!  Initialize FABM.
#ifdef _NEW_GOTM_
#ifdef _GOTM_FABM_NML_
   call configure_gotm_fabm_from_nml(NAMLST2,'gotm_fabm.nml')
#else
   inquire(file='gotm_fabm.yaml',exist=fabm_calc)
   if (.not. fabm_calc) then
      LEVEL0 LINE
      LEVEL0 'WARNING: gotm_fabm.yaml not found.'
      LEVEL0 'WARNING: will continue with fabm_calc=False.'
      LEVEL0 LINE
      return
   end if
   allocate(settings_gotm_fabm)
   call settings_gotm_fabm%load('gotm_fabm.yaml', unit_fabm)
   branch => settings_gotm_fabm%get_child('fabm', 'Framework for Aquatic Biogeochemical Models')
   call configure_gotm_fabm(branch)
#endif
   call gotm_fabm_create_model(NAMLST2, kmax, .true.)
   ! GETM supplies absolute model time in seconds to do_gotm_fabm; the
   ! optional FABM seconds_per_time_unit therefore must be 1, not the
   ! physical 3-D timestep (dt), which can span multiple seconds.
   call init_gotm_fabm(kmax, 1.0d0)
#else
   call init_gotm_fabm(kmax,NAMLST2,'gotm_fabm.nml')
#endif

!  Store fabm_calc and model for use by GETM
   fabm_calc = gotm_fabm_calc

   if (fabm_calc) then

      id_bottom_depth_below_geoid = model%get_horizontal_variable_id(standard_variables%bottom_depth_below_geoid)
      id_bottom_depth = model%get_horizontal_variable_id(standard_variables%bottom_depth)

!     Allocate and link bot_pel_conv (benthic-pelagic conversion factor)
!     Needed by WET/PCLake model for _PV (pelagic mirror) variables
      allocate(bot_pel_conv_col(kmax))
      bot_pel_conv_col = _ONE_
      call model%link_bulk_data(type_bulk_standard_variable(name='bot_pel_conv',units='-'), &
                               bot_pel_conv_col(1:kmax))

!     Temporary: make sure diagnostic variables store the last value,
!     not their time integral. This will be redundant when time-integrating/averaging
!     is moved from FABM to the physical host.
      do n=1,size(model%diagnostic_variables)
         if (model%diagnostic_variables(n)%output/=output_none) &
            model%diagnostic_variables(n)%output = output_instantaneous
      end do
      do n=1,size(model%horizontal_diagnostic_variables)
         if (model%horizontal_diagnostic_variables(n)%output/=output_none) &
            model%horizontal_diagnostic_variables(n)%output = output_instantaneous
      end do

!     Allocate memory for pelagic state variables.
      allocate(fabm_pel(I3DFIELD,size(model%state_variables)),stat=rc)
      if (rc /= 0) stop 'init_getm_fabm: Error allocating memory (fabm_pel)'
      fabm_pel = _ZERO_

!     Allocate memory for benthic state variables.
      allocate(fabm_ben(I2DFIELD,size(model%bottom_state_variables)),stat=rc)
      if (rc /= 0) stop 'init_getm_fabm: Error allocating memory (fabm_ben)'
      fabm_ben = _ZERO_

!     Allocate memory for 3D diagnostic variables.
      allocate(fabm_diag(I3DFIELD,size(model%diagnostic_variables)),stat=rc)
      if (rc /= 0) stop 'init_getm_fabm: Error allocating memory (fabm_diag)'
      fabm_diag = _ZERO_

!     Allocate memory for 2D [horizontal-only] diagnostic variables.
      allocate(fabm_diag_hz(I2DFIELD,size(model%horizontal_diagnostic_variables)),stat=rc)
      if (rc /= 0) stop 'init_getm_fabm: Error allocating memory (fabm_diag_hz)'
      fabm_diag_hz = _ZERO_

!     Read settings specific to GETM-FABM interaction.
      open(NAMLST2,status='unknown',file=trim(nml_file))
      read(NAMLST2,NML=getm_fabm_nml)
      close(NAMLST2)

!     Show settings specific to GETM-FABM interaction.
      LEVEL2 'Advection of FABM variables'
      if (fabm_adv_hor .eq. J7) stop 'init_getm_fabm: J7 not implemented yet'
      call print_adv_settings_3d(fabm_adv_split,fabm_adv_hor,fabm_adv_ver,fabm_AH)

!     Here we need to open the NetCDF file with FABM forcing data (if it exists)
!     and loop over all its variables.
!     For now 2D only, so make sure each NetCDF variable is 2D.
!     For each variable, register_horizontal_input_variable should be called (see below).
!     That looks up the FABM variable and also allocates the 2D field that will hold the input data.

      LEVEL2 'FABM input and forcing ...'
      if (len_trim(fabm_surface_flux_file) .ne. 0) then
         call inquire_file(fabm_surface_flux_file,ncid,varids,varnames)
         do n=1,size(varids)
            if ( varids(n) .ne. -1) then
               call register_horizontal_input_variable(trim(varnames(n))//'_flux',ncid,varids(n),rc)
               if (rc .eq. 0) then
                  LEVEL4 'remember to add external_surface_flux model to fabm.yaml'
               end if
            end if
         end do
      else
         LEVEL3 'no file with FABM surface fluxes specified in getm_fabm.inp'
      end if

!     Initialize biogeochemical state variables.
      if (.not. hotstart) then
         call init_getm_fabm_fields(hotstart)
      end if

   end if

   end subroutine init_getm_fabm
!EOC
!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: init_getm_fabm_fields - initialisation of the fabm fields
! \label{sec-init-getm-fabm-fields}
!
! !INTERFACE:
   subroutine init_getm_fabm_fields(hotstart)
!
! !DESCRIPTION:
! Initialisation of the getm-fabm fields as specified by fabm\_init\_method
! and exchange of the HALO zones
!
! !USES:
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   logical, intent(in) :: hotstart
!
! !INPUT/OUTPUT PARAMETERS:
!
! !OUTPUT PARAMETERS:
!
! !LOCAL VARIABLES:
   integer                   :: i,j,n
!EOP
!-------------------------------------------------------------------------
!BOC

   if (hotstart) then
      if (fabm_init_method .ne. 0) then
         LEVEL3 'WARNING: fabm variables from hotstart file will be overwritten!'
      end if
   else
      if (fabm_init_method .eq. 0) then
         call getm_error("init_getm_fabm_fields()", "fabm variables not initialized")
      end if
   end if

      select case (fabm_init_method)
         case(0)
            LEVEL3 'getting initial biogeochemical fields from hotstart file'
         case(1,2)
            LEVEL3 "initial biogeochemical fields from namelists - fabm.yaml"
            do j=jmin,jmax
               do i=imin,imax
                  if (az(i,j) .ge. 1 ) then
                     do n=1,size(model%state_variables)
                        fabm_pel(i,j,:,n) = cc_col(:,n)
                     end do
                     do n=1,size(model%bottom_state_variables)
                        fabm_ben(i,j,  n) = cc_col(1,size(model%state_variables)+n)
                     end do
                  end if
               end do
            end do
            if (fabm_init_method .eq. 2) then
               LEVEL3 'now checking initial fields from ',trim(fabm_init_file)
               do n=1,size(model%state_variables)
                  LEVEL4 'inquiring: ',trim(model%state_variables(n)%name)
                  call get_3d_field(fabm_init_file, &
                                 trim(model%state_variables(n)%name), &
                                 fabm_field_no,.false., &
                                 fabm_pel(:,:,:,n))
               end do
               do n=1,size(model%bottom_state_variables)
                  LEVEL4 'inquiring: ',trim(model%bottom_state_variables(n)%name)
                  call get_2d_field(fabm_init_file, &
                                 trim(model%bottom_state_variables(n)%name), &
                                 ilg,ihg,jlg,jhg,.false., &
                                 fabm_ben(ill:ihl,jll:jhl,n))
               end do
            end if
            call initialize_wet_benthic_mirrors()
         case default
            FATAL 'Not valid fabm_init_method specified'
            stop 'init_getm_fabm_fields()'
      end select

!     Update halos with biogeochemical variable values (distribute initial values).
      do n=1,size(model%state_variables)
         fabm_pel(:,:,0,n) = model%state_variables(n)%missing_value
         forall(i=imin:imax,j=jmin:jmax, az(i,j).eq.0) &
            fabm_pel(i,j,:,n) = model%state_variables(n)%missing_value
         call update_3d_halo(fabm_pel(:,:,:,n),fabm_pel(:,:,:,n),az, &
                             imin,jmin,imax,jmax,kmax,D_TAG)
         call wait_halo(D_TAG)
      end do
      do n=1,size(model%bottom_state_variables)
         where ( az.eq.0 ) fabm_ben(:,:,n) = model%bottom_state_variables(n)%missing_value
      end do
      do n=1,size(model%diagnostic_variables)
         fabm_diag(:,:,0,n) = model%diagnostic_variables(n)%missing_value
         forall(i=imin:imax,j=jmin:jmax, az(i,j).eq.0) &
            fabm_diag(i,j,:,n) = model%diagnostic_variables(n)%missing_value
      end do
      do n=1,size(model%horizontal_diagnostic_variables)
         where ( az.eq.0 ) fabm_diag_hz(:,:,n) = model%horizontal_diagnostic_variables(n)%missing_value
      end do

#ifdef DEBUG
   write(debug,*) 'Leaving init_getm_fabm_fields()'
   write(debug,*)
#endif
   return
   end subroutine init_getm_fabm_fields
!EOC

#ifdef _FABM_
!-----------------------------------------------------------------------
!BOP
!
! !ROUTINE: register_fabm_variables() - register FABM variables.
!
! !INTERFACE:
   subroutine register_fabm_variables(fm)
!
! !DESCRIPTION:
!
! !USES:
   use field_manager
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   type (type_field_manager) :: fm
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding & Jorn Bruggeman
!
! !LOCAL VARIABLES:
  integer :: i,output_level
  logical :: in_output
!EOP
!-----------------------------------------------------------------------
!BOC
   if (.not. fabm_calc) return
   LEVEL2 'register_fabm_variables()'

   do i=1,size(model%state_variables)
      output_level = output_level_default
      if (model%state_variables(i)%output==output_none) output_level = output_level_debug
      call fm%register(model%state_variables(i)%name, model%state_variables(i)%units, &
         model%state_variables(i)%long_name, minimum=model%state_variables(i)%minimum, maximum=model%state_variables(i)%maximum, &
         fill_value=model%state_variables(i)%missing_value, dimensions=(/id_dim_z/), data3d=fabm_pel(_3D_W_,i), category='fabm'//model%state_variables(i)%target%owner%get_path(), output_level=output_level)
   end do
   do i=1,size(model%bottom_state_variables)
      output_level = output_level_default
      if (model%bottom_state_variables(i)%output==output_none) output_level = output_level_debug
      call fm%register(model%bottom_state_variables(i)%name, model%bottom_state_variables(i)%units, &
         model%bottom_state_variables(i)%long_name, minimum=model%bottom_state_variables(i)%minimum, &
         maximum=model%bottom_state_variables(i)%maximum, fill_value=model%bottom_state_variables(i)%missing_value, &
         data2d=fabm_ben(_2D_W_,i), category='fabm'//model%bottom_state_variables(i)%target%owner%get_path(), output_level=output_level)
   end do
   do i=1,size(model%diagnostic_variables)
      output_level = output_level_default
      if (model%diagnostic_variables(i)%output==output_none) output_level = output_level_debug
      call fm%register(model%diagnostic_variables(i)%name, model%diagnostic_variables(i)%units, &
         model%diagnostic_variables(i)%long_name, minimum=model%diagnostic_variables(i)%minimum, maximum=model%diagnostic_variables(i)%maximum, &
         fill_value=model%diagnostic_variables(i)%missing_value, dimensions=(/id_dim_z/), data3d=fabm_diag(_3D_W_,i), category='fabm'//model%diagnostic_variables(i)%target%owner%get_path(), output_level=output_level, used=in_output)
      if (in_output) model%diagnostic_variables(i)%save = .true.
   end do
   do i=1,size(model%horizontal_diagnostic_variables)
      output_level = output_level_default
      if (model%horizontal_diagnostic_variables(i)%output==output_none) output_level = output_level_debug
      call fm%register(model%horizontal_diagnostic_variables(i)%name, model%horizontal_diagnostic_variables(i)%units, &
         model%horizontal_diagnostic_variables(i)%long_name, minimum=model%horizontal_diagnostic_variables(i)%minimum, maximum=model%horizontal_diagnostic_variables(i)%maximum, &
         fill_value=model%horizontal_diagnostic_variables(i)%missing_value, data2d=fabm_diag_hz(_2D_W_,i), category='fabm'//model%horizontal_diagnostic_variables(i)%target%owner%get_path(), output_level=output_level, used=in_output)
      if (in_output) model%horizontal_diagnostic_variables(i)%save = .true.
   end do

   return
   end subroutine register_fabm_variables
!EOC
#endif

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: register_horizontal_input_variable
!
! !INTERFACE:
   subroutine register_horizontal_input_variable(name,ncid,varid,rc)
!
! !DESCRIPTION:
!  Registers FABM horizontal fluxes (surface)
!
! !USES:
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   character(len=*),intent(in) :: name
   integer,         intent(in) :: ncid,varid
!
! !OUTPUT PARAMETERS:
   integer,         intent(out) :: rc
!
! !REVISION HISTORY:
!  See the log for the module
!
!  !LOCAL VARIABLES
      class (type_horizontal_input_variable), pointer :: variable
!EOP
!-------------------------------------------------------------------------
!BOC
!  Create the input variable and set associated data (FABM id,
!  NetCDF id, 2D data field).
   allocate(variable)
   variable%id = model%get_horizontal_variable_id(name)
   if (.not.fabm_is_variable_used(variable%id)) then
      LEVEL4 'register: no - ',trim(name)//' is not used by this FABM configuration.'
!      stop 'register_horizontal_input_variable: unrecognized variable name'
      deallocate(variable)
      rc = 1
   else
      LEVEL4 'register: yes - ',trim(name)
      variable%ncid  = ncid
      variable%varid = varid
      allocate(variable%data(I2DFIELD))
      variable%data = _ZERO_

      ! Prepend to the list of inout variables.
      variable%next => first_input_variable
      first_input_variable => variable
      rc = 0
   end if
   return
   end subroutine register_horizontal_input_variable
!EOC

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE:  do_getm_fabm()
!
! !INTERFACE:
   subroutine do_getm_fabm(dt,publish_diagnostics)
!
! !DESCRIPTION:
!
! !USES:
   use getm_timers, only: tic, toc, TIM_GETM_FABM, TIM_ADVECTFABM
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   REALTYPE, intent(in)                :: dt
   logical, intent(in), optional       :: publish_diagnostics
!
! !REVISION HISTORY:
!  See the log for the module
!
! !LOCAL VARIABLES:
   integer         :: n
   integer         :: i,j,k,kk
   integer         :: nthreads
   logical         :: publish
   REALTYPE        :: bioshade(1:kmax)
   REALTYPE        :: wind_speed,I_0,taub_nonnorm,cloud
   REALTYPE        :: z(1:kmax)
   class (type_input_variable), pointer :: current_input_variable
   integer         :: ncid,varid
   logical         :: some_var_ok=.false.
!EOP
!-----------------------------------------------------------------------
!BOC

   call tic(TIM_GETM_FABM)

   publish = .true.
   if (present(publish_diagnostics)) publish = publish_diagnostics
   call ensure_diag_keep()
   ! Instantaneous diagnostics are recomputed from the state. The 3D
   ! field is only read by output, so scatter them on output steps.
   ! Time-integrated diagnostics stay in the 3D field every step.
   save_instant_diagnostics = publish
   ! Pelagic carbonate equilibrium is diagnostic-only. Surface exchange
   ! still solves it. See wet/inorganic_carbon.F90.
   host_save_diagnostics = publish

!  First update all input fields
   if (month .ne. old_month) then
      old_month = month
      current_input_variable => first_input_variable
      do while (associated(current_input_variable))
         select type (current_input_variable)
            class is (type_horizontal_input_variable)
               ncid  = current_input_variable%ncid
               varid = current_input_variable%varid
               if (ncid .gt. 0 .and. varid .gt. 0) then
                  some_var_ok = .true.
                  call get_2d_field_ncdf_by_id(ncid,varid,ilg,ihg,jlg,jhg,month, &
                                               current_input_variable%data(ill:ihl,jll:jhl))
               end if
         end select
         current_input_variable => current_input_variable%next
      end do
      if (some_var_ok) then
         LEVEL3 timestr,': reading FABM surface fluxes ...',month
      end if
   end if

!  First we do all the vertical processes
#ifdef SLICE_MODEL
   do j=2,2
#else
   do j=jmin,jmax
#endif
      do i=imin,imax
         if (az(i,j) .ge. 1 ) then

!           Calculate wind speed from wind vector components.
            if (allocated(u10) .and. allocated(v10)) then
               wind_speed = sqrt(u10(i,j)*u10(i,j)+v10(i,j)*v10(i,j))
            else
               wind_speed = _ZERO_
            end if

!           Get surface short-wave radiation.
            if (allocated(swr)) then
               I_0 = swr(i,j)
            else
               I_0 = _ZERO_
            end if

            if (allocated(tcc)) then
               cloud = tcc(i,j)
            else
               cloud = _ZERO_
            end if

!           Calculate depths of cell centers from layer heights.
            z(kmax) = -_HALF_*hn(i,j,kmax)
            do k=kmax-1,1,-1
               z(k) = z(k+1) - _HALF_*(hn(i,j,k+1)+hn(i,j,k))
            end do

!           Calculate actual bottom stress from normalized bottom stress (taub/rho_0)
            taub_nonnorm = taub(i,j)*rho_0

!           Copy current values of biogeochemical variables from full 3D field to columns.
            do n=1,size(model%state_variables)
               cc_col(:,n) = fabm_pel(i,j,:,n)
            end do
            do n=1,size(model%bottom_state_variables)
               cc_col(1,size(model%state_variables)+n) = fabm_ben(i,j,n)
            end do
            if (publish) then
               do n=1,size(model%diagnostic_variables)
                  cc_diag_col(:,n) = fabm_diag(i,j,1:,n)
               end do
               do n=1,size(model%horizontal_diagnostic_variables)
                  cc_diag_hz_col(n) = fabm_diag_hz(i,j,n)
               end do
            else
               do kk=1,n_diag_keep
                  n = diag_keep(kk)
                  cc_diag_col(:,n) = fabm_diag(i,j,1:,n)
               end do
               do kk=1,n_diag_hz_keep
                  n = diag_hz_keep(kk)
                  cc_diag_hz_col(n) = fabm_diag_hz(i,j,n)
               end do
            end if

!           Transfer pointers to physical environment variables to FABM.
            call set_env_gotm_fabm(latc(i,j),lonc(i,j),dt,0,0,T(i,j,1:),S(i,j,1:), &
                                   rho(i,j,1:),nuh(i,j,0:),hn(i,j,0:),ww(i,j,0:), &
                                   bioshade,I_0,cloud,taub_nonnorm,wind_speed,precip(i,j),evap(i,j), &
                                   z,A(i,j),g1(i,j),g2(i,j),yearday,secondsofday)
            call model%link_horizontal_data(id_bottom_depth_below_geoid,H(i,j))
            call model%link_horizontal_data(id_bottom_depth,D(i,j))

!           Update bot_pel_conv for this column (1/dz per layer)
            do kk=1,kmax
               bot_pel_conv_col(kk) = _ONE_ / max(hn(i,j,kk), 1e-6)
            end do

!           Transfer prescribed input variables
            current_input_variable => first_input_variable
            do while (associated(current_input_variable))
               select type (current_input_variable)
               class is (type_horizontal_input_variable)
                  call model%link_horizontal_data(current_input_variable%id,current_input_variable%data(i,j))
               end select
               current_input_variable => current_input_variable%next
            end do

#ifndef _OLD_FABM_
            call restore_temporal_memory(i,j)
            if (model%status < status_start_done) call start_gotm_fabm(kmax)
#else
            call restore_temporal_memory(i,j)
            if (model%state < 3) call start_gotm_fabm(kmax)
#endif

!           Update biogeochemical variable values.
!           Pass elapsed simulation time (seconds) so FABM temporal_mean
!           (e.g. WET phytoplankton 24h-averaged PAR) can advance its window.
            call do_gotm_fabm(kmax, real(julianday,kind(_ONE_))*86400+real(secondsofday,kind(_ONE_)))
            call store_temporal_memory(i,j)

!           Copy updated column values of biogeochemical variables to full 3D field.
            do n=1,size(model%state_variables)
               fabm_pel(i,j,:,n) = cc_col(:,n)
            end do
            do n=1,size(model%bottom_state_variables)
               fabm_ben(i,j,n) = cc_col(1,size(model%state_variables)+n)
            end do
            if (publish) then
               do n=1,size(model%diagnostic_variables)
                  fabm_diag(i,j,1:,n) = cc_diag_col(:,n)
               end do
               do n=1,size(model%horizontal_diagnostic_variables)
                  fabm_diag_hz(i,j,n) = cc_diag_hz_col(n)
               end do
            else
               do kk=1,n_diag_keep
                  n = diag_keep(kk)
                  fabm_diag(i,j,1:,n) = cc_diag_col(:,n)
               end do
               do kk=1,n_diag_hz_keep
                  n = diag_hz_keep(kk)
                  fabm_diag_hz(i,j,n) = cc_diag_hz_col(n)
               end do
            end if

         end if
      end do
   end do

#ifdef SLICE_MODEL
   do i=imin,imax
      fabm_pel(i,3,:,:)=fabm_pel(i,2,:,:)
      fabm_ben(i,3,:)  =fabm_ben(i,2,:)
   end do
#endif

!  Advect pelagic biogeochemical variables. Each tracer is independent.
!  The team size is omp_get_max_threads(), which follows OMP_NUM_THREADS,
!  so the run-control core count applies here. Nesting stays off, so the
!  inner advection regions use one thread. Not used for MPI: halo exchange
!  shares one tag.
   call tic(TIM_ADVECTFABM)
   nthreads = 1
!$ nthreads = omp_get_max_threads()
   if (nthreads < 1) nthreads = 1
#ifndef GETM_PARALLEL
!$omp parallel do if(nthreads>1) num_threads(nthreads) default(shared) private(n) schedule(static)
#endif
   do n=1,size(model%state_variables)

      call update_3d_halo(fabm_pel(:,:,:,n),fabm_pel(:,:,:,n),az, &
                          imin,jmin,imax,jmax,kmax,D_TAG)
      call wait_halo(D_TAG)

      if (cc_transport(n)) call do_advection_3d(dt,fabm_pel(:,:,:,n),uu,vv,ww,hun,hvn,ho,hn,            &
                                                fabm_adv_split,fabm_adv_hor,fabm_adv_ver,fabm_AH,H_TAG)

   end do
#ifndef GETM_PARALLEL
!$omp end parallel do
#endif
   call toc(TIM_ADVECTFABM)

   call toc(TIM_GETM_FABM)

   end subroutine do_getm_fabm
!EOC

!-----------------------------------------------------------------------
!BOP
!
! !IROUTINE: ensure_diag_keep
!
! !INTERFACE:
   subroutine ensure_diag_keep()
!
! !DESCRIPTION:
!  Index diagnostics whose host copy must be kept every bio step.
!  Instantaneous diagnostics are overwritten from the current state, so
!  the strided 3D gather is only needed on steps that write output.
!
! !LOCAL VARIABLES:
   integer :: n, nkeep
!EOP
!-----------------------------------------------------------------------
!BOC
   if (diag_keep_ready) return

   nkeep = 0
   do n=1,size(model%diagnostic_variables)
      select case (model%diagnostic_variables(n)%output)
      case (output_time_integrated, output_time_step_averaged, output_time_step_integrated)
         nkeep = nkeep + 1
      end select
   end do
   allocate(diag_keep(max(nkeep,1)))
   n_diag_keep = 0
   do n=1,size(model%diagnostic_variables)
      select case (model%diagnostic_variables(n)%output)
      case (output_time_integrated, output_time_step_averaged, output_time_step_integrated)
         n_diag_keep = n_diag_keep + 1
         diag_keep(n_diag_keep) = n
      end select
   end do

   nkeep = 0
   do n=1,size(model%horizontal_diagnostic_variables)
      select case (model%horizontal_diagnostic_variables(n)%output)
      case (output_time_integrated, output_time_step_averaged, output_time_step_integrated)
         nkeep = nkeep + 1
      end select
   end do
   allocate(diag_hz_keep(max(nkeep,1)))
   n_diag_hz_keep = 0
   do n=1,size(model%horizontal_diagnostic_variables)
      select case (model%horizontal_diagnostic_variables(n)%output)
      case (output_time_integrated, output_time_step_averaged, output_time_step_integrated)
         n_diag_hz_keep = n_diag_hz_keep + 1
         diag_hz_keep(n_diag_hz_keep) = n
      end select
   end do

   diag_keep_ready = .true.
   LEVEL2 'FABM host diagnostics kept every step:', n_diag_keep, 'bulk,', n_diag_hz_keep, 'horizontal'
   LEVEL2 'Instantaneous FABM diagnostics are written to the 3D field only on output steps.'

   end subroutine ensure_diag_keep
!EOC

!-----------------------------------------------------------------------

   end module getm_fabm
#endif

!-----------------------------------------------------------------------
! Copyright (C) 2007 - Karsten Bolding and Hans Burchard               !
!-----------------------------------------------------------------------
