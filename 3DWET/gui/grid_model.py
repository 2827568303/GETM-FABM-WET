"""
3DWET Grid Editor - Data Model
Handles bathymetry.nc and riverinfo.dat I/O, with undo/redo support.
"""
import numpy as np
import netCDF4 as nc
from pathlib import Path
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


LAND_VALUE = -10.0  # GETM convention: negative = land


@dataclass
class River:
    """A river entry in riverinfo.dat. Multi-cell rivers share the same name."""
    i: int  # 1-based x index (column)
    j: int  # 1-based y index (row)
    name: str
    flag1: int = -1
    flag2: int = -1


@dataclass
class GridModel:
    """Holds all grid data and provides editing operations."""
    filepath: Optional[Path] = None
    nx: int = 0  # number of x cells (columns)
    ny: int = 0  # number of y cells (rows)
    bathymetry: np.ndarray = field(default_factory=lambda: np.array([]))  # shape (ny, nx)
    x_coords: np.ndarray = field(default_factory=lambda: np.array([]))  # shape (nx,)
    y_coords: np.ndarray = field(default_factory=lambda: np.array([]))  # shape (ny,)
    lonc: np.ndarray = field(default_factory=lambda: np.array([]))  # shape (ny, nx)
    latc: np.ndarray = field(default_factory=lambda: np.array([]))  # shape (ny, nx)
    cell_dx: float = 500.0
    cell_dy: float = 500.0
    rivers: List[River] = field(default_factory=list)
    river_filepath: Optional[Path] = None
    modified: bool = False

    # Undo/redo
    _undo_stack: List[dict] = field(default_factory=list)
    _redo_stack: List[dict] = field(default_factory=list)
    _max_undo: int = 50

    # ── Loading ──────────────────────────────────────────────────────────

    def load_bathymetry(self, filepath: str):
        """Load bathymetry from a GETM NetCDF file."""
        self.filepath = Path(filepath)
        with nc.Dataset(str(filepath), 'r') as f:
            self.x_coords = f.variables['x'][:].astype(np.float64)
            self.y_coords = f.variables['y'][:].astype(np.float64)
            self.bathymetry = f.variables['bathymetry'][:].astype(np.float64).filled(LAND_VALUE)
            if 'lonc' in f.variables:
                self.lonc = f.variables['lonc'][:].astype(np.float64)
            if 'latc' in f.variables:
                self.latc = f.variables['latc'][:].astype(np.float64)

        self.ny, self.nx = self.bathymetry.shape
        if len(self.x_coords) > 1:
            self.cell_dx = float(self.x_coords[1] - self.x_coords[0])
        if len(self.y_coords) > 1:
            self.cell_dy = float(self.y_coords[1] - self.y_coords[0])

        self._undo_stack.clear()
        self._redo_stack.clear()
        self.modified = False

    def load_rivers(self, filepath: str):
        """Load riverinfo.dat."""
        self.river_filepath = Path(filepath)
        self.rivers = []
        with open(filepath, 'r') as f:
            lines = f.readlines()
        if not lines:
            return
        count = int(lines[0].strip())
        for line in lines[1:count + 1]:
            parts = line.split()
            if len(parts) >= 3:
                i, j = int(parts[0]), int(parts[1])
                name = parts[2]
                f1 = int(parts[3]) if len(parts) > 3 else -1
                f2 = int(parts[4]) if len(parts) > 4 else -1
                self.rivers.append(River(i=i, j=j, name=name, flag1=f1, flag2=f2))

    # ── Saving ───────────────────────────────────────────────────────────

    def save_bathymetry(self, filepath: Optional[str] = None):
        """Save bathymetry to NetCDF. Overwrites original if no path given."""
        if filepath is None:
            if self.filepath is None:
                raise ValueError("No filepath specified")
            filepath = str(self.filepath)

        # Read original to preserve all variables/attributes
        with nc.Dataset(filepath, 'r+') as f:
            f.variables['bathymetry'][:] = self.bathymetry
        self.modified = False
        self.filepath = Path(filepath)

    def save_rivers(self, filepath: Optional[str] = None):
        """Save riverinfo.dat."""
        if filepath is None:
            if self.river_filepath is None:
                raise ValueError("No river filepath specified")
            filepath = str(self.river_filepath)
        with open(filepath, 'w') as f:
            f.write(f"{len(self.rivers)}\n")
            for r in self.rivers:
                f.write(f"{r.i} {r.j} {r.name} {r.flag1} {r.flag2}\n")
        self.river_filepath = Path(filepath)

    # ── Queries ──────────────────────────────────────────────────────────

    def is_water(self, i: int, j: int) -> bool:
        """Check if cell (i, j) 0-based is water."""
        if 0 <= i < self.nx and 0 <= j < self.ny:
            return self.bathymetry[j, i] > 0
        return False

    def get_depth(self, i: int, j: int) -> float:
        """Get depth at cell (i, j) 0-based. Returns 0 for land."""
        if 0 <= i < self.nx and 0 <= j < self.ny:
            v = float(self.bathymetry[j, i])
            return v if v > 0 else 0.0
        return 0.0

    def water_mask(self) -> np.ndarray:
        """Return boolean array of water cells."""
        return self.bathymetry > 0

    def water_count(self) -> int:
        return int((self.bathymetry > 0).sum())

    def depth_range(self) -> Tuple[float, float]:
        """Return (min, max) depth among water cells."""
        water = self.bathymetry[self.bathymetry > 0]
        if len(water) == 0:
            return (0.0, 0.0)
        return (float(water.min()), float(water.max()))

    def get_river_groups(self) -> dict:
        """Group rivers by name, returning {name: [(i,j), ...]} with 0-based indices."""
        groups = {}
        for r in self.rivers:
            if r.name not in groups:
                groups[r.name] = []
            groups[r.name].append((r.i - 1, r.j - 1))
        return groups

    # ── Editing ──────────────────────────────────────────────────────────

    def _push_undo(self):
        """Save current state for undo."""
        state = {
            'bathymetry': self.bathymetry.copy(),
            'rivers': deepcopy(self.rivers),
        }
        self._undo_stack.append(state)
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        current = {
            'bathymetry': self.bathymetry.copy(),
            'rivers': deepcopy(self.rivers),
        }
        self._redo_stack.append(current)
        state = self._undo_stack.pop()
        self.bathymetry = state['bathymetry']
        self.rivers = state['rivers']
        self.modified = True
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        current = {
            'bathymetry': self.bathymetry.copy(),
            'rivers': deepcopy(self.rivers),
        }
        self._undo_stack.append(current)
        state = self._redo_stack.pop()
        self.bathymetry = state['bathymetry']
        self.rivers = state['rivers']
        self.modified = True
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def set_depth(self, i: int, j: int, depth: float, record_undo: bool = True):
        """Set depth at cell (i, j) 0-based. depth <= 0 sets land."""
        if not (0 <= i < self.nx and 0 <= j < self.ny):
            return
        if record_undo:
            self._push_undo()
        self.bathymetry[j, i] = depth if depth > 0 else LAND_VALUE
        self.modified = True

    def toggle_land(self, i: int, j: int, record_undo: bool = True):
        """Toggle cell between land and water (default depth = mean)."""
        if not (0 <= i < self.nx and 0 <= j < self.ny):
            return
        if record_undo:
            self._push_undo()
        if self.bathymetry[j, i] > 0:
            self.bathymetry[j, i] = LAND_VALUE
        else:
            water = self.bathymetry[self.bathymetry > 0]
            default_depth = float(water.mean()) if len(water) > 0 else 3.0
            self.bathymetry[j, i] = default_depth
        self.modified = True

    def paint_region(self, cells: List[Tuple[int, int]], depth: float, record_undo: bool = True):
        """Paint a list of (i, j) 0-based cells with depth."""
        if not cells:
            return
        if record_undo:
            self._push_undo()
        for i, j in cells:
            if 0 <= i < self.nx and 0 <= j < self.ny:
                self.bathymetry[j, i] = depth if depth > 0 else LAND_VALUE
        self.modified = True

    def smooth_cell(self, i: int, j: int, record_undo: bool = True):
        """Replace cell depth with average of water-cell neighbors (3x3)."""
        if not (0 <= i < self.nx and 0 <= j < self.ny):
            return
        if self.bathymetry[j, i] <= 0:
            return  # don't smooth land
        neighbors = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < self.nx and 0 <= nj < self.ny:
                    v = self.bathymetry[nj, ni]
                    if v > 0:
                        neighbors.append(v)
        if neighbors:
            if record_undo:
                self._push_undo()
            self.bathymetry[j, i] = float(np.mean(neighbors))
            self.modified = True

    def smooth_region(self, cells: List[Tuple[int, int]], record_undo: bool = True):
        """Smooth a region of cells."""
        if not cells:
            return
        if record_undo:
            self._push_undo()
        # Compute new values from original bathymetry
        original = self.bathymetry.copy()
        for i, j in cells:
            if not (0 <= i < self.nx and 0 <= j < self.ny):
                continue
            if original[j, i] <= 0:
                continue
            neighbors = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.nx and 0 <= nj < self.ny:
                        v = original[nj, ni]
                        if v > 0:
                            neighbors.append(v)
            if neighbors:
                self.bathymetry[j, i] = float(np.mean(neighbors))
        self.modified = True

    def add_river(self, i: int, j: int, name: str, record_undo: bool = True):
        """Add a river at 0-based (i, j)."""
        if record_undo:
            self._push_undo()
        self.rivers.append(River(i=i + 1, j=j + 1, name=name))
        self.modified = True

    def remove_river(self, index: int, record_undo: bool = True):
        """Remove river by index."""
        if 0 <= index < len(self.rivers):
            if record_undo:
                self._push_undo()
            self.rivers.pop(index)
            self.modified = True

    def remove_rivers_at(self, i: int, j: int, record_undo: bool = True):
        """Remove all rivers at 0-based (i, j)."""
        to_remove = [idx for idx, r in enumerate(self.rivers) if r.i - 1 == i and r.j - 1 == j]
        if to_remove:
            if record_undo:
                self._push_undo()
            for idx in reversed(to_remove):
                self.rivers.pop(idx)
            self.modified = True
