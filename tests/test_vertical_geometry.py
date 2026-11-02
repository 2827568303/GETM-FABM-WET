"""Dynamic vertical positions must come from the selected native record."""
from pathlib import Path
import sys
import netCDF4 as nc
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'3DWET/app'))


@pytest.fixture
def column(tmp_path):
    path=tmp_path/'output.nc'
    with nc.Dataset(path,'w') as ds:
        for name,size in [('time',2),('sigma',2),('y',2),('x',3)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-.75,-.25]
        var=ds.createVariable('temp','f8',('time','sigma','y','x'));var[:]=20
        h=ds.createVariable('hn','f8',var.dimensions);h.units='m'
        h[0,0]=3;h[0,1]=9;h[1,0]=4;h[1,1]=10
        ds.createVariable('bathymetry','f8',('y','x'))[:]=[[10,10,-10],[10,10,10]]
    return path


def read(path,time=0,**kwargs):
    from vertical_geometry import read_vertical_geometry
    with nc.Dataset(path) as ds:
        return read_vertical_geometry(ds,ds['temp'],time,ds['bathymetry'][:],**kwargs)


def test_dynamic_layer_depths_and_elevations_are_not_static_sigma(column):
    first=read(column);last=read(column,1)
    np.testing.assert_allclose(first['center_depth'][:,0,0],[10.5,4.5])
    np.testing.assert_allclose(first['center_elevation'][:,0,0],[-8.5,-2.5])
    np.testing.assert_allclose(first['depth_edges'][:,0,0],[12,9,0])
    assert first['surface_elevation'][0,0]==2
    np.testing.assert_allclose(last['center_depth'][:,0,0],[12,5])
    assert last['surface_elevation'][0,0]==4
    assert first['source']=='hn' and first['position']=='center'
    assert not first['valid'][0,2]
    assert np.isnan(first['center_depth'][:,0,2]).all()


def test_actual_zc_has_precedence_over_assumed_midpoints(column):
    with nc.Dataset(column,'a') as ds:
        zc=ds.createVariable('zc','f8',ds['temp'].dimensions);zc.units='m'
        zc[:,0]=-8.4;zc[:,1]=-2.4
    result=read(column)
    np.testing.assert_allclose(result['center_elevation'][:,0,0],[-8.4,-2.4])
    np.testing.assert_allclose(result['center_depth'][:,0,0],[10.4,4.4])
    assert result['source']=='hn+zc'


def test_bad_thickness_or_zc_masks_column_without_sigma_substitution(column):
    with nc.Dataset(column,'a') as ds:
        ds['hn'][0,0,0,0]=0
        zc=ds.createVariable('zc','f8',ds['temp'].dimensions);zc.units='m'
        zc[:,0]=-8.5;zc[:,1]=-2.5;zc[0,1,1,0]=-30
    result=read(column)
    for j,i in [(0,0),(1,0)]:
        assert not result['valid'][j,i]
        assert np.isnan(result['center_depth'][:,j,i]).all()
    assert result['valid'][1,1]


def test_hyperslab_reads_only_selected_time_rows_and_columns(column):
    from vertical_geometry import read_vertical_geometry
    accesses=[]
    class Tracked:
        def __init__(self,v):self.v=v
        def __getattr__(self,key):return getattr(self.v,key)
        def __getitem__(self,key):accesses.append((self.v.name,key));return self.v[key]
    from types import SimpleNamespace
    with nc.Dataset(column) as ds:
        proxy=SimpleNamespace(variables={k:Tracked(v) for k,v in ds.variables.items()})
        result=read_vertical_geometry(proxy,proxy.variables['temp'],1,np.asarray(ds['bathymetry'][:]),
            ys=slice(1,2),xs=slice(None,None,2))
    assert result['center_depth'].shape==(2,1,2)
    for name,key in accesses:
        if name in ('hn','zc','z'):
            assert key[0]==1 and key[-2]==slice(1,2) and key[-1]==slice(None,None,2)


def test_explicit_sigma_fallback_uses_current_water_level_and_discloses_source(column):
    with nc.Dataset(column,'a') as ds:
        ds.renameVariable('hn','unused_hn')
        z=ds.createVariable('z','f8',('time','y','x'));z.units='m';z[0]=2;z[1]=4
    result=read(column)
    np.testing.assert_allclose(result['center_depth'][:,0,0],[9,3])
    np.testing.assert_allclose(result['center_elevation'][:,0,0],[-7,-1])
    assert result['source']=='sigma+z' and result['dynamic']


def test_missing_geometry_cannot_be_fabricated_from_layer_count(column):
    with nc.Dataset(column,'a') as ds:
        ds.renameVariable('hn','unused_hn');ds.renameVariable('sigma','unused_sigma')
    with pytest.raises(ValueError,match='hn.*sigma'):read(column)


def test_nonmetre_thickness_cannot_silently_be_used_as_metres(column):
    with nc.Dataset(column,'a') as ds:ds['hn'].units='centimeters'
    with pytest.raises(ValueError,match='hn.*单位'):read(column)


