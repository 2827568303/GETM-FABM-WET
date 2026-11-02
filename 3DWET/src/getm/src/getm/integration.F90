#include "cppdefs.h"
!-----------------------------------------------------------------------
!BOP
!
! !MODULE:  integration - Initialise the time and do the time loop
!
! !INTERFACE:
   module integration
!
! !DESCRIPTION:
!
! !USES:
   IMPLICIT NONE
!
! !PUBLIC DATA MEMBERS:
   integer                             :: MinN=1,MaxN=-1
!
! !REVISION HISTORY:
!  Original author(s): Karsten Bolding & Hans Burchard
!
!EOP
!-----------------------------------------------------------------------

   contains

!-----------------------------------------------------------------------
!BOP
!
! !ROUTINE: time_loop - the main loop of getm
!
! !INTERFACE:
   subroutine time_loop(runtype)
!
! !DESCRIPTION:
!  A wrapper that calls meteo\_forcing, integrate\_2d, integrate\_3d,
!  do\_getm\_bio and output
!  within a time loop.
!
! !USES:
   use time,     only: update_time,timestep
   use time,     only: julianday,secondsofday,microseconds
   use domain,   only: kmax
   use meteo,    only: do_meteo,tausx,tausy,airp,swr,albedo
   use meteo,    only: fwf_method,evap,precip
   use m2d,      only: integrate_2d
   use variables_2d, only: fwf,fwf_int
#ifndef NO_3D
   use m3d,      only: integrate_3d,M
#ifndef NO_BAROCLINIC
   use variables_3d, only: T
#endif
   use rivers,   only: do_rivers
#ifdef _FABM_
   use getm_fabm, only: fabm_calc,do_getm_fabm
#endif
#ifdef GETM_BIO
   use bio, only: bio_calc
   use getm_bio, only: do_getm_bio
#endif
#endif
#ifdef SPM
   use suspended_matter, only: spm_calc,do_spm
#endif
   use input,    only: do_input
   use output_processing, only: do_output_processing
   use output,   only: do_output
#ifdef TEST_NESTING
   use nesting,   only: nesting_file
#endif
   use output_manager
   use getm_timers, only: tic, toc, TIM_FLEX_OUTPUT, TIM_OUTPUT_PROC
   IMPLICIT NONE
!
! !INPUT PARAMETERS:
   integer, intent(in)                 :: runtype
!
! !REVISION HISTORY:
!
! !LOCAL VARIABLES
   logical                   :: do_3d
   integer                   :: n
   integer                   :: progress=100
   character(8)              :: d_
   character(10)             :: t_
!EOP
!-----------------------------------------------------------------------
!BOC
#ifdef DEBUG
   integer, save :: Ncall = 0
   Ncall = Ncall+1
   write(debug,*) 'time_loop() # ',Ncall
#endif

   STDERR LINE
   LEVEL1 'integrating....'
   STDERR LINE

   do n=MinN,MaxN

      if (progress .gt. 0 .and. mod(n,progress) .eq. 0) then
         call date_and_time(date=d_,time=t_)
         LEVEL1 t_(1:2),':',t_(3:4),':',t_(5:10),' n=',n
      end if

#ifndef NO_3D
      do_3d = (runtype .ge. 2 .and. mod(n,M) .eq. 0)
#else
      do_3d = .false.
#endif
      call do_input(n)
      if(runtype .le. 2) then
         call do_meteo(n)
#ifndef NO_3D
#ifndef NO_BAROCLINIC
      else
         call do_meteo(n,T(:,:,kmax))
         swr = swr*(_ONE_-albedo)
#endif
#endif
      end if

      if (fwf_method .ge. 1) then
         fwf = evap+precip
#ifndef NO_3D
         fwf_int = fwf_int+timestep*fwf
#endif
      end if

#ifndef NO_BAROTROPIC
      call integrate_2d(runtype,n,tausx,tausy,airp)
#endif
#ifndef NO_3D
      call do_rivers(do_3d)
      if (do_3d) then
         call integrate_3d(runtype,n)
#ifdef SPM
         if (spm_calc) call do_spm()
#endif
#ifdef _FABM_
         if (fabm_calc) call do_getm_fabm(M*timestep)
#endif
#ifdef GETM_BIO
         if (bio_calc) call do_getm_bio(M*timestep)
