# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import numpy as np
import torchvision.models as tv_models

from qai_hub_models.models._shared.imagenet_classifier.test_utils import (  # noqa: F401
    imagenet_sample_torch,
    run_imagenet_classifier_test,
    run_imagenet_classifier_trace_test,
)
from qai_hub_models.models.swin_tiny.demo import main as demo_main
from qai_hub_models.models.swin_tiny.model import MODEL_ID, SwinTiny


def test_task(imagenet_sample_torch):
    # Ensure that the optimized SwinTiny matches the original one numerically
    x = imagenet_sample_torch
    model_opt = SwinTiny.from_pretrained().eval()
    model_orig = tv_models.swin_t(weights="IMAGENET1K_V1").eval()
    np.testing.assert_allclose(
        model_opt(x).detach().numpy(),
        model_orig(x).detach().numpy(),
        atol=1e-5,
        rtol=1e-3,
    )


def test_task():
    run_imagenet_classifier_test(
        SwinTiny.from_pretrained(), MODEL_ID, probability_threshold=0.53
    )


def test_trace():
    run_imagenet_classifier_trace_test(SwinTiny.from_pretrained())


def test_demo():
    # Verify demo does not crash
    demo_main(is_test=True)