def test_native_padding_and_real_interfaces_remain_distinct(tmp_path):
    from vertical_geometry import read_vertical_geometry
    path=tmp_path/'native.nc'
    with nc.Dataset(path,'w') as ds:
        ds.model='GETM'
        for name,size in [('time',1),('sigma',3),('y',1),('x',1)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-1,-.5,0]
        v=ds.createVariable('temp','f8',('time','sigma','y','x'),fill_value=-9999)
        v[:]=1;v[:,0]=-9999
        hn=ds.createVariable('hn','f8',v.dimensions);hn.units='m';hn[:]=np.array([0,3,9]).reshape(1,3,1,1)
        w=ds.createVariable('w','f8',v.dimensions);w[:]=0
    with nc.Dataset(path) as ds:
        centers=read_vertical_geometry(ds,ds['temp'],0,np.array([[10.]]))
        faces=read_vertical_geometry(ds,ds['w'],0,np.array([[10.]]))
    np.testing.assert_allclose(centers['center_depth'][:,0,0],[10.5,4.5])
    np.testing.assert_allclose(faces['center_depth'][:,0,0],[12,9,0])
    assert centers['position']=='center' and faces['position']=='interface'


def test_valid_hn_layer_is_not_discarded_to_match_scalar_padding(tmp_path):
    from vertical_geometry import read_vertical_geometry
    path=tmp_path/'incompatible-native.nc'
    with nc.Dataset(path,'w') as ds:
        ds.model='GETM'
        for name,size in [('time',1),('sigma',3),('y',1),('x',1)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-1,-.5,0]
        var=ds.createVariable('temp','f8',('time','sigma','y','x'),fill_value=-9999);var[:]=1;var[:,0]=-9999
        hn=ds.createVariable('hn','f8',var.dimensions);hn.units='m';hn[:]=np.array([2,3,9]).reshape(1,3,1,1)
    with nc.Dataset(path) as ds:
        with pytest.raises(ValueError,match='层数'):
            read_vertical_geometry(ds,ds['temp'],0,np.array([[10.]]))


def test_positive_sigma_interfaces_match_actual_layer_thickness(tmp_path):
    from vertical_geometry import read_vertical_geometry
    path=tmp_path/'interfaces.nc'
    with nc.Dataset(path,'w') as ds:
        for name,size in [('time',1),('sigma',3),('layer',2),('y',1),('x',1)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[0,.5,1]
        ds.createVariable('w','f8',('time','sigma','y','x'))[:]=0
        hn=ds.createVariable('hn','f8',('time','layer','y','x'));hn.units='m';hn[:]=np.array([3,9]).reshape(1,2,1,1)
    with nc.Dataset(path) as ds:result=read_vertical_geometry(ds,ds['w'],0,np.array([[10.]]))
    np.testing.assert_allclose(result['center_depth'][:,0,0],[12,9,0])
    assert result['position']=='interface'


@pytest.mark.parametrize('name',['hn','zc','z','D'])
def test_equal_shape_does_not_establish_grid_identity(column,name):
    with nc.Dataset(column,'a') as ds:
        ds.createDimension('yu',2);ds.createDimension('xu',3)
        if name in ('hn','D'):ds.renameVariable('hn','unused_hn')
        dims=('time','sigma','yu','xu') if name in ('hn','zc') else ('time','yu','xu')
        value=ds.createVariable(name,'f8',dims);value.units='m';value[:]=3
    with pytest.raises(ValueError,match='网格|维度'):read(column)


def test_explicit_bathymetry_units_cannot_be_assumed_metres(column):
    with nc.Dataset(column,'a') as ds:ds['bathymetry'].units='cm';ds['bathymetry'][:]=1000
    with pytest.raises(ValueError,match='bathymetry.*单位'):read(column)


def test_native_hn_padding_identity_cannot_change_with_selected_row(tmp_path):
    from vertical_geometry import read_vertical_geometry
    path=tmp_path/'mixed-native.nc'
    with nc.Dataset(path,'w') as ds:
        ds.model='GETM'
        for name,size in [('time',1),('sigma',3),('y',2),('x',1)]:ds.createDimension(name,size)
        ds.createVariable('sigma','f8',('sigma',))[:]=[-1,-.5,0]
        var=ds.createVariable('temp','f8',('time','sigma','y','x'),fill_value=-9999);var[:]=1;var[:,0]=-9999
        hn=ds.createVariable('hn','f8',var.dimensions);hn.units='m';hn[:,0]=0;hn[:,1]=3;hn[:,2]=9
        hn[0,0,1,0]=2
    with nc.Dataset(path) as ds:
        with pytest.raises(ValueError,match='层数'):
            read_vertical_geometry(ds,ds['temp'],0,np.full((2,1),10.),ys=0)


def test_split_timestep_surface_difference_does_not_invalidate_native_3d(column):
    with nc.Dataset(column,'a') as ds:
        z=ds.createVariable('z','f8',('time','y','x'));z.units='m';z[:]=2.3
    result=read(column)
    assert result['valid'][0,0]
    assert result['surface_elevation'][0,0]==2
    assert result['barotropic_surface_elevation'][0,0]==2.3
    assert result['surface_difference'][0,0]==pytest.approx(.3)
    assert not result['surface_synchronized'][0,0]
    np.testing.assert_allclose(result['center_depth'][:,0,0],[10.5,4.5])
    assert result['depth_reference']=='below native 3D geometry surface'
