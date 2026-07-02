#include <stdio.h>
#include <netcdf.h>
int main() {
    int ncid, varid, err;
    int nx, ny, nt;
    int dimid;
    static float data[44*54*31];
    err = nc_open("test_nc3.nc", NC_NOWRITE, &ncid);
    printf("nc_open: %d\n", err);
    err = nc_inq_dimid(ncid, "lon", &dimid);
    err = nc_inq_dimlen(ncid, dimid, &nx);
    err = nc_inq_dimid(ncid, "lat", &dimid);
    err = nc_inq_dimlen(ncid, dimid, &ny);
    err = nc_inq_dimid(ncid, "time", &dimid);
    err = nc_inq_dimlen(ncid, dimid, &nt);
    printf("dims: lon=%d lat=%d time=%d\n", nx, ny, nt);
    err = nc_inq_varid(ncid, "u10", &varid);
    printf("nc_inq_varid: %d\n", err);
    size_t start[3] = {0, 0, 0};
    size_t count[3] = {nx, ny, 1};
    err = nc_get_vara(ncid, varid, start, count, data);
    printf("nc_get_vara (2D slice): %d\n", err);
    err = nc_get_var(ncid, varid, data);
    printf("nc_get_var (entire): %d\n", err);
    nc_close(ncid);
    return 0;
}
