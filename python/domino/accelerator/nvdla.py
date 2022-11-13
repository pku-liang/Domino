import os
import copy
from typing import Dict, Any
from collections import OrderedDict
from ..base import AcceleratorBase, AccTask
from ..utils import run_maestro, generate_maestro_command, find_maestro
from .conv_acc import ConvAccelerator


class NVDLA(ConvAccelerator):
    def __init__(self, name, freq=200, num_pes=65536, noc_bw=81920000, off_chip_bw=81920000, l1_size=4000000, l2_size=24000000) -> None:
        super(NVDLA, self).__init__(name, freq=freq, num_pes=65536, noc_bw=81920000,
                                    off_chip_bw=81920000, l1_size=4000000, l2_size=24000000)

    def get_mapping(self, H, W, P, Q, K, C, R, S, stride_h, stride_w):
        mapping = ("Network sample_net {\n"
                   "Layer Conv2d {\n"
                   "Type: CONV\n"
                   "Stride { "
                   f"X: {stride_h}, Y: {stride_w} "
                   "}\n"
                   "Dimensions { "
                   f"K: {K}, C: {C}, R: {R}, S: {S}, Y: {H}, X: {W} "
                   "}\n"
                   "Dataflow {\n"
                   "        SpatialMap(1,1) K;\n"
                   "        TemporalMap(64,64) C;\n"
                   "        TemporalMap(Sz(R),Sz(R)) R;\n"
                   "        TemporalMap(Sz(S),Sz(S)) S;\n"
                   "        TemporalMap(Sz(R),1) Y;\n"
                   "        TemporalMap(Sz(S),1) X;\n"
                   "        Cluster(64, P);\n"
                   "        SpatialMap(1,1) C;\n"
                   "        TemporalMap(Sz(R),1) Y;\n"
                   "        TemporalMap(Sz(S),1) X;\n"
                   "        TemporalMap(Sz(R),Sz(R)) R;\n"
                   "        TemporalMap(Sz(S),Sz(S)) S;\n"
                   "}\n"
                   "}\n"
                   "}\n")

        return mapping

    def spatial_used_pes(self, H, W, P, Q, K, C, R, S, stride_h, stride_w):
        """
        Return how many PEs are actually needed
        This is calculated according to the mapping
        """
        return K * 64