#endif
#ifndef NO_3D
         if (fwf_method .ge. 1) then
            fwf_int = _ZERO_
         end if
#endif
      end if
#endif

#ifdef TEST_NESTING
      if (mod(n,80) .eq. 0) then
         call nesting_file(WRITING)
      end if
#endif

      call update_time(n)

      call tic(TIM_FLEX_OUTPUT)
      call output_manager_prepare_save(julianday, secondsofday, microseconds, n)
      call toc(TIM_FLEX_OUTPUT)
      call tic(TIM_OUTPUT_PROC)
      call do_output_processing()
      call toc(TIM_OUTPUT_PROC)
      call tic(TIM_FLEX_OUTPUT)
      call output_manager_save(julianday, secondsofday, microseconds, n)
      call toc(TIM_FLEX_OUTPUT)
      call do_output(runtype,n,timestep)
#ifdef DIAGNOSE
      call diagnose(n,MaxN,runtype)
#endif
#ifdef GETM_RUNTIME_PHYSICS_DIAGNOSTICS
      if (mod(n,progress) .eq. 0 .or. n .eq. MinN .or. n .eq. MaxN) then
#ifdef GETM_PARALLEL
         call emit_getm_physics_diagnostic_mpi(n,runtype,do_3d)
#else
         call emit_getm_physics_diagnostic(n,runtype,do_3d)
#endif
      end if
#endif
   end do


#ifdef DEBUG
   write(debug,*) 'Leaving time_loop()'
   write(debug,*)
#endif
   return
   end subroutine time_loop
!EOC

#ifdef GETM_RUNTIME_PHYSICS_DIAGNOSTICS
   subroutine physics_velocity_suffix(velocity_status,reason_code,layer_indices,velocity_values,suffix)
   IMPLICIT NONE
   integer, intent(in) :: velocity_status,reason_code,layer_indices(2)
   real(kind=8), intent(in) :: velocity_values(6)
   character(len=*), intent(out) :: suffix
   character(len=40) :: reason

   if (velocity_status .eq. 1) then
      write(suffix,'(1X,A,1X,A,I0,1X,A,I0,1X,A,ES0.8E3,1X,A,ES0.8E3,1X,A,ES0.8E3, &
                     1X,A,ES0.8E3,1X,A,ES0.8E3,1X,A,ES0.8E3)') &
         'velocity_status=available','surface_k=',layer_indices(1),'bottom_k=',layer_indices(2), &
         'u_surface_grid_m_s=',velocity_values(1),'v_surface_grid_m_s=',velocity_values(2), &
         'speed_surface_m_s=',velocity_values(3),'u_bottom_grid_m_s=',velocity_values(4), &
         'v_bottom_grid_m_s=',velocity_values(5),'speed_bottom_m_s=',velocity_values(6)
   else
      select case (reason_code)
      case (1)
         reason = 'no_3d_runtime'
      case (2)
         reason = 'not_3d_update_step'
      case (3)
         reason = 'no_valid_3d_layer'
      case (5)
         reason = 'mpi_comm_mode_unverified'
      case default
         reason = 'invalid_wet_velocity_face'
      end select
      write(suffix,'(1X,A,1X,A,A)') &
         'velocity_status=unavailable','reason=',trim(reason)
   end if
   end subroutine physics_velocity_suffix

