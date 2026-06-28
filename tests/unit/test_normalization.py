from backend.pipeline.normalization import normalize_one


def test_case_normalization():
    assert normalize_one("Integral Definida") == "integral definida"


def test_trim_whitespace():
    assert normalize_one("  Derivada  ") == "derivada"


def test_alias_integral_de_riemann():
    assert normalize_one("integral de riemann") == "integral definida"


def test_alias_antiderivada():
    assert normalize_one("antiderivada") == "integral indefinida"


def test_inversion_no_error():
    # "derivada de função" triggers inversion path; just assert it runs
    result = normalize_one("derivada de função")
    assert isinstance(result, str)
