import pytest

from domain.enums import NodeColor
from domain.rules import calculate_dominio_score, calculate_node_color, sm2_update


# --- calculate_node_color ---

def test_color_none_is_azul():
    assert calculate_node_color(None, False) == NodeColor.azul


def test_color_none_with_deps_is_azul():
    assert calculate_node_color(None, True) == NodeColor.azul


def test_color_08_is_verde():
    assert calculate_node_color(0.8, False) == NodeColor.verde


def test_color_09_is_verde():
    assert calculate_node_color(0.9, False) == NodeColor.verde


def test_color_079_is_amarelo():
    assert calculate_node_color(0.79, False) == NodeColor.amarelo


def test_color_05_is_amarelo():
    assert calculate_node_color(0.5, False) == NodeColor.amarelo


def test_color_low_no_deps_is_amarelo():
    assert calculate_node_color(0.49, False) == NodeColor.amarelo


def test_color_low_with_deps_is_vermelho():
    assert calculate_node_color(0.49, True) == NodeColor.vermelho


def test_color_zero_with_deps_is_vermelho():
    assert calculate_node_color(0.0, True) == NodeColor.vermelho


def test_color_zero_no_deps_is_amarelo():
    assert calculate_node_color(0.0, False) == NodeColor.amarelo


# --- calculate_dominio_score ---

def test_score_empty_is_none():
    assert calculate_dominio_score([]) is None


def test_score_single_one():
    assert calculate_dominio_score([1.0]) == pytest.approx(1.0)


def test_score_single_zero():
    assert calculate_dominio_score([0.0]) == pytest.approx(0.0)


def test_score_single_half():
    assert calculate_dominio_score([0.5]) == pytest.approx(0.5)


def test_score_clamped_in_range():
    result = calculate_dominio_score([0.0, 1.0])
    assert result is not None
    assert 0.0 <= result <= 1.0


def test_score_recent_weighs_more():
    # [0.0, 1.0] → recent is 1.0 (high), should score higher than [1.0, 0.0]
    assert calculate_dominio_score([0.0, 1.0]) > calculate_dominio_score([1.0, 0.0])  # type: ignore[operator]


# --- sm2_update ---

def test_sm2_low_quality_resets_interval():
    _, interval = sm2_update(2.5, 6, 2)
    assert interval == 1


def test_sm2_low_quality_preserves_ef():
    ef, _ = sm2_update(2.5, 6, 2)
    assert ef == pytest.approx(2.5)


def test_sm2_quality5_first_interval_gives_6():
    _, interval = sm2_update(2.5, 1, 5)
    assert interval == 6


def test_sm2_ef_floor_at_1_3():
    ef, _ = sm2_update(1.3, 6, 3)
    assert ef >= 1.3


def test_sm2_high_quality_increases_ef():
    ef, _ = sm2_update(2.5, 6, 5)
    assert ef > 2.5
