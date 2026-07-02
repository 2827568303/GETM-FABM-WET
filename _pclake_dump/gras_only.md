# Grass Carp (Gras) Module - Complete Equation Reference

All Gras-defined and Gras-referenced equations from derivatives sheet.

## A. Gras-defined equations (name contains 'Gras')

### `_aDGras_`  [_gDW_*_m_^-2]  *state_auxiliary*
- DESC: state_auxiliary_with_error_catching
```
_aDGras_= _IF_ _sDGras_ _GT_ _NearZero_ _THEN_ _sDGras_ _ELSE_ _NearZero_ _ENDIF_
```

### `_uGrasMortHyp_`  [0]  *Gras_fish_processes*
- DESC: Grass_carp_fraction
```
_uGrasMortHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasMortHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uGrasEgesHyp_`  [0]  *Gras_fish_processes*
- DESC: Grass_carp_fraction
```
_uGrasEgesHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasEgesHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uGrasExcrHyp_`  [0]  *Gras_fish_processes*
- DESC: Grass_carp_fraction
```
_uGrasExcrHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasExcrHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tDGrazVegGras_`  [_gDW_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: Biomass_loss_due_to_grazing_of_Gras_fish
```
_tDGrazVegGras_ = _IF_ _tDConsGras_ _GT_ _NearZero_ _THEN_ _tDConsGras_ _ELSE_ _NearZero_ _ENDIF_
```

### `_tPGrazVegGras_`  [_gP_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: P_mortality_flux_of_vegetation_by_Gras_grazing
```
_tPGrazVegGras_ = _rPDVeg_ * _tDGrazVegGras_
```

### `_tNGrazVegGras_`  [_gN_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: N_mortality_flux_of_vegetation_by_Gras_grazing
```
_tNGrazVegGras_ = _rNDVeg_ * _tDGrazVegGras_
```

### `_uFunTmGras_`  [0]  *Gras_fish_processes*
- DESC: temp_function_of_Grass_carp
```
_uFunTmGras_ = _EXP_(-0.5 /(_cSigTmGras_*_cSigTmGras_) *((_uTmEpi_ - _cTmOptGras_)*(_uTmEpi_ - _cTmOptGras_) - (_cTmRef_ - _cTmOptGras_)*(_cTmRef_ - _cTmOptGras_)))
```

### `_akDIncrGras_`  [_d_^-1]  *Gras_fish_processes*
- DESC: intrinsic_net_increase_rate_of_Grass_carp
```
_akDIncrGras_ = (_kDAssGras_ - _kDRespGras_) * _uFunTmGras_ - _kMortGras_
```

### `_ukHarvGras_`  [_d_^-1]  *Gras_fish_processes*
- DESC: fish_harvesting_constant
```
_ukHarvGras_ = _IF_ (_COS_(2.0*_Pi_ * _sTime_ / _DaysPerYear_) _GT_ 0.1) _THEN_ _kHarvGrasWin_ _ELSE_ _kHarvGrasSum_ _ENDIF_
```

### `_aDSatGras_`  [0]  *Gras_fish_processes*
- DESC: food_limitation_function_of_Grass_carp
```
_aDSatGras_ = _aDVeg_*_aDVeg_ /(_hDVegGras_*_hDVegGras_ + _aDVeg_*_aDVeg_)
```

### `_tDEnvGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: environmental_correction_of_Grass_carp
```
_tDEnvGras_ = _MAX_(0.0,_akDIncrGras_ / _cDCarrGras_ * _aDGras_*_aDGras_)
```

### `_tDAssGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: assimilation_of_Grass_carp
```
_tDAssGras_ = _aDSatGras_ *(_kDAssGras_ * _uFunTmGras_ * _aDGras_ - _tDEnvGras_)
```

### `_tDConsGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: consumption_of_Grass_carp
```
_tDConsGras_ = _tDAssGras_ / _fDAssGras_
```

### `_tDEgesGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: egestion_of_Grass_carp
```
_tDEgesGras_ = _tDConsGras_ - _tDAssGras_
```

### `_tDMortGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: mortality_of_Grass_carp(incl_environmental_correction)
```
_tDMortGras_ = _kMortGras_ * _aDGras_ +(1.0 - _aDSatGras_) * _tDEnvGras_
```

### `_tDMigrGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: migration_flux_of_Grass_carp
```
_tDMigrGras_ = _kMigrGras_ *(_cDGrasIn_ - _aDGras_)
```

### `_tDRespGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: respiration_of_Grass_carp
```
_tDRespGras_ = _kDRespGras_ * _uFunTmGras_ * _aDGras_
```

### `_tDMortGrasBot_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_fish_DW_fixed_in_bones_AND_scales
```
_tDMortGrasBot_ = _fDBone_ * _tDMortGras_
```

### `_tDMortGrasDet_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_Grass_carp_DW_becoming_detritus
```
_tDMortGrasDet_ = _tDMortGras_ - _tDMortGrasBot_
```

### `_tDHarvGras_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: harvesting_of_Grass_carp
```
_tDHarvGras_ = _ukHarvGras_ * _aDGras_
```

### `_aPGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: total_P_in_Grass_carp
```
_aPGras_ = _cPDGras_ * _aDGras_
```

### `_tPConsGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: total_P_consumption_by_Grass_carp
```
_tPConsGras_ = _rPDVeg_ * _tDConsGras_
```

### `_rPDFoodGras_`  [_gP_*_gDW_^-1]  *Gras_fish_processes*
- DESC: average_P/D_ratio_of_Grass_carp_food
```
_rPDFoodGras_ = _tPConsGras_ / _tDConsGras_
```

### `_tDConsGrasNut_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: Consumption_of_Gras_corrected_for_N_and_P_limitation
```
_tDConsGrasNut_ = (_tDAssGras_ / _fDAssGras_) * _MAX_ (1.0, _cNDGras_ / _rNDFoodGras_ * _fDAssGras_, _cPDGras_ / _rPDFoodGras_ * _fDAssGras_)
```

### `_tDEgesGrasNut_`  [_gDW_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: Egestion_of_Gras_corrected_for_N_and_P_limitation
```
_tDEgesGrasNut_ = _tDConsGrasNut_ - _tDAssGras_
```

### `_tPConsGrasNut_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: Total_P_consumption_by_Gras
```
_tPConsGrasNut_ = _rPDVeg_ * _tDConsGrasNut_
```

### `_tNConsGrasNut_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: Total_N_consumption_by_Gras
```
_tNConsGrasNut_ = _rNDVeg_ * _tDConsGrasNut_
```

### `_afPAssGras_`  [0]  *Gras_fish_processes*
- DESC: P_assim_efficiency_of_Grass_carp
```
_afPAssGras_ = _MIN_(1.0,_cPDGras_ / _rPDFoodGras_ * _fDAssGras_)
```

### `_tPAssGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: P_assimilation_of_Grass_carp
```
_tPAssGras_ = _afPAssGras_ * _tPConsGras_
```

### `_tPEgesGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: egestion_of_Grass_carp
```
_tPEgesGras_ = _tPConsGras_ - _tPAssGras_
```

### `_tPEgesGrasPO4_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: SRP_egestion_of_Grass_carp
```
_tPEgesGrasPO4_ = _fDissEgesGras_ * _tPEgesGras_
```

### `_tPEgesGrasDet_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: detrital_P_egestion_of_Grass_carp
```
_tPEgesGrasDet_ = _tPEgesGras_ - _tPEgesGrasPO4_
```

### `_tPExcrGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: respiration_of_Grass_carp
```
_tPExcrGras_ = _cPDGras_ * _tDRespGras_
```

### `_tPMortGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: mortality_of_Grass_carp
```
_tPMortGras_ = _cPDGras_ * _tDMortGras_
```

### `_tPMortGrasBot_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_Grass_carp_P_fixed_in_bones_AND_scales
```
_tPMortGrasBot_ = _fPBone_ * _tPMortGras_
```

### `_tPMortGrasPO4_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_fish_P_becoming_dissolved_P
```
_tPMortGrasPO4_ = _fDissMortGras_ *(_tPMortGras_ - _tPMortGrasBot_)
```

### `_tPMortGrasDet_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_Grass_carp_P_becoming_detrital_P
```
_tPMortGrasDet_ = _tPMortGras_ - _tPMortGrasBot_ - _tPMortGrasPO4_
```

### `_tPMigrGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: net_migration_flux
```
_tPMigrGras_ = _kMigrGras_ *(_cPDGras_ * _cDGrasIn_ - _aPGras_)
```

### `_tPHarvGras_`  [_gP_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: harvesting_of_Grass_carp
```
_tPHarvGras_ = _cPDGras_ * _tDHarvGras_
```

### `_aNGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: total_N_in_Grass_carp
```
_aNGras_ = _cNDGras_ * _aDGras_
```

### `_tNConsGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: total_N_consumption_by_Grass_carp
```
_tNConsGras_ = _rNDVeg_ * _tDConsGras_
```

### `_rNDFoodGras_`  [_gN_*_gDW_^-1]  *Gras_fish_processes*
- DESC: average_N/D_ratio_of_Grass_carp_food
```
_rNDFoodGras_ = _tNConsGras_ / _tDConsGras_
```

### `_afNAssGras_`  [0]  *Gras_fish_processes*
- DESC: N_assim_efficiency_of_Grass_carp
```
_afNAssGras_ = _MIN_(1.0,_cNDGras_ / _rNDFoodGras_ * _fDAssGras_)
```

### `_tNAssGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: N_assimilation_of_Grass_carp
```
_tNAssGras_ = _afNAssGras_ * _tNConsGras_
```

### `_tNEgesGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: egestion_of_Grass_carp
```
_tNEgesGras_ = _tNConsGras_ - _tNAssGras_
```

### `_tNEgesGrasNH4_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: SRN_egestion_of_Grass_carp
```
_tNEgesGrasNH4_ = _fDissEgesGras_ * _tNEgesGras_
```

### `_tNEgesGrasDet_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: detrital_N_egestion_of_Grass_carp
```
_tNEgesGrasDet_ = _tNEgesGras_ - _tNEgesGrasNH4_
```

### `_tNExcrGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: respiration_of_Grass_carp
```
_tNExcrGras_ = _cNDGras_ * _tDRespGras_
```

### `_tNMortGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: mortality_of_Grass_carp
```
_tNMortGras_ = _cNDGras_ * _tDMortGras_
```

### `_tNMortGrasBot_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_Grass_carp_N_fixed_in_bones_AND_scales
```
_tNMortGrasBot_ = _fDBone_ * _tNMortGras_
```

### `_tNMortGrasNH4_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_fish_N_becoming_dissolved_N
```
_tNMortGrasNH4_ = _fDissMortGras_ *(_tNMortGras_ - _tNMortGrasBot_)
```

### `_tNMortGrasDet_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: part_of_died_Grass_carp_N_becoming_detrital_N
```
_tNMortGrasDet_ = _tNMortGras_ - _tNMortGrasBot_ - _tNMortGrasNH4_
```

### `_tNMigrGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: net_migration_flux
```
_tNMigrGras_ = _kMigrGras_ *(_cNDGras_ * _cDGrasIn_ - _aNGras_)
```

### `_tNHarvGras_`  [_gN_*_m_^-2*_d_^-1]  *Gras_fish_processes*
- DESC: harvesting_of_Grass_carp
```
_tNHarvGras_ = _cNDGras_ * _tDHarvGras_
```

### `_tDWebGras_`  [_gDW_*_m_^-2*_d_^-1]  *Total_fluxes_for_animal_groups*
- DESC: total_food_web_flux_of_DW_in_Gras_fish
```
_tDWebGras_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrGras_ + _tDAssGras_ - _tDRespGras_ - _tDMortGras_ - _tDHarvGras_ _ENDIF_
```

### `_aGrowGras_`  [_d_^-1]  *Gras_fish_processes*
- DESC: per_gDW_veg_consumption_per_gDW_Grass_carp
```
_aGrowGras_ = _tDGrazVegGras_ / _aDGras_
```

### `_dDGras_`  [_gDW_*_m_^-2*_d_^-1]  *Derivatives*
- DESC: Derivative_for_DW_Grass_carp_in_lake_water
```
_dDGras_ = _tDWebGras_
```


## B. Other equations referencing Gras (coupling points)

### `_tDBedVeg_`  [_gDW_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: Derivative_of_vegetation_biomass
```
_tDBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tDMigrVeg_ + _tDProdVegEpi_ + _tDProdVegHyp_- _tDRespVeg_ - _tDMortVegEpi_ - _tDMortVegHyp_ - _tDGrazVegBird_ - _tDGrazVegGras_ - _tDManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBedVeg_`  [_gP_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: Total_vegetation_P_flux_in_bed_module
```
_tPBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tPMigrVeg_ + _tPUptVegEpi_ + _tPUptVegHyp_ - _tPExcrVeg_ - _tPMortVegEpi_ - _tPMortVegHyp_ - _tPGrazVegBird_ - _tPGrazVegGras_ - _tPManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBedVeg_`  [_gN_*_m_^-2*_d_^-1]  *Vegetation_processes*
- DESC: Total_vegetation_N_flux_in_bed_module
```
_tNBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tNMigrVeg_ + _tNUptVeg_ - _tNExcrVeg_ - _tNMortVegEpi_ - _tNMortVegHyp_ - _tNGrazVegBird_ - _tNGrazVegGras_ - _tNManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_wDWebDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_DW_in_Detritus_in_lake_water
```
_wDWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDetZooHyp_ + _wDEgesZooHyp_ + _wDMortZooHyp_ +(_tDEgesFiJv_ * _uFiJvEgesHyp_ + _tDEgesFiAd_ * _uFiAdEgesHyp_ + _tDMortFiJvDet_ * _uFiJvMortHyp_ + _tDMortFiAdDet_ * _uFiAdMortHyp_ + _tDEgesPiscNut_ * _uPiscEgesHyp_ + _tDMortPiscDet_ * _uPiscMortHyp_  + _tDEgesGras_ * _uGrasEgesHyp_ + _tDMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wDWebDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_DW_in_Detritus_in_lake_water
```
_wDWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDetZooEpi_ + _wDEgesZooEpi_ + _wDMortZooEpi_ +(_tDEgesFiJv_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tDEgesFiAd_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tDMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tDMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ ) + _tDEgesPiscNut_ * ( 1.0 - _uPiscEgesHyp_ ) + _tDMortPiscDet_ * ( 1.0 - _uPiscMortHyp_) + _tDEgesGrasNut_ * ( 1.0 - _uGrasEgesHyp_ ) + _tDMortGrasDet_ * ( 1.0 - _uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_tDWebTotT_`  [_gDW_*_m_^-2*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_DW_in_system
```
_tDWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDRespZooEpi_ * _uDepthWEpi_ - _wDRespZooHyp_ * _uDepthWHyp_ + _tDMigrFiJv_ + _tDMigrFiAd_ + _tDMigrPisc_ + _tDMigrGras_ + _tDMigrBent_ - _tDRespFiJv_ - _tDRespFiAd_ - _tDRespPisc_ - _tDRespGras_ - _tDRespBent_ - _tDMortFiJvBot_ - _tDMortFiAdBot_- _tDMortPiscBot_ - _tDMortGrasBot_ - _tDHarvFish_ - _tDHarvPisc_ - _tDHarvGras_ _ENDIF_
```

### `_wPWebPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_P_in_SRP_in_water_in_lake_water
```
_wPWebPO4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wPExcrZooHyp_ + _wPEgesZooPO4Hyp_ + _wPMortZooPO4Hyp_ +(_tPExcrFiJv_ *_uFiJvExcrHyp_ + _tPExcrFiAd_ * _uFiAdExcrHyp_ + _tPEgesFiJvPO4_ * _uFiJvEgesHyp_ + _tPEgesFiAdPO4_ * _uFiAdEgesHyp_ + _tPMortFiJvPO4_ * _uFiJvMortHyp_ + _tPMortFiAdPO4_ * _uFiAdMortHyp_+ _tPExcrPisc_ * _uPiscExcrHyp_ + _tPEgesPiscPO4_ * _uPiscEgesHyp_ + _tPMortPiscPO4_ * _uPiscMortHyp_ + _tPExcrGras_ * _uGrasExcrHyp_ + _tPEgesGrasPO4_ * _uGrasEgesHyp_ + _tPMortGrasPO4_ * _uGrasMortHyp_ ) / _uDepthWHyp_ _ENDIF_
```

### `_wPWebDetWHyp_`  [_gP_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_P_in_Detritus_in_lake_water
```
_wPWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDetZooHyp_ + _wPEgesZooDetHyp_ + _wPMortZooDetHyp_ +(_tPEgesFiJvDet_ * _uFiJvEgesHyp_ + _tPEgesFiAdDet_ * _uFiAdEgesHyp_+ _tPMortFiJvDet_ * _uFiJvMortHyp_ + _tPMortFiAdDet_ * _uFiAdMortHyp_ + _tPEgesPiscDet_ * _uPiscEgesHyp_+ _tPMortPiscDet_ * _uPiscMortHyp_ + _tPEgesGrasDet_ * _uGrasEgesHyp_+ _tPMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wPWebPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_P_in_SRP_in_water_in_lake_water
```
_wPWebPO4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wPExcrZooEpi_ + _wPEgesZooPO4Epi_ + _wPMortZooPO4Epi_ +(_tPExcrFiJv_ * ( 1.0 -_uFiJvExcrHyp_ ) + _tPExcrFiAd_ * ( 1.0 - _uFiAdExcrHyp_ )+ _tPEgesFiJvPO4_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tPEgesFiAdPO4_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tPMortFiJvPO4_ * ( 1.0 - _uFiJvMortHyp_ ) + _tPMortFiAdPO4_ * ( 1.0 - _uFiAdMortHyp_ )+ _tPExcrPisc_ * ( 1.0 - _uPiscExcrHyp_ ) + _tPEgesPiscPO4_ * ( 1.0 - _uPiscEgesHyp_ ) + _tPMortPiscPO4_ * ( 1.0 - _uPiscMortHyp_) + _tPExcrGras_ * ( 1.0 - _uGrasExcrHyp_ ) + _tPEgesGrasPO4_ * ( 1.0 - _uGrasEgesHyp_ ) + _tPMortGrasPO4_ * ( 1.0 - _uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_wPWebDetWEpi_`  [_gP_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_P_in_Detritus_in_lake_water
```
_wPWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDetZooEpi_ + _wPEgesZooDetEpi_ + _wPMortZooDetEpi_ +(_tPEgesFiJvDet_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tPEgesFiAdDet_ * ( 1.0 - _uFiAdEgesHyp_ )+ _tPMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tPMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ )+ _tPEgesPiscDet_ * ( 1.0 - _uPiscEgesHyp_ )+ _tPMortPiscDet_ * ( 1.0 - _uPiscMortHyp_ ) + _tPEgesGrasDet_ * ( 1.0 - _uGrasEgesHyp_ )+ _tPMortGrasDet_ * ( 1.0 - _uGrasMortHyp_ )) / _uDepthWEpi_ _ENDIF_
```

### `_tPWebTotT_`  [_gP_*_m_^-2*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_P_in_system
```
_tPWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPMigrFiJv_ + _tPMigrFiAd_ + _tPMigrPisc_ + _tPMigrGras_ + _tPMigrBent_ - _tPMortFiJvBot_ - _tPMortFiAdBot_- _tPMortPiscBot_ - _tPMortGrasBot_ - _tPHarvFish_ - _tPHarvPisc_ - _tPHarvGras_ _ENDIF_
```

### `_wNWebNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_N_in_ammonium_in_water_in_lake_water
```
_wNWebNH4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wNExcrZooHyp_ + _wNEgesZooNH4Hyp_ + _wNMortZooNH4Hyp_ +(_tNExcrFiJv_ * _uFiJvExcrHyp_ + _tNExcrFiAd_ * _uFiAdExcrHyp_ + _tNEgesFiJvNH4_ * _uFiJvEgesHyp_+ _tNEgesFiAdNH4_ * _uFiAdEgesHyp_ + _tNMortFiAdNH4_ *_uFiAdMortHyp_+ _tNMortFiJvNH4_*_uFiJvMortHyp_ + _tNExcrPisc_ *_uPiscExcrHyp_ + _tNEgesPiscNH4_ *_uPiscEgesHyp_ + _tNMortPiscNH4_ *_uPiscMortHyp_ + _tNExcrGras_ *_uGrasExcrHyp_ + _tNEgesGrasNH4_ *_uGrasEgesHyp_ + _tNMortGrasNH4_ *_uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wNWebDetWHyp_`  [_gN_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_N_in_Detritus_in_lake_water
```
_wNWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDetZooHyp_ + _wNEgesZooDetHyp_ + _wNMortZooDetHyp_ +(_tNEgesFiJvDet_ * _uFiJvEgesHyp_ +_tNEgesFiAdDet_ * _uFiAdEgesHyp_+ _tNMortFiJvDet_ * _uFiJvMortHyp_ + _tNMortFiAdDet_ * _uFiAdMortHyp_ + _tNEgesPiscDet_ * _uPiscEgesHyp_ + _tNMortPiscDet_ * _uPiscMortHyp_ + _tNEgesGrasDet_ * _uGrasEgesHyp_ + _tNMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wNWebNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_N_in_ammonium_in_water_in_lake_water
```
_wNWebNH4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wNExcrZooEpi_ + _wNEgesZooNH4Epi_ + _wNMortZooNH4Epi_ +(_tNExcrFiJv_ * ( 1.0 - _uFiJvExcrHyp_) + _tNExcrFiAd_ * ( 1.0 - _uFiAdExcrHyp_) + _tNEgesFiJvNH4_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tNEgesFiAdNH4_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tNMortFiAdNH4_ * ( 1.0 -_uFiAdMortHyp_ ) + _tNMortFiJvNH4_* ( 1.0 -_uFiJvMortHyp_) + _tNExcrPisc_ * ( 1.0 -_uPiscExcrHyp_ ) + _tNEgesPiscNH4_ * ( 1.0 -_uPiscEgesHyp_ ) + _tNMortPiscNH4_ * ( 1.0 -_uPiscMortHyp_) + _tNExcrGras_ * ( 1.0 -_uGrasExcrHyp_ ) + _tNEgesGrasNH4_ * ( 1.0 -_uGrasEgesHyp_ ) + _tNMortGrasNH4_ * ( 1.0 -_uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_wNWebDetWEpi_`  [_gN_*_m_^-3*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_food_web_flux_of_N_in_Detritus_in_lake_water
```
_wNWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDetZooEpi_ + _wNEgesZooDetEpi_ + _wNMortZooDetEpi_ +(_tNEgesFiJvDet_ * ( 1.0 - _uFiJvEgesHyp_ ) +_tNEgesFiAdDet_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tNMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tNMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ ) + _tNEgesPiscDet_ * ( 1.0 - _uPiscEgesHyp_ ) + _tNMortPiscDet_ * ( 1.0 - _uPiscMortHyp_ ) + _tNEgesGrasDet_ * ( 1.0 - _uGrasEgesHyp_ ) + _tNMortGrasDet_ * ( 1.0 - _uGrasMortHyp_ )) / _uDepthWEpi_ _ENDIF_
```

### `_tNWebTotT_`  [_gN_*_m_^-2*_d_^-1]  *Total_fluxes_to/from_other_components*
- DESC: Total_N_in_system
```
_tNWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNMigrFiJv_ + _tNMigrFiAd_ + _tNMigrPisc_ + _tNMigrGras_ + _tNMigrBent_ - _tNMortFiJvBot_- _tNMortFiAdBot_ - _tNMortPiscBot_ - _tNMortGrasBot_ - _tNHarvFish_ - _tNHarvPisc_ - _tNHarvGras_ _ENDIF_
```

### `_aDTotT_`  [_gDW_*_m_^-2]  *Mass_balance*
- DESC: Total_DW_in_system
```
_aDTotT_ = _aDTotTHyp_ + (_oDIMWEpi_+_oDDetWEpi_+_oDDiatWEpi_+_oDGrenWEpi_+_oDBlueWEpi_+_oDZooEpi_) * _uDepthWEpi_ +_aDFish_+_aDPisc_ + _aDGras_ +_aDVeg_ +_aDIMS_+_aDHumS_+_aDDetS_+_aDDiatS_+_aDGrenS_+_aDBlueS_+_aDBent_ + _aDTotM_ + _aDBlueSurf_
```

### `_aNTotT_`  [_gN_*_m_^-2]  *Mass_balance*
- DESC: Total_N_in_system
```
_aNTotT_ = _aNTotTHyp_+ (_oNH4WEpi_+_oNO3WEpi_+_oNDetWEpi_+_oNDiatWEpi_+_oNGrenWEpi_+_oNBlueWEpi_ +_oNZooEpi_)*_uDepthWEpi_ +_aNFish_+_aNPisc_ + _aNGras_ +_aNVeg_ +_aNH4S_+_aNO3S_+_aNDetS_+_aNHumS_+_aNDiatS_+_aNGrenS_+_aNBlueS_ +_aNBent_ + _aNTotM_ + _aNBlueSurf_
```

### `_aPTotT_`  [_gP_*_m_^-2]  *Mass_balance*
- DESC: Total_P_in_system
```
_aPTotT_ = _aPTotTHyp_ + (_oPO4WEpi_+_oPDetWEpi_+_oPDiatWEpi_+_oPGrenWEpi_+_oPBlueWEpi_ +_oPZooEpi_+_oPAIMWEpi_) * _uDepthWEpi_ +_aPFish_+_aPPisc_ + _aPGras_ +_aPVeg_ +_aPO4S_+_aPDetS_+_aPHumS_+_aPDiatS_+_aPGrenS_+_aPBlueS_ +_aPAIMS_+_aPBent_ + _aPTotM_ +_aPBlueSurf_
```

