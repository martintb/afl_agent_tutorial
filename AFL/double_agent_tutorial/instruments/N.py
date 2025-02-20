import pathlib

import pandas as pd
import xarray as xr

from AFL.double_agent_tutorial.core.VirtualInstrument import VirtualSAS
from AFL.double_agent_tutorial import PACKAGE_DIR, DATA_DIR


def get_virtual_instrument(
        noise=1e-5,
        hull_tracing_ratio=0.2,
        boundary_dataset_path=str(DATA_DIR / "phase_data/N.nc"),
        reference_data_path=str(DATA_DIR / "SANS"),
):
    boundary_dataset = xr.load_dataset(boundary_dataset_path)
    boundary_dataset.attrs['labels'] = 'labels'
    boundary_dataset.attrs['components'] = ['c', 'a', 'b']

    inst_client = VirtualSAS(noise=noise)
    inst_client.boundary_dataset = boundary_dataset
    inst_client.trace_boundaries(hull_tracing_ratio=hull_tracing_ratio, drop_phases=['D'])
    for fname in ['low_q.ABS', 'med_q.ABS', 'high_q.ABS']:
        data = pd.read_csv(str(pathlib.Path(reference_data_path) / fname),sep=r'\s+')#, delim_whitespace=True)
        inst_client.add_configuration(
            q=list(data.q),
            I=list(data.I),
            dI=list(data.dI),
            dq=list(data.dq),
            reset=False
        )
    inst_client.add_sasview_model(
        label='A',
        model_name='teubner_strey',
        model_kw={
            'scale': 0.05,
            'background': 1.0,
            'sld_a': 1.0,
            'sld_b': 6.0,
            'volfraction_a': 0.5,
            'd': 150,
            'xi': 150
        }
    )

    inst_client.add_sasview_model(
        label='D',
        model_name='power_law',
        model_kw={
            'scale': 0.0,
            'background': 1.0,
        }
    )
    return inst_client