#ifndef NO_3D
   subroutine sample_getm_tpoint_velocity(i,j,k,u,v,valid)
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use domain, only: au,av,kmax
   use variables_3d, only: uu,vv,hun,hvn
   IMPLICIT NONE
   integer, intent(in) :: i,j,k
   REALTYPE, intent(out) :: u,v
   logical, intent(out) :: valid
   REALTYPE, parameter :: eps=1.E-5
   REALTYPE :: h_ul,h_ur,h_vt,h_vb,ul,ur,vt,vb

   valid = .false.
   u = _ZERO_
   v = _ZERO_
   if (k .lt. 1 .or. k .gt. kmax) return
   if (au(i-1,j) .le. 0 .or. au(i,j) .le. 0 .or. &
       av(i,j) .le. 0 .or. av(i,j-1) .le. 0) return

   h_ul = hun(i-1,j,k)
   h_ur = hun(i,j,k)
   h_vt = hvn(i,j,k)
   h_vb = hvn(i,j-1,k)
   if (.not. ieee_is_finite(h_ul) .or. .not. ieee_is_finite(h_ur) .or. &
       .not. ieee_is_finite(h_vt) .or. .not. ieee_is_finite(h_vb)) return
   if (min(h_ul,h_ur,h_vt,h_vb) .le. _ZERO_) return
   if (.not. ieee_is_finite(uu(i-1,j,k)) .or. .not. ieee_is_finite(uu(i,j,k)) .or. &
       .not. ieee_is_finite(vv(i,j,k)) .or. .not. ieee_is_finite(vv(i,j-1,k))) return

   ul = uu(i-1,j,k)/(h_ul+eps)
   ur = uu(i,j,k)/(h_ur+eps)
   vt = vv(i,j,k)/(h_vt+eps)
   vb = vv(i,j-1,k)/(h_vb+eps)
   u = 0.5*(ul+ur)
   v = 0.5*(vt+vb)
   valid = ieee_is_finite(u) .and. ieee_is_finite(v)
   end subroutine sample_getm_tpoint_velocity
#endif

#ifdef GETM_PARALLEL
! Emit one distributed sample for the same global center-nearest wet T point
! selected by the serial path. This routine is called only at common main-loop
! iteration numbers (all ranks share MinN, MaxN, and this cadence). It performs
! a one-time deterministic station selection, then a read-only broadcast from
! the owner at each diagnostic interval. Only rank 0 writes the record.
   subroutine emit_getm_physics_diagnostic_mpi(n,runtype,do_3d)
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use mpi, only: MPI_ALLREDUCE,MPI_BCAST,MPI_DOUBLE_PRECISION,MPI_INTEGER,MPI_MIN
   use halo_mpi, only: myid,comm_getm,runtime_physics_diag_dynamic_supported, &
                       runtime_physics_diag_velocity_supported
   use getm_config, only: runtime_diag_hotstart
   use domain, only: H,az,au,av,imin,imax,jmin,jmax,il,ih,jl,jh,ioff,joff
#ifndef NO_3D
   use domain, only: kmax
#endif
   use time, only: write_time_string,julianday,secondsofday
   use variables_2d, only: z,D
#ifndef NO_3D
   use variables_3d, only: kmin
