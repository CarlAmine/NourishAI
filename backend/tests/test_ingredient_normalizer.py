from backend.app.services.ingredient_normalizer import normalize_ingredient, normalize_ingredient_list


def test_normalize_ingredient_aliases():
    assert normalize_ingredient("Garbanzo Beans") == "chickpea"
    assert normalize_ingredient("Scallions") == "green onion"


def test_normalize_ingredient_plural():
    assert normalize_ingredient("tomatoes") == "tomato"


def test_normalize_list():
    values = normalize_ingredient_list(["Chicken breasts", "BELL peppers"])
    assert values == ["chicken breast", "bell pepper"]
