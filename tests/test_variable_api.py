import sys
import threading
from pathlib import Path
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'3DWET/app'))


def test_reference_endpoint_checks_real_units_and_busy_state(tmp_path):
    from variable_api import register_variable_routes
    context = dict(case_path=tmp_path, busy=False, lock=threading.RLock(),
                   lookup=lambda name: {'name':name,'units':'Celsius','long_name':'temperature'} if name=='temp' else None)
    app=Flask(__name__);register_variable_routes(app,lambda:context)
    client=app.test_client()
    assert client.post('/api/results/reference',json={'name':'missing','units':'m','value':2}).status_code==404
    assert client.post('/api/results/reference',json={'name':'temp','units':'m','value':2}).status_code==400
    context['busy']=True
    assert client.post('/api/results/reference',json={'name':'temp','units':'Celsius','value':20}).status_code==409
    assert not (tmp_path/'variable_references.json').exists()
    context['busy']=False
    response=client.post('/api/results/reference',json={'name':'temp','units':'Celsius','value':20})
    assert response.status_code==200
    assert response.json['variable']['reference']['kind']=='custom'
    assert response.json['variable']['name']=='temp'
    assert response.json['variable']['reference']['value']==20


def test_reference_uses_actual_external_output_units(tmp_path):
    from variable_api import register_variable_routes
    (tmp_path/'fabm.yaml').write_text('instances:\n  abiotic_water:\n    model: wet/abiotic_water\n',encoding='utf-8')
    context = dict(case_path=tmp_path,busy=False,lock=threading.RLock(),
        lookup=lambda name:dict(name=name,units='mgO2/L',long_name='oxygen'))
    app=Flask(__name__);register_variable_routes(app,lambda:context)
    client=app.test_client()
    response=client.post('/api/results/reference',json=dict(name='abiotic_water_sO2W',units='mgO2/L',value=7))
    assert response.status_code==200, response.json
    assert response.json['variable']['reference']['value']==7
    assert client.post('/api/results/reference',json=dict(name='abiotic_water_sO2W',units='g/m3',value=7)).status_code==400