#endif
   IMPLICIT NONE
   integer, intent(in) :: n,runtype
   logical, intent(in) :: do_3d
   integer, save :: station_i=0,station_j=0,station_global_i=0,station_global_j=0
   integer, save :: station_owner=-1
   logical, save :: station_initialized=.false.,station_found=.false.,unsupported_notice_written=.false.
   integer :: i,j,global_i,global_j,local_global_i,local_global_j
   integer :: local_j_candidate,global_j_candidate,local_i_candidate,global_i_candidate
   integer :: local_owner,diag_status,ierr,target_global_i,target_global_j
   integer :: velocity_status,velocity_reason_code,layer_indices(2)
   real(kind=8) :: local_distance,global_distance,distance,values(3),velocity_values(6)
   character(len=19) :: sample_time
   character(len=1024) :: diagnostic_line
   character(len=512) :: velocity_suffix
   REALTYPE :: u_surface,v_surface,u_bottom,v_bottom,speed_surface,speed_bottom
   logical :: surface_valid,bottom_valid

   if (runtime_diag_hotstart .or. .not. runtime_physics_diag_dynamic_supported()) then
      if (myid .eq. 0 .and. .not. unsupported_notice_written) then
         if (runtime_diag_hotstart) then
            STDERR 'GETM_PHYSICS_DIAG status=unsupported reason=mpi_hotstart_unverified'
         else
            STDERR 'GETM_PHYSICS_DIAG status=unsupported reason=mpi_decomposition_unverified'
         end if
      end if
      unsupported_notice_written = .true.
      return
   end if

   if (.not. station_initialized) then
      target_global_i = il + (ih-il)/2
      target_global_j = jl + (jh-jl)/2
      station_global_i = 0
      station_global_j = 0
      station_owner = -1
      local_distance = huge(1.0d0)
      local_global_i = huge(1)
      local_global_j = huge(1)
      do j=jmin,jmax
         do i=imin,imax
            global_i = i + ioff
            global_j = j + joff
            if (global_i .lt. il .or. global_i .gt. ih .or. &
                global_j .lt. jl .or. global_j .gt. jh) cycle
            if (az(i,j) .eq. 1 .and. ieee_is_finite(H(i,j)) .and. H(i,j) .gt. 0) then
               distance = real(global_i-target_global_i,kind=8)**2 + &
                          real(global_j-target_global_j,kind=8)**2
               if (distance .lt. local_distance .or. &
                   (distance .eq. local_distance .and. global_j .lt. local_global_j) .or. &
                   (distance .eq. local_distance .and. global_j .eq. local_global_j .and. &
                    global_i .lt. local_global_i)) then
                  local_distance = distance
                  local_global_i = global_i
                  local_global_j = global_j
               end if
            end if
         end do
      end do

      call MPI_ALLREDUCE(local_distance,global_distance,1,MPI_DOUBLE_PRECISION,MPI_MIN,comm_getm,ierr)
      local_j_candidate = huge(1)
      if (local_distance .eq. global_distance) local_j_candidate = local_global_j
      call MPI_ALLREDUCE(local_j_candidate,global_j_candidate,1,MPI_INTEGER,MPI_MIN,comm_getm,ierr)
      local_i_candidate = huge(1)
      if (local_distance .eq. global_distance .and. local_global_j .eq. global_j_candidate) then
         local_i_candidate = local_global_i
      end if
      call MPI_ALLREDUCE(local_i_candidate,global_i_candidate,1,MPI_INTEGER,MPI_MIN,comm_getm,ierr)

      if (global_j_candidate .ne. huge(1) .and. global_i_candidate .ne. huge(1)) then
         local_owner = huge(1)
         if (local_distance .eq. global_distance .and. local_global_j .eq. global_j_candidate .and. &
             local_global_i .eq. global_i_candidate) local_owner = myid
         call MPI_ALLREDUCE(local_owner,station_owner,1,MPI_INTEGER,MPI_MIN,comm_getm,ierr)
         if (station_owner .ne. huge(1)) then
            station_global_i = global_i_candidate
            station_global_j = global_j_candidate
            station_i = station_global_i - ioff
            station_j = station_global_j - joff
            station_found = .true.
         end if
      end if
      station_initialized = .true.
   end if

   if (.not. station_found) then
      if (myid .eq. 0) write(stderr,'(A,I0)') &
         'GETM_PHYSICS_DIAG status=unavailable reason=no_wet_cell completed_step=',n
      return
   end if

   diag_status = 0
   values = 0.0d0
   if (myid .eq. station_owner) then
      if (az(station_i,station_j) .eq. 1 .and. ieee_is_finite(z(station_i,station_j)) .and. &
          ieee_is_finite(H(station_i,station_j)) .and. ieee_is_finite(D(station_i,station_j)) .and. &
          z(station_i,station_j) .gt. -9000 .and. H(station_i,station_j) .gt. 0 .and. &
          D(station_i,station_j) .gt. 0) then
         diag_status = 1
         values = (/ z(station_i,station_j),H(station_i,station_j),D(station_i,station_j) /)
      end if
   end if
   call MPI_BCAST(diag_status,1,MPI_INTEGER,station_owner,comm_getm,ierr)
   if (diag_status .eq. 1) call MPI_BCAST(values,3,MPI_DOUBLE_PRECISION,station_owner,comm_getm,ierr)

   velocity_status = 0
   velocity_reason_code = 0
   layer_indices = 0
   velocity_values = 0.0d0
   if (diag_status .eq. 1) then
      if (myid .eq. station_owner) then
#ifdef NO_3D
         velocity_reason_code = 1
