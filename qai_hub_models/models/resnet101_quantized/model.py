# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from __future__ import annotations

# isort: off
# This verifies aimet is installed, and this must be included first.
from qai_hub_models.utils.quantization_aimet import (
    AIMETQuantizableMixin,
)

# isort: on

import torch
from aimet_torch.cross_layer_equalization import (
    equalize_bn_folded_model,
    fold_all_batch_norms,
)
from aimet_torch.quantsim import QuantizationSimModel, load_encodings_to_sim

from qai_hub_models.models.resnet101.model import ResNet101
from qai_hub_models.utils.aimet.config_loader import get_per_channel_aimet_config
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset

MODEL_ID = __name__.split(".")[-2]
MODEL_ASSET_VERSION = 3
DEFAULT_ENCODINGS = "resnet101_quantized_encodings.json"


class ResNet101Quantizable(AIMETQuantizableMixin, ResNet101):
    """ResNet101 with post train quantization support.

    Supports only 8 bit weights and activations, and only loads pre-quantized checkpoints.
    Support for quantizing using your own weights & data will come at a later date."""

    def __init__(
        self,
        sim_model: QuantizationSimModel,
    ) -> None:
        ResNet101.__init__(self, sim_model.model)
        AIMETQuantizableMixin.__init__(
            self, sim_model, needs_onnx_direct_aimet_export=False
        )

    @classmethod
    def from_pretrained(
        cls,
        aimet_encodings: str | None = "DEFAULT",
    ) -> "ResNet101Quantizable":
        """
        Parameters:
          aimet_encodings:
            if "DEFAULT": Loads the model with aimet encodings calibrated on imagenette.
            elif None: Doesn't load any encodings. Used when computing encodings.
            else: Interprets as a filepath and loads the encodings stored there.
        """
        model = ResNet101.from_pretrained()
        input_shape = model.get_input_spec()["image_tensor"][0]
        dummy_input = torch.rand(input_shape)
        pairs = fold_all_batch_norms(model, input_shape, dummy_input)
        equalize_bn_folded_model(model, input_shape, pairs, dummy_input)

        sim = QuantizationSimModel(
            model.net,
            quant_scheme="tf_enhanced",
            default_param_bw=8,
            default_output_bw=8,
            config_file=get_per_channel_aimet_config(),
            dummy_input=torch.rand(input_shape),
        )

        if aimet_encodings:
            if aimet_encodings == "DEFAULT":
                aimet_encodings = CachedWebModelAsset.from_asset_store(
                    MODEL_ID, MODEL_ASSET_VERSION, DEFAULT_ENCODINGS
                ).fetch()
            load_encodings_to_sim(sim, aimet_encodings)

        sim.model.eval()
        return cls(sim)
