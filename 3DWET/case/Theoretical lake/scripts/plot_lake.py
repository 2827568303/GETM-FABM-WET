"""Plot the Theoretical Lake: horizontal (plan), vertical (cross-section),
and 3-D multi-angle views.

Reads  ../case/bathymetry.nc  and  ../case/riverinfo.dat  and writes PNG
images into  ../plots/ :

  plot_01_horizontal_plan.png      - top-down bathymetry + rivers + contours
  plot_02_vertical_crosssections.png - N-S and E-W depth cross-sections
  plot_03_3d_multiview.png         - 2x2 panel, 3-D surface from 4 angles
  plot_04_overview.png             - single composite of all three views
"""
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)
import os

CASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
PLOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

DX = DY = 500.0

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
ds = nc.Dataset(os.path.join(CASE_DIR, "bathymetry.nc"))
bathy = ds.variables["bathymetry"][:].astype(float)    # (NY, NX),  j=0 north
NX, NY = bathy.shape[1], bathy.shape[0]
ds.close()

mask = bathy > 0.0
depth = np.where(mask, bathy, np.nan)

# river positions (1-indexed in file -> 0-indexed here)
river_cells = {}      # name -> [(i, j), ...]
with open(os.path.join(CASE_DIR, "riverinfo.dat")) as f:
    n = int(f.readline())
    for _ in range(n):
        parts = f.readline().split()
        i, j, name = int(parts[0]) - 1, int(parts[1]) - 1, parts[2]
        river_cells.setdefault(name, []).append((i, j))

INFLOWS = [n for n in river_cells if n.startswith("INFL")]
OUTFLOWS = [n for n in river_cells if n.startswith("OUTFL")]

# deepest point
dj_deep, di_deep = np.unravel_index(np.nanargmax(depth), depth.shape)
deep_val = float(depth[dj_deep, di_deep])
print(f"Grid {NX}x{NY}  wet={mask.sum()}  deepest=({di_deep+1},{dj_deep+1})={deep_val:.2f}m")

# coordinate axes in metres (cell-centre distances from SW corner of grid)
# j=0 is north, so for plotting "north up" we keep j increasing downward.
x_km = (np.arange(NX) + 0.5) * DX / 1000.0
y_km = (np.arange(NY) + 0.5) * DY / 1000.0

# custom bathymetry colormap: shallow -> deep (light blue -> navy)
cmap_depth = LinearSegmentedColormap.from_list(
    "lake", ["#a8d8f0", "#5fb3e0", "#2d8fd1", "#1565a8", "#0a3d6b", "#04203f"], N=256)
cmap_depth.set_bad("#d9cdb8")   # land = tan


# ==================================================================
# 1.  Horizontal (plan) view
# ==================================================================
print("Plotting horizontal plan view ...")
fig, ax = plt.subplots(figsize=(11, 9))

# bathymetry
Xc, Yc = np.meshgrid(x_km, y_km)
pcm = ax.pcolormesh(Xc, Yc, depth, cmap=cmap_depth, shading="auto",
                    vmin=0, vmax=deep_val)

# depth contours
levels = np.arange(1, int(deep_val) + 1, 1)
cs = ax.contour(Xc, Yc, depth, levels=levels, colors="white",
                linewidths=0.6, alpha=0.6)
ax.clabel(cs, inline=True, fontsize=6, fmt="%.0fm")

# shoreline outline
from matplotlib.patches import PathPatch
from matplotlib.path import Path
# build shoreline polygon from mask boundary
shore_i, shore_j = [], []
for j in range(NY):
    for i in range(NX):
        if mask[j, i]:
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                jj, ii = j + dj, i + di
                if not (0 <= jj < NY and 0 <= ii < NX) or not mask[jj, ii]:
                    shore_i.append(x_km[i])
                    shore_j.append(y_km[j])
                    break
ax.scatter(shore_i, shore_j, s=4, c="#333333", zorder=3, alpha=0.4)

# rivers
river_colors = {"INFL_NW": "#1b9e3a", "INFL_NE": "#2ecc40", "INFL_W": "#7fdb2a"}
out_colors = {"OUTFL_S": "#e63946", "OUTFL_E": "#ff6b35"}
markers = {"inflow": ("o", "#1b9e3a"), "outflow": ("s", "#e63946")}