#else
         if (runtype .le. 1) then
            velocity_reason_code = 1
         else if (.not. do_3d) then
            velocity_reason_code = 2
         else if (.not. runtime_physics_diag_velocity_supported()) then
            velocity_reason_code = 5
         else
            layer_indices = (/ kmax,kmin(station_i,station_j) /)
            if (layer_indices(2) .lt. 1 .or. layer_indices(2) .gt. kmax) then
               velocity_reason_code = 3
            else
               call sample_getm_tpoint_velocity(station_i,station_j,layer_indices(1), &
                                                u_surface,v_surface,surface_valid)
               call sample_getm_tpoint_velocity(station_i,station_j,layer_indices(2), &
                                                u_bottom,v_bottom,bottom_valid)
               if (.not. surface_valid .or. .not. bottom_valid) then
                  velocity_reason_code = 4
               else
                  speed_surface = sqrt(u_surface*u_surface+v_surface*v_surface)
                  speed_bottom = sqrt(u_bottom*u_bottom+v_bottom*v_bottom)
                  if (.not. ieee_is_finite(speed_surface) .or. .not. ieee_is_finite(speed_bottom)) then
                     velocity_reason_code = 4
                  else
                     velocity_status = 1
                     velocity_values = (/ u_surface,v_surface,speed_surface, &
                                          u_bottom,v_bottom,speed_bottom /)
                  end if
               end if
            end if
         end if
#endif
      end if
      call MPI_BCAST(velocity_status,1,MPI_INTEGER,station_owner,comm_getm,ierr)
      call MPI_BCAST(velocity_reason_code,1,MPI_INTEGER,station_owner,comm_getm,ierr)
      if (velocity_status .eq. 1) then
         call MPI_BCAST(layer_indices,2,MPI_INTEGER,station_owner,comm_getm,ierr)
         call MPI_BCAST(velocity_values,6,MPI_DOUBLE_PRECISION,station_owner,comm_getm,ierr)
      end if
   end if

   if (myid .eq. 0) then
      if (diag_status .ne. 1) then
         write(stderr,'(A,I0,1X,A,I0,1X,A,I0)') &
            'GETM_PHYSICS_DIAG status=unavailable reason=selected_cell_dry completed_step=',n, &
            'global_i=',station_global_i,'global_j=',station_global_j
      else
         call write_time_string(julianday,secondsofday,sample_time)
         sample_time(11:11) = 'T'
         write(diagnostic_line,'(A,I0,1X,A,A,1X,A,I0,1X,A,I0,1X,A,I0,1X,A,ES0.8E3,1X,A,ES0.8E3,1X,A,ES0.8E3)') &
            'GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=',n, &
            'sim_time=',trim(sample_time),'global_i=',station_global_i,'global_j=',station_global_j, &
            'owner_rank=',station_owner,'z_surface_m=',values(1),'H_static_m=',values(2), &
            'D_total_m=',values(3)
         call physics_velocity_suffix(velocity_status,velocity_reason_code,layer_indices, &
                                     velocity_values,velocity_suffix)
         write(stderr,'(A)') trim(diagnostic_line)//trim(velocity_suffix)
      end if
   end if
   end subroutine emit_getm_physics_diagnostic_mpi
#else
!-----------------------------------------------------------------------
! Emit one solver-owned T-point sample after a completed step. The station is
! the wet interior cell nearest the configured domain centre, with deterministic
! global-j/global-i ordering for ties. It is selected once per process run.
   subroutine emit_getm_physics_diagnostic(n,runtype,do_3d)
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use domain, only: H,az,au,av,imin,imax,jmin,jmax,il,ih,jl,jh,ioff,joff
#ifndef NO_3D
   use domain, only: kmax
#endif
   use time, only: write_time_string,julianday,secondsofday
   use variables_2d, only: z,D
#ifndef NO_3D
   use variables_3d, only: kmin
