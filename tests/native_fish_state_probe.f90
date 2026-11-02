program fish_state_probe
   use wet_fish
   use fabm_types
   implicit none
   type(type_wet_fish) :: fish
   type(type_environment) :: env
   logical :: valid, changed
   integer :: stage, transport, diagnostics, i, cases
   allocate(env%prefetch(6,24),env%scratch(6,8),env%prefetch_scalar(1))
   env%n=6
   cases=0
   fish%id_sDFi%index=7
   fish%id_sDSiz%index=8
   fish%id_sNFi%index=9
   fish%id_sPFi%index=10
   fish%id_sCFi%index=11
   fish%id_FiJu_D%index=12
   fish%id_FiJu_P%index=13
   fish%id_FiJu_N%index=14
   fish%id_FiJu_C%index=15
   fish%id_FiJu_Res%index=16
   fish%id_FiJu_Siz%index=17
   fish%id_DPOMpoolW%index=18
   fish%id_NPOMpoolW%index=19
   fish%id_PPOMpoolW%index=20
   fish%id_CPOMpoolW%index=21
   do stage=0,3
      do transport=0,3
         do diagnostics=0,1
            fish%qStage=stage
            fish%qTrans=transport
            fish%diagnostics=diagnostics==1
            fish%cDayReprFish=120.0_rk
            fish%fResMax=0.25_rk
            fish%fResMin=0.0_rk
            fish%id_Day%global_index=1
            fish%id_Day_last_state%index=6
            fish%id_Day_last_save%diag_index=1
            ! Match registration: absent optional variables retain invalid IDs.
            fish%id_sFRes%index=-1
            if(stage>0) fish%id_sFRes%index=2
            fish%id_tDReproPOM%diag_index=2
            fish%id_tNReproPOM%diag_index=3
            fish%id_tPReproPOM%diag_index=4
            fish%id_tCReproPOM%diag_index=5
            env%prefetch=2000.0_rk
            env%prefetch(:,1)=0.0_rk
            env%prefetch(:,2)=0.5_rk
            env%prefetch_scalar=1.0_rk
            env%scratch=777.0_rk
            valid=.true.
            changed=.false.
            call fish%check_state(env,.true.,valid,changed)
            if(.not.valid) stop 10
            if(any(env%prefetch(:,3:4)/=2000.0_rk)) stop 11
            if(any(env%prefetch(:,6)/=1.0_rk)) stop 18
            if(stage>0 .and. transport>1) then
               if(any(env%prefetch(:,2)/=0.25_rk).or..not.changed) stop 12
            else
               if(any(env%prefetch(:,2)/=0.5_rk).or..not.changed) stop 13
            endif
            if(any(env%scratch(:,1)/=1.0_rk)) stop 14
            if(any(env%scratch(:,2:5)/=0.0_rk)) stop 15
            if(any(env%scratch(:,6:8)/=777.0_rk)) stop 17
            cases=cases+1
         enddo
      enddo
   enddo
   ! Exercise the real check_state dispatch over six independent cells.
   fish%qStage=1
   fish%qTrans=0
   fish%cDayReprFish=120.0_rk
   fish%fResMax=0.25_rk
   fish%fResMin=0.0_rk
   fish%fGonad=0.1_rk
   fish%fReproFish=0.5_rk
   fish%cDegg=0.5_rk
   env%prefetch=0.0_rk
   env%prefetch(:,2)=0.2_rk
   env%prefetch(:,6)=[119.5_rk,120.0_rk,0.0_rk,119.5_rk,119.5_rk,119.5_rk]
   env%prefetch(:,7)=10.0_rk
   env%prefetch(:,8)=1.0_rk
   env%prefetch(:,9)=1.0_rk
   env%prefetch(:,10)=0.2_rk
   env%prefetch(:,11)=4.0_rk
   env%prefetch(:,12)=2.0_rk
   env%prefetch(:,13)=0.2_rk
   env%prefetch(:,14)=1.0_rk
   env%prefetch(:,15)=4.0_rk
   env%prefetch(:,16)=0.1_rk
   env%prefetch(:,17)=1.0_rk
   env%prefetch(:,18:21)=0.0_rk
   env%prefetch_scalar(1)=120.0_rk
   env%scratch=0.0_rk
   valid=.true.
   changed=.false.
   call fish%check_state(env,.true.,valid,changed)
   if(.not.valid.or..not.changed) stop 20
   if(env%prefetch(1,7)>=10.0_rk.or.env%prefetch(1,12)<=2.0_rk) stop 21
   if(env%prefetch(2,7)/=10.0_rk.or.env%prefetch(2,12)/=2.0_rk) stop 22
   if(env%prefetch(3,7)>=10.0_rk.or.env%prefetch(3,12)<=2.0_rk) stop 23
   if(any(env%prefetch(:,6)/=120.0_rk)) stop 24
   ! A new model object represents the restart continuation; restored state remains per cell.
   env%prefetch_scalar(1)=120.5_rk
   valid=.true.
   changed=.false.
   call fish%check_state(env,.true.,valid,changed)
   if(env%prefetch(1,7)/=9.2_rk.or.env%prefetch(2,7)/=10.0_rk) stop 25
   if(any(env%prefetch(:,6)/=120.5_rk)) stop 26
   ! Annual day-of-year rollover resets the persisted comparison point before next breeding day.
   env%prefetch_scalar(1)=0.0_rk
   valid=.true.
   changed=.false.
   call fish%check_state(env,.true.,valid,changed)
   if(any(env%prefetch(:,6)/=0.0_rk)) stop 27
   env%prefetch_scalar(1)=119.0_rk
   valid=.true.
   changed=.false.
   call fish%check_state(env,.true.,valid,changed)
   if(any(env%prefetch(:,6)/=119.0_rk)) stop 28
   env%prefetch_scalar(1)=120.0_rk
   valid=.true.
   changed=.false.
   call fish%check_state(env,.true.,valid,changed)
   if(env%prefetch(1,7)>=9.2_rk.or.env%prefetch(2,7)>=10.0_rk) stop 29
   if(any(env%prefetch(:,6)/=120.0_rk)) stop 30
   print *, 'PASS optional fish state and diagnostics:',cases,'combinations'
end program
