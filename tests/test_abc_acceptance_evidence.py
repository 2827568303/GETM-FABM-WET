"""ABC acceptance is a database-backed distribution check, not random-start optimization."""
import copy
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'3DWET/app'))
from verify_calibration_acceptance import validate_abc_evidence, complete_calibration_history, record_failure
from calibration import PyabcEngine


@pytest.fixture(scope='module')
def abc_result(tmp_path_factory):
    np.random.seed(1402)
    params=[dict(module='lake',param='rate',min=0,max=1)]
    calls=[]
    def objective(values):
        score=.001 if not calls else .002+.001*(values[0]['value']-.4)**2
        calls.append(score)
        return score
    result=PyabcEngine().calibrate(params,objective,max_iter=2,population_size=4,
                                   max_simulations=80,minimum_epsilon=0,
                                   database_path=tmp_path_factory.mktemp('abc-evidence')/'run.db')
    assert result['success'],result
    assert result['best_objective']==calls[0] and min(calls[1:])>calls[0]
    return result,params


def test_real_abc_distribution_passes_even_when_first_draw_is_best(abc_result):
    result,params=abc_result
    evidence=validate_abc_evidence(result,result['history'],params,.01)
    assert evidence['database_matches_api']
    assert len(evidence['populations'])==2
    assert all(pop['particles']==4 for pop in evidence['populations'])


def test_distinct_particles_with_equal_distance_and_weight_are_all_verified(tmp_path):
    # Equal objectives occur naturally when native output precision quantizes
    # nearby trials. Particle identity must survive the evidence table pivot.
    np.random.seed(1601)
    params=[dict(module='lake',param='rate',min=0,max=1)]
    result=PyabcEngine().calibrate(params,lambda values:.01,max_iter=2,population_size=4,
                                   max_simulations=80,minimum_epsilon=0,
                                   database_path=tmp_path/'equal-distances.db')
    assert result['success'],result
    assert len({particle['params'][0]['value'] for particle in result['posterior']})==4
    import pyabc
    database=pyabc.History('sqlite:///'+Path(result['database_path']).resolve().as_posix())
    tidy=database.get_population_extended(m=0,t=0)
    raw=database.get_population_extended(m=0,t=0,tidy=False)
    assert len(raw['particle_id'].unique())==4
    assert len(tidy)<4, 'Fixture must reproduce tidy-pivot loss of distinct equal distance/weight particles'
    evidence=validate_abc_evidence(result,result['history'],params,.1)
    assert all(pop['particles']==4 for pop in evidence['populations'])


def test_failure_report_names_phase_and_preserves_empty_assertion_type():
    report={}
    record_failure(report,'abc_evidence_validation',AssertionError())
    assert report=={
        'failure_phase':'abc_evidence_validation',
        'error_type':'AssertionError',
        'error_message':'',
        'error':'AssertionError: ',
    }


@pytest.mark.parametrize('corruption',['weight','parameter','populations','iterations','samples','best','best_params'])
def test_abc_evidence_rejects_inconsistent_api_results(abc_result,corruption):
    original,params=abc_result;result=copy.deepcopy(original)
    if corruption=='weight':result['posterior'][0]['weight']+=.2
    elif corruption=='parameter':result['posterior'][0]['params'][0]['value']=99
    elif corruption=='populations':result['n_populations']=1
    elif corruption=='iterations':result['n_iterations']+=1
    elif corruption=='samples':result['populations'][0]['samples']+=1
    elif corruption=='best':result['best_objective']=.5
    elif corruption=='best_params':result['best_params'][0]['value']=99
    with pytest.raises(AssertionError):
        validate_abc_evidence(result,result['history'],params,.01)


def test_abc_posterior_must_improve_fixed_baseline(abc_result):
    result,params=abc_result
    with pytest.raises(AssertionError,match='fixed midpoint baseline'):
        validate_abc_evidence(result,result['history'],params,1e-8)


def test_completed_api_tail_keeps_full_history_beyond_fifty_evaluations():
    history=[dict(iteration=i+1,params=[dict(module='lake',param='rate',value=i/100)],objective=.001+i/100)
             for i in range(60)]
    status=dict(result=dict(history=history,n_iterations=60),history_len=60,
                history=[dict(row,timestamp='2026-10-14T00:00:00') for row in history[-50:]])
    complete=complete_calibration_history(status)
    assert len(complete)==60 and complete[0]['objective']==.001
    status['history'][0]['objective']=999
    with pytest.raises(AssertionError,match='evaluation tail'):
        complete_calibration_history(status)
