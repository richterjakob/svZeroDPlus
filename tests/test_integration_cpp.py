import json
import os

import numpy as np

from svzerodplus import run_from_config

this_file_dir = os.path.abspath(os.path.dirname(__file__))
cpp_exec = os.path.join(this_file_dir, "..", "Release", "svzerodsolver")

RTOL_PRES = 1.0e-7
RTOL_FLOW = 1.0e-8


def run_test_case_by_name(name):
    """Run a test case by its case name.

    Args:
        name: Name of the test case.
        testdir: Directory for performing the simulation.
    """
    testfile = os.path.join(os.path.dirname(__file__), "cases", name + ".json")
    with open(testfile) as ff:
        config = json.load(ff)
    result = run_from_config(config)

    output = {
        "pressure_in": {},
        "pressure_out": {},
        "flow_in": {},
        "flow_out": {},
    }

    last_seg_id = 0

    for vessel in config["vessels"]:
        name = vessel["vessel_name"]
        branch_id, seg_id = name.split("_")
        branch_id, seg_id = int(branch_id[6:]), int(seg_id[3:])
        vessel_id = vessel["vessel_id"]

        if seg_id == 0:
            output["pressure_in"][branch_id] = np.array(
                result[result.name == name]["pressure_in"]
            )
            output["flow_in"][branch_id] = np.array(
                result[result.name == name]["flow_in"]
            )
            output["pressure_out"][branch_id] = np.array(
                result[result.name == name]["pressure_out"]
            )
            output["flow_out"][branch_id] = np.array(
                result[result.name == name]["flow_out"]
            )
        elif seg_id > last_seg_id:
            output["pressure_out"][branch_id] = np.array(
                result[result.name == name]["pressure_out"]
            )
            output["flow_out"][branch_id] = np.array(
                result[result.name == name]["flow_out"]
            )

        last_seg_id = seg_id

    return output


def get_result(result_array, field, branch, time_step):
    """ "Get results at specific field, branch, branch_node and time step."""
    # extract result
    return result_array[field][branch][time_step]


def test_steady_flow_R_R():
    results = run_test_case_by_name("steadyFlow_R_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1100.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_r_coronary():
    results = run_test_case_by_name("steadyFlow_R_coronary")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 2000.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 1500.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_rlc_r():
    results = run_test_case_by_name("steadyFlow_RLC_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1100.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_rc_r():
    results = run_test_case_by_name("steadyFlow_RC_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1100.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_rl_r():
    results = run_test_case_by_name("steadyFlow_RL_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1100.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_r_rcr():
    results = run_test_case_by_name("steadyFlow_R_RCR")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 10500.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 10000.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_r_steady_pressure():
    results = run_test_case_by_name("steadyFlow_R_steadyPressure")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1500.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 1000.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_stenosis_r():
    results = run_test_case_by_name("steadyFlow_stenosis_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 3600.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # outlet flow


def test_steady_flow_bifurcationr_r1():
    results = run_test_case_by_name("steadyFlow_bifurcationR_R1")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 1100.0, rtol=RTOL_PRES
    )  # parent inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 600.0, rtol=RTOL_PRES
    )  # parent outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 1, -1), 600.0, rtol=RTOL_PRES
    )  # daughter1 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 1, -1), 350.0, rtol=RTOL_PRES
    )  # daughter1 outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 2, -1), 600.0, rtol=RTOL_PRES
    )  # daughter2 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 2, -1), 350.0, rtol=RTOL_PRES
    )  # daughter2 outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 1, -1), 2.5, rtol=RTOL_FLOW
    )  # daughter1 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 1, -1), 2.5, rtol=RTOL_FLOW
    )  # daughter1 outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 2, -1), 2.5, rtol=RTOL_FLOW
    )  # daughter2 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 2, -1), 2.5, rtol=RTOL_FLOW
    )  # daughter2 outlet flow


def test_steady_flow_bifurcationr_r2():
    results = run_test_case_by_name("steadyFlow_bifurcationR_R2")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 3462.5, rtol=RTOL_PRES
    )  # parent inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 1962.5, rtol=RTOL_PRES
    )  # parent outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 1, -1), 1962.5, rtol=RTOL_PRES
    )  # daughter1 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 1, -1), 432.5, rtol=RTOL_PRES
    )  # daughter1 outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 2, -1), 1962.5, rtol=RTOL_PRES
    )  # daughter2 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 2, -1), 1375.0, rtol=RTOL_PRES
    )  # daughter2 outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 1, -1), 3.825, rtol=RTOL_FLOW
    )  # daughter1 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 1, -1), 3.825, rtol=RTOL_FLOW
    )  # daughter1 outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 2, -1), 1.175, rtol=RTOL_FLOW
    )  # daughter2 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 2, -1), 1.175, rtol=RTOL_FLOW
    )  # daughter2 outlet flow


