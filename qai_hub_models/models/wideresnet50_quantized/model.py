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
from aimet_torch.model_preparer import prepare_model
from aimet_torch.quantsim import QuantizationSimModel, load_encodings_to_sim

from qai_hub_models.models.wideresnet50.model import WideResNet50
from qai_hub_models.utils.aimet.config_loader import get_default_aimet_config
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset
from qai_hub_models.utils.base_model import SourceModelFormat, TargetRuntime

MODEL_ID = __name__.split(".")[-2]
MODEL_ASSET_VERSION = 2
DEFAULT_ENCODINGS = "wideresnet50_quantized_encodings.json"


class WideResNet50Quantizable(AIMETQuantizableMixin, WideResNet50):
    """WideResNet50 with post train quantization support.

    Supports only 8 bit weights and activations, and only loads pre-quantized checkpoints.
    Support for quantizing using your own weights & data will come at a later date."""

    def __init__(
        self,
        sim_model: QuantizationSimModel,
    ) -> None:
        WideResNet50.__init__(self, sim_model.model)
        AIMETQuantizableMixin.__init__(
            self,
            sim_model,
        )

    def preferred_hub_source_model_format(
        self, target_runtime: TargetRuntime
    ) -> SourceModelFormat:
        return SourceModelFormat.ONNX

    @classmethod
    def from_pretrained(
        cls,
        aimet_encodings: str | None = "DEFAULT",
    ) -> "WideResNet50Quantizable":
        """
        Parameters:
          aimet_encodings:
            if "DEFAULT": Loads the model with aimet encodings calibrated on imagenette.
            elif None: Doesn't load any encodings. Used when computing encodings.
            else: Interprets as a filepath and loads the encodings stored there.
        """
        model = WideResNet50.from_pretrained()
        input_shape = cls.get_input_spec()["image_tensor"][0]
        model = prepare_model(model)
        dummy_input = torch.rand(input_shape)

        pairs = fold_all_batch_norms(model, input_shape, dummy_input)
        equalize_bn_folded_model(model, input_shape, pairs, dummy_input)
        sim = QuantizationSimModel(
            model,
            quant_scheme="tf_enhanced",
            default_param_bw=8,
            default_output_bw=8,
            config_file=get_default_aimet_config(),
            dummy_input=dummy_input,
        )

        if aimet_encodings:
            if aimet_encodings == "DEFAULT":
                aimet_encodings = CachedWebModelAsset.from_asset_store(
                    MODEL_ID, MODEL_ASSET_VERSION, DEFAULT_ENCODINGS
                ).fetch()
            load_encodings_to_sim(sim, aimet_encodings)

        sim.model.eval()
        return cls(sim)

    def get_hub_compile_options(
        self, target_runtime: TargetRuntime, other_compile_options: str = ""
    ) -> str:
        compile_options = super().get_hub_compile_options(
            target_runtime, other_compile_options
        )
        return compile_options + " --quantize_full_type int8 --quantize_io"