#endif
   IMPLICIT NONE
   integer, intent(in) :: n,runtype
   logical, intent(in) :: do_3d
   integer, save :: station_i=0,station_j=0,station_global_i=0,station_global_j=0
   integer, save :: target_global_i=0,target_global_j=0
   logical, save :: station_initialized=.false.,station_found=.false.
   integer :: i,j,global_i,global_j
   integer :: velocity_status,velocity_reason_code,layer_indices(2)
   real(kind=8) :: best_distance,distance
   character(len=19) :: sample_time
   character(len=40) :: velocity_reason
   character(len=1024) :: diagnostic_line
   character(len=512) :: velocity_suffix
   REALTYPE :: u_surface,v_surface,u_bottom,v_bottom,speed_surface,speed_bottom
   logical :: surface_valid,bottom_valid

   if (.not. station_initialized) then
      target_global_i = il + (ih-il)/2
      target_global_j = jl + (jh-jl)/2
      best_distance = huge(best_distance)
      do j=jmin,jmax
         do i=imin,imax
            if (az(i,j) .eq. 1 .and. ieee_is_finite(H(i,j)) .and. H(i,j) .gt. 0) then
               global_i = i + ioff
               global_j = j + joff
               distance = real(global_i-target_global_i,kind=8)**2 + &
                          real(global_j-target_global_j,kind=8)**2
               if (distance .lt. best_distance) then
                  best_distance = distance
                  station_i = i
                  station_j = j
                  station_global_i = global_i
                  station_global_j = global_j
                  station_found = .true.
               end if
            end if
         end do
      end do
      station_initialized = .true.
   end if

   if (.not. station_found) then
      write(stderr,'(A,I0)') 'GETM_PHYSICS_DIAG status=unavailable reason=no_wet_cell completed_step=',n
      return
   end if
   if (az(station_i,station_j) .ne. 1 .or. .not. ieee_is_finite(z(station_i,station_j)) .or. &
       .not. ieee_is_finite(H(station_i,station_j)) .or. .not. ieee_is_finite(D(station_i,station_j)) .or. &
       z(station_i,station_j) .le. -9000 .or. H(station_i,station_j) .le. 0 .or. &
       D(station_i,station_j) .le. 0) then
      write(stderr,'(A,I0,1X,A,I0,1X,A,I0)') &
         'GETM_PHYSICS_DIAG status=unavailable reason=selected_cell_dry completed_step=',n, &
         'global_i=',station_global_i,'global_j=',station_global_j
      return
   end if

   call write_time_string(julianday,secondsofday,sample_time)
   sample_time(11:11) = 'T'
   velocity_status = 0
   velocity_reason_code = 0
   layer_indices = 0
#ifdef NO_3D
   velocity_reason_code = 1
#else
   if (runtype .le. 1) then
      velocity_reason_code = 1
   else if (.not. do_3d) then
      velocity_reason_code = 2
   else
      layer_indices = (/ kmax,kmin(station_i,station_j) /)
      if (layer_indices(2) .lt. 1 .or. layer_indices(2) .gt. kmax) then
         velocity_reason_code = 3
      else
         call sample_getm_tpoint_velocity(station_i,station_j,layer_indices(1), &
                                          u_surface,v_surface,surface_valid)
         call sample_getm_tpoint_velocity(station_i,station_j,layer_indices(2), &
                                          u_bottom,v_bottom,bottom_valid)
         if (.not. surface_valid .or. .not. bottom_valid) then
            velocity_reason_code = 4
         else
            speed_surface = sqrt(u_surface*u_surface+v_surface*v_surface)
            speed_bottom = sqrt(u_bottom*u_bottom+v_bottom*v_bottom)
            if (.not. ieee_is_finite(speed_surface) .or. .not. ieee_is_finite(speed_bottom)) then
               velocity_reason_code = 4
            else
               velocity_status = 1
            end if
         end if
      end if
   end if
#endif
   write(diagnostic_line,'(A,I0,1X,A,A,1X,A,I0,1X,A,I0,1X,A,ES0.8E3,1X,A,ES0.8E3,1X,A,ES0.8E3)') &
      'GETM_PHYSICS_DIAG status=available kind=center_wet_T completed_step=',n, &
      'sim_time=',trim(sample_time),'global_i=',station_global_i,'global_j=',station_global_j, &
      'z_surface_m=',z(station_i,station_j),'H_static_m=',H(station_i,station_j), &
      'D_total_m=',D(station_i,station_j)
   if (velocity_status .eq. 1) then
      call physics_velocity_suffix(velocity_status,velocity_reason_code,layer_indices, &
                                   (/ u_surface,v_surface,speed_surface,u_bottom,v_bottom,speed_bottom /), &
                                   velocity_suffix)
   else
      call physics_velocity_suffix(velocity_status,velocity_reason_code,layer_indices, &
                                   (/ 0.0d0,0.0d0,0.0d0,0.0d0,0.0d0,0.0d0 /),velocity_suffix)
   end if
   write(stderr,'(A)') trim(diagnostic_line)//trim(velocity_suffix)
   end subroutine emit_getm_physics_diagnostic
#endif
#endif

!-----------------------------------------------------------------------

   end module integration

!-----------------------------------------------------------------------
! Copyright (C) 2001 - Hans Burchard and Karsten Bolding               !
!-----------------------------------------------------------------------
