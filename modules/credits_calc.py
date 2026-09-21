def compute_credits(E_project, E_baseline, LK, H,
                    unc_allowance=0.10, buf=0.15):
    """Расчёт потенциальных единиц Q по логике кейса."""
    R = -(E_project - E_baseline) - LK

    if R <= 0:
        return {"R": R, "Q": 0, "status": "Нет дополнительного эффекта"}

    if H <= 0:
        return {"R": R, "H": H, "Q": 0, "status": "Нулевая неопределённость"}

    hr = H / R
    if hr >= 1:
        return {"R": R, "H": H, "H/R": hr, "Q": 0,
                "status": "Неопределённость превышает результат"}

    UNC = unc_allowance if hr < 0.10 else hr
    Radj = R * (1 - UNC)
    B = Radj * buf
    Q = int(Radj - B)

    return {
        "R": R, "H": H, "H/R": hr,
        "UNC": UNC, "Radj": Radj, "B": B,
        "Q": max(Q, 0),
        "status": "OK"
    }