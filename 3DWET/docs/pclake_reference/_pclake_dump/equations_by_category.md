# PCLake+Gras - All Equations Grouped by Category

Source: `PL613162PLUS_Gras_Mode_order_mass_DC_Run.xls` (derivatives sheet, 2669 equations)

Equation syntax: ACSL (Advanced Continuous Simulation Language). Variables/constants wrapped in `_underscores_`. Operators: `_IF_/_THEN_/_ELSE_/_ENDIF_`, `_POW_`, `_EXP_`, `_MAX_`, `_MIN_`, `_COS_`, `_EQ_`, `_GT_`, `_AND_`, `_OR_`.

---

## Time  (4 equations)

### `_sTime_`  [_d_]
- **Description**: Time
- **Equation**:

```
_sTime_ = _time_ + _DayStart_
```

### `_TimeYears_`  [_y_]
- **Description**: Time_in_years
- **Equation**:

```
_TimeYears_ = _sTime_ / _DaysPerYear_
```

### `_Day_`  [_d_]
- **Description**: Time_(day_number)_within_the_year_(0-365)
- **Equation**:

```
_Day_ = _sTime_ - _FLOOR_(_TimeYears_) * _DaysPerYear_
```

### `_Years_`  [_y_]
- **Description**: Time_in_calendar_years
- **Equation**:

```
_Years_ = _YearZero_ + _TimeYears_
```

## Days  (1 equations)

### `_DaysInYear_`  [_d_]
- **Description**: Days_In_A_Year
- **Equation**:

```
_DaysInYear_ = _DaysPerYear_* 1
```

## Stratification  (1 equations)

### `_aInclStrat_`  [0]
- **Description**: If_T_Include_stratification
- **Equation**:

```
_aInclStrat_ =_IF_ ( _InclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSE_ 1.0 _ENDIF_
```

## Depth  (3 equations)

### `_uDepthMixMeas_`  [_m_]
- **Description**: Mixing_depth
- **Equation**:

```
_uDepthMixMeas_ =_IF_ ( _calcMixDepth_ _EQ_ _TRUE_ ) _THEN_ _cAMix_ * _POW_ ( _cFetch_ _POWOPERATOR_ (_cBMix_) ) _ELSEIF_ (_ReadMixDepth_ _EQ_ _TRUE_) _THEN_ _mMixDepth_ _ELSE_ _cMixDepth_ _ENDIF_
```

### `_uDepthWHyp_`  [_m_]
- **Description**: Total_Depth
- **Equation**:

```
_uDepthWHyp_ =_IF_ ( ( _aInclStrat_ _EQ_ _TRUE_ ) _AND_ ((_uDepthW_ - _sMixDepthW_ ) _GE_ _cMinDepthHypEpi_ ) ) _THEN_ _uDepthW_ - _sMixDepthW_  _ELSE_ _cMinDepthHypEpi_ _ENDIF_
```

### `_uDepthWEpi_`  [_m_]
- **Description**: Total_Depth
- **Equation**:

```
_uDepthWEpi_ =_IF_( ( _aInclStrat_ _EQ_ _TRUE_ ) _AND_ ( _sMixDepthW_ _GE_ _cMinDepthHypEpi_ ) _AND_ ( _uDepthW_ _GE_ _sMixDepthW_ ) ) _THEN_ _sMixDepthW_ _ELSEIF_ ( ( _aInclStrat_ _EQ_ _TRUE_ ) _AND_ ( (_sMixDepthW_ _LE_ _cMinDepthHypEpi_ ) _OR_ (_uDepthW_ _LE_ _cMinDepthHypEpi_ ) ) ) _THEN_ _cMinDepthHypEpi_ _ELSEIF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _uDepthW_ _ELSE_ _uDepthW_ - _uDepthWHyp_ _ENDIF_
```

## state_auxiliary  (149 equations)

### `_uDepthW_`  [_m_]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_uDepthW_= _IF_ _sDepthW_ _GT_ (_cMinDepthHypEpi_ + _cMinDepthHypEpi_) _THEN_ _sDepthW_ _ELSE_ (_cMinDepthHypEpi_ + _cMinDepthHypEpi_) _ENDIF_
```

### `_oNH4WHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNH4WHyp_= _IF_ _sNH4WHyp_ _GT_ _NearZero_ _THEN_ _sNH4WHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNO3WHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNO3WHyp_= _IF_ _sNO3WHyp_ _GT_ _NearZero_ _THEN_ _sNO3WHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPO4WHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPO4WHyp_= _IF_ _sPO4WHyp_ _GT_ _NearZero_ _THEN_ _sPO4WHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPAIMWHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPAIMWHyp_= _IF_ _sPAIMWHyp_ _GT_ _NearZero_ _THEN_ _sPAIMWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiO2WHyp_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiO2WHyp_= _IF_ _sSiO2WHyp_ _GT_ _NearZero_ _THEN_ _sSiO2WHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oO2WHyp_`  [_gO2_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oO2WHyp_= _IF_ _sO2WHyp_ _GT_ _NearZero_ _THEN_ _sO2WHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDetWHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDetWHyp_= _IF_ _sDDetWHyp_ _GT_ _NearZero_ _THEN_ _sDDetWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDetWHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDetWHyp_= _IF_ _sNDetWHyp_ _GT_ _NearZero_ _THEN_ _sNDetWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDetWHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDetWHyp_= _IF_ _sPDetWHyp_ _GT_ _NearZero_ _THEN_ _sPDetWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiDetWHyp_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiDetWHyp_= _IF_ _sSiDetWHyp_ _GT_ _NearZero_ _THEN_ _sSiDetWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDIMWHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDIMWHyp_= _IF_ _sDIMWHyp_ _GT_ _NearZero_ _THEN_ _sDIMWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDiatWHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDiatWHyp_= _IF_ _sDDiatWHyp_ _GT_ _NearZero_ _THEN_ _sDDiatWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDiatWHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDiatWHyp_= _IF_ _sNDiatWHyp_ _GT_ _NearZero_ _THEN_ _sNDiatWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDiatWHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDiatWHyp_= _IF_ _sPDiatWHyp_ _GT_ _NearZero_ _THEN_ _sPDiatWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDGrenWHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDGrenWHyp_= _IF_ _sDGrenWHyp_ _GT_ _NearZero_ _THEN_ _sDGrenWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNGrenWHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNGrenWHyp_= _IF_ _sNGrenWHyp_ _GT_ _NearZero_ _THEN_ _sNGrenWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPGrenWHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPGrenWHyp_= _IF_ _sPGrenWHyp_ _GT_ _NearZero_ _THEN_ _sPGrenWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDBlueWHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDBlueWHyp_= _IF_ _sDBlueWHyp_ _GT_ _NearZero_ _THEN_ _sDBlueWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNBlueWHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNBlueWHyp_= _IF_ _sNBlueWHyp_ _GT_ _NearZero_ _THEN_ _sNBlueWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPBlueWHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPBlueWHyp_= _IF_ _sPBlueWHyp_ _GT_ _NearZero_ _THEN_ _sPBlueWHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDZooHyp_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDZooHyp_= _IF_ _sDZooHyp_ _GT_ _NearZero_ _THEN_ _sDZooHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNZooHyp_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNZooHyp_= _IF_ _sNZooHyp_ _GT_ _NearZero_ _THEN_ _sNZooHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPZooHyp_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPZooHyp_= _IF_ _sPZooHyp_ _GT_ _NearZero_ _THEN_ _sPZooHyp_ / _MassHyp_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDFiAd_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDFiAd_= _IF_ _sDFiAd_ _GT_ _NearZero_ _THEN_ _sDFiAd_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDFiJv_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDFiJv_= _IF_ _sDFiJv_ _GT_ _NearZero_ _THEN_ _sDFiJv_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNFiAd_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNFiAd_= _IF_ _sNFiAd_ _GT_ _NearZero_ _THEN_ _sNFiAd_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNFiJv_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNFiJv_= _IF_ _sNFiJv_ _GT_ _NearZero_ _THEN_ _sNFiJv_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPFiAd_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPFiAd_= _IF_ _sPFiAd_ _GT_ _NearZero_ _THEN_ _sPFiAd_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPFiJv_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPFiJv_= _IF_ _sPFiJv_ _GT_ _NearZero_ _THEN_ _sPFiJv_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDPisc_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDPisc_= _IF_ _sDPisc_ _GT_ _NearZero_ _THEN_ _sDPisc_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDGras_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDGras_= _IF_ _sDGras_ _GT_ _NearZero_ _THEN_ _sDGras_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNH4S_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNH4S_= _IF_ _sNH4S_ _GT_ _NearZero_ _THEN_ _sNH4S_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNO3S_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNO3S_= _IF_ _sNO3S_ _GT_ _NearZero_ _THEN_ _sNO3S_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPO4S_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPO4S_= _IF_ _sPO4S_ _GT_ _NearZero_ _THEN_ _sPO4S_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPAIMS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPAIMS_= _IF_ _sPAIMS_ _GT_ _NearZero_ _THEN_ _sPAIMS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDDetS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDDetS_= _IF_ _sDDetS_ _GT_ _NearZero_ _THEN_ _sDDetS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNDetS_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNDetS_= _IF_ _sNDetS_ _GT_ _NearZero_ _THEN_ _sNDetS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPDetS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPDetS_= _IF_ _sPDetS_ _GT_ _NearZero_ _THEN_ _sPDetS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aSiDetS_`  [_gSi_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aSiDetS_= _IF_ _sSiDetS_ _GT_ _NearZero_ _THEN_ _sSiDetS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDHumS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDHumS_= _IF_ _sDHumS_ _GT_ _NearZero_ _THEN_ _sDHumS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNHumS_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNHumS_= _IF_ _sNHumS_ _GT_ _NearZero_ _THEN_ _sNHumS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPHumS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPHumS_= _IF_ _sPHumS_ _GT_ _NearZero_ _THEN_ _sPHumS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDIMS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDIMS_= _IF_ _sDIMS_ _GT_ _NearZero_ _THEN_ _sDIMS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDDiatS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDDiatS_= _IF_ _sDDiatS_ _GT_ _NearZero_ _THEN_ _sDDiatS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNDiatS_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNDiatS_= _IF_ _sNDiatS_ _GT_ _NearZero_ _THEN_ _sNDiatS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPDiatS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPDiatS_= _IF_ _sPDiatS_ _GT_ _NearZero_ _THEN_ _sPDiatS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDGrenS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDGrenS_= _IF_ _sDGrenS_ _GT_ _NearZero_ _THEN_ _sDGrenS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNGrenS_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNGrenS_= _IF_ _sNGrenS_ _GT_ _NearZero_ _THEN_ _sNGrenS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPGrenS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPGrenS_= _IF_ _sPGrenS_ _GT_ _NearZero_ _THEN_ _sPGrenS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDBlueS_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDBlueS_= _IF_ _sDBlueS_ _GT_ _NearZero_ _THEN_ _sDBlueS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNBlueS_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNBlueS_= _IF_ _sNBlueS_ _GT_ _NearZero_ _THEN_ _sNBlueS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPBlueS_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPBlueS_= _IF_ _sPBlueS_ _GT_ _NearZero_ _THEN_ _sPBlueS_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDVeg_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDVeg_= _IF_ _sDVeg_ _GT_ _NearZero_ _THEN_ _sDVeg_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNVeg_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNVeg_= _IF_ _sNVeg_ _GT_ _NearZero_ _THEN_ _sNVeg_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPVeg_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPVeg_= _IF_ _sPVeg_ _GT_ _NearZero_ _THEN_ _sPVeg_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aVegHeight_`  [_m_]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aVegHeight_= _IF_ _sVegHeight_ _GT_ _NearZero_ _THEN_ _sVegHeight_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDBent_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDBent_= _IF_ _sDBent_ _GT_ _NearZero_ _THEN_ _sDBent_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNBent_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNBent_= _IF_ _sNBent_ _GT_ _NearZero_ _THEN_ _sNBent_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPBent_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPBent_= _IF_ _sPBent_ _GT_ _NearZero_ _THEN_ _sPBent_ _ELSE_ _NearZero_ _ENDIF_
```

### `_uDepthWM_`  [_m_]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_uDepthWM_= _IF_ _sDepthWM_ _GT_ _NearZero_ _THEN_ _sDepthWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNH4WM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNH4WM_= _IF_ _sNH4WM_ _GT_ _NearZero_ _THEN_ _sNH4WM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNO3WM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNO3WM_= _IF_ _sNO3WM_ _GT_ _NearZero_ _THEN_ _sNO3WM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPO4WM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPO4WM_= _IF_ _sPO4WM_ _GT_ _NearZero_ _THEN_ _sPO4WM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPAIMWM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPAIMWM_= _IF_ _sPAIMWM_ _GT_ _NearZero_ _THEN_ _sPAIMWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiO2WM_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiO2WM_= _IF_ _sSiO2WM_ _GT_ _NearZero_ _THEN_ _sSiO2WM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oO2WM_`  [_gO2_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oO2WM_= _IF_ _sO2WM_ _GT_ _NearZero_ _THEN_ _sO2WM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDetWM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDetWM_= _IF_ _sDDetWM_ _GT_ _NearZero_ _THEN_ _sDDetWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDetWM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDetWM_= _IF_ _sNDetWM_ _GT_ _NearZero_ _THEN_ _sNDetWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDetWM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDetWM_= _IF_ _sPDetWM_ _GT_ _NearZero_ _THEN_ _sPDetWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiDetWM_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiDetWM_= _IF_ _sSiDetWM_ _GT_ _NearZero_ _THEN_ _sSiDetWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDIMWM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDIMWM_= _IF_ _sDIMWM_ _GT_ _NearZero_ _THEN_ _sDIMWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDiatWM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDiatWM_= _IF_ _sDDiatWM_ _GT_ _NearZero_ _THEN_ _sDDiatWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDiatWM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDiatWM_= _IF_ _sNDiatWM_ _GT_ _NearZero_ _THEN_ _sNDiatWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDiatWM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDiatWM_= _IF_ _sPDiatWM_ _GT_ _NearZero_ _THEN_ _sPDiatWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDGrenWM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDGrenWM_= _IF_ _sDGrenWM_ _GT_ _NearZero_ _THEN_ _sDGrenWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNGrenWM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNGrenWM_= _IF_ _sNGrenWM_ _GT_ _NearZero_ _THEN_ _sNGrenWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPGrenWM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPGrenWM_= _IF_ _sPGrenWM_ _GT_ _NearZero_ _THEN_ _sPGrenWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDBlueWM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDBlueWM_= _IF_ _sDBlueWM_ _GT_ _NearZero_ _THEN_ _sDBlueWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNBlueWM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNBlueWM_= _IF_ _sNBlueWM_ _GT_ _NearZero_ _THEN_ _sNBlueWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPBlueWM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPBlueWM_= _IF_ _sPBlueWM_ _GT_ _NearZero_ _THEN_ _sPBlueWM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDZooM_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDZooM_= _IF_ _sDZooM_ _GT_ _NearZero_ _THEN_ _sDZooM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNZooM_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNZooM_= _IF_ _sNZooM_ _GT_ _NearZero_ _THEN_ _sNZooM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPZooM_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPZooM_= _IF_ _sPZooM_ _GT_ _NearZero_ _THEN_ _sPZooM_ / _MassWM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNH4SM_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNH4SM_= _IF_ _sNH4SM_ _GT_ _NearZero_ _THEN_ _sNH4SM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNO3SM_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNO3SM_= _IF_ _sNO3SM_ _GT_ _NearZero_ _THEN_ _sNO3SM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPO4SM_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPO4SM_= _IF_ _sPO4SM_ _GT_ _NearZero_ _THEN_ _sPO4SM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPAIMSM_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPAIMSM_= _IF_ _sPAIMSM_ _GT_ _NearZero_ _THEN_ _sPAIMSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDDetSM_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDDetSM_= _IF_ _sDDetSM_ _GT_ _NearZero_ _THEN_ _sDDetSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNDetSM_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNDetSM_= _IF_ _sNDetSM_ _GT_ _NearZero_ _THEN_ _sNDetSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPDetSM_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPDetSM_= _IF_ _sPDetSM_ _GT_ _NearZero_ _THEN_ _sPDetSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aSiDetSM_`  [_gSi_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aSiDetSM_= _IF_ _sSiDetSM_ _GT_ _NearZero_ _THEN_ _sSiDetSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDHumSM_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDHumSM_= _IF_ _sDHumSM_ _GT_ _NearZero_ _THEN_ _sDHumSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNHumSM_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNHumSM_= _IF_ _sNHumSM_ _GT_ _NearZero_ _THEN_ _sNHumSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPHumSM_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPHumSM_= _IF_ _sPHumSM_ _GT_ _NearZero_ _THEN_ _sPHumSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDIMSM_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDIMSM_= _IF_ _sDIMSM_ _GT_ _NearZero_ _THEN_ _sDIMSM_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDRootPhra_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDRootPhra_= _IF_ _sDRootPhra_ _GT_ _NearZero_ _THEN_ _sDRootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDShootPhra_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDShootPhra_= _IF_ _sDShootPhra_ _GT_ _NearZero_ _THEN_ _sDShootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNRootPhra_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNRootPhra_= _IF_ _sNRootPhra_ _GT_ _NearZero_ _THEN_ _sNRootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNShootPhra_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNShootPhra_= _IF_ _sNShootPhra_ _GT_ _NearZero_ _THEN_ _sNShootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPRootPhra_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPRootPhra_= _IF_ _sPRootPhra_ _GT_ _NearZero_ _THEN_ _sPRootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPShootPhra_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPShootPhra_= _IF_ _sPShootPhra_ _GT_ _NearZero_ _THEN_ _sPShootPhra_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNH4WEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNH4WEpi_= _IF_ _sNH4WEpi_ _GT_ _NearZero_ _THEN_ _sNH4WEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNO3WEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNO3WEpi_= _IF_ _sNO3WEpi_ _GT_ _NearZero_ _THEN_ _sNO3WEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPO4WEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPO4WEpi_= _IF_ _sPO4WEpi_ _GT_ _NearZero_ _THEN_ _sPO4WEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPAIMWEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPAIMWEpi_= _IF_ _sPAIMWEpi_ _GT_ _NearZero_ _THEN_ _sPAIMWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiO2WEpi_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiO2WEpi_= _IF_ _sSiO2WEpi_ _GT_ _NearZero_ _THEN_ _sSiO2WEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oO2WEpi_`  [_gO2_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oO2WEpi_= _IF_ _sO2WEpi_ _GT_ _NearZero_ _THEN_ _sO2WEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDetWEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDetWEpi_= _IF_ _sDDetWEpi_ _GT_ _NearZero_ _THEN_ _sDDetWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDetWEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDetWEpi_= _IF_ _sNDetWEpi_ _GT_ _NearZero_ _THEN_ _sNDetWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDetWEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDetWEpi_= _IF_ _sPDetWEpi_ _GT_ _NearZero_ _THEN_ _sPDetWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oSiDetWEpi_`  [_gSi_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oSiDetWEpi_= _IF_ _sSiDetWEpi_ _GT_ _NearZero_ _THEN_ _sSiDetWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDIMWEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDIMWEpi_= _IF_ _sDIMWEpi_ _GT_ _NearZero_ _THEN_ _sDIMWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDDiatWEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDDiatWEpi_= _IF_ _sDDiatWEpi_ _GT_ _NearZero_ _THEN_ _sDDiatWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNDiatWEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNDiatWEpi_= _IF_ _sNDiatWEpi_ _GT_ _NearZero_ _THEN_ _sNDiatWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPDiatWEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPDiatWEpi_= _IF_ _sPDiatWEpi_ _GT_ _NearZero_ _THEN_ _sPDiatWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDGrenWEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDGrenWEpi_= _IF_ _sDGrenWEpi_ _GT_ _NearZero_ _THEN_ _sDGrenWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNGrenWEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNGrenWEpi_= _IF_ _sNGrenWEpi_ _GT_ _NearZero_ _THEN_ _sNGrenWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPGrenWEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPGrenWEpi_= _IF_ _sPGrenWEpi_ _GT_ _NearZero_ _THEN_ _sPGrenWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDBlueWEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDBlueWEpi_= _IF_ _sDBlueWEpi_ _GT_ _NearZero_ _THEN_ _sDBlueWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNBlueWEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNBlueWEpi_= _IF_ _sNBlueWEpi_ _GT_ _NearZero_ _THEN_ _sNBlueWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPBlueWEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPBlueWEpi_= _IF_ _sPBlueWEpi_ _GT_ _NearZero_ _THEN_ _sPBlueWEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oDZooEpi_`  [_gDW_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oDZooEpi_= _IF_ _sDZooEpi_ _GT_ _NearZero_ _THEN_ _sDZooEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oNZooEpi_`  [_gN_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oNZooEpi_= _IF_ _sNZooEpi_ _GT_ _NearZero_ _THEN_ _sNZooEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_oPZooEpi_`  [_gP_*_m_^-3]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_oPZooEpi_= _IF_ _sPZooEpi_ _GT_ _NearZero_ _THEN_ _sPZooEpi_ / _MassEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDBlueSurf_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDBlueSurf_= _IF_ _sDBlueSurf_ _GT_ _NearZero_ _THEN_ _sDBlueSurf_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNBlueSurf_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNBlueSurf_= _IF_ _sNBlueSurf_ _GT_ _NearZero_ _THEN_ _sNBlueSurf_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aPBlueSurf_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPBlueSurf_= _IF_ _sPBlueSurf_ _GT_ _NearZero_ _THEN_ _sPBlueSurf_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aDExtTotT_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDExtTotT_= _sDExtTotT_
```

### `_aNExtTotT_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNExtTotT_= _sNExtTotT_
```

### `_aPExtTotT_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPExtTotT_=  _sPExtTotT_
```

### `_aSiExtTotT_`  [_gSi_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aSiExtTotT_= _sSiExtTotT_
```

### `_aO2ExtTotT_`  [_gO2_*m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aO2ExtTotT_=_sO2ExtTotT_
```

### `_aDepthExtTotT_`  [_m_]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDepthExtTotT_=_sDepthExtTotT_
```

### `_aDDetWEpi_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDDetWEpi_= _IF_ _sDDetWEpi_ _GT_ _NearZero_ _THEN_ _sDDetWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNDetWEpi_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNDetWEpi_= _IF_ _sNDetWEpi_ _GT_ _NearZero_ _THEN_ _sNDetWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aPDetWEpi_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPDetWEpi_= _IF_ _sPDetWEpi_ _GT_ _NearZero_ _THEN_ _sPDetWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aSiDetWEpi_`  [_gSi_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aSiDetWEpi_= _IF_ _sSiDetWEpi_ _GT_ _NearZero_ _THEN_ _sSiDetWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDIMWEpi_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDIMWEpi_= _IF_ _sDIMWEpi_ _GT_ _NearZero_ _THEN_ _aDIMWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aDDiatWEpi_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDDiatWEpi_= _IF_ _sDDiatWEpi_ _GT_ _NearZero_ _THEN_ _sDDiatWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNDiatWEpi_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNDiatWEpi_= _IF_ _sNDiatWEpi_ _GT_ _NearZero_ _THEN_ _sNDiatWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aPDiatWEpi_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPDiatWEpi_= _IF_ _sPDiatWEpi_ _GT_ _NearZero_ _THEN_ _sPDiatWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aDGrenWEpi_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDGrenWEpi_= _IF_ _sDGrenWEpi_ _GT_ _NearZero_ _THEN_ _sDGrenWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNGrenWEpi_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNGrenWEpi_= _IF_ _sNGrenWEpi_ _GT_ _NearZero_ _THEN_ _sNGrenWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aPGrenWEpi_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPGrenWEpi_= _IF_ _sPGrenWEpi_ _GT_ _NearZero_ _THEN_ _sPGrenWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDBlueWEpi_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDBlueWEpi_= _IF_ _sDBlueWEpi_ _GT_ _NearZero_ _THEN_ _sDBlueWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aNBlueWEpi_`  [_gN_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aNBlueWEpi_= _IF_ _sNBlueWEpi_ _GT_ _NearZero_ _THEN_ _sNBlueWEpi_  _ELSE_ _NearZero_ _ENDIF_
```

### `_aPBlueWEpi_`  [_gP_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aPBlueWEpi_= _IF_ _sPBlueWEpi_ _GT_ _NearZero_ _THEN_ _sPBlueWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

### `_aDBlueWHyp_`  [_gDW_*_m_^-2]
- **Description**: state_auxiliary_with_error_catching
- **Equation**:

```
_aDBlueWHyp_= _IF_ _sDBlueWEpi_ _GT_ _NearZero_ _THEN_ _sDBlueWEpi_ _ELSE_ _NearZero_ _ENDIF_
```

## Conversion_factor_from_concentration_to_mass  (3 equations)

### `_MassHyp_`  [_m_]
- **Description**: Conversion_factor_from_concentration_to_mass
- **Equation**:

```
_MassHyp_ = _IF_ _CalcMass_ _EQ_ _TRUE_ _THEN_ _uDepthWHyp_ _ELSE_ 1.0 _ENDIF_
```

### `_MassEpi_`  [_m_]
- **Description**: Conversion_factor_from_concentration_to_mass
- **Equation**:

```
_MassEpi_ = _IF_ _CalcMass_ _EQ_ _TRUE_ _THEN_ _uDepthWEpi_ _ELSE_ 1.0 _ENDIF_
```

### `_MassWM_`  [_m_]
- **Description**: Conversion_factor_from_concentration_to_mass
- **Equation**:

```
_MassWM_ = _IF_ _CalcMass_ _EQ_ _TRUE_ _THEN_ _sDepthWM_ _ELSE_ 1.0 _ENDIF_
```

## Vegetation  (11 equations)

### `_aVegEHeight_`  [_m_]
- **Description**: Vegetation_height_based_on_empirical_biomass_length_relationship_of_Haga_2007
- **Equation**:

```
_aVegEHeight_ =   _POW_ ( _cVegHPar1_*_aDVeg_ _POWOPERATOR_ _cVegHPar2_ )
```

### `_uVegHeight_`  [_m_]
- **Description**: Vegetation_height
- **Equation**:

```
_uVegHeight_ =  _IF_ ( _UseVegHeight_ _EQ_ _FALSE_ _AND_  _aVegHeight_ _LT_ _uDepthW_ ) _THEN_ _aVegHeight_ _ELSEIF_ ( _UseVegHeight_ _EQ_ _FALSE_ ) _THEN_ ( _uDepthW_ ) _ELSE_ _MIN_ ( _aVegHeight_ , _uDepthW_ , _aVegEHeight_ ) _ENDIF_
```

### `_uVegHeightHyp_`  [_m_]
- **Description**: Vegetation_height_hyp
- **Equation**:

```
_uVegHeightHyp_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uVegHeight_ _GT_ _uDepthWHyp_ ) _THEN_ _uDepthWHyp_ _ELSE_ _uVegHeight_ _ENDIF_
```

### `_uVegHeightEpi_`  [_m_]
- **Description**: Vegetation_height_epi
- **Equation**:

```
_uVegHeightEpi_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_ _AND_ _uVegHeight_ _LT_ _uDepthWEpi_ ) _THEN_ _uVegHeight_ _ELSEIF_ ( _aInclStrat_ _EQ_ _FALSE_ _AND_ _uVegHeight_ _GE_ _uDepthWEpi_ ) _THEN_ _uDepthWEpi_ _ELSEIF_ (_uVegHeight_ _GT_ _uDepthWHyp_ ) _THEN_ _uVegHeight_ -_uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uVegHeightLight_`  [_m_]
- **Description**: Vegetation_height_epi
- **Equation**:

```
_uVegHeightLight_ = _cVegL_ *_LN_( 1.0 + _uVegHeight_ )
```

### `_uVegHeightLightSum_`  [_m_]
- **Description**: Vegetation_height_epi
- **Equation**:

```
_uVegHeightLightSum_ = _cVegL_ *_LN_( 1.0 + _MAX_ (_uVegHeight_, _MIN_ (_uDepthW_, _cVegHeight_) ) )
```

### `_uVegHeightLightEpi_`  [_m_]
- **Description**: Vegetation_Light
- **Equation**:

```
_uVegHeightLightEpi_ = _IF_ (  _uVegHeightLight_ _GT_ _uVegHeightEpi_ ) _THEN_ _uVegHeightEpi_ _ELSE_ _uVegHeightLight_ _ENDIF_
```

### `_uVegHeightLightHyp_`  [_m_]
- **Description**: Vegetation_Light
- **Equation**:

```
_uVegHeightLightHyp_ =  _uVegHeightLight_ - _uVegHeightLightEpi_
```

### `_uDVegHyp_`  [_gDW_*_m_^-2]
- **Description**: Vegetation_biomass_hyp
- **Equation**:

```
_uDVegHyp_ = _uVegHeightHyp_ / _uVegHeight_ * _aDVeg_
```

### `_uDVegEpi_`  [_gDW_*_m_^-2]
- **Description**: Vegetation_biomass_epi
- **Equation**:

```
_uDVegEpi_ = _uVegHeightEpi_ / _uVegHeight_ * _aDVeg_
```

### `_uVegShade_`  [0]
- **Description**: Vegetation_shading_factor
- **Equation**:

```
_uVegShade_ = _IF_ ( _ReadVegShade_  _EQ_  _TRUE_) _THEN_ _mVegShade_ _ELSE_ _fVegShade_ _ENDIF_
```

## Vegetation_processes  (205 equations)

### `_aDepth2VegHyp_`  [_m_]
- **Description**: Lower_depth_of_vegetation_layer_(maximum_=_water_depth)
- **Equation**:

```
_aDepth2VegHyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ _fDepth2Veg_ _GE_ 1 ) _THEN_ _uDepthWHyp_  _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ _fDepth2Veg_ _LT_ 1 ) _THEN_ _MAX_ (0.0, _uVegHeight_ - _uDepthWEpi_ ) _ELSE_ 0.0 _ENDIF_
```

### `_aDepth1VegHyp_`  [_m_]
- **Description**: Upper_depth_of_vegetation_layer_(minimum_=_0_m_=_surface)
- **Equation**:

```
_aDepth1VegHyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ _fDepth2Veg_ _GE_ 1 ) _THEN_ _uDepthWHyp_ - _uVegHeightHyp_  _ELSE_ 0.0 _ENDIF_
```

### `_aDepth2VegEpi_`  [_m_]
- **Description**: Lower_depth_of_vegetation_layer_(maximum_=_water_depth)
- **Equation**:

```
_aDepth2VegEpi_ = _IF_ (_fDepth2Veg_ _GE_ 1 ) _THEN_ _uDepthWEpi_ _ELSE_ _uDepthWEpi_ - _uVegHeightEpi_ _ENDIF_
```

### `_aDepth1VegEpi_`  [_m_]
- **Description**: Upper_depth_of_vegetation_layer_(minimum_=_0_m_=_surface)
- **Equation**:

```
_aDepth1VegEpi_ = _IF_ (_fDepth2Veg_ _GE_ 1 ) _THEN_ _uDepthWEpi_ - _uVegHeightEpi_  _ELSE_ 0.0 _ENDIF_
```

### `_aLPARBotEpiOpen_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_bottom_of_Epi
- **Equation**:

```
_aLPARBotEpiOpen_ = _aLPARBotSurf_ * _EXP_(- _aExtCoefOpenEpi_ * _uDepthWEpi_)
```

### `_aLPARBotHypOpen_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_bottom_of_Epi
- **Equation**:

```
_aLPARBotHypOpen_ = _aLPARBotEpiOpen_ * _EXP_(- _aExtCoefOpenHyp_ * _uDepthWHyp_)
```

### `_aLPAR1VegEpi_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_top_of_vegetation_layer
- **Equation**:

```
_aLPAR1VegEpi_ = _aLPARBotSurf_ * _EXP_(- _aExtCoefOpenEpi_ * _aDepth1VegEpi_) * ( 1 - _uVegShade_ )
```

### `_aLPAR1VegHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_top_of_vegetation_layer
- **Equation**:

```
_aLPAR1VegHyp_ = _aLPAR1VegEpi_ * _EXP_(- _aExtCoefOpenHyp_ * _aDepth1VegHyp_)
```

### `_aLPARVegLight_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_bottom_of_Epi
- **Equation**:

```
_aLPARVegLight_ =  _IF_  ( _aInclStrat_ _EQ_ _TRUE_ _AND_  _uVegHeight_ _LE_ _uDepthWHyp_ ) _THEN_ _aLPAR1VegHyp_ *   _EXP_(- _aExtCoefOpenHyp_ * _uVegHeightLightEpi_) _ELSE_ _aLPAR1VegEpi_ *  _EXP_(- _aExtCoefOpenEpi_ * _uVegHeightLightEpi_)  *  _EXP_(- _aExtCoefOpenHyp_ * _uVegHeightLightEpi_) _ENDIF_
```

### `_uTmVegAve_`  [_oC_]
- **Description**: Average_temperature_for_vegetation
- **Equation**:

```
_uTmVegAve_ = ( _uVegHeightHyp_ * _uTmHyp_ + _uVegHeightEpi_ * _uTmEpi_ ) / _uVegHeight_
```

### `_uFunTmVeg_`  [0]
- **Description**: Temperature_function_of_growth_vegetation
- **Equation**:

```
_uFunTmVeg_ = _EXP_(-0.5/(_cSigTmVeg_*_cSigTmVeg_) *((_uTmVegAve_-_cTmOptVeg_)*(_uTmVegAve_-_cTmOptVeg_) - (_cTmRef_-_cTmOptVeg_)*(_cTmRef_-_cTmOptVeg_)))
```

### `_uFunTmProdVeg_`  [0]
- **Description**: Temperature_function_of_vegetation_production
- **Equation**:

```
_uFunTmProdVeg_ = _IF_ ( _UseExpVeg_ _EQ_ _TRUE_ ) _THEN_ _uFunTmVeg_ _ELSE_ _POW_ ( _cQ10ProdVeg_ _POWOPERATOR_ (0.1 * (_uTmVegAve_ - _cTmRef_))) _ENDIF_
```

### `_uhLVeg_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Half-sat_light_for_vegetation_production_at_current_temp
- **Equation**:

```
_uhLVeg_ = _hLRefVeg_ * _uFunTmProdVeg_
```

### `_aLPIVeg_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Integrated_PI_curve_over_depth_for_vegetation
- **Equation**:

```
_aLPIVeg_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_  _uVegHeight_ _GT_ _uDepthWHyp_ ) _THEN_ _cPMax_*(_aLPAR1VegEpi_- _aLPARVegLight_ + _uhLVeg_*_LN_((1.0 +_aLPARVegLight_/ _uhLVeg_)  /(1.0 +_aLPAR1VegEpi_  / _uhLVeg_) + _NearZero_  ) )_ELSEIF_  ( _aInclStrat_ _EQ_ _TRUE_ _AND_  _uVegHeight_ _LE_ _uDepthWHyp_ ) _THEN_ _cPMax_*( _aLPAR1VegHyp_- _aLPARVegLight_ + _uhLVeg_* _LN_((1.0 +_aLPARVegLight_/ _uhLVeg_)  / (1.0 +_aLPAR1VegHyp_  / _uhLVeg_) ) ) _ELSE_ _cPMax_ * (_aLPAR1VegEpi_- _aLPARVegLight_ + _uhLVeg_*_LN_((1.0 +_aLPARVegLight_/ _uhLVeg_)  /(1.0 +_aLPAR1VegEpi_  / _uhLVeg_) + _NearZero_  ) )_ENDIF_
```

### `_aSpring_`  [_d_]
- **Description**: Day_at_which_plants_change_strategy_towards_overwintering
- **Equation**:

```
_aSpring_ =  _IF_ ( _cLAT_ _LT_ 0 _AND_ _Day_ _GE_ 265 _AND_ _Day_ _LE_ 356 ) _THEN_ 1 _ELSEIF_ ( _cLAT_ _GT_ 0 _AND_ _Day_ _GE_ 80 _AND_ _Day_ _LE_ 173) _THEN_ 1 _ELSEIF_ ( _cLAT_ _EQ_ 0) _THEN_ 1 _ELSE_ 0 _ENDIF_
```

### `_aTimeWinVeg_`  [_d_]
- **Description**: Day_at_which_plants_change_strategy_towards_overwintering
- **Equation**:

```
_aTimeWinVeg_ =  _IF_ ( _sTime_ _LT_ _StartTime_ + 1.0 ) _THEN_ -999 _ELSEIF_ ( _UsePhotVeg_ _EQ_ _FALSE_  _AND_  ( _uTmBot_ _GE_ _cTmInitVeg_ )  _AND_ _aSpring_ _EQ_ 1 ) _THEN_ _sTime_  _ELSEIF_ (_UsePhotVeg_ _EQ_ _TRUE_  _AND_  _uSunHours_ _GE_ _cPhotInitVeg_   _AND_ _aSpring_ _EQ_ 1 ) _THEN_ _sTime_ _ELSEIF_ (( _aLPIVeg_ / _uVegHeightLight_ )_LE_ _cLAlloVeg_ ) _THEN_ _aTimeWinVeg_ _ELSEIF_ (_FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeWinVeg_ + 0.3) _GT_ 1 _AND_ _FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeWinVeg_ + 0.3) _LT_ _cVegWinLen_ ) _THEN_ _aTimeWinVeg_ _ELSE_ _sTime_ _ENDIF_
```

### `_aTimeInitVeg_`  [_d_]
- **Description**: Counter_for_start_off_plant_growth_in_summer
- **Equation**:

```
_aTimeInitVeg_ =  _IF_ ( _sTime_ _LT_ _StartTime_ + 1.0 ) _THEN_ -999 _ELSEIF_ ( _FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeWinVeg_ + 0.3) _GT_ 1 ) _THEN_ _sTime_ _ELSEIF_ ( _UsePhotVeg_ _EQ_ _FALSE_  _AND_  _uTmBot_ _GE_ _cTmInitVeg_ ) _THEN_ _aTimeInitVeg_ _ELSEIF_ ( _UsePhotVeg_ _EQ_ _TRUE_  _AND_    _uSunHours_ _GE_ _cPhotInitVeg_  ) _THEN_ _aTimeInitVeg_ _ELSEIF_ (_UsePhotVeg_ _EQ_ _FALSE_  _AND_  _uTmBot_ _LT_ _cTmInitVeg_ _AND_ ( ( _aLPIVeg_ / _uVegHeightLight_ ) _GE_ _cLAlloVeg_ ) _AND_ _FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeInitVeg_ + 0.3) _GT_ 1) _THEN_ _aTimeInitVeg_ _ELSEIF_ (_UsePhotVeg_ _EQ_ _TRUE_  _AND_   _uSunHours_ _LT_ _cPhotInitVeg_ _AND_ ( ( _aLPIVeg_ / _uVegHeightLight_ ) _GE_ _cLAlloVeg_ ) _AND_ _FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeInitVeg_ + 0.3) _GT_ 1) _THEN_ _aTimeInitVeg_ _ELSEIF_ (_FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeInitVeg_ + 0.3) _GT_ 1 _AND_ _FLOOR_ ( _sTime_+ 0.3 ) - _FLOOR_ (_aTimeInitVeg_ + 0.3) _LT_ _cVegInitLen_ ) _THEN_ _aTimeInitVeg_ _ELSE_ _sTime_ _ENDIF_
```

### `_aTimeWinVegCor_`  [_d_]
- **Description**: Counter_for_termination_of_plant_growth_in_winter_corrected_for_backward_compatibility
- **Equation**:

```
_aTimeWinVegCor_ = _IF_ ( _UseLWinVeg_ _LE_ _NearZero_ ) _THEN_ _FLOOR_ (_TimeYears_ - 1) + _cDayWinVeg_  _ELSE_ _aTimeWinVeg_ _ENDIF_
```

### `_aDayInitVeg_`  [_d_]
- **Description**: Initial_growth_only_once_a_year
- **Equation**:

```
_aDayInitVeg_ = _IF_ (_Day_ _LT_ 1.0 _OR_ _sTime_ _LT_ _StartTime_ + 1.0) _THEN_ 367 _ELSEIF_ (_uTmBot_ _GE_ _cTmInitVeg_ _AND_ _aDayInitVeg_ _GT_ 366) _THEN_ _Day_ _ELSE_ _aDayInitVeg_ _ENDIF_
```

### `_aTimeInitVegCor_`  [_d_]
- **Description**: Counter_for_start_off_plant_growth_in_summer_corrected_for_backward_compatibility
- **Equation**:

```
_aTimeInitVegCor_ = _IF_ (_UsePhotVeg_ _LE_ _NearZero_ _AND_ _UseLWinVeg_ _LE_ _NearZero_ ) _THEN_  (_TimeYears_ - 1)  + _aDayInitVeg_  _ELSE_ _aTimeInitVeg_ _ENDIF_
```

### `_aVegSum_`  [0]
- **Description**: Switch_showing_if_plant_is_in_summer_mode
- **Equation**:

```
_aVegSum_ =  _IF_ ( _FLOOR_ ( _aTimeInitVegCor_ + 0.3) _LT_ _FLOOR_ (  _sTime_ + 0.3 ) _AND_ _FLOOR_ ( _aTimeWinVegCor_ + 0.3 ) _EQ_ _FLOOR_ (  _sTime_  + 0.3 ) ) _THEN_ 1 _ELSE_ 0 _ENDIF_
```

### `_aVegWin_`  [0]
- **Description**: Switch_showing_if_plant_is_in_winter_mode
- **Equation**:

```
_aVegWin_ =  1 - _aVegSum_
```

### `_aDaysVegSum_`  [_d_]
- **Description**: Days_that_plants_have_been_in_summer_mode
- **Equation**:

```
_aDaysVegSum_ = ( _FLOOR_ ( _sTime_+ 0.3) - _FLOOR_ (_aTimeInitVegCor_ + 0.3) ) * _aVegSum_
```

### `_aDaysVegWin_`  [_d_]
- **Description**: Days_that_plants_have_been_in_winter_mode
- **Equation**:

```
_aDaysVegWin_ = ( _FLOOR_ ( _sTime_ + 0.3) - _FLOOR_ ( _aTimeWinVegCor_  + 0.3 )  ) * _aVegWin_
```

### `_bfRootVeg_`  [_gDW_*_gDW_^-1]
- **Description**: Setting_root_fraction
- **Equation**:

```
_bfRootVeg_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _fRootVegSum_ _ELSEIF_ (_aVegWin_ _EQ_ _TRUE_ _AND_ _aDaysVegWin_ _GT_ _cLengAllo_) _THEN_ _fRootVegWin_ _ELSEIF_ (_aVegSum_ _EQ_ _TRUE_ _AND_ _aDaysVegSum_ _LE_ _cLengAllo_) _THEN_ 0.5*(_fRootVegWin_ + _fRootVegSum_) + 0.5*(_fRootVegWin_ - _fRootVegSum_) * _COS_ ( _Pi_ /_cLengAllo_ * ( _sTime_ - _aTimeInitVegCor_ )) _ELSEIF_ ( _aVegWin_ _EQ_ _TRUE_ _AND_ _aDaysVegWin_ _EQ_ 0) _THEN_ _fRootVegWin_ _ELSEIF_ ( _aVegWin_ _EQ_ _TRUE_) _THEN_ 0.5*( _fRootVegWin_ + _fRootVegSum_) - 0.5*( _fRootVegWin_ - _fRootVegSum_) * _COS_ ( _Pi_ / _cLengAllo_ * ( _sTime_ - _aTimeWinVegCor_ )) _ELSE_ _fRootVegSum_ _ENDIF_
```

### `_bfShootVeg_`  [0]
- **Description**: Shoot_fraction
- **Equation**:

```
_bfShootVeg_ = 1.0 - _bfRootVeg_
```

### `_aDShootVeg_`  [_gDW_*_m_^-2]
- **Description**: Shoot_biomass
- **Equation**:

```
_aDShootVeg_ = _bfShootVeg_ * _aDVeg_
```

### `_aDEmergVeg_`  [_gDW_*_m_^-2]
- **Description**: Emergent_biomass
- **Equation**:

```
_aDEmergVeg_ = _fEmergVeg_ * _aDShootVeg_
```

### `_aDFloatVeg_`  [_gDW_*_m_^-2]
- **Description**: Floating_biomass
- **Equation**:

```
_aDFloatVeg_ = _IF_  ( _aDepth1VegEpi_ _LT_ 0.005 ) _THEN_ _fFloatVeg_ * _aDShootVeg_ _ELSE_ 0 _ENDIF_
```

### `_bfSubVeg_`  [0]
- **Description**: Submerged_fraction_of_shoot
- **Equation**:

```
_bfSubVeg_ = 1.0 - _fFloatVeg_ - _fEmergVeg_
```

### `_aDSubVeg_`  [_gDW_*_m_^-2]
- **Description**: Submerged_biomass
- **Equation**:

```
_aDSubVeg_ = _bfSubVeg_ * _aDShootVeg_
```

### `_aExtVegHyp_`  [_m_^-1]
- **Description**: Contribution_of_plant_species_to_extinction_(submerged)
- **Equation**:

```
_aExtVegHyp_ = _cExtSpVeg_ * _aDSubVeg_ / _uDepthWHyp_ * (_uVegHeightHyp_ /_uDepthW_ )
```

### `_aExtCoefHyp_`  [_m_^-1]
- **Description**: Extinction_coefficient_incl_vegetation
- **Equation**:

```
_aExtCoefHyp_ = _aExtCoefOpenHyp_ + _aExtVegHyp_
```

### `_aExtVegEpi_`  [_m_^-1]
- **Description**: Contribution_of_plant_species_to_extinction_(submerged)
- **Equation**:

```
_aExtVegEpi_ = _cExtSpVeg_ * _aDSubVeg_ / _uDepthWEpi_ * (_uVegHeightEpi_ /_uDepthW_ )
```

### `_aExtCoefEpi_`  [_m_^-1]
- **Description**: Extinction_coefficient_incl_vegetation
- **Equation**:

```
_aExtCoefEpi_ = _aExtCoefOpenEpi_ + _aExtVegEpi_
```

### `_aLPARBotEpi_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_bottom_of_Epi
- **Equation**:

```
_aLPARBotEpi_ = _aLPARBotSurf_ * _EXP_(- _aExtCoefEpi_ * _uDepthWEpi_)
```

### `_aLPAR2VegEpi_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_bottom_of_vegetation_layer
- **Equation**:

```
_aLPAR2VegEpi_ = _aLPAR1VegEpi_ * _EXP_(- _aExtCoefEpi_ * (_aDepth2VegEpi_ - _aDepth1VegEpi_))
```

### `_aLPAR2VegHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_bottom_of_vegetation_layer
- **Equation**:

```
_aLPAR2VegHyp_ = _aLPAR1VegHyp_ * _EXP_(- _aExtCoefHyp_ * (_aDepth2VegHyp_ - _aDepth1VegHyp_))
```

### `_aDRootVeg_`  [_gDW_*_m_^-2]
- **Description**: Root_biomass
- **Equation**:

```
_aDRootVeg_ = _bfRootVeg_ * _aDVeg_
```

### `_bfSubVegEpi_`  [0]
- **Description**: Submerged_fraction_of_shoot_in_epilimnion
- **Equation**:

```
_bfSubVegEpi_ = _bfSubVeg_ * ( _uVegHeightEpi_ / _uDepthW_ )
```

### `_bfSubVegHyp_`  [0]
- **Description**: Submerged_fraction_of_shoot
- **Equation**:

```
_bfSubVegHyp_ = _bfSubVeg_ * ( _uVegHeightHyp_ / _uDepthW_ )
```

### `_afCovSurfVeg_`  [0]
- **Description**: Fraction_of_water_SURFACE_covered_by_plant_species
- **Equation**:

```
_afCovSurfVeg_ = _MIN_(1.0, _MAX_(_aDFloatVeg_ / (_cDLayerVeg_ + _NearZero_), _aDEmergVeg_ / (_fEmergVeg_ * _cDCarrVeg_ + _NearZero_) ) )
```

### `_afCovEmergVeg_`  [0]
- **Description**: Fraction_emergent_coverage
- **Equation**:

```
_afCovEmergVeg_ = _MIN_(1.0, _PerCent_ * _cCovSpVeg_ * _aDEmergVeg_)
```

### `_aCovVeg_`  [0]
- **Description**: Percent_cover
- **Equation**:

```
_aCovVeg_ = _MIN_(100.0, _cCovSpVeg_ * _aDShootVeg_)
```

### `_aLPARBotHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_bottom_of_Hyp
- **Equation**:

```
_aLPARBotHyp_ = _uLPARSurfHyp_ * _EXP_(- _aExtCoefHyp_ * _uDepthWHyp_)
```

### `_rPDVeg_`  [_gP_*_gDW_^-1]
- **Description**: P/DW_ratio_of_vegetation
- **Equation**:

```
_rPDVeg_ = _aPVeg_ / (_aDVeg_+_NearZero_)
```

### `_rNDVeg_`  [_gN_*_gDW_^-1]
- **Description**: N/DW_ratio_of_vegetation
- **Equation**:

```
_rNDVeg_ = _aNVeg_ / (_aDVeg_+_NearZero_)
```

### `_tDMigrVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Migration_flux
- **Equation**:

```
_tDMigrVeg_ = _kMigrVeg_ * (_cDVegIn_ - _aDVeg_)
```

### `_tPMigrVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tPMigrVeg_ = _kMigrVeg_ * (_cPDVeg0_* _cDVegIn_ - _aPVeg_)
```

### `_tNMigrVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tNMigrVeg_ = _kMigrVeg_ * (_cNDVeg0_* _cDVegIn_ - _aNVeg_)
```

### `_uFunTmRespVeg_`  [0]
- **Description**: Temperature_function_of_vegetation_respiration
- **Equation**:

```
_uFunTmRespVeg_ = _IF_ ( _UseExpVeg_ _GT_ _NearZero_ ) _THEN_ _uFunTmVeg_ _ELSE_ _POW_(_cQ10RespVeg_ _POWOPERATOR_ (0.1 * (_uTmVegAve_ - _cTmRef_))) _ENDIF_
```

### `_afPUptVegS_`  [0]
- **Description**: Fraction_of_P_uptake_from_sediment
- **Equation**:

```
_afPUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ 0.0 _ELSEIF_ (_bfRootVeg_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_fFloatVeg_ + _bfSubVeg_ _LE_ _NearZero_) _THEN_ 1.0 _ELSEIF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ ((_oPO4S_+_NearZero_) / (_oPO4WHyp_+_NearZero_)) _GT_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(((_oPO4S_+_NearZero_) / (_oPO4WHyp_+_NearZero_)) _POWOPERATOR_ _fSedUptVegExp_)) _ELSEIF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ ((_oPO4S_+_NearZero_) / (_oPO4WHyp_+_NearZero_)) _LE_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_( _NearZero_ _POWOPERATOR_ _fSedUptVegExp_)) _ELSEIF_ (((_oPO4S_+_NearZero_) / (_oPO4WEpi_+_NearZero_)) _LE_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_ (_NearZero_ _POWOPERATOR_ _fSedUptVegExp_)) _ELSE_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(((_oPO4S_+_NearZero_) / (_oPO4WEpi_+_NearZero_)) _POWOPERATOR_ _fSedUptVegExp_)) _ENDIF_
```

### `_afNUptVegS_`  [0]
- **Description**: Fraction_of_N_uptake_from_sediment
- **Equation**:

```
_afNUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ 0.0 _ELSEIF_ (_bfRootVeg_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_fFloatVeg_ + _bfSubVeg_ _LE_ _NearZero_) _THEN_ 1.0 _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ ((_oNDissS_+_NearZero_) / (_oNDissWHyp_+_NearZero_)) _GT_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(((_oNDissS_+_NearZero_) / (_oNDissWHyp_+_NearZero_)) _POWOPERATOR_ _fSedUptVegExp_)) _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ ((_oNDissS_+_NearZero_) / (_oNDissWHyp_+_NearZero_)) _LE_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(_NearZero_ _POWOPERATOR_ _fSedUptVegExp_)) _ELSEIF_ ( ((_oNDissS_+_NearZero_) / (_oNDissWEpi_+_NearZero_)) _LE_ _NearZero_ ) _THEN_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(_NearZero_ _POWOPERATOR_ _fSedUptVegExp_)) _ELSE_ _fSedUptVegMax_ / (1.0 + _fSedUptVegCoef_ * _POW_(((_oNDissS_+_NearZero_) / (_oNDissWEpi_+_NearZero_)) _POWOPERATOR_ _fSedUptVegExp_)) _ENDIF_
```

### `_aVPUptMaxCrVeg_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_vegetation_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrVeg_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _MAX_( 0.0, _cVPUptMaxVeg_ * _uFunTmProdVeg_ * (_cPDVegMax_-_rPDVeg_) / (_cPDVegMax_-_cPDVegMin_) ) _ELSE_ _MAX_( 0.0, _cVPUptMaxVeg_ * _uFunTmProdVeg_ * (_cPDVegMax_-_rPDVeg_) / (_cPDVegMax_-_cPDVegMin_) ) _ENDIF_
```

### `_aVPUptVegWHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_by_submerged_AND_floating_parts
- **Equation**:

```
_aVPUptVegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oPO4WHyp_ * _aVPUptMaxCrVeg_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4WHyp_) _ELSE_ 0.0 _ENDIF_
```

### `_aVPUptVegS_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_by_roots
- **Equation**:

```
_aVPUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oPO4S_ * _aVPUptMaxCrVeg_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4S_) _ELSE_ 0.0 _ENDIF_
```

### `_aVPUptVegWEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_by_submerged_AND_floating_parts
- **Equation**:

```
_aVPUptVegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oPO4WEpi_ * _aVPUptMaxCrVeg_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_tPUptVegWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_from_water
- **Equation**:

```
_tPUptVegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVPUptVegWEpi_ * (_aDSubVeg_ + _aDFloatVeg_) _ELSE_ (1.0 - _afPUptVegS_) * _aVPUptMaxCrVeg_ * _oPO4WEpi_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4WEpi_) * _uDVegEpi_ _ENDIF_
```

### `_tPUptVegWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_from_water
- **Equation**:

```
_tPUptVegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVPUptVegWHyp_ * (_aDSubVeg_ + _aDFloatVeg_) _ELSE_ (1.0 - _afPUptVegS_) * _aVPUptMaxCrVeg_ * _oPO4WHyp_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4WHyp_) * _uDVegHyp_ _ENDIF_
```

### `_tPUptVegS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_from_pore_water_(by_root_fraction)
- **Equation**:

```
_tPUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVPUptVegS_ * _aDRootVeg_ _ELSE_ _afPUptVegS_ * _aVPUptMaxCrVeg_ * _oPO4S_ / (_aVPUptMaxCrVeg_ / _cAffPUptVeg_ + _oPO4S_) * _aDVeg_ _ENDIF_
```

### `_tPUptVegEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_uptake_vegetation
- **Equation**:

```
_tPUptVegEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tPUptVegWEpi_ + _tPUptVegS_ * _uDVegEpi_ / _aDVeg_ _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_ _AND_ _FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _tPUptVegWEpi_ + _tPUptVegS_ _ELSE_ _tPUptVegWEpi_ + _tPUptVegS_ _ENDIF_
```

### `_tPUptVegHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_uptake_vegetation
- **Equation**:

```
_tPUptVegHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _tPUptVegWHyp_ + _tPUptVegS_ * _uDVegHyp_ / _aDVeg_ _ELSE_ _tPUptVegWHyp_ + _tPUptVegS_ * _uDVegHyp_ / _aDVeg_ _ENDIF_
```

### `_aVNUptMaxCrVeg_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_vegetation_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrVeg_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _MAX_( 0.0, _cVNUptMaxVeg_ * _uFunTmProdVeg_ * (_cNDVegMax_ - _rNDVeg_) / (_cNDVegMax_ - _cNDVegMin_)) _ELSE_ _MAX_( 0.0, _cVNUptMaxVeg_ * _uFunTmProdVeg_ * (_cNDVegMax_ - _rNDVeg_) / (_cNDVegMax_ - _cNDVegMin_)) _ENDIF_
```

### `_ahNUptVeg_`  [_gN_*_m_^-3]
- **Description**: Half-sat_constant_for_N_uptake
- **Equation**:

```
_ahNUptVeg_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVNUptMaxCrVeg_ / _cAffNUptVeg_ _ELSE_ _aVNUptMaxCrVeg_ / _cAffNUptVeg_ _ENDIF_
```

### `_aVNUptVegWEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_RATE_by_submerged_AND_floating_parts
- **Equation**:

```
_aVNUptVegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNDissWEpi_ * _aVNUptMaxCrVeg_ / (_ahNUptVeg_ + _oNDissWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_aVNUptVegWHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_RATE_by_submerged_AND_floating_parts
- **Equation**:

```
_aVNUptVegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNDissWHyp_ * _aVNUptMaxCrVeg_ / (_ahNUptVeg_ + _oNDissWHyp_) _ELSE_ 0.0 _ENDIF_
```

### `_afNH4UptVegWEpi_`  [0]
- **Description**: Fraction_ammonium_uptake_from_water_column_(from_WASP_model_EPA)
- **Equation**:

```
_afNH4UptVegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNH4WEpi_ * _oNO3WEpi_ / ((_ahNUptVeg_ + _oNH4WEpi_) * (_ahNUptVeg_ + _oNO3WEpi_ + _NearZero_)) + _oNH4WEpi_ * _ahNUptVeg_ / ((_oNH4WEpi_ + _oNO3WEpi_ + _NearZero_) * (_ahNUptVeg_ + _oNO3WEpi_ + _NearZero_)) _ELSE_ _oNH4WEpi_ * _oNO3WEpi_ / ((_ahNUptVeg_ + _oNH4WEpi_) * (_ahNUptVeg_ + _oNO3WEpi_ + _NearZero_)) + _oNH4WEpi_ * _ahNUptVeg_ / ((_oNH4WEpi_ + _oNO3WEpi_ + _NearZero_) * (_ahNUptVeg_ + _oNO3WEpi_ + _NearZero_)) _ENDIF_
```

### `_afNH4UptVegWHyp_`  [0]
- **Description**: Fraction_ammonium_uptake_from_water_column_(from_WASP_model_EPA)
- **Equation**:

```
_afNH4UptVegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNH4WHyp_ * _oNO3WHyp_ / ((_ahNUptVeg_ + _oNH4WHyp_) * (_ahNUptVeg_ + _oNO3WHyp_ + _NearZero_)) + _oNH4WHyp_ * _ahNUptVeg_ / ((_oNH4WHyp_ + _oNO3WHyp_ + _NearZero_) * (_ahNUptVeg_ + _oNO3WHyp_ + _NearZero_)) _ELSE_ _oNH4WHyp_ * _oNO3WHyp_ / ((_ahNUptVeg_ + _oNH4WHyp_) * (_ahNUptVeg_ + _oNO3WHyp_ + _NearZero_)) + _oNH4WHyp_ * _ahNUptVeg_ / ((_oNH4WHyp_ + _oNO3WHyp_ + _NearZero_) * (_ahNUptVeg_ + _oNO3WHyp_ + _NearZero_)) _ENDIF_
```

### `_tNUptVegWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_from_water_(by_shoots)
- **Equation**:

```
_tNUptVegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVNUptVegWEpi_ * (_aDSubVeg_ + _aDFloatVeg_) _ELSE_ (1.0 - _afNUptVegS_) * _aVNUptMaxCrVeg_ * _oNDissWEpi_ / (_aVNUptMaxCrVeg_ / _cAffNUptVeg_ + _oNDissWEpi_) * _uDVegEpi_ _ENDIF_
```

### `_tNUptVegWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_from_water_(by_shoots)
- **Equation**:

```
_tNUptVegWHyp_ = _IF_ (_FALSE_ _EQ_ _aInclStrat_) _THEN_ 0.0 _ELSEIF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVNUptVegWHyp_ * (_aDSubVeg_ + _aDFloatVeg_) _ELSE_ (1.0 - _afNUptVegS_) * _aVNUptMaxCrVeg_ * _oNDissWHyp_ / (_aVNUptMaxCrVeg_ / _cAffNUptVeg_ + _oNDissWHyp_) * _uDVegHyp_ _ENDIF_
```

### `_tNUptNH4VegWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_uptake_of_vegetation_from_water
- **Equation**:

```
_tNUptNH4VegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _afNH4UptVegWEpi_ * _tNUptVegWEpi_ _ELSE_ _afNH4UptVegWEpi_ * _tNUptVegWEpi_ _ENDIF_
```

### `_tNUptNO3VegWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_uptake_of_vegetation_from_water
- **Equation**:

```
_tNUptNO3VegWEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _tNUptVegWEpi_ - _tNUptNH4VegWEpi_ _ELSE_ _tNUptVegWEpi_ - _tNUptNH4VegWEpi_ _ENDIF_
```

### `_tNUptNH4VegWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_uptake_of_vegetation_from_water
- **Equation**:

```
_tNUptNH4VegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _afNH4UptVegWHyp_ * _tNUptVegWHyp_ _ELSE_ _afNH4UptVegWHyp_ * _tNUptVegWHyp_ _ENDIF_
```

### `_tNUptNO3VegWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_uptake_of_vegetation_from_water
- **Equation**:

```
_tNUptNO3VegWHyp_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _tNUptVegWHyp_ - _tNUptNH4VegWHyp_ _ELSE_ _tNUptVegWHyp_ - _tNUptNH4VegWHyp_ _ENDIF_
```

### `_aVNUptVegS_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_RATE_of_roots
- **Equation**:

```
_aVNUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNDissS_ * _aVNUptMaxCrVeg_ / (_ahNUptVeg_ + _oNDissS_) _ELSE_ 0.0 _ENDIF_
```

### `_tNUptVegS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_from_pore_water_(by_roots)
- **Equation**:

```
_tNUptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVNUptVegS_ * _aDRootVeg_ _ELSE_ _afNUptVegS_ * _aVNUptMaxCrVeg_ * _oNDissS_ / (_aVNUptMaxCrVeg_ / _cAffNUptVeg_ + _oNDissS_) * _aDVeg_ _ENDIF_
```

### `_afNH4UptVegS_`  [0]
- **Description**: Fraction_ammonium_uptake_from_pore_water_(from_WASP_model_EPA)
- **Equation**:

```
_afNH4UptVegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _oNH4S_ * _oNO3S_ / ((_ahNUptVeg_ + _oNH4S_ +_NearZero_) * (_ahNUptVeg_ + _oNO3S_ +_NearZero_)) + _oNH4S_ * _ahNUptVeg_ / ((_oNH4S_ + _oNO3S_+_NearZero_) * (_ahNUptVeg_ + _oNO3S_+_NearZero_)) _ELSE_ _oNH4S_ * _oNO3S_ / ((_ahNUptVeg_ + _oNH4S_ +_NearZero_) * (_ahNUptVeg_ + _oNO3S_ +_NearZero_)) + _oNH4S_ * _ahNUptVeg_ / ((_oNH4S_ + _oNO3S_+_NearZero_) * (_ahNUptVeg_ + _oNO3S_+_NearZero_)) _ENDIF_
```

### `_tNUptNH4VegS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_uptake_of_vegetation_from_sediment
- **Equation**:

```
_tNUptNH4VegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _afNH4UptVegS_ * _tNUptVegS_ _ELSE_ _afNH4UptVegS_ * _tNUptVegS_ _ENDIF_
```

### `_tNUptVegSEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_from_pore_water_(by_roots)
- **Equation**:

```
_tNUptVegSEpi_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _aVNUptVegS_ * _aDRootVeg_ _ELSE_ _afNUptVegS_ * _aVNUptMaxCrVeg_ * _oNDissS_ / (_aVNUptMaxCrVeg_ / _cAffNUptVeg_ + _oNDissS_) * _aDVeg_ _ENDIF_
```

### `_tNUptNO3VegS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_uptake_of_vegetation_from_sediment
- **Equation**:

```
_tNUptNO3VegS_ = _IF_ (_FALSE_ _EQ_ _UseEmpUpt_) _THEN_ _tNUptVegS_ - _tNUptNH4VegS_ _ELSE_ _tNUptVegS_ - _tNUptNH4VegS_ _ENDIF_
```

### `_tNUptVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_uptake_vegetation
- **Equation**:

```
_tNUptVeg_ =_tNUptVegWEpi_ + _tNUptVegWHyp_ + _tNUptVegS_
```

### `_aLLimShootVegEpi_`  [0]
- **Description**: Light_function_of_growth_based_on_shoot_fraction
- **Equation**:

```
_aLLimShootVegEpi_ = _fEmergVeg_ + _fFloatVeg_ * (1.0 - _afCovEmergVeg_) + _bfSubVegEpi_ * (1.0 - _afCovSurfVeg_) * 1.0 / (_aExtCoefEpi_ * _uDepthWEpi_) * _LN_( (1.0 + _aLPAR1VegEpi_ / _uhLVeg_) / (1.0 + _aLPAR2VegEpi_ / _uhLVeg_))
```

### `_aLLimShootVegHyp_`  [0]
- **Description**: Light_function_of_growth_based_on_shoot_fraction
- **Equation**:

```
_aLLimShootVegHyp_ = _fEmergVeg_ + _fFloatVeg_ * (1.0 - _afCovEmergVeg_) + _bfSubVegHyp_ * (1.0 - _afCovSurfVeg_) * 1.0 / (_aExtCoefHyp_ * _uDepthWHyp_) * _LN_( (1.0 + _aLPAR1VegHyp_ / _uhLVeg_) / (1.0 + _aLPAR2VegHyp_ / _uhLVeg_))
```

### `_aMuTmLVegHyp_`  [_gDW_*_gDW_^-1*_d_^-1]
- **Description**: Max_growth_rate_at_current_temp_AND_light
- **Equation**:

```
_aMuTmLVegHyp_ = _ufDay_ * _bfShootVeg_ * _aLLimShootVegHyp_ * _uFunTmProdVeg_ * _cMuMaxVeg_
```

### `_aPLimVeg_`  [0]
- **Description**: Droop_function_(P)_for_vegetation
- **Equation**:

```
_aPLimVeg_ = _MAX_(0.0, (1.0 - _cPDVegMin_ / _rPDVeg_) * _cPDVegMax_ / (_cPDVegMax_ - _cPDVegMin_) )
```

### `_aNLimVeg_`  [0]
- **Description**: Droop_function_(N)_for_vegetation
- **Equation**:

```
_aNLimVeg_ = _MAX_(0.0, (1.0 - _cNDVegMin_ / _rNDVeg_) * _cNDVegMax_ / (_cNDVegMax_ - _cNDVegMin_) )
```

### `_aNutLimVeg_`  [0]
- **Description**: Nutrient_limitation_function_of_vegetation
- **Equation**:

```
_aNutLimVeg_ = _MIN_( _aPLimVeg_, _aNLimVeg_)
```

### `_aMuVegHyp_`  [_gDW_*_gDW_^-1*_d_^-1]
- **Description**: Actual_growth_rate_of_vegetation
- **Equation**:

```
_aMuVegHyp_ = _aMuTmLVegHyp_ * _aNutLimVeg_
```

### `_bkMortVeg_`  [_d_^-1]
- **Description**: Mortality_constant
- **Equation**:

```
_bkMortVeg_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _kMortVegSum_ _ELSEIF_ (_aVegWin_ _EQ_ _TRUE_ _AND_ _aDaysVegWin_ _LE_ _cLengMort_ _AND_ _aDaysVegWin_ _GT_ 0) _THEN_ - _LN_(_fWinVeg_) / _cLengMort_ _ELSE_ _kMortVegSum_ _ENDIF_
```

### `_akDIncrVegHyp_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_vegetation
- **Equation**:

```
_akDIncrVegHyp_ = _aMuTmLVegHyp_ - _kDRespVeg_ * _uFunTmRespVeg_ - _bkMortVeg_
```

### `_tDEnvVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_vegetation
- **Equation**:

```
_tDEnvVegHyp_ = _MAX_(0.0, _akDIncrVegHyp_ / (_cDCarrVeg_+_NearZero_) * _aDVeg_*_aDVeg_)
```

### `_tDEnvProdVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_production
- **Equation**:

```
_tDEnvProdVegHyp_ = _aMuVegHyp_ / _cMuMaxVeg_ * _tDEnvVegHyp_
```

### `_tDProdVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Vegetation_production
- **Equation**:

```
_tDProdVegHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _MAX_(0.0, _aMuVegHyp_ * _uDVegHyp_ - _tDEnvProdVegHyp_) _ENDIF_
```

### `_tDProdSubVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Submerged_production
- **Equation**:

```
_tDProdSubVegHyp_ = _bfSubVegHyp_ * _tDProdVegHyp_
```

### `_tDRespVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dark_respiration_of_vegetation
- **Equation**:

```
_tDRespVeg_ = _kDRespVeg_ * _uFunTmRespVeg_ * _aDVeg_
```

### `_tDEnvMortVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_mortality
- **Equation**:

```
_tDEnvMortVegHyp_ = _tDEnvVegHyp_ - _tDEnvProdVegHyp_
```

### `_tDMortVegHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_mortality_flux_DW_vegetation
- **Equation**:

```
_tDMortVegHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _bkMortVeg_ * _uDVegHyp_ + _tDEnvMortVegHyp_ _ENDIF_
```

### `_tDMortVegWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_becoming_water_detritus
- **Equation**:

```
_tDMortVegWHyp_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tDMortVegHyp_
```

### `_tDGrazVegBird_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Biomass_loss_due_to_grazing_of_birds
- **Equation**:

```
_tDGrazVegBird_ = _IF_ ( (_sTime_ _GE_ _cYearStartBirds_ * _DaysPerYear_) _AND_ (_Day_ _GE_ _cDayStartBirds_) _AND_ (_Day_ _LE_ _cDayEndBirds_) ) _THEN_ _cPrefVegBird_ * _aDVeg_ / (_hDVegBird_ + _aDVeg_) * _cBirdsPerha_ / _m2Perha_ * _cDGrazPerBird_ _ELSE_ 0.0 _ENDIF_
```

### `_tDGrazVegGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Biomass_loss_due_to_grazing_of_Gras_fish
- **Equation**:

```
_tDGrazVegGras_ = _IF_ _tDConsGras_ _GT_ _NearZero_ _THEN_ _tDConsGras_ _ELSE_ _NearZero_ _ENDIF_
```

### `_bkManVeg_`  [_d_^-1]
- **Description**: Rate_constant_during_mowing_period
- **Equation**:

```
_bkManVeg_ = _IF_ ((_Day_ _GE_ _cDayManVeg1_ _AND_ _Day_ _LT_ _cDayManVeg1_ + _cLengMan_) _OR_ (_Day_ _GE_ _cDayManVeg2_ _AND_ _Day_ _LT_ _cDayManVeg2_ + _cLengMan_)) _THEN_ -_LN_(1.0 - _fManVeg_) / _cLengMan_ _ELSE_ 0.0 _ENDIF_
```

### `_tDManVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mowing_of_vegetation_DW
- **Equation**:

```
_tDManVeg_ = _bkManVeg_ * _aDVeg_
```

### `_tPManVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mowing_of_vegetation_P
- **Equation**:

```
_tPManVeg_ = _rPDVeg_ * _tDManVeg_
```

### `_tNManVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mowing_of_vegetation_N
- **Equation**:

```
_tNManVeg_ = _rNDVeg_ * _tDManVeg_
```

### `_tO2ProdVegHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Vegetation_O2_production
- **Equation**:

```
_tO2ProdVegHyp_ = _molO2molC_ * _cCPerDW_ * _tDProdVegHyp_
```

### `_tO2RespVegWHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Submerged_O2_respiration
- **Equation**:

```
_tO2RespVegWHyp_ = _molO2molC_ * _cCPerDW_ * _bfSubVegHyp_ * _tDRespVeg_ * _aCorO2BODHyp_
```

### `_tO2RespVegS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Root_O2_respiration
- **Equation**:

```
_tO2RespVegS_ = _molO2molC_ * _cCPerDW_ * _bfRootVeg_ * _tDRespVeg_ * _afOxySed_
```

### `_tO2ProdVegSHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_transport_to_roots
- **Equation**:

```
_tO2ProdVegSHyp_ = _MIN_ (_tO2RespVegS_, _tO2ProdVegHyp_)
```

### `_tO2ProdVegWHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_used_for_vegetation_production
- **Equation**:

```
_tO2ProdVegWHyp_ = _MIN_( _tO2ProdVegHyp_ - _tO2ProdVegSHyp_, _bfSubVeg_ * _tO2ProdVegHyp_)
```

### `_tO2UptNO3VegWHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_production_to_water_due_to_NO3_uptake_by_macrophytes
- **Equation**:

```
_tO2UptNO3VegWHyp_ = _O2PerNO3_ * _molO2molN_ * _bfSubVeg_ * _tNUptNO3VegWHyp_
```

### `_tO2UptNO3VegS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_production_due_to_NO3_uptake_from_sed_by_macrophytes
- **Equation**:

```
_tO2UptNO3VegS_ = _O2PerNO3_ * _molO2molN_ * _tNUptNO3VegS_
```

### `_tPExcrVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_by_vegetation
- **Equation**:

```
_tPExcrVeg_ = (_rPDVeg_ *2.0)/ (_cPDVegMax_ + _rPDVeg_) * _rPDVeg_ * _tDRespVeg_
```

### `_tPExcrVegS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_by_vegetation_in_sediment
- **Equation**:

```
_tPExcrVegS_ = _bfRootVeg_ * _tPExcrVeg_
```

### `_tPExcrVegW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_by_vegetation_in_water
- **Equation**:

```
_tPExcrVegW_ = _tPExcrVeg_ - _tPExcrVegS_
```

### `_tPMortVegHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_flux_of_vegetation
- **Equation**:

```
_tPMortVegHyp_ = _rPDVeg_ * _tDMortVegHyp_
```

### `_tPMortVegPO4Hyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P
- **Equation**:

```
_tPMortVegPO4Hyp_ = _fDissMortVeg_ * _tPMortVegHyp_
```

### `_tPMortVegPO4SHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P_in_sediment
- **Equation**:

```
_tPMortVegPO4SHyp_ = _bfRootVeg_ * _tPMortVegPO4Hyp_
```

### `_tPMortVegPO4WHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P_in_water
- **Equation**:

```
_tPMortVegPO4WHyp_ = _tPMortVegPO4Hyp_ - _tPMortVegPO4SHyp_
```

### `_tPMortVegDetHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P
- **Equation**:

```
_tPMortVegDetHyp_ = _tPMortVegHyp_ - _tPMortVegPO4Hyp_
```

### `_tPMortVegDetWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P_in_water
- **Equation**:

```
_tPMortVegDetWHyp_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tPMortVegDetHyp_
```

### `_tPMortVegDetSHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P_in_sediment
- **Equation**:

```
_tPMortVegDetSHyp_ = _tPMortVegDetHyp_ - _tPMortVegDetWHyp_
```

### `_tPGrazVegBird_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_flux_of_vegetation_by_bird_grazing
- **Equation**:

```
_tPGrazVegBird_ = _rPDVeg_ * _tDGrazVegBird_
```

### `_tPGrazVegGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_flux_of_vegetation_by_Gras_grazing
- **Equation**:

```
_tPGrazVegGras_ = _rPDVeg_ * _tDGrazVegGras_
```

### `_tNExcrVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_by_vegetation
- **Equation**:

```
_tNExcrVeg_ = (2.0 * _rNDVeg_) / (_cNDVegMax_ + _rNDVeg_) * _rNDVeg_ * _tDRespVeg_
```

### `_tNExcrVegS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_by_vegetation_to_sediment
- **Equation**:

```
_tNExcrVegS_ = _bfRootVeg_ * _tNExcrVeg_
```

### `_tNExcrVegW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_by_vegetation_to_water
- **Equation**:

```
_tNExcrVegW_ = _tNExcrVeg_ - _tNExcrVegS_
```

### `_tNMortVegHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_flux_of_vegetation
- **Equation**:

```
_tNMortVegHyp_ = _rNDVeg_ * _tDMortVegHyp_
```

### `_tNMortVegNH4Hyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N
- **Equation**:

```
_tNMortVegNH4Hyp_ = _fDissMortVeg_ * _tNMortVegHyp_
```

### `_tNMortVegNH4SHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N_in_sediment
- **Equation**:

```
_tNMortVegNH4SHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _bfRootVeg_ * _tNMortVegNH4Hyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMortVegNH4WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N_in_water
- **Equation**:

```
_tNMortVegNH4WHyp_ = _tNMortVegNH4Hyp_ - _tNMortVegNH4SHyp_
```

### `_tNMortVegDetHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N
- **Equation**:

```
_tNMortVegDetHyp_ = _tNMortVegHyp_ - _tNMortVegNH4Hyp_
```

### `_tNMortVegDetWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N_in_water
- **Equation**:

```
_tNMortVegDetWHyp_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tNMortVegDetHyp_
```

### `_tNMortVegDetSHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N_in_sediment
- **Equation**:

```
_tNMortVegDetSHyp_ = _tNMortVegDetHyp_ - _tNMortVegDetWHyp_
```

### `_tNGrazVegBird_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_flux_of_vegetation_by_bird_grazing
- **Equation**:

```
_tNGrazVegBird_ = _rNDVeg_ * _tDGrazVegBird_
```

### `_tNGrazVegGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_flux_of_vegetation_by_Gras_grazing
- **Equation**:

```
_tNGrazVegGras_ = _rNDVeg_ * _tDGrazVegGras_
```

### `_tDAssVegBird_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: DW_assimilation_by_herbivorous_birds
- **Equation**:

```
_tDAssVegBird_ = _fDAssBird_ * _tDGrazVegBird_
```

### `_tDEgesBird_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: DW_egestion_by_herbivorous_birds
- **Equation**:

```
_tDEgesBird_ = _tDGrazVegBird_ - _tDAssVegBird_
```

### `_tPAssVegBird_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_by_herbivorous_birds
- **Equation**:

```
_tPAssVegBird_ = _fDAssBird_ * _tPGrazVegBird_
```

### `_tPEgesBird_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_egestion_by_herbivorous_birds
- **Equation**:

```
_tPEgesBird_ = _tPGrazVegBird_ - _tPAssVegBird_
```

### `_tPEgesBirdPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: PO4_egestion_by_herbivorous_birds
- **Equation**:

```
_tPEgesBirdPO4_ = _fDissEgesBird_ * _tPEgesBird_
```

### `_tPEgesBirdDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_detritus_egestion_by_herbivorous_birds
- **Equation**:

```
_tPEgesBirdDet_ = _tPEgesBird_ - _tPEgesBirdPO4_
```

### `_tNAssVegBird_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_by_herbivorous_birds
- **Equation**:

```
_tNAssVegBird_ = _fDAssBird_ * _tNGrazVegBird_
```

### `_tNEgesBird_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_egestion_by_herbivorous_birds
- **Equation**:

```
_tNEgesBird_ = _tNGrazVegBird_ - _tNAssVegBird_
```

### `_tNEgesBirdNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_egestion_by_herbivorous_birds
- **Equation**:

```
_tNEgesBirdNH4_ = _fDissEgesBird_ * _tNEgesBird_
```

### `_tNEgesBirdDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_detritus_egestion_by_herbivorous_birds
- **Equation**:

```
_tNEgesBirdDet_ = _tNEgesBird_ - _tNEgesBirdNH4_
```

### `_wDBedDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_DW_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wDBedDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_) _THEN_ (_tDMortVegWHyp_) / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aMuTmLVegEpi_`  [_gDW_*_gDW_^-1*_d_^-1]
- **Description**: Max_growth_rate_at_current_temp_AND_light
- **Equation**:

```
_aMuTmLVegEpi_ = _ufDay_ * _bfShootVeg_ * _aLLimShootVegEpi_ * _uFunTmProdVeg_ * _cMuMaxVeg_
```

### `_akDIncrVegEpi_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_vegetation
- **Equation**:

```
_akDIncrVegEpi_ = _aMuTmLVegEpi_ - _kDRespVeg_ * _uFunTmRespVeg_ - _bkMortVeg_
```

### `_tDEnvVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_vegetation
- **Equation**:

```
_tDEnvVegEpi_ = _MAX_(0.0, _akDIncrVegEpi_ / (_cDCarrVeg_+_NearZero_) * _aDVeg_*_aDVeg_)
```

### `_aMuVegEpi_`  [_gDW_*_gDW_^-1*_d_^-1]
- **Description**: Actual_growth_rate_of_vegetation
- **Equation**:

```
_aMuVegEpi_ = _aMuTmLVegEpi_ * _aNutLimVeg_
```

### `_tDEnvProdVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_production
- **Equation**:

```
_tDEnvProdVegEpi_ = _aMuVegEpi_ / _cMuMaxVeg_ * _tDEnvVegEpi_
```

### `_tDProdVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Vegetation_production
- **Equation**:

```
_tDProdVegEpi_ = _MAX_(0.0, _aMuVegEpi_ * _uDVegEpi_ - _tDEnvProdVegEpi_)
```

### `_tDEnvMortVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Logistic_correction_of_mortality
- **Equation**:

```
_tDEnvMortVegEpi_ = _tDEnvVegEpi_ - _tDEnvProdVegEpi_
```

### `_tDMortVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_mortality_flux_DW_vegetation
- **Equation**:

```
_tDMortVegEpi_ = _bkMortVeg_ * _uDVegEpi_ + _tDEnvMortVegEpi_
```

### `_tNMortVegEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_flux_of_vegetation
- **Equation**:

```
_tNMortVegEpi_ = _rNDVeg_ * _tDMortVegEpi_
```

### `_tNMortVegNH4Epi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N
- **Equation**:

```
_tNMortVegNH4Epi_ = _fDissMortVeg_ * _tNMortVegEpi_
```

### `_tNMortVegNH4SEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N_in_sediment
- **Equation**:

```
_tNMortVegNH4SEpi_ = _bfRootVeg_ * _tNMortVegNH4Epi_
```

### `_wPBedPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_PO4_in_water
- **Equation**:

```
_wPBedPO4WHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_ ) _THEN_ (- _tPUptVegWHyp_ + _tPExcrVegW_ * _uVegHeightHyp_ / _uVegHeight_ + _tPMortVegPO4WHyp_ ) /_uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wPBedDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wPBedDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_) _THEN_ (_tPMortVegDetWHyp_ ) / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NH4_in_water
- **Equation**:

```
_wNBedNH4WHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_ ) _THEN_ (- _tNUptNH4VegWHyp_ + _tNExcrVegW_ * (_uVegHeightHyp_ /_uVegHeight_ ) + _tNMortVegNH4WHyp_ ) / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NO3_in_water
- **Equation**:

```
_wNBedNO3WHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_) _THEN_ - _tNUptNO3VegWHyp_ / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wNBedDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_) _THEN_ (_tNMortVegDetWHyp_ ) / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMortVegSHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_becoming_sediment_detritus
- **Equation**:

```
_tDMortVegSHyp_ = _tDMortVegHyp_ - _tDMortVegWHyp_
```

### `_tDBedDetSHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NH4_in_pore_water
- **Equation**:

```
_tDBedDetSHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_ ) _THEN_ _tDMortVegSHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2BedWHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Total_water_O2_flux_in_vegetation_module
- **Equation**:

```
_tO2BedWHyp_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _InclVeg_ _EQ_ _TRUE_ ) _THEN_ _tO2ProdVegWHyp_ - _tO2RespVegWHyp_ + _tO2UptNO3VegWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tDProdSubVegEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Submerged_production
- **Equation**:

```
_tDProdSubVegEpi_ = _bfSubVegEpi_ * _tDProdVegEpi_
```

### `_tDMortVegWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_becoming_water_detritus
- **Equation**:

```
_tDMortVegWEpi_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tDMortVegEpi_
```

### `_tDMortVegSEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_becoming_sediment_detritus
- **Equation**:

```
_tDMortVegSEpi_ = _tDMortVegEpi_ - _tDMortVegWEpi_
```

### `_tDBedVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_of_vegetation_biomass
- **Equation**:

```
_tDBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tDMigrVeg_ + _tDProdVegEpi_ + _tDProdVegHyp_- _tDRespVeg_ - _tDMortVegEpi_ - _tDMortVegHyp_ - _tDGrazVegBird_ - _tDGrazVegGras_ - _tDManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2ProdVegEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Vegetation_O2_production
- **Equation**:

```
_tO2ProdVegEpi_ = _molO2molC_ * _cCPerDW_ * _tDProdVegEpi_
```

### `_tO2RespVegWEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Submerged_O2_respiration
- **Equation**:

```
_tO2RespVegWEpi_ = _molO2molC_ * _cCPerDW_ * _bfSubVegEpi_ * _tDRespVeg_ * _aCorO2BODEpi_
```

### `_tO2ProdVegSEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_transport_to_roots
- **Equation**:

```
_tO2ProdVegSEpi_ = _MIN_ (_tO2RespVegS_, _tO2ProdVegEpi_)
```

### `_tO2ProdVegWEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_used_for_vegetation_production
- **Equation**:

```
_tO2ProdVegWEpi_ = _MIN_ ( _tO2ProdVegEpi_ - _tO2ProdVegSEpi_, _bfSubVeg_ * _tO2ProdVegEpi_)
```

### `_tO2BedS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Total_sediment_O2_flux_in_vegetation_module
- **Equation**:

```
_tO2BedS_ = _tO2ProdVegSHyp_ + _tO2ProdVegSEpi_ - _tO2RespVegS_ + _tO2UptNO3VegS_
```

### `_tO2UptNO3VegWEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_production_to_water_due_to_NO3_uptake_by_macrophytes
- **Equation**:

```
_tO2UptNO3VegWEpi_ = _O2PerNO3_ * _molO2molN_ * _bfSubVeg_ * _tNUptNO3VegWEpi_
```

### `_tPMortVegEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_flux_of_vegetation
- **Equation**:

```
_tPMortVegEpi_ = _rPDVeg_ * _tDMortVegEpi_
```

### `_tPMortVegPO4Epi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P
- **Equation**:

```
_tPMortVegPO4Epi_ = _fDissMortVeg_ * _tPMortVegEpi_
```

### `_tPMortVegPO4SEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P_in_sediment
- **Equation**:

```
_tPMortVegPO4SEpi_ = _bfRootVeg_ * _tPMortVegPO4Epi_
```

### `_tPMortVegPO4WEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_P_in_water
- **Equation**:

```
_tPMortVegPO4WEpi_ = _tPMortVegPO4Epi_ - _tPMortVegPO4SEpi_
```

### `_tPMortVegDetEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P
- **Equation**:

```
_tPMortVegDetEpi_ = _tPMortVegEpi_ - _tPMortVegPO4Epi_
```

### `_tPMortVegDetWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P_in_water
- **Equation**:

```
_tPMortVegDetWEpi_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tPMortVegDetEpi_
```

### `_tPMortVegDetSEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_P_in_sediment
- **Equation**:

```
_tPMortVegDetSEpi_ = _tPMortVegDetEpi_ - _tPMortVegDetWEpi_
```

### `_tPBedVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_vegetation_P_flux_in_bed_module
- **Equation**:

```
_tPBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tPMigrVeg_ + _tPUptVegEpi_ + _tPUptVegHyp_ - _tPExcrVeg_ - _tPMortVegEpi_ - _tPMortVegHyp_ - _tPGrazVegBird_ - _tPGrazVegGras_ - _tPManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMortVegNH4WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_dissolved_N_in_water
- **Equation**:

```
_tNMortVegNH4WEpi_ = _tNMortVegNH4Epi_ - _tNMortVegNH4SEpi_
```

### `_tNMortVegDetEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N
- **Equation**:

```
_tNMortVegDetEpi_ = _tNMortVegEpi_ - _tNMortVegNH4Epi_
```

### `_tNMortVegDetWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N_in_water
- **Equation**:

```
_tNMortVegDetWEpi_ = _fDetWMortVeg_ * (1.0 - _bfRootVeg_) * _tNMortVegDetEpi_
```

### `_tNMortVegDetSEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_flux_of_vegetation_becoming_detritus_N_in_sediment
- **Equation**:

```
_tNMortVegDetSEpi_ = _tNMortVegDetEpi_ - _tNMortVegDetWEpi_
```

### `_tNBedVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_vegetation_N_flux_in_bed_module
- **Equation**:

```
_tNBedVeg_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tNMigrVeg_ + _tNUptVeg_ - _tNExcrVeg_ - _tNMortVegEpi_ - _tNMortVegHyp_ - _tNGrazVegBird_ - _tNGrazVegGras_ - _tNManVeg_ _ELSE_ 0.0 _ENDIF_
```

### `_wDBedDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_DW_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wDBedDetWEpi_ = _IF_ (_InclVeg_ _EQ_ _TRUE_) _THEN_ (_tDMortVegWEpi_ + _tDEgesBird_) / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tDBedDetSEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_flux_from_Vegetation_module_to_sediment_detritus
- **Equation**:

```
_tDBedDetSEpi_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_) _THEN_ _tDMortVegSEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wPBedPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_PO4_in_water
- **Equation**:

```
_wPBedPO4WEpi_ = _IF_ (_InclVeg_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (- _tPUptVegWEpi_ + _tPExcrVegW_ * _uVegHeightEpi_ / _uVegHeight_ + _tPMortVegPO4WEpi_ + _tPEgesBirdPO4_) /_uDepthWEpi_ _ENDIF_
```

### `_wPBedDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wPBedDetWEpi_ = _IF_ (_InclVeg_ _EQ_ _TRUE_) _THEN_ (_tPMortVegDetWEpi_ + _tPEgesBirdDet_ ) / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBedPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_pore_water_PO4
- **Equation**:

```
_tPBedPO4S_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_) _THEN_ - _tPUptVegS_ + _tPExcrVegS_ + _tPMortVegPO4SEpi_ + _tPMortVegPO4SHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBedDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module_to_sediment_detritus
- **Equation**:

```
_tPBedDetS_ = _IF_ (_InclVeg_ _EQ_ _TRUE_) _THEN_ _tPMortVegDetSEpi_ + _tPMortVegDetSHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NH4_in_water
- **Equation**:

```
_wNBedNH4WEpi_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_ ) _THEN_ (- _tNUptNH4VegWEpi_ + _tNExcrVegW_ * (_uVegHeightEpi_ /_uVegHeight_ ) + _tNMortVegNH4WEpi_ + _tNEgesBirdNH4_) / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NO3_in_water
- **Equation**:

```
_wNBedNO3WEpi_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_) _THEN_ - _tNUptNO3VegWEpi_ / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wNBedDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_water_detritus
- **Equation**:

```
_wNBedDetWEpi_ = _IF_ (_InclVeg_ _EQ_ _TRUE_) _THEN_ (_tNMortVegDetWEpi_ + _tNEgesBirdDet_) / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBedNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NH4_in_pore_water
- **Equation**:

```
_tNBedNH4S_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_) _THEN_ - _tNUptNH4VegS_ + _tNExcrVegS_ + _tNMortVegNH4SEpi_ + _tNMortVegNH4SHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBedNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_NO3_in_pore_water
- **Equation**:

```
_tNBedNO3S_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_ ) _THEN_ - _tNUptNO3VegS_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBedDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module_to_sediment_detritus
- **Equation**:

```
_tNBedDetS_ = _IF_ ( _InclVeg_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ _tNMortVegDetSEpi_ + _tNMortVegDetSHyp_ _ELSE_ _tNMortVegDetSEpi_ _ENDIF_
```

### `_tO2BedWEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Total_water_O2_flux_in_vegetation_module
- **Equation**:

```
_tO2BedWEpi_ = _IF_ ( _InclVeg_ _EQ_ _TRUE_ ) _THEN_ _tO2ProdVegWEpi_ - _tO2RespVegWEpi_ + _tO2UptNO3VegWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tDBedTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_flux_from_Vegetation_module
- **Equation**:

```
_tDBedTotT_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tDMigrVeg_ + _tDProdVegHyp_+ _tDProdVegEpi_ - _tDRespVeg_ - _tDManVeg_ - _tDAssVegBird_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBedTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_flux_from_Vegetation_module
- **Equation**:

```
_tPBedTotT_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tPMigrVeg_ - _tPManVeg_ - _tPAssVegBird_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBedTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux_from_Vegetation_module
- **Equation**:

```
_tNBedTotT_ = _IF_ _InclVeg_ _EQ_ _TRUE_ _THEN_ _tNMigrVeg_ - _tNManVeg_ - _tNAssVegBird_  _ELSE_ 0.0 _ENDIF_
```

### `_cCheckVegHeight_`  [0]
- **Description**: Check
- **Equation**:

```
_cCheckVegHeight_ = _IF_ ( _aVegWin_ _EQ_ 1 _AND_  _uVegHeight_ _LT_ _MIN_ (_cVegHeightWin_, _uDepthW_) ) _THEN_ 1.0 _ELSEIF_ ( _aVegWin_ _EQ_ 1 _AND_  _uVegHeight_ _GT_ _MIN_ (_cVegHeightWin_, _uDepthW_) ) _THEN_ 2.0 _ELSEIF_ ( _aVegWin_ _EQ_ 0 _AND_  _uVegHeight_ _LT_ _MIN_ (_cVegHeight_, _uDepthW_) ) _THEN_  3.0 _ELSEIF_ ( _aVegWin_ _EQ_ 0 _AND_  _uVegHeight_ _GT_ _MIN_ (_cVegHeight_, _uDepthW_) ) _THEN_ 4.0 _ELSE_ 0.0 _ENDIF_
```

## Extinction_coefficients  (8 equations)

### `_aExtPhytHyp_`  [_m_^-1]
- **Description**: Contribution_of_algae_to_extinction
- **Equation**:

```
_aExtPhytHyp_ = _cExtSpDiat_ * _oDDiatWHyp_ + _cExtSpGren_ * _oDGrenWHyp_ + _cExtSpBlue_ * _oDBlueWHyp_
```

### `_aExtDetHyp_`  [_m_^-1]
- **Description**: Detrital_contribution_to_extinction
- **Equation**:

```
_aExtDetHyp_ = _cExtSpDet_ * _oDDetWHyp_
```

### `_aExtIMHyp_`  [_m_^-1]
- **Description**: Contribution_of_inert_matter_to_extinction
- **Equation**:

```
_aExtIMHyp_ = _cExtSpIM_ * _oDIMWHyp_
```

### `_aExtCoefOpenHyp_`  [_m_^-1]
- **Description**: Extinction_coefficient_without_vegetation
- **Equation**:

```
_aExtCoefOpenHyp_ = _cExtWat_ + _aExtIMHyp_ + _aExtDetHyp_ + _aExtPhytHyp_
```

### `_aExtPhytEpi_`  [_m_^-1]
- **Description**: Contribution_of_algae_to_extinction
- **Equation**:

```
_aExtPhytEpi_ = _cExtSpDiat_ * _oDDiatWEpi_ + _cExtSpGren_ * _oDGrenWEpi_ + _cExtSpBlue_ * _oDBlueWEpi_
```

### `_aExtDetEpi_`  [_m_^-1]
- **Description**: Detrital_contribution_to_extinction
- **Equation**:

```
_aExtDetEpi_ = _cExtSpDet_ * _oDDetWEpi_
```

### `_aExtIMEpi_`  [_m_^-1]
- **Description**: Contribution_of_inert_matter_to_extinction
- **Equation**:

```
_aExtIMEpi_ = _cExtSpIM_ * _oDIMWEpi_
```

### `_aExtCoefOpenEpi_`  [_m_^-1]
- **Description**: Extinction_coefficient_without_vegetation
- **Equation**:

```
_aExtCoefOpenEpi_ = _cExtWat_ + _aExtIMEpi_ + _aExtDetEpi_ + _aExtPhytEpi_
```

## Extinction  (1 equations)

### `_aExtSurf_`  [0]
- **Description**: Extinction_of_Blue_on_surface
- **Equation**:

```
_aExtSurf_ = _cExtSpBlue_ * _aDBlueSurf_
```

## Forcing_function  (22 equations)

### `_aTmEpi_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_aTmEpi_ =  _cTmAveEpi_ - _cTmVarEpi_ * _COS_(2.0*_Pi_*(_sTime_ + _TenDays_ - _cTimeLag_) / _DaysInYear_)
```

### `_aTmHyp_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_aTmHyp_ =  _cTmAveHyp_ - _cTmVarHyp_ * _COS_(2.0*_Pi_*(_sTime_ + _TenDays_ - _cTimeLag_) / _DaysInYear_)
```

### `_uTmEpi_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_uTmEpi_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _cTmAveEpi_ _ELSEIF_ (_ReadTemp_ _EQ_ _TRUE_) _THEN_ _mTempEpi_ _ELSEIF_ ( _aTmEpi_ _GT_ 0.0  ) _THEN_ _aTmEpi_ _ELSE_  0.0 _ENDIF_
```

### `_uTmHyp_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_uTmHyp_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _cTmAveHyp_ _ELSEIF_ (_ReadTemp_ _EQ_ _TRUE_) _THEN_ _mTempHyp_ _ELSEIF_ ( _aTmHyp_ _GT_ 0.0  ) _THEN_ _aTmHyp_ _ELSE_  0.0 _ENDIF_
```

### `_uTmBot_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_uTmBot_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _uTmHyp_ _ELSE_ _uTmEpi_ _ENDIF_
```

### `_uTmSurf_`  [_oC_]
- **Description**: Forcing_function_temperature
- **Equation**:

```
_uTmSurf_ = _uTmEpi_
```

### `_uSolDecAng_`  [_rad_]
- **Description**: Solar_Declination_angle
- **Equation**:

```
_uSolDecAng_= _IF_(_InclLat_ _EQ_ _TRUE_) _THEN_ _cPhiR_*_COS_(2*_Pi_*(_Day_-_cDayR_)/_DaysInYear_) _ELSE_ 0.0 _ENDIF_
```

### `_uSunRise_`  [_h_]
- **Description**: Time_of_sun_rise
- **Equation**:

```
_uSunRise_ = _HoursInDay_/(2*_Pi_)*_ACOS_((_SIN_(_uLAT_)* _SIN_(_uSolDecAng_))/(_COS_(_uLAT_)*_COS_(_uSolDecAng_)))
```

### `_uSunSet_`  [_h_]
- **Description**: Time_of_sun_set
- **Equation**:

```
_uSunSet_=_HoursInDay_-_uSunRise_
```

### `_uSunHours_`  [_h_]
- **Description**: Hours_of_sun_per_day
- **Equation**:

```
_uSunHours_=_uSunSet_-_uSunRise_
```

### `_uSunPath_`  [_h_]
- **Description**: Integration_of_the_sunpath_over_the_local_rise_and_falls
- **Equation**:

```
_uSunPath_= _IF_(_InclLat_ _EQ_ _TRUE_) _THEN_ _SIN_(_uLAT_)*_SIN_( _uSolDecAng_ )*( _uSunSet_-_uSunRise_)- _COS_(_uLAT_) * _COS_ (_uSolDecAng_) * _HoursInDay_ / (2*_Pi_) * ( _SIN_ (2*_Pi_*_uSunSet_/_HoursInDay_ ) -_SIN_(2*_Pi_*_uSunRise_ /_HoursInDay_ )) _ELSE_ 0.0 _ENDIF_
```

### `_uTrans_`  [0]
- **Description**: Transmissivity_atmosphere
- **Equation**:

```
_uTrans_=_IF_((_InclLat_ _EQ_ _TRUE_) _AND_ (_ConstTrans_ _EQ_ _FALSE_)) _THEN_ (0.6-0.2*(_uSunPath_/(_uSunSet_ - _uSunRise_)))*(1-0.4*_fCloudH_) *(1-0.7* _fCloudM_) *(1-0.4*_fCloudL_)_ELSEIF_ ((_InclLat_ _EQ_ _TRUE_) _AND_ (_ConstTrans_ _EQ_ _TRUE_)) _THEN_ _cTrans_ _ELSE_ 0.0 _ENDIF_
```

### `_ufDay_`  [_h_*_h_^-1]
- **Description**: Day_length
- **Equation**:

```
_ufDay_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _cfDayAve_ _ELSEIF_ (_InclLat_ _EQ_ _TRUE_) _THEN_ (_uSunSet_ -_uSunRise_ )/ _HoursInDay_ _ELSE_ _cfDayAve_ - _cfDayVar_ * _COS_( 2.0 *_Pi_*(_sTime_+_TenDays_) / _DaysInYear_) _ENDIF_
```

### `_uLDay_`  [_J_*_m_^-2*_d_^-1]
- **Description**: Total_daily_radiation
- **Equation**:

```
_uLDay_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _cLDayAve_ _ELSEIF_ (_ReadLOut_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSEIF_ (_InclLat_ _EQ_ _TRUE_) _THEN_ _cSolar_*_uTrans_*_uSunPath_ * _SecsPerDay_ /_HoursInDay_ _ELSE_ _cLDayAve_ - _cLDayVar_ * _COS_(2.0*_Pi_*(_sTime_+_TenDays_) / _DaysInYear_) _ENDIF_
```

### `_uLOut_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Average_light_intensity_during_daytime
- **Equation**:

```
_uLOut_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _uLDay_ / _SecsPerDay_ / _ufDay_ _ELSEIF_ (_ReadLOut_ _EQ_ _TRUE_) _THEN_ _mLOut_ / _ufDay_ _ELSE_ _uLDay_ / _SecsPerDay_ / _ufDay_ _ENDIF_
```

### `_uLPARSurf_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Average_PAR_at_zero_depth
- **Equation**:

```
_uLPARSurf_ = _fPAR_ * (1.0 - _fRefl_) * _uLOut_
```

### `_uVWind_`  [_m_*_s_^-1]
- **Description**: Forcing_function_wind_speed
- **Equation**:

```
_uVWind_ = _IF_ (_ReadVWind_ _EQ_ _TRUE_)_THEN_ _mVWind_ _ELSE_ _cVWind_ _ENDIF_
```

### `_aStrat_`  [0]
- **Description**: Presence_of_stratification
- **Equation**:

```
_aStrat_ = _IF_ (_ReadStrat_ _EQ_ _TRUE_) _THEN_ _mStrat_ _ELSEIF_ ((_uTmEpi_ -_uTmHyp_) _GT_  _cStratTm_ _OR_ (_uTmHyp_ -_uTmEpi_) _GT_  _cStratTm_) _THEN_ 1.0  _ELSE_ 0.0 _ENDIF_
```

### `_aLPARAveSurf_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Average_PAR_at_Surface
- **Equation**:

```
_aLPARAveSurf_ = _MAX_(0.0,(_uLPARSurf_ - _aLPARBotSurf_)/_aExtSurf_)
```

### `_aLPARAveEpi_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Average_PAR_at_Epilimnion
- **Equation**:

```
_aLPARAveEpi_ = (_aLPARBotSurf_ - _aLPARBotEpi_)/ (_aExtCoefOpenEpi_ * _uDepthWEpi_)
```

### `_aLPARAveHyp_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Average_PAR_at_Hypolimnion
- **Equation**:

```
_aLPARAveHyp_ = (_aLPARBotEpiOpen_ -_aLPARBotHyp_)/ (_aExtCoefOpenHyp_ * _uDepthWEpi_)
```

### `_aLPAREupho_`  [_J_*_m_^-2*_s_^-1]
- **Description**: One_percent_PAR_of_incident_light
- **Equation**:

```
_aLPAREupho_ = _PerCent_ * _uLPARSurf_
```

## Conversion  (1 equations)

### `_uLAT_`  [_rad_]
- **Description**: Latitude_conversion_to_radians
- **Equation**:

```
_uLAT_= _cLAT_*2*_Pi_/360
```

## Light_intensity  (1 equations)

### `_aLPARBotSurf_`  [_J_*_m_^-2*_s_^-1]
- **Description**: Light_at_the_bottom_of_Surface
- **Equation**:

```
_aLPARBotSurf_ = _IF_ (_InclSurf_ _EQ_ _TRUE_) _THEN_ _uLPARSurf_ * _EXP_(- _aExtSurf_) _ELSE_ _uLPARSurf_ _ENDIF_
```

## Light  (7 equations)

### `_uLPARSurfHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_the_top_of_Hyp
- **Equation**:

```
_uLPARSurfHyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _aLPARBotEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_aLPIEpi_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Integrated_PI_curve_for_phytoplankton_growth
- **Equation**:

```
_aLPIEpi_ =  (_aLPARBotSurf_- _aLPARBotEpiOpen_ + _uhLVeg_* _LN_((1.0 +_aLPARBotEpiOpen_/ _uhLVeg_)  /(1.0 + _aLPARBotSurf_  / _uhLVeg_) + _NearZero_  ) ) / _uDepthWEpi_
```

### `_aLPIHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Integrated_PI_curve_for_phytoplankton_growth_Hyp
- **Equation**:

```
_aLPIHyp_ =  (_aLPARBotEpi_- _aLPARBotHypOpen_ + _uhLVeg_* _LN_((1.0 +_aLPARBotHypOpen_/ _uhLVeg_)  /(1.0 + _aLPARBotEpi_  / _uhLVeg_) + _NearZero_  ) ) / _uDepthWHyp_
```

### `_aLPIMeasEpi_`  [_J_*_s_^-1*_m_^-1]
- **Description**: Integrated_PI_curve_for_phytoplankton_growth_Epi
- **Equation**:

```
_aLPIMeasEpi_ =  (_aLPARBotSurf_- _aLPARBotEpi_ ) /_aExtCoefEpi_
```

### `_aLPIMeasHyp_`  [_J_*_s_^-1*_m_^-1]
- **Description**: Integrated_PI_curve_for_phytoplankton_growth_Hyp
- **Equation**:

```
_aLPIMeasHyp_ =  (_aLPARBotEpi_- _aLPARBotHyp_) / _aExtCoefHyp_
```

### `_aLMeasEpi_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_measurement_depth
- **Equation**:

```
_aLMeasEpi_ = _aLPARBotSurf_ * _EXP_(- _aExtCoefOpenEpi_ *_cDepthMeasoChl_)
```

### `_aLMeasHyp_`  [_J_*_s_^-1*_m_^-2]
- **Description**: Light_at_measurement_depth_Hyp
- **Equation**:

```
_aLMeasHyp_ = _aLPARBotEpi_ * _EXP_(- _aExtCoefOpenHyp_ * (_cDepthMeasoChl_ -  _uDepthWEpi_))
```

## Water_budget  (83 equations)

### `_uQInSeason_`  [_mm_*_d_^-1]
- **Description**: Seasonal_inflow
- **Equation**:

```
_uQInSeason_ = _IF_ (_FALSE_ _EQ_ _UseSeasonLoad_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _cDayApril1_ - 0.5*_cLengChange_) _THEN_ _cQInWin_ _ELSEIF_ (_Day_ _LT_ _cDayApril1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cQInWin_ + _cQInSum_) + 0.5*(_cQInWin_ - _cQInSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayApril1_)) _ELSEIF_ (_Day_ _LT_ _cDayOct1_ - 0.5*_cLengChange_) _THEN_ _cQInSum_ _ELSEIF_ (_Day_ _LT_ _cDayOct1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cQInWin_ + _cQInSum_) - 0.5*(_cQInWin_ - _cQInSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayOct1_)) _ELSE_ _cQInWin_ _ENDIF_
```

### `_uQEvSinus_`  [_mm_*_d_^-1]
- **Description**: Sinusoid_evaporation
- **Equation**:

```
_uQEvSinus_ = _cQEvAve_ - _cQEvVar_ * _COS_(2.0*_Pi_ * (_sTime_ + _TenDays_ - _cTimeLag_) / _DaysInYear_)
```

### `_aQEv_`  [_mm_*_d_^-1]
- **Description**: Evaporation_from_heat_based_on_Thornthwaite
- **Equation**:

```
_aQEv_ = _IF_ (10 *_uTmEpi_ /_cHeat_) _LE_ _NearZero_ _THEN_ 16 * 2*_ufDay_ * 1 / 30 * _POW_ ( _NearZero_ _POWOPERATOR_ (_cAlpha_) ) _ELSE_ 16 * 2*_ufDay_ * 1 / 30 * _POW_ ( 10 *_uTmEpi_ /_cHeat_ _POWOPERATOR_ (_cAlpha_) ) _ENDIF_
```

### `_uQEv_`  [_mm_*_d_^-1]
- **Description**: Evaporation
- **Equation**:

```
_uQEv_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ _cQEvAve_ _ELSEIF_ (_ReadQEv_ _EQ_ _TRUE_) _THEN_ _mQEv_ _ELSEIF_ (_calcQEv_ _EQ_ _TRUE_ ) _THEN_ _aQEv_ _ELSE_ _uQEvSinus_ _ENDIF_
```

### `_uDepthDifMeas_`  [_m_]
- **Description**: Change_in_water_depth
- **Equation**:

```
_uDepthDifMeas_ = _IF_ ( _ReadDepthW_ _EQ_ _TRUE_ ) _THEN_ _mDepthW_ - _uDepthW_ _ELSE_ 0.0 _ENDIF_
```

### `_uQInCor_`  [_mm_]
- **Description**: Correction_for_water_inflow_when_depth_is_measured
- **Equation**:

```
_uQInCor_ = _IF_ (_uDepthDifMeas_ _GE_ 0) _THEN_ _uDepthDifMeas_ * _cMaxWOut_ * _mmPerm_ _ELSE_ 0.0 _ENDIF_
```

### `_uQOutCor_`  [_mm_]
- **Description**: Correction_for_water_outflow_when_depth_is_measured
- **Equation**:

```
_uQOutCor_ = _IF_ (_uDepthDifMeas_ _LT_ 0) _THEN_ -1 * _uDepthDifMeas_ * _cMaxWOut_ * _mmPerm_ _ELSE_ 0.0 _ENDIF_
```

### `_uQInEpi_`  [_mm_*_d_^-1]
- **Description**: Inflow_epilimnion
- **Equation**:

```
_uQInEpi_ = _IF_ ((_ReadQIn_ _EQ_ _TRUE_) _OR_ (_ReadTranFrac_ _EQ_ _TRUE_)) _THEN_ _mQInEpi_ + _uQInCor_ _ELSEIF_ (_UseSeasonLoad_ _EQ_ _TRUE_) _THEN_ _uQInSeason_ + _uQInCor_ _ELSE_ _cQInEpi_ + _uQInCor_ _ENDIF_
```

### `_uQInHyp_`  [_mm_*_d_^-1]
- **Description**: Inflow_hypolimnion
- **Equation**:

```
_uQInHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ ((_ReadQIn_ _EQ_ _TRUE_) _OR_ (_ReadTranFrac_ _EQ_ _TRUE_)) _THEN_ _mQInHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aQInTot_`  [_mm_*_d_^-1]
- **Description**: Inflow_total
- **Equation**:

```
_aQInTot_ = _uQInEpi_ + _uQInHyp_
```

### `_uQPrec_`  [_mm_*_d_^-1]
- **Description**: Inflow_precipitation_to_epilimnion
- **Equation**:

```
_uQPrec_ = _IF_ (_ReadQPrec_ _EQ_ _TRUE_) _THEN_ _mQPrec_ _ELSE_ 0 _ENDIF_
```

### `_uQInSeep_`  [_mm_*_d_^-1]
- **Description**: Inflow_from_groundwater_called_seepage
- **Equation**:

```
_uQInSeep_ = _IF_ (_ReadQGround_ _EQ_ _TRUE_) _THEN_ _mQInSeep_ _ELSE_ _cQInSeep_ _ENDIF_
```

### `_uQOutInf_`  [_mm_*_d_^-1]
- **Description**: Outflow_to_groundwater_called_infiltration
- **Equation**:

```
_uQOutInf_ = _IF_ (_ReadQGround_ _EQ_ _TRUE_) _THEN_ _mQOutInf_ _ELSE_ _cQOutInf_ _ENDIF_
```

### `_uQOutPot_`  [_mm_*_d_^-1]
- **Description**: Potential_outflow
- **Equation**:

```
_uQOutPot_ = _uQPrec_ + _uQInEpi_ - _uQInCor_ + _uQInHyp_ + _uQInSeep_ - _uQEv_ - _uQOutCor_ - _uQOutInf_
```

### `_aMaxQOutEpi_`  [_mm_*_d_^-1]
- **Description**: Maximum_outflow_for_epilimnion
- **Equation**:

```
_aMaxQOutEpi_ = _IF_ ( _uDepthWEpi_ _LE_ _cMinDepthHypEpi_ ) _THEN_ 0.0 _ELSE_ _uDepthWEpi_ * _mmPerm_ * _cMaxWOut_ _ENDIF_
```

### `_aMaxQOutHyp_`  [_mm_*_d_^-1]
- **Description**: Maximum_outflow_for_hypolimnion
- **Equation**:

```
_aMaxQOutHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _AND_ ( _uDepthWHyp_ _GT_ _cMinDepthHypEpi_ ) _THEN_ (_uDepthWHyp_ - _cMinDepthHypEpi_) * _mmPerm_ * _cMaxWOut_ _ELSE_ 0.0 _ENDIF_
```

### `_uQOutEpi_`  [_mm_*_d_^-1]
- **Description**: Outflow_epilimnion
- **Equation**:

```
_uQOutEpi_ = _IF_ (_ReadQOut_ _EQ_ _TRUE_) _THEN_ _MIN_(_mQOutEpi_, _aMaxQOutEpi_) _ELSE_ _MIN_(_aMaxQOutEpi_, _MAX_(0.0, _uQOutPot_)) _ENDIF_
```

### `_uQOutHyp_`  [_mm_*_d_^-1]
- **Description**: Outflow_hypolimnion
- **Equation**:

```
_uQOutHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadQOut_ _EQ_ _TRUE_) _THEN_ _MIN_(_mQOutHyp_, _aMaxQOutHyp_) _ELSE_ _MIN_(_aMaxQOutHyp_, _MAX_(0.0, (_uQOutPot_ - _uQOutEpi_))) _ENDIF_
```

### `_ukOutEpi_`  [_d_^-1]
- **Description**: Outflow_rate_of_substances
- **Equation**:

```
_ukOutEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uQOutEpi_ / _mmPerm_ / _uDepthWEpi_ _ENDIF_
```

### `_ukOutHyp_`  [_d_^-1]
- **Description**: Outflow_rate_of_substances
- **Equation**:

```
_ukOutHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uQOutHyp_ / _mmPerm_ / _uDepthWHyp_ _ENDIF_
```

### `_uTauWatEpi_`  [_d_]
- **Description**: Water_residence_time
- **Equation**:

```
_uTauWatEpi_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 1.0 / ((_uQInEpi_ + _uQPrec_ + _uQInSeep_) / _mmPerm_ / _uDepthWEpi_ +_NearZero_) _ELSE_ 1.0 / (( _uQInEpi_ + _uQPrec_ ) / _mmPerm_ / _uDepthWEpi_ +_NearZero_) _ENDIF_
```

### `_uTauWatHyp_`  [_d_]
- **Description**: Water_residence_time
- **Equation**:

```
_uTauWatHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ )_THEN_ -9999 _ELSE_ 1.0 / ((_uQInHyp_ + _uQInSeep_ ) / _mmPerm_ / _uDepthWHyp_ +_NearZero_) _ENDIF_
```

### `_uTauWat_`  [_d_]
- **Description**: Water_residence_time
- **Equation**:

```
_uTauWat_ = 1.0 / ((_uQPrec_ + _uQInEpi_ + _uQInHyp_ + _uQInSeep_ ) / _mmPerm_ / _uDepthW_ +_NearZero_)
```

### `_uTauSubstHyp_`  [_d_]
- **Description**: Residence_time_of_substances
- **Equation**:

```
_uTauSubstHyp_ = 1.0 / (_ukOutHyp_+_NearZero_)
```

### `_vTranDepthW_`  [_m_*_d_^-1]
- **Description**: Change_in_water_depth
- **Equation**:

```
_vTranDepthW_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ (_uQInEpi_ + _uQInHyp_ + _uQPrec_ + _uQInSeep_ - _uQEv_ - _uQOutInf_ - _uQOutHyp_ - _uQOutEpi_ - _uQOutCor_) / _mmPerm_ _ELSE_ ((_uQInEpi_ + _uQInHyp_ + _uQPrec_ + _uQInSeep_ - _uQEv_ - _uQOutInf_ - _uQOutHyp_ - _uQOutEpi_ - _uQOutCor_) / _mmPerm_) / (1.0 + _fMarsh_) _ENDIF_
```

### `_vTranHypEpiW_`  [_m_*_d_^-1]
- **Description**: Exchange_flux_of_water_over_the_vertical_water_layers
- **Equation**:

```
_vTranHypEpiW_ = _IF_ (_InclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ ( _uDepthW_ -_uDepthMixMeas_ _LT_ _cMinDepthHypEpi_ ) _THEN_ ( _uDepthW_ - _cMinDepthHypEpi_ -_uDepthWEpi_ ) * _kExchW_ _ELSEIF_ ( _uDepthMixMeas_ _LT_ _cMinDepthHypEpi_ ) _THEN_ ( _cMinDepthHypEpi_ -_uDepthWEpi_ ) * _kExchW_ _ELSE_ ( _uDepthMixMeas_ -_uDepthWEpi_ ) * _kExchW_ _ENDIF_
```

### `_vDeltaWHyp_`  [_m_*_d_^-1]
- **Description**: Change_in_water_depth_hypolimnion
- **Equation**:

```
_vDeltaWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_ ) _THEN_ (_uQInHyp_ + _uQInSeep_ - _uQOutInf_ - _uQOutHyp_) / _mmPerm_ _ELSE_ (_uQInHyp_ + _uQInSeep_ - _uQOutInf_ - _uQOutHyp_) / _mmPerm_ / (1.0 + _fMarsh_ ) _ENDIF_
```

### `_vDeltaWEpi_`  [_m_*_d_^-1]
- **Description**: Change_in_water_depth_epilimnion
- **Equation**:

```
_vDeltaWEpi_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _AND_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_ ) _THEN_ (_uQInEpi_ + _uQPrec_ + _uQInSeep_ - _uQEv_ - _uQOutEpi_ - _uQOutInf_ - _uQOutCor_) / _mmPerm_ _ELSEIF_ (_aInclStrat_ _EQ_ _TRUE_) _AND_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_ ) _THEN_ (_uQInEpi_ + _uQPrec_ - _uQEv_ - _uQOutEpi_ - _uQOutCor_) / _mmPerm_ _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_) _AND_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_ ) _THEN_ (_uQInEpi_ + _uQPrec_ + _uQInSeep_ - _uQEv_ - _uQOutEpi_ - _uQOutInf_ - _uQOutCor_) / _mmPerm_ / (1.0 + _fMarsh_ ) _ELSE_ (_uQInEpi_ + _uQPrec_ - _uQEv_ - _uQOutEpi_ - _uQOutCor_) / _mmPerm_ / (1.0 + _fMarsh_ ) _ENDIF_
```

### `_wDAdvIMW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_inorganic_matter_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvIMW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDIMWHyp_ _ELSE_ _vTranHypEpiW_ * _oDIMWEpi_ _ENDIF_
```

### `_wPAdvPO4W_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_PO4_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvPO4W_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPO4WHyp_ _ELSE_ _vTranHypEpiW_ * _oPO4WEpi_ _ENDIF_
```

### `_wPAdvAIMW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_adsorbed_to_inorganic_matter_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvAIMW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPAIMWHyp_ _ELSE_ _vTranHypEpiW_ * _oPAIMWEpi_ _ENDIF_
```

### `_wNAdvNH4W_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_NH4_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvNH4W_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNH4WHyp_ _ELSE_ _vTranHypEpiW_ * _oNH4WEpi_ _ENDIF_
```

### `_wNAdvNO3W_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_NO3_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvNO3W_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNO3WHyp_ _ELSE_ _vTranHypEpiW_ * _oNO3WEpi_ _ENDIF_
```

### `_wSiAdvSiO2W_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_SiO2_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wSiAdvSiO2W_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oSiO2WHyp_ _ELSE_ _vTranHypEpiW_ * _oSiO2WEpi_ _ENDIF_
```

### `_wO2AdvW_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_O2_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wO2AdvW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oO2WHyp_ _ELSE_ _vTranHypEpiW_ * _oO2WEpi_ _ENDIF_
```

### `_wDAdvDetW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_of_detritus_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvDetW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDDetWHyp_ _ELSE_ _vTranHypEpiW_ * _oDDetWEpi_ _ENDIF_
```

### `_wPAdvDetW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_detritus_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvDetW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPDetWHyp_ _ELSE_ _vTranHypEpiW_ * _oPDetWEpi_ _ENDIF_
```

### `_wNAdvDetW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_detritus_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvDetW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNDetWHyp_ _ELSE_ _vTranHypEpiW_ * _oNDetWEpi_ _ENDIF_
```

### `_wSiAdvDetW_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_Si_in_detritus_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wSiAdvDetW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oSiDetWHyp_ _ELSE_ _vTranHypEpiW_ * _oSiDetWEpi_ _ENDIF_
```

### `_wDAdvDiatW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_diatoms_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvDiatW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDDiatWHyp_ _ELSE_ _vTranHypEpiW_ * _oDDiatWEpi_ _ENDIF_
```

### `_wPAdvDiatW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_diatoms_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvDiatW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPDiatWHyp_ _ELSE_ _vTranHypEpiW_ * _oPDiatWEpi_ _ENDIF_
```

### `_wNAdvDiatW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_diatoms_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvDiatW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNDiatWHyp_ _ELSE_ _vTranHypEpiW_ * _oNDiatWEpi_ _ENDIF_
```

### `_wSiAdvDiatW_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_Si_in_diatoms_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wSiAdvDiatW_ = _vTranHypEpiW_ * _cSiDDiat_
```

### `_wDAdvGrenW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_green_algae_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvGrenW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDGrenWHyp_ _ELSE_ _vTranHypEpiW_ * _oDGrenWEpi_ _ENDIF_
```

### `_wPAdvGrenW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_green_algae_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvGrenW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPGrenWHyp_ _ELSE_ _vTranHypEpiW_ * _oPGrenWEpi_ _ENDIF_
```

### `_wNAdvGrenW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_green_algae_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvGrenW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNGrenWHyp_ _ELSE_ _vTranHypEpiW_ * _oNGrenWEpi_ _ENDIF_
```

### `_wDAdvBlueW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_blue_greens_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvBlueW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDBlueWHyp_ _ELSE_ _vTranHypEpiW_ * _oDBlueWEpi_ _ENDIF_
```

### `_wPAdvBlueW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_blue_greens_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvBlueW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPBlueWHyp_ _ELSE_ _vTranHypEpiW_ * _oPBlueWEpi_ _ENDIF_
```

### `_wNAdvBlueW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_blue_greens_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvBlueW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNBlueWHyp_ _ELSE_ _vTranHypEpiW_ * _oNBlueWEpi_ _ENDIF_
```

### `_wDAdvZooW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_zooplankton_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvZooW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oDZooHyp_ _ELSE_ _vTranHypEpiW_ * _oDZooEpi_ _ENDIF_
```

### `_wPAdvZooW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_zooplankton_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wPAdvZooW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oPZooHyp_ _ELSE_ _vTranHypEpiW_ * _oPZooEpi_ _ENDIF_
```

### `_wNAdvZooW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_zooplankton_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wNAdvZooW_ = _IF_ ( _vTranHypEpiW_ _GT_ 0.0) _THEN_ _vTranHypEpiW_ * _oNZooHyp_ _ELSE_ _vTranHypEpiW_ * _oNZooEpi_ _ENDIF_
```

### `_wDAdvIMWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_inorganic_matter_between_hypolimnion_and_epilimnion
- **Equation**:

```
_wDAdvIMWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDIMWEpi_ _ELSE_ _vTranDepthW_ *  _oDIMWM_ _ENDIF_
```

### `_wPAdvPO4WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_PO4_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvPO4WM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPO4WEpi_ _ELSE_ _vTranDepthW_ *  _oPO4WM_ _ENDIF_
```

### `_wPAdvAIMWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_adsorbed_to_inorganic_matter_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvAIMWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPAIMWEpi_ _ELSE_ _vTranDepthW_ *  _oPAIMWM_ _ENDIF_
```

### `_wNAdvNH4WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_NH4_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvNH4WM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNH4WEpi_ _ELSE_ _vTranDepthW_ *  _oNH4WM_ _ENDIF_
```

### `_wNAdvNO3WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_NO3_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvNO3WM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNO3WEpi_ _ELSE_ _vTranDepthW_ *  _oNO3WM_ _ENDIF_
```

### `_wSiAdvSiO2WM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_SiO2_between_marsh_and_epilimnion
- **Equation**:

```
_wSiAdvSiO2WM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oSiO2WEpi_ _ELSE_ _vTranDepthW_ *  _oSiO2WM_ _ENDIF_
```

### `_wO2AdvWM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_O2_between_marsh_and_epilimnion
- **Equation**:

```
_wO2AdvWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oO2WEpi_ _ELSE_ _vTranDepthW_ *  _oO2WM_ _ENDIF_
```

### `_wDAdvDetWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_of_detritus_between_marsh_and_epilimnion
- **Equation**:

```
_wDAdvDetWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDDetWEpi_ _ELSE_ _vTranDepthW_ *  _oDDetWM_ _ENDIF_
```

### `_wPAdvDetWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_detritus_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvDetWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPDetWEpi_ _ELSE_ _vTranDepthW_ *  _oPDetWM_ _ENDIF_
```

### `_wNAdvDetWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_detritus_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvDetWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNDetWEpi_ _ELSE_ _vTranDepthW_ *  _oNDetWM_ _ENDIF_
```

### `_wSiAdvDetWM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_Si_in_detritus_between_marsh_and_epilimnion
- **Equation**:

```
_wSiAdvDetWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oSiDetWEpi_ _ELSE_ _vTranDepthW_ *  _oSiDetWM_ _ENDIF_
```

### `_wDAdvDiatWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_diatoms_between_marsh_and_epilimnion
- **Equation**:

```
_wDAdvDiatWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDDiatWEpi_ _ELSE_ _vTranDepthW_ *  _oDDiatWM_ _ENDIF_
```

### `_wPAdvDiatWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_diatoms_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvDiatWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPDiatWEpi_ _ELSE_ _vTranDepthW_ *  _oPDiatWM_ _ENDIF_
```

### `_wNAdvDiatWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_diatoms_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvDiatWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNDiatWEpi_ _ELSE_ _vTranDepthW_ *  _oNDiatWM_ _ENDIF_
```

### `_wDAdvGrenWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_green_algae_between_marsh_and_epilimnion
- **Equation**:

```
_wDAdvGrenWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDGrenWEpi_ _ELSE_ _vTranDepthW_ *  _oDGrenWM_ _ENDIF_
```

### `_wPAdvGrenWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_green_algae_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvGrenWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPGrenWEpi_ _ELSE_ _vTranDepthW_ *  _oPGrenWM_ _ENDIF_
```

### `_wNAdvGrenWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_green_algae_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvGrenWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNGrenWEpi_ _ELSE_ _vTranDepthW_ *  _oNGrenWM_ _ENDIF_
```

### `_wDAdvBlueWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_blue_greens_between_marsh_and_epilimnion
- **Equation**:

```
_wDAdvBlueWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDBlueWEpi_ _ELSE_ _vTranDepthW_ *  _oDBlueWM_ _ENDIF_
```

### `_wPAdvBlueWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_blue_greens_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvBlueWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPBlueWEpi_ _ELSE_ _vTranDepthW_ *  _oPBlueWM_ _ENDIF_
```

### `_wNAdvBlueWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_blue_greens_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvBlueWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNBlueWEpi_ _ELSE_ _vTranDepthW_ *  _oNBlueWM_ _ENDIF_
```

### `_wDAdvZooWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_DW_in_zooplankton_between_marsh_and_epilimnion
- **Equation**:

```
_wDAdvZooWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oDZooEpi_ _ELSE_ _vTranDepthW_ *  _oDZooM_ _ENDIF_
```

### `_wPAdvZooWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_P_in_zooplankton_between_marsh_and_epilimnion
- **Equation**:

```
_wPAdvZooWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oPZooEpi_ _ELSE_ _vTranDepthW_ *  _oPZooM_ _ENDIF_
```

### `_wNAdvZooWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Advective_exchange_flux_of_N_in_zooplankton_between_marsh_and_epilimnion
- **Equation**:

```
_wNAdvZooWM_= _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ( _vTranDepthW_ _GT_ 0.0) _THEN_ _vTranDepthW_ * _oNZooEpi_ _ELSE_ _vTranDepthW_ *  _oNZooM_ _ENDIF_
```

### `_uExchMaxW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusive_exchange_rate_between_epilimnion_and_hypolimnion
- **Equation**:

```
_uExchMaxW_ =   _IF_ ( _aInclStrat_ _EQ_ _TRUE_) _THEN_ _kExchMaxW_ /( _aStrat_* _fMeta_ * _uDepthW_ + _cDepthMetaMin_ ) _ELSE_ 0.0 _ENDIF_
```

### `_akExchMHyp_`  [_m_^3*_m_^-3*_d_^-1]
- **Description**: Marsh_water_exchange_coefficient
- **Equation**:

```
_akExchMHyp_ = 0.0
```

### `_akExchLHyp_`  [_m_^3*_m_^-3*_d_^-1]
- **Description**: Lake_water_exchange_coefficient
- **Equation**:

```
_akExchLHyp_ = 0.0
```

### `_uTauSubstEpi_`  [_d_]
- **Description**: Residence_time_of_substances
- **Equation**:

```
_uTauSubstEpi_ = 1.0 / (_ukOutEpi_+_NearZero_)
```

### `_akExchMEpi_`  [_m_^3*_m_^-3*_d_^-1]
- **Description**: Marsh_water_exchange_coefficient
- **Equation**:

```
_akExchMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kExchMaxM_ * _hfMarsh_ /(_hfMarsh_ + _fMarsh_)  _ELSE_ 0.0 _ENDIF_
```

### `_afVolMarshEpi_`  [_m_^3*_m_^-3]
- **Description**: Relative_marsh_volume
- **Equation**:

```
_afVolMarshEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fMarsh_ * _uDepthWM_ / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_akExchLEpi_`  [_m_^3*_m_^-3*_d_^-1]
- **Description**: Lake_water_exchange_coefficient
- **Equation**:

```
_akExchLEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ * _afVolMarshEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_ukDilSurf_`  [_d_^-1]
- **Description**: Dilution_rate_of_substances
- **Equation**:

```
_ukDilSurf_ = _ukOutEpi_
```

## Fijv_process  (3 equations)

### `_uFiJvMortHyp_`  [0]
- **Description**: Fijv_fraction
- **Equation**:

```
_uFiJvMortHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiJvMortHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uFiJvEgesHyp_`  [0]
- **Description**: Fijv_fraction
- **Equation**:

```
_uFiJvEgesHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiJvEgesHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uFiJvExcrHyp_`  [0]
- **Description**: Fijv_fraction
- **Equation**:

```
_uFiJvExcrHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiJvExcrHyp_ _ELSE_ 0.0 _ENDIF_
```

## Fiad_process  (3 equations)

### `_uFiAdMortHyp_`  [0]
- **Description**: Fiad_fraction
- **Equation**:

```
_uFiAdMortHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiAdMortHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uFiAdEgesHyp_`  [0]
- **Description**: Fiad_fraction
- **Equation**:

```
_uFiAdEgesHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiAdEgesHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uFiAdExcrHyp_`  [0]
- **Description**: Fiad_fraction
- **Equation**:

```
_uFiAdExcrHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fFiAdExcrHyp_ _ELSE_ 0.0 _ENDIF_
```

## Pisc_process  (3 equations)

### `_uPiscMortHyp_`  [0]
- **Description**: Pisc_fraction
- **Equation**:

```
_uPiscMortHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fPiscMortHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uPiscEgesHyp_`  [0]
- **Description**: Pisc_fraction
- **Equation**:

```
_uPiscEgesHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fPiscEgesHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uPiscExcrHyp_`  [0]
- **Description**: Pisc_fraction
- **Equation**:

```
_uPiscExcrHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fPiscExcrHyp_ _ELSE_ 0.0 _ENDIF_
```

## Gras_fish_processes  (52 equations)

### `_uGrasMortHyp_`  [0]
- **Description**: Grass_carp_fraction
- **Equation**:

```
_uGrasMortHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasMortHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uGrasEgesHyp_`  [0]
- **Description**: Grass_carp_fraction
- **Equation**:

```
_uGrasEgesHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasEgesHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uGrasExcrHyp_`  [0]
- **Description**: Grass_carp_fraction
- **Equation**:

```
_uGrasExcrHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _fGrasExcrHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_uFunTmGras_`  [0]
- **Description**: temp_function_of_Grass_carp
- **Equation**:

```
_uFunTmGras_ = _EXP_(-0.5 /(_cSigTmGras_*_cSigTmGras_) *((_uTmEpi_ - _cTmOptGras_)*(_uTmEpi_ - _cTmOptGras_) - (_cTmRef_ - _cTmOptGras_)*(_cTmRef_ - _cTmOptGras_)))
```

### `_akDIncrGras_`  [_d_^-1]
- **Description**: intrinsic_net_increase_rate_of_Grass_carp
- **Equation**:

```
_akDIncrGras_ = (_kDAssGras_ - _kDRespGras_) * _uFunTmGras_ - _kMortGras_
```

### `_ukHarvGras_`  [_d_^-1]
- **Description**: fish_harvesting_constant
- **Equation**:

```
_ukHarvGras_ = _IF_ (_COS_(2.0*_Pi_ * _sTime_ / _DaysPerYear_) _GT_ 0.1) _THEN_ _kHarvGrasWin_ _ELSE_ _kHarvGrasSum_ _ENDIF_
```

### `_aDSatGras_`  [0]
- **Description**: food_limitation_function_of_Grass_carp
- **Equation**:

```
_aDSatGras_ = _aDVeg_*_aDVeg_ /(_hDVegGras_*_hDVegGras_ + _aDVeg_*_aDVeg_)
```

### `_tDEnvGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: environmental_correction_of_Grass_carp
- **Equation**:

```
_tDEnvGras_ = _MAX_(0.0,_akDIncrGras_ / _cDCarrGras_ * _aDGras_*_aDGras_)
```

### `_tDAssGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: assimilation_of_Grass_carp
- **Equation**:

```
_tDAssGras_ = _aDSatGras_ *(_kDAssGras_ * _uFunTmGras_ * _aDGras_ - _tDEnvGras_)
```

### `_tDConsGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: consumption_of_Grass_carp
- **Equation**:

```
_tDConsGras_ = _tDAssGras_ / _fDAssGras_
```

### `_tDEgesGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: egestion_of_Grass_carp
- **Equation**:

```
_tDEgesGras_ = _tDConsGras_ - _tDAssGras_
```

### `_tDMortGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: mortality_of_Grass_carp(incl_environmental_correction)
- **Equation**:

```
_tDMortGras_ = _kMortGras_ * _aDGras_ +(1.0 - _aDSatGras_) * _tDEnvGras_
```

### `_tDMigrGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: migration_flux_of_Grass_carp
- **Equation**:

```
_tDMigrGras_ = _kMigrGras_ *(_cDGrasIn_ - _aDGras_)
```

### `_tDRespGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: respiration_of_Grass_carp
- **Equation**:

```
_tDRespGras_ = _kDRespGras_ * _uFunTmGras_ * _aDGras_
```

### `_tDMortGrasBot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: part_of_died_fish_DW_fixed_in_bones_AND_scales
- **Equation**:

```
_tDMortGrasBot_ = _fDBone_ * _tDMortGras_
```

### `_tDMortGrasDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: part_of_died_Grass_carp_DW_becoming_detritus
- **Equation**:

```
_tDMortGrasDet_ = _tDMortGras_ - _tDMortGrasBot_
```

### `_tDHarvGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: harvesting_of_Grass_carp
- **Equation**:

```
_tDHarvGras_ = _ukHarvGras_ * _aDGras_
```

### `_aPGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: total_P_in_Grass_carp
- **Equation**:

```
_aPGras_ = _cPDGras_ * _aDGras_
```

### `_tPConsGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: total_P_consumption_by_Grass_carp
- **Equation**:

```
_tPConsGras_ = _rPDVeg_ * _tDConsGras_
```

### `_rPDFoodGras_`  [_gP_*_gDW_^-1]
- **Description**: average_P/D_ratio_of_Grass_carp_food
- **Equation**:

```
_rPDFoodGras_ = _tPConsGras_ / _tDConsGras_
```

### `_tDConsGrasNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Consumption_of_Gras_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDConsGrasNut_ = (_tDAssGras_ / _fDAssGras_) * _MAX_ (1.0, _cNDGras_ / _rNDFoodGras_ * _fDAssGras_, _cPDGras_ / _rPDFoodGras_ * _fDAssGras_)
```

### `_tDEgesGrasNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_Gras_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDEgesGrasNut_ = _tDConsGrasNut_ - _tDAssGras_
```

### `_tPConsGrasNut_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_consumption_by_Gras
- **Equation**:

```
_tPConsGrasNut_ = _rPDVeg_ * _tDConsGrasNut_
```

### `_tNConsGrasNut_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_consumption_by_Gras
- **Equation**:

```
_tNConsGrasNut_ = _rNDVeg_ * _tDConsGrasNut_
```

### `_afPAssGras_`  [0]
- **Description**: P_assim_efficiency_of_Grass_carp
- **Equation**:

```
_afPAssGras_ = _MIN_(1.0,_cPDGras_ / _rPDFoodGras_ * _fDAssGras_)
```

### `_tPAssGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_of_Grass_carp
- **Equation**:

```
_tPAssGras_ = _afPAssGras_ * _tPConsGras_
```

### `_tPEgesGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: egestion_of_Grass_carp
- **Equation**:

```
_tPEgesGras_ = _tPConsGras_ - _tPAssGras_
```

### `_tPEgesGrasPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_egestion_of_Grass_carp
- **Equation**:

```
_tPEgesGrasPO4_ = _fDissEgesGras_ * _tPEgesGras_
```

### `_tPEgesGrasDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: detrital_P_egestion_of_Grass_carp
- **Equation**:

```
_tPEgesGrasDet_ = _tPEgesGras_ - _tPEgesGrasPO4_
```

### `_tPExcrGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: respiration_of_Grass_carp
- **Equation**:

```
_tPExcrGras_ = _cPDGras_ * _tDRespGras_
```

### `_tPMortGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: mortality_of_Grass_carp
- **Equation**:

```
_tPMortGras_ = _cPDGras_ * _tDMortGras_
```

### `_tPMortGrasBot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: part_of_died_Grass_carp_P_fixed_in_bones_AND_scales
- **Equation**:

```
_tPMortGrasBot_ = _fPBone_ * _tPMortGras_
```

### `_tPMortGrasPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: part_of_died_fish_P_becoming_dissolved_P
- **Equation**:

```
_tPMortGrasPO4_ = _fDissMortGras_ *(_tPMortGras_ - _tPMortGrasBot_)
```

### `_tPMortGrasDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: part_of_died_Grass_carp_P_becoming_detrital_P
- **Equation**:

```
_tPMortGrasDet_ = _tPMortGras_ - _tPMortGrasBot_ - _tPMortGrasPO4_
```

### `_tPMigrGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: net_migration_flux
- **Equation**:

```
_tPMigrGras_ = _kMigrGras_ *(_cPDGras_ * _cDGrasIn_ - _aPGras_)
```

### `_tPHarvGras_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: harvesting_of_Grass_carp
- **Equation**:

```
_tPHarvGras_ = _cPDGras_ * _tDHarvGras_
```

### `_aNGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: total_N_in_Grass_carp
- **Equation**:

```
_aNGras_ = _cNDGras_ * _aDGras_
```

### `_tNConsGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: total_N_consumption_by_Grass_carp
- **Equation**:

```
_tNConsGras_ = _rNDVeg_ * _tDConsGras_
```

### `_rNDFoodGras_`  [_gN_*_gDW_^-1]
- **Description**: average_N/D_ratio_of_Grass_carp_food
- **Equation**:

```
_rNDFoodGras_ = _tNConsGras_ / _tDConsGras_
```

### `_afNAssGras_`  [0]
- **Description**: N_assim_efficiency_of_Grass_carp
- **Equation**:

```
_afNAssGras_ = _MIN_(1.0,_cNDGras_ / _rNDFoodGras_ * _fDAssGras_)
```

### `_tNAssGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_of_Grass_carp
- **Equation**:

```
_tNAssGras_ = _afNAssGras_ * _tNConsGras_
```

### `_tNEgesGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: egestion_of_Grass_carp
- **Equation**:

```
_tNEgesGras_ = _tNConsGras_ - _tNAssGras_
```

### `_tNEgesGrasNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: SRN_egestion_of_Grass_carp
- **Equation**:

```
_tNEgesGrasNH4_ = _fDissEgesGras_ * _tNEgesGras_
```

### `_tNEgesGrasDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: detrital_N_egestion_of_Grass_carp
- **Equation**:

```
_tNEgesGrasDet_ = _tNEgesGras_ - _tNEgesGrasNH4_
```

### `_tNExcrGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: respiration_of_Grass_carp
- **Equation**:

```
_tNExcrGras_ = _cNDGras_ * _tDRespGras_
```

### `_tNMortGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: mortality_of_Grass_carp
- **Equation**:

```
_tNMortGras_ = _cNDGras_ * _tDMortGras_
```

### `_tNMortGrasBot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: part_of_died_Grass_carp_N_fixed_in_bones_AND_scales
- **Equation**:

```
_tNMortGrasBot_ = _fDBone_ * _tNMortGras_
```

### `_tNMortGrasNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: part_of_died_fish_N_becoming_dissolved_N
- **Equation**:

```
_tNMortGrasNH4_ = _fDissMortGras_ *(_tNMortGras_ - _tNMortGrasBot_)
```

### `_tNMortGrasDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: part_of_died_Grass_carp_N_becoming_detrital_N
- **Equation**:

```
_tNMortGrasDet_ = _tNMortGras_ - _tNMortGrasBot_ - _tNMortGrasNH4_
```

### `_tNMigrGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: net_migration_flux
- **Equation**:

```
_tNMigrGras_ = _kMigrGras_ *(_cNDGras_ * _cDGrasIn_ - _aNGras_)
```

### `_tNHarvGras_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: harvesting_of_Grass_carp
- **Equation**:

```
_tNHarvGras_ = _cNDGras_ * _tDHarvGras_
```

### `_aGrowGras_`  [_d_^-1]
- **Description**: per_gDW_veg_consumption_per_gDW_Grass_carp
- **Equation**:

```
_aGrowGras_ = _tDGrazVegGras_ / _aDGras_
```

## Exchange_fluxes_for_hypolimnion_and_epilimnion  (51 equations)

### `_afVolHypEpi_`  [_m_^3*_m_^-3]
- **Description**: Fraction_change_in_hypolimnion_to_epilimnion_volume
- **Equation**:

```
_afVolHypEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _uDepthWHyp_ _GT_ _NearZero_) _THEN_  _uDepthWHyp_ / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_akExchWHyp_`  [_d_^-1]
- **Description**: Diffusive_exchange_rate_of_hypolimnion
- **Equation**:

```
_akExchWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ _AND_ _uDepthWHyp_ _GT_ _NearZero_) _THEN_  ( _uExchMaxW_ ) / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_akExchWEpi_`  [_m_^3*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_rate_of_epilimnion
- **Equation**:

```
_akExchWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ * _afVolHypEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchIMWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_inorganic_matter_from_and_to_hypolimnion
- **Equation**:

```
_wDExchIMWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDIMWHyp_ - _oDIMWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_PO4_from_and_to_hypolimnion
- **Equation**:

```
_wPExchPO4WHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPO4WHyp_ - _oPO4WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_adsorbed_to_inorganic_matter_from_and_to_hypolimnion
- **Equation**:

```
_wPExchAIMWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPAIMWHyp_ - _oPAIMWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_NH4_from_and_to_hypolimnion
- **Equation**:

```
_wNExchNH4WHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNH4WHyp_ - _oNH4WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_NO3_from_and_to_hypolimnion
- **Equation**:

```
_wNExchNO3WHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNO3WHyp_ - _oNO3WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2WHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_and_to_hypolimnion
- **Equation**:

```
_wSiExchSiO2WHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oSiO2WHyp_ - _oSiO2WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_and_to_hypolimnion
- **Equation**:

```
_wO2ExchWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oO2WHyp_ - _oO2WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_of_detritus_from_and_to_hypolimnion
- **Equation**:

```
_wDExchDetWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDDetWHyp_ - _oDDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_and_to_hypolimnion
- **Equation**:

```
_wPExchDetWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPDetWHyp_ - _oPDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_and_to_hypolimnion
- **Equation**:

```
_wNExchDetWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNDetWHyp_ - _oNDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_and_to_hypolimnion
- **Equation**:

```
_wSiExchDetWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oSiDetWHyp_ - _oSiDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_and_to_hypolimnion
- **Equation**:

```
_wDExchDiatWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDDiatWHyp_ - _oDDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_and_to_hypolimnion
- **Equation**:

```
_wPExchDiatWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPDiatWHyp_ - _oPDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_and_to_hypolimnion
- **Equation**:

```
_wNExchDiatWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNDiatWHyp_ - _oNDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_and_to_hypolimnion
- **Equation**:

```
_wSiExchDiatWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _cSiDDiat_ * _wDExchDiatWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_and_to_hypolimnion
- **Equation**:

```
_wDExchGrenWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDGrenWHyp_ - _oDGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_and_to_hypolimnion
- **Equation**:

```
_wPExchGrenWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPGrenWHyp_ - _oPGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_and_to_hypolimnion
- **Equation**:

```
_wNExchGrenWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNGrenWHyp_ - _oNGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_and_to_hypolimnion
- **Equation**:

```
_wDExchBlueWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDBlueWHyp_ - _oDBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_and_to_hypolimnion
- **Equation**:

```
_wPExchBlueWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPBlueWHyp_ - _oPBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_and_to_hypolimnion
- **Equation**:

```
_wNExchBlueWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNBlueWHyp_ - _oNBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_and_to_hypolimnion
- **Equation**:

```
_wDExchZooWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oDZooHyp_ - _oDZooEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_and_to_hypolimnion
- **Equation**:

```
_wPExchZooWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oPZooHyp_ - _oPZooEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_and_to_hypolimnion
- **Equation**:

```
_wNExchZooWHyp_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWHyp_ *(_oNZooHyp_ - _oNZooEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchIMWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_inorganic_matter_from_and_to_epilimnion
- **Equation**:

```
_wDExchIMWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDIMWHyp_ - _oDIMWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_PO4_from_and_to_epilimnion
- **Equation**:

```
_wPExchPO4WEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPO4WHyp_ - _oPO4WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_adsorbed_to_inorganic_matter_from_and_to_epilimnion
- **Equation**:

```
_wPExchAIMWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPAIMWHyp_ - _oPAIMWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_NH4_from_and_to_epilimnion
- **Equation**:

```
_wNExchNH4WEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNH4WHyp_ - _oNH4WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_NO3_from_and_to_epilimnion
- **Equation**:

```
_wNExchNO3WEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNO3WHyp_ - _oNO3WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2WEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_and_to_epilimnion
- **Equation**:

```
_wSiExchSiO2WEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oSiO2WHyp_ - _oSiO2WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_and_to_epilimnion
- **Equation**:

```
_wO2ExchWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oO2WHyp_ - _oO2WEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_of_detritus_from_and_to_epilimnion
- **Equation**:

```
_wDExchDetWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDDetWHyp_ - _oDDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_and_to_epilimnion
- **Equation**:

```
_wPExchDetWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPDetWHyp_ - _oPDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_and_to_epilimnion
- **Equation**:

```
_wNExchDetWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNDetWHyp_ - _oNDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_and_to_epilimnion
- **Equation**:

```
_wSiExchDetWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oSiDetWHyp_ - _oSiDetWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_and_to_epilimnion
- **Equation**:

```
_wDExchDiatWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDDiatWHyp_ - _oDDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_and_to_epilimnion
- **Equation**:

```
_wPExchDiatWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPDiatWHyp_ - _oPDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_and_to_epilimnion
- **Equation**:

```
_wNExchDiatWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNDiatWHyp_ - _oNDiatWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_and_to_epilimnion
- **Equation**:

```
_wSiExchDiatWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _cSiDDiat_ * _wDExchDiatWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_and_to_epilimnion
- **Equation**:

```
_wDExchGrenWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDGrenWHyp_ - _oDGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_and_to_epilimnion
- **Equation**:

```
_wPExchGrenWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPGrenWHyp_ - _oPGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_and_to_epilimnion
- **Equation**:

```
_wNExchGrenWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNGrenWHyp_ - _oNGrenWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_and_to_epilimnion
- **Equation**:

```
_wDExchBlueWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDBlueWHyp_ - _oDBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_and_to_epilimnion
- **Equation**:

```
_wPExchBlueWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPBlueWHyp_ - _oPBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_and_to_epilimnion
- **Equation**:

```
_wNExchBlueWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNBlueWHyp_ - _oNBlueWEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_and_to_epilimnion
- **Equation**:

```
_wDExchZooWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oDZooHyp_ - _oDZooEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_and_to_epilimnion
- **Equation**:

```
_wPExchZooWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oPZooHyp_ - _oPZooEpi_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_and_to_epilimnion
- **Equation**:

```
_wNExchZooWEpi_= _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _akExchWEpi_ *(_oNZooHyp_ - _oNZooEpi_) _ELSE_ 0.0 _ENDIF_
```

## Lake_water_total_phytoplankton  (9 equations)

### `_oDPhytWHyp_`  [_gDW_*_m_^-3]
- **Description**: Total_DW_phytoplankton_in_lake_water
- **Equation**:

```
_oDPhytWHyp_ = _oDDiatWHyp_ + _oDGrenWHyp_ + _oDBlueWHyp_
```

### `_oPPhytWHyp_`  [_gP_*_m_^-3]
- **Description**: Total_P_phytoplankton_in_lake_water
- **Equation**:

```
_oPPhytWHyp_ = _oPDiatWHyp_ + _oPGrenWHyp_ + _oPBlueWHyp_
```

### `_oNPhytWHyp_`  [_gN_*_m_^-3]
- **Description**: Total_N_phytoplankton_in_lake_water
- **Equation**:

```
_oNPhytWHyp_ = _oNDiatWHyp_ + _oNGrenWHyp_ + _oNBlueWHyp_
```

### `_aDPhytS_`  [_gDW_*_m_^-2]
- **Description**: Total_DW_phytoplankton_on_lake_sediment
- **Equation**:

```
_aDPhytS_ = _aDDiatS_ + _aDGrenS_ + _aDBlueS_
```

### `_aPPhytS_`  [_gP_*_m_^-2]
- **Description**: Total_P_phytoplankton_on_lake_sediment
- **Equation**:

```
_aPPhytS_ = _aPDiatS_ + _aPGrenS_ + _aPBlueS_
```

### `_aNPhytS_`  [_gN_*_m_^-2]
- **Description**: Total_N_phytoplankton_on_lake_sediment
- **Equation**:

```
_aNPhytS_ = _aNDiatS_ + _aNGrenS_ + _aNBlueS_
```

### `_oDPhytWEpi_`  [_gDW_*_m_^-3]
- **Description**: Total_DW_phytoplankton_in_lake_water
- **Equation**:

```
_oDPhytWEpi_ = _oDDiatWEpi_ + _oDGrenWEpi_ + _oDBlueWEpi_
```

### `_oPPhytWEpi_`  [_gP_*_m_^-3]
- **Description**: Total_P_phytoplankton_in_lake_water
- **Equation**:

```
_oPPhytWEpi_ = _oPDiatWEpi_ + _oPGrenWEpi_ + _oPBlueWEpi_
```

### `_oNPhytWEpi_`  [_gN_*_m_^-3]
- **Description**: Total_N_phytoplankton_in_lake_water
- **Equation**:

```
_oNPhytWEpi_ = _oNDiatWEpi_ + _oNGrenWEpi_ + _oNBlueWEpi_
```

## Lake_water_total_DW_variables  (5 equations)

### `_oDOMWEpi_`  [_gDW_*_m_^-3]
- **Description**: Organic_seston
- **Equation**:

```
_oDOMWEpi_ = _oDDetWEpi_ + _oDPhytWEpi_
```

### `_oDOMWHyp_`  [_gDW_*_m_^-3]
- **Description**: Organic_seston
- **Equation**:

```
_oDOMWHyp_ = _oDDetWHyp_ + _oDPhytWHyp_
```

### `_oTDOMW_`  [_gDW_*_m_^-3]
- **Description**: Organic_seston
- **Equation**:

```
_oTDOMW_ = _oDOMWEpi_ + _oDOMWHyp_
```

### `_oDSestWHyp_`  [_gDW_*_m_^-3]
- **Description**: Total_seston
- **Equation**:

```
_oDSestWHyp_ = _oDOMWHyp_ + _oDIMWHyp_
```

### `_oDSestWEpi_`  [_gDW_*_m_^-3]
- **Description**: Total_seston
- **Equation**:

```
_oDSestWEpi_ = _oDOMWEpi_ + _oDIMWEpi_
```

## Lake_water_total_P_variables  (8 equations)

### `_oPOMWHyp_`  [_gP_*_m_^-3]
- **Description**: Organic_P_in_water
- **Equation**:

```
_oPOMWHyp_ = _oPPhytWHyp_ + _oPDetWHyp_
```

### `_oPSestWHyp_`  [_gP_*_m_^-3]
- **Description**: Total_seston_P_(incl_adsorbed
- **Equation**:

```
_oPSestWHyp_ = _oPPhytWHyp_ + _oPDetWHyp_ + _oPAIMWHyp_
```

### `_oPInorgWHyp_`  [_gP_*_m_^-3]
- **Description**: Inorganic_P_in_water
- **Equation**:

```
_oPInorgWHyp_ = _oPO4WHyp_ + _oPAIMWHyp_
```

### `_oPTotWHyp_`  [_gP_*_m_^-3]
- **Description**: Total_P_in_water_(excl_animals_AND_vegetation)
- **Equation**:

```
_oPTotWHyp_ = _oPSestWHyp_ + _oPO4WHyp_
```

### `_oPOMWEpi_`  [_gP_*_m_^-3]
- **Description**: Organic_P_in_water
- **Equation**:

```
_oPOMWEpi_ = _oPPhytWEpi_ + _oPDetWEpi_
```

### `_oPSestWEpi_`  [_gP_*_m_^-3]
- **Description**: Total_seston_P_(incl_adsorbed
- **Equation**:

```
_oPSestWEpi_ = _oPPhytWEpi_ + _oPDetWEpi_ + _oPAIMWEpi_
```

### `_oPInorgWEpi_`  [_gP_*_m_^-3]
- **Description**: Inorganic_P_in_water
- **Equation**:

```
_oPInorgWEpi_ = _oPO4WEpi_ + _oPAIMWEpi_
```

### `_oPTotWEpi_`  [_gP_*_m_^-3]
- **Description**: Total_P_in_water_(excl_animals_AND_vegetation)
- **Equation**:

```
_oPTotWEpi_ = _oPSestWEpi_ + _oPO4WEpi_
```

## Lake_water_total_N_variables  (10 equations)

### `_oNDissWEpi_`  [_gN_*_m_^-3]
- **Description**: SRN_in_water
- **Equation**:

```
_oNDissWEpi_ = _oNO3WEpi_ + _oNH4WEpi_
```

### `_oNDissWHyp_`  [_gN_*_m_^-3]
- **Description**: SRN_in_water
- **Equation**:

```
_oNDissWHyp_ = _oNO3WHyp_ + _oNH4WHyp_
```

### `_oNOMWHyp_`  [_gN_*_m_^-3]
- **Description**: Org_seston_N
- **Equation**:

```
_oNOMWHyp_ = _oNPhytWHyp_ + _oNDetWHyp_
```

### `_oNSestWHyp_`  [_gN_*_m_^-3]
- **Description**: Total_seston_N
- **Equation**:

```
_oNSestWHyp_ = _oNOMWHyp_
```

### `_oNkjWHyp_`  [_gN_*_m_^-3]
- **Description**: Kjeldahl_N_in_water
- **Equation**:

```
_oNkjWHyp_ = _oNSestWHyp_ + _oNH4WHyp_
```

### `_oNTotWHyp_`  [_gN_*_m_^-3]
- **Description**: Total_N_in_water_(without_animals_AND_vegetation)
- **Equation**:

```
_oNTotWHyp_ = _oNkjWHyp_ + _oNO3WHyp_
```

### `_oNOMWEpi_`  [_gN_*_m_^-3]
- **Description**: Organic_seston_N
- **Equation**:

```
_oNOMWEpi_ = _oNPhytWEpi_ + _oNDetWEpi_
```

### `_oNSestWEpi_`  [_gN_*_m_^-3]
- **Description**: Total_seston_N
- **Equation**:

```
_oNSestWEpi_ = _oNOMWEpi_
```

### `_oNkjWEpi_`  [_gN_*_m_^-3]
- **Description**: Kjeldahl_N_in_water
- **Equation**:

```
_oNkjWEpi_ = _oNSestWEpi_ + _oNH4WEpi_
```

### `_oNTotWEpi_`  [_gN_*_m_^-3]
- **Description**: Total_N_in_water_(without_animals_AND_vegetation)
- **Equation**:

```
_oNTotWEpi_ = _oNkjWEpi_ + _oNO3WEpi_
```

## Lake_sediment  (2 equations)

### `_bPorS_`  [_m_^3*_m_^-3]
- **Description**: Porosity
- **Equation**:

```
_bPorS_ = (1.0 - _fDTotS0_) * (_fDOrgS0_ * _cRhoOM_ + (1 - _fDOrgS0_) * _cRhoIM_) / _cRhoWat_ / ( _fDTotS0_ + (1.0 - _fDTotS0_) * (_fDOrgS0_ * _cRhoOM_ + (1 - _fDOrgS0_) * _cRhoIM_) / _cRhoWat_ )
```

### `_bPorCorS_`  [0]
- **Description**: Sediment_porosity_corrected_for_tortuosity
- **Equation**:

```
_bPorCorS_ = _IF_ _POW_(_bPorS_ _POWOPERATOR_ (_bPorS_ + 1.0)) _LE_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_bPorS_ _POWOPERATOR_ (_bPorS_ + 1.0)) _ENDIF_
```

## Lake_sediment_total_DW_variables  (7 equations)

### `_aDTotS_`  [_gDW_*_m_^-2]
- **Description**: Total_sediment_(excl_biota)
- **Equation**:

```
_aDTotS_ = _aDIMS_ + _aDHumS_ + _aDDetS_
```

### `_aRhoTotS_`  [_gDW_*_m_^-3]
- **Description**: (apparent)_bulk_density_of_sediment
- **Equation**:

```
_aRhoTotS_ = _aDTotS_ / _cDepthS_
```

### `_aRhoSolidS_`  [_gDW_*_m_^-3]
- **Description**: Average_solid_density
- **Equation**:

```
_aRhoSolidS_ = (_aDIMS_ * _cRhoIM_ + (_aDHumS_ + _aDDetS_) * _cRhoOM_) / _aDTotS_
```

### `_afDTotS_`  [_gDW_*_gDW_^-1]
- **Description**: Sediment_dry-weight_fraction
- **Equation**:

```
_afDTotS_ = 1.0 / (1.0 + _bPorS_/(1.0-_bPorS_) * _cRhoWat_ / _aRhoSolidS_)
```

### `_afDOrgS_`  [0]
- **Description**: Total_organic_fraction_of_sediment_DW
- **Equation**:

```
_afDOrgS_ = (_aDHumS_ + _aDDetS_) / _aDTotS_
```

### `_afDetS_`  [0]
- **Description**: Detrital_fraction_of_sediment_organic_DW
- **Equation**:

```
_afDetS_ = _aDDetS_ / (_aDHumS_ + _aDDetS_)
```

### `_afDetTotS_`  [0]
- **Description**: Detrital_fraction_of_total_sediment_DW
- **Equation**:

```
_afDetTotS_ = _aDDetS_ / (_aDIMS_ + _aDHumS_ + _aDDetS_)
```

## Lake_sediment_total_P_variables  (7 equations)

### `_aPInorgS_`  [_gP_*_m_^-2]
- **Description**: Inorganic_P_in_sediment
- **Equation**:

```
_aPInorgS_ = _aPO4S_ + _aPAIMS_
```

### `_aPTotAvailS_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_sediment_(excl_humus_animals_AND_vegetation)
- **Equation**:

```
_aPTotAvailS_ = _aPDetS_ + _aPInorgS_ + _aPPhytS_
```

### `_aPTotS_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_sediment_(excl_animals_AND_vegetation)
- **Equation**:

```
_aPTotS_ = _aPTotAvailS_ + _aPHumS_
```

### `_afPInorgS_`  [_gP_*_gDW_^-1]
- **Description**: Fraction_inorganic_P_in_sediment
- **Equation**:

```
_afPInorgS_ = _aPInorgS_ / _aDTotS_
```

### `_afPTotS_`  [_gP_*_gDW_^-1]
- **Description**: Total_P_fraction_in_sediment
- **Equation**:

```
_afPTotS_ = _aPTotS_ / _aDTotS_
```

### `_afPO4S_`  [0]
- **Description**: Fraction_dissolved_P_in_sediment
- **Equation**:

```
_afPO4S_ = _aPO4S_ / (_aPTotAvailS_ + _NearZero_)
```

### `_oPO4S_`  [_gP_*_m_^-3]
- **Description**: Conc_dissolved_P_in_interstitial_water
- **Equation**:

```
_oPO4S_ = _aPO4S_ / _cDepthS_ / _bPorS_
```

## Lake_sediment_total_N_variables  (10 equations)

### `_aNDissS_`  [_gN_*_m_^-2]
- **Description**: Total_dissolved_N_in_pore_water
- **Equation**:

```
_aNDissS_ = _aNH4S_ + _aNO3S_
```

### `_aNkjAvailS_`  [_gN_*_m_^-2]
- **Description**: Kjeldahl_N_in_sediment_excl_humus
- **Equation**:

```
_aNkjAvailS_ = _aNDetS_ + _aNPhytS_ + _aNH4S_
```

### `_aNkjS_`  [_gN_*_m_^-2]
- **Description**: Kjeldahl_N_in_sediment
- **Equation**:

```
_aNkjS_ = _aNkjAvailS_ + _aNHumS_
```

### `_aNTotAvailS_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_sediment_excl_humus
- **Equation**:

```
_aNTotAvailS_ = _aNkjAvailS_ + _aNO3S_
```

### `_aNTotS_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_sediment
- **Equation**:

```
_aNTotS_ = _aNkjS_ + _aNO3S_
```

### `_afNInorgS_`  [_gN_*_gDW_^-1]
- **Description**: Fraction_inorganic_N_in_sediment
- **Equation**:

```
_afNInorgS_ = _aNDissS_ / _aDTotS_
```

### `_afNTotS_`  [_gN_*_gDW_^-1]
- **Description**: Total_N_fraction_in_sediment
- **Equation**:

```
_afNTotS_ = _aNTotS_ / _aDTotS_
```

### `_oNO3S_`  [_gN_*_m_^-3]
- **Description**: Conc_dissolved_N-NO3_in_interstitial_water
- **Equation**:

```
_oNO3S_ = _aNO3S_ / _cDepthS_ / _bPorS_
```

### `_oNH4S_`  [_gN_*_m_^-3]
- **Description**: Conc_dissolved_N-NH4_in_interstitial_water
- **Equation**:

```
_oNH4S_ = _aNH4S_ / _cDepthS_ / _bPorS_
```

### `_oNDissS_`  [_gN_*_m_^-3]
- **Description**: Dissolved_N_conc_in_sediment_needed_for_calc_of_veg_uptake_rate
- **Equation**:

```
_oNDissS_ = _aNDissS_ / _cDepthS_ / _bPorS_
```

## Nutrient_D/W_ratios  (14 equations)

### `_rPDIMWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_water_DIM
- **Equation**:

```
_rPDIMWHyp_ = _oPAIMWHyp_ / _oDIMWHyp_
```

### `_rPDIMS_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_sediment_DIM
- **Equation**:

```
_rPDIMS_ = _aPAIMS_ / _aDIMS_
```

### `_rPDDetWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_water_detritus
- **Equation**:

```
_rPDDetWHyp_ = _oPDetWHyp_ / (_oDDetWHyp_+_NearZero_)
```

### `_rNDDetWHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_water_detritus
- **Equation**:

```
_rNDDetWHyp_ = _oNDetWHyp_ / (_oDDetWHyp_+_NearZero_)
```

### `_rSiDDetWHyp_`  [_gSi_*_gDW_^-1]
- **Description**: Si/D_ratio_of_water_detritus
- **Equation**:

```
_rSiDDetWHyp_ = _oSiDetWHyp_ / (_oDDetWHyp_+_NearZero_)
```

### `_rPDHumS_`  [_gP_*_gDW_^-1]
- **Description**: P_content_of_sediment_OM
- **Equation**:

```
_rPDHumS_ = _aPHumS_ / (_aDHumS_+_NearZero_)
```

### `_rNDHumS_`  [_gN_*_gDW_^-1]
- **Description**: N_content_of_sediment_OM
- **Equation**:

```
_rNDHumS_ = _aNHumS_ / (_aDHumS_+_NearZero_)
```

### `_rPDDetS_`  [_gP_*_gDW_^-1]
- **Description**: P_content_of_sediment_detritus
- **Equation**:

```
_rPDDetS_ = _aPDetS_ / (_aDDetS_+_NearZero_)
```

### `_rNDDetS_`  [_gN_*_gDW_^-1]
- **Description**: N_content_of_sediment_detritus
- **Equation**:

```
_rNDDetS_ = _aNDetS_ / (_aDDetS_+_NearZero_)
```

### `_rSiDDetS_`  [_gSi_*_gDW_^-1]
- **Description**: Si_content_of_sediment_detritus
- **Equation**:

```
_rSiDDetS_ = _aSiDetS_ / (_aDDetS_+_NearZero_)
```

### `_rPDIMWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_water_DIM
- **Equation**:

```
_rPDIMWEpi_ = _oPAIMWEpi_ / _oDIMWEpi_
```

### `_rPDDetWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_water_detritus
- **Equation**:

```
_rPDDetWEpi_ = _oPDetWEpi_ / (_oDDetWEpi_+_NearZero_)
```

### `_rNDDetWEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_water_detritus
- **Equation**:

```
_rNDDetWEpi_ = _oNDetWEpi_ / (_oDDetWEpi_+_NearZero_)
```

### `_rSiDDetWEpi_`  [_gSi_*_gDW_^-1]
- **Description**: Si/D_ratio_of_water_detritus
- **Equation**:

```
_rSiDDetWEpi_ = _oSiDetWEpi_ / (_oDDetWEpi_+_NearZero_)
```

## Marsh_water_total_phytplankton  (4 equations)

### `_oDPhytWM_`  [_gDW_*_m_^-3]
- **Description**: Total_DW_phytoplankton_in_marsh_water
- **Equation**:

```
_oDPhytWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oDDiatWM_ + _oDGrenWM_ + _oDBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oPPhytWM_`  [_gP_*_m_^-3]
- **Description**: Total_P_phytoplankton_in_marsh_water
- **Equation**:

```
_oPPhytWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPDiatWM_ + _oPGrenWM_ + _oPBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNPhytWM_`  [_gN_*_m_^-3]
- **Description**: Total_N_phytoplankton_in_marsh_water
- **Equation**:

```
_oNPhytWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNDiatWM_ + _oNGrenWM_ + _oNBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oSiDiatWM_`  [_gSi_*_m_^-3]
- **Description**: Total_Si_diatoms_in_marsh_water
- **Equation**:

```
_oSiDiatWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cSiDDiat_ * _oDDiatWM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_water_DW_variables  (2 equations)

### `_oDOMWM_`  [_gDW_*_m_^-3]
- **Description**: Organic_seston
- **Equation**:

```
_oDOMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oDDetWM_ + _oDPhytWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oDSestWM_`  [_gDW_*_m_^-3]
- **Description**: Total_seston
- **Equation**:

```
_oDSestWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oDOMWM_ + _oDIMWM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_water_P_variables  (4 equations)

### `_oPOMWM_`  [_gP_*_m_^-3]
- **Description**: Organic_P_in_water
- **Equation**:

```
_oPOMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPPhytWM_ + _oPDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oPSestWM_`  [_gP_*_m_^-3]
- **Description**: Total_seston_P(incl_adsorbed
- **Equation**:

```
_oPSestWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPPhytWM_ + _oPDetWM_ + _oPAIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oPInorgWM_`  [_gP_*_m_^-3]
- **Description**: Inorganic_P_in_water
- **Equation**:

```
_oPInorgWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPO4WM_ + _oPAIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oPTotWM_`  [_gP_*_m_^-3]
- **Description**: Total_P_in_water
- **Equation**:

```
_oPTotWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPSestWM_ + _oPO4WM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_water_N_variables  (5 equations)

### `_oNDissWM_`  [_gN_*_m_^-3]
- **Description**: SRN_in_water
- **Equation**:

```
_oNDissWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNO3WM_ + _oNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNOMWM_`  [_gN_*_m_^-3]
- **Description**: Org_seston_N
- **Equation**:

```
_oNOMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNPhytWM_ + _oNDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNSestWM_`  [_gN_*_m_^-3]
- **Description**: Total_seston_N
- **Equation**:

```
_oNSestWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNOMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNkjWM_`  [_gN_*_m_^-3]
- **Description**: Kjeldahl_N_in_water
- **Equation**:

```
_oNkjWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNSestWM_ + _oNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNTotWM_`  [_gN_*_m_^-3]
- **Description**: Total_N_in_water
- **Equation**:

```
_oNTotWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNkjWM_ + _oNO3WM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_sediment  (2 equations)

### `_bPorSM_`  [_m_^3*_m_^-3]
- **Description**: Porosity
- **Equation**:

```
_bPorSM_ = (1.0 - _fDTotSM0_) * (_fDOrgSM0_ * _cRhoOM_ +(1 - _fDOrgSM0_) * _cRhoIM_) / _cRhoWat_ /(_fDTotSM0_ + (1.0 - _fDTotSM0_) * (_fDOrgSM0_ * _cRhoOM_ +(1 - _fDOrgSM0_) * _cRhoIM_) / _cRhoWat_)
```

### `_bPorCorSM_`  [0]
- **Description**: Sediment_porosity_corrected_for_tortuosity
- **Equation**:

```
_bPorCorSM_ = _IF_ _POW_ ( _bPorSM_ _POWOPERATOR_ (_bPorSM_ + 1.0)) _LE_ _NearZero_ _THEN_ 1 _ELSE_ _POW_ ( _bPorSM_ _POWOPERATOR_ (_bPorSM_ + 1.0)) _ENDIF_
```

## Marsh_sediment_DW  (7 equations)

### `_aDTotSM_`  [_gDW_*_m_^-2]
- **Description**: Total_sediment(excl_biota)
- **Equation**:

```
_aDTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDIMSM_ + _aDHumSM_ + _aDDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aRhoTotSM_`  [_gDW_*_m_^-3]
- **Description**: (apparent)_bulk_density_of_sediment
- **Equation**:

```
_aRhoTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDTotSM_ / _cDepthSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aRhoSolidSM_`  [_gDW_*_m_^-3]
- **Description**: Average_solid_density
- **Equation**:

```
_aRhoSolidSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_aDIMSM_ * _cRhoIM_ +(_aDHumSM_ + _aDDetSM_) * _cRhoOM_) / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afDTotSM_`  [_gDW_*_gDW_^-1]
- **Description**: Sediment_dry-weight_fraction
- **Equation**:

```
_afDTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ 1.0 /(1.0 + _bPorSM_/(1.0-_bPorSM_) * _cRhoWat_ / _aRhoSolidSM_) _ELSE_ 0.0 _ENDIF_
```

### `_afDOrgSM_`  [0]
- **Description**: Total_organic_fraction_of_sediment_DW
- **Equation**:

```
_afDOrgSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_aDHumSM_ + _aDDetSM_) / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afDetSM_`  [0]
- **Description**: Detrital_fraction_of_sediment_organic_DW
- **Equation**:

```
_afDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDDetSM_ /(_aDHumSM_ + _aDDetSM_) _ELSE_ 0.0 _ENDIF_
```

### `_afDetTotSM_`  [0]
- **Description**: Detrital_fraction_of_total_sediment_DW
- **Equation**:

```
_afDetTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDDetSM_ /(_aDIMSM_ + _aDHumSM_ + _aDDetSM_) _ELSE_ 0.0 _ENDIF_
```

## Marsh_sediment_P  (7 equations)

### `_aPInorgSM_`  [_gP_*_m_^-2]
- **Description**: Inorganic_P_in_sediment
- **Equation**:

```
_aPInorgSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPO4SM_ + _aPAIMSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aPTotAvailSM_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_sediment(excl_humus_animals_AND_vegetation)
- **Equation**:

```
_aPTotAvailSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPDetSM_ + _aPInorgSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aPTotSM_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_sediment(excl_animals_AND_vegetation)
- **Equation**:

```
_aPTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPTotAvailSM_ + _aPHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afPInorgSM_`  [_gP_*_gDW_^-1]
- **Description**: Fraction_inorganic_P_in_sediment
- **Equation**:

```
_afPInorgSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPInorgSM_ / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afPTotSM_`  [_gP_*_gDW_^-1]
- **Description**: Total_P_fraction_in_sediment
- **Equation**:

```
_afPTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPTotSM_ / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afPO4SM_`  [0]
- **Description**: Fraction_dissolved_P_in_sediment
- **Equation**:

```
_afPO4SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPO4SM_ /(_aPTotAvailSM_ + _NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_oPO4SM_`  [_gP_*_m_^-3]
- **Description**: Conc_dissolved_P_in_interstitial_water
- **Equation**:

```
_oPO4SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPO4SM_ / _cDepthSM_ / _bPorSM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_sediment_N  (10 equations)

### `_aNDissSM_`  [_gN_*_m_^-2]
- **Description**: Total_dissolved_N_in_pore_water
- **Equation**:

```
_aNDissSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNH4SM_ + _aNO3SM_ _ELSE_ 0.0 _ENDIF_
```

### `_aNkjAvailSM_`  [_gN_*_m_^-2]
- **Description**: Kjeldahl_N_in_sediment_excl_humus
- **Equation**:

```
_aNkjAvailSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNDetSM_ + _aNH4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_aNkjSM_`  [_gN_*_m_^-2]
- **Description**: Kjeldahl_N_in_sediment
- **Equation**:

```
_aNkjSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNkjAvailSM_ + _aNHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aNTotAvailSM_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_sediment_excl_humus
- **Equation**:

```
_aNTotAvailSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNkjAvailSM_ + _aNO3SM_ _ELSE_ 0.0 _ENDIF_
```

### `_aNTotSM_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_sediment
- **Equation**:

```
_aNTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNkjSM_ + _aNO3SM_ _ELSE_ 0.0 _ENDIF_
```

### `_afNInorgSM_`  [_gN_*_gDW_^-1]
- **Description**: Fraction_inorganic_N_in_sediment
- **Equation**:

```
_afNInorgSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNDissSM_ / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_afNTotSM_`  [_gN_*_gDW_^-1]
- **Description**: Total_N_fraction_in_sediment
- **Equation**:

```
_afNTotSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNTotSM_ / _aDTotSM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNO3SM_`  [_gN_*_m_^-3]
- **Description**: Conc_dissolved_N-NO3_in_interstitial_marsh_water
- **Equation**:

```
_oNO3SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNO3SM_ / _cDepthSM_ / _bPorSM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNH4SM_`  [_gN_*_m_^-3]
- **Description**: Conc_dissolved_N-NH4_in_interstitial_marsh_water
- **Equation**:

```
_oNH4SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNH4SM_ / _cDepthSM_ / _bPorSM_ _ELSE_ 0.0 _ENDIF_
```

### `_oNDissSM_`  [_gN_*_m_^-3]
- **Description**: Dissolved_N_conc_in_marsh_sediment
- **Equation**:

```
_oNDissSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNDissSM_ / _cDepthSM_ / _bPorSM_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_nutrient_D/W_ratios  (10 equations)

### `_rPDIMWM_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_DIM_in_marsh_water
- **Equation**:

```
_rPDIMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPAIMWM_ / _oDIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_rPDIMSM_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_DIM_marsh_sediment
- **Equation**:

```
_rPDIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPAIMSM_ / _aDIMSM_ _ELSE_ 0.0 _ENDIF_
```

### `_rPDDetWM_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_marsh_water_detritus
- **Equation**:

```
_rPDDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oPDetWM_ /(_oDDetWM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rNDDetWM_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_marsh_water_detritus
- **Equation**:

```
_rNDDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNDetWM_ /(_oDDetWM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rSiDDetWM_`  [_gSi_*_gDW_^-1]
- **Description**: Si/D_ratio_of_marsh_water_detritus
- **Equation**:

```
_rSiDDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oSiDetWM_ /(_oDDetWM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rPDHumSM_`  [_gP_*_gDW_^-1]
- **Description**: P_content_of_marsh_sediment_OM
- **Equation**:

```
_rPDHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPHumSM_ /(_aDHumSM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rNDHumSM_`  [_gN_*_gDW_^-1]
- **Description**: N_content_of_marsh_sediment_OM
- **Equation**:

```
_rNDHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNHumSM_ /(_aDHumSM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rPDDetSM_`  [_gP_*_gDW_^-1]
- **Description**: P_content_of_marsh_sediment_detritus
- **Equation**:

```
_rPDDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPDetSM_ /(_aDDetSM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rNDDetSM_`  [_gN_*_gDW_^-1]
- **Description**: N_content_of_marsh_sediment_detritus
- **Equation**:

```
_rNDDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNDetSM_ /(_aDDetSM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

### `_rSiDDetSM_`  [_gSi_*_gDW_^-1]
- **Description**: Si_content_of_marsh_sediment_detritus
- **Equation**:

```
_rSiDDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aSiDetSM_ /(_aDDetSM_+_NearZero_) _ELSE_ 0.0 _ENDIF_
```

## Marsh_total_DW  (1 equations)

### `_aDTotM_`  [_gDW_*_m_^-2]
- **Description**: Total_D_in_marsh
- **Equation**:

```
_aDTotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ((_oDIMWM_ + _oDDetWM_ + _oDPhytWM_ + _oDZooM_) * _uDepthWM_ + _aDIMSM_ + _aDHumSM_ + _aDDetSM_ + _aDShootPhra_ + _aDRootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_total_P  (1 equations)

### `_aPTotM_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_marsh
- **Equation**:

```
_aPTotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ((_oPO4WM_ + _oPDetWM_ + _oPAIMWM_ + _oPPhytWM_ + _oPZooM_) * _uDepthWM_ + _aPO4SM_ + _aPHumSM_ + _aPDetSM_ + _aPAIMSM_ + _aPShootPhra_ + _aPRootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_total_N  (1 equations)

### `_aNTotM_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_marsh
- **Equation**:

```
_aNTotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ((_oNH4WM_ + _oNO3WM_ + _oNDetWM_ + _oNPhytWM_ + _oNZooM_) * _uDepthWM_ + _aNH4SM_ + _aNO3SM_ + _aNHumSM_ + _aNDetSM_ + _aNShootPhra_ + _aNRootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

## Marsh_total_Si  (2 equations)

### `_aSiTotM_`  [_gSi_*_m_^-2]
- **Description**: Total_Si_in_marsh
- **Equation**:

```
_aSiTotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ((_oSiO2WM_ + _oSiDetWM_ + _oSiDiatWM_) * _uDepthWM_ + _aSiDetSM_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

### `_aO2TotM_`  [_gO2_*_m_^-2]
- **Description**: Total_Si_in_marsh
- **Equation**:

```
_aO2TotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ((_oO2WM_) * _uDepthWM_ ) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

## Loading  (72 equations)

### `_uPLoadSeasonEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seasonal_P_load_epilimnion
- **Equation**:

```
_uPLoadSeasonEpi_ = _IF_ (_FALSE_ _EQ_ _UseSeasonLoad_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _cDayApril1_ - 0.5*_cLengChange_) _THEN_ _cPLoadWin_ _ELSEIF_ (_Day_ _LT_ _cDayApril1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cPLoadWin_ + _cPLoadSum_) + 0.5*(_cPLoadWin_ - _cPLoadSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayApril1_)) _ELSEIF_ (_Day_ _LT_ _cDayOct1_ - 0.5*_cLengChange_) _THEN_ _cPLoadSum_ _ELSEIF_ (_Day_ _LT_ _cDayOct1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cPLoadWin_ + _cPLoadSum_) - 0.5*(_cPLoadWin_ - _cPLoadSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayOct1_)) _ELSE_ _cPLoadWin_ _ENDIF_
```

### `_uPLoadEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_load_epilimnion
- **Equation**:

```
_uPLoadEpi_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mPLoadPO4Epi_ + _mPLoadAIMEpi_ + _mPLoadDiatEpi_ + _mPLoadGrenEpi_ + _mPLoadBlueEpi_ + _mPLoadDetEpi_) _ELSEIF_ (_ReadPLoad_ _EQ_ _TRUE_ _AND_ _ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadPO4Epi_ + _mPLoadOrgEpi_ _ELSEIF_ (_ReadPLoad_ _EQ_ _TRUE_ _AND_ _FALSE_ _EQ_ _ReadNutFrac_) _THEN_ _mPLoadEpi_ * _mPLoadEpiMult_ _ELSEIF_ (_UsePulseLoad_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSEIF_ (_UseSeasonLoad_ _EQ_ _TRUE_) _THEN_ _uPLoadSeasonEpi_ _ELSE_ _cPLoad_ _ENDIF_
```

### `_uPLoadPO4Epi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_load_PO4_epilimnion
- **Equation**:

```
_uPLoadPO4Epi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadPO4Epi_ _ELSEIF_ (_ReadPLoad_ _EQ_ _FALSE_) _THEN_ _fPO4In_ * _uPLoadEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadPO4Epi_ _ELSE_ _fPO4In_ * _uPLoadEpi_ _ENDIF_
```

### `_uPLoadOrgEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_load_bound_to_org_matter_epilimnion
- **Equation**:

```
_uPLoadOrgEpi_ = _IF_ (_FALSE_ _EQ_ _ReadPLoad_) _THEN_ (1.0 - _fPO4In_) * _uPLoadEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadOrgEpi_ _ELSE_ (1.0 - _fPO4In_) * _uPLoadEpi_ _ENDIF_
```

### `_uPLoadPhytTotEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: (total)_algal_P_input_epilimnion
- **Equation**:

```
_uPLoadPhytTotEpi_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ (((_fPhytInSum_ + _fPhytInWin_)/2)*_uPLoadOrgEpi_) _ELSEIF_ (_ReadPLoadPhyt_ _EQ_ _TRUE_) _THEN_ _mPLoadPhytTotEpi_ _ELSE_ ((_fPhytInSum_+_fPhytInWin_)/2.0 - (_fPhytInSum_-_fPhytInWin_)/2.0 * _COS_(2.0*_Pi_ * (_sTime_ + _TenDays_ - _cTimeLag_) / _DaysInYear_)) * _uPLoadOrgEpi_ _ENDIF_
```

### `_uPLoadDetEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_input_epilimnion
- **Equation**:

```
_uPLoadDetEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadDetEpi_ _ELSE_ _uPLoadOrgEpi_ - _uPLoadPhytTotEpi_ _ENDIF_
```

### `_uPLoadAIMEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Adsorbed_P_loading_epilimnion
- **Equation**:

```
_uPLoadAIMEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadAIMEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_uPBackLoadHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: P_background_loading_into_the_hypolimnion
- **Equation**:

```
_uPBackLoadHyp_ = _IF_ (_FALSE_ _EQ_ _aInclStrat_) _THEN_ 0.0 _ELSE_ _cPBackLoad_ _ENDIF_
```

### `_uPTotInEpi_`  [_gP_*_m_^-3]
- **Description**: External_P_concentration
- **Equation**:

```
_uPTotInEpi_ = _uPLoadEpi_ / (_uQInEpi_ / _mmPerm_ + _NearZero_)
```

### `_uNLoadSeasonEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seasonal_N_load_for_epilimnion
- **Equation**:

```
_uNLoadSeasonEpi_ = _IF_ (_FALSE_ _EQ_ _UseSeasonLoad_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _cDayApril1_ - 0.5*_cLengChange_) _THEN_ _cNLoadWin_ _ELSEIF_ (_Day_ _LT_ _cDayApril1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cNLoadWin_ + _cNLoadSum_) + 0.5*(_cNLoadWin_ - _cNLoadSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayApril1_)) _ELSEIF_ (_Day_ _LT_ _cDayOct1_ - 0.5*_cLengChange_) _THEN_ _cNLoadSum_ _ELSEIF_ (_Day_ _LT_ _cDayOct1_ + 0.5*_cLengChange_) _THEN_ 0.5*(_cNLoadWin_ + _cNLoadSum_) - 0.5*(_cNLoadWin_ - _cNLoadSum_) * _COS_(_Pi_/_cLengChange_ * (_Day_ - _cDayOct1_)) _ELSE_ _cNLoadWin_ _ENDIF_
```

### `_uNLoadPhytTotEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: (total)_algal_N_input_epilimnion
- **Equation**:

```
_uNLoadPhytTotEpi_ = _IF_ (_ReadNutFrac_ _EQ_ _FALSE_) _THEN_ (_cNPPhytIn_ * _uPLoadPhytTotEpi_) _ELSE_  _mNLoadPhytTotEpi_ _ENDIF_
```

### `_uNLoadEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_load_epilimnion
- **Equation**:

```
_uNLoadEpi_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mNLoadNH4Epi_ + _mNLoadNO3Epi_ + _mNLoadGrenEpi_ + _mNLoadDiatEpi_ + _mNLoadBlueEpi_ + _mNLoadDetEpi_) _ELSEIF_ (_ReadNLoad_ _EQ_ _TRUE_ _AND_ _ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNH4Epi_ + _mNLoadNO3Epi_ + _mNLoadOrgEpi_ _ELSEIF_ (_ReadNLoad_ _EQ_ _TRUE_ _AND_ _ReadNutFrac_ _EQ_ _FALSE_) _THEN_ _mNLoadEpi_ _ELSEIF_ (_UsePulseLoad_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSEIF_ (_ReadPLoad_ _EQ_ _TRUE_) _THEN_ _cNPLoadMeas_ * _uPLoadEpi_ _ELSEIF_ (_UseSeasonLoad_ _EQ_ _TRUE_) _THEN_ _uNLoadSeasonEpi_ _ELSE_ _cNLoad_ _ENDIF_
```

### `_uNLoadDetEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_load_detritus_epilimnion
- **Equation**:

```
_uNLoadDetEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadDetEpi_ _ELSEIF_ (_ReadNLoad_ _EQ_ _FALSE_ ) _THEN_ _MIN_(_cNPDetIn_ * _uPLoadDetEpi_, _uNLoadEpi_ - _uNLoadPhytTotEpi_) _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadOrgEpi_ - _mNLoadPhytTotEpi_ _ELSE_ _MIN_(_cNPDetIn_ * _uPLoadDetEpi_, _uNLoadEpi_ - _uNLoadPhytTotEpi_) _ENDIF_
```

### `_uNLoadOrgEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Loading_N_bound_to_org_matter_in_epilimnion
- **Equation**:

```
_uNLoadOrgEpi_ = _IF_ (_FALSE_ _EQ_ _ReadNLoad_) _THEN_ _uNLoadPhytTotEpi_ + _uNLoadDetEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadOrgEpi_ _ELSE_ _uNLoadPhytTotEpi_ + _uNLoadDetEpi_ _ENDIF_
```

### `_uNLoadDissEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_loading_dissolved_(sum_of_NO2_and_NH4)_in_epilimnion
- **Equation**:

```
_uNLoadDissEpi_ = _IF_ (_FALSE_ _EQ_ _ReadNLoad_) _THEN_ _uNLoadEpi_ - _uNLoadOrgEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSE_ _uNLoadEpi_ - _uNLoadOrgEpi_ _ENDIF_
```

### `_uNLoadNH4Epi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_loading_epilimnion
- **Equation**:

```
_uNLoadNH4Epi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNH4Epi_ _ELSEIF_ (_ReadNLoad_ _EQ_ _FALSE_) _THEN_ _fNH4DissIn_ * _uNLoadDissEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNH4Epi_ _ELSE_ _fNH4DissIn_ * _uNLoadDissEpi_ _ENDIF_
```

### `_uNLoadNO3Epi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_loading
- **Equation**:

```
_uNLoadNO3Epi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNO3Epi_ _ELSEIF_ (_ReadNLoad_ _EQ_ _FALSE_) _THEN_ (1.0 - _fNH4DissIn_) * _uNLoadDissEpi_ _ELSEIF_ (_ReadNutFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNO3Epi_ _ELSE_ (1.0 - _fNH4DissIn_) * _uNLoadDissEpi_ _ENDIF_
```

### `_uNBackLoadHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_background_loading_into_the_hypolimnion
- **Equation**:

```
_uNBackLoadHyp_ = _IF_ (_FALSE_ _EQ_ _aInclStrat_) _THEN_ 0.0 _ELSE_ _cNBackLoad_ _ENDIF_
```

### `_uNTotInEpi_`  [_gN_*_m_^-3]
- **Description**: External_N_conc
- **Equation**:

```
_uNTotInEpi_ = _uNLoadEpi_ / (_uQInEpi_ / _mmPerm_ + _NearZero_)
```

### `_uDLoadDetEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Detrital_DW_loading_epilimnion
- **Equation**:

```
_uDLoadDetEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadDetEpi_ _ELSEIF_ (_ReadDLoadDet_ _EQ_ _TRUE_) _THEN_ _mDLoadDetEpi_ _ELSE_ _uNLoadDetEpi_ / _cNDDetIn_ _ENDIF_
```

### `_uDLoadPhytTotEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: (total)_algal_DW_input_epilimnion
- **Equation**:

```
_uDLoadPhytTotEpi_ = _uNLoadPhytTotEpi_ / _cNDPhytIn_
```

### `_uDLoadIMEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Loading_of_DW_of_inorg_matter
- **Equation**:

```
_uDLoadIMEpi_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadIMEpi_ _ELSEIF_ (_ReadDLoadIM_ _EQ_ _TRUE_) _THEN_ _mDLoadIMEpi_ _ELSE_ _cDIMIn_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_uDLoadEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_input_epilimnion
- **Equation**:

```
_uDLoadEpi_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mDLoadIMEpi_ + _mDLoadDetEpi_ + _mDLoadDiatEpi_ + _mDLoadGrenEpi_ + _mDLoadBlueEpi_) _ELSE_ _uDLoadIMEpi_ + _uDLoadDetEpi_ + _uDLoadPhytTotEpi_ _ENDIF_
```

### `_uDLoadDiatEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_diatoms_loading_for_epilimnion
- **Equation**:

```
_uDLoadDiatEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadDiatEpi_ _ELSE_ _fDiatPhytIn_ * _uDLoadPhytTotEpi_ _ENDIF_
```

### `_uPLoadDiatEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_diatoms_loading_for_epilimnion
- **Equation**:

```
_uPLoadDiatEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadDiatEpi_ _ELSE_ _fDiatPhytIn_ * _uPLoadPhytTotEpi_ _ENDIF_
```

### `_uNLoadDiatEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_diatoms_loading_for_epilimnion
- **Equation**:

```
_uNLoadDiatEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadDiatEpi_ _ELSE_ _fDiatPhytIn_ * _uNLoadPhytTotEpi_ _ENDIF_
```

### `_uDLoadGrenEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_greens_loading_for_epilimnion
- **Equation**:

```
_uDLoadGrenEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadGrenEpi_ _ELSE_ _fGrenPhytIn_ * _uDLoadPhytTotEpi_ _ENDIF_
```

### `_uPLoadGrenEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_greens_loading_for_epilimnion
- **Equation**:

```
_uPLoadGrenEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadGrenEpi_ _ELSE_ _fGrenPhytIn_ * _uPLoadPhytTotEpi_ _ENDIF_
```

### `_uNLoadGrenEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_greens_loading_for_epilimnion
- **Equation**:

```
_uNLoadGrenEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadGrenEpi_ _ELSE_ _fGrenPhytIn_ * _uNLoadPhytTotEpi_ _ENDIF_
```

### `_uDLoadBlueEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_bluegreens_loading_for_epilimnion
- **Equation**:

```
_uDLoadBlueEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadBlueEpi_ _ELSE_ _fBluePhytIn_ * _uDLoadPhytTotEpi_ _ENDIF_
```

### `_uPLoadBlueEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_bluegreens_loading_for_epilimnion
- **Equation**:

```
_uPLoadBlueEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadBlueEpi_ _ELSE_ _fBluePhytIn_ * _uPLoadPhytTotEpi_ _ENDIF_
```

### `_uNLoadBlueEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_bluegreens_loading_for_epilimnion
- **Equation**:

```
_uNLoadBlueEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadBlueEpi_ _ELSE_ _fBluePhytIn_ * _uNLoadPhytTotEpi_ _ENDIF_
```

### `_uDLoadZooEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_zooplankton_loading_for_epilimnion
- **Equation**:

```
_uDLoadZooEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadZooEpi_ _ELSE_ _cDZooIn_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_uPLoadZooEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_zooplankton_loading_for_epilimnion
- **Equation**:

```
_uPLoadZooEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadZooEpi_ _ELSE_ _cDZooIn_ * _cPDZooRef_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_uNLoadZooEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_zooplankton_loading_for_epilimnion
- **Equation**:

```
_uNLoadZooEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadZooEpi_ _ELSE_ _cDZooIn_ * _cNDZooRef_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_uDLoadBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_bluegreens_loading_for_surface
- **Equation**:

```
_uDLoadBlueSurf_= _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadBlueSurf_ _ELSE_ 0.0 _ENDIF_
```

### `_uPLoadBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_bluegreens_loading_for_surface
- **Equation**:

```
_uPLoadBlueSurf_= _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadBlueSurf_ _ELSE_ 0.0 _ENDIF_
```

### `_uNLoadBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_bluegreens_loading_for_surface
- **Equation**:

```
_uNLoadBlueSurf_= _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadBlueSurf_ _ELSE_ 0.0 _ENDIF_
```

### `_uNLoadNH4Hyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_loading_for_hypolimnion
- **Equation**:

```
_uNLoadNH4Hyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNH4Hyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadNO3Hyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_loading_for_hypolimnion
- **Equation**:

```
_uNLoadNO3Hyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadNO3Hyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadPO4Hyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: PO4_loading_for_hypolimnion
- **Equation**:

```
_uPLoadPO4Hyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadPO4Hyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadAIMHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_adsorbed_onto_IM_loading_for_hypolimnion
- **Equation**:

```
_uPLoadAIMHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadAIMHyp_ _ELSE_ 0 _ENDIF_
```

### `_uSiLoadSiO2Hyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Si_loading_for_hypolimnion
- **Equation**:

```
_uSiLoadSiO2Hyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mSiLoadSiO2Hyp_ _ELSE_ 0 _ENDIF_
```

### `_uO2LoadHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_loading_for_hypolimnion
- **Equation**:

```
_uO2LoadHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mO2LoadHyp_ _ELSE_ _cO2In_ * _uQInHyp_ / _mmPerm_ _ENDIF_
```

### `_uDLoadDetHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_detritus_loading_for_hypolimnion
- **Equation**:

```
_uDLoadDetHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadDetHyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadDetHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_detritus_loading_for_hypolimnion
- **Equation**:

```
_uNLoadDetHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadDetHyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadDetHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_detritus_loading_for_hypolimnion
- **Equation**:

```
_uPLoadDetHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadDetHyp_ _ELSE_ 0 _ENDIF_
```

### `_uSiLoadDetHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Si_in_detritus_loading_for_hypolimnion
- **Equation**:

```
_uSiLoadDetHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mSiLoadDetHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadIMHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_inorg_matter_loading_for_hypolimnion
- **Equation**:

```
_uDLoadIMHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadIMHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadDiatHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_diatoms_loading_for_hypolimnion
- **Equation**:

```
_uDLoadDiatHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadDiatHyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadDiatHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_diatoms_loading_for_hypolimnion
- **Equation**:

```
_uNLoadDiatHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadDiatHyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadDiatHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_diatoms_loading_for_hypolimnion
- **Equation**:

```
_uPLoadDiatHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadDiatHyp_ _ELSE_ 0 _ENDIF_
```

### `_uSiLoadDiatHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Si_in_diatoms_loading_for_hypolimnion
- **Equation**:

```
_uSiLoadDiatHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _cSiDDiat_ * _uDLoadDiatHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadGrenHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_greens_loading_for_hypolimnion
- **Equation**:

```
_uDLoadGrenHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadGrenHyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadGrenHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_greens_loading_for_hypolimnion
- **Equation**:

```
_uNLoadGrenHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadGrenHyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadGrenHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_greens_loading_for_hypolimnion
- **Equation**:

```
_uPLoadGrenHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadGrenHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadBlueHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_bluegreens_loading_for_hypolimnion
- **Equation**:

```
_uDLoadBlueHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadBlueHyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadBlueHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_bluegreens_loading_for_hypolimnion
- **Equation**:

```
_uNLoadBlueHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadBlueHyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadBlueHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_bluegreens_loading_for_hypolimnion
- **Equation**:

```
_uPLoadBlueHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadBlueHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadZooHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: D_in_zooplankton_loading_for_hypolimnion
- **Equation**:

```
_uDLoadZooHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mDLoadZooHyp_ _ELSE_ 0 _ENDIF_
```

### `_uNLoadZooHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_in_zooplankton_loading_for_hypolimnion
- **Equation**:

```
_uNLoadZooHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mNLoadZooHyp_ _ELSE_ 0 _ENDIF_
```

### `_uPLoadZooHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_in_zooplankton_loading_for_hypolimnion
- **Equation**:

```
_uPLoadZooHyp_= _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mPLoadZooHyp_ _ELSE_ 0 _ENDIF_
```

### `_uDLoadHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_load_hypolimnion
- **Equation**:

```
_uDLoadHyp_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mDLoadIMHyp_ + _mDLoadDetHyp_ + _mDLoadDiatHyp_ + _mDLoadGrenHyp_ + _mDLoadBlueHyp_) _ELSE_ 0.0 _ENDIF_
```

### `_uNLoadHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_load_hypolimnion
- **Equation**:

```
_uNLoadHyp_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mNLoadNH4Hyp_ + _mNLoadNO3Hyp_ + _mNLoadGrenHyp_ + _mNLoadDiatHyp_ + _mNLoadBlueHyp_ + _mNLoadDetHyp_) _ELSE_ 0.0 _ENDIF_
```

### `_uPLoadHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_load_hypolimnion
- **Equation**:

```
_uPLoadHyp_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ (_mPLoadPO4Hyp_ + _mPLoadAIMHyp_ + _mPLoadDiatHyp_ + _mPLoadGrenHyp_ + _mPLoadBlueHyp_ + _mPLoadDetHyp_) _ELSE_ 0.0 _ENDIF_
```

### `_uSiLoadHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_load_hypolimnion
- **Equation**:

```
_uSiLoadHyp_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _uSiLoadSiO2Hyp_ + _uSiLoadDetHyp_ + _uSiLoadDiatHyp_ _ENDIF_
```

### `_uDLoadTotTW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_load_water
- **Equation**:

```
_uDLoadTotTW_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadEpi_ + _uDLoadHyp_ _ENDIF_
```

### `_uPLoadTotTW_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_load_water
- **Equation**:

```
_uPLoadTotTW_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadEpi_ + _uPLoadHyp_ _ENDIF_
```

### `_uNLoadTotTW_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_load_water
- **Equation**:

```
_uNLoadTotTW_ =  _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadEpi_ + _uNLoadHyp_ _ENDIF_
```

### `_uSiLoadTotTW_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_load_water
- **Equation**:

```
_uSiLoadTotTW_ =  _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadEpi_ + _uSiLoadHyp_ _ENDIF_
```

### `_tNH4LoadS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_load_to_sediment_from_artificial_fertilizer
- **Equation**:

```
_tNH4LoadS_ = _fNH4LoadS_ * _cNLoadS_
```

### `_tNO3LoadS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_load_to_sediment_from_artificial_fertilizer
- **Equation**:

```
_tNO3LoadS_ = _cNLoadS_ - _tNH4LoadS_
```

## Transport  (61 equations)

### `_uSiLoadSiO2Epi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_transport_flux_of_Si_in_sio2
- **Equation**:

```
_uSiLoadSiO2Epi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mSiLoadSiO2Epi_ _ELSE_ _cSiO2In_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_uSiLoadDetEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_transport_flux_of_Si_in_Det
- **Equation**:

```
_uSiLoadDetEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mSiLoadDetEpi_ _ELSE_ _cSiDDetIn_ * _uDLoadDetEpi_ _ENDIF_
```

### `_uSiLoadDiatEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_transport_flux_of_Si_in_Diat
- **Equation**:

```
_uSiLoadDiatEpi_ = _cSiDDiat_ * _uDLoadDiatEpi_
```

### `_uSiLoadEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Silica_loading_epilimnion
- **Equation**:

```
_uSiLoadEpi_ = _IF_ (_InclTran_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _uSiLoadSiO2Epi_ + _uSiLoadDetEpi_ + _uSiLoadDiatEpi_ _ENDIF_
```

### `_wDTranDiatHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Diat
- **Equation**:

```
_wDTranDiatHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadDiatHyp_ / _uDepthWHyp_ - _wDDilDiatHyp_ _ENDIF_
```

### `_wPTranDiatHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Diat
- **Equation**:

```
_wPTranDiatHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadDiatHyp_ / _uDepthWHyp_ - _wPDilDiatHyp_ _ENDIF_
```

### `_wNTranDiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Diat
- **Equation**:

```
_wNTranDiatHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadDiatHyp_ / _uDepthWHyp_ - _wNDilDiatHyp_ _ENDIF_
```

### `_wDTranGrenHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Gren
- **Equation**:

```
_wDTranGrenHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadGrenHyp_ / _uDepthWHyp_ - _wDDilGrenHyp_ _ENDIF_
```

### `_wPTranGrenHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Gren
- **Equation**:

```
_wPTranGrenHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadGrenHyp_ / _uDepthWHyp_ - _wPDilGrenHyp_ _ENDIF_
```

### `_wNTranGrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Gren
- **Equation**:

```
_wNTranGrenHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadGrenHyp_ / _uDepthWHyp_ - _wNDilGrenHyp_ _ENDIF_
```

### `_wDTranBlueHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Blue
- **Equation**:

```
_wDTranBlueHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadBlueHyp_ / _uDepthWHyp_ - _wDDilBlueHyp_ _ENDIF_
```

### `_wPTranBlueHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Blue
- **Equation**:

```
_wPTranBlueHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadBlueHyp_ / _uDepthWHyp_ - _wPDilBlueHyp_ _ENDIF_
```

### `_wNTranBlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Blue
- **Equation**:

```
_wNTranBlueHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadBlueHyp_ / _uDepthWHyp_ - _wNDilBlueHyp_ _ENDIF_
```

### `_wDTranPhytHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_D_in_Phyt
- **Equation**:

```
_wDTranPhytHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wDTranDiatHyp_ + _wDTranGrenHyp_ + _wDTranBlueHyp_ _ENDIF_
```

### `_wPTranPhytHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_P_in_Phyt
- **Equation**:

```
_wPTranPhytHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wPTranDiatHyp_ + _wPTranGrenHyp_ + _wPTranBlueHyp_ _ENDIF_
```

### `_wNTranPhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_N_in_Phyt
- **Equation**:

```
_wNTranPhytHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wNTranDiatHyp_ + _wNTranGrenHyp_ + _wNTranBlueHyp_ _ENDIF_
```

### `_wSiTranSiO2Hyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_Si_in_SIO2
- **Equation**:

```
_wSiTranSiO2Hyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadSiO2Hyp_ / _uDepthWHyp_ - _wSiDilSiO2Hyp_ _ENDIF_
```

### `_wSiTranDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_Si_in_detritus
- **Equation**:

```
_wSiTranDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadDetHyp_ / _uDepthWHyp_ - _wSiDilDetHyp_ _ENDIF_
```

### `_tSiTranTotTHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_transport_flux
- **Equation**:

```
_tSiTranTotTHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadHyp_ - _wSiDilTotHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_wDTranZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_D_in_Zoo
- **Equation**:

```
_wDTranZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uDLoadZooHyp_ /_uDepthWHyp_ - _wDDilZooHyp_) _ENDIF_
```

### `_wPTranZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_P_in_ZOO
- **Equation**:

```
_wPTranZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uPLoadZooHyp_ /_uDepthWHyp_ - _wPDilZooHyp_) _ENDIF_
```

### `_wNTranZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_N_in_Zoo
- **Equation**:

```
_wNTranZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uNLoadZooHyp_ /_uDepthWHyp_ - _wNDilZooHyp_) _ENDIF_
```

### `_wDTranIMWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_DW_in_IM
- **Equation**:

```
_wDTranIMWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadIMHyp_ / _uDepthWHyp_ - _wDDilIMHyp_ _ENDIF_
```

### `_wDTranDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_DW_in_detritus
- **Equation**:

```
_wDTranDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadDetHyp_ / _uDepthWHyp_ - _wDDilDetHyp_ _ENDIF_
```

### `_wO2TranWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_O2
- **Equation**:

```
_wO2TranWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uO2LoadHyp_ / _uDepthWHyp_ - _wO2OutflHyp_ _ENDIF_
```

### `_wPTranPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_PO4
- **Equation**:

```
_wPTranPO4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadPO4Hyp_ / _uDepthWHyp_ - _wPDilPO4Hyp_ _ENDIF_
```

### `_wPTranAIMWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_AIM
- **Equation**:

```
_wPTranAIMWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadAIMHyp_ / _uDepthWHyp_ - _wPDilAIMHyp_ _ENDIF_
```

### `_wPTranDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_detritus
- **Equation**:

```
_wPTranDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadDetHyp_ / _uDepthWHyp_ - _wPDilDetHyp_ _ENDIF_
```

### `_wNTranNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_NH4
- **Equation**:

```
_wNTranNH4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadNH4Hyp_ / _uDepthWHyp_ - _wNDilNH4Hyp_ _ENDIF_
```

### `_wNTranNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_NO3
- **Equation**:

```
_wNTranNO3WHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadNO3Hyp_ / _uDepthWHyp_ - _wNDilNO3Hyp_ _ENDIF_
```

### `_wNTranDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_detritus
- **Equation**:

```
_wNTranDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadDetHyp_ / _uDepthWHyp_ - _wNDilDetHyp_ _ENDIF_
```

### `_wDTranDiatEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Diat
- **Equation**:

```
_wDTranDiatEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadDiatEpi_ / _uDepthWEpi_ - _wDDilDiatEpi_ _ENDIF_
```

### `_wPTranDiatEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Diat
- **Equation**:

```
_wPTranDiatEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadDiatEpi_ / _uDepthWEpi_ - _wPDilDiatEpi_ _ENDIF_
```

### `_wNTranDiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Diat
- **Equation**:

```
_wNTranDiatEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadDiatEpi_ / _uDepthWEpi_ - _wNDilDiatEpi_ _ENDIF_
```

### `_wDTranGrenEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Gren
- **Equation**:

```
_wDTranGrenEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadGrenEpi_ / _uDepthWEpi_ - _wDDilGrenEpi_ _ENDIF_
```

### `_wPTranGrenEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Gren
- **Equation**:

```
_wPTranGrenEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadGrenEpi_ / _uDepthWEpi_ - _wPDilGrenEpi_ _ENDIF_
```

### `_wNTranGrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Gren
- **Equation**:

```
_wNTranGrenEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadGrenEpi_ / _uDepthWEpi_ - _wNDilGrenEpi_ _ENDIF_
```

### `_wDTranBlueEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_D_in_Blue
- **Equation**:

```
_wDTranBlueEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadBlueEpi_ / _uDepthWEpi_ - _wDDilBlueEpi_ _ENDIF_
```

### `_wPTranBlueEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_Blue
- **Equation**:

```
_wPTranBlueEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadBlueEpi_ / _uDepthWEpi_ - _wPDilBlueEpi_ _ENDIF_
```

### `_wNTranBlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_Blue
- **Equation**:

```
_wNTranBlueEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadBlueEpi_ / _uDepthWEpi_ - _wNDilBlueEpi_ _ENDIF_
```

### `_wDTranPhytEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_D_in_Phyt
- **Equation**:

```
_wDTranPhytEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wDTranDiatEpi_ + _wDTranGrenEpi_ + _wDTranBlueEpi_ _ENDIF_
```

### `_wPTranPhytEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_P_in_Phyt
- **Equation**:

```
_wPTranPhytEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wPTranDiatEpi_ + _wPTranGrenEpi_ + _wPTranBlueEpi_ _ENDIF_
```

### `_wNTranPhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_transport_flux_of_N_in_Phyt
- **Equation**:

```
_wNTranPhytEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _wNTranDiatEpi_ + _wNTranGrenEpi_ + _wNTranBlueEpi_ _ENDIF_
```

### `_wSiTranSiO2Epi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_Si_in_SIO2_in_epilimnion
- **Equation**:

```
_wSiTranSiO2Epi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadSiO2Epi_ / _uDepthWEpi_ - _wSiDilSiO2Epi_ _ENDIF_
```

### `_wSiTranDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_Si_in_detritus_in_epilimnion
- **Equation**:

```
_wSiTranDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadDetEpi_ / _uDepthWEpi_ - _wSiDilDetEpi_ _ENDIF_
```

### `_tSiTranTotTEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_transport_flux
- **Equation**:

```
_tSiTranTotTEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uSiLoadEpi_ - _wSiDilTotEpi_ * _uDepthWEpi_ _ENDIF_
```

### `_wDTranZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_D_in_Zoo_in_epilimnion
- **Equation**:

```
_wDTranZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uDLoadZooEpi_ /_uDepthWEpi_ - _wDDilZooEpi_) _ENDIF_
```

### `_wPTranZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_P_in_Zoo_in_epilimnion
- **Equation**:

```
_wPTranZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uPLoadZooEpi_ /_uDepthWEpi_ - _wPDilZooEpi_) _ENDIF_
```

### `_wNTranZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Net_migration_flux_of_N_in_Zoo_in_epilimnion
- **Equation**:

```
_wNTranZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ (_uNLoadZooEpi_ /_uDepthWEpi_ - _wNDilZooEpi_) _ENDIF_
```

### `_wDTranIMWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_DW_in_IM
- **Equation**:

```
_wDTranIMWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadIMEpi_ / _uDepthWEpi_ - _wDDilIMEpi_ _ENDIF_
```

### `_wDTranDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_DW_in_detritus
- **Equation**:

```
_wDTranDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadDetEpi_ / _uDepthWEpi_ - _wDDilDetEpi_ _ENDIF_
```

### `_wO2TranWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_O2
- **Equation**:

```
_wO2TranWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uO2LoadEpi_ / _uDepthWEpi_ - _wO2OutflEpi_ _ENDIF_
```

### `_wPTranPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_PO4
- **Equation**:

```
_wPTranPO4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadPO4Epi_ / _uDepthWEpi_ - _wPDilPO4Epi_ _ENDIF_
```

### `_wPTranAIMWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_AIM
- **Equation**:

```
_wPTranAIMWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadAIMEpi_ / _uDepthWEpi_ - _wPDilAIMEpi_ _ENDIF_
```

### `_wPTranDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_P_in_detritus
- **Equation**:

```
_wPTranDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadDetEpi_ / _uDepthWEpi_ - _wPDilDetEpi_ _ENDIF_
```

### `_wNTranNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_NH4
- **Equation**:

```
_wNTranNH4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadNH4Epi_ / _uDepthWEpi_ - _wNDilNH4Epi_ _ENDIF_
```

### `_wNTranNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_NO3
- **Equation**:

```
_wNTranNO3WEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadNO3Epi_ / _uDepthWEpi_ - _wNDilNO3Epi_ _ENDIF_
```

### `_wNTranDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Transport_flux_of_N_in_detritus
- **Equation**:

```
_wNTranDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadDetEpi_ / _uDepthWEpi_ - _wNDilDetEpi_ _ENDIF_
```

### `_tDTranBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Transport_flux_of_D_in_Blue
- **Equation**:

```
_tDTranBlueSurf_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _uDLoadBlueSurf_ - _tDDilBlueSurf_ _ENDIF_
```

### `_tPTranBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Transport_flux_of_P_in_Blue
- **Equation**:

```
_tPTranBlueSurf_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _uPLoadBlueSurf_ - _tPDilBlueSurf_ _ENDIF_
```

### `_tNTranBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Transport_flux_of_N_in_Blue
- **Equation**:

```
_tNTranBlueSurf_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _uNLoadBlueSurf_ - _tNDilBlueSurf_ _ENDIF_
```

## Dillution  (66 equations)

### `_wDDilIMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_DW_IM
- **Equation**:

```
_wDDilIMHyp_ = _ukOutHyp_ * _oDIMWHyp_
```

### `_wDDilDetHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wDDilDetHyp_ = _ukOutHyp_ * _oDDetWHyp_
```

### `_wDDilGrenHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wDDilGrenHyp_ = _ukOutHyp_ * _oDGrenWHyp_
```

### `_wDDilBlueHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wDDilBlueHyp_ = _ukOutHyp_ * _oDBlueWHyp_
```

### `_wDDilDiatHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wDDilDiatHyp_ = _ukOutHyp_ * _oDDiatWHyp_
```

### `_wDDilZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_zooplankton_dilution
- **Equation**:

```
_wDDilZooHyp_ = _ukOutHyp_ * _oDZooHyp_
```

### `_wPDilZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_zooplankton_dilution
- **Equation**:

```
_wPDilZooHyp_ = _ukOutHyp_ * _oPZooHyp_
```

### `_wNDilZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_zooplankton_dilution
- **Equation**:

```
_wNDilZooHyp_ = _ukOutHyp_ * _oNZooHyp_
```

### `_wPDilPO4Hyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_SRP
- **Equation**:

```
_wPDilPO4Hyp_ = _ukOutHyp_ * _oPO4WHyp_
```

### `_wPDilDetHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wPDilDetHyp_ = _ukOutHyp_*_oPDetWHyp_
```

### `_wPDilAIMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_IM-ads_P
- **Equation**:

```
_wPDilAIMHyp_ = _ukOutHyp_ * _oPAIMWHyp_
```

### `_wNDilNH4Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_ammonium
- **Equation**:

```
_wNDilNH4Hyp_ = _ukOutHyp_ * _oNH4WHyp_
```

### `_wNDilNO3Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_nitrate
- **Equation**:

```
_wNDilNO3Hyp_ = _ukOutHyp_ * _oNO3WHyp_
```

### `_wNDilDetHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wNDilDetHyp_ = _ukOutHyp_ * _oNDetWHyp_
```

### `_wO2OutflHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Oxygen_outflow
- **Equation**:

```
_wO2OutflHyp_ = _ukOutHyp_ * _oO2WHyp_
```

### `_wPDilDiatHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wPDilDiatHyp_ = _ukOutHyp_ * _oPDiatWHyp_
```

### `_wNDilDiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wNDilDiatHyp_ = _ukOutHyp_ * _oNDiatWHyp_
```

### `_wPDilGrenHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wPDilGrenHyp_ = _ukOutHyp_ * _oPGrenWHyp_
```

### `_wNDilGrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wNDilGrenHyp_ = _ukOutHyp_ * _oNGrenWHyp_
```

### `_wPDilBlueHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wPDilBlueHyp_ = _ukOutHyp_ * _oPBlueWHyp_
```

### `_wNDilBlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wNDilBlueHyp_ = _ukOutHyp_ * _oNBlueWHyp_
```

### `_wSiDilSiO2Hyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_sio2
- **Equation**:

```
_wSiDilSiO2Hyp_ = _ukOutHyp_ * _oSiO2WHyp_
```

### `_wSiDilDetHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_detritus
- **Equation**:

```
_wSiDilDetHyp_ = _ukOutHyp_ * _oSiDetWHyp_
```

### `_wSiDilDiatHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_diatoms
- **Equation**:

```
_wSiDilDiatHyp_ = _cSiDDiat_ * _wDDilDiatHyp_
```

### `_wDDilPhytHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wDDilPhytHyp_ = _wDDilDiatHyp_ + _wDDilGrenHyp_ + _wDDilBlueHyp_
```

### `_wPDilPhytHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wPDilPhytHyp_ = _wPDilDiatHyp_ + _wPDilGrenHyp_ + _wPDilBlueHyp_
```

### `_wNDilPhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wNDilPhytHyp_ = _wNDilDiatHyp_ + _wNDilGrenHyp_ + _wNDilBlueHyp_
```

### `_wSiDilTotHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_SI_dilution_fluxes
- **Equation**:

```
_wSiDilTotHyp_ = _wSiDilDetHyp_ + _wSiDilSiO2Hyp_ + _wSiDilDiatHyp_
```

### `_wDDilTotHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_DW_dilution_fluxes
- **Equation**:

```
_wDDilTotHyp_ = _wDDilIMHyp_ + _wDDilDetHyp_ + _wDDilPhytHyp_
```

### `_wPDilTotHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_dilution_fluxes
- **Equation**:

```
_wPDilTotHyp_ = _wPDilDetHyp_ + _wPDilPO4Hyp_ + _wPDilAIMHyp_ + _wPDilPhytHyp_
```

### `_wNDilTotHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_dilution_fluxes
- **Equation**:

```
_wNDilTotHyp_ = _wNDilDetHyp_ + _wNDilNO3Hyp_ + _wNDilNH4Hyp_ + _wNDilPhytHyp_
```

### `_wDDilIMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_DW_IM
- **Equation**:

```
_wDDilIMEpi_ = _ukOutEpi_ * _oDIMWEpi_
```

### `_wDDilDetEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wDDilDetEpi_ = _ukOutEpi_ * _oDDetWEpi_
```

### `_wDDilDiatEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wDDilDiatEpi_ = _ukOutEpi_ * _oDDiatWEpi_
```

### `_wDDilGrenEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wDDilGrenEpi_ = _ukOutEpi_ * _oDGrenWEpi_
```

### `_wDDilBlueEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wDDilBlueEpi_ = _ukOutEpi_ * _oDBlueWEpi_
```

### `_wDDilPhytEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wDDilPhytEpi_ = _wDDilDiatEpi_ + _wDDilGrenEpi_ + _wDDilBlueEpi_
```

### `_wDDilZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wDDilZooEpi_ = _ukOutEpi_ * _oDZooEpi_
```

### `_wPDilZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wPDilZooEpi_ = _ukOutEpi_ * _oPZooEpi_
```

### `_wNDilZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wNDilZooEpi_ = _ukOutEpi_ * _oNZooEpi_
```

### `_wPDilPO4Epi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_SRP
- **Equation**:

```
_wPDilPO4Epi_ = _ukOutEpi_ * _oPO4WEpi_
```

### `_wPDilDetEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wPDilDetEpi_ = _ukOutEpi_*_oPDetWEpi_
```

### `_wPDilAIMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_IM-ads_P
- **Equation**:

```
_wPDilAIMEpi_ = _ukOutEpi_ * _oPAIMWEpi_
```

### `_wNDilNH4Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_ammonium
- **Equation**:

```
_wNDilNH4Epi_ = _ukOutEpi_ * _oNH4WEpi_
```

### `_wNDilNO3Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_nitrate
- **Equation**:

```
_wNDilNO3Epi_ = _ukOutEpi_ * _oNO3WEpi_
```

### `_wNDilDetEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_detritus
- **Equation**:

```
_wNDilDetEpi_ = _ukOutEpi_ * _oNDetWEpi_
```

### `_uO2LoadEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Oxygen_inflow
- **Equation**:

```
_uO2LoadEpi_ = _IF_ (_ReadTranFrac_ _EQ_ _TRUE_) _THEN_ _mO2LoadEpi_ _ELSE_ _cO2In_ * _uQInEpi_ / _mmPerm_ _ENDIF_
```

### `_wO2OutflEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Oxygen_outflow
- **Equation**:

```
_wO2OutflEpi_ = _ukOutEpi_ * _oO2WEpi_
```

### `_wPDilDiatEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wPDilDiatEpi_ = _ukOutEpi_ * _oPDiatWEpi_
```

### `_wNDilDiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Diat
- **Equation**:

```
_wNDilDiatEpi_ = _ukOutEpi_ * _oNDiatWEpi_
```

### `_wPDilGrenEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wPDilGrenEpi_ = _ukOutEpi_ * _oPGrenWEpi_
```

### `_wNDilGrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Gren
- **Equation**:

```
_wNDilGrenEpi_ = _ukOutEpi_ * _oNGrenWEpi_
```

### `_wPDilBlueEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wPDilBlueEpi_ = _ukOutEpi_ * _oPBlueWEpi_
```

### `_wNDilBlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_wNDilBlueEpi_ = _ukOutEpi_ * _oNBlueWEpi_
```

### `_wPDilPhytEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wPDilPhytEpi_ = _wPDilDiatEpi_ + _wPDilGrenEpi_ + _wPDilBlueEpi_
```

### `_wNDilPhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_algal_dilution
- **Equation**:

```
_wNDilPhytEpi_ = _wNDilDiatEpi_ + _wNDilGrenEpi_ + _wNDilBlueEpi_
```

### `_wSiDilSiO2Epi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_sio2
- **Equation**:

```
_wSiDilSiO2Epi_ = _ukOutEpi_ * _oSiO2WEpi_
```

### `_wSiDilDetEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_detritus
- **Equation**:

```
_wSiDilDetEpi_ = _ukOutEpi_ * _oSiDetWEpi_
```

### `_wSiDilDiatEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Dilution_of_Si_in_diatoms
- **Equation**:

```
_wSiDilDiatEpi_ = _cSiDDiat_ * _wDDilDiatEpi_
```

### `_wDDilTotEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_DW_dilution_fluxes
- **Equation**:

```
_wDDilTotEpi_ = _wDDilIMEpi_ + _wDDilDetEpi_ + _wDDilPhytEpi_
```

### `_wPDilTotEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_dilution_fluxes
- **Equation**:

```
_wPDilTotEpi_ = _wPDilDetEpi_ + _wPDilPO4Epi_ + _wPDilAIMEpi_ + _wPDilPhytEpi_
```

### `_wNDilTotEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_dilution_fluxes
- **Equation**:

```
_wNDilTotEpi_ = _wNDilDetEpi_ + _wNDilNO3Epi_ + _wNDilNH4Epi_ + _wNDilPhytEpi_
```

### `_wSiDilTotEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_SI_dilution_fluxes
- **Equation**:

```
_wSiDilTotEpi_ = _wSiDilDetEpi_ + _wSiDilSiO2Epi_ + _wSiDilDiatEpi_
```

### `_tDDilBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_tDDilBlueSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _ukDilSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_tNDilBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_tNDilBlueSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _ukDilSurf_ * _aNBlueSurf_ _ENDIF_
```

### `_tPDilBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dilution_of_Blue
- **Equation**:

```
_tPDilBlueSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _ukDilSurf_ * _aPBlueSurf_ _ENDIF_
```

## Outflow  (8 equations)

### `_wDOutflTotHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_DW
- **Equation**:

```
_wDOutflTotHyp_ = _ukOutHyp_ * _oDSestWHyp_
```

### `_wPOutflTotHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_P
- **Equation**:

```
_wPOutflTotHyp_ = _ukOutHyp_ * _oPTotWHyp_
```

### `_wNOutflTotHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_N
- **Equation**:

```
_wNOutflTotHyp_ = _ukOutHyp_ * _oNTotWHyp_
```

### `_wSiOutflTotHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_surface_outflow
- **Equation**:

```
_wSiOutflTotHyp_ = _ukOutHyp_ * (_oSiO2WHyp_ + _oSiDetWHyp_ + _cSiDDiat_ * _oDDiatWHyp_)
```

### `_wDOutflTotEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_DW
- **Equation**:

```
_wDOutflTotEpi_ = _ukOutEpi_ * _oDSestWEpi_
```

### `_wPOutflTotEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_P
- **Equation**:

```
_wPOutflTotEpi_ = _ukOutEpi_ * _oPTotWEpi_
```

### `_wNOutflTotEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Outflow_of_N
- **Equation**:

```
_wNOutflTotEpi_ = _ukOutEpi_ * _oNTotWEpi_
```

### `_wSiOutflTotEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_surface_outflow
- **Equation**:

```
_wSiOutflTotEpi_ = _ukOutEpi_ * (_oSiO2WEpi_ + _oSiDetWEpi_ + _cSiDDiat_ * _oDDiatWEpi_)
```

## Mass_balance_equations  (6 equations)

### `_tDTranTotTHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_DW_for_mass_balance_equations
- **Equation**:

```
_tDTranTotTHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadHyp_ - _wDDilTotHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_tPTranTotTHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_P_for_mass_balance_equations
- **Equation**:

```
_tPTranTotTHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadHyp_ - _wPDilTotHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_tNTranTotTHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_N_for_mass_balance_equations
- **Equation**:

```
_tNTranTotTHyp_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadHyp_ - _wNDilTotHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_tDTranTotTEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_DW_for_mass_balance_equations
- **Equation**:

```
_tDTranTotTEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uDLoadEpi_ - _wDDilTotEpi_ * _uDepthWEpi_ _ENDIF_
```

### `_tPTranTotTEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_P_for_mass_balance_equations
- **Equation**:

```
_tPTranTotTEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uPLoadEpi_ - _wPDilTotEpi_ * _uDepthWEpi_ _ENDIF_
```

### `_tNTranTotTEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_transport_fluxes_of_N_for_mass_balance_equations
- **Equation**:

```
_tNTranTotTEpi_ = _IF_ (_FALSE_ _EQ_ _InclTran_) _THEN_ 0.0 _ELSE_ _uNLoadEpi_ - _wNDilTotEpi_ * _uDepthWEpi_ _ENDIF_
```

## Exchange_fluxes_for_marsh  (96 equations)

### `_wDExchIMMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_IM_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchIMMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDIMWHyp_ - _oDIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4MHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_PO4_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchPO4MHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPO4WHyp_ - _oPO4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_AIM_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchAIMMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPAIMWHyp_ - _oPAIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4MHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NH4_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchNH4MHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNH4WHyp_ - _oNH4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3MHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NO3_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchNO3MHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNO3WHyp_ - _oNO3WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2MHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_hypolimnion_to_marsh
- **Equation**:

```
_wSiExchSiO2MHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oSiO2WHyp_ - _oSiO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchMHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_hypolimnion_to_marsh
- **Equation**:

```
_wO2ExchMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oO2WHyp_ - _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_detritus_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchDetMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDDetWHyp_ - _oDDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchDetMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPDetWHyp_ - _oPDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetMHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchDetMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNDetWHyp_ - _oNDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetMHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_hypolimnion_to_marsh
- **Equation**:

```
_wSiExchDetMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oSiDetWHyp_ - _oSiDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchDiatMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDDiatWHyp_ - _oDDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchDiatMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPDiatWHyp_ - _oPDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatMHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchDiatMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNDiatWHyp_ - _oNDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatMHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_hypolimnion_to_marsh
- **Equation**:

```
_wSiExchDiatMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cSiDDiat_ * _wDExchDiatMHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchGrenMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDGrenWHyp_ - _oDGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchGrenMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPGrenWHyp_ - _oPGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenMHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchGrenMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNGrenWHyp_ - _oNGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchBlueMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDBlueWHyp_ - _oDBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchBlueMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPBlueWHyp_ - _oPBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueMHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchBlueMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNBlueWHyp_ - _oNBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_hypolimnion_to_marsh
- **Equation**:

```
_wDExchZooMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oDZooHyp_ - _oDZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_hypolimnion_to_marsh
- **Equation**:

```
_wPExchZooMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oPZooHyp_ - _oPZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooMHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_hypolimnion_to_marsh
- **Equation**:

```
_wNExchZooMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMHyp_ *(_oNZooHyp_ - _oNZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchIMHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_IM_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchIMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDIMWHyp_ - _oDIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4Hyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_PO4_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchPO4Hyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPO4WHyp_ - _oPO4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_AIM_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchAIMHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPAIMWHyp_ - _oPAIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NH4_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchNH4Hyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNH4WHyp_ - _oNH4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NO3_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchNO3Hyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNO3WHyp_ - _oNO3WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2Hyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_marsh_to_hypolimnion
- **Equation**:

```
_wSiExchSiO2Hyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oSiO2WHyp_ - _oSiO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_marsh_to_hypolimnion
- **Equation**:

```
_wO2ExchHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oO2WHyp_ - _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_detritus_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchDetHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDDetWHyp_ - _oDDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchDetHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPDetWHyp_ - _oPDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchDetHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNDetWHyp_ - _oNDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_marsh_to_hypolimnion
- **Equation**:

```
_wSiExchDetHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oSiDetWHyp_ - _oSiDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchDiatHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDDiatWHyp_ - _oDDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchDiatHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPDiatWHyp_ - _oPDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchDiatHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNDiatWHyp_ - _oNDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_marsh_to_hypolimnion
- **Equation**:

```
_wSiExchDiatHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cSiDDiat_ * _wDExchDiatHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchGrenHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDGrenWHyp_ - _oDGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchGrenHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPGrenWHyp_ - _oPGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchGrenHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNGrenWHyp_ - _oNGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchBlueHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDBlueWHyp_ - _oDBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchBlueHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPBlueWHyp_ - _oPBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchBlueHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNBlueWHyp_ - _oNBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_marsh_to_hypolimnion
- **Equation**:

```
_wDExchZooHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oDZooHyp_ - _oDZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_marsh_to_hypolimnion
- **Equation**:

```
_wPExchZooHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oPZooHyp_ - _oPZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_marsh_to_hypolimnion
- **Equation**:

```
_wNExchZooHyp_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLHyp_ *(_oNZooHyp_ - _oNZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchIMMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_IM_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchIMMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDIMWEpi_ - _oDIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4MEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_PO4_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchPO4MEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPO4WEpi_ - _oPO4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_AIM_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchAIMMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPAIMWEpi_ - _oPAIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4MEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NH4_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchNH4MEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNH4WEpi_ - _oNH4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3MEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NO3_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchNO3MEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNO3WEpi_ - _oNO3WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2MEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_epilimnion_to_marsh
- **Equation**:

```
_wSiExchSiO2MEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oSiO2WEpi_ - _oSiO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchMEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_epilimnion_to_marsh
- **Equation**:

```
_wO2ExchMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oO2WEpi_ - _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_detritus_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchDetMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDDetWEpi_ - _oDDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchDetMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPDetWEpi_ - _oPDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetMEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchDetMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNDetWEpi_ - _oNDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetMEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_epilimnion_to_marsh
- **Equation**:

```
_wSiExchDetMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oSiDetWEpi_ - _oSiDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchDiatMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDDiatWEpi_ - _oDDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchDiatMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPDiatWEpi_ - _oPDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatMEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchDiatMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNDiatWEpi_ - _oNDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatMEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_epilimnion_to_marsh
- **Equation**:

```
_wSiExchDiatMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cSiDDiat_ * _wDExchDiatMEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchGrenMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDGrenWEpi_ - _oDGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchGrenMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPGrenWEpi_ - _oPGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenMEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchGrenMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNGrenWEpi_ - _oNGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchBlueMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDBlueWEpi_ - _oDBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchBlueMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPBlueWEpi_ - _oPBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueMEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchBlueMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNBlueWEpi_ - _oNBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_epilimnion_to_marsh
- **Equation**:

```
_wDExchZooMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oDZooEpi_ - _oDZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_epilimnion_to_marsh
- **Equation**:

```
_wPExchZooMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oPZooEpi_ - _oPZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooMEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_epilimnion_to_marsh
- **Equation**:

```
_wNExchZooMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchMEpi_ *(_oNZooEpi_ - _oNZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchIMEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_IM_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchIMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDIMWEpi_ - _oDIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchPO4Epi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_PO4_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchPO4Epi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPO4WEpi_ - _oPO4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchAIMEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_AIM_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchAIMEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPAIMWEpi_ - _oPAIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNH4Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NH4_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchNH4Epi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNH4WEpi_ - _oNH4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchNO3Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_NO3_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchNO3Epi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNO3WEpi_ - _oNO3WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchSiO2Epi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_SiO2_from_marsh_to_epilimnion
- **Equation**:

```
_wSiExchSiO2Epi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oSiO2WEpi_ - _oSiO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2ExchEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_O2_from_marsh_to_epilimnion
- **Equation**:

```
_wO2ExchEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oO2WEpi_ - _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDetEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_detritus_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchDetEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDDetWEpi_ - _oDDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDetEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_detritus_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchDetEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPDetWEpi_ - _oPDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDetEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_detritus_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchDetEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNDetWEpi_ - _oNDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDetEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_detritus_from_marsh_to_epilimnion
- **Equation**:

```
_wSiExchDetEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oSiDetWEpi_ - _oSiDetWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchDiatEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_diatoms_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchDiatEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDDiatWEpi_ - _oDDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchDiatEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_diatoms_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchDiatEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPDiatWEpi_ - _oPDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchDiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_diatoms_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchDiatEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNDiatWEpi_ - _oNDiatWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wSiExchDiatEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_Si_in_diatoms_from_marsh_to_epilimnion
- **Equation**:

```
_wSiExchDiatEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cSiDDiat_ * _wDExchDiatEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wDExchGrenEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_green_algae_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchGrenEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDGrenWEpi_ - _oDGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchGrenEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_green_algae_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchGrenEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPGrenWEpi_ - _oPGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchGrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_green_algae_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchGrenEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNGrenWEpi_ - _oNGrenWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchBlueEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_blue_greens_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchBlueEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDBlueWEpi_ - _oDBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchBlueEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_blue_greens_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchBlueEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPBlueWEpi_ - _oPBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchBlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_blue_greens_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchBlueEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNBlueWEpi_ - _oNBlueWM_) _ELSE_ 0.0 _ENDIF_
```

### `_wDExchZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_DW_in_zooplankton_from_marsh_to_epilimnion
- **Equation**:

```
_wDExchZooEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oDZooEpi_ - _oDZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wPExchZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_P_in_zooplankton_from_marsh_to_epilimnion
- **Equation**:

```
_wPExchZooEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oPZooEpi_ - _oPZooM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNExchZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Diffusive_exchange_flux_of_N_in_zooplankton_from_marsh_to_epilimnion
- **Equation**:

```
_wNExchZooEpi_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _akExchLEpi_ *(_oNZooEpi_ - _oNZooM_) _ELSE_ 0.0 _ENDIF_
```

## Infiltration  (21 equations)

### `_tInfSiO2WHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SiO2
- **Equation**:

```
_tInfSiO2WHyp_ =  _IF_ (_InclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oSiO2WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tInfO2WHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_O2
- **Equation**:

```
_tInfO2WHyp_ =  _IF_ (_InclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oO2WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPInfPO4WHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SRP
- **Equation**:

```
_tPInfPO4WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oPO4WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNH4WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_ammonium
- **Equation**:

```
_tNInfNH4WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNH4WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNO3WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_nitrate
- **Equation**:

```
_tNInfNO3WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNO3WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPInfPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_PO4
- **Equation**:

```
_tPInfPO4S_ = _IF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oPO4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_NH4
- **Equation**:

```
_tNInfNH4S_ = _IF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNH4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_NO3
- **Equation**:

```
_tNInfNO3S_ = _IF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNO3S_ _ELSE_ 0.0 _ENDIF_
```

### `_tInfSiO2WM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SiO2
- **Equation**:

```
_tInfSiO2WM_ = _IF_ ((_InclMarsh_ _EQ_ _FALSE_) _OR_ (_fMarsh_ _LE_ _NearZero_)) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oSiO2WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tInfO2WM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_O2
- **Equation**:

```
_tInfO2WM_ = _IF_ ((_InclMarsh_ _EQ_ _FALSE_) _OR_ (_fMarsh_ _LE_ _NearZero_)) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oO2WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPInfPO4WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SRP
- **Equation**:

```
_tPInfPO4WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oPO4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNH4WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_ammonium
- **Equation**:

```
_tNInfNH4WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNO3WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_nitrate
- **Equation**:

```
_tNInfNO3WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNO3WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPInfPO4SM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_PO4
- **Equation**:

```
_tPInfPO4SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oPO4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNH4SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_NH4
- **Equation**:

```
_tNInfNH4SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNH4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNO3SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_interstitial_NO3
- **Equation**:

```
_tNInfNO3SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNO3SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tInfSiO2WEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SiO2
- **Equation**:

```
_tInfSiO2WEpi_ =_IF_ (_InclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oSiO2WEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tInfO2WEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_O2
- **Equation**:

```
_tInfO2WEpi_ =_IF_ (_InclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oO2WEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tPInfPO4WEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_SRP
- **Equation**:

```
_tPInfPO4WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oPO4WEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNH4WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_ammonium
- **Equation**:

```
_tNInfNH4WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNH4WEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tNInfNO3WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Infiltration_of_nitrate
- **Equation**:

```
_tNInfNO3WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQOutInf_ _GE_ 0.0) _THEN_ _uQOutInf_ / _mmPerm_ * _oNO3WEpi_ _ELSE_ 0.0 _ENDIF_
```

## Seepage  (21 equations)

### `_tSeepSiO2WHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SiO2
- **Equation**:

```
_tSeepSiO2WHyp_ =  _IF_ (_InclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tSeepO2WHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_O2
- **Equation**:

```
_tSeepO2WHyp_ =  _IF_ (_InclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tPSeepPO4WHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SRP
- **Equation**:

```
_tPSeepPO4WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oPO4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNH4WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_ammonium
- **Equation**:

```
_tNSeepNH4WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNH4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNO3WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_nitrate
- **Equation**:

```
_tNSeepNO3WHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNO3S_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSeepPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_PO4
- **Equation**:

```
_tPSeepPO4S_ = _IF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cPO4Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_NH4
- **Equation**:

```
_tNSeepNH4S_ = _IF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cNH4Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_NO3
- **Equation**:

```
_tNSeepNO3S_ = _IF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cNO3Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tSeepSiO2WM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SiO2
- **Equation**:

```
_tSeepSiO2WM_ = _IF_ ((_InclMarsh_ _EQ_ _FALSE_) _OR_ (_fMarsh_ _LT_ _NearZero_)) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tSeepO2WM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_O2
- **Equation**:

```
_tSeepO2WM_ = _IF_ ((_InclMarsh_ _EQ_ _FALSE_) _OR_ (_fMarsh_ _LT_ _NearZero_)) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tPSeepPO4WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SRP
- **Equation**:

```
_tPSeepPO4WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oPO4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNH4WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_ammonium
- **Equation**:

```
_tNSeepNH4WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNH4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNO3WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_nitrate
- **Equation**:

```
_tNSeepNO3WM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNO3SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSeepPO4SM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_PO4
- **Equation**:

```
_tPSeepPO4SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cPO4Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNH4SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_NH4
- **Equation**:

```
_tNSeepNH4SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cNH4Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNO3SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_interstitial_NO3
- **Equation**:

```
_tNSeepNO3SM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _cNO3Ground_ _ELSE_ 0.0 _ENDIF_
```

### `_tSeepSiO2WEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SiO2
- **Equation**:

```
_tSeepSiO2WEpi_ =_IF_ (_InclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tSeepO2WEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_O2
- **Equation**:

```
_tSeepO2WEpi_ =_IF_ (_InclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tPSeepPO4WEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_SRP
- **Equation**:

```
_tPSeepPO4WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oPO4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNH4WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_ammonium
- **Equation**:

```
_tNSeepNH4WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNH4S_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSeepNO3WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Seepage_of_nitrate
- **Equation**:

```
_tNSeepNO3WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSEIF_ (_uQInSeep_ _GE_ 0.0) _THEN_ _uQInSeep_ / _mmPerm_ * _oNO3S_ _ELSE_ 0.0 _ENDIF_
```

## Erosion  (6 equations)

### `_uDErosIM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: IM_input_from_banks
- **Equation**:

```
_uDErosIM_ = (1.0 - _fDOrgSoil_) * _cDErosTot_
```

### `_uDErosIMS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: IM_input_to_sediment_from_banks
- **Equation**:

```
_uDErosIMS_ = _fSedErosIM_ * _uDErosIM_
```

### `_uDErosIMW_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: IM_input_to_water_column_from_banks
- **Equation**:

```
_uDErosIMW_ = _uDErosIM_ - _uDErosIMS_
```

### `_uDErosOM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Organic_matter_input_from_banks
- **Equation**:

```
_uDErosOM_ = _fDOrgSoil_ * _cDErosTot_
```

### `_uPErosOM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Organic_P_input_from_banks
- **Equation**:

```
_uPErosOM_ = _cPDSoilOM_ * _uDErosOM_
```

### `_uNErosOM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Organic_N_input_from_banks
- **Equation**:

```
_uNErosOM_ = _cNDSoilOM_ * _uDErosOM_
```

## Reaeration  (13 equations)

### `_uO2SatEpi_`  [_gO2_*_m_^-3]
- **Description**: Oxygen_saturation_concentration
- **Equation**:

```
_uO2SatEpi_ = 14.652 - 0.41022 * _uTmEpi_ + 0.007991 * _uTmEpi_*_uTmEpi_ - 0.000077774 * _uTmEpi_*_uTmEpi_*_uTmEpi_
```

### `_uO2SatHyp_`  [_gO2_*_m_^-3]
- **Description**: Oxygen_saturation_concentration
- **Equation**:

```
_uO2SatHyp_ = 14.652 - 0.41022 * _uTmHyp_ + 0.007991 * _uTmHyp_*_uTmHyp_- 0.000077774 *_uTmHyp_*_uTmHyp_*_uTmHyp_
```

### `_kAer_`  [_m_*_d_^-1]
- **Description**: Reaeration_coefficient
- **Equation**:

```
_kAer_ = _IF_ _POW_ ( _uVWind_ _POWOPERATOR_ (0.5))  _LE_ _NearZero_ _THEN_ 1 _ELSE_ _cAerRoot_ * _POW_ ( _uVWind_ _POWOPERATOR_ (0.5)) + _cAerLin_ * _uVWind_ + _cAerSquare_ * _uVWind_*_uVWind_ _ENDIF_
```

### `_uFunTmAerEpi_`  [0]
- **Description**: Temperature_function_of_reaeration
- **Equation**:

```
_uFunTmAerEpi_ = _IF_  _POW_ ( _cThetaAer_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _LE_ _NearZero_ _THEN_ 1 _ELSE_ _POW_ ( _cThetaAer_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_uFunTmAerHyp_`  [0]
- **Description**: Temperature_function_of_reaeration
- **Equation**:

```
_uFunTmAerHyp_ = _IF_ _POW_ ( _cThetaAer_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_)) _LE_ _NearZero_ _THEN_ 1 _ELSE_ _POW_ ( _cThetaAer_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_)) _ENDIF_
```

### `_aFunFloatAer_`  [0]
- **Description**: Floating_leave_function_of_reaeration
- **Equation**:

```
_aFunFloatAer_ =  _MAX_( 0.0, 1.0 -  ( _kFloatAer_ * _aDFloatVeg_ ) )
```

### `_aFunBlueSurfAer_`  [0]
- **Description**: Surface_Blue_function_of_reaeration
- **Equation**:

```
_aFunBlueSurfAer_ = _MAX_(0.0, 1.0 - (_kBlueSurfAer_ * _aDBlueSurf_))
```

### `_tO2BubHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Bubble_formation
- **Equation**:

```
_tO2BubHyp_ = _IF_ (_uO2SatHyp_ _LT_ _oO2WHyp_ ) _THEN_ _kBub_ * _uFunTmAerHyp_ * (_uO2SatHyp_ - _oO2WHyp_) _ELSE_ 0 _ENDIF_
```

### `_tO2AerM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Reaeration_flux_of_O2_into_the_water
- **Equation**:

```
_tO2AerM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kAer_ * _uFunTmAerEpi_ *(_uO2SatEpi_ - _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_tO2AerEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Reaeration_flux_of_O2_into_the_water
- **Equation**:

```
_tO2AerEpi_ = _kAer_ * _uFunTmAerEpi_ * (_uO2SatEpi_ - _oO2WEpi_) * _aFunFloatAer_ * _aFunBlueSurfAer_
```

### `_dO2WHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_O2_oxygen_in_water_in_lake_water
- **Equation**:

```
_dO2WHyp_ = ( _wO2TranWHyp_ + _wO2AbioWHyp_ + _wO2PrimWHyp_ - _tO2PrimSHyp_ + _tO2BedWHyp_ / _uDepthWHyp_ - _aRelDeltaWHyp_* _oO2WHyp_ - _wO2ExchHyp_ - _wO2ExchWHyp_  - _wO2AdvW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dO2WM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_O2_O2_in_water_in_marsh_water
- **Equation**:

```
_dO2WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wO2AbioM_ + _wO2ExchMEpi_ + _wO2ExchMHyp_ - _aRelDeltaWM_ * _oO2WM_ - _tO2FlowPhra_ / _uDepthWM_ + _wO2AdvWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dO2WEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_O2_oxygen_in_water_in_lake_water
- **Equation**:

```
_dO2WEpi_ = ( _wO2TranWEpi_ + _wO2AbioWEpi_ + _wO2PrimWEpi_ -_tO2PrimSEpi_ + _tO2BedWEpi_ / _uDepthWEpi_ - _aRelDeltaWEpi_ * _oO2WEpi_ - _wO2ExchEpi_ + _wO2ExchWEpi_  + _wO2AdvW_ / _uDepthWEpi_  - _wO2AdvWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

## Fish_process  (1 equations)

### `_uFunTmFish_`  [0]
- **Description**: Temp_function_of_fish
- **Equation**:

```
_uFunTmFish_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ _EXP_( -0.5/(_cSigTmFish_*_cSigTmFish_) * (( _MAX_ (_uTmEpi_, _uTmHyp_ * _aInclStrat_) - _cTmOptFish_)*( _MAX_ (_uTmEpi_, _uTmHyp_ * _aInclStrat_) - _cTmOptFish_) - (_cTmRef_ - _cTmOptFish_)*(_cTmRef_ - _cTmOptFish_))) _ELSE_ 0.0 _ENDIF_
```

## Resuspension  (18 equations)

### `_tDTurbFish_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Bioturbation_by_fish
- **Equation**:

```
_tDTurbFish_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ (_kTurbFish_ * _uFunTmFish_ * _aDFiAd_) _ELSE_ 0.0 _ENDIF_
```

### `_aFunVegResus_`  [0]
- **Description**: Vegetation_dependence_of_resuspension
- **Equation**:

```
_aFunVegResus_ = _MAX_(1.0 - _kVegResus_ * _aDVeg_, _NearZero_)
```

### `_aFunDimSusp_`  [0]
- **Description**: Empirical_suspended_matter_function_(logistic_fit_to_data)
- **Equation**:

```
_aFunDimSusp_ = _IF_ (_uTmEpi_ _GE_ 0.1) _OR_  _POW_(((_cFetch_ +_NearZero_)/ _cFetchRef_) _POWOPERATOR_ (0.5)) _LE_ _NearZero_ _THEN_ _cSuspRef_ * ((_cSuspMin_ + _cSuspMax_ / (1.0 + _EXP_(_cSuspSlope_ * (_uDepthW_ - _hDepthSusp_)))) * _POW_(((_cFetch_ +_NearZero_)/ _cFetchRef_) _POWOPERATOR_ (0.5))) _ELSE_ 0.0 _ENDIF_
```

### `_tDResusTauDead_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_due_to_shear_stress
- **Equation**:

```
_tDResusTauDead_ = _IF_ _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5)) _LE_ _NearZero_ _THEN_ _MIN_(_aFunDimSusp_, _POW_( 1  _POWOPERATOR_ (0.5))) * _POW_(_fLutum_ / _fLutumRef_ _POWOPERATOR_ (0.5)) * _bPorS_ _ELSE_ _MIN_(_aFunDimSusp_, _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5))) * _POW_(_fLutum_ / _fLutumRef_ _POWOPERATOR_ (0.5)) * _bPorS_ _ENDIF_
```

### `_tDResusBareDead_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_due_to_shear_stress_AND_fish
- **Equation**:

```
_tDResusBareDead_ = _tDResusTauDead_ + _tDTurbFish_
```

### `_tDResusDead_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_corrected_for_vegetation_effect
- **Equation**:

```
_tDResusDead_ = _tDResusBareDead_ * _aFunVegResus_
```

### `_tDResusIM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: IM_resuspension
- **Equation**:

```
_tDResusIM_ = _fLutum_ * _aDIMS_ / (_fLutum_ * _aDIMS_ + _aDDetS_) * _tDResusDead_
```

### `_tDResusDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Detrital_resuspension
- **Equation**:

```
_tDResusDet_ = _aDDetS_ / (_fLutum_ * _aDIMS_ + _aDDetS_) * _tDResusDead_
```

### `_akResusPhytRef_`  [_d_^-1]
- **Description**: Phytoplankton_resuspension_rate_constant
- **Equation**:

```
_akResusPhytRef_ = _kResusPhytMax_ * (1.0 - _EXP_(_cResusPhytExp_ * _tDResusDead_))
```

### `_tDResusPhytTot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Phytoplankton_resuspension
- **Equation**:

```
_tDResusPhytTot_ = _akResusPhytRef_ * _aDPhytS_
```

### `_tPResusDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_detrital_P
- **Equation**:

```
_tPResusDet_ = _rPDDetS_ * _tDResusDet_
```

### `_tPResusPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_dissolved_P
- **Equation**:

```
_tPResusPO4_ = _aPO4S_ / _aDDetS_ * _tDResusDet_
```

### `_tPResusAIM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_P_adsorbed_onto_inert_matter
- **Equation**:

```
_tPResusAIM_ = _aPAIMS_ / _aDIMS_ * _tDResusIM_
```

### `_tNResusNO3_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_nitrate
- **Equation**:

```
_tNResusNO3_ = _aNO3S_ / _aDDetS_ * _tDResusDet_
```

### `_tNResusNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_ammonium
- **Equation**:

```
_tNResusNH4_ = _aNH4S_ / _aDDetS_ * _tDResusDet_
```

### `_tNResusDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_detrital_N
- **Equation**:

```
_tNResusDet_ = _rNDDetS_ * _tDResusDet_
```

### `_tSiResusDet_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Resuspension_flux_of_detrital_SI
- **Equation**:

```
_tSiResusDet_ = _rSiDDetS_ * _tDResusDet_
```

### `_tDTurbFishIM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: IM_bioturbation_by_fish
- **Equation**:

```
_tDTurbFishIM_ = _fLutum_ * _aDIMS_ / (_fLutum_ * _aDIMS_ + _aDDetS_) * _tDTurbFish_
```

## Sedimentation  (44 equations)

### `_aFunTauSetOMHyp_`  [0]
- **Description**: Correction_factor_for_IM_settling_rate_(<=_1)
- **Equation**:

```
_aFunTauSetOMHyp_ = _IF_ _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5)) _LT_ _NearZero_ _THEN_ 1 _ELSE_ _MIN_(1.0 / _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5)), 1.0) _ENDIF_
```

### `_aFunTauSetIMHyp_`  [0]
- **Description**: Correction_factor_for_OM_settling_rate_(<=_1)
- **Equation**:

```
_aFunTauSetIMHyp_ = _aFunTauSetOMHyp_
```

### `_uFunTmSetEpi_`  [0]
- **Description**: Temperature_correction_of_sedimentation
- **Equation**:

```
_uFunTmSetEpi_ = _IF_ _POW_ ( _cThetaSet_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_ ( _cThetaSet_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_uFunTmSetHyp_`  [0]
- **Description**: Temperature_correction_of_sedimentation
- **Equation**:

```
_uFunTmSetHyp_ = _IF_ _POW_(_cThetaSet_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaSet_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_)) _ENDIF_
```

### `_uCorVSetIMHyp_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_IM
- **Equation**:

```
_uCorVSetIMHyp_ = _IF_ _POW_((_fLutumRef_/_fLutum_) _POWOPERATOR_ (0.5))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _aFunTauSetIMHyp_ * _POW_((_fLutumRef_/_fLutum_) _POWOPERATOR_ (0.5)) * _uFunTmSetHyp_ * (_cVSetIM_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) _ENDIF_
```

### `_tDSetIMHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_inert_matter
- **Equation**:

```
_tDSetIMHyp_ = _uCorVSetIMHyp_ * _oDIMWHyp_
```

### `_tPSetAIMHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_P_adsorbed_onto_inert_org_matter
- **Equation**:

```
_tPSetAIMHyp_ = _oPAIMWHyp_ / _oDIMWHyp_ * _tDSetIMHyp_
```

### `_uCorVSetDetHyp_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_detritus
- **Equation**:

```
_uCorVSetDetHyp_ = (_cVSetDet_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMHyp_ * _uFunTmSetHyp_
```

### `_tDSetDetHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetDetHyp_ = _uCorVSetDetHyp_ * _oDDetWHyp_
```

### `_tPSetDetHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetDetHyp_ = _uCorVSetDetHyp_ * _oPDetWHyp_
```

### `_tNSetDetHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetDetHyp_ = _uCorVSetDetHyp_ * _oNDetWHyp_
```

### `_tSiSetDetHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_Si
- **Equation**:

```
_tSiSetDetHyp_ = _uCorVSetDetHyp_ * _oSiDetWHyp_
```

### `_tDSetIMM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_inert_matter
- **Equation**:

```
_tDSetIMM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetIM_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oDIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetAIMM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_P_adsorbed_onto_inert_org_matter
- **Equation**:

```
_tPSetAIMM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetIM_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oPAIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetDetM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetDetM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDet_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oDDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetDetM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetDetM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDet_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oPDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetDetM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetDetM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDet_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oNDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiSetDetM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_Si
- **Equation**:

```
_tSiSetDetM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDet_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oSiDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetDiatM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetDiatM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _cVSetDiat_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oDDiatWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetDiatM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetDiatM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDiat_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oPDiatWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetDiatM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetDiatM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _cVSetDiat_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oNDiatWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiSetDiatM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_Si
- **Equation**:

```
_tSiSetDiatM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetDiat_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oSiDiatWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetGrenM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetGrenM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetGren_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oDGrenWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetGrenM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetGrenM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetGren_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oPGrenWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetGrenM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetGrenM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetGren_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oNGrenWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetBlueM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetBlueM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_ * _oDBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetBlueM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetBlueM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_)* _uFunTmSetEpi_* _oPBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetBlueM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetBlueM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _uFunTmSetEpi_* _oNBlueWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetPhytM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetPhytM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDSetDiatM_ + _tDSetGrenM_ + _tDSetBlueM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetPhytM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetPhytM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPSetDiatM_ + _tPSetGrenM_ + _tPSetBlueM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetPhytM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetPhytM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNSetDiatM_ + _tNSetGrenM_ + _tNSetBlueM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDSetTotM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_sedimentation_in_marsh
- **Equation**:

```
_tDSetTotM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDSetIMM_ + _tDSetDetM_ + _tDSetPhytM_ _ELSE_ 0.0 _ENDIF_
```

### `_aFunTauSetOMEpi_`  [0]
- **Description**: Correction_factor_for_IM_settling_rate_(<=_1)
- **Equation**:

```
_aFunTauSetOMEpi_ = _MIN_(1.0 / _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5)), 1.0)
```

### `_aFunTauSetIMEpi_`  [0]
- **Description**: Correction_factor_for_OM_settling_rate_(<=_1)
- **Equation**:

```
_aFunTauSetIMEpi_ = _aFunTauSetOMEpi_
```

### `_uCorVSetIMEpi_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_IM
- **Equation**:

```
_uCorVSetIMEpi_ = (_aFunTauSetIMEpi_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _POW_((_fLutumRef_/_fLutum_) _POWOPERATOR_ (0.5)) * _uFunTmSetEpi_ * _cVSetIM_
```

### `_tDSetIMEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_inert_matter
- **Equation**:

```
_tDSetIMEpi_ = _uCorVSetIMEpi_ * _oDIMWEpi_
```

### `_tPSetAIMEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_P_adsorbed_onto_inert_org_matter
- **Equation**:

```
_tPSetAIMEpi_ = _oPAIMWEpi_ / _oDIMWEpi_ * _tDSetIMEpi_
```

### `_uCorVSetDetEpi_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_detritus
- **Equation**:

```
_uCorVSetDetEpi_ = (_cVSetDet_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMEpi_ * _uFunTmSetEpi_
```

### `_tDSetDetEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detritus
- **Equation**:

```
_tDSetDetEpi_ = _uCorVSetDetEpi_ * _oDDetWEpi_
```

### `_tPSetDetEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_P
- **Equation**:

```
_tPSetDetEpi_ = _uCorVSetDetEpi_ * _oPDetWEpi_
```

### `_tNSetDetEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_N
- **Equation**:

```
_tNSetDetEpi_ = _uCorVSetDetEpi_ * _oNDetWEpi_
```

### `_tSiSetDetEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_detrital_Si
- **Equation**:

```
_tSiSetDetEpi_ = _uCorVSetDetEpi_ * _oSiDetWEpi_
```

### `_aFunTauSetOMSurf_`  [0]
- **Description**: Correction_factor_for_OM_settling_rate_(<=_1)
- **Equation**:

```
_aFunTauSetOMSurf_ =_MIN_(1.0 / _POW_(_aFunDimSusp_ +_NearZero_ _POWOPERATOR_ (0.5)), 1.0)
```

### `_uFunTmSetSurf_`  [0]
- **Description**: Temperature_correction_of_sedimentation
- **Equation**:

```
_uFunTmSetSurf_ = _POW_(_cThetaSet_ _POWOPERATOR_ (_uTmSurf_-_cTmRef_))
```

## Mineralisation  (45 equations)

### `_kPMinDetW_`  [_d_^-1]
- **Description**: P_mineralisation_constant_in_water
- **Equation**:

```
_kPMinDetW_ = _kDMinDetW_
```

### `_kNMinDetW_`  [_d_^-1]
- **Description**: N_mineralisation_constant_in_water
- **Equation**:

```
_kNMinDetW_ = _kDMinDetW_
```

### `_kSiMinDetW_`  [_d_^-1]
- **Description**: Si_mineralisation_constant_in_water
- **Equation**:

```
_kSiMinDetW_ = _kDMinDetW_
```

### `_uFunTmMinWEpi_`  [0]
- **Description**: Temp_function_of_mineralization_in_water
- **Equation**:

```
_uFunTmMinWEpi_ =  _IF_ _POW_(_cThetaMinW_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaMinW_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_uFunTmMinWHyp_`  [0]
- **Description**: Temp_function_of_mineralization_in_water
- **Equation**:

```
_uFunTmMinWHyp_ = _IF_ _POW_(_cThetaMinW_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_  _POW_(_cThetaMinW_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_wDMinDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Decomposition
- **Equation**:

```
_wDMinDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kDMinDetW_ * _uFunTmMinWHyp_ * _oDDetWHyp_ _ENDIF_
```

### `_wPMinDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wPMinDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kPMinDetW_ * _uFunTmMinWHyp_ * _oPDetWHyp_ _ENDIF_
```

### `_wNMinDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wNMinDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kNMinDetW_ * _uFunTmMinWHyp_ * _oNDetWHyp_ _ENDIF_
```

### `_wSiMinDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wSiMinDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kSiMinDetW_ * _uFunTmMinWHyp_ * _oSiDetWHyp_ _ENDIF_
```

### `_aCorO2BODHyp_`  [0]
- **Description**: Correction_of_O2_demand_in_water_at_low_oxygen_conc
- **Equation**:

```
_aCorO2BODHyp_ = _oO2WHyp_ / (_hO2BOD_ + _oO2WHyp_)
```

### `_wO2MinDetWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_mineralization_of_detritus
- **Equation**:

```
_wO2MinDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _molO2molC_ * _cCPerDW_ * _aCorO2BODHyp_ * _wDMinDetWHyp_ _ENDIF_
```

### `_kPMinDetS_`  [_d_^-1]
- **Description**: P_mineralisation_constant_in_sed
- **Equation**:

```
_kPMinDetS_ = _kDMinDetS_
```

### `_kNMinDetS_`  [_d_^-1]
- **Description**: N_mineralisation_constant_in_sed
- **Equation**:

```
_kNMinDetS_ = _kDMinDetS_
```

### `_kSiMinDetS_`  [_d_^-1]
- **Description**: Si_mineralisation_constant_in_sed
- **Equation**:

```
_kSiMinDetS_ = _kDMinDetS_
```

### `_uFunTmMinS_`  [0]
- **Description**: Temp_function
- **Equation**:

```
_uFunTmMinS_ = _IF_ _POW_(_cThetaMinS_ _POWOPERATOR_ (_uTmBot_-_cTmRef_)) _LT_ _NearZero_ _THEN_ 1 _ELSE_  _POW_(_cThetaMinS_ _POWOPERATOR_ (_uTmBot_-_cTmRef_)) _ENDIF_
```

### `_tDMinDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Decomposition_of_upper_sediment
- **Equation**:

```
_tDMinDetS_ = _kDMinDetS_ * _uFunTmMinS_ * _aDDetS_
```

### `_tPMinDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_P_in_upper_sediment
- **Equation**:

```
_tPMinDetS_ = _kPMinDetS_ * _uFunTmMinS_ * _aPDetS_
```

### `_tNMinDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_N_in_upper_sediment
- **Equation**:

```
_tNMinDetS_ = _kNMinDetS_ * _uFunTmMinS_ * _aNDetS_
```

### `_tSiMinDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_Si_in_upper_sediment
- **Equation**:

```
_tSiMinDetS_ = _kSiMinDetS_ * _uFunTmMinS_ * _aSiDetS_
```

### `_wDMinDetWM_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Decomposition
- **Equation**:

```
_wDMinDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMinDetW_ * _uFunTmMinWEpi_ * _oDDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_wPMinDetWM_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wPMinDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kPMinDetW_ * _uFunTmMinWEpi_ * _oPDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_wNMinDetWM_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wNMinDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kNMinDetW_ * _uFunTmMinWEpi_ * _oNDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_wSiMinDetWM_`  [_gSi_*_m_^-3_*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wSiMinDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kSiMinDetW_ * _uFunTmMinWEpi_ * _oSiDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_aCorO2BODM_`  [0]
- **Description**: Correction_of_O2_demand_in_water_at_low_oxygen_conc
- **Equation**:

```
_aCorO2BODM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oO2WM_ /(_hO2BOD_ + _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wO2MinDetWM_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_mineralization_of_detritus
- **Equation**:

```
_wO2MinDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _molO2molC_ * _cCPerDW_ * _aCorO2BODM_ * _wDMinDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMinDetSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Decomposition_of_upper_sediment
- **Equation**:

```
_tDMinDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMinDetS_ * _uFunTmMinS_ * _aDDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPMinDetSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_P_in_upper_sediment
- **Equation**:

```
_tPMinDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kPMinDetS_ * _uFunTmMinS_ * _aPDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMinDetSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_N_in_upper_sediment
- **Equation**:

```
_tNMinDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kNMinDetS_ * _uFunTmMinS_ * _aNDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiMinDetSM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_Si_in_upper_sediment
- **Equation**:

```
_tSiMinDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kSiMinDetS_ * _uFunTmMinS_ * _aSiDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMinOxyDetSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Aerobic_mineralisation
- **Equation**:

```
_tDMinOxyDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _afOxySedM_ *(1.0 - _fRefrDetS_) * _tDMinDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2MinDetSM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Sediment_oxygen_demand
- **Equation**:

```
_tO2MinDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _molO2molC_ * _cCPerDW_ * _tDMinOxyDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMinHumSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Decomposition_of_upper_sediment_humus
- **Equation**:

```
_tDMinHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMinHum_ * _uFunTmMinS_ * _afOxySedM_ * _aDHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPMinHumSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_P_in_upper_sediment_humus
- **Equation**:

```
_tPMinHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMinHum_ * _uFunTmMinS_ * _afOxySedM_ * _aPHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMinHumSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_N_in_upper_sediment_humus
- **Equation**:

```
_tNMinHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMinHum_ * _uFunTmMinS_ * _afOxySedM_ * _aNHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_wDMinDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Decomposition
- **Equation**:

```
_wDMinDetWEpi_ = _kDMinDetW_ * _uFunTmMinWEpi_ * _oDDetWEpi_
```

### `_wPMinDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wPMinDetWEpi_ = _kPMinDetW_ * _uFunTmMinWEpi_ * _oPDetWEpi_
```

### `_wNMinDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wNMinDetWEpi_ = _kNMinDetW_ * _uFunTmMinWEpi_ * _oNDetWEpi_
```

### `_wSiMinDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Mineralization
- **Equation**:

```
_wSiMinDetWEpi_ = _kSiMinDetW_ * _uFunTmMinWEpi_ * _oSiDetWEpi_
```

### `_aCorO2BODEpi_`  [0]
- **Description**: Correction_of_O2_demand_in_water_at_low_oxygen_conc
- **Equation**:

```
_aCorO2BODEpi_ = _oO2WEpi_ / (_hO2BOD_ + _oO2WEpi_)
```

### `_wO2MinDetWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_mineralization_of_detritus
- **Equation**:

```
_wO2MinDetWEpi_ = _molO2molC_ * _cCPerDW_ * _aCorO2BODEpi_ * _wDMinDetWEpi_
```

### `_tDMinOxyDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Aerobic_mineralisation
- **Equation**:

```
_tDMinOxyDetS_ = _afOxySed_ * (1.0 - _fRefrDetS_) * _tDMinDetS_
```

### `_tO2MinDetS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Sediment_oxygen_demand
- **Equation**:

```
_tO2MinDetS_ = _molO2molC_ * _cCPerDW_ * _tDMinOxyDetS_
```

### `_tDMinHumS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Decomposition_of_upper_sediment_humus
- **Equation**:

```
_tDMinHumS_ = _kDMinHum_ * _uFunTmMinS_ * _afOxySed_ * _aDHumS_
```

### `_tPMinHumS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_P_in_upper_sediment_humus
- **Equation**:

```
_tPMinHumS_ = _kDMinHum_ * _uFunTmMinS_ * _afOxySed_ * _aPHumS_
```

### `_tNMinHumS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mineralization_of_N_in_upper_sediment_humus
- **Equation**:

```
_tNMinHumS_ = _kDMinHum_ * _uFunTmMinS_ * _afOxySed_ * _aNHumS_
```

## Denitirification  (10 equations)

### `_wDDenitWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mineralisation_flux_by_denitrification
- **Equation**:

```
_wDDenitWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _oNO3WHyp_*_oNO3WHyp_ / (_hNO3Denit_*_hNO3Denit_ + _oNO3WHyp_*_oNO3WHyp_) * (1.0 - _aCorO2BODHyp_) * _wDMinDetWHyp_ _ENDIF_
```

### `_wNDenitWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Denitrification_flux
- **Equation**:

```
_wNDenitWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _NO3PerC_ * _molNmolC_ * _cCPerDW_ * _wDDenitWHyp_ _ENDIF_
```

### `_wDDenitWM_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mineralisation_flux_by_denitrification
- **Equation**:

```
_wDDenitWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNO3WM_*_oNO3WM_ /(_hNO3Denit_*_hNO3Denit_ + _oNO3WM_*_oNO3WM_) *(1.0 - _aCorO2BODM_) * _wDMinDetWM_ _ELSE_ 0.0 _ENDIF_
```

### `_wNDenitWM_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Denitrification_flux
- **Equation**:

```
_wNDenitWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _NO3PerC_ * _molNmolC_ * _cCPerDW_ * _wDDenitWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDDenitSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mineralisation_flux_by_denitrification
- **Equation**:

```
_tDDenitSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oNO3SM_*_oNO3SM_ /(_hNO3Denit_*_hNO3Denit_ + _oNO3SM_*_oNO3SM_) *(1.0 - _afOxySedM_) *(1.0 - _fRefrDetS_) * _tDMinDetSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDenitSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Denitrification_flux
- **Equation**:

```
_tNDenitSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _NO3PerC_ * _molNmolC_ * _cCPerDW_ * _tDDenitSM_ _ELSE_ 0.0 _ENDIF_
```

### `_wDDenitWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mineralisation_flux_by_denitrification
- **Equation**:

```
_wDDenitWEpi_ = _oNO3WEpi_*_oNO3WEpi_ / (_hNO3Denit_*_hNO3Denit_ + _oNO3WEpi_*_oNO3WEpi_) * (1.0 - _aCorO2BODEpi_) * _wDMinDetWEpi_
```

### `_wNDenitWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Denitrification_flux
- **Equation**:

```
_wNDenitWEpi_ = _NO3PerC_ * _molNmolC_ * _cCPerDW_ * _wDDenitWEpi_
```

### `_tDDenitS_`  [_gDW_*_m_^-1*_d_^-1]
- **Description**: Mineralisation_flux_by_denitrification
- **Equation**:

```
_tDDenitS_ = _oNO3S_*_oNO3S_ / (_hNO3Denit_*_hNO3Denit_ + _oNO3S_*_oNO3S_) * (1.0 - _afOxySed_) * (1.0 - _fRefrDetS_) * _tDMinDetS_
```

### `_tNDenitS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Denitrification_flux
- **Equation**:

```
_tNDenitS_ = _NO3PerC_ * _molNmolC_ * _cCPerDW_ * _tDDenitS_
```

## Nitrification  (16 equations)

### `_uFunTmNitrHyp_`  [0]
- **Description**: Temperature_dependence_for_nitrification
- **Equation**:

```
_uFunTmNitrHyp_ = _IF_   _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmHyp_-_cTmRef_)) _ENDIF_
```

### `_uFunTmNitrEpi_`  [0]
- **Description**: Temperature_dependence_for_nitrification
- **Equation**:

```
_uFunTmNitrEpi_ =  _IF_ _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_uFunTmNitrS_`  [0]
- **Description**: Temperature_dependence_for_nitrification
- **Equation**:

```
_uFunTmNitrS_ = _IF_ _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_))  _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaNitr_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_aCorO2NitrWHyp_`  [0]
- **Description**: Oxygen_consumption_during_nitrification
- **Equation**:

```
_aCorO2NitrWHyp_ = _oO2WHyp_*_oO2WHyp_ / (_hO2Nitr_*_hO2Nitr_ + _oO2WHyp_*_oO2WHyp_)
```

### `_wNNitrWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrification_flux
- **Equation**:

```
_wNNitrWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kNitrW_ * _uFunTmNitrHyp_ * _aCorO2NitrWHyp_ * _oNH4WHyp_ _ENDIF_
```

### `_wO2NitrWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_nitrification
- **Equation**:

```
_wO2NitrWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _O2PerNH4_ * _molO2molN_ * _wNNitrWHyp_ _ENDIF_
```

### `_aCorO2NitrWM_`  [0]
- **Description**: Oxygen_use_for_nitrification_in_marsh_water
- **Equation**:

```
_aCorO2NitrWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _oO2WM_ * _oO2WM_ /(_hO2Nitr_ * _hO2Nitr_ + _oO2WM_ * _oO2WM_) _ELSE_ 0.0 _ENDIF_
```

### `_wNNitrWM_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrification_flux
- **Equation**:

```
_wNNitrWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kNitrW_ * _uFunTmNitrEpi_ * _aCorO2NitrWM_ * _oNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_wO2NitrWM_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_nitrification
- **Equation**:

```
_wO2NitrWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _O2PerNH4_ * _molO2molN_ * _wNNitrWM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNNitrSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Nitrification_flux
- **Equation**:

```
_tNNitrSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _afOxySedM_ * _kNitrS_ * _uFunTmNitrEpi_ * _aNH4SM_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2NitrSM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_flux_due_to_nitrification
- **Equation**:

```
_tO2NitrSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _O2PerNH4_ * _molO2molN_ * _tNNitrSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aCorO2NitrWEpi_`  [0]
- **Description**: Oxygen_consumption_during_nitrification
- **Equation**:

```
_aCorO2NitrWEpi_ = _oO2WEpi_*_oO2WEpi_ / (_hO2Nitr_*_hO2Nitr_ + _oO2WEpi_*_oO2WEpi_)
```

### `_wNNitrWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrification_flux
- **Equation**:

```
_wNNitrWEpi_ = _kNitrW_ * _uFunTmNitrEpi_ * _aCorO2NitrWEpi_ * _oNH4WEpi_
```

### `_wO2NitrWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_due_to_nitrification
- **Equation**:

```
_wO2NitrWEpi_ = _O2PerNH4_ * _molO2molN_ * _wNNitrWEpi_
```

### `_tNNitrS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Nitrification_flux
- **Equation**:

```
_tNNitrS_ = _afOxySed_ * _kNitrS_ * _uFunTmNitrS_ * _aNH4S_
```

### `_tO2NitrS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_flux_due_to_nitrification
- **Equation**:

```
_tO2NitrS_ = _O2PerNH4_ * _molO2molN_ * _tNNitrS_
```

## Oxygen_depth  (9 equations)

### `_uFunTmDif_`  [0]
- **Description**: Temperature_function_of_diffusion
- **Equation**:

```
_uFunTmDif_ = _IF_ _POW_(_cThetaDif_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _LT_ _NearZero_ _THEN_ 1 _ELSE_ _POW_(_cThetaDif_ _POWOPERATOR_ (_uTmEpi_-_cTmRef_)) _ENDIF_
```

### `_akO2DifCor_`  [_m_^2*_d_^-1]
- **Description**: Corrected_O2_diffusion_coefficient
- **Equation**:

```
_akO2DifCor_ = _kO2Dif_ * _uFunTmDif_ * _cTurbDifO2_ * _bPorCorS_
```

### `_tSOD_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Sediment_oxygen_demand
- **Equation**:

```
_tSOD_ = (_molO2molC_ * _cCPerDW_ * (1.0 - _fRefrDetS_) * _tDMinDetS_ + _O2PerNH4_ * _molO2molN_ * _kNitrS_ * _uFunTmNitrS_ * _aNH4S_) / _cDepthS_
```

### `_akO2DifCorM_`  [_m_^2*_d_^-1]
- **Description**: Corrected_O2_diffusion_coefficient
- **Equation**:

```
_akO2DifCorM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kO2Dif_ * _uFunTmDif_ * _cTurbDifO2_ * _bPorCorSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tSODM_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Sediment_oxygen_demand
- **Equation**:

```
_tSODM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_(_molO2molC_ * _cCPerDW_ *(1.0 - _fRefrDetS_) * _tDMinDetSM_ + _O2PerNH4_ * _molO2molN_ * _kNitrS_ * _uFunTmNitrEpi_ * _aNH4SM_) / _cDepthSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aDepthOxySedM_`  [_m_]
- **Description**: Oxygen_penetration_depth
- **Equation**:

```
_aDepthOxySedM_ = _IF_ (_InclMarsh_ _EQ_ _FALSE_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ _POW_((2.0 * _oO2WM_ * _akO2DifCorM_ / _tSODM_) _POWOPERATOR_ (0.5)) _LE_ _NearZero_ _THEN_ 1 _ELSE_ _POW_((2.0 * _oO2WM_ * _akO2DifCorM_ / _tSODM_) _POWOPERATOR_ (0.5)) _ENDIF_
```

### `_afOxySedM_`  [0]
- **Description**: Fraction_aerobic_sediment
- **Equation**:

```
_afOxySedM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDepthOxySedM_ / _cDepthSM_ _ELSE_ 0.0 _ENDIF_
```

### `_aDepthOxySed_`  [_m_]
- **Description**: Oxygen_penetration_depth
- **Equation**:

```
_aDepthOxySed_ = _IF_(_aInclStrat_ _EQ_ _TRUE_ _AND_ (2.0 * _oO2WHyp_ * _akO2DifCor_ / _tSOD_) _GT_ _NearZero_ ) _THEN_ _POW_((2.0 * _oO2WHyp_ * _akO2DifCor_ / _tSOD_) _POWOPERATOR_ (0.5)) _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ (2.0 * _oO2WHyp_ * _akO2DifCor_ / _tSOD_) _LE_ _NearZero_ ) _THEN_ _POW_ ( _NearZero_ _POWOPERATOR_ (0.5)) _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ ( 2.0 * _oO2WEpi_ * _akO2DifCor_ / _tSOD_ ) _LE_ _NearZero_ ) _THEN_ _POW_ ( _NearZero_ _POWOPERATOR_ (0.5)) _ELSE_ _POW_ ( ( 2.0 * _oO2WEpi_ * _akO2DifCor_ / _tSOD_ ) _POWOPERATOR_ (0.5)) _ENDIF_
```

### `_afOxySed_`  [0]
- **Description**: Fraction_aerobic_sediment
- **Equation**:

```
_afOxySed_ = _aDepthOxySed_ / _cDepthS_
```

## Diffusion  (20 equations)

### `_aDepthDif_`  [_m_]
- **Description**: Average_diffusion_distance
- **Equation**:

```
_aDepthDif_ = _fDepthDifS_ * _cDepthS_
```

### `_tPDifPO4Hyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_P_from_sediment_to_water
- **Equation**:

```
_tPDifPO4Hyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _kPDifPO4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oPO4S_ - _oPO4WHyp_ ) / _aDepthDif_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDifNO3Hyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NO3_from_sediment_to_water
- **Equation**:

```
_tNDifNO3Hyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _kNDifNO3_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oNO3S_ - _oNO3WHyp_ ) / _aDepthDif_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDifNH4Hyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NH4_from_sediment_to_water
- **Equation**:

```
_tNDifNH4Hyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _kNDifNH4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oNH4S_ - _oNH4WHyp_ ) / _aDepthDif_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2DifHyp_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_diffusion_(water_->_sediment)
- **Equation**:

```
_tO2DifHyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _kO2Dif_ / _aDepthDif_ * _uFunTmDif_ * _cTurbDifO2_ * _bPorCorS_ * _oO2WHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPDifGroundPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_P_from_pore_water_to_groundwater
- **Equation**:

```
_tPDifGroundPO4_ = 0.0
```

### `_tNDifGroundNO3_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_NO3_from_pore_water_to_groundwater
- **Equation**:

```
_tNDifGroundNO3_ = 0.0
```

### `_tNDifGroundNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_NH4_from_pore_water_to_groundwater
- **Equation**:

```
_tNDifGroundNH4_ = 0.0
```

### `_aDepthDifM_`  [_m_]
- **Description**: Average_diffusion_distance
- **Equation**:

```
_aDepthDifM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fDepthDifS_ * _cDepthSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPDifPO4M_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_P_from_sediment_to_water
- **Equation**:

```
_tPDifPO4M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kPDifPO4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorSM_ * (_oPO4SM_ - _oPO4WM_) / _aDepthDifM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDifNO3M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NO3_from_sediment_to_water
- **Equation**:

```
_tNDifNO3M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kNDifNO3_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorSM_ * (_oNO3SM_ - _oNO3WM_) / _aDepthDifM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDifNH4M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NH4_from_sediment_to_water
- **Equation**:

```
_tNDifNH4M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kNDifNH4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorSM_ * (_oNH4SM_ - _oNH4WM_) / _aDepthDifM_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2DifM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_diffusion(water_->_sediment)
- **Equation**:

```
_tO2DifM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kO2Dif_ / _aDepthDifM_ * _uFunTmDif_ * _cTurbDifO2_ * _bPorCorSM_ * _oO2WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPDifGroundPO4M_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_P_from_pore_water_to_groundwater
- **Equation**:

```
_tPDifGroundPO4M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tNDifGroundNO3M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NO3_from_pore_water_to_groundwater
- **Equation**:

```
_tNDifGroundNO3M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tNDifGroundNH4M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NH4_from_pore_water_to_groundwater
- **Equation**:

```
_tNDifGroundNH4M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tPDifPO4Epi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_dissolved_P_from_sediment_to_water
- **Equation**:

```
_tPDifPO4Epi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSE_ _kPDifPO4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oPO4S_ - _oPO4WEpi_ ) / _aDepthDif_ _ENDIF_
```

### `_tNDifNO3Epi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NO3_from_sediment_to_water
- **Equation**:

```
_tNDifNO3Epi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSE_ _kNDifNO3_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oNO3S_ - _oNO3WEpi_ ) / _aDepthDif_ _ENDIF_
```

### `_tNDifNH4Epi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diffusion_flux_of_NH4_from_sediment_to_water
- **Equation**:

```
_tNDifNH4Epi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSE_ _kNDifNH4_ * _uFunTmDif_ * _cTurbDifNut_ * _bPorCorS_ * (_oNH4S_ - _oNH4WEpi_ ) / _aDepthDif_ _ENDIF_
```

### `_tO2DifEpi_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_diffusion_(water_->_sediment)
- **Equation**:

```
_tO2DifEpi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSE_ _kO2Dif_ / _aDepthDif_ * _uFunTmDif_ * _cTurbDifO2_ * _bPorCorS_ * _oO2WEpi_ _ENDIF_
```

## P_sorption  (25 equations)

### `_aPAdsMaxWHyp_`  [_gP_*_gDW_^-1]
- **Description**: Max_P_adsorption_per_g_inorg_matter_in_water
- **Equation**:

```
_aPAdsMaxWHyp_ = _cRelPAdsD_ + _aCorO2BODHyp_ * _cRelPAdsFe_ * _fFeDIM_ + _cRelPAdsAl_ * _fAlDIM_
```

### `_aKPAdsWHyp_`  [_m_^3*_gP_^-1]
- **Description**: P_adsorption_affinity_corrected_for_redox_conditions
- **Equation**:

```
_aKPAdsWHyp_ = (1.0 - _fRedMax_ * (1.0-_aCorO2BODHyp_)) * _cKPAdsOx_
```

### `_aPIsoAdsWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P_adsorption_isotherm_onto_inorg_matter_in_sediment
- **Equation**:

```
_aPIsoAdsWHyp_ = _aPAdsMaxWHyp_ * _aKPAdsWHyp_ * _oPO4WHyp_ / (1.0 + _aKPAdsWHyp_ * _oPO4WHyp_)
```

### `_aPEqIMWHyp_`  [_gP_*_m_^-3]
- **Description**: Equilibrium_conc
- **Equation**:

```
_aPEqIMWHyp_ = _aPIsoAdsWHyp_ * _oDIMWHyp_
```

### `_wPSorpIMWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Sorption_flux_in_water
- **Equation**:

```
_wPSorpIMWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kPSorp_ * (_aPEqIMWHyp_ - _oPAIMWHyp_) _ENDIF_
```

### `_aPAdsMaxWM_`  [_gP_*_gDW_^-1]
- **Description**: Max_P_adsorption_per_g_inorg_matter_in_water_marsh
- **Equation**:

```
_aPAdsMaxWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cRelPAdsD_ + _aCorO2BODM_ * _cRelPAdsFe_ * _fFeDIM_ + _cRelPAdsAl_ * _fAlDIM_ _ELSE_ 0.0 _ENDIF_
```

### `_aKPAdsWM_`  [_m_^3*_gP_^-1]
- **Description**: P_adsorption_affinity_corrected_for_redox_conditions
- **Equation**:

```
_aKPAdsWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_(1.0 - _fRedMax_ *(1.0-_aCorO2BODM_)) * _cKPAdsOx_ _ELSE_ 0.0 _ENDIF_
```

### `_aPIsoAdsWM_`  [_gP_*_gDW_^-1]
- **Description**: P_adsorption_isotherm_onto_inorg_matter_in_sediment
- **Equation**:

```
_aPIsoAdsWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPAdsMaxWM_ * _aKPAdsWM_ * _oPO4WM_ /(1.0 + _aKPAdsWM_ * _oPO4WM_) _ELSE_ 0.0 _ENDIF_
```

### `_aPEqIMWM_`  [_gP_*_m_^-3]
- **Description**: Equilibrium_conc
- **Equation**:

```
_aPEqIMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPIsoAdsWM_ * _oDIMWM_ _ELSE_ 0.0 _ENDIF_
```

### `_wPSorpIMWM_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Sorption_flux_in_water
- **Equation**:

```
_wPSorpIMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kPSorp_ *(_aPEqIMWM_ - _oPAIMWM_) _ELSE_ 0.0 _ENDIF_
```

### `_aPAdsMaxSM_`  [_gP_*_gDW_^-1]
- **Description**: Max_P_adsorption_per_g_inorg_matter_in_sediment_marsh
- **Equation**:

```
_aPAdsMaxSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _cRelPAdsD_ + _afOxySedM_ * _cRelPAdsFe_ * _fFeDIM_ + _cRelPAdsAl_ * _fAlDIM_ _ELSE_ 0.0 _ENDIF_
```

### `_aKPAdsSM_`  [_m_^3*_gP_^-1]
- **Description**: P_adsorption_affinity_corrected_for_redox_conditions
- **Equation**:

```
_aKPAdsSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_(1.0 - _fRedMax_ *(1.0-_afOxySedM_)) * _cKPAdsOx_ _ELSE_ 0.0 _ENDIF_
```

### `_aPIsoAdsSM_`  [_gP_*_gDW_^-1]
- **Description**: P_adsorption_isotherm_onto_inorg_matter_in_sediment
- **Equation**:

```
_aPIsoAdsSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPAdsMaxSM_ * _aKPAdsSM_ * _oPO4SM_ /(1.0 + _aKPAdsSM_ * _oPO4SM_) _ELSE_ 0.0 _ENDIF_
```

### `_aPEqIMSM_`  [_gP_*_m_^-2]
- **Description**: Equilibrium_amount
- **Equation**:

```
_aPEqIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPIsoAdsSM_ * _aDIMSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSorpIMSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sorption
- **Equation**:

```
_tPSorpIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kPSorp_ *(_aPEqIMSM_ - _aPAIMSM_) _ELSE_ 0.0 _ENDIF_
```

### `_aPAdsMaxWEpi_`  [_gP_*_gDW_^-1]
- **Description**: Max_P_adsorption_per_g_inorg_matter_in_water
- **Equation**:

```
_aPAdsMaxWEpi_ = _cRelPAdsD_ + _aCorO2BODEpi_ * _cRelPAdsFe_ * _fFeDIM_ + _cRelPAdsAl_ * _fAlDIM_
```

### `_aKPAdsWEpi_`  [_m_^3*_gP_^-1]
- **Description**: P_adsorption_affinity_corrected_for_redox_conditions
- **Equation**:

```
_aKPAdsWEpi_ = (1.0 - _fRedMax_ * (1.0-_aCorO2BODEpi_)) * _cKPAdsOx_
```

### `_aPIsoAdsWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P_adsorption_isotherm_onto_inorg_matter_in_sediment
- **Equation**:

```
_aPIsoAdsWEpi_ = _aPAdsMaxWEpi_ * _aKPAdsWEpi_ * _oPO4WEpi_ / (1.0 + _aKPAdsWEpi_ * _oPO4WEpi_)
```

### `_aPEqIMWEpi_`  [_gP_*_m_^-3]
- **Description**: Equilibrium_conc
- **Equation**:

```
_aPEqIMWEpi_ = _aPIsoAdsWEpi_ * _oDIMWEpi_
```

### `_wPSorpIMWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Sorption_flux_in_water
- **Equation**:

```
_wPSorpIMWEpi_ = _kPSorp_ * (_aPEqIMWEpi_ - _oPAIMWEpi_)
```

### `_aPAdsMaxS_`  [_gP_*_gDW_^-1]
- **Description**: Max_P_adsorption_per_g_inorg_matter_in_sediment
- **Equation**:

```
_aPAdsMaxS_ = _cRelPAdsD_ + _afOxySed_ * _cRelPAdsFe_ * _fFeDIM_ + _cRelPAdsAl_ * _fAlDIM_
```

### `_aKPAdsS_`  [_m_^3*_gP_^-1]
- **Description**: P_adsorption_affinity_corrected_for_redox_conditions
- **Equation**:

```
_aKPAdsS_ = (1.0 - _fRedMax_ * (1.0-_afOxySed_)) * _cKPAdsOx_
```

### `_aPIsoAdsS_`  [_gP_*_gDW_^-1]
- **Description**: P_adsorption_isotherm_onto_inorg_matter_in_sediment
- **Equation**:

```
_aPIsoAdsS_ = _aPAdsMaxS_ * _aKPAdsS_ * _oPO4S_ / (1.0 + _aKPAdsS_ * _oPO4S_)
```

### `_aPEqIMS_`  [_gP_*_m_^-2]
- **Description**: Equilibrium_amount
- **Equation**:

```
_aPEqIMS_ = _aPIsoAdsS_ * _aDIMS_
```

### `_tPSorpIMS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sorption
- **Equation**:

```
_tPSorpIMS_ = _kPSorp_ * (_aPEqIMS_ - _aPAIMS_)
```

## Total_abiotic/microbial_fluxes  (40 equations)

### `_tPChemPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Chemical_loss_of_dissolved_P_from_pore_water
- **Equation**:

```
_tPChemPO4_ = _MAX_( 0.0, _kPChemPO4_ * (_oPO4S_ - _coPO4Max_) )
```

### `_tSiAbioTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_flux_for_mass_balance_check
- **Equation**:

```
_tSiAbioTotT_ = - _fRefrDetS_ * _tSiMinDetS_ - _tInfSiO2WHyp_ - _tInfSiO2WEpi_ + _tSeepSiO2WHyp_ + _tSeepSiO2WEpi_
```

### `_wO2AbioWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_O2_flux_in_water
- **Equation**:

```
_wO2AbioWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _tO2BubHyp_ / _uDepthWHyp_ - _wO2MinDetWHyp_ - _wO2NitrWHyp_ - (_tO2MinDetS_ + _tO2NitrS_) / _uDepthWHyp_ - (_tInfO2WHyp_ / _uDepthWHyp_) + (_tSeepO2WHyp_ / _uDepthWHyp_) _ENDIF_
```

### `_wPAbioDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_P_detritus_flux_in_water
- **Equation**:

```
_wPAbioDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ - _wPMinDetWHyp_ - (_tPSetDetHyp_ - _tPSetDetEpi_ - _tPResusDet_) / _uDepthWHyp_ _ENDIF_
```

### `_wPAbioPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_dissolved_P_flux_in_water
- **Equation**:

```
_wPAbioPO4WHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wPMinDetWHyp_ - _wPSorpIMWHyp_ - (_tPInfPO4WHyp_ / _uDepthWHyp_) + ((_tPSeepPO4WHyp_ + _tPDifPO4Hyp_ + _tPResusPO4_) / _uDepthWHyp_) _ENDIF_
```

### `_wPAbioAIMWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_P_absorbed_onto_inorganic_matter_flux_in_water
- **Equation**:

```
_wPAbioAIMWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (- _tPSetAIMHyp_ +_tPSetAIMEpi_ + _tPResusAIM_) / _uDepthWHyp_ + _wPSorpIMWHyp_ _ENDIF_
```

### `_tPAbioTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_P_flux_for_mass_balance_check
- **Equation**:

```
_tPAbioTotT_ = _uPErosOM_ - _tPChemPO4_ - _tPInfPO4S_ + _tPSeepPO4S_ - _tPDifGroundPO4_
```

### `_wNAbioNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NH4_flux_in_water
- **Equation**:

```
_wNAbioNH4WHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNMinDetWHyp_ - _wNNitrWHyp_ - (_tNInfNH4WHyp_ / _uDepthWHyp_) + ((_tNSeepNH4WHyp_ + _tNDifNH4Hyp_ + _tNResusNH4_) / _uDepthWHyp_) _ENDIF_
```

### `_wNAbioNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NO3_flux_in_water
- **Equation**:

```
_wNAbioNO3WHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNNitrWHyp_ - _wNDenitWHyp_ + ((_tNDifNO3Hyp_ + _tNResusNO3_ - _tNInfNO3WHyp_ + _tNSeepNO3WHyp_) / _uDepthWHyp_) _ENDIF_
```

### `_wNAbioDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_detritus_flux_in_water
- **Equation**:

```
_wNAbioDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ - _wNMinDetWHyp_ - (_tNSetDetHyp_ -_tNSetDetEpi_ - _tNResusDet_ ) / _uDepthWHyp_ _ENDIF_
```

### `_wSiAbioSiO2WHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_sio2_flux_in_water
- **Equation**:

```
_wSiAbioSiO2WHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wSiMinDetWHyp_ + (1.0 - _fRefrDetS_) * _tSiMinDetS_ / _uDepthWHyp_ - _tInfSiO2WHyp_ / _uDepthWHyp_ + _tSeepSiO2WHyp_ / _uDepthWHyp_ _ENDIF_
```

### `_wSiAbioDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_detritus_flux_in_water
- **Equation**:

```
_wSiAbioDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ - _wSiMinDetWHyp_ - (_tSiSetDetHyp_ -_tSiSetDetEpi_ - _tSiResusDet_) / _uDepthWHyp_ _ENDIF_
```

### `_wDAbioDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_detritus_flux_in_water
- **Equation**:

```
_wDAbioDetWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (- _tDSetDetHyp_ + _tDSetDetEpi_ + _tDResusDet_ ) / _uDepthWHyp_ - _wDMinDetWHyp_ _ENDIF_
```

### `_wDAbioIMWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_inorganic_matter_flux_in_water
- **Equation**:

```
_wDAbioIMWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (_uDErosIMW_ * _fHypErosIM_ - _tDSetIMHyp_+ _tDSetIMEpi_ + _tDResusIM_) / _uDepthWHyp_ _ENDIF_
```

### `_wDAbioIMWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_inorganic_matter_flux_in_water
- **Equation**:

```
_wDAbioIMWEpi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_uDErosIMW_ * (1- _fHypErosIM_) - _tDSetIMEpi_ ) / _uDepthWEpi_ _ELSE_ (_uDErosIMW_ * (1- _fHypErosIM_) - _tDSetIMEpi_ + _tDResusIM_) / _uDepthWEpi_ _ENDIF_
```

### `_wDAbioDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_detritus_flux_in_water
- **Equation**:

```
_wDAbioDetWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (- _tDSetDetEpi_ ) / _uDepthWEpi_ - _wDMinDetWEpi_ _ELSE_ (- _tDSetDetEpi_ + _tDResusDet_ ) / _uDepthWEpi_ - _wDMinDetWEpi_ _ENDIF_
```

### `_tDAbioIMS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_inorganic_matter_flux_in_sediment
- **Equation**:

```
_tDAbioIMS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _uDErosIMS_ + _tDSetIMHyp_ - _tDResusIM_ _ELSE_ _uDErosIMS_ + _tDSetIMEpi_ - _tDResusIM_ _ENDIF_
```

### `_tDAbioDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_detritus_flux_in_sediment
- **Equation**:

```
_tDAbioDetS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tDSetDetHyp_ - _tDResusDet_ - _tDMinDetS_ _ELSE_ _tDSetDetEpi_ - _tDResusDet_ - _tDMinDetS_ _ENDIF_
```

### `_tDAbioHumS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_humus_flux_in_sediment
- **Equation**:

```
_tDAbioHumS_ = _uDErosOM_ + _fRefrDetS_ * _tDMinDetS_ - _tDMinHumS_
```

### `_tDAbioTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_DW_flux_for_mass_balance_check
- **Equation**:

```
_tDAbioTotT_ = _cDErosTot_ - _wDMinDetWEpi_ * _uDepthWEpi_ - _wDMinDetWHyp_ * _uDepthWHyp_ - (1.0 - _fRefrDetS_) * _tDMinDetS_ - _tDMinHumS_
```

### `_wO2AbioWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_O2_flux_in_water
- **Equation**:

```
_wO2AbioWEpi_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _tO2AerEpi_ / _uDepthWEpi_ - _wO2MinDetWEpi_ - _wO2NitrWEpi_ - (_tO2MinDetS_ + _tO2NitrS_) / _uDepthWEpi_ - _tInfO2WEpi_/_uDepthWEpi_ + _tSeepO2WEpi_/_uDepthWEpi_ _ELSE_ _tO2AerEpi_ / _uDepthWEpi_ - _wO2MinDetWEpi_ - _wO2NitrWEpi_ _ENDIF_
```

### `_wO2AbioM_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_O2_flux_in_water
- **Equation**:

```
_wO2AbioM_ = _tO2AerM_ / _uDepthWM_ - _wO2MinDetWM_ - _wO2NitrWM_ - (_tO2MinDetSM_ + _tO2NitrSM_) / _uDepthWM_  - _tInfO2WM_ /_uDepthWM_  + _tSeepO2WM_ /_uDepthWM_
```

### `_wPAbioDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_P_detritus_flux_in_water
- **Equation**:

```
_wPAbioDetWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _wPMinDetWEpi_ - (_tPSetDetEpi_ ) / _uDepthWEpi_ _ELSE_ - _wPMinDetWEpi_ - (_tPSetDetEpi_ - _tPResusDet_) / _uDepthWEpi_ _ENDIF_
```

### `_wPAbioPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_dissolved_P_flux_in_water
- **Equation**:

```
_wPAbioPO4WEpi_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wPMinDetWEpi_ - _wPSorpIMWEpi_ + (_tPDifPO4Epi_ / _uDepthWEpi_) _ELSE_ _wPMinDetWEpi_ - _wPSorpIMWEpi_ + ((_tPSeepPO4WEpi_ - _tPInfPO4WEpi_ + _tPDifPO4Epi_ + _tPResusPO4_) / _uDepthWEpi_) _ENDIF_
```

### `_wPAbioAIMWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_P_absorbed_onto_inorganic_matter_flux_in_water
- **Equation**:

```
_wPAbioAIMWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (- _tPSetAIMEpi_ ) / _uDepthWEpi_ + _wPSorpIMWEpi_ _ELSE_ (- _tPSetAIMEpi_ + _tPResusAIM_ ) / _uDepthWEpi_ + _wPSorpIMWEpi_ _ENDIF_
```

### `_tPAbioDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_P_detritus_flux_in_sediment
- **Equation**:

```
_tPAbioDetS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _tPMinDetS_ + _tPSetDetHyp_ - _tPResusDet_ _ELSE_ - _tPMinDetS_ + _tPSetDetEpi_ - _tPResusDet_ _ENDIF_
```

### `_tPAbioHumS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_P_humus_flux_in_sediment
- **Equation**:

```
_tPAbioHumS_ = _uPErosOM_ + _fRefrDetS_ * _tPMinDetS_ - _tPMinHumS_
```

### `_tPAbioPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_dissolved_P_flux_in_sediment
- **Equation**:

```
_tPAbioPO4S_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tPInfPO4WHyp_ - _tPSeepPO4WHyp_ - _tPInfPO4S_ + _tPSeepPO4S_ + (1.0-_fRefrDetS_) * _tPMinDetS_ + _tPMinHumS_ - _tPSorpIMS_ - _tPResusPO4_ - _tPDifPO4Hyp_ - _tPDifGroundPO4_ - _tPChemPO4_ _ELSE_ _tPInfPO4WEpi_ - _tPSeepPO4WEpi_ - _tPInfPO4S_ + _tPSeepPO4S_ + (1.0-_fRefrDetS_) * _tPMinDetS_ + _tPMinHumS_ - _tPSorpIMS_ - _tPResusPO4_ - _tPDifPO4Epi_ - _tPDifGroundPO4_ - _tPChemPO4_ _ENDIF_
```

### `_tPAbioAIMS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_P_absorbed_onto_inorganic_matter_flux_in_sediment
- **Equation**:

```
_tPAbioAIMS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tPSetAIMHyp_ - _tPResusAIM_ + _tPSorpIMS_ _ELSE_ _tPSetAIMEpi_ - _tPResusAIM_ + _tPSorpIMS_ _ENDIF_
```

### `_wNAbioNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NH4_flux_in_water
- **Equation**:

```
_wNAbioNH4WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wNMinDetWEpi_ - _wNNitrWEpi_ + (_tNDifNH4Epi_ / _uDepthWEpi_) _ELSE_ _wNMinDetWEpi_ - _wNNitrWEpi_ + ((_tNSeepNH4WEpi_ - _tNInfNH4WEpi_ + _tNDifNH4Epi_ + _tNResusNH4_) / _uDepthWEpi_) _ENDIF_
```

### `_wNAbioNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NO3_flux_in_water
- **Equation**:

```
_wNAbioNO3WEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wNNitrWEpi_ - _wNDenitWEpi_ + (_tNDifNO3Epi_ / _uDepthWEpi_) _ELSE_ _wNNitrWEpi_ - _wNDenitWEpi_ + ((_tNDifNO3Epi_ + _tNResusNO3_ - _tNInfNO3WEpi_ + _tNSeepNO3WEpi_) / _uDepthWEpi_) _ENDIF_
```

### `_wNAbioDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_N_detritus_flux_in_water
- **Equation**:

```
_wNAbioDetWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _wNMinDetWEpi_ - (_tNSetDetEpi_) / _uDepthWEpi_ _ELSE_ - _wNMinDetWEpi_ - (_tNSetDetEpi_ - _tNResusDet_ ) / _uDepthWEpi_ _ENDIF_
```

### `_tNAbioNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NH4_flux_in_sediment
- **Equation**:

```
_tNAbioNH4S_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tNInfNH4WHyp_ - _tNSeepNH4WHyp_ - _tNInfNH4S_ + _tNSeepNH4S_ + (1.0-_fRefrDetS_) * _tNMinDetS_ + _tNMinHumS_ - _tNResusNH4_ - _tNDifNH4Hyp_ - _tNDifGroundNH4_ - _tNNitrS_ _ELSE_ _tNInfNH4WEpi_ - _tNSeepNH4WEpi_ - _tNInfNH4S_ + _tNSeepNH4S_ + (1.0-_fRefrDetS_) * _tNMinDetS_ + _tNMinHumS_ - _tNResusNH4_ - _tNDifNH4Epi_ - _tNDifGroundNH4_ - _tNNitrS_ _ENDIF_
```

### `_tNAbioNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_N_NO3_flux_in_sediment
- **Equation**:

```
_tNAbioNO3S_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _tNInfNO3WHyp_ - _tNSeepNO3WHyp_ - _tNInfNO3S_ + _tNSeepNO3S_ + _tNNitrS_ - _tNDenitS_ - _tNResusNO3_ - _tNDifNO3Hyp_ - _tNDifGroundNO3_ _ELSE_ _tNInfNO3WEpi_ - _tNSeepNO3WEpi_ - _tNInfNO3S_ + _tNSeepNO3S_ + _tNNitrS_ - _tNDenitS_ - _tNResusNO3_ - _tNDifNO3Epi_ - _tNDifGroundNO3_ _ENDIF_
```

### `_tNAbioDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_N_detritus_flux_in_sediment
- **Equation**:

```
_tNAbioDetS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _tNMinDetS_ + _tNSetDetHyp_ - _tNResusDet_ _ELSE_ - _tNMinDetS_ + _tNSetDetEpi_ - _tNResusDet_ _ENDIF_
```

### `_tNAbioHumS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_N_humus_flux_in_sediment
- **Equation**:

```
_tNAbioHumS_ = _uNErosOM_ + _fRefrDetS_ * _tNMinDetS_ - _tNMinHumS_
```

### `_tNAbioTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_N_flux_for_mass_balance_check
- **Equation**:

```
_tNAbioTotT_ = _uNErosOM_ - _tNDenitS_ - _wNDenitWEpi_ * _uDepthWEpi_ - _wNDenitWHyp_ * _uDepthWHyp_ - _tNInfNH4S_ - _tNInfNO3S_ + _tNSeepNH4S_ + _tNSeepNO3S_ - _tNDifGroundNO3_ - _tNDifGroundNH4_
```

### `_wSiAbioSiO2WEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_sio2_flux_in_water
- **Equation**:

```
_wSiAbioSiO2WEpi_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_ _wSiMinDetWEpi_ + (1.0 - _fRefrDetS_) * _tSiMinDetS_ / _uDepthWEpi_ - _tInfSiO2WEpi_ / _uDepthWEpi_ + _tSeepSiO2WEpi_ / _uDepthWEpi_ _ELSE_ _wSiMinDetWEpi_ _ENDIF_
```

### `_wSiAbioDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_detritus_flux_in_water
- **Equation**:

```
_wSiAbioDetWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _wSiMinDetWEpi_ - (_tSiSetDetEpi_ ) / _uDepthWEpi_ _ELSE_ - _wSiMinDetWEpi_ - (_tSiSetDetEpi_ - _tSiResusDet_) / _uDepthWEpi_ _ENDIF_
```

### `_tSiAbioDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_abiotic/microbial_Si_detritus_flux_in_sediment
- **Equation**:

```
_tSiAbioDetS_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ - _tSiMinDetS_ + _tSiSetDetHyp_ - _tSiResusDet_ _ELSE_ - _tSiMinDetS_ + _tSiSetDetEpi_ - _tSiResusDet_ _ENDIF_
```

## Process_equations  (1 equations)

### `_uQEvPhra_`  [_mm_*_d_^-1]
- **Description**: Reed_evaporation(set_EQUAL_to_lake_evaporation)
- **Equation**:

```
_uQEvPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _uQEv_ _ELSE_ 0.0 _ENDIF_
```

## Nutrient_flux_to_pore_water  (3 equations)

### `_tPEvPO4WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_flux
- **Equation**:

```
_tPEvPO4WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _uQEvPhra_ / _mmPerm_ * _oPO4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNEvNH4WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Ammonium_flux
- **Equation**:

```
_tNEvNH4WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _uQEvPhra_ / _mmPerm_ * _oNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNEvNO3WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Nitrate_flux
- **Equation**:

```
_tNEvNO3WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _uQEvPhra_ / _mmPerm_ * _oNO3WM_ _ELSE_ 0.0 _ENDIF_
```

## Loss_of_SRP_from_pore_water  (1 equations)

### `_tPChemPO4M_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Chemical_loss_of_dissolved_P_from_pore_water
- **Equation**:

```
_tPChemPO4M_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _MAX_(0.0,_kPChemPO4_ *(_oPO4SM_ - _coPO4Max_)) _ELSE_ 0.0 _ENDIF_
```

## Phytoplankton  (1 equations)

### `_UseLoss_`  [0]
- **Description**: If_T_Use_Loss_function
- **Equation**:

```
_UseLoss_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSE_ 1.0 _ENDIF_
```

## Phytoplankton_processes  (22 equations)

### `_uFunTmLossHyp_`  [0]
- **Description**: Temp_function_of_grazing
- **Equation**:

```
_uFunTmLossHyp_ = _EXP_(-0.5/(_cSigTmLoss_*_cSigTmLoss_) *((_uTmHyp_-_cTmOptLoss_)*(_uTmHyp_-_cTmOptLoss_) -(_cTmRef_-_cTmOptLoss_)*(_cTmRef_-_cTmOptLoss_)))
```

### `_uFunTmLossEpi_`  [0]
- **Description**: Temp_function_of_grazing
- **Equation**:

```
_uFunTmLossEpi_ = _EXP_(-0.5/(_cSigTmLoss_*_cSigTmLoss_) *((_uTmEpi_-_cTmOptLoss_)*(_uTmEpi_-_cTmOptLoss_) -(_cTmRef_-_cTmOptLoss_)*(_cTmRef_-_cTmOptLoss_)))
```

### `_wSiUptDiatHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatoms_silica_uptake
- **Equation**:

```
_wSiUptDiatHyp_ = _cSiDDiat_ * _wDAssDiatHyp_
```

### `_wSiExcrDiatWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Si_excretion
- **Equation**:

```
_wSiExcrDiatWHyp_ = _cSiDDiat_ * _wDRespDiatWHyp_
```

### `_wSiLossDiatHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatom_grazing_loss
- **Equation**:

```
_wSiLossDiatHyp_ = _cSiDDiat_ * _wDLossDiatHyp_
```

### `_wSiMortDiatWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatoms_mortality_in_water
- **Equation**:

```
_wSiMortDiatWHyp_ = _cSiDDiat_ * _wDMortDiatWHyp_
```

### `_tSiSetDiatHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Diatoms_sedimentation
- **Equation**:

```
_tSiSetDiatHyp_ = _cSiDDiat_ * _tDSetDiatHyp_
```

### `_tSiResusDiat_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Diatoms_sedimentation
- **Equation**:

```
_tSiResusDiat_ = _cSiDDiat_ * _tDResusDiat_
```

### `_rCyDBlueHyp_`  [_gChl_*_gDW_^-1]
- **Description**: C-phycocyanin/DW-ratio_blue-greens
- **Equation**:

```
_rCyDBlueHyp_ = _cCyDBlueMax_ -(_cCyDBlueMax_ - _cCyDBlueMin_) * _aLLimBlueHyp_
```

### `_oCyanHyp_`  [_mgChl_*_m_^-3]
- **Description**: C-phycocyanin
- **Equation**:

```
_oCyanHyp_ = _rCyDBlueHyp_ * _oDBlueWHyp_ * _mgPerg_
```

### `_fDDiatHyp_`  [0]
- **Description**: DW_fraction_of_algal_group_of_total_algae
- **Equation**:

```
_fDDiatHyp_ = _oDDiatWHyp_ /(_oDDiatWHyp_ + _oDGrenWHyp_ + _oDBlueWHyp_ + _NearZero_)
```

### `_uFunTmLossSurf_`  [0]
- **Description**: Temp_function_of_grazing
- **Equation**:

```
_uFunTmLossSurf_ = _EXP_(-0.5/(_cSigTmLoss_*_cSigTmLoss_) *((_uTmSurf_-_cTmOptLoss_)*(_uTmSurf_-_cTmOptLoss_) -(_cTmRef_-_cTmOptLoss_)*(_cTmRef_-_cTmOptLoss_)))
```

### `_wSiUptDiatEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatoms_silica_uptake
- **Equation**:

```
_wSiUptDiatEpi_ = _cSiDDiat_ * _wDAssDiatEpi_
```

### `_wSiExcrDiatWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Si_excretion
- **Equation**:

```
_wSiExcrDiatWEpi_ = _cSiDDiat_ * _wDRespDiatWEpi_
```

### `_wSiLossDiatEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatom_grazing_loss
- **Equation**:

```
_wSiLossDiatEpi_ = _cSiDDiat_ * _wDLossDiatEpi_
```

### `_wSiMortDiatWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Diatoms_mortality_in_water
- **Equation**:

```
_wSiMortDiatWEpi_ = _cSiDDiat_ * _wDMortDiatWEpi_
```

### `_tSiSetDiatEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Diatoms_sedimentation
- **Equation**:

```
_tSiSetDiatEpi_ = _cSiDDiat_ * _tDSetDiatEpi_
```

### `_wSiPrimDiatWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sed_diatoms_in_PRIM_module
- **Equation**:

```
_wSiPrimDiatWHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wSiUptDiatHyp_ - _tSiSetDiatHyp_ / _uDepthWHyp_ - _wSiExcrDiatWHyp_ - _wSiMortDiatWHyp_ - _wSiLossDiatHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_wSiPrimDiatWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sed_diatoms_in_PRIM_module
- **Equation**:

```
_wSiPrimDiatWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wSiUptDiatEpi_ - _tSiSetDiatEpi_ / _uDepthWEpi_ - _wSiExcrDiatWEpi_ - _wSiMortDiatWEpi_ - _wSiLossDiatEpi_ _ELSE_ _wSiUptDiatEpi_ - _tSiSetDiatEpi_ / _uDepthWEpi_ - _wSiExcrDiatWEpi_ - _wSiMortDiatWEpi_ - _wSiLossDiatEpi_ + _tSiResusDiat_ / _uDepthWEpi_ _ENDIF_
```

### `_rCyDBlueEpi_`  [_gChl_*_gDW_^-1]
- **Description**: C-phycocyanin/DW-ratio_blue-greens
- **Equation**:

```
_rCyDBlueEpi_ = _cCyDBlueMax_ -(_cCyDBlueMax_ - _cCyDBlueMin_) * _aLLimBlueEpi_
```

### `_oCyanEpi_`  [_mgChl_*_m_^-3]
- **Description**: C-phycocyanin
- **Equation**:

```
_oCyanEpi_ = _rCyDBlueEpi_ * _oDBlueWEpi_ * _mgPerg_
```

### `_fDDiatEpi_`  [0]
- **Description**: DW_fraction_of_algal_group_of_total_algae
- **Equation**:

```
_fDDiatEpi_ = _oDDiatWEpi_ /(_oDDiatWEpi_ + _oDGrenWEpi_ + _oDBlueWEpi_ + _NearZero_)
```

## Phytoplankton_processes_Blue  (197 equations)

### `_rPDBlueWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDBlueWHyp_ = _oPBlueWHyp_ /(_oDBlueWHyp_+_NearZero_)
```

### `_rNDBlueWHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDBlueWHyp_ = _oNBlueWHyp_ /(_oDBlueWHyp_+_NearZero_)
```

### `_rPDBlueS_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDBlueS_ = _aPBlueS_ /(_aDBlueS_+_NearZero_)
```

### `_rNDBlueS_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDBlueS_ = _aNBlueS_ /(_aDBlueS_+_NearZero_)
```

### `_uFunTmBlueHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmBlueHyp_ = _EXP_(-0.5/(_cSigTmBlue_*_cSigTmBlue_) *((_uTmHyp_-_cTmOptBlue_)*(_uTmHyp_-_cTmOptBlue_) - (_cTmRef_-_cTmOptBlue_)*(_cTmRef_-_cTmOptBlue_)))
```

### `_uFunTmProdBlueHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmProdBlueHyp_ = _uFunTmBlueHyp_
```

### `_uFunTmRespBlueHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespBlueHyp_ = _uFunTmBlueHyp_
```

### `_uFunTmBlueEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmBlueEpi_ = _EXP_(-0.5/(_cSigTmBlue_*_cSigTmBlue_) *((_uTmEpi_-_cTmOptBlue_)*(_uTmEpi_-_cTmOptBlue_) - (_cTmRef_-_cTmOptBlue_)*(_cTmRef_-_cTmOptBlue_)))
```

### `_uFunTmProdBlueEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmProdBlueEpi_ = _uFunTmBlueEpi_
```

### `_uFunTmRespBlueEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespBlueEpi_ = _uFunTmBlueEpi_
```

### `_uFunTmBlueS_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmBlueS_ = _EXP_(-0.5/(_cSigTmBlue_*_cSigTmBlue_) *((_uTmBot_-_cTmOptBlue_)*(_uTmBot_-_cTmOptBlue_) - (_cTmRef_-_cTmOptBlue_)*(_cTmRef_-_cTmOptBlue_)))
```

### `_uFunTmRespBlueS_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespBlueS_ = _uFunTmBlueS_
```

### `_uFunTmBlueSurf_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmBlueSurf_ = _EXP_(-0.5/(_cSigTmBlue_*_cSigTmBlue_) *((_uTmSurf_-_cTmOptBlue_)*(_uTmSurf_-_cTmOptBlue_) - (_cTmRef_-_cTmOptBlue_)*(_cTmRef_-_cTmOptBlue_)))
```

### `_uFunTmProdBlueSurf_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmProdBlueSurf_ = _uFunTmBlueSurf_
```

### `_uFunTmRespBlueSurf_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespBlueSurf_ = _uFunTmBlueSurf_
```

### `_aAuxNfixLSurf_`  [0]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aAuxNfixLSurf_ = _cAlphNfix_ * _aLPARAveSurf_
```

### `_aAuxNfixLEpi_`  [0]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aAuxNfixLEpi_ = _cAlphNfix_ * _aLPARAveEpi_
```

### `_aAuxNfixLHyp_`  [0]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aAuxNfixLHyp_ = _cAlphNfix_ * _aLPARAveHyp_
```

### `_rNfixBlueSurf_`  [_ugN_*_mgChl_^-1*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_rNfixBlueSurf_ = _cNfixMaxBlue_ - _cNfixMaxBlue_ * _EXP_(- _aAuxNfixLSurf_) + _cNfixDarkBlue_
```

### `_rNfixBlueEpi_`  [_ugN_*_mgChl_^-1*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_rNfixBlueEpi_ = _cNfixMaxBlue_ - _cNfixMaxBlue_ * _EXP_(- _aAuxNfixLEpi_) + _cNfixDarkBlue_
```

### `_rNfixBlueHyp_`  [_ugN_*_mgChl_^-1*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_rNfixBlueHyp_ = _cNfixMaxBlue_ - _cNfixMaxBlue_ * _EXP_(- _aAuxNfixLHyp_) + _cNfixDarkBlue_
```

### `_aVPUptMaxCrBlueHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrBlueHyp_ = _MAX_(0.0,_cVPUptMaxBlue_ * _uFunTmProdBlueHyp_ *(_cPDBlueMax_ - _rPDBlueWHyp_) /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_aVPUptBlueHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptBlueHyp_ = _oPO4WHyp_ * _aVPUptMaxCrBlueHyp_ /(_aVPUptMaxCrBlueHyp_ / _cAffPUptBlue_ + _oPO4WHyp_)
```

### `_wPUptBlueHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVPUptBlueHyp_ * _oDBlueWHyp_ _ENDIF_
```

### `_aVNUptMaxCrBlueHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrBlueHyp_ = _MAX_(0.0,_cVNUptMaxBlue_ * _uFunTmProdBlueHyp_ * (_cNDBlueMax_ - _rNDBlueWHyp_) /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_ahNUptBlueHyp_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptBlueHyp_ = _aVNUptMaxCrBlueHyp_ / _cAffNUptBlue_
```

### `_aVNUptBlueHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptBlueHyp_ = _oNDissWHyp_ * _aVNUptMaxCrBlueHyp_ /(_ahNUptBlueHyp_ + _oNDissWHyp_)
```

### `_wNUptBlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVNUptBlueHyp_ * _oDBlueWHyp_ _ENDIF_
```

### `_tNUptBlueHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueHyp_ = _wNUptBlueHyp_ * _uDepthWHyp_
```

### `_afNH4UptBlueHyp_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptBlueHyp_ = _oNH4WHyp_ * _oNO3WHyp_ /((_ahNUptBlueHyp_ + _oNH4WHyp_) *(_ahNUptBlueHyp_ + _oNO3WHyp_)) + _oNH4WHyp_ * _ahNUptBlueHyp_ /((_oNH4WHyp_ + _oNO3WHyp_) *(_ahNUptBlueHyp_ + _oNO3WHyp_))
```

### `_uMuMaxTmBlueHyp_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmBlueHyp_ = _cMuMaxBlue_ * _uFunTmProdBlueHyp_
```

### `_uMuMaxTmBlueEpi_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmBlueEpi_ = _cMuMaxBlue_ * _uFunTmProdBlueEpi_
```

### `_aPLimBlueHyp_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimBlueHyp_ = _MAX_(0.0,(1.0 - _cPDBlueMin_ / _rPDBlueWHyp_) * _cPDBlueMax_ /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_aNLimBlueHyp_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimBlueHyp_ = _MAX_(0.0,(1.0 - _cNDBlueMin_ / _rNDBlueWHyp_) * _cNDBlueMax_ /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_aSiLimBlueHyp_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimBlueHyp_ = _oSiO2WHyp_ /(_hSiAssBlue_ + _oSiO2WHyp_)
```

### `_aLLimBlueHyp_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimBlueHyp_ = _UseSteeleBlue_ *(_EXP_(1.0) /(_aExtCoefHyp_ * _uDepthWHyp_) *(_EXP_(- _aLPARBotHyp_ /(_cLOptRefBlue_ * _uFunTmProdBlueHyp_)) - _EXP_(- _uLPARSurfHyp_ /(_cLOptRefBlue_ * _uFunTmProdBlueHyp_)))) +(1.0 - _UseSteeleBlue_) *(1.0 /(_aExtCoefHyp_ * _uDepthWHyp_) * _LN_((1.0 + _uLPARSurfHyp_ / (_hLRefBlue_ * _uFunTmProdBlueHyp_)) / (1.0 + _aLPARBotHyp_ /(_hLRefBlue_ * _uFunTmProdBlueHyp_))))
```

### `_aMuTmLBlueHyp_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLBlueHyp_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimBlueHyp_ * _uMuMaxTmBlueHyp_
```

### `_aNutLimBlueHyp_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimBlueHyp_ = _MIN_(_aPLimBlueHyp_,(_MIN_(_aNLimBlueHyp_,_aSiLimBlueHyp_)))
```

### `_aMuBlueHyp_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuBlueHyp_ = _aNutLimBlueHyp_ * _aMuTmLBlueHyp_
```

### `_wDAssBlueHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aMuBlueHyp_*_oDBlueWHyp_ _ENDIF_
```

### `_rChDBlueHyp_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDBlueHyp_ = _cChDBlueMax_ -(_cChDBlueMax_ - _cChDBlueMin_) * _aLLimBlueHyp_
```

### `_oChlaBlueHyp_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaBlueHyp_ = _mgPerg_ * _rChDBlueHyp_ * _oDBlueWHyp_
```

### `_aChlaBlueHyp_`  [_mgChl_*_m_^-2]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_aChlaBlueHyp_ = _mgPerg_ * _rChDBlueHyp_ * _aDBlueWHyp_
```

### `_aExtChBlueHyp_`  [_m_^2*_gChl_^-1]
- **Description**: Specific_extinction_per_unit_chlorophyll-a
- **Equation**:

```
_aExtChBlueHyp_ = _cExtSpBlue_ / _rChDBlueHyp_
```

### `_aNfixBlueHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aNfixBlueHyp_  = _rNfixBlueHyp_ *_aChlaBlueHyp_ /_ugPerg_
```

### `_tNUptBlueAirHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_tNUptBlueAirHyp_ = _IF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aNfixBlueHyp_ _ENDIF_
```

### `_tNUptBlueWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueWHyp_ = _IF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ _tNUptBlueHyp_ _ELSE_ _tNUptBlueHyp_ - _tNUptBlueAirHyp_ _ENDIF_
```

### `_wNUptBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptBlueWHyp_ = _tNUptBlueWHyp_ / _uDepthWHyp_
```

### `_ukDRespTmBlueHyp_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmBlueHyp_ = _kDRespBlue_ * _uFunTmRespBlueHyp_
```

### `_wNUptNH4BlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4BlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _afNH4UptBlueHyp_ * _wNUptBlueWHyp_ _ENDIF_
```

### `_wNUptNO3BlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3BlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptBlueWHyp_ - _wNUptNH4BlueHyp_ _ENDIF_
```

### `_ukDRespTmBlueEpi_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmBlueEpi_ = _kDRespBlue_ * _uFunTmRespBlueEpi_
```

### `_ukDRespTmBlueS_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmBlueS_ = _kDRespBlue_ * _uFunTmRespBlueS_
```

### `_wDRespBlueWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukDRespTmBlueHyp_ * _oDBlueWHyp_ _ENDIF_
```

### `_ukDRespTmBlueSurf_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmBlueSurf_ = _kDRespBlue_ * _uFunTmRespBlueSurf_
```

### `_ukLossTmBlueHyp_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmBlueHyp_ = _UseLoss_ * _kLossBlue_ * _uFunTmLossHyp_
```

### `_ukLossTmBlueEpi_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmBlueEpi_ = _UseLoss_ * _kLossBlue_ * _uFunTmLossEpi_
```

### `_wDLossBlueHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukLossTmBlueHyp_ * _oDBlueWHyp_ _ENDIF_
```

### `_wDMortBlueWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _oDBlueWHyp_ _ENDIF_
```

### `_uCorVSetBlueHyp_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetBlueHyp_ = (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMHyp_ * _uFunTmSetHyp_
```

### `_tDResusBlue_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_DW_blue-greens
- **Equation**:

```
_tDResusBlue_ = _aDBlueS_ /(_aDPhytS_+_NearZero_) * _tDResusPhytTot_
```

### `_tDRespBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_sediment_Algae
- **Equation**:

```
_tDRespBlueS_ = _ukDRespTmBlueS_ * _aDBlueS_
```

### `_tDMortBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_in_sed
- **Equation**:

```
_tDMortBlueS_ = _kMortBlueS_ * _aDBlueS_
```

### `_ukDDecBlueHyp_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecBlueHyp_ = _ukDRespTmBlueHyp_ + _ukLossTmBlueHyp_ + _kMortBlueW_ +(_uCorVSetBlueHyp_ * _uFunTmSetHyp_) / _uDepthWHyp_
```

### `_wPExcrBlueWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (_rPDBlueWHyp_ * 2.0 )/(_cPDBlueMax_ + _rPDBlueWHyp_) * _rPDBlueWHyp_ * _wDRespBlueWHyp_ _ENDIF_
```

### `_wPLossBlueHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDBlueWHyp_ * _wDLossBlueHyp_ _ENDIF_
```

### `_wPMortBlueWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _oPBlueWHyp_ _ENDIF_
```

### `_tPResusBlue_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tPResusBlue_ = _rPDBlueS_ * _tDResusBlue_
```

### `_tPExcrBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_algae_in_sediment
- **Equation**:

```
_tPExcrBlueS_ = (_rPDBlueS_ *2.0)/(_cPDBlueMax_ + _rPDBlueS_) * _rPDBlueS_ * _tDRespBlueS_
```

### `_tPMortBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_of_algae_in_sediment
- **Equation**:

```
_tPMortBlueS_ = _kMortBlueS_ * _aPBlueS_
```

### `_wNExcrBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (_rNDBlueWHyp_ *2.0)/(_cNDBlueMax_ + _rNDBlueWHyp_) * _rNDBlueWHyp_ * _wDRespBlueWHyp_ _ENDIF_
```

### `_wNLossBlueHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDBlueWHyp_ * _wDLossBlueHyp_ _ENDIF_
```

### `_wNMortBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortBlueWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _oNBlueWHyp_ _ENDIF_
```

### `_tNResusBlue_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tNResusBlue_ = _rNDBlueS_ * _tDResusBlue_
```

### `_tNExcrBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_algae_in_sediment
- **Equation**:

```
_tNExcrBlueS_ = (2.0 * _rNDBlueS_) /(_cNDBlueMax_ + _rNDBlueS_) * _rNDBlueS_ * _tDRespBlueS_
```

### `_tNMortBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_of_algae_in_sediment
- **Equation**:

```
_tNMortBlueS_ = _kMortBlueS_ * _aNBlueS_
```

### `_uCorVSetBlueEpi_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetBlueEpi_ = (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMEpi_ * _uFunTmSetEpi_
```

### `_rPDBlueWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDBlueWEpi_ = _oPBlueWEpi_ /(_oDBlueWEpi_+_NearZero_)
```

### `_aVPUptMaxCrBlueEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrBlueEpi_ = _MAX_(0.0,_cVPUptMaxBlue_ * _uFunTmProdBlueEpi_ *(_cPDBlueMax_ - _rPDBlueWEpi_) /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_aVPUptBlueEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptBlueEpi_ = _oPO4WEpi_ * _aVPUptMaxCrBlueEpi_ /(_aVPUptMaxCrBlueEpi_ / _cAffPUptBlue_ + _oPO4WEpi_)
```

### `_wPUptBlueEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptBlueEpi_ = _aVPUptBlueEpi_ * _oDBlueWEpi_
```

### `_rNDBlueWEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDBlueWEpi_ = _oNBlueWEpi_ /(_oDBlueWEpi_+_NearZero_)
```

### `_aVNUptMaxCrBlueEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrBlueEpi_ = _MAX_(0.0,_cVNUptMaxBlue_ * _uFunTmProdBlueEpi_ * (_cNDBlueMax_ - _rNDBlueWEpi_) /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_ahNUptBlueEpi_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptBlueEpi_ = _aVNUptMaxCrBlueEpi_ / _cAffNUptBlue_
```

### `_aVNUptBlueEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptBlueEpi_ = _oNDissWEpi_ * _aVNUptMaxCrBlueEpi_ /(_ahNUptBlueEpi_ + _oNDissWEpi_)
```

### `_wNUptBlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptBlueEpi_ = _aVNUptBlueEpi_ * _oDBlueWEpi_
```

### `_tNUptBlueEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueEpi_ = _wNUptBlueEpi_ * _uDepthWEpi_
```

### `_aLLimBlueEpi_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimBlueEpi_ = _UseSteeleBlue_ *(_EXP_(1.0) /(_aExtCoefEpi_ * _uDepthWEpi_) *(_EXP_(- _aLPARBotEpi_ /(_cLOptRefBlue_ * _uFunTmProdBlueEpi_)) - _EXP_(- _aLPARBotSurf_ /(_cLOptRefBlue_ * _uFunTmProdBlueEpi_)))) +(1.0 - _UseSteeleBlue_) *(1.0 /(_aExtCoefEpi_ * _uDepthWEpi_) * _LN_((1.0 + _aLPARBotSurf_ / (_hLRefBlue_ * _uFunTmProdBlueEpi_)) / (1.0 + _aLPARBotEpi_ /(_hLRefBlue_ * _uFunTmProdBlueEpi_))))
```

### `_rChDBlueEpi_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDBlueEpi_ = _cChDBlueMax_ -(_cChDBlueMax_ - _cChDBlueMin_) * _aLLimBlueEpi_
```

### `_aChlaBlueEpi_`  [_mgChl_*_m_^-2]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_aChlaBlueEpi_ = _mgPerg_ * _rChDBlueEpi_ * _aDBlueWEpi_
```

### `_aNfixBlueEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aNfixBlueEpi_ = _rNfixBlueEpi_ *_aChlaBlueEpi_ /_ugPerg_
```

### `_afNH4UptBlueEpi_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptBlueEpi_ = _oNH4WEpi_ * _oNO3WEpi_ /((_ahNUptBlueEpi_ + _oNH4WEpi_) *(_ahNUptBlueEpi_ + _oNO3WEpi_)) + _oNH4WEpi_ * _ahNUptBlueEpi_ /((_oNH4WEpi_ + _oNO3WEpi_) *(_ahNUptBlueEpi_ + _oNO3WEpi_))
```

### `_tNUptBlueAirEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_tNUptBlueAirEpi_ = _IF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aNfixBlueEpi_ _ENDIF_
```

### `_tNUptBlueWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueWEpi_ = _IF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ _tNUptBlueEpi_ _ELSE_ _tNUptBlueEpi_ - _tNUptBlueAirEpi_ _ENDIF_
```

### `_wNUptBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptBlueWEpi_ = _tNUptBlueWEpi_ / _uDepthWEpi_
```

### `_wNUptNH4BlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4BlueEpi_ = _afNH4UptBlueEpi_ * _wNUptBlueWEpi_
```

### `_wNUptNO3BlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3BlueEpi_ = _wNUptBlueWEpi_ - _wNUptNH4BlueEpi_
```

### `_aPLimBlueEpi_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimBlueEpi_ = _MAX_(0.0,(1.0 - _cPDBlueMin_ / _rPDBlueWEpi_) * _cPDBlueMax_ /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_aNLimBlueEpi_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimBlueEpi_ = _MAX_(0.0,(1.0 - _cNDBlueMin_ / _rNDBlueWEpi_) * _cNDBlueMax_ /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_aSiLimBlueEpi_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimBlueEpi_ = _oSiO2WEpi_ /(_hSiAssBlue_ + _oSiO2WEpi_)
```

### `_aMuTmLBlueEpi_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLBlueEpi_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimBlueEpi_ * _uMuMaxTmBlueEpi_
```

### `_aNutLimBlueEpi_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimBlueEpi_ = _MIN_(_aPLimBlueEpi_ , (_MIN_(_aNLimBlueEpi_,_aSiLimBlueEpi_)))
```

### `_aMuBlueEpi_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuBlueEpi_ = _aNutLimBlueEpi_ * _aMuTmLBlueEpi_
```

### `_wDAssBlueEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssBlueEpi_ = _aMuBlueEpi_*_oDBlueWEpi_
```

### `_oChlaBlueEpi_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaBlueEpi_ = _mgPerg_ * _rChDBlueEpi_ * _oDBlueWEpi_
```

### `_aLLimBlueSurf_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ -9999 _ELSE_ _MAX_(0.0,_UseSteeleBlue_ *(_EXP_(1.0) /(_aExtSurf_) *(_EXP_(- _aLPARBotSurf_/(_cLOptRefBlue_ *  _uFunTmProdBlueSurf_)) - _EXP_(- _uLPARSurf_ /(_cLOptRefBlue_ *  _uFunTmProdBlueSurf_)))) +(1.0 - _UseSteeleBlue_) *(1.0 /(_aExtSurf_) * _LN_((1.0 + _uLPARSurf_ / (_hLRefBlue_ * _uFunTmProdBlueSurf_)) / (1.0 + _aLPARBotSurf_ /(_hLRefBlue_ * _uFunTmProdBlueSurf_))))) _ENDIF_
```

### `_aRepLLimBlue_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aRepLLimBlue_ = (_aLLimBlueSurf_* _aDBlueSurf_ + _aLLimBlueEpi_* _aDBlueWEpi_) / (_aDBlueSurf_ + _aDBlueWEpi_)
```

### `_aChlaLimFloBlueSurf_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aChlaLimFloBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ (1.0 - (_POW_ ((_aChlaBlueSurf_ / _cDepthSurf_) _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cChlaThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ ((_aChlaBlueSurf_ / _cDepthSurf_) _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aChlaLimFloBlueEpi_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aChlaLimFloBlueEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_  _OR_ _aDBlueWEpi_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ (1.0 - (_POW_ (_oChlaBlueEpi_ _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cChlaThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ (_oChlaBlueEpi_ _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aChlaLimFloBlueHyp_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aChlaLimFloBlueHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ _OR_ _aDBlueWHyp_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_  (1.0 - (_POW_ (_oChlaBlueHyp_ _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cChlaThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ (_oChlaBlueHyp_ _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aVWLimFloBlue_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aVWLimFloBlue_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_  (1.0 - (_POW_ (_uVWind_ _POWOPERATOR_ _cStepPow_)) / ((_POW_ (_cVWindThrBlue_ _POWOPERATOR_ _cStepPow_)) + (_POW_ (_uVWind_ _POWOPERATOR_ _cStepPow_)))) _ENDIF_
```

### `_aTmLimFloBlueSurf_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aTmLimFloBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ (1.0 - (_POW_ (_uTmSurf_ _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cTmThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ (_uTmSurf_ _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aTmLimFloBlueEpi_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aTmLimFloBlueEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (1.0 - (_POW_ (_uTmEpi_ _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cTmThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ (_uTmEpi_ _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aTmLimFloBlueHyp_`  [0]
- **Description**: Thresholds_floating
- **Equation**:

```
_aTmLimFloBlueHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_  (1.0 - (_POW_ (_uTmHyp_ _POWOPERATOR_ (-_cStepPow_))) / ((_POW_ (_cTmThrBlue_ _POWOPERATOR_ (-_cStepPow_))) + (_POW_ (_uTmHyp_ _POWOPERATOR_ (-_cStepPow_))))) _ENDIF_
```

### `_aTrigFloBlueSurf_`  [0]
- **Description**: Ability_floating
- **Equation**:

```
_aTrigFloBlueSurf_ =  _aVWLimFloBlue_ * _aTmLimFloBlueSurf_ * _aChlaLimFloBlueSurf_
```

### `_aTrigFloBlueEpi_`  [0]
- **Description**: Ability_floating
- **Equation**:

```
_aTrigFloBlueEpi_ =  _aVWLimFloBlue_ * _aTmLimFloBlueEpi_ * _aChlaLimFloBlueEpi_
```

### `_aTrigFloBlueHyp_`  [0]
- **Description**: Ability_floating
- **Equation**:

```
_aTrigFloBlueHyp_ =   _aTmLimFloBlueHyp_ * _aChlaLimFloBlueHyp_
```

### `_uVFloBlueSurf_`  [_m_*_d_^-1]
- **Description**: Floating_speed_of_Algae
- **Equation**:

```
_uVFloBlueSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _aTrigFloBlueSurf_ * _cVFloMaxBlueW_ _ENDIF_
```

### `_uVFloBlueEpi_`  [_m_*_d_^-1]
- **Description**: Floating_speed_of_Algae
- **Equation**:

```
_uVFloBlueEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aTrigFloBlueEpi_ * _cVFloMaxBlueW_ _ENDIF_
```

### `_uVFloBlueHyp_`  [_m_*_d_^-1]
- **Description**: Floating_speed_of_Algae
- **Equation**:

```
_uVFloBlueHyp_ =  _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aTrigFloBlueHyp_ * _cVFloMaxBlueW_ _ENDIF_
```

### `_uVBlueHyp_`  [_m_*_d_^-1]
- **Description**: Velocity_of_Algae_in_Hypolimnion
- **Equation**:

```
_uVBlueHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_  - _uCorVSetBlueHyp_ _ELSE_  _uVFloBlueHyp_ - _uCorVSetBlueHyp_  _ENDIF_
```

### `_tDSetBlueHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetBlueHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_uVBlueHyp_ _LT_ 0.0) _THEN_ - _uVBlueHyp_ * _oDBlueWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPSetBlueHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDBlueWHyp_ * _tDSetBlueHyp_ _ENDIF_
```

### `_tNSetBlueHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetBlueHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDBlueWHyp_ * _tDSetBlueHyp_ _ENDIF_
```

### `_tDFloBlueHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tDFloBlueHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_uVBlueHyp_ _GE_ 0.0) _THEN_ _uVBlueHyp_ * _oDBlueWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tPFloBlueHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tPFloBlueHyp_ =  _tDFloBlueHyp_  * _rPDBlueWHyp_
```

### `_tNFloBlueHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tNFloBlueHyp_ =  _tDFloBlueHyp_  * _rNDBlueWHyp_
```

### `_uVBlueEpi_`  [_m_*_d_^-1]
- **Description**: Velocity_of_Algae_in_Epilimnion
- **Equation**:

```
_uVBlueEpi_ = _IF_ (_InclSurf_ _EQ_ _TRUE_) _THEN_ _uVFloBlueEpi_ - _uCorVSetBlueEpi_ _ELSE_ - _uCorVSetBlueEpi_ _ENDIF_
```

### `_tDSetBlueEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetBlueEpi_ = _IF_ (_uVBlueEpi_ _LT_ 0.0) _THEN_ - _uVBlueEpi_ * _oDBlueWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tDFloBlueEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tDFloBlueEpi_ = _IF_ (_uVBlueEpi_ _GE_ 0.0) _THEN_ _uVBlueEpi_ * _oDBlueWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_tNSetBlueEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetBlueEpi_ = _rNDBlueWEpi_ * _tDSetBlueEpi_
```

### `_tNFloBlueEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tNFloBlueEpi_ =  _tDFloBlueEpi_  * _rNDBlueWEpi_
```

### `_tPSetBlueEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetBlueEpi_ = _rPDBlueWEpi_ * _tDSetBlueEpi_
```

### `_tPFloBlueEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Float_flux_of_Algae
- **Equation**:

```
_tPFloBlueEpi_ =  _tDFloBlueEpi_  * _rPDBlueWEpi_
```

### `_uCorVSetBlueSurf_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetBlueSurf_ = (_cVSetBlue_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMSurf_ * _uFunTmSetSurf_
```

### `_uVBlueSurf_`  [_m_*_d_^-1]
- **Description**: Velocity_of_Algae_in_Surface
- **Equation**:

```
_uVBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ - _uCorVSetBlueSurf_ _ELSE_ _uVFloBlueSurf_ - _uCorVSetBlueSurf_ _ENDIF_
```

### `_tDSetBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSEIF_ (_uVBlueSurf_ _LT_ 0.0) _THEN_ _aDBlueSurf_  / _cDepthSurf_ * (- _uVBlueSurf_) _ELSE_ 0.0 _ENDIF_
```

### `_rNDBlueSurf_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDBlueSurf_ = _aNBlueSurf_ / (_aDBlueSurf_ + _NearZero_)
```

### `_tNSetBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetBlueSurf_ = _rNDBlueSurf_ * _tDSetBlueSurf_
```

### `_rPDBlueSurf_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDBlueSurf_ = _aPBlueSurf_ / (_aDBlueSurf_ + _NearZero_)
```

### `_tPSetBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetBlueSurf_ = _rPDBlueSurf_ * _tDSetBlueSurf_
```

### `_wDPrimBlueWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimBlueWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wDAssBlueHyp_ - _wDRespBlueWHyp_ - _wDLossBlueHyp_ - _wDMortBlueWHyp_ + (_tDResusBlue_ + _tDSetBlueEpi_ - _tDSetBlueHyp_ - _tDFloBlueHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wPPrimBlueWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimBlueWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wPUptBlueHyp_ - _wPExcrBlueWHyp_ - _wPLossBlueHyp_ - _wPMortBlueWHyp_+ (_tPResusBlue_ + _tPSetBlueEpi_ - _tPSetBlueHyp_ - _tPFloBlueHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wNPrimBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimBlueWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptBlueHyp_ - _wNExcrBlueWHyp_ - _wNLossBlueHyp_ - _wNMortBlueWHyp_+ (_tNResusBlue_ + _tNSetBlueEpi_ - _tNSetBlueHyp_ - _tNFloBlueHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wDRespBlueWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespBlueWEpi_ = _ukDRespTmBlueEpi_ * _oDBlueWEpi_
```

### `_wDLossBlueEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossBlueEpi_ = _ukLossTmBlueEpi_ * _oDBlueWEpi_
```

### `_wDMortBlueWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortBlueWEpi_ = _kMortBlueW_ * _oDBlueWEpi_
```

### `_ukDDecBlueEpi_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecBlueEpi_ = _ukDRespTmBlueEpi_ + _ukLossTmBlueEpi_ + _kMortBlueW_ +(_uCorVSetBlueEpi_ * _uFunTmSetEpi_) / _uDepthWEpi_
```

### `_wPExcrBlueWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrBlueWEpi_ = (_rPDBlueWEpi_ * 2.0 )/(_cPDBlueMax_ + _rPDBlueWEpi_) * _rPDBlueWEpi_ * _wDRespBlueWEpi_
```

### `_wPLossBlueEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossBlueEpi_ = _rPDBlueWEpi_ * _wDLossBlueEpi_
```

### `_wPMortBlueWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortBlueWEpi_ = _kMortBlueW_ * _oPBlueWEpi_
```

### `_wNExcrBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrBlueWEpi_ = (_rNDBlueWEpi_ *2.0)/(_cNDBlueMax_ + _rNDBlueWEpi_) * _rNDBlueWEpi_ * _wDRespBlueWEpi_
```

### `_wNLossBlueEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossBlueEpi_ = _rNDBlueWEpi_ * _wDLossBlueEpi_
```

### `_wNMortBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortBlueWEpi_ = _kMortBlueW_ * _oNBlueWEpi_
```

### `_wDPrimBlueWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimBlueWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wDAssBlueEpi_ - _wDRespBlueWEpi_ - _wDLossBlueEpi_ - _wDMortBlueWEpi_ + (_tDSetBlueSurf_-_tDFloBlueEpi_ + _tDFloBlueHyp_- _tDSetBlueEpi_ ) / _uDepthWEpi_ _ELSE_ _wDAssBlueEpi_ - _wDRespBlueWEpi_ - _wDLossBlueEpi_ - _wDMortBlueWEpi_ + (_tDResusBlue_ + _tDSetBlueSurf_ - _tDSetBlueEpi_ -  _tDFloBlueEpi_) / _uDepthWEpi_ _ENDIF_
```

### `_wPPrimBlueWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimBlueWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wPUptBlueEpi_ - _wPExcrBlueWEpi_ - _wPLossBlueEpi_ - _wPMortBlueWEpi_+ (_tPSetBlueSurf_-_tPFloBlueEpi_ + _tPFloBlueHyp_- _tPSetBlueEpi_ ) / _uDepthWEpi_ _ELSE_ _wPUptBlueEpi_ - _wPExcrBlueWEpi_ - _wPLossBlueEpi_ - _wPMortBlueWEpi_+ (_tPResusBlue_ + _tPSetBlueSurf_ - _tPSetBlueEpi_ -  _tPFloBlueEpi_) / _uDepthWEpi_ _ENDIF_
```

### `_wNPrimBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimBlueWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wNUptBlueEpi_ - _wNExcrBlueWEpi_ - _wNLossBlueEpi_ - _wNMortBlueWEpi_ + (_tNSetBlueSurf_-_tNFloBlueEpi_ + _tNFloBlueHyp_- _tNSetBlueEpi_ ) / _uDepthWEpi_ _ELSE_ _wNUptBlueEpi_ - _wNExcrBlueWEpi_ - _wNLossBlueEpi_ - _wNMortBlueWEpi_+ (_tNResusBlue_ + _tNSetBlueSurf_ - _tNSetBlueEpi_ -  _tNFloBlueEpi_) / _uDepthWEpi_ _ENDIF_
```

### `_uMuMaxTmBlueSurf_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmBlueSurf_ = _cMuMaxBlue_ * _uFunTmProdBlueSurf_
```

### `_aMuTmLBlueSurf_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLBlueSurf_ = _ufDay_ * _aLLimBlueSurf_ * _uMuMaxTmBlueSurf_
```

### `_aPLimBlueSurf_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimBlueSurf_ = _MAX_(0.0,(1.0 - _cPDBlueMin_ / _rPDBlueSurf_) * _cPDBlueMax_ /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_aNLimBlueSurf_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimBlueSurf_ = _MAX_(0.0,(1.0 - _cNDBlueMin_ / _rNDBlueSurf_) * _cNDBlueMax_ /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_aSiLimBlueSurf_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimBlueSurf_ = _oSiO2WEpi_ /(_hSiAssBlue_ + _oSiO2WEpi_)
```

### `_aNutLimBlueSurf_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ -9999 _ELSE_ _MIN_(_aPLimBlueSurf_,_MIN_(_aNLimBlueSurf_,_aSiLimBlueSurf_)) _ENDIF_
```

### `_aRepPLimBlue_`  [0]
- **Description**: P_limitation_of_blue_greens
- **Equation**:

```
_aRepPLimBlue_ = (_aPLimBlueSurf_* _aDBlueSurf_ + _aPLimBlueEpi_* _aDBlueWEpi_) / (_aDBlueSurf_ + _aDBlueWEpi_)
```

### `_aRepNLimBlue_`  [0]
- **Description**: N_limitation_of_blue_greens
- **Equation**:

```
_aRepNLimBlue_ = (_aNLimBlueSurf_* _aDBlueSurf_ + _aNLimBlueEpi_* _aDBlueWEpi_) / (_aDBlueSurf_ + _aDBlueWEpi_)
```

### `_aRepNutLimBlue_`  [0]
- **Description**: Nutrient_limitation_of_blue_greens
- **Equation**:

```
_aRepNutLimBlue_ = (_aNutLimBlueSurf_* _aDBlueSurf_ + _aNutLimBlueEpi_* _aDBlueWEpi_) / (_aDBlueSurf_ + _aDBlueWEpi_)
```

### `_aMuBlueSurf_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuBlueSurf_ = _aNutLimBlueSurf_ * _aMuTmLBlueSurf_
```

### `_tDAssBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_tDAssBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _aMuBlueSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_aVNUptMaxCrBlueSurf_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algaecorrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrBlueSurf_ = _MAX_(0.0,_cVNUptMaxBlue_ * _uFunTmProdBlueSurf_ * (_cNDBlueMax_ - _rNDBlueSurf_) /(_cNDBlueMax_ - _cNDBlueMin_))
```

### `_aVPUptMaxCrBlueSurf_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algaecorrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrBlueSurf_ = _MAX_(0.0,_cVPUptMaxBlue_ * _uFunTmProdBlueSurf_ *(_cPDBlueMax_ - _rPDBlueSurf_) /(_cPDBlueMax_ - _cPDBlueMin_))
```

### `_ahNUptBlueSurf_`  [_gN_*_m_^-3]
- **Description**: Half-sat_ndissw_for_uptake_by_Algae
- **Equation**:

```
_ahNUptBlueSurf_ = _aVNUptMaxCrBlueSurf_ / _cAffNUptBlue_
```

### `_aVNUptBlueSurf_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptBlueSurf_ = _oNDissWEpi_ * _aVNUptMaxCrBlueSurf_ /(_ahNUptBlueSurf_ + _oNDissWEpi_)
```

### `_aVPUptBlueSurf_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptBlueSurf_ = _oPO4WEpi_ * _aVPUptMaxCrBlueSurf_ /(_aVPUptMaxCrBlueSurf_ / _cAffPUptBlue_ + _oPO4WEpi_)
```

### `_tNUptBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _aVNUptBlueSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_aNfixBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_aNfixBlueSurf_ = _rNfixBlueSurf_ *_aChlaBlueSurf_ /_ugPerg_
```

### `_tNUptBlueAirSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_fixation_Algae
- **Equation**:

```
_tNUptBlueAirSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSEIF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aNfixBlueSurf_ _ENDIF_
```

### `_tNUptBlueWSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_tNUptBlueWSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSEIF_ (_InclNfix_ _EQ_ _FALSE_) _THEN_ _tNUptBlueSurf_ _ELSE_ _tNUptBlueSurf_ - _tNUptBlueAirSurf_ _ENDIF_
```

### `_afNH4UptBlueSurf_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptBlueSurf_ = _oNH4WEpi_ * _oNO3WEpi_ /((_ahNUptBlueSurf_ + _oNH4WEpi_) *(_ahNUptBlueSurf_ + _oNO3WEpi_)) + _oNH4WEpi_ * _ahNUptBlueSurf_ /((_oNH4WEpi_ + _oNO3WEpi_) *(_ahNUptBlueSurf_ + _oNO3WEpi_))
```

### `_tNUptNH4BlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_tNUptNH4BlueSurf_ = _afNH4UptBlueSurf_ * _tNUptBlueWSurf_
```

### `_tNUptNO3BlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_tNUptNO3BlueSurf_ = _tNUptBlueWSurf_ - _tNUptNH4BlueSurf_
```

### `_tPUptBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_tPUptBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _aVPUptBlueSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_tDRespBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_Algae_on_Surface
- **Equation**:

```
_tDRespBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _ukDRespTmBlueSurf_ *_aDBlueSurf_ _ENDIF_
```

### `_tNExcrBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_Algae_in_surface_water
- **Equation**:

```
_tNExcrBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ (_rNDBlueSurf_ * 2.0 )/(_cNDBlueMax_ + _rNDBlueSurf_) * _rNDBlueSurf_ * _tDRespBlueSurf_ _ENDIF_
```

### `_tPExcrBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_Algae_in_surface_water
- **Equation**:

```
_tPExcrBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ (_rPDBlueSurf_ * 2.0 )/(_cPDBlueMax_ + _rPDBlueSurf_) * _rPDBlueSurf_ * _tDRespBlueSurf_ _ENDIF_
```

### `_tDMortBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_on_Surface
- **Equation**:

```
_tDMortBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _aDBlueSurf_ _ENDIF_
```

### `_tNMortBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_flux_by_mortality_on_Surface
- **Equation**:

```
_tNMortBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _aNBlueSurf_ _ENDIF_
```

### `_tPMortBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: P_flux_by_mortality_on_Surface
- **Equation**:

```
_tPMortBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _kMortBlueW_ * _aPBlueSurf_ _ENDIF_
```

### `_ukLossTmBlueSurf_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmBlueSurf_ = _UseLoss_ * _kLossBlue_ * _uFunTmLossSurf_
```

### `_tDLossBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_tDLossBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _ukLossTmBlueSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_tPLossBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_tPLossBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _rPDBlueSurf_ * _tDLossBlueSurf_ _ENDIF_
```

### `_tNLossBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_tNLossBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _rNDBlueSurf_ * _tDLossBlueSurf_ _ENDIF_
```

### `_tDPrimBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_surface_Algae
- **Equation**:

```
_tDPrimBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _tDAssBlueSurf_ - _tDRespBlueSurf_ + _tDFloBlueEpi_ - _tDSetBlueSurf_- _tDMortBlueSurf_ _ENDIF_
```

### `_tNPrimBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_flux_from_PRIM_module_to_surface_Algae
- **Equation**:

```
_tNPrimBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _tNUptBlueSurf_ - _tNExcrBlueSurf_  + _tNFloBlueEpi_ - _tNSetBlueSurf_ - _tNMortBlueSurf_ _ENDIF_
```

### `_tPPrimBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_flux_from_PRIM_module_to_surface_Algae
- **Equation**:

```
_tPPrimBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _tPUptBlueSurf_ - _tPExcrBlueSurf_ + _tPFloBlueEpi_ - _tPSetBlueSurf_- _tPMortBlueSurf_ _ENDIF_
```

### `_tDPrimBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tDPrimBlueS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tDSetBlueEpi_ - _tDResusBlue_ - _tDMortBlueS_ - _tDRespBlueS_ _ELSE_ _tDSetBlueHyp_ - _tDResusBlue_ - _tDMortBlueS_ - _tDRespBlueS_ _ENDIF_
```

### `_tPPrimBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tPPrimBlueS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tPSetBlueEpi_ - _tPResusBlue_ - _tPMortBlueS_ - _tPExcrBlueS_ _ELSE_ _tPSetBlueHyp_ - _tPResusBlue_ - _tPMortBlueS_ - _tPExcrBlueS_ _ENDIF_
```

### `_tNPrimBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tNPrimBlueS_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _tNSetBlueEpi_ - _tNResusBlue_ - _tNMortBlueS_ - _tNExcrBlueS_ _ELSE_ _tNSetBlueHyp_ - _tNResusBlue_ - _tNMortBlueS_ - _tNExcrBlueS_ _ENDIF_
```

## Phytoplankton_processes_Green  (109 equations)

### `_rNDGrenWHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDGrenWHyp_ = _oNGrenWHyp_ /(_oDGrenWHyp_+_NearZero_)
```

### `_rPDGrenS_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDGrenS_ = _aPGrenS_ /(_aDGrenS_+_NearZero_)
```

### `_rNDGrenS_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDGrenS_ = _aNGrenS_ /(_aDGrenS_+_NearZero_)
```

### `_uFunTmGrenHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmGrenHyp_ = _EXP_(-0.5/(_cSigTmGren_*_cSigTmGren_) *((_uTmHyp_-_cTmOptGren_)*(_uTmHyp_-_cTmOptGren_) - (_cTmRef_-_cTmOptGren_)*(_cTmRef_-_cTmOptGren_)))
```

### `_uFunTmGrenEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmGrenEpi_ = _EXP_(-0.5/(_cSigTmGren_*_cSigTmGren_) *((_uTmEpi_-_cTmOptGren_)*(_uTmEpi_-_cTmOptGren_) - (_cTmRef_-_cTmOptGren_)*(_cTmRef_-_cTmOptGren_)))
```

### `_uFunTmGrenS_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmGrenS_ = _EXP_(-0.5/(_cSigTmGren_*_cSigTmGren_) *((_uTmBot_-_cTmOptGren_)*(_uTmBot_-_cTmOptGren_) - (_cTmRef_-_cTmOptGren_)*(_cTmRef_-_cTmOptGren_)))
```

### `_uFunTmProdGrenHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmProdGrenHyp_ = _uFunTmGrenHyp_
```

### `_uFunTmRespGrenHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespGrenHyp_ = _uFunTmGrenHyp_
```

### `_uFunTmProdGrenEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmProdGrenEpi_ = _uFunTmGrenEpi_
```

### `_uFunTmRespGrenEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespGrenEpi_ = _uFunTmGrenEpi_
```

### `_uFunTmRespGrenS_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmRespGrenS_ = _uFunTmGrenS_
```

### `_aVNUptMaxCrGrenHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrGrenHyp_ = _MAX_(0.0,_cVNUptMaxGren_ * _uFunTmProdGrenHyp_ * (_cNDGrenMax_ - _rNDGrenWHyp_) /(_cNDGrenMax_ - _cNDGrenMin_))
```

### `_ahNUptGrenHyp_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptGrenHyp_ = _aVNUptMaxCrGrenHyp_ / _cAffNUptGren_
```

### `_aVNUptGrenHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptGrenHyp_ = _oNDissWHyp_ * _aVNUptMaxCrGrenHyp_ /(_ahNUptGrenHyp_ + _oNDissWHyp_)
```

### `_wNUptGrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVNUptGrenHyp_ * _oDGrenWHyp_ _ENDIF_
```

### `_afNH4UptGrenHyp_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptGrenHyp_ = _oNH4WHyp_ * _oNO3WHyp_ /((_ahNUptGrenHyp_ + _oNH4WHyp_) *(_ahNUptGrenHyp_ + _oNO3WHyp_)) + _oNH4WHyp_ * _ahNUptGrenHyp_ /((_oNH4WHyp_ + _oNO3WHyp_) *(_ahNUptGrenHyp_ + _oNO3WHyp_))
```

### `_wNUptNH4GrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4GrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _afNH4UptGrenHyp_ * _wNUptGrenHyp_ _ENDIF_
```

### `_wNUptNO3GrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3GrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptGrenHyp_ - _wNUptNH4GrenHyp_ _ENDIF_
```

### `_uMuMaxTmGrenHyp_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmGrenHyp_ = _cMuMaxGren_ * _uFunTmProdGrenHyp_
```

### `_uMuMaxTmGrenEpi_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmGrenEpi_ = _cMuMaxGren_ * _uFunTmProdGrenEpi_
```

### `_aNLimGrenHyp_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimGrenHyp_ = _MAX_(0.0,(1.0 - _cNDGrenMin_ / _rNDGrenWHyp_) * _cNDGrenMax_ /(_cNDGrenMax_ - _cNDGrenMin_))
```

### `_aSiLimGrenHyp_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimGrenHyp_ = _oSiO2WHyp_ /(_hSiAssGren_ + _oSiO2WHyp_)
```

### `_aLLimGrenHyp_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimGrenHyp_ = _UseSteeleGren_ *(_EXP_(1.0) /(_aExtCoefHyp_ * _uDepthWHyp_) *(_EXP_(- _aLPARBotHyp_ /(_cLOptRefGren_ * _uFunTmProdGrenHyp_)) - _EXP_(- _uLPARSurfHyp_ /(_cLOptRefGren_ * _uFunTmProdGrenHyp_)))) +(1.0 - _UseSteeleGren_) *(1.0 /(_aExtCoefHyp_ * _uDepthWHyp_) * _LN_((1.0 + _uLPARSurfHyp_ / (_hLRefGren_ * _uFunTmProdGrenHyp_)) / (1.0 + _aLPARBotHyp_ /(_hLRefGren_ * _uFunTmProdGrenHyp_))))
```

### `_aMuTmLGrenHyp_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLGrenHyp_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimGrenHyp_ * _uMuMaxTmGrenHyp_
```

### `_rChDGrenHyp_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDGrenHyp_ = _cChDGrenMax_ -(_cChDGrenMax_ - _cChDGrenMin_) * _aLLimGrenHyp_
```

### `_oChlaGrenHyp_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaGrenHyp_ = _mgPerg_ * _rChDGrenHyp_ * _oDGrenWHyp_
```

### `_aExtChGrenHyp_`  [_m_^2*_gChl_^-1]
- **Description**: Specific_extinction_per_unit_chlorophyll-a
- **Equation**:

```
_aExtChGrenHyp_ = _cExtSpGren_ / _rChDGrenHyp_
```

### `_ukDRespTmGrenHyp_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmGrenHyp_ = _kDRespGren_ * _uFunTmRespGrenHyp_
```

### `_ukDRespTmGrenEpi_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmGrenEpi_ = _kDRespGren_ * _uFunTmRespGrenEpi_
```

### `_ukDRespTmGrenS_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmGrenS_ = _kDRespGren_ * _uFunTmRespGrenS_
```

### `_wDRespGrenWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukDRespTmGrenHyp_ * _oDGrenWHyp_ _ENDIF_
```

### `_ukLossTmGrenHyp_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmGrenHyp_ = _UseLoss_ * _kLossGren_ * _uFunTmLossHyp_
```

### `_ukLossTmGrenEpi_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmGrenEpi_ = _UseLoss_ * _kLossGren_ * _uFunTmLossEpi_
```

### `_wDLossGrenHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukLossTmGrenHyp_ * _oDGrenWHyp_ _ENDIF_
```

### `_wDMortGrenWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortGrenW_ * _oDGrenWHyp_ _ENDIF_
```

### `_uCorVSetGrenHyp_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetGrenHyp_ = (_cVSetGren_+ _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMHyp_ * _uFunTmSetHyp_
```

### `_tDSetGrenHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _uCorVSetGrenHyp_ * _oDGrenWHyp_ _ENDIF_
```

### `_tDResusGren_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_Algae
- **Equation**:

```
_tDResusGren_ = _aDGrenS_ /(_aDPhytS_+_NearZero_) * _tDResusPhytTot_
```

### `_tDRespGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_sediment_Algae
- **Equation**:

```
_tDRespGrenS_ = _ukDRespTmGrenS_ * _aDGrenS_
```

### `_tDMortGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_in_sed
- **Equation**:

```
_tDMortGrenS_ = _kMortGrenS_ * _aDGrenS_
```

### `_ukDDecGrenHyp_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecGrenHyp_ = _ukDRespTmGrenHyp_ + _ukLossTmGrenHyp_ + _kMortGrenW_ +(_uCorVSetGrenHyp_ * _uFunTmSetHyp_) / _uDepthWHyp_
```

### `_wPMortGrenWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortGrenW_ * _oPGrenWHyp_ _ENDIF_
```

### `_tPResusGren_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tPResusGren_ = _rPDGrenS_ * _tDResusGren_
```

### `_tPExcrGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_algae_in_sediment
- **Equation**:

```
_tPExcrGrenS_ = (2.0 * _rPDGrenS_) /(_cPDGrenMax_ + _rPDGrenS_) * _rPDGrenS_ * _tDRespGrenS_
```

### `_tPMortGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_of_algae_in_sediment
- **Equation**:

```
_tPMortGrenS_ = _kMortGrenS_ * _aPGrenS_
```

### `_wNExcrGrenWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (2.0 * _rNDGrenWHyp_) /(_cNDGrenMax_ + _rNDGrenWHyp_) * _rNDGrenWHyp_ * _wDRespGrenWHyp_ _ENDIF_
```

### `_wNLossGrenHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDGrenWHyp_ * _wDLossGrenHyp_ _ENDIF_
```

### `_wNMortGrenWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortGrenW_ * _oNGrenWHyp_ _ENDIF_
```

### `_tNSetGrenHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDGrenWHyp_ * _tDSetGrenHyp_ _ENDIF_
```

### `_tNResusGren_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tNResusGren_ = _rNDGrenS_ * _tDResusGren_
```

### `_tNExcrGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_algae_in_sediment
- **Equation**:

```
_tNExcrGrenS_ = (2.0 * _rNDGrenS_) /(_cNDGrenMax_ + _rNDGrenS_) * _rNDGrenS_ * _tDRespGrenS_
```

### `_tNMortGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_of_algae_in_sediment
- **Equation**:

```
_tNMortGrenS_ = _kMortGrenS_ * _aNGrenS_
```

### `_uCorVSetGrenEpi_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetGrenEpi_ = (_cVSetGren_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMEpi_ * _uFunTmSetEpi_
```

### `_tDSetGrenEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetGrenEpi_ = _uCorVSetGrenEpi_ * _oDGrenWEpi_
```

### `_rNDGrenWEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDGrenWEpi_ = _oNGrenWEpi_ /(_oDGrenWEpi_+_NearZero_)
```

### `_tNSetGrenEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetGrenEpi_ = _rNDGrenWEpi_ * _tDSetGrenEpi_
```

### `_rPDGrenWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDGrenWEpi_ = _oPGrenWEpi_ /(_oDGrenWEpi_+_NearZero_)
```

### `_tPSetGrenEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetGrenEpi_ = _rPDGrenWEpi_ * _tDSetGrenEpi_
```

### `_wNPrimGrenWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimGrenWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptGrenHyp_ - _wNExcrGrenWHyp_ - _wNLossGrenHyp_ - _wNMortGrenWHyp_ -(_tNSetGrenHyp_ -_tNSetGrenEpi_ - _tNResusGren_) / _uDepthWHyp_ _ENDIF_
```

### `_rPDGrenWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDGrenWHyp_ = _oPGrenWHyp_ /(_oDGrenWHyp_+_NearZero_)
```

### `_aVPUptMaxCrGrenHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrGrenHyp_ = _MAX_(0.0,_cVPUptMaxGren_ * _uFunTmProdGrenHyp_ *(_cPDGrenMax_ - _rPDGrenWHyp_) /(_cPDGrenMax_ - _cPDGrenMin_))
```

### `_aVPUptGrenHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptGrenHyp_ = _oPO4WHyp_ * _aVPUptMaxCrGrenHyp_ /(_aVPUptMaxCrGrenHyp_ / _cAffPUptGren_ + _oPO4WHyp_)
```

### `_wPUptGrenHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVPUptGrenHyp_ * _oDGrenWHyp_ _ENDIF_
```

### `_wPExcrGrenWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrGrenWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (2.0 *_rPDGrenWHyp_) /(_cPDGrenMax_ + _rPDGrenWHyp_) * _rPDGrenWHyp_ * _wDRespGrenWHyp_ _ENDIF_
```

### `_aPLimGrenHyp_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimGrenHyp_ = _MAX_(0.0,(1.0 - _cPDGrenMin_ / _rPDGrenWHyp_) * _cPDGrenMax_ /(_cPDGrenMax_ - _cPDGrenMin_))
```

### `_aNutLimGrenHyp_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimGrenHyp_ = _MIN_(_aPLimGrenHyp_,(_MIN_(_aNLimGrenHyp_,_aSiLimGrenHyp_)))
```

### `_aMuGrenHyp_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuGrenHyp_ = _aNutLimGrenHyp_ * _aMuTmLGrenHyp_
```

### `_wDAssGrenHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aMuGrenHyp_*_oDGrenWHyp_ _ENDIF_
```

### `_wDPrimGrenWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimGrenWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wDAssGrenHyp_ - _wDRespGrenWHyp_ - _wDLossGrenHyp_ - _wDMortGrenWHyp_ -(_tDSetGrenHyp_ -_tDSetGrenEpi_ - _tDResusGren_) / _uDepthWHyp_ _ENDIF_
```

### `_wPLossGrenHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDGrenWHyp_ * _wDLossGrenHyp_ _ENDIF_
```

### `_tPSetGrenHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetGrenHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDGrenWHyp_ * _tDSetGrenHyp_ _ENDIF_
```

### `_wPPrimGrenWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimGrenWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wPUptGrenHyp_ - _wPExcrGrenWHyp_ - _wPLossGrenHyp_ - _wPMortGrenWHyp_ -(_tPSetGrenHyp_ -_tPSetGrenEpi_ - _tPResusGren_) / _uDepthWHyp_ _ENDIF_
```

### `_aLLimGrenEpi_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimGrenEpi_ = _UseSteeleGren_ *(_EXP_(1.0) /(_aExtCoefEpi_ * _uDepthWEpi_) *(_EXP_(- _aLPARBotEpi_ /(_cLOptRefGren_ * _uFunTmProdGrenEpi_)) - _EXP_(- _aLPARBotSurf_ /(_cLOptRefGren_ * _uFunTmProdGrenEpi_)))) +(1.0 - _UseSteeleGren_) *(1.0 /(_aExtCoefEpi_ * _uDepthWEpi_) * _LN_((1.0 + _aLPARBotSurf_ / (_hLRefGren_ * _uFunTmProdGrenEpi_)) / (1.0 + _aLPARBotEpi_ /(_hLRefGren_ * _uFunTmProdGrenEpi_))))
```

### `_rChDGrenEpi_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDGrenEpi_ = _cChDGrenMax_ -(_cChDGrenMax_ - _cChDGrenMin_) * _aLLimGrenEpi_
```

### `_oChlaGrenEpi_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaGrenEpi_ = _mgPerg_ * _rChDGrenEpi_ * _oDGrenWEpi_
```

### `_aVPUptMaxCrGrenEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrGrenEpi_ = _MAX_(0.0,_cVPUptMaxGren_ * _uFunTmProdGrenEpi_ *(_cPDGrenMax_ - _rPDGrenWEpi_) /(_cPDGrenMax_ - _cPDGrenMin_))
```

### `_aVPUptGrenEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptGrenEpi_ = _oPO4WEpi_ * _aVPUptMaxCrGrenEpi_ /(_aVPUptMaxCrGrenEpi_ / _cAffPUptGren_ + _oPO4WEpi_)
```

### `_wPUptGrenEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptGrenEpi_ = _aVPUptGrenEpi_ * _oDGrenWEpi_
```

### `_aVNUptMaxCrGrenEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrGrenEpi_ = _MAX_(0.0,_cVNUptMaxGren_ * _uFunTmProdGrenEpi_ * (_cNDGrenMax_ - _rNDGrenWEpi_) /(_cNDGrenMax_ - _cNDGrenMin_))
```

### `_ahNUptGrenEpi_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptGrenEpi_ = _aVNUptMaxCrGrenEpi_ / _cAffNUptGren_
```

### `_aVNUptGrenEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptGrenEpi_ = _oNDissWEpi_ * _aVNUptMaxCrGrenEpi_ /(_ahNUptGrenEpi_ + _oNDissWEpi_)
```

### `_wNUptGrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptGrenEpi_ = _aVNUptGrenEpi_ * _oDGrenWEpi_
```

### `_afNH4UptGrenEpi_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptGrenEpi_ = _oNH4WEpi_ * _oNO3WEpi_ /((_ahNUptGrenEpi_ + _oNH4WEpi_) *(_ahNUptGrenEpi_ + _oNO3WEpi_)) + _oNH4WEpi_ * _ahNUptGrenEpi_ /((_oNH4WEpi_ + _oNO3WEpi_) *(_ahNUptGrenEpi_ + _oNO3WEpi_))
```

### `_wNUptNH4GrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4GrenEpi_ = _afNH4UptGrenEpi_ * _wNUptGrenEpi_
```

### `_wNUptNO3GrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3GrenEpi_ = _wNUptGrenEpi_ - _wNUptNH4GrenEpi_
```

### `_aPLimGrenEpi_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimGrenEpi_ = _MAX_(0.0,(1.0 - _cPDGrenMin_ / _rPDGrenWEpi_) * _cPDGrenMax_ /(_cPDGrenMax_ - _cPDGrenMin_))
```

### `_aNLimGrenEpi_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimGrenEpi_ = _MAX_(0.0,(1.0 - _cNDGrenMin_ / _rNDGrenWEpi_) * _cNDGrenMax_ /(_cNDGrenMax_ - _cNDGrenMin_))
```

### `_aSiLimGrenEpi_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimGrenEpi_ = _oSiO2WEpi_ /(_hSiAssGren_ + _oSiO2WEpi_)
```

### `_aMuTmLGrenEpi_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLGrenEpi_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimGrenEpi_ * _uMuMaxTmGrenEpi_
```

### `_aNutLimGrenEpi_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimGrenEpi_ = _MIN_(_aPLimGrenEpi_ , (_MIN_(_aNLimGrenEpi_,_aSiLimGrenEpi_)))
```

### `_aMuGrenEpi_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuGrenEpi_ = _aNutLimGrenEpi_ * _aMuTmLGrenEpi_
```

### `_wDAssGrenEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssGrenEpi_ = _aMuGrenEpi_*_oDGrenWEpi_
```

### `_aExtChGrenEpi_`  [_m_^2*_gChl_^-1]
- **Description**: Specific_extinction_per_unit_chlorophyll-a
- **Equation**:

```
_aExtChGrenEpi_ = _cExtSpGren_ / _rChDGrenEpi_
```

### `_wDRespGrenWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespGrenWEpi_ = _ukDRespTmGrenEpi_ * _oDGrenWEpi_
```

### `_wDLossGrenEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossGrenEpi_ = _ukLossTmGrenEpi_ * _oDGrenWEpi_
```

### `_wDMortGrenWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortGrenWEpi_ = _kMortGrenW_ * _oDGrenWEpi_
```

### `_ukDDecGrenEpi_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecGrenEpi_ = _ukDRespTmGrenEpi_ + _ukLossTmGrenEpi_ + _kMortGrenW_ +(_uCorVSetGrenEpi_ * _uFunTmSetEpi_) / _uDepthWEpi_
```

### `_wPExcrGrenWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrGrenWEpi_ = (2.0 *_rPDGrenWEpi_) /(_cPDGrenMax_ + _rPDGrenWEpi_) * _rPDGrenWEpi_ * _wDRespGrenWEpi_
```

### `_wPLossGrenEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossGrenEpi_ = _rPDGrenWEpi_ * _wDLossGrenEpi_
```

### `_wPMortGrenWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortGrenWEpi_ = _kMortGrenW_ * _oPGrenWEpi_
```

### `_wNExcrGrenWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrGrenWEpi_ = (2.0 * _rNDGrenWEpi_) /(_cNDGrenMax_ + _rNDGrenWEpi_) * _rNDGrenWEpi_ * _wDRespGrenWEpi_
```

### `_wNLossGrenEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossGrenEpi_ = _rNDGrenWEpi_ * _wDLossGrenEpi_
```

### `_wNMortGrenWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortGrenWEpi_ = _kMortGrenW_ * _oNGrenWEpi_
```

### `_wDPrimGrenWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimGrenWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wDAssGrenEpi_ - _wDRespGrenWEpi_ - _wDLossGrenEpi_ - _wDMortGrenWEpi_ -(_tDSetGrenEpi_ ) / _uDepthWEpi_ _ELSE_ _wDAssGrenEpi_ - _wDRespGrenWEpi_ - _wDLossGrenEpi_ - _wDMortGrenWEpi_ -(_tDSetGrenEpi_ - _tDResusGren_) / _uDepthWEpi_ _ENDIF_
```

### `_wPPrimGrenWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimGrenWEpi_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wPUptGrenEpi_ - _wPExcrGrenWEpi_ - _wPLossGrenEpi_ - _wPMortGrenWEpi_ -(_tPSetGrenEpi_ ) / _uDepthWEpi_ _ELSE_ _wPUptGrenEpi_ - _wPExcrGrenWEpi_ - _wPLossGrenEpi_ - _wPMortGrenWEpi_ -(_tPSetGrenEpi_ - _tPResusGren_) / _uDepthWEpi_ _ENDIF_
```

### `_wNPrimGrenWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimGrenWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wNUptGrenEpi_ - _wNExcrGrenWEpi_ - _wNLossGrenEpi_ - _wNMortGrenWEpi_ -(_tNSetGrenEpi_ ) / _uDepthWEpi_ _ELSE_ _wNUptGrenEpi_ - _wNExcrGrenWEpi_ - _wNLossGrenEpi_ - _wNMortGrenWEpi_ -(_tNSetGrenEpi_ - _tNResusGren_) / _uDepthWEpi_ _ENDIF_
```

### `_tDPrimGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tDPrimGrenS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tDSetGrenEpi_ - _tDResusGren_ - _tDMortGrenS_ - _tDRespGrenS_ _ELSE_ _tDSetGrenHyp_ - _tDResusGren_ - _tDMortGrenS_ - _tDRespGrenS_ _ENDIF_
```

### `_tPPrimGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tPPrimGrenS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tPSetGrenEpi_ - _tPResusGren_ - _tPMortGrenS_ - _tPExcrGrenS_ _ELSE_ _tPSetGrenHyp_ - _tPResusGren_ - _tPMortGrenS_ - _tPExcrGrenS_ _ENDIF_
```

### `_tNPrimGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tNPrimGrenS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tNSetGrenEpi_ - _tNResusGren_ - _tNMortGrenS_ - _tNExcrGrenS_ _ELSE_ _tNSetGrenHyp_ - _tNResusGren_ - _tNMortGrenS_ - _tNExcrGrenS_ _ENDIF_
```

## Phytoplankton_processes_Diatom  (110 equations)

### `_rPDDiatWHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDDiatWHyp_ = _oPDiatWHyp_ /(_oDDiatWHyp_+_NearZero_)
```

### `_rNDDiatWHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDDiatWHyp_ = _oNDiatWHyp_ /(_oDDiatWHyp_+_NearZero_)
```

### `_rPDDiatS_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDDiatS_ = _aPDiatS_ /(_aDDiatS_+_NearZero_)
```

### `_uFunTmDiatHyp_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmDiatHyp_ = _EXP_(-0.5/(_cSigTmDiat_*_cSigTmDiat_) *((_uTmHyp_-_cTmOptDiat_)*(_uTmHyp_-_cTmOptDiat_) - (_cTmRef_-_cTmOptDiat_)*(_cTmRef_-_cTmOptDiat_)))
```

### `_rNDDiatS_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDDiatS_ = _aNDiatS_ /(_aDDiatS_+_NearZero_)
```

### `_uFunTmDiatEpi_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmDiatEpi_ = _EXP_(-0.5/(_cSigTmDiat_*_cSigTmDiat_) *((_uTmEpi_-_cTmOptDiat_)*(_uTmEpi_-_cTmOptDiat_) - (_cTmRef_-_cTmOptDiat_)*(_cTmRef_-_cTmOptDiat_)))
```

### `_uFunTmDiatS_`  [0]
- **Description**: Temperature_function_of_Algae
- **Equation**:

```
_uFunTmDiatS_ = _EXP_(-0.5/(_cSigTmDiat_*_cSigTmDiat_) *((_uTmBot_-_cTmOptDiat_)*(_uTmBot_-_cTmOptDiat_) - (_cTmRef_-_cTmOptDiat_)*(_cTmRef_-_cTmOptDiat_)))
```

### `_uFunTmProdDiatHyp_`  [0]
- **Description**: Temperature_function_production_of_Algae
- **Equation**:

```
_uFunTmProdDiatHyp_ = _uFunTmDiatHyp_
```

### `_uFunTmRespDiatHyp_`  [0]
- **Description**: Temperature_function_respiration_of_Algae
- **Equation**:

```
_uFunTmRespDiatHyp_ = _uFunTmDiatHyp_
```

### `_uFunTmProdDiatEpi_`  [0]
- **Description**: Temperature_function_production_of_Algae
- **Equation**:

```
_uFunTmProdDiatEpi_ = _uFunTmDiatEpi_
```

### `_uFunTmRespDiatEpi_`  [0]
- **Description**: Temperature_function_respiration_of_Algae
- **Equation**:

```
_uFunTmRespDiatEpi_ = _uFunTmDiatEpi_
```

### `_uFunTmRespDiatS_`  [0]
- **Description**: Temperature_function_respiration_of_Algae
- **Equation**:

```
_uFunTmRespDiatS_ = _uFunTmDiatS_
```

### `_aVPUptMaxCrDiatHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrDiatHyp_ = _MAX_(0.0,_cVPUptMaxDiat_ * _uFunTmProdDiatHyp_ *(_cPDDiatMax_ - _rPDDiatWHyp_) /(_cPDDiatMax_ - _cPDDiatMin_))
```

### `_aVPUptDiatHyp_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptDiatHyp_ = _oPO4WHyp_ * _aVPUptMaxCrDiatHyp_ /(_aVPUptMaxCrDiatHyp_ / _cAffPUptDiat_ + _oPO4WHyp_)
```

### `_wPUptDiatHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVPUptDiatHyp_ * _oDDiatWHyp_ _ENDIF_
```

### `_aVNUptMaxCrDiatHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrDiatHyp_ = _MAX_(0.0,_cVNUptMaxDiat_ * _uFunTmProdDiatHyp_ * (_cNDDiatMax_ - _rNDDiatWHyp_) /(_cNDDiatMax_ - _cNDDiatMin_))
```

### `_ahNUptDiatHyp_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptDiatHyp_ = _aVNUptMaxCrDiatHyp_ / _cAffNUptDiat_
```

### `_aVNUptDiatHyp_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptDiatHyp_ = _oNDissWHyp_ * _aVNUptMaxCrDiatHyp_ /(_ahNUptDiatHyp_ + _oNDissWHyp_)
```

### `_wNUptDiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aVNUptDiatHyp_ * _oDDiatWHyp_ _ENDIF_
```

### `_afNH4UptDiatHyp_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptDiatHyp_ = _oNH4WHyp_ * _oNO3WHyp_ /((_ahNUptDiatHyp_ + _oNH4WHyp_) *(_ahNUptDiatHyp_ + _oNO3WHyp_)) + _oNH4WHyp_ * _ahNUptDiatHyp_ /((_oNH4WHyp_ + _oNO3WHyp_) *(_ahNUptDiatHyp_ + _oNO3WHyp_))
```

### `_wNUptNH4DiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4DiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _afNH4UptDiatHyp_ * _wNUptDiatHyp_ _ENDIF_
```

### `_wNUptNO3DiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3DiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptDiatHyp_ - _wNUptNH4DiatHyp_ _ENDIF_
```

### `_uMuMaxTmDiatHyp_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmDiatHyp_ = _cMuMaxDiat_ * _uFunTmProdDiatHyp_
```

### `_uMuMaxTmDiatEpi_`  [_d_^-1]
- **Description**: Max_growth_rate_of_Algae_at_ambient_temperature
- **Equation**:

```
_uMuMaxTmDiatEpi_ = _cMuMaxDiat_ * _uFunTmProdDiatEpi_
```

### `_aPLimDiatHyp_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimDiatHyp_ = _MAX_(0.0,(1.0 - _cPDDiatMin_ / _rPDDiatWHyp_) * _cPDDiatMax_ /(_cPDDiatMax_ - _cPDDiatMin_))
```

### `_aNLimDiatHyp_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimDiatHyp_ = _MAX_(0.0,(1.0 - _cNDDiatMin_ / _rNDDiatWHyp_) * _cNDDiatMax_ /(_cNDDiatMax_ - _cNDDiatMin_))
```

### `_aSiLimDiatHyp_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimDiatHyp_ = _oSiO2WHyp_ /(_hSiAssDiat_ + _oSiO2WHyp_)
```

### `_aLLimDiatHyp_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimDiatHyp_ = _UseSteeleDiat_ *(_EXP_(1.0) /(_aExtCoefHyp_ * _uDepthWHyp_) *(_EXP_(- _aLPARBotHyp_ /(_cLOptRefDiat_ * _uFunTmProdDiatHyp_)) - _EXP_(- _uLPARSurfHyp_ /(_cLOptRefDiat_ * _uFunTmProdDiatHyp_)))) +(1.0 - _UseSteeleDiat_) *(1.0 /(_aExtCoefHyp_ * _uDepthWHyp_) * _LN_((1.0 + _uLPARSurfHyp_ / (_hLRefDiat_ * _uFunTmProdDiatHyp_)) / (1.0 + _aLPARBotHyp_ /(_hLRefDiat_ * _uFunTmProdDiatHyp_))))
```

### `_aMuTmLDiatHyp_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLDiatHyp_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimDiatHyp_ * _uMuMaxTmDiatHyp_
```

### `_aNutLimDiatHyp_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimDiatHyp_ = _MIN_(_aPLimDiatHyp_,(_MIN_(_aNLimDiatHyp_,_aSiLimDiatHyp_)))
```

### `_aMuDiatHyp_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuDiatHyp_ = _aNutLimDiatHyp_ * _aMuTmLDiatHyp_
```

### `_wDAssDiatHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aMuDiatHyp_*_oDDiatWHyp_ _ENDIF_
```

### `_rChDDiatHyp_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDDiatHyp_ = _cChDDiatMax_ -(_cChDDiatMax_ - _cChDDiatMin_) * _aLLimDiatHyp_
```

### `_oChlaDiatHyp_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaDiatHyp_ = _mgPerg_ * _rChDDiatHyp_ * _oDDiatWHyp_
```

### `_aExtChDiatHyp_`  [_m_^2*_gChl_^-1]
- **Description**: Specific_extinction_per_unit_chlorophyll-a
- **Equation**:

```
_aExtChDiatHyp_ = _cExtSpDiat_ / _rChDDiatHyp_
```

### `_ukDRespTmDiatHyp_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmDiatHyp_ = _kDRespDiat_ * _uFunTmRespDiatHyp_
```

### `_ukDRespTmDiatEpi_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmDiatEpi_ = _kDRespDiat_ * _uFunTmRespDiatEpi_
```

### `_ukDRespTmDiatS_`  [_d_^-1]
- **Description**: Temp_corrected_respiration_constant_of_Algae
- **Equation**:

```
_ukDRespTmDiatS_ = _kDRespDiat_ * _uFunTmRespDiatS_
```

### `_wDRespDiatWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukDRespTmDiatHyp_ * _oDDiatWHyp_ _ENDIF_
```

### `_ukLossTmDiatHyp_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmDiatHyp_ = _UseLoss_ * _kLossDiat_ * _uFunTmLossHyp_
```

### `_ukLossTmDiatEpi_`  [_d_^-1]
- **Description**: Daily_grazing_on_Algae
- **Equation**:

```
_ukLossTmDiatEpi_ = _UseLoss_ * _kLossDiat_ * _uFunTmLossEpi_
```

### `_wDLossDiatHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _ukLossTmDiatHyp_ * _oDDiatWHyp_ _ENDIF_
```

### `_wDMortDiatWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortDiatW_ * _oDDiatWHyp_ _ENDIF_
```

### `_uCorVSetDiatHyp_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetDiatHyp_ = (_cVSetDiat_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_) * _aFunTauSetOMHyp_ * _uFunTmSetHyp_
```

### `_tDSetDiatHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _uCorVSetDiatHyp_ * _oDDiatWHyp_ _ENDIF_
```

### `_tDResusDiat_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_Algae
- **Equation**:

```
_tDResusDiat_ = _aDDiatS_ /(_aDPhytS_+_NearZero_) * _tDResusPhytTot_
```

### `_tDRespDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_sediment_Algae
- **Equation**:

```
_tDRespDiatS_ = _ukDRespTmDiatS_ * _aDDiatS_
```

### `_tDMortDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_in_sed
- **Equation**:

```
_tDMortDiatS_ = _kMortDiatS_ * _aDDiatS_
```

### `_ukDDecDiatHyp_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecDiatHyp_ = _ukDRespTmDiatHyp_ + _ukLossTmDiatHyp_ + _kMortDiatW_ +(_uCorVSetDiatHyp_ * _uFunTmSetHyp_) / _uDepthWHyp_
```

### `_wPExcrDiatWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (2.0 * _rPDDiatWHyp_) /(_cPDDiatMax_ + _rPDDiatWHyp_) * _rPDDiatWHyp_ * _wDRespDiatWHyp_ _ENDIF_
```

### `_wPLossDiatHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDDiatWHyp_ * _wDLossDiatHyp_ _ENDIF_
```

### `_wPMortDiatWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortDiatW_ * _oPDiatWHyp_ _ENDIF_
```

### `_tPSetDiatHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rPDDiatWHyp_ * _tDSetDiatHyp_ _ENDIF_
```

### `_tPResusDiat_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tPResusDiat_ = _rPDDiatS_ * _tDResusDiat_
```

### `_tPExcrDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_algae_in_sediment
- **Equation**:

```
_tPExcrDiatS_ = (2.0 * _rPDDiatS_) /(_cPDDiatMax_ + _rPDDiatS_) * _rPDDiatS_ * _tDRespDiatS_
```

### `_tPMortDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_mortality_of_algae_in_sediment
- **Equation**:

```
_tPMortDiatS_ = _kMortDiatS_ * _aPDiatS_
```

### `_wNExcrDiatWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ (2.0 * _rNDDiatWHyp_) /(_cNDDiatMax_ + _rNDDiatWHyp_) * _rNDDiatWHyp_ * _wDRespDiatWHyp_ _ENDIF_
```

### `_wNLossDiatHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDDiatWHyp_ * _wDLossDiatHyp_ _ENDIF_
```

### `_wNMortDiatWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortDiatWHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortDiatW_ * _oNDiatWHyp_ _ENDIF_
```

### `_tNSetDiatHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetDiatHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _rNDDiatWHyp_ * _tDSetDiatHyp_ _ENDIF_
```

### `_tNResusDiat_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Resuspension_of_algae
- **Equation**:

```
_tNResusDiat_ = _rNDDiatS_ * _tDResusDiat_
```

### `_tNExcrDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_algae_in_sediment
- **Equation**:

```
_tNExcrDiatS_ = (2.0 * _rNDDiatS_) /(_cNDDiatMax_ + _rNDDiatS_) * _rNDDiatS_ * _tDRespDiatS_
```

### `_tNMortDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_mortality_of_algae_in_sediment
- **Equation**:

```
_tNMortDiatS_ = _kMortDiatS_ * _aNDiatS_
```

### `_uCorVSetDiatEpi_`  [_m_*_d_^-1]
- **Description**: Corrected_sedimentation_velocity_of_Algae
- **Equation**:

```
_uCorVSetDiatEpi_ = (_cVSetDiat_ + _uQOutInf_ /_mmPerm_ - _uQInSeep_ / _mmPerm_)  * _aFunTauSetOMEpi_ * _uFunTmSetEpi_
```

### `_tDSetDiatEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Sedimentation_flux_of_Algae
- **Equation**:

```
_tDSetDiatEpi_ = _uCorVSetDiatEpi_ * _oDDiatWEpi_
```

### `_rPDDiatWEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_Algae
- **Equation**:

```
_rPDDiatWEpi_ = _oPDiatWEpi_ /(_oDDiatWEpi_+_NearZero_)
```

### `_tPSetDiatEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tPSetDiatEpi_ = _rPDDiatWEpi_ * _tDSetDiatEpi_
```

### `_rNDDiatWEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_Algae
- **Equation**:

```
_rNDDiatWEpi_ = _oNDiatWEpi_ /(_oDDiatWEpi_+_NearZero_)
```

### `_tNSetDiatEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sedimentation
- **Equation**:

```
_tNSetDiatEpi_ = _rNDDiatWEpi_ * _tDSetDiatEpi_
```

### `_wDPrimDiatWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimDiatWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wDAssDiatHyp_ - _wDRespDiatWHyp_ - _wDLossDiatHyp_ - _wDMortDiatWHyp_ -(_tDSetDiatHyp_ - _tDSetDiatEpi_ - _tDResusDiat_) / _uDepthWHyp_ _ENDIF_
```

### `_wPPrimDiatWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimDiatWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wPUptDiatHyp_ - _wPExcrDiatWHyp_ - _wPLossDiatHyp_ - _wPMortDiatWHyp_ -(_tPSetDiatHyp_ -_tPSetDiatEpi_ - _tPResusDiat_) / _uDepthWHyp_ _ENDIF_
```

### `_wNPrimDiatWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimDiatWHyp_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNUptDiatHyp_ - _wNExcrDiatWHyp_ - _wNLossDiatHyp_ - _wNMortDiatWHyp_ -(_tNSetDiatHyp_ - _tNSetDiatEpi_ - _tNResusDiat_) / _uDepthWHyp_ _ENDIF_
```

### `_rChDBlueSurf_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDBlueSurf_ = _cChDBlueMax_ -(_cChDBlueMax_ - _cChDBlueMin_) * _aLLimBlueSurf_
```

### `_aLLimDiatEpi_`  [0]
- **Description**: Light_function
- **Equation**:

```
_aLLimDiatEpi_ = _UseSteeleDiat_ *(_EXP_(1.0) /(_aExtCoefEpi_ * _uDepthWEpi_) *(_EXP_(- _aLPARBotEpi_ /(_cLOptRefDiat_ * _uFunTmProdDiatEpi_)) - _EXP_(- _aLPARBotSurf_ /(_cLOptRefDiat_ * _uFunTmProdDiatEpi_)))) +(1.0 - _UseSteeleDiat_) *(1.0 /(_aExtCoefEpi_ * _uDepthWEpi_) * _LN_((1.0 + _aLPARBotSurf_ / (_hLRefDiat_ * _uFunTmProdDiatEpi_)) / (1.0 + _aLPARBotEpi_ /(_hLRefDiat_ * _uFunTmProdDiatEpi_))))
```

### `_rChDDiatEpi_`  [_gChl_*_gDW_^-1]
- **Description**: Chlorophyll-a/DW_ratio_Algae
- **Equation**:

```
_rChDDiatEpi_ = _cChDDiatMax_ -(_cChDDiatMax_ - _cChDDiatMin_) * _aLLimDiatEpi_
```

### `_oChlaDiatEpi_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_conc
- **Equation**:

```
_oChlaDiatEpi_ = _mgPerg_ * _rChDDiatEpi_ * _oDDiatWEpi_
```

### `_aVPUptMaxCrDiatEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_P_uptake_rate_of_Algae_corrected_for_P/D_ratio
- **Equation**:

```
_aVPUptMaxCrDiatEpi_ = _MAX_(0.0,_cVPUptMaxDiat_ * _uFunTmProdDiatEpi_ *(_cPDDiatMax_ - _rPDDiatWEpi_) /(_cPDDiatMax_ - _cPDDiatMin_))
```

### `_aVPUptDiatEpi_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate_of_Algae
- **Equation**:

```
_aVPUptDiatEpi_ = _oPO4WEpi_ * _aVPUptMaxCrDiatEpi_ /(_aVPUptMaxCrDiatEpi_ / _cAffPUptDiat_ + _oPO4WEpi_)
```

### `_wPUptDiatEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_uptake_Algae
- **Equation**:

```
_wPUptDiatEpi_ = _aVPUptDiatEpi_ * _oDDiatWEpi_
```

### `_aVNUptMaxCrDiatEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Maximum_N_uptake_rate_of_Algae_corrected_for_N/D_ratio
- **Equation**:

```
_aVNUptMaxCrDiatEpi_ = _MAX_(0.0,_cVNUptMaxDiat_ * _uFunTmProdDiatEpi_ * (_cNDDiatMax_ - _rNDDiatWEpi_) /(_cNDDiatMax_ - _cNDDiatMin_))
```

### `_ahNUptDiatEpi_`  [_gN_*_m_^-3]
- **Description**: Half-sat_dissolved_nitrogen_in_water_for_uptake_by_Algae
- **Equation**:

```
_ahNUptDiatEpi_ = _aVNUptMaxCrDiatEpi_ / _cAffNUptDiat_
```

### `_aVNUptDiatEpi_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate_of_Algae
- **Equation**:

```
_aVNUptDiatEpi_ = _oNDissWEpi_ * _aVNUptMaxCrDiatEpi_ /(_ahNUptDiatEpi_ + _oNDissWEpi_)
```

### `_wNUptDiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_uptake_Algae
- **Equation**:

```
_wNUptDiatEpi_ = _aVNUptDiatEpi_ * _oDDiatWEpi_
```

### `_afNH4UptDiatEpi_`  [0]
- **Description**: Fraction_ammonium_uptake_by_Algae
- **Equation**:

```
_afNH4UptDiatEpi_ = _oNH4WEpi_ * _oNO3WEpi_ /((_ahNUptDiatEpi_ + _oNH4WEpi_) *(_ahNUptDiatEpi_ + _oNO3WEpi_)) + _oNH4WEpi_ * _ahNUptDiatEpi_ /((_oNH4WEpi_ + _oNO3WEpi_) *(_ahNUptDiatEpi_ + _oNO3WEpi_))
```

### `_wNUptNH4DiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_uptake_by_Algae
- **Equation**:

```
_wNUptNH4DiatEpi_ = _afNH4UptDiatEpi_ * _wNUptDiatEpi_
```

### `_wNUptNO3DiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_uptake_by_Algae
- **Equation**:

```
_wNUptNO3DiatEpi_ = _wNUptDiatEpi_ - _wNUptNH4DiatEpi_
```

### `_aPLimDiatEpi_`  [0]
- **Description**: Droop_function(P)_for_Algae
- **Equation**:

```
_aPLimDiatEpi_ = _MAX_(0.0,(1.0 - _cPDDiatMin_ / _rPDDiatWEpi_) * _cPDDiatMax_ /(_cPDDiatMax_ - _cPDDiatMin_))
```

### `_aNLimDiatEpi_`  [0]
- **Description**: Droop_function(N)_for_Algae
- **Equation**:

```
_aNLimDiatEpi_ = _MAX_(0.0,(1.0 - _cNDDiatMin_ / _rNDDiatWEpi_) * _cNDDiatMax_ /(_cNDDiatMax_ - _cNDDiatMin_))
```

### `_aSiLimDiatEpi_`  [0]
- **Description**: Silica_dependence_of_growth_rate
- **Equation**:

```
_aSiLimDiatEpi_ = _oSiO2WEpi_ /(_hSiAssDiat_ + _oSiO2WEpi_)
```

### `_aMuTmLDiatEpi_`  [_d_^-1]
- **Description**: Growth_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuTmLDiatEpi_ = _ufDay_ *(1.0 - _afCovSurfVeg_) * _aLLimDiatEpi_ * _uMuMaxTmDiatEpi_
```

### `_aNutLimDiatEpi_`  [0]
- **Description**: Nutrient_limitation_function_of_Algae
- **Equation**:

```
_aNutLimDiatEpi_ = _MIN_(_aPLimDiatEpi_ , (_MIN_(_aNLimDiatEpi_,_aSiLimDiatEpi_)))
```

### `_aMuDiatEpi_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuDiatEpi_ = _aNutLimDiatEpi_ * _aMuTmLDiatEpi_
```

### `_wDAssDiatEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_Algae
- **Equation**:

```
_wDAssDiatEpi_ = _aMuDiatEpi_*_oDDiatWEpi_
```

### `_aExtChDiatEpi_`  [_m_^2*_gChl_^-1]
- **Description**: Specific_extinction_per_unit_chlorophyll-a
- **Equation**:

```
_aExtChDiatEpi_ = _cExtSpDiat_ / _rChDDiatEpi_
```

### `_wDRespDiatWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Respiration_of_Algae_in_water
- **Equation**:

```
_wDRespDiatWEpi_ = _ukDRespTmDiatEpi_ * _oDDiatWEpi_
```

### `_wDLossDiatEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wDLossDiatEpi_ = _ukLossTmDiatEpi_ * _oDDiatWEpi_
```

### `_wDMortDiatWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Mortality_in_water
- **Equation**:

```
_wDMortDiatWEpi_ = _kMortDiatW_ * _oDDiatWEpi_
```

### `_ukDDecDiatEpi_`  [_d_^-1]
- **Description**: Total_loss_rate_of_algae_in_water(excl_dilution)
- **Equation**:

```
_ukDDecDiatEpi_ = _ukDRespTmDiatEpi_ + _ukLossTmDiatEpi_ + _kMortDiatW_ +(_uCorVSetDiatEpi_ * _uFunTmSetEpi_) / _uDepthWEpi_
```

### `_wPExcrDiatWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion_Algae_in_water
- **Equation**:

```
_wPExcrDiatWEpi_ = (2.0 * _rPDDiatWEpi_) /(_cPDDiatMax_ + _rPDDiatWEpi_) * _rPDDiatWEpi_ * _wDRespDiatWEpi_
```

### `_wPLossDiatEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wPLossDiatEpi_ = _rPDDiatWEpi_ * _wDLossDiatEpi_
```

### `_wPMortDiatWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wPMortDiatWEpi_ = _kMortDiatW_ * _oPDiatWEpi_
```

### `_wNExcrDiatWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion_Algae_in_water
- **Equation**:

```
_wNExcrDiatWEpi_ = (2.0 * _rNDDiatWEpi_) /(_cNDDiatMax_ + _rNDDiatWEpi_) * _rNDDiatWEpi_ * _wDRespDiatWEpi_
```

### `_wNLossDiatEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Algae_grazing_loss
- **Equation**:

```
_wNLossDiatEpi_ = _rNDDiatWEpi_ * _wDLossDiatEpi_
```

### `_wNMortDiatWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality_Algae_in_water
- **Equation**:

```
_wNMortDiatWEpi_ = _kMortDiatW_ * _oNDiatWEpi_
```

### `_wDPrimDiatWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_algae_in_water
- **Equation**:

```
_wDPrimDiatWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wDAssDiatEpi_ - _wDRespDiatWEpi_ - _wDLossDiatEpi_ - _wDMortDiatWEpi_ -(_tDSetDiatEpi_ ) / _uDepthWEpi_ _ELSE_ _wDAssDiatEpi_ - _wDRespDiatWEpi_ - _wDLossDiatEpi_ - _wDMortDiatWEpi_ -(_tDSetDiatEpi_ - _tDResusDiat_) / _uDepthWEpi_ _ENDIF_
```

### `_wPPrimDiatWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wPPrimDiatWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wPUptDiatEpi_ - _wPExcrDiatWEpi_ - _wPLossDiatEpi_ - _wPMortDiatWEpi_ -(_tPSetDiatEpi_ ) / _uDepthWEpi_ _ELSE_ _wPUptDiatEpi_ - _wPExcrDiatWEpi_ - _wPLossDiatEpi_ - _wPMortDiatWEpi_ -(_tPSetDiatEpi_ - _tPResusDiat_) / _uDepthWEpi_ _ENDIF_
```

### `_wNPrimDiatWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_PRIM_flux_to_Algae
- **Equation**:

```
_wNPrimDiatWEpi_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _wNUptDiatEpi_ - _wNExcrDiatWEpi_ - _wNLossDiatEpi_ - _wNMortDiatWEpi_ -(_tNSetDiatEpi_ ) / _uDepthWEpi_ _ELSE_ _wNUptDiatEpi_ - _wNExcrDiatWEpi_ - _wNLossDiatEpi_ - _wNMortDiatWEpi_ -(_tNSetDiatEpi_ - _tNResusDiat_) / _uDepthWEpi_ _ENDIF_
```

### `_tDPrimDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tDPrimDiatS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tDSetDiatEpi_ - _tDResusDiat_ - _tDMortDiatS_ - _tDRespDiatS_ _ELSE_ _tDSetDiatHyp_ - _tDResusDiat_ - _tDMortDiatS_ - _tDRespDiatS_ _ENDIF_
```

### `_tPPrimDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tPPrimDiatS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tPSetDiatEpi_ - _tPResusDiat_ - _tPMortDiatS_ - _tPExcrDiatS_ _ELSE_ _tPSetDiatHyp_ - _tPResusDiat_ - _tPMortDiatS_ - _tPExcrDiatS_ _ENDIF_
```

### `_tNPrimDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_flux_from_PRIM_module_to_sediment_Algae
- **Equation**:

```
_tNPrimDiatS_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_) _THEN_ _tNSetDiatEpi_ - _tNResusDiat_ - _tNMortDiatS_ - _tNExcrDiatS_ _ELSE_ _tNSetDiatHyp_ - _tNResusDiat_ - _tNMortDiatS_ - _tNExcrDiatS_ _ENDIF_
```

## Phytoplankton_processes_total  (62 equations)

### `_oChlaHyp_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a
- **Equation**:

```
_oChlaHyp_ = _oChlaDiatHyp_ + _oChlaGrenHyp_ + _oChlaBlueHyp_
```

### `_wDRespPhytWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_respiration_in_water
- **Equation**:

```
_wDRespPhytWHyp_ = _wDRespDiatWHyp_ + _wDRespGrenWHyp_ + _wDRespBlueWHyp_
```

### `_wDMortPhytWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_mortality_in_water
- **Equation**:

```
_wDMortPhytWHyp_ = _wDMortDiatWHyp_ + _wDMortGrenWHyp_ + _wDMortBlueWHyp_
```

### `_wDLossPhytHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_phytoplankton_grazing_loss
- **Equation**:

```
_wDLossPhytHyp_ = _wDLossDiatHyp_ + _wDLossGrenHyp_ + _wDLossBlueHyp_
```

### `_wPMortPhytWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_mortality_phytoplankton_in_water
- **Equation**:

```
_wPMortPhytWHyp_ = _wPMortDiatWHyp_ + _wPMortGrenWHyp_ + _wPMortBlueWHyp_
```

### `_tPResusPhyt_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_resuspension_of_phytoplankton_in_hypolimnion_water
- **Equation**:

```
_tPResusPhyt_ = _tPResusDiat_ + _tPResusGren_ + _tPResusBlue_
```

### `_wNUptPhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_uptake_phytoplankton
- **Equation**:

```
_wNUptPhytHyp_ = _wNUptDiatHyp_ + _wNUptGrenHyp_ + _wNUptBlueHyp_
```

### `_wNUptNH4PhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_ammonium-N_uptake_phytoplankton
- **Equation**:

```
_wNUptNH4PhytHyp_ = _wNUptNH4DiatHyp_ + _wNUptNH4GrenHyp_ + _wNUptNH4BlueHyp_
```

### `_wNUptNO3PhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_nitrate-N_uptake_phytoplankton
- **Equation**:

```
_wNUptNO3PhytHyp_ = _wNUptNO3DiatHyp_ + _wNUptNO3GrenHyp_ + _wNUptNO3BlueHyp_
```

### `_wNExcrPhytWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_excretion_phytoplankton_in_water
- **Equation**:

```
_wNExcrPhytWHyp_ = _wNExcrDiatWHyp_ + _wNExcrGrenWHyp_ + _wNExcrBlueWHyp_
```

### `_wNMortPhytWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_mortality_phytoplankton_in_water
- **Equation**:

```
_wNMortPhytWHyp_ = _wNMortDiatWHyp_ + _wNMortGrenWHyp_ + _wNMortBlueWHyp_
```

### `_tNResusPhyt_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_resuspension_of_phytoplankton_in_hypolimnion_water
- **Equation**:

```
_tNResusPhyt_ = _tNResusDiat_ + _tNResusGren_ + _tNResusBlue_
```

### `_wNLossPhytHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_grazing_loss
- **Equation**:

```
_wNLossPhytHyp_ = _wNLossDiatHyp_ + _wNLossGrenHyp_ + _wNLossBlueHyp_
```

### `_tDRespPhytS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_algae_on_bottom
- **Equation**:

```
_tDRespPhytS_ = _tDRespDiatS_ + _tDRespGrenS_ + _tDRespBlueS_
```

### `_tDMortPhytS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_algae_on_bottom
- **Equation**:

```
_tDMortPhytS_ = _tDMortDiatS_ + _tDMortGrenS_ + _tDMortBlueS_
```

### `_tPExcrPhytS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_excretion_sediment_phytoplankton
- **Equation**:

```
_tPExcrPhytS_ = _tPExcrDiatS_ + _tPExcrGrenS_ + _tPExcrBlueS_
```

### `_tPMortPhytS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_phytoplankton_mortality
- **Equation**:

```
_tPMortPhytS_ = _tPMortDiatS_ + _tPMortGrenS_ + _tPMortBlueS_
```

### `_tNExcrPhytS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_excretion_sediment_phytoplankton
- **Equation**:

```
_tNExcrPhytS_ = _tNExcrDiatS_ + _tNExcrGrenS_ + _tNExcrBlueS_
```

### `_tNMortPhytS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_phytoplankton_mortality
- **Equation**:

```
_tNMortPhytS_ = _tNMortDiatS_ + _tNMortGrenS_ + _tNMortBlueS_
```

### `_aChlaBlueSurf_`  [_mgChl_*_m_^-2]
- **Description**: Total_bluegreen_chlorophyll-a_on_surface
- **Equation**:

```
_aChlaBlueSurf_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _mgPerg_ * _rChDBlueSurf_ * _aDBlueSurf_ _ENDIF_
```

### `_oChlaBlueW_`  [_mgChl_*_m_^-3]
- **Description**: Total_bluegreen_chlorophyll-a_in_water
- **Equation**:

```
_oChlaBlueW_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_oChlaBlueEpi_ * _uDepthWEpi_ + _oChlaBlueHyp_ * _uDepthWHyp_) / _uDepthW_ _ELSE_ (_oChlaBlueEpi_ * _uDepthWEpi_) / _uDepthW_ _ENDIF_
```

### `_oChlaBlue_`  [_mgChl_*_m_^-3]
- **Description**: Total_bluegreen_chlorophyll-a
- **Equation**:

```
_oChlaBlue_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_oChlaBlueEpi_ * _uDepthWEpi_ + _oChlaBlueHyp_ * _uDepthWHyp_ + _aChlaBlueSurf_) / _uDepthW_ _ELSE_ (_oChlaBlueEpi_ * _uDepthWEpi_ + _aChlaBlueSurf_ ) / _uDepthW_ _ENDIF_
```

### `_wPUptPhytHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_uptake_phytoplankton
- **Equation**:

```
_wPUptPhytHyp_ = _wPUptDiatHyp_ + _wPUptGrenHyp_ + _wPUptBlueHyp_
```

### `_wPExcrPhytWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_excretion_phytoplankton_in_water
- **Equation**:

```
_wPExcrPhytWHyp_ = _wPExcrDiatWHyp_ + _wPExcrGrenWHyp_ + _wPExcrBlueWHyp_
```

### `_wDAssPhytHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_growth
- **Equation**:

```
_wDAssPhytHyp_ = _wDAssDiatHyp_ + _wDAssGrenHyp_ + _wDAssBlueHyp_
```

### `_wPLossPhytHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_grazing_loss
- **Equation**:

```
_wPLossPhytHyp_ = _wPLossDiatHyp_ + _wPLossGrenHyp_ + _wPLossBlueHyp_
```

### `_tDSetPhytHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_phytoplankton_sedimentation
- **Equation**:

```
_tDSetPhytHyp_ = _tDSetDiatHyp_ + _tDSetGrenHyp_ + _tDSetBlueHyp_
```

### `_wDPrimPhytWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wDPrimPhytWHyp_ = _wDPrimDiatWHyp_ + _wDPrimGrenWHyp_ + _wDPrimBlueWHyp_
```

### `_tPSetPhytHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_sedimentation_of_algae
- **Equation**:

```
_tPSetPhytHyp_ = _tPSetDiatHyp_ + _tPSetGrenHyp_ + _tPSetBlueHyp_
```

### `_wPPrimPhytWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wPPrimPhytWHyp_ = _wPPrimDiatWHyp_ + _wPPrimGrenWHyp_ + _wPPrimBlueWHyp_
```

### `_tNSetPhytHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_sedimentation_of_algae
- **Equation**:

```
_tNSetPhytHyp_ = _tNSetDiatHyp_ + _tNSetGrenHyp_ + _tNSetBlueHyp_
```

### `_wNPrimPhytWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wNPrimPhytWHyp_ = _wNPrimDiatWHyp_ + _wNPrimGrenWHyp_ + _wNPrimBlueWHyp_
```

### `_oChlaEpi_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a
- **Equation**:

```
_oChlaEpi_ = _oChlaDiatEpi_ + _oChlaGrenEpi_ + _oChlaBlueEpi_
```

### `_oChla_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a
- **Equation**:

```
_oChla_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_oChlaEpi_ * _uDepthWEpi_ + _oChlaHyp_ * _uDepthWHyp_ + _aChlaBlueSurf_) / _uDepthW_ _ELSE_ (_oChlaEpi_ * _uDepthWEpi_+ _aChlaBlueSurf_ ) / _uDepthW_ _ENDIF_
```

### `_oChlaW_`  [_mgChl_*_m_^-3]
- **Description**: Chlorophyll-a_in_water
- **Equation**:

```
_oChlaW_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_oChlaEpi_ * _uDepthWEpi_ + _oChlaHyp_ * _uDepthWHyp_) / _uDepthW_ _ELSE_ (_oChlaEpi_ * _uDepthWEpi_) / _uDepthW_ _ENDIF_
```

### `_aChlaH_`  [_mgChl_*_m_^-2]
- **Description**: Chla_per_m2
- **Equation**:

```
_aChlaH_ = _oChla_ * _uDepthW_
```

### `_oChlaMeasEpi_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a_at_measurement_depth
- **Equation**:

```
_oChlaMeasEpi_ = _IF_ (_cDepthMeasoChl_ _LT_ _aDepthEuphW_) _THEN_ _aLMeasEpi_/ _aLPIMeasEpi_ *_oChlaEpi_ * _uDepthWEpi_ _ELSE_ _oChlaEpi_ _ENDIF_
```

### `_oChlaMeasHyp_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a_at_measurement_depth_in_Hyp
- **Equation**:

```
_oChlaMeasHyp_ = _IF_ (_cDepthMeasoChl_ _LT_ _aDepthEuphW_) _THEN_  _aLMeasHyp_/ _aLPIMeasHyp_ *_oChlaHyp_* _uDepthWHyp_  _ELSE_ _oChlaHyp_ _ENDIF_
```

### `_oChlaMeasW_`  [_mgChl_*_m_^-3]
- **Description**: Total_chlorophyll-a_at_measurement_depth
- **Equation**:

```
_oChlaMeasW_ = _IF_ (_cDepthMeasoChl_ _LT_ _uDepthWEpi_) _THEN_ _oChlaMeasEpi_ _ELSE_ _oChlaMeasHyp_ _ENDIF_
```

### `_wDAssPhytEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_growth
- **Equation**:

```
_wDAssPhytEpi_ = _wDAssDiatEpi_ + _wDAssGrenEpi_ + _wDAssBlueEpi_
```

### `_wDRespPhytWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_respiration_in_water
- **Equation**:

```
_wDRespPhytWEpi_ = _wDRespDiatWEpi_ + _wDRespGrenWEpi_ + _wDRespBlueWEpi_
```

### `_wDMortPhytWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_algal_mortality_in_water
- **Equation**:

```
_wDMortPhytWEpi_ = _wDMortDiatWEpi_ + _wDMortGrenWEpi_ + _wDMortBlueWEpi_
```

### `_tDSetPhytEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_phytoplankton_sedimentation
- **Equation**:

```
_tDSetPhytEpi_ = _tDSetDiatEpi_ + _tDSetGrenEpi_ + _tDSetBlueEpi_
```

### `_wDLossPhytEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_phytoplankton_grazing_loss
- **Equation**:

```
_wDLossPhytEpi_ = _wDLossDiatEpi_ + _wDLossGrenEpi_ + _wDLossBlueEpi_ + _tDLossBlueSurf_ / _uDepthWEpi_
```

### `_wDPrimPhytWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wDPrimPhytWEpi_ = _wDPrimDiatWEpi_ + _wDPrimGrenWEpi_ + _wDPrimBlueWEpi_
```

### `_wPUptPhytEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_uptake_phytoplankton
- **Equation**:

```
_wPUptPhytEpi_ = _wPUptDiatEpi_ + _wPUptGrenEpi_ + _wPUptBlueEpi_
```

### `_wPExcrPhytWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_excretion_phytoplankton_in_water
- **Equation**:

```
_wPExcrPhytWEpi_ = _wPExcrDiatWEpi_ + _wPExcrGrenWEpi_ + _wPExcrBlueWEpi_
```

### `_wPMortPhytWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_mortality_phytoplankton_in_water
- **Equation**:

```
_wPMortPhytWEpi_ = _wPMortDiatWEpi_ + _wPMortGrenWEpi_ + _wPMortBlueWEpi_
```

### `_tPSetPhytEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_sedimentation_of_algae
- **Equation**:

```
_tPSetPhytEpi_ = _tPSetDiatEpi_ + _tPSetGrenEpi_ + _tPSetBlueEpi_
```

### `_wPLossPhytEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_grazing_loss
- **Equation**:

```
_wPLossPhytEpi_ = _wPLossDiatEpi_ + _wPLossGrenEpi_ + _wPLossBlueEpi_ + _tPLossBlueSurf_ / _uDepthWEpi_
```

### `_wPPrimPhytWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wPPrimPhytWEpi_ = _wPPrimDiatWEpi_ + _wPPrimGrenWEpi_ + _wPPrimBlueWEpi_
```

### `_wNUptPhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_uptake_phytoplankton
- **Equation**:

```
_wNUptPhytEpi_ = _wNUptDiatEpi_ + _wNUptGrenEpi_ + _wNUptBlueEpi_
```

### `_wNUptNH4PhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_ammonium-N_uptake_phytoplankton
- **Equation**:

```
_wNUptNH4PhytEpi_ = _wNUptNH4DiatEpi_ + _wNUptNH4GrenEpi_ + _wNUptNH4BlueEpi_
```

### `_wNUptNO3PhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_nitrate-N_uptake_phytoplankton
- **Equation**:

```
_wNUptNO3PhytEpi_ = _wNUptNO3DiatEpi_ + _wNUptNO3GrenEpi_ + _wNUptNO3BlueEpi_
```

### `_wNExcrPhytWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_excretion_phytoplankton_in_water
- **Equation**:

```
_wNExcrPhytWEpi_ = _wNExcrDiatWEpi_ + _wNExcrGrenWEpi_ + _wNExcrBlueWEpi_
```

### `_wNMortPhytWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_mortality_phytoplankton_in_water
- **Equation**:

```
_wNMortPhytWEpi_ = _wNMortDiatWEpi_ + _wNMortGrenWEpi_ + _wNMortBlueWEpi_
```

### `_tNSetPhytEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_sedimentation_of_algae
- **Equation**:

```
_tNSetPhytEpi_ = _tNSetDiatEpi_ + _tNSetGrenEpi_ + _tNSetBlueEpi_
```

### `_wNLossPhytEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_grazing_loss
- **Equation**:

```
_wNLossPhytEpi_ = _wNLossDiatEpi_ + _wNLossGrenEpi_ + _wNLossBlueEpi_ + _tNLossBlueSurf_ / _uDepthWEpi_
```

### `_wNPrimPhytWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_of_PRIM_processes_of_algae_in_water
- **Equation**:

```
_wNPrimPhytWEpi_ = _wNPrimDiatWEpi_ + _wNPrimGrenWEpi_ + _wNPrimBlueWEpi_
```

### `_tDPrimPhytS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_flux_of_algae_on_bottom
- **Equation**:

```
_tDPrimPhytS_ = _tDPrimDiatS_ + _tDPrimGrenS_ + _tDPrimBlueS_
```

### `_tPPrimPhytS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_flux_of_algae_on_bottom
- **Equation**:

```
_tPPrimPhytS_ = _tPPrimDiatS_ + _tPPrimGrenS_ + _tPPrimBlueS_
```

### `_tNPrimPhytS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_flux_of_algae_on_bottom
- **Equation**:

```
_tNPrimPhytS_ = _tNPrimDiatS_ + _tNPrimGrenS_ + _tNPrimBlueS_
```

## Total_fluxes_to_detritus_and_dissolved_nutrients_in_'prim'_module  (66 equations)

### `_wDPrimDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Flux_to_water_detritus
- **Equation**:

```
_wDPrimDetWHyp_ = _wDMortPhytWHyp_ + _wDLossPhytHyp_
```

### `_wO2RespPhytWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_by_phytoplankton
- **Equation**:

```
_wO2RespPhytWHyp_ = _molO2molC_ * _cCPerDW_ * _wDRespPhytWHyp_ * _aCorO2BODHyp_
```

### `_wO2UptNO3PhytHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_due_to_NO3_uptake_by_phytoplankton
- **Equation**:

```
_wO2UptNO3PhytHyp_ = _O2PerNO3_ * _molO2molN_ * _wNUptNO3PhytHyp_
```

### `_wPMortPhytPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_flux_from_died_Algae
- **Equation**:

```
_wPMortPhytPO4WHyp_ = _fDissMortPhyt_ * _wPMortPhytWHyp_
```

### `_wPMortPhytDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_flux_from_died_Algae
- **Equation**:

```
_wPMortPhytDetWHyp_ = _wPMortPhytWHyp_ - _wPMortPhytPO4WHyp_
```

### `_tPMortPhytPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Soluble_P_flux_from_died_Algae
- **Equation**:

```
_tPMortPhytPO4S_ = _fDissMortPhyt_ * _tPMortPhytS_
```

### `_tPMortPhytDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_flux_from_died_Algae
- **Equation**:

```
_tPMortPhytDetS_ = _tPMortPhytS_ - _tPMortPhytPO4S_
```

### `_tPPrimPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Pore_water_P
- **Equation**:

```
_tPPrimPO4S_ = _tPExcrPhytS_ + _tPMortPhytPO4S_
```

### `_tPPrimTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_flux
- **Equation**:

```
_tPPrimTotT_ = 0.0
```

### `_wNMortPhytNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_flux_from_died_Algae
- **Equation**:

```
_wNMortPhytNH4WHyp_ = _fDissMortPhyt_ * _wNMortPhytWHyp_
```

### `_wNMortPhytDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_flux_from_died_Algae
- **Equation**:

```
_wNMortPhytDetWHyp_ = _wNMortPhytWHyp_ - _wNMortPhytNH4WHyp_
```

### `_wNLossPhytNH4Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: NH4-N_grazing_loss
- **Equation**:

```
_wNLossPhytNH4Hyp_ = _fDissLoss_ * _wNLossPhytHyp_
```

### `_wNLossPhytDetHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_grazing_loss
- **Equation**:

```
_wNLossPhytDetHyp_ = _wNLossPhytHyp_ - _wNLossPhytNH4Hyp_
```

### `_wNPrimNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_in_water
- **Equation**:

```
_wNPrimNH4WHyp_ = - _wNUptNH4PhytHyp_ + _wNExcrPhytWHyp_ + _wNLossPhytNH4Hyp_ + _wNMortPhytNH4WHyp_
```

### `_wNPrimNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_in_water
- **Equation**:

```
_wNPrimNO3WHyp_ = - _wNUptNO3PhytHyp_
```

### `_wNPrimDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detritus_in_water
- **Equation**:

```
_wNPrimDetWHyp_ = _wNLossPhytDetHyp_ + _wNMortPhytDetWHyp_
```

### `_tNMortPhytNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Ammonium_flux_from_died_Algae
- **Equation**:

```
_tNMortPhytNH4S_ = _fDissMortPhyt_ * _tNMortPhytS_
```

### `_tNMortPhytDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_N_flux_from_died_Algae
- **Equation**:

```
_tNMortPhytDetS_ = _tNMortPhytS_ - _tNMortPhytNH4S_
```

### `_tNPrimNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Pore_water_ammonium
- **Equation**:

```
_tNPrimNH4S_ = _tNExcrPhytS_ + _tNMortPhytNH4S_
```

### `_tNPrimNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Pore_water_nitrate
- **Equation**:

```
_tNPrimNO3S_ = 0.0
```

### `_tNPrimTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_flux
- **Equation**:

```
_tNPrimTotT_ = 0.0
```

### `_tSiExcrDiatS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Si_excretion_of_bottom_Algae
- **Equation**:

```
_tSiExcrDiatS_ = _cSiDDiat_ * _tDRespDiatS_
```

### `_tSiMortDiatS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_bottom_Algae
- **Equation**:

```
_tSiMortDiatS_ = _cSiDDiat_ * _tDMortDiatS_
```

### `_wSiPrimSiO2WHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sio2_in_PRIM_module
- **Equation**:

```
_wSiPrimSiO2WHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wSiExcrDiatWHyp_ - _wSiUptDiatHyp_ + _tSiExcrDiatS_ / _uDepthWHyp_ _ENDIF_
```

### `_wSiPrimDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sed_detritus_in_PRIM_module
- **Equation**:

```
_wSiPrimDetWHyp_ = _wSiMortDiatWHyp_ + _wSiLossDiatHyp_
```

### `_tSiPrimTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_flux
- **Equation**:

```
_tSiPrimTotT_ = 0.0
```

### `_wO2ProdPhytHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_by_phytoplankton
- **Equation**:

```
_wO2ProdPhytHyp_ = _molO2molC_ * _cCPerDW_ * _wDAssPhytHyp_
```

### `_wO2PrimWHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_by_water_algae
- **Equation**:

```
_wO2PrimWHyp_ = _wO2ProdPhytHyp_ - _wO2RespPhytWHyp_ + _wO2UptNO3PhytHyp_
```

### `_wPLossPhytPO4Hyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_grazing_loss
- **Equation**:

```
_wPLossPhytPO4Hyp_ = _fDissLoss_ * _wPLossPhytHyp_
```

### `_wPLossPhytDetHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_grazing_loss
- **Equation**:

```
_wPLossPhytDetHyp_ = _wPLossPhytHyp_ - _wPLossPhytPO4Hyp_
```

### `_wPPrimDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detritus_in_water
- **Equation**:

```
_wPPrimDetWHyp_ = _wPLossPhytDetHyp_ + _wPMortPhytDetWHyp_
```

### `_wPPrimPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: SRP_in_water
- **Equation**:

```
_wPPrimPO4WHyp_ = - _wPUptPhytHyp_ + _wPExcrPhytWHyp_ + _wPLossPhytPO4Hyp_ + _wPMortPhytPO4WHyp_
```

### `_wNMortBlueNH4WSurf_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_flux_from_died_Algae
- **Equation**:

```
_wNMortBlueNH4WSurf_ = _fDissMortPhyt_ * _tNMortBlueSurf_ / _uDepthWEpi_
```

### `_wNMortBlueDetSurf_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_flux_from_died_Algae
- **Equation**:

```
_wNMortBlueDetSurf_ = ( 1 -_fDissMortPhyt_) * _tNMortBlueSurf_ / _uDepthWEpi_
```

### `_wDPrimDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Flux_to_water_detritus
- **Equation**:

```
_wDPrimDetWEpi_ = _IF_ (_InclSurf_ _EQ_ _TRUE_) _THEN_ _wDMortPhytWEpi_ + _wDLossPhytEpi_ + _tDMortBlueSurf_ / _uDepthWEpi_ _ELSE_ _wDMortPhytWEpi_ + _wDLossPhytEpi_ _ENDIF_
```

### `_tDPrimDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Flux_to_sediment_detritus
- **Equation**:

```
_tDPrimDetS_ = _tDMortPhytS_
```

### `_tDPrimTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_flux
- **Equation**:

```
_tDPrimTotT_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_ ) _THEN_(_wDAssPhytEpi_ - _wDRespPhytWEpi_) * _uDepthWEpi_ - _tDRespPhytS_ + _tDPrimTotSurf_ _ELSE_ (_wDAssPhytEpi_ - _wDRespPhytWEpi_) * _uDepthWEpi_ + (_wDAssPhytHyp_ - _wDRespPhytWHyp_) * _uDepthWHyp_ - _tDRespPhytS_ + _tDPrimTotSurf_ _ENDIF_
```

### `_wO2ProdPhytEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_by_phytoplankton
- **Equation**:

```
_wO2ProdPhytEpi_ = _molO2molC_ * _cCPerDW_ * _wDAssPhytEpi_
```

### `_wO2RespPhytWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_by_phytoplankton
- **Equation**:

```
_wO2RespPhytWEpi_ = _molO2molC_ * _cCPerDW_ * _wDRespPhytWEpi_ * _aCorO2BODEpi_
```

### `_wO2UptNO3PhytEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_production_due_to_NO3_uptake_by_phytoplankton
- **Equation**:

```
_wO2UptNO3PhytEpi_ = _O2PerNO3_ * _molO2molN_ * _wNUptNO3PhytEpi_
```

### `_wO2PrimWEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_by_water_algae
- **Equation**:

```
_wO2PrimWEpi_ = _wO2ProdPhytEpi_ - _wO2RespPhytWEpi_ + _wO2UptNO3PhytEpi_
```

### `_tO2RespPhytS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_respiration_by_sediment_algae
- **Equation**:

```
_tO2RespPhytS_ = _molO2molC_ * _cCPerDW_ * _tDRespPhytS_ * _afOxySed_
```

### `_tO2PrimS_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_flux_by_sediment_algae
- **Equation**:

```
_tO2PrimS_ = _tO2RespPhytS_
```

### `_tO2PrimSHyp_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_from_sediment_algae_to_Hypolimnion
- **Equation**:

```
_tO2PrimSHyp_ = _IF_ _aInclStrat_ _EQ_ _TRUE_ _THEN_ _tO2PrimS_ / _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2PrimSEpi_`  [_gO2_*_m_^-3*_d_^-1]
- **Description**: O2_flux_from_sediment_algae_to_Epilimnion
- **Equation**:

```
_tO2PrimSEpi_ = _IF_ _aInclStrat_ _EQ_ _FALSE_ _THEN_ _tO2PrimS_ / _uDepthWEpi_ _ELSE_ 0.0 _ENDIF_
```

### `_wPMortBluePO4WSurf_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_flux_from_died_Algae_on_surface
- **Equation**:

```
_wPMortBluePO4WSurf_ = _fDissMortPhyt_ * _tPMortBlueSurf_ / _uDepthWEpi_
```

### `_wPMortBlueDetSurf_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_flux_from_died_Algae_on_surface
- **Equation**:

```
_wPMortBlueDetSurf_ = ( 1 -_fDissMortPhyt_) * _tPMortBlueSurf_ / _uDepthWEpi_
```

### `_wPMortPhytPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_flux_from_died_Algae
- **Equation**:

```
_wPMortPhytPO4WEpi_ = _fDissMortPhyt_ * _wPMortPhytWEpi_
```

### `_wPMortPhytDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_flux_from_died_Algae
- **Equation**:

```
_wPMortPhytDetWEpi_ = _wPMortPhytWEpi_ - _wPMortPhytPO4WEpi_ + _wPMortBlueDetSurf_
```

### `_wPLossPhytPO4Epi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_grazing_loss
- **Equation**:

```
_wPLossPhytPO4Epi_ = _fDissLoss_ * _wPLossPhytEpi_
```

### `_wPLossPhytDetEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_grazing_loss
- **Equation**:

```
_wPLossPhytDetEpi_ = _wPLossPhytEpi_ - _wPLossPhytPO4Epi_
```

### `_wPPrimPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: SRP_in_water
- **Equation**:

```
_wPPrimPO4WEpi_ = - _wPUptPhytEpi_ + _wPExcrPhytWEpi_ + _wPLossPhytPO4Epi_ + _wPMortPhytPO4WEpi_ - _tPUptBlueSurf_ / _uDepthWEpi_ + _tPExcrBlueSurf_ / _uDepthWEpi_ + _wPMortBluePO4WSurf_
```

### `_wPPrimDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detritus_in_water
- **Equation**:

```
_wPPrimDetWEpi_ = _wPLossPhytDetEpi_ + _wPMortPhytDetWEpi_
```

### `_tPPrimDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Sediment_detritus
- **Equation**:

```
_tPPrimDetS_ = _tPMortPhytDetS_
```

### `_wNMortPhytNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_flux_from_died_Algae
- **Equation**:

```
_wNMortPhytNH4WEpi_ = _fDissMortPhyt_ * _wNMortPhytWEpi_
```

### `_wNMortPhytDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_flux_from_died_Algae
- **Equation**:

```
_wNMortPhytDetWEpi_ = _wNMortPhytWEpi_ - _wNMortPhytNH4WEpi_+ _wNMortBlueDetSurf_
```

### `_wNLossPhytNH4Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: NH4-N_grazing_loss
- **Equation**:

```
_wNLossPhytNH4Epi_ = _fDissLoss_ * _wNLossPhytEpi_
```

### `_wNLossPhytDetEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_grazing_loss
- **Equation**:

```
_wNLossPhytDetEpi_ = _wNLossPhytEpi_ - _wNLossPhytNH4Epi_
```

### `_wNPrimNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Ammonium_in_water
- **Equation**:

```
_wNPrimNH4WEpi_ = - _wNUptNH4PhytEpi_ + _wNExcrPhytWEpi_ + _wNLossPhytNH4Epi_ + _wNMortPhytNH4WEpi_- _tNUptNH4BlueSurf_ / _uDepthWEpi_ + _tNExcrBlueSurf_ / _uDepthWEpi_ + _wNMortBlueNH4WSurf_
```

### `_wNPrimNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Nitrate_in_water
- **Equation**:

```
_wNPrimNO3WEpi_ = - _wNUptNO3PhytEpi_ - _tNUptNO3BlueSurf_ / _uDepthWEpi_
```

### `_wNPrimDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detritus_in_water
- **Equation**:

```
_wNPrimDetWEpi_ = _wNLossPhytDetEpi_ + _wNMortPhytDetWEpi_
```

### `_tNPrimDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Sediment_detritus
- **Equation**:

```
_tNPrimDetS_ = _tNMortPhytDetS_
```

### `_wSiPrimSiO2WEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sio2_in_PRIM_module
- **Equation**:

```
_wSiPrimSiO2WEpi_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _wSiExcrDiatWEpi_ - _wSiUptDiatEpi_ + _tSiExcrDiatS_ / _uDepthWEpi_ _ELSE_ _wSiExcrDiatWEpi_ - _wSiUptDiatEpi_ _ENDIF_
```

### `_wSiPrimDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_Si_flux_to_sed_detritus_in_PRIM_module
- **Equation**:

```
_wSiPrimDetWEpi_ = _wSiMortDiatWEpi_ + _wSiLossDiatEpi_
```

### `_tSiPrimDiatS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_flux_to_sed_diatoms_in_PRIM_module
- **Equation**:

```
_tSiPrimDiatS_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _tSiSetDiatEpi_ - _tSiResusDiat_ - _tSiExcrDiatS_ - _tSiMortDiatS_ _ELSE_ _tSiSetDiatHyp_ - _tSiResusDiat_ - _tSiExcrDiatS_ - _tSiMortDiatS_ _ENDIF_
```

### `_tSiPrimDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Sediment_detritus
- **Equation**:

```
_tSiPrimDetS_ = _tSiMortDiatS_
```

## Extra_ouput_variables_of_phytoplankton  (21 equations)

### `_aPACoefEpi_`  [0]
- **Description**: Poole-Atkins_coefficient
- **Equation**:

```
_aPACoefEpi_ = _cPACoefMin_ +(_cPACoefMax_ - _cPACoefMin_) * _hPACoef_ / (_hPACoef_ + _oDOMWEpi_)
```

### `_aPACoefHyp_`  [0]
- **Description**: Poole-Atkins_coefficient
- **Equation**:

```
_aPACoefHyp_ = _cPACoefMin_ +(_cPACoefMax_ - _cPACoefMin_) * _hPACoef_ / (_hPACoef_ + _oDOMWHyp_)
```

### `_bSecchiMaxEpi_`  [_m_]
- **Description**: Max_Secchi_depth
- **Equation**:

```
_bSecchiMaxEpi_ = _uDepthWEpi_
```

### `_aSecchiEpi_`  [_m_]
- **Description**: Secchi_depth
- **Equation**:

```
_aSecchiEpi_ = _MIN_(_bSecchiMaxEpi_,_aPACoefEpi_ / _aExtCoefOpenEpi_)
```

### `_aTransparencyEpi_`  [0]
- **Description**: Transparency
- **Equation**:

```
_aTransparencyEpi_ = _aSecchiEpi_ / _uDepthWEpi_
```

### `_bSecchiMaxHyp_`  [_m_]
- **Description**: Max_Secchi_depth
- **Equation**:

```
_bSecchiMaxHyp_ = _uDepthWHyp_ + _cSecchiPlus_
```

### `_aSecchiHyp_`  [_m_]
- **Description**: Secchi_depth_of_the_hypolimnion
- **Equation**:

```
_aSecchiHyp_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ _uDepthWEpi_ _LE_ _aPACoefEpi_ / _aExtCoefOpenEpi_ ) _THEN_ _MIN_(_bSecchiMaxHyp_,_aPACoefHyp_ / _aExtCoefOpenHyp_ - _aSecchiEpi_) _ELSEIF_ ( _aInclStrat_ _EQ_ _TRUE_ _AND_ _uDepthWEpi_ _GT_ _aPACoefEpi_ / _aExtCoefOpenEpi_) _THEN_ 0.0 _ELSE_ _MIN_(_bSecchiMaxHyp_,_aPACoefHyp_ / _aExtCoefOpenHyp_) _ENDIF_
```

### `_aSecchiT_`  [_m_]
- **Description**: Secchi_depth_total
- **Equation**:

```
_aSecchiT_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _aSecchiEpi_ +_aSecchiHyp_ _ELSE_ _aSecchiEpi_ _ENDIF_
```

### `_aTransparencyHyp_`  [0]
- **Description**: Transparency_of_the_hypolimnion
- **Equation**:

```
_aTransparencyHyp_ = _aSecchiHyp_ / _uDepthWHyp_
```

### `_aTransparencyT_`  [0]
- **Description**: Transparency_of_the_total_water_level
- **Equation**:

```
_aTransparencyT_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ _aSecchiT_ / _uDepthW_ _ELSE_ _aSecchiT_ / _uDepthWHyp_ _ENDIF_
```

### `_aDepthEuphHyp_`  [_m_]
- **Description**: Euphotic_depth
- **Equation**:

```
_aDepthEuphHyp_ = _cEuph_ * _aSecchiHyp_
```

### `_aRelDepthEuphHyp_`  [0]
- **Description**: Relative_euphotic_depth
- **Equation**:

```
_aRelDepthEuphHyp_ = _aDepthEuphHyp_ / _uDepthWHyp_
```

### `_aChlaHHyp_`  [_mgChl_*_m_^-2]
- **Description**: Chla_per_m2
- **Equation**:

```
_aChlaHHyp_ = _oChlaHyp_ * _uDepthWHyp_
```

### `_aCovPhytWHyp_`  [0]
- **Description**: %_cover_with_algae
- **Equation**:

```
_aCovPhytWHyp_ = _cCovSpPhyt_ *(_oDPhytWHyp_ * _uDepthWHyp_)
```

### `_rExtChPhytHyp_`  [_m_^2*_gChl_^-1]
- **Description**: Average_spec_extinction_of_algae_per_unit_chla
- **Equation**:

```
_rExtChPhytHyp_ = _aExtPhytHyp_ /(_oChlaHyp_ / _mgPerg_ + _NearZero_)
```

### `_aDepthEuphW_`  [_m_]
- **Description**: Euphotic_depth
- **Equation**:

```
_aDepthEuphW_ = _IF_ (_aLPAREupho_ _GT_ _aLPARBotSurf_) _THEN_  0.0 _ELSEIF_ (_aLPAREupho_ _GE_ _aLPARBotEpiOpen_) _THEN_ - _LN_(_aLPAREupho_/_aLPARBotSurf_) / _aExtCoefEpi_ _ELSE_ _uDepthWEpi_ - _LN_(_aLPAREupho_/_aLPARBotEpiOpen_) / _aExtCoefOpenHyp_ _ENDIF_
```

### `_aDepthEuphEpi_`  [_m_]
- **Description**: Euphotic_depth
- **Equation**:

```
_aDepthEuphEpi_ = _cEuph_ * _aSecchiEpi_
```

### `_aRelDepthEuphEpi_`  [0]
- **Description**: Relative_euphotic_depth
- **Equation**:

```
_aRelDepthEuphEpi_ = _aDepthEuphEpi_ / _uDepthWEpi_
```

### `_aChlaHEpi_`  [_mgChl_*_m_^-2]
- **Description**: Chla_per_m2
- **Equation**:

```
_aChlaHEpi_ = _oChlaEpi_ * _uDepthWEpi_
```

### `_aCovPhytWEpi_`  [0]
- **Description**: %_cover_with_algae
- **Equation**:

```
_aCovPhytWEpi_ = _cCovSpPhyt_ *(_oDPhytWEpi_ * _uDepthWEpi_)
```

### `_rExtChPhytEpi_`  [_m_^2*_gChl_^-1]
- **Description**: Average_spec_extinction_of_algae_per_unit_chla
- **Equation**:

```
_rExtChPhytEpi_ = _aExtPhytEpi_ /(_oChlaEpi_ / _mgPerg_ + _NearZero_)
```

## Zooplankton_processes  (125 equations)

### `_uFunTmZooHyp_`  [0]
- **Description**: Temp_function_of_zooplankton
- **Equation**:

```
_uFunTmZooHyp_ = _EXP_(-0.5/(_cSigTmZoo_*_cSigTmZoo_) *((_uTmHyp_-_cTmOptZoo_)*(_uTmHyp_-_cTmOptZoo_) -(_cTmRef_-_cTmOptZoo_)*(_cTmRef_-_cTmOptZoo_)))
```

### `_uFunTmZooEpi_`  [0]
- **Description**: Temp_function_of_zooplankton
- **Equation**:

```
_uFunTmZooEpi_ = _EXP_(-0.5/(_cSigTmZoo_*_cSigTmZoo_) *((_uTmEpi_-_cTmOptZoo_)*(_uTmEpi_-_cTmOptZoo_) -(_cTmRef_-_cTmOptZoo_)*(_cTmRef_-_cTmOptZoo_)))
```

### `_rPDZooHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_herbaceous_zooplankton
- **Equation**:

```
_rPDZooHyp_ = _oPZooHyp_ /(_oDZooHyp_+_NearZero_)
```

### `_rNDZooHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/C_ratio_herbaceous_zooplankton
- **Equation**:

```
_rNDZooHyp_ = _oNZooHyp_/(_oDZooHyp_+_NearZero_)
```

### `_oDFoodZooHyp_`  [_gDW_*_m_^-3]
- **Description**: Food_for_zooplankton
- **Equation**:

```
_oDFoodZooHyp_ = _cPrefDiat_ * _oDDiatWHyp_ + _cPrefGren_ * _oDGrenWHyp_ + _cPrefBlue_ * _oDBlueWHyp_ + _cPrefDet_ * _oDDetWHyp_
```

### `_aFiltHyp_`  [_m_^3*_gDW_^-1*_d_^-1]
- **Description**: Filtering_rate
- **Equation**:

```
_aFiltHyp_ = _cFiltMax_ * _uFunTmZooHyp_ * _hFilt_ /(_hFilt_ + _oDOMWHyp_)
```

### `_ukDAssTmZooHyp_`  [_d_^-1]
- **Description**: Max_assimilation_rate_of_zooplankton_temp_corrected
- **Equation**:

```
_ukDAssTmZooHyp_ = _fDAssZoo_ * _cFiltMax_ * _uFunTmZooHyp_ * _hFilt_
```

### `_ukDAssTmZooEpi_`  [_d_^-1]
- **Description**: Max_assimilation_rate_of_corrected
- **Equation**:

```
_ukDAssTmZooEpi_ = _fDAssZoo_ * _cFiltMax_ * _uFunTmZooEpi_ * _hFilt_
```

### `_aDSatZooHyp_`  [0]
- **Description**: Food_saturation_function_of_zooplankton
- **Equation**:

```
_aDSatZooHyp_ = _oDFoodZooHyp_ /(_hFilt_ + _oDOMWHyp_)
```

### `_ukDRespTmZooHyp_`  [_d_^-1]
- **Description**: Respiration_constant_of_zooplankton
- **Equation**:

```
_ukDRespTmZooHyp_ = _kDRespZoo_ * _uFunTmZooHyp_
```

### `_ukDRespTmZooEpi_`  [_d_^-1]
- **Description**: Respiration_constant_of_zooplankton
- **Equation**:

```
_ukDRespTmZooEpi_ = _kDRespZoo_ * _uFunTmZooEpi_
```

### `_ukDIncrZooHyp_`  [_d_^-1]
- **Description**: Intrinsic_rate_of_increase_of_zooplankton
- **Equation**:

```
_ukDIncrZooHyp_ = _ukDAssTmZooHyp_ - _ukDRespTmZooHyp_ - _kMortZoo_
```

### `_ukDIncrZooEpi_`  [_d_^-1]
- **Description**: Intrinsic_rate_of_increase_of_zooplankton
- **Equation**:

```
_ukDIncrZooEpi_ = _ukDAssTmZooEpi_ - _ukDRespTmZooEpi_ - _kMortZoo_
```

### `_wDEnvZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Environmental_correction_of_zooplankton
- **Equation**:

```
_wDEnvZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _MAX_(0.0,_ukDIncrZooHyp_ / _cDCarrZoo_ * _oDZooHyp_*_oDZooHyp_) _ENDIF_
```

### `_wDAssZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_of_zooplankton
- **Equation**:

```
_wDAssZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aDSatZooHyp_ *(_ukDAssTmZooHyp_ * _oDZooHyp_ - _wDEnvZooHyp_) _ENDIF_
```

### `_wDConsZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_zooplankton
- **Equation**:

```
_wDConsZooHyp_ = _wDAssZooHyp_ / _fDAssZoo_
```

### `_wDConsDetZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_detritus_consumption_by_zooplankton
- **Equation**:

```
_wDConsDetZooHyp_ = _cPrefDet_*_oDDetWHyp_ / _oDFoodZooHyp_ * _wDConsZooHyp_
```

### `_wDConsDiatZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_diatoms_consumption_by_zooplankton
- **Equation**:

```
_wDConsDiatZooHyp_ = _cPrefDiat_*_oDDiatWHyp_ / _oDFoodZooHyp_ * _wDConsZooHyp_
```

### `_wDConsGrenZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_greens_consumption_by_zooplankton
- **Equation**:

```
_wDConsGrenZooHyp_ = _cPrefGren_*_oDGrenWHyp_ / _oDFoodZooHyp_ * _wDConsZooHyp_
```

### `_wDConsBlueZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_wDConsBlueZooHyp_ = _cPrefBlue_*_oDBlueWHyp_ / _oDFoodZooHyp_ * _wDConsZooHyp_
```

### `_wDConsPhytZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wDConsPhytZooHyp_ = _wDConsDiatZooHyp_ + _wDConsGrenZooHyp_ + _wDConsBlueZooHyp_
```

### `_wDEgesZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Egestion_of_zooplankton
- **Equation**:

```
_wDEgesZooHyp_ = _wDConsZooHyp_ - _wDAssZooHyp_
```

### `_aCorDRespZooHyp_`  [0]
- **Description**: Correction_factor_of_zooplankton_respiration_for_P_and_N_content
- **Equation**:

```
_aCorDRespZooHyp_ = _MAX_(_cPDZooRef_ / _rPDZooHyp_,_cNDZooRef_ / _rNDZooHyp_)
```

### `_wDRespZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Zooplankton_respiration
- **Equation**:

```
_wDRespZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aCorDRespZooHyp_ * _ukDRespTmZooHyp_ * _oDZooHyp_ _ENDIF_
```

### `_wDMortZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Zooplankton_mortality_incl_environmental_correction
- **Equation**:

```
_wDMortZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kMortZoo_ * _oDZooHyp_ +(1.0 - _aDSatZooHyp_) * _wDEnvZooHyp_ _ENDIF_
```

### `_oPFoodZooHyp_`  [_gP_*_m_^-3]
- **Description**: Zooplankton_food
- **Equation**:

```
_oPFoodZooHyp_ = _cPrefDiat_*_oPDiatWHyp_ + _cPrefGren_*_oPGrenWHyp_ + _cPrefBlue_*_oPBlueWHyp_ + _cPrefDet_ * _oPDetWHyp_
```

### `_rPDFoodZooHyp_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_zooplankton_food
- **Equation**:

```
_rPDFoodZooHyp_ = _oPFoodZooHyp_ /(_oDFoodZooHyp_+_NearZero_)
```

### `_wPConsDiatZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_diatom_consumption_by_zooplankton
- **Equation**:

```
_wPConsDiatZooHyp_ = _rPDDiatWHyp_ * _wDConsDiatZooHyp_
```

### `_wPConsBlueZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_blue_green_consumption_by_zooplankton
- **Equation**:

```
_wPConsBlueZooHyp_ = _rPDBlueWHyp_ * _wDConsBlueZooHyp_
```

### `_wPConsDetZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_detrital_P
- **Equation**:

```
_wPConsDetZooHyp_ = _rPDDetWHyp_ * _wDConsDetZooHyp_
```

### `_afPAssZooHyp_`  [0]
- **Description**: P_assimilation_efficiency_of_herbivores
- **Equation**:

```
_afPAssZooHyp_ = _MIN_(1.0,_cPDZooRef_ / _rPDFoodZooHyp_ * _fDAssZoo_)
```

### `_akPExcrZooHyp_`  [_d_^-1]
- **Description**: P_excretion_rate_of_herbivores
- **Equation**:

```
_akPExcrZooHyp_ = _rPDZooHyp_ / _cPDZooRef_ * _kDRespZoo_ * _uFunTmZooHyp_
```

### `_wPExcrZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion
- **Equation**:

```
_wPExcrZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _akPExcrZooHyp_*_oPZooHyp_ _ENDIF_
```

### `_wPMortZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality
- **Equation**:

```
_wPMortZooHyp_ = _rPDZooHyp_ * _wDMortZooHyp_
```

### `_wPMortZooPO4Hyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_mortality
- **Equation**:

```
_wPMortZooPO4Hyp_ = _fDissMortZoo_ * _wPMortZooHyp_
```

### `_wPMortZooDetHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_mortality
- **Equation**:

```
_wPMortZooDetHyp_ = _wPMortZooHyp_ - _wPMortZooPO4Hyp_
```

### `_oNFoodZooHyp_`  [_gN_*_m_^-3]
- **Description**: Zooplankton_food
- **Equation**:

```
_oNFoodZooHyp_ = _cPrefDiat_*_oNDiatWHyp_ + _cPrefGren_*_oNGrenWHyp_ + _cPrefBlue_*_oNBlueWHyp_ + _cPrefDet_*_oNDetWHyp_
```

### `_rNDFoodZooHyp_`  [_gN_*_gDW_^-1]
- **Description**: N/C_ratio_of_zooplankton_food
- **Equation**:

```
_rNDFoodZooHyp_ = _oNFoodZooHyp_ /(_oDFoodZooHyp_+_NearZero_)
```

### `_wNConsDiatZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_diatom_consumption_by_zooplankton
- **Equation**:

```
_wNConsDiatZooHyp_ = _rNDDiatWHyp_*_wDConsDiatZooHyp_
```

### `_wNConsGrenZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_green_consumption_by_zooplankton
- **Equation**:

```
_wNConsGrenZooHyp_ = _rNDGrenWHyp_*_wDConsGrenZooHyp_
```

### `_wNConsBlueZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_blue_green_consumption_by_zooplankton
- **Equation**:

```
_wNConsBlueZooHyp_ = _rNDBlueWHyp_*_wDConsBlueZooHyp_
```

### `_wNConsPhytZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wNConsPhytZooHyp_ = _wNConsDiatZooHyp_ + _wNConsGrenZooHyp_ + _wNConsBlueZooHyp_
```

### `_wNConsDetZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_detrital_N
- **Equation**:

```
_wNConsDetZooHyp_ = _rNDDetWHyp_*_wDConsDetZooHyp_
```

### `_wNConsZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_consumption
- **Equation**:

```
_wNConsZooHyp_ = _wNConsPhytZooHyp_ + _wNConsDetZooHyp_
```

### `_afNAssZooHyp_`  [0]
- **Description**: N_assimilation_efficiency_of_herbivores
- **Equation**:

```
_afNAssZooHyp_ = _MIN_(1.0,_cNDZooRef_ / _rNDFoodZooHyp_ * _fDAssZoo_)
```

### `_wNAssZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Assimilation_by_herbivores
- **Equation**:

```
_wNAssZooHyp_ = _afNAssZooHyp_*_wNConsZooHyp_
```

### `_wNEgesZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_egestion
- **Equation**:

```
_wNEgesZooHyp_ = _wNConsZooHyp_ - _wNAssZooHyp_
```

### `_wNEgesZooNH4Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Soluble_N_egestion
- **Equation**:

```
_wNEgesZooNH4Hyp_ = _fDissEgesZoo_*_wNEgesZooHyp_
```

### `_wNEgesZooDetHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_egestion
- **Equation**:

```
_wNEgesZooDetHyp_ = _wNEgesZooHyp_ - _wNEgesZooNH4Hyp_
```

### `_kNExcrZooHyp_`  [_d_^-1]
- **Description**: N_excretion_rate_of_herbivores
- **Equation**:

```
_kNExcrZooHyp_ = _rNDZooHyp_ / _cNDZooRef_ * _kDRespZoo_ * _uFunTmZooHyp_
```

### `_wNExcrZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion
- **Equation**:

```
_wNExcrZooHyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _kNExcrZooHyp_*_oNZooHyp_ _ENDIF_
```

### `_wNMortZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality
- **Equation**:

```
_wNMortZooHyp_ = _rNDZooHyp_*_wDMortZooHyp_
```

### `_wNMortZooNH4Hyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Soluble_N_mortality
- **Equation**:

```
_wNMortZooNH4Hyp_ = _fDissMortZoo_*_wNMortZooHyp_
```

### `_wNMortZooDetHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_mortality
- **Equation**:

```
_wNMortZooDetHyp_ = _wNMortZooHyp_ - _wNMortZooNH4Hyp_
```

### `_wSiConsDiatZooHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_diatoms
- **Equation**:

```
_wSiConsDiatZooHyp_ = _cSiDDiat_ * _wDConsDiatZooHyp_
```

### `_wPConsGrenZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_green_consumption_by_zooplankton
- **Equation**:

```
_wPConsGrenZooHyp_ = _rPDGrenWHyp_ * _wDConsGrenZooHyp_
```

### `_wPConsPhytZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wPConsPhytZooHyp_ = _wPConsDiatZooHyp_ + _wPConsGrenZooHyp_ + _wPConsBlueZooHyp_
```

### `_wPConsZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_consumption
- **Equation**:

```
_wPConsZooHyp_ = _wPConsPhytZooHyp_ + _wPConsDetZooHyp_
```

### `_wPAssZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Assimilation_by_herbivores
- **Equation**:

```
_wPAssZooHyp_ = _afPAssZooHyp_ * _wPConsZooHyp_
```

### `_wPEgesZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_egestion
- **Equation**:

```
_wPEgesZooHyp_ = _wPConsZooHyp_ - _wPAssZooHyp_
```

### `_wPEgesZooPO4Hyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_egestion
- **Equation**:

```
_wPEgesZooPO4Hyp_ = _fDissEgesZoo_*_wPEgesZooHyp_
```

### `_wPEgesZooDetHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_egestion
- **Equation**:

```
_wPEgesZooDetHyp_ = _wPEgesZooHyp_ - _wPEgesZooPO4Hyp_
```

### `_rPDZooEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_herbaceous_zooplankton
- **Equation**:

```
_rPDZooEpi_ = _oPZooEpi_ /(_oDZooEpi_+_NearZero_)
```

### `_rNDZooEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/C_ratio_herbaceous_zooplankton
- **Equation**:

```
_rNDZooEpi_ = _oNZooEpi_/(_oDZooEpi_+_NearZero_)
```

### `_aDFoodZooEpi_`  [_gDW_*_m_^-2]
- **Description**: Food_for_zooplankton
- **Equation**:

```
_aDFoodZooEpi_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ _cPrefDiat_ * _aDDiatWEpi_ + _cPrefGren_ * _aDGrenWEpi_ + _cPrefBlue_ * _aDBlueWEpi_ + _cPrefDet_ * _aDDetWEpi_ _ELSE_ _cPrefDiat_ * _aDDiatWEpi_ + _cPrefGren_ * _aDGrenWEpi_ + _cPrefBlue_ * _aDBlueWEpi_ + _cPrefBlueSurf_ * _aDBlueSurf_ + _cPrefDet_ * _aDDetWEpi_ _ENDIF_
```

### `_oDFoodZooEpi_`  [_gDW_*_m_^-3]
- **Description**: Food_for_zooplankton
- **Equation**:

```
_oDFoodZooEpi_ = _aDFoodZooEpi_ / _uDepthWEpi_
```

### `_aFiltEpi_`  [_m_^3*_gDW_^-1*_d_^-1]
- **Description**: Filtering_rate
- **Equation**:

```
_aFiltEpi_ = _cFiltMax_ * _uFunTmZooEpi_ * _hFilt_ /(_hFilt_ + _oDOMWEpi_)
```

### `_aDSatZooEpi_`  [0]
- **Description**: Food_saturation_function_of_zooplankton
- **Equation**:

```
_aDSatZooEpi_ = _oDFoodZooEpi_ /(_hFilt_ + _oDOMWEpi_)
```

### `_wDEnvZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Environmental_correction_of_zooplankton
- **Equation**:

```
_wDEnvZooEpi_ = _MAX_(0.0,_ukDIncrZooEpi_ / _cDCarrZoo_ * _oDZooEpi_*_oDZooEpi_)
```

### `_wDAssZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Assimilation_of_zooplankton
- **Equation**:

```
_wDAssZooEpi_ = _aDSatZooEpi_ *(_ukDAssTmZooEpi_ * _oDZooEpi_ - _wDEnvZooEpi_)
```

### `_wDConsZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_zooplankton
- **Equation**:

```
_wDConsZooEpi_ = _wDAssZooEpi_ / _fDAssZoo_
```

### `_wDConsDetZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_detritus_consumption_by_zooplankton
- **Equation**:

```
_wDConsDetZooEpi_ = _cPrefDet_*_oDDetWEpi_ / _oDFoodZooEpi_ * _wDConsZooEpi_
```

### `_wDConsDiatZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_diatoms_consumption_by_zooplankton
- **Equation**:

```
_wDConsDiatZooEpi_ = _cPrefDiat_*_oDDiatWEpi_ / _oDFoodZooEpi_ * _wDConsZooEpi_
```

### `_wDConsGrenZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_greens_consumption_by_zooplankton
- **Equation**:

```
_wDConsGrenZooEpi_ = _cPrefGren_*_oDGrenWEpi_ / _oDFoodZooEpi_ * _wDConsZooEpi_
```

### `_wDConsBlueZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_wDConsBlueZooEpi_ = _cPrefBlue_*_oDBlueWEpi_ / _oDFoodZooEpi_ * _wDConsZooEpi_
```

### `_wDConsBlueZooSurf_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_wDConsBlueZooSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _cPrefBlueSurf_ *_aDBlueSurf_ / _aDFoodZooEpi_ * _wDConsZooEpi_ _ENDIF_
```

### `_tDConsBlueZooSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_tDConsBlueZooSurf_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ _wDConsBlueZooSurf_ *_uDepthWEpi_ _ENDIF_
```

### `_wDConsPhytZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wDConsPhytZooEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ _wDConsDiatZooEpi_ + _wDConsGrenZooEpi_ + _wDConsBlueZooEpi_ _ELSE_ _wDConsDiatZooEpi_ + _wDConsGrenZooEpi_ + _wDConsBlueZooEpi_ + _wDConsBlueZooSurf_ _ENDIF_
```

### `_wDEgesZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Egestion_of_zooplankton
- **Equation**:

```
_wDEgesZooEpi_ = _wDConsZooEpi_ - _wDAssZooEpi_
```

### `_aCorDRespZooEpi_`  [0]
- **Description**: Correction_factor_of_zooplankton_respiration_for_P_and_N_content
- **Equation**:

```
_aCorDRespZooEpi_ = _MAX_(_cPDZooRef_ / _rPDZooEpi_,_cNDZooRef_ / _rNDZooEpi_)
```

### `_wDRespZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Zooplankton_respiration
- **Equation**:

```
_wDRespZooEpi_ = _aCorDRespZooEpi_ * _ukDRespTmZooEpi_ * _oDZooEpi_
```

### `_wDMortZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Zooplankton_mortality_incl_environmental_correction
- **Equation**:

```
_wDMortZooEpi_ = _kMortZoo_ * _oDZooEpi_ +(1.0 - _aDSatZooEpi_) * _wDEnvZooEpi_
```

### `_aPFoodZooEpi_`  [_gP_*_m_^-2]
- **Description**: Zooplankton_food
- **Equation**:

```
_aPFoodZooEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ _cPrefDiat_*_aPDiatWEpi_ + _cPrefGren_*_aPGrenWEpi_ + _cPrefBlue_ * _aPBlueWEpi_  + _cPrefDet_ * _aPDetWEpi_ _ELSE_ _cPrefDiat_*_aPDiatWEpi_ + _cPrefGren_*_aPGrenWEpi_ + _cPrefBlue_*_aPBlueWEpi_ + _cPrefBlueSurf_ *_aPBlueSurf_ + _cPrefDet_ * _aPDetWEpi_ _ENDIF_
```

### `_oPFoodZooEpi_`  [_gP_*_m_^-3]
- **Description**: Zooplankton_food
- **Equation**:

```
_oPFoodZooEpi_ = _aPFoodZooEpi_ / _MassEpi_
```

### `_rPDFoodZooEpi_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_zooplankton_food
- **Equation**:

```
_rPDFoodZooEpi_ = _oPFoodZooEpi_ /(_oDFoodZooEpi_+_NearZero_)
```

### `_wPConsDiatZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_diatom_consumption_by_zooplankton
- **Equation**:

```
_wPConsDiatZooEpi_ = _rPDDiatWEpi_ * _wDConsDiatZooEpi_
```

### `_wPConsGrenZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_green_consumption_by_zooplankton
- **Equation**:

```
_wPConsGrenZooEpi_ = _rPDGrenWEpi_ * _wDConsGrenZooEpi_
```

### `_wPConsBlueZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_blue_green_consumption_by_zooplankton
- **Equation**:

```
_wPConsBlueZooEpi_ = _rPDBlueWEpi_ * _wDConsBlueZooEpi_
```

### `_wPConsBlueZooSurf_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_wPConsBlueZooSurf_ = _rPDBlueSurf_ * _wDConsBlueZooSurf_
```

### `_tPConsBlueZooSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: DW_blue-greens_consumption_by_zooplankton
- **Equation**:

```
_tPConsBlueZooSurf_ = _wPConsBlueZooSurf_ *_uDepthWEpi_
```

### `_wPConsPhytZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wPConsPhytZooEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ _wPConsDiatZooEpi_ + _wPConsGrenZooEpi_ + _wPConsBlueZooEpi_ _ELSE_ _wPConsDiatZooEpi_ + _wPConsGrenZooEpi_ + _wPConsBlueZooEpi_ + _wPConsBlueZooSurf_ _ENDIF_
```

### `_wPConsDetZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_detrital_P
- **Equation**:

```
_wPConsDetZooEpi_ = _rPDDetWEpi_ * _wDConsDetZooEpi_
```

### `_wPConsZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_P_consumption
- **Equation**:

```
_wPConsZooEpi_ = _wPConsPhytZooEpi_ + _wPConsDetZooEpi_
```

### `_afPAssZooEpi_`  [0]
- **Description**: P_assimilation_efficiency_of_herbivores
- **Equation**:

```
_afPAssZooEpi_ = _MIN_(1.0,_cPDZooRef_ / _rPDFoodZooEpi_ * _fDAssZoo_)
```

### `_wPAssZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Assimilation_by_herbivores
- **Equation**:

```
_wPAssZooEpi_ = _afPAssZooEpi_ * _wPConsZooEpi_
```

### `_wPEgesZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_egestion
- **Equation**:

```
_wPEgesZooEpi_ = _wPConsZooEpi_ - _wPAssZooEpi_
```

### `_wPEgesZooPO4Epi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_egestion
- **Equation**:

```
_wPEgesZooPO4Epi_ = _fDissEgesZoo_*_wPEgesZooEpi_
```

### `_wPEgesZooDetEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_egestion
- **Equation**:

```
_wPEgesZooDetEpi_ = _wPEgesZooEpi_ - _wPEgesZooPO4Epi_
```

### `_akPExcrZooEpi_`  [_d_^-1]
- **Description**: P_excretion_rate_of_herbivores
- **Equation**:

```
_akPExcrZooEpi_ = _rPDZooEpi_ / _cPDZooRef_ * _kDRespZoo_ * _uFunTmZooEpi_
```

### `_wPExcrZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: P_excretion
- **Equation**:

```
_wPExcrZooEpi_ = _akPExcrZooEpi_*_oPZooEpi_
```

### `_wPMortZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Mortality
- **Equation**:

```
_wPMortZooEpi_ = _rPDZooEpi_ * _wDMortZooEpi_
```

### `_wPMortZooPO4Epi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Soluble_P_mortality
- **Equation**:

```
_wPMortZooPO4Epi_ = _fDissMortZoo_ * _wPMortZooEpi_
```

### `_wPMortZooDetEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Detrital_P_mortality
- **Equation**:

```
_wPMortZooDetEpi_ = _wPMortZooEpi_ - _wPMortZooPO4Epi_
```

### `_aNFoodZooEpi_`  [_gN_*_m_^-2]
- **Description**: Zooplankton_food
- **Equation**:

```
_aNFoodZooEpi_ =  _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ _cPrefDiat_*_aNDiatWEpi_ + _cPrefGren_*_aNGrenWEpi_ + _cPrefBlue_*_aNBlueWEpi_ + _cPrefDet_ * _aNDetWEpi_ _ELSE_ _cPrefDiat_*_aNDiatWEpi_ + _cPrefGren_*_aNGrenWEpi_ + _cPrefBlue_*_aNBlueWEpi_ + _cPrefBlueSurf_*_aNBlueSurf_ + _cPrefDet_ * _aNDetWEpi_ _ENDIF_
```

### `_oNFoodZooEpi_`  [_gN_*_m_^-3]
- **Description**: Zooplankton_food
- **Equation**:

```
_oNFoodZooEpi_ = _aNFoodZooEpi_ / _MassEpi_
```

### `_rNDFoodZooEpi_`  [_gN_*_gDW_^-1]
- **Description**: N/C_ratio_of_zooplankton_food
- **Equation**:

```
_rNDFoodZooEpi_ = _oNFoodZooEpi_ /(_oDFoodZooEpi_+_NearZero_)
```

### `_wNConsDiatZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_diatom_consumption_by_zooplankton
- **Equation**:

```
_wNConsDiatZooEpi_ = _rNDDiatWEpi_*_wDConsDiatZooEpi_
```

### `_wNConsGrenZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_green_consumption_by_zooplankton
- **Equation**:

```
_wNConsGrenZooEpi_ = _rNDGrenWEpi_*_wDConsGrenZooEpi_
```

### `_wNConsBlueZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_blue_green_consumption_by_zooplankton
- **Equation**:

```
_wNConsBlueZooEpi_ = _rNDBlueWEpi_*_wDConsBlueZooEpi_
```

### `_wNConsBlueZooSurf_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_bluegreen_consumption_by_zoopl
- **Equation**:

```
_wNConsBlueZooSurf_ = _rNDBlueSurf_ * _wDConsBlueZooSurf_
```

### `_tNConsBlueZooSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_bluegreen_consumption_by_zoopl
- **Equation**:

```
_tNConsBlueZooSurf_ = _wNConsBlueZooSurf_ *_uDepthWEpi_
```

### `_wNConsPhytZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_phytoplankton_consumption_by_zooplankton
- **Equation**:

```
_wNConsPhytZooEpi_ = _IF_ (_InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_  _wNConsDiatZooEpi_ + _wNConsGrenZooEpi_ + _wNConsBlueZooEpi_ _ELSE_ _wNConsDiatZooEpi_ + _wNConsGrenZooEpi_ + _wNConsBlueZooEpi_ + _wNConsBlueZooSurf_ _ENDIF_
```

### `_wNConsDetZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_detrital_N
- **Equation**:

```
_wNConsDetZooEpi_ = _rNDDetWEpi_*_wDConsDetZooEpi_
```

### `_wNConsZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_N_consumption
- **Equation**:

```
_wNConsZooEpi_ = _wNConsPhytZooEpi_ + _wNConsDetZooEpi_
```

### `_afNAssZooEpi_`  [0]
- **Description**: N_assimilation_efficiency_of_herbivores
- **Equation**:

```
_afNAssZooEpi_ = _MIN_(1.0,_cNDZooRef_ / _rNDFoodZooEpi_ * _fDAssZoo_)
```

### `_wNAssZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Assimilation_by_herbivores
- **Equation**:

```
_wNAssZooEpi_ = _afNAssZooEpi_*_wNConsZooEpi_
```

### `_wNEgesZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_egestion
- **Equation**:

```
_wNEgesZooEpi_ = _wNConsZooEpi_ - _wNAssZooEpi_
```

### `_wNEgesZooNH4Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Soluble_N_egestion
- **Equation**:

```
_wNEgesZooNH4Epi_ = _fDissEgesZoo_*_wNEgesZooEpi_
```

### `_wNEgesZooDetEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_egestion
- **Equation**:

```
_wNEgesZooDetEpi_ = _wNEgesZooEpi_ - _wNEgesZooNH4Epi_
```

### `_kNExcrZooEpi_`  [_d_^-1]
- **Description**: N_excretion_rate_of_herbivores
- **Equation**:

```
_kNExcrZooEpi_ = _rNDZooEpi_ / _cNDZooRef_ * _kDRespZoo_ * _uFunTmZooEpi_
```

### `_wNExcrZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: N_excretion
- **Equation**:

```
_wNExcrZooEpi_ = _kNExcrZooEpi_*_oNZooEpi_
```

### `_wNMortZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Mortality
- **Equation**:

```
_wNMortZooEpi_ = _rNDZooEpi_*_wDMortZooEpi_
```

### `_wNMortZooNH4Epi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Soluble_N_mortality
- **Equation**:

```
_wNMortZooNH4Epi_ = _fDissMortZoo_*_wNMortZooEpi_
```

### `_wNMortZooDetEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Detrital_N_mortality
- **Equation**:

```
_wNMortZooDetEpi_ = _wNMortZooEpi_ - _wNMortZooNH4Epi_
```

### `_wSiConsDiatZooEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Consumption_of_diatoms
- **Equation**:

```
_wSiConsDiatZooEpi_ = _cSiDDiat_ * _wDConsDiatZooEpi_
```

## Zoobenthal_processes  (56 equations)

### `_uFunTmBent_`  [0]
- **Description**: Temp_function_of_zoobenthos
- **Equation**:

```
_uFunTmBent_ = _EXP_(-0.5/(_cSigTmBent_*_cSigTmBent_) *((_uTmBot_-_cTmOptBent_)*(_uTmBot_-_cTmOptBent_) - (_cTmRef_-_cTmOptBent_)*(_cTmRef_-_cTmOptBent_)))
```

### `_aDFoodBent_`  [_gDW_*_m_^-2]
- **Description**: Food_for_zoobenthos
- **Equation**:

```
_aDFoodBent_ = _aDDetS_ + _aDPhytS_
```

### `_rPDBent_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_zoobenthos
- **Equation**:

```
_rPDBent_ = _aPBent_ /(_aDBent_+_NearZero_)
```

### `_rNDBent_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_zoobenthos
- **Equation**:

```
_rNDBent_ = _aNBent_ /(_aDBent_+_NearZero_)
```

### `_tDMigrBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Migration_flux
- **Equation**:

```
_tDMigrBent_ = _kMigrBent_ *(_cDBentIn_ - _aDBent_)
```

### `_aDSatBent_`  [0]
- **Description**: Food_limitation_function_of_zoobenthos
- **Equation**:

```
_aDSatBent_ = _aDFoodBent_ /(_hDFoodBent_ + _aDFoodBent_)
```

### `_ukDIncrBent_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_zoobenthos
- **Equation**:

```
_ukDIncrBent_ = (_kDAssBent_ - _kDRespBent_) * _uFunTmBent_ - _kMortBent_
```

### `_tDEnvBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Environmental_correction_of_zoobenthos
- **Equation**:

```
_tDEnvBent_ = _MAX_(0.0,_ukDIncrBent_ / _cDCarrBent_ * _aDBent_*_aDBent_)
```

### `_tDAssBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Assimilation_of_zoobenthos
- **Equation**:

```
_tDAssBent_ = _aDSatBent_ *(_kDAssBent_ * _uFunTmBent_ * _aDBent_ - _tDEnvBent_)
```

### `_aDAssBentSp_`  [_d_^-1]
- **Description**: Specific_assimilation_rate_of_zoobenthos
- **Equation**:

```
_aDAssBentSp_ = _tDAssBent_ / _aDBent_
```

### `_tDConsBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Consumption_of_zoobenthos
- **Equation**:

```
_tDConsBent_ = _tDAssBent_ / _fDAssBent_
```

### `_tDConsDetBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Detritus_consumption_by_zoobenthos
- **Equation**:

```
_tDConsDetBent_ = _aDDetS_ / _aDFoodBent_ * _tDConsBent_
```

### `_tDConsDiatBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Diatoms_consumption_by_zoobenthos
- **Equation**:

```
_tDConsDiatBent_ = _aDDiatS_ / _aDFoodBent_ * _tDConsBent_
```

### `_tDConsGrenBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Greens_consumption_by_zoobenthos
- **Equation**:

```
_tDConsGrenBent_ = _aDGrenS_ / _aDFoodBent_ * _tDConsBent_
```

### `_tDConsBlueBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Blue-greens_consumption_by_zoobenthos
- **Equation**:

```
_tDConsBlueBent_ = _aDBlueS_ / _aDFoodBent_ * _tDConsBent_
```

### `_tDConsPhytBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Phytoplankton_consumption_by_zoobenthos
- **Equation**:

```
_tDConsPhytBent_ = _tDConsDiatBent_ + _tDConsGrenBent_ + _tDConsBlueBent_
```

### `_tDEgesBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_zoobenthos
- **Equation**:

```
_tDEgesBent_ = _tDConsBent_ - _tDAssBent_
```

### `_tDRespBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_zoobenthos
- **Equation**:

```
_tDRespBent_ = (_cPDBentRef_ / _rPDBent_) * _kDRespBent_ * _uFunTmBent_ * _aDBent_
```

### `_tDMortBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Zoobenthos_mortality_incl_environmental_correction
- **Equation**:

```
_tDMortBent_ = _kMortBent_*_aDBent_ +(1.0 - _aDSatBent_) * _tDEnvBent_
```

### `_aPFoodBent_`  [_gP_*_m_^-2]
- **Description**: Food_for_zoobenthos
- **Equation**:

```
_aPFoodBent_ = _aPDetS_ + _aPPhytS_
```

### `_rPDFoodBent_`  [_gP_*_gDW_^-1]
- **Description**: Average_P/D_ratio_of_zoobenthos_food
- **Equation**:

```
_rPDFoodBent_ = _aPFoodBent_ /(_aDFoodBent_+_NearZero_)
```

### `_tPConsDetBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_consumption_by_zoobenthos
- **Equation**:

```
_tPConsDetBent_ = _rPDDetS_ * _tDConsDetBent_
```

### `_tPConsDiatBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Diatom_P_consumption_by_zoobenthos
- **Equation**:

```
_tPConsDiatBent_ = _rPDDiatS_ * _tDConsDiatBent_
```

### `_tPConsGrenBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Greens_P_consumption_by_zoobenthos
- **Equation**:

```
_tPConsGrenBent_ = _rPDGrenS_ * _tDConsGrenBent_
```

### `_tPConsBlueBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Blue-greens_P_consumption_by_zoobenthos
- **Equation**:

```
_tPConsBlueBent_ = _rPDBlueS_ * _tDConsBlueBent_
```

### `_tPConsPhytBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Phytoplankton_P_consumption_by_zoobenthos
- **Equation**:

```
_tPConsPhytBent_ = _tPConsDiatBent_ + _tPConsGrenBent_ + _tPConsBlueBent_
```

### `_tPConsBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_consumption_of_zoobenthos
- **Equation**:

```
_tPConsBent_ = _tPConsDetBent_ + _tPConsPhytBent_
```

### `_afPAssBent_`  [0]
- **Description**: P_assimilation_efficiency_of_zoobenthos
- **Equation**:

```
_afPAssBent_ = _MIN_(1.0,_cPDBentRef_ / _rPDFoodBent_ * _fDAssBent_)
```

### `_tPAssBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_of_zoobenthos
- **Equation**:

```
_tPAssBent_ = _afPAssBent_ * _tPConsBent_
```

### `_tPEgesBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_zoobenthos
- **Equation**:

```
_tPEgesBent_ = _tPConsBent_ - _tPAssBent_
```

### `_tPEgesBentPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_egestion_of_zoobenthos
- **Equation**:

```
_tPEgesBentPO4_ = _fDissEgesBent_ * _tPEgesBent_
```

### `_tPEgesBentDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_egestion_of_zoobenthos
- **Equation**:

```
_tPEgesBentDet_ = (1.0 - _fDissEgesBent_) * _tPEgesBent_
```

### `_tPExcrBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_zoobenthos
- **Equation**:

```
_tPExcrBent_ = (_rPDBent_ / _cPDBentRef_) * _kDRespBent_ * _uFunTmBent_ * _aPBent_
```

### `_tPMortBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_zoobenthos
- **Equation**:

```
_tPMortBent_ = _rPDBent_ * _tDMortBent_
```

### `_tPMortBentPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_died_zoobenthos_P_becoming_dissolved_P
- **Equation**:

```
_tPMortBentPO4_ = _fDissMortBent_ * _tPMortBent_
```

### `_tPMortBentDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_died_zoobenthos_P_becoming_detrital_P
- **Equation**:

```
_tPMortBentDet_ = (1.0-_fDissMortBent_)*_tPMortBent_
```

### `_tPMigrBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tPMigrBent_ = _kMigrBent_ *(_cPDBentRef_*_cDBentIn_ - _aPBent_)
```

### `_aNFoodBent_`  [_gN_*_m_^-2]
- **Description**: Food_for_zoobenthos
- **Equation**:

```
_aNFoodBent_ = _aNDetS_ + _aNPhytS_
```

### `_rNDFoodBent_`  [_gN_*_gDW_^-1]
- **Description**: Average_N/D_ratio_of_zoobenthos_food
- **Equation**:

```
_rNDFoodBent_ = _aNFoodBent_ /(_aDFoodBent_+_NearZero_)
```

### `_tNMigrBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tNMigrBent_ = _kMigrBent_ *(_cNDBentRef_*_cDBentIn_ - _aNBent_)
```

### `_tNConsDetBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_N_consumption_by_zoobenthos
- **Equation**:

```
_tNConsDetBent_ = _rNDDetS_ * _tDConsDetBent_
```

### `_tNConsDiatBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Diatom_N_consumption_by_zoobenthos
- **Equation**:

```
_tNConsDiatBent_ = _rNDDiatS_ * _tDConsDiatBent_
```

### `_tNConsGrenBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Greens_N_consumption_by_zoobenthos
- **Equation**:

```
_tNConsGrenBent_ = _rNDGrenS_ * _tDConsGrenBent_
```

### `_tNConsBlueBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Blue-greens_N_consumption_by_zoobenthos
- **Equation**:

```
_tNConsBlueBent_ = _rNDBlueS_ * _tDConsBlueBent_
```

### `_tNConsPhytBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Phytoplankton_N_consumption_by_zoobenthos
- **Equation**:

```
_tNConsPhytBent_ = _tNConsDiatBent_ + _tNConsGrenBent_ + _tNConsBlueBent_
```

### `_tNConsBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_consumption_of_zoobenthos
- **Equation**:

```
_tNConsBent_ = _tNConsDetBent_ + _tNConsPhytBent_
```

### `_afNAssBent_`  [0]
- **Description**: N_assimilation_efficiency_of_zoobenthos
- **Equation**:

```
_afNAssBent_ = _MIN_(1.0,_cNDBentRef_ / _rNDFoodBent_ * _fDAssBent_)
```

### `_tNAssBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_of_zoobenthos
- **Equation**:

```
_tNAssBent_ = _afNAssBent_ * _tNConsBent_
```

### `_tNEgesBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_zoobenthos
- **Equation**:

```
_tNEgesBent_ = _tNConsBent_ - _tNAssBent_
```

### `_tNEgesBentNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_egestion_of_zoobenthos
- **Equation**:

```
_tNEgesBentNH4_ = _fDissEgesBent_ * _tNEgesBent_
```

### `_tNEgesBentDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_N_egestion_of_zoobenthos
- **Equation**:

```
_tNEgesBentDet_ = (1.0 - _fDissEgesBent_) * _tNEgesBent_
```

### `_tNExcrBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_zoobenthos
- **Equation**:

```
_tNExcrBent_ = (_rNDBent_ / _cNDBentRef_) * _kDRespBent_ * _uFunTmBent_ * _aNBent_
```

### `_tNMortBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_zoobenthos
- **Equation**:

```
_tNMortBent_ = _rNDBent_ * _tDMortBent_
```

### `_tNMortBentNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_died_zoobenthos_N_becoming_ammonium-N
- **Equation**:

```
_tNMortBentNH4_ = _fDissMortBent_*_tNMortBent_
```

### `_tNMortBentDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_died_zoobenthos_N_becoming_detrital_N
- **Equation**:

```
_tNMortBentDet_ = (1.0-_fDissMortBent_)*_tNMortBent_
```

### `_tSiConsDiatBent_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Diatom_consumption_by_zoobenthos
- **Equation**:

```
_tSiConsDiatBent_ = _cSiDDiat_ * _tDConsDiatBent_
```

## Bentfish_processes  (9 equations)

### `_aFunVegFish_`  [0]
- **Description**: Vegetation_dependence_of_fish_feeding
- **Equation**:

```
_aFunVegFish_ = _MAX_(0.0,1.0 - _cRelVegFish_ * _aCovVeg_)
```

### `_rPDFiJv_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_young_fish
- **Equation**:

```
_rPDFiJv_ = _aPFiJv_ /(_aDFiJv_+_NearZero_)
```

### `_rPDFiAd_`  [_gP_*_gDW_^-1]
- **Description**: P/D_ratio_of_adult_fish
- **Equation**:

```
_rPDFiAd_ = _aPFiAd_ /(_aDFiAd_+_NearZero_)
```

### `_rNDFiJv_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_young_fish
- **Equation**:

```
_rNDFiJv_ = _aNFiJv_ /(_aDFiJv_+_NearZero_)
```

### `_rNDFiAd_`  [_gN_*_gDW_^-1]
- **Description**: N/D_ratio_of_adult_fish
- **Equation**:

```
_rNDFiAd_ = _aNFiAd_ /(_aDFiAd_+_NearZero_)
```

### `_tDReprFish_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Reproduction_flux
- **Equation**:

```
_tDReprFish_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ ((1/_DaysInYear_)*_fReprFish_) * _aDFiAd_ _ELSEIF_ (_Day_ _GE_ _cDayReprFish_ _AND_ _Day_ _LT_ _cDayReprFish_ + 1.0) _THEN_ _fReprFish_ * _aDFiAd_ * _PerDay_ _ELSE_ 0.0 _ENDIF_
```

### `_aDFish_`  [_gDW_*_m_^-2]
- **Description**: Total_fish_biomass
- **Equation**:

```
_aDFish_ = _aDFiJv_ + _aDFiAd_
```

### `_aPFish_`  [_gP_*_m_^-2]
- **Description**: Total_fish_biomass
- **Equation**:

```
_aPFish_ = _aPFiJv_ + _aPFiAd_
```

### `_aNFish_`  [_gN_*_m_^-2]
- **Description**: Total_fish_biomass
- **Equation**:

```
_aNFish_ = _aNFiJv_ + _aNFiAd_
```

## Bentfish_processes_in_juvinile_fish  (12 equations)

### `_ukDIncrFiJv_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_fish
- **Equation**:

```
_ukDIncrFiJv_ = (_kDAssFiJv_ - _kDRespFiJv_) * _uFunTmFish_ - _kMortFiJv_
```

### `_aDTotZoo_`  [_gDW_*_m_^-2]
- **Description**: Food_limitation_function_of_young_fish
- **Equation**:

```
_aDTotZoo_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _oDZooEpi_ * _uDepthWEpi_ _ELSE_ _oDZooEpi_ * _uDepthWEpi_ + _oDZooHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_aPTotZoo_`  [_gP_*_m_^-2]
- **Description**: Food_limitation_function_of_young_fish
- **Equation**:

```
_aPTotZoo_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _oPZooEpi_ * _uDepthWEpi_ _ELSE_ _oPZooEpi_ * _uDepthWEpi_ + _oPZooHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_aNTotZoo_`  [_gN_*_m_^-2]
- **Description**: Food_limitation_function_of_young_fish
- **Equation**:

```
_aNTotZoo_ = _IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ _oNZooEpi_ * _uDepthWEpi_ _ELSE_ _oNZooEpi_ * _uDepthWEpi_ + _oNZooHyp_ * _uDepthWHyp_ _ENDIF_
```

### `_aDSatFiJv_`  [0]
- **Description**: Food_limitation_function_of_young_fish
- **Equation**:

```
_aDSatFiJv_ = _aDTotZoo_ * _aDTotZoo_ /(_hDZooFiJv_ * _hDZooFiJv_ + _aDTotZoo_ * _aDTotZoo_)
```

### `_tDEnvFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Environmental_correction_of_fish
- **Equation**:

```
_tDEnvFiJv_ = _MAX_(0.0,_ukDIncrFiJv_ /(_cDCarrFish_ - _aDFiAd_) * _aDFiJv_*_aDFiJv_)
```

### `_tDAssFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Assimilation_of_fish
- **Equation**:

```
_tDAssFiJv_ = _aDSatFiJv_ *(_kDAssFiJv_ * _uFunTmFish_ * _aDFiJv_ - _tDEnvFiJv_)
```

### `_tDConsFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Zooplankton_consumption_of_fish
- **Equation**:

```
_tDConsFiJv_ = _tDAssFiJv_ / _fDAssFiJv_
```

### `_tDEgesFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_fish
- **Equation**:

```
_tDEgesFiJv_ = _tDConsFiJv_ - _tDAssFiJv_
```

### `_tDRespFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_fish
- **Equation**:

```
_tDRespFiJv_ = (_cPDFishRef_ / _rPDFiJv_) * _kDRespFiJv_ * _uFunTmFish_ * _aDFiJv_
```

### `_tDMortFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Fish_mortality_incl_environmental_correction
- **Equation**:

```
_tDMortFiJv_ = _kMortFiJv_ * _aDFiJv_ +(1.0 - _aDSatFiJv_) * _tDEnvFiJv_
```

### `_tDMigrFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Migration_flux
- **Equation**:

```
_tDMigrFiJv_ = _kMigrFish_ *(_cDFiJvIn_ - _aDFiJv_)
```

## Bentfish_processes_in_adult_fish  (11 equations)

### `_aDSatFiAd_`  [0]
- **Description**: Food_limitation_function_of_adult_fish
- **Equation**:

```
_aDSatFiAd_ = (_aFunVegFish_ * _aDBent_) *(_aFunVegFish_ * _aDBent_) /(_hDBentFiAd_ * _hDBentFiAd_ + (_aFunVegFish_ * _aDBent_) *(_aFunVegFish_ * _aDBent_))
```

### `_ukDIncrFiAd_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_fish
- **Equation**:

```
_ukDIncrFiAd_ = (_kDAssFiAd_ - _kDRespFiAd_) * _uFunTmFish_ - _kMortFiAd_
```

### `_ukHarvFish_`  [_d_^-1]
- **Description**: Fish_harvesting_constant
- **Equation**:

```
_ukHarvFish_ = _IF_ (_COS_(2.0 * _Pi_ * _sTime_ / _DaysInYear_) _GT_ 0.1) _THEN_ _kHarvFishWin_ _ELSE_ _kHarvFishSum_ _ENDIF_
```

### `_tDEnvFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Environmental_correction_of_fish
- **Equation**:

```
_tDEnvFiAd_ = _MAX_(0.0,_ukDIncrFiAd_ /(_cDCarrFish_ - _aDFiJv_) * _aDFiAd_*_aDFiAd_)
```

### `_tDAssFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Assimilation_of_fish
- **Equation**:

```
_tDAssFiAd_ = _aDSatFiAd_ *(_kDAssFiAd_ * _uFunTmFish_ * _aDFiAd_ - _tDEnvFiAd_)
```

### `_tDConsFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Zoobenthos_consumption_of_fish
- **Equation**:

```
_tDConsFiAd_ = _tDAssFiAd_ / _fDAssFiAd_
```

### `_tDEgesFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_fish
- **Equation**:

```
_tDEgesFiAd_ = _tDConsFiAd_ - _tDAssFiAd_
```

### `_tDRespFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_fish
- **Equation**:

```
_tDRespFiAd_ = (_cPDFishRef_ / _rPDFiAd_) * _kDRespFiAd_ * _uFunTmFish_ * _aDFiAd_
```

### `_tDMortFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Fish_mortality_incl_environmental_correction
- **Equation**:

```
_tDMortFiAd_ = _kMortFiAd_ * _aDFiAd_ +(1.0 - _aDSatFiAd_) * _tDEnvFiAd_
```

### `_tDHarvFish_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_fish
- **Equation**:

```
_tDHarvFish_ = _ukHarvFish_ * _aDFiAd_
```

### `_tDMigrFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Migration_flux
- **Equation**:

```
_tDMigrFiAd_ = _kMigrFish_ *(_cDFiAdIn_ - _aDFiAd_)
```

## Fish_processes_of_adult_fish  (16 equations)

### `_afPAssFiAd_`  [0]
- **Description**: P_assimilation_efficiency_of_FiAd
- **Equation**:

```
_afPAssFiAd_ = _MIN_(1.0,_cPDFishRef_ / _rPDBent_ * _fDAssFiAd_)
```

### `_afNAssFiAd_`  [0]
- **Description**: N_assimilation_efficiency_of_FiAd
- **Equation**:

```
_afNAssFiAd_ = _MIN_(1.0,_cNDFishRef_ / _rNDBent_ * _fDAssFiAd_)
```

### `_tPMigrFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tPMigrFiAd_ = _kMigrFish_ *(_cPDFishRef_ * _cDFiAdIn_ - _aPFiAd_)
```

### `_tPConsFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: (zoobenthos)_P_consumption_by_FiAd
- **Equation**:

```
_tPConsFiAd_ = _rPDBent_ * _tDConsFiAd_
```

### `_tPAssFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_of_FiAd
- **Equation**:

```
_tPAssFiAd_ = _afPAssFiAd_ * _tPConsFiAd_
```

### `_tPEgesFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_FiAd
- **Equation**:

```
_tPEgesFiAd_ = _tPConsFiAd_ - _tPAssFiAd_
```

### `_tPExcrFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_FiAd
- **Equation**:

```
_tPExcrFiAd_ = (_rPDFiAd_ / _cPDFishRef_) * _kDRespFiAd_ * _uFunTmFish_ * _aPFiAd_
```

### `_tPMortFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_FiAd
- **Equation**:

```
_tPMortFiAd_ = _rPDFiAd_ * _tDMortFiAd_
```

### `_tPHarvFish_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_FiAd
- **Equation**:

```
_tPHarvFish_ = _rPDFiAd_ * _tDHarvFish_
```

### `_tNMigrFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tNMigrFiAd_ = _kMigrFish_ *(_cNDFishRef_ * _cDFiAdIn_ - _aNFiAd_)
```

### `_tNConsFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: (zoobenthos)_N_consumption_by_FiAd
- **Equation**:

```
_tNConsFiAd_ = _rNDBent_ * _tDConsFiAd_
```

### `_tNAssFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_of_FiAd
- **Equation**:

```
_tNAssFiAd_ = _afNAssFiAd_ * _tNConsFiAd_
```

### `_tNEgesFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_FiAd
- **Equation**:

```
_tNEgesFiAd_ = _tNConsFiAd_ - _tNAssFiAd_
```

### `_tNExcrFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_FiAd
- **Equation**:

```
_tNExcrFiAd_ = (_rNDFiAd_ / _cNDFishRef_) * _kDRespFiAd_ * _uFunTmFish_ * _aNFiAd_
```

### `_tNMortFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_FiAd
- **Equation**:

```
_tNMortFiAd_ = _rNDFiAd_ * _tDMortFiAd_
```

### `_tNHarvFish_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_FiAd
- **Equation**:

```
_tNHarvFish_ = _rNDFiAd_ * _tDHarvFish_
```

## Pisc_fish_processes  (62 equations)

### `_uFunTmPisc_`  [0]
- **Description**: Temp_function_of_Pisc
- **Equation**:

```
_uFunTmPisc_ = _EXP_(-0.5 /(_cSigTmPisc_*_cSigTmPisc_) *((_uTmEpi_ - _cTmOptPisc_)*(_uTmEpi_ - _cTmOptPisc_) - (_cTmRef_ - _cTmOptPisc_)*(_cTmRef_ - _cTmOptPisc_)))
```

### `_aDCarrPisc_`  [_gDW_*_m_^-2]
- **Description**: Carrying_capacity_of_Pisc_for_lake_without_OR_with_marsh_zone_respectively
- **Equation**:

```
_aDCarrPisc_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ _MAX_(_cDCarrPiscMin_,_MIN_(_cDCarrPiscMax_,_cDCarrPiscBare_)) _ELSEIF_ (_aDShootPhra_ _LT_ _cDPhraMinPisc_) _THEN_ _cDCarrPiscMin_ _ELSEIF_ (_aCovVeg_ _LT_ _cCovVegMin_) _THEN_ _MAX_(_cDCarrPiscMin_,_MIN_(_cDCarrPiscMax_,_fMarsh_ *(1.0/_PerCent_) * _cRelPhraPisc_)) _ELSE_ _MAX_(_cDCarrPiscMin_,_MIN_(_cDCarrPiscMax_,_fMarsh_ *(1.0/_PerCent_) *(_cRelPhraPisc_ + _cRelVegPisc_))) _ENDIF_
```

### `_aFunVegPisc_`  [0]
- **Description**: Vegetation_dependence_of_Pisc_growth_rate
- **Equation**:

```
_aFunVegPisc_ = _aDSubVeg_ /(_hDVegPisc_ + _aDSubVeg_ + _NearZero_)
```

### `_akDIncrPisc_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_Pisc
- **Equation**:

```
_akDIncrPisc_ = (_kDAssPisc_ * _aFunVegPisc_ - _kDRespPisc_) * _uFunTmPisc_ - _kMortPisc_
```

### `_ukHarvPisc_`  [_d_^-1]
- **Description**: Fish_harvesting_constant
- **Equation**:

```
_ukHarvPisc_ = _IF_ (_COS_(2.0*_Pi_ * _sTime_ / _DaysInYear_) _GT_ 0.1) _THEN_ _kHarvPiscWin_ _ELSE_ _kHarvPiscSum_ _ENDIF_
```

### `_tDMigrPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Migration_flux
- **Equation**:

```
_tDMigrPisc_ = _kMigrPisc_ *(_cDPiscIn_ - _aDPisc_)
```

### `_aDSatPisc_`  [0]
- **Description**: Food_limitation_function_of_Pisc
- **Equation**:

```
_aDSatPisc_ = _aDFish_*_aDFish_ /(_hDFishPisc_*_hDFishPisc_ + _aDFish_*_aDFish_)
```

### `_tDEnvPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Environmental_correction_of_Pisc
- **Equation**:

```
_tDEnvPisc_ = _MAX_(0.0,_akDIncrPisc_ / _aDCarrPisc_ * _aDPisc_*_aDPisc_)
```

### `_tDAssPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Assimilation_of_Pisc
- **Equation**:

```
_tDAssPisc_ = _aDSatPisc_ *(_kDAssPisc_ * _aFunVegPisc_ * _uFunTmPisc_ * _aDPisc_ - _tDEnvPisc_)
```

### `_tDConsPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Consumption_of_Pisc
- **Equation**:

```
_tDConsPisc_ = _tDAssPisc_ / _fDAssPisc_
```

### `_tDEgesPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_Pisc
- **Equation**:

```
_tDEgesPisc_ = _tDConsPisc_ - _tDAssPisc_
```

### `_tDConsFiJvPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc
- **Equation**:

```
_tDConsFiJvPisc_ = _aDFiJv_ / _aDFish_ * _tDConsPisc_
```

### `_tDConsFiAdPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc
- **Equation**:

```
_tDConsFiAdPisc_ = _tDConsPisc_ - _tDConsFiJvPisc_
```

### `_tDMortPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_Pisc(incl_environmental_correction)
- **Equation**:

```
_tDMortPisc_ = _kMortPisc_ * _aDPisc_ +(1.0 - _aDSatPisc_) * _tDEnvPisc_
```

### `_tDMortPiscBot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_DW_fixed_in_bones_AND_scales
- **Equation**:

```
_tDMortPiscBot_ = _fDBone_ * _tDMortPisc_
```

### `_tDMortPiscDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_Pisc_DW_becoming_detritus
- **Equation**:

```
_tDMortPiscDet_ = _tDMortPisc_ - _tDMortPiscBot_
```

### `_tDHarvPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_Pisc
- **Equation**:

```
_tDHarvPisc_ = _ukHarvPisc_ * _aDPisc_
```

### `_aPPisc_`  [_gP_*_m_^-2]
- **Description**: Piscivorous_fish
- **Equation**:

```
_aPPisc_ = _cPDPisc_ * _aDPisc_
```

### `_tPConsFiJvPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc
- **Equation**:

```
_tPConsFiJvPisc_ = _rPDFiJv_ * _tDConsFiJvPisc_
```

### `_tPConsFiAdPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc
- **Equation**:

```
_tPConsFiAdPisc_ = _rPDFiAd_ * _tDConsFiAdPisc_
```

### `_tPConsPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_consumption_by_Pisc
- **Equation**:

```
_tPConsPisc_ = _tPConsFiJvPisc_ + _tPConsFiAdPisc_
```

### `_rPDFoodPisc_`  [_gP_*_gDW_^-1]
- **Description**: Average_P/D_ratio_of_Pisc_food
- **Equation**:

```
_rPDFoodPisc_ = _tPConsPisc_ / _tDConsPisc_
```

### `_aNPisc_`  [_gN_*_m_^-2]
- **Description**: Piscivorous_fish
- **Equation**:

```
_aNPisc_ = _cNDPisc_ * _aDPisc_
```

### `_tNConsFiJvPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc
- **Equation**:

```
_tNConsFiJvPisc_ = _rNDFiJv_ * _tDConsFiJvPisc_
```

### `_tNConsFiAdPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc
- **Equation**:

```
_tNConsFiAdPisc_ = _rNDFiAd_ * _tDConsFiAdPisc_
```

### `_tNConsPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_consumption_by_Pisc
- **Equation**:

```
_tNConsPisc_ = _tNConsFiJvPisc_ + _tNConsFiAdPisc_
```

### `_rNDFoodPisc_`  [_gN_*_gDW_^-1]
- **Description**: Average_N/D_ratio_of_Pisc_food
- **Equation**:

```
_rNDFoodPisc_ = _tNConsPisc_ / _tDConsPisc_
```

### `_tDConsPiscNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Consumption_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDConsPiscNut_ = (_tDAssPisc_ / _fDAssPisc_) * _MAX_ (1.0, _cNDPisc_ / _rNDFoodPisc_ * _fDAssPisc_, _cPDPisc_ / _rPDFoodPisc_ * _fDAssPisc_)
```

### `_tDEgesPiscNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDEgesPiscNut_ = _tDConsPiscNut_ - _tDAssPisc_
```

### `_tDConsFiJvPiscNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDConsFiJvPiscNut_ = _aDFiJv_ / _aDFish_ * _tDConsPiscNut_
```

### `_tDConsFiAdPiscNut_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tDConsFiAdPiscNut_ = _tDConsPiscNut_ - _tDConsFiJvPiscNut_
```

### `_tPConsFiJvPiscNut_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc
- **Equation**:

```
_tPConsFiJvPiscNut_ = _rPDFiJv_ * _tDConsFiJvPiscNut_
```

### `_tPConsFiAdPiscNut_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc
- **Equation**:

```
_tPConsFiAdPiscNut_ = _rPDFiAd_ * _tDConsFiAdPiscNut_
```

### `_tPConsPiscNut_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_consumption_by_Pisc
- **Equation**:

```
_tPConsPiscNut_ = _tPConsFiJvPiscNut_ + _tPConsFiAdPiscNut_
```

### `_tNConsFiJvPiscNut_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Young_fish_consumption_by_Pisc
- **Equation**:

```
_tNConsFiJvPiscNut_ = _rNDFiJv_ * _tDConsFiJvPiscNut_
```

### `_tNConsFiAdPiscNut_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Adult_fish_consumption_by_Pisc
- **Equation**:

```
_tNConsFiAdPiscNut_ = _rNDFiAd_ * _tDConsFiAdPiscNut_
```

### `_tNConsPiscNut_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_consumption_by_Pisc
- **Equation**:

```
_tNConsPiscNut_ = _tNConsFiJvPiscNut_ + _tNConsFiAdPiscNut_
```

### `_afPAssPisc_`  [0]
- **Description**: P_assimilation_efficiency_of_Pisc
- **Equation**:

```
_afPAssPisc_ = _MIN_(1.0, ((_cPDPisc_ / _rPDFoodPisc_ * _fDAssPisc_) / (_tDConsPiscNut_ / _tDConsPisc_ )) )
```

### `_tPAssPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tPAssPisc_ = _afPAssPisc_ * _tPConsPiscNut_
```

### `_tPEgesPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tPEgesPisc_ = _tPConsPiscNut_ - _tPAssPisc_
```

### `_tPEgesPiscPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_egestion_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tPEgesPiscPO4_ = _fDissEgesPisc_ * _tPEgesPisc_
```

### `_tPEgesPiscDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_egestion_of_Pisc_corrected_for_N_and_P_limitation
- **Equation**:

```
_tPEgesPiscDet_ = _tPEgesPisc_ - _tPEgesPiscPO4_
```

### `_tDRespPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_Pisc
- **Equation**:

```
_tDRespPisc_ = _kDRespPisc_ * _uFunTmPisc_ * _aDPisc_
```

### `_tPExcrPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_Pisc
- **Equation**:

```
_tPExcrPisc_ = _cPDPisc_ * _tDRespPisc_
```

### `_tPMortPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_Pisc
- **Equation**:

```
_tPMortPisc_ = _cPDPisc_ * _tDMortPisc_
```

### `_tPMortPiscBot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_Pisc_P_fixed_in_bones_AND_scales
- **Equation**:

```
_tPMortPiscBot_ = _fPBone_ * _tPMortPisc_
```

### `_tPMortPiscPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_P_becoming_dissolved_P
- **Equation**:

```
_tPMortPiscPO4_ = _fDissMortPisc_ *(_tPMortPisc_ - _tPMortPiscBot_)
```

### `_tPMortPiscDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_Pisc_P_becoming_detrital_P
- **Equation**:

```
_tPMortPiscDet_ = _tPMortPisc_ - _tPMortPiscBot_ - _tPMortPiscPO4_
```

### `_tPMigrPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tPMigrPisc_ = _kMigrPisc_ *(_cPDPisc_ * _cDPiscIn_ - _aPPisc_)
```

### `_tPHarvPisc_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_Pisc
- **Equation**:

```
_tPHarvPisc_ = _cPDPisc_ * _tDHarvPisc_
```

### `_afNAssPisc_`  [0]
- **Description**: N_assimilation_efficiency_of_Pisc
- **Equation**:

```
_afNAssPisc_ = _MIN_(1.0, ((_cNDPisc_ / _rNDFoodPisc_ * _fDAssPisc_) / (_tDConsPiscNut_ / _tDConsPisc_ )) )
```

### `_tNAssPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_of_Pisc
- **Equation**:

```
_tNAssPisc_ = _afNAssPisc_ * _tNConsPiscNut_
```

### `_tNEgesPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_Pisc
- **Equation**:

```
_tNEgesPisc_ = _tNConsPiscNut_ - _tNAssPisc_
```

### `_tNEgesPiscNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: SRN_egestion_of_Pisc
- **Equation**:

```
_tNEgesPiscNH4_ = _fDissEgesPisc_ * _tNEgesPisc_
```

### `_tNEgesPiscDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_N_egestion_of_Pisc
- **Equation**:

```
_tNEgesPiscDet_ = _tNEgesPisc_ - _tNEgesPiscNH4_
```

### `_tNExcrPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Respiration_of_Pisc
- **Equation**:

```
_tNExcrPisc_ = _cNDPisc_ * _tDRespPisc_
```

### `_tNMortPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_Pisc
- **Equation**:

```
_tNMortPisc_ = _cNDPisc_ * _tDMortPisc_
```

### `_tNMortPiscBot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_Pisc_N_fixed_in_bones_AND_scales
- **Equation**:

```
_tNMortPiscBot_ = _fDBone_ * _tNMortPisc_
```

### `_tNMortPiscNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_N_becoming_dissolved_N
- **Equation**:

```
_tNMortPiscNH4_ = _fDissMortPisc_ *(_tNMortPisc_ - _tNMortPiscBot_)
```

### `_tNMortPiscDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_Pisc_N_becoming_detrital_N
- **Equation**:

```
_tNMortPiscDet_ = _tNMortPisc_ - _tNMortPiscBot_ - _tNMortPiscNH4_
```

### `_tNMigrPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tNMigrPisc_ = _kMigrPisc_ *(_cNDPisc_ * _cDPiscIn_ - _aNPisc_)
```

### `_tNHarvPisc_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Harvesting_of_Pisc
- **Equation**:

```
_tNHarvPisc_ = _cNDPisc_ * _tDHarvPisc_
```

## Total_fluxes_to/from_other_components  (75 equations)

### `_tDWebDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Sediment_detritus_in_lake
- **Equation**:

```
_tDWebDetS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tDConsDetBent_ + _tDEgesBent_ + _tDMortBent_ _ENDIF_
```

### `_tDWebDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_sediment_diatoms_in_lake
- **Equation**:

```
_tDWebDiatS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tDConsDiatBent_ _ENDIF_
```

### `_tDWebGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_sediment_greens_in_lake
- **Equation**:

```
_tDWebGrenS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tDConsGrenBent_ _ENDIF_
```

### `_tDWebBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_sediment_blue-greens_in_lake
- **Equation**:

```
_tDWebBlueS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tDConsBlueBent_ _ENDIF_
```

### `_tDWebPhytS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_sediment_algae
- **Equation**:

```
_tDWebPhytS_ = _tDWebDiatS_ + _tDWebGrenS_ + _tDWebBlueS_
```

### `_tPWebPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_pore_water_P_in_lake_sediment
- **Equation**:

```
_tPWebPO4S_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPExcrBent_ + _tPEgesBentPO4_ + _tPMortBentPO4_ _ENDIF_
```

### `_tPWebDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Sediment_P_in_lake
- **Equation**:

```
_tPWebDetS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tPConsDetBent_ + _tPEgesBentDet_ + _tPMortBentDet_ _ENDIF_
```

### `_tPWebDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_sediment_diatoms_in_lake
- **Equation**:

```
_tPWebDiatS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tPConsDiatBent_ _ENDIF_
```

### `_tPWebGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_sediment_greens_in_lake
- **Equation**:

```
_tPWebGrenS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tPConsGrenBent_ _ENDIF_
```

### `_tPWebBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_sediment_blue-greens_in_lake
- **Equation**:

```
_tPWebBlueS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tPConsBlueBent_ _ENDIF_
```

### `_tPWebPhytS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_sediment_algae
- **Equation**:

```
_tPWebPhytS_ = _tPWebDiatS_ + _tPWebGrenS_ + _tPWebBlueS_
```

### `_tNWebNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_pore_water_ammonium_in_lake_sediment
- **Equation**:

```
_tNWebNH4S_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNExcrBent_ + _tNEgesBentNH4_ + _tNMortBentNH4_ _ENDIF_
```

### `_tNWebNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_pore_water_nitrate_in_lake_sediment
- **Equation**:

```
_tNWebNO3S_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_tNWebDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Sediment_N_in_lake_sediment
- **Equation**:

```
_tNWebDetS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tNConsDetBent_ + _tNEgesBentDet_ + _tNMortBentDet_ _ENDIF_
```

### `_tNWebDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_sediment_diatoms_in_lake
- **Equation**:

```
_tNWebDiatS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tNConsDiatBent_ _ENDIF_
```

### `_tNWebGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_sediment_greens_in_lake
- **Equation**:

```
_tNWebGrenS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tNConsGrenBent_ _ENDIF_
```

### `_tNWebBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_sediment_blue-greens_in_lake
- **Equation**:

```
_tNWebBlueS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _tNConsBlueBent_ _ENDIF_
```

### `_tNWebPhytS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_sediment_algae
- **Equation**:

```
_tNWebPhytS_ = _tNWebDiatS_ + _tNWebGrenS_ + _tNWebBlueS_
```

### `_wSiWebSiO2W_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_silica_in_sio2_lake_water
- **Equation**:

```
_wSiWebSiO2W_ = 0.0
```

### `_wSiWebDetWHyp_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_silica_in_lake_water_detritus
- **Equation**:

```
_wSiWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wSiConsDiatZooHyp_ _ENDIF_
```

### `_tSiWebDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_silica_in_sediment_detritus
- **Equation**:

```
_tSiWebDetS_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tSiConsDiatBent_ _ENDIF_
```

### `_tSiWebTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_silica
- **Equation**:

```
_tSiWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_aPrefAveHyp_`  [0]
- **Description**: Average_selection_factor
- **Equation**:

```
_aPrefAveHyp_ = (_cPrefDiat_ * _oDDiatWHyp_ + _cPrefGren_ * _oDGrenWHyp_ + _cPrefBlue_ * _oDBlueWHyp_ + _cPrefDet_ * _oDDetWHyp_) / _oDOMWHyp_
```

### `_wDConsZoo2Hyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_zooplankton_consumption(check)
- **Equation**:

```
_wDConsZoo2Hyp_ =_IF_ (_aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _aFiltHyp_ * _aPrefAveHyp_ * _oDOMWHyp_ * _oDZooHyp_ _ENDIF_
```

### `_aDConsZooSpHyp_`  [_d_^-1]
- **Description**: Specific_consumption_rate_of_zooplankton(daily_ration)
- **Equation**:

```
_aDConsZooSpHyp_ = _wDConsZooHyp_ / _oDZooHyp_
```

### `_aDAssZooSpHyp_`  [_d_^-1]
- **Description**: Specific_C_assimilation_of_zooplankton
- **Equation**:

```
_aDAssZooSpHyp_ = _wDAssZooHyp_ / _oDZooHyp_
```

### `_aDGrazSpHyp_`  [_d_^-1]
- **Description**: Specific_DW_grazing(daily_grazing)
- **Equation**:

```
_aDGrazSpHyp_ = _wDConsZooHyp_ / _oDOMWHyp_
```

### `_aNConsZooSpHyp_`  [_d_^-1]
- **Description**: Specific_N_consumption_OR_daily_ration
- **Equation**:

```
_aNConsZooSpHyp_ = _wNConsZooHyp_ / _oNZooHyp_
```

### `_aNGrazSpHyp_`  [_d_^-1]
- **Description**: Specific_N_grazing_OR_daily_grazing
- **Equation**:

```
_aNGrazSpHyp_ = _wNConsZooHyp_ / _oNOMWHyp_
```

### `_aPConsZooSpHyp_`  [_d_^-1]
- **Description**: Specific_P_consumption_OR_daily_ration
- **Equation**:

```
_aPConsZooSpHyp_ = _wPConsZooHyp_ / _oPZooHyp_
```

### `_aPGrazSpHyp_`  [_d_^-1]
- **Description**: Specific_P_grazing_OR_daily_grazing
- **Equation**:

```
_aPGrazSpHyp_ = _wPConsZooHyp_ / _oPOMWHyp_
```

### `_wDWebDetWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Detritus_in_lake_water
- **Equation**:

```
_wDWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDetZooHyp_ + _wDEgesZooHyp_ + _wDMortZooHyp_ +(_tDEgesFiJv_ * _uFiJvEgesHyp_ + _tDEgesFiAd_ * _uFiAdEgesHyp_ + _tDMortFiJvDet_ * _uFiJvMortHyp_ + _tDMortFiAdDet_ * _uFiAdMortHyp_ + _tDEgesPiscNut_ * _uPiscEgesHyp_ + _tDMortPiscDet_ * _uPiscMortHyp_  + _tDEgesGras_ * _uGrasEgesHyp_ + _tDMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wDWebDiatWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Diatoms_in_lake_water
- **Equation**:

```
_wDWebDiatWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDiatZooHyp_ _ENDIF_
```

### `_wDWebGrenWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Greens_in_lake_water
- **Equation**:

```
_wDWebGrenWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsGrenZooHyp_ _ENDIF_
```

### `_wDWebBlueWHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Blue-greens_in_lake_water
- **Equation**:

```
_wDWebBlueWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsBlueZooHyp_ _ENDIF_
```

### `_wDWebDetWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Detritus_in_lake_water
- **Equation**:

```
_wDWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDetZooEpi_ + _wDEgesZooEpi_ + _wDMortZooEpi_ +(_tDEgesFiJv_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tDEgesFiAd_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tDMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tDMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ ) + _tDEgesPiscNut_ * ( 1.0 - _uPiscEgesHyp_ ) + _tDMortPiscDet_ * ( 1.0 - _uPiscMortHyp_) + _tDEgesGrasNut_ * ( 1.0 - _uGrasEgesHyp_ ) + _tDMortGrasDet_ * ( 1.0 - _uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_wDWebDiatWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Diatoms_in_lake_water
- **Equation**:

```
_wDWebDiatWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsDiatZooEpi_ _ENDIF_
```

### `_wDWebGrenWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Greens_in_lake_water
- **Equation**:

```
_wDWebGrenWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsGrenZooEpi_ _ENDIF_
```

### `_wDWebBlueWEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Blue-greens_in_lake_water
- **Equation**:

```
_wDWebBlueWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDConsBlueZooEpi_ _ENDIF_
```

### `_tDWebBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_foodweb_flux_of_DW_in_surface_blue-greens_in_lake
- **Equation**:

```
_tDWebBlueSurf_ = _IF_ (_InclWeb_ _EQ_ _FALSE_ _OR_ _InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ - _tDConsBlueZooSurf_ _ENDIF_
```

### `_tDWebTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_in_system
- **Equation**:

```
_tDWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wDRespZooEpi_ * _uDepthWEpi_ - _wDRespZooHyp_ * _uDepthWHyp_ + _tDMigrFiJv_ + _tDMigrFiAd_ + _tDMigrPisc_ + _tDMigrGras_ + _tDMigrBent_ - _tDRespFiJv_ - _tDRespFiAd_ - _tDRespPisc_ - _tDRespGras_ - _tDRespBent_ - _tDMortFiJvBot_ - _tDMortFiAdBot_- _tDMortPiscBot_ - _tDMortGrasBot_ - _tDHarvFish_ - _tDHarvPisc_ - _tDHarvGras_ _ENDIF_
```

### `_wPWebPO4WHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_SRP_in_water_in_lake_water
- **Equation**:

```
_wPWebPO4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wPExcrZooHyp_ + _wPEgesZooPO4Hyp_ + _wPMortZooPO4Hyp_ +(_tPExcrFiJv_ *_uFiJvExcrHyp_ + _tPExcrFiAd_ * _uFiAdExcrHyp_ + _tPEgesFiJvPO4_ * _uFiJvEgesHyp_ + _tPEgesFiAdPO4_ * _uFiAdEgesHyp_ + _tPMortFiJvPO4_ * _uFiJvMortHyp_ + _tPMortFiAdPO4_ * _uFiAdMortHyp_+ _tPExcrPisc_ * _uPiscExcrHyp_ + _tPEgesPiscPO4_ * _uPiscEgesHyp_ + _tPMortPiscPO4_ * _uPiscMortHyp_ + _tPExcrGras_ * _uGrasExcrHyp_ + _tPEgesGrasPO4_ * _uGrasEgesHyp_ + _tPMortGrasPO4_ * _uGrasMortHyp_ ) / _uDepthWHyp_ _ENDIF_
```

### `_wPWebDetWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Detritus_in_lake_water
- **Equation**:

```
_wPWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDetZooHyp_ + _wPEgesZooDetHyp_ + _wPMortZooDetHyp_ +(_tPEgesFiJvDet_ * _uFiJvEgesHyp_ + _tPEgesFiAdDet_ * _uFiAdEgesHyp_+ _tPMortFiJvDet_ * _uFiJvMortHyp_ + _tPMortFiAdDet_ * _uFiAdMortHyp_ + _tPEgesPiscDet_ * _uPiscEgesHyp_+ _tPMortPiscDet_ * _uPiscMortHyp_ + _tPEgesGrasDet_ * _uGrasEgesHyp_+ _tPMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wPWebDiatWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Diatoms_in_lake_water
- **Equation**:

```
_wPWebDiatWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDiatZooHyp_ _ENDIF_
```

### `_wPWebGrenWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Greens_in_lake_water
- **Equation**:

```
_wPWebGrenWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsGrenZooHyp_ _ENDIF_
```

### `_wPWebBlueWHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Blue-greens_in_lake_water
- **Equation**:

```
_wPWebBlueWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsBlueZooHyp_ _ENDIF_
```

### `_wPWebPO4WEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_SRP_in_water_in_lake_water
- **Equation**:

```
_wPWebPO4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wPExcrZooEpi_ + _wPEgesZooPO4Epi_ + _wPMortZooPO4Epi_ +(_tPExcrFiJv_ * ( 1.0 -_uFiJvExcrHyp_ ) + _tPExcrFiAd_ * ( 1.0 - _uFiAdExcrHyp_ )+ _tPEgesFiJvPO4_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tPEgesFiAdPO4_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tPMortFiJvPO4_ * ( 1.0 - _uFiJvMortHyp_ ) + _tPMortFiAdPO4_ * ( 1.0 - _uFiAdMortHyp_ )+ _tPExcrPisc_ * ( 1.0 - _uPiscExcrHyp_ ) + _tPEgesPiscPO4_ * ( 1.0 - _uPiscEgesHyp_ ) + _tPMortPiscPO4_ * ( 1.0 - _uPiscMortHyp_) + _tPExcrGras_ * ( 1.0 - _uGrasExcrHyp_ ) + _tPEgesGrasPO4_ * ( 1.0 - _uGrasEgesHyp_ ) + _tPMortGrasPO4_ * ( 1.0 - _uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_wPWebDetWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Detritus_in_lake_water
- **Equation**:

```
_wPWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDetZooEpi_ + _wPEgesZooDetEpi_ + _wPMortZooDetEpi_ +(_tPEgesFiJvDet_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tPEgesFiAdDet_ * ( 1.0 - _uFiAdEgesHyp_ )+ _tPMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tPMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ )+ _tPEgesPiscDet_ * ( 1.0 - _uPiscEgesHyp_ )+ _tPMortPiscDet_ * ( 1.0 - _uPiscMortHyp_ ) + _tPEgesGrasDet_ * ( 1.0 - _uGrasEgesHyp_ )+ _tPMortGrasDet_ * ( 1.0 - _uGrasMortHyp_ )) / _uDepthWEpi_ _ENDIF_
```

### `_wPWebDiatWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Diatoms_in_lake_water
- **Equation**:

```
_wPWebDiatWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsDiatZooEpi_ _ENDIF_
```

### `_wPWebGrenWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Greens_in_lake_water
- **Equation**:

```
_wPWebGrenWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsGrenZooEpi_ _ENDIF_
```

### `_wPWebBlueWEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Blue-greens_in_lake_water
- **Equation**:

```
_wPWebBlueWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wPConsBlueZooEpi_ _ENDIF_
```

### `_tPWebTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_in_system
- **Equation**:

```
_tPWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPMigrFiJv_ + _tPMigrFiAd_ + _tPMigrPisc_ + _tPMigrGras_ + _tPMigrBent_ - _tPMortFiJvBot_ - _tPMortFiAdBot_- _tPMortPiscBot_ - _tPMortGrasBot_ - _tPHarvFish_ - _tPHarvPisc_ - _tPHarvGras_ _ENDIF_
```

### `_wNWebNO3WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_nitrate_in_water_in_lake_water
- **Equation**:

```
_wNWebNO3WHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_wNWebNO3WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_nitrate_in_water_in_lake_water
- **Equation**:

```
_wNWebNO3WEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ 0.0 _ENDIF_
```

### `_wNWebNH4WHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_ammonium_in_water_in_lake_water
- **Equation**:

```
_wNWebNH4WHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wNExcrZooHyp_ + _wNEgesZooNH4Hyp_ + _wNMortZooNH4Hyp_ +(_tNExcrFiJv_ * _uFiJvExcrHyp_ + _tNExcrFiAd_ * _uFiAdExcrHyp_ + _tNEgesFiJvNH4_ * _uFiJvEgesHyp_+ _tNEgesFiAdNH4_ * _uFiAdEgesHyp_ + _tNMortFiAdNH4_ *_uFiAdMortHyp_+ _tNMortFiJvNH4_*_uFiJvMortHyp_ + _tNExcrPisc_ *_uPiscExcrHyp_ + _tNEgesPiscNH4_ *_uPiscEgesHyp_ + _tNMortPiscNH4_ *_uPiscMortHyp_ + _tNExcrGras_ *_uGrasExcrHyp_ + _tNEgesGrasNH4_ *_uGrasEgesHyp_ + _tNMortGrasNH4_ *_uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wNWebDetWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Detritus_in_lake_water
- **Equation**:

```
_wNWebDetWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDetZooHyp_ + _wNEgesZooDetHyp_ + _wNMortZooDetHyp_ +(_tNEgesFiJvDet_ * _uFiJvEgesHyp_ +_tNEgesFiAdDet_ * _uFiAdEgesHyp_+ _tNMortFiJvDet_ * _uFiJvMortHyp_ + _tNMortFiAdDet_ * _uFiAdMortHyp_ + _tNEgesPiscDet_ * _uPiscEgesHyp_ + _tNMortPiscDet_ * _uPiscMortHyp_ + _tNEgesGrasDet_ * _uGrasEgesHyp_ + _tNMortGrasDet_ * _uGrasMortHyp_) / _uDepthWHyp_ _ENDIF_
```

### `_wNWebDiatWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Diatoms_in_lake_water
- **Equation**:

```
_wNWebDiatWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDiatZooHyp_ _ENDIF_
```

### `_wNWebGrenWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Greens_in_lake_water
- **Equation**:

```
_wNWebGrenWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsGrenZooHyp_ _ENDIF_
```

### `_wNWebBlueWHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Blue-greens_in_lake_water
- **Equation**:

```
_wNWebBlueWHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsBlueZooHyp_ _ENDIF_
```

### `_wNWebNH4WEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_ammonium_in_water_in_lake_water
- **Equation**:

```
_wNWebNH4WEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wNExcrZooEpi_ + _wNEgesZooNH4Epi_ + _wNMortZooNH4Epi_ +(_tNExcrFiJv_ * ( 1.0 - _uFiJvExcrHyp_) + _tNExcrFiAd_ * ( 1.0 - _uFiAdExcrHyp_) + _tNEgesFiJvNH4_ * ( 1.0 - _uFiJvEgesHyp_ ) + _tNEgesFiAdNH4_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tNMortFiAdNH4_ * ( 1.0 -_uFiAdMortHyp_ ) + _tNMortFiJvNH4_* ( 1.0 -_uFiJvMortHyp_) + _tNExcrPisc_ * ( 1.0 -_uPiscExcrHyp_ ) + _tNEgesPiscNH4_ * ( 1.0 -_uPiscEgesHyp_ ) + _tNMortPiscNH4_ * ( 1.0 -_uPiscMortHyp_) + _tNExcrGras_ * ( 1.0 -_uGrasExcrHyp_ ) + _tNEgesGrasNH4_ * ( 1.0 -_uGrasEgesHyp_ ) + _tNMortGrasNH4_ * ( 1.0 -_uGrasMortHyp_)) / _uDepthWEpi_ _ENDIF_
```

### `_wNWebDetWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Detritus_in_lake_water
- **Equation**:

```
_wNWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDetZooEpi_ + _wNEgesZooDetEpi_ + _wNMortZooDetEpi_ +(_tNEgesFiJvDet_ * ( 1.0 - _uFiJvEgesHyp_ ) +_tNEgesFiAdDet_ * ( 1.0 - _uFiAdEgesHyp_ ) + _tNMortFiJvDet_ * ( 1.0 - _uFiJvMortHyp_ ) + _tNMortFiAdDet_ * ( 1.0 - _uFiAdMortHyp_ ) + _tNEgesPiscDet_ * ( 1.0 - _uPiscEgesHyp_ ) + _tNMortPiscDet_ * ( 1.0 - _uPiscMortHyp_ ) + _tNEgesGrasDet_ * ( 1.0 - _uGrasEgesHyp_ ) + _tNMortGrasDet_ * ( 1.0 - _uGrasMortHyp_ )) / _uDepthWEpi_ _ENDIF_
```

### `_wNWebDiatWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Diatoms_in_lake_water
- **Equation**:

```
_wNWebDiatWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsDiatZooEpi_ _ENDIF_
```

### `_wNWebGrenWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Greens_in_lake_water
- **Equation**:

```
_wNWebGrenWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsGrenZooEpi_ _ENDIF_
```

### `_wNWebBlueWEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Blue-greens_in_lake_water
- **Equation**:

```
_wNWebBlueWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ - _wNConsBlueZooEpi_ _ENDIF_
```

### `_tNWebTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_in_system
- **Equation**:

```
_tNWebTotT_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNMigrFiJv_ + _tNMigrFiAd_ + _tNMigrPisc_ + _tNMigrGras_ + _tNMigrBent_ - _tNMortFiJvBot_- _tNMortFiAdBot_ - _tNMortPiscBot_ - _tNMortGrasBot_ - _tNHarvFish_ - _tNHarvPisc_ - _tNHarvGras_ _ENDIF_
```

### `_wSiWebDetWEpi_`  [_gSi_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_silica_in_lake_water_detritus
- **Equation**:

```
_wSiWebDetWEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wSiConsDiatZooEpi_ _ENDIF_
```

### `_aPrefAveEpi_`  [0]
- **Description**: Average_selection_factor
- **Equation**:

```
_aPrefAveEpi_ = (_cPrefDiat_ * _oDDiatWEpi_ + _cPrefGren_ * _oDGrenWEpi_ + _cPrefBlue_ * _oDBlueWEpi_ + _cPrefDet_ * _oDDetWEpi_) / _oDOMWEpi_
```

### `_wDConsZoo2Epi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_zooplankton_consumption(check)
- **Equation**:

```
_wDConsZoo2Epi_ = _aFiltEpi_ * _aPrefAveEpi_ * _oDOMWEpi_ * _oDZooEpi_
```

### `_aDConsZooSpEpi_`  [_d_^-1]
- **Description**: Specific_consumption_rate_of_zooplankton(daily_ration)
- **Equation**:

```
_aDConsZooSpEpi_ = _wDConsZooEpi_ / _oDZooEpi_
```

### `_aDAssZooSpEpi_`  [_d_^-1]
- **Description**: Specific_C_assimilation_of_zooplankton
- **Equation**:

```
_aDAssZooSpEpi_ = _wDAssZooEpi_ / _oDZooEpi_
```

### `_aDGrazSpEpi_`  [_d_^-1]
- **Description**: Specific_DW_grazing(daily_grazing)
- **Equation**:

```
_aDGrazSpEpi_ = _wDConsZooEpi_ / _oDOMWEpi_
```

### `_aPConsZooSpEpi_`  [_d_^-1]
- **Description**: Specific_P_consumption_OR_daily_ration
- **Equation**:

```
_aPConsZooSpEpi_ = _wPConsZooEpi_ / _oPZooEpi_
```

### `_aPGrazSpEpi_`  [_d_^-1]
- **Description**: Specific_P_grazing_OR_daily_grazing
- **Equation**:

```
_aPGrazSpEpi_ = _wPConsZooEpi_ / _oPOMWEpi_
```

### `_aNConsZooSpEpi_`  [_d_^-1]
- **Description**: Specific_N_consumption_OR_daily_ration
- **Equation**:

```
_aNConsZooSpEpi_ = _wNConsZooEpi_ / _oNZooEpi_
```

### `_aNGrazSpEpi_`  [_d_^-1]
- **Description**: Specific_N_grazing_OR_daily_grazing
- **Equation**:

```
_aNGrazSpEpi_ = _wNConsZooEpi_ / _oNOMWEpi_
```

## Marsh_vegetation  (57 equations)

### `_afDShootPhra_`  [0]
- **Description**: Shoot/total_-ratio
- **Equation**:

```
_afDShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDShootPhra_ /(_aDRootPhra_ + _aDShootPhra_) _ELSE_ 0.0 _ENDIF_
```

### `_rDSRPhra_`  [0]
- **Description**: Shoot/Root_-ratio
- **Equation**:

```
_rDSRPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDShootPhra_/_aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_rPDShootPhra_`  [_gP_*_gDW_^-1]
- **Description**: Shoot_P/D_-ratio
- **Equation**:

```
_rPDShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPShootPhra_/_aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_rNDShootPhra_`  [_gN_*_gDW_^-1]
- **Description**: Shoot_N/D_-ratio
- **Equation**:

```
_rNDShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNShootPhra_/_aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_rPDRootPhra_`  [_gP_*_gDW_^-1]
- **Description**: Root_P/D_-ratio
- **Equation**:

```
_rPDRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aPRootPhra_/_aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_rNDRootPhra_`  [_gN_*_gDW_^-1]
- **Description**: Root_N/D_-ratio
- **Equation**:

```
_rNDRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNRootPhra_/_aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_aLengShootPhra_`  [_m_]
- **Description**: Shoot_length_of_phragmites_marsh_vegetation
- **Equation**:

```
_aLengShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aDShootPhra_ / _cDStemPhra_ / _cDensStemPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_bDayInitPhra_`  [_d_]
- **Description**: Marks_start_of_root_allocation_to_shoot_of_phragmites
- **Equation**:

```
_bDayInitPhra_ = _IF_ (_Day_ _LT_ 1.0 _OR_ _sTime_ _LT_ _StartTime_ + 1.0) _THEN_ 367 _ELSEIF_ (_uTmEpi_ _GE_ _cTmInitPhra_ _AND_ _bDayInitPhra_ _GT_ 366) _THEN_ _Day_ _ELSE_ _bDayInitPhra_ _ENDIF_
```

### `_aDAllPhra_`  [_gDW_*_m_^-2]
- **Description**: Root_biomass_available_for_allocation_to_shoot
- **Equation**:

```
_aDAllPhra_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _bDayInitPhra_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LE_ _bDayInitPhra_ + 1.0 / _kDAllPhra_) _THEN_ _fDAllPhra_ * _aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDAllPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Allocation_flux
- **Equation**:

```
_tDAllPhra_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ 0.0 _ELSEIF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _bDayInitPhra_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LE_ _bDayInitPhra_ + 1.0 / _kDAllPhra_) _THEN_ _kDAllPhra_ * _aDAllPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNTransPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Translocation_of_N_initial_growth
- **Equation**:

```
_tNTransPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rNDRootPhra_ * _tDAllPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPTransPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Translocation_of_P_initial_growth
- **Equation**:

```
_tPTransPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rPDRootPhra_ * _tDAllPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_aVNUptPhraMaxCr_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: Max_uptake_rate_at_current_N/D_ratio_AND_temp
- **Equation**:

```
_aVNUptPhraMaxCr_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _MAX_(0.0,_cVNUptPhraMax_ * _POW_(_cQ10ProdPhra_ _POWOPERATOR_ (0.1 *(_uTmEpi_ - _cTmRef_))) *(_cNDPhraMax_ - _rNDRootPhra_) /(_cNDPhraMax_ - _cNDPhraMin_)) _ELSE_ 0.0 _ENDIF_
```

### `_ahNUptPhraS_`  [_gN_*_m_^-3]
- **Description**: Half-saturating_N_concentration
- **Equation**:

```
_ahNUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVNUptPhraMaxCr_ / _cAffNUptPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_aVNUptPhraS_`  [_gN_*_gDW_^-1*_d_^-1]
- **Description**: N_uptake_rate(by_roots)
- **Equation**:

```
_aVNUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVNUptPhraMaxCr_ * _oNDissSM_ /(_ahNUptPhraS_ + _oNDissSM_) _ELSE_ 0.0 _ENDIF_
```

### `_tNUptPhraS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_uptake_of_reed
- **Equation**:

```
_tNUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVNUptPhraS_ * _aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNUptNH4PhraS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_uptake_of_reed
- **Equation**:

```
_tNUptNH4PhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aNH4SM_ / _aNDissSM_ * _tNUptPhraS_ _ELSE_ 0.0 _ENDIF_
```

### `_tNUptNO3PhraS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NO3_uptake_of_reed
- **Equation**:

```
_tNUptNO3PhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNUptPhraS_ - _tNUptNH4PhraS_ _ELSE_ 0.0 _ENDIF_
```

### `_tNUptShootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_shoot
- **Equation**:

```
_tNUptShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _afDShootPhra_ * _tNUptPhraS_ _ELSE_ 0.0 _ENDIF_
```

### `_tNUptRootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_uptake_root
- **Equation**:

```
_tNUptRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNUptPhraS_ - _tNUptShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_aVPUptPhraMaxCr_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: Max_uptake_rate_at_current_P/D_ratio_AND_temp
- **Equation**:

```
_aVPUptPhraMaxCr_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _MAX_(0.0,_cVPUptPhraMax_ * _POW_(_cQ10ProdPhra_ _POWOPERATOR_ (0.1 *(_uTmEpi_ - _cTmRef_))) *(_cPDPhraMax_ - _rPDRootPhra_) /(_cPDPhraMax_ - _cPDPhraMin_)) _ELSE_ 0.0 _ENDIF_
```

### `_ahPUptPhraS_`  [_gP_*_m_^-3]
- **Description**: Half-saturating_P_concentration
- **Equation**:

```
_ahPUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVPUptPhraMaxCr_ / _cAffPUptPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_aVPUptPhraS_`  [_gP_*_gDW_^-1*_d_^-1]
- **Description**: P_uptake_rate(by_roots)
- **Equation**:

```
_aVPUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVPUptPhraMaxCr_ * _oPO4SM_ /(_ahPUptPhraS_ + _oPO4SM_) _ELSE_ 0.0 _ENDIF_
```

### `_tPUptPhraS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_uptake_of_reed
- **Equation**:

```
_tPUptPhraS_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aVPUptPhraS_ * _aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPUptShootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_shoot
- **Equation**:

```
_tPUptShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _afDShootPhra_ * _tPUptPhraS_ _ELSE_ 0.0 _ENDIF_
```

### `_tPUptRootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_uptake_root
- **Equation**:

```
_tPUptRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPUptPhraS_ - _tPUptShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_uFunTmProdPhra_`  [0]
- **Description**: Temperature_function_production_vegetation
- **Equation**:

```
_uFunTmProdPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _POW_(_cQ10ProdPhra_ _POWOPERATOR_ (0.1 *(_uTmEpi_ - _cTmRef_))) _ELSE_ 0.0 _ENDIF_
```

### `_ukDRespTmPhra_`  [_d_^-1]
- **Description**: Maintenance_respiration_rate_at_current_temperature
- **Equation**:

```
_ukDRespTmPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDRespPhra_ * _POW_(_cQ10RespPhra_ _POWOPERATOR_ (0.1 *(_uTmEpi_ - _cTmRef_))) _ELSE_ 0.0 _ENDIF_
```

### `_aMuPhotPhra_`  [_d_^-1]
- **Description**: Max_photosynthetic_rate_at_current_light_AND_temp
- **Equation**:

```
_aMuPhotPhra_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_aLengShootPhra_ _GE_ _uDepthWM_) _THEN_ _cMuPhraMax_ * _uFunTmProdPhra_ * _ufDay_ _ELSE_ 0.0 _ENDIF_
```

### `_aNLimProdPhra_`  [0]
- **Description**: Droop_function_N-limitation
- **Equation**:

```
_aNLimProdPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (1.0 - _cNDPhraMin_ / _rNDRootPhra_) * _cNDPhraMax_ /(_cNDPhraMax_ - _cNDPhraMin_) _ELSE_ 0.0 _ENDIF_
```

### `_aPLimProdPhra_`  [0]
- **Description**: Droop_function_P-limitation
- **Equation**:

```
_aPLimProdPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (1.0 - _cPDPhraMin_ / _rPDRootPhra_) * _cPDPhraMax_ /(_cPDPhraMax_ - _cPDPhraMin_) _ELSE_ 0.0 _ENDIF_
```

### `_aNutLimPhra_`  [0]
- **Description**: Nutrient_reduction_function
- **Equation**:

```
_aNutLimPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _MIN_(_aNLimProdPhra_,_aPLimProdPhra_) _ELSE_ 0.0 _ENDIF_
```

### `_aMuPhra_`  [_d_^-1]
- **Description**: Growth_rate
- **Equation**:

```
_aMuPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aMuPhotPhra_ * _aNutLimPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_akDIncrPhra_`  [_d_^-1]
- **Description**: Intrinsic_net_increase_rate_of_reed
- **Equation**:

```
_akDIncrPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aMuPhotPhra_ - _ukDRespTmPhra_ - _kDMortShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDDensPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Density_correction_of_reed
- **Equation**:

```
_tDDensPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _MAX_(0.0,_akDIncrPhra_ / _cDShootPhraMax_ * _aDShootPhra_ * _aDShootPhra_) _ELSE_ 0.0 _ENDIF_
```

### `_tDDensProdPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Density_correction_of_production
- **Equation**:

```
_tDDensProdPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aMuPhra_ / _cMuPhraMax_ * _tDDensPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDProdPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Production_of_reed
- **Equation**:

```
_tDProdPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _aMuPhra_ * _aDShootPhra_ - _tDDensProdPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDProdShootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Production_shoot_of_reed
- **Equation**:

```
_tDProdShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _afDShootPhra_ * _tDProdPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDProdRootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Production_root_of_reed
- **Equation**:

```
_tDProdRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDProdPhra_ - _tDProdShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDRespShootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Maintenance_respiration_shoot_of_reed
- **Equation**:

```
_tDRespShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _ukDRespTmPhra_ * _aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDRespRootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Maintenance_respiration_root_of_reed
- **Equation**:

```
_tDRespRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _ukDRespTmPhra_ * _aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2RespRootPhra_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Root_O2_respiration
- **Equation**:

```
_tO2RespRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _molO2molC_ * _cCPerDW_ * _tDRespRootPhra_ * _afOxySedM_ _ELSE_ 0.0 _ENDIF_
```

### `_tO2FlowPhra_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: O2_flux_to_sediment
- **Equation**:

```
_tO2FlowPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tO2RespRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_bDayRealPhra_`  [_d_]
- **Description**: Counter_for_winter_mode_of_phragmites
- **Equation**:

```
_bDayRealPhra_ = _IF_ (_Day_ _LT_ 180.0) _THEN_ 367 _ELSEIF_ (_ufDay_ _LE_ _fDayWin_ _AND_ _bDayRealPhra_ _GT_ 366) _THEN_ _Day_ _ELSE_ _bDayRealPhra_ _ENDIF_
```

### `_aDRealPhra_`  [_gDW_*_m_^-2]
- **Description**: Shoot_biomass_available_for_reallocation_to_root
- **Equation**:

```
_aDRealPhra_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _bDayRealPhra_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LE_ _bDayRealPhra_ + 1.0 / _kDRealPhra_) _THEN_ _fDRealPhra_ * _aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDRealPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Reallocation_of_D_per_day_at_end_of_growing_season
- **Equation**:

```
_tDRealPhra_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ 0.0 _ELSEIF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LT_ _bDayRealPhra_) _THEN_ 0.0 _ELSEIF_ (_Day_ _LE_ _bDayRealPhra_ + 1.0 / _kDRealPhra_) _THEN_ _kDRealPhra_ * _aDRealPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNRetrPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Retranslocation_of_N_end_growing_season
- **Equation**:

```
_tNRetrPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rNDShootPhra_ * _tDRealPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPRetrPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Retranslocation_of_P_end_growing_season
- **Equation**:

```
_tPRetrPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rPDShootPhra_ * _tDRealPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMortShootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_shoots
- **Equation**:

```
_tDMortShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMortShootPhra_ * _aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMortShootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_shoots
- **Equation**:

```
_tNMortShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rNDShootPhra_ * _tDMortShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPMortShootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_shoots
- **Equation**:

```
_tPMortShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rPDShootPhra_ * _tDMortShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDMortRootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_roots
- **Equation**:

```
_tDMortRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _kDMortRootPhra_ * _aDRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMortRootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_roots
- **Equation**:

```
_tNMortRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rNDRootPhra_ * _tDMortRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPMortRootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_roots
- **Equation**:

```
_tPMortRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _rPDRootPhra_ * _tDMortRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tDManShootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Loss_flux_of_biomass_by_management
- **Equation**:

```
_tDManShootPhra_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _GT_ _NearZero_) _THEN_ 0.0 _ELSEIF_ ((_Day_ _GE_ _cDayManPhra_) _AND_ (_Day_ _LT_ _cDayManPhra_ + 1.0)) _THEN_ _fManPhra_ * _aDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tNManShootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Loss_flux_of_N_through_management
- **Equation**:

```
_tNManShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDManShootPhra_ * _rNDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_tPManShootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Loss_flux_of_P_through_management
- **Equation**:

```
_tPManShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDManShootPhra_ * _rPDShootPhra_ _ELSE_ 0.0 _ENDIF_
```

## Burial_of_sediment  (23 equations)

### `_tDIMSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_inorganic_matter_in_sediment
- **Equation**:

```
_tDIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDSetIMM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDHumSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_sediment_humus_in_marsh
- **Equation**:

```
_tDHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fRefrDetS_ * _tDMinDetSM_ - _tDMinHumSM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDDetSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_sediment_detritus_in_marsh
- **Equation**:

```
_tDDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDSetDetM_ - _tDMinDetSM_ + _tDSetPhytM_ + _tDMortRootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_vDeltaSM_`  [_m_*_d_^-1]
- **Description**: Turnover_depth_in_marsh
- **Equation**:

```
_vDeltaSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (_tDIMSM_ / _cRhoIM_ +(_tDHumSM_ + _tDDetSM_) / _cRhoOM_)/(1.0 - _bPorS_) _ELSE_ 0.0 _ENDIF_
```

### `_tDBurIMM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_inorganic_matter_in_marsh
- **Equation**:

```
_tDBurIMM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ ((_tDHumSM_ + _tDDetSM_) +(_cRhoOM_ / _cRhoIM_) * _tDIMSM_) / ((_aDHumSM_ + _aDDetSM_) / _aDIMSM_ + _cRhoOM_ / _cRhoIM_) _ELSE_ ((_tDHumSM_ + _tDDetSM_) +(_cRhoOM_ / _cRhoIM_) * _tDIMSM_) / (_fDOrgSoil_ /(1.0 - _fDOrgSoil_) + _cRhoOM_ / _cRhoIM_) _ENDIF_
```

### `_tDBurOMM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_organic_matter_in_marsh
- **Equation**:

```
_tDBurOMM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ (_aDHumSM_ + _aDDetSM_) / _aDIMSM_ * _tDBurIMM_ _ELSE_ _fDOrgSoil_ /(1.0 - _fDOrgSoil_) * _tDBurIMM_ _ENDIF_
```

### `_tDBurDetM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_detritus_in_marsh
- **Equation**:

```
_tDBurDetM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _aDDetSM_ /(_aDHumSM_ + _aDDetSM_) * _tDBurOMM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDBurHumM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_humus_in_marsh
- **Equation**:

```
_tDBurHumM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _tDBurOMM_ - _tDBurDetM_ _ELSE_ _tDBurOMM_ _ENDIF_
```

### `_tDBurTotM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_burial_flux_in_marsh
- **Equation**:

```
_tDBurTotM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _tDBurIMM_ + _tDBurOMM_ _ELSE_ _tDBurIMM_ + _tDBurOMM_ _ENDIF_
```

### `_tPBurHumM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_in_humus_in_marsh
- **Equation**:

```
_tPBurHumM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _rPDHumSM_ * _tDBurHumM_ _ELSE_ _cPDSoilOM_ * _tDBurHumM_ _ENDIF_
```

### `_tPBurDetM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_in_detritus_in_marsh
- **Equation**:

```
_tPBurDetM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _rPDDetSM_ * _tDBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBurAIMM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_absorbed_onto_inorganic_matter_in_marsh
- **Equation**:

```
_tPBurAIMM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _aPAIMSM_ / _aDIMSM_ * _tDBurIMM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBurPO4M_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_P_in_marsh
- **Equation**:

```
_tPBurPO4M_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _aPO4SM_ *(_vDeltaSM_ / _cDepthSM_) _ELSE_ _cPO4Ground_ *(_bPorSM_ * _vDeltaSM_) _ENDIF_
```

### `_tPBurTotM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_burial_flux_in_marsh
- **Equation**:

```
_tPBurTotM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _tPBurDetM_ + _tPBurHumM_ + _tPBurAIMM_ + _tPBurPO4M_ _ELSE_ _tPBurHumM_ + _tPBurAIMM_ + _tPBurPO4M_ _ENDIF_
```

### `_tNBurHumM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_N_in_humus_in_marsh
- **Equation**:

```
_tNBurHumM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _rNDHumSM_ * _tDBurHumM_ _ELSE_ _cNDSoilOM_ * _tDBurHumM_ _ENDIF_
```

### `_tNBurDetM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_N_in_detritus_in_marsh
- **Equation**:

```
_tNBurDetM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _rNDDetSM_ * _tDBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBurNH4M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_NH4_in_marsh
- **Equation**:

```
_tNBurNH4M_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _aNH4SM_ *(_vDeltaSM_ / _cDepthSM_) _ELSE_ _cNH4Ground_ *(_bPorSM_ * _vDeltaSM_) _ENDIF_
```

### `_tNBurNO3M_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_NO3_in_marsh
- **Equation**:

```
_tNBurNO3M_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _aNO3SM_ *(_vDeltaSM_ / _cDepthSM_) _ELSE_ _cNO3Ground_ *(_bPorSM_ * _vDeltaSM_) _ENDIF_
```

### `_tNBurTotM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_burial_flux_in_marsh
- **Equation**:

```
_tNBurTotM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _tNBurDetM_ + _tNBurHumM_ + _tNBurNH4M_ + _tNBurNO3M_ _ELSE_ _tNBurHumM_ + _tNBurNH4M_ + _tNBurNO3M_ _ENDIF_
```

### `_tSiBurDetM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_Si_in_detritus_in_marsh
- **Equation**:

```
_tSiBurDetM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _rSiDDetSM_ * _tDBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiBurTotM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_burial_flux_in_marsh
- **Equation**:

```
_tSiBurTotM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_vDeltaSM_ _GE_ 0.0) _THEN_ _tSiBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_vDeltaWM_`  [_m_*_d_^-1]
- **Description**: Marsh_water_depth_change
- **Equation**:

```
_vDeltaWM_ = _IF_ (_FALSE_ _EQ_ _InclMarsh_ _OR_ _fMarsh_ _LE_ _NearZero_) _THEN_ 0.0 _ELSEIF_ (_ConstDepth_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSE_ - _vDeltaSM_ _ENDIF_
```

### `_aRelDeltaWM_`  [_d_^-1]
- **Description**: Relative_marsh_water_depth_change
- **Equation**:

```
_aRelDeltaWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _vDeltaWM_ / _uDepthWM_ _ELSE_ 0.0 _ENDIF_
```

## Dredging  (39 equations)

### `_bTimeDred_`  [_d_]
- **Description**: Dredging_time(every_nth_year)
- **Equation**:

```
_bTimeDred_ = _IF_ (_sTime_ _GE_ _cDredStart_ * _DaysPerYear_) _THEN_ (_FLOOR_(_TimeYears_/_cDredInterval_) * _cDredInterval_) * _DaysPerYear_ _ELSE_ -9999.999 _ENDIF_
```

### `_bRhoSolidSoil_`  [_gDW_*_m_^-3]
- **Description**: Average_solid_density_of_soil_material
- **Equation**:

```
_bRhoSolidSoil_ = _fDOrgSoil_ * _cRhoOM_ +(1.0 - _fDOrgSoil_) * _cRhoIM_
```

### `_aDepthStart_`  [_m_]
- **Description**: Update_dredged_layer
- **Equation**:

```
_aDepthStart_ = _IF_ (_sTime_ _EQ_ _bTimeDred_) _THEN_ _uDepthW_ _ELSE_ _aDepthStart_ _ENDIF_
```

### `_akDredDepth_`  [_d_^-1]
- **Description**: Rate_constant_of_deepening
- **Equation**:

```
_akDredDepth_ = _IF_ ((_sTime_ _GE_ _bTimeDred_) _AND_ (_sTime_ _LT_ _bTimeDred_ + _cLengDred_) _AND_ (_aDepthStart_ _LE_ _cDepthRef_ - _cDepthS_)) _THEN_ (_LN_(_cDepthRef_ / _aDepthStart_)) / _cLengDred_ _ELSE_ 0.0 _ENDIF_
```

### `_akDred_`  [_d_^-1]
- **Description**: Rate_constant_of_dredging(exponential_function)
- **Equation**:

```
_akDred_ = _IF_ ((_sTime_ _GE_ _bTimeDred_) _AND_ (_sTime_ _LT_ _bTimeDred_ + _cLengDred_) _AND_ (_aDepthStart_ _LE_ _cDepthRef_ - _cDepthS_)) _THEN_ (- _LN_(1.0 - _fEffDred_)) / _cLengDred_ _ELSE_ 0.0 _ENDIF_
```

### `_akDredBent_`  [_d_^-1]
- **Description**: Rate_constant_of_dredging_for_zoobenthos
- **Equation**:

```
_akDredBent_ = _IF_ ((_sTime_ _GE_ _bTimeDred_) _AND_ (_sTime_ _LT_ _bTimeDred_ + _cLengDred_) _AND_ (_aDepthStart_ _LE_ _cDepthRef_ - _cDepthS_)) _THEN_ (- _LN_(1.0 - _fEffDredBent_)) / _cLengDred_ _ELSE_ 0.0 _ENDIF_
```

### `_vDredDepthW_`  [_m_*_d_^-1]
- **Description**: Change_in_water_depth_due_to_dredging
- **Equation**:

```
_vDredDepthW_ =_IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ 0.0 _ELSE_ _akDredDepth_ * _uDepthW_ _ENDIF_
```

### `_tDDredDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Detritus_in_lake_sediment
- **Equation**:

```
_tDDredDetS_ = _akDred_ * _aDDetS_
```

### `_tPDredDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Detritus_in_lake_sediment
- **Equation**:

```
_tPDredDetS_ = _akDred_ * _aPDetS_
```

### `_tNDredDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Detritus_in_lake_sediment
- **Equation**:

```
_tNDredDetS_ = _akDred_ * _aNDetS_
```

### `_tSiDredDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_Si_Det_in_lake_sediment
- **Equation**:

```
_tSiDredDetS_ = _akDred_ * _aSiDetS_
```

### `_tPDredAIMS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_absorbed_onto_inorganic_matter_in_lake_sediment
- **Equation**:

```
_tPDredAIMS_ = _akDred_ * _aPAIMS_
```

### `_tDDredNetSoil_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_net_soil_in_lake_sediment
- **Equation**:

```
_tDDredNetSoil_ = -(_tDDredDetS_ / _cRhoOM_) * _bRhoSolidSoil_
```

### `_tDDredNetIMS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_net_inorganic_matter_in_lake_sediment
- **Equation**:

```
_tDDredNetIMS_ = (1.0 - _fDOrgSoil_) * _tDDredNetSoil_
```

### `_tDDredNetHumS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_net_humic_substances_in_lake_sediment
- **Equation**:

```
_tDDredNetHumS_ = _fDOrgSoil_ * _tDDredNetSoil_
```

### `_tPDredNetHumS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_net_humic_substances_in_lake_sediment
- **Equation**:

```
_tPDredNetHumS_ = _cPDSoilOM_ * _tDDredNetHumS_
```

### `_tNDredNetHumS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_net_humic_substances_in_lake_sediment
- **Equation**:

```
_tNDredNetHumS_ = _cNDSoilOM_ * _tDDredNetHumS_
```

### `_tDDredDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Diat_on_lake_sediment
- **Equation**:

```
_tDDredDiatS_ = _akDred_ * _aDDiatS_
```

### `_tPDredDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Diat_on_lake_sediment
- **Equation**:

```
_tPDredDiatS_ = _akDred_ * _aPDiatS_
```

### `_tNDredDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Diat_on_lake_sediment
- **Equation**:

```
_tNDredDiatS_ = _akDred_ * _aNDiatS_
```

### `_tDDredGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Gren_on_lake_sediment
- **Equation**:

```
_tDDredGrenS_ = _akDred_ * _aDGrenS_
```

### `_tPDredGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Gren_on_lake_sediment
- **Equation**:

```
_tPDredGrenS_ = _akDred_ * _aPGrenS_
```

### `_tNDredGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Gren_on_lake_sediment
- **Equation**:

```
_tNDredGrenS_ = _akDred_ * _aNGrenS_
```

### `_tDDredBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Blue_on_lake_sediment
- **Equation**:

```
_tDDredBlueS_ = _akDred_ * _aDBlueS_
```

### `_tPDredBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Blue_on_lake_sediment
- **Equation**:

```
_tPDredBlueS_ = _akDred_ * _aPBlueS_
```

### `_tNDredBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Blue_on_lake_sediment
- **Equation**:

```
_tNDredBlueS_ = _akDred_ * _aNBlueS_
```

### `_tDDredPhytS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Phyt_on_lake_sediment
- **Equation**:

```
_tDDredPhytS_ = _tDDredDiatS_+_tDDredGrenS_+_tDDredBlueS_
```

### `_tPDredPhytS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Phyt_on_lake_sediment
- **Equation**:

```
_tPDredPhytS_ = _tPDredDiatS_+_tPDredGrenS_+_tPDredBlueS_
```

### `_tNDredPhytS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Phyt_on_lake_sediment
- **Equation**:

```
_tNDredPhytS_ = _tNDredDiatS_+_tNDredGrenS_+_tNDredBlueS_
```

### `_tDDredBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Bent_on_lake_sediment
- **Equation**:

```
_tDDredBent_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ _akDredBent_ * _aDBent_ _ELSE_ 0.0 _ENDIF_
```

### `_tPDredBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Bent_on_lake_sediment
- **Equation**:

```
_tPDredBent_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ _akDredBent_ * _aPBent_ _ELSE_ 0.0 _ENDIF_
```

### `_tNDredBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Bent_on_lake_sediment
- **Equation**:

```
_tNDredBent_ = _IF_ (_InclWeb_ _EQ_ _TRUE_) _THEN_ _akDredBent_ * _aNBent_ _ELSE_ 0.0 _ENDIF_
```

### `_tDDredVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_DW_Veg_on_lake_sediment
- **Equation**:

```
_tDDredVeg_ = _akDred_ * _aDVeg_
```

### `_tPDredVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_P_Veg_on_lake_sediment
- **Equation**:

```
_tPDredVeg_ = _akDred_ * _aPVeg_
```

### `_tNDredVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Dredging_flux_of_N_Veg_on_lake_sediment
- **Equation**:

```
_tNDredVeg_ = _akDred_ * _aNVeg_
```

### `_tDDredNetTot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_dredging_flux
- **Equation**:

```
_tDDredNetTot_ = _tDDredDetS_ - _tDDredNetSoil_ + _tDDredPhytS_ + _tDDredBent_ + _tDDredVeg_
```

### `_tPDredNetTot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_dredging_flux
- **Equation**:

```
_tPDredNetTot_ = _tPDredDetS_ - _tPDredNetHumS_ + _tPDredAIMS_ + _tPDredPhytS_ + _tPDredBent_ + _tPDredVeg_
```

### `_tNDredNetTot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_dredging_flux
- **Equation**:

```
_tNDredNetTot_ = _tNDredDetS_ - _tNDredNetHumS_ + _tNDredPhytS_ + _tNDredBent_ + _tNDredVeg_
```

### `_tSiDredTot_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_dredging_flux
- **Equation**:

```
_tSiDredTot_ = _tSiDredDetS_ + _cSiDDiat_ * _tDDredDiatS_
```

## Mass_balance  (25 equations)

### `_tDMarsTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Mass_balance_totals_of_DW_marsh_water_and_vegetation_module
- **Equation**:

```
_tDMarsTotT_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (- _tDBurTotM_ - _wDMinDetWM_ * _uDepthWM_ -(1.0 - _fRefrDetS_) * _tDMinDetSM_ - _tDMinHumSM_ + _tDProdPhra_ - _tDRespShootPhra_ - _tDRespRootPhra_ - _tDManShootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

### `_tPMarsTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mass_balance_totals_of_P_marsh_water_and_vegetation_module
- **Equation**:

```
_tPMarsTotT_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (- _tPInfPO4SM_ + _tPSeepPO4SM_ - _tPDifGroundPO4M_ - _tPBurTotM_ - _tPChemPO4M_ - _tPManShootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

### `_tNMarsTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mass_balance_totals_of_N_marsh_water_and_vegetation_module
- **Equation**:

```
_tNMarsTotT_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ (- _tNInfNH4SM_ + _tNSeepNH4SM_ - _tNInfNO3SM_ + _tNSeepNO3SM_ - _tNDifGroundNO3M_ - _tNDifGroundNH4M_ - _tNBurTotM_ - _wNDenitWM_ * _uDepthWM_ - _tNDenitSM_ - _tNManShootPhra_) * _fMarsh_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiMarsTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Mass_balance_totals_of_SI_marsh_water_and_vegetation_module
- **Equation**:

```
_tSiMarsTotT_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ - _tSiBurDetM_ * _fMarsh_ - _tInfSiO2WM_ + _tSeepSiO2WM_ _ELSE_ 0.0 _ENDIF_
```

### `_aDRelTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_in_system
- **Equation**:

```
_aDRelTotT_ = _uDepthWHyp_ * _aRelDeltaWHyp_ * ( _oDDetWHyp_ + _oDIMWHyp_ + _oDDiatWHyp_ + _oDGrenWHyp_ + _oDBlueWHyp_ + _oDZooHyp_ ) + _fMarsh_ * _uDepthWM_ * _aRelDeltaWM_ * ( _oDDetWM_ + _oDIMWM_ + _oDDiatWM_ + _oDGrenWM_ + _oDBlueWM_ + _oDZooM_) + _uDepthWEpi_ * _aRelDeltaWEpi_ * (_oDDetWEpi_ + _oDIMWEpi_ + _oDDiatWEpi_ + _oDGrenWEpi_ + _oDBlueWEpi_ + _oDZooEpi_ )
```

### `_aNRelTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_in_system
- **Equation**:

```
_aNRelTotT_ = _uDepthWHyp_ * _aRelDeltaWHyp_ * ( _oNH4WHyp_ + _oNO3WHyp_ + _oNDetWHyp_ + _oNDiatWHyp_ + _oNGrenWHyp_ + _oNBlueWHyp_ + _oNZooHyp_ ) + _fMarsh_ * _uDepthWM_ * _aRelDeltaWM_ * ( _oNH4WM_ + _oNO3WM_ + _oNDetWM_ + _oNDiatWM_ + _oNGrenWM_ + _oNBlueWM_ + _oNZooM_ ) + _uDepthWEpi_ * _aRelDeltaWEpi_ * ( _oNH4WEpi_ + _oNO3WEpi_ + _oNDetWEpi_ + _oNDiatWEpi_ + _oNGrenWEpi_ + _oNBlueWEpi_ + _oNZooEpi_ )
```

### `_aPRelTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_in_system
- **Equation**:

```
_aPRelTotT_ = _uDepthWHyp_ * _aRelDeltaWHyp_ * ( _oPO4WHyp_ + _oPAIMWHyp_ + _oPDetWHyp_ + _oPDiatWHyp_ + _oPGrenWHyp_ + _oPBlueWHyp_ + _oPZooHyp_ ) + _fMarsh_ * _uDepthWM_ * _aRelDeltaWM_ * (_oPO4WM_ + _oPAIMWM_ + _oPDetWM_ + _oPDiatWM_ + _oPGrenWM_ + _oPBlueWM_ + _oPZooM_ ) + _uDepthWEpi_ * _aRelDeltaWEpi_ * (_oPO4WEpi_ + _oPAIMWEpi_ + _oPDetWEpi_ + _oPDiatWEpi_ + _oPGrenWEpi_ + _oPBlueWEpi_ + _oPZooEpi_ )
```

### `_aSiRelTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_in_system
- **Equation**:

```
_aSiRelTotT_ = _uDepthWHyp_ * _aRelDeltaWHyp_ * ( _oSiO2WHyp_ + _oSiDetWHyp_ + _cSiDDiat_*_oDDiatWHyp_) + _fMarsh_ * _uDepthWM_ * _aRelDeltaWM_ * ( _oSiO2WM_ + _oSiDetWM_ + _cSiDDiat_*_oDDiatWM_) + _uDepthWEpi_ * _aRelDeltaWEpi_ * ( _oSiO2WEpi_ + _oSiDetWEpi_ + _cSiDDiat_*_oDDiatWEpi_)
```

### `_aO2RelTotT_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Total_Si_in_system
- **Equation**:

```
_aO2RelTotT_ = _uDepthWHyp_ * _aRelDeltaWHyp_* _oO2WHyp_ + _fMarsh_ * _uDepthWM_ * _aRelDeltaWM_ * _oO2WM_ + _uDepthWEpi_ * _aRelDeltaWEpi_ * _oO2WEpi_
```

### `_aDTotTHyp_`  [_gDW_*_m_^-2]
- **Description**: Total_DW_in_system
- **Equation**:

```
_aDTotTHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ (_oDIMWHyp_+_oDDetWHyp_+_oDDiatWHyp_+_oDGrenWHyp_+_oDBlueWHyp_+_oDZooHyp_) * _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aNTotTHyp_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_system
- **Equation**:

```
_aNTotTHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ (_oNH4WHyp_+_oNO3WHyp_+_oNDetWHyp_+_oNDiatWHyp_+_oNGrenWHyp_+_oNBlueWHyp_ +_oNZooHyp_)*_uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aPTotTHyp_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_system
- **Equation**:

```
_aPTotTHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ (_oPO4WHyp_+_oPDetWHyp_+_oPDiatWHyp_+_oPGrenWHyp_+_oPBlueWHyp_ +_oPZooHyp_+_oPAIMWHyp_) * _uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aSiTotTHyp_`  [_gSi_*_m_^-2]
- **Description**: Total_Si_in_system
- **Equation**:

```
_aSiTotTHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ (_oSiO2WHyp_ + _oSiDetWHyp_ + _cSiDDiat_*_oDDiatWHyp_) *_uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aO2TotTHyp_`  [_gO2_*_m_^-2]
- **Description**: Total_Si_in_system
- **Equation**:

```
_aO2TotTHyp_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ (_oO2WHyp_ ) *_uDepthWHyp_ _ELSE_ 0.0 _ENDIF_
```

### `_aDTotT_`  [_gDW_*_m_^-2]
- **Description**: Total_DW_in_system
- **Equation**:

```
_aDTotT_ = _aDTotTHyp_ + (_oDIMWEpi_+_oDDetWEpi_+_oDDiatWEpi_+_oDGrenWEpi_+_oDBlueWEpi_+_oDZooEpi_) * _uDepthWEpi_ +_aDFish_+_aDPisc_ + _aDGras_ +_aDVeg_ +_aDIMS_+_aDHumS_+_aDDetS_+_aDDiatS_+_aDGrenS_+_aDBlueS_+_aDBent_ + _aDTotM_ + _aDBlueSurf_
```

### `_aNTotT_`  [_gN_*_m_^-2]
- **Description**: Total_N_in_system
- **Equation**:

```
_aNTotT_ = _aNTotTHyp_+ (_oNH4WEpi_+_oNO3WEpi_+_oNDetWEpi_+_oNDiatWEpi_+_oNGrenWEpi_+_oNBlueWEpi_ +_oNZooEpi_)*_uDepthWEpi_ +_aNFish_+_aNPisc_ + _aNGras_ +_aNVeg_ +_aNH4S_+_aNO3S_+_aNDetS_+_aNHumS_+_aNDiatS_+_aNGrenS_+_aNBlueS_ +_aNBent_ + _aNTotM_ + _aNBlueSurf_
```

### `_aPTotT_`  [_gP_*_m_^-2]
- **Description**: Total_P_in_system
- **Equation**:

```
_aPTotT_ = _aPTotTHyp_ + (_oPO4WEpi_+_oPDetWEpi_+_oPDiatWEpi_+_oPGrenWEpi_+_oPBlueWEpi_ +_oPZooEpi_+_oPAIMWEpi_) * _uDepthWEpi_ +_aPFish_+_aPPisc_ + _aPGras_ +_aPVeg_ +_aPO4S_+_aPDetS_+_aPHumS_+_aPDiatS_+_aPGrenS_+_aPBlueS_ +_aPAIMS_+_aPBent_ + _aPTotM_ +_aPBlueSurf_
```

### `_aSiTotT_`  [_gSi_*_m_^-2]
- **Description**: Total_Si_in_system
- **Equation**:

```
_aSiTotT_ = _aSiTotTHyp_ + (_oSiO2WEpi_ + _oSiDetWEpi_ + _cSiDDiat_*_oDDiatWEpi_) *_uDepthWEpi_ + _aSiDetS_ + _cSiDDiat_*_aDDiatS_ + _aSiTotM_
```

### `_aO2TotT_`  [_gO2_*_m_^-2]
- **Description**: Total_O2_in_system
- **Equation**:

```
_aO2TotT_ = _aO2TotTHyp_ + ( _oO2WEpi_) *_uDepthWEpi_ + _aO2TotM_
```

### `_aDError_`  [_gDW_*_m_^-2]
- **Description**: DW_mass_balance_error
- **Equation**:

```
_aDError_ = _aDTotT_ - _aDExtTotT_
```

### `_aNError_`  [_gN_*_m_^-2]
- **Description**: N_mass_balance_error
- **Equation**:

```
_aNError_ = _aNTotT_ - _aNExtTotT_
```

### `_aPError_`  [_gP_*_m_^-2]
- **Description**: P_mass_balance_error
- **Equation**:

```
_aPError_ = _aPTotT_ - _aPExtTotT_
```

### `_aSiError_`  [_gSi_*_m_^-2]
- **Description**: Si_mass_balance_error
- **Equation**:

```
_aSiError_ = _aSiTotT_ - _aSiExtTotT_
```

### `_aO2Error_`  [_gO2_*_m_^-2]
- **Description**: O2_mass_balance_error
- **Equation**:

```
_aO2Error_ = _aO2TotT_ - _aO2ExtTotT_
```

### `_aDepthError_`  [_m_]
- **Description**: Q_mass_balance_error
- **Equation**:

```
_aDepthError_ = _sDepthW_ - _aDepthExtTotT_
```

## Total_settling  (9 equations)

### `_tDSetTotHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tDSetTotHyp_ = _tDSetIMHyp_ + _tDSetDetHyp_ + _tDSetPhytHyp_
```

### `_tPSetTotHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tPSetTotHyp_ = _tPSetAIMHyp_ + _tPSetDetHyp_ + _tPSetPhytHyp_
```

### `_tNSetTotHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tNSetTotHyp_ = _tNSetDetHyp_ + _tNSetPhytHyp_
```

### `_tDSetTotEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tDSetTotEpi_ = _tDSetIMEpi_ + _tDSetDetEpi_ + _tDSetPhytEpi_
```

### `_tPSetTotEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tPSetTotEpi_ = _tPSetAIMEpi_ + _tPSetDetEpi_ + _tPSetPhytEpi_
```

### `_tNSetTotEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_settling
- **Equation**:

```
_tNSetTotEpi_ = _tNSetDetEpi_ + _tNSetPhytEpi_
```

### `_tDResusTot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_resuspension
- **Equation**:

```
_tDResusTot_ = _tDResusDead_ + _tDResusPhytTot_
```

### `_tPResusTot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_resuspension_flux
- **Equation**:

```
_tPResusTot_ = _tPResusDet_ + _tPResusAIM_ + _tPResusPhyt_ + _tPResusPO4_
```

### `_tNResusTot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_resuspension_flux
- **Equation**:

```
_tNResusTot_ = _tNResusDet_ + _tNResusNH4_ + _tNResusNO3_ + _tNResusPhyt_
```

## total_fluxes_in_Surface_to_detritus_and_dissolved_nutrients_in_'prim'_module  (1 equations)

### `_tDPrimTotSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: total_DW_flux_in_Surface
- **Equation**:

```
_tDPrimTotSurf_ = _IF_ (_InclSurf_ _EQ_ _TRUE_) _THEN_ _tDAssBlueSurf_ - _tDRespBlueSurf_ _ELSE_ 0.0 _ENDIF_
```

## Fish_processes  (5 equations)

### `_tDAgeFish_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Ageing
- **Equation**:

```
_tDAgeFish_ = _IF_ (_FALSE_ _EQ_ _InclSeason_) _THEN_ ((1/_DaysInYear_)*_fAgeFish_) * _aDFiJv_ _ELSEIF_ (_Day_ _GE_ 364.0) _THEN_ _fAgeFish_ * _aDFiJv_ *_PerDay_ _ELSE_ 0.0 _ENDIF_
```

### `_tPReprFish_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Reproduction_flux
- **Equation**:

```
_tPReprFish_ = _rPDFiAd_ * _tDReprFish_
```

### `_tPAgeFish_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Ageing
- **Equation**:

```
_tPAgeFish_ = _rPDFiJv_ * _tDAgeFish_
```

### `_tNReprFish_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Reproduction_flux
- **Equation**:

```
_tNReprFish_ = _rNDFiAd_ * _tDReprFish_
```

### `_tNAgeFish_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Ageing
- **Equation**:

```
_tNAgeFish_ = _rNDFiJv_ * _tDAgeFish_
```

## Total_fish_loss_fluxes  (24 equations)

### `_tDMortFiJvBot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_DW_fixed_in_bones_and_scales
- **Equation**:

```
_tDMortFiJvBot_ = _fDBone_ * _tDMortFiJv_
```

### `_tDMortFiJvDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_DW_becoming_detritus
- **Equation**:

```
_tDMortFiJvDet_ = _tDMortFiJv_ - _tDMortFiJvBot_
```

### `_tDMortFiAdBot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_DW_fixed_in_bones_and_scales
- **Equation**:

```
_tDMortFiAdBot_ = _fDBone_ * _tDMortFiAd_
```

### `_tDMortFiAdDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_DW_becoming_detritus
- **Equation**:

```
_tDMortFiAdDet_ = _tDMortFiAd_ - _tDMortFiAdBot_
```

### `_tPMortFiJvBot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_P_fixed_in_bones_AND_scales
- **Equation**:

```
_tPMortFiJvBot_ = _fPBone_ * _tPMortFiJv_
```

### `_tPMortFiJvPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_P_becoming_dissolved_P
- **Equation**:

```
_tPMortFiJvPO4_ = _fDissMortFish_ *(_tPMortFiJv_ - _tPMortFiJvBot_)
```

### `_tPMortFiJvDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_PW_becoming_detritus
- **Equation**:

```
_tPMortFiJvDet_ = _tPMortFiJv_ - _tPMortFiJvBot_ - _tPMortFiJvPO4_
```

### `_tPMortFiAdBot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_P_fixed_in_bones_AND_scales
- **Equation**:

```
_tPMortFiAdBot_ = _fPBone_ * _tPMortFiAd_
```

### `_tPMortFiAdPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_P_becoming_dissolved_P
- **Equation**:

```
_tPMortFiAdPO4_ = _fDissMortFish_ *(_tPMortFiAd_ - _tPMortFiAdBot_)
```

### `_tPMortFiAdDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_PW_becoming_detritus
- **Equation**:

```
_tPMortFiAdDet_ = _tPMortFiAd_ - _tPMortFiAdBot_ - _tPMortFiAdPO4_
```

### `_tPEgesFiJvPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_egestion_of_fish
- **Equation**:

```
_tPEgesFiJvPO4_ = _fDissEgesFish_ * _tPEgesFiJv_
```

### `_tPEgesFiJvDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_egestion_of_fish
- **Equation**:

```
_tPEgesFiJvDet_ = _tPEgesFiJv_ - _tPEgesFiJvPO4_
```

### `_tPEgesFiAdPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: SRP_egestion_of_fish
- **Equation**:

```
_tPEgesFiAdPO4_ = _fDissEgesFish_ * _tPEgesFiAd_
```

### `_tPEgesFiAdDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Detrital_P_egestion_of_fish
- **Equation**:

```
_tPEgesFiAdDet_ = _tPEgesFiAd_ - _tPEgesFiAdPO4_
```

### `_tNMortFiAdBot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_N_fixed_in_bones_AND_scales
- **Equation**:

```
_tNMortFiAdBot_ = _fDBone_ * _tNMortFiAd_
```

### `_tNMortFiAdNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_N_becoming_dissolved_N
- **Equation**:

```
_tNMortFiAdNH4_ = _fDissMortFish_ *(_tNMortFiAd_ - _tNMortFiAdBot_)
```

### `_tNMortFiAdDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_NW_becoming_detritus
- **Equation**:

```
_tNMortFiAdDet_ = _tNMortFiAd_ - _tNMortFiAdBot_ - _tNMortFiAdNH4_
```

### `_tNMortFiJvBot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_N_fixed_in_bones_AND_scales
- **Equation**:

```
_tNMortFiJvBot_ = _fDBone_ * _tNMortFiJv_
```

### `_tNMortFiJvNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_N_becoming_dissolved_N
- **Equation**:

```
_tNMortFiJvNH4_ = _fDissMortFish_ *(_tNMortFiJv_ - _tNMortFiJvBot_)
```

### `_tNMortFiJvDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Part_of_dead_fish_NW_becoming_detritus
- **Equation**:

```
_tNMortFiJvDet_ = _tNMortFiJv_ - _tNMortFiJvBot_ - _tNMortFiJvNH4_
```

### `_tNEgesFiJvNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_egestion_of_fish
- **Equation**:

```
_tNEgesFiJvNH4_ = _fDissEgesFish_ * _tNEgesFiJv_
```

### `_tNEgesFiJvDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_egestion_of_fish
- **Equation**:

```
_tNEgesFiJvDet_ = _tNEgesFiJv_ - _tNEgesFiJvNH4_
```

### `_tNEgesFiAdNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: NH4_egestion_of_fish
- **Equation**:

```
_tNEgesFiAdNH4_ = _fDissEgesFish_ * _tNEgesFiAd_
```

### `_tNEgesFiAdDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Detrital_egestion_of_fish
- **Equation**:

```
_tNEgesFiAdDet_ = _tNEgesFiAd_ - _tNEgesFiAdNH4_
```

## Fish_processes_of_young_fish  (14 equations)

### `_tPMigrFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tPMigrFiJv_ = _kMigrFish_ *(_cPDFishRef_ * _cDFiJvIn_ - _aPFiJv_)
```

### `_tPConsFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: (zooplankton)_P_consumption_by_juvenile_fish
- **Equation**:

```
_tPConsFiJv_ = _rPDZooEpi_ * _tDConsFiJv_
```

### `_afPAssFiJv_`  [0]
- **Description**: P_assimilation_efficiency_of_juvenile_fish
- **Equation**:

```
_afPAssFiJv_ = _MIN_(1.0,_cPDFishRef_ / _rPDZooEpi_ * _fDAssFiJv_)
```

### `_tPAssFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_assimilation_of_juvenile_fish
- **Equation**:

```
_tPAssFiJv_ = _afPAssFiJv_ * _tPConsFiJv_
```

### `_tPEgesFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_juvenile_fish
- **Equation**:

```
_tPEgesFiJv_ = _tPConsFiJv_ - _tPAssFiJv_
```

### `_tPExcrFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: P_excretion_of_juvenile_fish
- **Equation**:

```
_tPExcrFiJv_ = (_rPDFiJv_ / _cPDFishRef_) * _kDRespFiJv_ * _uFunTmFish_ * _aPFiJv_
```

### `_tPMortFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_juvenile_fish
- **Equation**:

```
_tPMortFiJv_ = _rPDFiJv_ * _tDMortFiJv_
```

### `_tNMigrFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Net_migration_flux
- **Equation**:

```
_tNMigrFiJv_ = _kMigrFish_ *(_cNDFishRef_ * _cDFiJvIn_ - _aNFiJv_)
```

### `_tNConsFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: (zooplankton)_N_consumption_by_juvenile_fish
- **Equation**:

```
_tNConsFiJv_ = _rNDZooEpi_ * _tDConsFiJv_
```

### `_afNAssFiJv_`  [0]
- **Description**: N_assimilation_efficiency_of_juvenile_fish
- **Equation**:

```
_afNAssFiJv_ = _MIN_(1.0,_cNDFishRef_ / _rNDZooEpi_ * _fDAssFiJv_)
```

### `_tNAssFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_assimilation_of_juvenile_fish
- **Equation**:

```
_tNAssFiJv_ = _afNAssFiJv_ * _tNConsFiJv_
```

### `_tNEgesFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Egestion_of_juvenile_fish
- **Equation**:

```
_tNEgesFiJv_ = _tNConsFiJv_ - _tNAssFiJv_
```

### `_tNExcrFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: N_excretion_of_juvenile_fish
- **Equation**:

```
_tNExcrFiJv_ = (_rNDFiJv_ / _cNDFishRef_) * _kDRespFiJv_ * _uFunTmFish_ * _aNFiJv_
```

### `_tNMortFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Mortality_of_juvenile_fish
- **Equation**:

```
_tNMortFiJv_ = _rNDFiJv_ * _tDMortFiJv_
```

## Total_fluxes_for_animal_groups  (17 equations)

### `_tDWebBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Zoobenthos
- **Equation**:

```
_tDWebBent_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrBent_ + _tDAssBent_ - _tDConsFiAd_ - _tDRespBent_ - _tDMortBent_ _ENDIF_
```

### `_tPWebBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Zoobenthos
- **Equation**:

```
_tPWebBent_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPMigrBent_ + _tPAssBent_ - _tPConsFiAd_ - _tPExcrBent_ - _tPMortBent_ _ENDIF_
```

### `_tNWebBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Zoobenthos
- **Equation**:

```
_tNWebBent_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNMigrBent_ + _tNAssBent_ - _tNConsFiAd_ - _tNExcrBent_ - _tNMortBent_ _ENDIF_
```

### `_tDWebFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Young_fish
- **Equation**:

```
_tDWebFiJv_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrFiJv_ + _tDReprFish_ - _tDAgeFish_ + _tDAssFiJv_ - _tDRespFiJv_ - _tDMortFiJv_ - _tDConsFiJvPiscNut_ _ENDIF_
```

### `_tPWebFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Young_fish
- **Equation**:

```
_tPWebFiJv_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPMigrFiJv_ + _tPReprFish_ - _tPAgeFish_ + _tPAssFiJv_ - _tPExcrFiJv_ - _tPMortFiJv_ - _tPConsFiJvPiscNut_ _ENDIF_
```

### `_tNWebFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Young_fish
- **Equation**:

```
_tNWebFiJv_ =_IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNMigrFiJv_ + _tNReprFish_ - _tNAgeFish_ + _tNAssFiJv_ - _tNExcrFiJv_ - _tNMortFiJv_ - _tNConsFiJvPiscNut_ _ENDIF_
```

### `_tDWebFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Adult_fish
- **Equation**:

```
_tDWebFiAd_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrFiAd_ + _tDAssFiAd_ - _tDRespFiAd_ - _tDMortFiAd_ - _tDReprFish_ + _tDAgeFish_ - _tDConsFiAdPiscNut_ - _tDHarvFish_ _ENDIF_
```

### `_tPWebFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Adult_fish
- **Equation**:

```
_tPWebFiAd_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tPMigrFiAd_ + _tPAssFiAd_ - _tPExcrFiAd_ - _tPMortFiAd_ - _tPReprFish_ + _tPAgeFish_ - _tPConsFiAdPiscNut_ - _tPHarvFish_ _ENDIF_
```

### `_tNWebFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Adult_fish
- **Equation**:

```
_tNWebFiAd_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tNMigrFiAd_ + _tNAssFiAd_ - _tNExcrFiAd_ - _tNMortFiAd_ - _tNReprFish_ + _tNAgeFish_ - _tNConsFiAdPiscNut_ - _tNHarvFish_ _ENDIF_
```

### `_tDWebPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_predatory_fish
- **Equation**:

```
_tDWebPisc_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrPisc_ + _tDAssPisc_ - _tDRespPisc_ - _tDMortPisc_ - _tDHarvPisc_ _ENDIF_
```

### `_tDWebGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: total_food_web_flux_of_DW_in_Gras_fish
- **Equation**:

```
_tDWebGras_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _tDMigrGras_ + _tDAssGras_ - _tDRespGras_ - _tDMortGras_ - _tDHarvGras_ _ENDIF_
```

### `_wDWebZooHyp_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Herbivorous_zooplankton
- **Equation**:

```
_wDWebZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_ _OR_ _aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wDAssZooHyp_ - _wDRespZooHyp_ - _wDMortZooHyp_ - _tDConsFiJv_ * (( _aDTotZoo_ - _oDZooEpi_ * _uDepthWEpi_) / (_aDTotZoo_ + _NearZero_)) / _uDepthWHyp_ _ENDIF_
```

### `_wDWebZooEpi_`  [_gDW_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_DW_in_Herbivorous_zooplankton
- **Equation**:

```
_wDWebZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wDAssZooEpi_ - _wDRespZooEpi_ - _wDMortZooEpi_ - _tDConsFiJv_ * (_oDZooEpi_ * _uDepthWEpi_ / (_aDTotZoo_ + _NearZero_) ) / _uDepthWEpi_ _ENDIF_
```

### `_wPWebZooHyp_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Herbivorous_zooplankton
- **Equation**:

```
_wPWebZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_ _OR_ _aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wPAssZooHyp_ - _wPExcrZooHyp_ - _wPMortZooHyp_ - _tPConsFiJv_ * (( _aPTotZoo_ - _oPZooEpi_ * _uDepthWEpi_ ) / (_aPTotZoo_ + _NearZero_) ) / _uDepthWHyp_ _ENDIF_
```

### `_wPWebZooEpi_`  [_gP_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_P_in_Herbivorous_zooplankton
- **Equation**:

```
_wPWebZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wPAssZooEpi_ - _wPExcrZooEpi_ - _wPMortZooEpi_ - _tPConsFiJv_ * (_oPZooEpi_ * _uDepthWEpi_ / (_aPTotZoo_ + _NearZero_)) / _uDepthWEpi_ _ENDIF_
```

### `_wNWebZooHyp_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Herbivorous_zooplankton
- **Equation**:

```
_wNWebZooHyp_ = _IF_ (_FALSE_ _EQ_ _InclWeb_ _OR_ _aInclStrat_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSE_ _wNAssZooHyp_ - _wNExcrZooHyp_ - _wNMortZooHyp_ - _tNConsFiJv_ * (( _aNTotZoo_ -_oNZooEpi_ * _uDepthWEpi_ ) / (_aNTotZoo_ + _NearZero_) ) / _uDepthWHyp_ _ENDIF_
```

### `_wNWebZooEpi_`  [_gN_*_m_^-3*_d_^-1]
- **Description**: Total_food_web_flux_of_N_in_Herbivorous_zooplankton
- **Equation**:

```
_wNWebZooEpi_ = _IF_ (_FALSE_ _EQ_ _InclWeb_) _THEN_ 0.0 _ELSE_ _wNAssZooEpi_ - _wNExcrZooEpi_ - _wNMortZooEpi_ - _tNConsFiJv_ * (_oNZooEpi_ * _uDepthWEpi_ / (_aNTotZoo_ + _NearZero_) ) / _uDepthWEpi_ _ENDIF_
```

## P_fluxes_to/from_other_components  (1 equations)

### `_tPWebBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_foodweb_flux_of_P_in_surface_blue-greens_in_lake
- **Equation**:

```
_tPWebBlueSurf_ = _IF_ (_InclWeb_ _EQ_ _FALSE_ _OR_ _InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ - _tPConsBlueZooSurf_ _ENDIF_
```

## N_fluxes_to/from_other_components  (1 equations)

### `_tNWebBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_foodweb_flux_of_N_in_surface_blue-greens_in_lake
- **Equation**:

```
_tNWebBlueSurf_ = _IF_ (_InclWeb_ _EQ_ _FALSE_ _OR_ _InclSurf_ _EQ_ _FALSE_ _OR_ _aDBlueSurf_ _LT_ _cDBlueSurfMin_) _THEN_ 0.0 _ELSE_ - _tNConsBlueZooSurf_ _ENDIF_
```

## Burial  (24 equations)

### `_tDIMS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_inorganic_matter_in_sediment
- **Equation**:

```
_tDIMS_ = _tDAbioIMS_
```

### `_tDHumS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_sediment_humus_in_lake
- **Equation**:

```
_tDHumS_ = _tDAbioHumS_
```

### `_tDDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Increase_in_sediment_detritus_in_lake
- **Equation**:

```
_tDDetS_ = _tDAbioDetS_ + _tDPrimDetS_ + _tDWebDetS_ + _tDBedDetSEpi_ + _tDBedDetSHyp_
```

### `_vDeltaS_`  [_m_*_d_^-1]
- **Description**: Turnover_depth_in_lake
- **Equation**:

```
_vDeltaS_ = (_tDIMS_ / _cRhoIM_ +(_tDHumS_ + _tDDetS_) / _cRhoOM_)/(1.0 - _bPorS_)
```

### `_vDeltaW_`  [_m_*_d_^-1]
- **Description**: Lake_water_depth_change
- **Equation**:

```
_vDeltaW_ = _IF_ (_ConstDepth_ _EQ_ _TRUE_ ) _THEN_ 0.0 _ELSE_ - _vDeltaS_ _ENDIF_
```

### `_tDBurIM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_inorganic_matter_in_lake
- **Equation**:

```
_tDBurIM_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ ((_tDHumS_ + _tDDetS_) +(_cRhoOM_ / _cRhoIM_) * _tDIMS_) / ((_aDHumS_ + _aDDetS_) / _aDIMS_ + _cRhoOM_ / _cRhoIM_) _ELSE_ ((_tDHumS_ + _tDDetS_) +(_cRhoOM_ / _cRhoIM_) * _tDIMS_) / (_fDOrgSoil_ /(1.0 - _fDOrgSoil_) + _cRhoOM_ / _cRhoIM_) _ENDIF_
```

### `_tDBurOM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_organic_matter_in_lake
- **Equation**:

```
_tDBurOM_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ (_aDHumS_ + _aDDetS_) / _aDIMS_ * _tDBurIM_ _ELSE_ _fDOrgSoil_ /(1.0 - _fDOrgSoil_) * _tDBurIM_ _ENDIF_
```

### `_tDBurDet_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_detritus_in_lake
- **Equation**:

```
_tDBurDet_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _aDDetS_ /(_aDHumS_ + _aDDetS_) * _tDBurOM_ _ELSE_ 0.0 _ENDIF_
```

### `_tDBurHum_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_DW_in_humus_in_lake
- **Equation**:

```
_tDBurHum_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _tDBurOM_ - _tDBurDet_ _ELSE_ _tDBurOM_ _ENDIF_
```

### `_tDBurTot_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Total_DW_burial_flux_in_lake
- **Equation**:

```
_tDBurTot_ =_IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_(_vDeltaS_ _GE_ 0.0) _THEN_ _tDBurIM_ + _tDBurOM_ _ELSE_ _tDBurIM_ + _tDBurOM_ _ENDIF_
```

### `_tPBurHum_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_in_humus_in_lake
- **Equation**:

```
_tPBurHum_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _rPDHumS_ * _tDBurHum_ _ELSE_ _cPDSoilOM_ * _tDBurHum_ _ENDIF_
```

### `_tPBurDet_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_in_detritus_in_lake
- **Equation**:

```
_tPBurDet_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_(_vDeltaS_ _GE_ 0.0) _THEN_ _rPDDetS_ * _tDBurDet_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBurAIM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_P_absorbed_onto_inorganic_matter_in_lake
- **Equation**:

```
_tPBurAIM_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _aPAIMS_ / _aDIMS_ * _tDBurIM_ _ELSE_ 0.0 _ENDIF_
```

### `_tPBurPO4_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_P_in_lake
- **Equation**:

```
_tPBurPO4_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _aPO4S_ *(_vDeltaS_ / _cDepthS_) _ELSE_ _cPO4Ground_ *(_bPorS_ * _vDeltaS_) _ENDIF_
```

### `_tPBurTot_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Total_P_burial_flux_in_lake
- **Equation**:

```
_tPBurTot_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _tPBurDet_ + _tPBurHum_ + _tPBurAIM_ + _tPBurPO4_ _ELSE_ _tPBurHum_ + _tPBurAIM_ + _tPBurPO4_ _ENDIF_
```

### `_tNBurHum_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_N_in_humus_in_lake
- **Equation**:

```
_tNBurHum_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _rNDHumS_ * _tDBurHum_ _ELSE_ _cNDSoilOM_ * _tDBurHum_ _ENDIF_
```

### `_tNBurDet_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_N_in_detritus_in_lake
- **Equation**:

```
_tNBurDet_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _rNDDetS_ * _tDBurDet_ _ELSE_ 0.0 _ENDIF_
```

### `_tNBurNH4_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_NH4_in_lake
- **Equation**:

```
_tNBurNH4_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _aNH4S_ *(_vDeltaS_ / _cDepthS_) _ELSE_ _cNH4Ground_ *(_bPorS_ * _vDeltaS_) _ENDIF_
```

### `_tNBurNO3_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_dissolved_NO3_in_lake
- **Equation**:

```
_tNBurNO3_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _aNO3S_ *(_vDeltaS_ / _cDepthS_) _ELSE_ _cNO3Ground_ *(_bPorS_ * _vDeltaS_) _ENDIF_
```

### `_tNBurTot_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Total_N_burial_flux_in_lake
- **Equation**:

```
_tNBurTot_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _tNBurDet_ + _tNBurHum_ + _tNBurNH4_ + _tNBurNO3_ _ELSE_ _tNBurHum_ + _tNBurNH4_ + _tNBurNO3_ _ENDIF_
```

### `_tSiBurDet_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Burial_flux_of_Si_in_detritus_in_lake
- **Equation**:

```
_tSiBurDet_ = _IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _rSiDDetS_ * _tDBurDet_ _ELSE_ 0.0 _ENDIF_
```

### `_tSiBurTot_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Total_Si_burial_flux_in_lake
- **Equation**:

```
_tSiBurTot_ =_IF_ (_InclBur_ _EQ_ _FALSE_) _THEN_ 0.0 _ELSEIF_ (_vDeltaS_ _GE_ 0.0) _THEN_ _tSiBurDet_ _ELSE_ 0.0 _ENDIF_
```

### `_aRelDeltaWEpi_`  [_d_^-1]
- **Description**: Relative_water_depth_change_due_to_sediment_turnover_AND_dredging
- **Equation**:

```
_aRelDeltaWEpi_ = _IF_ ( _aInclStrat_ _EQ_ _TRUE_ ) _THEN_ (_vDeltaW_ ) / _uDepthWEpi_ _ELSE_ (_vDeltaW_ + _vDredDepthW_) / _uDepthWEpi_ _ENDIF_
```

### `_aRelDeltaWHyp_`  [_d_^-1]
- **Description**: Relative_water_depth_change_due_to_sediment_turnover_AND_dredging
- **Equation**:

```
_aRelDeltaWHyp_ = _IF_ ( _aInclStrat_ _EQ_ _FALSE_ ) _THEN_ 0.0 _ELSE_ (_vDeltaW_ + _vDredDepthW_) / _uDepthWHyp_ _ENDIF_
```

## Derivatives  (132 equations)

### `_dDepthW_`  [_m_*_d_^-1]
- **Description**: Derivative_for_water_depth_change_in_lake_water
- **Equation**:

```
_dDepthW_ = _IF_ (_aInclStrat_ _EQ_ _TRUE_) _THEN_ _vDeltaWEpi_ + _vDeltaW_ + _vDeltaWHyp_ + _vDredDepthW_ _ELSE_ 0.0 + _vDeltaWEpi_ + _vDeltaW_ + _vDredDepthW_ _ENDIF_
```

### `_dMixDepthW_`  [_m_*_d_^-1]
- **Description**: Derivative_for_water_depth_change_in_lake_water
- **Equation**:

```
_dMixDepthW_ = _vTranHypEpiW_
```

### `_dNH4WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_ammonium_in_water_in_lake_water
- **Equation**:

```
_dNH4WHyp_ = ( _wNTranNH4WHyp_ + _wNAbioNH4WHyp_ + _wNPrimNH4WHyp_ + _wNBedNH4WHyp_ + _wNWebNH4WHyp_ + _uNBackLoadHyp_ / _uDepthWHyp_ - _aRelDeltaWHyp_ * _oNH4WHyp_ - _wNExchNH4Hyp_ - _wNExchNH4WHyp_  - _wNAdvNH4W_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNO3WHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_nitrate_in_water_in_lake_water
- **Equation**:

```
_dNO3WHyp_ = ( _wNTranNO3WHyp_ + _wNAbioNO3WHyp_ + _wNPrimNO3WHyp_ + _wNBedNO3WHyp_ + _wNWebNO3WHyp_ - _aRelDeltaWHyp_ * _oNO3WHyp_ - _wNExchNO3Hyp_ - _wNExchNO3WHyp_  - _wNAdvNO3W_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPO4WHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_SRP_in_water_in_lake_water
- **Equation**:

```
_dPO4WHyp_ = ( _wPTranPO4WHyp_ + _wPAbioPO4WHyp_ + _wPPrimPO4WHyp_ + _wPBedPO4WHyp_ + _wPWebPO4WHyp_ + _uPBackLoadHyp_ / _uDepthWHyp_ - _aRelDeltaWHyp_ * _oPO4WHyp_ - _wPExchPO4Hyp_ - _wPExchPO4WHyp_  - _wPAdvPO4W_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPAIMWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P-adsorbed_onto_IM_in_water_in_lake_water
- **Equation**:

```
_dPAIMWHyp_ = ( _wPTranAIMWHyp_ + _wPAbioAIMWHyp_ - _aRelDeltaWHyp_ * _oPAIMWHyp_ - _wPExchAIMHyp_ - _wPExchAIMWHyp_  - _wPAdvAIMW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dSiO2WHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_dissolved_silica_in_water_in_lake_water
- **Equation**:

```
_dSiO2WHyp_ = ( _wSiTranSiO2Hyp_ + _wSiAbioSiO2WHyp_ + _wSiPrimSiO2WHyp_ - _aRelDeltaWHyp_ * _oSiO2WHyp_ - _wSiExchSiO2Hyp_ - _wSiExchSiO2WHyp_  - _wSiAdvSiO2W_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDDetWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Detritus_in_lake_water
- **Equation**:

```
_dDDetWHyp_ = ( _wDTranDetWHyp_ + _wDAbioDetWHyp_ + _wDPrimDetWHyp_ + _wDBedDetWHyp_ + _wDWebDetWHyp_ - _aRelDeltaWHyp_ * _oDDetWHyp_ - _wDExchDetHyp_ - _wDExchDetWHyp_  - _wDAdvDetW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNDetWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Detritus_in_lake_water
- **Equation**:

```
_dNDetWHyp_ = ( _wNTranDetWHyp_ + _wNAbioDetWHyp_ + _wNPrimDetWHyp_ + _wNBedDetWHyp_ + _wNWebDetWHyp_ -_aRelDeltaWHyp_ * _oNDetWHyp_ - _wNExchDetHyp_ - _wNExchDetWHyp_  - _wNAdvDetW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPDetWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Detritus_in_lake_water
- **Equation**:

```
_dPDetWHyp_ = ( _wPTranDetWHyp_ + _wPAbioDetWHyp_ + _wPPrimDetWHyp_ + _wPBedDetWHyp_ + _wPWebDetWHyp_ - _aRelDeltaWHyp_ * _oPDetWHyp_ - _wPExchDetHyp_ - _wPExchDetWHyp_  - _wPAdvDetW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dSiDetWHyp_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_Detritus_in_lake_water
- **Equation**:

```
_dSiDetWHyp_ = ( _wSiTranDetWHyp_ + _wSiAbioDetWHyp_ + _wSiPrimDetWHyp_ + _wSiWebDetWHyp_ - _aRelDeltaWHyp_ * _oSiDetWHyp_ - _wSiExchDetHyp_ - _wSiExchDetWHyp_  - _wSiAdvDetW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDIMWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_inorg_matter_in_water_in_lake_water
- **Equation**:

```
_dDIMWHyp_ = ( _wDTranIMWHyp_ + _wDAbioIMWHyp_ - _aRelDeltaWHyp_ * _oDIMWHyp_ - _wDExchIMHyp_ - _wDExchIMWHyp_  - _wDAdvIMW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDDiatWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Diatoms_in_lake_water
- **Equation**:

```
_dDDiatWHyp_ = ( _wDTranDiatHyp_ + _wDPrimDiatWHyp_ + _wDWebDiatWHyp_ - _aRelDeltaWHyp_ * _oDDiatWHyp_ - _wDExchDiatHyp_ - _wDExchDiatWHyp_  - _wDAdvDiatW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNDiatWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Diatoms_in_lake_water
- **Equation**:

```
_dNDiatWHyp_ = ( _wNTranDiatHyp_ + _wNPrimDiatWHyp_ + _wNWebDiatWHyp_ -_aRelDeltaWHyp_ * _oNDiatWHyp_ - _wNExchDiatHyp_ - _wNExchDiatWHyp_  - _wNAdvDiatW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPDiatWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Diatoms_in_lake_water
- **Equation**:

```
_dPDiatWHyp_ = ( _wPTranDiatHyp_ + _wPPrimDiatWHyp_ + _wPWebDiatWHyp_ -_aRelDeltaWHyp_ * _oPDiatWHyp_ - _wPExchDiatHyp_ - _wPExchDiatWHyp_  - _wPAdvDiatW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDGrenWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Greens_in_lake_water
- **Equation**:

```
_dDGrenWHyp_ = ( _wDTranGrenHyp_ + _wDPrimGrenWHyp_ + _wDWebGrenWHyp_ - _aRelDeltaWHyp_* _oDGrenWHyp_ - _wDExchGrenHyp_ - _wDExchGrenWHyp_  - _wDAdvGrenW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNGrenWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Greens_in_lake_water
- **Equation**:

```
_dNGrenWHyp_ = ( _wNTranGrenHyp_ + _wNPrimGrenWHyp_ + _wNWebGrenWHyp_ - _aRelDeltaWHyp_ * _oNGrenWHyp_ - _wNExchGrenHyp_ - _wNExchGrenWHyp_  - _wNAdvGrenW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPGrenWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Greens_in_lake_water
- **Equation**:

```
_dPGrenWHyp_ = ( _wPTranGrenHyp_ + _wPPrimGrenWHyp_ + _wPWebGrenWHyp_ - _aRelDeltaWHyp_ * _oPGrenWHyp_ - _wPExchGrenHyp_ - _wPExchGrenWHyp_  - _wPAdvGrenW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDBlueWHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Blue_greens_in_lake_water
- **Equation**:

```
_dDBlueWHyp_ = ( _wDTranBlueHyp_ + _wDPrimBlueWHyp_ + _wDWebBlueWHyp_ - _aRelDeltaWHyp_* _oDBlueWHyp_ - _wDExchBlueHyp_ - _wDExchBlueWHyp_  - _wDAdvBlueW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNBlueWHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Blue_greens_in_lake_water
- **Equation**:

```
_dNBlueWHyp_ = ( _wNTranBlueHyp_ + _wNPrimBlueWHyp_ + _wNWebBlueWHyp_ - _aRelDeltaWHyp_ * _oNBlueWHyp_ - _wNExchBlueHyp_ - _wNExchBlueWHyp_  - _wNAdvBlueW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPBlueWHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Blue_greens_in_lake_water
- **Equation**:

```
_dPBlueWHyp_ = ( _wPTranBlueHyp_ + _wPPrimBlueWHyp_ + _wPWebBlueWHyp_ -_aRelDeltaWHyp_ * _oPBlueWHyp_ - _wPExchBlueHyp_ - _wPExchBlueWHyp_  - _wPAdvBlueW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDZooHyp_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Zooplankton_in_lake_water
- **Equation**:

```
_dDZooHyp_ = ( _wDTranZooHyp_ + _wDWebZooHyp_ - _aRelDeltaWHyp_ * _oDZooHyp_ - _wDExchZooHyp_ - _wDExchZooWHyp_  - _wDAdvZooW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dNZooHyp_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Zooplankton_in_lake_water
- **Equation**:

```
_dNZooHyp_ = ( _wNTranZooHyp_ + _wNWebZooHyp_ -_aRelDeltaWHyp_ * _oNZooHyp_ - _wNExchZooHyp_ - _wNExchZooWHyp_  - _wNAdvZooW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dPZooHyp_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Zooplankton_in_lake_water
- **Equation**:

```
_dPZooHyp_ = ( _wPTranZooHyp_ + _wPWebZooHyp_ - _aRelDeltaWHyp_ * _oPZooHyp_ - _wPExchZooHyp_ - _wPExchZooWHyp_  - _wPAdvZooW_ / _uDepthWHyp_ ) * _MassHyp_
```

### `_dDFiAd_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Adult_whitefish_in_lake_water
- **Equation**:

```
_dDFiAd_ = _tDWebFiAd_
```

### `_dDFiJv_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Juvenile_whitefish_in_lake_water
- **Equation**:

```
_dDFiJv_ = _tDWebFiJv_
```

### `_dNFiAd_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Adult_whitefish_in_lake_water
- **Equation**:

```
_dNFiAd_ = _tNWebFiAd_
```

### `_dNFiJv_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Juvenile_whitefish_in_lake_water
- **Equation**:

```
_dNFiJv_ = _tNWebFiJv_
```

### `_dPFiAd_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Adult_whitefish_in_lake_water
- **Equation**:

```
_dPFiAd_ = _tPWebFiAd_
```

### `_dPFiJv_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Juvenile_whitefish_in_lake_water
- **Equation**:

```
_dPFiJv_ = _tPWebFiJv_
```

### `_dDPisc_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_predatory_fish_in_lake_water
- **Equation**:

```
_dDPisc_ = _tDWebPisc_
```

### `_dDGras_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Grass_carp_in_lake_water
- **Equation**:

```
_dDGras_ = _tDWebGras_
```

### `_dNH4S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_pore_water_ammonium_in_lake_water
- **Equation**:

```
_dNH4S_ = _tNAbioNH4S_ - _tNBurNH4_ + _tNPrimNH4S_ + _tNBedNH4S_ + _tNWebNH4S_
```

### `_dNO3S_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_pore_water_nitrate_in_lake_water
- **Equation**:

```
_dNO3S_ = _tNAbioNO3S_ - _tNBurNO3_ + _tNPrimNO3S_ + _tNBedNO3S_ + _tNWebNO3S_
```

### `_dPO4S_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_pore_water_SRP_in_lake_water
- **Equation**:

```
_dPO4S_ = _tPAbioPO4S_ - _tPBurPO4_ + _tPPrimPO4S_ + _tPBedPO4S_ + _tPWebPO4S_
```

### `_dPAIMS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P-adsorbed_onto_IM_in_sediment_in_lake_sediment
- **Equation**:

```
_dPAIMS_ = _tPAbioAIMS_ - _tPBurAIM_ - _tPDredAIMS_
```

### `_dDDetS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Sediment_detritus_in_lake_sediment
- **Equation**:

```
_dDDetS_ = _tDAbioDetS_ - _tDBurDet_ + _tDPrimDetS_ + _tDBedDetSEpi_ + _tDBedDetSHyp_ + _tDWebDetS_ - _tDDredDetS_
```

### `_dNDetS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Sediment_detritus_N_in_lake_sediment
- **Equation**:

```
_dNDetS_ = _tNAbioDetS_ - _tNBurDet_ + _tNPrimDetS_ + _tNBedDetS_ + _tNWebDetS_ - _tNDredDetS_
```

### `_dPDetS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Sediment_detritus_P_in_lake_sediment
- **Equation**:

```
_dPDetS_ = _tPAbioDetS_ - _tPBurDet_ + _tPPrimDetS_ + _tPBedDetS_ + _tPWebDetS_ - _tPDredDetS_
```

### `_dSiDetS_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_Sediment_detritus_Si_in_lake_sediment
- **Equation**:

```
_dSiDetS_ = _tSiAbioDetS_ - _tSiBurDet_ + _tSiPrimDetS_ + _tSiWebDetS_ - _tSiDredDetS_
```

### `_dDHumS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_humus_in_lake_sediment
- **Equation**:

```
_dDHumS_ = _tDAbioHumS_ - _tDBurHum_ - _tDDredNetHumS_
```

### `_dNHumS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_humus_in_lake_sediment
- **Equation**:

```
_dNHumS_ = _tNAbioHumS_ - _tNBurHum_ - _tNDredNetHumS_
```

### `_dPHumS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_humus_in_lake_sediment
- **Equation**:

```
_dPHumS_ = _tPAbioHumS_ - _tPBurHum_ - _tPDredNetHumS_
```

### `_dDIMS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_inorg_matter_in_sediment_in_lake_sediment
- **Equation**:

```
_dDIMS_ = _tDAbioIMS_ - _tDBurIM_ - _tDDredNetIMS_
```

### `_dDDiatS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Sed_Diatoms_in_lake_sediment
- **Equation**:

```
_dDDiatS_= _tDPrimDiatS_ + _tDWebDiatS_ - _tDDredDiatS_
```

### `_dNDiatS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Sediment_diatoms_in_lake_sediment
- **Equation**:

```
_dNDiatS_= _tNPrimDiatS_ + _tNWebDiatS_ - _tNDredDiatS_
```

### `_dPDiatS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Sediment_diatoms_in_lake_sediment
- **Equation**:

```
_dPDiatS_= _tPPrimDiatS_ + _tPWebDiatS_ - _tPDredDiatS_
```

### `_dDGrenS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Sed_Greens_in_lake_sediment
- **Equation**:

```
_dDGrenS_= _tDPrimGrenS_ + _tDWebGrenS_ - _tDDredGrenS_
```

### `_dNGrenS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Sediment_green_algae_in_lake_sediment
- **Equation**:

```
_dNGrenS_= _tNPrimGrenS_ + _tNWebGrenS_ - _tPDredGrenS_
```

### `_dPGrenS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Sediment_green_algae_in_lake_sediment
- **Equation**:

```
_dPGrenS_= _tPPrimGrenS_ + _tPWebGrenS_ - _tPDredGrenS_
```

### `_dDBlueS_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Sed_Blue-greens_in_lake_sediment
- **Equation**:

```
_dDBlueS_= _tDPrimBlueS_ + _tDWebBlueS_ - _tDDredBlueS_
```

### `_dNBlueS_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Sediment_blue-greens_in_lake_sediment
- **Equation**:

```
_dNBlueS_= _tNPrimBlueS_ + _tNWebBlueS_ - _tNDredBlueS_
```

### `_dPBlueS_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Sediment_blue-greens_in_lake_sediment
- **Equation**:

```
_dPBlueS_=_tPPrimBlueS_ + _tPWebBlueS_ - _tPDredBlueS_
```

### `_dDVeg_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Vegetation_in_lake_sediment
- **Equation**:

```
_dDVeg_ = _tDBedVeg_ - _tDDredVeg_
```

### `_dNVeg_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Vegetation_in_lake_sediment
- **Equation**:

```
_dNVeg_ = _tNBedVeg_ - _tNDredVeg_
```

### `_dPVeg_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Vegetation_in_lake_sediment
- **Equation**:

```
_dPVeg_ = _tPBedVeg_ - _tPDredVeg_
```

### `_dVegHeight_`  [_m_*_d_^-1]
- **Description**: Derivative_for_vegetation_height_change
- **Equation**:

```
_dVegHeight_ =  _IF_ ( _aVegWin_ _EQ_ 1 _AND_  _uVegHeight_ _LT_ _MIN_ (_cVegHeightWin_, _uDepthW_) ) _THEN_  _MIN_ ( _cVegHeightWin_ - _uVegHeight_ , ( _MIN_ (_uDepthW_ , _MAX_ ( _cVegHeightWin_ , _cVegHeight_) ) -  _MIN_ ( _cVegHeightWin_ , _cVegHeight_ , _uDepthW_) ) / _cLengAllo_) _ELSEIF_ ( _aVegWin_ _EQ_ 1 _AND_  _uVegHeight_ _GT_ _MIN_ (_cVegHeightWin_, _uDepthW_) ) _THEN_ _MAX_ (_cVegHeightWin_ - _uVegHeight_ , ( _MIN_ ( _cVegHeightWin_ , _cVegHeight_ , _uDepthW_) - _MIN_ (_uDepthW_ , _MAX_ ( _cVegHeightWin_ , _cVegHeight_) ) ) / _cLengMort_) _ELSEIF_ ( _aVegWin_ _EQ_ 0 _AND_  _uVegHeight_ _LT_ _MIN_ (_cVegHeight_, _uDepthW_) ) _THEN_  _MIN_ ( _cVegHeight_ - _uVegHeight_ , ( _MIN_ (_uDepthW_ , _MAX_ ( _cVegHeightWin_ , _cVegHeight_) ) -  _MIN_ ( _cVegHeightWin_ , _cVegHeight_ , _uDepthW_) ) / _cLengAllo_) _ELSEIF_ ( _aVegWin_ _EQ_ 0 _AND_  _uVegHeight_ _GT_ _MIN_ (_cVegHeight_, _uDepthW_) ) _THEN_ _MAX_ ( _uVegHeight_ -  _cVegHeight_, ( _MIN_ ( _cVegHeightWin_ , _cVegHeight_ , _uDepthW_) - _MIN_ (_uDepthW_ , _MAX_ ( _cVegHeightWin_ , _cVegHeight_) ) ) / _cLengMort_) _ELSE_ 0.0 _ENDIF_
```

### `_dDBent_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Zoobenthos_in_lake_sediment
- **Equation**:

```
_dDBent_ = _tDWebBent_ - _tDDredBent_
```

### `_dNBent_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Zoobenthos_in_lake_sediment
- **Equation**:

```
_dNBent_ = _tNWebBent_ - _tNDredBent_
```

### `_dPBent_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Zoobenthos_in_lake_sediment
- **Equation**:

```
_dPBent_ = _tPWebBent_ - _tPDredBent_
```

### `_dDepthWM_`  [_m_*_d_^-1]
- **Description**: Derivative_for_water_depth_change_in_marsh_water
- **Equation**:

```
_dDepthWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _vTranDepthW_ + _vDeltaWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNH4WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_NH4_in_water_in_marsh_water
- **Equation**:

```
_dNH4WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _tNDifNH4M_/_uDepthWM_ - _wNNitrWM_ + _wNMinDetWM_ - _tNEvNH4WM_/_uDepthWM_ - _tNInfNH4WM_/_uDepthWM_ + _tNSeepNH4WM_/_uDepthWM_ + _wNExchNH4MEpi_ + _wNExchNH4MHyp_ - _aRelDeltaWM_ * _oNH4WM_ + _wNAdvNH4WM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNO3WM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_NO3_in_water_in_marsh_water
- **Equation**:

```
_dNO3WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _tNDifNO3M_/_uDepthWM_ + _wNNitrWM_ - _wNDenitWM_ - _tNEvNO3WM_/_uDepthWM_ - _tNInfNO3WM_/_uDepthWM_ + _tNSeepNO3WM_/_uDepthWM_ + _wNExchNO3MEpi_ + _wNExchNO3MHyp_- _aRelDeltaWM_ * _oNO3WM_ + _wNAdvNO3WM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPO4WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_PO4_in_water_in_marsh_water
- **Equation**:

```
_dPO4WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( - _tPInfPO4WM_ / _uDepthWM_ + _tPSeepPO4WM_ / _uDepthWM_ + _tPDifPO4M_ / _uDepthWM_ + _wPMinDetWM_ - _tPEvPO4WM_ / _uDepthWM_ - _wPSorpIMWM_ + _wPExchPO4MEpi_ + _wPExchPO4MHyp_ - _aRelDeltaWM_ * _oPO4WM_ + _wPAdvPO4WM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPAIMWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P_adsorbed_onto_IM_in_water_in_marsh_water
- **Equation**:

```
_dPAIMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( - _tPSetAIMM_ / _uDepthWM_ + _wPSorpIMWM_ + _wPExchAIMMEpi_+ _wPExchAIMMHyp_ - _aRelDeltaWM_ * _oPAIMWM_ + _wPAdvAIMWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dSiO2WM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_sio2_in_marsh_water
- **Equation**:

```
_dSiO2WM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wSiMinDetWM_ + _tSiMinDetSM_ / _uDepthWM_ + _wSiExchSiO2MEpi_ + _wSiExchSiO2MHyp_- _aRelDeltaWM_ * _oSiO2WM_ + _wSiAdvSiO2WM_/_uDepthWM_ - _tInfSiO2WM_ /_uDepthWM_ + _tSeepSiO2WM_ /_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDDetWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Detritus_in_marsh_water
- **Equation**:

```
_dDDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _tDMortShootPhra_/_uDepthWM_ - _tDSetDetM_/_uDepthWM_ - _wDMinDetWM_ + _wDExchDetMEpi_ + _wDExchDetMHyp_- _aRelDeltaWM_ * _oDDetWM_ + _wDAdvDetWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNDetWM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_detritus_in_marsh_water
- **Equation**:

```
_dNDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _tNMortShootPhra_ / _uDepthWM_ - _tNSetDetM_ / _uDepthWM_ - _wNMinDetWM_ + _wNExchDetMEpi_ + _wNExchDetMHyp_ - _aRelDeltaWM_ * _oNDetWM_ + _wNAdvDetWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPDetWM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_detritus_in_marsh_water
- **Equation**:

```
_dPDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _tPMortShootPhra_ / _uDepthWM_ - _tPSetDetM_ / _uDepthWM_ - _wPMinDetWM_ + _wPExchDetMEpi_ + _wPExchDetMHyp_ - _aRelDeltaWM_ * _oPDetWM_ + _wPAdvDetWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dSiDetWM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_detritus_in_marsh_water
- **Equation**:

```
_dSiDetWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( - _tSiSetDetM_ / _uDepthWM_ - _wSiMinDetWM_ + _wSiExchDetMEpi_ + _wSiExchDetMHyp_ - _aRelDeltaWM_ * _oSiDetWM_ + _wSiAdvDetWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDIMWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Inorg_matter_in_marsh_water
- **Equation**:

```
_dDIMWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( - _tDSetIMM_/_uDepthWM_ + _wDExchIMMEpi_ + _wDExchIMMHyp_ - _aRelDeltaWM_ * _oDIMWM_ + _wDAdvIMWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDDiatWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_diatoms_in_marsh_water
- **Equation**:

```
_dDDiatWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wDExchDiatMEpi_ +_wDExchDiatMHyp_ - _tDSetDiatM_ / _uDepthWM_ - _aRelDeltaWM_ * _oDDiatWM_ + _wDAdvDiatWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNDiatWM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_diatoms_in_marsh_water
- **Equation**:

```
_dNDiatWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wNExchDiatMEpi_ + _wNExchDiatMHyp_ - _tNSetDiatM_ / _uDepthWM_ - _aRelDeltaWM_ * _oNDiatWM_ + _wNAdvDiatWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPDiatWM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_diatoms_in_marsh_water
- **Equation**:

```
_dPDiatWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wPExchDiatMEpi_ +_wPExchDiatMHyp_ - _tPSetDiatM_ / _uDepthWM_ - _aRelDeltaWM_ * _oPDiatWM_ + _wPAdvDiatWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDGrenWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_greens_in_marsh_water
- **Equation**:

```
_dDGrenWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wDExchGrenMEpi_ + _wDExchGrenMHyp_- _tDSetGrenM_ / _uDepthWM_ - _aRelDeltaWM_ * _oDGrenWM_ + _wDAdvGrenWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNGrenWM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_greens_in_marsh_water
- **Equation**:

```
_dNGrenWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wNExchGrenMEpi_ + _wNExchGrenMHyp_ - _tNSetGrenM_ / _uDepthWM_ - _aRelDeltaWM_ * _oNGrenWM_ + _wNAdvGrenWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPGrenWM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_greens_in_marsh_water
- **Equation**:

```
_dPGrenWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wPExchGrenMEpi_ + _wPExchGrenMHyp_ - _tPSetGrenM_ / _uDepthWM_ - _aRelDeltaWM_ * _oPGrenWM_ + _wPAdvGrenWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDBlueWM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_blue-greens_in_marsh_water
- **Equation**:

```
_dDBlueWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wDExchBlueMEpi_ + _wDExchBlueMHyp_- _tDSetBlueM_ / _uDepthWM_ - _aRelDeltaWM_ * _oDBlueWM_ + _wDAdvBlueWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNBlueWM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_blue-greens_in_marsh_water
- **Equation**:

```
_dNBlueWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wNExchBlueMEpi_ + _wNExchBlueMHyp_ - _tNSetBlueM_ / _uDepthWM_ - _aRelDeltaWM_ * _oNBlueWM_ + _wNAdvBlueWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPBlueWM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_blue-greens_in_marsh_water
- **Equation**:

```
_dPBlueWM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wPExchBlueMEpi_ + _wPExchBlueMHyp_ - _tPSetBlueM_ / _uDepthWM_ - _aRelDeltaWM_ * _oPBlueWM_ + _wPAdvBlueWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDZooM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_zooplankton_in_marsh_water
- **Equation**:

```
_dDZooM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wDExchZooMEpi_ + _wDExchZooMHyp_ - _aRelDeltaWM_ * _oDZooM_ + _wDAdvZooWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNZooM_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_zooplankton_in_marsh_water
- **Equation**:

```
_dNZooM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wNExchZooMEpi_ + _wNExchZooMHyp_ - _aRelDeltaWM_ * _oNZooM_ + _wNAdvZooWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPZooM_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_zooplankton_in_marsh_water
- **Equation**:

```
_dPZooM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ ( _wPExchZooMEpi_ + _wPExchZooMHyp_ - _aRelDeltaWM_ * _oPZooM_ + _wPAdvZooWM_/_uDepthWM_) * _MassWM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNH4SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_NH4_in_water_in_marsh_sediment
- **Equation**:

```
_dNH4SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNInfNH4WM_ - _tNSeepNH4WM_ - _tNInfNH4SM_ + _tNSeepNH4SM_ +(1.0-_fRefrDetS_) * _tNMinDetSM_ + _tNMinHumSM_ - _tNDifNH4M_ - _tNDifGroundNH4M_ - _tNNitrSM_ - _tNBurNH4M_ - _tNUptNH4PhraS_ + _tNEvNH4WM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNO3SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_NO3_in_marsh_sediment
- **Equation**:

```
_dNO3SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNInfNO3WM_ - _tNSeepNO3WM_ - _tNInfNO3SM_ + _tNSeepNO3SM_ + _tNNitrSM_ - _tNDenitSM_ - _tNDifNO3M_ - _tNDifGroundNO3M_ - _tNBurNO3M_ - _tNUptNO3PhraS_ + _tNEvNO3WM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPO4SM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_PO4_in_marsh_sediment
- **Equation**:

```
_dPO4SM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPInfPO4WM_ - _tPSeepPO4WM_- _tPInfPO4SM_ + _tPSeepPO4SM_ + _tPEvPO4WM_ +(1.0-_fRefrDetS_) * _tPMinDetSM_ + _tPMinHumSM_ - _tPSorpIMSM_ - _tPDifPO4M_ - _tPDifGroundPO4M_ - _tPChemPO4M_ - _tPUptPhraS_ - _tPBurPO4M_ _ELSE_ 0.0 _ENDIF_
```

### `_dPAIMSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P_adsorbed_onto_IM_in_marsh_sediment
- **Equation**:

```
_dPAIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPSetAIMM_ - _tPBurAIMM_ + _tPSorpIMSM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDDetSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Detritus_in_marsh_sediment
- **Equation**:

```
_dDDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDMortRootPhra_ + _tDSetDetM_ - _tDMinDetSM_ + _tDSetPhytM_ - _tDBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNDetSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_detritus_in_marsh_sediment
- **Equation**:

```
_dNDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNMortRootPhra_ + _tNSetDetM_ - _tNMinDetSM_ + _tNSetPhytM_ - _tNBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPDetSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_detritus_in_marsh_sediment
- **Equation**:

```
_dPDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPMortRootPhra_ + _tPSetDetM_ - _tPMinDetSM_ + _tPSetPhytM_ - _tPBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_dSiDetSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_detritus_in_marsh_sediment
- **Equation**:

```
_dSiDetSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tSiSetDetM_ - _tSiMinDetSM_ + _cSiDDiat_ * _tDSetDiatM_ - _tSiBurDetM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDHumSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_sediment_humus_in_marsh_sediment
- **Equation**:

```
_dDHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fRefrDetS_ * _tDMinDetSM_ - _tDMinHumSM_ - _tDBurHumM_ _ELSE_ 0.0 _ENDIF_
```

### `_dNHumSM_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_sediment_humus_in_marsh_sediment
- **Equation**:

```
_dNHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fRefrDetS_ * _tNMinDetSM_ - _tNMinHumSM_ - _tNBurHumM_ _ELSE_ 0.0 _ENDIF_
```

### `_dPHumSM_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_sediment_humus_in_marsh_sediment
- **Equation**:

```
_dPHumSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _fRefrDetS_ * _tPMinDetSM_ - _tPMinHumSM_ - _tPBurHumM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDIMSM_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Inorg_matter_in_sediment_in_marsh_sediment
- **Equation**:

```
_dDIMSM_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDSetIMM_ - _tDBurIMM_ _ELSE_ 0.0 _ENDIF_
```

### `_dDRootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_biomass_root_reed_in_marsh_sediment
- **Equation**:

```
_dDRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDProdRootPhra_ - _tDRespRootPhra_ - _tDMortRootPhra_ - _tDAllPhra_ + _tDRealPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dDShootPhra_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_biomass_shoot_reed_in_marsh_sediment
- **Equation**:

```
_dDShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tDProdShootPhra_ - _tDRespShootPhra_ - _tDMortShootPhra_ + _tDAllPhra_ - _tDRealPhra_ - _tDManShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dNRootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_N_in_root_in_marsh_sediment
- **Equation**:

```
_dNRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNUptRootPhra_ - _tNMortRootPhra_ - _tNTransPhra_ + _tNRetrPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dNShootPhra_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_N_in_shoot_in_marsh_sediment
- **Equation**:

```
_dNShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tNUptShootPhra_ - _tNMortShootPhra_ + _tNTransPhra_ - _tNRetrPhra_ - _tNManShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dPRootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P_in_root_in_marsh_sediment
- **Equation**:

```
_dPRootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPUptRootPhra_ - _tPMortRootPhra_ - _tPTransPhra_ + _tPRetrPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dPShootPhra_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P_in_shoot_in_marsh_sediment
- **Equation**:

```
_dPShootPhra_ = _IF_ (_InclMarsh_ _EQ_ _TRUE_ _AND_ _fMarsh_ _GT_ _NearZero_) _THEN_ _tPUptShootPhra_ - _tPMortShootPhra_ + _tPTransPhra_ - _tPRetrPhra_ - _tPManShootPhra_ _ELSE_ 0.0 _ENDIF_
```

### `_dNH4WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_ammonium_in_water_in_lake_water
- **Equation**:

```
_dNH4WEpi_ = ( _wNTranNH4WEpi_ + _wNAbioNH4WEpi_ + _wNPrimNH4WEpi_ + _wNBedNH4WEpi_ + _wNWebNH4WEpi_ + _cNBackLoad_ / _uDepthWEpi_ - _aRelDeltaWEpi_ * _oNH4WEpi_ - _wNExchNH4Epi_ + _wNExchNH4WEpi_  + _wNAdvNH4W_ / _uDepthWEpi_  - _wNAdvNH4WM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNO3WEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_nitrate_in_water_in_lake_water
- **Equation**:

```
_dNO3WEpi_ = ( _wNTranNO3WEpi_ + _wNAbioNO3WEpi_ + _wNPrimNO3WEpi_ + _wNBedNO3WEpi_ + _wNWebNO3WEpi_ - _aRelDeltaWEpi_ * _oNO3WEpi_ - _wNExchNO3Epi_ + _wNExchNO3WEpi_  + _wNAdvNO3W_ / _uDepthWEpi_  - _wNAdvNO3WM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPO4WEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_SRP_in_water_in_lake_water
- **Equation**:

```
_dPO4WEpi_ = ( _wPTranPO4WEpi_ + _wPAbioPO4WEpi_ + _wPPrimPO4WEpi_ + _wPBedPO4WEpi_ + _wPWebPO4WEpi_ + _cPBackLoad_ / _uDepthWEpi_ - _aRelDeltaWEpi_ * _oPO4WEpi_ - _wPExchPO4Epi_ + _wPExchPO4WEpi_  + _wPAdvPO4W_ / _uDepthWEpi_  - _wPAdvPO4WM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPAIMWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_P-adsorbed_onto_IM_in_water_in_lake_water
- **Equation**:

```
_dPAIMWEpi_ = ( _wPTranAIMWEpi_ + _wPAbioAIMWEpi_ - _aRelDeltaWEpi_ * _oPAIMWEpi_ - _wPExchAIMEpi_ + _wPExchAIMWEpi_  + _wPAdvAIMW_ / _uDepthWEpi_  - _wPAdvAIMWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dSiO2WEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_dissolved_silica_in_water_in_lake_water
- **Equation**:

```
_dSiO2WEpi_ = ( _wSiTranSiO2Epi_ + _wSiAbioSiO2WEpi_ + _wSiPrimSiO2WEpi_ - _aRelDeltaWEpi_ * _oSiO2WEpi_ - _wSiExchSiO2Epi_ + _wSiExchSiO2WEpi_  + _wSiAdvSiO2W_ / _uDepthWEpi_  - _wSiAdvSiO2WM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDDetWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Detritus_in_lake_water
- **Equation**:

```
_dDDetWEpi_ = ( _wDTranDetWEpi_ + _wDAbioDetWEpi_ + _wDPrimDetWEpi_ + _wDBedDetWEpi_ + _wDWebDetWEpi_ - _aRelDeltaWEpi_ * _oDDetWEpi_ - _wDExchDetEpi_ + _wDExchDetWEpi_  + _wDAdvDetW_ / _uDepthWEpi_  - _wDAdvDetWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNDetWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Detritus_in_lake_water
- **Equation**:

```
_dNDetWEpi_ = ( _wNTranDetWEpi_ + _wNAbioDetWEpi_ + _wNPrimDetWEpi_ + _wNBedDetWEpi_ + _wNWebDetWEpi_ - _aRelDeltaWEpi_ * _oNDetWEpi_ - _wNExchDetEpi_ + _wNExchDetWEpi_  + _wNAdvDetW_ / _uDepthWEpi_  - _wNAdvDetWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPDetWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Detritus_in_lake_water
- **Equation**:

```
_dPDetWEpi_ = ( _wPTranDetWEpi_ + _wPAbioDetWEpi_ + _wPPrimDetWEpi_ + _wPBedDetWEpi_ + _wPWebDetWEpi_ - _aRelDeltaWEpi_ * _oPDetWEpi_ - _wPExchDetEpi_ + _wPExchDetWEpi_  + _wPAdvDetW_ / _uDepthWEpi_  - _wPAdvDetWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dSiDetWEpi_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_Si_Detritus_in_lake_water
- **Equation**:

```
_dSiDetWEpi_ = ( _wSiTranDetWEpi_ + _wSiAbioDetWEpi_ + _wSiPrimDetWEpi_ + _wSiWebDetWEpi_ - _aRelDeltaWEpi_ * _oSiDetWEpi_ - _wSiExchDetEpi_ + _wSiExchDetWEpi_  + _wSiAdvDetW_ / _uDepthWEpi_  - _wSiAdvDetWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDIMWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_inorg_matter_in_water_in_lake_water
- **Equation**:

```
_dDIMWEpi_ = ( _wDTranIMWEpi_ + _wDAbioIMWEpi_ - _aRelDeltaWEpi_ * _oDIMWEpi_ - _wDExchIMEpi_ + _wDExchIMWEpi_  + _wDAdvIMW_ / _uDepthWEpi_  - _wDAdvIMWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDDiatWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Diatoms_in_lake_water
- **Equation**:

```
_dDDiatWEpi_ = ( _wDTranDiatEpi_ + _wDPrimDiatWEpi_ + _wDWebDiatWEpi_ - _aRelDeltaWEpi_ * _oDDiatWEpi_ - _wDExchDiatEpi_ + _wDExchDiatWEpi_  + _wDAdvDiatW_ / _uDepthWEpi_  - _wDAdvDiatWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNDiatWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Diatoms_in_lake_water
- **Equation**:

```
_dNDiatWEpi_ = ( _wNTranDiatEpi_ + _wNPrimDiatWEpi_ + _wNWebDiatWEpi_ - _aRelDeltaWEpi_ * _oNDiatWEpi_ - _wNExchDiatEpi_ + _wNExchDiatWEpi_  + _wNAdvDiatW_ / _uDepthWEpi_  - _wNAdvDiatWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPDiatWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Diatoms_in_lake_water
- **Equation**:

```
_dPDiatWEpi_ = ( _wPTranDiatEpi_ + _wPPrimDiatWEpi_ + _wPWebDiatWEpi_ - _aRelDeltaWEpi_ * _oPDiatWEpi_ - _wPExchDiatEpi_ + _wPExchDiatWEpi_  + _wPAdvDiatW_ / _uDepthWEpi_  - _wPAdvDiatWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDGrenWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Greens_in_lake_water
- **Equation**:

```
_dDGrenWEpi_ = ( _wDTranGrenEpi_ + _wDPrimGrenWEpi_ + _wDWebGrenWEpi_ - _aRelDeltaWEpi_ * _oDGrenWEpi_ - _wDExchGrenEpi_ + _wDExchGrenWEpi_  + _wDAdvGrenW_ / _uDepthWEpi_  - _wDAdvGrenWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNGrenWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Greens_in_lake_water
- **Equation**:

```
_dNGrenWEpi_ = ( _wNTranGrenEpi_ + _wNPrimGrenWEpi_ + _wNWebGrenWEpi_ - _aRelDeltaWEpi_ * _oNGrenWEpi_ - _wNExchGrenEpi_ + _wNExchGrenWEpi_  + _wNAdvGrenW_ / _uDepthWEpi_  - _wNAdvGrenWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPGrenWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Greens_in_lake_water
- **Equation**:

```
_dPGrenWEpi_ = ( _wPTranGrenEpi_ + _wPPrimGrenWEpi_ + _wPWebGrenWEpi_ - _aRelDeltaWEpi_ * _oPGrenWEpi_ - _wPExchGrenEpi_ + _wPExchGrenWEpi_  + _wPAdvGrenW_ / _uDepthWEpi_  - _wPAdvGrenWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDBlueWEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Blue_greens_in_lake_water
- **Equation**:

```
_dDBlueWEpi_ = ( _wDTranBlueEpi_ + _wDPrimBlueWEpi_ + _wDWebBlueWEpi_ - _aRelDeltaWEpi_ * _oDBlueWEpi_ - _wDExchBlueEpi_ + _wDExchBlueWEpi_  + _wDAdvBlueW_ / _uDepthWEpi_  - _wDAdvBlueWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNBlueWEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Blue_greens_in_lake_water
- **Equation**:

```
_dNBlueWEpi_ = ( _wNTranBlueEpi_ + _wNPrimBlueWEpi_ + _wNWebBlueWEpi_ - _aRelDeltaWEpi_ * _oNBlueWEpi_ - _wNExchBlueEpi_ + _wNExchBlueWEpi_  + _wNAdvBlueW_ / _uDepthWEpi_  - _wNAdvBlueWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPBlueWEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Blue_greens_in_lake_water
- **Equation**:

```
_dPBlueWEpi_ = ( _wPTranBlueEpi_ + _wPPrimBlueWEpi_ + _wPWebBlueWEpi_ - _aRelDeltaWEpi_ * _oPBlueWEpi_ - _wPExchBlueEpi_ + _wPExchBlueWEpi_  + _wPAdvBlueW_ / _uDepthWEpi_  - _wPAdvBlueWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDZooEpi_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Zooplankton_in_lake_water
- **Equation**:

```
_dDZooEpi_ =  ( _wDTranZooEpi_ + _wDWebZooEpi_ - _aRelDeltaWEpi_ * _oDZooEpi_ - _wDExchZooEpi_ + _wDExchZooWEpi_  + _wDAdvZooW_ / _uDepthWEpi_  - _wDAdvZooWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dNZooEpi_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Zooplankton_in_lake_water
- **Equation**:

```
_dNZooEpi_ =  ( _wNTranZooEpi_ + _wNWebZooEpi_ - _aRelDeltaWEpi_ * _oNZooEpi_ - _wNExchZooEpi_ + _wNExchZooWEpi_  + _wNAdvZooW_ / _uDepthWEpi_  - _wNAdvZooWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dPZooEpi_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Zooplankton_in_lake_water
- **Equation**:

```
_dPZooEpi_ =  ( _wPTranZooEpi_ + _wPWebZooEpi_ - _aRelDeltaWEpi_ * _oPZooEpi_ - _wPExchZooEpi_ + _wPExchZooWEpi_  + _wPAdvZooW_ / _uDepthWEpi_  - _wPAdvZooWM_/_uDepthWM_ * _afVolMarshEpi_) * _MassEpi_
```

### `_dDBlueSurf_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_DW_Bluegreens_on_surface_layer
- **Equation**:

```
_dDBlueSurf_ =_tDTranBlueSurf_ + _tDPrimBlueSurf_ + _tDWebBlueSurf_
```

### `_dNBlueSurf_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_N_Bluegreens_on_surface_layer
- **Equation**:

```
_dNBlueSurf_ = _tNTranBlueSurf_ + _tNPrimBlueSurf_ + _tNWebBlueSurf_
```

### `_dPBlueSurf_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_P_Bluegreens_on_surface_layer
- **Equation**:

```
_dPBlueSurf_ = _tPTranBlueSurf_ + _tPPrimBlueSurf_ + _tPWebBlueSurf_
```

### `_dDExtTotT_`  [_gDW_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_total_external_DW_flux
- **Equation**:

```
_dDExtTotT_ = (_uDLoadEpi_ + _uDLoadHyp_) - _wDOutflTotEpi_*_uDepthWEpi_ - _tDDilBlueSurf_ - _wDOutflTotHyp_*_uDepthWHyp_ + _wDTranZooEpi_ * _uDepthWEpi_ + _wDTranZooHyp_ * _uDepthWHyp_ - _tDBurTot_ + _tDAbioTotT_ + _tDPrimTotT_ + _tDBedTotT_ + _tDWebTotT_+ _tDMarsTotT_ - _tDDredNetTot_ - _aDRelTotT_
```

### `_dNExtTotT_`  [_gN_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_total_external_N_flux
- **Equation**:

```
_dNExtTotT_ = (_uNLoadEpi_ + _uNLoadHyp_) - _wNOutflTotEpi_ * _uDepthWEpi_  - _tNDilBlueSurf_- _wNOutflTotHyp_ * _uDepthWHyp_+ _wNTranZooHyp_ * _uDepthWHyp_ + _wNTranZooEpi_ * _uDepthWEpi_ + _cNBackLoad_ - _tNBurTot_ + _tNAbioTotT_ + _tNPrimTotT_ + _tNBedTotT_ + _tNWebTotT_ + _tNMarsTotT_ - _tNDredNetTot_ - _aNRelTotT_ + _tNUptBlueAirSurf_ + _tNUptBlueAirEpi_ + _tNUptBlueAirHyp_
```

### `_dPExtTotT_`  [_gP_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_total_external_P_flux
- **Equation**:

```
_dPExtTotT_ = (_uPLoadEpi_ + _uPLoadHyp_) - _wPOutflTotHyp_ * _uDepthWHyp_  - _tPDilBlueSurf_ - _wPOutflTotEpi_ * _uDepthWEpi_ + _wPTranZooHyp_ * _uDepthWHyp_ + _wPTranZooEpi_ * _uDepthWEpi_ + _cPBackLoad_ - _tPBurTot_ + _tPAbioTotT_ + _tPPrimTotT_ + _tPBedTotT_ + _tPWebTotT_ + _tPMarsTotT_- _tPDredNetTot_ - _aPRelTotT_
```

### `_dSiExtTotT_`  [_gSi_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_total_external_Si_flux
- **Equation**:

```
_dSiExtTotT_ = (_uSiLoadEpi_ + _uSiLoadHyp_) - _wSiDilTotHyp_*_uDepthWHyp_ - _wSiDilTotEpi_*_uDepthWEpi_ + _tSiAbioTotT_ - _tSiBurTot_ + _tSiPrimTotT_ + _tSiMarsTotT_ - _tSiDredTot_ +_tSiWebTotT_ - _aSiRelTotT_
```

### `_dO2ExtTotT_`  [_gO2_*_m_^-2*_d_^-1]
- **Description**: Derivative_for_total_external_O2_flux
- **Equation**:

```
_dO2ExtTotT_ = _wO2TranWHyp_ * _uDepthWHyp_ + _wO2TranWEpi_ * _uDepthWEpi_ + _tO2BedWHyp_ + _tO2BedWEpi_ + _wO2PrimWHyp_ * _uDepthWHyp_ + _wO2PrimWEpi_ * _uDepthWEpi_ + _wO2AbioWHyp_ * _uDepthWHyp_ + _wO2AbioWEpi_ * _uDepthWEpi_ + _wO2AbioM_* _uDepthWM_ * _fMarsh_ - _tO2PrimS_ - _tO2FlowPhra_ * _fMarsh_ - _aO2RelTotT_
```

### `_dDepthExtTotT_`  [_m_]
- **Description**: Derivative_for_total_external_Q_flux
- **Equation**:

```
_dDepthExtTotT_ = (_uQPrec_ + _uQInEpi_ + _uQInHyp_ + _uQInSeep_ - _uQEv_ - _uQOutEpi_ - _uQOutHyp_ - _uQOutCor_ - _uQOutInf_) / _mmPerm_
```

