import sys
from unittest.mock import MagicMock

# stub heavy deps that aren't installed; keep real numpy (installed, needed by pytest.approx)
for _mod in ("sentence_transformers", "sentence_transformers.cross_encoder"):
    sys.modules.setdefault(_mod, MagicMock())
sys.modules.setdefault("backend.infrastructure.local_embeddings", MagicMock(encode_one=MagicMock()))
sys.modules.setdefault("backend.infrastructure.vector_store", MagicMock(knn_search=MagicMock()))

from backend.services.dedup import classify  # noqa: E402


def test_high_score_auto_merge():
    assert classify(0.96) == "auto_merge"


def test_mid_score_review_queue():
    assert classify(0.80) == "review_queue"


def test_low_score_new_node():
    assert classify(0.50) == "new_node"


def test_boundary_0_75_inclusive():
    assert classify(0.75) == "review_queue"


def test_boundary_0_95_conservative():
    assert classify(0.95) == "review_queue"


def test_boundary_0_951_auto_merge():
    assert classify(0.951) == "auto_merge"