for name, cells in river_cells.items():
    is_in = name.startswith("INFL")
    color = "#1b9e3a" if is_in else "#e63946"
    for (i, j) in cells:
        cx, cy = x_km[i], y_km[j]
        ax.scatter(cx, cy, s=180, c=color, edgecolors="white",
                   linewidths=1.5, zorder=5, marker="o" if is_in else "s")
        # direction arrow (inflow points inward, outflow outward)
        # find the dry neighbour to point the arrow away from
        dry_dir = None
        for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            jj, ii = j + dj, i + di
            if not (0 <= jj < NY and 0 <= ii < NX) or not mask[jj, ii]:
                dry_dir = (di, dj)
                break
        if dry_dir:
            dx_a, dy_a = dry_dir
            if is_in:
                dx_a, dy_a = -dx_a, -dy_a     # inflow: arrow into the lake
            ax.annotate(name, xy=(cx, cy), xytext=(cx + dx_a * 1.2, cy + dy_a * 1.2),
                        fontsize=7, fontweight="bold", color=color,
                        ha="center", va="center",
                        arrowprops=dict(arrowstyle="->", color=color, lw=1.8))

# deepest point marker
ax.scatter(x_km[di_deep], y_km[dj_deep], marker="*", s=350, c="gold",
           edgecolors="black", linewidths=1.2, zorder=6)
ax.annotate(f"Max depth\n{deep_val:.1f} m",
            xy=(x_km[di_deep], y_km[dj_deep]),
            xytext=(x_km[di_deep] + 2.0, y_km[dj_deep] - 1.5),
            fontsize=8, color="black", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="black", alpha=0.85))

# north arrow
ax.annotate("", xy=(0.96, 0.96), xytext=(0.96, 0.88),
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color="black", lw=2.5))
ax.text(0.96, 0.975, "N", transform=ax.transAxes, fontsize=14,
        fontweight="bold", ha="center", va="bottom")

cbar = fig.colorbar(pcm, ax=ax, shrink=0.75, pad=0.02)
cbar.set_label("Water depth (m)", fontsize=11)

avg_d = float(np.nanmean(depth))
ax.set_title(f"Theoretical Lake - Plan View (Horizontal)\n"
             f"Heart shape, 70.0 km², avg {avg_d:.1f} m, max {deep_val:.1f} m",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Easting (km)", fontsize=11)
ax.set_ylabel("Northing (km)", fontsize=11)
ax.set_aspect("equal")
ax.set_xlim(x_km.min() - 0.5, x_km.max() + 0.5)
ax.set_ylim(y_km.min() - 0.5, y_km.max() + 0.5)
# legend
from matplotlib.lines import Line2D
legend_items = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#1b9e3a", markersize=10, label="Inflow river"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#e63946", markersize=10, label="Outflow river"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="gold", markersize=14, label="Deepest point"),
]
ax.legend(handles=legend_items, loc="lower left", fontsize=9, framealpha=0.9)

fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "plot_01_horizontal_plan.png"), dpi=150)
plt.close(fig)
print("  -> plot_01_horizontal_plan.png")


# ==================================================================
# 2.  Vertical cross-sections (through the deepest point)
# ==================================================================
print("Plotting vertical cross-sections ...")
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# --- N-S cross-section (along j, at i = di_deep) ---
ax1 = axes[0]
i_cut = di_deep
profile_ns = depth[:, i_cut]            # j=0 (north) ... j=NY-1 (south)
valid_ns = ~np.isnan(profile_ns)
dist_ns = y_km.copy()                    # distance from north (km)

ax1.fill_between(dist_ns, -profile_ns, 0, where=valid_ns,
                 color="#2d8fd1", alpha=0.75, label="Water column")
ax1.fill_between(dist_ns, -profile_ns, -deep_val - 2, where=valid_ns,
                 color="#8b7355", alpha=0.6, label="Lake bed")
