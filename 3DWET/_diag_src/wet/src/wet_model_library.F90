!*******************************************************************************
!*                                                                             *
!* wet_model_library.F90                                                    *
!*                                                                             *
!*******************************************************************************

module wet_model_library

   use fabm_types, only: type_base_model_factory,type_base_model

   use wet_version
   use wet_abiotic_water
   use wet_abiotic_sediment
   use wet_om_pool
   use wet_phytoplankton
   use wet_macrophytes
   use wet_zooplankton
   use wet_fish
   use wet_fish_pclake
   use wet_zoobenthos
   use wet_burial
   use wet_sediment_exchange
   use wet_bot_pel_interface
   use wet_bivalves
   use wet_inorganic_carbon
   use wet_methane

   implicit none

   private

   type,extends(type_base_model_factory) :: type_factory
      contains
      procedure :: initialize
      procedure :: create
   end type

   type (type_factory),save,target,public :: wet_model_factory

contains

   subroutine initialize(self)
      class (type_factory), intent(inout) :: self
      call self%register_version('WET',git_commit_id//' ('//git_branch_name//' branch)')
   end subroutine initialize

   subroutine create(self,name,model)
      class (type_factory),intent(in) :: self
      character(*),        intent(in) :: name
      class (type_base_model),pointer :: model

      select case (name)
         case ('abiotic_water');          allocate(type_wet_abiotic_water::model);
         case ('abiotic_sediment');       allocate(type_wet_abiotic_sediment::model);
         case ('om_pool');                allocate(type_wet_om_pool::model);
         case ('phytoplankton');          allocate(type_wet_phytoplankton::model);
         case ('macrophytes');            allocate(type_wet_macrophytes::model);
         case ('zooplankton');            allocate(type_wet_zooplankton::model);
         case ('fish');                   allocate(type_wet_fish::model);
         case ('fish_pclake');            allocate(type_wet_fish_pclake::model);
         case ('bivalves');               allocate(type_wet_bivalves::model);
         case ('zoobenthos');             allocate(type_wet_zoobenthos::model);
         case ('burial');                 allocate(type_wet_burial::model);
         case ('sediment_exchange');      allocate(type_wet_sediment_exchange::model);
         case ('bot_pel_interface');      allocate(type_wet_bot_pel_interface::model);
         case ('inorganic_carbon');       allocate(type_wet_inorganic_carbon::model);
         case ('methane');                allocate(type_wet_methane::model);
         case default
            call self%type_base_model_factory%create(name,model)
       end select
   end subroutine create

end module

!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
