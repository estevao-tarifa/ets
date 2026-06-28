from __future__ import annotations

from domain.enums import NodeColor


def calculate_node_color(dominio: float | None, tem_dependentes: bool) -> NodeColor:
    if dominio is None:
        return NodeColor.azul
    if dominio >= 0.8:
        return NodeColor.verde
    if dominio >= 0.5:
        return NodeColor.amarelo
    # dominio < 0.5
    return NodeColor.vermelho if tem_dependentes else NodeColor.amarelo


def calculate_dominio_score(resultados: list[float]) -> float | None:
    if not resultados:
        return None
    decay = 0.8
    n = len(resultados)
    weights = [decay ** (n - 1 - i) for i in range(n)]
    score = sum(r * w for r, w in zip(resultados, weights)) / sum(weights)
    return max(0.0, min(1.0, score))


def sm2_update(ease_factor: float, interval_days: int, quality: int) -> tuple[float, int]:
    if quality < 3:
        return ease_factor, 1
    if interval_days <= 1:  # ponytail: first review → jump to 6-day interval (SM-2 step 1→6)
        new_interval = 6
    else:
        new_interval = round(interval_days * ease_factor)
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)
    return new_ef, new_interval


if __name__ == "__main__":
    assert calculate_node_color(None, False) == NodeColor.azul
    assert calculate_node_color(0.9, False) == NodeColor.verde
    assert calculate_node_color(0.6, True) == NodeColor.amarelo
    assert calculate_node_color(0.3, True) == NodeColor.vermelho
    assert calculate_node_color(0.3, False) == NodeColor.amarelo

    assert calculate_dominio_score([]) is None
    score = calculate_dominio_score([0.0, 1.0])
    assert score is not None and 0.0 <= score <= 1.0
    # recent result should weigh more
    assert calculate_dominio_score([0.0, 1.0]) > calculate_dominio_score([1.0, 0.0])  # type: ignore[operator]

    ef, iv = sm2_update(2.5, 1, 2)  # quality < 3
    assert iv == 1 and ef == 2.5
    ef2, iv2 = sm2_update(2.5, 1, 5)  # perfect on first
    assert iv2 == 6
    ef3, iv3 = sm2_update(2.5, 6, 5)  # perfect on second
    assert iv3 == round(6 * 2.5)

    print("all assertions passed")