def test_pulsatile_flow_r_rcr():
    results = run_test_case_by_name("pulsatileFlow_R_RCR")
    assert np.isclose(
        get_result(results, "pressure_in", 0, 0), 4620.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, 0), 4400.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, 0), 2.2, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, 0), 2.2, rtol=RTOL_FLOW
    )  # outlet flow


def test_pulsatile_flow_r_coronary():
    results = run_test_case_by_name("pulsatileFlow_R_coronary")
    assert np.isclose(
        get_result(results, "pressure_in", 0, 0), 880.0, rtol=RTOL_PRES
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, 0), 660.0, rtol=RTOL_PRES
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, 0), 2.2, rtol=RTOL_FLOW
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, 0), 2.2, rtol=RTOL_FLOW
    )  # outlet flow


def test_pusatile_flow_cstenosis_steady_pressure():
    results = run_test_case_by_name("pusatileFlow_CStenosis_steadyPressure")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -439),
        0.5933049197138334,
        rtol=1.0e-5,
    )  # inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -439), 0.1, rtol=1.0e-5
    )  # outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -439),
        0.7023611813029965,
        rtol=1.0e-5,
    )  # inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -439),
        0.7023611813029965,
        rtol=1.0e-5,
    )  # outlet flow


def test_steady_flow_confluencer_r():
    results = run_test_case_by_name("steadyFlow_confluenceR_R")
    assert np.isclose(
        get_result(results, "pressure_in", 0, -1), 6600.0, rtol=RTOL_PRES
    )  # parent inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 0, -1), 6100.0, rtol=RTOL_PRES
    )  # parent outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 1, -1), 8100.0, rtol=RTOL_PRES
    )  # daughter1 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 1, -1), 6100.0, rtol=RTOL_PRES
    )  # daughter1 outlet pressure
    assert np.isclose(
        get_result(results, "pressure_in", 2, -1), 6100.0, rtol=RTOL_PRES
    )  # daughter2 inlet pressure
    assert np.isclose(
        get_result(results, "pressure_out", 2, -1), 1600.0, rtol=RTOL_PRES
    )  # daughter2 outlet pressure
    assert np.isclose(
        get_result(results, "flow_in", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 0, -1), 5.0, rtol=RTOL_FLOW
    )  # parent outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 1, -1), 10.0, rtol=RTOL_FLOW
    )  # daughter1 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 1, -1), 10.0, rtol=RTOL_FLOW
    )  # daughter1 outlet flow
    assert np.isclose(
        get_result(results, "flow_in", 2, -1), 15.0, rtol=RTOL_FLOW
    )  # daughter2 inlet flow
    assert np.isclose(
        get_result(results, "flow_out", 2, -1), 15.0, rtol=RTOL_FLOW
    )  # daughter2 outlet flow


def test_closed_loop_heart_single_vessel(tmpdir):
    results = run_test_case_by_name("closedLoopHeart_singleVessel")
    assert np.isclose(
        np.mean(np.array(results['pressure_in'][0])), 55.703345704742844, rtol=RTOL_PRES
    )  # mean aortic pressure
    assert np.isclose(
        np.amax(np.array(results['pressure_in'][0])), 73.97450170686889, rtol=RTOL_PRES
    )  # max aortic pressure
    assert np.isclose(
        np.amin(np.array(results['pressure_in'][0])), 0.0, rtol=RTOL_PRES
    )  # min aortic pressure
    assert np.isclose(
        np.mean(np.array(results['flow_in'][0])), 43.21028819256006, rtol=RTOL_FLOW
    )  # aortic inflow


def test_closed_loop_heart_with_coronaries(tmpdir):
    results = run_test_case_by_name("closedLoopHeart_withCoronaries")
    assert np.isclose(
        np.mean(np.array(results['pressure_in'][0])), 50.162313086833805, rtol=RTOL_PRES
    )  # mean aortic pressure
    assert np.isclose(
        np.amax(np.array(results['pressure_in'][0])), 69.01524513715958, rtol=RTOL_PRES
    )  # max aortic pressure
    assert np.isclose(
        np.mean(np.array(results['flow_in'][0])), 38.05442038841015, rtol=RTOL_FLOW
    )  # mean aortic flow
    assert np.isclose(
        np.amax(np.array(results['flow_in'][0])), 171.35198346122127, rtol=RTOL_FLOW
    )  # max aortic flow
