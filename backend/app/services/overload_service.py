def recommend_overload(target_sets: int, rep_min: int, rep_max: int, sets: list[dict], current_weight: float) -> str:
    if len(sets) < target_sets:
        return "Termine d'abord toutes les series de travail prevues."

    reps = [s.get("reps", 0) for s in sets[:target_sets]]
    if all(r >= rep_max for r in reps):
        next_weight = round(current_weight + 2.0, 1)
        return f"Objectif valide. Monte a {next_weight} kg a la prochaine seance."

    low_count = sum(1 for r in reps if r < rep_min)
    if low_count >= max(2, target_sets // 2):
        return "Performance en baisse recurrente: surveille fatigue, sommeil et deficit calorique."

    return "Continue sur cette charge jusqu'a stabiliser la fourchette haute de repetitions."
