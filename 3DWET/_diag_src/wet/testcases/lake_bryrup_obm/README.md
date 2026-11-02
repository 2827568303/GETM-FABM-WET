## Model set-up for fish optimal behaviour model

This lake model setup represents a one year cycle for Lake Bryrup, Denmark, based on work presented in Chen et al., 2020, Water, (see "Lake Bryrup" test case). 
The one year forcing of weather and nutrient input was looped to create a 250-year period. 
This setup was then used to test different model parameterizations of the optimal behaviour model, as described in Schnedler-Meyer & Andersen, submitted.
 
**You should run "Lake Bryrup OBM" setup with WET version 0.2.0 or newer.**

In addition to the required files to run "Lake Bryrup OBM" test case, this setup includes:

**Four versions of fabm.yaml:**

* fabm_control_no_OBM.yaml :

Control version with OBM module for both fish groups disabled (qODB: 0).

* fabm_fig6.yaml :

Version with OBM module for both fish groups enabled and selected OBM parameters to plot food web dynamics (figure 6).

** Five version of inflow_chem.dat ** with changes in inflow nutrient concentrations corresponding (100 pct equals control, ie. no change):

* inflow_chem-20pct.dat
* inflow_chem-50pct.dat
* inflow_chem-100pct.dat
* inflow_chem-200pct.dat
* inflow_chem-400pct.dat

Current fabm.yaml and inflow-chem.dat are fabm_control_no_OBM.yaml and inflow_chem-100pct.dat, respectively.
For a detailed description of the parameterization of fish module and the nutrient input scenarios, see Schnedler-Meyer & Andersen, submitted.

