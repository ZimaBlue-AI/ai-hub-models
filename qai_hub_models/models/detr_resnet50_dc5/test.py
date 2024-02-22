# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from qai_hub_models.models._shared.detr.app import DETRApp
from qai_hub_models.models.detr_resnet50_dc5.demo import MODEL_ASSET_VERSION, MODEL_ID
from qai_hub_models.models.detr_resnet50_dc5.demo import main as demo_main
from qai_hub_models.models.detr_resnet50_dc5.model import (
    DEFAULT_WEIGHTS,
    DETRResNet50DC5,
)
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset, load_image

IMAGE_ADDRESS = CachedWebModelAsset.from_asset_store(
    MODEL_ID, MODEL_ASSET_VERSION, "detr_test_image.jpg"
)


def test_task():
    net = DETRResNet50DC5.from_pretrained(DEFAULT_WEIGHTS)
    img = load_image(IMAGE_ADDRESS)
    _, _, label, _ = DETRApp(net).predict(img, DEFAULT_WEIGHTS)
    assert set(list(label.numpy())) == {75, 63, 17}


def test_trace():
    net = DETRResNet50DC5.from_pretrained(DEFAULT_WEIGHTS).convert_to_torchscript()
    img = load_image(IMAGE_ADDRESS)
    _, _, label, _ = DETRApp(net).predict(img, DEFAULT_WEIGHTS)
    assert set(list(label.numpy())) == {75, 63, 17}


def test_demo():
    demo_main(is_test=True)
