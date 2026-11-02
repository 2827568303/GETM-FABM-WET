"""Read one result record's vertical geometry without loading its history."""
import numpy as np
from result_layers import physical_vertical_grid

_METRES={'m','meter','meters','metre','metres'}


def _array(value):
    return np.asarray(np.ma.filled(np.ma.asarray(value,dtype=float),np.nan),dtype=float)


def require_metres(name,units):
    units=str(units).strip().lower()
    if units and units not in _METRES:
        raise ValueError(f'{name} 单位必须为米，当前为 {units}')


def _metres(var):
    # Legacy GETM hn/zc names have SI definitions. An explicit incompatible
    # unit is never silently treated as metres.
    require_metres(var.name,getattr(var,'units',''))


def read_vertical_geometry(ds,var,time,bottom,ys=slice(None),xs=slice(None),bottom_units=None):
    """Return native positions, positive-down depths and validity per column.

    bottom may be the full bathymetry or an already selected spatial section.
    hn is accumulated before any vertical sampling; invalid columns stay absent.
    Sigma fallback requires an explicit coordinate and discloses static geometry.
    """
    if var.ndim!=4 or not 0<=time<var.shape[0]:
        raise ValueError('垂向几何需要有效的四维结果时刻')
    start,coords=physical_vertical_grid(ds,var)
    count=var.shape[1]-start
    if bottom_units is None:
        bottom_units=getattr(ds.variables.get('bathymetry'),'units','')
    require_metres('bathymetry',bottom_units)
    depth=_array(bottom)
    if depth.shape==var.shape[2:]:depth=depth[ys,xs]
    wet=np.isfinite(depth)&(depth>0)
    mask=ds.variables.get('mask')
    if mask is not None and mask.shape==var.shape[2:]:
        wet&=_array(mask[ys,xs])>0

    def horizontal(name):
        value=ds.variables.get(name)
        if value is None or value.ndim!=3:
            return None
        if (value.shape[1:]!=var.shape[2:] or value.shape[0]<=time
                or value.dimensions[0]!=var.dimensions[0] or value.dimensions[1:]!=var.dimensions[2:]):
            raise ValueError(f'{name} 与所选结果的时间或网格维度不一致')
        _metres(value)
        return _array(value[time,ys,xs])

    water=horizontal('z')
    if water is None:water=horizontal('elev')
    surface_source='z' if water is not None else ''
    hn=ds.variables.get('hn')
    position='center'
    if hn is not None:
        if (hn.ndim!=4 or hn.shape[0]<=time or hn.shape[2:]!=var.shape[2:]
                or hn.dimensions[0]!=var.dimensions[0] or hn.dimensions[2:]!=var.dimensions[2:]):
            raise ValueError('hn 与所选结果的时间或网格不一致')
        _metres(hn)
        hstart,_=physical_vertical_grid(ds,hn)
        thickness=_array(hn[time,hstart:,ys,xs])
        layers=thickness.shape[0]
        if layers==count-1:
            raw=ds.variables.get('sigma')
            raw=_array(raw[:]) if raw is not None else np.array([])
            lo,hi=(0.,1.) if raw.size and raw.min()>=0 else ((-1.,1.) if raw.size and raw.max()>0 else (-1.,0.))
            if (raw.size!=var.shape[1] or not np.isfinite(raw).all() or np.any(np.diff(raw)<=0)
                    or not (np.isclose(raw[0],lo) and np.isclose(raw[-1],hi))):
                raise ValueError('界面变量与 hn 层厚无法对齐')
            position='interface'
        elif layers!=count:
            raise ValueError('hn 与所选变量的实际垂向层数不一致')
        elif hn.dimensions[1]!=var.dimensions[1]:
            raise ValueError('hn 与所选变量的垂向网格维度不一致')
        if thickness.shape[1:]!=depth.shape:
            raise ValueError('hn 与水深采样网格不一致')
        valid=wet & np.all(np.isfinite(thickness)&(thickness>0),axis=0)
        edges=np.concatenate([np.cumsum(thickness[::-1],axis=0)[::-1],np.zeros((1,)+depth.shape)],axis=0)
        surface=edges[0]-depth
        # GETM advances barotropic z every microstep and hn/zc at 3D steps.
        # Keep the 3D geometry bed-anchored; expose the separate surface rather
        # than rejecting valid hn/zc or moving its layers to a later 2D state.
        surface_source='hn-bathymetry'
        centers=edges.copy() if position=='interface' else (edges[:-1]+edges[1:])/2
        elevation=surface[None,...]-centers
        source='hn'
        zc=ds.variables.get('zc')
        if zc is not None and position=='center':
            _metres(zc)
            if (zc.ndim!=4 or zc.shape[0]<=time or zc.shape[2:]!=var.shape[2:]
                    or zc.dimensions!=var.dimensions):
                raise ValueError('zc 与所选结果的时间或网格不一致')
            zstart,_=physical_vertical_grid(ds,zc)
            elevation=_array(zc[time,zstart:,ys,xs])
            if elevation.shape!=centers.shape:raise ValueError('zc 与 hn 实际层数不一致')
            centers=surface[None,...]-elevation
            tolerance=1e-5*np.maximum(edges[0],1)+1e-6
            valid&=np.all(np.isfinite(centers)&(centers>=edges[1:]-tolerance)&(centers<=edges[:-1]+tolerance),axis=0)
            source='hn+zc'
        dynamic=True
    else:
        total=horizontal('D') if water is None else None
        sigma=ds.variables.get('sigma')
        if sigma is None:raise ValueError('缺少实际层厚 hn 或显式 sigma 坐标')
        raw=_array(sigma[:])
        if raw.ndim!=1 or not np.isfinite(raw).all() or np.any(np.diff(raw)<=0):
            raise ValueError('sigma 坐标必须有限且严格递增')
        lo,hi=(0.,1.) if raw.min()>=0 else ((-1.,1.) if raw.max()>0 else (-1.,0.))
        if raw.min()<lo or raw.max()>hi:raise ValueError('不支持此 sigma 坐标范围')
        if raw.size==var.shape[1]+1:
            interfaces=raw[start:];sigma=(interfaces[:-1]+interfaces[1:])/2
        elif raw.size==var.shape[1] and start==1:
            interfaces=raw;sigma=(raw[:-1]+raw[1:])/2
        elif raw.size==var.shape[1]:
            sigma=raw[start:]
            if var.name=='w' and np.isclose(sigma[0],lo) and np.isclose(sigma[-1],hi):
                position='interface';interfaces=sigma
            else:interfaces=np.r_[lo,(sigma[:-1]+sigma[1:])/2,hi]
        else:raise ValueError('sigma 坐标与实际层数不一致')
        if water is not None:surface=water;source='sigma+z';dynamic=True
        elif total is not None:surface=total-depth;source='sigma+D';surface_source='D-bathymetry';dynamic=True
        else:surface=np.zeros(depth.shape);source='sigma+bathymetry';surface_source='static bathymetry';dynamic=False
        column_depth=depth+surface
        valid=wet&np.isfinite(column_depth)&(column_depth>0)
        fraction=(hi-sigma)/(hi-lo)
        centers=fraction.reshape((-1,)+(1,)*depth.ndim)*column_depth
        edges=((hi-interfaces)/(hi-lo)).reshape((-1,)+(1,)*depth.ndim)*column_depth
        elevation=surface[None,...]-centers
    reference='below native 3D geometry surface' if hn is not None else (
        'below instantaneous water surface' if dynamic else 'below static bathymetric surface')
    difference=water-surface if water is not None else None
    synchronized=np.isfinite(difference)&np.isclose(difference,0,rtol=0,atol=1e-5) if difference is not None else None
    return dict(center_depth=np.where(valid,centers,np.nan),
        center_elevation=np.where(valid,elevation,np.nan),depth_edges=np.where(valid,edges,np.nan),
        surface_elevation=np.where(valid,surface,np.nan),valid=valid,source=source,
        position=position,dynamic=dynamic,surface_source=surface_source,
        depth_reference=reference,
        barotropic_surface_elevation=np.where(valid,water,np.nan) if water is not None else None,
        surface_difference=np.where(valid,difference,np.nan) if difference is not None else None,
        surface_synchronized=valid&synchronized if synchronized is not None else None,
        elevation_reference='model vertical datum',units='m')
