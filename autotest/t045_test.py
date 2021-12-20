"""
Test the gmg load and write with an external summary file
"""
import pytest
import os
import flopy
import pymake
from ci_framework import base_test_dir, FlopyTestSetup

base_dir = base_test_dir(__file__, rel_path="temp", verbose=True)


path = os.path.join("..", "examples", "data", "secp")

mf_items = ["secp.nam"]
pths = []
for val in mf_items:
    pths.append(path)


def load_and_write_gmg(mfnam, pth):
    """
    test045 load and write of MODFLOW-2005 GMG example problem
    """
    exe_name = "mf2005"
    v = flopy.which(exe_name)
    run = v is not None

    model_ws = f"{base_dir}_{mfnam}"
    compth = os.path.join(model_ws, "flopy")
    test_setup = FlopyTestSetup(verbose=True, test_dirs=model_ws)

    pymake.setup(os.path.join(pth, mfnam), model_ws)

    m = flopy.modflow.Modflow.load(
        mfnam,
        model_ws=model_ws,
        verbose=True,
        exe_name=exe_name,
    )
    assert m.load_fail is False

    if run:
        try:
            success, buff = m.run_model(silent=False)
        except:
            success = False
        assert success, "base model run did not terminate successfully"
        fn0 = os.path.join(model_ws, mfnam)

    # rewrite files
    m.change_model_ws(compth)
    m.write_input()
    if run:
        try:
            success, buff = m.run_model(silent=False)
        except:
            success = False
        assert success, "new model run did not terminate successfully"
        fn1 = os.path.join(compth, mfnam)

    if run:
        fsum = os.path.join(model_ws, f"{os.path.splitext(mfnam)[0]}.head.out")
        success = False
        try:
            success = pymake.compare_heads(fn0, fn1, outfile=fsum)
        except:
            success = False
            print("could not perform head comparison")

        assert success, "head comparison failure"

        fsum = os.path.join(
            model_ws, f"{os.path.splitext(mfnam)[0]}.budget.out"
        )
        success = False
        try:
            success = pymake.compare_budget(
                fn0, fn1, max_incpd=0.1, max_cumpd=0.1, outfile=fsum
            )
        except:
            success = False
            print("could not perform budget comparison")

        assert success, "budget comparison failure"

    return


@pytest.mark.parametrize(
    "namfile, pth",
    zip(mf_items, pths),
)
def test_mf2005gmgload(namfile, pth):
    load_and_write_gmg(namfile, pth)
    return


if __name__ == "__main__":
    for namfile, pth in zip(mf_items, pths):
        load_and_write_gmg(namfile, pth)
