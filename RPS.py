def player(prev_play, opponent_history=[]):
    if not hasattr(player, "state"):
        player.state = {
            "my_history": [],
            "scores": {"quincy": 0.0, "mrugesh": 0.0, "kris": 0.0, "abbey": 0.0},
            "abbey_order": {
                "RR": 0, "RP": 0, "RS": 0,
                "PR": 0, "PP": 0, "PS": 0,
                "SR": 0, "SP": 0, "SS": 0,
            },
            "last_preds": None,          
            "rounds": 0,
            "abbey_hits": 0,            
            "abbey_checks": 0,          
            "lock": None                
        }
    S = player.state

    beat = {"R":"P","P":"S","S":"R"}
    lose = {"R":"S","P":"R","S":"P"}

    if prev_play:
        opponent_history.append(prev_play)
        if S["last_preds"] and "abbey" in S["last_preds"]:
            S["abbey_checks"] += 1
            if S["last_preds"]["abbey"] == prev_play:
                S["abbey_hits"] += 1

        if S["last_preds"]:
            for k, pred in S["last_preds"].items():
                S["scores"][k] *= 0.9
                S["scores"][k] += (1.0 if pred == prev_play else -0.25)

    if len(S["my_history"]) >= 2:
        key = S["my_history"][-2] + S["my_history"][-1]
        if key in S["abbey_order"]:
            S["abbey_order"][key] += 1

    preds = {}

    last_my = S["my_history"][-1] if S["my_history"] else "R"
    preds["kris"] = beat[last_my]

    if S["my_history"]:
        window = S["my_history"][-10:]
        mf = max(set(window), key=window.count)
    else:
        mf = "S"
    preds["mrugesh"] = beat[mf]

    if S["my_history"]:
        base = S["my_history"][-1]
        candidates = [base + "R", base + "P", base + "S"]
        sub = {c: S["abbey_order"].get(c, 0) + 1 for c in candidates}
        q = max(sub, key=sub.get)[-1]  
    else:
        q = "R"
    preds["abbey"] = beat[q]       
    abbey_counter_move = beat[preds["abbey"]] 

    cycle = ["R","P","S"]
    def predict_cycle(hist):
        n = len(hist)
        if n < 3:
            return "R"
        best = (-1, 2, 0) 
        tail_len = min(n, 12)
        tail = hist[-tail_len:]
        for L in range(2, 6):
            if n < L: continue
            proto = hist[-L:]
            for off in range(L):
                cyc = proto[off:] + proto[:off]
                tiled = (cyc * ((tail_len // L) + 2))[:tail_len]
                score = sum(a == b for a, b in zip(tail, tiled))
                if score > best[0]:
                    best = (score, L, off)
        _, L, off = best
        proto = hist[-L:]
        cyc = proto[off:] + proto[:off]
        nxt = cyc[(tail_len) % L]
        return nxt if nxt in cycle else "R"

    preds["quincy"] = predict_cycle(opponent_history)

    S["rounds"] += 1
    if S["lock"] is None:
        if S["abbey_checks"] >= 20 and (S["abbey_hits"] / S["abbey_checks"] >= 0.6):
            S["lock"] = "abbey"
        elif S["rounds"] < 20:
            top = max(S["scores"], key=S["scores"].get)
            close = sorted(S["scores"].items(), key=lambda x: -x[1])
            if len(close) >= 2 and abs(close[0][1] - close[1][1]) < 0.6:
                target = "quincy" if (S["rounds"] % 2) else "abbey"
            else:
                target = top
        else:
            target = max(S["scores"], key=S["scores"].get)
    else:
        target = S["lock"]

    # 4) 出手
    if target == "abbey":
        my_move = abbey_counter_move  
    else:
        my_move = beat[preds[target]]

    S["my_history"].append(my_move)
    S["last_preds"] = preds
    return my_move

