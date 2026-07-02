## The **Water Ecosystems Tool (WET)** model 

WET is a new generation, open source, aquatic ecosystem model. It is based on FABM-PCLake by Fenjuan Hu et al. (2016), and includes features from the original PCLake model by Jan Janse (1997), as well as selected features from CAEDYM (Hamilton and Schladow 1997). 
The WET model is completely modularized, which allow a highly flexible configuration of the food web and the conceptual model. WET can describe interactions between multiple trophic levels, including piscivorous, zooplanktivorous and benthivorous fish, zooplankton, zoobenthos, phytoplankton and rooted, submerged macrophytes. 
The model accounts for oxygen and carbon dynamics and a fully closed nutrient cycle for nitrogen and phosphorus. In contrast to the original PCLake model, WET enables coupling to hydrodynamic models (e.g., GOTM and GETM), and a range of additional features, including a flexible configuration of the conceptual model (i.e. any number of phytoplankton groups, zooplankton etc.), bottom-shear-dependent resuspension, a choice between multiple light-limitation functions for primary producers, additional organic matter fractions, options for vertical mobility of phytoplankton, zooplankton and fish, optimal fish foraging, and coupling to other biogeochemical models available through FABM.

For the latest stable version of WET, download [version 0.2.0](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/releases/v0.2.0)

**The master branch includes the latest development with bivalves. See _Bivalves module_ sections below for further details on these new modules. The master branch also includes the latest development with carbon in all modules and modularization of organic matter pools and their bio-transformations in the module om_pool.f90. See _OM pool module_ section below for further details on this new module.**

WET was originally published in:
**Water Ecosystems Tool (WET) 0.1.0 – a new generation of flexible aquatic ecosystem model**, Geoscientific Model Development 15: 3861-3871
by Schnedler-Meyer, N. A.,Andersen, T. K., Hu, F., Bolding, K., Nielsen, A., and Trolle, D.  2022

New features of WET v0.2.0 is documented in:
**Dining in danger: Resolving adaptive fish behavior increases realism of modeled ecosystem dynamics**, Ecology and Evolution 14
by Schnedler-Meyer and N. A.,Andersen, T. K., 2024

FABM-PCLake was originally published in: 

**FABM-PCLake – linking aquatic ecology with hydrodynamics**, Geoscientific Model Development 9: 2271-2278,
by Hu, F., Bolding, K., Bruggeman, J., Jeppesen, E., Flindt, M. R., van Gerven, L., Janse, J. H., Janssen, A. B. G., Kuiper, J. J., Mooij, W. M., and Trolle, D. 2016. 

The original PCLake model was published in:
**A model of nutrient dynamics in shallow lakes in relation to multiple stable states**, Hydrobiologia 342/343: 1-8, by Janse, J. 1997.



###### If you have questions and suggestions regarding this model, please contact the developer team:
* Nicolas Azaña Schnedler-Meyer: niaz@aqua.dtu.dk
* Tobias Kuhlmann Andersen: tkan@aqua.dtu.dk 
* Dennis Trolle: dt@wateritech.com                                           
* Anders Nielsen: an@wateritech.com

## How to reference WET
All versions of the Water Ecosystems Tool (WET) model are open-source and distributed under the Creative Commons Attribution 4.0 International License. This license permits redistribution and reuse of the WET source code, provided that the WET model development team is appropriately credited.
When citing or referencing WET in scientific work, please follow these guidelines:

1. **Specify the model version**

    Clearly indicate the exact version of the WET model that was used.

2. **Reference the Zenodo repository**

    Cite the corresponding Zenodo repository entry for the model version applied in your work. Alternatively, you can reference the corresponding WET Gitlab release.

3. **Include related scientific publications**

    If available, reference any scientific publications that document the applied model version.

4.	**Acknowledge specific model developments (if relevant)**

    When your work makes use of, or discusses, particular model developments, also cite the relevant scientific documentation in addition to the applied model version.


## Major revision history
New bivalve module by Dennis Trolle and developer team, July 2025

Incorporation of carbon in all modules (in preparation for greenhouse gas module) by Tobias Kuhlmann Andersen, June 2025

Modularized organic matter bio-transformations and re-work of resus_sed.f90 into sediment_exchange.f90 by Tobias Kuhlmann Andersen and developer team

