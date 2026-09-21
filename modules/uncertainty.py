def scenario_uncertainty(E, ratio=0.20):
    """Сценарный диапазон: ±ratio от E."""
    H = abs(E) * ratio
    return {"E": E, "L": E - H, "U": E + H, "H": H}