ax1.plot(dist_ns, -profile_ns, color="#04203f", lw=2)
ax1.axhline(0, color="#1565a8", lw=1.2, ls="-", alpha=0.7)   # water surface

# mark deepest point
ax1.scatter(y_km[dj_deep], -deep_val, s=120, c="gold", edgecolors="black", zorder=5,
            marker="*", label=f"Deepest point ({deep_val:.1f} m)")

# mark rivers on this column
for name, cells in river_cells.items():
    for (i, j) in cells:
        if i == i_cut and valid_ns[j]:
            is_in = name.startswith("INFL")
            ax1.scatter(y_km[j], 0, s=100, c="#1b9e3a" if is_in else "#e63946",
                        edgecolors="white", zorder=5, marker="o" if is_in else "s")
            ax1.annotate(name, (y_km[j], 0), textcoords="offset points",
                         xytext=(8, 10), fontsize=7, fontweight="bold",
                         color="#1b9e3a" if is_in else "#e63946")

ax1.set_title(f"North-South cross-section  (at column i={i_cut+1}, through deepest point)",
              fontsize=12, fontweight="bold")
ax1.set_xlabel("Distance from north (km)", fontsize=10)
ax1.set_ylabel("Elevation (m)", fontsize=10)
ax1.set_ylim(-deep_val - 2, 1.5)
ax1.legend(loc="lower right", fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.text(0.01, 0.95, "N", transform=ax1.transAxes, fontsize=14, fontweight="bold", va="top")
ax1.text(0.98, 0.95, "S", transform=ax1.transAxes, fontsize=14, fontweight="bold", va="top", ha="right")

# --- E-W cross-section (along i, at j = dj_deep) ---
ax2 = axes[1]
j_cut = dj_deep
profile_ew = depth[j_cut, :]            # i=0 (west) ... i=NX-1 (east)
valid_ew = ~np.isnan(profile_ew)
dist_ew = x_km.copy()

ax2.fill_between(dist_ew, -profile_ew, 0, where=valid_ew,
                 color="#2d8fd1", alpha=0.75, label="Water column")
ax2.fill_between(dist_ew, -profile_ew, -deep_val - 2, where=valid_ew,
                 color="#8b7355", alpha=0.6, label="Lake bed")
ax2.plot(dist_ew, -profile_ew, color="#04203f", lw=2)
ax2.axhline(0, color="#1565a8", lw=1.2, ls="-", alpha=0.7)

ax2.scatter(x_km[di_deep], -deep_val, s=120, c="gold", edgecolors="black", zorder=5,
            marker="*", label=f"Deepest point ({deep_val:.1f} m)")

for name, cells in river_cells.items():
    for (i, j) in cells:
        if j == j_cut and valid_ew[i]:
            is_in = name.startswith("INFL")
            ax2.scatter(x_km[i], 0, s=100, c="#1b9e3a" if is_in else "#e63946",
                        edgecolors="white", zorder=5, marker="o" if is_in else "s")
            ax2.annotate(name, (x_km[i], 0), textcoords="offset points",
                         xytext=(8, 10), fontsize=7, fontweight="bold",
                         color="#1b9e3a" if is_in else "#e63946")

ax2.set_title(f"East-West cross-section  (at row j={j_cut+1}, through deepest point)",
              fontsize=12, fontweight="bold")
ax2.set_xlabel("Distance from west (km)", fontsize=10)
ax2.set_ylabel("Elevation (m)", fontsize=10)
ax2.set_ylim(-deep_val - 2, 1.5)
ax2.legend(loc="lower right", fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.text(0.01, 0.95, "W", transform=ax2.transAxes, fontsize=14, fontweight="bold", va="top")
ax2.text(0.98, 0.95, "E", transform=ax2.transAxes, fontsize=14, fontweight="bold", va="top", ha="right")

fig.suptitle("Theoretical Lake - Vertical Cross-Sections", fontsize=14, fontweight="bold", y=1.0)
fig.tight_layout()
fig.savefig(os.path.join(PLOT_DIR, "plot_02_vertical_crosssections.png"), dpi=150,
            bbox_inches="tight")
plt.close(fig)
print("  -> plot_02_vertical_crosssections.png")


# ==================================================================
# 3.  3-D multi-angle views (2x2 panel)
# ==================================================================
print("Plotting 3-D multi-angle views ...")

# Prepare grid for 3-D: flip j so north is +Y (away from viewer at bottom)
X3, Y3 = np.meshgrid(x_km, y_km)
Z3 = -np.where(mask, bathy, np.nan)     # negative = below surface

# also a "water surface" plane at z=0 for context
views = [
    (35,  45,  "SE perspective"),
    (35, 225,  "NW perspective"),
    (90,   0,  "Top-down"),
    (20, 135,  "SW low-angle"),
]

fig = plt.figure(figsize=(16, 14))
for idx, (elev, azim, title) in enumerate(views):
    ax = fig.add_subplot(2, 2, idx + 1, projection="3d")
    # lake bed surface
    surf = ax.plot_surface(X3, Y3, Z3, cmap=cmap_depth, linewidth=0,
                           antialiased=True, rstride=1, cstride=1,
                           vmin=-deep_val, vmax=0, alpha=0.95)
    # water-surface outline (polygon at z=0 of the shoreline)
    # simple: scatter the wet cells at z=0
    wet_x = X3[mask]
    wet_y = Y3[mask]
    ax.scatter(wet_x, wet_y, np.zeros_like(wet_x), s=1, c="#a8d8f0", alpha=0.25)

    # deepest point
    ax.scatter([x_km[di_deep]], [y_km[dj_deep]], [-deep_val],
               s=120, c="gold", edgecolors="black", marker="*", zorder=10)

    # rivers
    for name, cells in river_cells.items():
        is_in = name.startswith("INFL")
        c = "#1b9e3a" if is_in else "#e63946"
        xs = [x_km[i] for (i, j) in cells]
        ys = [y_km[j] for (i, j) in cells]
        zs = [0.0 for _ in cells]
        ax.scatter(xs, ys, zs, s=60, c=c, edgecolors="white", linewidths=1.0,
                   marker="o" if is_in else "s", zorder=10)

    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("East (km)", fontsize=9, labelpad=6)
    ax.set_ylabel("North (km)", fontsize=9, labelpad=6)
    ax.set_zlabel("Depth (m)", fontsize=9, labelpad=6)
    ax.set_zlim(-deep_val - 1, 1)
    # invert Z so deeper = downward is already negative; keep as is
    try:
        ax.set_box_aspect((1, NY / NX, 0.55))
    except Exception:
        pass

fig.suptitle("Theoretical Lake - 3-D Bathymetry (Multi-Angle)",
             fontsize=15, fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(os.path.join(PLOT_DIR, "plot_03_3d_multiview.png"), dpi=140,
            bbox_inches="tight")
plt.close(fig)
print("  -> plot_03_3d_multiview.png")


# ==================================================================
# 4.  Overview composite (plan + cross-sections + 3D)
# ==================================================================
print("Plotting overview composite ...")
fig = plt.figure(figsize=(18, 14))

# (a) plan view - top left
ax_a = fig.add_subplot(2, 2, 1)
pcm = ax_a.pcolormesh(Xc, Yc, depth, cmap=cmap_depth, shading="auto", vmin=0, vmax=deep_val)
cs = ax_a.contour(Xc, Yc, depth, levels=levels, colors="white", linewidths=0.5, alpha=0.6)
ax_a.clabel(cs, inline=True, fontsize=6, fmt="%.0f")
for name, cells in river_cells.items():
    is_in = name.startswith("INFL")
    c = "#1b9e3a" if is_in else "#e63946"
    for (i, j) in cells:
        ax_a.scatter(x_km[i], y_km[j], s=130, c=c, edgecolors="white", linewidths=1.2,
                     marker="o" if is_in else "s", zorder=5)
ax_a.scatter(x_km[di_deep], y_km[dj_deep], marker="*", s=280, c="gold",
             edgecolors="black", linewidths=1.0, zorder=6)
ax_a.set_title("(a) Horizontal plan view", fontsize=12, fontweight="bold")
ax_a.set_xlabel("Easting (km)")
ax_a.set_ylabel("Northing (km)")
ax_a.set_aspect("equal")
fig.colorbar(pcm, ax=ax_a, shrink=0.7, label="Depth (m)")

# (b) N-S cross-section - top right
ax_b = fig.add_subplot(2, 2, 2)
ax_b.fill_between(dist_ns, -profile_ns, 0, where=valid_ns, color="#2d8fd1", alpha=0.75)
ax_b.fill_between(dist_ns, -profile_ns, -deep_val - 2, where=valid_ns, color="#8b7355", alpha=0.6)
ax_b.plot(dist_ns, -profile_ns, color="#04203f", lw=2)
ax_b.axhline(0, color="#1565a8", lw=1.2, alpha=0.7)
ax_b.scatter(y_km[dj_deep], -deep_val, s=100, c="gold", edgecolors="black", marker="*")
ax_b.set_title(f"(b) N-S cross-section (i={i_cut+1})", fontsize=12, fontweight="bold")
ax_b.set_xlabel("Distance from north (km)")
ax_b.set_ylabel("Elevation (m)")
ax_b.set_ylim(-deep_val - 2, 1.5)
ax_b.grid(True, alpha=0.3)

# (c) E-W cross-section - bottom left
ax_c = fig.add_subplot(2, 2, 3)
ax_c.fill_between(dist_ew, -profile_ew, 0, where=valid_ew, color="#2d8fd1", alpha=0.75)
ax_c.fill_between(dist_ew, -profile_ew, -deep_val - 2, where=valid_ew, color="#8b7355", alpha=0.6)
ax_c.plot(dist_ew, -profile_ew, color="#04203f", lw=2)
ax_c.axhline(0, color="#1565a8", lw=1.2, alpha=0.7)
ax_c.scatter(x_km[di_deep], -deep_val, s=100, c="gold", edgecolors="black", marker="*")
ax_c.set_title(f"(c) E-W cross-section (j={j_cut+1})", fontsize=12, fontweight="bold")
ax_c.set_xlabel("Distance from west (km)")
ax_c.set_ylabel("Elevation (m)")
ax_c.set_ylim(-deep_val - 2, 1.5)
ax_c.grid(True, alpha=0.3)

# (d) 3D perspective - bottom right
ax_d = fig.add_subplot(2, 2, 4, projection="3d")
ax_d.plot_surface(X3, Y3, Z3, cmap=cmap_depth, linewidth=0, antialiased=True,
                  rstride=1, cstride=1, vmin=-deep_val, vmax=0, alpha=0.95)
ax_d.scatter([x_km[di_deep]], [y_km[dj_deep]], [-deep_val],
             s=100, c="gold", edgecolors="black", marker="*")
for name, cells in river_cells.items():
    is_in = name.startswith("INFL")
    c = "#1b9e3a" if is_in else "#e63946"
    xs = [x_km[i] for (i, j) in cells]
    ys = [y_km[j] for (i, j) in cells]
    ax_d.scatter(xs, ys, [0]*len(xs), s=50, c=c, edgecolors="white",
                 marker="o" if is_in else "s")
ax_d.view_init(elev=30, azim=55)
ax_d.set_title("(d) 3-D perspective", fontsize=12, fontweight="bold")
ax_d.set_xlabel("E (km)")
ax_d.set_ylabel("N (km)")
ax_d.set_zlabel("Depth (m)")
ax_d.set_zlim(-deep_val - 1, 1)
try:
    ax_d.set_box_aspect((1, NY / NX, 0.55))
except Exception:
    pass

fig.suptitle("Theoretical Lake - Model Overview  "
             f"(70.0 km², avg {avg_d:.1f} m, max {deep_val:.1f} m, 5 rivers)",
             fontsize=15, fontweight="bold", y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig(os.path.join(PLOT_DIR, "plot_04_overview.png"), dpi=140, bbox_inches="tight")
plt.close(fig)
print("  -> plot_04_overview.png")

print("\nAll plots generated in", PLOT_DIR)
for f in sorted(os.listdir(PLOT_DIR)):
    print(f"  {f}  ({os.path.getsize(os.path.join(PLOT_DIR, f))//1024} KB)")