Feeding overhaul and optimal fish foraging to the master: November 2021 to February 2023 by Nicolas Azaña Schnedler-Meyer and Tobias Kuhlmann Andersen
With release of stable [version 0.2.0](https://gitlab.com/wateritech-public/waterecosystemstool/wet/-/releases/v0.2.0): 13 December 2023

Zoobenthos oxygen-stress mortality: November 2022 by Tobias Kuhlmann Andersen

Release of stable [version 0.1.0](https://gitlab.com/WET/wet/-/releases#v0.1.0): 5 June 2021, by Nicolas Azaña Schnedler-Meyer and developer team

Release of WET, which replaces the FABM-PCLake repository: 25 February 2020, by Nicolas Azaña Schnedler-Meyer and developer team

Original implementation of FABM-PCLake in its own repository: 06 March 2017, by Fenjuan Hu and developer team

## C implemented in WET
WET can now simulate, in addition to dry-weight, nitrogen and phosphorous, carbon content in all functional groups, both organic matter module (om_pool) and food web groups. Carbon content follows nitrogen and phosphorous content in functional groups with a state variable for the carbon concentration and diagnostic variable for C:DW ratio. No new parameters have been included. For organic matter instances (om_pool.F90), carbon bio-transformation is scaled by DW bio-transformation and C:DW ratio. For primary producers (phytoplankton.F90 and macrophytes.F90) C:DW are fixed by the constant cCPerDW. For animals (zooplankton.F90, zoobenthos.F90 and fish.F90), C:DW is dynamic, but regulated by scaling respiration  to a user-defined C:DW ratio (the parameter cCDRef, identical to regulation of N and P content). 

## OM pool module
Three (dead) organic matter (OM) pools existed in FABM-PCLake and WET versions older than v0.2.0 October 2024: particulate organic matter (POM), dissolved organic matter (DOM), both in water and sediment, and humus, only in sediment. To allow for a more flexible biogeochemical and food web setup and to be able to include new OM pools during runtime configuration, for instance colored DOM or coarse POM, we removed POM, DOM and humus pools and processes from mainly abiotic_water.F90 and abiotic_sediment.F90 as well as resus_sed.F90 and burial.F90, and wrote a new module, named om_pool.F90, to handle specific OM pools. 

In-depth documentation of the new modularization of OM pools is currently not available. Below is a brief description and user manual for the new module and other changes to the WET code from the modularization.

**New module: om_pool.F90**

The new om_pool module is optional and currently handles bio-transformations, in water and sediment, and light extinction of an OM pool. The module operates with two clear distinguishing of OM pools: either particulate OM (POM) or dissolved OM (DOM). Both POM and DOM are subject to resuspension. POM will sediment out of water and DOM will diffuse between sediment-water interface. POM instances also need to be accounted for in burial.F90 when calculating sediment turnover.
To be able to reproduce previous WET case study configurations, several toggles have been implemented to reproduce historic descriptions of specific OM pools such as humus, particle OM and dissolved OM.


_Notes on annotation and terminology_

A module is a Fortan code block in WET describing a specific set of processes, e.g. phytoplankton.F90 and om_pool.F90

An instance is a specific parameterized instance of a module coupled to other instances. As WET relies on FABM organization and is modularized, all components of a WET model consist of different parameterized and coupled instances. Some modules are required, and some modules are optional (see WET paper for more on this). For example, a WET model configuration should always include instances of abiotic_water.F90 and abiotic_sediment.F90, and could include three instances of phytoplankton.F90 parameterized and coupled to represent cyanobacteria, diatoms and green algae.

All parameters are in italic, e.g. _lPOMtoDOM_ and _fRefrDWS_.

All instance coupling is in bold e.g. **DW_transformation_water** and **pom_model1**. If coupling starts with **X_** three couplings exist for dry-weight, nitrogen and phosphorous: **DW_**, **N_** and **P_**.
If a sediment state variable should be accessible to water state variables, then sediment state variable needs a pelagic mirror (ends in _PV). The pelagic mirror is calculated by the module bot_pel_interface.F90.


**Toogles for adaptable configuration in an om_pool instance**

_lTransPV_: If om_pool coupling **X_transformation_sediment** target is projected to the water column by state_variable_PV (pelagic mirror) this parameter should be set to true.

_lPOMtoDOM_: If this om_pool instance is POM and **DW_transformation_water** and **DW_transformation_sediment** points to a DOM om_pool instance, _lPOMtoDOM_ should be set to true. This is required for burial.F90 when accounting for rate of change of all POM groups in sediment.

_fRefrDWS_ and _fRefrNutS_: Parameters describe fraction of biotransformation to be split between sinks coupling **X_transformation_sediment** and **X_refractory_sediment**. If one of the parameters are above 0, then om_pool instance should couple to both **X_transformation_sediment** and **X_refractory_sediment**. _fRefrDWS_ describes fraction of DW to **DW_refractory_sediment** and _fRefrNutS_ describes fraction to _N_refractory_sediment_ and _P_refractory_sediment_.

_lRefrPV_: If _fRefrDWS_ or _fRefrNutS_ is > 0 and **X_refractory_sediment** is a POM group with a pelagic mirror, _lRefrPV_ should be set to true.

_lRefrpool_: If the om_pool instance sediment biotransformation is not costing oxygen or nitrate and is dependent upon the oxygen fraction of the sediment (afOxySed), then _lRefrpool_ should be set to true. This toogle was implemented to reproduce historic description of the instance humus in FABM-PCLake and older versions of WET.

_lTransDWtarget_: If om_pool instance should not couple to a specific state variable for **DW_transformation_water** and **DW_transformation_sediment**, _lTransDWtarget_ should be set to true. This toogle was implemented to run current OM_module WET version without pointing to carbon gas (CO2 or CH4) after biotransformation of DOM.

fabm-wet.yaml file includes default parameterization identical to older versions of OM parameter values (with DOM, POM and humus pools), but in current om_pool configuration. 

Modularization of OM pools has also led to changes in other modules.

**Converting resus_sed.F90 into sediment_exchange.F90**

Now, sediment_exchange.F90 includes all water-sediment interactions: Resuspension, sedimentation of particles and diffusion of dissolved substances.
To distinguish which om_pool instances are subject to sedimentation or diffusion, user must point to each POM and DOM instance in sediment_exchange coupling and set number of POM and DOM instances (with nPOM and nDOM parameters). 


**Updated burial.F90 to handle new OM pools**

Each om_pool instance registers the diagnostic tDPOMS. If _lPOMtoDOM_ = true then tDPOMS is updated, else tDPOMS is set to 0 for this om_pool instance. This is required for burial to know rate-of-change (ROC) for all POM. If _lPOMtoDOM_ = false then the target of biotransformation is another particulate OM pool. 

As in sediment_exchange instance, user should point to each POM and DOM instance in burial coupling and set number of POM and DOM instances (with _nPOM_ and _nDOM_ parameters, respectively). The user also needs to specify how many and which parameters of POM instances are subject to sediment_exchange with _nPOMexch_ and **POM_exchange_update**. Be aware that sediment_exchange/_nPOM_ should match burial/_nPOMexch_.

Be aware that burial.F90 requires to point to POM instance to supply OM if sediment turnover is negative (i.e. addition of OM to sediment as negative burial is occurring.). This is done with the couplings **humus_X_in_deep_sediment**.


**Separating bot_pel_conv diagnostic into bot_pel_interface.F90 module**

To avoid circle dependencies in the new WET OM_module version, we removed bot_pel_conv diagnostic from abiotic_sediment.F90 and created its own module: bot_pel_interface.f90.

**Other considerations during this development**

This WET OM_module version includes, although currently commented out, code from [DOMCAST](https://github.com/fabm-model/fabm/blob/1a653ed8bfeeec8ee22cb87f96e9f11f3142397b/src/models/niva/domcast/domcast.F90#L4 ) to describe photo-oxidation, photo-mineralization, and flocculation. WET developer team are available to support users wtih implementation and testing of photo-oxidation, photo-mineralization, and flocculation in WET.

For more details on new OM pool version, please contact Tobias Kuhlmann Andersen.


## Conversion of old feeding parameters to new
As of Novemer 2021 and with stable release v0.2.0, the feeding functions of the heterotrophic modules (fish, zooplankton and zoobenthos) have been changed to a different formulation of the Holling Disc equation.
Version 0.2.0 uses a prey-specific clearance rate (cClear), a prey specific gut occupation factor (fGutOcc), ad a maximum consumption rate (kDConsMax).
Conversion from the old parameters of maximum assimilation, preferences, and half-saturation constant (kDAss, pref and hD) can be done as follows:

kDConsmax = kDAss/fDAss

cClear = kDConsMax/hD*pref

The new gut occupation parameter fGutOcc represent how consumption of a specific prey saturates the predator, relative to other prey. Thus, only relative fGutOcc values between prey types matter.

## Module overview
WET is comprised of 14 Fortran modules, including:

* wet_model_library.f90
* utility.f90
* bot_pel_conv.f90
* sediment_exchange.f90
* burial.f90
* abiotic_water.f90
* abiotic_sediment.f90
* om_pool.f90
* phytoplankton.f90
* macrophytes.f90
* zooplankton.f90
* zoobenthos.f90
* fish.f90
* fish_PCLake.f90
* bivalves.f90

The overall tasks of individual modules are described in brief below. 


### wet_model_library

This module is a FABM wrapper module for initialising all the modules of WET.


### utility

This module includes a day-light function, and 3 types of temperature functions that are used throughout the WET model: 

* uFunTmArrh the Arrhenius temperature function 
* uFunTmGaus the Gaussian (optimum) temperature function 
* uFunTmQ10 the Q10 temperature coefficient function

### bot_pel_conv

This module creates pelagic mirrors of sediment state variables to interact with pelagic state variables. Previously, this function resided in abiotic_water module.

### sediment_exchange

This module handles resuspension, sedimention and diffusion processes between water and sediment. This module was previously named resus_sed.f90 and did not include diffusion. 

### burial

This module includes a burial process, which is the loss of a small layer of sediment as a compensation for sediment thickening, as the model assumes that only the sediment top (e.g. 10 cm) layer actively takes part in the nutrient cycling.

### abiotic_water

This module describes the state variables which are related to abiotic processes and state variables in the water column, including: inorganic matter (IM), dissolved nutrients (ammonium, nitrate, phosphate and dissolved silica dioxide), immobilized phosphorus (absorbed phosphorus) and dissolved oxygen. 

The processes described in this module include nitrification, denitrification, phosphorus sorption and oxygen reaeration.  

### abiotic_sediment

This module describes the processes and state variables which are related to abiotic processes in the sediment, including: inorganic matter (IM), dissolved nutrients (ammonia, nitrate and phosphate) immobilized phosphorus (adsorbed phosphorus).

The processes described in this module include nitrification, denitrification, and phosphorus sorption. The module also describes the sediment oxic layer fraction, which is an important diagnostic variable used in several process descriptions, e.g. relating to sorption of phosphorus. Settling and resuspension processes are described in the resus_sed module.

### om_pool
This module describes bio-transformations, in water and sediment, and light extinction of an OM pool. The module operates with two clear distinguishing of OM pools: either particulate OM (POM) or dissolved OM (DOM). Both POM and DOM are subject to resuspension. POM will sediment out of water and DOM will diffuse between sediment-water interface.

### phytoplankton

This module describes the processes and state variables related to a phytoplankton group in both the water column and the sediment. Each phytoplankton group is accounted for in three elements including dry-weight, nitrogen and phosphorus. For diatoms, the silica concentration is not a state variables, but a diagnostic variable, as the model assumes a fixed Si/DW ratio for diatoms (i.e. 0.1).

The processes described in this module include assimilation (primary production), nutrient uptake, nitrogen fixation, respiration, excretion, mortality, oxygen consumption/production, settlement and vertical migration.

The zooplankton and zoobenthos modules influence phytoplankton through grazing.

### macrophytes

This module describes the processes and state variables related to submerged macrophytes, and is implemented as a benthic module. Macrophytes are accounted for in three elements including dry-weight, nitrogen and phosphorus, and is further subdivided into a (dynamic) shoot and root fraction.

The processes described in this module include assimilation (primary production), nutrient updake, respiration, excretion, mortality and migration. The latter relates to the user option of including a colonisation rate for macrophytes, e.g., originating from the surrounding catchment.

The macrophyte module influence resuspension described in the resus_sed module. The macrophyte module also contain the macrophytes coverage percentage, which is a key diagnostic variable used by the fish and phytoplankton modules.

### zooplankton

This module describes the processes and state variables relating to zooplankton, and is implemented as a pelagic module. Zooplankton are accounted for in three elements including dry-weight, nitrogen and phosphorus. 

The processes described in this module include phytoplankton and POM grazing and assimilation, respiration, excretion, mortality and vertical migration.

This module includes the (default) option of Optimal Diet Breadth (ODB) calculation, which choses the optimal set of prey types to include in the diet from the set of available (coupled) prey types. The optimal prey set is the one that maximizes consumption, based on both prey availability, but also based on the gut occupation factors of individual prey.
this means that abundant, but low quality (low energy concentration, or difficult to digest) may be excluded from the diet, when better quality prey is available, but included when prey is scarce. 

The fish module (and other zooplankton groups) can influence zooplankton through predation. 

### zoobenthos

This module describes the processes and state variables relating to zoobenthos, and is implemented as a benthic module. Zoobenthos are accounted for in three elements including dry-weight, nitrogen and phosphorus. Zoobenthos feed on detritus in the sediments, and on settled phytoplankton. 

The processes described in this module include consumption and assimilation, migration, respiration, excretion and mortality.

The fish module (and other zoobenthos groups) can influence zoobenthos through predation. 

### fish

The fish module describes the processes and state variables relating to fish, and is implemented as a pelagic module. Fish are accounted for in three elements including dry-weight, nitrogen and phosphorus. Fish may be configured as either planktivorous, benthivorous, herbivorous or piscivorous, or as a mix of the three. 

The processes described in this module include migration, reproduction (moving biomass from adult to juvenile fish), aging (moving biomass from juvenile to adult fish), assimilation (grazing on vegetation and phytplankton or predation on zooplankton, zoobenthos, or fish), respiration, excretion and mortality.

Other fish modules can influence the fish module through predation, reproduction or aging.

This module includes the (default) option of Optimal Diet Breadth (ODB) calculation, which choses the optimal set of prey types to include in the diet from the set of available (coupled) prey types. The optimal prey set is the one that maximizes consumption, based on both prey availability, but also based on the gut occupation factors of individual prey.
this means that abundant, but low quality (low energy concentration, or difficult to digest) may be excluded from the diet, when better quality prey is available, but included when prey is scarce. 

The module also includes the option of optimal foraging effort, through the inclusion of a Foraging Arena (FA). both prey availablity and vulnerability to predation may be different in and out of the FA, and fish calculate the optimal frction of time spent in the FA in each time step, based on the balance between predation and food availability.
This foraging arena can represent both physical habitat, such as the open water column vs refuge habitat such as macrophyte beds, but may also represent increased feeding activity, or risk-reducing behaviors such as schooling.

A full description of both the ODB and optimal foraging options, as well as an exploration of the resulting dynamics is documented in [Schnedler-Meyer and Andersen (2024)](https://doi.org/10.1002/ece3.70020).

### fish_pclake

This fish module is included for backwards compatibility of models, and is the basic modularized PCLake-type fish module that was relesed with WET 0.1.0. 

The module describes the processes and state variables relating to fish, and is implemented as a pelagic module. Fish are accounted for in three elements including dry-weight, nitrogen and phosphorus. Fish may be configured as either planktivorous, benthivorous, herbivorous or piscivorous, or as a mix of the three. 

The processes described in this module include migration, reproduction (moving biomass from adult to juvenile fish), aging (moving biomass from juvenile to adult fish), assimilation (grazing on vegetation and phytplankton or predation on zooplankton, zoobenthos, or fish), respiration, excretion and mortality.

Other fish modules can influence the fish module through predation, reproduction or aging.

### bivalves

**New module: bivalves.F90**

The new bivalve module is optional and enables simulation of one or several bivalves and how they may influence organic matter, nutrient cycling and light extinction. The module can be used to simulate several size classes of bivalves, and, optionally, also transfer of biomass between these through spawning and aging. The simulated ingestion of bivalves is dependent on temperature, food availability, suspended inorganic solids and the density of bivalves. In addition, the mortality rate of bivalves is dependent on oxygen. Additional details on the concept is described in the Whitepaper by WateriTech on www.wateritech.com/whitepapers.