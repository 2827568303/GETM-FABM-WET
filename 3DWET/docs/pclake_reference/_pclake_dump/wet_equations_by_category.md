# WET Equations by Category

Total equations: 2584

## Aging

### `tCAgeBiv` [g/m2/s] *Aging*
- DESC: default: C aging flux (zero)
- Source: bivalves.F90 (537)
- Formula (d⁻¹): `tCAgeBiv = 0.0_rk`
- Code: `tCAgeBiv = 0.0_rk`

### `tCAgeBiv` [g/m2/s] *Aging*
- DESC: aging C flux
- Source: bivalves.F90 (563)
- Formula (d⁻¹): `tCAgeBiv = rCDBiv * tDAgeBiv`
- Code: `tCAgeBiv = rCDBiv * tDAgeBiv`

### `tDAgeBiv` [g/m2/s] *Aging*
- DESC: default: DW aging flux (zero)
- Source: bivalves.F90 (534)
- Formula (d⁻¹): `tDAgeBiv = 0.0_rk`
- Code: `tDAgeBiv = 0.0_rk`

### `tDAgeBiv` [g/m2/s] *Aging*
- DESC: case qStageOpt=2 or 3: DW aging flux
- Source: bivalves.F90 (560)
- Formula (d⁻¹): `tDAgeBiv = self%fAgeBiv * sDBiv`
- Code: `tDAgeBiv = self%fAgeBiv * sDBiv`

### `tNAgeBiv` [g/m2/s] *Aging*
- DESC: default: N aging flux (zero)
- Source: bivalves.F90 (536)
- Formula (d⁻¹): `tNAgeBiv = 0.0_rk`
- Code: `tNAgeBiv = 0.0_rk`

### `tNAgeBiv` [g/m2/s] *Aging*
- DESC: aging N flux
- Source: bivalves.F90 (561)
- Formula (d⁻¹): `tNAgeBiv = rNDBiv * tDAgeBiv`
- Code: `tNAgeBiv = rNDBiv * tDAgeBiv`

### `tPAgeBiv` [g/m2/s] *Aging*
- DESC: default: P aging flux (zero)
- Source: bivalves.F90 (535)
- Formula (d⁻¹): `tPAgeBiv = 0.0_rk`
- Code: `tPAgeBiv = 0.0_rk`

### `tPAgeBiv` [g/m2/s] *Aging*
- DESC: aging P flux
- Source: bivalves.F90 (562)
- Formula (d⁻¹): `tPAgeBiv = rPDBiv * tDAgeBiv`
- Code: `tPAgeBiv = rPDBiv * tDAgeBiv`

## Assimilation

### `afCAssZoo` [-] *Assimilation*
- DESC: calculate C assimilation efficiency
- Source: zooplankton.F90 (323)
- Formula (d⁻¹): `min(1.0_rk,cCDRef / rCDFoodZoo * fDAssZoo)`
- Code: `afCAssZoo = min(1.0_rk,self%cCDRef / rCDFoodZoo * self%fDAssZoo)`

### `afNAssZoo` [-] *Assimilation*
- DESC: calculate N assimilation efficiency
- Source: zooplankton.F90 (311)
- Formula (d⁻¹): `min(1.0_rk,cNDRef / rNDFoodZoo * fDAssZoo)`
- Code: `afNAssZoo = min(1.0_rk,self%cNDRef / rNDFoodZoo * self%fDAssZoo)`

### `afPAssZoo` [-] *Assimilation*
- DESC: calculate P assimilation efficiency
- Source: zooplankton.F90 (317)
- Formula (d⁻¹): `min(1.0_rk,cPDRef / rPDFoodZoo * fDAssZoo)`
- Code: `afPAssZoo = min(1.0_rk,self%cPDRef / rPDFoodZoo * self%fDAssZoo)`

### `wCAssZoo` [gC/m3/s] *Assimilation*
- DESC: calculate C assimilation rate
- Source: zooplankton.F90 (324)
- Formula (d⁻¹): `afCAssZoo * wCConsZooTot`
- Code: `wCAssZoo = afCAssZoo* wCConsZooTot`

### `wDAssZoo` [gDW/m3/s] *Assimilation*
- DESC: calculate total assimilation
- Source: zooplankton.F90 (294)
- Formula (d⁻¹): `fDAssZoo * sum(wDConsZoo)`
- Code: `wDAssZoo = self%fDAssZoo * sum(wDConsZoo)`

### `wNAssZoo` [gN/m3/s] *Assimilation*
- DESC: calculate N assimilation rate
- Source: zooplankton.F90 (312)
- Formula (d⁻¹): `afNAssZoo * wNConsZooTot`
- Code: `wNAssZoo = afNAssZoo* wNConsZooTot`

### `wPAssZoo` [gP/m3/s] *Assimilation*
- DESC: calculate P assimilation rate
- Source: zooplankton.F90 (318)
- Formula (d⁻¹): `afPAssZoo * wPConsZooTot`
- Code: `wPAssZoo = afPAssZoo* wPConsZooTot`

### `afCAssBent` [-] *Assimilation*
- DESC: calculate C assimilation efficiency
- Source: zoobenthos.F90 (357)
- Formula (d⁻¹): `min(1.0_rk,cCDRef / rCDFoodBent * fDAssBent)`
- Code: `afCAssBent = min(1.0_rk,self%cCDRef / rCDFoodBent * self%fDAssBent)`

### `afNAssBent` [-] *Assimilation*
- DESC: calculate N assimilation efficiency
- Source: zoobenthos.F90 (345)
- Formula (d⁻¹): `min(1.0_rk,cNDRef / rNDFoodBent * fDAssBent)`
- Code: `afNAssBent = min(1.0_rk,self%cNDRef / rNDFoodBent * self%fDAssBent)`

### `afPAssBent` [-] *Assimilation*
- DESC: calculate P assimilation efficiency
- Source: zoobenthos.F90 (351)
- Formula (d⁻¹): `min(1.0_rk,cPDRef / rPDFoodBent * fDAssBent)`
- Code: `afPAssBent = min(1.0_rk,self%cPDRef / rPDFoodBent * self%fDAssBent)`

### `tCAssBent` [gC/m2/s] *Assimilation*
- DESC: calculate C assimilation rate
- Source: zoobenthos.F90 (358)
- Formula (d⁻¹): `afCAssBent * tCConsBentTot`
- Code: `tCAssBent = afCAssBent * tCConsBentTot`

### `tDAssBent` [gDW/m2/s] *Assimilation*
- DESC: calculate total assimilation
- Source: zoobenthos.F90 (328)
- Formula (d⁻¹): `fDAssBent * sum(tDConsBent)`
- Code: `tDAssBent = self%fDAssBent * sum(tDConsBent)`

### `tNAssBent` [gN/m2/s] *Assimilation*
- DESC: calculate N assimilation rate
- Source: zoobenthos.F90 (346)
- Formula (d⁻¹): `afNAssBent * tNConsBentTot`
- Code: `tNAssBent = afNAssBent * tNConsBentTot`

### `tPAssBent` [gP/m2/s] *Assimilation*
- DESC: calculate P assimilation rate
- Source: zoobenthos.F90 (352)
- Formula (d⁻¹): `afPAssBent * tPConsBentTot`
- Code: `tPAssBent = afPAssBent * tPConsBentTot`

### `afCAssFiBent` [-] *Assimilation*
- DESC: calculate C assimilation efficiency of benthos
- Source: fish.F90 (803)
- Formula (d⁻¹): `afCAssFiBent = min(1.0_rk,(self%cCDRef / rCDBent) * self%fDAssFi)`
- Code: `afCAssFiBent = min(1.0_rk,(self%cCDRef / rCDBent) * self%fDAssFi)`

### `afCAssFiPisc` [-] *Assimilation*
- DESC: calculate C assimilation efficiency of fish
- Source: fish.F90 (820)
- Formula (d⁻¹): `afCAssFiPisc = min(1.0_rk,(self%cCDRef / rCDPisc) * self%fDAssFi)`
- Code: `afCAssFiPisc = min(1.0_rk,(self%cCDRef / rCDPisc) * self%fDAssFi)`

### `afCAssFiPlan` [-] *Assimilation*
- DESC: calculate C assimilation efficiency of plankton
- Source: fish.F90 (786)
- Formula (d⁻¹): `afCAssFiPlan = min(1.0_rk,(self%cCDRef / rCDPlan) * self%fDAssFi)`
- Code: `afCAssFiPlan = min(1.0_rk,(self%cCDRef / rCDPlan) * self%fDAssFi)`

### `afNAssFiBent` [-] *Assimilation*
- DESC: calculate N assimilation efficiency of benthos
- Source: fish.F90 (793)
- Formula (d⁻¹): `afNAssFiBent = min(1.0_rk,(self%cNDRef / rNDBent) * self%fDAssFi)`
- Code: `afNAssFiBent = min(1.0_rk,(self%cNDRef / rNDBent) * self%fDAssFi)`

### `afNAssFiPisc` [-] *Assimilation*
- DESC: calculate N assimilation efficiency of fish
- Source: fish.F90 (810)
- Formula (d⁻¹): `afNAssFiPisc = min(1.0_rk,(self%cNDRef / rNDPisc) * self%fDAssFi)`
- Code: `afNAssFiPisc = min(1.0_rk,(self%cNDRef / rNDPisc) * self%fDAssFi)`

### `afNAssFiPlan` [-] *Assimilation*
- DESC: calculate N assimilation efficiency of plankton
- Source: fish.F90 (776)
- Formula (d⁻¹): `afNAssFiPlan = min(1.0_rk,(self%cNDRef / rNDPlan) * self%fDAssFi)`
- Code: `afNAssFiPlan = min(1.0_rk,(self%cNDRef / rNDPlan) * self%fDAssFi)`

### `afPAssFiBent` [-] *Assimilation*
- DESC: calculate P assimilation efficiency of benthos
- Source: fish.F90 (798)
- Formula (d⁻¹): `afPAssFiBent = min(1.0_rk,(self%cPDRef / rPDBent) * self%fDAssFi)`
- Code: `afPAssFiBent = min(1.0_rk,(self%cPDRef / rPDBent) * self%fDAssFi)`

### `afPAssFiPisc` [-] *Assimilation*
- DESC: calculate P assimilation efficiency of fish
- Source: fish.F90 (815)
- Formula (d⁻¹): `afPAssFiPisc = min(1.0_rk,(self%cPDRef / rPDPisc) * self%fDAssFi)`
- Code: `afPAssFiPisc = min(1.0_rk,(self%cPDRef / rPDPisc) * self%fDAssFi)`

### `afPAssFiPlan` [-] *Assimilation*
- DESC: calculate P assimilation efficiency of plankton
- Source: fish.F90 (781)
- Formula (d⁻¹): `afPAssFiPlan = min(1.0_rk,(self%cPDRef / rPDPlan) * self%fDAssFi)`
- Code: `afPAssFiPlan = min(1.0_rk,(self%cPDRef / rPDPlan) * self%fDAssFi)`

### `tCAssFiBent` [-] *Assimilation*
- DESC: calculate C assimilation rate from bentivory
- Source: fish.F90 (804)
- Formula (d⁻¹): `tCAssFiBent = afCAssFiBent * tCConsFiBent`
- Code: `tCAssFiBent = afCAssFiBent * tCConsFiBent`

### `tCAssFiPisc` [-] *Assimilation*
- DESC: calculate C assimilation rate from piscivory
- Source: fish.F90 (821)
- Formula (d⁻¹): `tCAssFiPisc = afCAssFiPisc * tCConsFiPisc`
- Code: `tCAssFiPisc = afCAssFiPisc * tCConsFiPisc`

### `tCAssFiPlan` [-] *Assimilation*
- DESC: calculate C assimilation rate from planktivy
- Source: fish.F90 (787)
- Formula (d⁻¹): `tCAssFiPlan = afCAssFiPlan * tCConsFiPlan`
- Code: `tCAssFiPlan = afCAssFiPlan * tCConsFiPlan`

### `tCAssFiTot` [-] *Assimilation*
- DESC: calculate total C assimilation rate
- Source: fish.F90 (827)
- Formula (d⁻¹): `tCAssFiTot = sum(tCAssFiPlan) + sum(tCAssFiBent) + sum(tCAssFiPisc)`
- Code: `tCAssFiTot = sum(tCAssFiPlan) + sum(tCAssFiBent) + sum(tCAssFiPisc)`

### `tCEgesFi` [-] *Assimilation*
- DESC: calculate C egestion rate
- Source: fish.F90 (849)
- Formula (d⁻¹): `tCEgesFi = tCConsFiTot - tCAssFiTot`
- Code: `tCEgesFi = tCConsFiTot - tCAssFiTot`

### `tDAssFiBent` [-] *Assimilation*
- DESC: calculate bentivorous assimilation rate
- Source: fish.F90 (730)
- Formula (d⁻¹): `tDAssFiBent = tDConsFiBentSum*self%fDAssFi`
- Code: `tDAssFiBent = tDConsFiBentSum*self%fDAssFi  !- tDEnvFi * fFishBent`

### `tDAssFiBentPot` [-] *Assimilation*
- DESC: calculate bentivorous assimilation rate at constant feeding
- Source: fish.F90 (670)
- Formula (d⁻¹): `tDAssFiBentPot = tDConsFiBentTotPot * self%fDAssFi * fFishBent`
- Code: `tDAssFiBentPot = tDConsFiBentTotPot * self%fDAssFi * fFishBent`

### `tDAssFiPisc` [-] *Assimilation*
- DESC: calculate piscivorous assimilation rate
- Source: fish.F90 (731)
- Formula (d⁻¹): `tDAssFiPisc = tDConsFiPiscSum*self%fDAssFi`
- Code: `tDAssFiPisc = tDConsFiPiscSum*self%fDAssFi !- tDEnvFi * fFishPisc`

### `tDAssFiPiscPot` [-] *Assimilation*
- DESC: calculate piscivorous assimilation rate at constant feeding
- Source: fish.F90 (671)
- Formula (d⁻¹): `tDAssFiPiscPot = tDConsFiPiscTotPot * self%fDAssFi * fFishPisc`
- Code: `tDAssFiPiscPot = tDConsFiPiscTotPot * self%fDAssFi * fFishPisc`

### `tDAssFiPlan` [-] *Assimilation*
- DESC: calculate planktivorous assimilation rate
- Source: fish.F90 (729)
- Formula (d⁻¹): `tDAssFiPlan = tDConsFiPlanSum*self%fDAssFi`
- Code: `tDAssFiPlan = tDConsFiPlanSum*self%fDAssFi  !- tDEnvFi * fFishPlan`

### `tDAssFiPlanPot` [-] *Assimilation*
- DESC: calculate planktivorous assimilation rate at constant feeding
- Source: fish.F90 (669)
- Formula (d⁻¹): `tDAssFiPlanPot = tDConsFiPlanTotPot * self%fDAssFi * fFishPlan`
- Code: `tDAssFiPlanPot = tDConsFiPlanTotPot * self%fDAssFi * fFishPlan`

### `tDAssFiTot` [-] *Assimilation*
- DESC: calculate total DW assimilation rate
- Source: fish.F90 (732)
- Formula (d⁻¹): `tDAssFiTot = tDAssFiPlan + tDAssFiBent + tDAssFiPisc`
- Code: `tDAssFiTot = tDAssFiPlan + tDAssFiBent + tDAssFiPisc`

### `tDAssFiTotPot` [-] *Assimilation*
- DESC: calculate total DW assimilation rate at constant feeding
- Source: fish.F90 (672)
- Formula (d⁻¹): `tDAssFiTotPot = tDAssFiPlanPot + tDAssFiBentPot + tDAssFiPiscPot`
- Code: `tDAssFiTotPot = tDAssFiPlanPot + tDAssFiBentPot + tDAssFiPiscPot`

### `tDEgesFi` [-] *Assimilation*
- DESC: calculate DW egestion rate
- Source: fish.F90 (846)
- Formula (d⁻¹): `tDEgesFi = tDConsFiTot - tDAssFiTot`
- Code: `tDEgesFi = tDConsFiTot - tDAssFiTot`

### `tNAssFiBent` [-] *Assimilation*
- DESC: calculate N assimilation rate from bentivory
- Source: fish.F90 (794)
- Formula (d⁻¹): `tNAssFiBent = afNAssFiBent * tNConsFiBent`
- Code: `tNAssFiBent = afNAssFiBent * tNConsFiBent`

### `tNAssFiPisc` [-] *Assimilation*
- DESC: calculate N assimilation rate from piscivory
- Source: fish.F90 (811)
- Formula (d⁻¹): `tNAssFiPisc = afNAssFiPisc * tNConsFiPisc`
- Code: `tNAssFiPisc = afNAssFiPisc * tNConsFiPisc`

### `tNAssFiPlan` [-] *Assimilation*
- DESC: calculate N assimilation rate from planktivory
- Source: fish.F90 (777)
- Formula (d⁻¹): `tNAssFiPlan = afNAssFiPlan * tNConsFiPlan`
- Code: `tNAssFiPlan = afNAssFiPlan * tNConsFiPlan`

### `tNAssFiTot` [-] *Assimilation*
- DESC: calculate total N assimilation rate
- Source: fish.F90 (826)
- Formula (d⁻¹): `tNAssFiTot = sum(tNAssFiPlan) + sum(tNAssFiBent) + sum(tNAssFiPisc)`
- Code: `tNAssFiTot = sum(tNAssFiPlan) + sum(tNAssFiBent) + sum(tNAssFiPisc)`

### `tNEgesFi` [-] *Assimilation*
- DESC: calculate N egestion rate
- Source: fish.F90 (848)
- Formula (d⁻¹): `tNEgesFi = tNConsFiTot - tNAssFiTot`
- Code: `tNEgesFi = tNConsFiTot - tNAssFiTot`

### `tPAssFiBent` [-] *Assimilation*
- DESC: calculate P assimilation rate from bentivory
- Source: fish.F90 (799)
- Formula (d⁻¹): `tPAssFiBent = afPAssFiBent * tPConsFiBent`
- Code: `tPAssFiBent = afPAssFiBent * tPConsFiBent`

### `tPAssFiPisc` [-] *Assimilation*
- DESC: calculate P assimilation rate from piscivory
- Source: fish.F90 (816)
- Formula (d⁻¹): `tPAssFiPisc = afPAssFiPisc * tPConsFiPisc`
- Code: `tPAssFiPisc = afPAssFiPisc * tPConsFiPisc`

### `tPAssFiPlan` [-] *Assimilation*
- DESC: calculate P assimilation rate from planktivy
- Source: fish.F90 (782)
- Formula (d⁻¹): `tPAssFiPlan = afPAssFiPlan * tPConsFiPlan`
- Code: `tPAssFiPlan = afPAssFiPlan * tPConsFiPlan`

### `tPAssFiTot` [-] *Assimilation*
- DESC: calculate total P assimilation rate
- Source: fish.F90 (825)
- Formula (d⁻¹): `tPAssFiTot = sum(tPAssFiPlan) + sum(tPAssFiBent) + sum(tPAssFiPisc)`
- Code: `tPAssFiTot = sum(tPAssFiPlan) + sum(tPAssFiBent) + sum(tPAssFiPisc)`

### `tPEgesFi` [-] *Assimilation*
- DESC: calculate P egestion rate
- Source: fish.F90 (847)
- Formula (d⁻¹): `tPEgesFi = tPConsFiTot - tPAssFiTot`
- Code: `tPEgesFi = tPConsFiTot - tPAssFiTot`

### `tDAssFiBen` [1/d] *Assimilation*
- DESC: bentivorous assimilation rate
- Source: fish_pclake.F90 (529)
- Formula (d⁻¹): `tDAssFiBen = aDSatFiBen *(kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishBen`
- Code: `tDAssFiBen = aDSatFiBen * (self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishBen`

### `tDAssFiPisc` [1/d] *Assimilation*
- DESC: piscivorous assimilation rate
- Source: fish_pclake.F90 (530)
- Formula (d⁻¹): `tDAssFiPisc = aDSatFiPisc *(kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishPisc`
- Code: `tDAssFiPisc = aDSatFiPisc * (self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishPisc`

### `tDAssFiZoo` [1/d] *Assimilation*
- DESC: zooplanktivorous assimilation rate
- Source: fish_pclake.F90 (528)
- Formula (d⁻¹): `tDAssFiZoo = aDSatFiZoo *(kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishZoo`
- Code: `tDAssFiZoo = aDSatFiZoo * (self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishZoo`

### `tDEnvFi` [1/d] *Assimilation*
- DESC: environmental correction (carrying capacity)
- Source: fish_pclake.F90 (527)
- Formula (d⁻¹): `tDEnvFi = max(0.0_rk,(ukDIncrFi / (cDCarrFish - sDFiOS)) * sDFi*sDFi)`
- Code: `tDEnvFi = max(0.0_rk, (ukDIncrFi / (self%cDCarrFish - sDFiOS)) * sDFi * sDFi)`

### `ukDIncrFi` [1/d] *Assimilation*
- DESC: maximum net population growth rate
- Source: fish_pclake.F90 (526)
- Formula (d⁻¹): `ukDIncrFi = (kDAssFi * aFunVegAss - kDRespFi) * uFunTmFish - kMortFi`
- Code: `ukDIncrFi = (self%kDAssFi * aFunVegAss - self%kDRespFi) * uFunTmFish - self%kMortFi`

### `afCAssBiv` [-] *Assimilation*
- DESC: C assimilation efficiency
- Source: bivalves.F90 (488)
- Formula (d⁻¹): `afCAssBiv = min(1.0_rk,self%cCDRef / max(NearZero,rCDFoodBiv) * self%fDAssBiv)`
- Code: `afCAssBiv = min(1.0_rk,self%cCDRef / max(NearZero,rCDFoodBiv) * self%fDAssBiv)`

### `afNAssBiv` [-] *Assimilation*
- DESC: N assimilation efficiency
- Source: bivalves.F90 (476)
- Formula (d⁻¹): `afNAssBiv = min(1.0_rk,self%cNDRef / max(NearZero,rNDFoodBiv) * self%fDAssBiv)`
- Code: `afNAssBiv = min(1.0_rk,self%cNDRef / max(NearZero,rNDFoodBiv) * self%fDAssBiv)`

### `afPAssBiv` [-] *Assimilation*
- DESC: P assimilation efficiency
- Source: bivalves.F90 (482)
- Formula (d⁻¹): `afPAssBiv = min(1.0_rk,self%cPDRef / max(NearZero,rPDFoodBiv) * self%fDAssBiv)`
- Code: `afPAssBiv = min(1.0_rk,self%cPDRef / max(NearZero,rPDFoodBiv) * self%fDAssBiv)`

### `rCDFoodBiv` [-] *Assimilation*
- DESC: total available prey C ratio
- Source: bivalves.F90 (487)
- Formula (d⁻¹): `rCDFoodBiv = tCConsBivTot / max(NearZero,tDConsBivTot)`
- Code: `rCDFoodBiv = tCConsBivTot / max(NearZero,tDConsBivTot)`

### `rNDFoodBiv` [-] *Assimilation*
- DESC: total available prey N ratio
- Source: bivalves.F90 (475)
- Formula (d⁻¹): `rNDFoodBiv = tNConsBivTot / max(NearZero,tDConsBivTot)`
- Code: `rNDFoodBiv = tNConsBivTot / max(NearZero,tDConsBivTot)`

### `rPDFoodBiv` [-] *Assimilation*
- DESC: total available prey P ratio
- Source: bivalves.F90 (481)
- Formula (d⁻¹): `rPDFoodBiv = tPConsBivTot / max(NearZero,tDConsBivTot)`
- Code: `rPDFoodBiv = tPConsBivTot / max(NearZero,tDConsBivTot)`

### `tCAssBiv` [g/m2/s] *Assimilation*
- DESC: C assimilation rate
- Source: bivalves.F90 (489)
- Formula (d⁻¹): `tCAssBiv = afCAssBiv * tCConsBivTot`
- Code: `tCAssBiv = afCAssBiv * tCConsBivTot`

### `tDAssBiv` [g/m2/s] *Assimilation*
- DESC: total DW assimilation
- Source: bivalves.F90 (471)
- Formula (d⁻¹): `tDAssBiv = self%fDAssBiv * tDConsBivTot`
- Code: `tDAssBiv = self%fDAssBiv * tDConsBivTot`

### `tNAssBiv` [g/m2/s] *Assimilation*
- DESC: N assimilation rate
- Source: bivalves.F90 (477)
- Formula (d⁻¹): `tNAssBiv = afNAssBiv * tNConsBivTot`
- Code: `tNAssBiv = afNAssBiv * tNConsBivTot`

### `tPAssBiv` [g/m2/s] *Assimilation*
- DESC: P assimilation rate
- Source: bivalves.F90 (483)
- Formula (d⁻¹): `tPAssBiv = afPAssBiv * tPConsBivTot`
- Code: `tPAssBiv = afPAssBiv * tPConsBivTot`

## Atmospheric deposition

### `sDIMW` [-] *Atmospheric deposition*
- DESC: surface exchange IM deposition
- Source: abiotic_water.F90 (343-343)
- Formula (d⁻¹): `tDDepoIM`
- Code: `_SET_SURFACE_EXCHANGE_(self%id_sDIMW, self%tDDepoIM)`

### `sNH4W` [-] *Atmospheric deposition*
- DESC: surface exchange NH4 deposition
- Source: abiotic_water.F90 (344-344)
- Formula (d⁻¹): `tNDepoNH4`
- Code: `_SET_SURFACE_EXCHANGE_(self%id_sNH4W, self%tNDepoNH4)`

### `sNO3W` [-] *Atmospheric deposition*
- DESC: surface exchange NO3 deposition
- Source: abiotic_water.F90 (345-345)
- Formula (d⁻¹): `tNDepoNO3`
- Code: `_SET_SURFACE_EXCHANGE_(self%id_sNO3W, self%tNDepoNO3)`

### `sPO4W` [-] *Atmospheric deposition*
- DESC: surface exchange PO4 deposition
- Source: abiotic_water.F90 (346-346)
- Formula (d⁻¹): `tPDepoPO4`
- Code: `_SET_SURFACE_EXCHANGE_(self%id_sPO4W, self%tPDepoPO4)`

## Auxiliary functions

### `fdens_bivalve` [-] *Auxiliary functions*
- DESC: bivalve density limitation: sDBiv<=cDmaxOpt (optimal)
- Source: bivalves.F90 (801-802)
- Formula (d⁻¹): `fdens_bivalve = 1.0`
- Code: `fdens_bivalve = 1.0`

### `fdens_bivalve` [-] *Auxiliary functions*
- DESC: bivalve density limitation: cDmaxOpt<sDBiv<cDmax (sub-optimal)
- Source: bivalves.F90 (803-805)
- Formula (d⁻¹): `fdens_bivalve = (-sDBiv**2 + 2*cDmaxOpt*sDBiv - 2*cDmaxOpt*cDmax + cDmax**2) / ((cDmaxOpt-cDmax)**2)`
- Code: `fdens_bivalve = (-sDBiv ** 2 + 2 * cDmaxOpt * sDBiv - 2 * cDmaxOpt * cDmax + cDmax ** 2) / ((cDmaxOpt - cDmax) ** 2)`

### `fdens_bivalve` [-] *Auxiliary functions*
- DESC: bivalve density limitation: sDBiv>=cDmax (no ingestion)
- Source: bivalves.F90 (806-808)
- Formula (d⁻¹): `fdens_bivalve = 0.0`
- Code: `fdens_bivalve = 0.0`

### `flength_weight_bivalve` [g DW] *Auxiliary functions*
- DESC: bivalve weight function: weight from length
- Source: bivalves.F90 (735-747)
- Formula (d⁻¹): `flength_weight_bivalve = exp((cAw*log(aL)-cBw))`
- Code: `bivalve_weight = exp((cAw*log(aL)-cBw)); flength_weight_bivalve = bivalve_weight`

### `fmortality_bivalve` [/sec] *Auxiliary functions*
- DESC: bivalve mortality function (oxygen-dependent)
- Source: bivalves.F90 (842)
- Formula (d⁻¹): `fmortality_bivalve = kmort * (1 + kbdo * (hKdo / (hKdo + O2)))`
- Code: `fmortality_bivalve = kmort * (1 + kbdo * (hKdo / (hKdo + O2)))`

### `fSS_bivalve` [-] *Auxiliary functions*
- DESC: bivalve SS limitation: sDIMW<=cSSIMmaxOpt (optimal)
- Source: bivalves.F90 (823-824)
- Formula (d⁻¹): `fSS_bivalve = 1.0`
- Code: `fSS_bivalve = 1.0`

### `fSS_bivalve` [-] *Auxiliary functions*
- DESC: bivalve SS limitation: cSSIMmaxOpt<sDIMW<cSSIMmax (sub-optimal)
- Source: bivalves.F90 (825-827)
- Formula (d⁻¹): `fSS_bivalve = (-sDIMW**2 + 2*cSSIMmaxOpt*sDIMW - 2*cSSIMmaxOpt*cSSIMmax + cSSIMmax**2) / ((cSSIMmaxOpt-cSSIMmax)**2)`
- Code: `fSS_bivalve = (-sDIMW ** 2 + 2 * cSSIMmaxOpt * sDIMW - 2 * cSSIMmaxOpt * cSSIMmax + cSSIMmax ** 2) / ((cSSIMmaxOpt - cSSIMmax) ** 2)`

### `fSS_bivalve` [-] *Auxiliary functions*
- DESC: bivalve SS limitation: sDIMW>=cSSIMmax (no ingestion)
- Source: bivalves.F90 (828-830)
- Formula (d⁻¹): `fSS_bivalve = 0.0`
- Code: `fSS_bivalve = 0.0`

### `ftemp_bivalve` [-] *Auxiliary functions*
- DESC: bivalve temperature limitation: uTm<=cTmin (filtration ceases)
- Source: bivalves.F90 (763-765)
- Formula (d⁻¹): `ftemp_bivalve = 0.0`
- Code: `ftemp_bivalve = 0.0`

### `ftemp_bivalve` [-] *Auxiliary functions*
- DESC: bivalve temperature limitation: cTmin<uTm<cTminOpt (sub-optimal low)
- Source: bivalves.F90 (767-771)
- Formula (d⁻¹): `ftemp_bivalve = a*(1.0/(-((cTminOpt-cTmin)*(cTminOpt-cTmin)/(cTminOpt*cTminOpt)) + (2.0*(cTminOpt-cTmin)/cTminOpt)))*(-((uTm-cTmin)*(uTm-cTmin)/(cTminOpt*cTminOpt)) + 2.0*((uTm-cTmin)/cTminOpt))`
- Code: `ftemp_bivalve = a*(1.0/(-((cTminOpt - cTmin) * (cTminOpt - cTmin)/ (cTminOpt * cTminOpt)) + (2.0*( cTminOpt - cTmin)/ cTminOpt)))*(-((uTm- cTmin)*(uTm - cTmin)/(cTminOpt * cTminOpt)) + 2.0*((uTm - cTmin)/cTminOpt))`

### `ftemp_bivalve` [-] *Auxiliary functions*
- DESC: bivalve temperature limitation: cTminOpt<=uTm<=cTmaxOpt (optimal range)
- Source: bivalves.F90 (774-775)
- Formula (d⁻¹): `ftemp_bivalve = a`
- Code: `ftemp_bivalve = a`

### `ftemp_bivalve` [-] *Auxiliary functions*
- DESC: bivalve temperature limitation: cTmaxOpt<uTm<cTmax (sub-optimal high)
- Source: bivalves.F90 (778-781)
- Formula (d⁻¹): `ftemp_bivalve = a*((-(uTm*uTm) + 2.0*(cTmaxOpt*uTm) - 2.0*(cTmaxOpt*cTmax) + (cTmax*cTmax))/((cTmaxOpt-cTmax)*(cTmaxOpt-cTmax)))`
- Code: `ftemp_bivalve = a*((-(uTm * uTm) + 2.0*(cTmaxOpt * uTm) - 2.0*(cTmaxOpt * cTmax) + ( cTmax * cTmax))/ ((cTmaxOpt - cTmax)*( cTmaxOpt - cTmax)))`

### `ftemp_bivalve` [-] *Auxiliary functions*
- DESC: bivalve temperature limitation: uTm>=cTmax (filtration ceases)
- Source: bivalves.F90 (784-785)
- Formula (d⁻¹): `ftemp_bivalve = 0.0`
- Code: `ftemp_bivalve = 0.0`

## Auxiliary variables

### `DayLength` [-] *Auxiliary variables*
- DESC: fraction of day with sun shine
- Source: utility.F90 (79-79)
- Formula (d⁻¹): `acos(1.0-m)/Pi`
- Code: `DayLength = acos(1._rk-m)/Pi`

### `m` [-] *Auxiliary variables*
- DESC: daylength intermediate variable
- Source: utility.F90 (78-78)
- Formula (d⁻¹): `1.0-tan(deg2rad*latitude)*tan(ecliptic*cos(0.0172*Day))`
- Code: `m = 1._rk-tan(deg2rad*latitude)*tan(ecliptic*cos(0.0172_rk*Day))`

### `bot_pel_conv` [-] *Auxiliary variables*
- DESC: conversion factor hypsograph case
- Source: abiotic_sediment.F90 (293-293)
- Formula (d⁻¹): `1.0/bot_pel_conv`
- Code: `bot_pel_conv = 1.0_rk/bot_pel_conv`

### `bot_pel_conv` [-] *Auxiliary variables*
- DESC: conversion factor non-hypsograph case
- Source: abiotic_sediment.F90 (296-296)
- Formula (d⁻¹): `1.0/bot_pel_conv`
- Code: `bot_pel_conv = 1.0_rk/bot_pel_conv`

### `oNO3S` [-] *Auxiliary variables*
- DESC: conc. of dissolved NO3 in interstitial water
- Source: abiotic_sediment.F90 (218-218)
- Formula (d⁻¹): `max(0.0, sNO3S / cDepthS / bPorS)`
- Code: `oNO3S = max(0.0_rk, sNO3S / self%cDepthS / self%bPorS)`

### `oPO4S` [-] *Auxiliary variables*
- DESC: conc. of dissolved PO4 in interstitial water
- Source: abiotic_sediment.F90 (220-220)
- Formula (d⁻¹): `max(0.0, sPO4S / cDepthS / bPorS)`
- Code: `oPO4S = max(0.0_rk, sPO4S / self%cDepthS / self%bPorS)`

### `ext` [-] *Auxiliary variables*
- DESC: extinction coefficient
- Source: om_pool.F90 (561)
- Formula (d⁻¹): `ext=self%cExtSp*sDW`
- Code: `ext=self%cExtSp*sDW`

### `rCDS` [-] *Auxiliary variables*
- DESC: C/D ratio sediment
- Source: om_pool.F90 (416)
- Formula (d⁻¹): `rCDS = sCS /(sDS+NearZero)`
- Code: `rCDS = sCS /(sDS+NearZero)`

### `rCDW` [-] *Auxiliary variables*
- DESC: C/D ratio water
- Source: om_pool.F90 (296)
- Formula (d⁻¹): `rCDW = sCW /(sDW+NearZero)`
- Code: `rCDW = sCW /(sDW+NearZero)`

### `rNDS` [-] *Auxiliary variables*
- DESC: N/D ratio sediment
- Source: om_pool.F90 (415)
- Formula (d⁻¹): `rNDS = sNS /(sDS+NearZero)`
- Code: `rNDS = sNS /(sDS+NearZero)`

### `rNDW` [-] *Auxiliary variables*
- DESC: N/D ratio water
- Source: om_pool.F90 (295)
- Formula (d⁻¹): `rNDW = sNW /(sDW+NearZero)`
- Code: `rNDW = sNW /(sDW+NearZero)`

### `rPDS` [-] *Auxiliary variables*
- DESC: P/D ratio sediment
- Source: om_pool.F90 (414)
- Formula (d⁻¹): `rPDS = sPS /(sDS+NearZero)`
- Code: `rPDS = sPS /(sDS+NearZero)`

### `rPDW` [-] *Auxiliary variables*
- DESC: P/D ratio water
- Source: om_pool.F90 (294)
- Formula (d⁻¹): `rPDW = sPW /(sDW+NearZero)`
- Code: `rPDW = sPW /(sDW+NearZero)`

### `rCDFoodZoo` [gC/gDW] *Auxiliary variables*
- DESC: calculate total available prey carbon ratio
- Source: zooplankton.F90 (322)
- Formula (d⁻¹): `wCConsZooTot / wDConsZooTot`
- Code: `rCDFoodZoo = wCConsZooTot / wDConsZooTot`

### `rCDprey` [gC/gDW] *Auxiliary variables*
- DESC: calculate prey C:DW ratios (dimensions: nPrey)
- Source: zooplankton.F90 (274)
- Formula (d⁻¹): `sCprey/(sDprey+NearZero)`
- Code: `rCDprey = sCprey/(sDprey+NearZero)`

### `rCDZoo` [gC/gDW] *Auxiliary variables*
- DESC: calculate C:DW ratio
- Source: zooplankton.F90 (257)
- Formula (d⁻¹): `sCZoo/(sDZoo+NearZero)`
- Code: `rCDZoo = sCZoo/(sDZoo+NearZero)`

### `rNDFoodZoo` [gN/gDW] *Auxiliary variables*
- DESC: calculate total available prey nitrogen ratio
- Source: zooplankton.F90 (310)
- Formula (d⁻¹): `wNConsZooTot / wDConsZooTot`
- Code: `rNDFoodZoo = wNConsZooTot / wDConsZooTot`

### `rNDprey` [gN/gDW] *Auxiliary variables*
- DESC: calculate prey N:DW ratios (dimensions: nPrey)
- Source: zooplankton.F90 (272)
- Formula (d⁻¹): `sNprey/(sDprey+NearZero)`
- Code: `rNDprey = sNprey/(sDprey+NearZero)`

### `rNDZoo` [gN/gDW] *Auxiliary variables*
- DESC: calculate N:DW ratio
- Source: zooplankton.F90 (256)
- Formula (d⁻¹): `sNZoo/(sDZoo+NearZero)`
- Code: `rNDZoo = sNZoo/(sDZoo+NearZero)`

### `rPDFoodZoo` [gP/gDW] *Auxiliary variables*
- DESC: calculate total available prey phosphorus ratio
- Source: zooplankton.F90 (316)
- Formula (d⁻¹): `wPConsZooTot / wDConsZooTot`
- Code: `rPDFoodZoo = wPConsZooTot / wDConsZooTot`

### `rPDprey` [gP/gDW] *Auxiliary variables*
- DESC: calculate prey P:DW ratios (dimensions: nPrey)
- Source: zooplankton.F90 (273)
- Formula (d⁻¹): `sPprey/(sDprey+NearZero)`
- Code: `rPDprey = sPprey/(sDprey+NearZero)`

### `rPDZoo` [gP/gDW] *Auxiliary variables*
- DESC: calculate P:DW ratio
- Source: zooplankton.F90 (255)
- Formula (d⁻¹): `sPZoo/(sDZoo+NearZero)`
- Code: `rPDZoo = sPZoo/(sDZoo+NearZero)`

### `rSiDprey` [gSi/gDW] *Auxiliary variables*
- DESC: calculate prey Si:DW ratios (dimensions: nPrey)
- Source: zooplankton.F90 (275)
- Formula (d⁻¹): `sSiPrey/(sDprey+NearZero)`
- Code: `rSiDprey = sSiPrey/(sDprey+NearZero)`

### `tDEnvZoo` [gDW/m3/s] *Auxiliary variables*
- DESC: calculate environmental correction
- Source: zooplankton.F90 (292-293)
- Formula (d⁻¹): `max(0.0_rk,(((kDConsMaxZoo*fDAssZoo-kDRespZoo)*uFunTmZoo-kMortZoo) / cDCarrZoo) * sDZoo*sDZoo)`
- Code: `tDEnvZoo = max(0.0_rk,(((self%kDConsMaxZoo*self%fDAssZoo-self%kDRespZoo)*uFunTmZoo-self%kMortZoo) / self%cDCarrZoo) * sDZoo*sDZoo)`

### `cDCarrBentVeg` [gDW/m2] *Auxiliary variables*
- DESC: carrying capacity scaled by macrophyte biomass
- Source: zoobenthos.F90 (325)
- Formula (d⁻¹): `cDVegCarr * aDSubVeg`
- Code: `cDCarrBentVeg = self%cDVegCarr * aDSubVeg`

### `rCDBent` [gC/gDW] *Auxiliary variables*
- DESC: calculate C:DW ratio
- Source: zoobenthos.F90 (291)
- Formula (d⁻¹): `sCBent/(sDBent+NearZero)`
- Code: `rCDBent=sCBent/(sDBent+NearZero)`

### `rCDFoodBent` [gC/gDW] *Auxiliary variables*
- DESC: calculate total available prey C ratio
- Source: zoobenthos.F90 (356)
- Formula (d⁻¹): `tCConsBentTot / max(NearZero,tDConsBentTot)`
- Code: `rCDFoodBent = tCConsBentTot / max(NearZero,tDConsBentTot)`

### `rCDprey` [gC/gDW] *Auxiliary variables*
- DESC: calculate prey C:DW ratios (dimensions: nPrey)
- Source: zoobenthos.F90 (308)
- Formula (d⁻¹): `sCprey/(sDprey+NearZero)`
- Code: `rCDprey = sCprey/(sDprey+NearZero)`

### `rNDBent` [gN/gDW] *Auxiliary variables*
- DESC: calculate N:DW ratio
- Source: zoobenthos.F90 (290)
- Formula (d⁻¹): `sNBent/(sDBent+NearZero)`
- Code: `rNDBent=sNBent/(sDBent+NearZero)`

### `rNDFoodBent` [gN/gDW] *Auxiliary variables*
- DESC: calculate total available prey N ratio
- Source: zoobenthos.F90 (344)
- Formula (d⁻¹): `tNConsBentTot / max(NearZero,tDConsBentTot)`
- Code: `rNDFoodBent = tNConsBentTot / max(NearZero,tDConsBentTot)`

### `rNDprey` [gN/gDW] *Auxiliary variables*
- DESC: calculate prey N:DW ratios (dimensions: nPrey)
- Source: zoobenthos.F90 (306)
- Formula (d⁻¹): `sNprey/(sDprey+NearZero)`
- Code: `rNDprey = sNprey/(sDprey+NearZero)`

### `rPDBent` [gP/gDW] *Auxiliary variables*
- DESC: calculate P:DW ratio
- Source: zoobenthos.F90 (289)
- Formula (d⁻¹): `sPBent/(sDBent+NearZero)`
- Code: `rPDBent=sPBent/(sDBent+NearZero)`

### `rPDFoodBent` [gP/gDW] *Auxiliary variables*
- DESC: calculate total available prey P ratio
- Source: zoobenthos.F90 (350)
- Formula (d⁻¹): `tPConsBentTot / max(NearZero,tDConsBentTot)`
- Code: `rPDFoodBent = tPConsBentTot / max(NearZero,tDConsBentTot)`

### `rPDprey` [gP/gDW] *Auxiliary variables*
- DESC: calculate prey P:DW ratios (dimensions: nPrey)
- Source: zoobenthos.F90 (307)
- Formula (d⁻¹): `sPprey/(sDprey+NearZero)`
- Code: `rPDprey = sPprey/(sDprey+NearZero)`

### `tDEnvBent` [gDW/m2/s] *Auxiliary variables*
- DESC: calculate environmental correction
- Source: zoobenthos.F90 (326-327)
- Formula (d⁻¹): `max(0.0_rk,(((kDConsMaxBent*fDAssBent-kDRespBent)*uFunTmBent*fO2-kMortBent) / (cDCarrBent + cDCarrBentVeg)) * sDBent*sDBent)`
- Code: `tDEnvBent = max(0.0_rk,(((self%kDConsMaxBent*self%fDAssBent-self%kDRespBent)*uFunTmBent*fO2-self%kMortBent) / (self%cDCarrBent + cDCarrBentVeg)) * sDBent*sDBent)`

### `afCovEmergVeg` [-] *Auxiliary variables*
- DESC: fraction emergent coverage
- Source: macrophytes.F90 (413)
- Formula (d⁻¹): `min(1.0, 0.01 * cCovSpVeg * aDEmergVeg)`
- Code: `afCovEmergVeg = min(1.0_rk, 0.01_rk * self%cCovSpVeg * aDEmergVeg)`

### `oNDissS` [gN/m3] *Auxiliary variables*
- DESC: total dissolved N in pore water (conc.)
- Source: macrophytes.F90 (384)
- Formula (d⁻¹): `(sNO3S + sNH4S)/cDepthS/bPorS`
- Code: `oNDissS = (sNO3S + sNH4S)/cDepthS / bPorS`

### `oNDissW` [gN/m3] *Auxiliary variables*
- DESC: total dissolved N in water
- Source: macrophytes.F90 (383)
- Formula (d⁻¹): `sNO3W + sNH4W`
- Code: `oNDissW = sNO3W + sNH4W`

### `oNH4S` [gN/m3] *Auxiliary variables*
- DESC: NH4 conc. in pore water
- Source: macrophytes.F90 (385)
- Formula (d⁻¹): `sNH4S/cDepthS/bPorS`
- Code: `oNH4S = sNH4S/cDepthS / bPorS`

### `oNO3S` [gN/m3] *Auxiliary variables*
- DESC: NO3 conc. in pore water
- Source: macrophytes.F90 (386)
- Formula (d⁻¹): `sNO3S/cDepthS/bPorS`
- Code: `oNO3S = sNO3S/cDepthS / bPorS`

### `oPO4S` [gP/m3] *Auxiliary variables*
- DESC: PO4 conc. in pore water
- Source: macrophytes.F90 (387)
- Formula (d⁻¹): `sPO4S/cDepthS/bPorS`
- Code: `oPO4S = sPO4S/cDepthS / bPorS`

### `rCDVeg` [gC/gDW] *Auxiliary variables*
- DESC: macrophyte C/DW ratio
- Source: macrophytes.F90 (371)
- Formula (d⁻¹): `sCVeg/(sDVeg+NearZero)`
- Code: `rCDVeg = sCVeg/(sDVeg+NearZero)`

### `rNDVeg` [gN/gDW] *Auxiliary variables*
- DESC: macrophyte N/DW ratio
- Source: macrophytes.F90 (370)
- Formula (d⁻¹): `sNVeg/(sDVeg+NearZero)`
- Code: `rNDVeg = sNVeg/(sDVeg+NearZero)`

### `rPDVeg` [gP/gDW] *Auxiliary variables*
- DESC: macrophyte P/DW ratio
- Source: macrophytes.F90 (369)
- Formula (d⁻¹): `sPVeg/(sDVeg+NearZero)`
- Code: `rPDVeg = sPVeg/(sDVeg+NearZero)`

### `sDCompts` [gDW/m2] *Auxiliary variables*
- DESC: sum of competitor macrophyte DW (loop nCompts)
- Source: macrophytes.F90 (357)
- Formula (d⁻¹): `sum(sDCompts_all)`
- Code: `sDCompts = sum(sDCompts_all)`

### `aFunVegAss` [-] *Auxiliary variables*
- DESC: calculate macrophyte-dependence of growth
- Source: fish.F90 (621)
- Formula (d⁻¹): `aFunVegAss = aDSubVeg /(self%hDVegGrowth + aDSubVeg + NearZero)`
- Code: `aFunVegAss = aDSubVeg /(self%hDVegGrowth + aDSubVeg + NearZero)`

### `aFunVegBent` [-] *Auxiliary variables*
- DESC: calculate dependence of bentivory on macrophytes
- Source: fish.F90 (618)
- Formula (d⁻¹): `aFunVegBent = max(0.0_rk,1.0_rk - self%cRelVegBent * aCovVeg)`
- Code: `aFunVegBent = max(0.0_rk,1.0_rk - self%cRelVegBent * aCovVeg)`

### `aFunVegPlan` [-] *Auxiliary variables*
- DESC: calcuate dependence of planktivory on macrophytes
- Source: fish.F90 (619)
- Formula (d⁻¹): `aFunVegPlan = max(0.0_rk,1.0_rk - self%cRelVegPlan * aCovVeg)`
- Code: `aFunVegPlan = max(0.0_rk,1.0_rk - self%cRelVegPlan * aCovVeg)`

### `BioTurb` [gDW/m3/d] *Auxiliary variables*
- DESC: current bioturbation by fish (zero without benthivory)
- Source: fish.F90 (734)
- Formula (d⁻¹): `BioTurb = fFishBent * fFeed*sDfiEff * uFunTmFish * self%kTurbFish`
- Code: `BioTurb = fFishBent * fFeed*sDfiEff * uFunTmFish * self%kTurbFish`

### `lCon` [-] *Auxiliary variables*
- DESC: check state of reserves
- Source: fish.F90 (533)
- Formula (d⁻¹): `lCon = sFRes > self%fResMin*1.75_rk`
- Code: `lCon = sFRes > self%fResMin*1.75_rk`

### `NetGrowthFA` [-] *Auxiliary variables*
- DESC: calculate net energy gain from constant feeding
- Source: fish.F90 (673)
- Formula (d⁻¹): `NetGrowthFA = tDAssFiTotPot - (1.0_rk+self%fDRespActFi)*self%kDRespFi*uFunTmFish`
- Code: `NetGrowthFA = tDAssFiTotPot - (1.0_rk+self%fDRespActFi)*self%kDRespFi*uFunTmFish`

### `relConsBent` [-] *Auxiliary variables*
- DESC: weighted average consumption (relative contributions)
- Source: fish.F90 (656)
- Formula (d⁻¹): `relConsBent = tDConsFiBentPot/sum(tDConsFiBentPot)`
- Code: `relConsBent = tDConsFiBentPot/sum(tDConsFiBentPot)`

### `relConsPisc` [-] *Auxiliary variables*
- DESC: weighted average consumption (relative contributions)
- Source: fish.F90 (657)
- Formula (d⁻¹): `relConsPisc = tDConsFiPiscPot/sum(tDConsFiPiscPot)`
- Code: `relConsPisc = tDConsFiPiscPot/sum(tDConsFiPiscPot)`

### `relConsPlan` [-] *Auxiliary variables*
- DESC: weighted average consumption (relative contributions)
- Source: fish.F90 (655)
- Formula (d⁻¹): `relConsPlan = tDConsFiPlanPot/sum(tDConsFiPlanPot)`
- Code: `relConsPlan = tDConsFiPlanPot/sum(tDConsFiPlanPot)`

### `rCDDOMS` [-] *Auxiliary variables*
- DESC: DOMS C:DW ratios (dim nDOM)
- Source: sediment_exchange.F90 (378)
- Formula (d⁻¹): `rCDDOMS = sCDOMS/(sDDOMS+NearZero)`
- Code: `rCDDOMS = sCDOMS/(sDDOMS+NearZero)`

### `rCDPOMS` [-] *Auxiliary variables*
- DESC: POMS C:DW ratios (dim nPOM)
- Source: sediment_exchange.F90 (355)
- Formula (d⁻¹): `rCDPOMS = sCPOMS/(sDPOMS+NearZero)`
- Code: `rCDPOMS = sCPOMS/(sDPOMS+NearZero)`

### `rNDDOMS` [-] *Auxiliary variables*
- DESC: DOMS N:DW ratios (dim nDOM)
- Source: sediment_exchange.F90 (376)
- Formula (d⁻¹): `rNDDOMS = sNDOMS/(sDDOMS+NearZero)`
- Code: `rNDDOMS = sNDOMS/(sDDOMS+NearZero)`

### `rNDPOMS` [-] *Auxiliary variables*
- DESC: POMS N:DW ratios (dim nPOM)
- Source: sediment_exchange.F90 (353)
- Formula (d⁻¹): `rNDPOMS = sNPOMS/(sDPOMS+NearZero)`
- Code: `rNDPOMS = sNPOMS/(sDPOMS+NearZero)`

### `rPDDOMS` [-] *Auxiliary variables*
- DESC: DOMS P:DW ratios (dim nDOM)
- Source: sediment_exchange.F90 (377)
- Formula (d⁻¹): `rPDDOMS = sPDOMS/(sDDOMS+NearZero)`
- Code: `rPDDOMS = sPDOMS/(sDDOMS+NearZero)`

### `rPDPOMS` [-] *Auxiliary variables*
- DESC: POMS P:DW ratios (dim nPOM)
- Source: sediment_exchange.F90 (354)
- Formula (d⁻¹): `rPDPOMS = sPPOMS/(sDPOMS+NearZero)`
- Code: `rPDPOMS = sPPOMS/(sDPOMS+NearZero)`

### `rSiDPOMS` [-] *Auxiliary variables*
- DESC: Si to total POM DW ratio
- Source: sediment_exchange.F90 (360)
- Formula (d⁻¹): `rSiDPOMS=sSiPaS/(sum(sDPOMS)+NearZero)`
- Code: `rSiDPOMS=sSiPaS/(sum(sDPOMS)+NearZero)`

### `rNDPOMS` [-] *Auxiliary variables*
- DESC: POMS N:DW ratio
- Source: resus_sed.F90 (176)
- Formula (d⁻¹): `rNDPOMS=sNPOMS/(sDPOMS+NearZero)`
- Code: `rNDPOMS=sNPOMS/(sDPOMS+NearZero)`

### `rPDPOMS` [-] *Auxiliary variables*
- DESC: POMS P:DW ratio
- Source: resus_sed.F90 (175)
- Formula (d⁻¹): `rPDPOMS=sPPOMS/(sDPOMS+NearZero)`
- Code: `rPDPOMS=sPPOMS/(sDPOMS+NearZero)`

### `rSiDPOMS` [-] *Auxiliary variables*
- DESC: Si to POM DW ratio
- Source: resus_sed.F90 (177)
- Formula (d⁻¹): `rSiDPOMS=sSiPaS/(sDPOMS+NearZero)`
- Code: `rSiDPOMS=sSiPaS/(sDPOMS+NearZero)`

### `rCDPOMS` [-] *Auxiliary variables*
- DESC: POMS C:DW ratios (dim nPOM)
- Source: burial.F90 (302)
- Formula (d⁻¹): `rCDPOMS=sCPOMS/(sDPOMS+NearZero)`
- Code: `rCDPOMS=sCPOMS/(sDPOMS+NearZero)`

### `rNDPOMS` [-] *Auxiliary variables*
- DESC: POMS N:DW ratios (dim nPOM)
- Source: burial.F90 (301)
- Formula (d⁻¹): `rNDPOMS=sNPOMS/(sDPOMS+NearZero)`
- Code: `rNDPOMS=sNPOMS/(sDPOMS+NearZero)`

### `rPDPOMS` [-] *Auxiliary variables*
- DESC: POMS P:DW ratios (dim nPOM)
- Source: burial.F90 (300)
- Formula (d⁻¹): `rPDPOMS=sPPOMS/(sDPOMS+NearZero)`
- Code: `rPDPOMS=sPPOMS/(sDPOMS+NearZero)`

### `rSiDPOMS` [-] *Auxiliary variables*
- DESC: Si to total POM DW ratio
- Source: burial.F90 (303)
- Formula (d⁻¹): `rSiDPOMS=sSiPaS/(sDPOMSTot+NearZero)`
- Code: `rSiDPOMS=sSiPaS/(sDPOMSTot+NearZero)`

### `sDPOMSTot` [g/m2] *Auxiliary variables*
- DESC: total DW POM in sediment
- Source: burial.F90 (299)
- Formula (d⁻¹): `sDPOMSTot = sum(sDPOMS)`
- Code: `sDPOMSTot = sum(sDPOMS)`

### `rCDBiv` [-] *Auxiliary variables*
- DESC: bivalve C:DW ratio
- Source: bivalves.F90 (369)
- Formula (d⁻¹): `rCDBiv=sCBiv/(sDBiv+NearZero)`
- Code: `rCDBiv=sCBiv/(sDBiv+NearZero)`

### `rCDprey` [-] *Auxiliary variables*
- DESC: prey C:DW ratios (dim nPrey)
- Source: bivalves.F90 (389)
- Formula (d⁻¹): `rCDprey = sCprey/(sDprey+NearZero)`
- Code: `rCDprey = sCprey/(sDprey+NearZero)`

### `rNDBiv` [-] *Auxiliary variables*
- DESC: bivalve N:DW ratio
- Source: bivalves.F90 (367)
- Formula (d⁻¹): `rNDBiv=sNBiv/(sDBiv+NearZero)`
- Code: `rNDBiv=sNBiv/(sDBiv+NearZero)`

### `rNDprey` [-] *Auxiliary variables*
- DESC: prey N:DW ratios (dim nPrey)
- Source: bivalves.F90 (387)
- Formula (d⁻¹): `rNDprey = sNprey/(sDprey+NearZero)`
- Code: `rNDprey = sNprey/(sDprey+NearZero)`

### `rPDBiv` [-] *Auxiliary variables*
- DESC: bivalve P:DW ratio
- Source: bivalves.F90 (368)
- Formula (d⁻¹): `rPDBiv=sPBiv/(sDBiv+NearZero)`
- Code: `rPDBiv=sPBiv/(sDBiv+NearZero)`

### `rPDprey` [-] *Auxiliary variables*
- DESC: prey P:DW ratios (dim nPrey)
- Source: bivalves.F90 (388)
- Formula (d⁻¹): `rPDprey = sPprey/(sDprey+NearZero)`
- Code: `rPDprey = sPprey/(sDprey+NearZero)`

### `sDBivOS` [g/m2] *Auxiliary variables*
- DESC: total biomass of all stages (juv+adult+other) initialized to 0
- Source: bivalves.F90 (395)
- Formula (d⁻¹): `sDBivOS = 0.0_rk`
- Code: `sDBivOS = 0.0_rk`

### `sDBivOS` [g/m2] *Auxiliary variables*
- DESC: case qStageOpt=1 or 3: add juvenile stage biomass
- Source: bivalves.F90 (398)
- Formula (d⁻¹): `sDBivOS = sDBivOS + sDJu`
- Code: `sDBivOS = sDBivOS + sDJu`

### `sDBivOS` [g/m2] *Auxiliary variables*
- DESC: case qStageOpt=2 or 3: add adult stage biomass
- Source: bivalves.F90 (402)
- Formula (d⁻¹): `sDBivOS = sDBivOS + sDAd`
- Code: `sDBivOS = sDBivOS + sDAd`

### `sDBivOS` [g/m2] *Auxiliary variables*
- DESC: case nKShares>0: add other stage biomasses
- Source: bivalves.F90 (409)
- Formula (d⁻¹): `sDBivOS = sDBivOS + sDBivSt`
- Code: `sDBivOS = sDBivOS + sDBivSt`

### `sDBivSt` [g/m2] *Auxiliary variables*
- DESC: sum of other not-coupled stage biomasses
- Source: bivalves.F90 (408)
- Formula (d⁻¹): `sDBivSt = sum(sDBivSt_all)`
- Code: `sDBivSt = sum(sDBivSt_all)`

### `total_food_DW` [-] *Auxiliary variables*
- DESC: total food dry weight (sum over prey with preference)
- Source: bivalves.F90 (385)
- Formula (d⁻¹): `total_food_DW = total_food_DW + sDprey(i_prey)*self%pref(i_prey)`
- Code: `total_food_DW = total_food_DW + sDprey(i_prey)*self%pref(i_prey)`

### `total_food_DW` [-] *Auxiliary variables*
- DESC: total food dry weight floored at NearZero
- Source: bivalves.F90 (390)
- Formula (d⁻¹): `total_food_DW = max(NearZero,total_food_DW)`
- Code: `total_food_DW = max(NearZero,total_food_DW)`

### `weight` [g DW] *Auxiliary variables*
- DESC: individual bivalve dry weight from length
- Source: bivalves.F90 (416)
- Formula (d⁻¹): `weight = flength_weight_bivalve(self%aL,self%cAw,self%cBw)`
- Code: `weight = flength_weight_bivalve(self%aL,self%cAw,self%cBw)`

## Biomass fractions

### `aCovVeg` [%] *Biomass fractions*
- DESC: percent cover
- Source: macrophytes.F90 (964)
- Formula (d⁻¹): `min(100.0, cCovSpVeg * aDShootVeg_int)`
- Code: `aCovVeg = min(100.0_rk, self%cCovSpVeg * aDShootVeg_int)`

### `aDEmergVeg` [gDW/m2] *Biomass fractions*
- DESC: emergent biomass
- Source: macrophytes.F90 (960)
- Formula (d⁻¹): `fEmergVeg * aDShootVeg_int`
- Code: `aDEmergVeg_int = self%fEmergVeg * aDShootVeg_int`

### `aDFloatVeg` [gDW/m2] *Biomass fractions*
- DESC: floating biomass
- Source: macrophytes.F90 (961)
- Formula (d⁻¹): `fFloatVeg * aDShootVeg_int`
- Code: `aDFloatVeg_int = self%fFloatVeg * aDShootVeg_int`

### `aDRootVeg` [gDW/m2] *Biomass fractions*
- DESC: root biomass
- Source: macrophytes.F90 (958)
- Formula (d⁻¹): `bfRootVeg_int * sDVeg`
- Code: `aDRootVeg_int = bfRootVeg_int * sDVeg`

### `aDShootVeg` [gDW/m2] *Biomass fractions*
- DESC: shoot biomass
- Source: macrophytes.F90 (959)
- Formula (d⁻¹): `bfShootVeg_int * sDVeg`
- Code: `aDShootVeg_int = bfShootVeg_int * sDVeg`

### `aDSubVeg` [gDW/m2] *Biomass fractions*
- DESC: submerged biomass
- Source: macrophytes.F90 (963)
- Formula (d⁻¹): `bfSubVeg_int * aDShootVeg_int`
- Code: `aDSubVeg = bfSubVeg_int * aDShootVeg_int`

### `afCovSurfVeg` [-] *Biomass fractions*
- DESC: fraction of water surface covered by plant species
- Source: macrophytes.F90 (965)
- Formula (d⁻¹): `min(1.0, max(aDFloatVeg_int/(cDLayerVeg+NearZero), aDEmergVeg_int/(fEmergVeg*cDCarrVeg+NearZero)))`
- Code: `afCovSurfVeg = min(1.0_rk, max(aDFloatVeg_int/(self%cDLayerVeg + NearZero), aDEmergVeg_int/(self%fEmergVeg * self%cDCarrVeg + NearZero)))`

### `bfShootVeg` [-] *Biomass fractions*
- DESC: shoot fraction (1 - root fraction)
- Source: macrophytes.F90 (957)
- Formula (d⁻¹): `1.0 - bfRootVeg_int`
- Code: `bfShootVeg_int = 1.0_rk - bfRootVeg_int`

### `bfSubVeg` [-] *Biomass fractions*
- DESC: submerged fraction of shoot (1 - fFloatVeg - fEmergVeg)
- Source: macrophytes.F90 (962)
- Formula (d⁻¹): `1.0 - fFloatVeg - fEmergVeg`
- Code: `bfSubVeg_int = 1.0_rk - self%fFloatVeg - self%fEmergVeg`

### `calc_veg_fractions` [-] *Biomass fractions*
- DESC: calc. biomass fractions in shoots/roots (shared with do)
- Source: macrophytes.F90 (408)
- Formula (d⁻¹): `calc_veg_fractions(Day, sDVeg, uTm, lat, aDSubVeg, aCovVeg, afCovSurfVeg, aDayInitVeg, aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg)`
- Code: `call self%calc_veg_fractions(Day, sDVeg, uTm, lat, aDSubVeg, aCovVeg, afCovSurfVeg, aDayInitVeg, aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg)`

## Bone settling

### `tCMortFiBot` [-] *Bone settling*
- DESC: calculate C flux out of the system (into the sediment) from mortality
- Source: fish.F90 (960)
- Formula (d⁻¹): `tCMortFiBot = self%fDBone * (tCMortFi)`
- Code: `tCMortFiBot = self%fDBone * (tCMortFi)`

### `tCMortFiTOM` [-] *Bone settling*
- DESC: calculate part of dead fish C staying in the system [BUG] tCMortFiTOM should use tCMortFi not tDMortFi; code uses (tDMortFi) - tDMortFiBot
- Source: fish.F90 (961)
- Formula (d⁻¹): `tCMortFiTOM = (tCMortFi) - tCMortFiBot`
- Code: `tCMortFiTOM = (tDMortFi) - tDMortFiBot`

### `tDMortFiBot` [-] *Bone settling*
- DESC: calculate flux out of the system (into the sediment) from mortality
- Source: fish.F90 (927)
- Formula (d⁻¹): `tDMortFiBot = self%fDBone * (tDMortFi)`
- Code: `tDMortFiBot = self%fDBone * (tDMortFi)`

### `tDMortFiTOM` [-] *Bone settling*
- DESC: calculate part of dead fish staying in the system
- Source: fish.F90 (928)
- Formula (d⁻¹): `tDMortFiTOM = (tDMortFi) - tDMortFiBot`
- Code: `tDMortFiTOM = (tDMortFi) - tDMortFiBot`

### `tNMortFiBot` [-] *Bone settling*
- DESC: calculate flux of N out of the system (into the sediment) from mortality
- Source: fish.F90 (936)
- Formula (d⁻¹): `tNMortFiBot = self%fDBone * tNMortFi`
- Code: `tNMortFiBot = self%fDBone * tNMortFi`

### `tPMortFiBot` [-] *Bone settling*
- DESC: calculate flux of P out of the system (into the sediment) from mortality
- Source: fish.F90 (948)
- Formula (d⁻¹): `tPMortFiBot = self%fPBone * tPMortFi`
- Code: `tPMortFiBot = self%fPBone * tPMortFi`

## Bottom exchange

### `O2ConsSed` [-] *Bottom exchange*
- DESC: bottom exchange O2 consumption
- Source: abiotic_sediment.F90 (314-314)
- Formula (d⁻¹): `- tO2MinTOMS - tO2NitrS`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_O2ConsSed, - tO2MinTOMS - tO2NitrS)`

### `CRefrS_PV` [-] *Bottom exchange*
- DESC: ODE for C refractory target pelagic mirror
- Source: om_pool.F90 (505)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CRefrS_PV, tCRefr*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CRefrS_PV, tCRefr*bot_pel_conv)`

### `CTransS_PV` [-] *Bottom exchange*
- DESC: ODE for C bio-transf. target pelagic mirror
- Source: om_pool.F90 (494)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CTransS_PV, tCTrans*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CTransS_PV,    tCTrans*bot_pel_conv)`

### `DRefrS_PV` [-] *Bottom exchange*
- DESC: ODE for DW refractory target pelagic mirror
- Source: om_pool.F90 (502)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DRefrS_PV, tDRefr*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DRefrS_PV, tDRefr*bot_pel_conv)`

### `DTransS_PV` [-] *Bottom exchange*
- DESC: ODE for DW bio-transf. target pelagic mirror
- Source: om_pool.F90 (491)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DTransS_PV, tDTrans*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DTransS_PV,    tDTrans*bot_pel_conv)`

### `NRefrS_PV` [-] *Bottom exchange*
- DESC: ODE for N refractory target pelagic mirror
- Source: om_pool.F90 (503)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NRefrS_PV, tNRefr*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NRefrS_PV, tNRefr*bot_pel_conv)`

### `NTransS_PV` [-] *Bottom exchange*
- DESC: ODE for N bio-transf. target pelagic mirror
- Source: om_pool.F90 (492)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NTransS_PV, tNTrans*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NTransS_PV,    tNTrans*bot_pel_conv)`

### `PRefrS_PV` [-] *Bottom exchange*
- DESC: ODE for P refractory target pelagic mirror
- Source: om_pool.F90 (504)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PRefrS_PV, tPRefr*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PRefrS_PV, tPRefr*bot_pel_conv)`

### `PTransS_PV` [-] *Bottom exchange*
- DESC: ODE for P bio-transf. target pelagic mirror
- Source: om_pool.F90 (493)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PTransS_PV, tPTrans*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PTransS_PV,    tPTrans*bot_pel_conv)`

### `sCS_PV` [-] *Bottom exchange*
- DESC: projected sediment OM C ODE
- Source: om_pool.F90 (480)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)`

### `sDS_PV` [-] *Bottom exchange*
- DESC: projected sediment OM DW ODE
- Source: om_pool.F90 (477)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)`

### `sNS_PV` [-] *Bottom exchange*
- DESC: projected sediment OM N ODE
- Source: om_pool.F90 (478)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)`

### `sPS_PV` [-] *Bottom exchange*
- DESC: projected sediment OM P ODE
- Source: om_pool.F90 (479)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)`

### `PreyC_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (473)
- Formula (d⁻¹): `-tCConsBent(i_prey)*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PreyC_PV(i_prey),-tCConsBent(i_prey)*bot_pel_conv)`

### `PreyD_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (470)
- Formula (d⁻¹): `-tDConsBent(i_prey)*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PreyD_PV(i_prey),-tDConsBent(i_prey)*bot_pel_conv)`

### `PreyN_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (471)
- Formula (d⁻¹): `-tNConsBent(i_prey)*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PreyN_PV(i_prey),-tNConsBent(i_prey)*bot_pel_conv)`

### `PreyP_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (472)
- Formula (d⁻¹): `-tPConsBent(i_prey)*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PreyP_PV(i_prey),-tPConsBent(i_prey)*bot_pel_conv)`

### `sCBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (461)
- Formula (d⁻¹): `tCBenBent*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCBent_PV,tCBenBent*bot_pel_conv)`

### `sDBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (458)
- Formula (d⁻¹): `tDBenBent*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDBent_PV,tDBenBent*bot_pel_conv)`

### `sNBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (460)
- Formula (d⁻¹): `tNBenBent*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNBent_PV,tNBenBent*bot_pel_conv)`

### `sPBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables
- Source: zoobenthos.F90 (459)
- Formula (d⁻¹): `tPBenBent*bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPBent_PV,tPBenBent*bot_pel_conv)`

### `bot_pel_conv` [-] *Bottom exchange*
- DESC: bottom/pelagic conversion factor
- Source: fish.F90 (1132)
- Formula (d⁻¹): `_GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)`
- Code: `_GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)`

### `tCConsFiBent_bottom` [-] *Bottom exchange*
- DESC: apply consumption to benthos prey C
- Source: fish.F90 (1142)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CFoodBent(i_prey), -tCConsFiBent(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_CFoodBent(i_prey), -tCConsFiBent(i_prey)*bot_pel_conv)`

### `tCConsFiBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables (C)
- Source: fish.F90 (1146)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CFoodBent_PV(i_prey),-tCConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CFoodBent_PV(i_prey),-tCConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`

### `tDConsFiBent_bottom` [-] *Bottom exchange*
- DESC: apply consumption to benthos prey DW
- Source: fish.F90 (1139)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DFoodBent(i_prey), -tDConsFiBent(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_DFoodBent(i_prey), -tDConsFiBent(i_prey)*bot_pel_conv)`

### `tDConsFiBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables (DW)
- Source: fish.F90 (1143)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DFoodBent_PV(i_prey),-tDConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DFoodBent_PV(i_prey),-tDConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`

### `tNConsFiBent_bottom` [-] *Bottom exchange*
- DESC: apply consumption to benthos prey N
- Source: fish.F90 (1140)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NFoodBent(i_prey), -tNConsFiBent(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_NFoodBent(i_prey), -tNConsFiBent(i_prey)*bot_pel_conv)`

### `tNConsFiBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables (N)
- Source: fish.F90 (1144)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NFoodBent_PV(i_prey),-tNConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NFoodBent_PV(i_prey),-tNConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`

### `tPConsFiBent_bottom` [-] *Bottom exchange*
- DESC: apply consumption to benthos prey P
- Source: fish.F90 (1141)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PFoodBent(i_prey), -tPConsFiBent(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_PFoodBent(i_prey), -tPConsFiBent(i_prey)*bot_pel_conv)`

### `tPConsFiBent_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom variables (P)
- Source: fish.F90 (1145)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PFoodBent_PV(i_prey),-tPConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PFoodBent_PV(i_prey),-tPConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)`

### `BioTurb` [gDW/m2/d] *Bottom exchange*
- DESC: bioturbation converted from gDW/m3/d to gDW/m2/d
- Source: sediment_exchange.F90 (406)
- Formula (d⁻¹): `BioTurb=BioTurb*bot_pel_conv`
- Code: `BioTurb=BioTurb*bot_pel_conv`

### `s*DOMS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom DOM variables per group (dim nDOM)
- Source: sediment_exchange.F90 (587-590)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDDOMS_PV(i_dom),tDAbioDOMS(i_dom)*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDDOMS_PV(i_dom),tDAbioDOMS(i_dom)*bot_pel_conv)`

### `s*POMS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom POM variables per group (dim nPOM)
- Source: sediment_exchange.F90 (573-576)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV(i_pom),tDAbioPOMS(i_pom)*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV(i_pom),tDAbioPOMS(i_pom)*bot_pel_conv)`

### `sDIMW` [-] *Bottom exchange*
- DESC: water IM exchange (resus - sed)
- Source: sediment_exchange.F90 (607)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDIMW, tDResusIM -tDSedIM)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDIMW,  tDResusIM   -tDSedIM)`

### `sNH4W/sNO3W/sPO4W` [-] *Bottom exchange*
- DESC: water DIN/PO4 exchange (resus + dif)
- Source: sediment_exchange.F90 (611-613)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNH4W, tNResusNH4 +tNDifNH4)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNH4W,  tNResusNH4  +tNDifNH4)`

### `sSiO2W` [-] *Bottom exchange*
- DESC: water SiO2 exchange (resus + dif)
- Source: sediment_exchange.F90 (609)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sSiO2W, tSiResusSiO2+tSiDifSiO2)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sSiO2W, tSiResusSiO2+tSiDifSiO2)`

### `BioTurb` [gDW/m2/d] *Bottom exchange*
- DESC: bioturbation converted from gDW/m3/d to gDW/m2/d
- Source: resus_sed.F90 (200)
- Formula (d⁻¹): `BioTurb=BioTurb*bot_pel_conv`
- Code: `BioTurb=BioTurb*bot_pel_conv`

### `s*POMS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom POM variables
- Source: resus_sed.F90 (287-289)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV,tDAbioPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV,tDAbioPOMS*bot_pel_conv)`

### `sNH4W/sNO3W/sPO4W` [-] *Bottom exchange*
- DESC: water DIN/PO4 exchange (resus only, no diffusion)
- Source: resus_sed.F90 (304-306)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNH4W, tNResusNH4)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNH4W,  tNResusNH4)`

### `SWDIM` [-] *Bottom exchange*
- DESC: water IM exchange (resus - sed)
- Source: resus_sed.F90 (298)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_SWDIM, tDResusIM -tDSetIM)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_SWDIM,  tDResusIM   -tDSetIM)`

### `DOM*_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom DOM variables per group (dim nDOM)
- Source: burial.F90 (407-410)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DOMD_PV(i_spec),-tDBurDOM(i_spec)*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DOMD_PV(i_spec),-tDBurDOM(i_spec)*bot_pel_conv)`

### `POM*_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom POM variables per group (dim nPOM)
- Source: burial.F90 (397-400)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_POMD_PV(i_spec),-tDBurPOM(i_spec)*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_POMD_PV(i_spec),-tDBurPOM(i_spec)*bot_pel_conv)`

### `WSDHum_PV etc.` [-] *Bottom exchange*
- DESC: update ROC of projected bottom humus variables
- Source: burial.F90 (422-425)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_WSDHum_PV, tDBurHum*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_WSDHum_PV, tDBurHum*bot_pel_conv)`

### `BivAd_D/N/P/C` [-] *Bottom exchange*
- DESC: case qStageOpt=2 or 3: update adult stage ODEs (aging flux)
- Source: bivalves.F90 (660-663)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_BivAd_D, tDAgeBiv)`
- Code: `_SET_BOTTOM_ODE_(self%id_BivAd_D, tDAgeBiv)`

### `BivAd_D/N/P/C_PV` [-] *Bottom exchange*
- DESC: update ROC of projected adult stage variables
- Source: bivalves.F90 (664-667)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_BivAd_D_PV,tDAgeBiv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_BivAd_D_PV,tDAgeBiv*bot_pel_conv)`

### `BivJu_D/N/P/C` [-] *Bottom exchange*
- DESC: case qStageOpt=1 or 3: update juvenile stage ODEs (reproduction flux)
- Source: bivalves.F90 (650-653)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_BivJu_D, tDReprBiv)`
- Code: `_SET_BOTTOM_ODE_(self%id_BivJu_D, tDReprBiv)`

### `BivJu_D/N/P/C_PV` [-] *Bottom exchange*
- DESC: update ROC of projected juvenile stage variables
- Source: bivalves.F90 (654-657)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_BivJu_D_PV,tDReprBiv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_BivJu_D_PV,tDReprBiv*bot_pel_conv)`

### `CPOMpoolS` [-] *Bottom exchange*
- DESC: update abiotic POM C pool in sediment
- Source: bivalves.F90 (639)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCBivPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCBivPOMS)`

### `CPOMpoolS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected POM C sediment variable
- Source: bivalves.F90 (645)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCBivPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCBivPOMS*bot_pel_conv)`

### `CPOMpoolW` [-] *Bottom exchange*
- DESC: update abiotic POM C pool in water
- Source: bivalves.F90 (633)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolW, tCBivPOMW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolW, tCBivPOMW)`

### `DPOMpoolS` [-] *Bottom exchange*
- DESC: update abiotic POM DW pool in sediment
- Source: bivalves.F90 (636)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDBivPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDBivPOMS)`

### `DPOMpoolS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected POM DW sediment variable
- Source: bivalves.F90 (642)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDBivPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDBivPOMS*bot_pel_conv)`

### `DPOMpoolW` [-] *Bottom exchange*
- DESC: update abiotic POM DW pool in water
- Source: bivalves.F90 (630)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolW, tDBivPOMW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolW, tDBivPOMW)`

### `NH4poolW` [-] *Bottom exchange*
- DESC: update abiotic NH4 pool in water
- Source: bivalves.F90 (634)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NH4poolW, tNBivNH4W)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NH4poolW, tNBivNH4W)`

### `NPOMpoolS` [-] *Bottom exchange*
- DESC: update abiotic POM N pool in sediment
- Source: bivalves.F90 (637)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNBivPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNBivPOMS)`

### `NPOMpoolS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected POM N sediment variable
- Source: bivalves.F90 (643)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNBivPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNBivPOMS*bot_pel_conv)`

### `NPOMpoolW` [-] *Bottom exchange*
- DESC: update abiotic POM N pool in water
- Source: bivalves.F90 (631)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolW, tNBivPOMW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolW, tNBivPOMW)`

### `PO4poolW` [-] *Bottom exchange*
- DESC: update abiotic PO4 pool in water
- Source: bivalves.F90 (635)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PO4poolW, tPBivPO4W)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PO4poolW, tPBivPO4W)`

### `PPOMpoolS` [-] *Bottom exchange*
- DESC: update abiotic POM P pool in sediment
- Source: bivalves.F90 (638)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPBivPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPBivPOMS)`

### `PPOMpoolS_PV` [-] *Bottom exchange*
- DESC: update ROC of projected POM P sediment variable
- Source: bivalves.F90 (644)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPBivPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPBivPOMS*bot_pel_conv)`

### `PPOMpoolW` [-] *Bottom exchange*
- DESC: update abiotic POM P pool in water
- Source: bivalves.F90 (632)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolW, tPBivPOMW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolW, tPBivPOMW)`

### `PreyD/N/P/C` [-] *Bottom exchange*
- DESC: update prey ODEs (negative consumption)
- Source: bivalves.F90 (622-625)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PreyD(i_prey),-tDConsBiv(i_prey))`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PreyD(i_prey),-tDConsBiv(i_prey))`

### `sCBiv` [-] *Bottom exchange*
- DESC: update bivalves C ODE
- Source: bivalves.F90 (612)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sCBiv,tCBivBiva)`
- Code: `_SET_BOTTOM_ODE_(self%id_sCBiv,tCBivBiva)`

### `sCBiv_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom C variable
- Source: bivalves.F90 (617)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sCBiv_PV,tCBivBiva*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCBiv_PV,tCBivBiva*bot_pel_conv)`

### `sDBiv` [-] *Bottom exchange*
- DESC: update bivalves DW ODE
- Source: bivalves.F90 (609)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sDBiv,tDBivBiva)`
- Code: `_SET_BOTTOM_ODE_(self%id_sDBiv,tDBivBiva)`

### `sDBiv_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom DW variable
- Source: bivalves.F90 (614)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDBiv_PV,tDBivBiva*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDBiv_PV,tDBivBiva*bot_pel_conv)`

### `SiPapoolS` [-] *Bottom exchange*
- DESC: update abiotic SiPa pool in sediment
- Source: bivalves.F90 (640)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiO2BivS)`
- Code: `_SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiO2BivS)`

### `sNBiv` [-] *Bottom exchange*
- DESC: update bivalves N ODE
- Source: bivalves.F90 (610)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sNBiv,tNBivBiva)`
- Code: `_SET_BOTTOM_ODE_(self%id_sNBiv,tNBivBiva)`

### `sNBiv_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom N variable
- Source: bivalves.F90 (615)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNBiv_PV,tNBivBiva*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNBiv_PV,tNBivBiva*bot_pel_conv)`

### `sPBiv` [-] *Bottom exchange*
- DESC: update bivalves P ODE
- Source: bivalves.F90 (611)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sPBiv,tPBivBiva)`
- Code: `_SET_BOTTOM_ODE_(self%id_sPBiv,tPBivBiva)`

### `sPBiv_PV` [-] *Bottom exchange*
- DESC: update ROC of projected bottom P variable
- Source: bivalves.F90 (616)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sPBiv_PV,tPBivBiva*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPBiv_PV,tPBivBiva*bot_pel_conv)`

### `tDBivPOMS` [-] *Bottom exchange*
- DESC: update compulsory diagnostic POMS production
- Source: bivalves.F90 (672)
- Formula (d⁻¹): `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBivPOMS,tDBivPOMS)`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBivPOMS,tDBivPOMS)`

## Bottom-pelagic conversion

### `bot_pel_conv` [-] *Bottom-pelagic conversion*
- DESC: if hypsograph: conversion factor = 1/bot_pel_conv (per area to per m3)
- Source: bot_pel_interface.F90 (75)
- Formula (d⁻¹): `bot_pel_conv = 1.0_rk/bot_pel_conv`
- Code: `bot_pel_conv = 1.0_rk/bot_pel_conv`

### `bot_pel_conv` [-] *Bottom-pelagic conversion*
- DESC: else (no hypsograph): conversion factor = cell thickness dz
- Source: bot_pel_interface.F90 (77)
- Formula (d⁻¹): `_GET_(self%id_dz,bot_pel_conv)`
- Code: `_GET_(self%id_dz,bot_pel_conv)`

### `bot_pel_conv` [-] *Bottom-pelagic conversion*
- DESC: set diagnostic conversion factor
- Source: bot_pel_interface.F90 (79)
- Formula (d⁻¹): `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_bot_pel_conv_out,bot_pel_conv)`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_bot_pel_conv_out,bot_pel_conv)`

## Burial

### `tCBurDOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of CDOM per group (dim nDOM)
- Source: burial.F90 (341)
- Formula (d⁻¹): `tCBurDOM = sCDOMS *(vDeltaS / cDepthS)`
- Code: `tCBurDOM = sCDOMS *(vDeltaS / cDepthS)`

### `tCBurPOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of C in POM per group (dim nPOM)
- Source: burial.F90 (340)
- Formula (d⁻¹): `tCBurPOM = rCDPOMS * tDBurPOM`
- Code: `tCBurPOM = rCDPOMS * tDBurPOM`

### `tDBurDOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of DDOM per group (dim nDOM)
- Source: burial.F90 (322)
- Formula (d⁻¹): `tDBurDOM = sDDOMS *(vDeltaS / cDepthS)`
- Code: `tDBurDOM = sDDOMS *(vDeltaS / cDepthS)`

### `tDBurIM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of DW in inorganic matter
- Source: burial.F90 (318-319)
- Formula (d⁻¹): `tDBurIM = (tDPOMS + (self%cRhoOM / self%cRhoIM) * tDAbioIMS) / (sDPOMSTot / (sDIMS+NearZero) + self%cRhoOM / self%cRhoIM)`
- Code: `tDBurIM = (tDPOMS + (self%cRhoOM / self%cRhoIM) * tDAbioIMS) / (sDPOMSTot / (sDIMS+NearZero) + self%cRhoOM / self%cRhoIM)`

### `tDBurOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of DW in organic matter
- Source: burial.F90 (320)
- Formula (d⁻¹): `tDBurOM = sDPOMSTot / (sDIMS+NearZero) * tDBurIM`
- Code: `tDBurOM = sDPOMSTot / (sDIMS+NearZero) * tDBurIM`

### `tDBurPOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of DW in POM per group (dim nPOM)
- Source: burial.F90 (321)
- Formula (d⁻¹): `tDBurPOM = sDPOMS /(sDPOMSTot) * tDBurOM`
- Code: `tDBurPOM = sDPOMS /(sDPOMSTot) * tDBurOM`

### `tDPOMS` [g/m2/s] *Burial*
- DESC: current ROC of total sediment POM
- Source: burial.F90 (309)
- Formula (d⁻¹): `tDPOMS= sum(tDReSedPOMS) + sum(tDPOMS_POM) + sum(tDPOMS_Phyt) + sum(tDPOMS_Bent) + sum(tDPOMS_Macro)`
- Code: `tDPOMS= sum(tDReSedPOMS) + sum(tDPOMS_POM) + sum(tDPOMS_Phyt) + sum(tDPOMS_Bent) + sum(tDPOMS_Macro)`

### `tNBurDOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of NDOM per group (dim nDOM)
- Source: burial.F90 (336)
- Formula (d⁻¹): `tNBurDOM = sNDOMS *(vDeltaS / cDepthS)`
- Code: `tNBurDOM = sNDOMS *(vDeltaS / cDepthS)`

### `tNBurNH4` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of dissolved NH4
- Source: burial.F90 (334)
- Formula (d⁻¹): `tNBurNH4 = sNH4S *(vDeltaS /cDepthS)`
- Code: `tNBurNH4 = sNH4S *(vDeltaS /cDepthS)`

### `tNBurNO3` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of dissolved NO3
- Source: burial.F90 (335)
- Formula (d⁻¹): `tNBurNO3 = sNO3S *(vDeltaS / cDepthS)`
- Code: `tNBurNO3 = sNO3S *(vDeltaS / cDepthS)`

### `tNBurPOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of N in POM per group (dim nPOM)
- Source: burial.F90 (333)
- Formula (d⁻¹): `tNBurPOM = rNDPOMS * tDBurPOM`
- Code: `tNBurPOM = rNDPOMS * tDBurPOM`

### `tPBurAIM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of P adsorbed onto IM
- Source: burial.F90 (327)
- Formula (d⁻¹): `tPBurAIM = sPAIMS / sDIMS * tDBurIM`
- Code: `tPBurAIM = sPAIMS / sDIMS * tDBurIM`

### `tPBurDOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of PDOM per group (dim nDOM)
- Source: burial.F90 (329)
- Formula (d⁻¹): `tPBurDOM = sPDOMS *(vDeltaS / cDepthS)`
- Code: `tPBurDOM = sPDOMS *(vDeltaS / cDepthS)`

### `tPBurPO4` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of dissolved P
- Source: burial.F90 (328)
- Formula (d⁻¹): `tPBurPO4 = sPO4S *(vDeltaS / cDepthS)`
- Code: `tPBurPO4 = sPO4S *(vDeltaS / cDepthS)`

### `tPBurPOM` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of P in POM per group (dim nPOM)
- Source: burial.F90 (326)
- Formula (d⁻¹): `tPBurPOM = rPDPOMS * tDBurPOM`
- Code: `tPBurPOM = rPDPOMS * tDBurPOM`

### `tSiBurPa` [g/m2/s] *Burial*
- DESC: case vDeltaS>=0: burial flux of particulate Si
- Source: burial.F90 (345)
- Formula (d⁻¹): `tSiBurPa = rSiDPOMS * tDBurOM`
- Code: `tSiBurPa = rSiDPOMS * tDBurOM`

### `vDeltaS` [m] *Burial*
- DESC: turnover depth in lake (core variable: >=0 normal burial; <0 erosion+humus)
- Source: burial.F90 (310)
- Formula (d⁻¹): `vDeltaS = (tDAbioIMS / self%cRhoIM + tDPOMS / self%cRhoOM)/(1.0_rk - bPorS)`
- Code: `vDeltaS = (tDAbioIMS / self%cRhoIM + tDPOMS / self%cRhoOM)/(1.0_rk - bPorS)`

## Consumption

### `tDConsFiBen` [1/d] *Consumption*
- DESC: DW consumption of zoobenthos (per prey)
- Source: fish_pclake.F90 (542)
- Formula (d⁻¹): `tDConsFiBen = relabBEN * (tDAssFiBen / fDAssFi)`
- Code: `tDConsFiBen = relabBEN * (tDAssFiBen / self%fDAssFi)`

### `tDConsFiBenSum` [1/d] *Consumption*
- DESC: total zoobenthos DW consumption
- Source: fish_pclake.F90 (555)
- Formula (d⁻¹): `tDConsFiBenSum = sum(tDConsFiBen)`
- Code: `tDConsFiBenSum = sum(tDConsFiBen)`

### `tDConsFiPisc` [1/d] *Consumption*
- DESC: DW consumption of fish (per prey)
- Source: fish_pclake.F90 (548)
- Formula (d⁻¹): `tDConsFiPisc = relabPISC * (tDAssFiPisc / fDAssFi)`
- Code: `tDConsFiPisc = relabPISC * (tDAssFiPisc / self%fDAssFi)`

### `tDConsFiPiscSum` [1/d] *Consumption*
- DESC: total fish DW consumption
- Source: fish_pclake.F90 (556)
- Formula (d⁻¹): `tDConsFiPiscSum = sum(tDConsFiPisc)`
- Code: `tDConsFiPiscSum = sum(tDConsFiPisc)`

### `tDConsFiTot` [1/d] *Consumption*
- DESC: total DW consumption
- Source: fish_pclake.F90 (563)
- Formula (d⁻¹): `tDConsFiTot = tDConsFiZooSum + tDConsFiBenSum + tDConsFiPiscSum`
- Code: `tDConsFiTot = tDConsFiZooSum + tDConsFiBenSum + tDConsFiPiscSum`

### `tDConsFiZoo` [1/d] *Consumption*
- DESC: DW consumption of zooplankton (per prey)
- Source: fish_pclake.F90 (536)
- Formula (d⁻¹): `tDConsFiZoo = relabZOO * (tDAssFiZoo / fDAssFi)`
- Code: `tDConsFiZoo = relabZOO * (tDAssFiZoo / self%fDAssFi)`

### `tDConsFiZooSum` [1/d] *Consumption*
- DESC: total zooplankton DW consumption
- Source: fish_pclake.F90 (554)
- Formula (d⁻¹): `tDConsFiZooSum = sum(tDConsFiZoo)`
- Code: `tDConsFiZooSum = sum(tDConsFiZoo)`

### `tNConsFiBen` [1/d] *Consumption*
- DESC: N consumption of zoobenthos (per prey)
- Source: fish_pclake.F90 (544)
- Formula (d⁻¹): `tNConsFiBen = rNDBent * tDConsFiBen`
- Code: `tNConsFiBen = rNDBent * tDConsFiBen`

### `tNConsFiBenSum` [1/d] *Consumption*
- DESC: total zoobenthos N consumption
- Source: fish_pclake.F90 (561)
- Formula (d⁻¹): `tNConsFiBenSum = sum(tNConsFiBen)`
- Code: `tNConsFiBenSum = sum(tNConsFiBen)`

### `tNConsFiPisc` [1/d] *Consumption*
- DESC: N consumption of fish (per prey)
- Source: fish_pclake.F90 (550)
- Formula (d⁻¹): `tNConsFiPisc = rNDPisc * tDConsFiPisc`
- Code: `tNConsFiPisc = rNDPisc * tDConsFiPisc`

### `tNConsFiPiscSum` [1/d] *Consumption*
- DESC: total fish N consumption
- Source: fish_pclake.F90 (562)
- Formula (d⁻¹): `tNConsFiPiscSum = sum(tNConsFiPisc)`
- Code: `tNConsFiPiscSum = sum(tNConsFiPisc)`

### `tNConsFiTot` [1/d] *Consumption*
- DESC: total N consumption
- Source: fish_pclake.F90 (565)
- Formula (d⁻¹): `tNConsFiTot = tNConsFiZooSum + tNConsFiBenSum + tNConsFiPiscSum`
- Code: `tNConsFiTot = tNConsFiZooSum + tNConsFiBenSum + tNConsFiPiscSum`

### `tNConsFiZoo` [1/d] *Consumption*
- DESC: N consumption of zooplankton (per prey)
- Source: fish_pclake.F90 (538)
- Formula (d⁻¹): `tNConsFiZoo = rNDZoo * tDConsFiZoo`
- Code: `tNConsFiZoo = rNDZoo * tDConsFiZoo`

### `tNConsFiZooSum` [1/d] *Consumption*
- DESC: total zooplankton N consumption
- Source: fish_pclake.F90 (560)
- Formula (d⁻¹): `tNConsFiZooSum = sum(tNConsFiZoo)`
- Code: `tNConsFiZooSum = sum(tNConsFiZoo)`

### `tPConsFiBen` [1/d] *Consumption*
- DESC: P consumption of zoobenthos (per prey)
- Source: fish_pclake.F90 (543)
- Formula (d⁻¹): `tPConsFiBen = rPDBent * tDConsFiBen`
- Code: `tPConsFiBen = rPDBent * tDConsFiBen`

### `tPConsFiBenSum` [1/d] *Consumption*
- DESC: total zoobenthos P consumption
- Source: fish_pclake.F90 (558)
- Formula (d⁻¹): `tPConsFiBenSum = sum(tPConsFiBen)`
- Code: `tPConsFiBenSum = sum(tPConsFiBen)`

### `tPConsFiPisc` [1/d] *Consumption*
- DESC: P consumption of fish (per prey)
- Source: fish_pclake.F90 (549)
- Formula (d⁻¹): `tPConsFiPisc = rPDPisc * tDConsFiPisc`
- Code: `tPConsFiPisc = rPDPisc * tDConsFiPisc`

### `tPConsFiPiscSum` [1/d] *Consumption*
- DESC: total fish P consumption
- Source: fish_pclake.F90 (559)
- Formula (d⁻¹): `tPConsFiPiscSum = sum(tPConsFiPisc)`
- Code: `tPConsFiPiscSum = sum(tPConsFiPisc)`

### `tPConsFiTot` [1/d] *Consumption*
- DESC: total P consumption
- Source: fish_pclake.F90 (564)
- Formula (d⁻¹): `tPConsFiTot = tPConsFiZooSum + tPConsFiBenSum + tPConsFiPiscSum`
- Code: `tPConsFiTot = tPConsFiZooSum + tPConsFiBenSum + tPConsFiPiscSum`

### `tPConsFiZoo` [1/d] *Consumption*
- DESC: P consumption of zooplankton (per prey)
- Source: fish_pclake.F90 (537)
- Formula (d⁻¹): `tPConsFiZoo = rPDZoo * tDConsFiZoo`
- Code: `tPConsFiZoo = rPDZoo * tDConsFiZoo`

### `tPConsFiZooSum` [1/d] *Consumption*
- DESC: total zooplankton P consumption
- Source: fish_pclake.F90 (557)
- Formula (d⁻¹): `tPConsFiZooSum = sum(tPConsFiZoo)`
- Code: `tPConsFiZooSum = sum(tPConsFiZoo)`

## Denitrification

### `tCDenitS` [-] *Denitrification*
- DESC: calculate C mineralization flux by denitrification
- Source: abiotic_sediment.F90 (251-252)
- Formula (d⁻¹): `oNO3S*oNO3S/(hNO3DenitS*hNO3DenitS+oNO3S*oNO3S)*(1.0-afOxySed)*(sum(tCTrans_POM) + sum(tCTrans_DOM))`
- Code: `tCDenitS=oNO3S*oNO3S/(self%hNO3DenitS*self%hNO3DenitS+oNO3S*oNO3S)*(1.0-afOxySed)*(sum(tCTrans_POM) + sum(tCTrans_DOM))`

### `tNDenitS` [-] *Denitrification*
- DESC: calculate N denitrification flux
- Source: abiotic_sediment.F90 (253-253)
- Formula (d⁻¹): `NO3PerCS*molNmolC*tCDenitS`
- Code: `tNDenitS=self%NO3PerCS*molNmolC*tCDenitS`

### `wDDenitW` [-] *Denitrification*
- DESC: mineralization flux by denitrification
- Source: om_pool.F90 (317)
- Formula (d⁻¹): `wDDenitW = sNO3W*sNO3W/(self%hNO3DenitW*self%hNO3DenitW+sNO3W*sNO3W)*(1.0_rk-aCorO2BOD)*wDMin`
- Code: `wDDenitW = sNO3W*sNO3W/(self%hNO3DenitW*self%hNO3DenitW+sNO3W*sNO3W)*(1.0_rk-aCorO2BOD)*wDMin`

### `wNDenitW` [-] *Denitrification*
- DESC: Denitrification flux
- Source: om_pool.F90 (318)
- Formula (d⁻¹): `wNDenitW=self%NO3PerCW*molNmolC*rCDW*wDDenitW`
- Code: `wNDenitW=self%NO3PerCW*molNmolC*rCDW*wDDenitW`

## Dependencies

### `salt` [-] *Dependencies*
- DESC: practical_salinity
- Source: abiotic_water.F90 (148-148)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_salt, standard_variables%practical_salinity)`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: abiotic_water.F90 (146-146)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `uVWind` [-] *Dependencies*
- DESC: wind_speed
- Source: abiotic_water.F90 (147-147)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uVWind, standard_variables%wind_speed)`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bot_pel_conv
- Source: abiotic_sediment.F90 (161-161)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_bot_pel_conv, type_bulk_standard_variable(name='bot_pel_conv',units='-'))`

### `depth` [-] *Dependencies*
- DESC: bottom_depth
- Source: abiotic_sediment.F90 (158-158)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_depth, standard_variables%bottom_depth)`

### `dz` [-] *Dependencies*
- DESC: cell_thickness
- Source: abiotic_sediment.F90 (159-159)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_dz, standard_variables%cell_thickness)`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: abiotic_sediment.F90 (157-157)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `afOxySed` [m/m] *Dependencies*
- DESC: fraction of aerobic sediment
- Source: om_pool.F90 (163)
- Formula (d⁻¹): `call self%register_horizontal_dependency(self%id_afOxySed, 'afOxySed', 'm/m', 'fraction of aerobic sediment')`
- Code: `call self%register_horizontal_dependency(self%id_afOxySed,  'afOxySed',       'm/m',   'fraction of aerobic sediment'                                                                          )`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: om_pool.F90 (253)
- Formula (d⁻¹): `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`
- Code: `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `C_refractory_sediment` [g/m2] *Dependencies*
- DESC: C refractory target sediment
- Source: om_pool.F90 (241)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CRefrS, 'C_refractory_sediment', 'g/m2', 'C refractory target sediment')`
- Code: `call self%register_state_dependency(self%id_CRefrS,          'C_refractory_sediment',         'g/m2',            'C refractory target sediment')`

### `C_refractory_sediment_PV` [g/m3] *Dependencies*
- DESC: C refractory target sediment pelagic mirror
- Source: om_pool.F90 (246)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CRefrS_PV, 'C_refractory_sediment_PV', 'g/m3', 'C refractory target sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_CRefrS_PV,   'C_refractory_sediment_PV',      'g/m3',            'C refractory target sediment pelagic mirror')`

### `C_transformation_sediment` [g/m2] *Dependencies*
- DESC: C biotransformation target sediment
- Source: om_pool.F90 (226)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CTransS, 'C_transformation_sediment', 'g/m2', 'C biotransformation target sediment')`
- Code: `call self%register_state_dependency(self%id_CTransS,         'C_transformation_sediment',     'g/m2',            'C biotransformation target sediment')`

### `C_transformation_sediment_PV` [g/m3] *Dependencies*
- DESC: C biotransformation sediment pelagic mirror
- Source: om_pool.F90 (234)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CTransS_PV, 'C_transformation_sediment_PV', 'g/m3', 'C biotransformation sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_CTransS_PV,      'C_transformation_sediment_PV',  'g/m3',            'C biotransformation sediment pelagic mirror')`

### `C_transformation_water` [g/m3] *Dependencies*
- DESC: C biotransformation target water
- Source: om_pool.F90 (208)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CTransW, 'C_transformation_water', 'g/m3', 'C biotransformation target water')`
- Code: `call self%register_state_dependency(self%id_CTransW,         'C_transformation_water',       'g/m3',            'C biotransformation target water')`

### `DW_refractory_sediment` [g/m2] *Dependencies*
- DESC: DW refractory target sediment
- Source: om_pool.F90 (238)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DRefrS, 'DW_refractory_sediment', 'g/m2', 'DW refractory target sediment')`
- Code: `call self%register_state_dependency(self%id_DRefrS,          'DW_refractory_sediment',        'g/m2',            'DW refractory target sediment')`

### `DW_refractory_sediment_PV` [g/m3] *Dependencies*
- DESC: DW refractory target sediment pelagic mirror
- Source: om_pool.F90 (243)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DRefrS_PV, 'DW_refractory_sediment_PV', 'g/m3', 'DW refractory target sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_DRefrS_PV,   'DW_refractory_sediment_PV',     'g/m3',            'DW refractory target sediment pelagic mirror')`

### `DW_transformation_sediment` [g/m2] *Dependencies*
- DESC: DW biotransformation target sediment
- Source: om_pool.F90 (225)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DTransS, 'DW_transformation_sediment', 'g/m2', 'DW biotransformation target sediment')`
- Code: `call self%register_state_dependency(self%id_DTransS,         'DW_transformation_sediment',    'g/m2',            'DW biotransformation target sediment')`

### `DW_transformation_sediment_PV` [g/m3] *Dependencies*
- DESC: DW biotransformation sediment pelagic mirror
- Source: om_pool.F90 (231)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DTransS_PV, 'DW_transformation_sediment_PV', 'g/m3', 'DW biotransformation sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_DTransS_PV,      'DW_transformation_sediment_PV', 'g/m3',            'DW biotransformation sediment pelagic mirror')`

### `DW_transformation_water` [g/m3] *Dependencies*
- DESC: DW biotransformation target water
- Source: om_pool.F90 (207)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DTransW, 'DW_transformation_water', 'g/m3', 'DW biotransformation target water')`
- Code: `call self%register_state_dependency(self%id_DTransW,         'DW_transformation_water',      'g/m3',            'DW biotransformation target water')`

### `N_refractory_sediment` [g/m2] *Dependencies*
- DESC: N refractory target sediment
- Source: om_pool.F90 (239)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NRefrS, 'N_refractory_sediment', 'g/m2', 'N refractory target sediment')`
- Code: `call self%register_state_dependency(self%id_NRefrS,          'N_refractory_sediment',         'g/m2',            'N refractory target sediment')`

### `N_refractory_sediment_PV` [g/m3] *Dependencies*
- DESC: N refractory target sediment pelagic mirror
- Source: om_pool.F90 (244)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NRefrS_PV, 'N_refractory_sediment_PV', 'g/m3', 'N refractory target sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_NRefrS_PV,   'N_refractory_sediment_PV',      'g/m3',            'N refractory target sediment pelagic mirror')`

### `N_transformation_sediment` [g/m2] *Dependencies*
- DESC: N biotransformation target sediment
- Source: om_pool.F90 (228)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NTransS, 'N_transformation_sediment', 'g/m2', 'N biotransformation target sediment')`
- Code: `call self%register_state_dependency(self%id_NTransS,             'N_transformation_sediment',     'g/m2',            'N biotransformation target sediment')`

### `N_transformation_sediment_PV` [g/m3] *Dependencies*
- DESC: N biotransformation sediment pelagic mirror
- Source: om_pool.F90 (232)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NTransS_PV, 'N_transformation_sediment_PV', 'g/m3', 'N biotransformation sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_NTransS_PV,      'N_transformation_sediment_PV',  'g/m3',            'N biotransformation sediment pelagic mirror')`

### `N_transformation_water` [g/m3] *Dependencies*
- DESC: N biotransformation target water
- Source: om_pool.F90 (210)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NTransW, 'N_transformation_water', 'g/m3', 'N biotransformation target water')`
- Code: `call self%register_state_dependency(self%id_NTransW,             'N_transformation_water',       'g/m3',            'N biotransformation target water')`

### `NO3_pool_water` [g/m3] *Dependencies*
- DESC: NO3 pool water
- Source: om_pool.F90 (213)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NO3poolW, 'NO3_pool_water', 'g/m3', 'NO3 pool water')`
- Code: `call self%register_state_dependency(self%id_NO3poolW,            'NO3_pool_water',               'g/m3',            'NO3 pool water')`

### `oxygen_pool_water` [g/m3] *Dependencies*
- DESC: oxygen_pool_water
- Source: om_pool.F90 (212)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_O2poolW, 'oxygen_pool_water', 'g/m3', 'oxygen_pool_water')`
- Code: `call self%register_state_dependency(self%id_O2poolW,             'oxygen_pool_water',            'g/m3',            'oxygen_pool_water')`

### `P_refractory_sediment` [g/m2] *Dependencies*
- DESC: P refractory target sediment
- Source: om_pool.F90 (240)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PRefrS, 'P_refractory_sediment', 'g/m2', 'P refractory target sediment')`
- Code: `call self%register_state_dependency(self%id_PRefrS,          'P_refractory_sediment',         'g/m2',            'P refractory target sediment')`

### `P_refractory_sediment_PV` [g/m3] *Dependencies*
- DESC: P refractory target sediment pelagic mirror
- Source: om_pool.F90 (245)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PRefrS_PV, 'P_refractory_sediment_PV', 'g/m3', 'P refractory target sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_PRefrS_PV,   'P_refractory_sediment_PV',      'g/m3',            'P refractory target sediment pelagic mirror')`

### `P_transformation_sediment` [g/m2] *Dependencies*
- DESC: P biotransformation target sediment
- Source: om_pool.F90 (229)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PTransS, 'P_transformation_sediment', 'g/m2', 'P biotransformation target sediment')`
- Code: `call self%register_state_dependency(self%id_PTransS,             'P_transformation_sediment',     'g/m2',            'P biotransformation target sediment')`

### `P_transformation_sediment_PV` [g/m3] *Dependencies*
- DESC: P biotransformation sediment pelagic mirror
- Source: om_pool.F90 (233)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PTransS_PV, 'P_transformation_sediment_PV', 'g/m3', 'P biotransformation sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_PTransS_PV,      'P_transformation_sediment_PV',  'g/m3',            'P biotransformation sediment pelagic mirror')`

### `P_transformation_water` [g/m3] *Dependencies*
- DESC: P biotransformation target water
- Source: om_pool.F90 (211)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PTransW, 'P_transformation_water', 'g/m3', 'P biotransformation target water')`
- Code: `call self%register_state_dependency(self%id_PTransW,             'P_transformation_water',       'g/m3',            'P biotransformation target water')`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: om_pool.F90 (255)
- Formula (d⁻¹): `call self%register_dependency(self%id_uTm, standard_variables%temperature)`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `afCovSurfVeg` [-] *Dependencies*
- DESC: fraction of surface vegetation coverage
- Source: phytoplankton.F90 (298)
- Formula (d⁻¹): `call self%register_dependency(self%id_afCovSurfVeg, type_bulk_standard_variable(name='total_afCovSurfVeg',units='-'))`
- Code: `call self%register_dependency(self%id_afCovSurfVeg,type_bulk_standard_variable(name='total_afCovSurfVeg',units='-'))`

### `aFunTauTmSet` [-] *Dependencies*
- DESC: basic settling rate
- Source: phytoplankton.F90 (300)
- Formula (d⁻¹): `call self%register_dependency(self%id_aFunTauTmSet, 'aFunTauTmSet', '-', 'basic settling rate')`
- Code: `call self%register_dependency(self%id_aFunTauTmSet,    'aFunTauTmSet',                    '-',              'basic settling rate')`

### `aLLim_in` [-] *Dependencies*
- DESC: light limitation factor (input)
- Source: phytoplankton.F90 (190)
- Formula (d⁻¹): `call self%register_dependency(self%id_aLLim_in, 'aLLim', '-', 'light limitation factor')`
- Code: `call self%register_dependency(self%id_aLLim_in,                 'aLLim',          '-',     'light limitation factor')`

### `aNutLim_in` [-] *Dependencies*
- DESC: nutrient limitation factor (input)
- Source: phytoplankton.F90 (194)
- Formula (d⁻¹): `call self%register_dependency(self%id_aNutLim_in, 'aNutLim', '-', 'nutrient limitation factor')`
- Code: `call self%register_dependency(self%id_aNutLim_in,               'aNutLim',        '-',     'nutrient limitation factor')`

### `base_resuspension_rate` [-] *Dependencies*
- DESC: base resuspension rate
- Source: phytoplankton.F90 (299)
- Formula (d⁻¹): `call self%register_dependency(self%id_tDResusDead, 'base_resuspension_rate', '-', 'base resuspension rate')`
- Code: `call self%register_dependency(self%id_tDResusDead,     'base_resuspension_rate',          '-',              'base resuspension rate')`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: phytoplankton.F90 (301)
- Formula (d⁻¹): `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`
- Code: `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `Day` [-] *Dependencies*
- DESC: number of days since start of the year
- Source: phytoplankton.F90 (306)
- Formula (d⁻¹): `call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`
- Code: `call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`

### `DOM_C_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM C in sediment
- Source: phytoplankton.F90 (288)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CDOMpoolS, 'DOM_C_pool_sediment', 'g/m2', 'DOM C in sediment')`
- Code: `call self%register_state_dependency(self%id_CDOMpoolS,          'DOM_C_pool_sediment',    'g/m2',            'DOM C in sediment')`

### `DOM_C_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM C in sediment pelagic mirror
- Source: phytoplankton.F90 (292)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CDOMpoolS_PV, 'DOM_C_pool_sediment_PV', 'g/m2', 'DOM C in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_CDOMpoolS_PV,       'DOM_C_pool_sediment_PV', 'g/m2',            'DOM C in sediment pelagic mirror')`

### `DOM_C_pool_water` [g/m3] *Dependencies*
- DESC: DOM C water
- Source: phytoplankton.F90 (273)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CDOMpoolW, 'DOM_C_pool_water', 'g/m3', 'DOM C water')`
- Code: `call self%register_state_dependency(self%id_CDOMpoolW,          'DOM_C_pool_water',       'g/m3',            'DOM C water')`

### `DOM_DW_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM DW in sediment
- Source: phytoplankton.F90 (285)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DDOMpoolS, 'DOM_DW_pool_sediment', 'g/m2', 'DOM DW in sediment')`
- Code: `call self%register_state_dependency(self%id_DDOMpoolS,          'DOM_DW_pool_sediment',   'g/m2',            'DOM DW in sediment')`

### `DOM_DW_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM DW in sediment pelagic mirror
- Source: phytoplankton.F90 (289)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DDOMpoolS_PV, 'DOM_DW_pool_sediment_PV', 'g/m2', 'DOM DW in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_DDOMpoolS_PV,       'DOM_DW_pool_sediment_PV','g/m2',            'DOM DW in sediment pelagic mirror')`

### `DOM_DW_pool_water` [g/m3] *Dependencies*
- DESC: DOM DW water
- Source: phytoplankton.F90 (270)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DDOMpoolW, 'DOM_DW_pool_water', 'g/m3', 'DOM DW water')`
- Code: `call self%register_state_dependency(self%id_DDOMpoolW,          'DOM_DW_pool_water',      'g/m3',            'DOM DW water')`

### `DOM_N_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM N in sediment
- Source: phytoplankton.F90 (286)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NDOMpoolS, 'DOM_N_pool_sediment', 'g/m2', 'DOM N in sediment')`
- Code: `call self%register_state_dependency(self%id_NDOMpoolS,          'DOM_N_pool_sediment',    'g/m2',            'DOM N in sediment')`

### `DOM_N_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM N in sediment pelagic mirror
- Source: phytoplankton.F90 (290)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NDOMpoolS_PV, 'DOM_N_pool_sediment_PV', 'g/m2', 'DOM N in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_NDOMpoolS_PV,       'DOM_N_pool_sediment_PV', 'g/m2',            'DOM N in sediment pelagic mirror')`

### `DOM_N_pool_water` [g/m3] *Dependencies*
- DESC: DOM N water
- Source: phytoplankton.F90 (271)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NDOMpoolW, 'DOM_N_pool_water', 'g/m3', 'DOM N water')`
- Code: `call self%register_state_dependency(self%id_NDOMpoolW,          'DOM_N_pool_water',       'g/m3',            'DOM N water')`

### `DOM_P_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM P in sediment
- Source: phytoplankton.F90 (287)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PDOMpoolS, 'DOM_P_pool_sediment', 'g/m2', 'DOM P in sediment')`
- Code: `call self%register_state_dependency(self%id_PDOMpoolS,          'DOM_P_pool_sediment',    'g/m2',            'DOM P in sediment')`

### `DOM_P_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM P in sediment pelagic mirror
- Source: phytoplankton.F90 (291)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PDOMpoolS_PV, 'DOM_P_pool_sediment_PV', 'g/m2', 'DOM P in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_PDOMpoolS_PV,       'DOM_P_pool_sediment_PV', 'g/m2',            'DOM P in sediment pelagic mirror')`

### `DOM_P_pool_water` [g/m3] *Dependencies*
- DESC: DOM P water
- Source: phytoplankton.F90 (272)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PDOMpoolW, 'DOM_P_pool_water', 'g/m3', 'DOM P water')`
- Code: `call self%register_state_dependency(self%id_PDOMpoolW,          'DOM_P_pool_water',       'g/m3',            'DOM P water')`

### `dz` [-] *Dependencies*
- DESC: cell thickness
- Source: phytoplankton.F90 (304)
- Formula (d⁻¹): `call self%register_dependency(self%id_dz, standard_variables%cell_thickness)`
- Code: `call self%register_dependency(self%id_dz,  standard_variables%cell_thickness)`

### `extc` [-] *Dependencies*
- DESC: attenuation coefficient of PAR
- Source: phytoplankton.F90 (305)
- Formula (d⁻¹): `call self%register_dependency(self%id_extc, standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)`
- Code: `call self%register_dependency(self%id_extc,standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)`

### `lat` [-] *Dependencies*
- DESC: latitude
- Source: phytoplankton.F90 (307)
- Formula (d⁻¹): `call self%register_dependency(self%id_lat, standard_variables%latitude)`
- Code: `call self%register_dependency(self%id_lat, standard_variables%latitude)`

### `meanpar` [-] *Dependencies*
- DESC: temporal mean of PAR
- Source: phytoplankton.F90 (309)
- Formula (d⁻¹): `call self%register_dependency(self%id_meanpar, temporal_mean(self%id_par,period=86400._rk,resolution=3600._rk,missing_value=0.0_rk))`
- Code: `call self%register_dependency(self%id_meanpar,temporal_mean(self%id_par,period=86400._rk,resolution=3600._rk,missing_value=0.0_rk))`

### `NH4_pool_sediment` [g/m2] *Dependencies*
- DESC: NH4 pool in sediment
- Source: phytoplankton.F90 (276)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NH4poolS, 'NH4_pool_sediment', 'g/m2', 'NH4 pool in sediment')`
- Code: `call self%register_state_dependency(self%id_NH4poolS,           'NH4_pool_sediment',      'g/m2',            'NH4 pool in sediment')`

### `NH4_pool_water` [g/m3] *Dependencies*
- DESC: NH4 pool water
- Source: phytoplankton.F90 (262)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NH4poolW, 'NH4_pool_water', 'g/m3', 'NH4 pool water')`
- Code: `call self%register_state_dependency(self%id_NH4poolW,           'NH4_pool_water',         'g/m3',            'NH4 pool water')`

### `NO3_pool_water` [g/m3] *Dependencies*
- DESC: NO3 pool water
- Source: phytoplankton.F90 (263)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NO3poolW, 'NO3_pool_water', 'g/m3', 'NO3 pool water')`
- Code: `call self%register_state_dependency(self%id_NO3poolW,           'NO3_pool_water',         'g/m3',            'NO3 pool water')`

### `oxygen_pool_water` [g/m3] *Dependencies*
- DESC: oxygen_pool_water
- Source: phytoplankton.F90 (264)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_O2poolW, 'oxygen_pool_water', 'g/m3', 'oxygen_pool_water')`
- Code: `call self%register_state_dependency(self%id_O2poolW,            'oxygen_pool_water',      'g/m3',            'oxygen_pool_water)')`

### `par` [-] *Dependencies*
- DESC: downwelling photosynthetic radiative flux
- Source: phytoplankton.F90 (308)
- Formula (d⁻¹): `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`
- Code: `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`

### `PO4_pool_sediment` [g/m2] *Dependencies*
- DESC: PO4 pool in sediment
- Source: phytoplankton.F90 (274)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PO4poolS, 'PO4_pool_sediment', 'g/m2', 'PO4 pool in sediment')`
- Code: `call self%register_state_dependency(self%id_PO4poolS,           'PO4_pool_sediment',      'g/m2',            'PO4 pool in sediment')`

### `PO4_pool_water` [g/m3] *Dependencies*
- DESC: PO4 pool water
- Source: phytoplankton.F90 (261)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PO4poolW, 'PO4_pool_water', 'g/m3', 'PO4 pool water')`
- Code: `call self%register_state_dependency(self%id_PO4poolW,           'PO4_pool_water',         'g/m3',            'PO4 pool water')`

### `POM_C_pool_sediment` [g/m2] *Dependencies*
- DESC: POM C pool in sediment
- Source: phytoplankton.F90 (280)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CPOMpoolS, 'POM_C_pool_sediment', 'g/m2', 'POM C pool in sediment')`
- Code: `call self%register_state_dependency(self%id_CPOMpoolS,          'POM_C_pool_sediment',    'g/m2',            'POM C pool in sediment')`

### `POM_C_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM C pool in sediment pelagic mirror
- Source: phytoplankton.F90 (284)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV', 'g/m2', 'POM C pool in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_CPOMpoolS_PV,       'POM_C_pool_sediment_PV', 'g/m2',            'POM C pool in sediment pelagic mirror')`

### `POM_C_pool_water` [g/m3] *Dependencies*
- DESC: POM C pool water
- Source: phytoplankton.F90 (269)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CPOMpoolW, 'POM_C_pool_water', 'g/m3', 'POM C pool water')`
- Code: `call self%register_state_dependency(self%id_CPOMpoolW,          'POM_C_pool_water',       'g/m3',            'POM C pool water')`

### `POM_DW_pool_sediment` [g/m2] *Dependencies*
- DESC: POM DW pool in sediment
- Source: phytoplankton.F90 (277)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DPOMpoolS, 'POM_DW_pool_sediment', 'g/m2', 'POM DW pool in sediment')`
- Code: `call self%register_state_dependency(self%id_DPOMpoolS,          'POM_DW_pool_sediment',   'g/m2',            'POM DW pool in sediment')`

### `POM_DW_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM DW pool in sediment pelagic mirror
- Source: phytoplankton.F90 (281)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV', 'g/m2', 'POM DW pool in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_DPOMpoolS_PV,       'POM_DW_pool_sediment_PV','g/m2',            'POM DW pool in sediment pelagic mirror')`

### `POM_DW_pool_water` [g/m3] *Dependencies*
- DESC: POM DW pool water
- Source: phytoplankton.F90 (266)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DPOMpoolW, 'POM_DW_pool_water', 'g/m3', 'POM DW pool water')`
- Code: `call self%register_state_dependency(self%id_DPOMpoolW,          'POM_DW_pool_water',      'g/m3',            'POM DW pool water')`

### `POM_N_pool_sediment` [g/m2] *Dependencies*
- DESC: POM N pool in sediment
- Source: phytoplankton.F90 (278)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NPOMpoolS, 'POM_N_pool_sediment', 'g/m2', 'POM N pool in sediment')`
- Code: `call self%register_state_dependency(self%id_NPOMpoolS,          'POM_N_pool_sediment',    'g/m2',            'POM N pool in sediment')`

### `POM_N_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM N pool in sediment pelagic mirror
- Source: phytoplankton.F90 (282)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV', 'g/m2', 'POM N pool in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_NPOMpoolS_PV,       'POM_N_pool_sediment_PV', 'g/m2',            'POM N pool in sediment pelagic mirror')`

### `POM_N_pool_water` [g/m3] *Dependencies*
- DESC: POM N pool water
- Source: phytoplankton.F90 (267)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NPOMpoolW, 'POM_N_pool_water', 'g/m3', 'POM N pool water')`
- Code: `call self%register_state_dependency(self%id_NPOMpoolW,          'POM_N_pool_water',       'g/m3',            'POM N pool water')`

### `POM_P_pool_sediment` [g/m2] *Dependencies*
- DESC: POM P pool in sediment
- Source: phytoplankton.F90 (279)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PPOMpoolS, 'POM_P_pool_sediment', 'g/m2', 'POM P pool in sediment')`
- Code: `call self%register_state_dependency(self%id_PPOMpoolS,          'POM_P_pool_sediment',    'g/m2',            'POM P pool in sediment')`

### `POM_P_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM P pool in sediment pelagic mirror
- Source: phytoplankton.F90 (283)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV', 'g/m2', 'POM P pool in sediment pelagic mirror')`
- Code: `call self%register_state_dependency(self%id_PPOMpoolS_PV,       'POM_P_pool_sediment_PV', 'g/m2',            'POM P pool in sediment pelagic mirror')`

### `POM_P_pool_water` [g/m3] *Dependencies*
- DESC: POM P pool water
- Source: phytoplankton.F90 (268)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PPOMpoolW, 'POM_P_pool_water', 'g/m3', 'POM P pool water')`
- Code: `call self%register_state_dependency(self%id_PPOMpoolW,          'POM_P_pool_water',       'g/m3',            'POM P pool water')`

### `SiO2_pool_sediment` [g/m2] *Dependencies*
- DESC: SiO2 in sediment
- Source: phytoplankton.F90 (296)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_SiO2poolS, 'SiO2_pool_sediment', 'g/m2', 'SiO2 in sediment')`
- Code: `call self%register_state_dependency(self%id_SiO2poolS,          'SiO2_pool_sediment',     'g/m2',            'SiO2 in sediment')`

### `SiO2_pool_water` [g/m3] *Dependencies*
- DESC: SiO2 pool water
- Source: phytoplankton.F90 (294)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_SiO2poolW, 'SiO2_pool_water', 'g/m3', 'SiO2 pool water')`
- Code: `call self%register_state_dependency(self%id_SiO2poolW,          'SiO2_pool_water',        'g/m3',            'SiO2 pool water')`

### `SiPa_pool_sediment` [g/m2] *Dependencies*
- DESC: SiPa pool in sediment
- Source: phytoplankton.F90 (295)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_SiPapoolS, 'SiPa_pool_sediment', 'g/m2', 'SiPa pool in sediment')`
- Code: `call self%register_state_dependency(self%id_SiPapoolS,          'SiPa_pool_sediment',     'g/m2',            'SiPa pool in sediment')`

### `SiPa_pool_water` [g/m3] *Dependencies*
- DESC: SiPa pool water
- Source: phytoplankton.F90 (293)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_SiPapoolW, 'SiPa_pool_water', 'g/m3', 'SiPa pool water')`
- Code: `call self%register_state_dependency(self%id_SiPapoolW,          'SiPa_pool_water',        'g/m3',            'SiPa pool water')`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: phytoplankton.F90 (303)
- Formula (d⁻¹): `call self%register_dependency(self%id_uTm, standard_variables%temperature)`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `dz` [-] *Dependencies*
- DESC: cell thickness
- Source: zooplankton.F90 (210)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_dz, standard_variables%cell_thickness)`

### `oxygen` [g/m3] *Dependencies*
- DESC: Oxygen pool water
- Source: zooplankton.F90 (212)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')`

### `par` [-] *Dependencies*
- DESC: downwelling photosynthetic radiative flux
- Source: zooplankton.F90 (213)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`

### `sDepthW` [-] *Dependencies*
- DESC: bottom depth
- Source: zooplankton.F90 (211)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_sDepthW, standard_variables%bottom_depth)`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: zooplankton.F90 (209)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `aDSubVeg` [gDW/m2] *Dependencies*
- DESC: total_aDSubVeg
- Source: zoobenthos.F90 (244)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: zoobenthos.F90 (243)
- Formula (d⁻¹): `-`
- Code: `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `pO2Sat` [pct] *Dependencies*
- DESC: oxygen saturation
- Source: zoobenthos.F90 (242)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_pO2Sat, 'pO2Sat', 'pct', 'oxygen saturation')`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: zoobenthos.F90 (241)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `aDayInitVeg` [d] *Dependencies*
- DESC: aDayInitVeg (dependency)
- Source: macrophytes.F90 (300)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_aDayInitVeg, 'aDayInitVeg', 'd', 'aDayInitVeg')`

### `aDayInitVeg_out` [d] *Dependencies*
- DESC: aDayInitVeg diagnostic output
- Source: macrophytes.F90 (299)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aDayInitVeg_out, 'aDayInitVeg', 'd', 'aDayInitVeg', output=output_instantaneous, missing_value=-1.0_rk, source=source_do)`

### `bPorS` [m3/m3] *Dependencies*
- DESC: sediment porosity
- Source: macrophytes.F90 (301)
- Formula (d⁻¹): `-`
- Code: `call self%register_horizontal_dependency(self%id_bPorS, 'bPorS', 'm3/m3', 'sediment porosity')`

### `cDepthS` [m] *Dependencies*
- DESC: sediment depth
- Source: macrophytes.F90 (302)
- Formula (d⁻¹): `-`
- Code: `call self%register_horizontal_dependency(self%id_cDepthS, 'cDepthS', 'm', 'sediment depth')`

### `Day` [-] *Dependencies*
- DESC: number of days since start of the year
- Source: macrophytes.F90 (306)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`

### `DOM_C_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM C in sediment
- Source: macrophytes.F90 (282)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CDOMpoolS, 'DOM_C_pool_sediment', 'g/m2', 'DOM C in sediment')`

### `DOM_C_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM C in sediment pelagic mirror
- Source: macrophytes.F90 (286)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CDOMpoolS_PV, 'DOM_C_pool_sediment_PV', 'g/m2', 'DOM C in sediment pelagic mirror')`

### `DOM_C_pool_water` [g/m3] *Dependencies*
- DESC: DOM C in water
- Source: macrophytes.F90 (278)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CDOMpoolW, 'DOM_C_pool_water', 'g/m3', 'DOM C in water')`

### `DOM_DW_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM DW in sediment
- Source: macrophytes.F90 (279)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DDOMpoolS, 'DOM_DW_pool_sediment', 'g/m2', 'DOM DW in sediment')`

### `DOM_DW_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM DW in sediment pelagic mirror
- Source: macrophytes.F90 (283)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DDOMpoolS_PV, 'DOM_DW_pool_sediment_PV', 'g/m2', 'DOM DW in sediment pelagic mirror')`

### `DOM_DW_pool_water` [g/m3] *Dependencies*
- DESC: DOM DW in water
- Source: macrophytes.F90 (275)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DDOMpoolW, 'DOM_DW_pool_water', 'g/m3', 'DOM DW in water')`

### `DOM_N_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM N in sediment
- Source: macrophytes.F90 (280)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NDOMpoolS, 'DOM_N_pool_sediment', 'g/m2', 'DOM N in sediment')`

### `DOM_N_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM N in sediment pelagic mirror
- Source: macrophytes.F90 (284)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NDOMpoolS_PV, 'DOM_N_pool_sediment_PV', 'g/m2', 'DOM N in sediment pelagic mirror')`

### `DOM_N_pool_water` [g/m3] *Dependencies*
- DESC: DOM N in water
- Source: macrophytes.F90 (276)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NDOMpoolW, 'DOM_N_pool_water', 'g/m3', 'DOM N in water')`

### `DOM_P_pool_sediment` [g/m2] *Dependencies*
- DESC: DOM P in sediment
- Source: macrophytes.F90 (281)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PDOMpoolS, 'DOM_P_pool_sediment', 'g/m2', 'DOM P in sediment')`

### `DOM_P_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: DOM P in sediment pelagic mirror
- Source: macrophytes.F90 (285)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PDOMpoolS_PV, 'DOM_P_pool_sediment_PV', 'g/m2', 'DOM P in sediment pelagic mirror')`

### `DOM_P_pool_water` [g/m3] *Dependencies*
- DESC: DOM P in water
- Source: macrophytes.F90 (277)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PDOMpoolW, 'DOM_P_pool_water', 'g/m3', 'DOM P in water')`

### `DW_macrophyte{nCompts}` [gDW/m2] *Dependencies*
- DESC: DW of macrophyte competitor n (loop nCompts)
- Source: macrophytes.F90 (292)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_Compts(i_mac), 'DW_macrophyte'//trim(index), 'gDW/m2', 'DW of macrophyte'//trim(index)); call self%request_coupling_to_model(self%id_Compts(i_mac), self%id_Compt_Models(i_mac), 'sD')`

### `dz` [-] *Dependencies*
- DESC: cell thickness
- Source: macrophytes.F90 (309)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_dz, standard_variables%cell_thickness)`

### `extc` [-] *Dependencies*
- DESC: attenuation coefficient of photosynthetic radiative flux
- Source: macrophytes.F90 (305)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_extc, standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)`

### `lat` [-] *Dependencies*
- DESC: latitude
- Source: macrophytes.F90 (308)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_lat, standard_variables%latitude)`

### `macrophyte_competitor{nCompts}` [-] *Dependencies*
- DESC: model dependency for competitor n (loop nCompts)
- Source: macrophytes.F90 (293)
- Formula (d⁻¹): `-`
- Code: `call self%register_model_dependency(self%id_Compt_Models(i_mac), 'macrophyte_competitor'//trim(index))`

### `meanpar` [-] *Dependencies*
- DESC: temporal mean of par (period=86400s, resolution=3600s)
- Source: macrophytes.F90 (311)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_meanpar, temporal_mean(self%id_par, period=86400._rk, resolution=3600._rk, missing_value=0.0_rk))`

### `NH4_pool_sediment` [g/m2] *Dependencies*
- DESC: NH4 pool for nutrient uptake
- Source: macrophytes.F90 (263)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NH4poolS, 'NH4_pool_sediment', 'g/m2', 'NH4 pool for nutrient uptake')`

### `NH4_pool_water` [g/m3] *Dependencies*
- DESC: NH4 pool for nutrient uptake
- Source: macrophytes.F90 (254)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NH4poolW, 'NH4_pool_water', 'g/m3', 'NH4 pool for nutrient uptake')`

### `NO3_pool_sediment` [g/m2] *Dependencies*
- DESC: NO3 pool for nutrient uptake
- Source: macrophytes.F90 (264)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NO3poolS, 'NO3_pool_sediment', 'g/m2', 'NO3 pool for nutrient uptake')`

### `NO3_pool_water` [g/m3] *Dependencies*
- DESC: NO3 pool for nutrient uptake
- Source: macrophytes.F90 (255)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NO3poolW, 'NO3_pool_water', 'g/m3', 'NO3 pool for nutrient uptake')`

### `oxic_layer_fraction` [-] *Dependencies*
- DESC: oxic layer fraction
- Source: macrophytes.F90 (298)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_afOxySed, 'oxic_layer_fraction', '-', 'oxic layer fraction')`

### `oxygen_pool_water` [g/m3] *Dependencies*
- DESC: oxygen pool in water
- Source: macrophytes.F90 (257)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_O2poolW, 'oxygen_pool_water', 'g/m3', 'oxygen pool in water')`

### `par` [-] *Dependencies*
- DESC: downwelling photosynthetic radiative flux
- Source: macrophytes.F90 (310)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`

### `PO4_pool_sediment` [g/m2] *Dependencies*
- DESC: PO4 pool for nutrient uptake
- Source: macrophytes.F90 (265)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PO4poolS, 'PO4_pool_sediment', 'g/m2', 'PO4 pool for nutrient uptake')`

### `PO4_pool_water` [g/m3] *Dependencies*
- DESC: PO4 pool for nutrient uptake
- Source: macrophytes.F90 (256)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PO4poolW, 'PO4_pool_water', 'g/m3', 'PO4 pool for nutrient uptake')`

### `POM_C_pool_sediment` [g/m2] *Dependencies*
- DESC: POM C pool sediment
- Source: macrophytes.F90 (269)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CPOMpoolS, 'POM_C_pool_sediment', 'g/m2', 'POM C pool sediment')`

### `POM_C_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM C pool sediment pelagic mirror
- Source: macrophytes.F90 (273)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV', 'g/m2', 'POM C pool sediment pelagic mirror')`

### `POM_C_pool_water` [g/m3] *Dependencies*
- DESC: POM C pool in water
- Source: macrophytes.F90 (262)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_CPOMpoolW, 'POM_C_pool_water', 'g/m3', 'POM C pool in water')`

### `POM_DW_pool_sediment` [g/m2] *Dependencies*
- DESC: POM DW pool sediment
- Source: macrophytes.F90 (266)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DPOMpoolS, 'POM_DW_pool_sediment', 'g/m2', 'POM DW pool sediment')`

### `POM_DW_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM DW pool sediment pelagic mirror
- Source: macrophytes.F90 (270)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV', 'g/m2', 'POM DW pool sediment pelagic mirror')`

### `POM_DW_pool_water` [g/m3] *Dependencies*
- DESC: POM DW pool in water
- Source: macrophytes.F90 (259)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_DPOMpoolW, 'POM_DW_pool_water', 'g/m3', 'POM DW pool in water')`

### `POM_N_pool_sediment` [g/m2] *Dependencies*
- DESC: POM N pool sediment
- Source: macrophytes.F90 (267)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NPOMpoolS, 'POM_N_pool_sediment', 'g/m2', 'POM N pool sediment')`

### `POM_N_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM N pool sediment pelagic mirror
- Source: macrophytes.F90 (271)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV', 'g/m2', 'POM N pool sediment pelagic mirror')`

### `POM_N_pool_water` [g/m3] *Dependencies*
- DESC: POM N pool in water
- Source: macrophytes.F90 (260)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_NPOMpoolW, 'POM_N_pool_water', 'g/m3', 'POM N pool in water')`

### `POM_P_pool_sediment` [g/m2] *Dependencies*
- DESC: POM P pool sediment
- Source: macrophytes.F90 (268)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PPOMpoolS, 'POM_P_pool_sediment', 'g/m2', 'POM P pool sediment')`

### `POM_P_pool_sediment_PV` [g/m2] *Dependencies*
- DESC: POM P pool sediment pelagic mirror
- Source: macrophytes.F90 (272)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV', 'g/m2', 'POM P pool sediment pelagic mirror')`

### `POM_P_pool_water` [g/m3] *Dependencies*
- DESC: POM P pool in water
- Source: macrophytes.F90 (261)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_PPOMpoolW, 'POM_P_pool_water', 'g/m3', 'POM P pool in water')`

### `sDepthW` [-] *Dependencies*
- DESC: bottom depth
- Source: macrophytes.F90 (307)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_sDepthW, standard_variables%bottom_depth)`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: macrophytes.F90 (304)
- Formula (d⁻¹): `-`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `aCovVeg` [%] *Dependencies*
- DESC: macrophyte cover percentage
- Source: fish.F90 (459)
- Formula (d⁻¹): `call self%register_dependency(self%id_aCovVeg,type_bulk_standard_variable(name='total_aCovVeg',units='%'))`
- Code: `call self%register_dependency(self%id_aCovVeg,type_bulk_standard_variable(name='total_aCovVeg',units='%'))`

### `aDSubVeg` [gDW/m2] *Dependencies*
- DESC: macrophyte biomass
- Source: fish.F90 (460)
- Formula (d⁻¹): `call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))`
- Code: `call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))`

### `aTotFish` [g/m3] *Dependencies*
- DESC: total fish DW aggregate
- Source: fish.F90 (461)
- Formula (d⁻¹): `call self%register_dependency(self%id_aTotFish,type_bulk_standard_variable(name='wet_fish_totD',units='g/m3'))`
- Code: `call self%register_dependency(self%id_aTotFish,type_bulk_standard_variable(name='wet_fish_totD', units='g/m3'))`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: fish.F90 (456)
- Formula (d⁻¹): `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`
- Code: `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `CDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM C in water
- Source: fish.F90 (235)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CDOMpoolW,'DOM_C_pool_water','g/m3','DOM C in water')`
- Code: `call self%register_state_dependency(self%id_CDOMpoolW, 'DOM_C_pool_water', 'g/m3', 'DOM C in water')`

### `CPOMpoolW` [g/m3] *Dependencies*
- DESC: POM C pool in water
- Source: fish.F90 (229)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_CPOMpoolW,'POM_C_pool_water','g/m3','POM C pool in water')`
- Code: `call self%register_state_dependency(self%id_CPOMpoolW, 'POM_C_pool_water', 'g/m3', 'POM C pool in water')`

### `Day` [-] *Dependencies*
- DESC: number of days since start of year
- Source: fish.F90 (455)
- Formula (d⁻¹): `call self%register_dependency(self%id_Day,standard_variables%number_of_days_since_start_of_the_year)`
- Code: `call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`

### `DDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM DW in water
- Source: fish.F90 (232)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DDOMpoolW,'DOM_DW_pool_water','g/m3','DOM DW in water')`
- Code: `call self%register_state_dependency(self%id_DDOMpoolW, 'DOM_DW_pool_water', 'g/m3', 'DOM DW in water')`

### `DPOMpoolW` [g/m3] *Dependencies*
- DESC: POM DW pool in water
- Source: fish.F90 (226)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DPOMpoolW,'POM_DW_pool_water','g/m3','POM DW pool in water')`
- Code: `call self%register_state_dependency(self%id_DPOMpoolW, 'POM_DW_pool_water', 'g/m3', 'POM DW pool in water')`

### `NDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM N in water
- Source: fish.F90 (233)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NDOMpoolW,'DOM_N_pool_water','g/m3','DOM N in water')`
- Code: `call self%register_state_dependency(self%id_NDOMpoolW, 'DOM_N_pool_water', 'g/m3', 'DOM N in water')`

### `NH4poolW` [g/m3] *Dependencies*
- DESC: NH4 pool in water
- Source: fish.F90 (230)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NH4poolW,'NH4_pool_water','g/m3','NH4 pool in water')`
- Code: `call self%register_state_dependency(self%id_NH4poolW, 'NH4_pool_water', 'g/m3', 'NH4 pool in water')`

### `NPOMpoolW` [g/m3] *Dependencies*
- DESC: POM N pool in water
- Source: fish.F90 (227)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NPOMpoolW,'POM_N_pool_water','g/m3','POM N pool in water')`
- Code: `call self%register_state_dependency(self%id_NPOMpoolW, 'POM_N_pool_water', 'g/m3', 'POM N pool in water')`

### `oxygen` [g/m3] *Dependencies*
- DESC: Oxygen pool water
- Source: fish.F90 (457)
- Formula (d⁻¹): `call self%register_dependency(self%id_oxygen,'oxygen_pool_water','g/m3','Oxygen pool water')`
- Code: `call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')`

### `par` [-] *Dependencies*
- DESC: downwelling photosynthetic radiative flux
- Source: fish.F90 (458)
- Formula (d⁻¹): `call self%register_dependency(self%id_par,standard_variables%downwelling_photosynthetic_radiative_flux)`
- Code: `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`

### `PDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM P in water
- Source: fish.F90 (234)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PDOMpoolW,'DOM_P_pool_water','g/m3','DOM P in water')`
- Code: `call self%register_state_dependency(self%id_PDOMpoolW, 'DOM_P_pool_water', 'g/m3', 'DOM P in water')`

### `PO4poolW` [g/m3] *Dependencies*
- DESC: PO4 pool in water
- Source: fish.F90 (231)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PO4poolW,'PO4_pool_water','g/m3','PO4 pool in water')`
- Code: `call self%register_state_dependency(self%id_PO4poolW, 'PO4_pool_water', 'g/m3', 'PO4 pool in water')`

### `PPOMpoolW` [g/m3] *Dependencies*
- DESC: POM P pool in water
- Source: fish.F90 (228)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PPOMpoolW,'POM_P_pool_water','g/m3','POM P pool in water')`
- Code: `call self%register_state_dependency(self%id_PPOMpoolW, 'POM_P_pool_water', 'g/m3', 'POM P pool in water')`

### `pred_sms` [-] *Dependencies*
- DESC: predation rate
- Source: fish.F90 (219)
- Formula (d⁻¹): `call self%register_dependency(self%id_pred_sms,'pred_sms','-','predation rate')`
- Code: `call self%register_dependency(self%id_pred_sms, 'pred_sms', '-', 'predation rate')`

### `uTm` [-] *Dependencies*
- DESC: temperature
- Source: fish.F90 (454)
- Formula (d⁻¹): `call self%register_dependency(self%id_uTm,standard_variables%temperature)`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `aCovVeg` [%] *Dependencies*
- DESC: macrophyte cover percentage (bulk)
- Source: fish_pclake.F90 (343)
- Formula (d⁻¹): `call self%register_dependency(self%id_aCovVeg,type_bulk_standard_variable(name='total_aCovVeg',units='%'))`
- Code: `call self%register_dependency(self%id_aCovVeg, type_bulk_standard_variable(name='total_aCovVeg', units='%'))`

### `aDSubVeg` [gDW/m2] *Dependencies*
- DESC: macrophyte biomass (bulk)
- Source: fish_pclake.F90 (344)
- Formula (d⁻¹): `call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))`
- Code: `call self%register_dependency(self%id_aDSubVeg, type_bulk_standard_variable(name='total_aDSubVeg', units='gDW/m2'))`

### `BioTurb` [gDW/m3/d] *Dependencies*
- DESC: Bioturbation diagnostic
- Source: fish_pclake.F90 (204)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_BioTurb,'Bioturbation','gDW/m3/d','Bioturbation')`
- Code: `call self%register_diagnostic_variable(self%id_BioTurb, 'Bioturbation', 'gDW/m3/d', 'Bioturbation')`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: fish_pclake.F90 (340)
- Formula (d⁻¹): `call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`
- Code: `call self%register_horizontal_dependency(self%id_bot_pel_conv, 'bot_pel_conv', '-', 'bottom/pelagic conversion factor')`

### `Day` [-] *Dependencies*
- DESC: simulation day (global dependency)
- Source: fish_pclake.F90 (339)
- Formula (d⁻¹): `call self%register_dependency(self%id_Day,standard_variables%number_of_days_since_start_of_the_year)`
- Code: `call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`

### `DDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM DW in water
- Source: fish_pclake.F90 (175)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DDOMpoolW,'DOM_DW_pool_water','g/m3','DOM DW in water')`
- Code: `call self%register_state_dependency(self%id_DDOMpoolW, 'DOM_DW_pool_water', 'g/m3', 'DOM DW in water')`

### `DPOMpoolW` [g/m3] *Dependencies*
- DESC: POM DW pool in water
- Source: fish_pclake.F90 (170)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_DPOMpoolW,'POM_DW_pool_water','g/m3','POM DW pool in water')`
- Code: `call self%register_state_dependency(self%id_DPOMpoolW, 'POM_DW_pool_water', 'g/m3', 'POM DW pool in water')`

### `NDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM N in water
- Source: fish_pclake.F90 (176)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NDOMpoolW,'DOM_N_pool_water','g/m3','DOM N in water')`
- Code: `call self%register_state_dependency(self%id_NDOMpoolW, 'DOM_N_pool_water', 'g/m3', 'DOM N in water')`

### `NH4poolW` [g/m3] *Dependencies*
- DESC: NH4 pool in water
- Source: fish_pclake.F90 (173)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NH4poolW,'NH4_pool_water','g/m3','NH4 pool in water')`
- Code: `call self%register_state_dependency(self%id_NH4poolW, 'NH4_pool_water', 'g/m3', 'NH4 pool in water')`

### `NPOMpoolW` [g/m3] *Dependencies*
- DESC: POM N pool in water
- Source: fish_pclake.F90 (171)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_NPOMpoolW,'POM_N_pool_water','g/m3','POM N pool in water')`
- Code: `call self%register_state_dependency(self%id_NPOMpoolW, 'POM_N_pool_water', 'g/m3', 'POM N pool in water')`

### `oxygen` [g/m3] *Dependencies*
- DESC: Oxygen pool water
- Source: fish_pclake.F90 (341)
- Formula (d⁻¹): `call self%register_dependency(self%id_oxygen,'oxygen_pool_water','g/m3','Oxygen pool water')`
- Code: `call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')`

### `par` [-] *Dependencies*
- DESC: downwelling photosynthetic radiative flux
- Source: fish_pclake.F90 (342)
- Formula (d⁻¹): `call self%register_dependency(self%id_par,standard_variables%downwelling_photosynthetic_radiative_flux)`
- Code: `call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)`

### `PDOMpoolW` [g/m3] *Dependencies*
- DESC: DOM P in water
- Source: fish_pclake.F90 (177)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PDOMpoolW,'DOM_P_pool_water','g/m3','DOM P in water')`
- Code: `call self%register_state_dependency(self%id_PDOMpoolW, 'DOM_P_pool_water', 'g/m3', 'DOM P in water')`

### `PO4poolW` [g/m3] *Dependencies*
- DESC: PO4 pool in water
- Source: fish_pclake.F90 (174)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PO4poolW,'PO4_pool_water','g/m3','PO4 pool in water')`
- Code: `call self%register_state_dependency(self%id_PO4poolW, 'PO4_pool_water', 'g/m3', 'PO4 pool in water')`

### `PPOMpoolW` [g/m3] *Dependencies*
- DESC: POM P pool in water
- Source: fish_pclake.F90 (172)
- Formula (d⁻¹): `call self%register_state_dependency(self%id_PPOMpoolW,'POM_P_pool_water','g/m3','POM P pool in water')`
- Code: `call self%register_state_dependency(self%id_PPOMpoolW, 'POM_P_pool_water', 'g/m3', 'POM P pool in water')`

### `uTm` [-] *Dependencies*
- DESC: local temperature (env. dependency)
- Source: fish_pclake.F90 (338)
- Formula (d⁻¹): `call self%register_dependency(self%id_uTm,standard_variables%temperature)`
- Code: `call self%register_dependency(self%id_uTm, standard_variables%temperature)`

### `BioTurb` [gDW/m3/d] *Dependencies*
- DESC: total bioturbation
- Source: sediment_exchange.F90 (282)
- Formula (d⁻¹): `register_dependency id_BioTurb`
- Code: `register_dependency(self%id_BioTurb,type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d'))`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: sediment_exchange.F90 (284)
- Formula (d⁻¹): `register_horizontal_dependency id_bot_pel_conv`
- Code: `register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `bPorCorS` [m3/m3] *Dependencies*
- DESC: sediment porosity corrected for tortuosity
- Source: sediment_exchange.F90 (279)
- Formula (d⁻¹): `register_horizontal_dependency id_bPorCorS`
- Code: `register_horizontal_dependency(self%id_bPorCorS, 'bPorCorS', 'm3/m3','sediment porosity corrected for tortuosity')`

### `bPorS` [m3/m3] *Dependencies*
- DESC: sediment porosity
- Source: sediment_exchange.F90 (278)
- Formula (d⁻¹): `register_horizontal_dependency id_bPorS`
- Code: `register_horizontal_dependency(self%id_bPorS, 'bPorS', 'm3/m3','sediment porosity')`

### `cDepthS` [m] *Dependencies*
- DESC: sediment depth
- Source: sediment_exchange.F90 (280)
- Formula (d⁻¹): `register_horizontal_dependency id_cDepthS`
- Code: `register_horizontal_dependency(self%id_cDepthS, 'cDepthS', 'm', 'sediment depth')`

### `depth` [-] *Dependencies*
- DESC: bottom depth (standard variable)
- Source: sediment_exchange.F90 (276)
- Formula (d⁻¹): `register_dependency id_depth = standard_variables%bottom_depth`
- Code: `register_dependency(self%id_depth,standard_variables%bottom_depth)`

### `DragVeg` [gDW/m2] *Dependencies*
- DESC: total macrophyte biomass
- Source: sediment_exchange.F90 (283)
- Formula (d⁻¹): `register_dependency id_DragVeg`
- Code: `register_dependency(self%id_DragVeg,type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2'))`

### `fDepthDifS` [-] *Dependencies*
- DESC: nutrient diffusion distance as fraction of sediment depth
- Source: sediment_exchange.F90 (281)
- Formula (d⁻¹): `register_horizontal_dependency id_fDepthDifS`
- Code: `register_horizontal_dependency(self%id_fDepthDifS, 'fDepthDifS', '-', 'nutrient diffusion distance as fraction of sediment depth')`

### `shear` [-] *Dependencies*
- DESC: bottom stress (standard variable)
- Source: sediment_exchange.F90 (274)
- Formula (d⁻¹): `register_dependency id_shear = standard_variables%bottom_stress`
- Code: `register_dependency(self%id_shear,standard_variables%bottom_stress)`

### `uTm` [-] *Dependencies*
- DESC: temperature (standard variable)
- Source: sediment_exchange.F90 (275)
- Formula (d⁻¹): `register_dependency id_uTm = standard_variables%temperature`
- Code: `register_dependency(self%id_uTm,standard_variables%temperature)`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bot_pel_conv bulk standard variable (if hypsograph)
- Source: bot_pel_interface.F90 (53)
- Formula (d⁻¹): `register_dependency id_bot_pel_conv = type_bulk_standard_variable(name='bot_pel_conv',units='-')`
- Code: `register_dependency(self%id_bot_pel_conv, type_bulk_standard_variable(name='bot_pel_conv',units='-'))`

### `dz` [-] *Dependencies*
- DESC: cell thickness (standard variable)
- Source: bot_pel_interface.F90 (51)
- Formula (d⁻¹): `register_dependency id_dz = standard_variables%cell_thickness`
- Code: `register_dependency(self%id_dz, standard_variables%cell_thickness)`

### `BioTurb` [gDW/m3/d] *Dependencies*
- DESC: total bioturbation
- Source: resus_sed.F90 (112)
- Formula (d⁻¹): `register_dependency id_BioTurb`
- Code: `register_dependency(self%id_BioTurb,type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d'))`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: resus_sed.F90 (114)
- Formula (d⁻¹): `register_horizontal_dependency id_bot_pel_conv`
- Code: `register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `bPorS` [m3/m3] *Dependencies*
- DESC: sediment porosity
- Source: resus_sed.F90 (111)
- Formula (d⁻¹): `register_horizontal_dependency id_bPorS`
- Code: `register_horizontal_dependency(self%id_bPorS, 'bPorS', 'm3/m3','sediment porosity')`

### `depth` [-] *Dependencies*
- DESC: bottom depth (standard variable)
- Source: resus_sed.F90 (109)
- Formula (d⁻¹): `register_dependency id_depth = standard_variables%bottom_depth`
- Code: `register_dependency(self%id_depth,standard_variables%bottom_depth)`

### `DragVeg` [gDW/m2] *Dependencies*
- DESC: total macrophyte biomass
- Source: resus_sed.F90 (113)
- Formula (d⁻¹): `register_dependency id_DragVeg`
- Code: `register_dependency(self%id_DragVeg,type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2'))`

### `shear` [-] *Dependencies*
- DESC: bottom stress (standard variable)
- Source: resus_sed.F90 (107)
- Formula (d⁻¹): `register_dependency id_shear = standard_variables%bottom_stress`
- Code: `register_dependency(self%id_shear,standard_variables%bottom_stress)`

### `uTm` [-] *Dependencies*
- DESC: temperature (standard variable)
- Source: resus_sed.F90 (108)
- Formula (d⁻¹): `register_dependency id_uTm = standard_variables%temperature`
- Code: `register_dependency(self%id_uTm,standard_variables%temperature)`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: burial.F90 (209)
- Formula (d⁻¹): `register_horizontal_dependency id_bot_pel_conv`
- Code: `register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')`

### `bPorS` [m3/m3] *Dependencies*
- DESC: sediment porosity
- Source: burial.F90 (99)
- Formula (d⁻¹): `register_horizontal_dependency id_bPorS`
- Code: `register_horizontal_dependency(self%id_bPorS, 'bPorS', 'm3/m3', 'sediment porosity')`

### `cDepthS` [m] *Dependencies*
- DESC: sediment depth
- Source: burial.F90 (100)
- Formula (d⁻¹): `register_horizontal_dependency id_cDepthS`
- Code: `register_horizontal_dependency(self%id_cDepthS, 'cDepthS', 'm', 'sediment depth')`

### `tDAbioIMS` [g/m2/s] *Dependencies*
- DESC: IM abiotic update (from sediment_exchange)
- Source: burial.F90 (98)
- Formula (d⁻¹): `register_dependency id_tDAbioIMS`
- Code: `register_dependency(self%id_tDAbioIMS, 'IM_abiotic_update', 'g/m2/s', 'IM abiotic update')`

### `tDPOMS_Phyt/tDPOMS_Bent/tDPOMS_Macro/tDPOMS_POM/tDReSedPOMS` [g/m2/s] *Dependencies*
- DESC: POM update from various sources
- Source: burial.F90 (135-177)
- Formula (d⁻¹): `register_horizontal_dependency id_tDPOMS_*`
- Code: `register_horizontal_dependency(self%id_tDPOMS_Phyt(i_spec), 'POM_phytoplankton_update'//trim(index),'g/m2/s','POM phytoplankton update'//trim(index))`

### `BivSt_D` [g/m2] *Dependencies*
- DESC: other not-coupled stages sharing carrying capacity (dim nKShares)
- Source: bivalves.F90 (138)
- Formula (d⁻¹): `register_state_dependency id_BivSt_D`
- Code: `register_state_dependency(self%id_BivSt_D(i_stage), 'otherStage'//trim(index), 'g/m2', 'otherStage'//trim(index))`

### `bot_pel_conv` [-] *Dependencies*
- DESC: bottom/pelagic conversion factor
- Source: bivalves.F90 (261)
- Formula (d⁻¹): `register_horizontal_dependency id_bot_pel_conv`
- Code: `register_horizontal_dependency(self%id_bot_pel_conv, 'bot_pel_conv', '-', 'bottom/pelagic conversion factor')`

### `CPOMpoolS` [g/m2] *Dependencies*
- DESC: POM C pool in sediment
- Source: bivalves.F90 (241)
- Formula (d⁻¹): `register_state_dependency id_CPOMpoolS`
- Code: `register_state_dependency(self%id_CPOMpoolS, 'POM_C_pool_sediment', 'g/m2', 'particulate organic matter C pool in sediment')`

### `CPOMpoolS_PV` [g/m2] *Dependencies*
- DESC: POM C pool sediment pelagic mirror
- Source: bivalves.F90 (243)
- Formula (d⁻¹): `register_state_dependency id_CPOMpoolS_PV`
- Code: `register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV', 'g/m2', 'particulate organic matter C pool in sediment pelagic mirror')`

### `CPOMpoolW` [g/m3] *Dependencies*
- DESC: POM C pool in water
- Source: bivalves.F90 (251)
- Formula (d⁻¹): `register_state_dependency id_CPOMpoolW`
- Code: `register_state_dependency(self%id_CPOMpoolW, 'POM_C_pool_water', 'g/m3', 'POM C pool in water')`

### `Day` [-] *Dependencies*
- DESC: day of year (standard variable)
- Source: bivalves.F90 (260)
- Formula (d⁻¹): `register_dependency id_Day`
- Code: `register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)`

### `DPOMpoolS` [g/m2] *Dependencies*
- DESC: POM DW pool in sediment
- Source: bivalves.F90 (238)
- Formula (d⁻¹): `register_state_dependency id_DPOMpoolS`
- Code: `register_state_dependency(self%id_DPOMpoolS, 'POM_DW_pool_sediment', 'g/m2', 'particulate organic matter DW pool in sediment')`

### `DPOMpoolS_PV` [g/m2] *Dependencies*
- DESC: POM DW pool sediment pelagic mirror
- Source: bivalves.F90 (242)
- Formula (d⁻¹): `register_state_dependency id_DPOMpoolS_PV`
- Code: `register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV', 'g/m2', 'particulate organic matter DW pool in sediment pelagic mirror')`

### `DPOMpoolW` [g/m3] *Dependencies*
- DESC: POM DW pool in water
- Source: bivalves.F90 (248)
- Formula (d⁻¹): `register_state_dependency id_DPOMpoolW`
- Code: `register_state_dependency(self%id_DPOMpoolW, 'POM_DW_pool_water', 'g/m3', 'POM DW pool in water')`

### `NH4poolW` [g/m3] *Dependencies*
- DESC: NH4 pool in water
- Source: bivalves.F90 (253)
- Formula (d⁻¹): `register_state_dependency id_NH4poolW`
- Code: `register_state_dependency(self%id_NH4poolW, 'NH4_pool_water', 'g/m3', 'NH4 pool in water')`

### `NPOMpoolS` [g/m2] *Dependencies*
- DESC: POM N pool in sediment
- Source: bivalves.F90 (240)
- Formula (d⁻¹): `register_state_dependency id_NPOMpoolS`
- Code: `register_state_dependency(self%id_NPOMpoolS, 'POM_N_pool_sediment', 'g/m2', 'particulate organic matter N pool in sediment')`

### `NPOMpoolS_PV` [g/m2] *Dependencies*
- DESC: POM N pool sediment pelagic mirror
- Source: bivalves.F90 (245)
- Formula (d⁻¹): `register_state_dependency id_NPOMpoolS_PV`
- Code: `register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV', 'g/m2', 'particulate organic matter N pool in sediment pelagic mirror')`

### `NPOMpoolW` [g/m3] *Dependencies*
- DESC: POM N pool in water
- Source: bivalves.F90 (249)
- Formula (d⁻¹): `register_state_dependency id_NPOMpoolW`
- Code: `register_state_dependency(self%id_NPOMpoolW, 'POM_N_pool_water', 'g/m3', 'POM N pool in water')`

### `oxygen` [g/m3] *Dependencies*
- DESC: oxygen pool water
- Source: bivalves.F90 (258)
- Formula (d⁻¹): `register_dependency id_oxygen`
- Code: `register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')`

### `PO4poolW` [g/m3] *Dependencies*
- DESC: PO4 pool in water
- Source: bivalves.F90 (254)
- Formula (d⁻¹): `register_state_dependency id_PO4poolW`
- Code: `register_state_dependency(self%id_PO4poolW, 'PO4_pool_water', 'g/m3', 'PO4 pool in water')`

### `PPOMpoolS` [g/m2] *Dependencies*
- DESC: POM P pool in sediment
- Source: bivalves.F90 (239)
- Formula (d⁻¹): `register_state_dependency id_PPOMpoolS`
- Code: `register_state_dependency(self%id_PPOMpoolS, 'POM_P_pool_sediment', 'g/m2', 'particulate organic matter P pool in sediment')`

### `PPOMpoolS_PV` [g/m2] *Dependencies*
- DESC: POM P pool sediment pelagic mirror
- Source: bivalves.F90 (244)
- Formula (d⁻¹): `register_state_dependency id_PPOMpoolS_PV`
- Code: `register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV', 'g/m2', 'particulate organic matter P pool in sediment pelagic mirror')`

### `PPOMpoolW` [g/m3] *Dependencies*
- DESC: POM P pool in water
- Source: bivalves.F90 (250)
- Formula (d⁻¹): `register_state_dependency id_PPOMpoolW`
- Code: `register_state_dependency(self%id_PPOMpoolW, 'POM_P_pool_water', 'g/m3', 'POM P pool in water')`

### `PreyD/N/P/C` [g/m3] *Dependencies*
- DESC: prey DW/N/P/C per type (dim nPrey)
- Source: bivalves.F90 (216-219)
- Formula (d⁻¹): `register_state_dependency id_Prey*`
- Code: `register_state_dependency(self%id_PreyD(i_prey), 'Prey_D_'//trim(index), 'g/m3', 'prey D'//trim(index))`

### `PreySi` [g/m3] *Dependencies*
- DESC: prey silica per type (if lSi=true)
- Source: bivalves.F90 (226)
- Formula (d⁻¹): `register_dependency id_PreySi`
- Code: `register_dependency(self%id_PreySi(i_prey), 'Prey_Si_'//trim(index), 'g/m3', 'prey Si'//trim(index))`

### `sDIMW` [g/m3] *Dependencies*
- DESC: inorganic matter
- Source: bivalves.F90 (259)
- Formula (d⁻¹): `register_dependency id_sDIMW`
- Code: `register_dependency(self%id_sDIMW, 'sDIMW', 'g/m3', 'inorganic matter')`

### `SiPapoolS` [g/m2] *Dependencies*
- DESC: particulate Si pool sediment
- Source: bivalves.F90 (246)
- Formula (d⁻¹): `register_state_dependency id_SiPapoolS`
- Code: `register_state_dependency(self%id_SiPapoolS, 'SiPa_pool_sediment', 'g/m2', 'particulate Si pool sediment')`

### `uTm` [-] *Dependencies*
- DESC: temperature (standard variable)
- Source: bivalves.F90 (257)
- Formula (d⁻¹): `register_dependency id_uTm`
- Code: `register_dependency(self%id_uTm, standard_variables%temperature)`

## Derivatives

### `sDIMW` [-] *Derivatives*
- DESC: ODE for inorganic matter
- Source: abiotic_water.F90 (247-247)
- Formula (d⁻¹): `wDAbioIMW`
- Code: `_SET_ODE_(self%id_sDIMW,wDAbioIMW)`

### `sNH4W` [-] *Derivatives*
- DESC: ODE for ammonium
- Source: abiotic_water.F90 (250-250)
- Formula (d⁻¹): `wNAbioNH4W`
- Code: `_SET_ODE_(self%id_sNH4W,wNAbioNH4W)`

### `sNO3W` [-] *Derivatives*
- DESC: ODE for nitrate
- Source: abiotic_water.F90 (251-251)
- Formula (d⁻¹): `wNAbioNO3W`
- Code: `_SET_ODE_(self%id_sNO3W,wNAbioNO3W)`

### `sO2W` [-] *Derivatives*
- DESC: ODE for oxygen
- Source: abiotic_water.F90 (253-253)
- Formula (d⁻¹): `wO2AbioW`
- Code: `_SET_ODE_(self%id_sO2W,wO2AbioW)`

### `sPAIMW` [-] *Derivatives*
- DESC: ODE for IM-adsorbed P
- Source: abiotic_water.F90 (249-249)
- Formula (d⁻¹): `wPAbioAIMW`
- Code: `_SET_ODE_(self%id_sPAIMW,wPAbioAIMW)`

### `sPO4W` [-] *Derivatives*
- DESC: ODE for phosphate
- Source: abiotic_water.F90 (248-248)
- Formula (d⁻¹): `wPAbioPO4W`
- Code: `_SET_ODE_(self%id_sPO4W,wPAbioPO4W)`

### `sSiO2W` [-] *Derivatives*
- DESC: ODE for silica dioxide
- Source: abiotic_water.F90 (252-252)
- Formula (d⁻¹): `wSiAbioSiO2W`
- Code: `_SET_ODE_(self%id_sSiO2W,wSiAbioSiO2W)`

### `sSiPaW` [-] *Derivatives*
- DESC: ODE for particulate Si
- Source: abiotic_water.F90 (254-254)
- Formula (d⁻¹): `wSiAbioPaW`
- Code: `_SET_ODE_(self%id_sSiPaW,wSiAbioPaW)`

### `sDIMS` [-] *Derivatives*
- DESC: bottom ODE for inorganic matter
- Source: abiotic_sediment.F90 (304-304)
- Formula (d⁻¹): `tDAbioIMS`
- Code: `_SET_BOTTOM_ODE_(self%id_sDIMS,tDAbioIMS)`

### `sNH4S` [-] *Derivatives*
- DESC: bottom ODE for ammonium
- Source: abiotic_sediment.F90 (306-306)
- Formula (d⁻¹): `tNAbioNH4S`
- Code: `_SET_BOTTOM_ODE_(self%id_sNH4S,tNAbioNH4S)`

### `sNO3S` [-] *Derivatives*
- DESC: bottom ODE for nitrate
- Source: abiotic_sediment.F90 (307-307)
- Formula (d⁻¹): `tNAbioNO3S`
- Code: `_SET_BOTTOM_ODE_(self%id_sNO3S,tNAbioNO3S)`

### `sPAIMS` [-] *Derivatives*
- DESC: bottom ODE for absorbed phosphate
- Source: abiotic_sediment.F90 (309-309)
- Formula (d⁻¹): `tPAbioAIMS`
- Code: `_SET_BOTTOM_ODE_(self%id_sPAIMS,tPAbioAIMS)`

### `sPO4S` [-] *Derivatives*
- DESC: bottom ODE for phosphate
- Source: abiotic_sediment.F90 (308-308)
- Formula (d⁻¹): `tPAbioPO4S`
- Code: `_SET_BOTTOM_ODE_(self%id_sPO4S,tPAbioPO4S)`

### `sSiO2S` [-] *Derivatives*
- DESC: bottom ODE for dissolved SiO2
- Source: abiotic_sediment.F90 (310-310)
- Formula (d⁻¹): `tSiO2AbioS`
- Code: `_SET_BOTTOM_ODE_(self%id_sSiO2S,tSiO2AbioS)`

### `sSiPaS` [-] *Derivatives*
- DESC: bottom ODE for particulate Si
- Source: abiotic_sediment.F90 (305-305)
- Formula (d⁻¹): `tSiAbioPaS`
- Code: `_SET_BOTTOM_ODE_(self%id_sSiPaS,tSiAbioPaS)`

### `CRefrS` [-] *Derivatives*
- DESC: ODE for C refractory target
- Source: om_pool.F90 (500)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CRefrS, tCRefr)`
- Code: `_SET_BOTTOM_ODE_(self%id_CRefrS,             tCRefr)`

### `CTransS` [-] *Derivatives*
- DESC: ODE for C bio-transformation target
- Source: om_pool.F90 (486)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CTransS, tCTrans)`
- Code: `_SET_BOTTOM_ODE_(self%id_CTransS,            tCTrans)`

### `CTransW` [-] *Derivatives*
- DESC: ODE for C bio-transformation target
- Source: om_pool.F90 (358)
- Formula (d⁻¹): `_SET_ODE_(self%id_CTransW,wCMin)`
- Code: `_SET_ODE_(self%id_CTransW,wCMin)`

### `DRefrS` [-] *Derivatives*
- DESC: ODE for DW refractory target
- Source: om_pool.F90 (497)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DRefrS, tDRefr)`
- Code: `_SET_BOTTOM_ODE_(self%id_DRefrS,             tDRefr)`

### `DTransS` [-] *Derivatives*
- DESC: ODE for DW bio-transformation target
- Source: om_pool.F90 (485)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DTransS, tDTrans)`
- Code: `_SET_BOTTOM_ODE_(self%id_DTransS,            tDTrans)`

### `DTransW` [-] *Derivatives*
- DESC: ODE for DW bio-transformation target
- Source: om_pool.F90 (357)
- Formula (d⁻¹): `_SET_ODE_(self%id_DTransW,wDMin)`
- Code: `_SET_ODE_(self%id_DTransW,wDMin)`

### `NO3poolW` [-] *Derivatives*
- DESC: ODE for NO3 pool
- Source: om_pool.F90 (363)
- Formula (d⁻¹): `_SET_ODE_(self%id_NO3poolW,-wNDenitW)`
- Code: `_SET_ODE_(self%id_NO3poolW,-wNDenitW)`

### `NRefrS` [-] *Derivatives*
- DESC: ODE for N refractory target
- Source: om_pool.F90 (498)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NRefrS, tNRefr)`
- Code: `_SET_BOTTOM_ODE_(self%id_NRefrS,             tNRefr)`

### `NTransS` [-] *Derivatives*
- DESC: ODE for N bio-transformation target
- Source: om_pool.F90 (488)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NTransS, tNTrans)`
- Code: `_SET_BOTTOM_ODE_(self%id_NTransS,                tNTrans)`

### `NTransW` [-] *Derivatives*
- DESC: ODE for N bio-transformation target
- Source: om_pool.F90 (360)
- Formula (d⁻¹): `_SET_ODE_(self%id_NTransW,wNMin)`
- Code: `_SET_ODE_(self%id_NTransW,wNMin)`

### `O2poolW` [-] *Derivatives*
- DESC: ODE for oxygen pool
- Source: om_pool.F90 (362)
- Formula (d⁻¹): `_SET_ODE_(self%id_O2poolW,-wO2Min)`
- Code: `_SET_ODE_(self%id_O2poolW,-wO2Min)`

### `PRefrS` [-] *Derivatives*
- DESC: ODE for P refractory target
- Source: om_pool.F90 (499)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PRefrS, tPRefr)`
- Code: `_SET_BOTTOM_ODE_(self%id_PRefrS,             tPRefr)`

### `PTransS` [-] *Derivatives*
- DESC: ODE for P bio-transformation target
- Source: om_pool.F90 (489)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PTransS, tPTrans)`
- Code: `_SET_BOTTOM_ODE_(self%id_PTransS,                tPTrans)`

### `PTransW` [-] *Derivatives*
- DESC: ODE for P bio-transformation target
- Source: om_pool.F90 (361)
- Formula (d⁻¹): `_SET_ODE_(self%id_PTransW,wPMin)`
- Code: `_SET_ODE_(self%id_PTransW,wPMin)`

### `sCW` [-] *Derivatives*
- DESC: ODE for water column C
- Source: om_pool.F90 (344)
- Formula (d⁻¹): `_SET_ODE_(self%id_sCW,-wCMin)`
- Code: `_SET_ODE_(self%id_sCW,-wCMin)`

### `sDW` [-] *Derivatives*
- DESC: ODE for water column DW
- Source: om_pool.F90 (341)
- Formula (d⁻¹): `_SET_ODE_(self%id_sDW,-wDMin)`
- Code: `_SET_ODE_(self%id_sDW,-wDMin)`

### `sNW` [-] *Derivatives*
- DESC: ODE for water column N
- Source: om_pool.F90 (342)
- Formula (d⁻¹): `_SET_ODE_(self%id_sNW,-wNMin)`
- Code: `_SET_ODE_(self%id_sNW,-wNMin)`

### `sPW` [-] *Derivatives*
- DESC: ODE for water column P
- Source: om_pool.F90 (343)
- Formula (d⁻¹): `_SET_ODE_(self%id_sPW,-wPMin)`
- Code: `_SET_ODE_(self%id_sPW,-wPMin)`

### `tCS` [-] *Derivatives*
- DESC: final ROC in C
- Source: om_pool.F90 (449)
- Formula (d⁻¹): `tCS = -tCMin`
- Code: `tCS = -tCMin`

### `tDS` [-] *Derivatives*
- DESC: final ROC in DW
- Source: om_pool.F90 (446)
- Formula (d⁻¹): `tDS = -tDMin`
- Code: `tDS = -tDMin`

### `tNS` [-] *Derivatives*
- DESC: final ROC in N
- Source: om_pool.F90 (447)
- Formula (d⁻¹): `tNS = -tNMin`
- Code: `tNS = -tNMin`

### `tPS` [-] *Derivatives*
- DESC: final ROC in P
- Source: om_pool.F90 (448)
- Formula (d⁻¹): `tPS = -tPMin`
- Code: `tPS = -tPMin`

### `wCZoo` [gC/m3/s] *Derivatives*
- DESC: calculate final rate of change of C
- Source: zooplankton.F90 (357)
- Formula (d⁻¹): `wCAssZoo - wCRespZoo - wCMortZoo`
- Code: `wCZoo = wCAssZoo - wCRespZoo - wCMortZoo`

### `wDZoo` [gDW/m3/s] *Derivatives*
- DESC: calculate final rate of change of DW
- Source: zooplankton.F90 (354)
- Formula (d⁻¹): `wDAssZoo - wDRespZoo - wDMortZoo`
- Code: `wDZoo = wDAssZoo - wDRespZoo - wDMortZoo`

### `wNZoo` [gN/m3/s] *Derivatives*
- DESC: calculate final rate of change of N
- Source: zooplankton.F90 (355)
- Formula (d⁻¹): `wNAssZoo - wNExcrZoo - wNMortZoo`
- Code: `wNZoo = wNAssZoo - wNExcrZoo - wNMortZoo`

### `wPZoo` [gP/m3/s] *Derivatives*
- DESC: calculate final rate of change of P
- Source: zooplankton.F90 (356)
- Formula (d⁻¹): `wPAssZoo - wPExcrZoo - wPMortZoo`
- Code: `wPZoo = wPAssZoo - wPExcrZoo - wPMortZoo`

### `tCBenBent` [gC/m2/s] *Derivatives*
- DESC: calculate final rate of change of C
- Source: zoobenthos.F90 (400)
- Formula (d⁻¹): `tCMigrBent + tCAssBent - tCRespBent - tCMortBent`
- Code: `tCBenBent = tCMigrBent + tCAssBent - tCRespBent - tCMortBent`

### `tDBenBent` [gDW/m2/s] *Derivatives*
- DESC: calculate final rate of change of DW
- Source: zoobenthos.F90 (397)
- Formula (d⁻¹): `tDMigrBent + tDAssBent - tDRespBent - tDMortBent`
- Code: `tDBenBent = tDMigrBent + tDAssBent - tDRespBent - tDMortBent`

### `tNBenBent` [gN/m2/s] *Derivatives*
- DESC: calculate final rate of change of N
- Source: zoobenthos.F90 (399)
- Formula (d⁻¹): `tNMigrBent + tNAssBent - tNExcrBent - tNMortBent`
- Code: `tNBenBent = tNMigrBent + tNAssBent - tNExcrBent - tNMortBent`

### `tPBenBent` [gP/m2/s] *Derivatives*
- DESC: calculate final rate of change of P
- Source: zoobenthos.F90 (398)
- Formula (d⁻¹): `tPMigrBent + tPAssBent - tPExcrBent - tPMortBent`
- Code: `tPBenBent = tPMigrBent + tPAssBent - tPExcrBent - tPMortBent`

### `tCFi` [-] *Derivatives*
- DESC: calculate the final rate of change in C
- Source: fish.F90 (921)
- Formula (d⁻¹): `tCFi = tCMigrFi + tCAssFiTot - tCRespFi - tCMortFi - tCAgeFish`
- Code: `tCFi = tCMigrFi + tCAssFiTot - tCRespFi - tCMortFi - tCAgeFish`

### `tDFi` [-] *Derivatives*
- DESC: calculate the final rate of change in DW
- Source: fish.F90 (918)
- Formula (d⁻¹): `tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish`
- Code: `tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish`

### `tNFi` [-] *Derivatives*
- DESC: calculate the final rate of change in N
- Source: fish.F90 (920)
- Formula (d⁻¹): `tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish`
- Code: `tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish`

### `tPFi` [-] *Derivatives*
- DESC: calculate the final rate of change in P
- Source: fish.F90 (919)
- Formula (d⁻¹): `tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish`
- Code: `tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish`

## Diagnostic variables

### `aCovVegdummy` [%] *Diagnostic variables*
- DESC: dummy aCovVeg
- Source: abiotic_water.F90 (137-137)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aCovVegdummy, 'aCovVegdummy', '%', 'dummy aCovVeg', output=output_none)`

### `aCovVegdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (265-265)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_aCovVegdummy,0.0_rk)`

### `aDSubVegdummy` [gDW/m2] *Diagnostic variables*
- DESC: dummy aDSubVeg
- Source: abiotic_water.F90 (135-135)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aDSubVegdummy, 'aDSubVegdummy', 'gDW/m2', 'dummy aDSubVeg', output=output_none)`

### `aDSubVegdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (266-266)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_aDSubVegdummy,0.0_rk)`

### `afCovSurfVegdummy` [-] *Diagnostic variables*
- DESC: dummy afCovSurfVeg
- Source: abiotic_water.F90 (140-140)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_afCovSurfVegdummy, 'afCovSurfVegdummy', '-', 'dummy afCovSurfVeg', output=output_none)`

### `afCovSurfVegdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (267-267)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_afCovSurfVegdummy,0.0_rk)`

### `BTdummy` [gDW/m2/d] *Diagnostic variables*
- DESC: bioturbation dummy
- Source: abiotic_water.F90 (130-130)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_BTdummy, 'BTdummy', 'gDW/m2/d', 'bioturbation dummy', output=output_none)`

### `BTdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (263-263)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_BTdummy,0.0_rk)`

### `chladummy` [ug/L] *Diagnostic variables*
- DESC: dummy chlorophyl a
- Source: abiotic_water.F90 (143-143)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_chladummy, 'chladummy', 'ug/L', 'dummy chlorophyl a', output=output_none)`

### `chladummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (264-264)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_chladummy,0.0_rk)`

### `extIM` [-] *Diagnostic variables*
- DESC: extIM
- Source: abiotic_water.F90 (110-110)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_extIM, 'extIM', '-', 'extIM', output=output_instantaneous)`

### `pO2Sat` [pct] *Diagnostic variables*
- DESC: oxygen saturation
- Source: abiotic_water.F90 (114-114)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_pO2Sat, 'pO2Sat', 'pct', 'oxygen saturation', output=output_instantaneous)`

### `pO2Sat` [pct] *Diagnostic variables*
- DESC: set diagnostic pO2Sat
- Source: abiotic_water.F90 (258-258)
- Formula (d⁻¹): `pO2Sat`
- Code: `_SET_DIAGNOSTIC_(self%id_pO2Sat,pO2Sat)`

### `TMdummy` [gDW/m2] *Diagnostic variables*
- DESC: total macrophyte dummy
- Source: abiotic_water.F90 (132-132)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_TMdummy, 'TMdummy', 'gDW/m2', 'total macrophyte dummy', output=output_none)`

### `TMdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_water.F90 (262-262)
- Formula (d⁻¹): `0.0`
- Code: `_SET_DIAGNOSTIC_(self%id_TMdummy,0.0_rk)`

### `tO2Aer` [g/m2/s] *Diagnostic variables*
- DESC: O2_reareation
- Source: abiotic_water.F90 (112-112)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2Aer, 'tO2Aer', 'g/m2/s', 'O2_reareation', output=output_instantaneous, source=source_do_surface)`

### `wind` [m/s] *Diagnostic variables*
- DESC: windspeed
- Source: abiotic_water.F90 (109-109)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wind, 'wind', 'm/s', 'windspeed', output=output_instantaneous, source=source_do_surface)`

### `wNNitrW` [g/m3/s] *Diagnostic variables*
- DESC: rate nitrification
- Source: abiotic_water.F90 (118-118)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNNitrW, 'wNNitrW', 'g/m3/s', 'rate nitrification', output=output_instantaneous)`

### `wO2NitrW` [g/m3/s] *Diagnostic variables*
- DESC: rate O2 cons. by nitrification
- Source: abiotic_water.F90 (120-120)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wO2NitrW, 'wO2NitrW', 'g/m3/s', 'rate O2 cons. by nitrification', output=output_instantaneous)`

### `wPSorpIMW` [g/m3/s] *Diagnostic variables*
- DESC: rate P adsorped
- Source: abiotic_water.F90 (117-117)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPSorpIMW, 'wPSorpIMW', 'g/m3/s', 'rate P adsorped', output=output_instantaneous)`

### `wSiMinPaW` [g/m3/s] *Diagnostic variables*
- DESC: rate Si particulate mineralization
- Source: abiotic_water.F90 (116-116)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wSiMinPaW, 'wSiMinPaW', 'g/m3/s', 'rate Si particulate mineralization', output=output_instantaneous)`

### `afOxySed` [-] *Diagnostic variables*
- DESC: fraction of aerobic sediment
- Source: abiotic_sediment.F90 (120-120)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_afOxySed, 'afOxySed', '-', 'fraction of aerobic sediment', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `afOxySed` [-] *Diagnostic variables*
- DESC: set diagnostic fraction aerobic sediment
- Source: abiotic_sediment.F90 (320-320)
- Formula (d⁻¹): `afOxySed`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_afOxySed,afOxySed)`

### `aPEqIMS` [-] *Diagnostic variables*
- DESC: equilibrium adsorbed PO4
- Source: abiotic_sediment.F90 (121-121)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aPEqIMS, 'aPEqIMS', '-', 'equilibrium adsorbed PO4', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `aPEqIMS` [-] *Diagnostic variables*
- DESC: set diagnostic equilibrium adsorbed PO4
- Source: abiotic_sediment.F90 (321-321)
- Formula (d⁻¹): `aPEqIMS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_aPEqIMS,aPEqIMS)`

### `bot_pel_conv` [-] *Diagnostic variables*
- DESC: current conversion between m-2 and m-3
- Source: abiotic_sediment.F90 (146-146)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_bot_pel_conv_out, 'bot_pel_conv', '-', 'current conversion between m-2 and m-3', output=output_none, domain=domain_bottom, source=source_do_bottom)`

### `bPorCorS` [m3/m3] *Diagnostic variables*
- DESC: sediment porosity corrected for tortuosity
- Source: abiotic_sediment.F90 (126-126)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_bPorCorS, 'bPorCorS', 'm3/m3', 'sediment porosity corrected for tortuosity', output=output_none, domain=domain_bottom, missing_value=self%bPorCorS, source=source_do_bottom)`

### `bPorS` [m3/m3] *Diagnostic variables*
- DESC: sediment porosity
- Source: abiotic_sediment.F90 (125-125)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_bPorS, 'bPorS', 'm3/m3', 'sediment porosity', output=output_none, domain=domain_bottom, missing_value=self%bPorS, source=source_do_bottom)`

### `cDepthS` [m] *Diagnostic variables*
- DESC: sediment depth
- Source: abiotic_sediment.F90 (127-127)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_cDepthS, 'cDepthS', 'm', 'sediment depth', output=output_none, domain=domain_bottom, missing_value=self%cDepthS, source=source_do_bottom)`

### `fDepthDifS` [m] *Diagnostic variables*
- DESC: diffusion distance as fraction of sediment depth
- Source: abiotic_sediment.F90 (128-128)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_fDepthDifS, 'fDepthDifS', 'm', 'diffusion distance as fraction of sediment depth', output=output_none, domain=domain_bottom, missing_value=self%fDepthDifS, source=source_do_bottom)`

### `fPEqIMS` [-] *Diagnostic variables*
- DESC: fraction of PAIMS in equilibrium
- Source: abiotic_sediment.F90 (154-154)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_fPEqIMS, 'fPEqIMS', '-', 'fraction of PAIMS in equilibrium', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `fPEqIMS` [-] *Diagnostic variables*
- DESC: diagnostic output fraction of PAIMS in equilibrium
- Source: abiotic_sediment.F90 (341-341)
- Formula (d⁻¹): `fPEqIMS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_fPEqIMS, fPEqIMS)`

### `tDAbioIMS` [g/m2/s] *Diagnostic variables*
- DESC: IM ROC
- Source: abiotic_sediment.F90 (123-123)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDAbioIMS, 'tDAbioIMS', 'g/m2/s', 'IM ROC', output=output_none, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioIMS` [-] *Diagnostic variables*
- DESC: set diagnostic IM ROC
- Source: abiotic_sediment.F90 (325-325)
- Formula (d⁻¹): `tDAbioIMS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioIMS,tDAbioIMS)`

### `tDAbioO2S` [g/m2/d] *Diagnostic variables*
- DESC: O2 consumption
- Source: abiotic_sediment.F90 (122-122)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDAbioO2S, 'tDAbioO2S', 'g/m2/d', 'O2 consumption', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioO2S` [g/m2/d] *Diagnostic variables*
- DESC: set diagnostic O2 consumption
- Source: abiotic_sediment.F90 (326-326)
- Formula (d⁻¹): `(-tO2MinTOMS - tO2NitrS)`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioO2S,(-tO2MinTOMS - tO2NitrS)*secs_pr_day)`

### `tDPOMdummy` [gDW/m2] *Diagnostic variables*
- DESC: dummy total sediment POM increase from biology
- Source: abiotic_sediment.F90 (129-129)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDPOMdummy, 'tDPOMdummy', 'gDW/m2', 'dummy total sediment POM increase from biology', domain=domain_bottom, source=source_do_bottom)`

### `tDPOMdummy` [-] *Diagnostic variables*
- DESC: set dummy diagnostic
- Source: abiotic_sediment.F90 (331-331)
- Formula (d⁻¹): `0.0`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDPOMdummy,0.0_rk)`

### `tNDenitS` [g/m2/s] *Diagnostic variables*
- DESC: rate denitrification
- Source: abiotic_sediment.F90 (152-152)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNDenitS, 'tNDenitS', 'g/m2/s', 'rate denitrification', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNNitrS` [g/m2/s] *Diagnostic variables*
- DESC: rate nitrification
- Source: abiotic_sediment.F90 (151-151)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNNitrS, 'tNNitrS', 'g/m2/s', 'rate nitrification', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPChemPO4` [g/m2/s] *Diagnostic variables*
- DESC: rate chem. loss of diss. P from pore water
- Source: abiotic_sediment.F90 (149-149)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPChemPO4, 'tPChemPO4', 'g/m2/s', 'rate chem. loss of diss. P from pore water', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPSorpIMS` [g/m2/s] *Diagnostic variables*
- DESC: rate P sorped to IM
- Source: abiotic_sediment.F90 (150-150)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPSorpIMS, 'tPSorpIMS', 'g/m2/s', 'rate P sorped to IM', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tSiMinPaS` [g/m2/s] *Diagnostic variables*
- DESC: rate Si particulate mineralization
- Source: abiotic_sediment.F90 (153-153)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tSiMinPaS, 'tSiMinPaS', 'g/m2/s', 'rate Si particulate mineralization', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `extinction` [-] *Diagnostic variables*
- DESC: extinction
- Source: om_pool.F90 (156)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_ext, 'extinction', '-', 'extinction', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_ext,             'extinction',     '-',     'extinction',                     output=output_instantaneous,source=source_do                           )`

### `rCDS` [-] *Diagnostic variables*
- DESC: C/D ratio sediment
- Source: om_pool.F90 (159)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rCDS, 'rCDS', '-', 'C/D ratio sediment', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rCDS,            'rCDS',           '-',     'C/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `rCDW` [-] *Diagnostic variables*
- DESC: C/D ratio water
- Source: om_pool.F90 (154)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rCDW, 'rCDW', '-', 'C/D ratio water', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rCDW,            'rCDW',           '-',     'C/D ratio water',                output=output_instantaneous,source=source_do                           )`

### `rNDS` [-] *Diagnostic variables*
- DESC: N/D ratio sediment
- Source: om_pool.F90 (158)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rNDS, 'rNDS', '-', 'N/D ratio sediment', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rNDS,            'rNDS',           '-',     'N/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `rNDW` [-] *Diagnostic variables*
- DESC: N/D ratio water
- Source: om_pool.F90 (153)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rNDW, 'rNDW', '-', 'N/D ratio water', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rNDW,            'rNDW',           '-',     'N/D ratio water',                output=output_instantaneous,source=source_do                           )`

### `rPDS` [-] *Diagnostic variables*
- DESC: P/D ratio sediment
- Source: om_pool.F90 (157)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rPDS, 'rPDS', '-', 'P/D ratio sediment', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rPDS,            'rPDS',           '-',     'P/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `rPDW` [-] *Diagnostic variables*
- DESC: P/D ratio water
- Source: om_pool.F90 (152)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rPDW, 'rPDW', '-', 'P/D ratio water', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rPDW,            'rPDW',           '-',     'P/D ratio water',                output=output_instantaneous,source=source_do                           )`

### `tCMin` [g/m2/s] *Diagnostic variables*
- DESC: rate C biotransform. in sediment
- Source: om_pool.F90 (179)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCMin, 'tCMin', 'g/m2/s', 'rate C biotransform. in sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCMin,       'tCMin',          'g/m2/s',  'rate C biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCRefr` [g/m2/s] *Diagnostic variables*
- DESC: rate C refraction
- Source: om_pool.F90 (187)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCRefr, 'tCRefr', 'g/m2/s', 'rate C refraction', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCRefr,   'tCRefr',         'g/m2/s',  'rate C refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCRefr_PV` [g/m3/s] *Diagnostic variables*
- DESC: rate C refraction pelagic mirror
- Source: om_pool.F90 (192)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCRefr_PV, 'tCRefr_PV', 'g/m3/s', 'rate C refraction pelagic mirror', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tCRefr_PV, 'tCRefr_PV',  'g/m3/s',  'rate C refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )`

### `tCTrans` [g/m2/s] *Diagnostic variables*
- DESC: rate C biotrans. minus refraction
- Source: om_pool.F90 (166)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCTrans, 'tCTrans', 'g/m2/s', 'rate C biotrans. minus refraction', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCTrans,         'tCTrans',        'g/m2/s','rate C biotrans. minus refraction',    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDMin` [g/m2/s] *Diagnostic variables*
- DESC: rate DW biotransform. in sediment
- Source: om_pool.F90 (176)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDMin, 'tDMin', 'g/m2/s', 'rate DW biotransform. in sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDMin,       'tDMin',          'g/m2/s',  'rate DW biotransform. in sediment',  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDPOMS` [g/m2/s] *Diagnostic variables*
- DESC: ROC DW OM pool in sediment
- Source: om_pool.F90 (161)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDPOMS, 'tDPOMS', 'g/m2/s', 'ROC DW OM pool in sediment', output=output_instantaneous,source=source_do_bottom, domain=domain_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDPOMS,          'tDPOMS',         'g/m2/s','ROC DW OM pool in sediment',           output=output_instantaneous,source=source_do_bottom, domain=domain_bottom)`

### `tDRefr` [g/m2/s] *Diagnostic variables*
- DESC: rate DW refraction
- Source: om_pool.F90 (184)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDRefr, 'tDRefr', 'g/m2/s', 'rate DW refraction', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDRefr,   'tDRefr',         'g/m2/s',  'rate DW refraction',                 output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDRefr_PV` [g/m3/s] *Diagnostic variables*
- DESC: rate DW refraction pelagic mirror
- Source: om_pool.F90 (189)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDRefr_PV, 'tDRefr_PV', 'g/m3/s', 'rate DW refraction pelagic mirror', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tDRefr_PV, 'tDRefr_PV',  'g/m3/s',  'rate DW refraction pelagic mirror',  output=output_instantaneous,source=source_do                    )`

### `tDTrans` [g/m2/s] *Diagnostic variables*
- DESC: rate DW biotrans. minus refraction
- Source: om_pool.F90 (165)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDTrans, 'tDTrans', 'g/m2/s', 'rate DW biotrans. minus refraction', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDTrans,         'tDTrans',        'g/m2/s','rate DW biotrans. minus refraction',   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNMin` [g/m2/s] *Diagnostic variables*
- DESC: rate N biotransform. in sediment
- Source: om_pool.F90 (177)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNMin, 'tNMin', 'g/m2/s', 'rate N biotransform. in sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNMin,       'tNMin',          'g/m2/s',  'rate N biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNRefr` [g/m2/s] *Diagnostic variables*
- DESC: rate N refraction
- Source: om_pool.F90 (185)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNRefr, 'tNRefr', 'g/m2/s', 'rate N refraction', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNRefr,   'tNRefr',         'g/m2/s',  'rate N refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNRefr_PV` [g/m3/s] *Diagnostic variables*
- DESC: rate N refraction pelagic mirror
- Source: om_pool.F90 (190)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNRefr_PV, 'tNRefr_PV', 'g/m3/s', 'rate N refraction pelagic mirror', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tNRefr_PV, 'tNRefr_PV',  'g/m3/s',  'rate N refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )`

### `tNTrans` [g/m2/s] *Diagnostic variables*
- DESC: rate N biotrans. minus refraction
- Source: om_pool.F90 (181)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNTrans, 'tNTrans', 'g/m2/s', 'rate N biotrans. minus refraction', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tNTrans,     'tNTrans',        'g/m2/s',  'rate N biotrans. minus refraction',  output=output_instantaneous,source=source_do                    )`

### `tPMin` [g/m2/s] *Diagnostic variables*
- DESC: rate P biotransform. in sediment
- Source: om_pool.F90 (178)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPMin, 'tPMin', 'g/m2/s', 'rate P biotransform. in sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPMin,       'tPMin',          'g/m2/s',  'rate P biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPRefr` [g/m2/s] *Diagnostic variables*
- DESC: rate P refraction
- Source: om_pool.F90 (186)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPRefr, 'tPRefr', 'g/m2/s', 'rate P refraction', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPRefr,   'tPRefr',         'g/m2/s',  'rate P refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPRefr_PV` [g/m3/s] *Diagnostic variables*
- DESC: rate P refraction pelagic mirror
- Source: om_pool.F90 (191)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPRefr_PV, 'tPRefr_PV', 'g/m3/s', 'rate P refraction pelagic mirror', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tPRefr_PV, 'tPRefr_PV',  'g/m3/s',  'rate P refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )`

### `tPTrans` [g/m2/s] *Diagnostic variables*
- DESC: rate P biotrans. minus refraction
- Source: om_pool.F90 (182)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPTrans, 'tPTrans', 'g/m2/s', 'rate P biotrans. minus refraction', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_tPTrans,     'tPTrans',        'g/m2/s',  'rate P biotrans. minus refraction',  output=output_instantaneous,source=source_do                    )`

### `wCMin` [-] *Diagnostic variables*
- DESC: C bio-transformation in water
- Source: om_pool.F90 (155)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wCMin, 'wCMin', '-', 'C bio-transformation in water', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wCMin,           'wCMin',          '-',     'C bio-transformation in water',  output=output_instantaneous,source=source_do                           )`

### `wDMin` [g/m3/s] *Diagnostic variables*
- DESC: rate D OM bio-transform. in water
- Source: om_pool.F90 (169)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wDMin, 'wDMin', 'g/m3/s', 'rate D OM bio-transform. in water', output=output_instantaneous)`
- Code: `call self%register_diagnostic_variable(self%id_wDMin,       'wDMin',          'g/m3/s',  'rate D OM bio-transform. in water',  output=output_instantaneous                                     )`

### `wNDenitW` [g/m3/s] *Diagnostic variables*
- DESC: rate denitrification in water
- Source: om_pool.F90 (172)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNDenitW, 'wNDenitW', 'g/m3/s', 'rate denitrification in water', output=output_instantaneous)`
- Code: `call self%register_diagnostic_variable(self%id_wNDenitW,    'wNDenitW',       'g/m3/s',  'rate denitrification in water',      output=output_instantaneous                                     )`

### `wNMin` [g/m3/s] *Diagnostic variables*
- DESC: rate N OM bio-transform. in water
- Source: om_pool.F90 (170)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNMin, 'wNMin', 'g/m3/s', 'rate N OM bio-transform. in water', output=output_instantaneous)`
- Code: `call self%register_diagnostic_variable(self%id_wNMin,       'wNMin',          'g/m3/s',  'rate N OM bio-transform. in water',  output=output_instantaneous                                     )`

### `wO2Min` [g/m3/s] *Diagnostic variables*
- DESC: rate O2 cons. by OM biotransformation in water
- Source: om_pool.F90 (173)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wO2Min, 'wO2Min', 'g/m3/s', 'rate O2 cons. by OM biotransformation in water', output=output_instantaneous)`
- Code: `call self%register_diagnostic_variable(self%id_wO2Min,      'wO2Min',         'g/m3/s',  'rate O2 cons. by OM biotransformation in water',  output=output_instantaneous                        )`

### `wPMin` [g/m3/s] *Diagnostic variables*
- DESC: rate P OM bio-transform. in water
- Source: om_pool.F90 (171)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPMin, 'wPMin', 'g/m3/s', 'rate P OM bio-transform. in water', output=output_instantaneous)`
- Code: `call self%register_diagnostic_variable(self%id_wPMin,       'wPMin',          'g/m3/s',  'rate P OM bio-transform. in water',  output=output_instantaneous                                     )`

### `aLLim` [-] *Diagnostic variables*
- DESC: light limitation factor
- Source: phytoplankton.F90 (189)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_aLLim, 'aLLim', '-', 'light limitation factor', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_aLLim,           'aLLim',          '-',     'light limitation factor',              output=output_instantaneous,source=source_do                   )`

### `aNLim` [-] *Diagnostic variables*
- DESC: N limitation factor
- Source: phytoplankton.F90 (193)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_aNLim, 'aNLim', '-', 'N limitation factor', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_aNLim,           'aNLim',          '-',     'N limitation factor',                  output=output_instantaneous,source=source_do                   )`

### `aNutLim` [-] *Diagnostic variables*
- DESC: nutrient limitation factor
- Source: phytoplankton.F90 (191)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_aNutLim, 'aNutLim', '-', 'nutrient limitation factor', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_aNutLim,         'aNutLim',        '-',     'nutrient limitation factor',           output=output_instantaneous,source=source_do                   )`

### `aPLim` [-] *Diagnostic variables*
- DESC: P limitation factor
- Source: phytoplankton.F90 (192)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_aPLim, 'aPLim', '-', 'P limitation factor', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_aPLim,           'aPLim',          '-',     'P limitation factor',                  output=output_instantaneous,source=source_do                   )`

### `ext` [-] *Diagnostic variables*
- DESC: phytoextinction factor
- Source: phytoplankton.F90 (184)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_ext, 'ext', '-', 'phytoextinction factor', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_ext,             'ext',            '-',     'phytoextinction factor',               output=output_instantaneous,source=source_do )`

### `extinction` [-] *Diagnostic variables*
- DESC: extinction
- Source: phytoplankton.F90 (185)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_phytoextinction, 'extinction', '-', 'extinction', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_phytoextinction, 'extinction',     '-',     'extinction',                           output=output_instantaneous,source=source_do                   )`

### `meanparout` [W] *Diagnostic variables*
- DESC: mean par for light
- Source: phytoplankton.F90 (227)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_meanparout, 'meanparout', 'W', 'mean par for light', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_meanparout,  'meanparout',     'W',     'mean par for light',                   output=output_instantaneous,source=source_do          )`

### `oChla` [mg/m3] *Diagnostic variables*
- DESC: chlorophyll a
- Source: phytoplankton.F90 (180)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_oChla, 'oChla', 'mg/m3', 'chlorophyll a', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_oChla,           'oChla',          'mg/m3', 'chlorophyll a',                        output=output_instantaneous,source=source_do                   )`

### `oSiS` [g/m2/s] *Diagnostic variables*
- DESC: oSiS
- Source: phytoplankton.F90 (178)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_oSiS, 'oSiS', 'g/m2/s', 'oSiS', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_oSiS,         'oSiS',           'g/m2/s','oSiS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )`

### `oSiW` [g/m3] *Diagnostic variables*
- DESC: Si
- Source: phytoplankton.F90 (177)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_oSiW, 'oSiW', 'g/m3 ', 'Si', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_oSiW,         'oSiW',           'g/m3 ', 'Si',                                   output=output_instantaneous,source=source_do                   )`

### `rCDS` [-] *Diagnostic variables*
- DESC: rCDS
- Source: phytoplankton.F90 (188)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rCDS, 'rCDS', '-', 'rCDS', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rCDS,            'rCDS',           '-',     'rCDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )`

### `rCDW` [-] *Diagnostic variables*
- DESC: C/D ratio
- Source: phytoplankton.F90 (183)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rCDW, 'rCDW', '-', 'C/D ratio', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rCDW,            'rCDW',           '-',     'C/D ratio',                            output=output_instantaneous,source=source_do                   )`

### `rNDS` [-] *Diagnostic variables*
- DESC: rNDS
- Source: phytoplankton.F90 (187)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rNDS, 'rNDS', '-', 'rNDS', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rNDS,            'rNDS',           '-',     'rNDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )`

### `rNDW` [-] *Diagnostic variables*
- DESC: N/D ratio
- Source: phytoplankton.F90 (182)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rNDW, 'rNDW', '-', 'N/D ratio', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rNDW,            'rNDW',           '-',     'N/D ratio',                            output=output_instantaneous,source=source_do                   )`

### `rPDS` [-] *Diagnostic variables*
- DESC: rPDS
- Source: phytoplankton.F90 (186)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rPDS, 'rPDS', '-', 'rPDS', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_rPDS,            'rPDS',           '-',     'rPDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )`

### `rPDW` [-] *Diagnostic variables*
- DESC: P/D ratio
- Source: phytoplankton.F90 (181)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_rPDW, 'rPDW', '-', 'P/D ratio', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_rPDW,            'rPDW',           '-',     'P/D ratio',                            output=output_instantaneous,source=source_do                   )`

### `Swim` [m/s] *Diagnostic variables*
- DESC: rate Swim speed
- Source: phytoplankton.F90 (197)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_Swim, 'Swim', 'm/s', 'rate Swim speed', output=output_instantaneous,source=source_get_vertical_movement)`
- Code: `call self%register_diagnostic_variable(self%id_Swim,            'Swim',           'm/s',   'rate Swim speed',                      output=output_instantaneous,source=source_get_vertical_movement)`

### `tCDOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate CDOMS from mortality
- Source: phytoplankton.F90 (245)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCDOMS, 'tCDOMS', 'g/m3/s', 'rate CDOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCDOMS,      'tCDOMS',         'g/m3/s','rate CDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tCPOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate CPOMS from mortality
- Source: phytoplankton.F90 (244)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCPOMS, 'tCPOMS', 'g/m3/s', 'rate CPOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCPOMS,      'tCPOMS',         'g/m3/s','rate CPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tCRespS` [g/m3/s] *Diagnostic variables*
- DESC: rate CO2 respired
- Source: phytoplankton.F90 (243)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tCRespS, 'tCRespS', 'g/m3/s', 'rate CO2 respired', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tCRespS,     'tCRespS',        'g/m3/s','rate CO2 respired',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tDDOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate DDOMS from mortality
- Source: phytoplankton.F90 (234)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDDOMS, 'tDDOMS', 'g/m3/s', 'rate DDOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDDOMS,      'tDDOMS',         'g/m3/s','rate DDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tDPOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate DPOMS from mortality
- Source: phytoplankton.F90 (196)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDPOMS, 'tDPOMS', 'g/m3/s', 'rate DPOMS from mortality', output=output_instantaneous,source=source_do_bottom, domain=domain_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDPOMS,          'tDPOMS',         'g/m3/s','rate DPOMS from mortality',            output=output_instantaneous,source=source_do_bottom, domain=domain_bottom            )`

### `tDResus` [g/m3/s] *Diagnostic variables*
- DESC: rate DW resuspension
- Source: phytoplankton.F90 (231)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDResus, 'tDResus', 'g/m3/s', 'rate DW resuspension', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDResus,     'tDResus',        'g/m3/s','rate DW resuspension',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tDSed` [g/m3/s] *Diagnostic variables*
- DESC: rate DW sedimentation
- Source: phytoplankton.F90 (228)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tDSed, 'tDSed', 'g/m3/s', 'rate DW sedimentation', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tDSed,       'tDSed',          'g/m3/s','rate DW sedimentation',                output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNDOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate NDOMS from mortality
- Source: phytoplankton.F90 (238)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNDOMS, 'tNDOMS', 'g/m3/s', 'rate NDOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNDOMS,      'tNDOMS',         'g/m3/s','rate NDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNExcrS` [g/m3/s] *Diagnostic variables*
- DESC: rate HN4S excreted
- Source: phytoplankton.F90 (236)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNExcrS, 'tNExcrS', 'g/m3/s', 'rate HN4S excreted', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNExcrS,     'tNExcrS',        'g/m3/s','rate HN4S excreted',                   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNMortNH4S` [g/m3/s] *Diagnostic variables*
- DESC: rate HN4S from mortality
- Source: phytoplankton.F90 (235)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNMortNH4S, 'tNMortNH4S', 'g/m3/s', 'rate HN4S from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNMortNH4S,  'tNMortNH4S',     'g/m3/s','rate HN4S from mortality',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNPOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate NPOMS from mortality
- Source: phytoplankton.F90 (237)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNPOMS, 'tNPOMS', 'g/m3/s', 'rate NPOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNPOMS,      'tNPOMS',         'g/m3/s','rate NPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNResus` [g/m3/s] *Diagnostic variables*
- DESC: rate N resuspension
- Source: phytoplankton.F90 (233)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNResus, 'tNResus', 'g/m3/s', 'rate N resuspension', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNResus,     'tNResus',        'g/m3/s','rate N resuspension',                  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tNSed` [g/m3/s] *Diagnostic variables*
- DESC: rate N sedimentation
- Source: phytoplankton.F90 (230)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tNSed, 'tNSed', 'g/m3/s', 'rate N sedimentation', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tNSed,       'tNSed',          'g/m3/s','rate N sedimentation',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPDOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate PDOMS from mortality
- Source: phytoplankton.F90 (242)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPDOMS, 'tPDOMS', 'g/m3/s', 'rate PDOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPDOMS,      'tPDOMS',         'g/m3/s','rate PDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPExcrS` [g/m3/s] *Diagnostic variables*
- DESC: rate PO4S excreted
- Source: phytoplankton.F90 (240)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPExcrS, 'tPExcrS', 'g/m3/s', 'rate PO4S excreted', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPExcrS,     'tPExcrS',        'g/m3/s','rate PO4S excreted',                   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPMortPO4S` [g/m3/s] *Diagnostic variables*
- DESC: rate PO4S from mortality
- Source: phytoplankton.F90 (239)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPMortPO4S, 'tPMortPO4S', 'g/m3/s', 'rate PO4S from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPMortPO4S,  'tPMortPO4S',     'g/m3/s','rate PO4S from mortality',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPPOMS` [g/m3/s] *Diagnostic variables*
- DESC: rate PPOMS from mortality
- Source: phytoplankton.F90 (241)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPPOMS, 'tPPOMS', 'g/m3/s', 'rate PPOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPPOMS,      'tPPOMS',         'g/m3/s','rate PPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPResus` [g/m3/s] *Diagnostic variables*
- DESC: rate P resuspension
- Source: phytoplankton.F90 (232)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPResus, 'tPResus', 'g/m3/s', 'rate P resuspension', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPResus,     'tPResus',        'g/m3/s','rate P resuspension',                  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tPSed` [g/m3/s] *Diagnostic variables*
- DESC: rate P sedimentation
- Source: phytoplankton.F90 (229)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tPSed, 'tPSed', 'g/m3/s', 'rate P sedimentation', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tPSed,       'tPSed',          'g/m3/s','rate P sedimentation',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tSiExcrS` [g/m3/s] *Diagnostic variables*
- DESC: rate SiS excreted
- Source: phytoplankton.F90 (250)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tSiExcrS, 'tSiExcrS', 'g/m3/s', 'rate SiS excreted', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tSiExcrS,    'tSiExcrS',       'g/m3/s','rate SiS excreted',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tSiO2S` [g/m3/s] *Diagnostic variables*
- DESC: rate SiDOMS from mortality
- Source: phytoplankton.F90 (249)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tSiO2S, 'tSiO2S', 'g/m3/s', 'rate SiDOMS from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tSiO2S,      'tSiO2S',         'g/m3/s','rate SiDOMS from mortality',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `tSiPaS` [g/m3/s] *Diagnostic variables*
- DESC: rate Si part. S from mortality
- Source: phytoplankton.F90 (248)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_tSiPaS, 'tSiPaS', 'g/m3/s', 'rate Si part. S from mortality', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`
- Code: `call self%register_diagnostic_variable(self%id_tSiPaS,      'tSiPaS',         'g/m3/s','rate Si part. S from mortality',       output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )`

### `wCDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate CDOMW from mortality
- Source: phytoplankton.F90 (226)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wCDOMW, 'wCDOMW', 'g/m3/s', 'rate CDOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wCDOMW,      'wCDOMW',         'g/m3/s','rate CDOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wCO2RespW` [g/m3/s] *Diagnostic variables*
- DESC: rate CO2 production
- Source: phytoplankton.F90 (224)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wCO2RespW, 'wCO2RespW', 'g/m3/s', 'rate CO2 production', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wCO2RespW,   'wCO2RespW',      'g/m3/s','rate CO2 production',                  output=output_instantaneous,source=source_do          )`

### `wCO2UptW` [g/m3/s] *Diagnostic variables*
- DESC: rate CO2 uptake
- Source: phytoplankton.F90 (223)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wCO2UptW, 'wCO2UptW', 'g/m3/s', 'rate CO2 uptake', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wCO2UptW,    'wCO2UptW',       'g/m3/s','rate CO2 uptake',                      output=output_instantaneous,source=source_do          )`

### `wCPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate CPOMW from mortality
- Source: phytoplankton.F90 (225)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wCPOMW, 'wCPOMW', 'g/m3/s', 'rate CPOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wCPOMW,      'wCPOMW',         'g/m3/s','rate CPOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wDAss` [g/m3/s] *Diagnostic variables*
- DESC: rate DW assimilation
- Source: phytoplankton.F90 (199)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wDAss, 'wDAss', 'g/m3/s', 'rate DW assimilation', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wDAss,       'wDAss',          'g/m3/s','rate DW assimilation',                 output=output_instantaneous,source=source_do          )`

### `wDDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate DDOMW from mortality
- Source: phytoplankton.F90 (202)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wDDOMW, 'wDDOMW', 'g/m3/s', 'rate DDOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wDDOMW,      'wDDOMW',         'g/m3/s','rate DDOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wDPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate DPOMW from mortality
- Source: phytoplankton.F90 (201)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wDPOMW, 'wDPOMW', 'g/m3/s', 'rate DPOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wDPOMW,      'wDPOMW',         'g/m3/s','rate DPOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wDRespW` [g/m3/s] *Diagnostic variables*
- DESC: rate DW respiration
- Source: phytoplankton.F90 (200)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wDRespW, 'wDRespW', 'g/m3/s', 'rate DW respiration', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wDRespW,     'wDRespW',        'g/m3/s','rate DW respiration',                  output=output_instantaneous,source=source_do          )`

### `wNDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate NDOMW from mortality
- Source: phytoplankton.F90 (214)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNDOMW, 'wNDOMW', 'g/m3/s', 'rate NDOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNDOMW,      'wNDOMW',         'g/m3/s','rate NDOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wNExcrW` [g/m3/s] *Diagnostic variables*
- DESC: rate NH4W excreted
- Source: phytoplankton.F90 (211)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNExcrW, 'wNExcrW', 'g/m3/s', 'rate NH4W excreted', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNExcrW,     'wNExcrW',        'g/m3/s','rate NH4W excreted',                   output=output_instantaneous,source=source_do          )`

### `wNFix` [g/m3/s] *Diagnostic variables*
- DESC: rate N fixation
- Source: phytoplankton.F90 (210)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNFix, 'wNFix', 'g/m3/s', 'rate N fixation', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNFix,       'wNFix',          'g/m3/s','rate N fixation',                      output=output_instantaneous,source=source_do          )`

### `wNMortNH4W` [g/m3/s] *Diagnostic variables*
- DESC: rate NH4W from mortality
- Source: phytoplankton.F90 (212)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNMortNH4W, 'wNMortNH4W', 'g/m3/s', 'rate NH4W from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNMortNH4W,  'wNMortNH4W',     'g/m3/s','rate NH4W from mortality',             output=output_instantaneous,source=source_do          )`

### `wNPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate NPOMW from mortality
- Source: phytoplankton.F90 (213)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNPOMW, 'wNPOMW', 'g/m3/s', 'rate NPOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNPOMW,      'wNPOMW',         'g/m3/s','rate NPOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wNUptNH4` [g/m3/s] *Diagnostic variables*
- DESC: rate NH4W uptake
- Source: phytoplankton.F90 (208)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNUptNH4, 'wNUptNH4', 'g/m3/s', 'rate NH4W uptake', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNUptNH4,    'wNUptNH4',       'g/m3/s','rate NH4W uptake',                     output=output_instantaneous,source=source_do          )`

### `wNUptNO3` [g/m3/s] *Diagnostic variables*
- DESC: rate NO3W uptake
- Source: phytoplankton.F90 (209)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wNUptNO3, 'wNUptNO3', 'g/m3/s', 'rate NO3W uptake', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wNUptNO3,    'wNUptNO3',       'g/m3/s','rate NO3W uptake',                     output=output_instantaneous,source=source_do          )`

### `wO2Prod` [g/m3/s] *Diagnostic variables*
- DESC: rate O2 production
- Source: phytoplankton.F90 (221)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wO2Prod, 'wO2Prod', 'g/m3/s', 'rate O2 production', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wO2Prod,     'wO2Prod',        'g/m3/s','rate O2 production',                   output=output_instantaneous,source=source_do          )`

### `wO2RespW` [g/m3/s] *Diagnostic variables*
- DESC: rate O2 respiration
- Source: phytoplankton.F90 (222)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wO2RespW, 'wO2RespW', 'g/m3/s', 'rate O2 respiration', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wO2RespW,    'wO2RespW',       'g/m3/s','rate O2 respiration',                  output=output_instantaneous,source=source_do          )`

### `wPDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate PDOMW from mortality
- Source: phytoplankton.F90 (207)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPDOMW, 'wPDOMW', 'g/m3/s', 'rate PDOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wPDOMW,      'wPDOMW',         'g/m3/s','rate PDOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wPExcrW` [g/m3/s] *Diagnostic variables*
- DESC: rate PO4W excreted
- Source: phytoplankton.F90 (204)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPExcrW, 'wPExcrW', 'g/m3/s', 'rate PO4W excreted', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wPExcrW,     'wPExcrW',        'g/m3/s','rate PO4W excreted',                   output=output_instantaneous,source=source_do          )`

### `wPMortPO4W` [g/m3/s] *Diagnostic variables*
- DESC: rate PO4W dead
- Source: phytoplankton.F90 (205)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPMortPO4W, 'wPMortPO4W', 'g/m3/s', 'rate PO4W dead', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wPMortPO4W,  'wPMortPO4W',     'g/m3/s','rate PO4W dead',                       output=output_instantaneous,source=source_do          )`

### `wPPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate PPOMW from mortality
- Source: phytoplankton.F90 (206)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPPOMW, 'wPPOMW', 'g/m3/s', 'rate PPOMW from mortality', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wPPOMW,      'wPPOMW',         'g/m3/s','rate PPOMW from mortality',            output=output_instantaneous,source=source_do          )`

### `wPUpt` [g/m3/s] *Diagnostic variables*
- DESC: rate P abs. uptake
- Source: phytoplankton.F90 (203)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_wPUpt, 'wPUpt', 'g/m3/s', 'rate P abs. uptake', output=output_instantaneous,source=source_do)`
- Code: `call self%register_diagnostic_variable(self%id_wPUpt,       'wPUpt',          'g/m3/s','rate P abs. uptake',                   output=output_instantaneous,source=source_do          )`

### `aFeedLvlZoo` [-] *Diagnostic variables*
- DESC: feeding level
- Source: zooplankton.F90 (184)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aFeedLvlZoo, 'aFeedLvlZoo', '-', 'feeding level', output=output_instantaneous)`

### `rCDZoo` [gC/gDW] *Diagnostic variables*
- DESC: C/D ratio
- Source: zooplankton.F90 (178)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rCDZoo, 'rCDZoo', 'gC/gDW', 'C/D ratio', output=output_instantaneous,source=source_do)`

### `rNDZoo` [gN/gDW] *Diagnostic variables*
- DESC: N/D ratio
- Source: zooplankton.F90 (177)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rNDZoo, 'rNDZoo', 'gN/gDW', 'N/D ratio', output=output_instantaneous,source=source_do)`

### `rPDZoo` [gP/gDW] *Diagnostic variables*
- DESC: P/D ratio
- Source: zooplankton.F90 (176)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rPDZoo, 'rPDZoo', 'gP/gDW', 'P/D ratio', output=output_instantaneous,source=source_do)`

### `wCConsZooTot` [g/m3/s] *Diagnostic variables*
- DESC: rate C prey consumed
- Source: zooplankton.F90 (183)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCConsZooTot, 'wCConsZooTot', 'g/m3/s', 'rate C prey consumed', output=output_instantaneous)`

### `wCEgesZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate C egested
- Source: zooplankton.F90 (188)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCEgesZoo, 'wCEgesZoo', 'g/m3/s', 'rate C egested', output=output_instantaneous)`

### `wCMortZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate C from mortality
- Source: zooplankton.F90 (192)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCMortZoo, 'wCMortZoo', 'g/m3/s', 'rate C from mortality', output=output_instantaneous)`

### `wCRespZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate C respired
- Source: zooplankton.F90 (202)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCRespZoo, 'wCRespZoo', 'g/m3/s', 'rate C respired', output=output_instantaneous)`

### `wCZooDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate CDOMW out
- Source: zooplankton.F90 (200)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCZooDOMW, 'wCZooDOMW', 'g/m3/s', 'rate CDOMW out', output=output_instantaneous)`

### `wCZooPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate CPOMW out
- Source: zooplankton.F90 (196)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCZooPOMW, 'wCZooPOMW', 'g/m3/s', 'rate CPOMW out', output=output_instantaneous)`

### `wDConsZooTot` [g/m3/s] *Diagnostic variables*
- DESC: rate D prey consumed
- Source: zooplankton.F90 (180)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDConsZooTot, 'wDConsZooTot', 'g/m3/s', 'rate D prey consumed', output=output_instantaneous)`

### `wDEgesZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate DW egested
- Source: zooplankton.F90 (185)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDEgesZoo, 'wDEgesZoo', 'g/m3/s', 'rate DW egested', output=output_instantaneous)`

### `wDMortZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate DW from mortality
- Source: zooplankton.F90 (189)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDMortZoo, 'wDMortZoo', 'g/m3/s', 'rate DW from mortality', output=output_instantaneous)`

### `wDRespZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate DW respired
- Source: zooplankton.F90 (201)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDRespZoo, 'wDRespZoo', 'g/m3/s', 'rate DW respired', output=output_instantaneous)`

### `wDZooDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate DDOMW out
- Source: zooplankton.F90 (197)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDZooDOMW, 'wDZooDOMW', 'g/m3/s', 'rate DDOMW out', output=output_instantaneous)`

### `wDZooPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate DPOMW out
- Source: zooplankton.F90 (193)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDZooPOMW, 'wDZooPOMW', 'g/m3/s', 'rate DPOMW out', output=output_instantaneous)`

### `wNConsZooTot` [g/m3/s] *Diagnostic variables*
- DESC: rate N prey consumed
- Source: zooplankton.F90 (181)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNConsZooTot, 'wNConsZooTot', 'g/m3/s', 'rate N prey consumed', output=output_instantaneous)`

### `wNEgesZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate N egested
- Source: zooplankton.F90 (186)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNEgesZoo, 'wNEgesZoo', 'g/m3/s', 'rate N egested', output=output_instantaneous)`

### `wNMortZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate N from mortality
- Source: zooplankton.F90 (190)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNMortZoo, 'wNMortZoo', 'g/m3/s', 'rate N from mortality', output=output_instantaneous)`

### `wNZooDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate NDOMW out
- Source: zooplankton.F90 (198)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNZooDOMW, 'wNZooDOMW', 'g/m3/s', 'rate NDOMW out', output=output_instantaneous)`

### `wNZooNH4W` [g/m3/s] *Diagnostic variables*
- DESC: rate NH4W out
- Source: zooplankton.F90 (203)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNZooNH4W, 'wNZooNH4W', 'g/m3/s', 'rate NH4W out', output=output_instantaneous)`

### `wNZooPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate NPOMW out
- Source: zooplankton.F90 (194)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNZooPOMW, 'wNZooPOMW', 'g/m3/s', 'rate NPOMW out', output=output_instantaneous)`

### `wPConsZooTot` [g/m3/s] *Diagnostic variables*
- DESC: rate P prey consumed
- Source: zooplankton.F90 (182)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPConsZooTot, 'wPConsZooTot', 'g/m3/s', 'rate P prey consumed', output=output_instantaneous)`

### `wPEgesZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate P egested
- Source: zooplankton.F90 (187)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPEgesZoo, 'wPEgesZoo', 'g/m3/s', 'rate P egested', output=output_instantaneous)`

### `wPMortZoo` [g/m3/s] *Diagnostic variables*
- DESC: rate P from mortality
- Source: zooplankton.F90 (191)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPMortZoo, 'wPMortZoo', 'g/m3/s', 'rate P from mortality', output=output_instantaneous)`

### `wPZooDOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate PDOMW out
- Source: zooplankton.F90 (199)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPZooDOMW, 'wPZooDOMW', 'g/m3/s', 'rate PDOMW out', output=output_instantaneous)`

### `wPZooPO4W` [g/m3/s] *Diagnostic variables*
- DESC: rate PO4W out
- Source: zooplankton.F90 (204)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPZooPO4W, 'wPZooPO4W', 'g/m3/s', 'rate PO4W out', output=output_instantaneous)`

### `wPZooPOMW` [g/m3/s] *Diagnostic variables*
- DESC: rate PPOMW out
- Source: zooplankton.F90 (195)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPZooPOMW, 'wPZooPOMW', 'g/m3/s', 'rate PPOMW out', output=output_instantaneous)`

### `wSiO2ZooW` [g/m3/s] *Diagnostic variables*
- DESC: rate SiO2W out
- Source: zooplankton.F90 (205)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wSiO2ZooW, 'wSiO2ZooW', 'g/m3/s', 'rate SiO2W out', output=output_instantaneous)`

### `wSiPaZooW` [g/m3/s] *Diagnostic variables*
- DESC: rate Si particulate W egested
- Source: zooplankton.F90 (206)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wSiPaZooW, 'wSiPaZooW', 'g/m3/s', 'rate Si particulate W egested', output=output_instantaneous)`

### `fO2` [-] *Diagnostic variables*
- DESC: oxygen stress fraction
- Source: zoobenthos.F90 (165)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_fO2, 'fO2', '-', 'oxygen stress fraction', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `rCDBent` [gC/gDW] *Diagnostic variables*
- DESC: C/D ratio
- Source: zoobenthos.F90 (134)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rCDBent, 'rCDBent', 'gC/gDW','C/D ratio', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `rNDBent` [gN/gDW] *Diagnostic variables*
- DESC: N/D ratio
- Source: zoobenthos.F90 (133)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rNDBent, 'rNDBent', 'gN/gDW','N/D ratio', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `rPDBent` [gP/gDW] *Diagnostic variables*
- DESC: P/D ratio
- Source: zoobenthos.F90 (132)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_rPDBent, 'rPDBent', 'gP/gDW','P/D ratio', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCBentDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate CDOMS out
- Source: zoobenthos.F90 (159)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCBentDOMS, 'tCBentDOMS', 'g/m2/s','rate CDOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCBentPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate CPOMS out
- Source: zoobenthos.F90 (158)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCBentPOMS, 'tCBentPOMS', 'g/m2/s','rate CPOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCConsBentTot` [g/m2/s] *Diagnostic variables*
- DESC: rate C prey consumed
- Source: zoobenthos.F90 (143)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCConsBentTot,'tCConsBentTot','g/m2/s','rate C prey consumed', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCEgesBent` [g/m2/s] *Diagnostic variables*
- DESC: rate C egested
- Source: zoobenthos.F90 (147)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCEgesBent, 'tCEgesBent', 'g/m2/s','rate C egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCMigrBent` [g/m2/s] *Diagnostic variables*
- DESC: rate C migrated
- Source: zoobenthos.F90 (139)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCMigrBent, 'tCMigrBent', 'g/m2/s','rate C migrated', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCMortBent` [g/m2/s] *Diagnostic variables*
- DESC: rate C from mortality
- Source: zoobenthos.F90 (163)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCMortBent, 'tCMortBent', 'g/m2/s','rate C from mortality', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tCRespBent` [g/m2/s] *Diagnostic variables*
- DESC: rate C respired
- Source: zoobenthos.F90 (149)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCRespBent, 'tCRespBent', 'g/m2/s','rate C respired', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDBentDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate DDOMS out
- Source: zoobenthos.F90 (153)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBentDOMS, 'tDBentDOMS', 'g/m2/s','rate DDOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDBentPOMS` [g/m2/s] *Diagnostic variables*
- DESC: tDBentPOMS
- Source: zoobenthos.F90 (130)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBentPOMS, 'tDBentPOMS', 'g/m2/s','tDBentPOMS', output=output_none,domain=domain_bottom,source=source_do_bottom)`

### `tDBentTPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate DPOMS out
- Source: zoobenthos.F90 (152)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBentTPOMS, 'tDBentTPOMS', 'g/m2/s','rate DPOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDConsBentTot` [g/m2/s] *Diagnostic variables*
- DESC: rate D prey consumed
- Source: zoobenthos.F90 (140)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDConsBentTot,'tDConsBentTot','g/m2/s','rate D prey consumed', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDEgesBent` [g/m2/s] *Diagnostic variables*
- DESC: rate DW egested
- Source: zoobenthos.F90 (144)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDEgesBent, 'tDEgesBent', 'g/m2/s','rate DW egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDMigrBent` [g/m2/s] *Diagnostic variables*
- DESC: rate DW migrated
- Source: zoobenthos.F90 (136)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDMigrBent, 'tDMigrBent', 'g/m2/s','rate DW migrated', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDMortBent` [g/m2/s] *Diagnostic variables*
- DESC: rate DW from mortality
- Source: zoobenthos.F90 (160)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDMortBent, 'tDMortBent', 'g/m2/s','rate DW from mortality', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDMortO2` [g/m2/s] *Diagnostic variables*
- DESC: rate DW from mort. due to O2
- Source: zoobenthos.F90 (164)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDMortO2, 'tDMortO2', 'g/m2/s','rate DW from mort. due to O2', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tDRespBent` [g/m2/s] *Diagnostic variables*
- DESC: rate DW respired
- Source: zoobenthos.F90 (148)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDRespBent, 'tDRespBent', 'g/m2/s','rate DW respired', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNBentDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate NDOMS out
- Source: zoobenthos.F90 (155)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBentDOMS, 'tNBentDOMS', 'g/m2/s','rate NDOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNBentNH4S` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4S out
- Source: zoobenthos.F90 (151)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBentNH4S, 'tNBentNH4S', 'g/m2/s','rate NH4S out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNBentTPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate NPOMS out
- Source: zoobenthos.F90 (154)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBentTPOMS, 'tNBentTPOMS', 'g/m2/s','rate NPOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNConsBentTot` [g/m2/s] *Diagnostic variables*
- DESC: rate N prey consumed
- Source: zoobenthos.F90 (141)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNConsBentTot,'tNConsBentTot','g/m2/s','rate N prey consumed', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNEgesBent` [g/m2/s] *Diagnostic variables*
- DESC: rate N egested
- Source: zoobenthos.F90 (145)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNEgesBent, 'tNEgesBent', 'g/m2/s','rate N egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNMigrBent` [g/m2/s] *Diagnostic variables*
- DESC: rate N migrated
- Source: zoobenthos.F90 (137)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNMigrBent, 'tNMigrBent', 'g/m2/s','rate N migrated', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tNMortBent` [g/m2/s] *Diagnostic variables*
- DESC: rate N from mortality
- Source: zoobenthos.F90 (161)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNMortBent, 'tNMortBent', 'g/m2/s','rate N from mortality', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPBentDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate PDOMS out
- Source: zoobenthos.F90 (157)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBentDOMS, 'tPBentDOMS', 'g/m2/s','rate PDOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPBentPO4S` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4S out
- Source: zoobenthos.F90 (150)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBentPO4S, 'tPBentPO4S', 'g/m2/s','rate PO4S out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPBentTPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate PPOMS out
- Source: zoobenthos.F90 (156)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBentTPOMS, 'tPBentTPOMS', 'g/m2/s','rate PPOMS out', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPConsBentTot` [g/m2/s] *Diagnostic variables*
- DESC: rate P prey consumed
- Source: zoobenthos.F90 (142)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPConsBentTot,'tPConsBentTot','g/m2/s','rate P prey consumed', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPEgesBent` [g/m2/s] *Diagnostic variables*
- DESC: rate P egested
- Source: zoobenthos.F90 (146)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPEgesBent, 'tPEgesBent', 'g/m2/s','rate P egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPMigrBent` [g/m2/s] *Diagnostic variables*
- DESC: rate P migrated
- Source: zoobenthos.F90 (138)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPMigrBent, 'tPMigrBent', 'g/m2/s','rate P migrated', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tPMortBent` [g/m2/s] *Diagnostic variables*
- DESC: rate P from mortality
- Source: zoobenthos.F90 (162)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPMortBent, 'tPMortBent', 'g/m2/s','rate P from mortality', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tSiBentPaS` [g/m2/s] *Diagnostic variables*
- DESC: rate Si partic. S egested
- Source: zoobenthos.F90 (167)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tSiBentPaS, 'tSiBentPaS', 'g/m2/s','rate Si partic. S egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `tSiO2BentS` [g/m2/s] *Diagnostic variables*
- DESC: rate SiO2W egested
- Source: zoobenthos.F90 (166)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tSiO2BentS, 'tSiO2BentS', 'g/m2/s','rate SiO2W egested', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)`

### `aCovVeg` [%] *Diagnostic variables*
- DESC: aCovVeg
- Source: macrophytes.F90 (181)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aCovVeg, 'aCovVeg', '%', 'aCovVeg', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `aCovVeg_PV` [%] *Diagnostic variables*
- DESC: aCovVeg_PV
- Source: macrophytes.F90 (178)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aCovVeg_PV, 'aCovVeg_PV', '%', 'aCovVeg_PV', output=output_instantaneous,missing_value=0.0_rk,source=source_do)`

### `aDSubVeg` [gDW/m2] *Diagnostic variables*
- DESC: aDSubVeg
- Source: macrophytes.F90 (180)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aDSubVeg, 'aDSubVeg', 'gDW/m2','aDSubVeg', output=output_instantaneous,missing_value=0.0_rk,source=source_do_bottom)`

### `aDSubVeg_PV` [gDW/m2] *Diagnostic variables*
- DESC: aDSubVeg_PV
- Source: macrophytes.F90 (175)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aDSubVeg_PV, 'aDSubVeg_PV', 'gDW/m2','aDSubVeg_PV', output=output_instantaneous,missing_value=0.0_rk,source=source_do)`

### `afCovSurfVeg` [-] *Diagnostic variables*
- DESC: afCovSurfVeg
- Source: macrophytes.F90 (182)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_afCovSurfVeg, 'afCovSurfVeg', '-', 'afCovSurfVeg', output=output_none, domain=domain_bottom,source=source_do_bottom)`

### `afCovSurfVeg_PV` [-] *Diagnostic variables*
- DESC: afCovSurfVeg
- Source: macrophytes.F90 (179)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_afCovSurfVeg_PV, 'afCovSurfVeg_PV','-', 'afCovSurfVeg', output=output_none, missing_value=0.0_rk,source=source_do)`

### `aLLimVeg` [-] *Diagnostic variables*
- DESC: light limitation factor
- Source: macrophytes.F90 (185)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aLLimVeg, 'aLLimVeg', '-', 'light limitation factor', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `aLPAR1Veg` [W/m2] *Diagnostic variables*
- DESC: light at top of the macrophytes
- Source: macrophytes.F90 (186)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aLPAR1Veg, 'aLPAR1Veg', 'W/m2', 'light at top of the macrophytes', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `aLPAR2Veg` [W/m2] *Diagnostic variables*
- DESC: light at bottom of the macrophytes
- Source: macrophytes.F90 (187)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aLPAR2Veg, 'aLPAR2Veg', 'W/m2', 'light at bottom of the macrophytes', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `aMuVeg` [1/s] *Diagnostic variables*
- DESC: rate DW actual growth
- Source: macrophytes.F90 (197)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aMuVeg, 'aMuVeg', '1/s', 'rate DW actual growth', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `aNutLimVeg` [-] *Diagnostic variables*
- DESC: nutrient limitation factor
- Source: macrophytes.F90 (183)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_aNutLimVeg, 'aNutLimVeg', '-', 'nutrient limitation factor', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `bfRootVeg_PV` [gDW/m2] *Diagnostic variables*
- DESC: bfRootVeg
- Source: macrophytes.F90 (173)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_bfRootVeg_PV, 'bfRootVeg_PV', 'gDW/m2','bfRootVeg', output=output_instantaneous,missing_value=0.0_rk,source=source_do)`

### `macroextinction` [-] *Diagnostic variables*
- DESC: macroextinction
- Source: macrophytes.F90 (184)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_macroextinction, 'macroextinction','-', 'macroextinction', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCBedDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate CDOMS from mortality
- Source: macrophytes.F90 (245)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCBedDOMS, 'tCBedDOMS', 'g/m2/s','rate CDOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCBedPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate CPOMS from mortality
- Source: macrophytes.F90 (244)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCBedPOMS, 'tCBedPOMS', 'g/m2/s','rate CPOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCBedVeg` [g/m2/s] *Diagnostic variables*
- DESC: CVeg exchange
- Source: macrophytes.F90 (192)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCBedVeg, 'tCBedVeg', 'g/m2/s','CVeg exchange', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCMigrVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate C migration
- Source: macrophytes.F90 (223)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCMigrVeg, 'tCMigrVeg', 'g/m2/s','rate C migration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCMortVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate C mortality
- Source: macrophytes.F90 (225)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCMortVeg, 'tCMortVeg', 'g/m2/s','rate C mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCProdVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate C production
- Source: macrophytes.F90 (224)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCProdVeg, 'tCProdVeg', 'g/m2/s','rate C production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tCRespVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate C respiration
- Source: macrophytes.F90 (228)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tCRespVeg, 'tCRespVeg', 'g/m2/s','rate C respiration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDBedDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate DDOMS from mortality
- Source: macrophytes.F90 (230)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBedDOMS, 'tDBedDOMS', 'g/m2/s','rate DDOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDBedPOMS` [g/m2/s] *Diagnostic variables*
- DESC: tDBedPOMS
- Source: macrophytes.F90 (188)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBedPOMS, 'tDBedPOMS', 'g/m2/s','tDBedPOMS', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDBedVeg` [g/m2/s] *Diagnostic variables*
- DESC: DVeg exchange
- Source: macrophytes.F90 (189)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDBedVeg, 'tDBedVeg', 'g/m2/s','DVeg exchange', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDEnvProdVeg` [g/m2/s] *Diagnostic variables*
- DESC: logistic correction of production
- Source: macrophytes.F90 (198)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDEnvProdVeg, 'tDEnvProdVeg', 'g/m2/s','logistic correction of production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDMigrVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate DW migration
- Source: macrophytes.F90 (199)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDMigrVeg, 'tDMigrVeg', 'g/m2/s','rate DW migration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDMortVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate DW mortality
- Source: macrophytes.F90 (201)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDMortVeg, 'tDMortVeg', 'g/m2/s','rate DW mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDProdVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate DW production
- Source: macrophytes.F90 (200)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDProdVeg, 'tDProdVeg', 'g/m2/s','rate DW production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDRespVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate DW respiration
- Source: macrophytes.F90 (204)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tDRespVeg, 'tDRespVeg', 'g/m2/s','rate DW respiration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNBedDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate NDOMS from mortality
- Source: macrophytes.F90 (237)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBedDOMS, 'tNBedDOMS', 'g/m2/s','rate NDOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNBedPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate NPOMS from mortality
- Source: macrophytes.F90 (236)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBedPOMS, 'tNBedPOMS', 'g/m2/s','rate NPOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNBedVeg` [g/m2/s] *Diagnostic variables*
- DESC: NVeg exchange
- Source: macrophytes.F90 (190)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNBedVeg, 'tNBedVeg', 'g/m2/s','NVeg exchange', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNExcrVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate N excretion
- Source: macrophytes.F90 (207)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNExcrVeg, 'tNExcrVeg', 'g/m2/s','rate N excretion', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNExcrVegS` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4S excreted
- Source: macrophytes.F90 (233)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNExcrVegS, 'tNExcrVegS', 'g/m2/s','rate NH4S excreted', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNExcrVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4W excreted
- Source: macrophytes.F90 (209)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNExcrVegW, 'tNExcrVegW', 'g/m2/s','rate NH4W excreted', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNMigrVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate N migration
- Source: macrophytes.F90 (205)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNMigrVeg, 'tNMigrVeg', 'g/m2/s','rate N migration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNMortVegNH4S` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4S from mortality
- Source: macrophytes.F90 (234)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNMortVegNH4S, 'tNMortVegNH4S', 'g/m2/s','rate NH4S from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNMortVegNH4W` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4W from mortality
- Source: macrophytes.F90 (210)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNMortVegNH4W,'tNMortVegNH4W', 'g/m2/s','rate NH4W from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptNH4VegS` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4S uptake
- Source: macrophytes.F90 (231)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptNH4VegS, 'tNUptNH4VegS', 'g/m2/s','rate NH4S uptake', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptNH4VegW` [g/m2/s] *Diagnostic variables*
- DESC: rate NH4W uptake
- Source: macrophytes.F90 (208)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptNH4VegW, 'tNUptNH4VegW', 'g/m2/s','rate NH4W uptake', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptNO3VegS` [g/m2/s] *Diagnostic variables*
- DESC: rate NO3S uptake
- Source: macrophytes.F90 (235)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptNO3VegS, 'tNUptNO3VegS', 'g/m2/s','rate NO3S uptake', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptNO3VegW` [g/m2/s] *Diagnostic variables*
- DESC: rate NO3W uptake
- Source: macrophytes.F90 (211)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptNO3VegW, 'tNUptNO3VegW', 'g/m2/s','rate NO3W uptake', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptVegS` [g/m2/s] *Diagnostic variables*
- DESC: rate N uptake from sediment
- Source: macrophytes.F90 (232)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptVegS, 'tNUptVegS', 'g/m2/s','rate N uptake from sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tNUptVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate N uptake from water
- Source: macrophytes.F90 (206)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tNUptVegW, 'tNUptVegW', 'g/m2/s','rate N uptake from water', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tO2BedW` [g/m2/s] *Diagnostic variables*
- DESC: tO2BedW exchange
- Source: macrophytes.F90 (193)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2BedW, 'tO2BedW', 'g/m2/s','tO2BedW exchange', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tO2ProdVegS` [g/m2/s] *Diagnostic variables*
- DESC: rate O2S production
- Source: macrophytes.F90 (243)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2ProdVegS, 'tO2ProdVegS', 'g/m2/s','rate O2S production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tO2ProdVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate O2W production
- Source: macrophytes.F90 (220)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2ProdVegW, 'tO2ProdVegW', 'g/m2/s','rate O2W production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tO2RespVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate O2W respiration
- Source: macrophytes.F90 (221)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2RespVegW, 'tO2RespVegW', 'g/m2/s','rate O2W respiration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tO2UptNO3VegW` [g/m2/s] *Diagnostic variables*
- DESC: rate O2W release due to NO3 uptake
- Source: macrophytes.F90 (222)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tO2UptNO3VegW,'tO2UptNO3VegW', 'g/m2/s','rate O2W release due to NO3 uptake',output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPBedDOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate PDOMS from mortality
- Source: macrophytes.F90 (242)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBedDOMS, 'tPBedDOMS', 'g/m2/s','rate PDOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPBedPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate PPOMS from mortality
- Source: macrophytes.F90 (241)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBedPOMS, 'tPBedPOMS', 'g/m2/s','rate PPOMS from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPBedVeg` [g/m2/s] *Diagnostic variables*
- DESC: PVeg exchange
- Source: macrophytes.F90 (191)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPBedVeg, 'tPBedVeg', 'g/m2/s','PVeg exchange', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPExcrVegS` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4S excreted
- Source: macrophytes.F90 (239)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPExcrVegS, 'tPExcrVegS', 'g/m2/s','rate PO4S excreted', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPExcrVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4W excreted
- Source: macrophytes.F90 (216)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPExcrVegW, 'tPExcrVegW', 'g/m2/s','rate PO4W excreted', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPMigrVeg` [g/m2/s] *Diagnostic variables*
- DESC: rate P migration
- Source: macrophytes.F90 (214)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPMigrVeg, 'tPMigrVeg', 'g/m2/s','rate P migration', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPMortVegPO4S` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4S from mortality
- Source: macrophytes.F90 (240)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPMortVegPO4S, 'tPMortVegPO4S', 'g/m2/s','rate PO4S from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPMortVegPO4W` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4W from mortality
- Source: macrophytes.F90 (217)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPMortVegPO4W,'tPMortVegPO4W', 'g/m2/s','rate PO4W from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPUptVegS` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4S uptake from sediment
- Source: macrophytes.F90 (238)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPUptVegS, 'tPUptVegS', 'g/m2/s','rate PO4S uptake from sediment', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tPUptVegW` [g/m2/s] *Diagnostic variables*
- DESC: rate PO4W uptake from water
- Source: macrophytes.F90 (215)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_tPUptVegW, 'tPUptVegW', 'g/m2/s','rate PO4W uptake from water', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `ufDay` [d] *Diagnostic variables*
- DESC: day length
- Source: macrophytes.F90 (196)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_ufDay, 'ufDay', 'd', 'day length', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wCBedDOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate CDOMW from mortality
- Source: macrophytes.F90 (227)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCBedDOMW, 'wCBedDOMW', 'g/m2/s','rate CDOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wCBedPOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate CPOMW from mortality
- Source: macrophytes.F90 (226)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wCBedPOMW, 'wCBedPOMW', 'g/m2/s','rate CPOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wDBedDOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate DDOMW from mortality
- Source: macrophytes.F90 (203)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDBedDOMW, 'wDBedDOMW', 'g/m2/s','rate DDOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wDBedPOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate DPOMW from mortality
- Source: macrophytes.F90 (202)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wDBedPOMW, 'wDBedPOMW', 'g/m2/s','rate DPOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wNBedDOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate NDOMW from mortality
- Source: macrophytes.F90 (213)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNBedDOMW, 'wNBedDOMW', 'g/m2/s','rate NDOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wNBedPOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate NPOMW from mortality
- Source: macrophytes.F90 (212)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wNBedPOMW, 'wNBedPOMW', 'g/m2/s','rate NPOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wPBedDOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate PDOMW from mortality
- Source: macrophytes.F90 (219)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPBedDOMW, 'wPBedDOMW', 'g/m2/s','rate PDOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `wPBedPOMW` [g/m2/s] *Diagnostic variables*
- DESC: rate PPOMW from mortality
- Source: macrophytes.F90 (218)
- Formula (d⁻¹): `-`
- Code: `call self%register_diagnostic_variable(self%id_wPBedPOMW, 'wPBedPOMW', 'g/m2/s','rate PPOMW from mortality', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `BioTurb` [gDW/m3/d] *Diagnostic variables*
- DESC: Bioturbation
- Source: fish.F90 (269)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_BioTurb,'Bioturbation','gDW/m3/d','Bioturbation')`
- Code: `call self%register_diagnostic_variable(self%id_BioTurb, 'Bioturbation', 'gDW/m3/d', 'Bioturbation')`

### `Day_last` [d] *Diagnostic variables*
- DESC: last time step day
- Source: fish.F90 (451)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_Day_last_save,'Day_last','d','last time step day',output=output_none)`
- Code: `call self%register_diagnostic_variable(self%id_Day_last_save, 'Day_last', 'd', 'last time step day', output=output_none)`

### `pred_dummy` [-] *Diagnostic variables*
- DESC: predation dummy
- Source: fish.F90 (220)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_predD,'pred_dummy','-','predation dummy',output=output_none,act_as_state_variable=.true.,source=source_none)`
- Code: `call self%register_diagnostic_variable(self%id_predD, 'pred_dummy', '-', 'predation dummy', output=output_none, act_as_state_variable=.true., source=source_none)`

### `PStar` [-] *Diagnostic variables*
- DESC: extent of risk-reducing behaviors employed
- Source: fish.F90 (446-449)
- Formula (d⁻¹): `call self%register_diagnostic_variable(self%id_PStar,'PStar','-','extent of risk-reducing behaviors employed',...)`
- Code: `call self%register_diagnostic_variable(self%id_PStar, 'PStar', '-', 'extent of risk-reducing behaviors employed', output=output_none/output_instantaneous, missing_value=0.0_rk)`

### `aFunTauTmSet` [-] *Diagnostic variables*
- DESC: basic settling rate
- Source: sediment_exchange.F90 (287)
- Formula (d⁻¹): `register_diagnostic_variable id_aFunTauTmSet`
- Code: `register_diagnostic_variable(self%id_aFunTauTmSet, 'aFunTauTmSet','-', 'basic settling rate', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioIMS` [g/m2/s] *Diagnostic variables*
- DESC: IM abiotic update
- Source: sediment_exchange.F90 (288)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAbioIMS`
- Code: `register_diagnostic_variable(self%id_tDAbioIMS, 'tDAbioIMS', 'g/m2/s','IM abiotic update', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioTotPOMS` [g/m2/s] *Diagnostic variables*
- DESC: Total POM abiotic update
- Source: sediment_exchange.F90 (289)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAbioTotPOMS`
- Code: `register_diagnostic_variable(self%id_tDAbioTotPOMS, 'tDAbioTotPOMS', 'g/m2/s','Total POM abiotic update', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDDifDOM/tPDifDOM/tNDifDOM/tCDifDOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C DOM diffussion per group (diagnostic)
- Source: sediment_exchange.F90 (249-252)
- Formula (d⁻¹): `register_diagnostic_variable id_t*DifDOM`
- Code: `register_diagnostic_variable(self%id_tDDifDOM(i_dom), 'tDDifDOM_'//trim(index), 'g/m2/s','rate DDOM diffussion '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDExchPOMS` [g/m2/s] *Diagnostic variables*
- DESC: ROC DPOM exchange per group (for burial)
- Source: sediment_exchange.F90 (179)
- Formula (d⁻¹): `register_diagnostic_variable id_tDExchPOMS`
- Code: `register_diagnostic_variable(self%id_tDExchPOMS(i_pom), 'tDExchPOMS_'//trim(index), 'g/m2/s','ROC DPOM exchange '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDResusDead` [-] *Diagnostic variables*
- DESC: resuspension rate corrected for macrophytes
- Source: sediment_exchange.F90 (286)
- Formula (d⁻¹): `register_diagnostic_variable id_tDResusDead`
- Code: `register_diagnostic_variable(self%id_tDResusDead, 'tDResusDead', '-', 'tDResusDead', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDResusDOM/tPResusDOM/tNResusDOM/tCResusDOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C DOM resuspended per group (diagnostic)
- Source: sediment_exchange.F90 (245-248)
- Formula (d⁻¹): `register_diagnostic_variable id_t*ResusDOM`
- Code: `register_diagnostic_variable(self%id_tDResusDOM(i_dom), 'tDResusDOM_'//trim(index), 'g/m2/s','rate DDOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDResusIM/tSiResusPa/tPResusPO4/tPResusAIM/tNResusNO3/tNResusNH4/tDSedIM/tPSedAIM/tSiSedPa/tPDifPO4/tNDifNO3/tNDifNH4/tSiResusSiO2/tSiDifSiO2` [g/m2/s] *Diagnostic variables*
- DESC: rates IM/Si/P/N resus/sed/dif (diagnostic, if enabled)
- Source: sediment_exchange.F90 (292-304)
- Formula (d⁻¹): `register_diagnostic_variable id_t*`
- Code: `register_diagnostic_variable(self%id_tDResusIM, 'tDResusIM', 'g/m2/s','rate IM resuspended', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDResusPOM/tPResusPOM/tNResusPOM/tCResusPOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C POM resuspended per group (diagnostic)
- Source: sediment_exchange.F90 (181-188)
- Formula (d⁻¹): `register_diagnostic_variable id_t*ResusPOM`
- Code: `register_diagnostic_variable(self%id_tDResusPOM(i_pom), 'tDResusPOM_'//trim(index), 'g/m2/s','rate DPOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDSedPOM/tPSedPOM/tNSedPOM/tCSedPOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C POM sedimented per group (diagnostic)
- Source: sediment_exchange.F90 (185-188)
- Formula (d⁻¹): `register_diagnostic_variable id_t*SedPOM`
- Code: `register_diagnostic_variable(self%id_tDSedPOM(i_pom), 'tDSedPOM_'//trim(index), 'g/m2/s','rate DPOM sedimented '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `bot_pel_conv` [-] *Diagnostic variables*
- DESC: current conversion between m-2 and m-3
- Source: bot_pel_interface.F90 (49)
- Formula (d⁻¹): `register_diagnostic_variable id_bot_pel_conv_out`
- Code: `register_diagnostic_variable(self%id_bot_pel_conv_out, 'bot_pel_conv', '-', 'current conversion between m-2 and m-3', output=output_none, domain=domain_bottom, source=source_do_bottom)`

### `aFunTauTmSet` [-] *Diagnostic variables*
- DESC: basic settling rate
- Source: resus_sed.F90 (117)
- Formula (d⁻¹): `register_diagnostic_variable id_aFunTauTmSet`
- Code: `register_diagnostic_variable(self%id_aFunTauTmSet, 'aFunTauTmSet','-', 'basic settling rate', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioIMS` [g/m2/s] *Diagnostic variables*
- DESC: IM abiotic update
- Source: resus_sed.F90 (118)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAbioIMS`
- Code: `register_diagnostic_variable(self%id_tDAbioIMS, 'tDAbioIMS', 'g/m2/s','IM abiotic update', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAbioPOMS` [g/m2/s] *Diagnostic variables*
- DESC: POM abiotic update
- Source: resus_sed.F90 (119)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAbioPOMS`
- Code: `register_diagnostic_variable(self%id_tDAbioPOMS, 'tDAbioPOMS', 'g/m2/s','POM abiotic update', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDResusDead` [-] *Diagnostic variables*
- DESC: resuspension rate corrected for macrophytes
- Source: resus_sed.F90 (116)
- Formula (d⁻¹): `register_diagnostic_variable id_tDResusDead`
- Code: `register_diagnostic_variable(self%id_tDResusDead, 'tDResusDead', '-', 'tDResusDead', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDResusIM/tDResusPOM/tNResusPOM/tPResusPOM/tSiResusPa/tPResusPO4/tPResusAIM/tNResusNO3/tNResusNH4` [g/m2/s] *Diagnostic variables*
- DESC: rates resuspended (diagnostic if enabled)
- Source: resus_sed.F90 (122-130)
- Formula (d⁻¹): `register_diagnostic_variable id_t*`
- Code: `register_diagnostic_variable(self%id_tDResusIM, 'tDResusIM', 'g/m2/s','rate IM resuspended', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDSetIM/tDSetPOM/tNSetPOM/tPSetPOM/tPSetAIM/tSiSetPa` [g/m2/s] *Diagnostic variables*
- DESC: rates sedimented (diagnostic if enabled)
- Source: resus_sed.F90 (131-136)
- Formula (d⁻¹): `register_diagnostic_variable id_t*Set`
- Code: `register_diagnostic_variable(self%id_tDSetIM, 'tDSetIM', 'g/m2/s','rate IM sedimented', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDBurDOM/tPBurDOM/tNBurDOM/tCBurDOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C DOM buried per group (diagnostic)
- Source: burial.F90 (201-204)
- Formula (d⁻¹): `register_diagnostic_variable id_t*BurDOM`
- Code: `register_diagnostic_variable(self%id_tDBurDOM(i_spec),'tDBurDOM_'//trim(index),'g/m2/s','rate D DOM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `tDBurIM/tSiBurPa/tPBurPO4/tPBurAIM/tNBurNH4/tNBurNO3/tDBurHum/tPBurHum/tNBurHum/tCBurHum` [g/m2/s] *Diagnostic variables*
- DESC: burial rates (diagnostic if enabled)
- Source: burial.F90 (214-223)
- Formula (d⁻¹): `register_diagnostic_variable id_t*Bur`
- Code: `register_diagnostic_variable(self%id_tDBurIM, 'tDBurIM', 'g/m2/s', 'rate IM burial', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDBurPOM/tPBurPOM/tNBurPOM/tCBurPOM` [g/m2/s] *Diagnostic variables*
- DESC: rate D/P/N/C POM buried per group (diagnostic)
- Source: burial.F90 (167-170)
- Formula (d⁻¹): `register_diagnostic_variable id_t*BurPOM`
- Code: `register_diagnostic_variable(self%id_tDBurPOM(i_spec),'tDBurPOM_'//trim(index),'g/m2/s','rate D POM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)`

### `VDeltaS` [m] *Diagnostic variables*
- DESC: sediment turnover depth (core variable)
- Source: burial.F90 (211)
- Formula (d⁻¹): `register_diagnostic_variable id_VDeltaS`
- Code: `register_diagnostic_variable(self%id_VDeltaS, 'VDeltaS', 'm', 'sediment turnover depth', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `f_dens` [-] *Diagnostic variables*
- DESC: limitation function for density
- Source: bivalves.F90 (300)
- Formula (d⁻¹): `register_diagnostic_variable id_f_dens`
- Code: `register_diagnostic_variable(self%id_f_dens, 'f_dens', '-', 'limitation function for density', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `f_DOmort` [/sec] *Diagnostic variables*
- DESC: mortality function DO
- Source: bivalves.F90 (302)
- Formula (d⁻¹): `register_diagnostic_variable id_f_DOmort`
- Code: `register_diagnostic_variable(self%id_f_DOmort, 'f_DOmort', '/sec', 'mortality function DO', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `f_food` [-] *Diagnostic variables*
- DESC: limitation function for food
- Source: bivalves.F90 (298)
- Formula (d⁻¹): `register_diagnostic_variable id_f_food`
- Code: `register_diagnostic_variable(self%id_f_food, 'f_food', '-', 'limitation function for food', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `f_SS` [-] *Diagnostic variables*
- DESC: limitation function for SS IM
- Source: bivalves.F90 (301)
- Formula (d⁻¹): `register_diagnostic_variable id_f_SS`
- Code: `register_diagnostic_variable(self%id_f_SS, 'f_SS', '-', 'limitation function for SS IM', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `f_temp` [-] *Diagnostic variables*
- DESC: limitation function for temperature
- Source: bivalves.F90 (299)
- Formula (d⁻¹): `register_diagnostic_variable id_f_temp`
- Code: `register_diagnostic_variable(self%id_f_temp, 'f_temp', '-', 'limitation function for temperature', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `FR` [m3/gDW/s] *Diagnostic variables*
- DESC: water filtration rate
- Source: bivalves.F90 (303)
- Formula (d⁻¹): `register_diagnostic_variable id_FR`
- Code: `register_diagnostic_variable(self%id_FR, 'FR', 'm3/gDW/s', 'water filtration rate', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `Imax` [g DW/g DW/s] *Diagnostic variables*
- DESC: maximum potential ingestion rate
- Source: bivalves.F90 (305)
- Formula (d⁻¹): `register_diagnostic_variable id_Imax`
- Code: `register_diagnostic_variable(self%id_Imax, 'Imax', 'g DW/g DW/s', 'maximum potential ingestion rate', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCAgeBiv` [g/m2/s] *Diagnostic variables*
- DESC: aging rate C
- Source: bivalves.F90 (291)
- Formula (d⁻¹): `register_diagnostic_variable id_tCAgeBiv`
- Code: `register_diagnostic_variable(self%id_tCAgeBiv, 'tCAgeBiv', 'g/m2/s', 'aging rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCAssBiv` [g/m2/s] *Diagnostic variables*
- DESC: assimilation rate C
- Source: bivalves.F90 (275)
- Formula (d⁻¹): `register_diagnostic_variable id_tCAssBiv`
- Code: `register_diagnostic_variable(self%id_tCAssBiv, 'tCAssBiv', 'g/m2/s', 'assimilation rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCBivPOMS` [g/m2/s] *Diagnostic variables*
- DESC: rate CPOMS
- Source: bivalves.F90 (296)
- Formula (d⁻¹): `register_diagnostic_variable id_tCBivPOMS`
- Code: `register_diagnostic_variable(self%id_tCBivPOMS, 'tCBivPOMS', 'g/m2/s', 'rate CPOMS', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCConsBivTot` [g/m2/s] *Diagnostic variables*
- DESC: total prey consumption C
- Source: bivalves.F90 (271)
- Formula (d⁻¹): `register_diagnostic_variable id_tCConsBivTot`
- Code: `register_diagnostic_variable(self%id_tCConsBivTot, 'tCConsBivTot', 'g/m2/s', 'total prey consumption C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCEgesBiv` [g/m2/s] *Diagnostic variables*
- DESC: egestion rate C
- Source: bivalves.F90 (279)
- Formula (d⁻¹): `register_diagnostic_variable id_tCEgesBiv`
- Code: `register_diagnostic_variable(self%id_tCEgesBiv, 'tCEgesBiv', 'g/m2/s', 'egestion rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCMortBiv` [g/m2/s] *Diagnostic variables*
- DESC: mortality rate C
- Source: bivalves.F90 (287)
- Formula (d⁻¹): `register_diagnostic_variable id_tCMortBiv`
- Code: `register_diagnostic_variable(self%id_tCMortBiv, 'tCMortBiv', 'g/m2/s', 'mortality rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCReprBiv` [g/m2/s] *Diagnostic variables*
- DESC: reproduction rate C
- Source: bivalves.F90 (295)
- Formula (d⁻¹): `register_diagnostic_variable id_tCReprBiv`
- Code: `register_diagnostic_variable(self%id_tCReprBiv, 'tCReprBiv', 'g/m2/s', 'reproduction rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tCRespBiv` [g/m2/s] *Diagnostic variables*
- DESC: respiration rate C
- Source: bivalves.F90 (283)
- Formula (d⁻¹): `register_diagnostic_variable id_tCRespBiv`
- Code: `register_diagnostic_variable(self%id_tCRespBiv, 'tCRespBiv', 'g/m2/s', 'respiration rate C', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAgeBiv` [g/m2/s] *Diagnostic variables*
- DESC: aging rate DW
- Source: bivalves.F90 (288)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAgeBiv`
- Code: `register_diagnostic_variable(self%id_tDAgeBiv, 'tDAgeBiv', 'g/m2/s', 'aging rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDAssBiv` [g/m2/s] *Diagnostic variables*
- DESC: assimilation rate DW
- Source: bivalves.F90 (272)
- Formula (d⁻¹): `register_diagnostic_variable id_tDAssBiv`
- Code: `register_diagnostic_variable(self%id_tDAssBiv, 'tDAssBiv', 'g/m2/s', 'assimilation rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDBivPOMS` [g/m2/s] *Diagnostic variables*
- DESC: bivalve POMS production (compulsory)
- Source: bivalves.F90 (264)
- Formula (d⁻¹): `register_diagnostic_variable id_tDBivPOMS`
- Code: `register_diagnostic_variable(self%id_tDBivPOMS, 'tDBivPOMS', 'g/m2/s', 'tDBivPOMS', output=output_none, domain=domain_bottom, source=source_do_bottom)`

### `tDBivPOMS` [-] *Diagnostic variables*
- DESC: contribution to global aggregate total_tDPOMbio
- Source: bivalves.F90 (310)
- Formula (d⁻¹): `add_to_aggregate_variable(total_tDPOMbio, id_tDBivPOMS)`
- Code: `call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDBivPOMS,scale_factor=1._rk)`

### `tDConsBiv/tNConsBiv/tPConsBiv/tCConsBiv` [g/m2/s] *Diagnostic variables*
- DESC: consumption rate per prey type (dim nPrey)
- Source: bivalves.F90 (231-234)
- Formula (d⁻¹): `register_diagnostic_variable id_t*ConsBiv`
- Code: `register_diagnostic_variable(self%id_tDConsBiv(i_prey), 'tDConsBiv_'//trim(index), 'g/m2/s', 'consumption rate DW'//trim(index), output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDConsBivTot` [g/m2/s] *Diagnostic variables*
- DESC: total prey consumption DW
- Source: bivalves.F90 (268)
- Formula (d⁻¹): `register_diagnostic_variable id_tDConsBivTot`
- Code: `register_diagnostic_variable(self%id_tDConsBivTot, 'tDConsBivTot', 'g/m2/s', 'total prey consumption DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDEgesBiv` [g/m2/s] *Diagnostic variables*
- DESC: egestion rate DW
- Source: bivalves.F90 (276)
- Formula (d⁻¹): `register_diagnostic_variable id_tDEgesBiv`
- Code: `register_diagnostic_variable(self%id_tDEgesBiv, 'tDEgesBiv', 'g/m2/s', 'egestion rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDMortBiv` [g/m2/s] *Diagnostic variables*
- DESC: mortality rate DW
- Source: bivalves.F90 (284)
- Formula (d⁻¹): `register_diagnostic_variable id_tDMortBiv`
- Code: `register_diagnostic_variable(self%id_tDMortBiv, 'tDMortBiv', 'g/m2/s', 'mortality rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDpseudofaecesBiv` [g/m2/s] *Diagnostic variables*
- DESC: pseudofaeces production rate DW
- Source: bivalves.F90 (297)
- Formula (d⁻¹): `register_diagnostic_variable id_tDpseudofaecesBiv`
- Code: `register_diagnostic_variable(self%id_tDpseudofaecesBiv, 'tDpseudofaecesBiv', 'g/m2/s', 'pseudofaeces production rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDReprBiv` [g/m2/s] *Diagnostic variables*
- DESC: reproduction rate DW
- Source: bivalves.F90 (292)
- Formula (d⁻¹): `register_diagnostic_variable id_tDReprBiv`
- Code: `register_diagnostic_variable(self%id_tDReprBiv, 'tDReprBiv', 'g/m2/s', 'reproduction rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tDRespBiv` [g/m2/s] *Diagnostic variables*
- DESC: respiration rate DW
- Source: bivalves.F90 (280)
- Formula (d⁻¹): `register_diagnostic_variable id_tDRespBiv`
- Code: `register_diagnostic_variable(self%id_tDRespBiv, 'tDRespBiv', 'g/m2/s', 'respiration rate DW', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNAgeBiv` [g/m2/s] *Diagnostic variables*
- DESC: aging rate N
- Source: bivalves.F90 (289)
- Formula (d⁻¹): `register_diagnostic_variable id_tNAgeBiv`
- Code: `register_diagnostic_variable(self%id_tNAgeBiv, 'tNAgeBiv', 'g/m2/s', 'aging rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNAssBiv` [g/m2/s] *Diagnostic variables*
- DESC: assimilation rate N
- Source: bivalves.F90 (273)
- Formula (d⁻¹): `register_diagnostic_variable id_tNAssBiv`
- Code: `register_diagnostic_variable(self%id_tNAssBiv, 'tNAssBiv', 'g/m2/s', 'assimilation rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNConsBivTot` [g/m2/s] *Diagnostic variables*
- DESC: total prey consumption N
- Source: bivalves.F90 (269)
- Formula (d⁻¹): `register_diagnostic_variable id_tNConsBivTot`
- Code: `register_diagnostic_variable(self%id_tNConsBivTot, 'tNConsBivTot', 'g/m2/s', 'total prey consumption N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNEgesBiv` [g/m2/s] *Diagnostic variables*
- DESC: egestion rate N
- Source: bivalves.F90 (277)
- Formula (d⁻¹): `register_diagnostic_variable id_tNEgesBiv`
- Code: `register_diagnostic_variable(self%id_tNEgesBiv, 'tNEgesBiv', 'g/m2/s', 'egestion rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNExcrBiv` [g/m2/s] *Diagnostic variables*
- DESC: excretion rate N
- Source: bivalves.F90 (281)
- Formula (d⁻¹): `register_diagnostic_variable id_tNExcrBiv`
- Code: `register_diagnostic_variable(self%id_tNExcrBiv, 'tNExcrBiv', 'g/m2/s', 'excretion rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNMortBiv` [g/m2/s] *Diagnostic variables*
- DESC: mortality rate N
- Source: bivalves.F90 (285)
- Formula (d⁻¹): `register_diagnostic_variable id_tNMortBiv`
- Code: `register_diagnostic_variable(self%id_tNMortBiv, 'tNMortBiv', 'g/m2/s', 'mortality rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tNReprBiv` [g/m2/s] *Diagnostic variables*
- DESC: reproduction rate N
- Source: bivalves.F90 (293)
- Formula (d⁻¹): `register_diagnostic_variable id_tNReprBiv`
- Code: `register_diagnostic_variable(self%id_tNReprBiv, 'tNReprBiv', 'g/m2/s', 'reproduction rate N', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPAgeBiv` [g/m2/s] *Diagnostic variables*
- DESC: aging rate P
- Source: bivalves.F90 (290)
- Formula (d⁻¹): `register_diagnostic_variable id_tPAgeBiv`
- Code: `register_diagnostic_variable(self%id_tPAgeBiv, 'tPAgeBiv', 'g/m2/s', 'aging rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPAssBiv` [g/m2/s] *Diagnostic variables*
- DESC: assimilation rate P
- Source: bivalves.F90 (274)
- Formula (d⁻¹): `register_diagnostic_variable id_tPAssBiv`
- Code: `register_diagnostic_variable(self%id_tPAssBiv, 'tPAssBiv', 'g/m2/s', 'assimilation rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPConsBivTot` [g/m2/s] *Diagnostic variables*
- DESC: total prey consumption P
- Source: bivalves.F90 (270)
- Formula (d⁻¹): `register_diagnostic_variable id_tPConsBivTot`
- Code: `register_diagnostic_variable(self%id_tPConsBivTot, 'tPConsBivTot', 'g/m2/s', 'total prey consumption P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPEgesBiv` [g/m2/s] *Diagnostic variables*
- DESC: egestion rate P
- Source: bivalves.F90 (278)
- Formula (d⁻¹): `register_diagnostic_variable id_tPEgesBiv`
- Code: `register_diagnostic_variable(self%id_tPEgesBiv, 'tPEgesBiv', 'g/m2/s', 'egestion rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPExcrBiv` [g/m2/s] *Diagnostic variables*
- DESC: excretion rate P
- Source: bivalves.F90 (282)
- Formula (d⁻¹): `register_diagnostic_variable id_tPExcrBiv`
- Code: `register_diagnostic_variable(self%id_tPExcrBiv, 'tPExcrBiv', 'g/m2/s', 'excretion rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPMortBiv` [g/m2/s] *Diagnostic variables*
- DESC: mortality rate P
- Source: bivalves.F90 (286)
- Formula (d⁻¹): `register_diagnostic_variable id_tPMortBiv`
- Code: `register_diagnostic_variable(self%id_tPMortBiv, 'tPMortBiv', 'g/m2/s', 'mortality rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `tPReprBiv` [g/m2/s] *Diagnostic variables*
- DESC: reproduction rate P
- Source: bivalves.F90 (294)
- Formula (d⁻¹): `register_diagnostic_variable id_tPReprBiv`
- Code: `register_diagnostic_variable(self%id_tPReprBiv, 'tPReprBiv', 'g/m2/s', 'reproduction rate P', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

### `weight` [g DW] *Diagnostic variables*
- DESC: weight
- Source: bivalves.F90 (304)
- Formula (d⁻¹): `register_diagnostic_variable id_weight`
- Code: `register_diagnostic_variable(self%id_weight, 'weight', 'g DW', 'weight', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)`

## Diffusion

### `aDepthDif` [m] *Diffusion*
- DESC: average diffusion distance
- Source: sediment_exchange.F90 (515)
- Formula (d⁻¹): `aDepthDif= max(NearZero, fDepthDifS*cDepthS)`
- Code: `aDepthDif= max(NearZero, fDepthDifS*cDepthS)`

### `bIntVol` [m] *Diffusion*
- DESC: interstitial water volume in sediment
- Source: sediment_exchange.F90 (493)
- Formula (d⁻¹): `bIntVol = max(NearZero, cDepthS / bPorS)`
- Code: `bIntVol = max(NearZero, cDepthS / bPorS)`

### `oCDOMS` [g/m3] *Diffusion*
- DESC: conc. of dissolved organic C in interstitial water (dim nDOM)
- Source: sediment_exchange.F90 (507)
- Formula (d⁻¹): `oCDOMS = sCDOMS / bIntVol`
- Code: `oCDOMS  = sCDOMS  / bIntVol`

### `oDDOMS` [g/m3] *Diffusion*
- DESC: conc. of dissolved organic D in interstitial water (dim nDOM)
- Source: sediment_exchange.F90 (504)
- Formula (d⁻¹): `oDDOMS = sDDOMS / bIntVol`
- Code: `oDDOMS  = sDDOMS  / bIntVol`

### `oNDOMS` [g/m3] *Diffusion*
- DESC: conc. of dissolved organic N in interstitial water (dim nDOM)
- Source: sediment_exchange.F90 (505)
- Formula (d⁻¹): `oNDOMS = sNDOMS / bIntVol`
- Code: `oNDOMS  = sNDOMS  / bIntVol`

### `oNH4S` [g/m3] *Diffusion*
- DESC: conc. of dissolved NH4 in interstitial water
- Source: sediment_exchange.F90 (498)
- Formula (d⁻¹): `oNH4S=max(0.0_rk, sNH4S / bIntVol)`
- Code: `oNH4S=max(0.0_rk, sNH4S / bIntVol)`

### `oNO3S` [g/m3] *Diffusion*
- DESC: conc. of dissolved NO3 in interstitial water
- Source: sediment_exchange.F90 (497)
- Formula (d⁻¹): `oNO3S = max(0.0_rk, sNO3S / bIntVol)`
- Code: `oNO3S = max(0.0_rk, sNO3S / bIntVol)`

### `oPDOMS` [g/m3] *Diffusion*
- DESC: conc. of dissolved organic P in interstitial water (dim nDOM)
- Source: sediment_exchange.F90 (506)
- Formula (d⁻¹): `oPDOMS = sPDOMS / bIntVol`
- Code: `oPDOMS  = sPDOMS  / bIntVol`

### `oPO4S` [g/m3] *Diffusion*
- DESC: conc. of dissolved PO4 in interstitial water
- Source: sediment_exchange.F90 (499)
- Formula (d⁻¹): `oPO4S = max(0.0_rk, sPO4S / bIntVol)`
- Code: `oPO4S = max(0.0_rk, sPO4S / bIntVol)`

### `oSiO2S` [g/m3] *Diffusion*
- DESC: conc. of dissolved SiO2 in interstitial water
- Source: sediment_exchange.F90 (500)
- Formula (d⁻¹): `oSiO2S = sSiO2S / bIntVol`
- Code: `oSiO2S  = sSiO2S  / bIntVol`

### `tCDifDOM` [g/m2/s] *Diffusion*
- DESC: [BUG?] diffusion flux of dissolved organic C - uses kDDifDOM instead of a C-specific diffusion constant
- Source: sediment_exchange.F90 (529)
- Formula (d⁻¹): `tCDifDOM =self%kCDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oCDOMS-sCDOMW)/aDepthDif`
- Code: `tCDifDOM =self%kDDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oCDOMS-sCDOMW)/aDepthDif`

### `tDDifDOM` [g/m2/s] *Diffusion*
- DESC: diffusion flux of dissolved organic DW per group (dim nDOM)
- Source: sediment_exchange.F90 (526)
- Formula (d⁻¹): `tDDifDOM =self%kDDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oDDOMS-sDDOMW)/aDepthDif`
- Code: `tDDifDOM =self%kDDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oDDOMS-sDDOMW)/aDepthDif`

### `tNDifDOM` [g/m2/s] *Diffusion*
- DESC: diffusion flux of dissolved organic N per group (dim nDOM)
- Source: sediment_exchange.F90 (527)
- Formula (d⁻¹): `tNDifDOM =self%kNDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oNDOMS-sNDOMW)/aDepthDif`
- Code: `tNDifDOM =self%kNDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oNDOMS-sNDOMW)/aDepthDif`

### `tNDifNH4` [g/m2/s] *Diffusion*
- DESC: diffusion flux of NH4
- Source: sediment_exchange.F90 (517)
- Formula (d⁻¹): `tNDifNH4=self%kNDifNH4*(oNH4S-sNH4W)*uCorDif`
- Code: `tNDifNH4=self%kNDifNH4*(oNH4S-sNH4W)*uCorDif`

### `tNDifNO3` [g/m2/s] *Diffusion*
- DESC: diffusion flux of NO3
- Source: sediment_exchange.F90 (518)
- Formula (d⁻¹): `tNDifNO3=self%kNDifNO3*(oNO3S-sNO3W)*uCorDif`
- Code: `tNDifNO3=self%kNDifNO3*(oNO3S-sNO3W)*uCorDif`

### `tPDifDOM` [g/m2/s] *Diffusion*
- DESC: diffusion flux of dissolved organic P per group (dim nDOM)
- Source: sediment_exchange.F90 (528)
- Formula (d⁻¹): `tPDifDOM =self%kPDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oPDOMS-sPDOMW)/aDepthDif`
- Code: `tPDifDOM =self%kPDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oPDOMS-sPDOMW)/aDepthDif`

### `tPDifPO4` [g/m2/s] *Diffusion*
- DESC: diffusion flux of PO4
- Source: sediment_exchange.F90 (519)
- Formula (d⁻¹): `tPDifPO4=self%kPDifPO4*(oPO4S-sPO4W)*uCorDif`
- Code: `tPDifPO4=self%kPDifPO4*(oPO4S-sPO4W)*uCorDif`

### `tSiDifSiO2` [g/m2/s] *Diffusion*
- DESC: diffusion flux of SiO2
- Source: sediment_exchange.F90 (520)
- Formula (d⁻¹): `tSiDifSiO2=self%kSiO2Dif*(oSiO2S-sSiO2W)*uCorDif`
- Code: `tSiDifSiO2=self%kSiO2Dif*(oSiO2S-sSiO2W)*uCorDif`

### `uCorDif` [m/d] *Diffusion*
- DESC: corrected water to sediment diffusion constant
- Source: sediment_exchange.F90 (516)
- Formula (d⁻¹): `uCorDif = uFunTmDif*self%cTurbDifNut*bPorCorS/aDepthDif`
- Code: `uCorDif = uFunTmDif*self%cTurbDifNut*bPorCorS/aDepthDif`

## do (diagnostic)

### `aCovVeg_PV` [-] *do (diagnostic)*
- DESC: set percent cover diagnostic (PV)
- Source: macrophytes.F90 (853)
- Formula (d⁻¹): `aCovVeg`
- Code: `_SET_DIAGNOSTIC_(self%id_aCovVeg_PV, aCovVeg)`

### `aDayInitVeg_out` [-] *do (diagnostic)*
- DESC: set aDayInitVeg output
- Source: macrophytes.F90 (855)
- Formula (d⁻¹): `aDayInitVeg`
- Code: `_SET_DIAGNOSTIC_(self%id_aDayInitVeg_out, aDayInitVeg)`

### `aDSubVeg_PV` [-] *do (diagnostic)*
- DESC: set submerged biomass diagnostic (PV)
- Source: macrophytes.F90 (852)
- Formula (d⁻¹): `aDSubVeg`
- Code: `_SET_DIAGNOSTIC_(self%id_aDSubVeg_PV, aDSubVeg)`

### `afCovSurfVeg_PV` [-] *do (diagnostic)*
- DESC: set surface cover diagnostic (PV)
- Source: macrophytes.F90 (854)
- Formula (d⁻¹): `afCovSurfVeg`
- Code: `_SET_DIAGNOSTIC_(self%id_afCovSurfVeg_PV, afCovSurfVeg)`

### `bfRootVeg_PV` [-] *do (diagnostic)*
- DESC: set root fraction diagnostic (PV)
- Source: macrophytes.F90 (856)
- Formula (d⁻¹): `bfRootVeg`
- Code: `_SET_DIAGNOSTIC_(self%id_bfRootVeg_PV, bfRootVeg)`

### `calc_veg_fractions` [-] *do (diagnostic)*
- DESC: calc. biomass fractions in do subroutine (shared with do_bottom)
- Source: macrophytes.F90 (848)
- Formula (d⁻¹): `calc_veg_fractions(Day, sDVeg, uTm, lat, aDSubVeg, aCovVeg, afCovSurfVeg, aDayInitVeg, aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg)`
- Code: `call self%calc_veg_fractions(Day, sDVeg, uTm, lat, aDSubVeg, aCovVeg, afCovSurfVeg, aDayInitVeg, aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg)`

### `sDVeg` [-] *do (diagnostic)*
- DESC: retrieve macrophyte DW (PV) for do subroutine
- Source: macrophytes.F90 (844)
- Formula (d⁻¹): `-`
- Code: `_GET_(self%id_sDVeg_PV, sDVeg)`

## do - auxiliary

### `afCovSurfVeg` [-] *do - auxiliary*
- DESC: surface vegetation cover (clipped)
- Source: phytoplankton.F90 (344)
- Formula (d⁻¹): `afCovSurfVeg = min(1.0_rk,afCovSurfVeg)`
- Code: `afCovSurfVeg = min(1.0_rk,afCovSurfVeg)`

### `meanparout` [-] *do - auxiliary*
- DESC: meanpar output copy
- Source: phytoplankton.F90 (339)
- Formula (d⁻¹): `meanparout = meanpar`
- Code: `meanparout = meanpar`

### `oSiW` [gSi/m3] *do - auxiliary*
- DESC: silica content of phytoplankton
- Source: phytoplankton.F90 (358)
- Formula (d⁻¹): `oSiW=self%cSiD*sDW`
- Code: `oSiW=self%cSiD*sDW`

### `rCDW` [-] *do - auxiliary*
- DESC: C/D ratio water
- Source: phytoplankton.F90 (356)
- Formula (d⁻¹): `rCDW = sCW /(sDW+NearZero)`
- Code: `rCDW = sCW /(sDW+NearZero)`

### `rNDW` [-] *do - auxiliary*
- DESC: N/D ratio water
- Source: phytoplankton.F90 (355)
- Formula (d⁻¹): `rNDW = sNW /(sDW+NearZero)`
- Code: `rNDW = sNW /(sDW+NearZero)`

### `rPDW` [-] *do - auxiliary*
- DESC: P/D ratio water
- Source: phytoplankton.F90 (354)
- Formula (d⁻¹): `rPDW = sPW /(sDW+NearZero)`
- Code: `rPDW = sPW /(sDW+NearZero)`

## do - chlorophyll

### `oChla` [ug/l] *do - chlorophyll*
- DESC: chlorophyll-a concentration
- Source: phytoplankton.F90 (557)
- Formula (d⁻¹): `oChla = mgPerg * rChD * sDW`
- Code: `oChla = mgPerg * rChD * sDW`

### `rChD` [-] *do - chlorophyll*
- DESC: chlorophyll-a/DW ratio
- Source: phytoplankton.F90 (556)
- Formula (d⁻¹): `rChD = self%cChDMax - (self%cChDMax - self%cChDMin) * aLLim`
- Code: `rChD = self%cChDMax - (self%cChDMax - self%cChDMin) * aLLim`

## do - derivatives

### `CDOMpoolW` [-] *do - derivatives*
- DESC: update DOM C ODE
- Source: phytoplankton.F90 (546)
- Formula (d⁻¹): `_SET_ODE_(self%id_CDOMpoolW, wCDOMW)`
- Code: `_SET_ODE_(self%id_CDOMpoolW, wCDOMW)`

### `CPOMpoolW` [-] *do - derivatives*
- DESC: update POM C ODE
- Source: phytoplankton.F90 (545)
- Formula (d⁻¹): `_SET_ODE_(self%id_CPOMpoolW, wCPOMW)`
- Code: `_SET_ODE_(self%id_CPOMpoolW, wCPOMW)`

### `DDOMpoolW` [-] *do - derivatives*
- DESC: update DOM DW ODE
- Source: phytoplankton.F90 (542)
- Formula (d⁻¹): `_SET_ODE_(self%id_DDOMpoolW, wDDOMW)`
- Code: `_SET_ODE_(self%id_DDOMpoolW, wDDOMW)`

### `DPOMpoolW` [-] *do - derivatives*
- DESC: update POM DW ODE
- Source: phytoplankton.F90 (539)
- Formula (d⁻¹): `_SET_ODE_(self%id_DPOMpoolW, wDPOMW)`
- Code: `_SET_ODE_(self%id_DPOMpoolW, wDPOMW)`

### `NDOMpoolW` [-] *do - derivatives*
- DESC: update DOM N ODE
- Source: phytoplankton.F90 (543)
- Formula (d⁻¹): `_SET_ODE_(self%id_NDOMpoolW, wNDOMW)`
- Code: `_SET_ODE_(self%id_NDOMpoolW, wNDOMW)`

### `NH4poolW` [-] *do - derivatives*
- DESC: update NH4 ODE
- Source: phytoplankton.F90 (536)
- Formula (d⁻¹): `_SET_ODE_(self%id_NH4poolW, wNNH4W)`
- Code: `_SET_ODE_(self%id_NH4poolW, wNNH4W)`

### `NO3poolW` [-] *do - derivatives*
- DESC: update NO3 ODE
- Source: phytoplankton.F90 (535)
- Formula (d⁻¹): `_SET_ODE_(self%id_NO3poolW, wNNO3W)`
- Code: `_SET_ODE_(self%id_NO3poolW, wNNO3W)`

### `NPOMpoolW` [-] *do - derivatives*
- DESC: update POM N ODE
- Source: phytoplankton.F90 (540)
- Formula (d⁻¹): `_SET_ODE_(self%id_NPOMpoolW, wNPOMW)`
- Code: `_SET_ODE_(self%id_NPOMpoolW, wNPOMW)`

### `O2poolW` [-] *do - derivatives*
- DESC: update O2 ODE
- Source: phytoplankton.F90 (537)
- Formula (d⁻¹): `_SET_ODE_(self%id_O2poolW, wO2W)`
- Code: `_SET_ODE_(self%id_O2poolW, wO2W)`

### `PDOMpoolW` [-] *do - derivatives*
- DESC: update DOM P ODE
- Source: phytoplankton.F90 (544)
- Formula (d⁻¹): `_SET_ODE_(self%id_PDOMpoolW, wPDOMW)`
- Code: `_SET_ODE_(self%id_PDOMpoolW, wPDOMW)`

### `PO4poolW` [-] *do - derivatives*
- DESC: update PO4 ODE
- Source: phytoplankton.F90 (534)
- Formula (d⁻¹): `_SET_ODE_(self%id_PO4poolW, wPPO4W)`
- Code: `_SET_ODE_(self%id_PO4poolW, wPPO4W)`

### `PPOMpoolW` [-] *do - derivatives*
- DESC: update POM P ODE
- Source: phytoplankton.F90 (541)
- Formula (d⁻¹): `_SET_ODE_(self%id_PPOMpoolW, wPPOMW)`
- Code: `_SET_ODE_(self%id_PPOMpoolW, wPPOMW)`

### `sCW` [-] *do - derivatives*
- DESC: update phytoplankton C ODE
- Source: phytoplankton.F90 (530)
- Formula (d⁻¹): `_SET_ODE_(self%id_sCW, wCW)`
- Code: `_SET_ODE_(self%id_sCW, wCW)`

### `sDW` [-] *do - derivatives*
- DESC: update phytoplankton DW ODE
- Source: phytoplankton.F90 (527)
- Formula (d⁻¹): `_SET_ODE_(self%id_sDW, wDW)`
- Code: `_SET_ODE_(self%id_sDW, wDW)`

### `SiO2poolW` [-] *do - derivatives*
- DESC: update SiO2 ODE (if lSi)
- Source: phytoplankton.F90 (549)
- Formula (d⁻¹): `_SET_ODE_(self%id_SiO2poolW, wSiSiO2W)`
- Code: `_SET_ODE_(self%id_SiO2poolW, wSiSiO2W)`

### `SiPapoolW` [-] *do - derivatives*
- DESC: update SiPa ODE (if lSi)
- Source: phytoplankton.F90 (548)
- Formula (d⁻¹): `_SET_ODE_(self%id_SiPapoolW, wSiPaW)`
- Code: `_SET_ODE_(self%id_SiPapoolW, wSiPaW)`

### `sNW` [-] *do - derivatives*
- DESC: update phytoplankton N ODE
- Source: phytoplankton.F90 (529)
- Formula (d⁻¹): `_SET_ODE_(self%id_sNW, wNW)`
- Code: `_SET_ODE_(self%id_sNW, wNW)`

### `sPW` [-] *do - derivatives*
- DESC: update phytoplankton P ODE
- Source: phytoplankton.F90 (528)
- Formula (d⁻¹): `_SET_ODE_(self%id_sPW, wPW)`
- Code: `_SET_ODE_(self%id_sPW, wPW)`

## do - excretion

### `wNExcrW` [gN/m3/d] *do - excretion*
- DESC: absolute N excretion rate
- Source: phytoplankton.F90 (450)
- Formula (d⁻¹): `wNExcrW = (2.0_rk * rNDW) /(self%cNDMax + rNDW) * rNDW * wDRespW`
- Code: `wNExcrW = (2.0_rk * rNDW) /(self%cNDMax + rNDW) * rNDW * wDRespW`

### `wPExcrW` [gP/m3/d] *do - excretion*
- DESC: absolute P excretion rate
- Source: phytoplankton.F90 (449)
- Formula (d⁻¹): `wPExcrW = (2.0_rk * rPDW) /(self%cPDMax + rPDW) * rPDW * wDRespW`
- Code: `wPExcrW = (2.0_rk * rPDW) /(self%cPDMax + rPDW) * rPDW * wDRespW`

## do - external fluxes C

### `wCDOMW` [gC/m3/d] *do - external fluxes C*
- DESC: flux of DOM-bound C to water column
- Source: phytoplankton.F90 (521)
- Formula (d⁻¹): `wCDOMW = wCMortTOMW * self%fDOMW`
- Code: `wCDOMW = wCMortTOMW * self%fDOMW`

### `wCMortTOMW` [gC/m3/d] *do - external fluxes C*
- DESC: flux of dead C in organic matter
- Source: phytoplankton.F90 (519)
- Formula (d⁻¹): `wCMortTOMW = wCMortW`
- Code: `wCMortTOMW = wCMortW`

### `wCO2RespW` [gC/m3/d] *do - external fluxes C*
- DESC: uptake of CO2 due to respiration
- Source: phytoplankton.F90 (517)
- Formula (d⁻¹): `wCO2RespW = wCRespW * aCorO2BOD`
- Code: `wCO2RespW = wCRespW * aCorO2BOD`

### `wCO2UptW` [gC/m3/d] *do - external fluxes C*
- DESC: photosynthetic CO2 uptake
- Source: phytoplankton.F90 (516)
- Formula (d⁻¹): `wCO2UptW = wCAss`
- Code: `wCO2UptW = wCAss`

### `wCO2W` [gC/m3/d] *do - external fluxes C*
- DESC: total CO2 flux to water column
- Source: phytoplankton.F90 (518)
- Formula (d⁻¹): `wCO2W = wCO2UptW - wCO2RespW`
- Code: `wCO2W = wCO2UptW - wCO2RespW`

### `wCPOMW` [gC/m3/d] *do - external fluxes C*
- DESC: flux of POM-bound C to water column
- Source: phytoplankton.F90 (520)
- Formula (d⁻¹): `wCPOMW = wCMortTOMW * (1.0_rk - self%fDOMW)`
- Code: `wCPOMW = wCMortTOMW * (1.0_rk - self%fDOMW)`

## do - external fluxes DW

### `wDDOMW` [gDW/m3/d] *do - external fluxes DW*
- DESC: mortality flux to DOM
- Source: phytoplankton.F90 (473)
- Formula (d⁻¹): `wDDOMW = wDMortW * self%fDOMW`
- Code: `wDDOMW = wDMortW * self%fDOMW`

### `wDPOMW` [gDW/m3/d] *do - external fluxes DW*
- DESC: mortality flux to POM
- Source: phytoplankton.F90 (472)
- Formula (d⁻¹): `wDPOMW = wDMortW * (1.0_rk - self%fDOMW)`
- Code: `wDPOMW = wDMortW * (1.0_rk - self%fDOMW)`

## do - external fluxes N

### `afNH4Upt` [-] *do - external fluxes N*
- DESC: fraction of N uptake taken as ammonia
- Source: phytoplankton.F90 (477)
- Formula (d⁻¹): `afNH4Upt = sNH4W*sNO3W/((ahNUpt+sNH4W)*(ahNUpt+sNO3W)) + sNH4W*ahNUpt/((sNH4W+sNO3W)*(ahNUpt+sNO3W))`
- Code: `afNH4Upt = sNH4W*sNO3W/((ahNUpt+sNH4W)*(ahNUpt+sNO3W)) + sNH4W*ahNUpt/((sNH4W+sNO3W)*(ahNUpt+sNO3W))`

### `wNDOMW` [gN/m3/d] *do - external fluxes N*
- DESC: flux of DOM-bound N to water column
- Source: phytoplankton.F90 (485)
- Formula (d⁻¹): `wNDOMW = wNMortTOMW * self%fDOMW`
- Code: `wNDOMW = wNMortTOMW * self%fDOMW`

### `wNMortNH4W` [gN/m3/d] *do - external fluxes N*
- DESC: fraction of mortality N released as ammonia
- Source: phytoplankton.F90 (479)
- Formula (d⁻¹): `wNMortNH4W = self%fDissMort * wNMortW`
- Code: `wNMortNH4W = self%fDissMort * wNMortW`

### `wNMortTOMW` [gN/m3/d] *do - external fluxes N*
- DESC: part of mortality N bound in organic matter
- Source: phytoplankton.F90 (483)
- Formula (d⁻¹): `wNMortTOMW = wNMortW - wNMortNH4W`
- Code: `wNMortTOMW = wNMortW - wNMortNH4W`

### `wNNH4W` [gN/m3/d] *do - external fluxes N*
- DESC: total flux of ammonia to water column
- Source: phytoplankton.F90 (480)
- Formula (d⁻¹): `wNNH4W = wNExcrW + wNMortNH4W - wNUptNH4`
- Code: `wNNH4W = wNExcrW + wNMortNH4W - wNUptNH4`

### `wNNO3W` [gN/m3/d] *do - external fluxes N*
- DESC: total flux of nitrate to water column
- Source: phytoplankton.F90 (482)
- Formula (d⁻¹): `wNNO3W = - wNUptNO3`
- Code: `wNNO3W = - wNUptNO3`

### `wNPOMW` [gN/m3/d] *do - external fluxes N*
- DESC: flux of POM-bound N to water column
- Source: phytoplankton.F90 (484)
- Formula (d⁻¹): `wNPOMW = wNMortTOMW * (1.0_rk - self%fDOMW)`
- Code: `wNPOMW = wNMortTOMW * (1.0_rk - self%fDOMW)`

### `wNUptNH4` [gN/m3/d] *do - external fluxes N*
- DESC: absolute ammonia uptake
- Source: phytoplankton.F90 (478)
- Formula (d⁻¹): `wNUptNH4 = afNH4Upt * wNUpt`
- Code: `wNUptNH4 = afNH4Upt * wNUpt`

### `wNUptNO3` [gN/m3/d] *do - external fluxes N*
- DESC: absolute nitrate uptake
- Source: phytoplankton.F90 (481)
- Formula (d⁻¹): `wNUptNO3 = wNUpt - wNUptNH4`
- Code: `wNUptNO3 = wNUpt - wNUptNH4`

## do - external fluxes O2

### `aCorO2BOD` [-] *do - external fluxes O2*
- DESC: correction of O2 demand at low oxygen conc
- Source: phytoplankton.F90 (509)
- Formula (d⁻¹): `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`
- Code: `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`

### `wO2Prod` [gO2/m3/d] *do - external fluxes O2*
- DESC: photosynthetic O2 production
- Source: phytoplankton.F90 (508)
- Formula (d⁻¹): `wO2Prod = molO2molC * self%cCPerDW * wDAss`
- Code: `wO2Prod = molO2molC * self%cCPerDW * wDAss`

### `wO2RespW` [gO2/m3/d] *do - external fluxes O2*
- DESC: uptake of O2 due to respiration
- Source: phytoplankton.F90 (510)
- Formula (d⁻¹): `wO2RespW = molO2molC * self%cCPerDW * wDRespW * aCorO2BOD`
- Code: `wO2RespW = molO2molC * self%cCPerDW * wDRespW * aCorO2BOD`

### `wO2UptNO3` [gO2/m3/d] *do - external fluxes O2*
- DESC: O2 reduction due to NO3 uptake
- Source: phytoplankton.F90 (511)
- Formula (d⁻¹): `wO2UptNO3 = O2PerNO3 * molO2molN * wNUptNO3`
- Code: `wO2UptNO3 = O2PerNO3 * molO2molN * wNUptNO3`

### `wO2W` [gO2/m3/d] *do - external fluxes O2*
- DESC: total O2 flux to water column
- Source: phytoplankton.F90 (512)
- Formula (d⁻¹): `wO2W = wO2Prod - wO2RespW + wO2UptNO3`
- Code: `wO2W = wO2Prod - wO2RespW + wO2UptNO3`

## do - external fluxes P

### `wPDOMW` [gP/m3/d] *do - external fluxes P*
- DESC: flux of DOM-bound P to water column
- Source: phytoplankton.F90 (493)
- Formula (d⁻¹): `wPDOMW = wPMortTOMW * self%fDOMW`
- Code: `wPDOMW = wPMortTOMW * self%fDOMW`

### `wPMortPO4W` [gP/m3/d] *do - external fluxes P*
- DESC: fraction of mortality P released as phosphate
- Source: phytoplankton.F90 (489)
- Formula (d⁻¹): `wPMortPO4W = self%fDissMort * wPMortW`
- Code: `wPMortPO4W = self%fDissMort * wPMortW`

### `wPMortTOMW` [gP/m3/d] *do - external fluxes P*
- DESC: part of mortality P bound in organic matter
- Source: phytoplankton.F90 (491)
- Formula (d⁻¹): `wPMortTOMW = wPMortW - wPMortPO4W`
- Code: `wPMortTOMW = wPMortW - wPMortPO4W`

### `wPPO4W` [gP/m3/d] *do - external fluxes P*
- DESC: total flux of phosphate to water column
- Source: phytoplankton.F90 (490)
- Formula (d⁻¹): `wPPO4W = wPExcrW + wPMortPO4W - wPUpt`
- Code: `wPPO4W = wPExcrW + wPMortPO4W - wPUpt`

### `wPPOMW` [gP/m3/d] *do - external fluxes P*
- DESC: flux of POM-bound P to water column
- Source: phytoplankton.F90 (492)
- Formula (d⁻¹): `wPPOMW = wPMortTOMW * (1.0_rk - self%fDOMW)`
- Code: `wPPOMW = wPMortTOMW * (1.0_rk - self%fDOMW)`

## do - external fluxes Si

### `wSiExcrW` [gSi/m3/d] *do - external fluxes Si*
- DESC: Si excretion
- Source: phytoplankton.F90 (499)
- Formula (d⁻¹): `wSiExcrW = self%cSiD * wDRespW`
- Code: `wSiExcrW = self%cSiD * wDRespW`

### `wSiMortW` [gSi/m3/d] *do - external fluxes Si*
- DESC: silica bound in dead phytoplankton
- Source: phytoplankton.F90 (500)
- Formula (d⁻¹): `wSiMortW = self%cSiD * wDMortW`
- Code: `wSiMortW = self%cSiD * wDMortW`

### `wSiO2MortW` [gSi/m3/d] *do - external fluxes Si*
- DESC: flux of dissolved organic silica to water column
- Source: phytoplankton.F90 (502)
- Formula (d⁻¹): `wSiO2MortW = wSiMortW * self%fDOMW`
- Code: `wSiO2MortW = wSiMortW * self%fDOMW`

### `wSiPaW` [gSi/m3/d] *do - external fluxes Si*
- DESC: flux of particulate organic silica to water column
- Source: phytoplankton.F90 (501)
- Formula (d⁻¹): `wSiPaW = wSiMortW * (1.0_rk - self%fDOMW)`
- Code: `wSiPaW = wSiMortW * (1.0_rk - self%fDOMW)`

### `wSiSiO2W` [gSi/m3/d] *do - external fluxes Si*
- DESC: total SiO2 flux to water column
- Source: phytoplankton.F90 (503)
- Formula (d⁻¹): `wSiSiO2W = wSiExcrW + wSiO2MortW - wSiUpt`
- Code: `wSiSiO2W = wSiExcrW + wSiO2MortW - wSiUpt`

### `wSiUpt` [gSi/m3/d] *do - external fluxes Si*
- DESC: Si uptake
- Source: phytoplankton.F90 (498)
- Formula (d⁻¹): `wSiUpt = self%cSiD * wDAss`
- Code: `wSiUpt = self%cSiD * wDAss`

## do - final fluxes

### `wCW` [gC/m3/d] *do - final fluxes*
- DESC: final ROC in C
- Source: phytoplankton.F90 (466)
- Formula (d⁻¹): `wCW = wCAss - wCRespW - wCMortW`
- Code: `wCW = wCAss - wCRespW - wCMortW`

### `wDW` [gDW/m3/d] *do - final fluxes*
- DESC: final ROC in DW
- Source: phytoplankton.F90 (463)
- Formula (d⁻¹): `wDW = wDAss - wDRespW - wDMortW`
- Code: `wDW = wDAss - wDRespW - wDMortW`

### `wNW` [gN/m3/d] *do - final fluxes*
- DESC: final ROC in N
- Source: phytoplankton.F90 (465)
- Formula (d⁻¹): `wNW = wNUpt + wNFix - wNExcrW - wNMortW`
- Code: `wNW = wNUpt + wNFix - wNExcrW - wNMortW`

### `wPW` [gP/m3/d] *do - final fluxes*
- DESC: final ROC in P
- Source: phytoplankton.F90 (464)
- Formula (d⁻¹): `wPW = wPUpt - wPExcrW  - wPMortW`
- Code: `wPW = wPUpt - wPExcrW  - wPMortW`

## do - growth

### `aMu` [1/d] *do - growth*
- DESC: current growth rate
- Source: phytoplankton.F90 (419)
- Formula (d⁻¹): `aMu = aNutLim * aMuTmL * aNFixLim`
- Code: `aMu = aNutLim * aMuTmL * aNFixLim`

### `wCAss` [gC/m3/d] *do - growth*
- DESC: absolute C assimilation
- Source: phytoplankton.F90 (421)
- Formula (d⁻¹): `wCAss = wDAss * self%cCPerDW`
- Code: `wCAss = wDAss * self%cCPerDW`

### `wDAss` [gDW/m3/d] *do - growth*
- DESC: absolute dry weight assimilation
- Source: phytoplankton.F90 (420)
- Formula (d⁻¹): `wDAss = aMu*sDW`
- Code: `wDAss = aMu*sDW`

## do - light limitation

### `aLLim (case 1)` [-] *do - light limitation*
- DESC: light limitation without photoinhibition (Chalker 1980)
- Source: phytoplankton.F90 (385)
- Formula (d⁻¹): `aLLim= 1.0_rk /(extc * dz) * log((1.0_rk + uLPARSurf / uhL) / (1.0_rk + aLPARBot /uhL))`
- Code: `aLLim= 1.0_rk /(extc * dz) * log((1.0_rk + uLPARSurf / uhL) / (1.0_rk + aLPARBot /uhL))`

### `aLLim (case 2)` [-] *do - light limitation*
- DESC: light limitation with photoinhibition (Steele/Klepper 1988)
- Source: phytoplankton.F90 (388)
- Formula (d⁻¹): `aLLim = exp(1.0_rk) /(extc * dz) *(exp(- aLPARBot /uOpt) - exp(- uLPARSurf /uOpt))`
- Code: `aLLim = exp(1.0_rk) /(extc * dz) *(exp(- aLPARBot /uOpt) - exp(- uLPARSurf /uOpt))`

### `aLPARBot` [umol/m2/s] *do - light limitation*
- DESC: light at bottom of local layer
- Source: phytoplankton.F90 (381)
- Formula (d⁻¹): `aLPARBot = meanpar * EXP( -extc * dz/2.0_rk )`
- Code: `aLPARBot = meanpar * EXP( -extc * dz/2.0_rk )`

### `aMuTmL` [1/d] *do - light limitation*
- DESC: max growth rate dictated by light and temp
- Source: phytoplankton.F90 (394)
- Formula (d⁻¹): `aMuTmL = ufDay *(1.0_rk - afCovSurfVeg)*aLLim * uFunTm*self%cMuMax`
- Code: `aMuTmL = ufDay *(1.0_rk - afCovSurfVeg)*aLLim * uFunTm*self%cMuMax`

### `ufDay` [-] *do - light limitation*
- DESC: day length fraction
- Source: phytoplankton.F90 (393)
- Formula (d⁻¹): `ufDay = DayLength(lat,int(Day))`
- Code: `ufDay = DayLength(lat,int(Day))`

### `uhL (case 1)` [umol/m2/s] *do - light limitation*
- DESC: half-saturation light intensity at current temperature (Chalker 1980)
- Source: phytoplankton.F90 (384)
- Formula (d⁻¹): `uhL=self%hLRef*uFunTm`
- Code: `uhL=self%hLRef*uFunTm`

### `uLPARSurf` [umol/m2/s] *do - light limitation*
- DESC: light at top of local layer
- Source: phytoplankton.F90 (380)
- Formula (d⁻¹): `uLPARSurf = meanpar / EXP( -extc * dz/2.0_rk )`
- Code: `uLPARSurf = meanpar / EXP( -extc * dz/2.0_rk )`

### `uOpt (case 2)` [umol/m2/s] *do - light limitation*
- DESC: optimal light intensity at current temperature (Klepper 1988)
- Source: phytoplankton.F90 (387)
- Formula (d⁻¹): `uOpt=uFunTm*self%cLOptRef`
- Code: `uOpt=uFunTm*self%cLOptRef`

## do - mortality

### `wCMortW` [gC/m3/d] *do - mortality*
- DESC: mortality rate in C
- Source: phytoplankton.F90 (457)
- Formula (d⁻¹): `wCMortW = self%kMortW * sCW`
- Code: `wCMortW = self%kMortW * sCW`

### `wDMortW` [gDW/m3/d] *do - mortality*
- DESC: mortality rate in DW
- Source: phytoplankton.F90 (454)
- Formula (d⁻¹): `wDMortW = self%kMortW * sDW`
- Code: `wDMortW = self%kMortW * sDW`

### `wNMortW` [gN/m3/d] *do - mortality*
- DESC: mortality rate in N
- Source: phytoplankton.F90 (456)
- Formula (d⁻¹): `wNMortW = self%kMortW * sNW`
- Code: `wNMortW = self%kMortW * sNW`

### `wPMortW` [gP/m3/d] *do - mortality*
- DESC: mortality rate in P
- Source: phytoplankton.F90 (455)
- Formula (d⁻¹): `wPMortW = self%kMortW * sPW`
- Code: `wPMortW = self%kMortW * sPW`

## do - nutrient limitation

### `aNFix (lNfix=F)` [1/d] *do - nutrient limitation*
- DESC: current specific N fixation rate equal to zero
- Source: phytoplankton.F90 (412)
- Formula (d⁻¹): `aNFix = 0.0_rk`
- Code: `aNFix = 0.0_rk`

### `aNFix (lNfix=T)` [1/d] *do - nutrient limitation*
- DESC: current specific N fixation rate
- Source: phytoplankton.F90 (408)
- Formula (d⁻¹): `aNFix = self%cNFixMax * (1 - aNLim)`
- Code: `aNFix = self%cNFixMax * (1 - aNLim)`

### `aNFixLim (lNfix=F)` [-] *do - nutrient limitation*
- DESC: growth limitation due to N fixation equal to zero
- Source: phytoplankton.F90 (411)
- Formula (d⁻¹): `aNFixLim = 1.0_rk`
- Code: `aNFixLim = 1.0_rk`

### `aNFixLim (lNfix=T)` [-] *do - nutrient limitation*
- DESC: growth rate limitation due to N fixation
- Source: phytoplankton.F90 (407)
- Formula (d⁻¹): `aNFixLim = self%fMuNFix + aNLim*(1-self%fMuNFix)`
- Code: `aNFixLim = self%fMuNFix + aNLim*(1-self%fMuNFix)`

### `aNLim` [-] *do - nutrient limitation*
- DESC: Droop nitrogen limitation
- Source: phytoplankton.F90 (399)
- Formula (d⁻¹): `aNLim = max(0.0_rk,(1.0_rk - self%cNDMin / rNDW) * self%cNDMax /(self%cNDMax - self%cNDMin))`
- Code: `aNLim = max(0.0_rk,(1.0_rk - self%cNDMin / rNDW) * self%cNDMax /(self%cNDMax - self%cNDMin))`

### `aNutLim (lNfix=F)` [-] *do - nutrient limitation*
- DESC: total nutrient limitation without N fixation (N potentially limiting)
- Source: phytoplankton.F90 (410)
- Formula (d⁻¹): `aNutLim = min(aPLim,(min(aNLim,aSiLim)))`
- Code: `aNutLim = min(aPLim,(min(aNLim,aSiLim)))`

### `aNutLim (lNfix=T)` [-] *do - nutrient limitation*
- DESC: total nutrient limitation with N fixation (N not limiting)
- Source: phytoplankton.F90 (406)
- Formula (d⁻¹): `aNutLim = min(aPLim,aSiLim)`
- Code: `aNutLim = min(aPLim,aSiLim)`

### `aPLim` [-] *do - nutrient limitation*
- DESC: Droop phosphorus limitation
- Source: phytoplankton.F90 (398)
- Formula (d⁻¹): `aPLim = max(0.0_rk,(1.0_rk - self%cPDMin / rPDW) * self%cPDMax /(self%cPDMax - self%cPDMin))`
- Code: `aPLim = max(0.0_rk,(1.0_rk - self%cPDMin / rPDW) * self%cPDMax /(self%cPDMax - self%cPDMin))`

### `aSiLim` [-] *do - nutrient limitation*
- DESC: Monod silica limitation
- Source: phytoplankton.F90 (401)
- Formula (d⁻¹): `aSiLim = sSiO2W /(self%hSiAss + sSiO2W)`
- Code: `aSiLim = sSiO2W /(self%hSiAss + sSiO2W)`

### `aSiLim (no Si)` [-] *do - nutrient limitation*
- DESC: silica limitation when lSi=false
- Source: phytoplankton.F90 (403)
- Formula (d⁻¹): `aSiLim = 100000000.0_rk`
- Code: `aSiLim = 100000000.0_rk`

## do - nutrient uptake

### `ahNUpt` [gN/m3] *do - nutrient uptake*
- DESC: half-sat. N for uptake
- Source: phytoplankton.F90 (428)
- Formula (d⁻¹): `ahNUpt = aVNUptMaxCr / self%cAffNUpt`
- Code: `ahNUpt = aVNUptMaxCr / self%cAffNUpt`

### `aVNUpt` [1/d] *do - nutrient uptake*
- DESC: current specific N uptake rate
- Source: phytoplankton.F90 (429)
- Formula (d⁻¹): `aVNUpt = (sNO3W + sNH4W) * aVNUptMaxCr /(ahNUpt + sNO3W + sNH4W)`
- Code: `aVNUpt = (sNO3W + sNH4W) * aVNUptMaxCr /(ahNUpt + sNO3W + sNH4W)`

### `aVNUptMaxCr` [1/d] *do - nutrient uptake*
- DESC: max specific N uptake rate corrected for N/D ratio
- Source: phytoplankton.F90 (427)
- Formula (d⁻¹): `aVNUptMaxCr = max(0.0_rk,self%cVNUptMax * uFunTm * (self%cNDMax - rNDW) /(self%cNDMax - self%cNDMin))`
- Code: `aVNUptMaxCr = max(0.0_rk,self%cVNUptMax * uFunTm * (self%cNDMax - rNDW) /(self%cNDMax - self%cNDMin))`

### `aVPUpt` [1/d] *do - nutrient uptake*
- DESC: realized specific P uptake rate
- Source: phytoplankton.F90 (436)
- Formula (d⁻¹): `aVPUpt = sPO4W * aVPUptMaxCr /(aVPUptMaxCr / self%cAffPUpt + sPO4W)`
- Code: `aVPUpt = sPO4W * aVPUptMaxCr /(aVPUptMaxCr / self%cAffPUpt + sPO4W)`

### `aVPUptMaxCr` [1/d] *do - nutrient uptake*
- DESC: max specific P uptake rate corrected for P/D ratio
- Source: phytoplankton.F90 (435)
- Formula (d⁻¹): `aVPUptMaxCr = max(0.0_rk,self%cVPUptMax * uFunTm *(self%cPDMax - rPDW)/(self%cPDMax - self%cPDMin))`
- Code: `aVPUptMaxCr = max(0.0_rk,self%cVPUptMax * uFunTm *(self%cPDMax - rPDW)/(self%cPDMax - self%cPDMin))`

### `wNFix` [gN/m3/d] *do - nutrient uptake*
- DESC: absolute N fixation rate
- Source: phytoplankton.F90 (431)
- Formula (d⁻¹): `wNFix = aNFix * sDW`
- Code: `wNFix = aNFix * sDW`

### `wNUpt` [gN/m3/d] *do - nutrient uptake*
- DESC: absolute N uptake rate
- Source: phytoplankton.F90 (430)
- Formula (d⁻¹): `wNUpt = aVNUpt * sDW`
- Code: `wNUpt = aVNUpt * sDW`

### `wPUpt` [gP/m3/d] *do - nutrient uptake*
- DESC: absolute P uptake rate
- Source: phytoplankton.F90 (437)
- Formula (d⁻¹): `wPUpt = aVPUpt * sDW`
- Code: `wPUpt = aVPUpt * sDW`

## do - respiration

### `ukDRespTm` [1/d] *do - respiration*
- DESC: temperature corrected specific respiration
- Source: phytoplankton.F90 (443)
- Formula (d⁻¹): `ukDRespTm = self%kDResp * uFunTm`
- Code: `ukDRespTm = self%kDResp * uFunTm`

### `wCRespW` [gC/m3/d] *do - respiration*
- DESC: absolute respiration rate in C
- Source: phytoplankton.F90 (445)
- Formula (d⁻¹): `wCRespW = ukDRespTm * sCW`
- Code: `wCRespW = ukDRespTm * sCW`

### `wDRespW` [gDW/m3/d] *do - respiration*
- DESC: absolute respiration rate in DW
- Source: phytoplankton.F90 (444)
- Formula (d⁻¹): `wDRespW = ukDRespTm * sDW`
- Code: `wDRespW = ukDRespTm * sDW`

## do - temperature function

### `uFunTm` [-] *do - temperature function*
- DESC: Gaussian temperature function
- Source: phytoplankton.F90 (376)
- Formula (d⁻¹): `uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)`
- Code: `uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)`

## do_bottom

### `DFoodBen_ODE` [1/d] *do_bottom*
- DESC: apply consumption to zoobenthos prey DW
- Source: fish_pclake.F90 (867)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DFoodBen(i_prey),tDConsFiBen(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_DFoodBen(i_prey), tDConsFiBen(i_prey) * bot_pel_conv)`

### `DFoodBen_PV_exchange` [1/d] *do_bottom*
- DESC: update ROC of projected bottom variables (DW)
- Source: fish_pclake.F90 (870)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DFoodBen_PV(i_prey),tDConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DFoodBen_PV(i_prey), tDConsFiBen(i_prey) * bot_pel_conv * bot_pel_conv)`

### `NFoodBen_ODE` [1/d] *do_bottom*
- DESC: apply consumption to zoobenthos prey N
- Source: fish_pclake.F90 (868)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NFoodBen(i_prey),tNConsFiBen(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_NFoodBen(i_prey), tNConsFiBen(i_prey) * bot_pel_conv)`

### `NFoodBen_PV_exchange` [1/d] *do_bottom*
- DESC: update ROC of projected bottom variables (N)
- Source: fish_pclake.F90 (871)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NFoodBen_PV(i_prey),tNConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NFoodBen_PV(i_prey), tNConsFiBen(i_prey) * bot_pel_conv * bot_pel_conv)`

### `PFoodBen_ODE` [1/d] *do_bottom*
- DESC: apply consumption to zoobenthos prey P
- Source: fish_pclake.F90 (869)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PFoodBen(i_prey),tPConsFiBen(i_prey)*bot_pel_conv)`
- Code: `_SET_BOTTOM_ODE_(self%id_PFoodBen(i_prey), tPConsFiBen(i_prey) * bot_pel_conv)`

### `PFoodBen_PV_exchange` [1/d] *do_bottom*
- DESC: update ROC of projected bottom variables (P)
- Source: fish_pclake.F90 (872)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PFoodBen_PV(i_prey),tPConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PFoodBen_PV(i_prey), tPConsFiBen(i_prey) * bot_pel_conv * bot_pel_conv)`

## do_bottom - auxiliary

### `oSiS` [gSi/m2] *do_bottom - auxiliary*
- DESC: silica content of sediment phytoplankton
- Source: phytoplankton.F90 (647)
- Formula (d⁻¹): `oSiS=self%cSiD*sDS`
- Code: `oSiS=self%cSiD*sDS`

### `rCDS` [-] *do_bottom - auxiliary*
- DESC: C/D ratio sediment
- Source: phytoplankton.F90 (645)
- Formula (d⁻¹): `rCDS = sCS /(sDS+NearZero)`
- Code: `rCDS = sCS /(sDS+NearZero)`

### `rCDW` [-] *do_bottom - auxiliary*
- DESC: C/D ratio water (from water column state)
- Source: phytoplankton.F90 (655)
- Formula (d⁻¹): `rCDW = sCW /(sDW+NearZero)`
- Code: `rCDW = sCW /(sDW+NearZero)`

### `rNDS` [-] *do_bottom - auxiliary*
- DESC: N/D ratio sediment
- Source: phytoplankton.F90 (644)
- Formula (d⁻¹): `rNDS = sNS /(sDS+NearZero)`
- Code: `rNDS = sNS /(sDS+NearZero)`

### `rNDW` [-] *do_bottom - auxiliary*
- DESC: N/D ratio water (from water column state)
- Source: phytoplankton.F90 (654)
- Formula (d⁻¹): `rNDW = sNW /(sDW+NearZero)`
- Code: `rNDW = sNW /(sDW+NearZero)`

### `rPDS` [-] *do_bottom - auxiliary*
- DESC: P/D ratio sediment
- Source: phytoplankton.F90 (643)
- Formula (d⁻¹): `rPDS = sPS /(sDS+NearZero)`
- Code: `rPDS = sPS /(sDS+NearZero)`

### `rPDW` [-] *do_bottom - auxiliary*
- DESC: P/D ratio water (from water column state)
- Source: phytoplankton.F90 (653)
- Formula (d⁻¹): `rPDW = sPW /(sDW+NearZero)`
- Code: `rPDW = sPW /(sDW+NearZero)`

## do_bottom - bottom fluxes C

### `tCDOMS` [gC/m2/d] *do_bottom - bottom fluxes C*
- DESC: C DOM flux from mortality
- Source: phytoplankton.F90 (764)
- Formula (d⁻¹): `tCDOMS = tCMortS * self%fDOMS`
- Code: `tCDOMS = tCMortS * self%fDOMS`

### `tCPOMS` [gC/m2/d] *do_bottom - bottom fluxes C*
- DESC: C POM flux from mortality
- Source: phytoplankton.F90 (763)
- Formula (d⁻¹): `tCPOMS = tCMortS * (1.0_rk - self%fDOMS)`
- Code: `tCPOMS = tCMortS * (1.0_rk - self%fDOMS)`

## do_bottom - bottom fluxes DW

### `tDDOMS` [gDW/m2/d] *do_bottom - bottom fluxes DW*
- DESC: DW DOM flux from mortality
- Source: phytoplankton.F90 (737)
- Formula (d⁻¹): `tDDOMS = tDMortS * self%fDOMS`
- Code: `tDDOMS = tDMortS * self%fDOMS`

### `tDPOMS` [gDW/m2/d] *do_bottom - bottom fluxes DW*
- DESC: DW POM flux from mortality
- Source: phytoplankton.F90 (736)
- Formula (d⁻¹): `tDPOMS = tDMortS * (1.0_rk - self%fDOMS)`
- Code: `tDPOMS = tDMortS * (1.0_rk - self%fDOMS)`

## do_bottom - bottom fluxes N

### `tNDOMS` [gN/m2/d] *do_bottom - bottom fluxes N*
- DESC: DOM N flux to sediment
- Source: phytoplankton.F90 (745)
- Formula (d⁻¹): `tNDOMS = tNMortTOMS * self%fDOMS`
- Code: `tNDOMS = tNMortTOMS * self%fDOMS`

### `tNMortNH4S` [gN/m2/d] *do_bottom - bottom fluxes N*
- DESC: ammonia flux from mortality
- Source: phytoplankton.F90 (741)
- Formula (d⁻¹): `tNMortNH4S = self%fDissMort * tNMortS`
- Code: `tNMortNH4S = self%fDissMort * tNMortS`

### `tNMortTOMS` [gN/m2/d] *do_bottom - bottom fluxes N*
- DESC: organic matter N flux to sediment
- Source: phytoplankton.F90 (743)
- Formula (d⁻¹): `tNMortTOMS = tNMortS - tNMortNH4S`
- Code: `tNMortTOMS = tNMortS - tNMortNH4S`

### `tNNH4S` [gN/m2/d] *do_bottom - bottom fluxes N*
- DESC: total ammonia flux to sediment
- Source: phytoplankton.F90 (742)
- Formula (d⁻¹): `tNNH4S = tNExcrS + tNMortNH4S`
- Code: `tNNH4S = tNExcrS + tNMortNH4S`

### `tNPOMS` [gN/m2/d] *do_bottom - bottom fluxes N*
- DESC: POM N flux to sediment
- Source: phytoplankton.F90 (744)
- Formula (d⁻¹): `tNPOMS = tNMortTOMS * (1.0_rk - self%fDOMS)`
- Code: `tNPOMS = tNMortTOMS * (1.0_rk - self%fDOMS)`

## do_bottom - bottom fluxes O2

### `aCorO2BOD` [-] *do_bottom - bottom fluxes O2*
- DESC: correction of O2 demand at low oxygen conc
- Source: phytoplankton.F90 (757)
- Formula (d⁻¹): `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`
- Code: `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`

### `tO2RespS` [gO2/m2/d] *do_bottom - bottom fluxes O2*
- DESC: uptake of O2 due to respiration
- Source: phytoplankton.F90 (758)
- Formula (d⁻¹): `tO2RespS = molO2molC * tCRespS * aCorO2BOD`
- Code: `tO2RespS = molO2molC * tCRespS * aCorO2BOD`

### `tO2W` [gO2/m3/d] *do_bottom - bottom fluxes O2*
- DESC: total O2 flux to water column
- Source: phytoplankton.F90 (759)
- Formula (d⁻¹): `tO2W = tO2RespS`
- Code: `tO2W = tO2RespS`

## do_bottom - bottom fluxes P

### `tPDOMS` [gP/m2/d] *do_bottom - bottom fluxes P*
- DESC: DOM P flux to sediment
- Source: phytoplankton.F90 (753)
- Formula (d⁻¹): `tPDOMS = tPMortTOMS * self%fDOMS`
- Code: `tPDOMS = tPMortTOMS * self%fDOMS`

### `tPMortPO4S` [gP/m2/d] *do_bottom - bottom fluxes P*
- DESC: PO4 flux from mortality
- Source: phytoplankton.F90 (749)
- Formula (d⁻¹): `tPMortPO4S = self%fDissMort * tPMortS`
- Code: `tPMortPO4S = self%fDissMort * tPMortS`

### `tPMortTOMS` [gP/m2/d] *do_bottom - bottom fluxes P*
- DESC: organic matter P flux to sediment
- Source: phytoplankton.F90 (751)
- Formula (d⁻¹): `tPMortTOMS = tPMortS - tPMortPO4S`
- Code: `tPMortTOMS = tPMortS - tPMortPO4S`

### `tPPO4S` [gP/m2/d] *do_bottom - bottom fluxes P*
- DESC: total PO4 flux to sediment
- Source: phytoplankton.F90 (750)
- Formula (d⁻¹): `tPPO4S = tPExcrS + tPMortPO4S`
- Code: `tPPO4S = tPExcrS + tPMortPO4S`

### `tPPOMS` [gP/m2/d] *do_bottom - bottom fluxes P*
- DESC: POM P flux to sediment
- Source: phytoplankton.F90 (752)
- Formula (d⁻¹): `tPPOMS = tPMortTOMS * (1.0_rk - self%fDOMS)`
- Code: `tPPOMS = tPMortTOMS * (1.0_rk - self%fDOMS)`

## do_bottom - bottom fluxes Si

### `tSiExcrS` [gSi/m2/d] *do_bottom - bottom fluxes Si*
- DESC: silica excretion rate
- Source: phytoplankton.F90 (773)
- Formula (d⁻¹): `tSiExcrS = self%cSiD * tDRespS`
- Code: `tSiExcrS = self%cSiD * tDRespS`

### `tSiMortS` [gSi/m2/d] *do_bottom - bottom fluxes Si*
- DESC: silica flux from mortality
- Source: phytoplankton.F90 (770)
- Formula (d⁻¹): `tSiMortS = self%cSiD * tDMortS`
- Code: `tSiMortS = self%cSiD * tDMortS`

### `tSiO2S` [gSi/m2/d] *do_bottom - bottom fluxes Si*
- DESC: DOM part of mortality silica flux
- Source: phytoplankton.F90 (772)
- Formula (d⁻¹): `tSiO2S = tSiMortS * self%fDOMS`
- Code: `tSiO2S = tSiMortS * self%fDOMS`

### `tSiPaS` [gSi/m2/d] *do_bottom - bottom fluxes Si*
- DESC: POM part of mortality silica flux
- Source: phytoplankton.F90 (771)
- Formula (d⁻¹): `tSiPaS = tSiMortS* (1.0_rk - self%fDOMS)`
- Code: `tSiPaS = tSiMortS* (1.0_rk - self%fDOMS)`

## do_bottom - derivatives

### `CDOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment DOM C ODE
- Source: phytoplankton.F90 (815)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CDOMpoolS, tCDOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_CDOMpoolS, tCDOMS)`

### `CDOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment DOM C ODE
- Source: phytoplankton.F90 (819)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV, tCDOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV, tCDOMS*bot_pel_conv)`

### `CPOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment POM C ODE
- Source: phytoplankton.F90 (807)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCPOMS)`

### `CPOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment POM C ODE
- Source: phytoplankton.F90 (811)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCPOMS*bot_pel_conv)`

### `DDOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment DOM DW ODE
- Source: phytoplankton.F90 (812)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DDOMpoolS, tDDOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_DDOMpoolS, tDDOMS)`

### `DDOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment DOM DW ODE
- Source: phytoplankton.F90 (816)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV, tDDOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV, tDDOMS*bot_pel_conv)`

### `DPOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment POM DW ODE
- Source: phytoplankton.F90 (804)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDPOMS)`

### `DPOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment POM DW ODE
- Source: phytoplankton.F90 (808)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDPOMS*bot_pel_conv)`

### `NDOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment DOM N ODE
- Source: phytoplankton.F90 (813)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NDOMpoolS, tNDOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_NDOMpoolS, tNDOMS)`

### `NDOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment DOM N ODE
- Source: phytoplankton.F90 (817)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV, tNDOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV, tNDOMS*bot_pel_conv)`

### `NH4poolS` [-] *do_bottom - derivatives*
- DESC: update sediment NH4 ODE
- Source: phytoplankton.F90 (803)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NH4poolS, tNNH4S)`
- Code: `_SET_BOTTOM_ODE_(self%id_NH4poolS, tNNH4S)`

### `NPOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment POM N ODE
- Source: phytoplankton.F90 (805)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNPOMS)`

### `NPOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment POM N ODE
- Source: phytoplankton.F90 (809)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNPOMS*bot_pel_conv)`

### `O2poolW` [-] *do_bottom - derivatives*
- DESC: update water column O2 ODE
- Source: phytoplankton.F90 (824)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_O2poolW, tO2W)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_O2poolW, tO2W)`

### `PDOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment DOM P ODE
- Source: phytoplankton.F90 (814)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PDOMpoolS, tPDOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_PDOMpoolS, tPDOMS)`

### `PDOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment DOM P ODE
- Source: phytoplankton.F90 (818)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV, tPDOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV, tPDOMS*bot_pel_conv)`

### `PO4poolS` [-] *do_bottom - derivatives*
- DESC: update sediment PO4 ODE
- Source: phytoplankton.F90 (802)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PO4poolS, tPPO4S)`
- Code: `_SET_BOTTOM_ODE_(self%id_PO4poolS, tPPO4S)`

### `PPOMpoolS` [-] *do_bottom - derivatives*
- DESC: update sediment POM P ODE
- Source: phytoplankton.F90 (806)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPPOMS)`
- Code: `_SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPPOMS)`

### `PPOMpoolS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment POM P ODE
- Source: phytoplankton.F90 (810)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPPOMS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPPOMS*bot_pel_conv)`

### `sCS` [-] *do_bottom - derivatives*
- DESC: update sediment phytoplankton C ODE
- Source: phytoplankton.F90 (785)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sCS, tCS)`
- Code: `_SET_BOTTOM_ODE_(self%id_sCS, tCS)`

### `sCS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment phytoplankton C ODE
- Source: phytoplankton.F90 (790)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)`

### `sCW` [-] *do_bottom - derivatives*
- DESC: update water column phytoplankton C ODE
- Source: phytoplankton.F90 (797)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sCW, tCW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCW, tCW)`

### `sDS` [-] *do_bottom - derivatives*
- DESC: update sediment phytoplankton DW ODE
- Source: phytoplankton.F90 (782)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sDS, tDS)`
- Code: `_SET_BOTTOM_ODE_(self%id_sDS, tDS)`

### `sDS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment phytoplankton DW ODE
- Source: phytoplankton.F90 (787)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)`

### `sDW` [-] *do_bottom - derivatives*
- DESC: update water column phytoplankton DW ODE
- Source: phytoplankton.F90 (794)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sDW, tDW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDW, tDW)`

### `SiO2poolS` [-] *do_bottom - derivatives*
- DESC: update sediment SiO2 ODE (if lSi)
- Source: phytoplankton.F90 (822)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_SiO2poolS, tSiExcrS+tSiO2S)`
- Code: `_SET_BOTTOM_ODE_(self%id_SiO2poolS, tSiExcrS+tSiO2S)`

### `SiPapoolS` [-] *do_bottom - derivatives*
- DESC: update sediment SiPa ODE (if lSi)
- Source: phytoplankton.F90 (821)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiPaS)`
- Code: `_SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiPaS)`

### `sNS` [-] *do_bottom - derivatives*
- DESC: update sediment phytoplankton N ODE
- Source: phytoplankton.F90 (784)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sNS, tNS)`
- Code: `_SET_BOTTOM_ODE_(self%id_sNS, tNS)`

### `sNS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment phytoplankton N ODE
- Source: phytoplankton.F90 (788)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)`

### `sNW` [-] *do_bottom - derivatives*
- DESC: update water column phytoplankton N ODE
- Source: phytoplankton.F90 (795)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sNW, tNW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNW, tNW)`

### `sPS` [-] *do_bottom - derivatives*
- DESC: update sediment phytoplankton P ODE
- Source: phytoplankton.F90 (783)
- Formula (d⁻¹): `_SET_BOTTOM_ODE_(self%id_sPS, tPS)`
- Code: `_SET_BOTTOM_ODE_(self%id_sPS, tPS)`

### `sPS_PV` [-] *do_bottom - derivatives*
- DESC: update projected sediment phytoplankton P ODE
- Source: phytoplankton.F90 (789)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)`

### `sPW` [-] *do_bottom - derivatives*
- DESC: update water column phytoplankton P ODE
- Source: phytoplankton.F90 (796)
- Formula (d⁻¹): `_SET_BOTTOM_EXCHANGE_(self%id_sPW, tPW)`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPW, tPW)`

## do_bottom - excretion

### `tNExcrS` [gN/m2/d] *do_bottom - excretion*
- DESC: absolute N excretion rate
- Source: phytoplankton.F90 (686)
- Formula (d⁻¹): `tNExcrS = (2.0_rk * rNDS) /(self%cNDMax + rNDS) * rNDS * tDRespS`
- Code: `tNExcrS = (2.0_rk * rNDS) /(self%cNDMax + rNDS) * rNDS * tDRespS`

### `tPExcrS` [gP/m2/d] *do_bottom - excretion*
- DESC: absolute P excretion rate
- Source: phytoplankton.F90 (687)
- Formula (d⁻¹): `tPExcrS = (2.0_rk * rPDS) /(self%cPDMax + rPDS) * rPDS * tDRespS`
- Code: `tPExcrS = (2.0_rk * rPDS) /(self%cPDMax + rPDS) * rPDS * tDRespS`

## do_bottom - final ROC sediment

### `tCS` [gC/m2/d] *do_bottom - final ROC sediment*
- DESC: final sediment ROC in C
- Source: phytoplankton.F90 (723)
- Formula (d⁻¹): `tCS = tCSed - tCResus - tCMortS - tCRespS`
- Code: `tCS = tCSed - tCResus - tCMortS - tCRespS`

### `tDS` [gDW/m2/d] *do_bottom - final ROC sediment*
- DESC: final sediment ROC in DW
- Source: phytoplankton.F90 (720)
- Formula (d⁻¹): `tDS = tDSed - tDResus - tDMortS - tDRespS`
- Code: `tDS = tDSed - tDResus - tDMortS - tDRespS`

### `tNS` [gN/m2/d] *do_bottom - final ROC sediment*
- DESC: final sediment ROC in N
- Source: phytoplankton.F90 (721)
- Formula (d⁻¹): `tNS = tNSed - tNResus - tNMortS - tNExcrS`
- Code: `tNS = tNSed - tNResus - tNMortS - tNExcrS`

### `tPS` [gP/m2/d] *do_bottom - final ROC sediment*
- DESC: final sediment ROC in P
- Source: phytoplankton.F90 (722)
- Formula (d⁻¹): `tPS = tPSed - tPResus - tPMortS - tPExcrS`
- Code: `tPS = tPSed - tPResus - tPMortS - tPExcrS`

## do_bottom - final ROC water

### `tCW` [gC/m3/d] *do_bottom - final ROC water*
- DESC: final water column ROC in C
- Source: phytoplankton.F90 (730)
- Formula (d⁻¹): `tCW = tCResus - tCSed`
- Code: `tCW = tCResus - tCSed`

### `tDW` [gDW/m3/d] *do_bottom - final ROC water*
- DESC: final water column ROC in DW
- Source: phytoplankton.F90 (727)
- Formula (d⁻¹): `tDW = tDResus - tDSed`
- Code: `tDW = tDResus - tDSed`

### `tNW` [gN/m3/d] *do_bottom - final ROC water*
- DESC: final water column ROC in N
- Source: phytoplankton.F90 (728)
- Formula (d⁻¹): `tNW = tNResus - tNSed`
- Code: `tNW = tNResus - tNSed`

### `tPW` [gP/m3/d] *do_bottom - final ROC water*
- DESC: final water column ROC in P
- Source: phytoplankton.F90 (729)
- Formula (d⁻¹): `tPW = tPResus - tPSed`
- Code: `tPW = tPResus - tPSed`

## do_bottom - mortality

### `tCMortS` [gC/m2/d] *do_bottom - mortality*
- DESC: absolute mortality rate in C
- Source: phytoplankton.F90 (694)
- Formula (d⁻¹): `tCMortS = self%kMortS * sCS`
- Code: `tCMortS = self%kMortS * sCS`

### `tDMortS` [gDW/m2/d] *do_bottom - mortality*
- DESC: absolute mortality rate in DW
- Source: phytoplankton.F90 (691)
- Formula (d⁻¹): `tDMortS = self%kMortS * sDS`
- Code: `tDMortS = self%kMortS * sDS`

### `tNMortS` [gN/m2/d] *do_bottom - mortality*
- DESC: absolute mortality rate in N
- Source: phytoplankton.F90 (692)
- Formula (d⁻¹): `tNMortS = self%kMortS * sNS`
- Code: `tNMortS = self%kMortS * sNS`

### `tPMortS` [gP/m2/d] *do_bottom - mortality*
- DESC: absolute mortality rate in P
- Source: phytoplankton.F90 (693)
- Formula (d⁻¹): `tPMortS = self%kMortS * sPS`
- Code: `tPMortS = self%kMortS * sPS`

## do_bottom - respiration

### `tCRespS` [gC/m2/d] *do_bottom - respiration*
- DESC: absolute respiration rate in C
- Source: phytoplankton.F90 (682)
- Formula (d⁻¹): `tCRespS = ukDRespTm * sCS`
- Code: `tCRespS = ukDRespTm * sCS`

### `tDRespS` [gDW/m2/d] *do_bottom - respiration*
- DESC: absolute respiration rate in DW
- Source: phytoplankton.F90 (681)
- Formula (d⁻¹): `tDRespS = ukDRespTm * sDS`
- Code: `tDRespS = ukDRespTm * sDS`

### `ukDRespTm` [1/d] *do_bottom - respiration*
- DESC: temperature corrected specific respiration
- Source: phytoplankton.F90 (680)
- Formula (d⁻¹): `ukDRespTm = self%kDResp * uFunTm`
- Code: `ukDRespTm = self%kDResp * uFunTm`

## do_bottom - resuspension

### `akResusRef` [1/d] *do_bottom - resuspension*
- DESC: corrected daily resuspension rate
- Source: phytoplankton.F90 (709)
- Formula (d⁻¹): `akResusRef = self%kResusMax * (1.0_rk - exp(self%cResusExp * tDResusDead))`
- Code: `akResusRef = self%kResusMax * (1.0_rk - exp(self%cResusExp * tDResusDead))`

### `tCResus` [gC/m2/d] *do_bottom - resuspension*
- DESC: absolute resuspension flux in C
- Source: phytoplankton.F90 (714)
- Formula (d⁻¹): `tCResus = rCDS * tDResus`
- Code: `tCResus = rCDS * tDResus`

### `tDResus` [gDW/m2/d] *do_bottom - resuspension*
- DESC: absolute resuspension flux in DW
- Source: phytoplankton.F90 (711)
- Formula (d⁻¹): `tDResus=akResusRef*sDS`
- Code: `tDResus=akResusRef*sDS`

### `tNResus` [gN/m2/d] *do_bottom - resuspension*
- DESC: absolute resuspension flux in N
- Source: phytoplankton.F90 (712)
- Formula (d⁻¹): `tNResus = rNDS * tDResus`
- Code: `tNResus = rNDS * tDResus`

### `tPResus` [gP/m2/d] *do_bottom - resuspension*
- DESC: absolute resuspension flux in P
- Source: phytoplankton.F90 (713)
- Formula (d⁻¹): `tPResus = rPDS * tDResus`
- Code: `tPResus = rPDS * tDResus`

## do_bottom - settling

### `tCSed` [gC/m2/d] *do_bottom - settling*
- DESC: absolute settlement flux in C
- Source: phytoplankton.F90 (705)
- Formula (d⁻¹): `tCSed = rCDW * tDSed`
- Code: `tCSed = rCDW * tDSed`

### `tDSed` [gDW/m2/d] *do_bottom - settling*
- DESC: absolute settlement flux in DW
- Source: phytoplankton.F90 (702)
- Formula (d⁻¹): `tDSed = uCorVSed * sDW`
- Code: `tDSed = uCorVSed * sDW`

### `tNSed` [gN/m2/d] *do_bottom - settling*
- DESC: absolute settlement flux in N
- Source: phytoplankton.F90 (703)
- Formula (d⁻¹): `tNSed = rNDW * tDSed`
- Code: `tNSed = rNDW * tDSed`

### `tPSed` [gP/m2/d] *do_bottom - settling*
- DESC: absolute settlement flux in P
- Source: phytoplankton.F90 (704)
- Formula (d⁻¹): `tPSed = rPDW * tDSed`
- Code: `tPSed = rPDW * tDSed`

### `uCorVSed` [m/d] *do_bottom - settling*
- DESC: corrected daily sedimentation rate
- Source: phytoplankton.F90 (700)
- Formula (d⁻¹): `uCorVSed = self%cVSed * aFunTauTmSet`
- Code: `uCorVSed = self%cVSed * aFunTauTmSet`

## do_bottom - temperature function

### `uFunTm` [-] *do_bottom - temperature function*
- DESC: Gaussian temperature function
- Source: phytoplankton.F90 (676)
- Formula (d⁻¹): `uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)`
- Code: `uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)`

## Effective biomass

### `sCPisc` [gC/m3] *Effective biomass*
- DESC: apply vulnerability fraction to fish prey C
- Source: fish.F90 (596)
- Formula (d⁻¹): `sCPisc=sCPisc*fVulPisc`
- Code: `sCPisc=sCPisc*fVulPisc`

### `sDFiEff` [gDW/m3] *Effective biomass*
- DESC: calculate effective biomass of fish (ignoring condition)
- Source: fish.F90 (532)
- Formula (d⁻¹): `sDFiEff = sDFi - sFRes*sDFi + sDFi*(self%fResMax-self%fGonad)`
- Code: `sDFiEff = sDFi - sFRes*sDFi + sDFi*(self%fResMax-self%fGonad)`

### `sDPisc` [gDW/m3] *Effective biomass*
- DESC: apply vulnerability fraction to fish prey biomass
- Source: fish.F90 (593)
- Formula (d⁻¹): `sDPisc=sDPisc*fVulPisc`
- Code: `sDPisc=sDPisc*fVulPisc`

### `sNPisc` [gN/m3] *Effective biomass*
- DESC: apply vulnerability fraction to fish prey N
- Source: fish.F90 (594)
- Formula (d⁻¹): `sNPisc=sNPisc*fVulPisc`
- Code: `sNPisc=sNPisc*fVulPisc`

### `sPPisc` [gP/m3] *Effective biomass*
- DESC: apply vulnerability fraction to fish prey P
- Source: fish.F90 (595)
- Formula (d⁻¹): `sPPisc=sPPisc*fVulPisc`
- Code: `sPPisc=sPPisc*fVulPisc`

## Egestion

### `tDEgesFi` [1/d] *Egestion*
- DESC: DW egestion rate
- Source: fish_pclake.F90 (626)
- Formula (d⁻¹): `tDEgesFi = tDConsFiTot - tDAssFiTot`
- Code: `tDEgesFi = tDConsFiTot - tDAssFiTot`

### `tNEgesFi` [1/d] *Egestion*
- DESC: N egestion rate
- Source: fish_pclake.F90 (628)
- Formula (d⁻¹): `tNEgesFi = tNConsFiTot - tNAssFiTot`
- Code: `tNEgesFi = tNConsFiTot - tNAssFiTot`

### `tPEgesFi` [1/d] *Egestion*
- DESC: P egestion rate
- Source: fish_pclake.F90 (627)
- Formula (d⁻¹): `tPEgesFi = tPConsFiTot - tPAssFiTot`
- Code: `tPEgesFi = tPConsFiTot - tPAssFiTot`

### `tCEgesBiv` [g/m2/s] *Egestion*
- DESC: C egestion (goes to POMC)
- Source: bivalves.F90 (514)
- Formula (d⁻¹): `tCEgesBiv = tDEgesBiv * rCDBiv`
- Code: `tCEgesBiv = tDEgesBiv * rCDBiv`

### `tDEgesBiv` [g/m2/s] *Egestion*
- DESC: DW egestion (goes to POM)
- Source: bivalves.F90 (511)
- Formula (d⁻¹): `tDEgesBiv = tDAssBiv * self%fRegst * exp(self%cgegst*min(total_food_DW/self%hKfood,1.0))`
- Code: `tDEgesBiv = tDAssBiv * self%fRegst * exp(self%cgegst*min(total_food_DW/self%hKfood,1.0))`

### `tDpseudofaecesBiv` [g/m2/s] *Egestion*
- DESC: pseudofaeces in DW diagnostic
- Source: bivalves.F90 (495)
- Formula (d⁻¹): `tDpseudofaecesBiv = (1.0 - self%fDAssBiv) * tDConsBivTot`
- Code: `tDpseudofaecesBiv = (1.0 - self%fDAssBiv) * tDConsBivTot`

### `tNEgesBiv` [g/m2/s] *Egestion*
- DESC: N egestion (goes to POMN)
- Source: bivalves.F90 (512)
- Formula (d⁻¹): `tNEgesBiv = tDEgesBiv * rNDBiv`
- Code: `tNEgesBiv = tDEgesBiv * rNDBiv`

### `tPEgesBiv` [g/m2/s] *Egestion*
- DESC: P egestion (goes to POMP)
- Source: bivalves.F90 (513)
- Formula (d⁻¹): `tPEgesBiv = tDEgesBiv * rPDBiv`
- Code: `tPEgesBiv = tDEgesBiv * rPDBiv`

## Energy allocation

### `fIrreversible` [-] *Energy allocation*
- DESC: calculate allocation of growth to structural mass
- Source: fish.F90 (883)
- Formula (d⁻¹): `fIrreversible = 1.0_rk/((1.0_rk+q)*q) * fRes_now`
- Code: `fIrreversible = 1.0_rk/((1.0_rk+q)*q)   *   fRes_now`

### `fRes_now` [-] *Energy allocation*
- DESC: calculate current q value (Persson & de Roos 1998)
- Source: fish.F90 (879)
- Formula (d⁻¹): `fRes_now = sFRes/(1.0_rk-sFRes)`
- Code: `fRes_now = sFRes/(1.0_rk-sFRes)`

### `q` [-] *Energy allocation*
- DESC: adapted from Persson & de Roos 1998
- Source: fish.F90 (882)
- Formula (d⁻¹): `q=self%fResMax/(1.0_rk-self%fResMax)`
- Code: `q=self%fResMax/(1.0_rk-self%fResMax)`

### `rG` [-] *Energy allocation*
- DESC: calculate specific growth rate
- Source: fish.F90 (878)
- Formula (d⁻¹): `rG = (tDAssFiTot - tDRespFi)/sDFi`
- Code: `rG = (tDAssFiTot - tDRespFi)/sDFi`

### `tDSiz` [-] *Energy allocation*
- DESC: if size less than max and reserve fraction larger than min, average size grows
- Source: fish.F90 (880)
- Formula (d⁻¹): `tDSiz = rG*sDSiz`
- Code: `tDSiz = rG*sDSiz [if sDSiz < self%cDfin .AND. sFRes > self%fResMin]`

### `tFRes` [-] *Energy allocation*
- DESC: calculate reserve fraction rate of change (net positive growth)
- Source: fish.F90 (884)
- Formula (d⁻¹): `tFRes = ((1._rk-fIrreversible)-sFRes)*((tDAssFiTot - tDRespFi)/sDFi)`
- Code: `tFRes = ((1._rk-fIrreversible)-sFRes)*((tDAssFiTot - tDRespFi)/sDFi)`

### `tFRes` [-] *Energy allocation*
- DESC: calculate reserve fraction rate of change (net growth negative)
- Source: fish.F90 (886)
- Formula (d⁻¹): `tFRes = (1.0_rk-sFRes)*((tDAssFiTot - tDRespFi)/sDFi)`
- Code: `tFRes = (1.0_rk-sFRes)*((tDAssFiTot - tDRespFi)/sDFi)`

## Erosion

### `tCBurDOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of C in DOM (zero)
- Source: burial.F90 (379)
- Formula (d⁻¹): `tCBurDOM = 0.0_rk`
- Code: `tCBurDOM = 0.0_rk`

### `tCBurPOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of C in POM (zero)
- Source: burial.F90 (378)
- Formula (d⁻¹): `tCBurPOM = 0.0_rk`
- Code: `tCBurPOM = 0.0_rk`

### `tDBurDOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of DW in DOM (zero)
- Source: burial.F90 (357)
- Formula (d⁻¹): `tDBurDOM = 0.0_rk`
- Code: `tDBurDOM = 0.0_rk`

### `tDBurIM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of DW in inorganic matter (erosion)
- Source: burial.F90 (353-354)
- Formula (d⁻¹): `tDBurIM = (tDPOMS +(self%cRhoOM / self%cRhoIM) * tDAbioIMS) / (self%fDOrgSoil /(1.0_rk - self%fDOrgSoil) + self%cRhoOM / self%cRhoIM)`
- Code: `tDBurIM = ( tDPOMS +(self%cRhoOM / self%cRhoIM) * tDAbioIMS) / (self%fDOrgSoil /(1.0_rk - self%fDOrgSoil) + self%cRhoOM / self%cRhoIM)`

### `tDBurOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of DW in organic matter (erosion)
- Source: burial.F90 (355)
- Formula (d⁻¹): `tDBurOM = self%fDOrgSoil /(1.0 - self%fDOrgSoil) * tDBurIM`
- Code: `tDBurOM = self%fDOrgSoil /(1.0 - self%fDOrgSoil) * tDBurIM`

### `tDBurPOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of DW in POM (zero)
- Source: burial.F90 (356)
- Formula (d⁻¹): `tDBurPOM = 0.0_rk`
- Code: `tDBurPOM = 0.0_rk`

### `tNBurDOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of N in DOM (zero)
- Source: burial.F90 (371)
- Formula (d⁻¹): `tNBurDOM = 0.0_rk`
- Code: `tNBurDOM = 0.0_rk`

### `tNBurPOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of N in POM (zero)
- Source: burial.F90 (370)
- Formula (d⁻¹): `tNBurPOM = 0.0_rk`
- Code: `tNBurPOM = 0.0_rk`

### `tPBurAIM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of P adsorbed onto IM (zero)
- Source: burial.F90 (364)
- Formula (d⁻¹): `tPBurAIM = 0.0_rk`
- Code: `tPBurAIM = 0.0_rk`

### `tPBurDOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of P in DOM (zero)
- Source: burial.F90 (363)
- Formula (d⁻¹): `tPBurDOM = 0.0_rk`
- Code: `tPBurDOM = 0.0_rk`

### `tPBurPOM` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of P in POM (zero)
- Source: burial.F90 (362)
- Formula (d⁻¹): `tPBurPOM = 0.0_rk`
- Code: `tPBurPOM = 0.0_rk`

### `tSiBurPa` [g/m2/s] *Erosion*
- DESC: case vDeltaS<0: burial flux of particulate Si (zero)
- Source: burial.F90 (384)
- Formula (d⁻¹): `tSiBurPa = 0.0_rk`
- Code: `tSiBurPa = 0.0_rk`

## Excretion

### `wNExcrZoo` [gN/m3/s] *Excretion*
- DESC: calculate N excretion
- Source: zooplankton.F90 (333)
- Formula (d⁻¹): `rNDZoo / cNDRef * kDRespZoo * uFunTmZoo * sNZoo`
- Code: `wNExcrZoo = rNDZoo / self%cNDRef * self%kDRespZoo * uFunTmZoo * sNZoo`

### `wPExcrZoo` [gP/m3/s] *Excretion*
- DESC: calculate P excretion
- Source: zooplankton.F90 (334)
- Formula (d⁻¹): `rPDZoo / cPDRef * kDRespZoo * uFunTmZoo * sPZoo`
- Code: `wPExcrZoo = rPDZoo / self%cPDRef * self%kDRespZoo * uFunTmZoo * sPZoo`

### `tNExcrBent` [gN/m2/s] *Excretion*
- DESC: calculate N excretion
- Source: zoobenthos.F90 (369)
- Formula (d⁻¹): `(rNDBent / cNDRef) * kDRespBent * uFunTmBent * fO2 * sNBent`
- Code: `tNExcrBent = (rNDBent / self%cNDRef) * self%kDRespBent * uFunTmBent * fO2 * sNBent`

### `tPExcrBent` [gP/m2/s] *Excretion*
- DESC: calculate P excretion
- Source: zoobenthos.F90 (368)
- Formula (d⁻¹): `(rPDBent / cPDRef) * kDRespBent * uFunTmBent * fO2 * sPBent`
- Code: `tPExcrBent = (rPDBent / self%cPDRef) * self%kDRespBent * uFunTmBent * fO2 * sPBent`

### `tNExcrVeg` [gN/m2/s] *Excretion*
- DESC: N excretion by macrophytes
- Source: macrophytes.F90 (539)
- Formula (d⁻¹): `(2.0*rNDVeg)/(cNDVegMax + rNDVeg) * rNDVeg * tDRespVeg`
- Code: `tNExcrVeg = (2.0_rk * rNDVeg)/(self%cNDVegMax + rNDVeg) * rNDVeg * tDRespVeg`

### `tPExcrVeg` [gP/m2/s] *Excretion*
- DESC: P excretion by macrophytes
- Source: macrophytes.F90 (540)
- Formula (d⁻¹): `rPDVeg/(cPDVegMin + rPDVeg) * rPDVeg * tDRespVeg`
- Code: `tPExcrVeg = rPDVeg/(self%cPDVegMin + rPDVeg) * rPDVeg * tDRespVeg`

### `tNExcrFi` [-] *Excretion*
- DESC: calculate N excretion rate (dynamic)
- Source: fish.F90 (836)
- Formula (d⁻¹): `tNExcrFi = (rNDFi / self%cNDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sNFi`
- Code: `tNExcrFi = (rNDFi / self%cNDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sNFi`

### `tNExcrFi` [-] *Excretion*
- DESC: calculate N excretion rate (fixed)
- Source: fish.F90 (840)
- Formula (d⁻¹): `tNExcrFi = tDRespFi * self%cNDRef`
- Code: `tNExcrFi = tDRespFi * self%cNDRef`

### `tPExcrFi` [-] *Excretion*
- DESC: calculate P excretion rate (dynamic)
- Source: fish.F90 (835)
- Formula (d⁻¹): `tPExcrFi = (rPDFi / self%cPDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sPFi`
- Code: `tPExcrFi = (rPDFi / self%cPDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sPFi`

### `tPExcrFi` [-] *Excretion*
- DESC: calculate P excretion rate (fixed)
- Source: fish.F90 (839)
- Formula (d⁻¹): `tPExcrFi = tDRespFi * self%cPDRef`
- Code: `tPExcrFi = tDRespFi * self%cPDRef`

### `tNExcrBiv` [g/m2/s] *Excretion*
- DESC: N excretion (goes to NH4)
- Source: bivalves.F90 (505)
- Formula (d⁻¹): `tNExcrBiv = (rNDBiv / self%cNDRef) * tDRespBiv * sNBiv`
- Code: `tNExcrBiv = (rNDBiv / self%cNDRef) * tDRespBiv * sNBiv`

### `tPExcrBiv` [g/m2/s] *Excretion*
- DESC: P excretion (goes to PO4)
- Source: bivalves.F90 (506)
- Formula (d⁻¹): `tPExcrBiv = (rPDBiv / self%cPDRef) * tDRespBiv * sPBiv`
- Code: `tPExcrBiv = (rPDBiv / self%cPDRef) * tDRespBiv * sPBiv`

## External fluxes

### `tCMigrFi` [-] *External fluxes*
- DESC: calculate change in C from migration
- Source: fish.F90 (863)
- Formula (d⁻¹): `tCMigrFi = self%kMigrFish *(self%cCDRef * self%cDFiIn - sCFi)`
- Code: `tCMigrFi = self%kMigrFish *(self%cCDRef * self%cDFiIn - sCFi)`

### `tDMigrFi` [-] *External fluxes*
- DESC: calculate current migration rate
- Source: fish.F90 (860)
- Formula (d⁻¹): `tDMigrFi = self%kMigrFish *(self%cDFiIn - sDFi)`
- Code: `tDMigrFi = self%kMigrFish *(self%cDFiIn - sDFi)`

### `tNMigrFi` [-] *External fluxes*
- DESC: calculate change in N from migration
- Source: fish.F90 (862)
- Formula (d⁻¹): `tNMigrFi = self%kMigrFish *(self%cNDRef * self%cDFiIn - sNFi)`
- Code: `tNMigrFi = self%kMigrFish *(self%cNDRef * self%cDFiIn - sNFi)`

### `tPMigrFi` [-] *External fluxes*
- DESC: calculate change in P from migration
- Source: fish.F90 (861)
- Formula (d⁻¹): `tPMigrFi = self%kMigrFish *(self%cPDRef * self%cDFiIn - sPFi)`
- Code: `tPMigrFi = self%kMigrFish *(self%cPDRef * self%cDFiIn - sPFi)`

## Feeding/Consumption

### `aFeedLvlZoo (ODB final)` [-] *Feeding/Consumption*
- DESC: calculate final feeding level, ignoring not included prey
- Source: zooplankton.F90 (557)
- Formula (d⁻¹): `sum(incl*cClearPrey*fGutOccPrey*sDPrey)/(sum(incl*cClearPrey*fGutOccPrey*sDPrey) + uFunTmZoo*kDConsMaxZoo)`
- Code: `aFeedLvl = sum(incl*self%cClearPrey*self%fGutOccPrey*sDPrey)/(sum(incl*self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmZoo*self%kDConsMaxZoo)`

### `aFeedLvlZoo (ODB iter)` [-] *Feeding/Consumption*
- DESC: calculate feeding level using included prey
- Source: zooplankton.F90 (547-548)
- Formula (d⁻¹): `sum(cClearPrey*fGutOccPrey*sDPrey*incl) / (sum(cClearPrey*fGutOccPrey*sDPrey*incl) + uFunTmZoo*kDConsMaxZoo)`
- Code: `aFeedLvl = sum(self%cClearPrey*self%fGutOccPrey*sDPrey*incl)/ (sum(self%cClearPrey*self%fGutOccPrey*sDPrey*incl) + uFunTmZoo*self%kDConsMaxZoo)`

### `aFeedLvlZoo (qODB=0)` [-] *Feeding/Consumption*
- DESC: calculate feeding level, based on all available zoop. prey
- Source: zooplankton.F90 (286-287)
- Formula (d⁻¹): `sum(cClearPrey*fGutOccPrey*sDPrey) / (sum(cClearPrey*fGutOccPrey*sDPrey) + uFunTmZoo*kDConsMaxZoo)`
- Code: `aFeedLvlZoo = sum(self%cClearPrey*self%fGutOccPrey*sDPrey) / (sum(self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmZoo*self%kDConsMaxZoo)`

### `FoodProf` [-] *Feeding/Consumption*
- DESC: calculate food profitabilities (ODB)
- Source: zooplankton.F90 (532)
- Formula (d⁻¹): `1.0_rk/fGutOccPrey`
- Code: `FoodProf = 1.0_rk/self%fGutOccPrey`

### `wCConsZoo` [gC/m3/s] *Feeding/Consumption*
- DESC: calculate prey C consumption (dimensions: nPrey)
- Source: zooplankton.F90 (300)
- Formula (d⁻¹): `wDConsZoo * rCDprey`
- Code: `wCConsZoo = wDConsZoo * rCDprey`

### `wCConsZooTot` [gC/m3/s] *Feeding/Consumption*
- DESC: calculate total prey C consumption
- Source: zooplankton.F90 (304)
- Formula (d⁻¹): `sum(wCConsZoo)`
- Code: `wCConsZooTot = sum(wCConsZoo)`

### `wCEgesZoo` [gC/m3/s] *Feeding/Consumption*
- DESC: calculate C egestion
- Source: zooplankton.F90 (341)
- Formula (d⁻¹): `wCConsZooTot - wCAssZoo`
- Code: `wCEgesZoo = wCConsZooTot - wCAssZoo`

### `wDConsZoo (ODB final)` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate final consumption of all food, ignoring not included food
- Source: zooplankton.F90 (558)
- Formula (d⁻¹): `sDZoo*incl*cClearPrey*sDPrey*(1-aFeedLvl)`
- Code: `wDConsZoo = sDZoo*incl*self%cClearPrey*sDPrey*(1-aFeedLvl)`

### `wDConsZoo (qODB=0)` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate consumption of all available zoop. prey
- Source: zooplankton.F90 (288)
- Formula (d⁻¹): `sDZoo*cClearPrey*sDPrey*(1-aFeedLvlZoo)`
- Code: `wDConsZoo = sDZoo*self%cClearPrey*sDPrey*(1-aFeedLvlZoo)`

### `wDConsZoo (qODB=1)` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate ODB for planktivory
- Source: zooplankton.F90 (290)
- Formula (d⁻¹): `calc_ODB(wDConsZoo,aFeedLvlZoo,sDPrey,uFunTmZoo,sDZoo)`
- Code: `call self%calc_ODB(wDConsZoo,aFeedLvlZoo,sDPrey,uFunTmZoo,sDZoo)`

### `wDConsZoo_temp (ODB)` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate consumption of included prey
- Source: zooplankton.F90 (549)
- Formula (d⁻¹): `sDZoo*cClearPrey*sDPrey*incl*(1-aFeedLvl)`
- Code: `wDConsZoo_temp = sDZoo*self%cClearPrey*sDPrey*incl*(1-aFeedLvl)`

### `wDConsZooTot` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate total prey DW consumption
- Source: zooplankton.F90 (301)
- Formula (d⁻¹): `sum(wDConsZoo)`
- Code: `wDConsZooTot = sum(wDConsZoo)`

### `wDEgesZoo` [gDW/m3/s] *Feeding/Consumption*
- DESC: calculate DW egestion
- Source: zooplankton.F90 (338)
- Formula (d⁻¹): `wDConsZooTot - wDAssZoo`
- Code: `wDEgesZoo = wDConsZooTot - wDAssZoo`

### `wNConsZoo` [gN/m3/s] *Feeding/Consumption*
- DESC: calculate prey N consumption (dimensions: nPrey)
- Source: zooplankton.F90 (298)
- Formula (d⁻¹): `wDConsZoo * rNDprey`
- Code: `wNConsZoo = wDConsZoo * rNDprey`

### `wNConsZooTot` [gN/m3/s] *Feeding/Consumption*
- DESC: calculate total prey N consumption
- Source: zooplankton.F90 (302)
- Formula (d⁻¹): `sum(wNConsZoo)`
- Code: `wNConsZooTot = sum(wNConsZoo)`

### `wNEgesZoo` [gN/m3/s] *Feeding/Consumption*
- DESC: calculate N egestion
- Source: zooplankton.F90 (339)
- Formula (d⁻¹): `wNConsZooTot - wNAssZoo`
- Code: `wNEgesZoo = wNConsZooTot - wNAssZoo`

### `wPConsZoo` [gP/m3/s] *Feeding/Consumption*
- DESC: calculate prey P consumption (dimensions: nPrey)
- Source: zooplankton.F90 (299)
- Formula (d⁻¹): `wDConsZoo * rPDprey`
- Code: `wPConsZoo = wDConsZoo * rPDprey`

### `wPConsZooTot` [gP/m3/s] *Feeding/Consumption*
- DESC: calculate total prey P consumption
- Source: zooplankton.F90 (303)
- Formula (d⁻¹): `sum(wPConsZoo)`
- Code: `wPConsZooTot = sum(wPConsZoo)`

### `wPEgesZoo` [gP/m3/s] *Feeding/Consumption*
- DESC: calculate P egestion
- Source: zooplankton.F90 (340)
- Formula (d⁻¹): `wPConsZooTot - wPAssZoo`
- Code: `wPEgesZoo = wPConsZooTot - wPAssZoo`

### `aFeedLvlBent` [-] *Feeding/Consumption*
- DESC: calculate feeding level, based on all available zoobenthos prey
- Source: zoobenthos.F90 (322-323)
- Formula (d⁻¹): `sum(cClearPrey*fGutOccPrey*sDPrey) / (sum(cClearPrey*fGutOccPrey*sDPrey) + uFunTmBent*fO2*kDConsMaxBent)`
- Code: `aFeedLvlBent = sum(self%cClearPrey*self%fGutOccPrey*sDPrey) / (sum(self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmBent*fO2*self%kDConsMaxBent)`

### `tCConsBent` [gC/m2/s] *Feeding/Consumption*
- DESC: calculate prey C consumption (dimensions: nPrey)
- Source: zoobenthos.F90 (334)
- Formula (d⁻¹): `tDConsBent * rCDprey`
- Code: `tCConsBent = tDConsBent * rCDprey`

### `tCConsBentTot` [gC/m2/s] *Feeding/Consumption*
- DESC: calculate total prey C consumption
- Source: zoobenthos.F90 (338)
- Formula (d⁻¹): `sum(tCConsBent)`
- Code: `tCConsBentTot = sum(tCConsBent)`

### `tCEgesBent` [gC/m2/s] *Feeding/Consumption*
- DESC: calculate C egestion
- Source: zoobenthos.F90 (376)
- Formula (d⁻¹): `tCConsBentTot - tCAssBent`
- Code: `tCEgesBent = tCConsBentTot - tCAssBent`

### `tDConsBent` [gDW/m2/s] *Feeding/Consumption*
- DESC: calculate consumption of all available zoobenthos prey
- Source: zoobenthos.F90 (324)
- Formula (d⁻¹): `sDBent*cClearPrey*sDPrey*(1-aFeedLvlBent)`
- Code: `tDConsBent = sDBent*self%cClearPrey*sDPrey*(1-aFeedLvlBent)`

### `tDConsBentTot` [gDW/m2/s] *Feeding/Consumption*
- DESC: calculate total prey DW consumption
- Source: zoobenthos.F90 (335)
- Formula (d⁻¹): `sum(tDConsBent)`
- Code: `tDConsBentTot = sum(tDConsBent)`

### `tDEgesBent` [gDW/m2/s] *Feeding/Consumption*
- DESC: calculate DW egestion
- Source: zoobenthos.F90 (373)
- Formula (d⁻¹): `tDConsBentTot - tDAssBent`
- Code: `tDEgesBent = tDConsBentTot - tDAssBent`

### `tNConsBent` [gN/m2/s] *Feeding/Consumption*
- DESC: calculate prey N consumption (dimensions: nPrey)
- Source: zoobenthos.F90 (332)
- Formula (d⁻¹): `tDConsBent * rNDprey`
- Code: `tNConsBent = tDConsBent * rNDprey`

### `tNConsBentTot` [gN/m2/s] *Feeding/Consumption*
- DESC: calculate total prey N consumption
- Source: zoobenthos.F90 (336)
- Formula (d⁻¹): `sum(tNConsBent)`
- Code: `tNConsBentTot = sum(tNConsBent)`

### `tNEgesBent` [gN/m2/s] *Feeding/Consumption*
- DESC: calculate N egestion
- Source: zoobenthos.F90 (374)
- Formula (d⁻¹): `tNConsBentTot - tNAssBent`
- Code: `tNEgesBent = tNConsBentTot - tNAssBent`

### `tPConsBent` [gP/m2/s] *Feeding/Consumption*
- DESC: calculate prey P consumption (dimensions: nPrey)
- Source: zoobenthos.F90 (333)
- Formula (d⁻¹): `tDConsBent * rPDprey`
- Code: `tPConsBent = tDConsBent * rPDprey`

### `tPConsBentTot` [gP/m2/s] *Feeding/Consumption*
- DESC: calculate total prey P consumption
- Source: zoobenthos.F90 (337)
- Formula (d⁻¹): `sum(tPConsBent)`
- Code: `tPConsBentTot = sum(tPConsBent)`

### `tPEgesBent` [gP/m2/s] *Feeding/Consumption*
- DESC: calculate P egestion
- Source: zoobenthos.F90 (375)
- Formula (d⁻¹): `tPConsBentTot - tPAssBent`
- Code: `tPEgesBent = tPConsBentTot - tPAssBent`

### `aFeedLvlBent` [-] *Feeding/Consumption*
- DESC: calculate feeding level benthos (ODB off)
- Source: fish.F90 (637-638)
- Formula (d⁻¹): `aFeedLvlBent = aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent)/(aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent) + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlBent = aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent)/ (aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent) + uFunTmFish*kDConsMax)`

### `aFeedLvlBent` [-] *Feeding/Consumption*
- DESC: calculate feeding level benthos (final, with fFeed)
- Source: fish.F90 (715-716)
- Formula (d⁻¹): `aFeedLvlBent = aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed/(aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlBent = aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed/ (aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed + uFunTmFish*kDConsMax)`

### `aFeedLvlPisc` [-] *Feeding/Consumption*
- DESC: calculate feeding level fish prey (ODB off)
- Source: fish.F90 (639-640)
- Formula (d⁻¹): `aFeedLvlPisc = sum(self%cClearPisc*self%fGutOccPisc*sDPisc)/(sum(self%cClearPisc*self%fGutOccPisc*sDPisc) + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPisc = sum(self%cClearPisc*self%fGutOccPisc*sDPisc)/ (sum(self%cClearPisc*self%fGutOccPisc*sDPisc) + uFunTmFish*kDConsMax)`

### `aFeedLvlPisc` [-] *Feeding/Consumption*
- DESC: calculate feeding level fish prey (final, with fFeed)
- Source: fish.F90 (717-718)
- Formula (d⁻¹): `aFeedLvlPisc = sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed/(sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPisc = sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed/ (sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed + uFunTmFish*kDConsMax)`

### `aFeedLvlPlan` [-] *Feeding/Consumption*
- DESC: calculate feeding level plankton (ODB off)
- Source: fish.F90 (635-636)
- Formula (d⁻¹): `aFeedLvlPlan = aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan)/(aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan) + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPlan = aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan)/ (aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan) + uFunTmFish*kDConsMax)`

### `aFeedLvlPlan` [-] *Feeding/Consumption*
- DESC: calculate feeding level plankton (final, with fFeed)
- Source: fish.F90 (713-714)
- Formula (d⁻¹): `aFeedLvlPlan = aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed/(aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPlan = aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed/ (aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed + uFunTmFish*kDConsMax)`

### `fFishBent` [-] *Feeding/Consumption*
- DESC: time allocation to bentivory weighted by all consumption
- Source: fish.F90 (664)
- Formula (d⁻¹): `fFishBent = tDConsFiBentTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`
- Code: `fFishBent = tDConsFiBentTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`

### `fFishPisc` [-] *Feeding/Consumption*
- DESC: time allocation to piscivory weighted by all consumption
- Source: fish.F90 (665)
- Formula (d⁻¹): `fFishPisc = tDConsFiPiscTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`
- Code: `fFishPisc = tDConsFiPiscTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`

### `fFishPlan` [-] *Feeding/Consumption*
- DESC: time allocation to planktivory weighted by all consumption
- Source: fish.F90 (663)
- Formula (d⁻¹): `fFishPlan = tDConsFiPlanTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`
- Code: `fFishPlan = tDConsFiPlanTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)`

### `kDConsMax` [gDW/gDW/d] *Feeding/Consumption*
- DESC: limit max consumption as average size approaches max size
- Source: fish.F90 (630)
- Formula (d⁻¹): `kDConsMax = min(self%kDConsMax,max(NearZero,self%kDConsMax*(1._rk-(sDSiz-self%cDinit)/(self%cDfin-self%cDinit))))`
- Code: `kDConsMax = min(self%kDConsMax,max(NearZero,self%kDConsMax*(1._rk-(sDSiz-self%cDinit)/(self%cDfin-self%cDinit))))`

### `tCConsFiBent` [-] *Feeding/Consumption*
- DESC: calculate C consumption of benthos
- Source: fish.F90 (755)
- Formula (d⁻¹): `tCConsFiBent = rCDBent * tDConsFiBent`
- Code: `tCConsFiBent = rCDBent * tDConsFiBent`

### `tCConsFiPisc` [-] *Feeding/Consumption*
- DESC: calculate C consumption of fish
- Source: fish.F90 (761)
- Formula (d⁻¹): `tCConsFiPisc = rCDPisc * tDConsFiPisc`
- Code: `tCConsFiPisc = rCDPisc * tDConsFiPisc`

### `tCConsFiPlan` [-] *Feeding/Consumption*
- DESC: calculate C consumption of plankton
- Source: fish.F90 (749)
- Formula (d⁻¹): `tCConsFiPlan = rCDPlan * tDConsFiPlan`
- Code: `tCConsFiPlan = rCDPlan * tDConsFiPlan`

### `tCConsFiTot` [-] *Feeding/Consumption*
- DESC: calculate total C consumption
- Source: fish.F90 (768)
- Formula (d⁻¹): `tCConsFiTot = sum(tCConsFiPlan) + sum(tCConsFiBent) + sum(tCConsFiPisc)`
- Code: `tCConsFiTot = sum(tCConsFiPlan) + sum(tCConsFiBent) + sum(tCConsFiPisc)`

### `tDConsFiBent` [-] *Feeding/Consumption*
- DESC: calculate consumption of all available benthos prey
- Source: fish.F90 (720)
- Formula (d⁻¹): `tDConsFiBent = sDFiEff*fFeed*aFunVegBent*(inclBent*self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)`
- Code: `tDConsFiBent = sDFiEff*fFeed*aFunVegBent*(inclBent*self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)`

### `tDConsFiBent` [-] *Feeding/Consumption*
- DESC: apply time allocation to bentivory
- Source: fish.F90 (723)
- Formula (d⁻¹): `tDConsFiBent = tDConsFiBent*fFishBent`
- Code: `tDConsFiBent = tDConsFiBent*fFishBent`

### `tDConsFiBentPot` [-] *Feeding/Consumption*
- DESC: potential consumption of all available benthos prey (ODB off)
- Source: fish.F90 (642)
- Formula (d⁻¹): `tDConsFiBentPot = aFunVegBent*(self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)`
- Code: `tDConsFiBentPot = aFunVegBent*(self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)`

### `tDConsFiBentSum` [-] *Feeding/Consumption*
- DESC: sum benthos consumption
- Source: fish.F90 (727)
- Formula (d⁻¹): `tDConsFiBentSum = sum(tDConsFiBent)`
- Code: `tDConsFiBentSum = sum(tDConsFiBent)`

### `tDConsFiBentTotPot` [-] *Feeding/Consumption*
- DESC: total benthos consumption
- Source: fish.F90 (660)
- Formula (d⁻¹): `tDConsFiBentTotPot = sum(tDConsFiBentPot)`
- Code: `tDConsFiBentTotPot = sum(tDConsFiBentPot)`

### `tDConsFiPisc` [-] *Feeding/Consumption*
- DESC: calculate consumption of all available fish prey
- Source: fish.F90 (721)
- Formula (d⁻¹): `tDConsFiPisc = sDFiEff*fFeed*(inclPisc*self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)`
- Code: `tDConsFiPisc = sDFiEff*fFeed*(inclPisc*self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)`

### `tDConsFiPisc` [-] *Feeding/Consumption*
- DESC: apply time allocation to piscivory
- Source: fish.F90 (724)
- Formula (d⁻¹): `tDConsFiPisc = tDConsFiPisc*fFishPisc`
- Code: `tDConsFiPisc = tDConsFiPisc*fFishPisc`

### `tDConsFiPiscPot` [-] *Feeding/Consumption*
- DESC: potential consumption of all available fish prey (ODB off)
- Source: fish.F90 (643)
- Formula (d⁻¹): `tDConsFiPiscPot = (self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)`
- Code: `tDConsFiPiscPot = (self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)`

### `tDConsFiPiscSum` [-] *Feeding/Consumption*
- DESC: sum fish consumption
- Source: fish.F90 (728)
- Formula (d⁻¹): `tDConsFiPiscSum = sum(tDConsFiPisc)`
- Code: `tDConsFiPiscSum = sum(tDConsFiPisc)`

### `tDConsFiPiscTotPot` [-] *Feeding/Consumption*
- DESC: total fish consumption
- Source: fish.F90 (661)
- Formula (d⁻¹): `tDConsFiPiscTotPot = sum(tDConsFiPiscPot)`
- Code: `tDConsFiPiscTotPot = sum(tDConsFiPiscPot)`

### `tDConsFiPlan` [-] *Feeding/Consumption*
- DESC: calculate consumption of all available plankton prey
- Source: fish.F90 (719)
- Formula (d⁻¹): `tDConsFiPlan = sDFiEff*fFeed*aFunVegPlan*(inclPlan*self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)`
- Code: `tDConsFiPlan = sDFiEff*fFeed*aFunVegPlan*(inclPlan*self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)`

### `tDConsFiPlan` [-] *Feeding/Consumption*
- DESC: apply time allocation to planktivory
- Source: fish.F90 (722)
- Formula (d⁻¹): `tDConsFiPlan = tDConsFiPlan*fFishPlan`
- Code: `tDConsFiPlan = tDConsFiPlan*fFishPlan`

### `tDConsFiPlanPot` [-] *Feeding/Consumption*
- DESC: potential consumption of all available plankton prey (ODB off)
- Source: fish.F90 (641)
- Formula (d⁻¹): `tDConsFiPlanPot = aFunVegPlan*(self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)`
- Code: `tDConsFiPlanPot = aFunVegPlan*(self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)`

### `tDConsFiPlanSum` [-] *Feeding/Consumption*
- DESC: sum plankton consumption
- Source: fish.F90 (726)
- Formula (d⁻¹): `tDConsFiPlanSum = sum(tDConsFiPlan)`
- Code: `tDConsFiPlanSum = sum(tDConsFiPlan)`

### `tDConsFiPlanTotPot` [-] *Feeding/Consumption*
- DESC: total plankton consumption
- Source: fish.F90 (659)
- Formula (d⁻¹): `tDConsFiPlanTotPot = sum(tDConsFiPlanPot)`
- Code: `tDConsFiPlanTotPot = sum(tDConsFiPlanPot)`

### `tDConsFiTot` [-] *Feeding/Consumption*
- DESC: calculate total DW consumption
- Source: fish.F90 (765)
- Formula (d⁻¹): `tDConsFiTot = sum(tDConsFiPlan) + sum(tDConsFiBent) + sum(tDConsFiPisc)`
- Code: `tDConsFiTot = sum(tDConsFiPlan) + sum(tDConsFiBent) + sum(tDConsFiPisc)`

### `tNConsFiBent` [-] *Feeding/Consumption*
- DESC: calculate N consumption of benthos
- Source: fish.F90 (754)
- Formula (d⁻¹): `tNConsFiBent = rNDBent * tDConsFiBent`
- Code: `tNConsFiBent = rNDBent * tDConsFiBent`

### `tNConsFiPisc` [-] *Feeding/Consumption*
- DESC: calculate N consumption of fish
- Source: fish.F90 (760)
- Formula (d⁻¹): `tNConsFiPisc = rNDPisc * tDConsFiPisc`
- Code: `tNConsFiPisc = rNDPisc * tDConsFiPisc`

### `tNConsFiPlan` [-] *Feeding/Consumption*
- DESC: calculate N consumption of plankton
- Source: fish.F90 (748)
- Formula (d⁻¹): `tNConsFiPlan = rNDPlan * tDConsFiPlan`
- Code: `tNConsFiPlan = rNDPlan * tDConsFiPlan`

### `tNConsFiTot` [-] *Feeding/Consumption*
- DESC: calculate total N consumption
- Source: fish.F90 (767)
- Formula (d⁻¹): `tNConsFiTot = sum(tNConsFiPlan) + sum(tNConsFiBent) + sum(tNConsFiPisc)`
- Code: `tNConsFiTot = sum(tNConsFiPlan) + sum(tNConsFiBent) + sum(tNConsFiPisc)`

### `tPConsFiBent` [-] *Feeding/Consumption*
- DESC: calculate P consumption of benthos
- Source: fish.F90 (753)
- Formula (d⁻¹): `tPConsFiBent = rPDBent * tDConsFiBent`
- Code: `tPConsFiBent = rPDBent * tDConsFiBent`

### `tPConsFiPisc` [-] *Feeding/Consumption*
- DESC: calculate P consumption of fish
- Source: fish.F90 (759)
- Formula (d⁻¹): `tPConsFiPisc = rPDPisc * tDConsFiPisc`
- Code: `tPConsFiPisc = rPDPisc * tDConsFiPisc`

### `tPConsFiPlan` [-] *Feeding/Consumption*
- DESC: calculate P consumption of plankton
- Source: fish.F90 (747)
- Formula (d⁻¹): `tPConsFiPlan = rPDPlan * tDConsFiPlan`
- Code: `tPConsFiPlan = rPDPlan * tDConsFiPlan`

### `tPConsFiTot` [-] *Feeding/Consumption*
- DESC: calculate total P consumption
- Source: fish.F90 (766)
- Formula (d⁻¹): `tPConsFiTot = sum(tPConsFiPlan) + sum(tPConsFiBent) + sum(tPConsFiPisc)`
- Code: `tPConsFiTot = sum(tPConsFiPlan) + sum(tPConsFiBent) + sum(tPConsFiPisc)`

### `vPiscPred` [-] *Feeding/Consumption*
- DESC: calculate final mortality rate for all fish prey
- Source: fish.F90 (740)
- Formula (d⁻¹): `vPiscPred = vPiscPredPot*fFishPisc*fFeed`
- Code: `vPiscPred = vPiscPredPot*fFishPisc*fFeed`

### `vPiscPredPot` [-] *Feeding/Consumption*
- DESC: calculate potential predation rate on all available fish prey
- Source: fish.F90 (739)
- Formula (d⁻¹): `vPiscPredPot = sDFiEff*(inclPisc*self%cClearPisc)*(1._rk-aFeedLvlPisc)`
- Code: `vPiscPredPot = sDFiEff*(inclPisc*self%cClearPisc)*(1._rk-aFeedLvlPisc)`

## Feeding_fractions

### `BioTurb` [gDW/m3/d] *Feeding_fractions*
- DESC: current bioturbation by fish
- Source: fish_pclake.F90 (499)
- Formula (d⁻¹): `BioTurb = fFishBen * sDfi * uFunTmFish * self%kTurbFish`
- Code: `BioTurb = fFishBen * sDfi * uFunTmFish * self%kTurbFish`

### `fFishBen_norm` [-] *Feeding_fractions*
- DESC: normalized zoobentivory time fraction
- Source: fish_pclake.F90 (497)
- Formula (d⁻¹): `fFishBen = self%fFishBen / (self%fFishZoo + self%fFishBen + self%fFishPisc)`
- Code: `fFishBen = self%fFishBen / (self%fFishZoo + self%fFishBen + self%fFishPisc)`

### `fFishPisc_norm` [-] *Feeding_fractions*
- DESC: normalized piscivory time fraction
- Source: fish_pclake.F90 (498)
- Formula (d⁻¹): `fFishPisc = self%fFishPisc / (self%fFishZoo + self%fFishBen + self%fFishPisc)`
- Code: `fFishPisc = self%fFishPisc / (self%fFishZoo + self%fFishBen + self%fFishPisc)`

### `fFishZoo_norm` [-] *Feeding_fractions*
- DESC: normalized zooplanktivory time fraction
- Source: fish_pclake.F90 (496)
- Formula (d⁻¹): `fFishZoo = self%fFishZoo / (self%fFishZoo + self%fFishBen + self%fFishPisc)`
- Code: `fFishZoo = self%fFishZoo / (self%fFishZoo + self%fFishBen + self%fFishPisc)`

## Filtering rate

### `FR` [m3/gDW/s] *Filtering rate*
- DESC: water filtration rate (food-limited case: total_food_DW < hKfood)
- Source: bivalves.F90 (462)
- Formula (d⁻¹): `FR = tDConsBivTot / (self%hKfood * self%fDAssBiv)`
- Code: `FR = tDConsBivTot / (self%hKfood * self%fDAssBiv)`

### `FR` [m3/gDW/s] *Filtering rate*
- DESC: water filtration rate (food-saturated case: total_food_DW >= hKfood)
- Source: bivalves.F90 (464)
- Formula (d⁻¹): `FR = tDConsBivTot / (total_food_DW * self%fDAssBiv)`
- Code: `FR = tDConsBivTot / (total_food_DW * self%fDAssBiv)`

## Final fluxes

### `tCBedVeg` [gC/m2/s] *Final fluxes*
- DESC: total macrophytes C flux in bed module
- Source: macrophytes.F90 (573)
- Formula (d⁻¹): `tCMigrVeg + tCProdVeg - tCRespVeg - tCMortVeg`
- Code: `tCBedVeg = tCMigrVeg + tCProdVeg - tCRespVeg - tCMortVeg`

### `tDBedVeg` [gDW/m2/s] *Final fluxes*
- DESC: derivative of macrophytes biomass
- Source: macrophytes.F90 (570)
- Formula (d⁻¹): `tDMigrVeg + tDProdVeg - tDMortVeg - tDRespVeg`
- Code: `tDBedVeg = tDMigrVeg + tDProdVeg - tDMortVeg - tDRespVeg`

### `tNBedVeg` [gN/m2/s] *Final fluxes*
- DESC: total macrophytes N flux in bed module
- Source: macrophytes.F90 (571)
- Formula (d⁻¹): `tNMigrVeg + tNUptVeg - tNExcrVeg - tNMortVeg`
- Code: `tNBedVeg = tNMigrVeg + tNUptVeg - tNExcrVeg - tNMortVeg`

### `tPBedVeg` [gP/m2/s] *Final fluxes*
- DESC: total macrophytes P flux in bed module
- Source: macrophytes.F90 (572)
- Formula (d⁻¹): `tPMigrVeg + tPUptVeg - tPExcrVeg - tPMortVeg`
- Code: `tPBedVeg = tPMigrVeg + tPUptVeg - tPExcrVeg - tPMortVeg`

## Final fluxes (CO2 sediment)

### `tCBedDOMS` [gC/m2/s] *Final fluxes (CO2 sediment)*
- DESC: total C flux to sediment dissolved organic matter
- Source: macrophytes.F90 (673)
- Formula (d⁻¹): `tCMortVegS * fVegDOMS`
- Code: `tCBedDOMS = tCMortVegS * self%fVegDOMS`

### `tCBedPOMS` [gC/m2/s] *Final fluxes (CO2 sediment)*
- DESC: total C flux to sediment particulate organic matter
- Source: macrophytes.F90 (672)
- Formula (d⁻¹): `tCMortVegS * (1.0 - fVegDOMS)`
- Code: `tCBedPOMS = tCMortVegS * (1.0_rk - self%fVegDOMS)`

### `tCMortVegS` [gC/m2/s] *Final fluxes (CO2 sediment)*
- DESC: mortality flux to sediment organic matter
- Source: macrophytes.F90 (671)
- Formula (d⁻¹): `tCMortVeg - tCMortVegW`
- Code: `tCMortVegS = tCMortVeg - tCMortVegW`

## Final fluxes (CO2)

### `tCMortVegW` [gC/m2/s] *Final fluxes (CO2)*
- DESC: mortality flux to watercolumn organic matter
- Source: macrophytes.F90 (664)
- Formula (d⁻¹): `fTOMWMortVeg * (1.0 - bfRootVeg) * tCMortVeg`
- Code: `tCMortVegW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tCMortVeg`

### `tCO2BedW` [gC/m2/s] *Final fluxes (CO2)*
- DESC: total CO2 flux to the watercolumn
- Source: macrophytes.F90 (663)
- Formula (d⁻¹): `(tO2ProdVegW - tO2RespVegW)/molO2molC`
- Code: `tCO2BedW = (tO2ProdVegW - tO2RespVegW)/molO2molC`

### `wCBedDOMW` [gC/m2/s] *Final fluxes (CO2)*
- DESC: total C flux to watercolumn dissolved organic matter
- Source: macrophytes.F90 (667)
- Formula (d⁻¹): `wCBedTOMW * fVegDOMW`
- Code: `wCBedDOMW = wCBedTOMW * self%fVegDOMW`

### `wCBedPOMW` [gC/m2/s] *Final fluxes (CO2)*
- DESC: total C flux to watercolumn particulate organic matter
- Source: macrophytes.F90 (666)
- Formula (d⁻¹): `wCBedTOMW * (1.0 - fVegDOMW)`
- Code: `wCBedPOMW = wCBedTOMW * (1.0_rk - self%fVegDOMW)`

### `wCBedTOMW` [gC/m2/s] *Final fluxes (CO2)*
- DESC: total C flux to watercolumn organic matter
- Source: macrophytes.F90 (665)
- Formula (d⁻¹): `tCMortVegW`
- Code: `wCBedTOMW = tCMortVegW`

## Final fluxes (DW sediment)

### `tDBedDOMS` [gDW/m2/s] *Final fluxes (DW sediment)*
- DESC: total DW flux to sediment dissolved organic matter
- Source: macrophytes.F90 (588)
- Formula (d⁻¹): `tDMortVegS * fVegDOMS`
- Code: `tDBedDOMS = tDMortVegS * self%fVegDOMS`

### `tDBedPOMS` [gDW/m2/s] *Final fluxes (DW sediment)*
- DESC: total DW flux to sediment particulate organic matter
- Source: macrophytes.F90 (587)
- Formula (d⁻¹): `tDMortVegS * (1.0 - fVegDOMS)`
- Code: `tDBedPOMS = tDMortVegS * (1.0_rk - self%fVegDOMS)`

### `tDMortVegS` [gDW/m2/s] *Final fluxes (DW sediment)*
- DESC: mortality flux to sediment organic matter
- Source: macrophytes.F90 (586)
- Formula (d⁻¹): `tDMortVeg - tDMortVegW`
- Code: `tDMortVegS = tDMortVeg - tDMortVegW`

## Final fluxes (DW water)

### `tDMortVegW` [gDW/m2/s] *Final fluxes (DW water)*
- DESC: mortality flux to watercolumn organic matter
- Source: macrophytes.F90 (579)
- Formula (d⁻¹): `fTOMWMortVeg * (1.0 - bfRootVeg) * tDMortVeg`
- Code: `tDMortVegW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tDMortVeg`

### `wDBedDOMW` [gDW/m2/s] *Final fluxes (DW water)*
- DESC: total DW flux to watercolumn dissolved organic matter
- Source: macrophytes.F90 (582)
- Formula (d⁻¹): `wDBedTOMW * fVegDOMW`
- Code: `wDBedDOMW = wDBedTOMW * self%fVegDOMW`

### `wDBedPOMW` [gDW/m2/s] *Final fluxes (DW water)*
- DESC: total DW flux to watercolumn particulate organic matter
- Source: macrophytes.F90 (581)
- Formula (d⁻¹): `wDBedTOMW * (1.0 - fVegDOMW)`
- Code: `wDBedPOMW = wDBedTOMW * (1.0_rk - self%fVegDOMW)`

### `wDBedTOMW` [gDW/m2/s] *Final fluxes (DW water)*
- DESC: total DW flux to watercolumn organic matter
- Source: macrophytes.F90 (580)
- Formula (d⁻¹): `tDMortVegW`
- Code: `wDBedTOMW = tDMortVegW`

## Final fluxes (N sediment)

### `afNH4UptVegS` [-] *Final fluxes (N sediment)*
- DESC: fraction NH4 uptake from pore water (WASP/EPA model)
- Source: macrophytes.F90 (611)
- Formula (d⁻¹): `oNH4S*oNO3S/((ahNUptVeg+oNH4S+NearZero)*(ahNUptVeg+oNO3S+NearZero)) + oNH4S*ahNUptVeg/((oNH4S+oNO3S+NearZero)*(ahNUptVeg+oNO3S+NearZero))`
- Code: `afNH4UptVegS = oNH4S * oNO3S / ((ahNUptVeg + oNH4S + NearZero) * (ahNUptVeg + oNO3S + NearZero)) + oNH4S * ahNUptVeg / ((oNH4S + oNO3S + NearZero) * (ahNUptVeg + oNO3S + NearZero))`

### `tNBedDOMS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: total dissolved organic N flux to sediment
- Source: macrophytes.F90 (621)
- Formula (d⁻¹): `tNMortVegTOMS * fVegDOMS`
- Code: `tNBedDOMS = tNMortVegTOMS * self%fVegDOMS`

### `tNBedNH4S` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: total N flux to NH4 in pore water
- Source: macrophytes.F90 (616)
- Formula (d⁻¹): `-tNUptNH4VegS + tNExcrVegS + tNMortVegNH4S`
- Code: `tNBedNH4S = -tNUptNH4VegS + tNExcrVegS + tNMortVegNH4S`

### `tNBedNO3S` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: total N flux to NO3 in pore water
- Source: macrophytes.F90 (618)
- Formula (d⁻¹): `-tNUptNO3VegS`
- Code: `tNBedNO3S = -tNUptNO3VegS`

### `tNBedPOMS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: total particulate organic N flux to sediment
- Source: macrophytes.F90 (620)
- Formula (d⁻¹): `tNMortVegTOMS * (1.0 - fVegDOMS)`
- Code: `tNBedPOMS = tNMortVegTOMS * (1.0_rk - self%fVegDOMS)`

### `tNExcrVegS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: N excretion to sediment
- Source: macrophytes.F90 (613)
- Formula (d⁻¹): `bfRootVeg * tNExcrVeg`
- Code: `tNExcrVegS = bfRootVeg * tNExcrVeg`

### `tNMortVegNH4S` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: mortality flux as ammonia to sediment
- Source: macrophytes.F90 (614)
- Formula (d⁻¹): `bfRootVeg * tNMortVegNH4`
- Code: `tNMortVegNH4S = bfRootVeg * tNMortVegNH4`

### `tNMortVegTOMS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: mortality flux as organic N in sediment
- Source: macrophytes.F90 (619)
- Formula (d⁻¹): `tNMortVegTOM - tNMortVegTOMW`
- Code: `tNMortVegTOMS = tNMortVegTOM - tNMortVegTOMW`

### `tNUptNH4VegS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: NH4 uptake of macrophytes from sediment
- Source: macrophytes.F90 (615)
- Formula (d⁻¹): `afNH4UptVegS * tNUptVegS`
- Code: `tNUptNH4VegS = afNH4UptVegS * tNUptVegS`

### `tNUptNO3VegS` [gN/m2/s] *Final fluxes (N sediment)*
- DESC: NO3 uptake of macrophytes from sediment
- Source: macrophytes.F90 (617)
- Formula (d⁻¹): `tNUptVegS - tNUptNH4VegS`
- Code: `tNUptNO3VegS = tNUptVegS - tNUptNH4VegS`

## Final fluxes (N water)

### `afNH4UptVegW` [-] *Final fluxes (N water)*
- DESC: fraction NH4 uptake from water column (WASP/EPA model)
- Source: macrophytes.F90 (594)
- Formula (d⁻¹): `sNH4W*sNO3W/((ahNUptVeg+sNH4W)*(ahNUptVeg+sNO3W+NearZero)) + sNH4W*ahNUptVeg/((sNH4W+sNO3W+NearZero)*(ahNUptVeg+sNO3W+NearZero))`
- Code: `afNH4UptVegW = sNH4W * sNO3W / ((ahNUptVeg + sNH4W) * (ahNUptVeg + sNO3W + NearZero)) + sNH4W * ahNUptVeg / ((sNH4W + sNO3W + NearZero) * (ahNUptVeg + sNO3W + NearZero))`

### `tNExcrVegW` [gN/m2/s] *Final fluxes (N water)*
- DESC: N excretion to water
- Source: macrophytes.F90 (597)
- Formula (d⁻¹): `tNExcrVeg * (1.0 - bfRootVeg)`
- Code: `tNExcrVegW = tNExcrVeg * (1.0_rk - bfRootVeg)`

### `tNMortVegNH4` [gN/m2/s] *Final fluxes (N water)*
- DESC: mortality flux as ammonia
- Source: macrophytes.F90 (598)
- Formula (d⁻¹): `fDissMortVeg * tNMortVeg`
- Code: `tNMortVegNH4 = self%fDissMortVeg * tNMortVeg`

### `tNMortVegNH4W` [gN/m2/s] *Final fluxes (N water)*
- DESC: mortality flux to watercolumn NH4
- Source: macrophytes.F90 (599)
- Formula (d⁻¹): `tNMortVegNH4 * (1.0 - bfRootVeg)`
- Code: `tNMortVegNH4W = tNMortVegNH4 * (1.0_rk - bfRootVeg)`

### `tNMortVegTOM` [gN/m2/s] *Final fluxes (N water)*
- DESC: mortality flux as organic N
- Source: macrophytes.F90 (603)
- Formula (d⁻¹): `tNMortVeg - tNMortVegNH4`
- Code: `tNMortVegTOM = tNMortVeg - tNMortVegNH4`

### `tNMortVegTOMW` [gN/m2/s] *Final fluxes (N water)*
- DESC: mortality flux to watercolumn organic N
- Source: macrophytes.F90 (604)
- Formula (d⁻¹): `fTOMWMortVeg * (1.0 - bfRootVeg) * tNMortVegTOM`
- Code: `tNMortVegTOMW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tNMortVegTOM`

### `tNUptNH4VegW` [gN/m2/s] *Final fluxes (N water)*
- DESC: NH4 uptake from water
- Source: macrophytes.F90 (596)
- Formula (d⁻¹): `afNH4UptVegW * tNUptVegW`
- Code: `tNUptNH4VegW = afNH4UptVegW * tNUptVegW`

### `tNUptNO3VegW` [gN/m2/s] *Final fluxes (N water)*
- DESC: NO3 uptake from watercolumn
- Source: macrophytes.F90 (601)
- Formula (d⁻¹): `tNUptVegW - tNUptNH4VegW`
- Code: `tNUptNO3VegW = tNUptVegW - tNUptNH4VegW`

### `wNBedDOMW` [gN/m2/s] *Final fluxes (N water)*
- DESC: total dissolved organic N flux to watercolumn
- Source: macrophytes.F90 (607)
- Formula (d⁻¹): `wNBedTOMW * fVegDOMW`
- Code: `wNBedDOMW = wNBedTOMW * self%fVegDOMW`

### `wNBedNH4W` [gN/m2/s] *Final fluxes (N water)*
- DESC: total N flux to watercolumn NH4
- Source: macrophytes.F90 (600)
- Formula (d⁻¹): `-tNUptNH4VegW + tNExcrVegW + tNMortVegNH4W`
- Code: `wNBedNH4W = -tNUptNH4VegW + tNExcrVegW + tNMortVegNH4W`

### `wNBedNO3W` [gN/m2/s] *Final fluxes (N water)*
- DESC: total N flux to watercolumn NO3
- Source: macrophytes.F90 (602)
- Formula (d⁻¹): `-tNUptNO3VegW`
- Code: `wNBedNO3W = -tNUptNO3VegW`

### `wNBedPOMW` [gN/m2/s] *Final fluxes (N water)*
- DESC: total particulate organic N flux to watercolumn
- Source: macrophytes.F90 (606)
- Formula (d⁻¹): `wNBedTOMW * (1.0 - fVegDOMW)`
- Code: `wNBedPOMW = wNBedTOMW * (1.0_rk - self%fVegDOMW)`

### `wNBedTOMW` [gN/m2/s] *Final fluxes (N water)*
- DESC: total N flux to watercolumn organic matter
- Source: macrophytes.F90 (605)
- Formula (d⁻¹): `tNMortVegTOMW`
- Code: `wNBedTOMW = tNMortVegTOMW`

## Final fluxes (O2)

### `aCorO2BOD` [-] *Final fluxes (O2)*
- DESC: correction of O2 demand in water at low oxygen conc.
- Source: macrophytes.F90 (651)
- Formula (d⁻¹): `sO2W/(hO2BOD + sO2W)`
- Code: `aCorO2BOD = sO2W/(self%hO2BOD + sO2W)`

### `tO2BedW` [gO2/m2/s] *Final fluxes (O2)*
- DESC: total O2 flux to the watercolumn
- Source: macrophytes.F90 (657)
- Formula (d⁻¹): `tO2ProdVegW - tO2RespVegW + tO2UptNO3VegW`
- Code: `tO2BedW = tO2ProdVegW - tO2RespVegW + tO2UptNO3VegW`

### `tO2ProdVeg` [gO2/m2/s] *Final fluxes (O2)*
- DESC: macrophytes O2 production
- Source: macrophytes.F90 (654)
- Formula (d⁻¹): `molO2molC * cCPerDW * tDProdVeg`
- Code: `tO2ProdVeg = molO2molC * self%cCPerDW * tDProdVeg`

### `tO2ProdVegS` [gO2/m2/s] *Final fluxes (O2)*
- DESC: O2 transport to roots
- Source: macrophytes.F90 (655)
- Formula (d⁻¹): `min(tO2RespVegS, tO2ProdVeg)`
- Code: `tO2ProdVegS = min(tO2RespVegS, tO2ProdVeg)`

### `tO2ProdVegW` [gO2/m2/s] *Final fluxes (O2)*
- DESC: O2 used for macrophytes production
- Source: macrophytes.F90 (656)
- Formula (d⁻¹): `min(tO2ProdVeg - tO2ProdVegS, bfSubVeg * tO2ProdVeg)`
- Code: `tO2ProdVegW = min(tO2ProdVeg - tO2ProdVegS, bfSubVeg * tO2ProdVeg)`

### `tO2RespVegS` [gO2/m2/s] *Final fluxes (O2)*
- DESC: root O2 respiration
- Source: macrophytes.F90 (653)
- Formula (d⁻¹): `molO2molC * cCPerDW * bfRootVeg * tDRespVeg * afOxySed`
- Code: `tO2RespVegS = molO2molC * self%cCPerDW * bfRootVeg * tDRespVeg * afOxySed`

### `tO2RespVegW` [gO2/m2/s] *Final fluxes (O2)*
- DESC: submerged O2 respiration
- Source: macrophytes.F90 (652)
- Formula (d⁻¹): `molO2molC * cCPerDW * bfSubVeg * tDRespVeg * aCorO2BOD`
- Code: `tO2RespVegW = molO2molC * self%cCPerDW * bfSubVeg * tDRespVeg * aCorO2BOD`

### `tO2UptNO3VegW` [gO2/m2/s] *Final fluxes (O2)*
- DESC: O2 release to watercolumn due to NO3 uptake
- Source: macrophytes.F90 (650)
- Formula (d⁻¹): `O2PerNO3 * molO2molN * bfSubVeg * tNUptNO3VegW`
- Code: `tO2UptNO3VegW = O2PerNO3 * molO2molN * bfSubVeg * tNUptNO3VegW`

## Final fluxes (P sediment)

### `tPBedDOMS` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: total dissolved organic P flux to the sediment
- Source: macrophytes.F90 (644)
- Formula (d⁻¹): `tPMortVegTOMS * fVegDOMS`
- Code: `tPBedDOMS = tPMortVegTOMS * self%fVegDOMS`

### `tPBedPO4S` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: total P flux as PO4 to the sediment
- Source: macrophytes.F90 (641)
- Formula (d⁻¹): `-tPUptVegS + tPExcrVegS + tPMortVegPO4S`
- Code: `tPBedPO4S = -tPUptVegS + tPExcrVegS + tPMortVegPO4S`

### `tPBedPOMS` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: total particulate organic P flux to the sediment
- Source: macrophytes.F90 (643)
- Formula (d⁻¹): `tPMortVegTOMS * (1.0 - fVegDOMS)`
- Code: `tPBedPOMS = tPMortVegTOMS * (1.0_rk - self%fVegDOMS)`

### `tPExcrVegS` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: P excretion to the sediment
- Source: macrophytes.F90 (639)
- Formula (d⁻¹): `bfRootVeg * tPExcrVeg`
- Code: `tPExcrVegS = bfRootVeg * tPExcrVeg`

### `tPMortVegPO4S` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: mortality flux of phosphate to the sediment
- Source: macrophytes.F90 (640)
- Formula (d⁻¹): `bfRootVeg * tPMortVegPO4`
- Code: `tPMortVegPO4S = bfRootVeg * tPMortVegPO4`

### `tPMortVegTOMS` [gP/m2/s] *Final fluxes (P sediment)*
- DESC: mortality flux as organic P to the sediment
- Source: macrophytes.F90 (642)
- Formula (d⁻¹): `tPMortVegTOM - tPMortVegTOMW`
- Code: `tPMortVegTOMS = tPMortVegTOM - tPMortVegTOMW`

## Final fluxes (P water)

### `tPExcrVegW` [gP/m2/s] *Final fluxes (P water)*
- DESC: P excretion to the watercolumn
- Source: macrophytes.F90 (627)
- Formula (d⁻¹): `tPExcrVeg * (1.0 - bfRootVeg)`
- Code: `tPExcrVegW = tPExcrVeg * (1.0_rk - bfRootVeg)`

### `tPMortVegPO4` [gP/m2/s] *Final fluxes (P water)*
- DESC: mortality flux as phosphate
- Source: macrophytes.F90 (628)
- Formula (d⁻¹): `fDissMortVeg * tPMortVeg`
- Code: `tPMortVegPO4 = self%fDissMortVeg * tPMortVeg`

### `tPMortVegPO4W` [gP/m2/s] *Final fluxes (P water)*
- DESC: mortality flux of phosphate to the watercolumn
- Source: macrophytes.F90 (629)
- Formula (d⁻¹): `tPMortVegPO4 * (1.0 - bfRootVeg)`
- Code: `tPMortVegPO4W = tPMortVegPO4 * (1.0_rk - bfRootVeg)`

### `tPMortVegTOM` [gP/m2/s] *Final fluxes (P water)*
- DESC: mortality flux as organic P
- Source: macrophytes.F90 (631)
- Formula (d⁻¹): `tPMortVeg - tPMortVegPO4`
- Code: `tPMortVegTOM = tPMortVeg - tPMortVegPO4`

### `tPMortVegTOMW` [gP/m2/s] *Final fluxes (P water)*
- DESC: mortality flux as organic P to the watercolumn
- Source: macrophytes.F90 (632)
- Formula (d⁻¹): `fTOMWMortVeg * (1.0 - bfRootVeg) * tPMortVegTOM`
- Code: `tPMortVegTOMW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tPMortVegTOM`

### `wPBedDOMW` [gP/m2/s] *Final fluxes (P water)*
- DESC: total dissolved organic P flux to watercolumn
- Source: macrophytes.F90 (635)
- Formula (d⁻¹): `wPBedTOMW * fVegDOMW`
- Code: `wPBedDOMW = wPBedTOMW * self%fVegDOMW`

### `wPBedPO4W` [gP/m2/s] *Final fluxes (P water)*
- DESC: total P flux as PO4 to the watercolumn
- Source: macrophytes.F90 (630)
- Formula (d⁻¹): `-tPUptVegW + tPExcrVegW + tPMortVegPO4W`
- Code: `wPBedPO4W = -tPUptVegW + tPExcrVegW + tPMortVegPO4W`

### `wPBedPOMW` [gP/m2/s] *Final fluxes (P water)*
- DESC: total particulate organic P flux to watercolumn
- Source: macrophytes.F90 (634)
- Formula (d⁻¹): `wPBedTOMW * (1.0 - fVegDOMW)`
- Code: `wPBedPOMW = wPBedTOMW * (1.0_rk - self%fVegDOMW)`

### `wPBedTOMW` [gP/m2/s] *Final fluxes (P water)*
- DESC: total P flux as organic matter to the watercolumn
- Source: macrophytes.F90 (633)
- Formula (d⁻¹): `tPMortVegTOMW`
- Code: `wPBedTOMW = tPMortVegTOMW`

## Final_fluxes

### `tDFi` [1/d] *Final_fluxes*
- DESC: final rate of change in DW
- Source: fish_pclake.F90 (677)
- Formula (d⁻¹): `tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish - tDReprFish`
- Code: `tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish - tDReprFish`

### `tDFiDOMW` [1/d] *Final_fluxes*
- DESC: dissolved fraction of DW flux to water column
- Source: fish_pclake.F90 (689)
- Formula (d⁻¹): `tDFiDOMW = tDFiTOMW * fFiDOMW`
- Code: `tDFiDOMW = tDFiTOMW * self%fFiDOMW`

### `tDFiPOMW` [1/d] *Final_fluxes*
- DESC: particulate fraction of DW flux to water column
- Source: fish_pclake.F90 (688)
- Formula (d⁻¹): `tDFiPOMW = tDFiTOMW * (1.0_rk - fFiDOMW)`
- Code: `tDFiPOMW = tDFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tDFiTOMW` [1/d] *Final_fluxes*
- DESC: total flux of DW to water column
- Source: fish_pclake.F90 (687)
- Formula (d⁻¹): `tDFiTOMW = tDEgesFi + tDMortFiTOM`
- Code: `tDFiTOMW = tDEgesFi + tDMortFiTOM`

### `tDMortFiBot` [1/d] *Final_fluxes*
- DESC: flux out of system (into sediment) from mortality (DW)
- Source: fish_pclake.F90 (685)
- Formula (d⁻¹): `tDMortFiBot = fDBone * (tDMortFi)`
- Code: `tDMortFiBot = self%fDBone * (tDMortFi)`

### `tDMortFiTOM` [1/d] *Final_fluxes*
- DESC: part of dead fish staying in system (DW)
- Source: fish_pclake.F90 (686)
- Formula (d⁻¹): `tDMortFiTOM = (tDMortFi) - tDMortFiBot`
- Code: `tDMortFiTOM = (tDMortFi) - tDMortFiBot`

### `tNEgesFiNH4` [1/d] *Final_fluxes*
- DESC: dissolved N part of egestion flux
- Source: fish_pclake.F90 (693)
- Formula (d⁻¹): `tNEgesFiNH4 = fDissEgesFish * tNEgesFi`
- Code: `tNEgesFiNH4 = self%fDissEgesFish * tNEgesFi`

### `tNEgesFiTOM` [1/d] *Final_fluxes*
- DESC: organic N part of egestion
- Source: fish_pclake.F90 (699)
- Formula (d⁻¹): `tNEgesFiTOM = tNEgesFi - tNEgesFiNH4`
- Code: `tNEgesFiTOM = tNEgesFi - tNEgesFiNH4`

### `tNFi` [1/d] *Final_fluxes*
- DESC: final rate of change in N
- Source: fish_pclake.F90 (679)
- Formula (d⁻¹): `tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish - tNReprFish`
- Code: `tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish - tNReprFish`

### `tNFiDOMW` [1/d] *Final_fluxes*
- DESC: dissolved part of organic N flux to water column
- Source: fish_pclake.F90 (702)
- Formula (d⁻¹): `tNFiDOMW = tNFiTOMW * fFiDOMW`
- Code: `tNFiDOMW = tNFiTOMW * self%fFiDOMW`

### `tNFiNH4W` [1/d] *Final_fluxes*
- DESC: total dissolved N flux to water column
- Source: fish_pclake.F90 (696)
- Formula (d⁻¹): `tNFiNH4W = tNExcrFi + tNEgesFiNH4 + tNMortFiNH4`
- Code: `tNFiNH4W = tNExcrFi + tNEgesFiNH4 + tNMortFiNH4`

### `tNFiPOMW` [1/d] *Final_fluxes*
- DESC: particulate part of organic N flux to water column
- Source: fish_pclake.F90 (701)
- Formula (d⁻¹): `tNFiPOMW = tNFiTOMW * (1.0_rk - fFiDOMW)`
- Code: `tNFiPOMW = tNFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tNFiTOMW` [1/d] *Final_fluxes*
- DESC: total organic N flux to water column
- Source: fish_pclake.F90 (700)
- Formula (d⁻¹): `tNFiTOMW = tNEgesFiTOM + tNMortFiTOM`
- Code: `tNFiTOMW = tNEgesFiTOM + tNMortFiTOM`

### `tNMortFiBot` [1/d] *Final_fluxes*
- DESC: flux of N out of system (into sediment) from mortality
- Source: fish_pclake.F90 (694)
- Formula (d⁻¹): `tNMortFiBot = fDBone * tNMortFi`
- Code: `tNMortFiBot = self%fDBone * tNMortFi`

### `tNMortFiNH4` [1/d] *Final_fluxes*
- DESC: dissolved N part of mortality flux
- Source: fish_pclake.F90 (695)
- Formula (d⁻¹): `tNMortFiNH4 = fDissMortFish *(tNMortFi - tNMortFiBot)`
- Code: `tNMortFiNH4 = self%fDissMortFish * (tNMortFi - tNMortFiBot)`

### `tNMortFiTOM` [1/d] *Final_fluxes*
- DESC: organic N part of mortality flux
- Source: fish_pclake.F90 (698)
- Formula (d⁻¹): `tNMortFiTOM = tNMortFi - tNMortFiBot - tNMortFiNH4`
- Code: `tNMortFiTOM = tNMortFi - tNMortFiBot - tNMortFiNH4`

### `tPEgesFiPO4` [1/d] *Final_fluxes*
- DESC: dissolved P part of egestion flux
- Source: fish_pclake.F90 (706)
- Formula (d⁻¹): `tPEgesFiPO4 = fDissEgesFish * tPEgesFi`
- Code: `tPEgesFiPO4 = self%fDissEgesFish * tPEgesFi`

### `tPEgesFiTOM` [1/d] *Final_fluxes*
- DESC: organic P part of egestion
- Source: fish_pclake.F90 (712)
- Formula (d⁻¹): `tPEgesFiTOM = tPEgesFi - tPEgesFiPO4`
- Code: `tPEgesFiTOM = tPEgesFi - tPEgesFiPO4`

### `tPFi` [1/d] *Final_fluxes*
- DESC: final rate of change in P
- Source: fish_pclake.F90 (678)
- Formula (d⁻¹): `tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish - tPReprFish`
- Code: `tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish - tPReprFish`

### `tPFiDOMW` [1/d] *Final_fluxes*
- DESC: dissolved part of organic P flux to water column
- Source: fish_pclake.F90 (715)
- Formula (d⁻¹): `tPFiDOMW = tPFiTOMW * fFiDOMW`
- Code: `tPFiDOMW = tPFiTOMW * self%fFiDOMW`

### `tPFiPO4W` [1/d] *Final_fluxes*
- DESC: total dissolved P flux to water column
- Source: fish_pclake.F90 (709)
- Formula (d⁻¹): `tPFiPO4W = tPExcrFi + tPEgesFiPO4 + tPMortFiPO4`
- Code: `tPFiPO4W = tPExcrFi + tPEgesFiPO4 + tPMortFiPO4`

### `tPFiPOMW` [1/d] *Final_fluxes*
- DESC: particulate part of organic P flux to water column
- Source: fish_pclake.F90 (714)
- Formula (d⁻¹): `tPFiPOMW = tPFiTOMW * (1.0_rk - fFiDOMW)`
- Code: `tPFiPOMW = tPFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tPFiTOMW` [1/d] *Final_fluxes*
- DESC: total organic P flux to water column
- Source: fish_pclake.F90 (713)
- Formula (d⁻¹): `tPFiTOMW = tPEgesFiTOM + tPMortFiTOM`
- Code: `tPFiTOMW = tPEgesFiTOM + tPMortFiTOM`

### `tPMortFiBot` [1/d] *Final_fluxes*
- DESC: flux of P out of system (into sediment) from mortality
- Source: fish_pclake.F90 (707)
- Formula (d⁻¹): `tPMortFiBot = fPBone * tPMortFi`
- Code: `tPMortFiBot = self%fPBone * tPMortFi`

### `tPMortFiPO4` [1/d] *Final_fluxes*
- DESC: dissolved P part of mortality flux
- Source: fish_pclake.F90 (708)
- Formula (d⁻¹): `tPMortFiPO4 = fDissMortFish *(tPMortFi - tPMortFiBot)`
- Code: `tPMortFiPO4 = self%fDissMortFish * (tPMortFi - tPMortFiBot)`

### `tPMortFiTOM` [1/d] *Final_fluxes*
- DESC: organic P part of mortality flux
- Source: fish_pclake.F90 (711)
- Formula (d⁻¹): `tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4`
- Code: `tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4`

## Fluxes

### `wDAbioIMW` [-] *Fluxes*
- DESC: DW inorganic matter flux in water
- Source: abiotic_water.F90 (234-234)
- Formula (d⁻¹): `0.0`
- Code: `wDAbioIMW = 0.0_rk`

### `wNAbioNH4W` [-] *Fluxes*
- DESC: NH4 flux in water
- Source: abiotic_water.F90 (238-238)
- Formula (d⁻¹): `- wNNitrW`
- Code: `wNAbioNH4W = - wNNitrW`

### `wNAbioNO3W` [-] *Fluxes*
- DESC: NO3 flux in water
- Source: abiotic_water.F90 (240-240)
- Formula (d⁻¹): `wNNitrW`
- Code: `wNAbioNO3W = wNNitrW`

### `wNNitrW` [-] *Fluxes*
- DESC: diagnostic output rate nitrification
- Source: abiotic_water.F90 (274-274)
- Formula (d⁻¹): `wNNitrW`
- Code: `_SET_DIAGNOSTIC_(self%id_wNNitrW, wNNitrW)`

### `wO2AbioW` [-] *Fluxes*
- DESC: O2 flux in water
- Source: abiotic_water.F90 (241-241)
- Formula (d⁻¹): `- wO2NitrW`
- Code: `wO2AbioW = - wO2NitrW`

### `wO2NitrW` [-] *Fluxes*
- DESC: diagnostic output rate O2 cons. by nitrification
- Source: abiotic_water.F90 (275-275)
- Formula (d⁻¹): `wO2NitrW`
- Code: `_SET_DIAGNOSTIC_(self%id_wO2NitrW, wO2NitrW)`

### `wPAbioAIMW` [-] *Fluxes*
- DESC: P absorbed on inorganic matter flux in water
- Source: abiotic_water.F90 (237-237)
- Formula (d⁻¹): `wPSorpIMW`
- Code: `wPAbioAIMW = wPSorpIMW`

### `wPAbioPO4W` [-] *Fluxes*
- DESC: PO4 flux in water
- Source: abiotic_water.F90 (236-236)
- Formula (d⁻¹): `- wPSorpIMW`
- Code: `wPAbioPO4W = - wPSorpIMW`

### `wPSorpIMW` [-] *Fluxes*
- DESC: diagnostic output rate P adsorped
- Source: abiotic_water.F90 (273-273)
- Formula (d⁻¹): `wPSorpIMW`
- Code: `_SET_DIAGNOSTIC_(self%id_wPSorpIMW, wPSorpIMW)`

### `wSiAbioPaW` [-] *Fluxes*
- DESC: Si particulate OM flux in water
- Source: abiotic_water.F90 (235-235)
- Formula (d⁻¹): `- wSiMinPaW`
- Code: `wSiAbioPaW = - wSiMinPaW`

### `wSiAbioSiO2W` [-] *Fluxes*
- DESC: SiO2 flux in water
- Source: abiotic_water.F90 (239-239)
- Formula (d⁻¹): `wSiMinPaW`
- Code: `wSiAbioSiO2W = wSiMinPaW`

### `wSiMinPaW` [-] *Fluxes*
- DESC: diagnostic output rate Si particulate mineralization
- Source: abiotic_water.F90 (272-272)
- Formula (d⁻¹): `wSiMinPaW`
- Code: `_SET_DIAGNOSTIC_(self%id_wSiMinPaW, wSiMinPaW)`

### `tDAbioIMS` [-] *Fluxes*
- DESC: total ROC of IM in sediment
- Source: abiotic_sediment.F90 (281-281)
- Formula (d⁻¹): `0.0`
- Code: `tDAbioIMS = 0.0_rk`

### `tNAbioNH4S` [-] *Fluxes*
- DESC: total ROC of NH4 in the sediment
- Source: abiotic_sediment.F90 (284-284)
- Formula (d⁻¹): `- tNNitrS`
- Code: `tNAbioNH4S = - tNNitrS`

### `tNAbioNO3S` [-] *Fluxes*
- DESC: total ROC of NO3 in the sediment
- Source: abiotic_sediment.F90 (285-285)
- Formula (d⁻¹): `tNNitrS - tNDenitS`
- Code: `tNAbioNO3S = tNNitrS - tNDenitS`

### `tNDenitS` [-] *Fluxes*
- DESC: diagnostic output rate denitrification
- Source: abiotic_sediment.F90 (339-339)
- Formula (d⁻¹): `tNDenitS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDenitS, tNDenitS)`

### `tNNitrS` [-] *Fluxes*
- DESC: diagnostic output rate nitrification
- Source: abiotic_sediment.F90 (338-338)
- Formula (d⁻¹): `tNNitrS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNNitrS, tNNitrS)`

### `tPAbioAIMS` [-] *Fluxes*
- DESC: total ROC of absorbed P in the sediment
- Source: abiotic_sediment.F90 (283-283)
- Formula (d⁻¹): `tPSorpIMS`
- Code: `tPAbioAIMS = tPSorpIMS`

### `tPAbioPO4S` [-] *Fluxes*
- DESC: total ROC of PO4 in the sediment
- Source: abiotic_sediment.F90 (282-282)
- Formula (d⁻¹): `- tPSorpIMS - tPChemPO4`
- Code: `tPAbioPO4S = - tPSorpIMS - tPChemPO4`

### `tPChemPO4` [-] *Fluxes*
- DESC: diagnostic output rate chem. loss of diss. P
- Source: abiotic_sediment.F90 (336-336)
- Formula (d⁻¹): `tPChemPO4`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPChemPO4, tPChemPO4)`

### `tPSorpIMS` [-] *Fluxes*
- DESC: diagnostic output rate P sorped to IM
- Source: abiotic_sediment.F90 (337-337)
- Formula (d⁻¹): `tPSorpIMS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSorpIMS, tPSorpIMS)`

### `tSiAbioPaS` [-] *Fluxes*
- DESC: total ROC of POM Si in the sediment
- Source: abiotic_sediment.F90 (286-286)
- Formula (d⁻¹): `- tSiMinPaS`
- Code: `tSiAbioPaS = - tSiMinPaS`

### `tSiMinPaS` [-] *Fluxes*
- DESC: diagnostic output rate Si particulate mineralization
- Source: abiotic_sediment.F90 (340-340)
- Formula (d⁻¹): `tSiMinPaS`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiMinPaS, tSiMinPaS)`

### `tSiO2AbioS` [-] *Fluxes*
- DESC: total ROC of SiO2 in the sediment
- Source: abiotic_sediment.F90 (287-287)
- Formula (d⁻¹): `tSiMinPaS`
- Code: `tSiO2AbioS = tSiMinPaS`

### `wCZooCO2W` [gC/m3/s] *Fluxes*
- DESC: calculate C flux to CO2 in water
- Source: zooplankton.F90 (383)
- Formula (d⁻¹): `wCRespZoo`
- Code: `wCZooCO2W = wCRespZoo`

### `wCZooDOMW` [gC/m3/s] *Fluxes*
- DESC: calcualte dissolved fraction of organic carbon flux
- Source: zooplankton.F90 (386)
- Formula (d⁻¹): `wCZooTOMW * fZooDOMW`
- Code: `wCZooDOMW = wCZooTOMW * self%fZooDOMW`

### `wCZooPOMW` [gC/m3/s] *Fluxes*
- DESC: calculate particulate fraction of organic carbon flux
- Source: zooplankton.F90 (385)
- Formula (d⁻¹): `wCZooTOMW * (1.0_rk - fZooDOMW)`
- Code: `wCZooPOMW = wCZooTOMW * (1.0_rk - self%fZooDOMW)`

### `wCZooTOMW` [gC/m3/s] *Fluxes*
- DESC: calculate total organic carbon flux
- Source: zooplankton.F90 (384)
- Formula (d⁻¹): `wCMortZoo + wCEgesZoo`
- Code: `wCZooTOMW = wCMortZoo + wCEgesZoo`

### `wDZooDOMW` [gDW/m3/s] *Fluxes*
- DESC: calculate dissolved fraction of DW flux
- Source: zooplankton.F90 (365)
- Formula (d⁻¹): `wDZooTOMW * fZooDOMW`
- Code: `wDZooDOMW = wDZooTOMW * self%fZooDOMW`

### `wDZooPOMW` [gDW/m3/s] *Fluxes*
- DESC: calculate particulate fraction of DW flux
- Source: zooplankton.F90 (364)
- Formula (d⁻¹): `wDZooTOMW * (1.0_rk - fZooDOMW)`
- Code: `wDZooPOMW = wDZooTOMW * (1.0_rk - self%fZooDOMW)`

### `wDZooTOMW` [gDW/m3/s] *Fluxes*
- DESC: calculate total flux of DW to the water column
- Source: zooplankton.F90 (363)
- Formula (d⁻¹): `wDEgesZoo + wDMortZoo`
- Code: `wDZooTOMW = wDEgesZoo + wDMortZoo`

### `wNZooDOMW` [gN/m3/s] *Fluxes*
- DESC: calcualte dissolved fraction of organic nitrogen flux
- Source: zooplankton.F90 (372)
- Formula (d⁻¹): `wNZooTOMW * fZooDOMW`
- Code: `wNZooDOMW = wNZooTOMW * self%fZooDOMW`

### `wNZooNH4W` [gN/m3/s] *Fluxes*
- DESC: calculate dissolved fraction of N flux to the water column
- Source: zooplankton.F90 (369)
- Formula (d⁻¹): `wNExcrZoo + fDissEgesZoo*wNEgesZoo + fDissMortZoo*wNMortZoo`
- Code: `wNZooNH4W = wNExcrZoo + self%fDissEgesZoo*wNEgesZoo + self%fDissMortZoo*wNMortZoo`

### `wNZooPOMW` [gN/m3/s] *Fluxes*
- DESC: calculate particulate fraction of organic nitrogen flux
- Source: zooplankton.F90 (371)
- Formula (d⁻¹): `wNZooTOMW * (1.0_rk - fZooDOMW)`
- Code: `wNZooPOMW = wNZooTOMW * (1.0_rk - self%fZooDOMW)`

### `wNZooTOMW` [gN/m3/s] *Fluxes*
- DESC: calculate total organic nitrogen flux
- Source: zooplankton.F90 (370)
- Formula (d⁻¹): `wNMortZoo * (1.0_rk - fDissMortZoo) + wNEgesZoo * (1.0_rk - fDissEgesZoo)`
- Code: `wNZooTOMW = wNMortZoo * (1.0_rk - self%fDissMortZoo) + wNEgesZoo * (1.0_rk - self%fDissEgesZoo)`

### `wPZooDOMW` [gP/m3/s] *Fluxes*
- DESC: calcualte dissolved fraction of organic phosphorous flux
- Source: zooplankton.F90 (379)
- Formula (d⁻¹): `wPZooTOMW * fZooDOMW`
- Code: `wPZooDOMW = wPZooTOMW * self%fZooDOMW`

### `wPZooPO4W` [gP/m3/s] *Fluxes*
- DESC: calculate dissolved fraction of P flux to the water column
- Source: zooplankton.F90 (376)
- Formula (d⁻¹): `wPExcrZoo + fDissEgesZoo*wPEgesZoo + fDissMortZoo * wPMortZoo`
- Code: `wPZooPO4W = wPExcrZoo + self%fDissEgesZoo*wPEgesZoo + self%fDissMortZoo * wPMortZoo`

### `wPZooPOMW` [gP/m3/s] *Fluxes*
- DESC: calculate particulate fraction of organic phosphorous flux
- Source: zooplankton.F90 (378)
- Formula (d⁻¹): `wPZooTOMW * (1.0_rk - fZooDOMW)`
- Code: `wPZooPOMW = wPZooTOMW * (1.0_rk - self%fZooDOMW)`

### `wPZooTOMW` [gP/m3/s] *Fluxes*
- DESC: calculate total organic phosphorous flux
- Source: zooplankton.F90 (377)
- Formula (d⁻¹): `wPMortZoo * (1.0_rk - fDissMortZoo) + wPEgesZoo * (1.0_rk - fDissEgesZoo)`
- Code: `wPZooTOMW = wPMortZoo * (1.0_rk - self%fDissMortZoo) + wPEgesZoo * (1.0_rk - self%fDissEgesZoo)`

### `wSiO2ZooW` [gSi/m3/s] *Fluxes*
- DESC: flux of silica to the water column, dissolved fraction
- Source: zooplankton.F90 (390)
- Formula (d⁻¹): `sum((sSiprey/sDprey) * wDConsZoo) * fZooDOMW`
- Code: `wSiO2ZooW = sum((sSiprey/sDprey) * wDConsZoo) * self%fZooDOMW`

### `wSiPaZooW` [gSi/m3/s] *Fluxes*
- DESC: flux of silica to the water column, particulate fraction
- Source: zooplankton.F90 (391)
- Formula (d⁻¹): `sum((sSiprey/sDprey) * wDConsZoo) * (1.0_rk - fZooDOMW)`
- Code: `wSiPaZooW = sum((sSiprey/sDprey) * wDConsZoo) * (1.0_rk - self%fZooDOMW)`

### `tCBentCO2S` [gC/m2/s] *Fluxes*
- DESC: calculate total CO2 flux to the sediment
- Source: zoobenthos.F90 (438)
- Formula (d⁻¹): `tCRespBent`
- Code: `tCBentCO2S = tCRespBent`

### `tCBentDOMS` [gC/m2/s] *Fluxes*
- DESC: calculate dissolved fraction of organic C flux to the sediment
- Source: zoobenthos.F90 (442)
- Formula (d⁻¹): `tCBentTPOMS * fBentDOMS`
- Code: `tCBentDOMS = tCBentTPOMS * self%fBentDOMS`

### `tCBentPOMS` [gC/m2/s] *Fluxes*
- DESC: calculate particulate fraction of C flux
- Source: zoobenthos.F90 (441)
- Formula (d⁻¹): `tCBentTPOMS`
- Code: `tCBentPOMS = tCBentTPOMS`

### `tCBentTOMS` [gC/m2/s] *Fluxes*
- DESC: calculate total organic C flux to the sediment
- Source: zoobenthos.F90 (439)
- Formula (d⁻¹): `tCEgesBent + tCMortBent`
- Code: `tCBentTOMS = tCEgesBent + tCMortBent`

### `tCBentTPOMS` [gC/m2/s] *Fluxes*
- DESC: [BUG] calculate particulate organic C flux from zoobenthos (RHS should be tCBentTOMS, not tCBentTPOMS)
- Source: zoobenthos.F90 (440)
- Formula (d⁻¹): `tCBentTOMS * (1.0_rk -fBentDOMS)`
- Code: `tCBentTPOMS = tCBentTPOMS * (1.0_rk -self%fBentDOMS)`

### `tCMigrBent` [gC/m2/s] *Fluxes*
- DESC: calculate migration in C
- Source: zoobenthos.F90 (391)
- Formula (d⁻¹): `kMigrBent *(cCDRef*cDBentIn - sCBent)`
- Code: `tCMigrBent = self%kMigrBent *(self%cCDRef*self%cDBentIn - sCBent)`

### `tDBentDOMS` [gDW/m2/s] *Fluxes*
- DESC: calculate dissolved fraction of DW flux
- Source: zoobenthos.F90 (409)
- Formula (d⁻¹): `tDBentTOMS * fBentDOMS`
- Code: `tDBentDOMS = tDBentTOMS * self%fBentDOMS`

### `tDBentPOMS` [gDW/m2/s] *Fluxes*
- DESC: calculate particulate fraction of DW flux
- Source: zoobenthos.F90 (408)
- Formula (d⁻¹): `tDBentTPOMS`
- Code: `tDBentPOMS = tDBentTPOMS`

### `tDBentTOMS` [gDW/m2/s] *Fluxes*
- DESC: calculate total flux of DW to the sediment
- Source: zoobenthos.F90 (406)
- Formula (d⁻¹): `tDEgesBent + tDMortBent`
- Code: `tDBentTOMS = tDEgesBent + tDMortBent`

### `tDBentTPOMS` [gDW/m2/s] *Fluxes*
- DESC: calculate particulate organic DW flux from zoobenthos
- Source: zoobenthos.F90 (407)
- Formula (d⁻¹): `tDBentTOMS * (1.0_rk -fBentDOMS)`
- Code: `tDBentTPOMS = tDBentTOMS * (1.0_rk -self%fBentDOMS)`

### `tDMigrBent` [gDW/m2/s] *Fluxes*
- DESC: calculate migration in DW
- Source: zoobenthos.F90 (388)
- Formula (d⁻¹): `kMigrBent *(cDBentIn - sDBent)`
- Code: `tDMigrBent = self%kMigrBent *(self%cDBentIn - sDBent)`

### `tNBentDOMS` [gN/m2/s] *Fluxes*
- DESC: calculate total dissolved organic N flux to the sediment
- Source: zoobenthos.F90 (422)
- Formula (d⁻¹): `tNBentTOMS * fBentDOMS`
- Code: `tNBentDOMS = tNBentTOMS * self%fBentDOMS`

### `tNBentNH4S` [gN/m2/s] *Fluxes*
- DESC: calculate total ammonia flux to the sediment
- Source: zoobenthos.F90 (415)
- Formula (d⁻¹): `tNExcrBent + tNEgesBentNH4 + tNMortBentNH4`
- Code: `tNBentNH4S = tNExcrBent + tNEgesBentNH4 + tNMortBentNH4`

### `tNBentNO3S` [gN/m2/s] *Fluxes*
- DESC: calculate total nitrate flux to the sediment
- Source: zoobenthos.F90 (416)
- Formula (d⁻¹): `0.0_rk`
- Code: `tNBentNO3S = 0.0_rk`

### `tNBentPOMS` [gN/m2/s] *Fluxes*
- DESC: calculate total particulate organic N flux to the sediment
- Source: zoobenthos.F90 (421)
- Formula (d⁻¹): `tNBentTPOMS`
- Code: `tNBentPOMS = tNBentTPOMS`

### `tNBentTOMS` [gN/m2/s] *Fluxes*
- DESC: calculate total organic N flux to the sediment
- Source: zoobenthos.F90 (419)
- Formula (d⁻¹): `tNEgesBentTOM + tNMortBentTOM`
- Code: `tNBentTOMS = tNEgesBentTOM + tNMortBentTOM`

### `tNBentTPOMS` [gN/m2/s] *Fluxes*
- DESC: calculate particulate organic N flux from zoobenthos
- Source: zoobenthos.F90 (420)
- Formula (d⁻¹): `tNBentTOMS * (1.0_rk - fBentDOMS)`
- Code: `tNBentTPOMS = tNBentTOMS * (1.0_rk - self%fBentDOMS)`

### `tNEgesBentNH4` [gN/m2/s] *Fluxes*
- DESC: calculate ammonia fraction of egestion flux to the sediment
- Source: zoobenthos.F90 (414)
- Formula (d⁻¹): `fDissEgesBent * tNEgesBent`
- Code: `tNEgesBentNH4 = self%fDissEgesBent * tNEgesBent`

### `tNEgesBentTOM` [gN/m2/s] *Fluxes*
- DESC: calculate organic fraction of egestion N flux to the sediment
- Source: zoobenthos.F90 (418)
- Formula (d⁻¹): `(1.0_rk - fDissEgesBent) * tNEgesBent`
- Code: `tNEgesBentTOM = (1.0_rk - self%fDissEgesBent) * tNEgesBent`

### `tNMigrBent` [gN/m2/s] *Fluxes*
- DESC: calculate migration in N
- Source: zoobenthos.F90 (390)
- Formula (d⁻¹): `kMigrBent *(cNDRef*cDBentIn - sNBent)`
- Code: `tNMigrBent = self%kMigrBent *(self%cNDRef*self%cDBentIn - sNBent)`

### `tNMortBentNH4` [gN/m2/s] *Fluxes*
- DESC: calculate ammonia fraction of mortality flux to the sediment
- Source: zoobenthos.F90 (413)
- Formula (d⁻¹): `fDissMortBent*tNMortBent`
- Code: `tNMortBentNH4 = self%fDissMortBent*tNMortBent`

### `tNMortBentTOM` [gN/m2/s] *Fluxes*
- DESC: calculate organic fraction of mortality N flux to the sediment
- Source: zoobenthos.F90 (417)
- Formula (d⁻¹): `(1.0_rk-fDissMortBent)*tNMortBent`
- Code: `tNMortBentTOM = (1.0_rk-self%fDissMortBent)*tNMortBent`

### `tPBentDOMS` [gP/m2/s] *Fluxes*
- DESC: calculate dissolved fraction of organic P flux to the sediment
- Source: zoobenthos.F90 (434)
- Formula (d⁻¹): `tPBentTOMS * fBentDOMS`
- Code: `tPBentDOMS = tPBentTOMS * self%fBentDOMS`

### `tPBentPO4S` [gP/m2/s] *Fluxes*
- DESC: calculate total phosphate flux to the sediment
- Source: zoobenthos.F90 (428)
- Formula (d⁻¹): `tPExcrBent + tPEgesBentPO4 + tPMortBentPO4`
- Code: `tPBentPO4S = tPExcrBent + tPEgesBentPO4 + tPMortBentPO4`

### `tPBentPOMS` [gP/m2/s] *Fluxes*
- DESC: calculate particulate organic P flux to the sediment
- Source: zoobenthos.F90 (433)
- Formula (d⁻¹): `tPBentTPOMS`
- Code: `tPBentPOMS = tPBentTPOMS`

### `tPBentTOMS` [gP/m2/s] *Fluxes*
- DESC: calculate total organic P flux to the sediment
- Source: zoobenthos.F90 (431)
- Formula (d⁻¹): `tPEgesBentTOM + tPMortBentTOM`
- Code: `tPBentTOMS = tPEgesBentTOM + tPMortBentTOM`

### `tPBentTPOMS` [gP/m2/s] *Fluxes*
- DESC: calculate particulate organic P flux from zoobenthos
- Source: zoobenthos.F90 (432)
- Formula (d⁻¹): `tPBentTOMS * (1.0_rk -fBentDOMS)`
- Code: `tPBentTPOMS = tPBentTOMS * (1.0_rk -self%fBentDOMS)`

### `tPEgesBentPO4` [gP/m2/s] *Fluxes*
- DESC: calculate phosphate fraction of egestion flux to the sediment
- Source: zoobenthos.F90 (427)
- Formula (d⁻¹): `fDissEgesBent * tPEgesBent`
- Code: `tPEgesBentPO4 = self%fDissEgesBent * tPEgesBent`

### `tPEgesBentTOM` [gP/m2/s] *Fluxes*
- DESC: calculate organic fraction of egestion P flux to the sediment
- Source: zoobenthos.F90 (430)
- Formula (d⁻¹): `(1.0_rk - fDissEgesBent) * tPEgesBent`
- Code: `tPEgesBentTOM = (1.0_rk - self%fDissEgesBent) * tPEgesBent`

### `tPMigrBent` [gP/m2/s] *Fluxes*
- DESC: calculate migration in P
- Source: zoobenthos.F90 (389)
- Formula (d⁻¹): `kMigrBent *(cPDRef*cDBentIn - sPBent)`
- Code: `tPMigrBent = self%kMigrBent *(self%cPDRef*self%cDBentIn - sPBent)`

### `tPMortBentPO4` [gP/m2/s] *Fluxes*
- DESC: calculate phosphate fraction of mortality flux to the sediment
- Source: zoobenthos.F90 (426)
- Formula (d⁻¹): `fDissMortBent * tPMortBent`
- Code: `tPMortBentPO4 = self%fDissMortBent * tPMortBent`

### `tPMortBentTOM` [gP/m2/s] *Fluxes*
- DESC: calculate organic fraction of mortality P flux to the sediment
- Source: zoobenthos.F90 (429)
- Formula (d⁻¹): `(1.0_rk-fDissMortBent)*tPMortBent`
- Code: `tPMortBentTOM = (1.0_rk-self%fDissMortBent)*tPMortBent`

### `tSiBentPaS` [gSi/m2/s] *Fluxes*
- DESC: flux of silica to the water column, particulate fraction
- Source: zoobenthos.F90 (446)
- Formula (d⁻¹): `sum((sSiprey/sDprey) * tDConsBent) * (1.0_rk - fBentDOMS)`
- Code: `tSiBentPaS = sum((sSiprey/sDprey) * tDConsBent) * (1.0_rk - self%fBentDOMS)`

### `tSiO2BentS` [gSi/m2/s] *Fluxes*
- DESC: flux of silica to the water column, dissolved fraction
- Source: zoobenthos.F90 (447)
- Formula (d⁻¹): `sum((sSiprey/sDprey) * tDConsBent) * fBentDOMS`
- Code: `tSiO2BentS = sum((sSiprey/sDprey) * tDConsBent) * self%fBentDOMS`

### `tCFiCO2W` [-] *Fluxes*
- DESC: calculate total CO2 flux to the sediment
- Source: fish.F90 (959)
- Formula (d⁻¹): `tCFiCO2W = tCRespFi`
- Code: `tCFiCO2W = tCRespFi`

### `tCFiDOMW` [-] *Fluxes*
- DESC: calculate dissolved fraction of C flux to water column
- Source: fish.F90 (964)
- Formula (d⁻¹): `tCFiDOMW = tCFiTOMW * self%fFiDOMW`
- Code: `tCFiDOMW = tCFiTOMW * self%fFiDOMW`

### `tCFiPOMW` [-] *Fluxes*
- DESC: calculate particulate fraction of C flux to water column
- Source: fish.F90 (963)
- Formula (d⁻¹): `tCFiPOMW = tCFiTOMW * (1.0_rk - self%fFiDOMW)`
- Code: `tCFiPOMW = tCFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tCFiTOMW` [-] *Fluxes*
- DESC: calculate total flux of C to the water column
- Source: fish.F90 (962)
- Formula (d⁻¹): `tCFiTOMW = tCEgesFi + tCMortFiTOM`
- Code: `tCFiTOMW = tCEgesFi + tCMortFiTOM`

### `tDFiDOMW` [-] *Fluxes*
- DESC: calculate dissolved fraction of DW flux to water column
- Source: fish.F90 (931)
- Formula (d⁻¹): `tDFiDOMW = tDFiTOMW * self%fFiDOMW`
- Code: `tDFiDOMW = tDFiTOMW * self%fFiDOMW`

### `tDFiPOMW` [-] *Fluxes*
- DESC: calculate particulate fraction of DW flux to water column
- Source: fish.F90 (930)
- Formula (d⁻¹): `tDFiPOMW = tDFiTOMW * (1.0_rk - self%fFiDOMW)`
- Code: `tDFiPOMW = tDFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tDFiTOMW` [-] *Fluxes*
- DESC: calculate total flux of DW to the water column
- Source: fish.F90 (929)
- Formula (d⁻¹): `tDFiTOMW = tDEgesFi + tDMortFiTOM`
- Code: `tDFiTOMW = tDEgesFi + tDMortFiTOM`

### `tNEgesFiNH4` [-] *Fluxes*
- DESC: calculate dissolved N part of egestion flux
- Source: fish.F90 (935)
- Formula (d⁻¹): `tNEgesFiNH4 = self%fDissEgesFish * tNEgesFi`
- Code: `tNEgesFiNH4 = self%fDissEgesFish * tNEgesFi`

### `tNEgesFiTOM` [-] *Fluxes*
- DESC: calculate organic N part of egestion
- Source: fish.F90 (940)
- Formula (d⁻¹): `tNEgesFiTOM = tNEgesFi - tNEgesFiNH4`
- Code: `tNEgesFiTOM = tNEgesFi - tNEgesFiNH4`

### `tNFiDOMW` [-] *Fluxes*
- DESC: calculate dissolved part of organic N flux to water column
- Source: fish.F90 (943)
- Formula (d⁻¹): `tNFiDOMW = tNFiTOMW * self%fFiDOMW`
- Code: `tNFiDOMW = tNFiTOMW * self%fFiDOMW`

### `tNFiNH4W` [-] *Fluxes*
- DESC: calculate total dissolved N flux to the water column
- Source: fish.F90 (938)
- Formula (d⁻¹): `tNFiNH4W = tNExcrFi + tNEgesFiNH4 + tNMortFiNH4`
- Code: `tNFiNH4W = tNExcrFi + tNEgesFiNH4 + tNMortFiNH4`

### `tNFiPOMW` [-] *Fluxes*
- DESC: calculate particulate part of organic N flux to water column
- Source: fish.F90 (942)
- Formula (d⁻¹): `tNFiPOMW = tNFiTOMW * (1.0_rk - self%fFiDOMW)`
- Code: `tNFiPOMW = tNFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tNFiTOMW` [-] *Fluxes*
- DESC: calculate total organic N flux to the water column
- Source: fish.F90 (941)
- Formula (d⁻¹): `tNFiTOMW = tNEgesFiTOM + tNMortFiTOM`
- Code: `tNFiTOMW = tNEgesFiTOM + tNMortFiTOM`

### `tNMortFiNH4` [-] *Fluxes*
- DESC: calculate dissolved N part of mortality flux
- Source: fish.F90 (937)
- Formula (d⁻¹): `tNMortFiNH4 = self%fDissMortFish *(tNMortFi - tNMortFiBot)`
- Code: `tNMortFiNH4 = self%fDissMortFish *(tNMortFi - tNMortFiBot)`

### `tNMortFiTOM` [-] *Fluxes*
- DESC: calculate organic N part of mortality flux
- Source: fish.F90 (939)
- Formula (d⁻¹): `tNMortFiTOM = tNMortFi - tNMortFiBot - tNMortFiNH4`
- Code: `tNMortFiTOM = tNMortFi - tNMortFiBot - tNMortFiNH4`

### `tPEgesFiPO4` [-] *Fluxes*
- DESC: calculate dissolved P part of egestion flux
- Source: fish.F90 (947)
- Formula (d⁻¹): `tPEgesFiPO4 = self%fDissEgesFish * tPEgesFi`
- Code: `tPEgesFiPO4 = self%fDissEgesFish * tPEgesFi`

### `tPEgesFiTOM` [-] *Fluxes*
- DESC: calculate organic P part of egestion
- Source: fish.F90 (952)
- Formula (d⁻¹): `tPEgesFiTOM = tPEgesFi - tPEgesFiPO4`
- Code: `tPEgesFiTOM = tPEgesFi - tPEgesFiPO4`

### `tPFiDOMW` [-] *Fluxes*
- DESC: calculate dissolved part of organic P flux to water column
- Source: fish.F90 (955)
- Formula (d⁻¹): `tPFiDOMW = tPFiTOMW * self%fFiDOMW`
- Code: `tPFiDOMW = tPFiTOMW * self%fFiDOMW`

### `tPFiPO4W` [-] *Fluxes*
- DESC: calculate total dissolved P flux to the water column
- Source: fish.F90 (950)
- Formula (d⁻¹): `tPFiPO4W= tPExcrFi + tPEgesFiPO4 + tPMortFiPO4`
- Code: `tPFiPO4W= tPExcrFi + tPEgesFiPO4 + tPMortFiPO4`

### `tPFiPOMW` [-] *Fluxes*
- DESC: calculate particulate part of organic P flux to water column
- Source: fish.F90 (954)
- Formula (d⁻¹): `tPFiPOMW = tPFiTOMW * (1.0_rk - self%fFiDOMW)`
- Code: `tPFiPOMW = tPFiTOMW * (1.0_rk - self%fFiDOMW)`

### `tPFiTOMW` [-] *Fluxes*
- DESC: calculate total organic P flux to the water column
- Source: fish.F90 (953)
- Formula (d⁻¹): `tPFiTOMW = tPEgesFiTOM + tPMortFiTOM`
- Code: `tPFiTOMW = tPEgesFiTOM + tPMortFiTOM`

### `tPMortFiPO4` [-] *Fluxes*
- DESC: calculate dissolved P part of mortality flux
- Source: fish.F90 (949)
- Formula (d⁻¹): `tPMortFiPO4 = self%fDissMortFish *(tPMortFi - tPMortFiBot)`
- Code: `tPMortFiPO4 = self%fDissMortFish *(tPMortFi - tPMortFiBot)`

### `tPMortFiTOM` [-] *Fluxes*
- DESC: calculate organic P part of mortality flux
- Source: fish.F90 (951)
- Formula (d⁻¹): `tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4`
- Code: `tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4`

### `tCAbioDOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of DOM C in the sediment per group (dim nDOM)
- Source: sediment_exchange.F90 (544)
- Formula (d⁻¹): `tCAbioDOMS = -tCDifDOM - tCResusDOM`
- Code: `tCAbioDOMS  = -tCDifDOM  - tCResusDOM`

### `tCAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM C in the sediment per group (dim nPOM)
- Source: sediment_exchange.F90 (539)
- Formula (d⁻¹): `tCAbioPOMS = tCSedPOM - tCResusPOM`
- Code: `tCAbioPOMS  = tCSedPOM  - tCResusPOM`

### `tDAbioDOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of DOM DW in the sediment per group (dim nDOM)
- Source: sediment_exchange.F90 (541)
- Formula (d⁻¹): `tDAbioDOMS = -tDDifDOM - tDResusDOM`
- Code: `tDAbioDOMS  = -tDDifDOM  - tDResusDOM`

### `tDAbioIMS` [g/m2/s] *Fluxes*
- DESC: total ROC of IM DW in the sediment
- Source: sediment_exchange.F90 (552)
- Formula (d⁻¹): `tDAbioIMS = tDSedIM - tDResusIM`
- Code: `tDAbioIMS   = tDSedIM   - tDResusIM`

### `tDAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM DW in the sediment per group (dim nPOM)
- Source: sediment_exchange.F90 (536)
- Formula (d⁻¹): `tDAbioPOMS = tDSedPOM - tDResusPOM`
- Code: `tDAbioPOMS  = tDSedPOM  - tDResusPOM`

### `tNAbioDOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of DOM N in the sediment per group (dim nDOM)
- Source: sediment_exchange.F90 (543)
- Formula (d⁻¹): `tNAbioDOMS = -tNDifDOM - tNResusDOM`
- Code: `tNAbioDOMS  = -tNDifDOM  - tNResusDOM`

### `tNAbioNH4S` [g/m2/s] *Fluxes*
- DESC: total ROC of NH4 in the sediment
- Source: sediment_exchange.F90 (548)
- Formula (d⁻¹): `tNAbioNH4S = -tNDifNH4 - tNResusNH4`
- Code: `tNAbioNH4S  = -tNDifNH4 - tNResusNH4`

### `tNAbioNO3S` [g/m2/s] *Fluxes*
- DESC: total ROC of NO3 in the sediment
- Source: sediment_exchange.F90 (549)
- Formula (d⁻¹): `tNAbioNO3S = -tNDifNO3 - tNResusNO3`
- Code: `tNAbioNO3S  = -tNDifNO3 - tNResusNO3`

### `tNAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM N in the sediment per group (dim nPOM)
- Source: sediment_exchange.F90 (538)
- Formula (d⁻¹): `tNAbioPOMS = tNSedPOM - tNResusPOM`
- Code: `tNAbioPOMS  = tNSedPOM  - tNResusPOM`

### `tPAbioAIMS` [g/m2/s] *Fluxes*
- DESC: total ROC of absorbed P in the sediment
- Source: sediment_exchange.F90 (547)
- Formula (d⁻¹): `tPAbioAIMS = tPSedAIM - tPResusAIM`
- Code: `tPAbioAIMS  = tPSedAIM  - tPResusAIM`

### `tPAbioDOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of DOM P in the sediment per group (dim nDOM)
- Source: sediment_exchange.F90 (542)
- Formula (d⁻¹): `tPAbioDOMS = -tPDifDOM - tPResusDOM`
- Code: `tPAbioDOMS  = -tPDifDOM  - tPResusDOM`

### `tPAbioPO4S` [g/m2/s] *Fluxes*
- DESC: total ROC of PO4 in the sediment
- Source: sediment_exchange.F90 (546)
- Formula (d⁻¹): `tPAbioPO4S = -tPDifPO4 - tPResusPO4`
- Code: `tPAbioPO4S  = -tPDifPO4 - tPResusPO4`

### `tPAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM P in the sediment per group (dim nPOM)
- Source: sediment_exchange.F90 (537)
- Formula (d⁻¹): `tPAbioPOMS = tPSedPOM - tPResusPOM`
- Code: `tPAbioPOMS  = tPSedPOM  - tPResusPOM`

### `tSiAbioPaS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM Si in the sediment
- Source: sediment_exchange.F90 (551)
- Formula (d⁻¹): `tSiAbioPaS = tSiSedPa - tSiResusPa`
- Code: `tSiAbioPaS  = tSiSedPa  - tSiResusPa`

### `tSiAbioSiO2S` [g/m2/s] *Fluxes*
- DESC: total ROC of SiO2 in the sediment
- Source: sediment_exchange.F90 (550)
- Formula (d⁻¹): `tSiAbioSiO2S = -tSiDifSiO2 - tSiResusSiO2`
- Code: `tSiAbioSiO2S = -tSiDifSiO2 - tSiResusSiO2`

### `tDAbioIMS` [g/m2/s] *Fluxes*
- DESC: total ROC of IM DW in the sediment
- Source: resus_sed.F90 (269)
- Formula (d⁻¹): `tDAbioIMS = tDSetIM - tDResusIM`
- Code: `tDAbioIMS   = tDSetIM   - tDResusIM`

### `tDAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM DW in the sediment
- Source: resus_sed.F90 (270)
- Formula (d⁻¹): `tDAbioPOMS = tDSetPOM - tDResusPOM`
- Code: `tDAbioPOMS  = tDSetPOM  - tDResusPOM`

### `tNAbioNH4S` [g/m2/s] *Fluxes*
- DESC: total ROC of NH4 in the sediment (no diffusion - simplified)
- Source: resus_sed.F90 (274)
- Formula (d⁻¹): `tNAbioNH4S = -tNResusNH4`
- Code: `tNAbioNH4S  =           - tNResusNH4`

### `tNAbioNO3S` [g/m2/s] *Fluxes*
- DESC: total ROC of NO3 in the sediment (no diffusion - simplified)
- Source: resus_sed.F90 (275)
- Formula (d⁻¹): `tNAbioNO3S = -tNResusNO3`
- Code: `tNAbioNO3S  =           - tNResusNO3`

### `tNAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM N in the sediment
- Source: resus_sed.F90 (276)
- Formula (d⁻¹): `tNAbioPOMS = tNSetPOM - tNResusPOM`
- Code: `tNAbioPOMS  = tNSetPOM  - tNResusPOM`

### `tPAbioAIMS` [g/m2/s] *Fluxes*
- DESC: total ROC of absorbed P in the sediment
- Source: resus_sed.F90 (273)
- Formula (d⁻¹): `tPAbioAIMS = tPSetAIM - tPResusAIM`
- Code: `tPAbioAIMS  = tPSetAIM  - tPResusAIM`

### `tPAbioPO4S` [g/m2/s] *Fluxes*
- DESC: total ROC of PO4 in the sediment (no diffusion - simplified)
- Source: resus_sed.F90 (272)
- Formula (d⁻¹): `tPAbioPO4S = -tPResusPO4`
- Code: `tPAbioPO4S  =           - tPResusPO4`

### `tPAbioPOMS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM P in the sediment
- Source: resus_sed.F90 (271)
- Formula (d⁻¹): `tPAbioPOMS = tPSetPOM - tPResusPOM`
- Code: `tPAbioPOMS  = tPSetPOM  - tPResusPOM`

### `tSiAbioPaS` [g/m2/s] *Fluxes*
- DESC: total ROC of POM Si in the sediment
- Source: resus_sed.F90 (277)
- Formula (d⁻¹): `tSiAbioPaS = tSiSetPa - tSiResusPa`
- Code: `tSiAbioPaS  = tSiSetPa  - tSiResusPa`

### `tCBivBiva` [g/m2/s] *Fluxes*
- DESC: final rate of change of C
- Source: bivalves.F90 (574)
- Formula (d⁻¹): `tCBivBiva = tCAssBiv - tCRespBiv - tCEgesBiv - tCMortBiv - tCAgeBiv - tCReprBiv`
- Code: `tCBivBiva = tCAssBiv - tCRespBiv - tCEgesBiv - tCMortBiv - tCAgeBiv - tCReprBiv`

### `tCBivCO2S` [g/m2/s] *Fluxes*
- DESC: total CO2 flux to sediment (respiration)
- Source: bivalves.F90 (597)
- Formula (d⁻¹): `tCBivCO2S = tCRespBiv`
- Code: `tCBivCO2S = tCRespBiv`

### `tCBivPOMS` [g/m2/s] *Fluxes*
- DESC: total organic C flux to sediment (mortality)
- Source: bivalves.F90 (599)
- Formula (d⁻¹): `tCBivPOMS = tCMortBiv`
- Code: `tCBivPOMS = tCMortBiv`

### `tCBivPOMW` [g/m2/s] *Fluxes*
- DESC: total organic C flux to water (egestion)
- Source: bivalves.F90 (598)
- Formula (d⁻¹): `tCBivPOMW = tCEgesBiv`
- Code: `tCBivPOMW = tCEgesBiv`

### `tDBivBiva` [g/m2/s] *Fluxes*
- DESC: final rate of change of DW
- Source: bivalves.F90 (571)
- Formula (d⁻¹): `tDBivBiva = tDAssBiv - tDRespBiv - tDEgesBiv - tDMortBiv - tDAgeBiv - tDReprBiv`
- Code: `tDBivBiva = tDAssBiv - tDRespBiv - tDEgesBiv - tDMortBiv - tDAgeBiv - tDReprBiv`

### `tDBivPOMS` [g/m2/s] *Fluxes*
- DESC: total flux of DW to sediment (mortality)
- Source: bivalves.F90 (581)
- Formula (d⁻¹): `tDBivPOMS = tDMortBiv`
- Code: `tDBivPOMS = tDMortBiv`

### `tDBivPOMW` [g/m2/s] *Fluxes*
- DESC: total flux of DW to water column (egestion)
- Source: bivalves.F90 (580)
- Formula (d⁻¹): `tDBivPOMW = tDEgesBiv`
- Code: `tDBivPOMW = tDEgesBiv`

### `tNBivBiva` [g/m2/s] *Fluxes*
- DESC: final rate of change of N
- Source: bivalves.F90 (572)
- Formula (d⁻¹): `tNBivBiva = tNAssBiv - tNExcrBiv - tNEgesBiv - tNMortBiv - tNAgeBiv - tNReprBiv`
- Code: `tNBivBiva = tNAssBiv - tNExcrBiv - tNEgesBiv - tNMortBiv - tNAgeBiv - tNReprBiv`

### `tNBivNH4W` [g/m2/s] *Fluxes*
- DESC: total flux of NH4 to water column (excretion)
- Source: bivalves.F90 (585)
- Formula (d⁻¹): `tNBivNH4W = tNExcrBiv`
- Code: `tNBivNH4W = tNExcrBiv`

### `tNBivPOMS` [g/m2/s] *Fluxes*
- DESC: total flux of NPOM to sediment (mortality)
- Source: bivalves.F90 (587)
- Formula (d⁻¹): `tNBivPOMS = tNMortBiv`
- Code: `tNBivPOMS = tNMortBiv`

### `tNBivPOMW` [g/m2/s] *Fluxes*
- DESC: total flux of NPOM to water column (egestion)
- Source: bivalves.F90 (586)
- Formula (d⁻¹): `tNBivPOMW = tNEgesBiv`
- Code: `tNBivPOMW = tNEgesBiv`

### `tPBivBiva` [g/m2/s] *Fluxes*
- DESC: final rate of change of P
- Source: bivalves.F90 (573)
- Formula (d⁻¹): `tPBivBiva = tPAssBiv - tPExcrBiv - tPEgesBiv - tPMortBiv - tPAgeBiv - tPReprBiv`
- Code: `tPBivBiva = tPAssBiv - tPExcrBiv - tPEgesBiv - tPMortBiv - tPAgeBiv - tPReprBiv`

### `tPBivPO4W` [g/m2/s] *Fluxes*
- DESC: total flux of PO4 to water column (excretion)
- Source: bivalves.F90 (591)
- Formula (d⁻¹): `tPBivPO4W = tPExcrBiv`
- Code: `tPBivPO4W = tPExcrBiv`

### `tPBivPOMS` [g/m2/s] *Fluxes*
- DESC: total flux of PPOM to sediment (mortality)
- Source: bivalves.F90 (593)
- Formula (d⁻¹): `tPBivPOMS = tPMortBiv`
- Code: `tPBivPOMS = tPMortBiv`

### `tPBivPOMW` [g/m2/s] *Fluxes*
- DESC: total flux of PPOM to water column (egestion)
- Source: bivalves.F90 (592)
- Formula (d⁻¹): `tPBivPOMW = tPEgesBiv`
- Code: `tPBivPOMW = tPEgesBiv`

### `tSiO2BivS` [g/m2/s] *Fluxes*
- DESC: flux of silica to sediment due to bivalve feeding
- Source: bivalves.F90 (603)
- Formula (d⁻¹): `tSiO2BivS = sum((sSiprey/max(NearZero,sDprey)) * tDConsBiv)`
- Code: `tSiO2BivS = sum((sSiprey/max(NearZero,sDprey)) * tDConsBiv)`

## Food_saturation

### `aDSatFiBen` [-] *Food_saturation*
- DESC: bentivory saturation level (Michaelis-Menten form)
- Source: fish_pclake.F90 (509-511)
- Formula (d⁻¹): `aDSatFiBen = ((aFunVegBent*sum(sDBent*BENpref))^2)/(hDBentFi^2 + (aFunVegBent*sum(sDBent*BENpref))^2)`
- Code: `aDSatFiBen = ((aFunVegBent * sum(sDBent*self%BENpref)) * (aFunVegBent * sum(sDBent*self%BENpref))) / (self%hDBentFi * self%hDBentFi + (aFunVegBent * sum(sDBent*self%BENpref)) * (aFunVegBent * sum(sDBent*self%BENpref)))`

### `aDSatFiPisc` [-] *Food_saturation*
- DESC: piscivory saturation level (Michaelis-Menten form)
- Source: fish_pclake.F90 (516-517)
- Formula (d⁻¹): `aDSatFiPisc = (sum(sDPisc*PISCpref)^2)/(hDPiscFi^2 + sum(sDPisc*PISCpref)^2)`
- Code: `aDSatFiPisc = (sum(sDPisc*self%PISCpref) * sum(sDPisc*self%PISCpref)) / (self%hDPiscFi * self%hDPiscFi + sum(sDPisc*self%PISCpref) * sum(sDPisc*self%PISCpref))`

### `aDSatFiTot` [-] *Food_saturation*
- DESC: total (mean) saturation level
- Source: fish_pclake.F90 (522)
- Formula (d⁻¹): `aDSatFiTot = aDSatFiZoo*fFishZoo + aDSatFiBen*fFishBen + aDSatFiPisc*fFishPisc`
- Code: `aDSatFiTot = (aDSatFiZoo * fFishZoo + aDSatFiBen * fFishBen + aDSatFiPisc * fFishPisc)`

### `aDSatFiZoo` [-] *Food_saturation*
- DESC: zooplanktivory saturation level (Michaelis-Menten form)
- Source: fish_pclake.F90 (502-504)
- Formula (d⁻¹): `aDSatFiZoo = ((aFunVegZoo*sum(sDZoo*ZOOpref))^2)/(hDZooFi^2 + (aFunVegZoo*sum(sDZoo*ZOOpref))^2)`
- Code: `aDSatFiZoo = ((aFunVegZoo * sum(sDZoo*self%ZOOpref)) * (aFunVegZoo * sum(sDZoo*self%ZOOpref))) / (self%hDZooFi * self%hDZooFi + (aFunVegZoo * sum(sDZoo*self%ZOOpref)) * (aFunVegZoo * sum(sDZoo*self%ZOOpref)))`

## get_light_extinction

### `aDSubVeg` [-] *get_light_extinction*
- DESC: retrieve submerged macrophyte biomass (PV)
- Source: macrophytes.F90 (816)
- Formula (d⁻¹): `for get_light_extinction subroutine`
- Code: `_GET_(self%id_aDSubVeg_PV_in, aDSubVeg)`

### `extinction` [1/m] *get_light_extinction*
- DESC: self-shading contribution (background + macrophyte)
- Source: macrophytes.F90 (820)
- Formula (d⁻¹): `cExtSpVeg * aDSubVeg`
- Code: `_SET_EXTINCTION_(self%cExtSpVeg * aDSubVeg)`

## Groundwater

### `tNBurNH4` [g/m2/s] *Groundwater*
- DESC: case vDeltaS<0: burial flux of dissolved NH4 from groundwater
- Source: burial.F90 (372)
- Formula (d⁻¹): `tNBurNH4 = self%cNH4Ground *(bPorS * vDeltaS)`
- Code: `tNBurNH4 = self%cNH4Ground *(bPorS * vDeltaS)`

### `tNBurNO3` [g/m2/s] *Groundwater*
- DESC: case vDeltaS<0: burial flux of dissolved NO3 from groundwater
- Source: burial.F90 (373)
- Formula (d⁻¹): `tNBurNO3 = self%cNO3Ground *(bPorS * vDeltaS)`
- Code: `tNBurNO3 = self%cNO3Ground *(bPorS * vDeltaS)`

### `tPBurPO4` [g/m2/s] *Groundwater*
- DESC: case vDeltaS<0: burial flux of dissolved P from groundwater
- Source: burial.F90 (365)
- Formula (d⁻¹): `tPBurPO4 = self%cPO4Ground *(bPorS * vDeltaS)`
- Code: `tPBurPO4 = self%cPO4Ground *(bPorS * vDeltaS)`

## Growth rates

### `akDIncrVeg` [1/d] *Growth rates*
- DESC: intrinsic net increase rate of macrophytes
- Source: macrophytes.F90 (448)
- Formula (d⁻¹): `aMuTmLVeg - kDRespVeg*uFunTmRespVeg - bkMortVeg`
- Code: `akDIncrVeg = aMuTmLVeg - self%kDRespVeg * uFunTmRespVeg - bkMortVeg`

### `aMuVeg` [1/d] *Growth rates*
- DESC: actual growth rate of macrophytes
- Source: macrophytes.F90 (432)
- Formula (d⁻¹): `aMuTmLVeg * aNutLimVeg`
- Code: `aMuVeg = aMuTmLVeg * aNutLimVeg`

### `tCProdVeg` [gC/m2/s] *Growth rates*
- DESC: macrophyte C production
- Source: macrophytes.F90 (456)
- Formula (d⁻¹): `tDProdVeg * cCPerDW`
- Code: `tCProdVeg = tDProdVeg * self%cCPerDW`

### `tDEnvProdVeg` [gDW/m2/s] *Growth rates*
- DESC: logistic correction of production
- Source: macrophytes.F90 (450)
- Formula (d⁻¹): `aMuVeg/cMuMaxVeg * tDEnvVeg`
- Code: `tDEnvProdVeg = aMuVeg/self%cMuMaxVeg * tDEnvVeg`

### `tDEnvVeg` [gDW/m2/s] *Growth rates*
- DESC: logistic correction of macrophytes
- Source: macrophytes.F90 (449)
- Formula (d⁻¹): `max(0.0, (sDVeg+sDCompts)*sDVeg*akDIncrVeg/(cDCarrVeg+NearZero))`
- Code: `tDEnvVeg = max(0.0_rk, (sDVeg+sDCompts)*sDVeg*akDIncrVeg/(self%cDCarrVeg+NearZero))`

### `tDProdVeg` [gDW/m2/s] *Growth rates*
- DESC: macrophyte production w/ carrying capacity correction
- Source: macrophytes.F90 (452)
- Formula (d⁻¹): `max(0.0, aMuVeg*sDVeg - tDEnvProdVeg)`
- Code: `if (self%lCarrVeg) tDProdVeg = max(0.0_rk, aMuVeg * sDVeg - tDEnvProdVeg)`

### `tDProdVeg` [gDW/m2/s] *Growth rates*
- DESC: macrophyte production w/o carrying capacity correction
- Source: macrophytes.F90 (454)
- Formula (d⁻¹): `max(0.0, aMuVeg*sDVeg)`
- Code: `if (.NOT. self%lCarrVeg) tDProdVeg = max(0.0_rk, aMuVeg * sDVeg)`

## Humus formation

### `tCBurHum` [g/m2/s] *Humus formation*
- DESC: case vDeltaS<0: burial flux of C in humus (50% of tDBurOM)
- Source: burial.F90 (380)
- Formula (d⁻¹): `tCBurHum = 0.50_rk * tDBurOM`
- Code: `tCBurHum = 0.50_rk * tDBurOM`

### `tDBurHum` [g/m2/s] *Humus formation*
- DESC: case vDeltaS<0: burial flux of DW in humus (= tDBurOM)
- Source: burial.F90 (358)
- Formula (d⁻¹): `tDBurHum = tDBurOM`
- Code: `tDBurHum = tDBurOM`

### `tNBurHum` [g/m2/s] *Humus formation*
- DESC: case vDeltaS<0: burial flux of N in humus
- Source: burial.F90 (374)
- Formula (d⁻¹): `tNBurHum = 0.01_rk * tDBurHum`
- Code: `tNBurHum = 0.01_rk * tDBurHum`

### `tPBurHum` [g/m2/s] *Humus formation*
- DESC: case vDeltaS<0: burial flux of P in humus
- Source: burial.F90 (366)
- Formula (d⁻¹): `tPBurHum = 0.001_rk * tDBurHum`
- Code: `tPBurHum = 0.001_rk * tDBurHum`

## Ingestion

### `f_dens` [-] *Ingestion*
- DESC: density correction for ingestion (nKShares>0: use sDBivOS)
- Source: bivalves.F90 (432)
- Formula (d⁻¹): `f_dens = fdens_bivalve(sDBivOS, self%cDmaxOpt, self%cDmax)`
- Code: `f_dens = fdens_bivalve(sDBivOS, self%cDmaxOpt, self%cDmax)`

### `f_dens` [-] *Ingestion*
- DESC: density correction for ingestion (nKShares=0: use sDBiv)
- Source: bivalves.F90 (434)
- Formula (d⁻¹): `f_dens = fdens_bivalve(sDBiv, self%cDmaxOpt, self%cDmax)`
- Code: `f_dens = fdens_bivalve(sDBiv, self%cDmaxOpt, self%cDmax)`

### `f_food` [-] *Ingestion*
- DESC: food limitation function
- Source: bivalves.F90 (424)
- Formula (d⁻¹): `f_food = min(total_food_DW/self%hKfood,1.0)`
- Code: `f_food = min(total_food_DW/self%hKfood,1.0)`

### `f_SS` [-] *Ingestion*
- DESC: SS correction for ingestion
- Source: bivalves.F90 (438)
- Formula (d⁻¹): `f_SS = fSS_bivalve(sDIMW, self%cSSIMmaxOpt, self%cSSIMmax)`
- Code: `f_SS = fSS_bivalve(sDIMW, self%cSSIMmaxOpt, self%cSSIMmax)`

### `f_temp` [-] *Ingestion*
- DESC: temperature adjustment for ingestion
- Source: bivalves.F90 (428)
- Formula (d⁻¹): `f_temp = ftemp_bivalve(uTm, self%cTmin, self%cTminOpt, self%cTmaxOpt, self%cTmax)`
- Code: `f_temp = ftemp_bivalve(uTm, self%cTmin, self%cTminOpt, self%cTmaxOpt, self%cTmax)`

### `Imax` [g DW/g DW/s] *Ingestion*
- DESC: maximum potential ingestion rate
- Source: bivalves.F90 (420)
- Formula (d⁻¹): `Imax = self%kAi*weight**self%cBi`
- Code: `Imax = self%kAi*weight**self%cBi`

### `tCConsBiv` [g/m2/s] *Ingestion*
- DESC: prey C consumption per type (dim nPrey)
- Source: bivalves.F90 (447)
- Formula (d⁻¹): `tCConsBiv(i_prey) = tDConsBiv(i_prey) * rCDprey(i_prey)`
- Code: `tCConsBiv(i_prey) = tDConsBiv(i_prey) * rCDprey(i_prey)`

### `tCConsBivTot` [g/m2/s] *Ingestion*
- DESC: total prey C consumption
- Source: bivalves.F90 (457)
- Formula (d⁻¹): `tCConsBivTot = sum(tCConsBiv)`
- Code: `tCConsBivTot = sum(tCConsBiv)`

### `tDConsBiv` [g/m2/s] *Ingestion*
- DESC: prey DW consumption per type (dim nPrey)
- Source: bivalves.F90 (444)
- Formula (d⁻¹): `tDConsBiv(i_prey) = (Imax*f_food*f_temp*f_dens*f_SS)*sDBiv*self%pref(i_prey)`
- Code: `tDConsBiv(i_prey) = (Imax*f_food*f_temp*f_dens*f_SS)*sDBiv*self%pref(i_prey)`

### `tDConsBivTot` [g/m2/s] *Ingestion*
- DESC: total prey DW consumption
- Source: bivalves.F90 (454)
- Formula (d⁻¹): `tDConsBivTot = sum(tDConsBiv)`
- Code: `tDConsBivTot = sum(tDConsBiv)`

### `tNConsBiv` [g/m2/s] *Ingestion*
- DESC: prey N consumption per type (dim nPrey)
- Source: bivalves.F90 (445)
- Formula (d⁻¹): `tNConsBiv(i_prey) = tDConsBiv(i_prey) * rNDprey(i_prey)`
- Code: `tNConsBiv(i_prey) = tDConsBiv(i_prey) * rNDprey(i_prey)`

### `tNConsBivTot` [g/m2/s] *Ingestion*
- DESC: total prey N consumption
- Source: bivalves.F90 (455)
- Formula (d⁻¹): `tNConsBivTot = sum(tNConsBiv)`
- Code: `tNConsBivTot = sum(tNConsBiv)`

### `tPConsBiv` [g/m2/s] *Ingestion*
- DESC: prey P consumption per type (dim nPrey)
- Source: bivalves.F90 (446)
- Formula (d⁻¹): `tPConsBiv(i_prey) = tDConsBiv(i_prey) * rPDprey(i_prey)`
- Code: `tPConsBiv(i_prey) = tDConsBiv(i_prey) * rPDprey(i_prey)`

### `tPConsBivTot` [g/m2/s] *Ingestion*
- DESC: total prey P consumption
- Source: bivalves.F90 (456)
- Formula (d⁻¹): `tPConsBivTot = sum(tPConsBiv)`
- Code: `tPConsBivTot = sum(tPConsBiv)`

## light extinction

### `_SET_EXTINCTION_` [-] *light extinction*
- DESC: update extinction coefficient
- Source: phytoplankton.F90 (941)
- Formula (d⁻¹): `_SET_EXTINCTION_(ext)`
- Code: `_SET_EXTINCTION_(ext)`

### `ext` [1/m] *light extinction*
- DESC: light extinction coefficient from phytoplankton
- Source: phytoplankton.F90 (937)
- Formula (d⁻¹): `ext=self%cExtSp*sDW`
- Code: `ext=self%cExtSp*sDW`

## Light functions

### `aLLimShootVeg` [-] *Light functions*
- DESC: light limitation of shoots (with self-shading & surface cover)
- Source: macrophytes.F90 (421)
- Formula (d⁻¹): `fEmergVeg + fFloatVeg*(1.0 - afCovEmergVeg) + bfSubVeg*(1.0 - afCovSurfVeg)*1.0/(extc*cHeightVeg)*log((1.0 + aLPAR1Veg/uhLVeg)/(1.0 + aLPAR2Veg/uhLVeg))`
- Code: `aLLimShootVeg = self%fEmergVeg + self%fFloatVeg * (1.0 - afCovEmergVeg) + bfSubVeg * (1.0 - afCovSurfVeg) * 1.0 / (extc * self%cHeightVeg) * log((1.0 + aLPAR1Veg/uhLVeg)/(1.0 + aLPAR2Veg/uhLVeg))`

### `aLPAR1Veg` [W/m2] *Light functions*
- DESC: light at bottom of submerged canopy
- Source: macrophytes.F90 (420)
- Formula (d⁻¹): `aLPAR2Veg / exp(-extc * min(cHeightVeg, sDepthW - dz/2.0))`
- Code: `aLPAR1Veg = aLPAR2Veg / exp(-extc * min(self%cHeightVeg, sDepthW - dz/2.0_rk))`

### `aLPAR2Veg` [W/m2] *Light functions*
- DESC: light at top of submerged canopy
- Source: macrophytes.F90 (419)
- Formula (d⁻¹): `par_bott * exp(-extc * dz / 2.0)`
- Code: `aLPAR2Veg = par_bott * exp(-extc * dz / 2.0_rk)`

### `aMuTmLVeg` [1/d] *Light functions*
- DESC: max growth rate at current temp. AND light
- Source: macrophytes.F90 (425)
- Formula (d⁻¹): `ufDay * bfShootVeg * aLLimShootVeg * uFunTmProdVeg * cMuMaxVeg`
- Code: `aMuTmLVeg = ufDay * bfShootVeg * aLLimShootVeg * uFunTmProdVeg * self%cMuMaxVeg`

### `par_bott` [W/m2] *Light functions*
- DESC: par at bottom (meanpar)
- Source: macrophytes.F90 (418)
- Formula (d⁻¹): `meanpar`
- Code: `par_bott = meanpar`

### `ufDay` [-] *Light functions*
- DESC: day length fraction
- Source: macrophytes.F90 (424)
- Formula (d⁻¹): `DayLength(lat, int(Day))`
- Code: `ufDay = DayLength(lat, int(Day))`

### `uhLVeg` [W/m2] *Light functions*
- DESC: half-sat. light at current temp.
- Source: macrophytes.F90 (417)
- Formula (d⁻¹): `hLRefVeg * uFunTmProdVeg`
- Code: `uhLVeg = self%hLRefVeg * uFunTmProdVeg`

## Light limitation

### `extIM` [-] *Light limitation*
- DESC: light extinction from inorganic matter
- Source: abiotic_water.F90 (300-300)
- Formula (d⁻¹): `cExtSpIM*sDIMW`
- Code: `extIM=self%cExtSpIM*sDIMW`

### `extIM` [-] *Light limitation*
- DESC: set light extinction
- Source: abiotic_water.F90 (304-304)
- Formula (d⁻¹): `extIM`
- Code: `_SET_EXTINCTION_(extIM)`

### `extIM` [-] *Light limitation*
- DESC: set diagnostic extIM
- Source: abiotic_water.F90 (305-305)
- Formula (d⁻¹): `extIM`
- Code: `_SET_DIAGNOSTIC_(self%id_extIM,extIM)`

## Macrophyte_dependency

### `aFunVegAss_default` [-] *Macrophyte_dependency*
- DESC: no macrophyte effect (lVegOpt=false)
- Source: fish_pclake.F90 (491)
- Formula (d⁻¹): `aFunVegAss = 1.0_rk`
- Code: `aFunVegAss = 1.0_rk`

### `aFunVegAss_macro` [-] *Macrophyte_dependency*
- DESC: macrophyte-dependence of growth (lVegOpt=true)
- Source: fish_pclake.F90 (489)
- Formula (d⁻¹): `aFunVegAss = aDSubVeg /(self%hDVegGrowth + aDSubVeg + NearZero)`
- Code: `aFunVegAss = aDSubVeg / (self%hDVegGrowth + aDSubVeg + NearZero)`

### `aFunVegBent` [-] *Macrophyte_dependency*
- DESC: dependence of bentivory on macrophytes
- Source: fish_pclake.F90 (486)
- Formula (d⁻¹): `aFunVegBent = max(0.0_rk,1.0_rk - self%cRelVegBent * aCovVeg)`
- Code: `aFunVegBent = max(0.0_rk, 1.0_rk - self%cRelVegBent * aCovVeg)`

### `aFunVegZoo` [-] *Macrophyte_dependency*
- DESC: dependence of zooplanktivory on macrophytes
- Source: fish_pclake.F90 (487)
- Formula (d⁻¹): `aFunVegZoo = max(0.0_rk,1.0_rk - self%cRelVegZoo * aCovVeg)`
- Code: `aFunVegZoo = max(0.0_rk, 1.0_rk - self%cRelVegZoo * aCovVeg)`

## Migration

### `tCMigrVeg` [gC/m2/s] *Migration*
- DESC: net migration flux C
- Source: macrophytes.F90 (564)
- Formula (d⁻¹): `kMigrVeg * (cCPerDW*cDVegIn - sCVeg)`
- Code: `tCMigrVeg = self%kMigrVeg * (self%cCPerDW*self%cDVegIn - sCVeg)`

### `tDMigrVeg` [gDW/m2/s] *Migration*
- DESC: migration flux dry weight
- Source: macrophytes.F90 (561)
- Formula (d⁻¹): `kMigrVeg * (cDVegIn - sDVeg)`
- Code: `tDMigrVeg = self%kMigrVeg * (self%cDVegIn - sDVeg)`

### `tNMigrVeg` [gN/m2/s] *Migration*
- DESC: net migration flux N
- Source: macrophytes.F90 (563)
- Formula (d⁻¹): `kMigrVeg * (cNDVeg0*cDVegIn - sNVeg)`
- Code: `tNMigrVeg = self%kMigrVeg * (self%cNDVeg0*self%cDVegIn - sNVeg)`

### `tPMigrVeg` [gP/m2/s] *Migration*
- DESC: net migration flux P
- Source: macrophytes.F90 (562)
- Formula (d⁻¹): `kMigrVeg * (cPDVeg0*cDVegIn - sPVeg)`
- Code: `tPMigrVeg = self%kMigrVeg * (self%cPDVeg0*self%cDVegIn - sPVeg)`

### `tDMigrFi` [1/d] *Migration*
- DESC: current migration rate
- Source: fish_pclake.F90 (638)
- Formula (d⁻¹): `tDMigrFi = kMigrFish *(cDFiIn - sDFi)`
- Code: `tDMigrFi = self%kMigrFish * (self%cDFiIn - sDFi)`

### `tNMigrFi` [1/d] *Migration*
- DESC: change in N from migration
- Source: fish_pclake.F90 (640)
- Formula (d⁻¹): `tNMigrFi = kMigrFish *(cNDFishRef * cDFiIn - sNFi)`
- Code: `tNMigrFi = self%kMigrFish * (self%cNDFishRef * self%cDFiIn - sNFi)`

### `tPMigrFi` [1/d] *Migration*
- DESC: change in P from migration
- Source: fish_pclake.F90 (639)
- Formula (d⁻¹): `tPMigrFi = kMigrFish *(cPDFishRef * cDFiIn - sPFi)`
- Code: `tPMigrFi = self%kMigrFish * (self%cPDFishRef * self%cDFiIn - sPFi)`

## Mineralization

### `tCMin (else)` [-] *Mineralization*
- DESC: C bio-transform. of OM pool
- Source: om_pool.F90 (435)
- Formula (d⁻¹): `tCMin = self%kDMinS * uFunTmMinS * sCS`
- Code: `tCMin = self%kDMinS * uFunTmMinS * sCS`

### `tCMin (lRefrpool)` [-] *Mineralization*
- DESC: C bio-transform. of refractory OM pool
- Source: om_pool.F90 (430)
- Formula (d⁻¹): `tCMin = self%kDMinS * uFunTmMinS * sCS * afOxySed`
- Code: `tCMin = self%kDMinS * uFunTmMinS * sCS * afOxySed`

### `tDMin (else)` [-] *Mineralization*
- DESC: DW bio-transform. of OM pool
- Source: om_pool.F90 (432)
- Formula (d⁻¹): `tDMin = self%kDMinS * uFunTmMinS * sDS`
- Code: `tDMin = self%kDMinS * uFunTmMinS * sDS`

### `tDMin (lRefrpool)` [-] *Mineralization*
- DESC: DW bio-transform. of refractory OM pool
- Source: om_pool.F90 (427)
- Formula (d⁻¹): `tDMin = self%kDMinS * uFunTmMinS * sDS * afOxySed`
- Code: `tDMin = self%kDMinS * uFunTmMinS * sDS * afOxySed`

### `tNMin (else)` [-] *Mineralization*
- DESC: N bio-transform. of OM pool
- Source: om_pool.F90 (433)
- Formula (d⁻¹): `tNMin = self%kNMinS * uFunTmMinS * sNS`
- Code: `tNMin = self%kNMinS * uFunTmMinS * sNS`

### `tNMin (lRefrpool)` [-] *Mineralization*
- DESC: N bio-transform. of refractory OM pool
- Source: om_pool.F90 (428)
- Formula (d⁻¹): `tNMin = self%kNMinS * uFunTmMinS * sNS * afOxySed`
- Code: `tNMin = self%kNMinS * uFunTmMinS * sNS * afOxySed`

### `tPMin (else)` [-] *Mineralization*
- DESC: P bio-transform. of OM pool
- Source: om_pool.F90 (434)
- Formula (d⁻¹): `tPMin = self%kPMinS * uFunTmMinS * sPS`
- Code: `tPMin = self%kPMinS * uFunTmMinS * sPS`

### `tPMin (lRefrpool)` [-] *Mineralization*
- DESC: P bio-transform. of refractory OM pool
- Source: om_pool.F90 (429)
- Formula (d⁻¹): `tPMin = self%kPMinS * uFunTmMinS * sPS * afOxySed`
- Code: `tPMin = self%kPMinS * uFunTmMinS * sPS * afOxySed`

### `wCMin` [-] *Mineralization*
- DESC: particulate_OM_C mineralization
- Source: om_pool.F90 (311)
- Formula (d⁻¹): `wCMin = self%kDMinW * uFunTmMinW * sCW`
- Code: `wCMin = self%kDMinW * uFunTmMinW * sCW`

### `wDMin` [-] *Mineralization*
- DESC: decomposition (D bio-transform. in water)
- Source: om_pool.F90 (308)
- Formula (d⁻¹): `wDMin = self%kDMinW * uFunTmMinW * sDW`
- Code: `wDMin = self%kDMinW * uFunTmMinW * sDW`

### `wNMin` [-] *Mineralization*
- DESC: particulate_OM_N mineralization
- Source: om_pool.F90 (310)
- Formula (d⁻¹): `wNMin = self%kNMinW * uFunTmMinW * sNW`
- Code: `wNMin = self%kNMinW * uFunTmMinW * sNW`

### `wPMin` [-] *Mineralization*
- DESC: particulate_OM_P mineralization
- Source: om_pool.F90 (309)
- Formula (d⁻¹): `wPMin = self%kPMinW * uFunTmMinW * sPW`
- Code: `wPMin = self%kPMinW * uFunTmMinW * sPW`

## Module constants

### `cTmRef` [-] *Module constants*
- DESC: reference temperature
- Source: utility.F90 (20-20)
- Formula (d⁻¹): `20.0`
- Code: `real(rk), parameter :: cTmRef=20.0_rk`

### `deg2rad` [rad] *Module constants*
- DESC: degree to radian conversion
- Source: utility.F90 (72-72)
- Formula (d⁻¹): `Pi/180.0`
- Code: `real(rk),parameter :: deg2rad=Pi/180._rk`

### `ecliptic` [rad] *Module constants*
- DESC: obliquity of ecliptic
- Source: utility.F90 (73-73)
- Formula (d⁻¹): `23.439*deg2rad`
- Code: `real(rk),parameter :: ecliptic=23.439_rk*deg2rad`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: utility.F90 (71-71)
- Formula (d⁻¹): `3.14159265358979`
- Code: `real(rk),parameter :: Pi=3.14159265358979_rk`

### `molNmolC` [mol/mol] *Module constants*
- DESC: molar N per mol C
- Source: abiotic_water.F90 (53-53)
- Formula (d⁻¹): `1.1667`
- Code: `real(rk),parameter :: molNmolC = 1.1667_rk`

### `molO2molC` [mol/mol] *Module constants*
- DESC: molar O2 per mol C
- Source: abiotic_water.F90 (51-51)
- Formula (d⁻¹): `2.6667`
- Code: `real(rk),parameter :: molO2molC = 2.6667_rk`

### `molO2molN` [mol/mol] *Module constants*
- DESC: molar O2 per mol N
- Source: abiotic_water.F90 (52-52)
- Formula (d⁻¹): `2.2857`
- Code: `real(rk),parameter :: molO2molN = 2.2857_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero value
- Source: abiotic_water.F90 (50-50)
- Formula (d⁻¹): `1e-33`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: abiotic_water.F90 (49-49)
- Formula (d⁻¹): `86400.0`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `molNmolC` [mol/mol] *Module constants*
- DESC: molar N per mol C
- Source: abiotic_sediment.F90 (59-59)
- Formula (d⁻¹): `1.1667`
- Code: `real(rk),parameter :: molNmolC=1.1667_rk`

### `molO2molC` [mol/mol] *Module constants*
- DESC: molar O2 per mol C
- Source: abiotic_sediment.F90 (57-57)
- Formula (d⁻¹): `2.6667`
- Code: `real(rk),parameter :: molO2molC=2.6667_rk`

### `molO2molN` [mol/mol] *Module constants*
- DESC: molar O2 per mol N
- Source: abiotic_sediment.F90 (58-58)
- Formula (d⁻¹): `2.2857`
- Code: `real(rk),parameter :: molO2molN=2.2857_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero value
- Source: abiotic_sediment.F90 (56-56)
- Formula (d⁻¹): `1e-33`
- Code: `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: abiotic_sediment.F90 (55-55)
- Formula (d⁻¹): `86400.0`
- Code: `real(rk),parameter :: secs_pr_day= 86400.0_rk`

### `mgPerg` [mg/g] *Module constants*
- DESC: mg per g
- Source: om_pool.F90 (73)
- Formula (d⁻¹): `mgPerg = 1000_rk`
- Code: `mgPerg = 1000_rk`

### `molNmolC` [mol/mol] *Module constants*
- DESC: mol N per mol C
- Source: om_pool.F90 (72)
- Formula (d⁻¹): `molNmolC = 1.1667_rk`
- Code: `molNmolC = 1.1667_rk`

### `molO2molC` [mol/mol] *Module constants*
- DESC: mol O2 per mol C
- Source: om_pool.F90 (69)
- Formula (d⁻¹): `molO2molC = 2.6667_rk`
- Code: `molO2molC = 2.6667_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero to avoid division by zero
- Source: om_pool.F90 (68)
- Formula (d⁻¹): `NearZero = 0.000000000000000000000000000000001_rk`
- Code: `NearZero = 0.000000000000000000000000000000001_rk`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: om_pool.F90 (67)
- Formula (d⁻¹): `Pi=3.14159265358979_rk`
- Code: `Pi=3.14159265358979_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: om_pool.F90 (66)
- Formula (d⁻¹): `secs_pr_day=86400.0_rk`
- Code: `secs_pr_day=86400.0_rk`

### `mgPerg` [mg/g] *Module constants*
- DESC: mg per g
- Source: phytoplankton.F90 (81)
- Formula (d⁻¹): `mgPerg = 1000_rk`
- Code: `mgPerg = 1000_rk`

### `molO2molC` [mol/mol] *Module constants*
- DESC: mol O2 per mol C
- Source: phytoplankton.F90 (78)
- Formula (d⁻¹): `molO2molC = 2.6667_rk`
- Code: `molO2molC = 2.6667_rk`

### `molO2molN` [mol/mol] *Module constants*
- DESC: mol O2 per mol N
- Source: phytoplankton.F90 (80)
- Formula (d⁻¹): `molO2molN = 2.2857_rk`
- Code: `molO2molN = 2.2857_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero to avoid division by zero
- Source: phytoplankton.F90 (77)
- Formula (d⁻¹): `NearZero = 0.000000000000000000000000000000001_rk`
- Code: `NearZero = 0.000000000000000000000000000000001_rk`

### `O2PerNO3` [-] *Module constants*
- DESC: O2 per NO3
- Source: phytoplankton.F90 (79)
- Formula (d⁻¹): `O2PerNO3 = 1.5_rk`
- Code: `O2PerNO3 = 1.5_rk`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: phytoplankton.F90 (76)
- Formula (d⁻¹): `Pi=3.14159265358979_rk`
- Code: `Pi=3.14159265358979_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: phytoplankton.F90 (75)
- Formula (d⁻¹): `secs_pr_day=86400.0_rk`
- Code: `secs_pr_day=86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero value to avoid division by zero
- Source: zooplankton.F90 (54)
- Formula (d⁻¹): `0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `secs_pr_day` [-] *Module constants*
- DESC: seconds per day (86400)
- Source: zooplankton.F90 (53)
- Formula (d⁻¹): `86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero value to avoid division by zero
- Source: zoobenthos.F90 (58)
- Formula (d⁻¹): `0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`

### `secs_pr_day` [-] *Module constants*
- DESC: seconds per day (86400)
- Source: zoobenthos.F90 (57)
- Formula (d⁻¹): `86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `molO2molC` [molO2/molC] *Module constants*
- DESC: moles O2 per mol C
- Source: macrophytes.F90 (78)
- Formula (d⁻¹): `2.6667_rk`
- Code: `real(rk),parameter :: molO2molC = 2.6667_rk`

### `molO2molN` [molO2/molN] *Module constants*
- DESC: moles O2 per mol N
- Source: macrophytes.F90 (80)
- Formula (d⁻¹): `2.2857_rk`
- Code: `real(rk),parameter :: molO2molN = 2.2857_rk`

### `NearZero` [-] *Module constants*
- DESC: near zero value to avoid division by zero
- Source: macrophytes.F90 (76)
- Formula (d⁻¹): `0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `O2PerNO3` [molO2/molN] *Module constants*
- DESC: moles O2 per mol NO3
- Source: macrophytes.F90 (79)
- Formula (d⁻¹): `1.5_rk`
- Code: `real(rk),parameter :: O2PerNO3 = 1.5_rk`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: macrophytes.F90 (77)
- Formula (d⁻¹): `3.14159265358979_rk`
- Code: `real(rk),parameter :: Pi=3.14159265358979_rk`

### `secs_pr_day` [-] *Module constants*
- DESC: seconds per day (86400)
- Source: macrophytes.F90 (75)
- Formula (d⁻¹): `86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `FishZero` [gDW/m3] *Module constants*
- DESC: fish zero threshold
- Source: fish.F90 (81)
- Formula (d⁻¹): `FishZero=0.00001_rk`
- Code: `real(rk),parameter :: FishZero=0.00001_rk`

### `NearZero` [-] *Module constants*
- DESC: near-zero value to avoid division by zero
- Source: fish.F90 (79)
- Formula (d⁻¹): `NearZero = 0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: fish.F90 (80)
- Formula (d⁻¹): `Pi=3.14159265358979_rk`
- Code: `real(rk) :: Pi=3.14159265358979_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: fish.F90 (78)
- Formula (d⁻¹): `secs_pr_day=86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `FishZero` [gDW/m3] *Module constants*
- DESC: fish zero threshold
- Source: fish_pclake.F90 (69)
- Formula (d⁻¹): `FishZero=0.00001_rk`
- Code: `real(rk),parameter :: FishZero=0.00001_rk`

### `NearZero` [-] *Module constants*
- DESC: near-zero value to avoid division by zero
- Source: fish_pclake.F90 (67)
- Formula (d⁻¹): `NearZero = 0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `Pi` [-] *Module constants*
- DESC: pi
- Source: fish_pclake.F90 (68)
- Formula (d⁻¹): `Pi=3.14159265358979_rk`
- Code: `real(rk) :: Pi=3.14159265358979_rk`

### `secs_pr_day` [s/d] *Module constants*
- DESC: seconds per day
- Source: fish_pclake.F90 (66)
- Formula (d⁻¹): `secs_pr_day=86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: tiny number to avoid division by zero
- Source: sediment_exchange.F90 (52)
- Formula (d⁻¹): `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/day] *Module constants*
- DESC: seconds per day for d-1 to s-1 conversion
- Source: sediment_exchange.F90 (53)
- Formula (d⁻¹): `real(rk),parameter :: secs_pr_day= 86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day= 86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: tiny number to avoid division by zero
- Source: bot_pel_interface.F90 (32)
- Formula (d⁻¹): `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/day] *Module constants*
- DESC: seconds per day for d-1 to s-1 conversion
- Source: bot_pel_interface.F90 (31)
- Formula (d⁻¹): `real(rk),parameter :: secs_pr_day= 86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day= 86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: tiny number to avoid division by zero
- Source: resus_sed.F90 (42)
- Formula (d⁻¹): `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/day] *Module constants*
- DESC: seconds per day for d-1 to s-1 conversion
- Source: resus_sed.F90 (43)
- Formula (d⁻¹): `real(rk),parameter :: secs_pr_day= 86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day= 86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: tiny number to avoid division by zero
- Source: burial.F90 (48)
- Formula (d⁻¹): `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/day] *Module constants*
- DESC: seconds per day for d-1 to s-1 conversion
- Source: burial.F90 (49)
- Formula (d⁻¹): `real(rk),parameter :: secs_pr_day=86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

### `NearZero` [-] *Module constants*
- DESC: tiny number to avoid division by zero
- Source: bivalves.F90 (74)
- Formula (d⁻¹): `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`
- Code: `real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk`

### `secs_pr_day` [s/day] *Module constants*
- DESC: seconds per day for d-1 to s-1 conversion
- Source: bivalves.F90 (73)
- Formula (d⁻¹): `real(rk),parameter :: secs_pr_day=86400.0_rk`
- Code: `real(rk),parameter :: secs_pr_day=86400.0_rk`

## Mortality

### `wCMortZoo` [gC/m3/s] *Mortality*
- DESC: calculate mortality in C
- Source: zooplankton.F90 (348)
- Formula (d⁻¹): `rCDZoo * wDMortZoo`
- Code: `wCMortZoo = rCDZoo * wDMortZoo`

### `wDMortZoo` [gDW/m3/s] *Mortality*
- DESC: calculate mortality in DW
- Source: zooplankton.F90 (345)
- Formula (d⁻¹): `kMortZoo * sDZoo + tDEnvZoo`
- Code: `wDMortZoo = self%kMortZoo * sDZoo + tDEnvZoo`

### `wNMortZoo` [gN/m3/s] *Mortality*
- DESC: calculate mortality in N
- Source: zooplankton.F90 (346)
- Formula (d⁻¹): `rNDZoo * wDMortZoo`
- Code: `wNMortZoo = rNDZoo * wDMortZoo`

### `wPMortZoo` [gP/m3/s] *Mortality*
- DESC: calculate mortality in P
- Source: zooplankton.F90 (347)
- Formula (d⁻¹): `rPDZoo * wDMortZoo`
- Code: `wPMortZoo = rPDZoo * wDMortZoo`

### `tCMortBent` [gC/m2/s] *Mortality*
- DESC: calculate mortality in C
- Source: zoobenthos.F90 (384)
- Formula (d⁻¹): `rCDBent * tDMortBent`
- Code: `tCMortBent = rCDBent * tDMortBent`

### `tDMortBent` [gDW/m2/s] *Mortality*
- DESC: calculate mortality in DW
- Source: zoobenthos.F90 (381)
- Formula (d⁻¹): `kMortBent*sDBent + tDEnvBent + tDMortO2`
- Code: `tDMortBent = self%kMortBent*sDBent + tDEnvBent + tDMortO2`

### `tNMortBent` [gN/m2/s] *Mortality*
- DESC: calculate mortality in N
- Source: zoobenthos.F90 (383)
- Formula (d⁻¹): `rNDBent * tDMortBent`
- Code: `tNMortBent = rNDBent * tDMortBent`

### `tPMortBent` [gP/m2/s] *Mortality*
- DESC: calculate mortality in P
- Source: zoobenthos.F90 (382)
- Formula (d⁻¹): `rPDBent * tDMortBent`
- Code: `tPMortBent = rPDBent * tDMortBent`

### `bkMortVeg` [1/d] *Mortality*
- DESC: mortality rate (summer, Day<cDayWinVeg)
- Source: macrophytes.F90 (439)
- Formula (d⁻¹): `kMortVegSum`
- Code: `if (Day < self%cDayWinVeg) bkMortVeg = self%kMortVegSum`

### `bkMortVeg` [1/d] *Mortality*
- DESC: mortality rate (winter transition, cDayWinVeg <= Day < cDayWinVeg+cLengMort)
- Source: macrophytes.F90 (441)
- Formula (d⁻¹): `-log(fWinVeg)/cLengMort`
- Code: `if (Day < self%cDayWinVeg + self%cLengMort) bkMortVeg = -log(self%fWinVeg)/self%cLengMort/secs_pr_day`

### `bkMortVeg` [1/d] *Mortality*
- DESC: mortality rate (winter, Day >= cDayWinVeg+cLengMort)
- Source: macrophytes.F90 (443)
- Formula (d⁻¹): `kMortVegSum`
- Code: `if (Day >= self%cDayWinVeg + self%cLengMort) bkMortVeg = self%kMortVegSum`

### `tCMortVeg` [gC/m2/s] *Mortality*
- DESC: C mortality flux of macrophytes
- Source: macrophytes.F90 (557)
- Formula (d⁻¹): `rCDVeg * tDMortVeg`
- Code: `tCMortVeg = rCDVeg * tDMortVeg`

### `tDEnvMortVeg` [gDW/m2/s] *Mortality*
- DESC: logistic correction of mortality
- Source: macrophytes.F90 (546)
- Formula (d⁻¹): `tDEnvVeg - tDEnvProdVeg`
- Code: `tDEnvMortVeg = tDEnvVeg - tDEnvProdVeg`

### `tDMortVeg` [gDW/m2/s] *Mortality*
- DESC: total mortality flux DW (w/ correction)
- Source: macrophytes.F90 (548)
- Formula (d⁻¹): `bkMortVeg * sDVeg + tDEnvMortVeg`
- Code: `if (self%lCarrVeg) tDMortVeg = bkMortVeg * sDVeg + tDEnvMortVeg`

### `tDMortVeg` [gDW/m2/s] *Mortality*
- DESC: total mortality flux DW (w/o correction)
- Source: macrophytes.F90 (550)
- Formula (d⁻¹): `bkMortVeg * sDVeg`
- Code: `if (.NOT. self%lCarrVeg) tDMortVeg = bkMortVeg * sDVeg`

### `tNMortVeg` [gN/m2/s] *Mortality*
- DESC: N mortality flux of macrophytes
- Source: macrophytes.F90 (555)
- Formula (d⁻¹): `rNDVeg * tDMortVeg`
- Code: `tNMortVeg = rNDVeg * tDMortVeg`

### `tPMortVeg` [gP/m2/s] *Mortality*
- DESC: P mortality flux of macrophytes
- Source: macrophytes.F90 (556)
- Formula (d⁻¹): `rPDVeg * tDMortVeg`
- Code: `tPMortVeg = rPDVeg * tDMortVeg`

### `tCMortFi` [-] *Mortality*
- DESC: calculate loss of C from mortality
- Source: fish.F90 (856)
- Formula (d⁻¹): `tCMortFi = rCDFi * tDMortFi`
- Code: `tCMortFi = rCDFi * tDMortFi`

### `tDMortFi` [-] *Mortality*
- DESC: calculate current mortality rate
- Source: fish.F90 (853)
- Formula (d⁻¹): `tDMortFi = self%kMortFi * sDFi`
- Code: `tDMortFi = self%kMortFi * sDFi !+ (1.0_rk - aDSatFiTot) * tDEnvFi`

### `tNMortFi` [-] *Mortality*
- DESC: calculate loss of N from mortality
- Source: fish.F90 (855)
- Formula (d⁻¹): `tNMortFi = rNDFi * tDMortFi`
- Code: `tNMortFi = rNDFi * tDMortFi`

### `tPMortFi` [-] *Mortality*
- DESC: calculate loss of P from mortality
- Source: fish.F90 (854)
- Formula (d⁻¹): `tPMortFi = rPDFi * tDMortFi`
- Code: `tPMortFi = rPDFi * tDMortFi`

### `tDMortFi` [1/d] *Mortality*
- DESC: current mortality rate
- Source: fish_pclake.F90 (632)
- Formula (d⁻¹): `tDMortFi = kMortFi * sDFi + (1.0_rk - aDSatFiTot) * tDEnvFi`
- Code: `tDMortFi = self%kMortFi * sDFi + (1.0_rk - aDSatFiTot) * tDEnvFi`

### `tNMortFi` [1/d] *Mortality*
- DESC: loss of N from mortality
- Source: fish_pclake.F90 (634)
- Formula (d⁻¹): `tNMortFi = rNDFi * tDMortFi`
- Code: `tNMortFi = rNDFi * tDMortFi`

### `tPMortFi` [1/d] *Mortality*
- DESC: loss of P from mortality
- Source: fish_pclake.F90 (633)
- Formula (d⁻¹): `tPMortFi = rPDFi * tDMortFi`
- Code: `tPMortFi = rPDFi * tDMortFi`

### `f_DOmort` [/sec] *Mortality*
- DESC: mortality function DO
- Source: bivalves.F90 (520)
- Formula (d⁻¹): `f_DOmort = fmortality_bivalve(O2, self%kmort, self%kbdo, self%hKdo)`
- Code: `f_DOmort = fmortality_bivalve(O2, self%kmort, self%kbdo, self%hKdo)`

### `tCmortBiv` [g/m2/s] *Mortality*
- DESC: mortality POMC
- Source: bivalves.F90 (524)
- Formula (d⁻¹): `tCmortBiv = tDmortBiv * rCDBiv`
- Code: `tCmortBiv = tDmortBiv * rCDBiv`

### `tDmortBiv` [g/m2/s] *Mortality*
- DESC: POM DW produced from mortality
- Source: bivalves.F90 (521)
- Formula (d⁻¹): `tDmortBiv = sDBiv*f_DOmort`
- Code: `tDmortBiv = sDBiv*f_DOmort`

### `tNmortBiv` [g/m2/s] *Mortality*
- DESC: mortality POMN
- Source: bivalves.F90 (522)
- Formula (d⁻¹): `tNmortBiv = tDmortBiv * rNDBiv`
- Code: `tNmortBiv = tDmortBiv * rNDBiv`

### `tPmortBiv` [g/m2/s] *Mortality*
- DESC: mortality POMP
- Source: bivalves.F90 (523)
- Formula (d⁻¹): `tPmortBiv = tDmortBiv * rPDBiv`
- Code: `tPmortBiv = tDmortBiv * rPDBiv`

## Nitrification

### `aCorO2NitrW` [-] *Nitrification*
- DESC: oxygen correction for nitrification
- Source: abiotic_water.F90 (218-218)
- Formula (d⁻¹): `sO2W*sO2W / (hO2Nitr*hO2Nitr + sO2W*sO2W)`
- Code: `aCorO2NitrW = sO2W*sO2W / (self%hO2Nitr*self%hO2Nitr + sO2W*sO2W)`

### `wNNitrW` [-] *Nitrification*
- DESC: nitrification flux
- Source: abiotic_water.F90 (219-219)
- Formula (d⁻¹): `kNitrW * uFunTmNitr * aCorO2NitrW * sNH4W`
- Code: `wNNitrW = self%kNitrW * uFunTmNitr * aCorO2NitrW * sNH4W`

### `tNNitrS` [-] *Nitrification*
- DESC: calculate nitrification flux
- Source: abiotic_sediment.F90 (257-257)
- Formula (d⁻¹): `afOxySed*tNNitrS_base`
- Code: `tNNitrS=afOxySed*tNNitrS_base`

### `tNNitrS_base` [-] *Nitrification*
- DESC: potential nitrification (before oxygen)
- Source: abiotic_sediment.F90 (239-239)
- Formula (d⁻¹): `kNitrS*uFunTmNitr*sNH4S`
- Code: `tNNitrS_base=self%kNitrS*uFunTmNitr*sNH4S`

### `tO2NitrS` [-] *Nitrification*
- DESC: calculate O2 flux due to nitrification
- Source: abiotic_sediment.F90 (258-258)
- Formula (d⁻¹): `O2PerNH4S*molO2molN*tNNitrS`
- Code: `tO2NitrS=self%O2PerNH4S*molO2molN*tNNitrS`

## NP_assimilation

### `afNAssFiBen` [-] *NP_assimilation*
- DESC: N assimilation efficiency of zoobenthos
- Source: fish_pclake.F90 (585)
- Formula (d⁻¹): `afNAssFiBen = min(1.0_rk,(cNDFishRef / rNDBent) * fDAssFi)`
- Code: `afNAssFiBen = min(1.0_rk, (self%cNDFishRef / rNDBent) * self%fDAssFi)`

### `afNAssFiPisc` [-] *NP_assimilation*
- DESC: N assimilation efficiency of fish
- Source: fish_pclake.F90 (597)
- Formula (d⁻¹): `afNAssFiPisc = min(1.0_rk,(cNDFishRef / rNDPisc) * fDAssFi)`
- Code: `afNAssFiPisc = min(1.0_rk, (self%cNDFishRef / rNDPisc) * self%fDAssFi)`

### `afNAssFiZoo` [-] *NP_assimilation*
- DESC: N assimilation efficiency of zooplankton
- Source: fish_pclake.F90 (573)
- Formula (d⁻¹): `afNAssFiZoo = min(1.0_rk,(cNDFishRef / rNDZoo) * fDAssFi)`
- Code: `afNAssFiZoo = min(1.0_rk, (self%cNDFishRef / rNDZoo) * self%fDAssFi)`

### `afPAssFiBen` [-] *NP_assimilation*
- DESC: P assimilation efficiency of zoobenthos
- Source: fish_pclake.F90 (590)
- Formula (d⁻¹): `afPAssFiBen = min(1.0_rk,(cPDFishRef / rPDBent) * fDAssFi)`
- Code: `afPAssFiBen = min(1.0_rk, (self%cPDFishRef / rPDBent) * self%fDAssFi)`

### `afPAssFiPisc` [-] *NP_assimilation*
- DESC: P assimilation efficiency of fish
- Source: fish_pclake.F90 (602)
- Formula (d⁻¹): `afPAssFiPisc = min(1.0_rk,(cPDFishRef / rPDPisc) * fDAssFi)`
- Code: `afPAssFiPisc = min(1.0_rk, (self%cPDFishRef / rPDPisc) * self%fDAssFi)`

### `afPAssFiZoo` [-] *NP_assimilation*
- DESC: P assimilation efficiency of zooplankton
- Source: fish_pclake.F90 (578)
- Formula (d⁻¹): `afPAssFiZoo = min(1.0_rk,(cPDFishRef / rPDZoo) * fDAssFi)`
- Code: `afPAssFiZoo = min(1.0_rk, (self%cPDFishRef / rPDZoo) * self%fDAssFi)`

### `tDAssFiTot` [1/d] *NP_assimilation*
- DESC: total DW assimilation rate
- Source: fish_pclake.F90 (607)
- Formula (d⁻¹): `tDAssFiTot = tDAssFiZoo + tDAssFiBen + tDAssFiPisc`
- Code: `tDAssFiTot = tDAssFiZoo + tDAssFiBen + tDAssFiPisc`

### `tNAssFiBen` [1/d] *NP_assimilation*
- DESC: N assimilation rate from zoobentivory
- Source: fish_pclake.F90 (586)
- Formula (d⁻¹): `tNAssFiBen = afNAssFiBen * tNConsFiBen`
- Code: `tNAssFiBen = afNAssFiBen * tNConsFiBen`

### `tNAssFiPisc` [1/d] *NP_assimilation*
- DESC: N assimilation rate from piscivory
- Source: fish_pclake.F90 (598)
- Formula (d⁻¹): `tNAssFiPisc = afNAssFiPisc * tNConsFiPisc`
- Code: `tNAssFiPisc = afNAssFiPisc * tNConsFiPisc`

### `tNAssFiTot` [1/d] *NP_assimilation*
- DESC: total N assimilation rate
- Source: fish_pclake.F90 (609)
- Formula (d⁻¹): `tNAssFiTot = sum(tNAssFiZoo) + sum(tNAssFiBen) + sum(tNAssFiPisc)`
- Code: `tNAssFiTot = sum(tNAssFiZoo) + sum(tNAssFiBen) + sum(tNAssFiPisc)`

### `tNAssFiZoo` [1/d] *NP_assimilation*
- DESC: N assimilation rate from zooplanktivory
- Source: fish_pclake.F90 (574)
- Formula (d⁻¹): `tNAssFiZoo = afNAssFiZoo * tNConsFiZoo`
- Code: `tNAssFiZoo = afNAssFiZoo * tNConsFiZoo`

### `tPAssFiBen` [1/d] *NP_assimilation*
- DESC: P assimilation rate from zoobentivory
- Source: fish_pclake.F90 (591)
- Formula (d⁻¹): `tPAssFiBen = afPAssFiBen * tPConsFiBen`
- Code: `tPAssFiBen = afPAssFiBen * tPConsFiBen`

### `tPAssFiPisc` [1/d] *NP_assimilation*
- DESC: P assimilation rate from piscivory
- Source: fish_pclake.F90 (603)
- Formula (d⁻¹): `tPAssFiPisc = afPAssFiPisc * tPConsFiPisc`
- Code: `tPAssFiPisc = afPAssFiPisc * tPConsFiPisc`

### `tPAssFiTot` [1/d] *NP_assimilation*
- DESC: total P assimilation rate
- Source: fish_pclake.F90 (608)
- Formula (d⁻¹): `tPAssFiTot = sum(tPAssFiZoo) + sum(tPAssFiBen) + sum(tPAssFiPisc)`
- Code: `tPAssFiTot = sum(tPAssFiZoo) + sum(tPAssFiBen) + sum(tPAssFiPisc)`

### `tPAssFiZoo` [1/d] *NP_assimilation*
- DESC: P assimilation rate from zooplanktivory
- Source: fish_pclake.F90 (579)
- Formula (d⁻¹): `tPAssFiZoo = afPAssFiZoo * tPConsFiZoo`
- Code: `tPAssFiZoo = afPAssFiZoo * tPConsFiZoo`

## Nutrient limitation

### `aNLimVeg` [-] *Nutrient limitation*
- DESC: Droop N limitation for macrophytes
- Source: macrophytes.F90 (430)
- Formula (d⁻¹): `max(0.0, (1.0 - cNDVegMin/rNDVeg) * cNDVegMax / (cNDVegMax - cNDVegMin))`
- Code: `aNLimVeg = max(0.0_rk, (1.0_rk - self%cNDVegMin/rNDVeg) * self%cNDVegMax / (self%cNDVegMax - self%cNDVegMin))`

### `aNutLimVeg` [-] *Nutrient limitation*
- DESC: nutrient limitation function (min of P,N)
- Source: macrophytes.F90 (431)
- Formula (d⁻¹): `min(aPLimVeg, aNLimVeg)`
- Code: `aNutLimVeg = min(aPLimVeg, aNLimVeg)`

### `aPLimVeg` [-] *Nutrient limitation*
- DESC: Droop P limitation for macrophytes
- Source: macrophytes.F90 (429)
- Formula (d⁻¹): `max(0.0, (1.0 - cPDVegMin/rPDVeg) * cPDVegMax / (cPDVegMax - cPDVegMin))`
- Code: `aPLimVeg = max(0.0_rk, (1.0_rk - self%cPDVegMin/rPDVeg) * self%cPDVegMax / (self%cPDVegMax - self%cPDVegMin))`

## Nutrient uptake (N)

### `afNUptVegS` [-] *Nutrient uptake (N)*
- DESC: fraction N uptake from sediment (no lEmpUpt or bfRootVeg<=0)
- Source: macrophytes.F90 (465)
- Formula (d⁻¹): `0.0`
- Code: `if (.NOT. self%lEmpUpt .OR. bfRootVeg <= NearZero) afNUptVegS = 0.0_rk`

### `afNUptVegS` [-] *Nutrient uptake (N)*
- DESC: fraction N uptake from sediment (floating+submerged<=0)
- Source: macrophytes.F90 (467)
- Formula (d⁻¹): `1.0`
- Code: `if (self%fFloatVeg + bfSubVeg <= NearZero) afNUptVegS = 1.0_rk`

### `afNUptVegS` [-] *Nutrient uptake (N)*
- DESC: fraction N uptake from sediment (empirical, dual-source)
- Source: macrophytes.F90 (469)
- Formula (d⁻¹): `fSedUptVegMax/(1.0 + fSedUptVegCoef*((oNDissS+NearZero)/(oNDissW+NearZero))**fSedUptVegExp)`
- Code: `afNUptVegS = self%fSedUptVegMax / (1.0_rk + self%fSedUptVegCoef * (((oNDissS+NearZero)/(oNDissW+NearZero))**self%fSedUptVegExp))`

### `ahNUptVeg` [gN/m3] *Nutrient uptake (N)*
- DESC: half-sat. constant for N uptake
- Source: macrophytes.F90 (500)
- Formula (d⁻¹): `aVNUptMaxCrVeg/cAffNUptVeg`
- Code: `ahNUptVeg = aVNUptMaxCrVeg / self%cAffNUptVeg`

### `aVNUptMaxCrVeg` [gN/gDW/d] *Nutrient uptake (N)*
- DESC: max N uptake rate corrected for N/D ratio
- Source: macrophytes.F90 (488)
- Formula (d⁻¹): `max(0.0, cVNUptMaxVeg*uFunTmProdVeg*(cNDVegMax - rNDVeg)/(cNDVegMax - cNDVegMin))`
- Code: `aVNUptMaxCrVeg = max(0.0_rk, self%cVNUptMaxVeg * uFunTmProdVeg * (self%cNDVegMax - rNDVeg)/(self%cNDVegMax - self%cNDVegMin))`

### `aVNUptVegS` [gN/gDW/d] *Nutrient uptake (N)*
- DESC: N uptake rate of roots (non-empirical)
- Source: macrophytes.F90 (504)
- Formula (d⁻¹): `oNDissS * aVNUptMaxCrVeg/(ahNUptVeg + oNDissS)`
- Code: `if (.NOT. self%lEmpUpt) aVNUptVegS = oNDissS * aVNUptMaxCrVeg/(ahNUptVeg + oNDissS)`

### `aVNUptVegW` [gN/gDW/d] *Nutrient uptake (N)*
- DESC: N uptake rate by subm AND floating parts (non-empirical)
- Source: macrophytes.F90 (502)
- Formula (d⁻¹): `oNDissW * aVNUptMaxCrVeg/(ahNUptVeg + oNDissW)`
- Code: `if (.NOT. self%lEmpUpt) aVNUptVegW = oNDissW * aVNUptMaxCrVeg/(ahNUptVeg + oNDissW)`

### `tNUptVeg` [gN/m2/s] *Nutrient uptake (N)*
- DESC: total N uptake of water column and sediment
- Source: macrophytes.F90 (512)
- Formula (d⁻¹): `tNUptVegW + tNUptVegS`
- Code: `tNUptVeg = tNUptVegW + tNUptVegS`

### `tNUptVegS` [gN/m2/s] *Nutrient uptake (N)*
- DESC: N uptake from pore water by roots (non-empirical)
- Source: macrophytes.F90 (505)
- Formula (d⁻¹): `aVNUptVegS * aDRootVeg`
- Code: `if (.NOT. self%lEmpUpt) tNUptVegS = aVNUptVegS * aDRootVeg`

### `tNUptVegS` [gN/m2/s] *Nutrient uptake (N)*
- DESC: N uptake from pore water (empirical mode)
- Source: macrophytes.F90 (510)
- Formula (d⁻¹): `afNUptVegS * aVNUptMaxCrVeg * oNDissS/(ahNUptVeg + oNDissS) * sDVeg`
- Code: `if (self%lEmpUpt) tNUptVegS = afNUptVegS * aVNUptMaxCrVeg * oNDissS/(ahNUptVeg + oNDissS) * sDVeg`

### `tNUptVegW` [gN/m2/s] *Nutrient uptake (N)*
- DESC: N uptake from water by shoots (non-empirical)
- Source: macrophytes.F90 (503)
- Formula (d⁻¹): `aVNUptVegW * (aDSubVeg + aDFloatVeg)`
- Code: `if (.NOT. self%lEmpUpt) tNUptVegW = aVNUptVegW * (aDSubVeg + aDFloatVeg)`

### `tNUptVegW` [gN/m2/s] *Nutrient uptake (N)*
- DESC: N uptake from water (empirical mode)
- Source: macrophytes.F90 (508)
- Formula (d⁻¹): `(1.0 - afNUptVegS) * aVNUptMaxCrVeg * oNDissW/(ahNUptVeg + oNDissW) * sDVeg`
- Code: `if (self%lEmpUpt) tNUptVegW = (1.0_rk - afNUptVegS) * aVNUptMaxCrVeg * oNDissW/(ahNUptVeg + oNDissW) * sDVeg`

## Nutrient uptake (P)

### `afPUptVegS` [-] *Nutrient uptake (P)*
- DESC: fraction P uptake from sediment (no lEmpUpt or bfRootVeg<=0)
- Source: macrophytes.F90 (476)
- Formula (d⁻¹): `0.0`
- Code: `if (.NOT. self%lEmpUpt .OR. bfRootVeg <= NearZero) afPUptVegS = 0.0_rk`

### `afPUptVegS` [-] *Nutrient uptake (P)*
- DESC: fraction P uptake from sediment (floating+submerged<=0)
- Source: macrophytes.F90 (478)
- Formula (d⁻¹): `1.0`
- Code: `if (self%fFloatVeg + bfSubVeg <= NearZero) afPUptVegS = 1.0_rk`

### `afPUptVegS` [-] *Nutrient uptake (P)*
- DESC: fraction P uptake from sediment (empirical, dual-source)
- Source: macrophytes.F90 (480)
- Formula (d⁻¹): `fSedUptVegMax/(1.0 + fSedUptVegCoef*((oPO4S+NearZero)/(sPO4W+NearZero))**fSedUptVegExp)`
- Code: `afPUptVegS = self%fSedUptVegMax / (1.0_rk + self%fSedUptVegCoef * (((oPO4S+NearZero)/(sPO4W+NearZero))**self%fSedUptVegExp))`

### `ahPUptVeg` [gP/m3] *Nutrient uptake (P)*
- DESC: half-sat. constant for P uptake
- Source: macrophytes.F90 (516)
- Formula (d⁻¹): `aVPUptMaxCrVeg/cAffPUptVeg`
- Code: `ahPUptVeg = aVPUptMaxCrVeg / self%cAffPUptVeg`

### `aVPUptMaxCrVeg` [gP/gDW/d] *Nutrient uptake (P)*
- DESC: max P uptake rate corrected for P/D ratio
- Source: macrophytes.F90 (493)
- Formula (d⁻¹): `max(0.0, cVPUptMaxVeg*uFunTmProdVeg*(cPDVegMax - rPDVeg)/(cPDVegMax - cPDVegMin))`
- Code: `aVPUptMaxCrVeg = max(0.0_rk, self%cVPUptMaxVeg * uFunTmProdVeg * (self%cPDVegMax - rPDVeg)/(self%cPDVegMax - self%cPDVegMin))`

### `aVPUptVegS` [gP/gDW/d] *Nutrient uptake (P)*
- DESC: P uptake rate by roots (non-empirical)
- Source: macrophytes.F90 (519)
- Formula (d⁻¹): `oPO4S * aVPUptMaxCrVeg/(ahPUptVeg + oPO4S + NearZero)`
- Code: `if (.NOT. self%lEmpUpt) aVPUptVegS = oPO4S * aVPUptMaxCrVeg/(ahPUptVeg + oPO4S + NearZero)`

### `aVPUptVegW` [gP/gDW/d] *Nutrient uptake (P)*
- DESC: P uptake rate by subm AND floating parts (non-empirical)
- Source: macrophytes.F90 (518)
- Formula (d⁻¹): `sPO4W * aVPUptMaxCrVeg/(ahPUptVeg + sPO4W)`
- Code: `if (.NOT. self%lEmpUpt) aVPUptVegW = sPO4W * aVPUptMaxCrVeg/(ahPUptVeg + sPO4W)`

### `tPUptVeg` [gP/m2/s] *Nutrient uptake (P)*
- DESC: total P uptake macrophytes
- Source: macrophytes.F90 (528)
- Formula (d⁻¹): `tPUptVegW + tPUptVegS`
- Code: `tPUptVeg = tPUptVegW + tPUptVegS`

### `tPUptVegS` [gP/m2/s] *Nutrient uptake (P)*
- DESC: P uptake from pore water by root fraction (non-empirical)
- Source: macrophytes.F90 (521)
- Formula (d⁻¹): `aVPUptVegS * aDRootVeg`
- Code: `if (.NOT. self%lEmpUpt) tPUptVegS = aVPUptVegS * aDRootVeg`

### `tPUptVegS` [gP/m2/s] *Nutrient uptake (P)*
- DESC: P uptake from pore water (empirical mode)
- Source: macrophytes.F90 (526)
- Formula (d⁻¹): `afPUptVegS * aVPUptMaxCrVeg * oPO4S/(ahPUptVeg + oPO4S) * sDVeg`
- Code: `if (self%lEmpUpt) tPUptVegS = afPUptVegS * aVPUptMaxCrVeg * oPO4S/(ahPUptVeg + oPO4S) * sDVeg`

### `tPUptVegW` [gP/m2/s] *Nutrient uptake (P)*
- DESC: P uptake from water (non-empirical)
- Source: macrophytes.F90 (520)
- Formula (d⁻¹): `aVPUptVegW * (aDSubVeg + aDFloatVeg)`
- Code: `if (.NOT. self%lEmpUpt) tPUptVegW = aVPUptVegW * (aDSubVeg + aDFloatVeg)`

### `tPUptVegW` [gP/m2/s] *Nutrient uptake (P)*
- DESC: P uptake from water (empirical mode)
- Source: macrophytes.F90 (525)
- Formula (d⁻¹): `(1.0 - afPUptVegS) * aVPUptMaxCrVeg * sPO4W/(ahPUptVeg + sPO4W) * sDVeg`
- Code: `if (self%lEmpUpt) tPUptVegW = (1.0 - afPUptVegS) * aVPUptMaxCrVeg * sPO4W/(ahPUptVeg + sPO4W) * sDVeg`

## O2 consumption

### `aCorO2BOD` [-] *O2 consumption*
- DESC: correction_of_O2_demand_in_water_at_low_oxygen_conc.
- Source: om_pool.F90 (315)
- Formula (d⁻¹): `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`
- Code: `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`

### `wO2Min` [-] *O2 consumption*
- DESC: O2 consumption for biotransformation
- Source: om_pool.F90 (316)
- Formula (d⁻¹): `wO2Min = molO2molC * rCDW * aCorO2BOD * wDMin`
- Code: `wO2Min = molO2molC * rCDW * aCorO2BOD * wDMin`

## O2 processes

### `a` [-] *O2 processes*
- DESC: O2 solubility coefficient a
- Source: utility.F90 (95-95)
- Formula (d⁻¹): `-173.4292 + 249.6339*100/Tabs + 143.3483*log(Tabs/100)`
- Code: `a = -173.4292_rk + 249.6339_rk * 100 / Tabs + 143.3483_rk * log(Tabs/100)`

### `b` [-] *O2 processes*
- DESC: O2 solubility coefficient b
- Source: utility.F90 (96-96)
- Formula (d⁻¹): `21.8492*Tabs/100`
- Code: `b = 21.8492_rk * Tabs / 100`

### `c` [-] *O2 processes*
- DESC: O2 salinity correction
- Source: utility.F90 (97-97)
- Formula (d⁻¹): `salt * (-0.033096 + 0.014259*Tabs/100.0 - 0.0017*(Tabs/100)**2)`
- Code: `c = salt * (-0.033096_rk + 0.014259_rk * Tabs / 100.0_rk - 0.0017_rk * (Tabs / 100)**2)`

### `sol_coeff` [-] *O2 processes*
- DESC: O2 solubility coefficient
- Source: utility.F90 (98-98)
- Formula (d⁻¹): `a - b + c`
- Code: `sol_coeff = a - b + c`

### `Tabs` [K] *O2 processes*
- DESC: absolute temperature
- Source: utility.F90 (94-94)
- Formula (d⁻¹): `temp + 273.15`
- Code: `Tabs = temp + 273.15_rk`

### `uFunO2Sat` [g/m3] *O2 processes*
- DESC: oxygen saturation concentration
- Source: utility.F90 (86-101)
- Formula (d⁻¹): `1.42763 * exp(sol_coeff)`
- Code: `uFunO2Sat = 1.42763 * exp(sol_coeff)`

### `aCorO2BOD` [-] *O2 processes*
- DESC: correction_of_O2_demand_in_water_at_low_oxygen_conc.
- Source: abiotic_water.F90 (203-203)
- Formula (d⁻¹): `sO2W / (hO2BOD + sO2W)`
- Code: `aCorO2BOD = sO2W / (self%hO2BOD + sO2W)`

### `cO2Sat` [-] *O2 processes*
- DESC: O2 saturation in water
- Source: abiotic_water.F90 (229-229)
- Formula (d⁻¹): `uFunO2Sat(salt,uTm)`
- Code: `cO2Sat = uFunO2Sat(salt,uTm)`

### `pO2Sat` [pct] *O2 processes*
- DESC: O2 pct saturation in water
- Source: abiotic_water.F90 (230-230)
- Formula (d⁻¹): `sO2W / cO2Sat * 100`
- Code: `pO2Sat = sO2W / cO2Sat * 100`

### `wO2NitrW` [-] *O2 processes*
- DESC: O2 flux due to nitrification
- Source: abiotic_water.F90 (228-228)
- Formula (d⁻¹): `O2PerNH4W * molO2molN * wNNitrW`
- Code: `wO2NitrW = self%O2PerNH4W * molO2molN * wNNitrW`

### `aDepthDif` [-] *O2 processes*
- DESC: average diffusion distance
- Source: abiotic_sediment.F90 (230-230)
- Formula (d⁻¹): `max(NearZero, fDepthDifS*cDepthS)`
- Code: `aDepthDif= max(NearZero, self%fDepthDifS*self%cDepthS)`

### `aDepthOxySed` [-] *O2 processes*
- DESC: calculate oxygen penetration depth
- Source: abiotic_sediment.F90 (245-245)
- Formula (d⁻¹): `((2.0 * sO2W * akO2DifCor / tTotSOD) )** (0.5)`
- Code: `aDepthOxySed=(((2.0_rk * sO2W * akO2DifCor / tTotSOD) )** (0.5_rk))`

### `afOxySed` [-] *O2 processes*
- DESC: calculate fraction aerobic sediment
- Source: abiotic_sediment.F90 (246-246)
- Formula (d⁻¹): `min(1.0, max(0.0, aDepthOxySed/cDepthS))`
- Code: `afOxySed=min(1.0, max(0.0_rk, aDepthOxySed/self%cDepthS))`

### `akO2DifCor` [-] *O2 processes*
- DESC: corrected O2 diffusion coefficient
- Source: abiotic_sediment.F90 (231-231)
- Formula (d⁻¹): `kO2Dif*uFunTmDifO2*cTurbDifO2*bPorCorS`
- Code: `akO2DifCor=self%kO2Dif*uFunTmDifO2*self%cTurbDifO2*self%bPorCorS`

### `tO2Dif` [-] *O2 processes*
- DESC: O2 diffusion (water to sediment)
- Source: abiotic_sediment.F90 (232-232)
- Formula (d⁻¹): `akO2DifCor*sO2W/aDepthDif`
- Code: `tO2Dif= akO2DifCor*sO2W/aDepthDif`

### `tO2MinTOMS` [-] *O2 processes*
- DESC: calculate total oxygen consumption by TOM
- Source: abiotic_sediment.F90 (247-247)
- Formula (d⁻¹): `molO2molC*afOxySed*(sum(tCTrans_POM) + sum(tCTrans_DOM))`
- Code: `tO2MinTOMS=molO2molC*afOxySed*(sum(tCTrans_POM) + sum(tCTrans_DOM))`

### `tTotSOD` [-] *O2 processes*
- DESC: calculate total sediment oxygen demand
- Source: abiotic_sediment.F90 (243-244)
- Formula (d⁻¹): `max(NearZero, (molO2molC*(sum(tCTrans_POM) + sum(tCTrans_DOM)) + O2PerNH4S*molO2molN*tNNitrS_base) / cDepthS)`
- Code: `tTotSOD=max(NearZero, (molO2molC*(sum(tCTrans_POM) + sum(tCTrans_DOM)) + self%O2PerNH4S*molO2molN*tNNitrS_base) / self%cDepthS)`

## O2 stress

### `fO2` [-] *O2 stress*
- DESC: calc. oxygen stress correction of zoobenthos vital rates
- Source: zoobenthos.F90 (318)
- Formula (d⁻¹): `max(0.0_rk, pO2Sat**4 / max(NearZero,(hO2stress**4 + pO2Sat**4)))`
- Code: `fO2 = max(0.0_rk, pO2Sat**4 / max(NearZero,(self%hO2stress**4 + pO2Sat**4)))`

### `tDMortO2` [gDW/m2/s] *O2 stress*
- DESC: calculate add. mortality due to O2 stress
- Source: zoobenthos.F90 (380)
- Formula (d⁻¹): `kMortO2 *sDBent * (1 - fO2) * uFunTmBent`
- Code: `tDMortO2 = self%kMortO2 *sDBent * (1 - fO2) * uFunTmBent`

## ODE_updates

### `BioTurb_set` [1/d] *ODE_updates*
- DESC: set bioturbation diagnostic
- Source: fish_pclake.F90 (746)
- Formula (d⁻¹): `_SET_DIAGNOSTIC_(self%id_BioTurb,BioTurb)`
- Code: `_SET_DIAGNOSTIC_(self%id_BioTurb, BioTurb)`

### `DDOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update DOM DW water column ODE
- Source: fish_pclake.F90 (774)
- Formula (d⁻¹): `_SET_ODE_(self%id_DDOMpoolW,tDFiDOMW)`
- Code: `_SET_ODE_(self%id_DDOMpoolW, tDFiDOMW)`

### `DFoodPisc_ODE` [1/d] *ODE_updates*
- DESC: update fish prey DW ODEs
- Source: fish_pclake.F90 (752)
- Formula (d⁻¹): `_SET_ODE_(self%id_DFoodPisc(i_prey),-tDConsFiPisc(i_prey))`
- Code: `_SET_ODE_(self%id_DFoodPisc(i_prey), -tDConsFiPisc(i_prey))`

### `DFoodZoo_ODE` [1/d] *ODE_updates*
- DESC: update zooplankton prey DW ODEs
- Source: fish_pclake.F90 (731)
- Formula (d⁻¹): `_SET_ODE_(self%id_DFoodZoo(i_prey),-tDConsFiZoo(i_prey))`
- Code: `_SET_ODE_(self%id_DFoodZoo(i_prey), -tDConsFiZoo(i_prey))`

### `DPOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update POM DW water column ODE
- Source: fish_pclake.F90 (773)
- Formula (d⁻¹): `_SET_ODE_(self%id_DPOMpoolW,tDFiPOMW)`
- Code: `_SET_ODE_(self%id_DPOMpoolW, tDFiPOMW)`

### `FiAd_D_ODE` [1/d] *ODE_updates*
- DESC: update older stage DW ODE (aging)
- Source: fish_pclake.F90 (766)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiAd_D,tDAgeFish)`
- Code: `_SET_ODE_(self%id_FiAd_D, tDAgeFish)`

### `FiAd_N_ODE` [1/d] *ODE_updates*
- DESC: update older stage N ODE (aging)
- Source: fish_pclake.F90 (767)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiAd_N,tNAgeFish)`
- Code: `_SET_ODE_(self%id_FiAd_N, tNAgeFish)`

### `FiAd_P_ODE` [1/d] *ODE_updates*
- DESC: update older stage P ODE (aging)
- Source: fish_pclake.F90 (768)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiAd_P,tPAgeFish)`
- Code: `_SET_ODE_(self%id_FiAd_P, tPAgeFish)`

### `FiJu_D_ODE` [1/d] *ODE_updates*
- DESC: update juvenile stage DW ODE (reproduction)
- Source: fish_pclake.F90 (761)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiJu_D,tDReprFish)`
- Code: `_SET_ODE_(self%id_FiJu_D, tDReprFish)`

### `FiJu_N_ODE` [1/d] *ODE_updates*
- DESC: update juvenile stage N ODE (reproduction)
- Source: fish_pclake.F90 (762)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiJu_N,tNReprFish)`
- Code: `_SET_ODE_(self%id_FiJu_N, tNReprFish)`

### `FiJu_P_ODE` [1/d] *ODE_updates*
- DESC: update juvenile stage P ODE (reproduction)
- Source: fish_pclake.F90 (763)
- Formula (d⁻¹): `_SET_ODE_(self%id_FiJu_P,tPReprFish)`
- Code: `_SET_ODE_(self%id_FiJu_P, tPReprFish)`

### `NDOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update dissolved organic N water column ODE
- Source: fish_pclake.F90 (778)
- Formula (d⁻¹): `_SET_ODE_(self%id_NDOMpoolW,tNFiDOMW)`
- Code: `_SET_ODE_(self%id_NDOMpoolW, tNFiDOMW)`

### `NFoodPisc_ODE` [1/d] *ODE_updates*
- DESC: update fish prey N ODEs
- Source: fish_pclake.F90 (753)
- Formula (d⁻¹): `_SET_ODE_(self%id_NFoodPisc(i_prey),-tNConsFiPisc(i_prey))`
- Code: `_SET_ODE_(self%id_NFoodPisc(i_prey), -tNConsFiPisc(i_prey))`

### `NFoodZoo_ODE` [1/d] *ODE_updates*
- DESC: update zooplankton prey N ODEs
- Source: fish_pclake.F90 (732)
- Formula (d⁻¹): `_SET_ODE_(self%id_NFoodZoo(i_prey),-tNConsFiZoo(i_prey))`
- Code: `_SET_ODE_(self%id_NFoodZoo(i_prey), -tNConsFiZoo(i_prey))`

### `NH4poolW_ODE` [1/d] *ODE_updates*
- DESC: update dissolved inorganic N water column ODE
- Source: fish_pclake.F90 (776)
- Formula (d⁻¹): `_SET_ODE_(self%id_NH4poolW,tNFiNH4W)`
- Code: `_SET_ODE_(self%id_NH4poolW, tNFiNH4W)`

### `NPOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update particulate organic N water column ODE
- Source: fish_pclake.F90 (777)
- Formula (d⁻¹): `_SET_ODE_(self%id_NPOMpoolW,tNFiPOMW)`
- Code: `_SET_ODE_(self%id_NPOMpoolW, tNFiPOMW)`

### `PDOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update dissolved organic P water column ODE
- Source: fish_pclake.F90 (782)
- Formula (d⁻¹): `_SET_ODE_(self%id_PDOMpoolW,tPFiDOMW)`
- Code: `_SET_ODE_(self%id_PDOMpoolW, tPFiDOMW)`

### `PFoodPisc_ODE` [1/d] *ODE_updates*
- DESC: update fish prey P ODEs
- Source: fish_pclake.F90 (754)
- Formula (d⁻¹): `_SET_ODE_(self%id_PFoodPisc(i_prey),-tPConsFiPisc(i_prey))`
- Code: `_SET_ODE_(self%id_PFoodPisc(i_prey), -tPConsFiPisc(i_prey))`

### `PFoodZoo_ODE` [1/d] *ODE_updates*
- DESC: update zooplankton prey P ODEs
- Source: fish_pclake.F90 (733)
- Formula (d⁻¹): `_SET_ODE_(self%id_PFoodZoo(i_prey),-tPConsFiZoo(i_prey))`
- Code: `_SET_ODE_(self%id_PFoodZoo(i_prey), -tPConsFiZoo(i_prey))`

### `PO4poolW_ODE` [1/d] *ODE_updates*
- DESC: update dissolved inorganic P water column ODE
- Source: fish_pclake.F90 (780)
- Formula (d⁻¹): `_SET_ODE_(self%id_PO4poolW,tPFiPO4W)`
- Code: `_SET_ODE_(self%id_PO4poolW, tPFiPO4W)`

### `PPOMpoolW_ODE` [1/d] *ODE_updates*
- DESC: update particulate organic P water column ODE
- Source: fish_pclake.F90 (781)
- Formula (d⁻¹): `_SET_ODE_(self%id_PPOMpoolW,tPFiPOMW)`
- Code: `_SET_ODE_(self%id_PPOMpoolW, tPFiPOMW)`

### `sDFi_ODE` [1/d] *ODE_updates*
- DESC: set fish DW ODE
- Source: fish_pclake.F90 (721)
- Formula (d⁻¹): `_SET_ODE_(self%id_sDFi,tDFi)`
- Code: `_SET_ODE_(self%id_sDFi, tDFi)`

### `sNFi_ODE` [1/d] *ODE_updates*
- DESC: set fish N ODE
- Source: fish_pclake.F90 (723)
- Formula (d⁻¹): `_SET_ODE_(self%id_sNFi,tNFi)`
- Code: `_SET_ODE_(self%id_sNFi, tNFi)`

### `sPFi_ODE` [1/d] *ODE_updates*
- DESC: set fish P ODE
- Source: fish_pclake.F90 (722)
- Formula (d⁻¹): `_SET_ODE_(self%id_sPFi,tPFi)`
- Code: `_SET_ODE_(self%id_sPFi, tPFi)`

### `tDConsFiBen_out` [1/d] *ODE_updates*
- DESC: update bentivorous DW consumption diagnostic
- Source: fish_pclake.F90 (741)
- Formula (d⁻¹): `_SET_DIAGNOSTIC_(self%id_tDConsFiBen_out(i_prey),-tDConsFiBen(i_prey))`
- Code: `_SET_DIAGNOSTIC_(self%id_tDConsFiBen_out(i_prey), -tDConsFiBen(i_prey))`

### `tNConsFiBen_out` [1/d] *ODE_updates*
- DESC: update bentivorous N consumption diagnostic
- Source: fish_pclake.F90 (742)
- Formula (d⁻¹): `_SET_DIAGNOSTIC_(self%id_tNConsFiBen_out(i_prey),-tNConsFiBen(i_prey))`
- Code: `_SET_DIAGNOSTIC_(self%id_tNConsFiBen_out(i_prey), -tNConsFiBen(i_prey))`

### `tPConsFiBen_out` [1/d] *ODE_updates*
- DESC: update bentivorous P consumption diagnostic
- Source: fish_pclake.F90 (743)
- Formula (d⁻¹): `_SET_DIAGNOSTIC_(self%id_tPConsFiBen_out(i_prey),-tPConsFiBen(i_prey))`
- Code: `_SET_DIAGNOSTIC_(self%id_tPConsFiBen_out(i_prey), -tPConsFiBen(i_prey))`

## Optimal Diet Breadth (ODB)

### `aFeedLvlPrey_final` [-] *Optimal Diet Breadth (ODB)*
- DESC: calculate final feeding level ignoring not included prey
- Source: fish.F90 (1335-1336)
- Formula (d⁻¹): `aFeedLvlPrey = aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in/(aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPrey = aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in/ (aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in + uFunTmFish*kDConsMax)`

### `aFeedLvlPrey_iter` [-] *Optimal Diet Breadth (ODB)*
- DESC: calculate feeding level using included prey (iteration)
- Source: fish.F90 (1325-1326)
- Formula (d⁻¹): `aFeedLvlPrey = aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in/(aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in + uFunTmFish*kDConsMax)`
- Code: `aFeedLvlPrey = aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in/ (aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in + uFunTmFish*kDConsMax)`

### `cease` [-] *Optimal Diet Breadth (ODB)*
- DESC: stop iterating if new total consumption is lower than previous
- Source: fish.F90 (1329-1330)
- Formula (d⁻¹): `cease = .true. [if tDConsFiPreyPotTot < tDConsFiPreyPot_last]`
- Code: `if (i > 1 .and. tDConsFiPreyPotTot < tDConsFiPreyPot_last) then cease = .true.`

### `maxid` [-] *Optimal Diet Breadth (ODB)*
- DESC: find most profitable of remaining prey
- Source: fish.F90 (1322)
- Formula (d⁻¹): `maxid = maxloc(PreyProf,DIM=1,MASK=.not. mask)`
- Code: `maxid = maxloc(PreyProf,DIM=1,MASK=.not. mask)`

### `PreyProf` [-] *Optimal Diet Breadth (ODB)*
- DESC: calculate prey profitabilities (1/gut occupation)
- Source: fish.F90 (1310)
- Formula (d⁻¹): `PreyProf = 1._rk/fGutOccPrey`
- Code: `PreyProf = 1._rk/fGutOccPrey`

### `tDConsFiPreyPot_final` [-] *Optimal Diet Breadth (ODB)*
- DESC: calculate final consumption of all prey ignoring not included prey
- Source: fish.F90 (1337)
- Formula (d⁻¹): `tDConsFiPreyPot = fFeed_in*aFunVegPrey_in*incl*cClearPrey*sDPrey*(1._rk-aFeedLvlPrey)`
- Code: `tDConsFiPreyPot = fFeed_in*aFunVegPrey_in*incl*cClearPrey*sDPrey*(1._rk-aFeedLvlPrey)`

### `tDConsFiPreyPot_temp` [-] *Optimal Diet Breadth (ODB)*
- DESC: calculate consumption of included prey (iteration)
- Source: fish.F90 (1327)
- Formula (d⁻¹): `tDConsFiPreyPot_temp=fFeed_in*aFunVegPrey_in*cClearPrey*sDPrey*incl*(1._rk-aFeedLvlPrey)`
- Code: `tDConsFiPreyPot_temp=fFeed_in*aFunVegPrey_in*cClearPrey*sDPrey*incl*(1._rk-aFeedLvlPrey)`

### `tDConsFiPreyPotTot` [-] *Optimal Diet Breadth (ODB)*
- DESC: sum up total consumption from included prey
- Source: fish.F90 (1328)
- Formula (d⁻¹): `tDConsFiPreyPotTot = sum(tDConsFiPreyPot_temp)`
- Code: `tDConsFiPreyPotTot = sum(tDConsFiPreyPot_temp)`

## Optimal Foraging Arena

### `fFC` [-] *Optimal Foraging Arena*
- DESC: ensure fFC is non-zero
- Source: fish.F90 (695)
- Formula (d⁻¹): `fFC = max(NearZero,self%fFC)`
- Code: `fFC = max(NearZero,self%fFC)`

### `fFeed` [-] *Optimal Foraging Arena*
- DESC: optimal behavior off: full feeding
- Source: fish.F90 (683)
- Formula (d⁻¹): `fFeed = 1.0_rk`
- Code: `fFeed = 1.0_rk`

### `fFeed` [-] *Optimal Foraging Arena*
- DESC: starving: no feeding
- Source: fish.F90 (686)
- Formula (d⁻¹): `fFeed = 0.0_rk`
- Code: `fFeed = 0.0_rk`

### `fFeed` [-] *Optimal Foraging Arena*
- DESC: starving: feeding gains higher than costs
- Source: fish.F90 (688)
- Formula (d⁻¹): `fFeed = 1.0_rk`
- Code: `fFeed = 1.0_rk`

### `fFeed` [-] *Optimal Foraging Arena*
- DESC: calculate fFeed (total fish feeding efficiency)
- Source: fish.F90 (707)
- Formula (d⁻¹): `fFeed = 1.0_rk-PStar_now*self%fFC`
- Code: `fFeed = 1.0_rk-PStar_now*self%fFC`

### `fGOT` [-] *Optimal Foraging Arena*
- DESC: calculate overall fGutOcc value weighted by relative consumption
- Source: fish.F90 (696-697)
- Formula (d⁻¹): `fGOT = fFishPlan*sum(relConsPlan*self%fGutOccPlan) + fFishBent*sum(relConsBent*self%fGutOccBent) + fFishPisc*sum(relConsPisc*self%fGutOccPisc)`
- Code: `fGOT = fFishPlan*sum(relConsPlan*self%fGutOccPlan) + fFishBent*sum(relConsBent*self%fGutOccBent) + fFishPisc*sum(relConsPisc*self%fGutOccPisc)`

### `Fmax` [-] *Optimal Foraging Arena*
- DESC: temperature-corrected max consumption
- Source: fish.F90 (701)
- Formula (d⁻¹): `Fmax = kDConsMax*uFunTmFish`
- Code: `Fmax = kDConsMax*uFunTmFish`

### `M` [-] *Optimal Foraging Arena*
- DESC: temperature-corrected metabolism
- Source: fish.F90 (700)
- Formula (d⁻¹): `M = self%kDRespFi*uFunTmFish`
- Code: `M = self%kDRespFi*uFunTmFish`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: optimal behavior off: PStar near zero
- Source: fish.F90 (682)
- Formula (d⁻¹): `PStar = NearZero`
- Code: `PStar = NearZero`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: starving: cost of feeding higher than gain
- Source: fish.F90 (685)
- Formula (d⁻¹): `PStar = 1.0_rk`
- Code: `PStar = 1.0_rk`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: risk reduction does not reduce feeding
- Source: fish.F90 (690)
- Formula (d⁻¹): `PStar = 1.0_rk`
- Code: `PStar = 1.0_rk`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: risk reduction not possible
- Source: fish.F90 (692)
- Formula (d⁻¹): `PStar = NearZero`
- Code: `PStar = NearZero`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: analytical solution of PStar (quadratic equation root) - most complex formula
- Source: fish.F90 (702-705)
- Formula (d⁻¹): `PStar = (fFC*fGOT*Fmax*self%fPV*R**2._rk*vPred + M*fFC*fGOT*R*(Fmax + fGOT*R)*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)) - sqrt(max(0.0_rk,fFC**2._rk*fGOT*Fmax**2._rk*R**2._rk*(Fmax*self%fPV*R*vPred*(-self%fPV*vPred + fFC*(self%kMortFi + vPred)) + M*(-self%fPV*(Fmax + fGOT*R)*vPred + fFC*fGOT*R*(self%kMortFi + vPred))*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)))))) /(fFC**2._rk*fGOT*R**2._rk*(Fmax*self%fPV*vPred + M*fGOT*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi))))`
- Code: `PStar = (fFC*fGOT*Fmax*self%fPV*R**2._rk*vPred + M*fFC*fGOT*R*(Fmax + fGOT*R)*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)) & - sqrt(max(0.0_rk,fFC**2._rk*fGOT*Fmax**2._rk*R**2._rk*(Fmax*self%fPV*R*vPred*(-self%fPV*vPred + fFC*(self%kMortFi + vPred)) & + M*(-self%fPV*(Fmax + fGOT*R)*vPred + fFC*fGOT*R*(self%kMortFi + vPred))*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)))))) & /(fFC**2._rk*fGOT*R**2._rk*(Fmax*self%fPV*vPred + M*fGOT*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi))))`

### `PStar` [-] *Optimal Foraging Arena*
- DESC: constrain PStar to values between zero and one
- Source: fish.F90 (706)
- Formula (d⁻¹): `PStar = max(NearZero,min(1.0_rk,PStar))`
- Code: `PStar = max(NearZero,min(1.0_rk,PStar))`

### `PStar_now` [-] *Optimal Foraging Arena*
- DESC: back-calculate current feeding behavior
- Source: fish.F90 (680)
- Formula (d⁻¹): `PStar_now = (1._rk-fVul)/self%fPV`
- Code: `PStar_now = (1._rk-fVul)/self%fPV`

### `R` [-] *Optimal Foraging Arena*
- DESC: calculate overall food availability
- Source: fish.F90 (698-699)
- Formula (d⁻¹): `R = fFishPlan*aFunVegPlan*sum(inclPlan*sDPlan*self%cClearPlan) + fFishBent*aFunVegBent*sum(inclBent*sDBent*self%cClearBent) + fFishPisc*sum(inclPisc*sDPisc*self%cClearPisc)`
- Code: `R = fFishPlan*aFunVegPlan*sum(inclPlan*sDPlan*self%cClearPlan) + fFishBent*aFunVegBent*sum(inclBent*sDBent*self%cClearBent) + fFishPisc*sum(inclPisc*sDPisc*self%cClearPisc)`

### `tfVul` [-] *Optimal Foraging Arena*
- DESC: calculate rate of change in predation vulnerability
- Source: fish.F90 (709)
- Formula (d⁻¹): `tfVul = (PStar_now-PStar)*self%fPV`
- Code: `tfVul = (PStar_now-PStar)*self%fPV*(1._rk/secs_pr_day)`

## P adsorption

### `aKPAdsW` [-] *P adsorption*
- DESC: P adsorption affinity corrected for redox conditions
- Source: abiotic_water.F90 (211-211)
- Formula (d⁻¹): `(1.0 - fRedMaxW * (1.0-aCorO2BOD)) * cKPAdsOxW`
- Code: `aKPAdsW = (1.0_rk - self%fRedMaxW * (1.0_rk-aCorO2BOD)) * self%cKPAdsOxW`

### `aPAdsMaxW` [-] *P adsorption*
- DESC: max. P adsorption per g inorg. matter in water
- Source: abiotic_water.F90 (210-210)
- Formula (d⁻¹): `cRelPAdsDWW+aCorO2BOD*cRelPAdsFeW*fFeDIMW+cRelPAdsAlW*fAlDIMW`
- Code: `aPAdsMaxW = self%cRelPAdsDWW+aCorO2BOD*self%cRelPAdsFeW*self%fFeDIMW+self%cRelPAdsAlW*self%fAlDIMW`

### `aPEqIMW` [-] *P adsorption*
- DESC: equilibrium conc.
- Source: abiotic_water.F90 (213-213)
- Formula (d⁻¹): `aPIsoAdsW * sDIMW`
- Code: `aPEqIMW = aPIsoAdsW * sDIMW`

### `aPIsoAdsW` [-] *P adsorption*
- DESC: P adsorption isotherm onto inorg. matter in water
- Source: abiotic_water.F90 (212-212)
- Formula (d⁻¹): `aPAdsMaxW * aKPAdsW * sPO4W / (1.0 + aKPAdsW * sPO4W)`
- Code: `aPIsoAdsW = aPAdsMaxW * aKPAdsW * sPO4W / (1.0_rk + aKPAdsW * sPO4W)`

### `wPSorpIMW` [-] *P adsorption*
- DESC: adsorption flux in water
- Source: abiotic_water.F90 (214-214)
- Formula (d⁻¹): `kPSorpW * (aPEqIMW - sPAIMW)`
- Code: `wPSorpIMW = self%kPSorpW * (aPEqIMW - sPAIMW)`

### `aKPAdsS` [-] *P adsorption*
- DESC: calculate P adsorption affinity corrected for redox conditions
- Source: abiotic_sediment.F90 (263-263)
- Formula (d⁻¹): `(1.0-fRedMaxS*(1.0-afOxySed))*cKPAdsOxS`
- Code: `aKPAdsS=(1.0_rk-self%fRedMaxS*(1.0_rk-afOxySed))*self%cKPAdsOxS`

### `aPAdsMaxS` [-] *P adsorption*
- DESC: calculate max. P adsorption per g of inorg. matter
- Source: abiotic_sediment.F90 (262-262)
- Formula (d⁻¹): `cRelPAdsDWS+afOxySed*cRelPAdsFeS*fFeDIM+cRelPAdsAlS*fAlDIMS`
- Code: `aPAdsMaxS =self%cRelPAdsDWS+afOxySed*self%cRelPAdsFeS*self%fFeDIM+self%cRelPAdsAlS*self%fAlDIMS`

### `aPEqIMS` [-] *P adsorption*
- DESC: calculate equilibrium amount
- Source: abiotic_sediment.F90 (265-265)
- Formula (d⁻¹): `aPIsoAdsS * sDIMS`
- Code: `aPEqIMS = aPIsoAdsS * sDIMS`

### `aPIsoAdsS` [-] *P adsorption*
- DESC: calculate P adsorption isotherm onto inorg. matter in sediment
- Source: abiotic_sediment.F90 (264-264)
- Formula (d⁻¹): `aPAdsMaxS*aKPAdsS*oPO4S/(1.0+aKPAdsS*oPO4S)`
- Code: `aPIsoAdsS=aPAdsMaxS*aKPAdsS*oPO4S/(1.0_rk+aKPAdsS*oPO4S)`

### `fPEqIMS` [-] *P adsorption*
- DESC: calculate fraction of PAIMS is in equilibrium
- Source: abiotic_sediment.F90 (266-266)
- Formula (d⁻¹): `sPAIMS / max(aPEqIMS, NearZero)`
- Code: `fPEqIMS = sPAIMS / max(aPEqIMS, NearZero)`

### `tPChemPO4` [-] *P adsorption*
- DESC: calculate chem. loss of dissolved P from pore water
- Source: abiotic_sediment.F90 (268-268)
- Formula (d⁻¹): `max( 0.0, kPChemPO4*(oPO4S-coPO4Max))`
- Code: `tPChemPO4=max( 0.0_rk,self%kPChemPO4*(oPO4S-self%coPO4Max))`

### `tPSorpIMS` [-] *P adsorption*
- DESC: calculate sorption
- Source: abiotic_sediment.F90 (267-267)
- Formula (d⁻¹): `kPSorpS*(aPEqIMS-sPAIMS)`
- Code: `tPSorpIMS=self%kPSorpS*(aPEqIMS-sPAIMS)`

## Parameters

### `cExtSpIM` [m2/gDW] *Parameters*
- DESC: specific extinction inorganic matter
- Source: abiotic_water.F90 (67-67)
- Formula (d⁻¹): `0.05`
- Code: `call self%get_parameter(self%cExtSpIM, 'cExtSpIM', 'm2/gDW', 'specific extinction inorganic matter', default=0.05_rk)`

### `cKPAdsOxW` [m3/gP] *Parameters*
- DESC: P adsorption affinity at oxidized conditions
- Source: abiotic_water.F90 (68-68)
- Formula (d⁻¹): `0.6`
- Code: `call self%get_parameter(self%cKPAdsOxW, 'cKPAdsOxW', 'm3/gP', 'P adsorption affinity at oxidized conditions', default=0.6_rk)`

### `cRelPAdsAlW` [gP/gAl] *Parameters*
- DESC: maximum P adsorption per g Al
- Source: abiotic_water.F90 (69-69)
- Formula (d⁻¹): `0.134`
- Code: `call self%get_parameter(self%cRelPAdsAlW, 'cRelPAdsAlW', 'gP/gAl', 'maximum P adsorption per g Al', default=0.134_rk)`

### `cRelPAdsDWW` [gP/gDW] *Parameters*
- DESC: maximum P adsorption per g DW
- Source: abiotic_water.F90 (70-70)
- Formula (d⁻¹): `0.00003`
- Code: `call self%get_parameter(self%cRelPAdsDWW, 'cRelPAdsDWW', 'gP/gDW', 'maximum P adsorption per g DW', default=0.00003_rk)`

### `cRelPAdsFeW` [gP/gFe] *Parameters*
- DESC: maximum P adsorption per g Fe
- Source: abiotic_water.F90 (71-71)
- Formula (d⁻¹): `0.0675`
- Code: `call self%get_parameter(self%cRelPAdsFeW, 'cRelPAdsFeW', 'gP/gFe', 'maximum P adsorption per g Fe', default=0.0675_rk)`

### `cThetaAer` [1/e^*C] *Parameters*
- DESC: temperature coefficient for reaeration
- Source: abiotic_water.F90 (72-72)
- Formula (d⁻¹): `1.011`
- Code: `call self%get_parameter(self%cThetaAer, 'cThetaAer', '1/e^*C', 'temperature coefficient for reaeration', default=1.011_rk)`

### `cThetaMinSiW` [1/e^*C] *Parameters*
- DESC: temperature coefficient of SiO2 mineralization
- Source: abiotic_water.F90 (85-85)
- Formula (d⁻¹): `1.02`
- Code: `call self%get_parameter(self%cThetaMinSiW, 'cThetaMinSiW', '1/e^*C', 'temperature coefficient of SiO2 mineralization', default=1.02_rk)`

### `cThetaNitrW` [1/e^*C] *Parameters*
- DESC: temperature coefficient for nitrification
- Source: abiotic_water.F90 (73-73)
- Formula (d⁻¹): `1.03`
- Code: `call self%get_parameter(self%cThetaNitrW, 'cThetaNitrW', '1/e^*C', 'temperature coefficient for nitrification', default=1.03_rk)`

### `cVSetIM` [m/d] *Parameters*
- DESC: maximum settling rate of inorganic matter
- Source: abiotic_water.F90 (75-75)
- Formula (d⁻¹): `-1.1`
- Code: `call self%get_parameter(self%cVSetIM, 'cVSetIM', 'm/d', 'maximum settling rate of inorganic matter', default=-1.1_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cVSetSi` [m/d] *Parameters*
- DESC: maximum settling rate of Si particulate
- Source: abiotic_water.F90 (74-74)
- Formula (d⁻¹): `-0.3`
- Code: `call self%get_parameter(self%cVSetSi, 'cVSetSi', 'm/d', 'maximum settling rate of Si particulate', default=-0.3_rk, scale_factor=1.0_rk/secs_pr_day)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: abiotic_water.F90 (93-93)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fAlDIMW` [gAl/gDW] *Parameters*
- DESC: Al content of inorganic matter
- Source: abiotic_water.F90 (76-76)
- Formula (d⁻¹): `0.01`
- Code: `call self%get_parameter(self%fAlDIMW, 'fAlDIMW', 'gAl/gDW', 'Al content of inorganic matter', default=0.01_rk)`

### `fFeDIMW` [gFe/gDW] *Parameters*
- DESC: Fe content of inorganic matter
- Source: abiotic_water.F90 (77-77)
- Formula (d⁻¹): `0.01`
- Code: `call self%get_parameter(self%fFeDIMW, 'fFeDIMW', 'gFe/gDW', 'Fe content of inorganic matter', default=0.01_rk)`

### `fRedMaxW` [-] *Parameters*
- DESC: maximum reduction factor of P adsorption affinity
- Source: abiotic_water.F90 (78-78)
- Formula (d⁻¹): `0.9`
- Code: `call self%get_parameter(self%fRedMaxW, 'fRedMaxW', '-', 'maximum reduction factor of P adsorption affinity', default=0.9_rk)`

### `hO2BOD` [mgO2/l] *Parameters*
- DESC: half saturation oxygen conc. for BOD
- Source: abiotic_water.F90 (79-79)
- Formula (d⁻¹): `1.0`
- Code: `call self%get_parameter(self%hO2BOD, 'hO2BOD', 'mgO2/l', 'half saturation oxygen conc. for BOD', default=1.0_rk)`

### `hO2Nitr` [mgO2/l] *Parameters*
- DESC: half saturation oxygen conc. for nitrification
- Source: abiotic_water.F90 (80-80)
- Formula (d⁻¹): `2.0`
- Code: `call self%get_parameter(self%hO2Nitr, 'hO2Nitr', 'mgO2/l', 'half saturation oxygen conc. for nitrification', default=2.0_rk)`

### `kNitrW` [1/d] *Parameters*
- DESC: nitrification rate constant in water at 20*C
- Source: abiotic_water.F90 (81-81)
- Formula (d⁻¹): `0.3`
- Code: `call self%get_parameter(self%kNitrW, 'kNitrW', '1/d', 'nitrification rate constant in water at 20*C', default=0.3_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kPSorpW` [1/d] *Parameters*
- DESC: P adsorption rate constant
- Source: abiotic_water.F90 (82-82)
- Formula (d⁻¹): `0.05`
- Code: `call self%get_parameter(self%kPSorpW, 'kPSorpW', '1/d', 'P adsorption rate constant', default=0.05_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kSiMinPaW` [1/d] *Parameters*
- DESC: biodissolution constant of particulate Si to SiO2 at 20*C
- Source: abiotic_water.F90 (86-86)
- Formula (d⁻¹): `0.03`
- Code: `call self%get_parameter(self%kSiMinPaW, 'kSiMinPaW', '1/d', 'biodissolution constant of particulate Si to SiO2 at 20*C', default=0.03_rk, scale_factor=1.0_rk/secs_pr_day)`

### `O2PerNH4W` [mol/mol] *Parameters*
- DESC: used O2 per NH4 nitrified
- Source: abiotic_water.F90 (83-83)
- Formula (d⁻¹): `2.0`
- Code: `call self%get_parameter(self%O2PerNH4W, 'O2PerNH4W', 'mol/mol', 'used O2 per NH4 nitrified', default=2.0_rk)`

### `tDDepoIM` [g/m2/d] *Parameters*
- DESC: inorganic matter deposition
- Source: abiotic_water.F90 (88-88)
- Formula (d⁻¹): `0.0`
- Code: `call self%get_parameter(self%tDDepoIM, 'tDDepoIM', 'g/m2/d', 'inorganic matter deposition', default=0.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `tNDepoNH4` [g/m2/d] *Parameters*
- DESC: ammonium deposition
- Source: abiotic_water.F90 (90-90)
- Formula (d⁻¹): `0.0`
- Code: `call self%get_parameter(self%tNDepoNH4, 'tNDepoNH4', 'g/m2/d', 'ammonium deposition', default=0.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `tNDepoNO3` [g/m2/d] *Parameters*
- DESC: nitrate deposition
- Source: abiotic_water.F90 (91-91)
- Formula (d⁻¹): `0.0`
- Code: `call self%get_parameter(self%tNDepoNO3, 'tNDepoNO3', 'g/m2/d', 'nitrate deposition', default=0.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `tPDepoPO4` [g/m2/d] *Parameters*
- DESC: phosphate deposition
- Source: abiotic_water.F90 (89-89)
- Formula (d⁻¹): `0.0`
- Code: `call self%get_parameter(self%tPDepoPO4, 'tPDepoPO4', 'g/m2/d', 'phosphate deposition', default=0.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `bPorCorS` [m3/m3] *Parameters*
- DESC: sediment porosity corrected for tortuosity
- Source: abiotic_sediment.F90 (78-78)
- Formula (d⁻¹): `0.737275`
- Code: `call self%get_parameter(self%bPorCorS, 'bPorCorS', 'm3/m3', 'sediment porosity corrected for tortuosity', default=0.737275_rk)`

### `bPorS` [m3/m3] *Parameters*
- DESC: sediment porosity
- Source: abiotic_sediment.F90 (95-95)
- Formula (d⁻¹): `0.58`
- Code: `call self%get_parameter(self%bPorS, 'bPorS', 'm3/m3', 'sediment porosity', default=0.58_rk)`

### `cDepthS` [m] *Parameters*
- DESC: sediment depth
- Source: abiotic_sediment.F90 (76-76)
- Formula (d⁻¹): `0.1`
- Code: `call self%get_parameter(self%cDepthS, 'cDepthS', 'm', 'sediment depth', default=0.1_rk)`

### `cKPAdsOxS` [m3/gP] *Parameters*
- DESC: P adsorption affinity at oxidized conditions
- Source: abiotic_sediment.F90 (92-92)
- Formula (d⁻¹): `1.5`
- Code: `call self%get_parameter(self%cKPAdsOxS, 'cKPAdsOxS', 'm3/gP', 'P adsorption affinity at oxidized conditions', default=1.5_rk)`

### `coPO4Max` [mgP/l] *Parameters*
- DESC: max. soluble reactive P conc. in pore water
- Source: abiotic_sediment.F90 (94-94)
- Formula (d⁻¹): `1.4`
- Code: `call self%get_parameter(self%coPO4Max, 'coPO4Max', 'mgP/l', 'max. soluble reactive P conc. in pore water', default=1.4_rk)`

### `cRelPAdsAlS` [gP/gAl] *Parameters*
- DESC: max. P adsorption per g Al
- Source: abiotic_sediment.F90 (89-89)
- Formula (d⁻¹): `0.134`
- Code: `call self%get_parameter(self%cRelPAdsAlS, 'cRelPAdsAlS', 'gP/gAl', 'max. P adsorption per g Al', default=0.134_rk)`

### `cRelPAdsDWS` [gP/gDW] *Parameters*
- DESC: max. P adsorption per g DW
- Source: abiotic_sediment.F90 (86-86)
- Formula (d⁻¹): `0.00003`
- Code: `call self%get_parameter(self%cRelPAdsDWS, 'cRelPAdsDWS', 'gP/gDW', 'max. P adsorption per g DW', default=0.00003_rk)`

### `cRelPAdsFeS` [gP/gFe] *Parameters*
- DESC: max. P adsorption per g Fe
- Source: abiotic_sediment.F90 (87-87)
- Formula (d⁻¹): `0.06`
- Code: `call self%get_parameter(self%cRelPAdsFeS, 'cRelPAdsFeS', 'gP/gFe', 'max. P adsorption per g Fe', default=0.06_rk)`

### `cThetaDifO2` [1/e^*C] *Parameters*
- DESC: temperature coefficient for O2 diffusion
- Source: abiotic_sediment.F90 (96-96)
- Formula (d⁻¹): `1.01`
- Code: `call self%get_parameter(self%cThetaDifO2, 'cThetaDifO2', '1/e^*C', 'temperature coefficient for O2 diffusion', default=1.01_rk)`

### `cThetaMinSiS` [1/e^*C] *Parameters*
- DESC: temperature coefficient of SiO2 mineralization
- Source: abiotic_sediment.F90 (100-100)
- Formula (d⁻¹): `1.074`
- Code: `call self%get_parameter(self%cThetaMinSiS, 'cThetaMinSiS', '1/e^*C', 'temperature coefficient of SiO2 mineralization', default=1.074_rk)`

### `cThetaNitrS` [1/e^*C] *Parameters*
- DESC: temperature coefficient for nitrification
- Source: abiotic_sediment.F90 (82-82)
- Formula (d⁻¹): `1.03`
- Code: `call self%get_parameter(self%cThetaNitrS, 'cThetaNitrS', '1/e^*C', 'temperature coefficient for nitrification', default=1.03_rk)`

### `cTurbDifO2` [-] *Parameters*
- DESC: bioturbation factor for oxygen diffusion
- Source: abiotic_sediment.F90 (98-98)
- Formula (d⁻¹): `5.0`
- Code: `call self%get_parameter(self%cTurbDifO2, 'cTurbDifO2', '-', 'bioturbation factor for oxygen diffusion', default=5.0_rk)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: abiotic_sediment.F90 (105-105)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fAlDIMS` [gAl/gD] *Parameters*
- DESC: Al content of inorganic matter
- Source: abiotic_sediment.F90 (90-90)
- Formula (d⁻¹): `0.01`
- Code: `call self%get_parameter(self%fAlDIMS, 'fAlDIMS', 'gAl/gD', 'Al content of inorganic matter', default=0.01_rk)`

### `fDepthDifS` [-] *Parameters*
- DESC: nutrient diffusion distance as fraction of sediment depth
- Source: abiotic_sediment.F90 (77-77)
- Formula (d⁻¹): `0.5`
- Code: `call self%get_parameter(self%fDepthDifS, 'fDepthDifS', '-', 'nutrient diffusion distance as fraction of sediment depth', default=0.5_rk)`

### `fFeDIM` [gFe/gD] *Parameters*
- DESC: Fe content of inorganic matter
- Source: abiotic_sediment.F90 (88-88)
- Formula (d⁻¹): `0.04`
- Code: `call self%get_parameter(self%fFeDIM, 'fFeDIM', 'gFe/gD', 'Fe content of inorganic matter', default=0.04_rk)`

### `fRedMaxS` [-] *Parameters*
- DESC: max. reduction factor of P adsorption affinity
- Source: abiotic_sediment.F90 (91-91)
- Formula (d⁻¹): `0.96`
- Code: `call self%get_parameter(self%fRedMaxS, 'fRedMaxS', '-', 'max. reduction factor of P adsorption affinity', default=0.96_rk)`

### `hNO3DenitS` [mgN/l] *Parameters*
- DESC: quadratic half-sat. NO3 conc. for denitrification
- Source: abiotic_sediment.F90 (84-84)
- Formula (d⁻¹): `0.5`
- Code: `call self%get_parameter(self%hNO3DenitS, 'hNO3DenitS', 'mgN/l', 'quadratic half-sat. NO3 conc. for denitrification', default=0.5_rk)`

### `hypsograph` [-] *Parameters*
- DESC: indicate hypsograph presence/absence
- Source: abiotic_sediment.F90 (106-106)
- Formula (d⁻¹): `-`
- Code: `call self%get_parameter(self%hypsograph, 'hypsograph', '-', 'indicate hypsograph presence/absence')`

### `kDMinHum` [1/d] *Parameters*
- DESC: humic decomposition constant at 20*C
- Source: abiotic_sediment.F90 (99-99)
- Formula (d⁻¹): `0.00005`
- Code: `call self%get_parameter(self%kDMinHum, 'kDMinHum', '1/d', 'humic decomposition constant at 20*C', default=0.00005_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kNitrS` [1/d] *Parameters*
- DESC: nitrification rate constant at 20*C
- Source: abiotic_sediment.F90 (81-81)
- Formula (d⁻¹): `1.2`
- Code: `call self%get_parameter(self%kNitrS, 'kNitrS', '1/d', 'nitrification rate constant at 20*C', default=1.2_rk, scale_factor =1.0_rk/secs_pr_day)`

### `kO2Dif` [m2/d] *Parameters*
- DESC: O2 diffusion constant at 20*C
- Source: abiotic_sediment.F90 (97-97)
- Formula (d⁻¹): `0.00017`
- Code: `call self%get_parameter(self%kO2Dif, 'kO2Dif', 'm2/d', 'O2 diffusion constant at 20*C', default=0.00017_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kPChemPO4` [1/d] *Parameters*
- DESC: chemical PO4 loss rate
- Source: abiotic_sediment.F90 (93-93)
- Formula (d⁻¹): `0.03`
- Code: `call self%get_parameter(self%kPChemPO4, 'kPChemPO4', '1/d', 'chemical PO4 loss rate', default=0.03_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kPSorpS` [1/d] *Parameters*
- DESC: P sorption rate constant
- Source: abiotic_sediment.F90 (85-85)
- Formula (d⁻¹): `0.03`
- Code: `call self%get_parameter(self%kPSorpS, 'kPSorpS', '1/d', 'P sorption rate constant', default=0.03_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kSiMinPaS` [1/d] *Parameters*
- DESC: SiPOM to SiO2 biodissolution constant at 20*C
- Source: abiotic_sediment.F90 (101-101)
- Formula (d⁻¹): `0.03`
- Code: `call self%get_parameter(self%kSiMinPaS, 'kSiMinPaS', '1/d', 'SiPOM to SiO2 biodissolution constant at 20*C', default=0.03_rk, scale_factor=1.0_rk/secs_pr_day)`

### `nDOM` [-] *Parameters*
- DESC: number of benthic dissolved OM instances
- Source: abiotic_sediment.F90 (103-103)
- Formula (d⁻¹): `0`
- Code: `call self%get_parameter(self%nDOM, 'nDOM', '-', 'number of benthic dissolved OM instances', default=0)`

### `NO3PerCS` [mol/mol] *Parameters*
- DESC: NO3 denitrified per C mineralized
- Source: abiotic_sediment.F90 (83-83)
- Formula (d⁻¹): `1.0`
- Code: `call self%get_parameter(self%NO3PerCS, 'NO3PerCS', 'mol/mol', 'NO3 denitrified per C mineralized', default=1.0_rk)`

### `nPOM` [-] *Parameters*
- DESC: number of benthic particulate OM instances
- Source: abiotic_sediment.F90 (102-102)
- Formula (d⁻¹): `0`
- Code: `call self%get_parameter(self%nPOM, 'nPOM', '-', 'number of benthic particulate OM instances', default=0)`

### `O2PerNH4S` [mol/mol] *Parameters*
- DESC: O2 used per NH4 nitrified
- Source: abiotic_sediment.F90 (80-80)
- Formula (d⁻¹): `2.0`
- Code: `call self%get_parameter(self%O2PerNH4S, 'O2PerNH4S', 'mol/mol', 'O2 used per NH4 nitrified', default=2.0_rk)`

### `cExtSp` [m2/gDW] *Parameters*
- DESC: specific extinction factor for OM
- Source: om_pool.F90 (91)
- Formula (d⁻¹): `call self%get_parameter(self%cExtSp, 'cExtSp', 'm2/gDW', 'specific extinction factor for OM', default=0.15_rk)`
- Code: `call self%get_parameter(self%cExtSp,            'cExtSp',       'm2/gDW',      'specific extinction factor for OM',                         default=0.15_rk                                         )`

### `cThetaMinS` [1/e^*C] *Parameters*
- DESC: temperature coefficient of biotransformation in sediment
- Source: om_pool.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaMinS, 'cThetaMinS', '1/e^*C', 'temperature coefficient of biotransformation in sediment', default=1.02_rk)`
- Code: `call self%get_parameter(self%cThetaMinS,    'cThetaMinS',       '1/e^*C',      'temperature coefficient of biotransformation in sediment',  default=1.02_rk                                         )`

### `cThetaMinW` [1/e^*C] *Parameters*
- DESC: temperature coefficient of biotransformation in water
- Source: om_pool.F90 (95)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaMinW, 'cThetaMinW', '1/e^*C', 'temperature coefficient of biotransformation in water', default=1.02_rk)`
- Code: `call self%get_parameter(self%cThetaMinW,        'cThetaMinW',   '1/e^*C',      'temperature coefficient of biotransformation in water',     default=1.02_rk                                         )`

### `cVSet` [m/d] *Parameters*
- DESC: maximum settling rate of OM
- Source: om_pool.F90 (92)
- Formula (d⁻¹): `call self%get_parameter(self%cVSet, 'cVSet', 'm/d', 'maximum settling rate of OM', default=-0.3_rk)`
- Code: `call self%get_parameter(self%cVSet,             'cVSet',        'm/d',         'maximum settling rate of OM',                               default=-0.3_rk,   scale_factor=1.0_rk/secs_pr_day      )`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: om_pool.F90 (125)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,   'diagnostics',      '-',           'toggle diagnostic output',                                  default=.false.                                         )`

### `fRefrDWS` [-] *Parameters*
- DESC: refractory fraction of sediment DW OM
- Source: om_pool.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%fRefrDWS, 'fRefrDWS', '-', 'refractory fraction of sediment DW OM', default=0.0_rk)`
- Code: `call self%get_parameter(self%fRefrDWS,      'fRefrDWS',         '-',           'refractory fraction of sediment DW OM',                     default=0.0_rk                                          )`

### `fRefrNutS` [-] *Parameters*
- DESC: refractory fraction of sediment N and P OM
- Source: om_pool.F90 (122)
- Formula (d⁻¹): `call self%get_parameter(self%fRefrNutS, 'fRefrNutS', '-', 'refractory fraction of sediment N and P OM', default=0.0_rk)`
- Code: `call self%get_parameter(self%fRefrNutS,     'fRefrNutS',        '-',           'refractory fraction of sediment N and P OM',                default=0.0_rk                                          )`

### `hNO3DenitW` [mgN/l] *Parameters*
- DESC: quadratic half saturation NO3 conc. for denitrification
- Source: om_pool.F90 (100)
- Formula (d⁻¹): `call self%get_parameter(self%hNO3DenitW, 'hNO3DenitW', 'mgN/l', 'quadratic half saturation NO3 conc. for denitrification', default=1.0_rk)`
- Code: `call self%get_parameter(self%hNO3DenitW,        'hNO3DenitW',   'mgN/l',       'quadratic half saturation NO3 conc. for denitrification',   default=1.0_rk                                          )`

### `hO2BOD` [mgO2/l] *Parameters*
- DESC: half saturation oxygen conc. for BOD
- Source: om_pool.F90 (99)
- Formula (d⁻¹): `call self%get_parameter(self%hO2BOD, 'hO2BOD', 'mgO2/l', 'half saturation oxygen conc. for BOD', default=1.0_rk)`
- Code: `call self%get_parameter(self%hO2BOD,            'hO2BOD',       'mgO2/l',      'half saturation oxygen conc. for BOD',                      default=1.0_rk                                          )`

### `kDMinS` [1/d] *Parameters*
- DESC: bio-transform. in sediment constant of OM-DW at 20*C
- Source: om_pool.F90 (113)
- Formula (d⁻¹): `call self%get_parameter(self%kDMinS, 'kDMinS', '1/d', 'bio-transform. in sediment constant of OM-DW at 20*C', default=0.001_rk)`
- Code: `call self%get_parameter(self%kDMinS,        'kDMinS',           '1/d',         'bio-transform. in sediment constant of OM-DW at 20*C',      default=0.001_rk,  scale_factor=1.0_rk/secs_pr_day      )`

### `kDMinW` [1/d] *Parameters*
- DESC: bio-transform. in water constant of OM-DW at 20*C
- Source: om_pool.F90 (96)
- Formula (d⁻¹): `call self%get_parameter(self%kDMinW, 'kDMinW', '1/d', 'bio-transform. in water constant of OM-DW at 20*C', default=0.001_rk)`
- Code: `call self%get_parameter(self%kDMinW,            'kDMinW',       '1/d',         'bio-transform. in water constant of OM-DW at 20*C',         default=0.001_rk,  scale_factor=1.0_rk/secs_pr_day      )`

### `kNMinS` [1/d] *Parameters*
- DESC: bio-transform. in sediment constant of OM-N at 20*C
- Source: om_pool.F90 (114)
- Formula (d⁻¹): `call self%get_parameter(self%kNMinS, 'kNMinS', '1/d', 'bio-transform. in sediment constant of OM-N at 20*C', default=0.01_rk)`
- Code: `call self%get_parameter(self%kNMinS,        'kNMinS',           '1/d',         'bio-transform. in sediment constant of OM-N at 20*C',       default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )`

### `kNMinW` [1/d] *Parameters*
- DESC: bio-transform. in water constant of OM-N at 20*C
- Source: om_pool.F90 (97)
- Formula (d⁻¹): `call self%get_parameter(self%kNMinW, 'kNMinW', '1/d', 'bio-transform. in water constant of OM-N at 20*C', default=0.01_rk)`
- Code: `call self%get_parameter(self%kNMinW,            'kNMinW',       '1/d',         'bio-transform. in water constant of OM-N at 20*C',          default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )`

### `kPMinS` [1/d] *Parameters*
- DESC: bio-transform. in sediment constant of OM-P at 20*C
- Source: om_pool.F90 (115)
- Formula (d⁻¹): `call self%get_parameter(self%kPMinS, 'kPMinS', '1/d', 'bio-transform. in sediment constant of OM-P at 20*C', default=0.01_rk)`
- Code: `call self%get_parameter(self%kPMinS,        'kPMinS',           '1/d',         'bio-transform. in sediment constant of OM-P at 20*C',       default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )`

### `kPMinW` [1/d] *Parameters*
- DESC: bio-transform. in water constant of OM-P at 20*C
- Source: om_pool.F90 (98)
- Formula (d⁻¹): `call self%get_parameter(self%kPMinW, 'kPMinW', '1/d', 'bio-transform. in water constant of OM-P at 20*C', default=0.01_rk)`
- Code: `call self%get_parameter(self%kPMinW,            'kPMinW',       '1/d',         'bio-transform. in water constant of OM-P at 20*C',          default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )`

### `lPOMtoDOM` [-] *Parameters*
- DESC: toggle POM to DOM transformation
- Source: om_pool.F90 (117)
- Formula (d⁻¹): `call self%get_parameter(self%lPOMtoDOM, 'lPOMtoDOM', '-', 'toggle POM to DOM transformation', default=.false.)`
- Code: `call self%get_parameter(self%lPOMtoDOM,     'lPOMtoDOM',        '-',           'toggle POM to DOM transformation',                          default=.false.                                         )`

### `lRefrpool` [-] *Parameters*
- DESC: toggle bio-transform. dependent on oxic sediment fraction
- Source: om_pool.F90 (118)
- Formula (d⁻¹): `call self%get_parameter(self%lRefrpool, 'lRefrpool', '-', 'toggle bio-transform. dependent on oxic sediment fraction', default=.false.)`
- Code: `call self%get_parameter(self%lRefrpool,     'lRefrpool',        '-',           'toggle bio-transform. dependent on oxic sediment fraction', default=.false.                                         )`

### `lRefrPV` [-] *Parameters*
- DESC: refractory fraction to be projected to water
- Source: om_pool.F90 (123)
- Formula (d⁻¹): `call self%get_parameter(self%lRefrPV, 'lRefrPV', '-', 'refractory fraction to be projected to water', default=.true.)`
- Code: `call self%get_parameter(self%lRefrPV,       'lRefrPV',          '-',           'refractory fraction to be projected to water',              default=.true.                                          )`

### `lTransDWtarget` [-] *Parameters*
- DESC: toggle DW bio-transformation target
- Source: om_pool.F90 (119)
- Formula (d⁻¹): `call self%get_parameter(self%lTransDWtarget, 'lTransDWtarget', '-', 'toggle DW bio-transformation target', default=.true.)`
- Code: `call self%get_parameter(self%lTransDWtarget,'lTransDWtarget',   '-',           'toggle DW bio-transformation target',                       default=.true.                                         )`

### `lTransPV` [-] *Parameters*
- DESC: bio-transform. target to be projected to water
- Source: om_pool.F90 (116)
- Formula (d⁻¹): `call self%get_parameter(self%lTransPV, 'lTransPV', '-', 'bio-transform. target to be projected to water', default=.false.)`
- Code: `call self%get_parameter(self%lTransPV,      'lTransPV',         '-',           'bio-transform. target to be projected to water',            default=.false.                                         )`

### `NO3PerCW` [mol/mol] *Parameters*
- DESC: denitrified NO3 per C mineralised
- Source: om_pool.F90 (101)
- Formula (d⁻¹): `call self%get_parameter(self%NO3PerCW, 'NO3PerCW', 'mol/mol', 'denitrified NO3 per C mineralised', default=1.0_rk)`
- Code: `call self%get_parameter(self%NO3PerCW,          'NO3PerCW',     'mol/mol',     'denitrified NO3 per C mineralised',                         default=1.0_rk                                          )`

### `qTrans` [-] *Parameters*
- DESC: vert. trans. method: 0=no trans.; 1=constant)
- Source: om_pool.F90 (93)
- Formula (d⁻¹): `call self%get_parameter(self%qTrans, 'qTrans', '-', 'vert. trans. method: 0=no trans.; 1=constant)', default=1)`
- Code: `call self%get_parameter(self%qTrans,            'qTrans',       '-',           'vert. trans. method: 0=no trans.; 1=constant)',             default=1                                               )`

### `cAffNUpt` [l/mgDW/d] *Parameters*
- DESC: N uptake affinity
- Source: phytoplankton.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%cAffNUpt, 'cAffNUpt', 'l/mgDW/d', 'N uptake affinity', default=0.2_rk)`
- Code: `call self%get_parameter(self%cAffNUpt,      'cAffNUpt',      'l/mgDW/d',      'N uptake affinity',                                              default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day)`

### `cAffPUpt` [l/mgDW/d] *Parameters*
- DESC: P uptake affinity
- Source: phytoplankton.F90 (110)
- Formula (d⁻¹): `call self%get_parameter(self%cAffPUpt, 'cAffPUpt', 'l/mgDW/d', 'P uptake affinity', default=0.8_rk)`
- Code: `call self%get_parameter(self%cAffPUpt,      'cAffPUpt',      'l/mgDW/d',      'P uptake affinity',                                              default=0.8_rk,     scale_factor=1.0_rk/secs_pr_day)`

### `cChDMax` [mgChl/mgDW] *Parameters*
- DESC: maximum chlorophyll/C ratio
- Source: phytoplankton.F90 (138)
- Formula (d⁻¹): `call self%get_parameter(self%cChDMax, 'cChDMax', 'mgChl/mgDW', 'maximum chlorophyll/C ratio', default=0.015_rk)`
- Code: `call self%get_parameter(self%cChDMax,       'cChDMax',       'mgChl/mgDW',    'maximum chlorophyll/C ratio',                                    default=0.015_rk                                   )`

### `cChDMin` [mgChl/mgDW] *Parameters*
- DESC: minimum chlorophyll/C ratio
- Source: phytoplankton.F90 (137)
- Formula (d⁻¹): `call self%get_parameter(self%cChDMin, 'cChDMin', 'mgChl/mgDW', 'minimum chlorophyll/C ratio', default=0.005_rk)`
- Code: `call self%get_parameter(self%cChDMin,       'cChDMin',       'mgChl/mgDW',    'minimum chlorophyll/C ratio',                                    default=0.005_rk                                   )`

### `cCPerDW` [gC/gDW] *Parameters*
- DESC: C content of organic matter DW
- Source: phytoplankton.F90 (135)
- Formula (d⁻¹): `call self%get_parameter(self%cCPerDW, 'cCPerDW', 'gC/gDW', 'C content of organic matter DW', default=0.4_rk)`
- Code: `call self%get_parameter(self%cCPerDW,       'cCPerDW',       'gC/gDW',        'C content of organic matter DW',                                 default=0.4_rk                                     )`

### `cDMinS` [gDW/m3] *Parameters*
- DESC: minimum DW concentration in sediment
- Source: phytoplankton.F90 (143)
- Formula (d⁻¹): `call self%get_parameter(self%cDMinS, 'cDMinS', 'gDW/m3', 'minimum DW concentration in sediment', default=0.00001_rk)`
- Code: `call self%get_parameter(self%cDMinS,        'cDMinS',        'gDW/m3',        'minimum DW concentration in sediment',                           default=0.00001_rk                                 )`

### `cDMinW` [gDW/m3] *Parameters*
- DESC: minimum DW concentration in water
- Source: phytoplankton.F90 (114)
- Formula (d⁻¹): `call self%get_parameter(self%cDMinW, 'cDMinW', 'gDW/m3', 'minimum DW concentration in water', default=0.00001_rk)`
- Code: `call self%get_parameter(self%cDMinW,        'cDMinW',        'gDW/m3',        'minimum DW concentration in water',                              default=0.00001_rk                                 )`

### `cExtSp` [m2/gDW] *Parameters*
- DESC: specific extinction coefficient
- Source: phytoplankton.F90 (115)
- Formula (d⁻¹): `call self%get_parameter(self%cExtSp, 'cExtSp', 'm2/gDW', 'specific extinction coefficient', default=0.35_rk)`
- Code: `call self%get_parameter(self%cExtSp,        'cExtSp',        'm2/gDW',        'specific extinction coefficient',                                default=0.35_rk                                    )`

### `cLOptRef` [W/m2] *Parameters*
- DESC: qLightMethod=2; optimum PAR at 20*C; Steele function
- Source: phytoplankton.F90 (101)
- Formula (d⁻¹): `call self%get_parameter(self%cLOptRef, 'cLOptRef', 'W/m2', 'qLightMethod=2; optimum PAR at 20*C; Steele function', default=25.0_rk)`
- Code: `call self%get_parameter(self%cLOptRef,      'cLOptRef',      'W/m2',          'qLightMethod=2; optimum PAR at 20*C; Steele function',           default=25.0_rk                                    )`

### `cMuMax` [1/d] *Parameters*
- DESC: maximum growth rate at 20*C
- Source: phytoplankton.F90 (123)
- Formula (d⁻¹): `call self%get_parameter(self%cMuMax, 'cMuMax', '1/d', 'maximum growth rate at 20*C', default=1.4_rk)`
- Code: `call self%get_parameter(self%cMuMax,        'cMuMax',        '1/d',           'maximum growth rate at 20*C',                                    default=1.4_rk,     scale_factor=1.0_rk/secs_pr_day)`

### `cNDMax` [mgN/mgDW] *Parameters*
- DESC: maximum N/DW ratio
- Source: phytoplankton.F90 (133)
- Formula (d⁻¹): `call self%get_parameter(self%cNDMax, 'cNDMax', 'mgN/mgDW', 'maximum N/DW ratio', default=0.15_rk)`
- Code: `call self%get_parameter(self%cNDMax,        'cNDMax',        'mgN/mgDW',      'maximum N/DW ratio',                                             default=0.15_rk                                    )`

### `cNDMin` [mgN/mgDW] *Parameters*
- DESC: minimum N/DW ratio
- Source: phytoplankton.F90 (132)
- Formula (d⁻¹): `call self%get_parameter(self%cNDMin, 'cNDMin', 'mgN/mgDW', 'minimum N/DW ratio', default=0.018_rk)`
- Code: `call self%get_parameter(self%cNDMin,        'cNDMin',        'mgN/mgDW',      'minimum N/DW ratio',                                             default=0.018_rk                                   )`

### `cNFixMax` [mgN/mgDW/d] *Parameters*
- DESC: lNfix=.true.; maximum N fixation rate
- Source: phytoplankton.F90 (107)
- Formula (d⁻¹): `call self%get_parameter(self%cNFixMax, 'cNFixMax', 'mgN/mgDW/d', 'lNfix=.true.; maximum N fixation rate', default=0.01_rk)`
- Code: `call self%get_parameter(self%cNFixMax,      'cNFixMax',      'mgN/mgDW/d',    'lNfix=.true.; maximum N fixation rate',                          default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `cPDMax` [mgP/mgDW] *Parameters*
- DESC: maximum P/DW ratio
- Source: phytoplankton.F90 (131)
- Formula (d⁻¹): `call self%get_parameter(self%cPDMax, 'cPDMax', 'mgP/mgDW', 'maximum P/DW ratio', default=0.025_rk)`
- Code: `call self%get_parameter(self%cPDMax,        'cPDMax',        'mgP/mgDW',      'maximum P/DW ratio',                                             default=0.025_rk                                   )`

### `cPDMin` [mgP/mgDW] *Parameters*
- DESC: minimum P/DW ratio
- Source: phytoplankton.F90 (130)
- Formula (d⁻¹): `call self%get_parameter(self%cPDMin, 'cPDMin', 'mgP/mgDW', 'minimum P/DW ratio', default=0.003_rk)`
- Code: `call self%get_parameter(self%cPDMin,        'cPDMin',        'mgP/mgDW',      'minimum P/DW ratio',                                             default=0.003_rk                                   )`

### `cResusExp` [1/(gDW/m2/d)] *Parameters*
- DESC: exponent parameter for phytoplankton resuspension
- Source: phytoplankton.F90 (145)
- Formula (d⁻¹): `call self%get_parameter(self%cResusExp, 'cResusExp', '1/(gDW/m2/d)', 'exponent parameter for phytoplankton resuspension', default=-0.379_rk)`
- Code: `call self%get_parameter(self%cResusExp,     'cResusExp',     '1/(gDW/m2/d)',  'exponent parameter for phytoplankton resuspension',              default=-0.379_rk                                  )`

### `cSiD` [mgSi/mgDW] *Parameters*
- DESC: lSi=.true.; Si/DW ratio
- Source: phytoplankton.F90 (105)
- Formula (d⁻¹): `call self%get_parameter(self%cSiD, 'cSiD', 'mgSi/mgDW', 'lSi=.true.; Si/DW ratio', default=0.15_rk)`
- Code: `call self%get_parameter(self%cSiD,          'cSiD',          'mgSi/mgDW',     'lSi=.true.; Si/DW ratio',                                        default=0.15_rk                                    )`

### `cSigTm` [*C] *Parameters*
- DESC: growth rate temperature constant; sigma in Gaussian curve
- Source: phytoplankton.F90 (127)
- Formula (d⁻¹): `call self%get_parameter(self%cSigTm, 'cSigTm', '*C', 'growth rate temperature constant; sigma in Gaussian curve', default=11.6_rk)`
- Code: `call self%get_parameter(self%cSigTm,        'cSigTm',        '*C',            'growth rate temperature constant; sigma in Gaussian curve',      default=11.6_rk                                    )`

### `cTmOpt` [*C] *Parameters*
- DESC: optimum temperature of growth rate
- Source: phytoplankton.F90 (128)
- Formula (d⁻¹): `call self%get_parameter(self%cTmOpt, 'cTmOpt', '*C', 'optimum temperature of growth rate', default=25.0_rk)`
- Code: `call self%get_parameter(self%cTmOpt,        'cTmOpt',        '*C',            'optimum temperature of growth rate',                             default=25.0_rk                                    )`

### `cVNUptMax` [mgN/mgDW/d] *Parameters*
- DESC: N uptake capacity at 20*C
- Source: phytoplankton.F90 (111)
- Formula (d⁻¹): `call self%get_parameter(self%cVNUptMax, 'cVNUptMax', 'mgN/mgDW/d', 'N uptake capacity at 20*C', default=0.08_rk)`
- Code: `call self%get_parameter(self%cVNUptMax,     'cVNUptMax',     'mgN/mgDW/d',    'N uptake capacity at 20*C',                                      default=0.08_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `cVPUptMax` [mgP/mgDW/d] *Parameters*
- DESC: P uptake capacity at 20*C
- Source: phytoplankton.F90 (109)
- Formula (d⁻¹): `call self%get_parameter(self%cVPUptMax, 'cVPUptMax', 'mgP/mgDW/d', 'P uptake capacity at 20*C', default=0.04_rk)`
- Code: `call self%get_parameter(self%cVPUptMax,     'cVPUptMax',     'mgP/mgDW/d',    'P uptake capacity at 20*C',                                      default=0.04_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `cVSed` [m/d] *Parameters*
- DESC: sedimentation velocity
- Source: phytoplankton.F90 (147)
- Formula (d⁻¹): `call self%get_parameter(self%cVSed, 'cVSed', 'm/d', 'sedimentation velocity', default=0.2_rk)`
- Code: `call self%get_parameter(self%cVSed,         'cVSed',         'm/d',           'sedimentation velocity',                                         default=0.2_rk                                     )`

### `cVSet` [m/d] *Parameters*
- DESC: qTrans = 1; settling rate; NOTE: negative in case of sinking
- Source: phytoplankton.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%cVSet, 'cVSet', 'm/d', 'qTrans = 1; settling rate; NOTE: negative in case of sinking', default=0.05_rk)`
- Code: `call self%get_parameter(self%cVSet,         'cVSet',         'm/d',           'qTrans = 1; settling rate; NOTE: negative in case of sinking',   default=0.05_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `cVSwim` [m/d] *Parameters*
- DESC: qTrans > 1; vertical swimming speed
- Source: phytoplankton.F90 (117)
- Formula (d⁻¹): `call self%get_parameter(self%cVSwim, 'cVSwim', 'm/d', 'qTrans > 1; vertical swimming speed', default=10.0_rk)`
- Code: `call self%get_parameter(self%cVSwim,        'cVSwim',        'm/d',           'qTrans > 1; vertical swimming speed',                            default=10.0_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: phytoplankton.F90 (149)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,   'diagnostics',    '-',            'toggle diagnostic output',                                       default=.false.                                    )`

### `fDissMort` [-] *Parameters*
- DESC: soluble inorganic nutrient fraction of dead cells
- Source: phytoplankton.F90 (134)
- Formula (d⁻¹): `call self%get_parameter(self%fDissMort, 'fDissMort', '-', 'soluble inorganic nutrient fraction of dead cells', default=0.2_rk)`
- Code: `call self%get_parameter(self%fDissMort,     'fDissMort',     '-',             'soluble inorganic nutrient fraction of dead cells',              default=0.2_rk                                     )`

### `fDOMS` [-] *Parameters*
- DESC: DOM fraction of settled dead cells
- Source: phytoplankton.F90 (142)
- Formula (d⁻¹): `call self%get_parameter(self%fDOMS, 'fDOMS', '-', 'DOM fraction of settled dead cells', default=0.0_rk)`
- Code: `call self%get_parameter(self%fDOMS,         'fDOMS',         '-',             'DOM fraction of settled dead cells',                             default=0.0_rk                                     )`

### `fDOMW` [-] *Parameters*
- DESC: DOM fraction of dead cells
- Source: phytoplankton.F90 (139)
- Formula (d⁻¹): `call self%get_parameter(self%fDOMW, 'fDOMW', '-', 'DOM fraction of dead cells', default=0.0_rk)`
- Code: `call self%get_parameter(self%fDOMW,         'fDOMW',         '-',             'DOM fraction of dead cells',                                     default=0.0_rk                                     )`

### `fLVMmin` [W/m2] *Parameters*
- DESC: qTrans > 2; minimum detectable PAR level
- Source: phytoplankton.F90 (118)
- Formula (d⁻¹): `call self%get_parameter(self%fLVMmin, 'fLVMmin', 'W/m2', 'qTrans > 2; minimum detectable PAR level', default=0.025_rk)`
- Code: `call self%get_parameter(self%fLVMmin,       'fLVMmin',       'W/m2',          'qTrans > 2; minimum detectable PAR level',                       default=0.025_rk                                   )`

### `fMuNFix` [-] *Parameters*
- DESC: lNfix=.true.; fraction of MuMax at max N fix.
- Source: phytoplankton.F90 (108)
- Formula (d⁻¹): `call self%get_parameter(self%fMuNFix, 'fMuNFix', '-', 'lNfix=.true.; fraction of MuMax at max N fix.', default=0.9_rk)`
- Code: `call self%get_parameter(self%fMuNFix,       'fMuNFix',       '-',             'lNfix=.true.; fraction of MuMax at max N fix.',                  default=0.9_rk                                     )`

### `fNutLimVMdown` [-] *Parameters*
- DESC: qTrans = 2 or 4; threshold nut. limitation for downwards taxis
- Source: phytoplankton.F90 (119)
- Formula (d⁻¹): `call self%get_parameter(self%fNutLimVMdown, 'fNutLimVMdown', '-', 'qTrans = 2 or 4; threshold nut. limitation for downwards taxis', default=0.675_rk)`
- Code: `call self%get_parameter(self%fNutLimVMdown, 'fNutLimVMdown', '-',             'qTrans = 2 or 4; threshold nut. limitation for downwards taxis', default=0.675_rk                                   )`

### `fNutLimVMup` [-] *Parameters*
- DESC: qTrans > 2 or 4; threshold nut. limitation for upwards taxis
- Source: phytoplankton.F90 (120)
- Formula (d⁻¹): `call self%get_parameter(self%fNutLimVMup, 'fNutLimVMup', '-', 'qTrans > 2 or 4; threshold nut. limitation for upwards taxis', default=0.75_rk)`
- Code: `call self%get_parameter(self%fNutLimVMup,   'fNutLimVMup',   '-',             'qTrans > 2 or 4; threshold nut. limitation for upwards taxis',   default=0.75_rk                                    )`

### `hLRef` [W/m2] *Parameters*
- DESC: qLightMethod=1; half-sat. PAR at 20*C; Lehmann function
- Source: phytoplankton.F90 (100)
- Formula (d⁻¹): `call self%get_parameter(self%hLRef, 'hLRef', 'W/m2', 'qLightMethod=1; half-sat. PAR at 20*C; Lehmann function', default=17.0_rk)`
- Code: `call self%get_parameter(self%hLRef,         'hLRef',         'W/m2',          'qLightMethod=1; half-sat. PAR at 20*C; Lehmann function',        default=17.0_rk                                    )`

### `hO2BOD` [mgO2/l] *Parameters*
- DESC: half-saturation constant for oxygen conc. on BOD
- Source: phytoplankton.F90 (136)
- Formula (d⁻¹): `call self%get_parameter(self%hO2BOD, 'hO2BOD', 'mgO2/l', 'half-saturation constant for oxygen conc. on BOD', default=1.0_rk)`
- Code: `call self%get_parameter(self%hO2BOD,        'hO2BOD',        'mgO2/l',        'half-saturation constant for oxygen conc. on BOD',               default=1.0_rk                                     )`

### `hSiAss` [mgSi/l] *Parameters*
- DESC: half-saturation constant for Si; only for lSi=.true.
- Source: phytoplankton.F90 (104)
- Formula (d⁻¹): `call self%get_parameter(self%hSiAss, 'hSiAss', 'mgSi/l', 'half-saturation constant for Si; only for lSi=.true.', default=0.09_rk)`
- Code: `call self%get_parameter(self%hSiAss,        'hSiAss',        'mgSi/l',        'half-saturation constant for Si; only for lSi=.true.',           default=0.09_rk                                    )`

### `kDResp` [1/d] *Parameters*
- DESC: maintenance respiration constant at 20*C
- Source: phytoplankton.F90 (124)
- Formula (d⁻¹): `call self%get_parameter(self%kDResp, 'kDResp', '1/d', 'maintenance respiration constant at 20*C', default=0.03_rk)`
- Code: `call self%get_parameter(self%kDResp,        'kDResp',        '1/d',           'maintenance respiration constant at 20*C',                       default=0.03_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `kMortS` [1/d] *Parameters*
- DESC: mortality rate of settled phytoplankton
- Source: phytoplankton.F90 (141)
- Formula (d⁻¹): `call self%get_parameter(self%kMortS, 'kMortS', '1/d', 'mortality rate of settled phytoplankton', default=0.2_rk)`
- Code: `call self%get_parameter(self%kMortS,        'kMortS',        '1/d',           'mortality rate of settled phytoplankton',                        default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day)`

### `kMortW` [1/d] *Parameters*
- DESC: mortality constant in water
- Source: phytoplankton.F90 (125)
- Formula (d⁻¹): `call self%get_parameter(self%kMortW, 'kMortW', '1/d', 'mortality constant in water', default=0.01_rk)`
- Code: `call self%get_parameter(self%kMortW,        'kMortW',        '1/d',           'mortality constant in water',                                    default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)`

### `kResusMax` [1/d] *Parameters*
- DESC: maximum phytoplankton resuspension rate
- Source: phytoplankton.F90 (146)
- Formula (d⁻¹): `call self%get_parameter(self%kResusMax, 'kResusMax', '1/d', 'maximum phytoplankton resuspension rate', default=0.25_rk)`
- Code: `call self%get_parameter(self%kResusMax,     'kResusMax',     '1/d',           'maximum phytoplankton resuspension rate',                        default=0.25_rk                                    )`

### `lNfix` [-] *Parameters*
- DESC: toggle nitrogen fixation
- Source: phytoplankton.F90 (106)
- Formula (d⁻¹): `call self%get_parameter(self%lNfix, 'lNfix', '-', 'toggle nitrogen fixation', default=.false.)`
- Code: `call self%get_parameter(self%lNfix,         'lNfix',         '-',             'toggle nitrogen fixation',                                       default=.false.                                    )`

### `lSi` [-] *Parameters*
- DESC: toggle Si usage
- Source: phytoplankton.F90 (103)
- Formula (d⁻¹): `call self%get_parameter(self%lSi, 'lSi', '-', 'toggle Si usage', default=.false.)`
- Code: `call self%get_parameter(self%lSi,           'lSi',           '-',             'toggle Si usage',                                                default=.false.                                    )`

### `qLightMethod` [-] *Parameters*
- DESC: lightmethod 1=no photoinhibition; 2=photoinhibition
- Source: phytoplankton.F90 (99)
- Formula (d⁻¹): `call self%get_parameter(self%qLightMethod, 'qLightMethod', '-', 'lightmethod 1=no photoinhibition; 2=photoinhibition', default=2)`
- Code: `call self%get_parameter(self%qLightMethod,  'qLightMethod',  '-',             'lightmethod 1=no photoinhibition; 2=photoinhibition',            default=2                                          )`

### `qTrans` [-] *Parameters*
- DESC: vert. trans. method: 0=no trans.; 1=constant; 2=Nut. taxis; 3=Light taxis; 4=N&L)
- Source: phytoplankton.F90 (116)
- Formula (d⁻¹): `call self%get_parameter(self%qTrans, 'qTrans', '-', 'vert. trans. method: 0=no trans.; 1=constant; 2=Nut. taxis; 3=Light taxis; 4=N&L)', default=1)`
- Code: `call self%get_parameter(self%qTrans,        'qTrans',        '-',             'vert. trans. method: 0=no trans.; 1=constant; 2=Nut. taxis; 3=Light taxis; 4=N&L)',  default=1                      )`

### `cCDRef` [mgC/mgDW] *Parameters*
- DESC: reference C/DW-ratio
- Source: zooplankton.F90 (102)
- Formula (d⁻¹): `0.45_rk`
- Code: `call self%get_parameter(self%cCDRef, 'cCDRef', 'mgC/mgDW', 'reference C/DW-ratio', default=0.45_rk)`

### `cClearPrey` [m3/gDW/d] *Parameters*
- DESC: clearance rate for prey
- Source: zooplankton.F90 (91)
- Formula (d⁻¹): `2.0_rk`
- Code: `call self%get_parameter(self%cClearPrey(i_prey), 'cClearPrey'//trim(index), 'm3/gDW/d', 'clearance rate for prey '//trim(index), default=2.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cDCarrZoo` [gDW/m3] *Parameters*
- DESC: carrying capacity
- Source: zooplankton.F90 (73)
- Formula (d⁻¹): `25.0_rk`
- Code: `call self%get_parameter(self%cDCarrZoo, 'cDCarrZoo', 'gDW/m3', 'carrying capacity', default=25.0_rk)`

### `cDMinZoo` [gDW/m3] *Parameters*
- DESC: minimum DW concentration
- Source: zooplankton.F90 (72)
- Formula (d⁻¹): `0.00001_rk`
- Code: `call self%get_parameter(self%cDMinZoo, 'cDMinZoo', 'gDW/m3', 'minimum DW concentration', default=0.00001_rk)`

### `cMaxLight` [W/m2] *Parameters*
- DESC: qtrans = 3; light level triggering downwards swimming
- Source: zooplankton.F90 (78)
- Formula (d⁻¹): `40.0_rk`
- Code: `call self%get_parameter(self%cMaxLight, 'cMaxLight', 'W/m2', 'qtrans = 3; light level triggering downwards swimming', default=40.0_rk)`

### `cMinLight` [W/m2] *Parameters*
- DESC: qtrans = 3; light level triggering upwards swimming
- Source: zooplankton.F90 (77)
- Formula (d⁻¹): `40.0_rk`
- Code: `call self%get_parameter(self%cMinLight, 'cMinLight', 'W/m2', 'qtrans = 3; light level triggering upwards swimming', default=40.0_rk)`

### `cMinO2` [gO2/m3] *Parameters*
- DESC: qtrans > 1; oxygen conc. limit
- Source: zooplankton.F90 (76)
- Formula (d⁻¹): `2.0_rk`
- Code: `call self%get_parameter(self%cMinO2, 'cMinO2', 'gO2/m3', 'qtrans > 1; oxygen conc. limit', default=2.0_rk)`

### `cNDRef` [mgN/mgDW] *Parameters*
- DESC: reference N/DW-ratio
- Source: zooplankton.F90 (101)
- Formula (d⁻¹): `0.07_rk`
- Code: `call self%get_parameter(self%cNDRef, 'cNDRef', 'mgN/mgDW', 'reference N/DW-ratio', default=0.07_rk)`

### `cPDRef` [mgP/mgDW] *Parameters*
- DESC: reference P/DW-ratio
- Source: zooplankton.F90 (100)
- Formula (d⁻¹): `0.01_rk`
- Code: `call self%get_parameter(self%cPDRef, 'cPDRef', 'mgP/mgDW', 'reference P/DW-ratio', default=0.01_rk)`

### `cSigTmZoo` [*C] *Parameters*
- DESC: temperature constant; sigma in Gaussian curve
- Source: zooplankton.F90 (107)
- Formula (d⁻¹): `13.0_rk`
- Code: `call self%get_parameter(self%cSigTmZoo, 'cSigTmZoo', '*C', 'temperature constant; sigma in Gaussian curve', default=13.0_rk)`

### `cTmOptZoo` [*C] *Parameters*
- DESC: optimum temperature
- Source: zooplankton.F90 (108)
- Formula (d⁻¹): `22.0_rk`
- Code: `call self%get_parameter(self%cTmOptZoo, 'cTmOptZoo', '*C', 'optimum temperature', default=22.0_rk)`

### `cVswim` [m/d] *Parameters*
- DESC: qtrans > 1; vertical migration speed
- Source: zooplankton.F90 (79)
- Formula (d⁻¹): `15.0_rk`
- Code: `call self%get_parameter(self%cVswim, 'cVswim', 'm/d', 'qtrans > 1; vertical migration speed', default=15.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: zooplankton.F90 (110)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fDAssZoo` [-] *Parameters*
- DESC: dry weight assimilation efficiency
- Source: zooplankton.F90 (96)
- Formula (d⁻¹): `0.35_rk`
- Code: `call self%get_parameter(self%fDAssZoo, 'fDAssZoo', '-', 'dry weight assimilation efficiency', default=0.35_rk)`

### `fDissEgesZoo` [-] *Parameters*
- DESC: soluble inorg. nutrient fraction of egested food
- Source: zooplankton.F90 (103)
- Formula (d⁻¹): `0.25_rk`
- Code: `call self%get_parameter(self%fDissEgesZoo, 'fDissEgesZoo', '-', 'soluble inorg. nutrient fraction of egested food', default=0.25_rk)`

### `fDissMortZoo` [-] *Parameters*
- DESC: soluble inorg. nutrient fraction of dead ind.
- Source: zooplankton.F90 (104)
- Formula (d⁻¹): `0.1_rk`
- Code: `call self%get_parameter(self%fDissMortZoo, 'fDissMortZoo', '-', 'soluble inorg. nutrient fraction of dead ind.', default=0.1_rk)`

### `fGutOccPrey` [-] *Parameters*
- DESC: gut occupation factor for prey
- Source: zooplankton.F90 (92)
- Formula (d⁻¹): `1.0_rk`
- Code: `call self%get_parameter(self%fGutOccPrey(i_prey), 'fGutOccPrey'//trim(index), '-', 'gut occupation factor for prey '//trim(index), default=1.0_rk)`

### `fZooDOMW` [-] *Parameters*
- DESC: DOM fraction of dead individuals
- Source: zooplankton.F90 (105)
- Formula (d⁻¹): `0.35_rk`
- Code: `call self%get_parameter(self%fZooDOMW, 'fZooDOMW', '-', 'DOM fraction of dead individuals', default=0.35_rk)`

### `kDConsMaxZoo` [gDW/gDW/d] *Parameters*
- DESC: standard dry weight specific maximum consumption rate
- Source: zooplankton.F90 (98)
- Formula (d⁻¹): `0.5_rk`
- Code: `call self%get_parameter(self%kDConsMaxZoo, 'kDConsMaxZoo', 'gDW/gDW/d', 'standard dry weight specific maximum consumption rate', default=0.5_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kDRespZoo` [1/d] *Parameters*
- DESC: maintenance respiration rate at 20*C
- Source: zooplankton.F90 (95)
- Formula (d⁻¹): `0.2_rk`
- Code: `call self%get_parameter(self%kDRespZoo, 'kDRespZoo', '1/d', 'maintenance respiration rate at 20*C', default=0.2_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortZoo` [1/d] *Parameters*
- DESC: mortality rate
- Source: zooplankton.F90 (97)
- Formula (d⁻¹): `0.04_rk`
- Code: `call self%get_parameter(self%kMortZoo, 'kMortZoo', '1/d', 'mortality rate', default=0.04_rk, scale_factor=1.0_rk/secs_pr_day)`

### `nPrey` [-] *Parameters*
- DESC: number of prey types
- Source: zooplankton.F90 (81)
- Formula (d⁻¹): `1`
- Code: `call self%get_parameter(self%nPrey, 'nPrey', '-', 'number of prey types', default=1)`

### `qODB` [-] *Parameters*
- DESC: toggle optimal diet breadth: 0=off; 1=on
- Source: zooplankton.F90 (82)
- Formula (d⁻¹): `0`
- Code: `call self%get_parameter(self%qODB, 'qODB', '-', 'toggle optimal diet breadth: 0=off; 1=on', default=0)`

### `qTrans` [-] *Parameters*
- DESC: vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light
- Source: zooplankton.F90 (75)
- Formula (d⁻¹): `2`
- Code: `call self%get_parameter(self%qTrans, 'qTrans', '-', 'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light', default=2)`

### `cCDRef` [gC/gDW] *Parameters*
- DESC: reference C/DW ratio
- Source: zoobenthos.F90 (106)
- Formula (d⁻¹): `0.45_rk`
- Code: `call self%get_parameter(self%cCDRef, 'cCDRef', 'gC/gDW', 'reference C/DW ratio', default=0.45_rk)`

### `cClearPrey` [m2/gDW/d] *Parameters*
- DESC: clearance rate for prey
- Source: zoobenthos.F90 (88)
- Formula (d⁻¹): `0.015_rk`
- Code: `call self%get_parameter(self%cClearPrey(i_prey), 'cClearPrey'//trim(index), 'm2/gDW/d','clearance rate for prey '//trim(index), default=0.015_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cDBentIn` [gDW/m2] *Parameters*
- DESC: external density
- Source: zoobenthos.F90 (77)
- Formula (d⁻¹): `0.01_rk`
- Code: `call self%get_parameter(self%cDBentIn, 'cDBentIn', 'gDW/m2', 'external density', default=0.01_rk)`

### `cDCarrBent` [gDW/m2] *Parameters*
- DESC: carrying capacity
- Source: zoobenthos.F90 (76)
- Formula (d⁻¹): `10.0_rk`
- Code: `call self%get_parameter(self%cDCarrBent, 'cDCarrBent', 'gDW/m2', 'carrying capacity', default=10.0_rk)`

### `cDVegCarr` [gDW/m2/gDW] *Parameters*
- DESC: lVegOpt = .true.; scaling factor for carr cap. with macrophyte biomass
- Source: zoobenthos.F90 (100)
- Formula (d⁻¹): `0.025_rk`
- Code: `call self%get_parameter(self%cDVegCarr, 'cDVegCarr', 'gDW/m2/gDW', 'lVegOpt = .true.; scaling factor for carr cap. with macrophyte biomass', default=0.025_rk)`

### `cNDRef` [gN/gDW] *Parameters*
- DESC: reference N/DW ratio
- Source: zoobenthos.F90 (105)
- Formula (d⁻¹): `0.07_rk`
- Code: `call self%get_parameter(self%cNDRef, 'cNDRef', 'gN/gDW', 'reference N/DW ratio', default=0.07_rk)`

### `cPDRef` [gP/gDW] *Parameters*
- DESC: reference P/DW ratio
- Source: zoobenthos.F90 (104)
- Formula (d⁻¹): `0.01_rk`
- Code: `call self%get_parameter(self%cPDRef, 'cPDRef', 'gP/gDW', 'reference P/DW ratio', default=0.01_rk)`

### `cSigTmBent` [*C] *Parameters*
- DESC: temp. constant; sigma in Gaussian curve
- Source: zoobenthos.F90 (110)
- Formula (d⁻¹): `16.0_rk`
- Code: `call self%get_parameter(self%cSigTmBent, 'cSigTmBent', '*C', 'temp. constant; sigma in Gaussian curve', default=16.0_rk)`

### `cTmOptBent` [*C] *Parameters*
- DESC: optimal temperature
- Source: zoobenthos.F90 (109)
- Formula (d⁻¹): `25.0_rk`
- Code: `call self%get_parameter(self%cTmOptBent, 'cTmOptBent', '*C', 'optimal temperature', default=25.0_rk)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: zoobenthos.F90 (112)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fBentDOMS` [-] *Parameters*
- DESC: DOM fraction of dead individuals
- Source: zoobenthos.F90 (107)
- Formula (d⁻¹): `0.5_rk`
- Code: `call self%get_parameter(self%fBentDOMS, 'fBentDOMS', '-', 'DOM fraction of dead individuals', default=0.5_rk)`

### `fDAssBent` [-] *Parameters*
- DESC: C assimilation efficiency
- Source: zoobenthos.F90 (94)
- Formula (d⁻¹): `0.3_rk`
- Code: `call self%get_parameter(self%fDAssBent, 'fDAssBent', '-', 'C assimilation efficiency', default=0.3_rk)`

### `fDissEgesBent` [-] *Parameters*
- DESC: soluble inorg. nut. fract. of egested food
- Source: zoobenthos.F90 (102)
- Formula (d⁻¹): `0.25_rk`
- Code: `call self%get_parameter(self%fDissEgesBent, 'fDissEgesBent', '-', 'soluble inorg. nut. fract. of egested food', default=0.25_rk)`

### `fDissMortBent` [-] *Parameters*
- DESC: soluble inorg. nut. fract. of dead ind.
- Source: zoobenthos.F90 (103)
- Formula (d⁻¹): `0.1_rk`
- Code: `call self%get_parameter(self%fDissMortBent, 'fDissMortBent', '-', 'soluble inorg. nut. fract. of dead ind.', default=0.1_rk)`

### `fGutOccPrey` [-] *Parameters*
- DESC: gut occupation factor for prey
- Source: zoobenthos.F90 (87)
- Formula (d⁻¹): `1.0_rk`
- Code: `call self%get_parameter(self%fGutOccPrey(i_prey),'fGutOccPrey'//trim(index),'-', 'gut occupation factor for prey '//trim(index),default=1.0_rk)`

### `hO2stress` [pct] *Parameters*
- DESC: Michaelis-Menten constant for oxygen limitation
- Source: zoobenthos.F90 (97)
- Formula (d⁻¹): `25.0_rk`
- Code: `call self%get_parameter(self%hO2stress, 'hO2stress', 'pct', 'Michaelis-Menten constant for oxygen limitation', default=25.0_rk)`

### `kDConsMaxBent` [gDW/gDW/d] *Parameters*
- DESC: standard dry weight specific maximum consumption rate
- Source: zoobenthos.F90 (93)
- Formula (d⁻¹): `0.33_rk`
- Code: `call self%get_parameter(self%kDConsMaxBent, 'kDConsMaxBent', 'gDW/gDW/d','standard dry weight specific maximum consumption rate', default=0.33_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kDRespBent` [1/d] *Parameters*
- DESC: respiration rate at 20*C
- Source: zoobenthos.F90 (95)
- Formula (d⁻¹): `0.005_rk`
- Code: `call self%get_parameter(self%kDRespBent, 'kDRespBent', '1/d', 'respiration rate at 20*C', default=0.005_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMigrBent` [1/d] *Parameters*
- DESC: migration rate
- Source: zoobenthos.F90 (78)
- Formula (d⁻¹): `0.001_rk`
- Code: `call self%get_parameter(self%kMigrBent, 'kMigrBent', '1/d', 'migration rate', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortBent` [1/d] *Parameters*
- DESC: mortality rate
- Source: zoobenthos.F90 (96)
- Formula (d⁻¹): `0.005_rk`
- Code: `call self%get_parameter(self%kMortBent, 'kMortBent', '1/d', 'mortality rate', default=0.005_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortO2` [1/d] *Parameters*
- DESC: specific max. add. mortality due to oxygen stress
- Source: zoobenthos.F90 (98)
- Formula (d⁻¹): `0.05_rk`
- Code: `call self%get_parameter(self%kMortO2, 'kMortO2', '1/d', 'specific max. add. mortality due to oxygen stress', default=0.05_rk, scale_factor=1.0_rk/secs_pr_day)`

### `lVegOpt` [-] *Parameters*
- DESC: switch for macrophyte dependence on zoobenthos carrying capacity
- Source: zoobenthos.F90 (99)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%lVegOpt, 'lVegOpt', '-', 'switch for macrophyte dependence on zoobenthos carrying capacity',default=.false.)`

### `nPrey` [-] *Parameters*
- DESC: number of prey types
- Source: zoobenthos.F90 (80)
- Formula (d⁻¹): `1`
- Code: `call self%get_parameter(self%nPrey, 'nPrey', '-', 'number of prey types', default=1)`

### `cAffNUptVeg` [l/mgDW/d] *Parameters*
- DESC: N uptake affinity
- Source: macrophytes.F90 (110)
- Formula (d⁻¹): `0.2_rk`
- Code: `call self%get_parameter(self%cAffNUptVeg, 'cAffNUptVeg', 'l/mgDW/d', 'N uptake affinity', default=0.2_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cAffPUptVeg` [l/mgDW/d] *Parameters*
- DESC: P uptake affinity
- Source: macrophytes.F90 (112)
- Formula (d⁻¹): `0.2_rk`
- Code: `call self%get_parameter(self%cAffPUptVeg, 'cAffPUptVeg', 'l/mgDW/d', 'P uptake affinity', default=0.2_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cCovSpVeg` [l/gDW/m2] *Parameters*
- DESC: specific cover
- Source: macrophytes.F90 (125)
- Formula (d⁻¹): `0.5_rk`
- Code: `call self%get_parameter(self%cCovSpVeg, 'cCovSpVeg', 'l/gDW/m2', 'specific cover', default=0.5_rk)`

### `cCPerDW` [gC/gDW] *Parameters*
- DESC: C content of organic matter DW
- Source: macrophytes.F90 (144)
- Formula (d⁻¹): `0.4_rk`
- Code: `call self%get_parameter(self%cCPerDW, 'cCPerDW', 'gC/gDW', 'C content of organic matter DW', default=0.4_rk)`

### `cDaySumVegMin` [day of the year] *Parameters*
- DESC: earliest start of growing season date
- Source: macrophytes.F90 (118)
- Formula (d⁻¹): `1.0_rk`
- Code: `call self%get_parameter(self%cDaySumVegMin, 'cDaySumVegMin', 'day of the year', 'earliest start of growing season date', default=1.0_rk)`

### `cDayWinVeg` [day of the year] *Parameters*
- DESC: end of growing season date
- Source: macrophytes.F90 (117)
- Formula (d⁻¹): `259.0_rk`
- Code: `call self%get_parameter(self%cDayWinVeg, 'cDayWinVeg', 'day of the year', 'end of growing season date', default=259.0_rk)`

### `cDCarrVeg` [gDW/m2] *Parameters*
- DESC: carrying capacity
- Source: macrophytes.F90 (101)
- Formula (d⁻¹): `300.0_rk`
- Code: `call self%get_parameter(self%cDCarrVeg, 'cDCarrVeg', 'gDW/m2', 'carrying capacity', default=300.0_rk)`

### `cDLayerVeg` [gD/m2] *Parameters*
- DESC: biomass of a single layer of floating leaves
- Source: macrophytes.F90 (124)
- Formula (d⁻¹): `0.0_rk`
- Code: `call self%get_parameter(self%cDLayerVeg, 'cDLayerVeg', 'gD/m2', 'biomass of a single layer of floating leaves', default=0.0_rk)`

### `cDVegIn` [gDW/m2] *Parameters*
- DESC: external macrophyte density
- Source: macrophytes.F90 (99)
- Formula (d⁻¹): `1.0_rk`
- Code: `call self%get_parameter(self%cDVegIn, 'cDVegIn', 'gDW/m2', 'external macrophyte density', default=1.0_rk)`

### `cDVegMin` [gDW/m2] *Parameters*
- DESC: minimum dry weight
- Source: macrophytes.F90 (102)
- Formula (d⁻¹): `0.00001_rk`
- Code: `call self%get_parameter(self%cDVegMin, 'cDVegMin', 'gDW/m2', 'minimum dry weight', default=0.00001_rk)`

### `cExtSpVeg` [m2/gDW] *Parameters*
- DESC: specific extinction
- Source: macrophytes.F90 (131)
- Formula (d⁻¹): `0.0035_rk`
- Code: `call self%get_parameter(self%cExtSpVeg, 'cExtSpVeg', 'm2/gDW', 'specific extinction', default=0.0035_rk)`

### `cHeightVeg` [m] *Parameters*
- DESC: macrophyte height
- Source: macrophytes.F90 (130)
- Formula (d⁻¹): `0.5_rk`
- Code: `call self%get_parameter(self%cHeightVeg, 'cHeightVeg', 'm', 'macrophyte height', default=0.5_rk)`

### `cLengAllo` [d] *Parameters*
- DESC: duration of allocation and reallocation phase
- Source: macrophytes.F90 (119)
- Formula (d⁻¹): `15.0_rk`
- Code: `call self%get_parameter(self%cLengAllo, 'cLengAllo', 'd', 'duration of allocation and reallocation phase', default=15.0_rk)`

### `cLengMort` [d] *Parameters*
- DESC: length of shoot mortality period
- Source: macrophytes.F90 (127)
- Formula (d⁻¹): `15.0_rk`
- Code: `call self%get_parameter(self%cLengMort, 'cLengMort', 'd', 'length of shoot mortality period', default=15.0_rk)`

### `cMuMaxVeg` [1/d] *Parameters*
- DESC: maximum growth rate at 20*C
- Source: macrophytes.F90 (115)
- Formula (d⁻¹): `0.08_rk`
- Code: `call self%get_parameter(self%cMuMaxVeg, 'cMuMaxVeg', '1/d', 'maximum growth rate at 20*C', default=0.08_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cNDVeg0` [gN/gDW] *Parameters*
- DESC: reference N fraction in external veg
- Source: macrophytes.F90 (149)
- Formula (d⁻¹): `0.02_rk`
- Code: `call self%get_parameter(self%cNDVeg0, 'cNDVeg0', 'gN/gDW', 'reference N fraction in external veg', default=0.02_rk)`

### `cNDVegMax` [mgN/mgDW] *Parameters*
- DESC: maximum N/DW ratio
- Source: macrophytes.F90 (140)
- Formula (d⁻¹): `0.035_rk`
- Code: `call self%get_parameter(self%cNDVegMax, 'cNDVegMax', 'mgN/mgDW', 'maximum N/DW ratio', default=0.035_rk)`

### `cNDVegMin` [mgN/mgDW] *Parameters*
- DESC: minimum N/DW ratio
- Source: macrophytes.F90 (139)
- Formula (d⁻¹): `0.01_rk`
- Code: `call self%get_parameter(self%cNDVegMin, 'cNDVegMin', 'mgN/mgDW', 'minimum N/DW ratio', default=0.01_rk)`

### `cPDVeg0` [gP/gDW] *Parameters*
- DESC: reference P fraction in external veg
- Source: macrophytes.F90 (148)
- Formula (d⁻¹): `0.002_rk`
- Code: `call self%get_parameter(self%cPDVeg0, 'cPDVeg0', 'gP/gDW', 'reference P fraction in external veg', default=0.002_rk)`

### `cPDVegMax` [mgP/mgDW] *Parameters*
- DESC: maximum P/DW ratio
- Source: macrophytes.F90 (142)
- Formula (d⁻¹): `0.004_rk`
- Code: `call self%get_parameter(self%cPDVegMax, 'cPDVegMax', 'mgP/mgDW', 'maximum P/DW ratio', default=0.004_rk)`

### `cPDVegMin` [mgP/mg] *Parameters*
- DESC: minimum P/DW ratio
- Source: macrophytes.F90 (141)
- Formula (d⁻¹): `0.001_rk`
- Code: `call self%get_parameter(self%cPDVegMin, 'cPDVegMin', 'mgP/mg', 'minimum P/DW ratio', default=0.001_rk)`

### `cQ10ProdVeg` [-] *Parameters*
- DESC: temperature q10 of growth
- Source: macrophytes.F90 (134)
- Formula (d⁻¹): `1.2_rk`
- Code: `call self%get_parameter(self%cQ10ProdVeg, 'cQ10ProdVeg', '-', 'temperature q10 of growth', default=1.2_rk)`

### `cQ10RespVeg` [-] *Parameters*
- DESC: temperature q10 of respiration
- Source: macrophytes.F90 (135)
- Formula (d⁻¹): `2.0_rk`
- Code: `call self%get_parameter(self%cQ10RespVeg, 'cQ10RespVeg', '-', 'temperature q10 of respiration', default=2.0_rk)`

### `cSigTmVeg` [*C] *Parameters*
- DESC: lGausVeg = .true.; temp. const.; sigma in Gaussian curve
- Source: macrophytes.F90 (136)
- Formula (d⁻¹): `20.0_rk`
- Code: `call self%get_parameter(self%cSigTmVeg, 'cSigTmVeg', '*C', 'lGausVeg = .true.; temp. const.; sigma in Gaussian curve', default=20.0_rk)`

### `cTmInitVeg` [*C] *Parameters*
- DESC: temperature for onset of initial growth
- Source: macrophytes.F90 (133)
- Formula (d⁻¹): `9.0_rk`
- Code: `call self%get_parameter(self%cTmInitVeg, 'cTmInitVeg', '*C', 'temperature for onset of initial growth', default=9.0_rk)`

### `cTmOptVeg` [*C] *Parameters*
- DESC: lGausVeg = .true.; optimum temperature
- Source: macrophytes.F90 (137)
- Formula (d⁻¹): `20.0_rk`
- Code: `call self%get_parameter(self%cTmOptVeg, 'cTmOptVeg', '*C', 'lGausVeg = .true.; optimum temperature', default=20.0_rk)`

### `cVNUptMaxVeg` [mgN/mgDW/d] *Parameters*
- DESC: N uptake capacity at 20*C
- Source: macrophytes.F90 (111)
- Formula (d⁻¹): `0.1_rk`
- Code: `call self%get_parameter(self%cVNUptMaxVeg, 'cVNUptMaxVeg', 'mgN/mgDW/d', 'N uptake capacity at 20*C', default=0.1_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cVPUptMaxVeg` [mgP/mgDW/d] *Parameters*
- DESC: P uptake capacity at 20*C
- Source: macrophytes.F90 (113)
- Formula (d⁻¹): `0.01_rk`
- Code: `call self%get_parameter(self%cVPUptMaxVeg, 'cVPUptMaxVeg', 'mgP/mgDW/d', 'P uptake capacity at 20*C', default=0.01_rk, scale_factor=1.0_rk/secs_pr_day)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: macrophytes.F90 (153)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fDissMortVeg` [-] *Parameters*
- DESC: dissolved inorganic nutrient fraction of dead plants
- Source: macrophytes.F90 (143)
- Formula (d⁻¹): `0.25_rk`
- Code: `call self%get_parameter(self%fDissMortVeg, 'fDissMortVeg', '-', 'dissolved inorganic nutrient fraction of dead plants', default=0.25_rk)`

### `fEmergVeg` [gfloating/gshoot] *Parameters*
- DESC: emergent fraction of shoot
- Source: macrophytes.F90 (122)
- Formula (d⁻¹): `0.0_rk`
- Code: `call self%get_parameter(self%fEmergVeg, 'fEmergVeg', 'gfloating/gshoot', 'emergent fraction of shoot', default=0.0_rk)`

### `fFloatVeg` [gfloating/gshoot] *Parameters*
- DESC: floating fraction of shoot
- Source: macrophytes.F90 (123)
- Formula (d⁻¹): `0.0_rk`
- Code: `call self%get_parameter(self%fFloatVeg, 'fFloatVeg', 'gfloating/gshoot', 'floating fraction of shoot', default=0.0_rk)`

### `fRootVegSum` [groot/gveg] *Parameters*
- DESC: root fraction during growing season
- Source: macrophytes.F90 (121)
- Formula (d⁻¹): `0.1_rk`
- Code: `call self%get_parameter(self%fRootVegSum, 'fRootVegSum', 'groot/gveg', 'root fraction during growing season', default=0.1_rk)`

### `fRootVegWin` [groot/gveg] *Parameters*
- DESC: root fraction outside of growing season
- Source: macrophytes.F90 (120)
- Formula (d⁻¹): `0.6_rk`
- Code: `call self%get_parameter(self%fRootVegWin, 'fRootVegWin', 'groot/gveg', 'root fraction outside of growing season', default=0.6_rk)`

### `fSedUptVegCoef` [-] *Parameters*
- DESC: lEmpUpt = .true.; sediment nutrient fraction sigma
- Source: macrophytes.F90 (108)
- Formula (d⁻¹): `2.66_rk`
- Code: `call self%get_parameter(self%fSedUptVegCoef,'fSedUptVegCoef','-', 'lEmpUpt = .true.; sediment nutrient fraction sigma', default=2.66_rk)`

### `fSedUptVegExp` [-] *Parameters*
- DESC: lEmpUpt = .true.; sediment nutrient fraction exp.
- Source: macrophytes.F90 (109)
- Formula (d⁻¹): `-0.83_rk`
- Code: `call self%get_parameter(self%fSedUptVegExp, 'fSedUptVegExp', '-', 'lEmpUpt = .true.; sediment nutrient fraction exp.', default=-0.83_rk)`

### `fSedUptVegMax` [-] *Parameters*
- DESC: lEmpUpt = .true.; max. sediment nutrient fraction
- Source: macrophytes.F90 (107)
- Formula (d⁻¹): `0.5_rk`
- Code: `call self%get_parameter(self%fSedUptVegMax, 'fSedUptVegMax', '-', 'lEmpUpt = .true.; max. sediment nutrient fraction', default=0.5_rk)`

### `fTOMWMortVeg` [-] *Parameters*
- DESC: organic matter fraction of dead shoots to sediment
- Source: macrophytes.F90 (145)
- Formula (d⁻¹): `0.1_rk`
- Code: `call self%get_parameter(self%fTOMWMortVeg, 'fTOMWMortVeg', '-', 'organic matter fraction of dead shoots to sediment', default=0.1_rk)`

### `fVegDOMS` [-] *Parameters*
- DESC: dissolved organic matter fraction of dead roots
- Source: macrophytes.F90 (146)
- Formula (d⁻¹): `0.0_rk`
- Code: `call self%get_parameter(self%fVegDOMS, 'fVegDOMS', '-', 'dissolved organic matter fraction of dead roots', default=0.0_rk)`

### `fVegDOMW` [-] *Parameters*
- DESC: dissolved organic matter fraction of dead shoots
- Source: macrophytes.F90 (147)
- Formula (d⁻¹): `0.0_rk`
- Code: `call self%get_parameter(self%fVegDOMW, 'fVegDOMW', '-', 'dissolved organic matter fraction of dead shoots', default=0.0_rk)`

### `fWinVeg` [-] *Parameters*
- DESC: fraction surviving outside of growing season
- Source: macrophytes.F90 (128)
- Formula (d⁻¹): `0.3_rk`
- Code: `call self%get_parameter(self%fWinVeg, 'fWinVeg', '-', 'fraction surviving outside of growing season', default=0.3_rk)`

### `hLRefVeg` [W/m2] *Parameters*
- DESC: half-saturation PAR of macrophyte growth at 20*C
- Source: macrophytes.F90 (104)
- Formula (d⁻¹): `17.0_rk`
- Code: `call self%get_parameter(self%hLRefVeg, 'hLRefVeg', 'W/m2', 'half-saturation PAR of macrophyte growth at 20*C', default=17.0_rk)`

### `hO2BOD` [mgO2/l] *Parameters*
- DESC: half-saturation constant for oxygen conc. on BOD
- Source: macrophytes.F90 (129)
- Formula (d⁻¹): `1.0_rk`
- Code: `call self%get_parameter(self%hO2BOD, 'hO2BOD', 'mgO2/l', 'half-saturation constant for oxygen conc. on BOD', default=1.0_rk)`

### `kDRespVeg` [1/d] *Parameters*
- DESC: dark respiration rate at 20*C
- Source: macrophytes.F90 (116)
- Formula (d⁻¹): `0.02_rk`
- Code: `call self%get_parameter(self%kDRespVeg, 'kDRespVeg', '1/d', 'dark respiration rate at 20*C', default=0.02_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMigrVeg` [1/d] *Parameters*
- DESC: macrophytes immigration rate
- Source: macrophytes.F90 (100)
- Formula (d⁻¹): `0.001_rk`
- Code: `call self%get_parameter(self%kMigrVeg, 'kMigrVeg', '1/d', 'macrophytes immigration rate', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortVegSum` [1/d] *Parameters*
- DESC: mortality rate during growing season
- Source: macrophytes.F90 (126)
- Formula (d⁻¹): `0.005_rk`
- Code: `call self%get_parameter(self%kMortVegSum, 'kMortVegSum', '1/d', 'mortality rate during growing season', default=0.005_rk, scale_factor=1.0_rk/secs_pr_day)`

### `lCarrVeg` [-] *Parameters*
- DESC: toggle carrying capacity
- Source: macrophytes.F90 (150)
- Formula (d⁻¹): `.true.`
- Code: `call self%get_parameter(self%lCarrVeg, 'lCarrVeg', '-', 'toggle carrying capacity', default=.true.)`

### `lEmpUpt` [-] *Parameters*
- DESC: toggle empirical relat. for sed. fract. of nut. upt.
- Source: macrophytes.F90 (106)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%lEmpUpt, 'lEmpUpt', '-', 'toggle empirical relat. for sed. fract. of nut. upt.', default=.false.)`

### `lGausVeg` [-] *Parameters*
- DESC: toggle gaussian temperature modifier
- Source: macrophytes.F90 (151)
- Formula (d⁻¹): `.false.`
- Code: `call self%get_parameter(self%lGausVeg, 'lGausVeg', '-', 'toggle gaussian temperature modifier', default=.false.)`

### `nCompts` [-] *Parameters*
- DESC: number of macrophyte competitors
- Source: macrophytes.F90 (98)
- Formula (d⁻¹): `0`
- Code: `call self%get_parameter(self%nCompts, 'nCompts', '-', 'number of macrophyte competitors', default=0)`

### `cAggr` [m3/gDW/d] *Parameters*
- DESC: intraspecific aggresion level
- Source: fish.F90 (128)
- Formula (d⁻¹): `call self%get_parameter(self%cAggr,'cAggr','m3/gDW/d',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cAggr, 'cAggr', 'm3/gDW/d', 'intraspecific aggresion level', default=0.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cCDRef` [gC/gDW] *Parameters*
- DESC: reference C/DW ratio of fish
- Source: fish.F90 (189)
- Formula (d⁻¹): `call self%get_parameter(self%cCDRef,'cCDRef','gC/gDW',...,default=0.45_rk)`
- Code: `call self%get_parameter(self%cCDRef, 'cCDRef', 'gC/gDW', 'reference C/DW ratio of fish', default=0.45_rk)`

### `cClearBent` [m2/gDW/d] *Parameters*
- DESC: clearance rate for benthos prey
- Source: fish.F90 (156)
- Formula (d⁻¹): `call self%get_parameter(self%cClearBent(i_prey),'cClearBent'//trim(index),'m2/gDW/d',...,default=0.06_rk)`
- Code: `call self%get_parameter(self%cClearBent(i_prey),'cClearBent'//trim(index),'m2/gDW/d','clearance rate for benthos prey '//trim(index), default=0.06_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cClearPisc` [m3/gDW/d] *Parameters*
- DESC: clearance rate for fish prey
- Source: fish.F90 (167)
- Formula (d⁻¹): `call self%get_parameter(self%cClearPisc(i_prey),'cClearPisc'//trim(index),'m3/gDW/d',...,default=0.021_rk)`
- Code: `call self%get_parameter(self%cClearPisc(i_prey),'cClearPisc'//trim(index),'m3/gDW/d','clearance rate for fish prey '//trim(index), default=0.021_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cClearPlan` [m3/gDW/d] *Parameters*
- DESC: clearance rate for plankton prey
- Source: fish.F90 (143)
- Formula (d⁻¹): `call self%get_parameter(self%cClearPlan(i_prey),'cClearPlan'//trim(index),'m3/gDW/d',...,default=0.24_rk)`
- Code: `call self%get_parameter(self%cClearPlan(i_prey),'cClearPlan'//trim(index),'m3/gDW/d','clearance rate for plankton prey '//trim(index), default=0.24_rk, scale_factor=1.0_rk/secs_pr_day)`

### `cDayReprFish` [day-of-year] *Parameters*
- DESC: qStage = 1 or 3; reproduction date
- Source: fish.F90 (119)
- Formula (d⁻¹): `call self%get_parameter(self%cDayReprFish,'cDayReprFish','day-of-year',...,default=120.0_rk)`
- Code: `call self%get_parameter(self%cDayReprFish, 'cDayReprFish', 'day-of-year', 'qStage = 1 or 3; reproduction date', default=120.0_rk)`

### `cDegg` [gDW] *Parameters*
- DESC: hatching size
- Source: fish.F90 (122)
- Formula (d⁻¹): `call self%get_parameter(self%cDegg,'cDegg','gDW',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cDegg, 'cDegg', 'gDW', 'hatching size', default=0.0_rk)`

### `cDFiIn` [gDW/m3] *Parameters*
- DESC: external density
- Source: fish.F90 (100)
- Formula (d⁻¹): `call self%get_parameter(self%cDFiIn,'cDFiIn','gDW/m3','external density',default=0.005_rk)`
- Code: `call self%get_parameter(self%cDFiIn, 'cDFiIn', 'gDW/m3', 'external density', default=0.005_rk)`

### `cDFiMin` [gDW/m3] *Parameters*
- DESC: minimum DW density
- Source: fish.F90 (108)
- Formula (d⁻¹): `call self%get_parameter(self%cDFiMin,'cDFiMin','gDW/m3',...,default=0.0001_rk)`
- Code: `call self%get_parameter(self%cDFiMin, 'cDFiMin', 'gDW/m3', 'minimum DW density', default=0.0001_rk)`

### `cDfin` [gDW] *Parameters*
- DESC: final individual dry weight of stage
- Source: fish.F90 (116)
- Formula (d⁻¹): `call self%get_parameter(self%cDfin,'cDfin','gDW',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cDfin, 'cDfin', 'gDW', 'final individual dry weight of stage', default=0.0_rk)`

### `cDinit` [gDW] *Parameters*
- DESC: initial individual dry weight of stage
- Source: fish.F90 (115)
- Formula (d⁻¹): `call self%get_parameter(self%cDinit,'cDinit','gDW',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cDinit, 'cDinit', 'gDW', 'initial individual dry weight of stage', default=0.0_rk)`

### `cMaxLight` [W/m2] *Parameters*
- DESC: qtrans = 3; light level triggering downwards swimming
- Source: fish.F90 (105)
- Formula (d⁻¹): `call self%get_parameter(self%cMaxLight,'cMaxLight','W/m2',...,default=40.0_rk)`
- Code: `call self%get_parameter(self%cMaxLight, 'cMaxLight', 'W/m2', 'qtrans = 3; light level triggering downwards swimming', default=40.0_rk)`

### `cMinLight` [W/m2] *Parameters*
- DESC: qTrans = 3; light level triggering upwards swimming
- Source: fish.F90 (104)
- Formula (d⁻¹): `call self%get_parameter(self%cMinLight,'cMinLight','W/m2',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%cMinLight, 'cMinLight', 'W/m2', 'qTrans = 3; light level triggering upwards swimming', default=1.0_rk)`

### `cMinO2` [gO2/m3] *Parameters*
- DESC: qtrans >= 2; oxygen conc. limit
- Source: fish.F90 (103)
- Formula (d⁻¹): `call self%get_parameter(self%cMinO2,'cMinO2','gO2/m3',...,default=2.0_rk)`
- Code: `call self%get_parameter(self%cMinO2, 'cMinO2', 'gO2/m3', 'qtrans >= 2; oxygen conc. limit', default=2.0_rk)`

### `cMortStarv` [-] *Parameters*
- DESC: starvation mortality proportionality constant
- Source: fish.F90 (114)
- Formula (d⁻¹): `call self%get_parameter(self%cMortStarv,'cMortStarv','-',...,default=0.2_rk)`
- Code: `call self%get_parameter(self%cMortStarv, 'cMortStarv', '-', 'starvation mortality proportionality constant', default=0.2_rk)`

### `cNDRef` [gN/gDW] *Parameters*
- DESC: reference N/DW ratio of fish
- Source: fish.F90 (188)
- Formula (d⁻¹): `call self%get_parameter(self%cNDRef,'cNDRef','gN/gDW',...,default=0.1_rk)`
- Code: `call self%get_parameter(self%cNDRef, 'cNDRef', 'gN/gDW', 'reference N/DW ratio of fish', default=0.1_rk)`

### `cPDRef` [gP/gDW] *Parameters*
- DESC: reference P/DW ratio of fish
- Source: fish.F90 (187)
- Formula (d⁻¹): `call self%get_parameter(self%cPDRef,'cPDRef','gP/gDW',...,default=0.022_rk)`
- Code: `call self%get_parameter(self%cPDRef, 'cPDRef', 'gP/gDW', 'reference P/DW ratio of fish', default=0.022_rk)`

### `cRelVegBent` [-] *Parameters*
- DESC: decrease of fish feeding per macrophytes cover; max. 0.01
- Source: fish.F90 (177)
- Formula (d⁻¹): `call self%get_parameter(self%cRelVegBent,'cRelVegBent','-',...,default=0.009_rk)`
- Code: `call self%get_parameter(self%cRelVegBent, 'cRelVegBent', '-', 'decrease of fish feeding per macrophytes cover; max. 0.01', default=0.009_rk)`

### `cRelVegPlan` [-] *Parameters*
- DESC: decrease of fish feeding per macrophytes cover; max. 0.01
- Source: fish.F90 (178)
- Formula (d⁻¹): `call self%get_parameter(self%cRelVegPlan,'cRelVegPlan','-',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cRelVegPlan, 'cRelVegPlan', '-', 'decrease of fish feeding per macrophytes cover; max. 0.01', default=0.0_rk)`

### `cSigTmFish` [*C] *Parameters*
- DESC: temperature constant of fish; sigma in Gaussian curve
- Source: fish.F90 (193)
- Formula (d⁻¹): `call self%get_parameter(self%cSigTmFish,'cSigTmFish','*C',...,default=10.0_rk)`
- Code: `call self%get_parameter(self%cSigTmFish, 'cSigTmFish', '*C', 'temperature constant of fish; sigma in Gaussian curve', default=10.0_rk)`

### `cTmOptFish` [*C] *Parameters*
- DESC: optimal temperature of fish
- Source: fish.F90 (192)
- Formula (d⁻¹): `call self%get_parameter(self%cTmOptFish,'cTmOptFish','*C',...,default=25.0_rk)`
- Code: `call self%get_parameter(self%cTmOptFish, 'cTmOptFish', '*C', 'optimal temperature of fish', default=25.0_rk)`

### `cVswim` [m/d] *Parameters*
- DESC: qTrans > 1; vertical migration speed
- Source: fish.F90 (106)
- Formula (d⁻¹): `call self%get_parameter(self%cVswim,'cVswim','m/d',...,default=10.0_rk)`
- Code: `call self%get_parameter(self%cVswim, 'cVswim', 'm/d', 'qTrans > 1; vertical migration speed', default=10.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: fish.F90 (195)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics,'diagnostics','-',...,default=.false.)`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fDAssFi` [-] *Parameters*
- DESC: C assimilation efficiency of fish
- Source: fish.F90 (173)
- Formula (d⁻¹): `call self%get_parameter(self%fDAssFi,'fDAssFi','-',...,default=0.4_rk)`
- Code: `call self%get_parameter(self%fDAssFi, 'fDAssFi', '-', 'C assimilation efficiency of fish', default=0.4_rk)`

### `fDBone` [-] *Parameters*
- DESC: fraction of fish C fixed in bones and scales
- Source: fish.F90 (183)
- Formula (d⁻¹): `call self%get_parameter(self%fDBone,'fDBone','-',...,default=0.35_rk)`
- Code: `call self%get_parameter(self%fDBone, 'fDBone', '-', 'fraction of fish C fixed in bones and scales', default=0.35_rk)`

### `fDissEgesFish` [-] *Parameters*
- DESC: soluble inorg. nut. frac. of fish egested food
- Source: fish.F90 (185)
- Formula (d⁻¹): `call self%get_parameter(self%fDissEgesFish,'fDissEgesFish','-',...,default=0.25_rk)`
- Code: `call self%get_parameter(self%fDissEgesFish, 'fDissEgesFish', '-', 'soluble inorg. nut. frac. of fish egested food', default=0.25_rk)`

### `fDissMortFish` [-] *Parameters*
- DESC: soluble inorg. nut. frac. of dead fish; excl. bones & scales
- Source: fish.F90 (186)
- Formula (d⁻¹): `call self%get_parameter(self%fDissMortFish,'fDissMortFish','-',...,default=0.1_rk)`
- Code: `call self%get_parameter(self%fDissMortFish, 'fDissMortFish', '-', 'soluble inorg. nut. frac. of dead fish; excl. bones & scales', default=0.1_rk)`

### `fDRespActFi` [-] *Parameters*
- DESC: additional feeding respiration as fraction of kDRespFi
- Source: fish.F90 (175)
- Formula (d⁻¹): `call self%get_parameter(self%fDRespActFi,'fDRespActFi','-',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%fDRespActFi, 'fDRespActFi', '-', 'additional feeding respiration as fraction of kDRespFi', default=1.0_rk)`

### `fFC` [-] *Parameters*
- DESC: feeding efficiency in refuge relative to arena
- Source: fish.F90 (130-134)
- Formula (d⁻¹): `call self%get_parameter(self%fFC,'fFC','-',...,default=1.0_rk_or_0.0_rk)`
- Code: `call self%get_parameter(self%fFC, 'fFC', '-', 'feeding efficiency in refuge relative to arena', default=1.0_rk) [qOPT=0] or default=0.0_rk [qOPT=1]`

### `fFiDOMW` [-] *Parameters*
- DESC: dissolved organic matter fraction from fish
- Source: fish.F90 (190)
- Formula (d⁻¹): `call self%get_parameter(self%fFiDOMW,'fFiDOMW','-',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fFiDOMW, 'fFiDOMW', '-', 'dissolved organic matter fraction from fish', default=0.5_rk)`

### `fGonad` [-] *Parameters*
- DESC: maximum gonad fraction of reserve biomass
- Source: fish.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%fGonad,'fGonad','-',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%fGonad, 'fGonad', '-', 'maximum gonad fraction of reserve biomass', default=0.0_rk)`

### `fGutOccBent` [-] *Parameters*
- DESC: gut occupation factor for benthos prey
- Source: fish.F90 (157)
- Formula (d⁻¹): `call self%get_parameter(self%fGutOccBent(i_prey),'fGutOccBent'//trim(index),'-',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%fGutOccBent(i_prey),'fGutOccBent'//trim(index),'-','gut occupation factor for benthos prey '//trim(index),default=1.0_rk)`

### `fGutOccPisc` [-] *Parameters*
- DESC: gut occupation factor for fish prey
- Source: fish.F90 (168)
- Formula (d⁻¹): `call self%get_parameter(self%fGutOccPisc(i_prey),'fGutOccPisc'//trim(index),'-',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%fGutOccPisc(i_prey),'fGutOccPisc'//trim(index),'-','gut occupation factor for fish prey '//trim(index),default=1.0_rk)`

### `fGutOccPlan` [-] *Parameters*
- DESC: gut occupation factor for plankton prey
- Source: fish.F90 (144)
- Formula (d⁻¹): `call self%get_parameter(self%fGutOccPlan(i_prey),'fGutOccPlan'//trim(index),'-',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%fGutOccPlan(i_prey),'fGutOccPlan'//trim(index),'-','gut occupation factor for plankton prey '//trim(index),default=1.0_rk)`

### `fPBone` [-] *Parameters*
- DESC: fraction of fish P fixed in bones and scales
- Source: fish.F90 (184)
- Formula (d⁻¹): `call self%get_parameter(self%fPBone,'fPBone','-',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fPBone, 'fPBone', '-', 'fraction of fish P fixed in bones and scales', default=0.5_rk)`

### `fPV` [-] *Parameters*
- DESC: predation vulnerability in refuge relative to arena
- Source: fish.F90 (131-134)
- Formula (d⁻¹): `call self%get_parameter(self%fPV,'fPV','-',...,default=1.0_rk_or_0.0_rk)`
- Code: `call self%get_parameter(self%fPV, 'fPV', '-', 'predation vulnerability in refuge relative to arena', default=1.0_rk) [qOPT=0] or default=0.0_rk [qOPT=1]`

### `fReproFish` [-] *Parameters*
- DESC: reproductive conversion efficiency
- Source: fish.F90 (120)
- Formula (d⁻¹): `call self%get_parameter(self%fReproFish,'fReproFish','-',...,default=0.01_rk)`
- Code: `call self%get_parameter(self%fReproFish, 'fReproFish', '-', 'reproductive conversion efficiency', default=0.01_rk)`

### `fResMax` [-] *Parameters*
- DESC: maximum reserve fraction of total biomass
- Source: fish.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%fResMax,'fResMax','-',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fResMax, 'fResMax', '-', 'maximum reserve fraction of total biomass', default=0.5_rk)`

### `fResMin` [-] *Parameters*
- DESC: minimum reserve fraction of total biomass
- Source: fish.F90 (113)
- Formula (d⁻¹): `call self%get_parameter(self%fResMin,'fResMin','-',...,default=0.16_rk)`
- Code: `call self%get_parameter(self%fResMin, 'fResMin', '-', 'minimum reserve fraction of total biomass', default=0.16_rk)`

### `hDVegGrowth` [g/m2] *Parameters*
- DESC: lVegOpt = .true.; half-saturation macrophyte density for growth
- Source: fish.F90 (180)
- Formula (d⁻¹): `call self%get_parameter(self%hDVegGrowth,'hDVegGrowth','g/m2',...,default=0.015_rk)`
- Code: `call self%get_parameter(self%hDVegGrowth, 'hDVegGrowth', 'g/m2', 'lVegOpt = .true.; half-saturation macrophyte density for growth', default=0.015_rk)`

### `kDConsMax` [gDW/gDW/d] *Parameters*
- DESC: standard dry weight specific maximum consumption rate
- Source: fish.F90 (172)
- Formula (d⁻¹): `call self%get_parameter(self%kDConsMax,'kDConsMax','gDW/gDW/d',...,default=0.25_rk)`
- Code: `call self%get_parameter(self%kDConsMax, 'kDConsMax', 'gDW/gDW/d', 'standard dry weight specific maximum consumption rate', default=0.25_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kDRespFi` [1/d] *Parameters*
- DESC: maintenance respiration constant of fish at 20*C
- Source: fish.F90 (174)
- Formula (d⁻¹): `call self%get_parameter(self%kDRespFi,'kDRespFi','1/d',...,default=0.01_rk)`
- Code: `call self%get_parameter(self%kDRespFi, 'kDRespFi', '1/d', 'maintenance respiration constant of fish at 20*C', default=0.01_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMigrFish` [1/d] *Parameters*
- DESC: fish migration rate
- Source: fish.F90 (99)
- Formula (d⁻¹): `call self%get_parameter(self%kMigrFish,'kMigrFish','1/d','fish migration rate',default=0.001_rk)`
- Code: `call self%get_parameter(self%kMigrFish, 'kMigrFish', '1/d', 'fish migration rate', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortFi` [1/d] *Parameters*
- DESC: specific mortality of fish
- Source: fish.F90 (176)
- Formula (d⁻¹): `call self%get_parameter(self%kMortFi,'kMortFi','1/d',...,default=0.001_rk)`
- Code: `call self%get_parameter(self%kMortFi, 'kMortFi', '1/d', 'specific mortality of fish', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kTurbFish` [g/gDW/d] *Parameters*
- DESC: relative resuspension by fish bentivory
- Source: fish.F90 (153)
- Formula (d⁻¹): `call self%get_parameter(self%kTurbFish,'kTurbFish','g/gDW/d',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%kTurbFish, 'kTurbFish', 'g/gDW/d', 'relative resuspension by fish bentivory', default=1.0_rk)`

### `lAggr` [-] *Parameters*
- DESC: toggle intraspecific aggresion
- Source: fish.F90 (127)
- Formula (d⁻¹): `call self%get_parameter(self%lAggr,'lAggr','-',...,default=.false.)`
- Code: `call self%get_parameter(self%lAggr, 'lAggr', '-', 'toggle intraspecific aggresion', default=.false.)`

### `lNutMeth` [-] *Parameters*
- DESC: toggle fixed stochiometry
- Source: fish.F90 (182)
- Formula (d⁻¹): `call self%get_parameter(self%lNutMeth,'lNutMeth','-',...,default=.false.)`
- Code: `call self%get_parameter(self%lNutMeth, 'lNutMeth', '-', 'toggle fixed stochiometry', default=.false.)`

### `lVegOpt` [-] *Parameters*
- DESC: switch for macrophyte dependence on fish max assimilation
- Source: fish.F90 (179)
- Formula (d⁻¹): `call self%get_parameter(self%lVegOpt,'lVegOpt','-',...,default=.false.)`
- Code: `call self%get_parameter(self%lVegOpt, 'lVegOpt', '-', 'switch for macrophyte dependence on fish max assimilation', default=.false.)`

### `nBENprey` [-] *Parameters*
- DESC: number of benthos prey
- Source: fish.F90 (148)
- Formula (d⁻¹): `call self%get_parameter(self%nBENprey,'nBEN','-',...,default=0)`
- Code: `call self%get_parameter(self%nBENprey, 'nBEN', '-', 'number of benthos prey', default=0)`

### `nPISCprey` [-] *Parameters*
- DESC: number of fish prey
- Source: fish.F90 (161)
- Formula (d⁻¹): `call self%get_parameter(self%nPISCprey,'nPISC','-',...,default=0)`
- Code: `call self%get_parameter(self%nPISCprey, 'nPISC', '-', 'number of fish prey', default=0)`

### `nPLANprey` [-] *Parameters*
- DESC: number of plankton prey
- Source: fish.F90 (136)
- Formula (d⁻¹): `call self%get_parameter(self%nPLANprey,'nPLAN','-',...,default=0)`
- Code: `call self%get_parameter(self%nPLANprey, 'nPLAN', '-', 'number of plankton prey', default=0)`

### `qODB` [-] *Parameters*
- DESC: toggle optimal diet breadth: 0=off; 1=on
- Source: fish.F90 (125)
- Formula (d⁻¹): `call self%get_parameter(self%qODB,'qODB','-',...,default=1)`
- Code: `call self%get_parameter(self%qODB, 'qODB', '-', 'toggle optimal diet breadth: 0=off; 1=on', default=1)`

### `qOPT` [-] *Parameters*
- DESC: toggle optimal behavior: 0=off; 1=on
- Source: fish.F90 (126)
- Formula (d⁻¹): `call self%get_parameter(self%qOPT,'qOPT','-',...,default=0)`
- Code: `call self%get_parameter(self%qOPT, 'qOPT', '-', 'toggle optimal behavior: 0=off; 1=on', default=0)`

### `qStage` [-] *Parameters*
- DESC: stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both
- Source: fish.F90 (110)
- Formula (d⁻¹): `call self%get_parameter(self%qStage,'qStage','-',...,default=0)`
- Code: `call self%get_parameter(self%qStage, 'qStage', '-', 'stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both', default=0)`

### `qTrans` [-] *Parameters*
- DESC: vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light
- Source: fish.F90 (102)
- Formula (d⁻¹): `call self%get_parameter(self%qTrans,'qTrans','-',...,default=2)`
- Code: `call self%get_parameter(self%qTrans, 'qTrans', '-', 'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light', default=2)`

### `BENpref` [-] *Parameters*
- DESC: preference factor for zoobenthos prey
- Source: fish_pclake.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%BENpref(i_prey),'BENpref'//trim(index),'-','preference factor for zoobenthos prey '//trim(index),default=1.0_rk)`
- Code: `call self%get_parameter(self%BENpref(i_prey),  'BENpref'//trim(index), '-',  'preference factor for zoobenthos prey '//trim(index), default=1.0_rk)`

### `cDayAgeFish` [day of the year] *Parameters*
- DESC: qStageOpt = 2 or 3; aging day of year for fish
- Source: fish_pclake.F90 (100)
- Formula (d⁻¹): `call self%get_parameter(self%cDayAgeFish,'cDayAgeFish','day of the year',...,default=360.0_rk,maximum=364.0_rk)`
- Code: `call self%get_parameter(self%cDayAgeFish, 'cDayAgeFish', 'day of the year', 'qStageOpt = 2 or 3; aging day of year for fish ', default=360.0_rk, maximum=364.0_rk)`

### `cDayReprFish` [day of the year] *Parameters*
- DESC: qStageOpt = 1 or 3; reproduction date
- Source: fish_pclake.F90 (98)
- Formula (d⁻¹): `call self%get_parameter(self%cDayReprFish,'cDayReprFish','day of the year',...,default=120.0_rk)`
- Code: `call self%get_parameter(self%cDayReprFish, 'cDayReprFish', 'day of the year', 'qStageOpt = 1 or 3; reproduction date', default=120.0_rk)`

### `cDCarrFish` [gDW/m3] *Parameters*
- DESC: carrying capacity
- Source: fish_pclake.F90 (95)
- Formula (d⁻¹): `call self%get_parameter(self%cDCarrFish,'cDCarrFish','gDW/m3','carrying capacity',default=15.0_rk)`
- Code: `call self%get_parameter(self%cDCarrFish, 'cDCarrFish', 'gDW/m3', 'carrying capacity', default=15.0_rk)`

### `cDFiIn` [gDW/m3] *Parameters*
- DESC: external density
- Source: fish_pclake.F90 (88)
- Formula (d⁻¹): `call self%get_parameter(self%cDFiIn,'cDFiIn','gDW/m3','external density',default=0.005_rk)`
- Code: `call self%get_parameter(self%cDFiIn, 'cDFiIn', 'gDW/m3', 'external density', default=0.005_rk)`

### `cDFiMin` [gDW/m3] *Parameters*
- DESC: minimum DW density
- Source: fish_pclake.F90 (96)
- Formula (d⁻¹): `call self%get_parameter(self%cDFiMin,'cDFiMin','gDW/m3',...,default=0.0001_rk)`
- Code: `call self%get_parameter(self%cDFiMin, 'cDFiMin', 'gDW/m3', 'minimum DW density', default=0.0001_rk)`

### `cMinLight` [W/m2] *Parameters*
- DESC: qTrans = 3; light level triggering downwards swimming
- Source: fish_pclake.F90 (92)
- Formula (d⁻¹): `call self%get_parameter(self%cMinLight,'cMinLight','W/m2',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%cMinLight, 'cMinLight', 'W/m2', 'qTrans = 3; light level triggering downwards swimming', default=1.0_rk)`

### `cMinO2` [gO2/m3] *Parameters*
- DESC: qtrans > 1; oxygen conc. limit
- Source: fish_pclake.F90 (91)
- Formula (d⁻¹): `call self%get_parameter(self%cMinO2,'cMinO2','gO2/m3',...,default=2.0_rk)`
- Code: `call self%get_parameter(self%cMinO2, 'cMinO2', 'gO2/m3', 'qtrans > 1; oxygen conc. limit', default=2.0_rk)`

### `cNDFishRef` [mgN/mgDW] *Parameters*
- DESC: reference N/C ratio of fish
- Source: fish_pclake.F90 (151)
- Formula (d⁻¹): `call self%get_parameter(self%cNDFishRef,'cNDFishRef','mgN/mgDW',...,default=0.1_rk)`
- Code: `call self%get_parameter(self%cNDFishRef, 'cNDFishRef', 'mgN/mgDW', 'reference N/C ratio of fish', default=0.1_rk)`

### `cPDFishRef` [mgP/mgDW] *Parameters*
- DESC: reference P/C ratio of fish
- Source: fish_pclake.F90 (150)
- Formula (d⁻¹): `call self%get_parameter(self%cPDFishRef,'cPDFishRef','mgP/mgDW',...,default=0.022_rk)`
- Code: `call self%get_parameter(self%cPDFishRef, 'cPDFishRef', 'mgP/mgDW', 'reference P/C ratio of fish', default=0.022_rk)`

### `cRelVegBent` [-] *Parameters*
- DESC: decrease of fish feeding per macrophytes cover, max. 0.01
- Source: fish_pclake.F90 (140)
- Formula (d⁻¹): `call self%get_parameter(self%cRelVegBent,'cRelVegBent','-',...,default=0.009_rk)`
- Code: `call self%get_parameter(self%cRelVegBent, 'cRelVegBent', '-', 'decrease of fish feeding per macrophytes cover, max. 0.01', default=0.009_rk)`

### `cRelVegZoo` [-] *Parameters*
- DESC: decrease of fish feeding per macrophytes cover, max. 0.01
- Source: fish_pclake.F90 (141)
- Formula (d⁻¹): `call self%get_parameter(self%cRelVegZoo,'cRelVegZoo','-',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%cRelVegZoo, 'cRelVegZoo', '-', 'decrease of fish feeding per macrophytes cover, max. 0.01', default=0.0_rk)`

### `cSigTmFish` [*C] *Parameters*
- DESC: temperature constant of fish, sigma in Gaussian curve
- Source: fish_pclake.F90 (155)
- Formula (d⁻¹): `call self%get_parameter(self%cSigTmFish,'cSigTmFish','*C',...,default=10.0_rk)`
- Code: `call self%get_parameter(self%cSigTmFish, 'cSigTmFish', '*C', 'temperature constant of fish, sigma in Gaussian curve', default=10.0_rk)`

### `cTmOptFish` [*C] *Parameters*
- DESC: optimal temperature of zoo- and benthivorous fish
- Source: fish_pclake.F90 (154)
- Formula (d⁻¹): `call self%get_parameter(self%cTmOptFish,'cTmOptFish','*C',...,default=25.0_rk)`
- Code: `call self%get_parameter(self%cTmOptFish, 'cTmOptFish', '*C', 'optimal temperature of zoo- and benthivorous fish', default=25.0_rk)`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: fish_pclake.F90 (157)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics,'diagnostics','-',...,default=.false.)`
- Code: `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`

### `fAgeFish` [1/d] *Parameters*
- DESC: qStageOpt = 2 or 3; yearly maturation fraction
- Source: fish_pclake.F90 (101)
- Formula (d⁻¹): `call self%get_parameter(self%fAgeFish,'fAgeFish','1/d',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fAgeFish, 'fAgeFish', '1/d', 'qStageOpt = 2 or 3; yearly maturation fraction', default=0.5_rk, scale_factor=1.0_rk/secs_pr_day)`

### `fDAssFi` [-] *Parameters*
- DESC: C assimilation efficiency of fish
- Source: fish_pclake.F90 (136)
- Formula (d⁻¹): `call self%get_parameter(self%fDAssFi,'fDAssFi','-',...,default=0.4_rk)`
- Code: `call self%get_parameter(self%fDAssFi, 'fDAssFi', '-', 'C assimilation efficiency of fish', default=0.4_rk)`

### `fDBone` [-] *Parameters*
- DESC: fraction of fish C fixed in bones and scales
- Source: fish_pclake.F90 (146)
- Formula (d⁻¹): `call self%get_parameter(self%fDBone,'fDBone','-',...,default=0.35_rk)`
- Code: `call self%get_parameter(self%fDBone, 'fDBone', '-', 'fraction of fish C fixed in bones and scales', default=0.35_rk)`

### `fDissEgesFish` [-] *Parameters*
- DESC: soluble nutrient frac. of fish egested food
- Source: fish_pclake.F90 (148)
- Formula (d⁻¹): `call self%get_parameter(self%fDissEgesFish,'fDissEgesFish','-',...,default=0.25_rk)`
- Code: `call self%get_parameter(self%fDissEgesFish, 'fDissEgesFish', '-', 'soluble nutrient frac. of fish egested food', default=0.25_rk)`

### `fDissMortFish` [-] *Parameters*
- DESC: soluble nutrient frac. of dead fish, excl. bones & scales
- Source: fish_pclake.F90 (149)
- Formula (d⁻¹): `call self%get_parameter(self%fDissMortFish,'fDissMortFish','-',...,default=0.1_rk)`
- Code: `call self%get_parameter(self%fDissMortFish, 'fDissMortFish', '-', 'soluble nutrient frac. of dead fish, excl. bones & scales', default=0.1_rk)`

### `fFiDOMW` [-] *Parameters*
- DESC: dissolved organic matter fraction from fish
- Source: fish_pclake.F90 (152)
- Formula (d⁻¹): `call self%get_parameter(self%fFiDOMW,'fFiDOMW','-',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fFiDOMW, 'fFiDOMW', '-', 'dissolved organic matter fraction from fish', default=0.5_rk)`

### `fFishBen` [-] *Parameters*
- DESC: zoobentivory time fraction
- Source: fish_pclake.F90 (105)
- Formula (d⁻¹): `call self%get_parameter(self%fFishBen,'fFishBen','-',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%fFishBen, 'fFishBen', '-', 'zoobentivory time fraction', default=0.0_rk)`

### `fFishPisc` [-] *Parameters*
- DESC: piscivory time fraction
- Source: fish_pclake.F90 (106)
- Formula (d⁻¹): `call self%get_parameter(self%fFishPisc,'fFishPisc','-',...,default=0.0_rk)`
- Code: `call self%get_parameter(self%fFishPisc, 'fFishPisc', '-', 'piscivory time fraction', default=0.0_rk)`

### `fFishZoo` [-] *Parameters*
- DESC: zooplanktivory time fraction
- Source: fish_pclake.F90 (104)
- Formula (d⁻¹): `call self%get_parameter(self%fFishZoo,'fFishZoo','-',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%fFishZoo, 'fFishZoo', '-', 'zooplanktivory time fraction', default=1.0_rk)`

### `fPBone` [-] *Parameters*
- DESC: fraction of fish P fixed in bones and scales
- Source: fish_pclake.F90 (147)
- Formula (d⁻¹): `call self%get_parameter(self%fPBone,'fPBone','-',...,default=0.5_rk)`
- Code: `call self%get_parameter(self%fPBone, 'fPBone', '-', 'fraction of fish P fixed in bones and scales', default=0.5_rk)`

### `fReprFish` [1/d] *Parameters*
- DESC: qStageOpt = 1 or 3; yearly reproduction fraction
- Source: fish_pclake.F90 (99)
- Formula (d⁻¹): `call self%get_parameter(self%fReprFish,'fReprFish','1/d',...,default=0.02_rk)`
- Code: `call self%get_parameter(self%fReprFish, 'fReprFish', '1/d', 'qStageOpt = 1 or 3; yearly reproduction fraction', default=0.02_rk, scale_factor=1.0_rk/secs_pr_day)`

### `hDBentFi` [g/m2] *Parameters*
- DESC: half-saturation constant for zoobentivory
- Source: fish_pclake.F90 (135)
- Formula (d⁻¹): `call self%get_parameter(self%hDBentFi,'hDBentFi','g/m2',...,default=2.5_rk)`
- Code: `call self%get_parameter(self%hDBentFi, 'hDBentFi', 'g/m2', 'half-saturation constant for zoobentivory', default=2.5_rk)`

### `hDPiscFi` [g/m3] *Parameters*
- DESC: half-saturating DFish for fish predation
- Source: fish_pclake.F90 (139)
- Formula (d⁻¹): `call self%get_parameter(self%hDPiscFi,'hDPiscFi','g/m3',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%hDPiscFi, 'hDPiscFi', 'g/m3', 'half-saturating DFish for fish predation', default=1.0_rk)`

### `hDVegGrowth` [g/m2] *Parameters*
- DESC: lVegOpt = .true.; half-saturation macrophyte density for growth
- Source: fish_pclake.F90 (143)
- Formula (d⁻¹): `call self%get_parameter(self%hDVegGrowth,'hDVegGrowth','g/m2',...,default=0.015_rk)`
- Code: `call self%get_parameter(self%hDVegGrowth, 'hDVegGrowth', 'g/m2', 'lVegOpt = .true.; half-saturation macrophyte density for growth', default=0.015_rk)`

### `hDZooFi` [g/m3] *Parameters*
- DESC: half-saturation zooplankton for zooplanktivory
- Source: fish_pclake.F90 (134)
- Formula (d⁻¹): `call self%get_parameter(self%hDZooFi,'hDZooFi','g/m3',...,default=1.1_rk)`
- Code: `call self%get_parameter(self%hDZooFi, 'hDZooFi', 'g/m3', 'half-saturation zooplankton for zooplanktivory', default=1.1_rk)`

### `kDAssFi` [1/d] *Parameters*
- DESC: maximum assimilation rate of fish at 20*C
- Source: fish_pclake.F90 (133)
- Formula (d⁻¹): `call self%get_parameter(self%kDAssFi,'kDAssFi','1/d',...,default=0.12_rk)`
- Code: `call self%get_parameter(self%kDAssFi, 'kDAssFi', '1/d', 'maximum assimilation rate of fish at 20*C', default=0.12_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kDRespFi` [1/d] *Parameters*
- DESC: maintenance respiration constant of fish at 20*C
- Source: fish_pclake.F90 (137)
- Formula (d⁻¹): `call self%get_parameter(self%kDRespFi,'kDRespFi','1/d',...,default=0.01_rk)`
- Code: `call self%get_parameter(self%kDRespFi, 'kDRespFi', '1/d', 'maintenance respiration constant of fish at 20*C', default=0.01_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMigrFish` [1/d] *Parameters*
- DESC: fish migration rate
- Source: fish_pclake.F90 (87)
- Formula (d⁻¹): `call self%get_parameter(self%kMigrFish,'kMigrFish','1/d','fish migration rate',default=0.001_rk)`
- Code: `call self%get_parameter(self%kMigrFish, 'kMigrFish', '1/d', 'fish migration rate', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kMortFi` [1/d] *Parameters*
- DESC: specific mortality of fish
- Source: fish_pclake.F90 (138)
- Formula (d⁻¹): `call self%get_parameter(self%kMortFi,'kMortFi','1/d',...,default=0.001_rk)`
- Code: `call self%get_parameter(self%kMortFi, 'kMortFi', '1/d', 'specific mortality of fish', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `kTurbFish` [g/gDW/d] *Parameters*
- DESC: relative resuspension by adult fish browsing
- Source: fish_pclake.F90 (117)
- Formula (d⁻¹): `call self%get_parameter(self%kTurbFish,'kTurbFish','g/gDW/d',...,default=1.0_rk)`
- Code: `call self%get_parameter(self%kTurbFish, 'kTurbFish', 'g/gDW/d', 'relative resuspension by adult fish browsing', default=1.0_rk)`

### `lNutMeth` [-] *Parameters*
- DESC: toggle fixed stochiometry
- Source: fish_pclake.F90 (145)
- Formula (d⁻¹): `call self%get_parameter(self%lNutMeth,'lNutMeth','-',...,default=.false.)`
- Code: `call self%get_parameter(self%lNutMeth, 'lNutMeth', '-', 'toggle fixed stochiometry', default=.false.)`

### `lVegOpt` [-] *Parameters*
- DESC: switch for macrophyte dependence on fish max assimilation
- Source: fish_pclake.F90 (142)
- Formula (d⁻¹): `call self%get_parameter(self%lVegOpt,'lVegOpt','-',...,default=.false.)`
- Code: `call self%get_parameter(self%lVegOpt, 'lVegOpt', '-', 'switch for macrophyte dependence on fish max assimilation', default=.false.)`

### `nBENprey` [-] *Parameters*
- DESC: number of zoobenthos prey
- Source: fish_pclake.F90 (116)
- Formula (d⁻¹): `call self%get_parameter(self%nBENprey,'nBEN','-',...,default=0)`
- Code: `call self%get_parameter(self%nBENprey, 'nBEN', '-', 'number of zoobenthos prey', default=0)`

### `nKShares` [-] *Parameters*
- DESC: qStageOpt > 0; # of not-coupled other stages sharing carr. cap.
- Source: fish_pclake.F90 (102)
- Formula (d⁻¹): `call self%get_parameter(self%nKShares,'nKShares','-',...,default=0)`
- Code: `call self%get_parameter(self%nKShares, 'nKShares', '-', 'qStageOpt > 0; # of not-coupled other stages sharing carr. cap.', default=0)`

### `nPISCprey` [-] *Parameters*
- DESC: number of fish prey
- Source: fish_pclake.F90 (125)
- Formula (d⁻¹): `call self%get_parameter(self%nPISCprey,'nPISC','-',...,default=0)`
- Code: `call self%get_parameter(self%nPISCprey, 'nPISC', '-', 'number of fish prey', default=0)`

### `nZOOprey` [-] *Parameters*
- DESC: number of zooplankton prey
- Source: fish_pclake.F90 (108)
- Formula (d⁻¹): `call self%get_parameter(self%nZOOprey,'nZOO','-',...,default=0)`
- Code: `call self%get_parameter(self%nZOOprey, 'nZOO', '-', 'number of zooplankton prey', default=0)`

### `PISCpref` [-] *Parameters*
- DESC: preference factor for fish prey
- Source: fish_pclake.F90 (129)
- Formula (d⁻¹): `call self%get_parameter(self%PISCpref(i_prey),'PISCpref'//trim(index),'-','preference factor for fish prey '//trim(index),default=1.0_rk)`
- Code: `call self%get_parameter(self%PISCpref(i_prey), 'PISCpref'//trim(index), '-', 'preference factor for fish prey '//trim(index), default=1.0_rk)`

### `qStageOpt` [-] *Parameters*
- DESC: stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both
- Source: fish_pclake.F90 (97)
- Formula (d⁻¹): `call self%get_parameter(self%qStageOpt,'qStageOpt','-',...,default=0)`
- Code: `call self%get_parameter(self%qStageOpt, 'qStageOpt', '-', 'stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both', default=0)`

### `qTrans` [-] *Parameters*
- DESC: vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light
- Source: fish_pclake.F90 (90)
- Formula (d⁻¹): `call self%get_parameter(self%qTrans,'qTrans','-',...,default=2)`
- Code: `call self%get_parameter(self%qTrans, 'qTrans', '-', 'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light', default=2)`

### `Vswim` [m/d] *Parameters*
- DESC: qTrans > 1; vertical migration speed
- Source: fish_pclake.F90 (93)
- Formula (d⁻¹): `call self%get_parameter(self%Vswim,'Vswim','m/d',...,default=10.0_rk)`
- Code: `call self%get_parameter(self%Vswim, 'Vswim', 'm/d', 'qTrans > 1; vertical migration speed', default=10.0_rk, scale_factor=1.0_rk/secs_pr_day)`

### `ZOOpref` [-] *Parameters*
- DESC: preference factor for zooplankton prey
- Source: fish_pclake.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%ZOOpref(i_prey),'ZOOpref'//trim(index),'-','preference factor for zooplankton prey '//trim(index),default=1.0_rk)`
- Code: `call self%get_parameter(self%ZOOpref(i_prey),  'ZOOpref'//trim(index), '-', 'preference factor for zooplankton prey '//trim(index), default=1.0_rk)`

### `alpha` [g/m/d] *Parameters*
- DESC: qResus = 2; gross rate of sediment erosion (d-1 original)
- Source: sediment_exchange.F90 (82)
- Formula (d⁻¹): `call self%get_parameter(self%alpha, 'alpha', 'g/m/d', 'qResus = 2; gross rate of sediment erosion', default=9000.0_rk)`
- Code: `call self%get_parameter(self%alpha,        'alpha',        'g/m/d',     'qResus = 2; gross rate of sediment erosion',                     default=9000.0_rk, scale_factor=1.0_rk/secs_pr_day     )`

### `cFetch` [m] *Parameters*
- DESC: qResus = 1; length of water body in prevailing wind direction
- Source: sediment_exchange.F90 (79)
- Formula (d⁻¹): `call self%get_parameter(self%cFetch, 'cFetch', 'm', 'qResus = 1; length of water body in prevailing wind direction', default=1000.0_rk)`
- Code: `call self%get_parameter(self%cFetch,       'cFetch',       'm',         'qResus = 1; length of water body in prevailing wind direction',  default=1000.0_rk                                      )`

### `cFetchRef` [m] *Parameters*
- DESC: qResus = 1; reference fetch
- Source: sediment_exchange.F90 (78)
- Formula (d⁻¹): `call self%get_parameter(self%cFetchRef, 'cFetchRef', 'm', 'qResus = 1; reference fetch', default=1000.0_rk)`
- Code: `call self%get_parameter(self%cFetchRef,    'cFetchRef',    'm',         'qResus = 1; reference fetch',                                    default=1000.0_rk                                      )`

### `crt_shear` [N/m] *Parameters*
- DESC: qResus = 2; critical shear stress
- Source: sediment_exchange.F90 (80)
- Formula (d⁻¹): `call self%get_parameter(self%crt_shear, 'crt_shear', 'N/m', 'qResus = 2; critical shear stress', default=0.02_rk)`
- Code: `call self%get_parameter(self%crt_shear,    'crt_shear',    'N/m',       'qResus = 2; critical shear stress',                              default=0.02_rk                                        )`

### `cSuspMax` [-] *Parameters*
- DESC: qResus = 1; maximum value of logistic function
- Source: sediment_exchange.F90 (75)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspMax, 'cSuspMax', '-', 'qResus = 1; maximum value of logistic function', default=25.2_rk)`
- Code: `call self%get_parameter(self%cSuspMax,     'cSuspMax',     '-',         'qResus = 1; maximum value of logistic function',                 default=25.2_rk                                        )`

### `cSuspMin` [-] *Parameters*
- DESC: qResus = 1; minimum value of logistic function
- Source: sediment_exchange.F90 (74)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspMin, 'cSuspMin', '-', 'qResus = 1; minimum value of logistic function', default=6.1_rk)`
- Code: `call self%get_parameter(self%cSuspMin,     'cSuspMin',     '-',         'qResus = 1; minimum value of logistic function',                 default=6.1_rk                                         )`

### `cSuspRef` [-] *Parameters*
- DESC: qResus = 1; reference suspended matter function
- Source: sediment_exchange.F90 (73)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspRef, 'cSuspRef', '-', 'qResus = 1; reference suspended matter function', default=0.0_rk)`
- Code: `call self%get_parameter(self%cSuspRef,     'cSuspRef',     '-',         'qResus = 1; reference suspended matter function',                default=0.0_rk                                         )`

### `cSuspSlope` [-] *Parameters*
- DESC: qResus = 1; slope of logistic function
- Source: sediment_exchange.F90 (76)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspSlope, 'cSuspSlope', '-', 'qResus = 1; slope of logistic function', default=2.1_rk)`
- Code: `call self%get_parameter(self%cSuspSlope,   'cSuspSlope',   '-',         'qResus = 1; slope of logistic function',                         default=2.1_rk                                         )`

### `cThetaDif` [1/e^*C] *Parameters*
- DESC: temperature coefficient for diffusion
- Source: sediment_exchange.F90 (91)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaDif, 'cThetaDif', '1/e^*C', 'temperature coefficient for diffusion', default=1.016_rk)`
- Code: `call self%get_parameter(self%cThetaDif,    'cThetaDif',    '1/e^*C',    'temperature coefficient for diffusion',                          default=1.016_rk                                       )`

### `cThetaSed` [1/e^*C] *Parameters*
- DESC: temperature coefficient of sedimentation
- Source: sediment_exchange.F90 (87)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaSed, 'cThetaSed', '1/e^*C', 'temperature coefficient of sedimentation', default=1.01_rk)`
- Code: `call self%get_parameter(self%cThetaSed,    'cThetaSed',    '1/e^*C',    'temperature coefficient of sedimentation',                       default=1.01_rk                                        )`

### `cTurbDifNut` [-] *Parameters*
- DESC: bioturbation correction of nutrient diffusion
- Source: sediment_exchange.F90 (92)
- Formula (d⁻¹): `call self%get_parameter(self%cTurbDifNut, 'cTurbDifNut', '-', 'bioturbation correction of nutrient diffusion', default=12.0_rk)`
- Code: `call self%get_parameter(self%cTurbDifNut,  'cTurbDifNut',  '-',         'bioturbation correction of nutrient diffusion',                  default=12.0_rk                                        )`

### `cVSedIM` [m/d] *Parameters*
- DESC: IM sedimentation velocity constant at 20*C
- Source: sediment_exchange.F90 (88)
- Formula (d⁻¹): `call self%get_parameter(self%cVSedIM, 'cVSedIM', 'm/d', 'IM sedimentation velocity constant at 20*C', default=1.0_rk)`
- Code: `call self%get_parameter(self%cVSedIM,      'cVSedIM',      'm/d',       'IM sedimentation velocity constant at 20*C',                     default=1.0_rk                                         )`

### `cVSedPOM` [m/d] *Parameters*
- DESC: POM sedimentation velocity constant at 20*C per group
- Source: sediment_exchange.F90 (108)
- Formula (d⁻¹): `call self%get_parameter(self%cVSedPOM(i_pom), 'cVSedPOM'//trim(index), 'm/d', 'POM sedimentation velocity constant at 20*C '//trim(index), default=0.5_rk)`
- Code: `call self%get_parameter(self%cVSedPOM(i_pom),    'cVSedPOM'//trim(index),    'm/d',  'POM sedimentation velocity constant at 20*C '//trim(index),      default=0.5_rk                        )`

### `cVSedSiPa` [m/d] *Parameters*
- DESC: Si particulate sedimentation velocity constant at 20*C
- Source: sediment_exchange.F90 (89)
- Formula (d⁻¹): `call self%get_parameter(self%cVSedSiPa, 'cVSedSiPa', 'm/d', 'Si particulate sedimentation velocity constant at 20*C', default=0.5_rk)`
- Code: `call self%get_parameter(self%cVSedSiPa,    'cVSedSiPa',    'm/d',       'Si particulate sedimentation velocity constant at 20*C',         default=0.5_rk                                         )`

### `cVSetMain` [m/d] *Parameters*
- DESC: qResus = 2; depth averaged settling velocity (d-1 original)
- Source: sediment_exchange.F90 (84)
- Formula (d⁻¹): `call self%get_parameter(self%cVSetMain, 'cVSetMain', 'm/d', 'qResus = 2; depth averaged settling velocity', default=0.5_rk)`
- Code: `call self%get_parameter(self%cVSetMain,    'cVSetMain',    'm/d',       'qResus = 2; depth averaged settling velocity',                   default=0.5_rk,    scale_factor=1.0_rk/secs_pr_day     )`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: sediment_exchange.F90 (100)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,  'diagnostics',  '-',         'toggle diagnostic output',                                       default=.false.                                        )`

### `eta` [-] *Parameters*
- DESC: qResus = 2; shear stress correction factor
- Source: sediment_exchange.F90 (83)
- Formula (d⁻¹): `call self%get_parameter(self%eta, 'eta', '-', 'qResus = 2; shear stress correction factor', default=1.0_rk)`
- Code: `call self%get_parameter(self%eta,          'eta',          '-',         'qResus = 2; shear stress correction factor',                     default=1.0_rk                                         )`

### `fLutum` [-] *Parameters*
- DESC: lutum fraction of inorganic matter
- Source: sediment_exchange.F90 (85)
- Formula (d⁻¹): `call self%get_parameter(self%fLutum, 'fLutum', '-', 'lutum fraction of inorganic matter', default=0.1_rk)`
- Code: `call self%get_parameter(self%fLutum,       'fLutum',       '-',         'lutum fraction of inorganic matter',                             default=0.1_rk                                         )`

### `fLutumRef` [-] *Parameters*
- DESC: reference lutum fraction of inorganic matter
- Source: sediment_exchange.F90 (86)
- Formula (d⁻¹): `call self%get_parameter(self%fLutumRef, 'fLutumRef', '-', 'reference lutum fraction of inorganic matter', default=0.2_rk)`
- Code: `call self%get_parameter(self%fLutumRef,    'fLutumRef',    '-',         'reference lutum fraction of inorganic matter',                   default=0.2_rk                                         )`

### `hDepthSusp` [-] *Parameters*
- DESC: qResus = 1; half-sat. value of depth in logistic function
- Source: sediment_exchange.F90 (77)
- Formula (d⁻¹): `call self%get_parameter(self%hDepthSusp, 'hDepthSusp', '-', 'qResus = 1; half-sat. value of depth in logistic function', default=2.0_rk)`
- Code: `call self%get_parameter(self%hDepthSusp,   'hDepthSusp',   '-',         'qResus = 1; half-sat. value of depth in logistic function',      default=2.0_rk                                         )`

### `kDDifDOM` [m2/d] *Parameters*
- DESC: DOM diffusion constant DW at 20*C per group (d-1 original)
- Source: sediment_exchange.F90 (119)
- Formula (d⁻¹): `call self%get_parameter(self%kDDifDOM(i_dom), 'kDDifDOM'//trim(index), 'm2/d', 'DOM diffusion constant DW at 20*C '//trim(index), default=0.002_rk)`
- Code: `call self%get_parameter(self%kDDifDOM(i_dom),    'kDDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant DW at 20*C '//trim(index), default=0.002_rk,    scale_factor=1.0_rk/secs_pr_day )`

### `kNDifDOM` [m2/d] *Parameters*
- DESC: DOM diffusion constant N at 20*C per group (d-1 original)
- Source: sediment_exchange.F90 (120)
- Formula (d⁻¹): `call self%get_parameter(self%kNDifDOM(i_dom), 'kNDifDOM'//trim(index), 'm2/d', 'DOM diffusion constant N at 20*C '//trim(index), default=0.000085_rk)`
- Code: `call self%get_parameter(self%kNDifDOM(i_dom),    'kNDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant N at  20*C '//trim(index), default=0.000085_rk, scale_factor=1.0_rk/secs_pr_day )`

### `kNDifNH4` [m2/d] *Parameters*
- DESC: molecular NH4 diffusion constant at 20*C (d-1 original)
- Source: sediment_exchange.F90 (93)
- Formula (d⁻¹): `call self%get_parameter(self%kNDifNH4, 'kNDifNH4', 'm2/d', 'molecular NH4 diffusion constant at 20*C', default=0.000112_rk)`
- Code: `call self%get_parameter(self%kNDifNH4,     'kNDifNH4',     'm2/d',      'molecular NH4 diffusion constant at 20*C',                       default=0.000112_rk, scale_factor=1.0_rk/secs_pr_day   )`

### `kNDifNO3` [m2/d] *Parameters*
- DESC: NO3 diffusion constant at 20*C (d-1 original)
- Source: sediment_exchange.F90 (94)
- Formula (d⁻¹): `call self%get_parameter(self%kNDifNO3, 'kNDifNO3', 'm2/d', 'NO3 diffusion constant at 20*C', default=0.000086_rk)`
- Code: `call self%get_parameter(self%kNDifNO3,     'kNDifNO3',     'm2/d',      'NO3 diffusion constant at 20*C',                                 default=0.000086_rk, scale_factor=1.0_rk/secs_pr_day   )`

### `kPDifDOM` [m2/d] *Parameters*
- DESC: DOM diffusion constant P at 20*C per group (d-1 original)
- Source: sediment_exchange.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%kPDifDOM(i_dom), 'kPDifDOM'//trim(index), 'm2/d', 'DOM diffusion constant P at 20*C '//trim(index), default=0.00016_rk)`
- Code: `call self%get_parameter(self%kPDifDOM(i_dom),    'kPDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant P at  20*C '//trim(index), default=0.00016_rk,  scale_factor=1.0_rk/secs_pr_day )`

### `kPDifPO4` [m2/d] *Parameters*
- DESC: PO4 diffusion constant at 20*C (d-1 original)
- Source: sediment_exchange.F90 (95)
- Formula (d⁻¹): `call self%get_parameter(self%kPDifPO4, 'kPDifPO4', 'm2/d', 'PO4 diffusion constant at 20*C', default=0.000072_rk)`
- Code: `call self%get_parameter(self%kPDifPO4,     'kPDifPO4',     'm2/d',      'PO4 diffusion constant at 20*C',                                 default=0.000072_rk, scale_factor=1.0_rk/secs_pr_day   )`

### `kSiO2Dif` [m2/d] *Parameters*
- DESC: SiO2 diffusion constant at 20*C (d-1 original)
- Source: sediment_exchange.F90 (96)
- Formula (d⁻¹): `call self%get_parameter(self%kSiO2Dif, 'kSiO2Dif', 'm2/d', 'SiO2 diffusion constant at 20*C', default=0.0000864_rk)`
- Code: `call self%get_parameter(self%kSiO2Dif,     'kSiO2Dif',     'm2/d',      'SiO2 diffusion constant at 20*C',                                default=0.0000864_rk,scale_factor=1.0_rk/secs_pr_day   )`

### `kVegResus` [m2/gDW] *Parameters*
- DESC: relative resuspension reduction per gram macrophytes
- Source: sediment_exchange.F90 (71)
- Formula (d⁻¹): `call self%get_parameter(self%kVegResus, 'kVegResus', 'm2/gDW', 'relative resuspension reduction per gram macrophytes', default=0.05_rk)`
- Code: `call self%get_parameter(self%kVegResus,    'kVegResus',    'm2/gDW',    'relative resuspension reduction per gram macrophytes',           default=0.05_rk                                        )`

### `nDOM` [-] *Parameters*
- DESC: number of DOM groups
- Source: sediment_exchange.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%nDOM, 'nDOM', '-', 'number of DOM groups', default=1)`
- Code: `call self%get_parameter(self%nDOM,                   'nDOM',                     '-',    'number of DOM groups',                                           default=1                             )`

### `nPOM` [-] *Parameters*
- DESC: number of POM groups
- Source: sediment_exchange.F90 (103)
- Formula (d⁻¹): `call self%get_parameter(self%nPOM, 'nPOM', '-', 'number of POM groups', default=1)`
- Code: `call self%get_parameter(self%nPOM,                   'nPOM',                     '-',    'number of POM groups',                                           default=1                             )`

### `qResus` [-] *Parameters*
- DESC: 1=original PCLake; 2=based on shear stress
- Source: sediment_exchange.F90 (72)
- Formula (d⁻¹): `call self%get_parameter(self%qResus, 'qResus', '-', '1=original PCLake; 2=based on shear stress', default=2)`
- Code: `call self%get_parameter(self%qResus,       'qResus',       '-',         '1=original PCLake; 2=based on shear stress',                     default=2                                              )`

### `ref_shear` [N/m] *Parameters*
- DESC: qResus = 2; reference shear stress
- Source: sediment_exchange.F90 (81)
- Formula (d⁻¹): `call self%get_parameter(self%ref_shear, 'ref_shear', 'N/m', 'qResus = 2; reference shear stress', default=1.0_rk)`
- Code: `call self%get_parameter(self%ref_shear,    'ref_shear',    'N/m',       'qResus = 2; reference shear stress',                             default=1.0_rk                                         )`

### `hypsograph` [-] *Parameters*
- DESC: indicate hypsograph presence/absence
- Source: bot_pel_interface.F90 (45)
- Formula (d⁻¹): `call self%get_parameter(self%hypsograph, 'hypsograph', '-', 'indicate hypsograph presence/absence')`
- Code: `call self%get_parameter(self%hypsograph, 'hypsograph', '-', 'indicate hypsograph presence/absence')`

### `alpha` [g/m/d] *Parameters*
- DESC: qResus = 2; gross rate of sediment erosion (d-1 original)
- Source: resus_sed.F90 (71)
- Formula (d⁻¹): `call self%get_parameter(self%alpha, 'alpha', 'g/m/d', 'qResus = 2; gross rate of sediment erosion', default=9000.0_rk)`
- Code: `call self%get_parameter(self%alpha,        'alpha',        'g/m/d',     'qResus = 2; gross rate of sediment erosion',                     default=9000.0_rk, scale_factor=1.0_rk/secs_pr_day     )`

### `cFetch` [m] *Parameters*
- DESC: qResus = 1; length of water body in prevailing wind direction
- Source: resus_sed.F90 (68)
- Formula (d⁻¹): `call self%get_parameter(self%cFetch, 'cFetch', 'm', 'qResus = 1; length of water body in prevailing wind direction', default=1000.0_rk)`
- Code: `call self%get_parameter(self%cFetch,       'cFetch',       'm',         'qResus = 1; length of water body in prevailing wind direction',  default=1000.0_rk                                      )`

### `cFetchRef` [m] *Parameters*
- DESC: qResus = 1; reference fetch
- Source: resus_sed.F90 (67)
- Formula (d⁻¹): `call self%get_parameter(self%cFetchRef, 'cFetchRef', 'm', 'qResus = 1; reference fetch', default=1000.0_rk)`
- Code: `call self%get_parameter(self%cFetchRef,    'cFetchRef',    'm',         'qResus = 1; reference fetch',                                    default=1000.0_rk                                      )`

### `crt_shear` [N/m] *Parameters*
- DESC: qResus = 2; critical shear stress
- Source: resus_sed.F90 (69)
- Formula (d⁻¹): `call self%get_parameter(self%crt_shear, 'crt_shear', 'N/m', 'qResus = 2; critical shear stress', default=0.02_rk)`
- Code: `call self%get_parameter(self%crt_shear,    'crt_shear',    'N/m',       'qResus = 2; critical shear stress',                              default=0.02_rk                                        )`

### `cSuspMax` [-] *Parameters*
- DESC: qResus = 1; maximum value of logistic function
- Source: resus_sed.F90 (64)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspMax, 'cSuspMax', '-', 'qResus = 1; maximum value of logistic function', default=25.2_rk)`
- Code: `call self%get_parameter(self%cSuspMax,     'cSuspMax',     '-',         'qResus = 1; maximum value of logistic function',                 default=25.2_rk                                        )`

### `cSuspMin` [-] *Parameters*
- DESC: qResus = 1; minimum value of logistic function
- Source: resus_sed.F90 (63)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspMin, 'cSuspMin', '-', 'qResus = 1; minimum value of logistic function', default=6.1_rk)`
- Code: `call self%get_parameter(self%cSuspMin,     'cSuspMin',     '-',         'qResus = 1; minimum value of logistic function',                 default=6.1_rk                                         )`

### `cSuspRef` [-] *Parameters*
- DESC: qResus = 1; reference suspended matter function
- Source: resus_sed.F90 (62)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspRef, 'cSuspRef', '-', 'qResus = 1; reference suspended matter function', default=0.0_rk)`
- Code: `call self%get_parameter(self%cSuspRef,     'cSuspRef',     '-',         'qResus = 1; reference suspended matter function',                default=0.0_rk                                         )`

### `cSuspSlope` [-] *Parameters*
- DESC: qResus = 1; slope of logistic function
- Source: resus_sed.F90 (65)
- Formula (d⁻¹): `call self%get_parameter(self%cSuspSlope, 'cSuspSlope', '-', 'qResus = 1; slope of logistic function', default=2.1_rk)`
- Code: `call self%get_parameter(self%cSuspSlope,   'cSuspSlope',   '-',         'qResus = 1; slope of logistic function',                         default=2.1_rk                                         )`

### `cThetaSed` [1/e^*C] *Parameters*
- DESC: temperature coefficient of sedimentation
- Source: resus_sed.F90 (76)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaSed, 'cThetaSed', '1/e^*C', 'temperature coefficient of sedimentation', default=1.01_rk)`
- Code: `call self%get_parameter(self%cThetaSed,    'cThetaSed',    '1/e^*C',    'temperature coefficient of sedimentation',                       default=1.01_rk                                        )`

### `cVSedIM` [m/d] *Parameters*
- DESC: IM sedimentation velocity constant at 20*C
- Source: resus_sed.F90 (77)
- Formula (d⁻¹): `call self%get_parameter(self%cVSedIM, 'cVSedIM', 'm/d', 'IM sedimentation velocity constant at 20*C', default=1.0_rk)`
- Code: `call self%get_parameter(self%cVSedIM,      'cVSedIM',      'm/d',       'IM sedimentation velocity constant at 20*C',                     default=1.0_rk                                         )`

### `cVSedPOM` [m/d] *Parameters*
- DESC: POM sedimentation velocity constant at 20*C (single POM group)
- Source: resus_sed.F90 (78)
- Formula (d⁻¹): `call self%get_parameter(self%cVSedPOM, 'cVSedPOM', 'm/d', 'POM sedimentation velocity constant at 20*C', default=0.5_rk)`
- Code: `call self%get_parameter(self%cVSedPOM,     'cVSedPOM',     'm/d',       'POM sedimentation velocity constant at 20*C',                    default=0.5_rk                                         )`

### `cVSetMain` [m/d] *Parameters*
- DESC: qResus = 2; depth averaged settling velocity (d-1 original)
- Source: resus_sed.F90 (73)
- Formula (d⁻¹): `call self%get_parameter(self%cVSetMain, 'cVSetMain', 'm/d', 'qResus = 2; depth averaged settling velocity', default=0.5_rk)`
- Code: `call self%get_parameter(self%cVSetMain,    'cVSetMain',    'm/d',       'qResus = 2; depth averaged settling velocity',                   default=0.5_rk,    scale_factor=1.0_rk/secs_pr_day     )`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: resus_sed.F90 (79)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,  'diagnostics',  '-',         'toggle diagnostic output',                                       default=.false.                                        )`

### `eta` [-] *Parameters*
- DESC: qResus = 2; shear stress correction factor
- Source: resus_sed.F90 (72)
- Formula (d⁻¹): `call self%get_parameter(self%eta, 'eta', '-', 'qResus = 2; shear stress correction factor', default=1.0_rk)`
- Code: `call self%get_parameter(self%eta,          'eta',          '-',         'qResus = 2; shear stress correction factor',                     default=1.0_rk                                         )`

### `fLutum` [-] *Parameters*
- DESC: lutum fraction of inorganic matter
- Source: resus_sed.F90 (74)
- Formula (d⁻¹): `call self%get_parameter(self%fLutum, 'fLutum', '-', 'lutum fraction of inorganic matter', default=0.1_rk)`
- Code: `call self%get_parameter(self%fLutum,       'fLutum',       '-',         'lutum fraction of inorganic matter',                             default=0.1_rk                                         )`

### `fLutumRef` [-] *Parameters*
- DESC: reference lutum fraction of inorganic matter
- Source: resus_sed.F90 (75)
- Formula (d⁻¹): `call self%get_parameter(self%fLutumRef, 'fLutumRef', '-', 'reference lutum fraction of inorganic matter', default=0.2_rk)`
- Code: `call self%get_parameter(self%fLutumRef,    'fLutumRef',    '-',         'reference lutum fraction of inorganic matter',                   default=0.2_rk                                         )`

### `hDepthSusp` [-] *Parameters*
- DESC: qResus = 1; half-sat. value of depth in logistic function
- Source: resus_sed.F90 (66)
- Formula (d⁻¹): `call self%get_parameter(self%hDepthSusp, 'hDepthSusp', '-', 'qResus = 1; half-sat. value of depth in logistic function', default=2.0_rk)`
- Code: `call self%get_parameter(self%hDepthSusp,   'hDepthSusp',   '-',         'qResus = 1; half-sat. value of depth in logistic function',      default=2.0_rk                                         )`

### `kVegResus` [m2/gDW] *Parameters*
- DESC: relative resuspension reduction per gram macrophytes
- Source: resus_sed.F90 (60)
- Formula (d⁻¹): `call self%get_parameter(self%kVegResus, 'kVegResus', 'm2/gDW', 'relative resuspension reduction per gram macrophytes', default=0.05_rk)`
- Code: `call self%get_parameter(self%kVegResus,    'kVegResus',    'm2/gDW',    'relative resuspension reduction per gram macrophytes',           default=0.05_rk                                        )`

### `qResus` [-] *Parameters*
- DESC: 1=original PCLake; 2=based on shear stress
- Source: resus_sed.F90 (61)
- Formula (d⁻¹): `call self%get_parameter(self%qResus, 'qResus', '-', '1=original PCLake; 2=based on shear stress', default=2)`
- Code: `call self%get_parameter(self%qResus,       'qResus',       '-',         '1=original PCLake; 2=based on shear stress',                     default=2                                              )`

### `ref_shear` [N/m] *Parameters*
- DESC: qResus = 2; reference shear stress
- Source: resus_sed.F90 (70)
- Formula (d⁻¹): `call self%get_parameter(self%ref_shear, 'ref_shear', 'N/m', 'qResus = 2; reference shear stress', default=1.0_rk)`
- Code: `call self%get_parameter(self%ref_shear,    'ref_shear',    'N/m',       'qResus = 2; reference shear stress',                             default=1.0_rk                                         )`

### `cNH4Ground` [mgN/l] *Parameters*
- DESC: NH4 concentration in groundwater
- Source: burial.F90 (70)
- Formula (d⁻¹): `call self%get_parameter(self%cNH4Ground, 'cNH4Ground', 'mgN/l', 'NH4 concentration in groundwater', default=1.0_rk)`
- Code: `call self%get_parameter(self%cNH4Ground,   'cNH4Ground',   'mgN/l',     'NH4 concentration in groundwater',     default=1.0_rk         )`

### `cNO3Ground` [mgN/l] *Parameters*
- DESC: NO3 concentration in groundwater
- Source: burial.F90 (71)
- Formula (d⁻¹): `call self%get_parameter(self%cNO3Ground, 'cNO3Ground', 'mgN/l', 'NO3 concentration in groundwater', default=0.1_rk)`
- Code: `call self%get_parameter(self%cNO3Ground,   'cNO3Ground',   'mgN/l',     'NO3 concentration in groundwater',     default=0.1_rk         )`

### `cPO4Ground` [mgP/l] *Parameters*
- DESC: PO4 concentration in groundwater
- Source: burial.F90 (69)
- Formula (d⁻¹): `call self%get_parameter(self%cPO4Ground, 'cPO4Ground', 'mgP/l', 'PO4 concentration in groundwater', default=0.1_rk)`
- Code: `call self%get_parameter(self%cPO4Ground,   'cPO4Ground',   'mgP/l',     'PO4 concentration in groundwater',     default=0.1_rk         )`

### `cRhoIM` [g/m3] *Parameters*
- DESC: density of sediment inorganic matter
- Source: burial.F90 (66)
- Formula (d⁻¹): `call self%get_parameter(self%cRhoIM, 'cRhoIM', 'g/m3', 'density of sediment inorganic matter', default=2500000.0_rk)`
- Code: `call self%get_parameter(self%cRhoIM,       'cRhoIM',       'g/m3',      'density of sediment inorganic matter', default=2500000.0_rk   )`

### `cRhoOM` [g/m3] *Parameters*
- DESC: density of sediment organic matter
- Source: burial.F90 (67)
- Formula (d⁻¹): `call self%get_parameter(self%cRhoOM, 'cRhoOM', 'g/m3', 'density of sediment organic matter', default=1400000.0_rk)`
- Code: `call self%get_parameter(self%cRhoOM,       'cRhoOM',       'g/m3',      'density of sediment organic matter',   default=1400000.0_rk   )`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: burial.F90 (79)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,'diagnostics',    '-',         'toggle diagnostic output',             default=.false.        )`

### `fDOrgSoil` [-] *Parameters*
- DESC: deep sediment organic matter fraction
- Source: burial.F90 (68)
- Formula (d⁻¹): `call self%get_parameter(self%fDOrgSoil, 'fDOrgSoil', '-', 'deep sediment organic matter fraction', default=0.1_rk)`
- Code: `call self%get_parameter(self%fDOrgSoil,    'fDOrgSoil',    '-',         'deep sediment organic matter fraction',default=0.1_rk         )`

### `nBENT` [-] *Parameters*
- DESC: number of zoobenthos instances
- Source: burial.F90 (74)
- Formula (d⁻¹): `call self%get_parameter(self%nBENT, 'nBENT', '-', 'number of zoobenthos instances', default=0)`
- Code: `call self%get_parameter(self%nBENT,        'nBENT',        '-',         'number of zoobenthos instances',       default=0              )`

### `nDOM` [-] *Parameters*
- DESC: number of benthic dissolved OM instances
- Source: burial.F90 (77)
- Formula (d⁻¹): `call self%get_parameter(self%nDOM, 'nDOM', '-', 'number of benthic dissolved OM instances', default=0)`
- Code: `call self%get_parameter(self%nDOM,         'nDOM',         '-',         'number of benthic dissolved OM instances',  default=0         )`

### `nMACRO` [-] *Parameters*
- DESC: number of macrophyte instances
- Source: burial.F90 (73)
- Formula (d⁻¹): `call self%get_parameter(self%nMACRO, 'nMACRO', '-', 'number of macrophyte instances', default=0)`
- Code: `call self%get_parameter(self%nMACRO,       'nMACRO',       '-',         'number of macrophyte instances',       default=0              )`

### `nPHYT` [-] *Parameters*
- DESC: number of phytoplankton instances
- Source: burial.F90 (72)
- Formula (d⁻¹): `call self%get_parameter(self%nPHYT, 'nPHYT', '-', 'number of phytoplankton instances', default=0)`
- Code: `call self%get_parameter(self%nPHYT,        'nPHYT',        '-',         'number of phytoplankton instances',    default=0              )`

### `nPOM` [-] *Parameters*
- DESC: number of benthic particulate OM instances
- Source: burial.F90 (75)
- Formula (d⁻¹): `call self%get_parameter(self%nPOM, 'nPOM', '-', 'number of benthic particulate OM instances', default=0)`
- Code: `call self%get_parameter(self%nPOM,         'nPOM',         '-',         'number of benthic particulate OM instances',default=0         )`

### `nPOMexch` [-] *Parameters*
- DESC: number of resuspended benthic POM instances
- Source: burial.F90 (76)
- Formula (d⁻¹): `call self%get_parameter(self%nPOMexch, 'nPOMexch', '-', 'number of resuspended benthic POM instances', default=0)`
- Code: `call self%get_parameter(self%nPOMexch,     'nPOMexch',     '-',         'number of resuspended benthic  POM instances',default=0       )`

### `aL` [mm] *Parameters*
- DESC: bivalve length
- Source: bivalves.F90 (92)
- Formula (d⁻¹): `call self%get_parameter(self%aL, 'aL', 'mm', 'bivalve length', default=10.0_rk)`
- Code: `call self%get_parameter(self%aL,              'aL',              'mm',       'bivalve length',                                           default=10.0_rk                                         )`

### `cAw` [-] *Parameters*
- DESC: constant 2 for length to total shell-on dry-weight conversion
- Source: bivalves.F90 (93)
- Formula (d⁻¹): `call self%get_parameter(self%cAw, 'cAw', '-', 'constant 2 for length to total shell-on dry-weight conversion', default=2.766_rk)`
- Code: `call self%get_parameter(self%cAw,             'cAw',             '-',        'constant 2 for length to total shell-on dry-weight conversion',                 default=2.766_rk                   )`

### `cBi` [-] *Parameters*
- DESC: exponent for weight effect on ingestion
- Source: bivalves.F90 (99)
- Formula (d⁻¹): `call self%get_parameter(self%cBi, 'cBi', '-', 'exponent for weight effect on ingestion', default=-0.39_rk)`
- Code: `call self%get_parameter(self%cBi,             'cBi',             '-',        'exponent for weight effect on ingestion',                  default=-0.39_rk                                        )`

### `cBr` [-] *Parameters*
- DESC: exponent for maximum standard respiration
- Source: bivalves.F90 (113)
- Formula (d⁻¹): `call self%get_parameter(self%cBr, 'cBr', '-', 'exponent for maximum standard respiration', default=-0.25_rk)`
- Code: `call self%get_parameter(self%cBr,             'cBr',             '-',        'exponent for maximum standard respiration',                default=-0.25_rk                                        )`

### `cBw` [-] *Parameters*
- DESC: constant 2 for length to total shell-on dry-weight conversion
- Source: bivalves.F90 (94)
- Formula (d⁻¹): `call self%get_parameter(self%cBw, 'cBw', '-', 'constant 2 for length to total shell-on dry-weight conversion', default=9.472_rk)`
- Code: `call self%get_parameter(self%cBw,             'cBw',             '-',        'constant 2 for length to total shell-on dry-weight conversion',                 default=9.472_rk                   )`

### `cCDRef` [gC/gDW] *Parameters*
- DESC: reference total body carbon to DW ratio
- Source: bivalves.F90 (97)
- Formula (d⁻¹): `call self%get_parameter(self%cCDRef, 'cCDRef', 'gC/gDW', 'reference total body carbon to DW ratio', default=0.45_rk)`
- Code: `call self%get_parameter(self%cCDRef,          'cCDRef',          'gC/gDW',   'reference total body carbon to DW ratio',                  default=0.45_rk                                         )`

### `cDayAgeBiv` [day of year] *Parameters*
- DESC: day-of-year where aging of juveniles to adults occurs
- Source: bivalves.F90 (131)
- Formula (d⁻¹): `call self%get_parameter(self%cDayAgeBiv, 'cDayAgeBiv', 'day of year', 'day-of-year where aging of juveniles to adults occurs', default=360.0_rk)`
- Code: `call self%get_parameter(self%cDayAgeBiv,  'cDayAgeBiv',  'day of year',  'day-of-year where aging of juveniles to adults occurs',              default=360.0_rk                              )`

### `cDayReprBiv` [day of year] *Parameters*
- DESC: earliest day-of-year where spawning may occur
- Source: bivalves.F90 (128)
- Formula (d⁻¹): `call self%get_parameter(self%cDayReprBiv, 'cDayReprBiv', 'day of year', 'earliest day-of-year where spawning may occur', default=60.0_rk)`
- Code: `call self%get_parameter(self%cDayReprBiv, 'cDayReprBiv', 'day of year',  'earliest day-of-year where spawning may occur',          default=60.0_rk                                           )`

### `cDmax` [gDW/m2] *Parameters*
- DESC: maximum bivalves density where ingestion stops
- Source: bivalves.F90 (108)
- Formula (d⁻¹): `call self%get_parameter(self%cDmax, 'cDmax', 'gDW/m2', 'maximum bivalves density where ingestion stops', default=550.0_rk)`
- Code: `call self%get_parameter(self%cDmax,           'cDmax',           'gDW/m2',   'maximum bivalves density where ingestion stops',           default=550.0_rk                                        )`

### `cDmaxOpt` [gDW/m2] *Parameters*
- DESC: maximum bivalves density for optimal ingestion to occur
- Source: bivalves.F90 (107)
- Formula (d⁻¹): `call self%get_parameter(self%cDmaxOpt, 'cDmaxOpt', 'gDW/m2', 'maximum bivalves density for optimal ingestion to occur', default=175.0_rk)`
- Code: `call self%get_parameter(self%cDmaxOpt,        'cDmaxOpt',        'gDW/m2',   'maximum bivalves density for optimal ingestion to occur',  default=175.0_rk                                        )`

### `cgegst` [-] *Parameters*
- DESC: gamma coefficient for egestions food availability dependence
- Source: bivalves.F90 (117)
- Formula (d⁻¹): `call self%get_parameter(self%cgegst, 'cgegst', '-', 'gamma coefficient for egestions food availability dependence', default=0.88_rk)`
- Code: `call self%get_parameter(self%cgegst,          'cgegst',             '-',     'gamma coefficient for egestions food availability dependence',   default=0.88_rk                                   )`

### `cNDRef` [gN/gDW] *Parameters*
- DESC: reference total body nitrogen to DW ratio
- Source: bivalves.F90 (95)
- Formula (d⁻¹): `call self%get_parameter(self%cNDRef, 'cNDRef', 'gN/gDW', 'reference total body nitrogen to DW ratio ', default=0.1_rk)`
- Code: `call self%get_parameter(self%cNDRef,          'cNDRef',          'gN/gDW',   'reference total body nitrogen to DW ratio ',               default=0.1_rk                                          )`

### `cPDRef` [gP/gDW] *Parameters*
- DESC: reference total body phosphorus to DW ratio
- Source: bivalves.F90 (96)
- Formula (d⁻¹): `call self%get_parameter(self%cPDRef, 'cPDRef', 'gP/gDW', 'reference total body phosphorus to DW ratio ', default=0.01_rk)`
- Code: `call self%get_parameter(self%cPDRef,          'cPDRef',          'gP/gDW',   'reference total body phosphorus to DW ratio ',             default=0.01_rk                                         )`

### `cSSIMmax` [gDW/m3] *Parameters*
- DESC: maximum suspended inorganic solids concentration where ingestion stops
- Source: bivalves.F90 (110)
- Formula (d⁻¹): `call self%get_parameter(self%cSSIMmax, 'cSSIMmax', 'gDW/m3', 'maximum suspended (inorganic) solids concentration where ingestion stops', default=100.0_rk)`
- Code: `call self%get_parameter(self%cSSIMmax,        'cSSIMmax',        'gDW/m3',   'maximum suspended (inorganic) solids concentration where ingestion stops',           default=100.0_rk              )`

### `cSSIMmaxOpt` [gDW/m3] *Parameters*
- DESC: maximum suspended inorganic solids concentration for optimal ingestion
- Source: bivalves.F90 (109)
- Formula (d⁻¹): `call self%get_parameter(self%cSSIMmaxOpt, 'cSSIMmaxOpt', 'gDW/m3', 'maximum suspended (inorganic) solids concentration for optimal ingestion to occur', default=20.0_rk)`
- Code: `call self%get_parameter(self%cSSIMmaxOpt,     'cSSIMmaxOpt',     'gDW/m3',   'maximum suspended (inorganic) solids concentration for optimal ingestion to occur',  default=20.0_rk               )`

### `cTempReprBiv` [*C] *Parameters*
- DESC: minimum water temperature at which spawning can occur
- Source: bivalves.F90 (129)
- Formula (d⁻¹): `call self%get_parameter(self%cTempReprBiv, 'cTempReprBiv', '*C', 'minimum water temperature at which spawning can occur', default=4.0_rk)`
- Code: `call self%get_parameter(self%cTempReprBiv,'cTempReprBiv', '*C',           'minimum water temperature at which spawning can occur', default=4.0_rk                                            )`

### `cThetaResp` [-] *Parameters*
- DESC: temperature multiplier for respiration
- Source: bivalves.F90 (114)
- Formula (d⁻¹): `call self%get_parameter(self%cThetaResp, 'cThetaResp', '-', 'temperature multiplier for respiration', default=1.08_rk)`
- Code: `call self%get_parameter(self%cThetaResp,      'cThetaResp',      '-',        'temperature multiplier for respiration',                   default=1.08_rk                                         )`

### `cTmax` [*C] *Parameters*
- DESC: maximum temperature where ingestion stops
- Source: bivalves.F90 (106)
- Formula (d⁻¹): `call self%get_parameter(self%cTmax, 'cTmax', '*C', 'maximum temperature where ingestion stops', default=31.0_rk)`
- Code: `call self%get_parameter(self%cTmax,           'cTmax',           '*C',       'maximum temperature where ingestion stops',                default=31.0_rk                                         )`

### `cTmaxOpt` [*C] *Parameters*
- DESC: maximum temperature for optimal ingestion to occur
- Source: bivalves.F90 (105)
- Formula (d⁻¹): `call self%get_parameter(self%cTmaxOpt, 'cTmaxOpt', '*C', 'maximum temperature for optimal ingestion to occur', default=20.0_rk)`
- Code: `call self%get_parameter(self%cTmaxOpt,        'cTmaxOpt',        '*C',       'maximum temperature for optimal ingestion to occur',       default=20.0_rk                                         )`

### `cTmin` [*C] *Parameters*
- DESC: minimum temperature threshold for onset of ingestion
- Source: bivalves.F90 (103)
- Formula (d⁻¹): `call self%get_parameter(self%cTmin, 'cTmin', '*C', 'minimum temperature threshold for onset of ingestion', default=4.0_rk)`
- Code: `call self%get_parameter(self%cTmin,           'cTmin',           '*C',       'minimum temperature threshold for onset of ingestion',     default=4.0_rk                                          )`

### `cTminOpt` [*C] *Parameters*
- DESC: minimum temperature for optimal ingestion to occur
- Source: bivalves.F90 (104)
- Formula (d⁻¹): `call self%get_parameter(self%cTminOpt, 'cTminOpt', '*C', 'minimum temperature for optimal ingestion to occur', default=12.0_rk)`
- Code: `call self%get_parameter(self%cTminOpt,        'cTminOpt',        '*C',       'minimum temperature for optimal ingestion to occur',       default=12.0_rk                                         )`

### `diagnostics` [-] *Parameters*
- DESC: toggle diagnostic output
- Source: bivalves.F90 (153)
- Formula (d⁻¹): `call self%get_parameter(self%diagnostics, 'diagnostics', '-', 'toggle diagnostic output', default=.false.)`
- Code: `call self%get_parameter(self%diagnostics,     'diagnostics',     '-',        'toggle diagnostic output',                                 default=.false.                                         )`

### `fAgeBiv` [1/d] *Parameters*
- DESC: fraction of juvenile biomass transferred to adult biomass through aging (d-1 original)
- Source: bivalves.F90 (132)
- Formula (d⁻¹): `call self%get_parameter(self%fAgeBiv, 'fAgeBiv', '1/d', 'fraction of juvenile biomass which is transferred to adult biomass through aging', default=0.001_rk)`
- Code: `call self%get_parameter(self%fAgeBiv,     'fAgeBiv', '1/d','fraction of juvenile biomass which is transferred to adult biomass through aging', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `fDAssBiv` [-] *Parameters*
- DESC: fraction of filtered food that is assimilated
- Source: bivalves.F90 (101)
- Formula (d⁻¹): `call self%get_parameter(self%fDAssBiv, 'fDAssBiv', '-', 'fraction of filtered food that is assimilated', default=0.34_rk)`
- Code: `call self%get_parameter(self%fDAssBiv,        'fDAssBiv',          '-',      'fraction of filtered food that is assimilated',            default=0.34_rk                                         )`

### `fRegst` [-] *Parameters*
- DESC: minimum proportion egested as faeces
- Source: bivalves.F90 (116)
- Formula (d⁻¹): `call self%get_parameter(self%fRegst, 'fRegst', '-', 'minimum proportion egested as faeces', default=0.315_rk)`
- Code: `call self%get_parameter(self%fRegst,          'fRegst',             '-',     'minimum proportion egested as faeces',                     default=0.315_rk                                        )`

### `fReprBiv` [1/d] *Parameters*
- DESC: fraction of adult biomass transferred to juveniles during spawning (d-1 original)
- Source: bivalves.F90 (130)
- Formula (d⁻¹): `call self%get_parameter(self%fReprBiv, 'fReprBiv', '1/d', 'fraction of adult biomass which is transferred to juveniles during spawning', default=0.001_rk)`
- Code: `call self%get_parameter(self%fReprBiv,    'fReprBiv', '1/d',  'fraction of adult biomass which is transferred to juveniles during spawning',default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)`

### `hKdo` [g/m3] *Parameters*
- DESC: half saturation constant for metabolic response to dissolved oxygen
- Source: bivalves.F90 (123)
- Formula (d⁻¹): `call self%get_parameter(self%hKdo, 'hKdo', 'g/m3', 'half saturation constant for metabolic response to dissolved oxygen', default=0.25_rk)`
- Code: `call self%get_parameter(self%hKdo,            'hKdo',             'g/m3',    'half saturation constant for metabolic response to dissolved oxygen',      default=0.25_rk                         )`

### `hKfood` [gDW/m3] *Parameters*
- DESC: saturation food concentration
- Source: bivalves.F90 (102)
- Formula (d⁻¹): `call self%get_parameter(self%hKfood, 'hKfood', 'gDW/m3', 'saturation food concentration', default=5.0_rk)`
- Code: `call self%get_parameter(self%hKfood,          'hKfood',          'gDW/m3',   'saturation food concentration',                            default=5.0_rk                                          )`

### `kAi` [g DW/g DW/d] *Parameters*
- DESC: maximum standard ingestion rate (d-1 original)
- Source: bivalves.F90 (98)
- Formula (d⁻¹): `call self%get_parameter(self%kAi, 'kAi', 'g DW/g DW/d', 'maximum standard ingestion rate', default=0.003_rk)`
- Code: `call self%get_parameter(self%kAi,             'kAi',             'g DW/g DW/d',  'maximum standard ingestion rate',                      default=0.003_rk,   scale_factor=1.0_rk/secs_pr_day     )`

### `kAr` [1/d] *Parameters*
- DESC: intercept for maximum standard respiration (d-1 original)
- Source: bivalves.F90 (112)
- Formula (d⁻¹): `call self%get_parameter(self%kAr, 'kAr', '1/d', 'intercept for maximum standard respiration', default=0.0019_rk)`
- Code: `call self%get_parameter(self%kAr,             'kAr',             '1/d',      'intercept for maximum standard respiration',               default=0.0019_rk,   scale_factor=1.0_rk/secs_pr_day    )`

### `kbdo` [g/m3] *Parameters*
- DESC: basal respiration rate
- Source: bivalves.F90 (122)
- Formula (d⁻¹): `call self%get_parameter(self%kbdo, 'kbdo', 'g/m3', 'basal respiration rate', default=5.0_rk)`
- Code: `call self%get_parameter(self%kbdo,            'kbdo',             'g/m3',    'basal respiration rate',                                   default=5.0_rk                                          )`

### `kmort` [1/d] *Parameters*
- DESC: mortality rate coefficient (d-1 original)
- Source: bivalves.F90 (121)
- Formula (d⁻¹): `call self%get_parameter(self%kmort, 'kmort', '1/d', 'mortality rate coefficient', default=0.0002_rk)`
- Code: `call self%get_parameter(self%kmort,           'kmort',             '1/d',    'mortality rate coefficient',                               default=0.0002_rk,   scale_factor=1.0_rk/secs_pr_day    )`

### `lSi(i_prey)` [-] *Parameters*
- DESC: toggle prey silica tracking per type
- Source: bivalves.F90 (149)
- Formula (d⁻¹): `call self%get_parameter(self%lSi(i_prey), 'lSi'//trim(index), '-', 'toggle prey silica tracking '//trim(index), default=.false.)`
- Code: `call self%get_parameter(self%lSi(i_prey),        'lSi'//trim(index),        '-', 'toggle prey silica tracking '//trim(index),        default=.false.                                         )`

### `nKShares` [-] *Parameters*
- DESC: for qStageOpt > 0; # of not-coupled other stages sharing carrying capacity
- Source: bivalves.F90 (126)
- Formula (d⁻¹): `call self%get_parameter(self%nKShares, 'nKShares', '-', 'for qStageOpt > 0; # of not-coupled other stages sharing carr. cap.', default=0)`
- Code: `call self%get_parameter(self%nKShares,         'nKShares',      '-',         'for qStageOpt > 0; # of not-coupled other stages sharing carr. cap.',  default=0                                   )`

### `nPrey` [-] *Parameters*
- DESC: number of prey types
- Source: bivalves.F90 (142)
- Formula (d⁻¹): `call self%get_parameter(self%nPrey, 'nPrey', '-', 'number of prey types', default=1)`
- Code: `call self%get_parameter(self%nPrey,           'nPrey',           '-',        'number of prey types',                                     default=1                                               )`

### `pref(i_prey)` [-] *Parameters*
- DESC: preference for prey per type
- Source: bivalves.F90 (148)
- Formula (d⁻¹): `call self%get_parameter(self%pref(i_prey), 'pref'//trim(index), '-', 'preference for prey '//trim(index), default=1.0_rk)`
- Code: `call self%get_parameter(self%pref(i_prey),       'pref'//trim(index),       '-', 'preference for prey '//trim(index),                default=1.0_rk                                          )`

### `prey_suffix(i_prey)` [-] *Parameters*
- DESC: prey name suffix per type
- Source: bivalves.F90 (150)
- Formula (d⁻¹): `call self%get_parameter(self%prey_suffix(i_prey), 'prey_suffix'//trim(index), '-', 'prey name suffix '//trim(index), default='')`
- Code: `call self%get_parameter(self%prey_suffix(i_prey),'prey_suffix'//trim(index),'-', 'prey name suffix '//trim(index),                   default=''                                              )`

### `qStageOpt` [-] *Parameters*
- DESC: stage coupling method: 0=nothing; 1=repro.; 2=maturation;
- Source: bivalves.F90 (125)
- Formula (d⁻¹): `call self%get_parameter(self%qStageOpt, 'qStageOpt', '-', 'stage coupling method: 0=nothing; 1=repro.; 2=maturation;', default=0)`
- Code: `call self%get_parameter(self%qStageOpt,        'qStageOpt',      '-',        'stage coupling method: 0=nothing; 1=repro.; 2=maturation;',default=0                                               )`

## Reaeration

### `aFunLemnAer` [-] *Reaeration*
- DESC: duckweed function of reaeration
- Source: abiotic_water.F90 (335-335)
- Formula (d⁻¹): `1.0`
- Code: `aFunLemnAer = 1.0_rk`

### `kAer` [-] *Reaeration*
- DESC: reaeration coefficient
- Source: abiotic_water.F90 (334-334)
- Formula (d⁻¹): `(0.727*((uVWind)**(0.5))-0.371*uVWind+0.0376*uVWind*uVWind)`
- Code: `kAer=(0.727_rk*((uVWind)**(0.5_rk))-0.371_rk*uVWind+0.0376_rk*uVWind*uVWind)`

### `sO2W` [-] *Reaeration*
- DESC: surface exchange O2 reaeration
- Source: abiotic_water.F90 (340-340)
- Formula (d⁻¹): `tO2Aer`
- Code: `_SET_SURFACE_EXCHANGE_(self%id_sO2W,tO2Aer/secs_pr_day)`

### `tO2Aer` [-] *Reaeration*
- DESC: reaeration flux of O2 into the water
- Source: abiotic_water.F90 (336-336)
- Formula (d⁻¹): `kAer * uFunTmAer * (uO2Sat - sO2W) * aFunLemnAer`
- Code: `tO2Aer = kAer * uFunTmAer * (uO2Sat - sO2W) * aFunLemnAer`

### `tO2Aer` [-] *Reaeration*
- DESC: horizontal diagnostic O2 reaeration
- Source: abiotic_water.F90 (341-341)
- Formula (d⁻¹): `tO2Aer`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2Aer,tO2Aer/secs_pr_day)`

### `uFunTmAer` [-] *Reaeration*
- DESC: temperature function of reaeration
- Source: abiotic_water.F90 (332-332)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaAer)`
- Code: `uFunTmAer = uFunTmArrh(uTm,self%cThetaAer)`

### `uO2Sat` [-] *Reaeration*
- DESC: oxygen saturation concentration
- Source: abiotic_water.F90 (333-333)
- Formula (d⁻¹): `14.652 - 0.41022 * uTm + 0.007991 * uTm*uTm - 0.000077774 * uTm*uTm*uTm`
- Code: `uO2Sat = 14.652_rk - 0.41022 * uTm + 0.007991_rk * uTm*uTm - 0.000077774_rk * uTm*uTm*uTm`

### `wind` [-] *Reaeration*
- DESC: horizontal diagnostic windspeed
- Source: abiotic_water.F90 (342-342)
- Formula (d⁻¹): `uVWind`
- Code: `_SET_HORIZONTAL_DIAGNOSTIC_(self%id_wind,uVWind)`

## Refractory pool conversion

### `tCRefr` [-] *Refractory pool conversion*
- DESC: final ROC in refractory_target C
- Source: om_pool.F90 (464)
- Formula (d⁻¹): `tCRefr = self%fRefrNutS * tCMin`
- Code: `tCRefr = self%fRefrNutS * tCMin`

### `tCTrans` [-] *Refractory pool conversion*
- DESC: final ROC in biotransformation_target C
- Source: om_pool.F90 (457)
- Formula (d⁻¹): `tCTrans = (1.0_rk - self%fRefrDWS) * tCMin`
- Code: `tCTrans = (1.0_rk - self%fRefrDWS) * tCMin`

### `tDRefr` [-] *Refractory pool conversion*
- DESC: final ROC in refractory_target DW
- Source: om_pool.F90 (461)
- Formula (d⁻¹): `tDRefr = self%fRefrDWS * tDMin`
- Code: `tDRefr = self%fRefrDWS * tDMin`

### `tDTrans` [-] *Refractory pool conversion*
- DESC: final ROC in biotransformation_target DW
- Source: om_pool.F90 (453)
- Formula (d⁻¹): `tDTrans = (1.0_rk - self%fRefrDWS) * tDMin`
- Code: `tDTrans = (1.0_rk - self%fRefrDWS) * tDMin`

### `tNRefr` [-] *Refractory pool conversion*
- DESC: final ROC in refractory_target N
- Source: om_pool.F90 (462)
- Formula (d⁻¹): `tNRefr = self%fRefrNutS * tNMin`
- Code: `tNRefr = self%fRefrNutS * tNMin`

### `tNTrans` [-] *Refractory pool conversion*
- DESC: final ROC in biotransformation_target N
- Source: om_pool.F90 (454)
- Formula (d⁻¹): `tNTrans = (1.0_rk - self%fRefrNutS) * tNMin`
- Code: `tNTrans = (1.0_rk - self%fRefrNutS) * tNMin`

### `tPRefr` [-] *Refractory pool conversion*
- DESC: final ROC in refractory_target P
- Source: om_pool.F90 (463)
- Formula (d⁻¹): `tPRefr = self%fRefrNutS * tPMin`
- Code: `tPRefr = self%fRefrNutS * tPMin`

### `tPTrans` [-] *Refractory pool conversion*
- DESC: final ROC in biotransformation_target P
- Source: om_pool.F90 (455)
- Formula (d⁻¹): `tPTrans = (1.0_rk - self%fRefrNutS) * tPMin`
- Code: `tPTrans = (1.0_rk - self%fRefrNutS) * tPMin`

## Reproduction

### `tDAgeFish` [1/d] *Reproduction*
- DESC: aging DW flux (if Day=cDayAgeFish)
- Source: fish_pclake.F90 (667)
- Formula (d⁻¹): `tDAgeFish = fAgeFish * sDFi`
- Code: `tDAgeFish = self%fAgeFish * sDFi`

### `tDAgeFish_init` [1/d] *Reproduction*
- DESC: initialize DW aging flux
- Source: fish_pclake.F90 (649)
- Formula (d⁻¹): `tDAgeFish = 0.0_rk`
- Code: `tDAgeFish = 0.0_rk`

### `tDReprFish` [1/d] *Reproduction*
- DESC: reproduction DW flux (if Day=cDayReprFish)
- Source: fish_pclake.F90 (657)
- Formula (d⁻¹): `tDReprFish = fReprFish * sDFi`
- Code: `tDReprFish = self%fReprFish * sDFi`

### `tDReprFish_init` [1/d] *Reproduction*
- DESC: initialize DW reproduction flux
- Source: fish_pclake.F90 (646)
- Formula (d⁻¹): `tDReprFish = 0.0_rk`
- Code: `tDReprFish = 0.0_rk`

### `tNAgeFish` [1/d] *Reproduction*
- DESC: aging N flux
- Source: fish_pclake.F90 (669)
- Formula (d⁻¹): `tNAgeFish = rNDFi * tDAgeFish`
- Code: `tNAgeFish = rNDFi * tDAgeFish`

### `tNAgeFish_init` [1/d] *Reproduction*
- DESC: initialize N aging flux
- Source: fish_pclake.F90 (651)
- Formula (d⁻¹): `tNAgeFish = 0.0_rk`
- Code: `tNAgeFish = 0.0_rk`

### `tNReprFish` [1/d] *Reproduction*
- DESC: reproduction N flux
- Source: fish_pclake.F90 (659)
- Formula (d⁻¹): `tNReprFish = rNDFi * tDReprFish`
- Code: `tNReprFish = rNDFi * tDReprFish`

### `tNReprFish_init` [1/d] *Reproduction*
- DESC: initialize N reproduction flux
- Source: fish_pclake.F90 (648)
- Formula (d⁻¹): `tNReprFish = 0.0_rk`
- Code: `tNReprFish = 0.0_rk`

### `tPAgeFish` [1/d] *Reproduction*
- DESC: aging P flux
- Source: fish_pclake.F90 (668)
- Formula (d⁻¹): `tPAgeFish = rPDFi * tDAgeFish`
- Code: `tPAgeFish = rPDFi * tDAgeFish`

### `tPAgeFish_init` [1/d] *Reproduction*
- DESC: initialize P aging flux
- Source: fish_pclake.F90 (650)
- Formula (d⁻¹): `tPAgeFish = 0.0_rk`
- Code: `tPAgeFish = 0.0_rk`

### `tPReprFish` [1/d] *Reproduction*
- DESC: reproduction P flux
- Source: fish_pclake.F90 (658)
- Formula (d⁻¹): `tPReprFish = rPDFi * tDReprFish`
- Code: `tPReprFish = rPDFi * tDReprFish`

### `tPReprFish_init` [1/d] *Reproduction*
- DESC: initialize P reproduction flux
- Source: fish_pclake.F90 (647)
- Formula (d⁻¹): `tPReprFish = 0.0_rk`
- Code: `tPReprFish = 0.0_rk`

### `tCReprBiv` [g/m2/s] *Reproduction*
- DESC: default: C reproduction flux (zero)
- Source: bivalves.F90 (533)
- Formula (d⁻¹): `tCReprBiv = 0.0_rk`
- Code: `tCReprBiv = 0.0_rk`

### `tCReprBiv` [g/m2/s] *Reproduction*
- DESC: reproduction C flux
- Source: bivalves.F90 (550)
- Formula (d⁻¹): `tCReprBiv = rCDBiv * tDReprBiv`
- Code: `tCReprBiv = rCDBiv * tDReprBiv`

### `tDReprBiv` [g/m2/s] *Reproduction*
- DESC: default: DW reproduction flux (zero)
- Source: bivalves.F90 (530)
- Formula (d⁻¹): `tDReprBiv = 0.0_rk`
- Code: `tDReprBiv = 0.0_rk`

### `tDReprBiv` [g/m2/s] *Reproduction*
- DESC: case qStageOpt=1 or 3 + uTm>=cTempReprBiv: DW reproduction flux
- Source: bivalves.F90 (547)
- Formula (d⁻¹): `tDReprBiv = self%fReprBiv * sDBiv`
- Code: `tDReprBiv = self%fReprBiv * sDBiv`

### `tNReprBiv` [g/m2/s] *Reproduction*
- DESC: default: N reproduction flux (zero)
- Source: bivalves.F90 (532)
- Formula (d⁻¹): `tNReprBiv = 0.0_rk`
- Code: `tNReprBiv = 0.0_rk`

### `tNReprBiv` [g/m2/s] *Reproduction*
- DESC: reproduction N flux
- Source: bivalves.F90 (548)
- Formula (d⁻¹): `tNReprBiv = rNDBiv * tDReprBiv`
- Code: `tNReprBiv = rNDBiv * tDReprBiv`

### `tPReprBiv` [g/m2/s] *Reproduction*
- DESC: default: P reproduction flux (zero)
- Source: bivalves.F90 (531)
- Formula (d⁻¹): `tPReprBiv = 0.0_rk`
- Code: `tPReprBiv = 0.0_rk`

### `tPReprBiv` [g/m2/s] *Reproduction*
- DESC: reproduction P flux
- Source: bivalves.F90 (549)
- Formula (d⁻¹): `tPReprBiv = rPDBiv * tDReprBiv`
- Code: `tPReprBiv = rPDBiv * tDReprBiv`

## Respiration

### `wCRespZoo` [gC/m3/s] *Respiration*
- DESC: calculate C respired
- Source: zooplankton.F90 (332)
- Formula (d⁻¹): `rCDZoo / cCDRef * kDRespZoo * uFunTmZoo * sCZoo`
- Code: `wCRespZoo = rCDZoo / self%cCDRef * self%kDRespZoo * uFunTmZoo * sCZoo`

### `wDRespZoo` [gDW/m3/s] *Respiration*
- DESC: calculate zooplankton respiration (in DW)
- Source: zooplankton.F90 (331)
- Formula (d⁻¹): `aCorDRespZoo * kDRespZoo * uFunTmZoo * sDZoo`
- Code: `wDRespZoo = aCorDRespZoo * self%kDRespZoo * uFunTmZoo * sDZoo`

### `tCRespBent` [gC/m2/s] *Respiration*
- DESC: calculate C respiration
- Source: zoobenthos.F90 (367)
- Formula (d⁻¹): `(rCDBent / cCDRef) * kDRespBent * uFunTmBent * fO2 * sCBent`
- Code: `tCRespBent = (rCDBent / self%cCDRef) * self%kDRespBent * uFunTmBent * fO2 * sCBent`

### `tDRespBent` [gDW/m2/s] *Respiration*
- DESC: calculate respiration (in DW)
- Source: zoobenthos.F90 (366)
- Formula (d⁻¹): `aCorDRespBent * kDRespBent * uFunTmBent * fO2 * sDBent`
- Code: `tDRespBent = aCorDRespBent * self%kDRespBent * uFunTmBent * fO2 * sDBent`

### `tCRespVeg` [gC/m2/s] *Respiration*
- DESC: dark respiration of macrophytes in C
- Source: macrophytes.F90 (535)
- Formula (d⁻¹): `tDRespVeg * rCDVeg`
- Code: `tCRespVeg = tDRespVeg * rCDVeg`

### `tDRespVeg` [gDW/m2/s] *Respiration*
- DESC: dark respiration of macrophytes in DW
- Source: macrophytes.F90 (534)
- Formula (d⁻¹): `kDRespVeg * uFunTmRespVeg * sDVeg`
- Code: `tDRespVeg = self%kDRespVeg * uFunTmRespVeg * sDVeg`

### `tCRespFi` [-] *Respiration*
- DESC: calculate C respiration rate (dynamic)
- Source: fish.F90 (837)
- Formula (d⁻¹): `tCRespFi = (rCDFi / self%cCDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sCFi`
- Code: `tCRespFi = (rCDFi / self%cCDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sCFi`

### `tCRespFi` [-] *Respiration*
- DESC: calculate C respiration rate (fixed)
- Source: fish.F90 (841)
- Formula (d⁻¹): `tCRespFi = tDRespFi * self%cCDRef`
- Code: `tCRespFi = tDRespFi * self%cCDRef`

### `tDRespFi` [-] *Respiration*
- DESC: calculate DW respiration rate
- Source: fish.F90 (833)
- Formula (d⁻¹): `tDRespFi = (self%cPDRef / rPDFi) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi * uFunTmFish * sDFi`
- Code: `tDRespFi = (self%cPDRef / rPDFi) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi * uFunTmFish * sDFi`

### `tDRespFi` [1/d] *Respiration*
- DESC: DW respiration rate
- Source: fish_pclake.F90 (615)
- Formula (d⁻¹): `tDRespFi = (cPDFishRef / rPDFi) * kDRespFi * uFunTmFish * sDFi`
- Code: `tDRespFi = (self%cPDFishRef / rPDFi) * self%kDRespFi * uFunTmFish * sDFi`

### `tNExcrFi_dynamic` [1/d] *Respiration*
- DESC: N excretion rate (dynamic stoichiometry)
- Source: fish_pclake.F90 (618)
- Formula (d⁻¹): `tNExcrFi = (rNDFi / cNDFishRef) * kDRespFi * uFunTmFish * sNFi`
- Code: `tNExcrFi = (rNDFi / self%cNDFishRef) * self%kDRespFi * uFunTmFish * sNFi`

### `tNExcrFi_fixed` [1/d] *Respiration*
- DESC: N excretion rate (fixed stoichiometry)
- Source: fish_pclake.F90 (621)
- Formula (d⁻¹): `tNExcrFi = tDRespFi * cNDFishRef`
- Code: `tNExcrFi = tDRespFi * self%cNDFishRef`

### `tPExcrFi_dynamic` [1/d] *Respiration*
- DESC: P excretion rate (dynamic stoichiometry)
- Source: fish_pclake.F90 (617)
- Formula (d⁻¹): `tPExcrFi = (rPDFi / cPDFishRef) * kDRespFi * uFunTmFish * sPFi`
- Code: `tPExcrFi = (rPDFi / self%cPDFishRef) * self%kDRespFi * uFunTmFish * sPFi`

### `tPExcrFi_fixed` [1/d] *Respiration*
- DESC: P excretion rate (fixed stoichiometry)
- Source: fish_pclake.F90 (620)
- Formula (d⁻¹): `tPExcrFi = tDRespFi * cPDFishRef`
- Code: `tPExcrFi = tDRespFi * self%cPDFishRef`

### `tCRespBiv` [g/m2/s] *Respiration*
- DESC: C respiration
- Source: bivalves.F90 (504)
- Formula (d⁻¹): `tCRespBiv = (rCDBiv / self%cCDRef) * tDRespBiv * sCBiv`
- Code: `tCRespBiv = (rCDBiv / self%cCDRef) * tDRespBiv * sCBiv`

### `tDRespBiv` [g/m2/s] *Respiration*
- DESC: respiration in DW
- Source: bivalves.F90 (503)
- Formula (d⁻¹): `tDRespBiv = tRespInd*sDBiv`
- Code: `tDRespBiv = tRespInd*sDBiv`

### `tRespInd` [-] *Respiration*
- DESC: individual respiration (g DW/g DW mussel)
- Source: bivalves.F90 (502)
- Formula (d⁻¹): `tRespInd = self%cThetaResp**(uTm-20.0) * self%kAr*weight**self%cBr`
- Code: `tRespInd = self%cThetaResp**(uTm-20.0) * self%kAr*weight**self%cBr`

## Resuspension

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=1 PCLake empirical logistic resuspension function (when uTm>=0.1)
- Source: sediment_exchange.F90 (425-426)
- Formula (d⁻¹): `aFunDimSusp=self%cSuspRef*((self%cSuspMin+self%cSuspMax/(1.0_rk+exp(self%cSuspSlope*(depth-self%hDepthSusp))))*((((self%cFetch+NearZero)/self%cFetchRef))**(0.5_rk)))`
- Code: `aFunDimSusp=self%cSuspRef*((self%cSuspMin+self%cSuspMax/(1.0_rk+exp(self%cSuspSlope* & (depth-self%hDepthSusp))))*((((self%cFetch +NearZero)/ self%cFetchRef) )** (0.5_rk)))`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=1 zero when temperature below 0.1
- Source: sediment_exchange.F90 (428)
- Formula (d⁻¹): `aFunDimSusp=0.0_rk`
- Code: `aFunDimSusp=0.0_rk`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=2 zero when shear below critical
- Source: sediment_exchange.F90 (432)
- Formula (d⁻¹): `aFunDimSusp=0.0_rk`
- Code: `aFunDimSusp=0.0_rk`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=2 shear-stress driven resuspension function
- Source: sediment_exchange.F90 (434)
- Formula (d⁻¹): `aFunDimSusp=(self%alpha/self%cVSetMain)*((shear-self%crt_shear)/self%ref_shear)**self%eta`
- Code: `aFunDimSusp=(self%alpha/self%cVSetMain)*((shear-self%crt_shear)/self%ref_shear)**self%eta`

### `aFunVegResus` [-] *Resuspension*
- DESC: macrophyte dependence of resuspension
- Source: sediment_exchange.F90 (418)
- Formula (d⁻¹): `aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)`
- Code: `aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)`

### `tCResusDOM` [g/m2/d] *Resuspension*
- DESC: resuspension of C DOM per group (dim nDOM)
- Source: sediment_exchange.F90 (455)
- Formula (d⁻¹): `tCResusDOM=rCDDOMS*tDResusDOM`
- Code: `tCResusDOM=rCDDOMS*tDResusDOM`

### `tCResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in C per group (dim nPOM)
- Source: sediment_exchange.F90 (450)
- Formula (d⁻¹): `tCResusPOM=rCDPOMS*tDResusPOM`
- Code: `tCResusPOM=rCDPOMS*tDResusPOM`

### `tDResusBareDead` [1/d] *Resuspension*
- DESC: resuspension due to shear stress and fish/bioturbation
- Source: sediment_exchange.F90 (439)
- Formula (d⁻¹): `tDResusBareDead=tDResusTauDead+BioTurb`
- Code: `tDResusBareDead=tDResusTauDead+BioTurb`

### `tDResusDead` [1/d] *Resuspension*
- DESC: resuspension corrected for macrophytes effect
- Source: sediment_exchange.F90 (440)
- Formula (d⁻¹): `tDResusDead=tDResusBareDead*aFunVegResus`
- Code: `tDResusDead=tDResusBareDead*aFunVegResus`

### `tDResusDOM` [g/m2/d] *Resuspension*
- DESC: resuspension of DW DOM per group (dim nDOM)
- Source: sediment_exchange.F90 (452)
- Formula (d⁻¹): `tDResusDOM=sDDOMS/(sum(sDPOMS)+NearZero)*tDResusPOMTot`
- Code: `tDResusDOM=sDDOMS/(sum(sDPOMS)+NearZero)*tDResusPOMTot`

### `tDResusIM` [g/m2/d] *Resuspension*
- DESC: inorganic matter resuspension flux
- Source: sediment_exchange.F90 (444)
- Formula (d⁻¹): `tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*tDResusDead`
- Code: `tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)`

### `tDResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in DW per group (dim nPOM)
- Source: sediment_exchange.F90 (447)
- Formula (d⁻¹): `tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*tDResusDead`
- Code: `tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)`

### `tDResusPOMTot` [g/m2/d] *Resuspension*
- DESC: Total POM resuspension in DW
- Source: sediment_exchange.F90 (446)
- Formula (d⁻¹): `tDResusPOMTot=sum(sDPOMS)/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*tDResusDead`
- Code: `tDResusPOMTot=sum(sDPOMS)/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)`

### `tDResusTauDead` [1/d] *Resuspension*
- DESC: resuspension due to shear stress
- Source: sediment_exchange.F90 (437-438)
- Formula (d⁻¹): `tDResusTauDead=min(aFunDimSusp, ((aFunDimSusp+NearZero)**(0.5_rk)))*((self%fLutum/self%fLutumRef)**(0.5_rk))*bPorS`
- Code: `tDResusTauDead=min(aFunDimSusp, ((aFunDimSusp +NearZero )**(0.5_rk))) & *((self%fLutum/ self%fLutumRef )** (0.5_rk))*bPorS`

### `tNResusDOM` [g/m2/d] *Resuspension*
- DESC: resuspension of N DOM per group (dim nDOM)
- Source: sediment_exchange.F90 (454)
- Formula (d⁻¹): `tNResusDOM=rNDDOMS*tDResusDOM`
- Code: `tNResusDOM=rNDDOMS*tDResusDOM`

### `tNResusNH4` [g/m2/d] *Resuspension*
- DESC: resuspension of NH4
- Source: sediment_exchange.F90 (461)
- Formula (d⁻¹): `tNResusNH4=sNH4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`
- Code: `tNResusNH4=sNH4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`

### `tNResusNO3` [g/m2/d] *Resuspension*
- DESC: resuspension of NO3
- Source: sediment_exchange.F90 (460)
- Formula (d⁻¹): `tNResusNO3=sNO3S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`
- Code: `tNResusNO3=sNO3S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`

### `tNResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in N per group (dim nPOM)
- Source: sediment_exchange.F90 (449)
- Formula (d⁻¹): `tNResusPOM=rNDPOMS*tDResusPOM`
- Code: `tNResusPOM=rNDPOMS*tDResusPOM`

### `tPResusAIM` [g/m2/d] *Resuspension*
- DESC: resuspension adsorbed PAIM
- Source: sediment_exchange.F90 (458)
- Formula (d⁻¹): `tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM`
- Code: `tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM`

### `tPResusDOM` [g/m2/d] *Resuspension*
- DESC: resuspension of P DOM per group (dim nDOM)
- Source: sediment_exchange.F90 (453)
- Formula (d⁻¹): `tPResusDOM=rPDDOMS*tDResusDOM`
- Code: `tPResusDOM=rPDDOMS*tDResusDOM`

### `tPResusPO4` [g/m2/d] *Resuspension*
- DESC: resuspension of PO4
- Source: sediment_exchange.F90 (459)
- Formula (d⁻¹): `tPResusPO4=sPO4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`
- Code: `tPResusPO4=sPO4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`

### `tPResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in P per group (dim nPOM)
- Source: sediment_exchange.F90 (448)
- Formula (d⁻¹): `tPResusPOM=rPDPOMS*tDResusPOM`
- Code: `tPResusPOM=rPDPOMS*tDResusPOM`

### `tSiResusPa` [g/m2/d] *Resuspension*
- DESC: POM resuspension in Si
- Source: sediment_exchange.F90 (457)
- Formula (d⁻¹): `tSiResusPa=rSiDPOMS*tDResusPOMTot`
- Code: `tSiResusPa=rSiDPOMS*tDResusPOMTot`

### `tSiResusSiO2` [g/m2/d] *Resuspension*
- DESC: resuspension of SiO2
- Source: sediment_exchange.F90 (462)
- Formula (d⁻¹): `tSiResusSiO2=sSiO2S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`
- Code: `tSiResusSiO2=sSiO2S/(sum(sDPOMS)+NearZero)*tDResusPOMTot`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=1 PCLake empirical logistic resuspension function (when uTm>=0.1)
- Source: resus_sed.F90 (216-217)
- Formula (d⁻¹): `aFunDimSusp=self%cSuspRef*((self%cSuspMin+self%cSuspMax/(1.0_rk+exp(self%cSuspSlope*(depth-self%hDepthSusp))))*((((self%cFetch+NearZero)/self%cFetchRef))**(0.5_rk)))`
- Code: `aFunDimSusp=self%cSuspRef*((self%cSuspMin+self%cSuspMax/(1.0_rk+exp(self%cSuspSlope* & (depth-self%hDepthSusp))))*((((self%cFetch +NearZero)/ self%cFetchRef) )** (0.5_rk)))`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=1 zero when temperature below 0.1
- Source: resus_sed.F90 (219)
- Formula (d⁻¹): `aFunDimSusp=0.0_rk`
- Code: `aFunDimSusp=0.0_rk`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=2 zero when shear below critical
- Source: resus_sed.F90 (223)
- Formula (d⁻¹): `aFunDimSusp=0.0_rk`
- Code: `aFunDimSusp=0.0_rk`

### `aFunDimSusp` [1/d] *Resuspension*
- DESC: qResus=2 shear-stress driven resuspension function
- Source: resus_sed.F90 (225)
- Formula (d⁻¹): `aFunDimSusp=(self%alpha/self%cVSetMain)*((shear-self%crt_shear)/self%ref_shear)**self%eta`
- Code: `aFunDimSusp=(self%alpha/self%cVSetMain)*((shear-self%crt_shear)/self%ref_shear)**self%eta`

### `aFunVegResus` [-] *Resuspension*
- DESC: macrophyte dependence of resuspension
- Source: resus_sed.F90 (209)
- Formula (d⁻¹): `aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)`
- Code: `aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)`

### `tDResusBareDead` [1/d] *Resuspension*
- DESC: resuspension due to shear stress and fish/bioturbation
- Source: resus_sed.F90 (230)
- Formula (d⁻¹): `tDResusBareDead=tDResusTauDead+BioTurb`
- Code: `tDResusBareDead=tDResusTauDead+BioTurb`

### `tDResusDead` [1/d] *Resuspension*
- DESC: resuspension corrected for macrophytes effect
- Source: resus_sed.F90 (231)
- Formula (d⁻¹): `tDResusDead=tDResusBareDead*aFunVegResus`
- Code: `tDResusDead=tDResusBareDead*aFunVegResus`

### `tDResusIM` [g/m2/d] *Resuspension*
- DESC: inorganic matter resuspension flux
- Source: resus_sed.F90 (235)
- Formula (d⁻¹): `tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*tDResusDead`
- Code: `tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*(tDResusDead/secs_pr_day)`

### `tDResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in DW (single group)
- Source: resus_sed.F90 (236)
- Formula (d⁻¹): `tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*tDResusDead`
- Code: `tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*(tDResusDead/secs_pr_day)`

### `tDResusTauDead` [1/d] *Resuspension*
- DESC: resuspension due to shear stress
- Source: resus_sed.F90 (228-229)
- Formula (d⁻¹): `tDResusTauDead=min(aFunDimSusp, ((aFunDimSusp+NearZero)**(0.5_rk)))*((self%fLutum/self%fLutumRef)**(0.5_rk))*bPorS`
- Code: `tDResusTauDead=min(aFunDimSusp, ((aFunDimSusp +NearZero )**(0.5_rk))) & *((self%fLutum/ self%fLutumRef )** (0.5_rk))*bPorS`

### `tNResusNH4` [g/m2/d] *Resuspension*
- DESC: resuspension of NH4
- Source: resus_sed.F90 (243)
- Formula (d⁻¹): `tNResusNH4=sNH4S/(sDPOMS+NearZero)*tDResusPOM`
- Code: `tNResusNH4=sNH4S/(sDPOMS+NearZero)*tDResusPOM`

### `tNResusNO3` [g/m2/d] *Resuspension*
- DESC: resuspension of NO3
- Source: resus_sed.F90 (242)
- Formula (d⁻¹): `tNResusNO3=sNO3S/(sDPOMS+NearZero)*tDResusPOM`
- Code: `tNResusNO3=sNO3S/(sDPOMS+NearZero)*tDResusPOM`

### `tNResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in N
- Source: resus_sed.F90 (238)
- Formula (d⁻¹): `tNResusPOM=rNDPOMS*tDResusPOM`
- Code: `tNResusPOM=rNDPOMS*tDResusPOM`

### `tPResusAIM` [g/m2/d] *Resuspension*
- DESC: resuspension adsorbed PAIM
- Source: resus_sed.F90 (240)
- Formula (d⁻¹): `tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM`
- Code: `tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM`

### `tPResusPO4` [g/m2/d] *Resuspension*
- DESC: resuspension of PO4
- Source: resus_sed.F90 (241)
- Formula (d⁻¹): `tPResusPO4=sPO4S/(sDPOMS+NearZero)*tDResusPOM`
- Code: `tPResusPO4=sPO4S/(sDPOMS+NearZero)*tDResusPOM`

### `tPResusPOM` [g/m2/d] *Resuspension*
- DESC: POM resuspension in P
- Source: resus_sed.F90 (237)
- Formula (d⁻¹): `tPResusPOM=rPDPOMS*tDResusPOM`
- Code: `tPResusPOM=rPDPOMS*tDResusPOM`

### `tSiResusPa` [g/m2/d] *Resuspension*
- DESC: POM resuspension in Si
- Source: resus_sed.F90 (239)
- Formula (d⁻¹): `tSiResusPa=rSiDPOMS*tDResusPOM`
- Code: `tSiResusPa=rSiDPOMS*tDResusPOM`

## Season phenology

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 1: winter/summer transition, normal within-year)
- Source: macrophytes.F90 (936)
- Formula (d⁻¹): `0.5*(fRootVegWin + fRootVegSum) + 0.5*(fRootVegWin - fRootVegSum)*cos(Pi/cLengAllo * (Day - aDayInitVeg))`
- Code: `if (season == 1 .AND. .NOT. yeartrans) bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) + 0.5*(self%fRootVegWin - self%fRootVegSum)*cos(Pi/self%cLengAllo * (Day - aDayInitVeg))`

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 1: winter/summer transition, inherited from previous year)
- Source: macrophytes.F90 (933)
- Formula (d⁻¹): `0.5*(fRootVegWin + fRootVegSum) + 0.5*(fRootVegWin - fRootVegSum)*cos(Pi/cLengAllo * (Day + 366.0 - aDayInitVeg))`
- Code: `if (season == 1 .AND. yeartrans) bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) + 0.5*(self%fRootVegWin - self%fRootVegSum)*cos(Pi/self%cLengAllo * (Day + 366.0_rk - aDayInitVeg))`

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 2: summer)
- Source: macrophytes.F90 (940)
- Formula (d⁻¹): `fRootVegSum`
- Code: `if (season == 2) bfRootVeg_int = self%fRootVegSum`

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 3: summer/winter transition, normal within-year)
- Source: macrophytes.F90 (946)
- Formula (d⁻¹): `0.5*(fRootVegWin + fRootVegSum) - 0.5*(fRootVegWin - fRootVegSum)*cos(Pi/cLengAllo * (Day - cDayWinVeg))`
- Code: `if (season == 3 .AND. .NOT. yeartrans) bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) - 0.5*(self%fRootVegWin - self%fRootVegSum)*cos(Pi/self%cLengAllo * (Day - self%cDayWinVeg))`

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 3: summer/winter transition, inherited from previous year)
- Source: macrophytes.F90 (943)
- Formula (d⁻¹): `0.5*(fRootVegWin + fRootVegSum) - 0.5*(fRootVegWin - fRootVegSum)*cos(Pi/cLengAllo * (Day + 366.0 - cDayWinVeg))`
- Code: `if (season == 3 .AND. yeartrans) bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) - 0.5*(self%fRootVegWin - self%fRootVegSum)*cos(Pi/self%cLengAllo * (Day + 366.0_rk - self%cDayWinVeg))`

### `bfRootVeg` [-] *Season phenology*
- DESC: root fraction (season 4: winter)
- Source: macrophytes.F90 (951)
- Formula (d⁻¹): `fRootVegWin`
- Code: `if (season == 4) bfRootVeg_int = self%fRootVegWin; aDayInitVeg = -1.0_rk (reset)`

### `season` [-] *Season phenology*
- DESC: determine season (spring/summer case: Day<cDayWinVeg AND Day>=cDaySumVegMin)
- Source: macrophytes.F90 (880)
- Formula (d⁻¹): `season=4 (winter); if first day of growing season (aDayInitVeg==-1 AND uTm>=cTmInitVeg): season=1, aDayInitVeg=Day; elseif in transition (Day<=aDayInitVeg+cLengAllo): season=1; elseif past transition: season=2 (summer)`
- Code: `if (Day < self%cDayWinVeg .AND. Day >= self%cDaySumVegMin) then [spring/summer hemisphere logic with season=1/2/4]`

### `season` [-] *Season phenology*
- DESC: determine season (winter case: Day>=cDayWinVeg AND Day<cDaySumVegMin)
- Source: macrophytes.F90 (890)
- Formula (d⁻¹): `season=3 (summer/winter transition) if Day<cDayWinVeg+cLengAllo; season=4 (winter) if past transition`
- Code: `elseif (Day >= self%cDayWinVeg .AND. Day < self%cDaySumVegMin) then [winter hemisphere logic with season=3/4]`

### `season` [-] *Season phenology*
- DESC: determine season (beginning of year: Day<cDayWinVeg AND Day<cDaySumVegMin)
- Source: macrophytes.F90 (896)
- Formula (d⁻¹): `depends on cDayWinVeg vs cDaySumVegMin; yeartrans=.true. if inherited transition from previous year`
- Code: `elseif (Day < self%cDayWinVeg .AND. Day < self%cDaySumVegMin) then [year start logic with yeartrans flag]`

### `season` [-] *Season phenology*
- DESC: determine season (end of year: Day>=cDayWinVeg AND Day>=cDaySumVegMin)
- Source: macrophytes.F90 (912)
- Formula (d⁻¹): `depends on cDayWinVeg vs cDaySumVegMin; summer case triggers first-day check elseif (Day >= self%cDayWinVeg .AND. Day >= self%cDaySumVegMin) then [year end logic with season=1/2/3/4]`
- Code: ``

## Sedimentation

### `aFunTauTmSet` [-] *Sedimentation*
- DESC: correction factor for settling rate (<=1), net settling rate
- Source: sediment_exchange.F90 (469)
- Formula (d⁻¹): `aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp+NearZero)**(0.5_rk)))*uFunTmSed`
- Code: `aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp +NearZero )**(0.5_rk)))*uFunTmSed`

### `tCSedPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in C per group (dim nPOM)
- Source: sediment_exchange.F90 (484)
- Formula (d⁻¹): `tCSedPOM=uCorVSedPOM*sCPOMW`
- Code: `tCSedPOM=uCorVSedPOM*sCPOMW`

### `tDSedIM` [g/m2/s] *Sedimentation*
- DESC: sedimentation IM
- Source: sediment_exchange.F90 (476)
- Formula (d⁻¹): `tDSedIM=uCorVSedIM*sDIMW`
- Code: `tDSedIM=uCorVSedIM*sDIMW`

### `tDSedPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation flux of POM in DW per group (dim nPOM)
- Source: sediment_exchange.F90 (481)
- Formula (d⁻¹): `tDSedPOM=uCorVSedPOM*sDPOMW`
- Code: `tDSedPOM=uCorVSedPOM*sDPOMW`

### `tNSedPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in N per group (dim nPOM)
- Source: sediment_exchange.F90 (483)
- Formula (d⁻¹): `tNSedPOM=uCorVSedPOM*sNPOMW`
- Code: `tNSedPOM=uCorVSedPOM*sNPOMW`

### `tPSedAIM` [g/m2/s] *Sedimentation*
- DESC: sedimentation PAIM
- Source: sediment_exchange.F90 (477)
- Formula (d⁻¹): `tPSedAIM=sPAIMW/(sDIMW+NearZero)*tDSedIM`
- Code: `tPSedAIM=sPAIMW/(sDIMW+NearZero)*tDSedIM`

### `tPSedPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in P per group (dim nPOM)
- Source: sediment_exchange.F90 (482)
- Formula (d⁻¹): `tPSedPOM=uCorVSedPOM*sPPOMW`
- Code: `tPSedPOM=uCorVSedPOM*sPPOMW`

### `tSiSedPa` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in Si
- Source: sediment_exchange.F90 (488)
- Formula (d⁻¹): `tSiSedPa=uCorVSedSiPa*sSiPaW`
- Code: `tSiSedPa=uCorVSedSiPa*sSiPaW`

### `uCorVSedIM` [m/d] *Sedimentation*
- DESC: sedimentation velocity of IM
- Source: sediment_exchange.F90 (473)
- Formula (d⁻¹): `uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet`
- Code: `uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet`

### `uCorVSedIM` [m/s] *Sedimentation*
- DESC: sedimentation velocity of IM converted to s-1
- Source: sediment_exchange.F90 (474)
- Formula (d⁻¹): `uCorVSedIM=uCorVSedIM`
- Code: `uCorVSedIM=uCorVSedIM/secs_pr_day`

### `uCorVSedPOM` [m/d] *Sedimentation*
- DESC: sedimentation velocity of POM per group (dim nPOM)
- Source: sediment_exchange.F90 (479)
- Formula (d⁻¹): `uCorVSedPOM=self%cVSedPOM*aFunTauTmSet`
- Code: `uCorVSedPOM=self%cVSedPOM*aFunTauTmSet`

### `uCorVSedPOM` [m/s] *Sedimentation*
- DESC: sedimentation velocity of POM converted to s-1 (dim nPOM)
- Source: sediment_exchange.F90 (480)
- Formula (d⁻¹): `uCorVSedPOM=uCorVSedPOM`
- Code: `uCorVSedPOM=uCorVSedPOM/secs_pr_day`

### `uCorVSedSiPa` [m/d] *Sedimentation*
- DESC: sedimentation velocity of particulate Si
- Source: sediment_exchange.F90 (486)
- Formula (d⁻¹): `uCorVSedSiPa=self%cVSedSiPa*aFunTauTmSet`
- Code: `uCorVSedSiPa=self%cVSedSiPa*aFunTauTmSet`

### `uCorVSedSiPa` [m/s] *Sedimentation*
- DESC: sedimentation velocity of particulate Si converted to s-1
- Source: sediment_exchange.F90 (487)
- Formula (d⁻¹): `uCorVSedSiPa=uCorVSedSiPa`
- Code: `uCorVSedSiPa=uCorVSedSiPa/secs_pr_day`

### `aFunTauTmSet` [-] *Sedimentation*
- DESC: correction factor for settling rate (<=1), net settling rate
- Source: resus_sed.F90 (250)
- Formula (d⁻¹): `aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp+NearZero)**(0.5_rk)))*uFunTmSed`
- Code: `aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp +NearZero )**(0.5_rk)))*uFunTmSed`

### `tDSetIM` [g/m2/s] *Sedimentation*
- DESC: sedimentation IM
- Source: resus_sed.F90 (256)
- Formula (d⁻¹): `tDSetIM=uCorVSedIM*sDIMW`
- Code: `tDSetIM=uCorVSedIM*sDIMW`

### `tDSetPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation flux of POM in DW
- Source: resus_sed.F90 (260)
- Formula (d⁻¹): `tDSetPOM=uCorVSedPOM*sDPOMW`
- Code: `tDSetPOM=uCorVSedPOM*sDPOMW`

### `tNSetPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in N
- Source: resus_sed.F90 (262)
- Formula (d⁻¹): `tNSetPOM=uCorVSedPOM*sNPOMW`
- Code: `tNSetPOM=uCorVSedPOM*sNPOMW`

### `tPSetAIM` [g/m2/s] *Sedimentation*
- DESC: sedimentation PAIM
- Source: resus_sed.F90 (257)
- Formula (d⁻¹): `tPSetAIM=sPAIMW/(sDIMW+NearZero)*tDSetIM`
- Code: `tPSetAIM=sPAIMW/(sDIMW+NearZero)*tDSetIM`

### `tPSetPOM` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in P
- Source: resus_sed.F90 (261)
- Formula (d⁻¹): `tPSetPOM=uCorVSedPOM*sPPOMW`
- Code: `tPSetPOM=uCorVSedPOM*sPPOMW`

### `tSiSetPa` [g/m2/s] *Sedimentation*
- DESC: sedimentation of POM in Si
- Source: resus_sed.F90 (263)
- Formula (d⁻¹): `tSiSetPa=uCorVSedPOM*sSiPaW`
- Code: `tSiSetPa=uCorVSedPOM*sSiPaW`

### `uCorVSedIM` [m/d] *Sedimentation*
- DESC: sedimentation velocity of IM
- Source: resus_sed.F90 (254)
- Formula (d⁻¹): `uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet`
- Code: `uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet`

### `uCorVSedIM` [m/s] *Sedimentation*
- DESC: sedimentation velocity of IM converted to s-1
- Source: resus_sed.F90 (255)
- Formula (d⁻¹): `uCorVSedIM=uCorVSedIM`
- Code: `uCorVSedIM=uCorVSedIM/secs_pr_day`

### `uCorVSedPOM` [m/d] *Sedimentation*
- DESC: sedimentation velocity of POM
- Source: resus_sed.F90 (258)
- Formula (d⁻¹): `uCorVSedPOM=self%cVSedPOM*aFunTauTmSet`
- Code: `uCorVSedPOM=self%cVSedPOM*aFunTauTmSet`

### `uCorVSedPOM` [m/s] *Sedimentation*
- DESC: sedimentation velocity of POM converted to s-1
- Source: resus_sed.F90 (259)
- Formula (d⁻¹): `uCorVSedPOM=uCorVSedPOM`
- Code: `uCorVSedPOM=uCorVSedPOM/secs_pr_day`

## Si mineralization

### `wSiMinPaW` [-] *Si mineralization*
- DESC: particulate_OM_Si mineralization
- Source: abiotic_water.F90 (202-202)
- Formula (d⁻¹): `kSiMinPaW * uFunTmMinSiW * sSiPaW`
- Code: `wSiMinPaW = self%kSiMinPaW * uFunTmMinSiW * sSiPaW`

### `tSiMinPaS` [-] *Si mineralization*
- DESC: calculate upper sediment Si decomposition
- Source: abiotic_sediment.F90 (275-275)
- Formula (d⁻¹): `kSiMinPaS*uFunTmMinSiS*sSiPaS`
- Code: `tSiMinPaS = self%kSiMinPaS*uFunTmMinSiS*sSiPaS`

### `uFunTmMinSiS` [-] *Si mineralization*
- DESC: remineralization Si temperature function
- Source: abiotic_sediment.F90 (274-274)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaMinSiS)`
- Code: `uFunTmMinSiS = uFunTmArrh(uTm,self%cThetaMinSiS)`

## Stage coupling

### `eAge` [-] *Stage coupling*
- DESC: calculate maturation progress
- Source: fish.F90 (899)
- Formula (d⁻¹): `eAge = ((sDSiz-self%cDinit)/(self%cDfin-self%cDinit))`
- Code: `eAge = ((sDSiz-self%cDinit)/(self%cDfin-self%cDinit))`

### `fAgeFish` [-] *Stage coupling*
- DESC: calculate specific maturation rate
- Source: fish.F90 (901)
- Formula (d⁻¹): `fAgeFish = max(0._rk,min(1._rk,((((1._rk- k_mat)/ k_mat)**(2._rk*eAge)-1._rk)/(((1._rk- k_mat)/ k_mat)**(2._rk)-1._rk))))`
- Code: `fAgeFish = max(0._rk,min(1._rk,((((1._rk- k_mat)/ k_mat)**(2._rk*eAge)-1._rk)/(((1._rk- k_mat)/ k_mat)**(2._rk)-1._rk))))/secs_pr_day`

### `FiJu_Res_new` [-] *Stage coupling*
- DESC: calculate new juvenile reserve fraction
- Source: fish.F90 (1243)
- Formula (d⁻¹): `FiJu_Res_new = (FiJu_Res + sFRes*rDReprFish*self%fReproFish)/(1._rk + rDReprFish*self%fReproFish)`
- Code: `FiJu_Res_new = (FiJu_Res + sFRes*rDReprFish*self%fReproFish)/(1._rk + rDReprFish*self%fReproFish)`

### `FiJu_Siz_new` [-] *Stage coupling*
- DESC: calculate new juvenile mean size
- Source: fish.F90 (1244)
- Formula (d⁻¹): `FiJu_Siz_new = (FiJu_D+tDReprFish*self%fReproFish)/(FiJu_D/FiJu_Siz+tDReprFish*self%fReproFish/self%cDegg)`
- Code: `FiJu_Siz_new = (FiJu_D+tDReprFish*self%fReproFish)/(FiJu_D/FiJu_Siz+tDReprFish*self%fReproFish/self%cDegg)`

### `k_mat` [-] *Stage coupling*
- DESC: calculate current daily growth rate (hardcoded)
- Source: fish.F90 (900)
- Formula (d⁻¹): `k_mat = 0.5e-6_rk`
- Code: `k_mat = 0.5e-6_rk !rG*secs_pr_day*1e-5_rk`

### `rDReprFish` [-] *Stage coupling*
- DESC: calculate total reproduction investment fraction
- Source: fish.F90 (1238)
- Formula (d⁻¹): `rDReprFish = self%fGonad*(sFRes-self%fResmin)/(self%fResMax-self%fResMin)`
- Code: `rDReprFish = self%fGonad*(sFRes-self%fResmin)/(self%fResMax-self%fResMin)`

### `sFReproSet` [-] *Stage coupling*
- DESC: set fish reserve after reproduction
- Source: fish.F90 (1245)
- Formula (d⁻¹): `_SET_(self%id_sFRes,sFRes-tDReprFish/sDFi)`
- Code: `_SET_(self%id_sFRes,sFRes-tDReprFish/sDFi)`

### `tCAgeFish` [-] *Stage coupling*
- DESC: calculate aging C flux
- Source: fish.F90 (906)
- Formula (d⁻¹): `tCAgeFish = rCDFi * tDAgeFish`
- Code: `tCAgeFish = rCDFi * tDAgeFish`

### `tCReprFish` [-] *Stage coupling*
- DESC: calculate C reproduction flux
- Source: fish.F90 (1242)
- Formula (d⁻¹): `tCReprFish = tDReprFish*rCDFi`
- Code: `tCReprFish = tDReprFish*rCDFi`

### `tCReproPOM` [-] *Stage coupling*
- DESC: diagnostic CPOMW from reproduction
- Source: fish.F90 (1264)
- Formula (d⁻¹): `tCReproPOM = tCReprFish*(1.0_rk-self%fReproFish)`
- Code: `tCReproPOM = tCReprFish*(1.0_rk-self%fReproFish)`

### `tDAgeFish` [-] *Stage coupling*
- DESC: calculate maturation flux
- Source: fish.F90 (902)
- Formula (d⁻¹): `tDAgeFish = fAgeFish*sDFi`
- Code: `tDAgeFish = fAgeFish*sDFi`

### `tDAgeRes` [-] *Stage coupling*
- DESC: calculate rate of change of next stage reserve fraction
- Source: fish.F90 (910)
- Formula (d⁻¹): `tDAgeRes = min(1._rk/3600._rk,(sFRes - FiAd_Res)*(tDAgeFish/FiAd_D))`
- Code: `tDAgeRes = min(1._rk/3600._rk,(sFRes - FiAd_Res)*(tDAgeFish/FiAd_D)) !(tDAgeFish+FiAd_D)))`

### `tDAgeSiz` [-] *Stage coupling*
- DESC: calculate rate of change of next stage mean size
- Source: fish.F90 (911)
- Formula (d⁻¹): `tDAgeSiz = (tDAgeFish/FiAd_D)*((FiAd_Siz+NearZero)/self%cDfin)*(self%cDfin-FiAd_Siz)`
- Code: `tDAgeSiz = (tDAgeFish/FiAd_D)*((FiAd_Siz+NearZero)/self%cDfin)*(self%cDfin-FiAd_Siz)`

### `tDReprFish` [-] *Stage coupling*
- DESC: calculate total reproduction investment
- Source: fish.F90 (1239)
- Formula (d⁻¹): `tDReprFish = sDFi*rDReprFish`
- Code: `tDReprFish = sDFi*rDReprFish`

### `tDReproPOM` [-] *Stage coupling*
- DESC: diagnostic DPOMW from reproduction
- Source: fish.F90 (1261)
- Formula (d⁻¹): `tDReproPOM = tDReprFish*(1.0_rk-self%fReproFish)`
- Code: `tDReproPOM = tDReprFish*(1.0_rk-self%fReproFish)`

### `tDSiz` [-] *Stage coupling*
- DESC: calculate rate of change of individual size
- Source: fish.F90 (903)
- Formula (d⁻¹): `tDSiz = tDSiz - abs(fAgeFish*(sDSiz-self%cDfin))`
- Code: `tDSiz = tDSiz - abs(fAgeFish*(sDSiz-self%cDfin))`

### `tNAgeFish` [-] *Stage coupling*
- DESC: calculate aging N flux
- Source: fish.F90 (905)
- Formula (d⁻¹): `tNAgeFish = rNDFi * tDAgeFish`
- Code: `tNAgeFish = rNDFi * tDAgeFish`

### `tNReprFish` [-] *Stage coupling*
- DESC: calculate N reproduction flux
- Source: fish.F90 (1240)
- Formula (d⁻¹): `tNReprFish = tDReprFish*rNDFi`
- Code: `tNReprFish = tDReprFish*rNDFi`

### `tNReproPOM` [-] *Stage coupling*
- DESC: diagnostic NPOMW from reproduction
- Source: fish.F90 (1262)
- Formula (d⁻¹): `tNReproPOM = tNReprFish*(1.0_rk-self%fReproFish)`
- Code: `tNReproPOM = tNReprFish*(1.0_rk-self%fReproFish)`

### `tPAgeFish` [-] *Stage coupling*
- DESC: calculate aging P flux
- Source: fish.F90 (904)
- Formula (d⁻¹): `tPAgeFish = rPDFi * tDAgeFish`
- Code: `tPAgeFish = rPDFi * tDAgeFish`

### `tPReprFish` [-] *Stage coupling*
- DESC: calculate P reproduction flux
- Source: fish.F90 (1241)
- Formula (d⁻¹): `tPReprFish = tDReprFish*rPDFi`
- Code: `tPReprFish = tDReprFish*rPDFi`

### `tPReproPOM` [-] *Stage coupling*
- DESC: diagnostic PPOMW from reproduction
- Source: fish.F90 (1263)
- Formula (d⁻¹): `tPReproPOM = tPReprFish*(1.0_rk-self%fReproFish)`
- Code: `tPReproPOM = tPReprFish*(1.0_rk-self%fReproFish)`

## Starvation mortality

### `tCMortFi` [-] *Starvation mortality*
- DESC: calculate loss of C from mortality (starvation)
- Source: fish.F90 (892)
- Formula (d⁻¹): `tCMortFi = rCDFi * tDMortFi`
- Code: `tCMortFi = rCDFi * tDMortFi`

### `tDMortFi` [-] *Starvation mortality*
- DESC: calculate added mortality from starvation
- Source: fish.F90 (889)
- Formula (d⁻¹): `tDMortFi = tDMortFi + min(0.2_rk,sDFi*self%cMortStarv*(self%fResMin/(1.0_rk-self%fResMin)*(1.0_rk/fRes_now)-1.0_rk))`
- Code: `tDMortFi = tDMortFi + min(0.2_rk,sDFi*self%cMortStarv*(self%fResMin/(1.0_rk-self%fResMin)*(1.0_rk/fRes_now)-1.0_rk))/secs_pr_day`

### `tNMortFi` [-] *Starvation mortality*
- DESC: calculate loss of N from mortality (starvation)
- Source: fish.F90 (891)
- Formula (d⁻¹): `tNMortFi = rNDFi * tDMortFi`
- Code: `tNMortFi = rNDFi * tDMortFi`

### `tPMortFi` [-] *Starvation mortality*
- DESC: calculate loss of P from mortality (starvation)
- Source: fish.F90 (890)
- Formula (d⁻¹): `tPMortFi = rPDFi * tDMortFi`
- Code: `tPMortFi = rPDFi * tDMortFi`

## State updates

### `bot_pel_conv` [-] *State updates*
- DESC: bottom-pelagic conversion factor (retrieved)
- Source: macrophytes.F90 (684)
- Formula (d⁻¹): `-`
- Code: `_GET_HORIZONTAL_(self%id_bot_pel_conv, bot_pel_conv)`

### `sCVeg` [ODE] *State updates*
- DESC: set macrophyte C derivative
- Source: macrophytes.F90 (682)
- Formula (d⁻¹): `tCBedVeg`
- Code: `_SET_BOTTOM_ODE_(self%id_sCVeg, tCBedVeg)`

### `sCVeg_PV` [bottom exchange] *State updates*
- DESC: pelagic mirror C exchange
- Source: macrophytes.F90 (688)
- Formula (d⁻¹): `tCBedVeg * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sCVeg_PV, tCBedVeg*bot_pel_conv)`

### `sDVeg` [ODE] *State updates*
- DESC: set macrophyte DW derivative
- Source: macrophytes.F90 (679)
- Formula (d⁻¹): `tDBedVeg`
- Code: `_SET_BOTTOM_ODE_(self%id_sDVeg, tDBedVeg)`

### `sDVeg_PV` [bottom exchange] *State updates*
- DESC: pelagic mirror DW exchange
- Source: macrophytes.F90 (685)
- Formula (d⁻¹): `tDBedVeg * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sDVeg_PV, tDBedVeg*bot_pel_conv)`

### `sNVeg` [ODE] *State updates*
- DESC: set macrophyte N derivative
- Source: macrophytes.F90 (680)
- Formula (d⁻¹): `tNBedVeg`
- Code: `_SET_BOTTOM_ODE_(self%id_sNVeg, tNBedVeg)`

### `sNVeg_PV` [bottom exchange] *State updates*
- DESC: pelagic mirror N exchange
- Source: macrophytes.F90 (687)
- Formula (d⁻¹): `tNBedVeg * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sNVeg_PV, tNBedVeg*bot_pel_conv)`

### `sPVeg` [ODE] *State updates*
- DESC: set macrophyte P derivative
- Source: macrophytes.F90 (681)
- Formula (d⁻¹): `tPBedVeg`
- Code: `_SET_BOTTOM_ODE_(self%id_sPVeg, tPBedVeg)`

### `sPVeg_PV` [bottom exchange] *State updates*
- DESC: pelagic mirror P exchange
- Source: macrophytes.F90 (686)
- Formula (d⁻¹): `tPBedVeg * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_sPVeg_PV, tPBedVeg*bot_pel_conv)`

## State updates (external sediment PV)

### `CDOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror C DOM exchange
- Source: macrophytes.F90 (723)
- Formula (d⁻¹): `tCBedDOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV, tCBedDOMS*bot_pel_conv)`

### `CPOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror C POM exchange
- Source: macrophytes.F90 (715)
- Formula (d⁻¹): `tCBedPOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCBedPOMS*bot_pel_conv)`

### `DDOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror DW DOM exchange
- Source: macrophytes.F90 (720)
- Formula (d⁻¹): `tDBedDOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV, tDBedDOMS*bot_pel_conv)`

### `DPOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror DW POM exchange
- Source: macrophytes.F90 (712)
- Formula (d⁻¹): `tDBedPOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDBedPOMS*bot_pel_conv)`

### `NDOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror N DOM exchange
- Source: macrophytes.F90 (721)
- Formula (d⁻¹): `tNBedDOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV, tNBedDOMS*bot_pel_conv)`

### `NPOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror N POM exchange
- Source: macrophytes.F90 (713)
- Formula (d⁻¹): `tNBedPOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNBedPOMS*bot_pel_conv)`

### `PDOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror P DOM exchange
- Source: macrophytes.F90 (722)
- Formula (d⁻¹): `tPBedDOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV, tPBedDOMS*bot_pel_conv)`

### `PPOMpoolS_PV` [bottom exchange] *State updates (external sediment PV)*
- DESC: pelagic mirror P POM exchange
- Source: macrophytes.F90 (714)
- Formula (d⁻¹): `tPBedPOMS * bot_pel_conv`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPBedPOMS*bot_pel_conv)`

## State updates (external sediment)

### `CDOMpoolS` [ODE] *State updates (external sediment)*
- DESC: C DOM flux to sediment
- Source: macrophytes.F90 (719)
- Formula (d⁻¹): `tCBedDOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_CDOMpoolS, tCBedDOMS)`

### `CPOMpoolS` [ODE] *State updates (external sediment)*
- DESC: C POM flux to sediment
- Source: macrophytes.F90 (711)
- Formula (d⁻¹): `tCBedPOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCBedPOMS)`

### `DDOMpoolS` [ODE] *State updates (external sediment)*
- DESC: DW DOM flux to sediment
- Source: macrophytes.F90 (716)
- Formula (d⁻¹): `tDBedDOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_DDOMpoolS, tDBedDOMS)`

### `DPOMpoolS` [ODE] *State updates (external sediment)*
- DESC: DW POM flux to sediment
- Source: macrophytes.F90 (708)
- Formula (d⁻¹): `tDBedPOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDBedPOMS)`

### `NDOMpoolS` [ODE] *State updates (external sediment)*
- DESC: N DOM flux to sediment
- Source: macrophytes.F90 (717)
- Formula (d⁻¹): `tNBedDOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_NDOMpoolS, tNBedDOMS)`

### `NH4poolS` [ODE] *State updates (external sediment)*
- DESC: NH4 flux to sediment
- Source: macrophytes.F90 (705)
- Formula (d⁻¹): `tNBedNH4S`
- Code: `_SET_BOTTOM_ODE_(self%id_NH4poolS, tNBedNH4S)`

### `NO3poolS` [ODE] *State updates (external sediment)*
- DESC: NO3 flux to sediment
- Source: macrophytes.F90 (706)
- Formula (d⁻¹): `tNBedNO3S`
- Code: `_SET_BOTTOM_ODE_(self%id_NO3poolS, tNBedNO3S)`

### `NPOMpoolS` [ODE] *State updates (external sediment)*
- DESC: N POM flux to sediment
- Source: macrophytes.F90 (709)
- Formula (d⁻¹): `tNBedPOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNBedPOMS)`

### `PDOMpoolS` [ODE] *State updates (external sediment)*
- DESC: P DOM flux to sediment
- Source: macrophytes.F90 (718)
- Formula (d⁻¹): `tPBedDOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_PDOMpoolS, tPBedDOMS)`

### `PO4poolS` [ODE] *State updates (external sediment)*
- DESC: PO4 flux to sediment
- Source: macrophytes.F90 (707)
- Formula (d⁻¹): `tPBedPO4S`
- Code: `_SET_BOTTOM_ODE_(self%id_PO4poolS, tPBedPO4S)`

### `PPOMpoolS` [ODE] *State updates (external sediment)*
- DESC: P POM flux to sediment
- Source: macrophytes.F90 (710)
- Formula (d⁻¹): `tPBedPOMS`
- Code: `_SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPBedPOMS)`

## State updates (external water)

### `CDOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: C DOM flux to water column
- Source: macrophytes.F90 (704)
- Formula (d⁻¹): `wCBedDOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolW, wCBedDOMW)`

### `CPOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: C POM flux to water column
- Source: macrophytes.F90 (700)
- Formula (d⁻¹): `wCBedPOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolW, wCBedPOMW)`

### `DDOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: DW DOM flux to water column
- Source: macrophytes.F90 (701)
- Formula (d⁻¹): `wDBedDOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolW, wDBedDOMW)`

### `DPOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: DW POM flux to water column
- Source: macrophytes.F90 (697)
- Formula (d⁻¹): `wDBedPOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolW, wDBedPOMW)`

### `NDOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: N DOM flux to water column
- Source: macrophytes.F90 (702)
- Formula (d⁻¹): `wNBedDOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolW, wNBedDOMW)`

### `NH4poolW` [bottom exchange] *State updates (external water)*
- DESC: NH4 flux to water column
- Source: macrophytes.F90 (692)
- Formula (d⁻¹): `wNBedNH4W`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NH4poolW, wNBedNH4W)`

### `NO3poolW` [bottom exchange] *State updates (external water)*
- DESC: NO3 flux to water column
- Source: macrophytes.F90 (693)
- Formula (d⁻¹): `wNBedNO3W`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NO3poolW, wNBedNO3W)`

### `NPOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: N POM flux to water column
- Source: macrophytes.F90 (698)
- Formula (d⁻¹): `wNBedPOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolW, wNBedPOMW)`

### `O2poolW` [bottom exchange] *State updates (external water)*
- DESC: O2 flux to water column
- Source: macrophytes.F90 (695)
- Formula (d⁻¹): `tO2BedW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_O2poolW, tO2BedW)`

### `PDOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: P DOM flux to water column
- Source: macrophytes.F90 (703)
- Formula (d⁻¹): `wPBedDOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolW, wPBedDOMW)`

### `PO4poolW` [bottom exchange] *State updates (external water)*
- DESC: PO4 flux to water column
- Source: macrophytes.F90 (694)
- Formula (d⁻¹): `wPBedPO4W`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PO4poolW, wPBedPO4W)`

### `PPOMpoolW` [bottom exchange] *State updates (external water)*
- DESC: P POM flux to water column
- Source: macrophytes.F90 (699)
- Formula (d⁻¹): `wPBedPOMW`
- Code: `_SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolW, wPBedPOMW)`

## State variables

### `sDIMW` [g/m3] *State variables*
- DESC: inorganic matter
- Source: abiotic_water.F90 (97-97)
- Formula (d⁻¹): `initial_value=5.0_rk; vertical_movement=cVSetIM`
- Code: `call self%register_state_variable(self%id_sDIMW, 'sDIMW', 'g/m3','inorganic matter', initial_value=5.0_rk, minimum=0.0_rk,vertical_movement=self%cVSetIM, no_river_dilution=.TRUE.)`

### `sNH4W` [g/m3] *State variables*
- DESC: ammonium
- Source: abiotic_water.F90 (103-103)
- Formula (d⁻¹): `initial_value=0.1_rk`
- Code: `call self%register_state_variable(self%id_sNH4W, 'sNH4W', 'g/m3','ammonium', initial_value=0.1_rk, minimum=0.0_rk, no_river_dilution=.TRUE.)`

### `sNO3W` [g/m3] *State variables*
- DESC: nitrate
- Source: abiotic_water.F90 (104-104)
- Formula (d⁻¹): `initial_value=0.1_rk`
- Code: `call self%register_state_variable(self%id_sNO3W, 'sNO3W', 'g/m3','nitrate', initial_value=0.1_rk, minimum=0.0_rk, no_river_dilution=.TRUE.)`

### `sO2W` [g/m3] *State variables*
- DESC: oxygen
- Source: abiotic_water.F90 (107-107)
- Formula (d⁻¹): `initial_value=10.0_rk`
- Code: `call self%register_state_variable(self%id_sO2W, 'sO2W', 'g/m3','oxygen', initial_value=10.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE.)`

### `sPAIMW` [g/m3] *State variables*
- DESC: IM-adsorbed P
- Source: abiotic_water.F90 (102-102)
- Formula (d⁻¹): `initial_value=0.0_rk; vertical_movement=cVSetIM`
- Code: `call self%register_state_variable(self%id_sPAIMW, 'sPAIMW', 'g/m3','IM-adsorbed P', initial_value=0.0_rk, minimum=0.0_rk,vertical_movement=self%cVSetIM, no_river_dilution=.TRUE.)`

### `sPO4W` [g/m3] *State variables*
- DESC: phosphate
- Source: abiotic_water.F90 (101-101)
- Formula (d⁻¹): `initial_value=0.01_rk`
- Code: `call self%register_state_variable(self%id_sPO4W, 'sPO4W', 'g/m3','phosphate', initial_value=0.01_rk, minimum=0.0_rk, no_river_dilution=.TRUE.)`

### `sSiO2W` [g/m3] *State variables*
- DESC: silica dioxide
- Source: abiotic_water.F90 (105-105)
- Formula (d⁻¹): `initial_value=3.0_rk`
- Code: `call self%register_state_variable(self%id_sSiO2W, 'sSiO2W', 'g/m3','silica dioxide', initial_value=3.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE.)`

### `sSiPaW` [g/m3] *State variables*
- DESC: particulate Si
- Source: abiotic_water.F90 (99-99)
- Formula (d⁻¹): `initial_value=0.02_rk; vertical_movement=cVSetSi`
- Code: `call self%register_state_variable(self%id_sSiPaW, 'sSiPaW', 'g/m3','particulate Si', initial_value=0.02_rk, minimum=0.0_rk,vertical_movement=self%cVSetSi, no_river_dilution=.TRUE.)`

### `O2ConsSed` [g/m3] *State variables*
- DESC: oxygen pool water
- Source: abiotic_sediment.F90 (118-118)
- Formula (d⁻¹): `-`
- Code: `call self%register_state_dependency(self%id_O2ConsSed, 'oxygen_pool_water','g/m3', 'oxygen pool water')`

### `sDIMS` [g/m2] *State variables*
- DESC: inorganic matter
- Source: abiotic_sediment.F90 (110-110)
- Formula (d⁻¹): `initial_value=39611.3_rk`
- Code: `call self%register_state_variable(self%id_sDIMS, 'sDIMS', 'g/m2', 'inorganic matter', initial_value=39611.3_rk, minimum=10.0_rk)`

### `sNH4S` [g/m2] *State variables*
- DESC: ammonium
- Source: abiotic_sediment.F90 (115-115)
- Formula (d⁻¹): `initial_value=0.02_rk`
- Code: `call self%register_state_variable(self%id_sNH4S, 'sNH4S', 'g/m2', 'ammonium', initial_value=0.02_rk, minimum=0.0_rk)`

### `sNO3S` [g/m2] *State variables*
- DESC: nitrate
- Source: abiotic_sediment.F90 (116-116)
- Formula (d⁻¹): `initial_value=0.002_rk`
- Code: `call self%register_state_variable(self%id_sNO3S, 'sNO3S', 'g/m2', 'nitrate', initial_value=0.002_rk, minimum=0.0_rk)`

### `sPAIMS` [g/m2] *State variables*
- DESC: absorbed phosphate
- Source: abiotic_sediment.F90 (114-114)
- Formula (d⁻¹): `initial_value=17.99_rk`
- Code: `call self%register_state_variable(self%id_sPAIMS, 'sPAIMS', 'g/m2', 'absorbed phosphate', initial_value=17.99_rk, minimum=0.0_rk)`

### `sPO4S` [g/m2] *State variables*
- DESC: phosphate
- Source: abiotic_sediment.F90 (113-113)
- Formula (d⁻¹): `initial_value=0.182_rk`
- Code: `call self%register_state_variable(self%id_sPO4S, 'sPO4S', 'g/m2', 'phosphate', initial_value=0.182_rk, minimum=0.0_rk)`

### `sSiO2S` [g/m2] *State variables*
- DESC: dissolved SiO2
- Source: abiotic_sediment.F90 (112-112)
- Formula (d⁻¹): `initial_value=1.82_rk`
- Code: `call self%register_state_variable(self%id_sSiO2S, 'sSiO2S', 'g/m2', 'dissolved SiO2', initial_value=1.82_rk, minimum=0.0_rk)`

### `sSiPaS` [g/m2] *State variables*
- DESC: particulate Si
- Source: abiotic_sediment.F90 (111-111)
- Formula (d⁻¹): `initial_value=1.82_rk`
- Code: `call self%register_state_variable(self%id_sSiPaS, 'sSiPaS', 'g/m2', 'particulate Si', initial_value=1.82_rk, minimum=0.0_rk)`

### `sCS` [gC/m2] *State variables*
- DESC: sediment C
- Source: om_pool.F90 (142)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCS, 'sCS', 'gC/m2', 'sediment C', initial_value=0.0004_rk, minimum=0.0_rk)`
- Code: `call self%register_state_variable(self%id_sCS,     'sCS',       'gC/m2',  'sediment C',     initial_value=0.0004_rk, minimum=0.0_rk                                                                 )`

### `sCS_PV` [gC/m2] *State variables*
- DESC: sediment C PV (pelagic mirror)
- Source: om_pool.F90 (146)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCS_PV, 'sCS_PV', 'gC/m2', 'sediment C  PV', initial_value=0.0004_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sCS_PV,  'sCS_PV',    'gC/m2',  'sediment C  PV', initial_value=0.0004_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )`

### `sCW` [gC/m3] *State variables*
- DESC: water column C
- Source: om_pool.F90 (132)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCW, 'sCW', 'gC/m3', 'water column C', initial_value=0.20_rk, minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sCW,     'sCW',       'gC/m3',  'water column C', initial_value=0.20_rk,   minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )`

### `sDS` [gDW/m2] *State variables*
- DESC: sediment DW
- Source: om_pool.F90 (139)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDS, 'sDS', 'gDW/m2', 'sediment DW', initial_value=0.001_rk, minimum=0.0_rk)`
- Code: `call self%register_state_variable(self%id_sDS,     'sDS',       'gDW/m2', 'sediment DW',    initial_value=0.001_rk,  minimum=0.0_rk                                                                 )`

### `sDS_PV` [gDW/m2] *State variables*
- DESC: sediment DW PV (pelagic mirror)
- Source: om_pool.F90 (143)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDS_PV, 'sDS_PV', 'gDW/m2', 'sediment DW PV', initial_value=0.001_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sDS_PV,  'sDS_PV',    'gDW/m2', 'sediment DW PV', initial_value=0.001_rk,  minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )`

### `sDW` [gDW/m3] *State variables*
- DESC: water column DW
- Source: om_pool.F90 (129)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDW, 'sDW', 'gDW/m3', 'water column DW', initial_value=0.5_rk, minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sDW,     'sDW',       'gDW/m3', 'water column DW',initial_value=0.5_rk,    minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )`

### `sNS` [gN/m2] *State variables*
- DESC: sediment N
- Source: om_pool.F90 (141)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNS, 'sNS', 'gN/m2', 'sediment N', initial_value=0.0001_rk, minimum=0.0_rk)`
- Code: `call self%register_state_variable(self%id_sNS,     'sNS',       'gN/m2',  'sediment N',     initial_value=0.0001_rk, minimum=0.0_rk                                                                 )`

### `sNS_PV` [gN/m2] *State variables*
- DESC: sediment N PV (pelagic mirror)
- Source: om_pool.F90 (145)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNS_PV, 'sNS_PV', 'gN/m2', 'sediment N  PV', initial_value=0.0001_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sNS_PV,  'sNS_PV',    'gN/m2',  'sediment N  PV', initial_value=0.0001_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )`

### `sNW` [gN/m3] *State variables*
- DESC: water column N
- Source: om_pool.F90 (131)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNW, 'sNW', 'gN/m3', 'water column N', initial_value=0.05_rk, minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sNW,     'sNW',       'gN/m3',  'water column N', initial_value=0.05_rk,   minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )`

### `sPS` [gP/m2] *State variables*
- DESC: sediment P
- Source: om_pool.F90 (140)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPS, 'sPS', 'gP/m2', 'sediment P', initial_value=0.00001_rk, minimum=0.0_rk)`
- Code: `call self%register_state_variable(self%id_sPS,     'sPS',       'gP/m2',  'sediment P',     initial_value=0.00001_rk,minimum=0.0_rk                                                                 )`

### `sPS_PV` [gP/m2] *State variables*
- DESC: sediment P PV (pelagic mirror)
- Source: om_pool.F90 (144)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPS_PV, 'sPS_PV', 'gP/m2', 'sediment P  PV', initial_value=0.00001_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sPS_PV,  'sPS_PV',    'gP/m2',  'sediment P  PV', initial_value=0.00001_rk,minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )`

### `sPW` [gP/m3] *State variables*
- DESC: water column P
- Source: om_pool.F90 (130)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPW, 'sPW', 'gP/m3', 'water column P', initial_value=0.005_rk, minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sPW,     'sPW',       'gP/m3',  'water column P', initial_value=0.005_rk,  minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )`

### `sCS` [gC/m2] *State variables*
- DESC: sediment C
- Source: phytoplankton.F90 (166)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCS,'sCS','gC/m2','sediment C', initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW)`
- Code: `call self%register_state_variable(self%id_sCS,'sCS','gC/m2', 'sediment C',     initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW                                                        )`

### `sCS_PV` [gC/m2] *State variables*
- DESC: sediment C PV (pelagic mirror)
- Source: phytoplankton.F90 (170)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCS_PV,'sCS_PV','gC/m2','sediment C  PV',initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW,no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sCS_PV,'sCS_PV','gC/m2', 'sediment C  PV',initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW,no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sCW` [gC/m3] *State variables*
- DESC: water column C
- Source: phytoplankton.F90 (156)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCW,'sCW','gC/m3','water column C', initial_value=0.20_rk, minimum=self%cDMinW * self%cCPerDW,vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sCW,'sCW','gC/m3', 'water column C', initial_value=0.20_rk,   minimum=self%cDMinW * self%cCPerDW,vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`

### `sDS` [gDW/m2] *State variables*
- DESC: sediment DW
- Source: phytoplankton.F90 (163)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDS,'sDS','gDW/m2','sediment DW', initial_value=0.001_rk, minimum=self%cDMinS)`
- Code: `call self%register_state_variable(self%id_sDS,'sDS','gDW/m2','sediment DW',    initial_value=0.001_rk,  minimum=self%cDMinS                                                                       )`

### `sDS_PV` [gDW/m2] *State variables*
- DESC: sediment DW PV (pelagic mirror)
- Source: phytoplankton.F90 (167)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDS_PV,'sDS_PV','gDW/m2','sediment DW PV',initial_value=0.001_rk, minimum=self%cDMinS, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sDS_PV,'sDS_PV','gDW/m2','sediment DW PV',initial_value=0.001_rk,  minimum=self%cDMinS,               no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sDW` [gDW/m3] *State variables*
- DESC: water column DW
- Source: phytoplankton.F90 (153)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDW,'sDW','gDW/m3','water column DW',initial_value=0.5_rk, minimum=self%cDMinW, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sDW,'sDW','gDW/m3','water column DW',initial_value=0.5_rk,    minimum=self%cDMinW,               vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`

### `sNS` [gN/m2] *State variables*
- DESC: sediment N
- Source: phytoplankton.F90 (165)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNS,'sNS','gN/m2','sediment N', initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin)`
- Code: `call self%register_state_variable(self%id_sNS,'sNS','gN/m2', 'sediment N',     initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin                                                         )`

### `sNS_PV` [gN/m2] *State variables*
- DESC: sediment N PV (pelagic mirror)
- Source: phytoplankton.F90 (169)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNS_PV,'sNS_PV','gN/m2','sediment N  PV',initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sNS_PV,'sNS_PV','gN/m2', 'sediment N  PV',initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sNW` [gN/m3] *State variables*
- DESC: water column N
- Source: phytoplankton.F90 (155)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNW,'sNW','gN/m3','water column N', initial_value=0.05_rk, minimum=self%cDMinW * self%cNDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sNW,'sNW','gN/m3', 'water column N', initial_value=0.05_rk,   minimum=self%cDMinW * self%cNDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`

### `sPS` [gP/m2] *State variables*
- DESC: sediment P
- Source: phytoplankton.F90 (164)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPS,'sPS','gP/m2','sediment P', initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin)`
- Code: `call self%register_state_variable(self%id_sPS,'sPS','gP/m2', 'sediment P',     initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin                                                         )`

### `sPS_PV` [gP/m2] *State variables*
- DESC: sediment P PV (pelagic mirror)
- Source: phytoplankton.F90 (168)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPS_PV,'sPS_PV','gP/m2','sediment P  PV',initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sPS_PV,'sPS_PV','gP/m2', 'sediment P  PV',initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sPW` [gP/m3] *State variables*
- DESC: water column P
- Source: phytoplankton.F90 (154)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPW,'sPW','gP/m3','water column P', initial_value=0.005_rk, minimum=self%cDMinW * self%cPDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sPW,'sPW','gP/m3', 'water column P', initial_value=0.005_rk,  minimum=self%cDMinW * self%cPDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)`

### `sC` [gC/m3] *State variables*
- DESC: C (zooplankton carbon)
- Source: zooplankton.F90 (117)
- Formula (d⁻¹): `initial_value=0.02_rk, minimum=cDMinZoo*cCDRef`
- Code: `call self%register_state_variable(self%id_sCZoo, 'sC', 'gC/m3', 'C', initial_value=0.02_rk, minimum=self%cDMinZoo * self%cCDRef, no_river_dilution=.TRUE.)`

### `sD` [gDW/m3] *State variables*
- DESC: DW (zooplankton dry weight)
- Source: zooplankton.F90 (114)
- Formula (d⁻¹): `initial_value=0.05_rk, minimum=cDMinZoo, no_river_dilution=.TRUE.`
- Code: `call self%register_state_variable(self%id_sDZoo, 'sD', 'gDW/m3', 'DW', initial_value=0.05_rk, minimum=self%cDMinZoo, no_river_dilution=.TRUE.)`

### `sN` [gN/m3] *State variables*
- DESC: N (zooplankton nitrogen)
- Source: zooplankton.F90 (116)
- Formula (d⁻¹): `initial_value=0.0035_rk, minimum=cDMinZoo*cNDRef`
- Code: `call self%register_state_variable(self%id_sNZoo, 'sN', 'gN/m3', 'N', initial_value=0.0035_rk, minimum=self%cDMinZoo * self%cNDRef, no_river_dilution=.TRUE.)`

### `sP` [gP/m3] *State variables*
- DESC: P (zooplankton phosphorous)
- Source: zooplankton.F90 (115)
- Formula (d⁻¹): `initial_value=0.0005_rk, minimum=cDMinZoo*cPDRef`
- Code: `call self%register_state_variable(self%id_sPZoo, 'sP', 'gP/m3', 'P', initial_value=0.0005_rk, minimum=self%cDMinZoo * self%cPDRef, no_river_dilution=.TRUE.)`

### `sC` [gC/m2] *State variables*
- DESC: C (zoobenthos carbon)
- Source: zoobenthos.F90 (119)
- Formula (d⁻¹): `initial_value=0.40_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sCBent, 'sC', 'gC/m2', 'C', initial_value=0.40_rk, minimum=0.0_rk)`

### `sC_PV` [gC/m2] *State variables*
- DESC: C pel. var
- Source: zoobenthos.F90 (124)
- Formula (d⁻¹): `initial_value=0.40_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sCBent_PV, 'sC_PV', 'gC/m2', 'C pel. var', initial_value=0.40_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sD` [gDW/m2] *State variables*
- DESC: DW (zoobenthos dry weight)
- Source: zoobenthos.F90 (116)
- Formula (d⁻¹): `initial_value=1.0_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sDBent, 'sD', 'gDW/m2', 'DW', initial_value=1.0_rk, minimum=0.0_rk)`

### `sD_PV` [gDW/m2] *State variables*
- DESC: DW pel. var
- Source: zoobenthos.F90 (121)
- Formula (d⁻¹): `initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE.`
- Code: `call self%register_state_variable(self%id_sDBent_PV, 'sD_PV', 'gDW/m2', 'DW pel. var', initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sN` [gN/m2] *State variables*
- DESC: N (zoobenthos nitrogen)
- Source: zoobenthos.F90 (118)
- Formula (d⁻¹): `initial_value=0.01_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sNBent, 'sN', 'gN/m2', 'N', initial_value=0.01_rk, minimum=0.0_rk)`

### `sN_PV` [gN/m2] *State variables*
- DESC: N pel. var
- Source: zoobenthos.F90 (123)
- Formula (d⁻¹): `initial_value=0.01_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sNBent_PV, 'sN_PV', 'gN/m2', 'N pel. var', initial_value=0.01_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sP` [gP/m2] *State variables*
- DESC: P (zoobenthos phosphorous)
- Source: zoobenthos.F90 (117)
- Formula (d⁻¹): `initial_value=0.1_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sPBent, 'sP', 'gP/m2', 'P', initial_value=0.1_rk, minimum=0.0_rk)`

### `sP_PV` [gP/m2] *State variables*
- DESC: P pel. var
- Source: zoobenthos.F90 (122)
- Formula (d⁻¹): `initial_value=0.1_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sPBent_PV, 'sP_PV', 'gP/m2', 'P pel. var', initial_value=0.1_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sC` [gC/m2] *State variables*
- DESC: C (macrophyte carbon)
- Source: macrophytes.F90 (160)
- Formula (d⁻¹): `initial_value=0.4_rk`
- Code: `call self%register_state_variable(self%id_sCVeg, 'sC', 'gC/m2', 'P', initial_value=0.4_rk, minimum=0.0_rk)`

### `sC_PV` [gC/m2] *State variables*
- DESC: C pel. var
- Source: macrophytes.F90 (165)
- Formula (d⁻¹): `initial_value=0.4_rk`
- Code: `call self%register_state_variable(self%id_sCVeg_PV,'sC_PV','gC/m2', 'C pel. var', initial_value=0.4_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sD` [gDW/m2] *State variables*
- DESC: DW (macrophyte dry weight)
- Source: macrophytes.F90 (157)
- Formula (d⁻¹): `initial_value=1.0_rk, minimum=0.0_rk`
- Code: `call self%register_state_variable(self%id_sDVeg, 'sD', 'gDW/m2','DW', initial_value=1.0_rk, minimum=0.0_rk)`

### `sD_PV` [gDW/m2] *State variables*
- DESC: DW pel. var
- Source: macrophytes.F90 (162)
- Formula (d⁻¹): `initial_value=1.0_rk, no_river_dilution=.TRUE.`
- Code: `call self%register_state_variable(self%id_sDVeg_PV,'sD_PV','gDW/m2','DW pel. var',initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sN` [gN/m2] *State variables*
- DESC: N (macrophyte nitrogen)
- Source: macrophytes.F90 (158)
- Formula (d⁻¹): `initial_value=0.02_rk`
- Code: `call self%register_state_variable(self%id_sNVeg, 'sN', 'gN/m2', 'N', initial_value=0.02_rk, minimum=0.0_rk)`

### `sN_PV` [gN/m2] *State variables*
- DESC: N pel. var
- Source: macrophytes.F90 (164)
- Formula (d⁻¹): `initial_value=0.002_rk`
- Code: `call self%register_state_variable(self%id_sNVeg_PV,'sN_PV','gN/m2', 'N pel. var', initial_value=0.002_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sP` [gP/m2] *State variables*
- DESC: P (macrophyte phosphorous)
- Source: macrophytes.F90 (159)
- Formula (d⁻¹): `initial_value=0.002_rk`
- Code: `call self%register_state_variable(self%id_sPVeg, 'sP', 'gP/m2', 'P', initial_value=0.002_rk, minimum=0.0_rk)`

### `sP_PV` [gP/m2] *State variables*
- DESC: P pel. var
- Source: macrophytes.F90 (163)
- Formula (d⁻¹): `initial_value=0.02_rk`
- Code: `call self%register_state_variable(self%id_sPVeg_PV,'sP_PV','gP/m2', 'P pel. var', initial_value=0.02_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `fVul` [-] *State variables*
- DESC: biomass fraction vulnerable to predation
- Source: fish.F90 (203)
- Formula (d⁻¹): `call self%register_state_variable(self%id_fVul,'fVul','-',...,initial_value=1.0_rk,minimum=0.0_rk,...)`
- Code: `call self%register_state_variable(self%id_fVul, 'fVul', '-', 'biomass fraction vulnerable to predation', initial_value= 1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sCFi` [gN/m3] *State variables*
- DESC: C (fish C mass)
- Source: fish.F90 (202)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sCFi,'sC','gN/m3','C',initial_value=0.05_rk,minimum=self%cDFiMin*self%cCDRef,...)`
- Code: `call self%register_state_variable(self%id_sCFi, 'sC', 'gN/m3', 'C', initial_value= 0.05_rk, minimum=self%cDFiMin * self%cCDRef, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sDFi` [gDW/m3] *State variables*
- DESC: DW (fish dry weight)
- Source: fish.F90 (199)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDFi,'sD','gDW/m3','DW',initial_value=0.5_rk,minimum=self%cDFiMin,no_river_dilution=.TRUE.,no_precipitation_dilution=.TRUE.)`
- Code: `call self%register_state_variable(self%id_sDFi, 'sD', 'gDW/m3', 'DW', initial_value= 0.5_rk, minimum=self%cDFiMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sDSiz` [gDW/ind] *State variables*
- DESC: average individual fish size
- Source: fish.F90 (206)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDSiz,'sDSiz','gDW/ind','average individual fish size',initial_value=0.0_rk,minimum=0.0_rk,...)`
- Code: `call self%register_state_variable(self%id_sDSiz, 'sDSiz', 'gDW/ind', 'average individual fish size', initial_value= 0.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sFRes` [gDW/m3] *State variables*
- DESC: reserve fraction of biomass
- Source: fish.F90 (205)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sFRes,'sFRes','gDW/m3','reserve fraction of biomass',initial_value=0.0_rk,minimum=0.0_rk,...)`
- Code: `call self%register_state_variable(self%id_sFRes, 'sFRes', 'gDW/m3', 'reserve fraction of biomass', initial_value= 0.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sNFi` [gN/m3] *State variables*
- DESC: N (fish N mass)
- Source: fish.F90 (201)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNFi,'sN','gN/m3','N',initial_value=0.05_rk,minimum=self%cDFiMin*self%cNDRef,...)`
- Code: `call self%register_state_variable(self%id_sNFi, 'sN', 'gN/m3', 'N', initial_value= 0.05_rk, minimum=self%cDFiMin * self%cNDRef, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sPFi` [gP/m3] *State variables*
- DESC: P (fish P mass)
- Source: fish.F90 (200)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPFi,'sP','gP/m3','P',initial_value=0.011_rk,minimum=self%cDFiMin*self%cPDRef,...)`
- Code: `call self%register_state_variable(self%id_sPFi, 'sP', 'gP/m3', 'P', initial_value= 0.011_rk, minimum=self%cDFiMin * self%cPDRef, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sDFi` [gDW/m3] *State variables*
- DESC: DW (fish dry weight)
- Source: fish_pclake.F90 (161)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sDFi,'sD','gDW/m3','DW',initial_value=0.5_rk,minimum=self%cDFiMin)`
- Code: `call self%register_state_variable(self%id_sDFi, 'sD', 'gDW/m3', 'DW', initial_value= 0.5_rk, minimum=self%cDFiMin)`

### `sNFi` [gN/m3] *State variables*
- DESC: N (fish N mass)
- Source: fish_pclake.F90 (163)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sNFi,'sN','gN/m3','N',initial_value=0.05_rk,minimum=self%cDFiMin*self%cNDFishRef)`
- Code: `call self%register_state_variable(self%id_sNFi, 'sN', 'gN/m3', 'N', initial_value=0.05_rk, minimum=self%cDFiMin * self%cNDFishRef)`

### `sPFi` [gP/m3] *State variables*
- DESC: P (fish P mass)
- Source: fish_pclake.F90 (162)
- Formula (d⁻¹): `call self%register_state_variable(self%id_sPFi,'sP','gP/m3','P',initial_value=0.011_rk,minimum=self%cDFiMin*self%cPDFishRef)`
- Code: `call self%register_state_variable(self%id_sPFi, 'sP', 'gP/m3', 'P', initial_value=0.011_rk, minimum=self%cDFiMin * self%cPDFishRef)`

### `s*DOMS_PV` [g/m2] *State variables*
- DESC: DOM DW/N/P/C in sediment pelagic mirror per group
- Source: sediment_exchange.F90 (235-238)
- Formula (d⁻¹): `register_state_dependency id_s*DOMS_PV`
- Code: `register_state_dependency(self%id_sDDOMS_PV(i_dom), 'DOM_D_in_sediment_'//trim(index)//'_PV', 'g/m2', 'DOM D PV pelagic mirror'//trim(index))`

### `s*POMS_PV` [g/m2] *State variables*
- DESC: POM DW/N/P/C in sediment pelagic mirror per group
- Source: sediment_exchange.F90 (170-173)
- Formula (d⁻¹): `register_state_dependency id_s*POMS_PV`
- Code: `register_state_dependency(self%id_sDPOMS_PV(i_pom), 'POM_D_in_sediment_'//trim(index)//'_PV', 'g/m2', 'POM D PV pelagic mirror'//trim(index))`

### `sDDOMS/sNDOMS/sPDOMS/sCDOMS` [g/m2] *State variables*
- DESC: DOM DW/N/P/C in sediment per group (dim nDOM)
- Source: sediment_exchange.F90 (226-229)
- Formula (d⁻¹): `register_state_dependency id_s*DOMS`
- Code: `register_state_dependency(self%id_sDDOMS(i_dom), 'DOM_D_in_sediment_'//trim(index), 'g/m2', 'DOM D'//trim(index))`

### `sDDOMW/sNDOMW/sPDOMW/sCDOMW` [g/m3] *State variables*
- DESC: DOM DW/N/P/C in water per group (dim nDOM)
- Source: sediment_exchange.F90 (217-220)
- Formula (d⁻¹): `register_state_dependency id_s*DOMW`
- Code: `register_state_dependency(self%id_sDDOMW(i_dom), 'DOM_D_in_water_'//trim(index), 'g/m3', 'DOM D'//trim(index))`

### `sDIMS` [g/m2] *State variables*
- DESC: sediment inorganic matter
- Source: sediment_exchange.F90 (257)
- Formula (d⁻¹): `register_state_dependency id_sDIMS`
- Code: `register_state_dependency(self%id_sDIMS, 'inorg_pool_in_sediment', 'g/m2', 'sediment inorganic matter')`

### `sDIMW` [g/m3] *State variables*
- DESC: inorganic matter pool in water
- Source: sediment_exchange.F90 (270)
- Formula (d⁻¹): `register_state_dependency id_sDIMW`
- Code: `register_state_dependency(self%id_sDIMW, 'inorg_pool_in_water', 'g/m3', 'inorganic matter pool in water')`

### `sDPOMS/sNPOMS/sPPOMS/sCPOMS` [g/m2] *State variables*
- DESC: POM DW/N/P/C in sediment per group (dim nPOM)
- Source: sediment_exchange.F90 (161-164)
- Formula (d⁻¹): `register_state_dependency id_s*POMS`
- Code: `register_state_dependency(self%id_sDPOMS(i_pom), 'POM_D_in_sediment_'//trim(index), 'g/m2', 'POM D'//trim(index))`

### `sDPOMW/sNPOMW/sPPOMW/sCPOMW` [g/m3] *State variables*
- DESC: POM DW/N/P/C in water per group (dim nPOM)
- Source: sediment_exchange.F90 (152-155)
- Formula (d⁻¹): `register_state_dependency id_s*POMW`
- Code: `register_state_dependency(self%id_sDPOMW(i_pom), 'POM_D_in_water_'//trim(index), 'g/m3', 'POM D'//trim(index))`

### `sNH4S` [g/m2] *State variables*
- DESC: sediment ammonium
- Source: sediment_exchange.F90 (260)
- Formula (d⁻¹): `register_state_dependency id_sNH4S`
- Code: `register_state_dependency(self%id_sNH4S, 'NH4_in_sediment', 'g/m2', 'sediment ammonium')`

### `sNH4W` [g/m3] *State variables*
- DESC: water NH4
- Source: sediment_exchange.F90 (267)
- Formula (d⁻¹): `register_state_dependency id_sNH4W`
- Code: `register_state_dependency(self%id_sNH4W, 'NH4_in_water', 'g/m3', 'water NH4')`

### `sNO3S` [g/m2] *State variables*
- DESC: sediment nitrate
- Source: sediment_exchange.F90 (261)
- Formula (d⁻¹): `register_state_dependency id_sNO3S`
- Code: `register_state_dependency(self%id_sNO3S, 'NO3_in_sediment', 'g/m2', 'sediment nitrate')`

### `sNO3W` [g/m3] *State variables*
- DESC: water NO3
- Source: sediment_exchange.F90 (268)
- Formula (d⁻¹): `register_state_dependency id_sNO3W`
- Code: `register_state_dependency(self%id_sNO3W, 'NO3_in_water', 'g/m3', 'water NO3')`

### `sPAIMS` [g/m2] *State variables*
- DESC: sediment absorbed phosphate
- Source: sediment_exchange.F90 (259)
- Formula (d⁻¹): `register_state_dependency id_sPAIMS`
- Code: `register_state_dependency(self%id_sPAIMS, 'PAIM_in_sediment', 'g/m2', 'sediment absorbed phosphate')`

### `sPAIMW` [g/m3] *State variables*
- DESC: adsorbed phosphorus in water
- Source: sediment_exchange.F90 (271)
- Formula (d⁻¹): `register_state_dependency id_sPAIMW`
- Code: `register_state_dependency(self%id_sPAIMW, 'PAIM_in_water', 'g/m3', 'adsorbed phosphorus in water')`

### `sPO4S` [g/m2] *State variables*
- DESC: sediment phosphate
- Source: sediment_exchange.F90 (258)
- Formula (d⁻¹): `register_state_dependency id_sPO4S`
- Code: `register_state_dependency(self%id_sPO4S, 'PO4_in_sediment', 'g/m2', 'sediment phosphate')`

### `sPO4W` [g/m3] *State variables*
- DESC: water PO4
- Source: sediment_exchange.F90 (269)
- Formula (d⁻¹): `register_state_dependency id_sPO4W`
- Code: `register_state_dependency(self%id_sPO4W, 'PO4_in_water', 'g/m3', 'water PO4')`

### `sSiO2S` [g/m2] *State variables*
- DESC: sediment dissolved Si
- Source: sediment_exchange.F90 (263)
- Formula (d⁻¹): `register_state_dependency id_sSiO2S`
- Code: `register_state_dependency(self%id_sSiO2S, 'dissolved_Si_in_sediment', 'g/m2', 'sediment dissolved Si')`

### `sSiO2W` [g/m3] *State variables*
- DESC: water SiO2
- Source: sediment_exchange.F90 (266)
- Formula (d⁻¹): `register_state_dependency id_sSiO2W`
- Code: `register_state_dependency(self%id_sSiO2W, 'SiO2_in_water', 'g/m3', 'water SiO2')`

### `sSiPaS` [g/m2] *State variables*
- DESC: sediment particulate Si
- Source: sediment_exchange.F90 (262)
- Formula (d⁻¹): `register_state_dependency id_sSiPaS`
- Code: `register_state_dependency(self%id_sSiPaS, 'particulate_Si_in_sediment', 'g/m2', 'sediment particulate Si')`

### `sSiPaW` [g/m2] *State variables*
- DESC: water particulate Si
- Source: sediment_exchange.F90 (265)
- Formula (d⁻¹): `register_state_dependency id_sSiPaW`
- Code: `register_state_dependency(self%id_sSiPaW, 'particulate_Si_in_water', 'g/m2', 'water particulate Si')`

### `s*POMS_PV` [g/m2] *State variables*
- DESC: POM DW/N/P in sediment pelagic mirror
- Source: resus_sed.F90 (87-89)
- Formula (d⁻¹): `register_state_dependency id_s*POMS_PV`
- Code: `register_state_dependency(self%id_sDPOMS_PV,'POM_DW_in_sediment_PV', 'g/m2', 'POM DW in sediment pelagic mirror')`

### `sDIMS` [g/m2] *State variables*
- DESC: sediment inorganic matter
- Source: resus_sed.F90 (83)
- Formula (d⁻¹): `register_state_dependency id_sDIMS`
- Code: `register_state_dependency(self%id_sDIMS, 'inorg_pool_in_sediment', 'g/m2', 'sediment inorganic matter')`

### `sDPOMS/sNPOMS/sPPOMS` [g/m2] *State variables*
- DESC: POM DW/N/P in sediment (single group)
- Source: resus_sed.F90 (84-86)
- Formula (d⁻¹): `register_state_dependency id_s*POMS`
- Code: `register_state_dependency(self%id_sDPOMS, 'POM_DW_in_sediment', 'g/m2', 'POM DW in sediment')`

### `sPO4S/sPAIMS/sNH4S/sNO3S/sSiPaS` [g/m2] *State variables*
- DESC: sediment PO4/PAIM/NH4/NO3/SiPa
- Source: resus_sed.F90 (91-95)
- Formula (d⁻¹): `register_state_dependency id_s*`
- Code: `register_state_dependency(self%id_sPO4S, 'PO4_in_sediment', 'g/m2', 'sediment phosphate')`

### `SWDIM/SWPAIM/SWDPOM/SWNPOM/SWPPOM/sNH4W/sNO3W/sPO4W` [g/m3] *State variables*
- DESC: water inorganic/POM/NUT pools
- Source: resus_sed.F90 (98-105)
- Formula (d⁻¹): `register_state_dependency id_SW*`
- Code: `register_state_dependency(self%id_SWDIM, 'inorg_pool_in_water', 'g/m3', 'inorganic matter pool in water')`

### `SWSiPa` [g/m2] *State variables*
- DESC: water particulate Si
- Source: resus_sed.F90 (97)
- Formula (d⁻¹): `register_state_dependency id_SWSiPa`
- Code: `register_state_dependency(self%id_SWSiPa, 'particulate_Si_in_water', 'g/m2', 'water particulate Si')`

### `DOMD/DOMN/DOMP/DOMC` [g/m2] *State variables*
- DESC: DOM DW/N/P/C per group (dim nDOM)
- Source: burial.F90 (184-187)
- Formula (d⁻¹): `register_state_dependency id_DOM*`
- Code: `register_state_dependency(self%id_DOMD(i_spec), 'DOM_D_'//trim(index), 'g/m2', 'DOM D '//trim(index))`

### `DOMD_PV/DOMN_PV/DOMP_PV/DOMC_PV` [g/m2] *State variables*
- DESC: DOM DW/N/P/C pelagic mirror per group
- Source: burial.F90 (192-195)
- Formula (d⁻¹): `register_state_dependency id_DOM*_PV`
- Code: `register_state_dependency(self%id_DOMD_PV(i_spec), 'DOM_D_'//trim(index)//'_PV', 'g/m2', 'DOM D PV group number'//trim(index))`

### `POMD/POMN/POMP/POMC` [g/m2] *State variables*
- DESC: POM DW/N/P/C per group (dim nPOM)
- Source: burial.F90 (149-152)
- Formula (d⁻¹): `register_state_dependency id_POM*`
- Code: `register_state_dependency(self%id_POMD(i_spec), 'POM_D_'//trim(index), 'g/m2', 'POM D '//trim(index))`

### `POMD_PV/POMN_PV/POMP_PV/POMC_PV` [g/m2] *State variables*
- DESC: POM DW/N/P/C pelagic mirror per group
- Source: burial.F90 (157-160)
- Formula (d⁻¹): `register_state_dependency id_POM*_PV`
- Code: `register_state_dependency(self%id_POMD_PV(i_spec), 'POM_D_'//trim(index)//'_PV', 'g/m2', 'POM D PV group number '//trim(index))`

### `WSDHum/WSNHum/WSPHum/WSCHum` [g/m2] *State variables*
- DESC: humus DW/N/P/C in deep sediment
- Source: burial.F90 (88-91)
- Formula (d⁻¹): `register_state_dependency id_WS*Hum`
- Code: `register_state_dependency(self%id_WSDHum, 'humus_DW_in_deep_sediment', 'g/m2', 'humus DW in deep sediment')`

### `WSDHum_PV/WSNHum_PV/WSPHum_PV/WSCHum_PV` [g/m2] *State variables*
- DESC: humus DW/N/P/C deep sediment pelagic mirror
- Source: burial.F90 (92-95)
- Formula (d⁻¹): `register_state_dependency id_WS*Hum_PV`
- Code: `register_state_dependency(self%id_WSDHum_PV, 'humus_DW_in_deep_sediment_PV', 'g/m2', 'humus DW in deep sediment pelagic mirror')`

### `WSNH4/WSNO3/WSPO4/WSPAIM/WSDIM/WSSiPa` [g/m2] *State variables*
- DESC: sediment NUT/IM/SiPa pools
- Source: burial.F90 (83-96)
- Formula (d⁻¹): `register_state_dependency id_WS*`
- Code: `register_state_dependency(self%id_WSNH4, 'NH4_pool_in_sediment', 'g/m2', 'NH4 pool in sediment')`

### `BivAd_D/N/P/C` [g/m2] *State variables*
- DESC: adult stage (if qStageOpt=2 or 3)
- Source: bivalves.F90 (187-190)
- Formula (d⁻¹): `register_state_dependency id_BivAd_*`
- Code: `register_state_dependency(self%id_BivAd_D, 'adult_D', 'gDW/m2', 'adult D state')`

### `BivAd_D/N/P/C_PV` [g/m2] *State variables*
- DESC: adult stage pelagic variant
- Source: bivalves.F90 (191-194)
- Formula (d⁻¹): `register_state_variable id_BivAd_*_PV`
- Code: `register_state_variable(self%id_BivAd_D_PV, 'sD_PV', 'gDW/m2', 'DW pel. var', initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `BivJu_D/N/P/C` [g/m2] *State variables*
- DESC: juvenile stage (if qStageOpt=1 or 3)
- Source: bivalves.F90 (172-175)
- Formula (d⁻¹): `register_state_dependency id_BivJu_*`
- Code: `register_state_dependency(self%id_BivJu_D, 'juvenile_D', 'gDW/m2', 'juvenile D state')`

### `BivJu_D/N/P/C_PV` [g/m2] *State variables*
- DESC: juvenile stage pelagic variant
- Source: bivalves.F90 (176-179)
- Formula (d⁻¹): `register_state_variable id_BivJu_*_PV`
- Code: `register_state_variable(self%id_BivJu_D_PV, 'sD_PV', 'gDW/m2', 'DW pel. var', initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sCBiv` [gC/m2] *State variables*
- DESC: bivalve carbon
- Source: bivalves.F90 (160)
- Formula (d⁻¹): `register_state_variable id_sCBiv (initial=0.40)`
- Code: `register_state_variable(self%id_sCBiv, 'sC', 'gC/m2', 'C', initial_value=0.40_rk, minimum=0.0_rk)`

### `sCBiv_PV` [gC/m2] *State variables*
- DESC: bivalve C pelagic variant
- Source: bivalves.F90 (165)
- Formula (d⁻¹): `register_state_variable id_sCBiv_PV (initial=0.40)`
- Code: `register_state_variable(self%id_sCBiv_PV, 'sC_PV', 'gC/m2', 'C pel. var', initial_value=0.40_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sDBiv` [gDW/m2] *State variables*
- DESC: bivalve dry weight
- Source: bivalves.F90 (157)
- Formula (d⁻¹): `register_state_variable id_sDBiv (initial=1.0)`
- Code: `register_state_variable(self%id_sDBiv, 'sD', 'gDW/m2', 'DW', initial_value=1.0_rk, minimum=0.0_rk)`

### `sDBiv_PV` [gDW/m2] *State variables*
- DESC: bivalve DW pelagic variant (no_transport)
- Source: bivalves.F90 (162)
- Formula (d⁻¹): `register_state_variable id_sDBiv_PV (initial=1.0)`
- Code: `register_state_variable(self%id_sDBiv_PV, 'sD_PV', 'gDW/m2', 'DW pel. var', initial_value=1.0_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sNBiv` [gN/m2] *State variables*
- DESC: bivalve nitrogen
- Source: bivalves.F90 (158)
- Formula (d⁻¹): `register_state_variable id_sNBiv (initial=0.1)`
- Code: `register_state_variable(self%id_sNBiv, 'sN', 'gN/m2', 'N', initial_value=0.1_rk, minimum=0.0_rk)`

### `sNBiv_PV` [gN/m2] *State variables*
- DESC: bivalve N pelagic variant
- Source: bivalves.F90 (163)
- Formula (d⁻¹): `register_state_variable id_sNBiv_PV (initial=0.01)`
- Code: `register_state_variable(self%id_sNBiv_PV, 'sN_PV', 'gN/m2', 'N pel. var', initial_value=0.01_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

### `sPBiv` [gP/m2] *State variables*
- DESC: bivalve phosphorus
- Source: bivalves.F90 (159)
- Formula (d⁻¹): `register_state_variable id_sPBiv (initial=0.01)`
- Code: `register_state_variable(self%id_sPBiv, 'sP', 'gP/m2', 'P', initial_value=0.01_rk, minimum=0.0_rk)`

### `sPBiv_PV` [gP/m2] *State variables*
- DESC: bivalve P pelagic variant
- Source: bivalves.F90 (164)
- Formula (d⁻¹): `register_state_variable id_sPBiv_PV (initial=0.1)`
- Code: `register_state_variable(self%id_sPBiv_PV, 'sP_PV', 'gP/m2', 'P pel. var', initial_value=0.1_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)`

## Stoichiometric correction

### `aCorDRespZoo` [-] *Stoichiometric correction*
- DESC: calculate corr. factor between respiration and P, N, C content
- Source: zooplankton.F90 (330)
- Formula (d⁻¹): `max(cPDRef / rPDZoo,cNDRef / rNDZoo, cCDRef / rCDZoo)`
- Code: `aCorDRespZoo = max(self%cPDRef / rPDZoo,self%cNDRef / rNDZoo, self%cCDRef / rCDZoo)`

### `aCorDRespBent` [-] *Stoichiometric correction*
- DESC: calculate corr. factor between respiration and P, N, C content (currently only P)
- Source: zoobenthos.F90 (365)
- Formula (d⁻¹): `cPDRef / rPDBent`
- Code: `aCorDRespBent = self%cPDRef / rPDBent`

## Stoichiometry

### `rCDBent` [gC/gDW] *Stoichiometry*
- DESC: calculate C:DW ratio of benthos
- Source: fish.F90 (572)
- Formula (d⁻¹): `rCDBent = sCBent/(sDBent+NearZero)`
- Code: `rCDBent = sCBent/(sDBent+NearZero)`

### `rCDFi` [gC/gDW] *Stoichiometry*
- DESC: calculate C:DW ratio (dynamic)
- Source: fish.F90 (524)
- Formula (d⁻¹): `rCDFi = sCFi /(sDFi+NearZero)`
- Code: `rCDFi = sCFi /(sDFi+NearZero)`

### `rCDFi` [gC/gDW] *Stoichiometry*
- DESC: C ratio parameter (fixed)
- Source: fish.F90 (528)
- Formula (d⁻¹): `rCDFi = self%cCDRef`
- Code: `rCDFi = self%cCDRef`

### `rCDPisc` [gC/gDW] *Stoichiometry*
- DESC: calculate C:DW ratio of fish prey
- Source: fish.F90 (599)
- Formula (d⁻¹): `rCDPisc = sCPisc/(max(sDPisc,NearZero))`
- Code: `rCDPisc = sCPisc/(max(sDPisc,NearZero))`

### `rCDPlan` [gC/gDW] *Stoichiometry*
- DESC: calculate C:DW ratio of plankton
- Source: fish.F90 (550)
- Formula (d⁻¹): `rCDPlan = sCPlan / (sDPlan + NearZero)`
- Code: `rCDPlan = sCPlan / (sDPlan + NearZero)`

### `rNDBent` [gN/gDW] *Stoichiometry*
- DESC: calculate N:DW ratio of benthos
- Source: fish.F90 (571)
- Formula (d⁻¹): `rNDBent = sNBent/(sDBent+NearZero)`
- Code: `rNDBent = sNBent/(sDBent+NearZero)`

### `rNDFi` [gN/gDW] *Stoichiometry*
- DESC: calculate N:DW ratio (dynamic)
- Source: fish.F90 (523)
- Formula (d⁻¹): `rNDFi = sNFi /(sDFi+NearZero)`
- Code: `rNDFi = sNFi /(sDFi+NearZero)`

### `rNDFi` [gN/gDW] *Stoichiometry*
- DESC: N ratio parameter (fixed)
- Source: fish.F90 (527)
- Formula (d⁻¹): `rNDFi = self%cNDRef`
- Code: `rNDFi = self%cNDRef`

### `rNDPisc` [gN/gDW] *Stoichiometry*
- DESC: calculate N:DW ratio of fish prey
- Source: fish.F90 (598)
- Formula (d⁻¹): `rNDPisc = sNPisc/(max(sDPisc,NearZero))`
- Code: `rNDPisc = sNPisc/(max(sDPisc,NearZero))`

### `rNDPlan` [gN/gDW] *Stoichiometry*
- DESC: calculate N:DW ratio of plankton
- Source: fish.F90 (549)
- Formula (d⁻¹): `rNDPlan = sNPlan / (sDPlan + NearZero)`
- Code: `rNDPlan = sNPlan / (sDPlan + NearZero)`

### `rPDBent` [gP/gDW] *Stoichiometry*
- DESC: calculate P:DW ratio of benthos
- Source: fish.F90 (570)
- Formula (d⁻¹): `rPDBent = sPBent/(sDBent+NearZero)`
- Code: `rPDBent = sPBent/(sDBent+NearZero)`

### `rPDFi` [gP/gDW] *Stoichiometry*
- DESC: calculate P:DW ratio (dynamic)
- Source: fish.F90 (522)
- Formula (d⁻¹): `rPDFi = sPFi /(sDFi+NearZero)`
- Code: `rPDFi = sPFi /(sDFi+NearZero)`

### `rPDFi` [gP/gDW] *Stoichiometry*
- DESC: P ratio parameter (fixed)
- Source: fish.F90 (526)
- Formula (d⁻¹): `rPDFi = self%cPDRef`
- Code: `rPDFi = self%cPDRef`

### `rPDPisc` [gP/gDW] *Stoichiometry*
- DESC: calculate P:DW ratio of fish prey
- Source: fish.F90 (597)
- Formula (d⁻¹): `rPDPisc = sPPisc/(max(sDPisc,NearZero))`
- Code: `rPDPisc = sPPisc/(max(sDPisc,NearZero))`

### `rPDPlan` [gP/gDW] *Stoichiometry*
- DESC: calculate P:DW ratio of plankton
- Source: fish.F90 (548)
- Formula (d⁻¹): `rPDPlan = sPPlan / (sDPlan + NearZero)`
- Code: `rPDPlan = sPPlan / (sDPlan + NearZero)`

### `aCovVeg_clamped` [-] *Stoichiometry*
- DESC: macrophyte cover clamped to [0,1]
- Source: fish_pclake.F90 (382)
- Formula (d⁻¹): `aCovVeg = min(1.0_rk,aCovVeg)`
- Code: `aCovVeg = min(1.0_rk, aCovVeg)`

### `relabBEN` [-] *Stoichiometry*
- DESC: relative abundances of individual zoobenthos prey
- Source: fish_pclake.F90 (429)
- Formula (d⁻¹): `relabBEN = (sDBent*self%BENpref)/sum(sDBent*self%BENpref)`
- Code: `relabBEN = (sDBent * self%BENpref) / sum(sDBent * self%BENpref)`

### `relabPISC` [-] *Stoichiometry*
- DESC: relative abundances of individual fish prey
- Source: fish_pclake.F90 (449)
- Formula (d⁻¹): `relabPISC = (sDPisc*self%PISCpref)/sum(sDPisc*self%PISCpref)`
- Code: `relabPISC = (sDPisc * self%PISCpref) / sum(sDPisc * self%PISCpref)`

### `relabZOO` [-] *Stoichiometry*
- DESC: relative abundances of individual zooplankton prey
- Source: fish_pclake.F90 (409)
- Formula (d⁻¹): `relabZOO = (sDZoo*self%ZOOpref)/sum(sDZoo*self%ZOOpref)`
- Code: `relabZOO = (sDZoo * self%ZOOpref) / sum(sDZoo * self%ZOOpref)`

### `rNDBent` [gN/gDW] *Stoichiometry*
- DESC: N:DW ratio of zoobenthos prey
- Source: fish_pclake.F90 (428)
- Formula (d⁻¹): `rNDBent = sNBent/(sDBent+NearZero)`
- Code: `rNDBent = sNBent / (sDBent + NearZero)`

### `rNDFi` [gN/gDW] *Stoichiometry*
- DESC: N:DW ratio of fish (dynamic)
- Source: fish_pclake.F90 (393)
- Formula (d⁻¹): `rNDFi = sNFi /(sDFi+NearZero)`
- Code: `rNDFi = sNFi / (sDFi + NearZero)`

### `rNDFi_fixed` [gN/gDW] *Stoichiometry*
- DESC: N:DW ratio of fish (fixed stoichiometry)
- Source: fish_pclake.F90 (396)
- Formula (d⁻¹): `rNDFi = self%cNDFishRef`
- Code: `rNDFi = self%cNDFishRef`

### `rNDPisc` [gN/gDW] *Stoichiometry*
- DESC: N:DW ratio of fish prey
- Source: fish_pclake.F90 (448)
- Formula (d⁻¹): `rNDPisc = sNPisc/(sDPisc+NearZero)`
- Code: `rNDPisc = sNPisc / (sDPisc + NearZero)`

### `rNDZoo` [gN/gDW] *Stoichiometry*
- DESC: N:DW ratio of zooplankton prey
- Source: fish_pclake.F90 (408)
- Formula (d⁻¹): `rNDZoo = sNZoo / (sDZoo + NearZero)`
- Code: `rNDZoo = sNZoo / (sDZoo + NearZero)`

### `rPDBent` [gP/gDW] *Stoichiometry*
- DESC: P:DW ratio of zoobenthos prey
- Source: fish_pclake.F90 (427)
- Formula (d⁻¹): `rPDBent = sPBent /(sDBent+NearZero)`
- Code: `rPDBent = sPBent / (sDBent + NearZero)`

### `rPDFi` [gP/gDW] *Stoichiometry*
- DESC: P:DW ratio of fish (dynamic)
- Source: fish_pclake.F90 (392)
- Formula (d⁻¹): `rPDFi = sPFi /(sDFi+NearZero)`
- Code: `rPDFi = sPFi / (sDFi + NearZero)`

### `rPDFi_fixed` [gP/gDW] *Stoichiometry*
- DESC: P:DW ratio of fish (fixed stoichiometry)
- Source: fish_pclake.F90 (395)
- Formula (d⁻¹): `rPDFi = self%cPDFishRef`
- Code: `rPDFi = self%cPDFishRef`

### `rPDPisc` [gP/gDW] *Stoichiometry*
- DESC: P:DW ratio of fish prey
- Source: fish_pclake.F90 (447)
- Formula (d⁻¹): `rPDPisc = sPPisc /(sDPisc+NearZero)`
- Code: `rPDPisc = sPPisc / (sDPisc + NearZero)`

### `rPDZoo` [gP/gDW] *Stoichiometry*
- DESC: P:DW ratio of zooplankton prey
- Source: fish_pclake.F90 (407)
- Formula (d⁻¹): `rPDZoo = sPZoo / (sDZoo + NearZero)`
- Code: `rPDZoo = sPZoo / (sDZoo + NearZero)`

### `sDFiOS_init` [gDW/m3] *Stoichiometry*
- DESC: initialize total biomass of other stages
- Source: fish_pclake.F90 (461)
- Formula (d⁻¹): `sDFiOS = 0.0_rk`
- Code: `sDFiOS = 0.0_rk`

### `sDFiOS_with_adult` [gDW/m3] *Stoichiometry*
- DESC: total biomass incl. older stage
- Source: fish_pclake.F90 (468)
- Formula (d⁻¹): `sDFiOS = sDFiOS + sDAd`
- Code: `sDFiOS = sDFiOS + sDAd`

### `sDFiOS_with_juvenile` [gDW/m3] *Stoichiometry*
- DESC: total biomass incl. younger stage
- Source: fish_pclake.F90 (464)
- Formula (d⁻¹): `sDFiOS = sDFiOS + sDJu`
- Code: `sDFiOS = sDFiOS + sDJu`

### `sDFiOS_with_other_stages` [gDW/m3] *Stoichiometry*
- DESC: total biomass incl. other stages
- Source: fish_pclake.F90 (475)
- Formula (d⁻¹): `sDFiOS = sDFiOS + sDFiSt`
- Code: `sDFiOS = sDFiOS + sDFiSt`

### `sDFiSt_sum` [gDW/m3] *Stoichiometry*
- DESC: sum of other not-coupled stage biomasses
- Source: fish_pclake.F90 (474)
- Formula (d⁻¹): `sDFiSt = sum(sDFiSt_all)`
- Code: `sDFiSt = sum(sDFiSt_all)`

## Temperature

### `uFunTmFish` [-] *Temperature*
- DESC: temperature correction of fish vital rates (Gaussian)
- Source: fish_pclake.F90 (482)
- Formula (d⁻¹): `uFunTmFish = uFunTmGaus(uTm,self%cSigTmFish,self%cTmOptFish)`
- Code: `uFunTmFish = uFunTmGaus(uTm, self%cSigTmFish, self%cTmOptFish)`

## Temperature functions

### `uFunTmArrh` [-] *Temperature functions*
- DESC: Arrhenius temperature dependency
- Source: utility.F90 (27-35)
- Formula (d⁻¹): `cTheta**(uTm-cTmRef)`
- Code: `uFunTmArrh = cTheta**(uTm-cTmRef)`

### `uFunTmGaus` [-] *Temperature functions*
- DESC: Gaussian temperature dependency
- Source: utility.F90 (40-48)
- Formula (d⁻¹): `exp(-0.5/cSigTm**2 *((uTm-cTmOpt)**2 - (cTmRef -cTmOpt)**2))`
- Code: `uFunTmGaus = exp(-0.5_rk/cSigTm**2 *((uTm-cTmOpt)**2 - (cTmRef -cTmOpt)**2))`

### `uFunTmQ10` [-] *Temperature functions*
- DESC: Q10 temperature dependency of plants
- Source: utility.F90 (53-61)
- Formula (d⁻¹): `(cQ10Veg)**(0.1*(uTm-cTmRef))`
- Code: `uFunTmQ10 = ((cQ10Veg )** (0.1_rk * (uTm - cTmRef)))`

### `uFunTmMinSiW` [-] *Temperature functions*
- DESC: remineralization Si temperature function
- Source: abiotic_water.F90 (198-198)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaMinSiW)`
- Code: `uFunTmMinSiW = uFunTmArrh(uTm,self%cThetaMinSiW)`

### `uFunTmNitr` [-] *Temperature functions*
- DESC: nitrification temperature function
- Source: abiotic_water.F90 (197-197)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaNitrW)`
- Code: `uFunTmNitr = uFunTmArrh(uTm,self%cThetaNitrW)`

### `uFunTmDifO2` [-] *Temperature functions*
- DESC: temperature function of O2 diffusion
- Source: abiotic_sediment.F90 (226-226)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaDifO2)`
- Code: `uFunTmDifO2= uFunTmArrh(uTm,self%cThetaDifO2)`

### `uFunTmNitr` [-] *Temperature functions*
- DESC: Temperature dependence of nitrification
- Source: abiotic_sediment.F90 (238-238)
- Formula (d⁻¹): `uFunTmArrh(uTm,cThetaNitrS)`
- Code: `uFunTmNitr=uFunTmArrh(uTm,self%cThetaNitrS)`

### `uFunTmMinS` [-] *Temperature functions*
- DESC: bio-transformation temperature function
- Source: om_pool.F90 (422)
- Formula (d⁻¹): `uFunTmMinS = uFunTmArrh(uTm,self%cThetaMinS)`
- Code: `uFunTmMinS = uFunTmArrh(uTm,self%cThetaMinS)`

### `uFunTmMinW` [-] *Temperature functions*
- DESC: bio-transformation temperature function
- Source: om_pool.F90 (304)
- Formula (d⁻¹): `uFunTmMinW = uFunTmArrh(uTm,self%cThetaMinW)`
- Code: `uFunTmMinW = uFunTmArrh(uTm,self%cThetaMinW)`

### `uFunTmZoo` [-] *Temperature functions*
- DESC: calc. temperature correction of zooplankton vital rates
- Source: zooplankton.F90 (281)
- Formula (d⁻¹): `uFunTmGaus(uTm,cSigTmZoo,cTmOptZoo)`
- Code: `uFunTmZoo =uFunTmGaus(uTm,self%cSigTmZoo,self%cTmOptZoo)`

### `uFunTmBent` [-] *Temperature functions*
- DESC: calc. temperature correction of zoobenthos vital rates
- Source: zoobenthos.F90 (314)
- Formula (d⁻¹): `uFunTmGaus(uTm,cSigTmBent,cTmOptBent)`
- Code: `uFunTmBent = uFunTmGaus(uTm,self%cSigTmBent,self%cTmOptBent)`

### `uFunTmProdVeg` [-] *Temperature functions*
- DESC: temperature function for production (Gaussian mode)
- Source: macrophytes.F90 (399)
- Formula (d⁻¹): `uFunTmGaus(uTm, cSigTmVeg, cTmOptVeg)`
- Code: `if (self%lGausVeg) uFunTmProdVeg = uFunTmGaus(uTm, self%cSigTmVeg, self%cTmOptVeg)`

### `uFunTmProdVeg` [-] *Temperature functions*
- DESC: temperature function for production (Q10 mode)
- Source: macrophytes.F90 (402)
- Formula (d⁻¹): `uFunTmQ10(uTm, cQ10ProdVeg)`
- Code: `if (.NOT. self%lGausVeg) uFunTmProdVeg = uFunTmQ10(uTm, self%cQ10ProdVeg)`

### `uFunTmRespVeg` [-] *Temperature functions*
- DESC: temperature function for respiration (Gaussian mode)
- Source: macrophytes.F90 (400)
- Formula (d⁻¹): `uFunTmProdVeg`
- Code: `if (self%lGausVeg) uFunTmRespVeg = uFunTmProdVeg`

### `uFunTmRespVeg` [-] *Temperature functions*
- DESC: temperature function for respiration (Q10 mode)
- Source: macrophytes.F90 (403)
- Formula (d⁻¹): `uFunTmQ10(uTm, cQ10RespVeg)`
- Code: `if (.NOT. self%lGausVeg) uFunTmRespVeg = uFunTmQ10(uTm, self%cQ10RespVeg)`

### `uFunTmFish` [-] *Temperature functions*
- DESC: calc. temperature correction of fish vital rates
- Source: fish.F90 (614)
- Formula (d⁻¹): `uFunTmFish = uFunTmGaus(uTm,self%cSigTmFish,self%cTmOptFish)`
- Code: `uFunTmFish = uFunTmGaus(uTm,self%cSigTmFish,self%cTmOptFish)`

### `uFunTmDif` [-] *Temperature functions*
- DESC: temperature function of diffusion
- Source: sediment_exchange.F90 (511)
- Formula (d⁻¹): `uFunTmDif= uFunTmArrh(uTm,self%cThetaDif)`
- Code: `uFunTmDif= uFunTmArrh(uTm,self%cThetaDif)`

### `uFunTmSed` [-] *Temperature functions*
- DESC: temperature correction of sedimentation
- Source: sediment_exchange.F90 (468)
- Formula (d⁻¹): `uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)`
- Code: `uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)`

### `uFunTmSed` [-] *Temperature functions*
- DESC: temperature correction of sedimentation
- Source: resus_sed.F90 (249)
- Formula (d⁻¹): `uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)`
- Code: `uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)`

## Vertical movement

### `qSWIM` [-] *Vertical movement*
- DESC: determine vertical movements based on O2 and light
- Source: zooplankton.F90 (486-502)
- Formula (d⁻¹): `(if par > cMaxLight: qSWIM=-1; elseif par < cMinLight: qSWIM=1; if O2 < cMinO2: qSWIM=1)`
- Code: `if (self%qTrans == 2 .OR. self%qTrans ==3) then ... qSWIM = 0 ... if (par .GT. self%cMaxLight) then qSWIM = -1 elseif (par .LT. self%cMinLight) then qSWIM = 1 ... if (O2 < self%cMinO2) then qSWIM = 1 endif`

### `sCZoo migration` [m/d] *Vertical movement*
- DESC: set C migration speed
- Source: zooplankton.F90 (506)
- Formula (d⁻¹): `qSWIM*cVswim`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sCZoo,qSWIM*self%cVswim)`

### `sDZoo migration` [m/d] *Vertical movement*
- DESC: set DW migration speed
- Source: zooplankton.F90 (503)
- Formula (d⁻¹): `qSWIM*cVswim`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sDZoo,qSWIM*self%cVswim)`

### `sNZoo migration` [m/d] *Vertical movement*
- DESC: set N migration speed
- Source: zooplankton.F90 (505)
- Formula (d⁻¹): `qSWIM*cVswim`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sNZoo,qSWIM*self%cVswim)`

### `sPZoo migration` [m/d] *Vertical movement*
- DESC: set P migration speed
- Source: zooplankton.F90 (504)
- Formula (d⁻¹): `qSWIM*cVswim`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sPZoo,qSWIM*self%cVswim)`

### `qSWIM` [-] *Vertical movement*
- DESC: default no swimming (O2/light method)
- Source: fish.F90 (1170)
- Formula (d⁻¹): `qSWIM = 0`
- Code: `qSWIM = 0`

### `qSWIM` [-] *Vertical movement*
- DESC: swim down if light above max threshold
- Source: fish.F90 (1174)
- Formula (d⁻¹): `qSWIM = -1`
- Code: `qSWIM = -1 [if par .GT. self%cMaxLight]`

### `qSWIM` [-] *Vertical movement*
- DESC: swim up if light below min threshold
- Source: fish.F90 (1176)
- Formula (d⁻¹): `qSWIM = 1`
- Code: `qSWIM = 1 [if par .LT. self%cMinLight]`

### `qSWIM` [-] *Vertical movement*
- DESC: swim up if low oxygen
- Source: fish.F90 (1181)
- Formula (d⁻¹): `qSWIM = 1`
- Code: `qSWIM = 1 [if O2 < self%cMinO2]`

### `sCFi_vmove` [m/d] *Vertical movement*
- DESC: set C migration speed
- Source: fish.F90 (1189)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sCFi,qSWIM*self%cVswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sCFi,qSWIM*self%cVswim)`

### `sDFi_vmove` [m/d] *Vertical movement*
- DESC: set DW migration speed
- Source: fish.F90 (1186)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sDFi,qSWIM*self%cVswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sDFi,qSWIM*self%cVswim)`

### `sNFi_vmove` [m/d] *Vertical movement*
- DESC: set N migration speed
- Source: fish.F90 (1188)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sNFi,qSWIM*self%cVswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sNFi,qSWIM*self%cVswim)`

### `sPFi_vmove` [m/d] *Vertical movement*
- DESC: set P migration speed
- Source: fish.F90 (1187)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sPFi,qSWIM*self%cVswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sPFi,qSWIM*self%cVswim)`

## vertical movement - derivatives

### `sCW` [-] *vertical movement - derivatives*
- DESC: set C migration speed to settling rate + movement
- Source: phytoplankton.F90 (912)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sCW,vSWIM)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sCW,vSWIM)`

### `sDW` [-] *vertical movement - derivatives*
- DESC: set DW migration speed to settling rate + movement
- Source: phytoplankton.F90 (909)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sDW,vSWIM)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sDW,vSWIM)`

### `sNW` [-] *vertical movement - derivatives*
- DESC: set N migration speed to settling rate + movement
- Source: phytoplankton.F90 (911)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sNW,vSWIM)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sNW,vSWIM)`

### `sPW` [-] *vertical movement - derivatives*
- DESC: set P migration speed to settling rate + movement
- Source: phytoplankton.F90 (910)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sPW,vSWIM)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sPW,vSWIM)`

## vertical movement - qTrans=1

### `vSWIM` [m/d] *vertical movement - qTrans=1*
- DESC: no vertical migration, settling only
- Source: phytoplankton.F90 (886)
- Formula (d⁻¹): `vSWIM = self%cVSet`
- Code: `vSWIM = self%cVSet`

## vertical movement - qTrans=2/4

### `vSWIM (default)` [m/d] *vertical movement - qTrans=2/4*
- DESC: no nutrient starvation and no light-based VM
- Source: phytoplankton.F90 (899)
- Formula (d⁻¹): `vSWIM = self%cVSet`
- Code: `vSWIM = self%cVSet`

### `vSWIM (starved)` [m/d] *vertical movement - qTrans=2/4*
- DESC: swim down if nutrient starved
- Source: phytoplankton.F90 (890)
- Formula (d⁻¹): `vSWIM = -self%cVSwim`
- Code: `vSWIM = -self%cVSwim`

## vertical movement - qTrans=3

### `vSWIM (par<=fLVMmin)` [m/d] *vertical movement - qTrans=3*
- DESC: no swimming, so settling speed
- Source: phytoplankton.F90 (906)
- Formula (d⁻¹): `vSWIM = self%cVSet`
- Code: `vSWIM = self%cVSet`

### `vSWIM (par>fLVMmin)` [m/d] *vertical movement - qTrans=3*
- DESC: swim up towards (more) light
- Source: phytoplankton.F90 (904)
- Formula (d⁻¹): `vSWIM = self%cVSwim`
- Code: `vSWIM = self%cVSwim`

## vertical movement - qTrans=4

### `vSWIM (light, par<=fLVMmin)` [m/d] *vertical movement - qTrans=4*
- DESC: no swimming, settling speed
- Source: phytoplankton.F90 (896)
- Formula (d⁻¹): `vSWIM = self%cVSet`
- Code: `vSWIM = self%cVSet`

### `vSWIM (light, par>fLVMmin)` [m/d] *vertical movement - qTrans=4*
- DESC: swim up towards light when nutrient replete
- Source: phytoplankton.F90 (894)
- Formula (d⁻¹): `vSWIM = self%cVSwim`
- Code: `vSWIM = self%cVSwim`

## Vertical_movement

### `qSWIM_default` [-] *Vertical_movement*
- DESC: default setting: no swimming (qTrans>=2)
- Source: fish_pclake.F90 (896)
- Formula (d⁻¹): `qSWIM = 0`
- Code: `qSWIM = 0`

### `qSWIM_light_down` [-] *Vertical_movement*
- DESC: swim down if light level above threshold (qTrans=3)
- Source: fish_pclake.F90 (899-900)
- Formula (d⁻¹): `if par > cMinLight: qSWIM = -1`
- Code: `if (par .GT. self%cMinLight) then qSWIM = -1`

### `qSWIM_oxygen_up` [-] *Vertical_movement*
- DESC: swim up if low oxygen (qTrans>=2)
- Source: fish_pclake.F90 (904-905)
- Formula (d⁻¹): `if O2 < cMinO2: qSWIM = 1`
- Code: `if (O2 < self%cMinO2) then qSWIM = 1`

### `qSWIM_passive` [-] *Vertical_movement*
- DESC: no swimming (qTrans=1)
- Source: fish_pclake.F90 (908)
- Formula (d⁻¹): `qSWIM = 0`
- Code: `qSWIM = 0`

### `sDFi_migration` [m/d] *Vertical_movement*
- DESC: set DW migration speed
- Source: fish_pclake.F90 (910)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sDFi,qSWIM*Vswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sDFi, qSWIM * self%Vswim)`

### `sNFi_migration` [m/d] *Vertical_movement*
- DESC: set N migration speed
- Source: fish_pclake.F90 (912)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sNFi,qSWIM*Vswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sNFi, qSWIM * self%Vswim)`

### `sPFi_migration` [m/d] *Vertical_movement*
- DESC: set P migration speed
- Source: fish_pclake.F90 (911)
- Formula (d⁻¹): `_SET_VERTICAL_MOVEMENT_(self%id_sPFi,qSWIM*Vswim)`
- Code: `_SET_VERTICAL_MOVEMENT_(self%id_sPFi, qSWIM * self%Vswim)`

