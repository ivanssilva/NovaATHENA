"""E7.3: deterministic SYNTHETIC finite-queue pressure model, not OoO measurements."""
from collections import deque
import csv, json, os

def simulate(arrivals, learn_cap, control_cap, learn_rate, control_rate, policy):
    assert policy in ("drop", "backpressure")
    assert learn_cap > 0 and control_cap > 0 and learn_rate > 0 and control_rate > 0
    learn, control = deque(), deque()
    pending = deque((i, t) for t, count in enumerate(arrivals) for _ in range(count))
    accepted = dropped = blocked = completed = 0
    max_learn = max_control = 0
    latencies = []
    cycle = 0
    while pending or learn or control:
        # Input arrivals are released by their specified cycle; backpressure holds head.
        for _ in range(learn_rate):
            if learn:
                item, born = learn.popleft()
                if len(control) < control_cap:
                    control.append((item, born))
                else:
                    # ControlQ full: LearnQ head must wait; no silent loss.
                    learn.appendleft((item, born))
                    break
        for _ in range(control_rate):
            if control:
                item, born = control.popleft()
                completed += 1
                latencies.append(cycle - born + 1)
        # All offered items for this cycle; backpressure retains pending head.
        while pending and pending[0][1] <= cycle:
            if len(learn) < learn_cap:
                learn.append(pending.popleft())
                accepted += 1
            elif policy == "drop":
                pending.popleft()
                dropped += 1
            else:
                blocked += 1
                break
        max_learn = max(max_learn, len(learn))
        max_control = max(max_control, len(control))
        cycle += 1
        assert cycle < 100000, "possible deadlock"
    assert completed + dropped == sum(arrivals)
    assert accepted == completed
    return dict(cycles=cycle, offered=sum(arrivals), accepted=accepted, completed=completed,
                dropped=dropped, blocked_cycles=blocked, peak_learn=max_learn,
                peak_control=max_control, mean_latency=(sum(latencies)/len(latencies) if latencies else 0))

def main():
    # Directed checks, with fixed traffic (no measured OoO temporal claims).
    assert simulate([1, 0, 0], 1, 1, 1, 1, "drop")["completed"] == 1
    assert simulate([3], 1, 1, 1, 1, "drop")["offered"] == 3
    # Saturation stress: input burst vs deliberately slower downstream.
    traffic = [4] * 12 + [0] * 12
    for policy in ("drop", "backpressure"):
        r = simulate(traffic, 1, 1, 1, 1, policy)
        assert r["completed"] + r["dropped"] == 48
        if policy == "backpressure":
            assert r["dropped"] == 0
    os.makedirs("e7-3-results", exist_ok=True)
    with open("e7-3-results/queue_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pattern","policy","learn_cap","control_cap","learn_rate","control_rate",
            "cycles","offered","accepted","completed","dropped","blocked_cycles","peak_learn","peak_control","mean_latency"])
        w.writeheader()
        count = 0
        for name, arrivals in (("burst", [4]*12+[0]*12), ("sparse", [1 if i%4==0 else 0 for i in range(48)])):
            for policy in ("drop", "backpressure"):
                for lc in (1, 2, 4, 8):
                    for cc in (1, 2, 4):
                        for lr, cr in ((1, 1), (2, 1), (2, 2)):
                            result = simulate(arrivals, lc, cc, lr, cr, policy)
                            w.writerow(dict(pattern=name, policy=policy, learn_cap=lc, control_cap=cc,
                                            learn_rate=lr, control_rate=cr, **result))
                            count += 1
    with open("e7-3-results/manifest.json", "w") as f:
        json.dump({"model":"synthetic_discrete_queue","patterns":["burst","sparse"],
                   "policies":["drop","backpressure"],"scenarios":count,
                   "limitations":"not observed OoO events; input service model is assumed"},f,indent=2)
    print(f"E7_3_SYNTHETIC_PASS scenarios {count} invariants conservation and no silent loss", flush=True)

if __name__ == "__main__":
    main()
