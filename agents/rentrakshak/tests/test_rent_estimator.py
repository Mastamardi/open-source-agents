from rentrakshak.services.rent_estimator import estimate_bengaluru_rent


def test_whitefield_2bhk_sufficient():
    r = estimate_bengaluru_rent("Whitefield", bhk="2 BHK")
    assert r.sufficient_data
    assert r.comparable_count >= 2
    assert r.rent_median_inr is not None


def test_unknown_locality_insufficient():
    r = estimate_bengaluru_rent("Jayanagar 9th Block")
    assert not r.sufficient_data
    assert r.rent_median_inr is None


def test_illustrative_limitation():
    r = estimate_bengaluru_rent("Whitefield", bhk="2 BHK")
    assert r.sufficient_data
    assert any("illustrative" in x.lower() or "asking" in x.lower() for x in r.limitations)
