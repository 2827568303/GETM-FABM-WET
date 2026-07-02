"""Lake configuration - the single source of truth for lake parameters.

Users define their lake by filling a YAML file (see examples/lake_config_template.yaml)
and loading it via LakeConfig.from_yaml(). All preprocessor generators read from this
config, so there is one consistent place to describe a lake.

Field units are SI unless noted. All arrays use shape (ny, nx) = (lat, lon).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class RiverConfig:
    """One river (inflow or outflow) attached to a lake edge cell.

    For outflow, set flow_type='outflow'; discharge is computed from water balance
    so base_flow is ignored (sign convention: outflow discharge is negative).
    """
    name: str               # GETM river name, e.g. "INFL1", "OUTFL" (<=8 chars, uppercase)
    edge: str               # "north" | "south" | "west" | "east"
    flow_type: str          # "inflow" | "outflow"
    base_flow: float        # m3/s (mean discharge; ignored for outflow)
    temp: float = 15.0      # degC, river water temperature (annual mean)
    nh4: float = 0.2        # g/m3, ammonium concentration
    no3: float = 1.0        # g/m3, nitrate concentration
    po4: float = 0.05       # g/m3, phosphate concentration
    doc: float = 5.0        # g/m3, dissolved organic carbon
    poc: float = 2.0        # g/m3, particulate organic carbon
    seasonal_amp: float = 0.4   # fractional seasonal discharge variation (0=constant, 1=100%)
    wet_season_start: int = 120   # day-of-year when wet season begins (1-365)
    wet_season_end: int = 300     # day-of-year when wet season ends


@dataclass
class LakeConfig:
    """All parameters needed to generate standardized GETM-FABM-WET inputs.

    Load from YAML:  config = LakeConfig.from_yaml("my_lake.yaml")
    """

    # ---- Lake identification ----
    lake_name: str = "MyLake"           # human-readable name (used in titles)
    runid: str = "MYLAKE"               # GETM runid (uppercase, <=8 chars)

    # ---- Grid ----
    nx: int = 20                        # east-west cells
    ny: int = 6                         # north-south cells
    dx: float = 500.0                   # grid cell size in x (m)
    dy: float = 500.0                   # grid cell size in y (m)

    # ---- Geography ----
    lat0: float = 30.0                  # center latitude (degN)
    lon0: float = 120.0                 # center longitude (degE)
    x0_utm: float = 500000.0            # UTM origin x (m)
    y0_utm: float = 3300000.0           # UTM origin y (m)

    # ---- Bathymetry ----
    avg_depth: float = 3.5              # target average depth (m)
    max_depth: float = 7.0             # maximum depth (m)
    min_depth: float = 1.0              # minimum depth in water cells (m)
    shape: str = "oval"                 # "oval" | "rectangular" | "elliptical"
    shape_param: float = 0.45           # shape control (oval width variation, 0-1)

    # ---- Vertical grid ----
    n_sigma: int = 10                   # number of sigma layers
    maxdepth: float = 8.0              # GETM maxdepth (m), >= max_depth
    crit_depth: float = 0.3            # GETM critical depth (m)
    min_depth_getm: float = 0.1         # GETM min_depth (m)

    # ---- Simulation time ----
    start_date: str = "2020-01-01"      # YYYY-MM-DD
    end_date: str = "2020-12-31"        # YYYY-MM-DD
    timestep: float = 30.0             # seconds

    # ---- Climate ----
    avg_temp: float = 18.0              # annual mean air temperature (degC)
    temp_amplitude: float = 7.5         # seasonal temperature amplitude (degC)
    temp_peak_day: int = 170            # day-of-year of temperature peak (default ~Jun 19)
    annual_precip: float = 900.0        # mm/year total precipitation
    wet_season_start: int = 120          # day-of-year wet season starts (default ~Apr 30)
    wet_season_end: int = 300            # day-of-year wet season ends (default ~Oct 27)
    avg_wind_speed: float = 2.5          # m/s, mean wind speed at 10m
    wind_direction_variation: float = 1.0 # m/s, wind direction seasonal variation
    slp: float = 86000.0                 # Pa, sea level pressure (adjusted for elevation)
    avg_rh: float = 70.0                 # %, average relative humidity
    avg_tcc: float = 0.4                 # 0-1, average total cloud cover
    evap_avg: float = 3.0                # mm/day, average evaporation

    # ---- Rivers ----
    rivers: List[RiverConfig] = field(default_factory=list)

    # ---- Water quality (initial conditions) ----
    trophic_state: str = "eutrophic"   # "oligotrophic" | "mesotrophic" | "eutrophic"
    # Pelagic initial concentrations (uniform across lake unless fabm_init_file provided)
    nh4_init: float = 0.30              # g/m3, ammonium
    no3_init: float = 1.0               # g/m3, nitrate
    po4_init: float = 0.06              # g/m3, phosphate
    sio2_init: float = 3.5              # g/m3, silica
    o2_init: float = 10.0               # g/m3, dissolved oxygen
    dim_init: float = 10.0              # g/m3, inorganic matter
    # Phytoplankton initial (gDW/m3)
    diatoms_init: float = 0.30
    greens_init: float = 0.20
    cyanobacteria_init: float = 0.30
    # Zooplankton initial (gDW/m3)
    cladocerans_init: float = 0.30
    copepods_init: float = 0.30
    # Fish initial (gDW/m3)
    jufish_init: float = 0.15
    adfish_init: float = 0.40
    piscfish_init: float = 0.05
    # Macrophytes initial (gDW/m2)
    macrophyte_biomass: float = 30.0
    macrophyte_depth_range: tuple = (1.0, 2.5)  # depth range for macrophyte coverage (m)

    # ---- Output ----
    case_dir: str = "case/MyLake"       # relative to 3DWET/ root

    # ------------------------------------------------------------------
    # YAML loading
    # ------------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: str) -> "LakeConfig":
        """Load a LakeConfig from a YAML file.

        The YAML mirrors the dataclass fields. River entries go under a 'rivers:'
        list; each item must have at least 'name', 'edge', 'flow_type', 'base_flow'.
        """
        if yaml is None:
            raise ImportError("PyYAML is required: pip install pyyaml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        rivers_data = data.pop("rivers", [])
        rivers = [RiverConfig(**r) for r in rivers_data]
        # macrophyte_depth_range may come as a list from YAML
        if "macrophyte_depth_range" in data:
            data["macrophyte_depth_range"] = tuple(data["macrophyte_depth_range"])
        return cls(rivers=rivers, **data)

    # ------------------------------------------------------------------
    # Convenience derived properties
    # ------------------------------------------------------------------
    @property
    def n_days(self) -> int:
        """Number of days in the simulation (inclusive of both endpoints)."""
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        return (end - start).days + 1

    @property
    def lake_area_max(self) -> float:
        """Maximum possible lake area if all cells were water (m2)."""
        return self.nx * self.ny * self.dx * self.dy

    @property
    def inflow_rivers(self) -> List[RiverConfig]:
        return [r for r in self.rivers if r.flow_type == "inflow"]

    @property
    def outflow_rivers(self) -> List[RiverConfig]:
        return [r for r in self.rivers if r.flow_type == "outflow"]

    def __repr__(self) -> str:
        return (f"LakeConfig(name={self.lake_name!r}, runid={self.runid!r}, "
                f"grid={self.nx}x{self.ny}@{self.dx}m, "
                f"depth avg={self.avg_depth}m max={self.max_depth}m, "
                f"days={self.n_days}, rivers={len(self.rivers)})")
