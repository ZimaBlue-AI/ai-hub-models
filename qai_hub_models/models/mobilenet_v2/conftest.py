# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
# THIS FILE WAS AUTO-GENERATED. DO NOT EDIT MANUALLY.

from unittest.mock import patch

import pytest

from qai_hub_models.models.mobilenet_v2 import Model
from qai_hub_models.utils.testing import skip_clone_repo_check


@pytest.fixture(autouse=True)
@skip_clone_repo_check
def mock_from_pretrained():
    """
    Model.from_pretrained() can be slow. Invoke it once and cache it so all invocations
    across all tests return the cached instance of the model.
    """
    mock = patch(
        "qai_hub_models.models.mobilenet_v2.Model.from_pretrained",
        return_value=Model.from_pretrained(),
    )
    mock.start()
