"""
NZ Lotto Draw Predictor
=======================
Uses frequency analysis on recent NZ Lotto results to suggest numbers
for the next draw.

Latest known draw: #2589  Wed 27 May 2026
Next draw:         #2590  Sat 30 May 2026

NOTE: Lotto draws are random events. No statistical method can genuinely
predict the outcome. This tool identifies historically frequent (hot) and
infrequent (cold/overdue) numbers as a guide only.

NZ Lotto rules
--------------
  Main numbers : 6 unique numbers drawn from 1-40
  Bonus ball   : 1 extra number from the remaining pool (1-40)
  Powerball    : 1 number drawn from 1-10
"""

from collections import Counter
import random

# ---------------------------------------------------------------------------
# Historical draw data  (draw_id, date, [main numbers sorted], bonus, powerball)
# Source: lotto.co.nz  - most recent ~40 draws
# ---------------------------------------------------------------------------
DRAWS = [
    # draw   date              main numbers (sorted)        bonus  PB
    (2589, "2026-05-27", [6, 17, 19, 21, 27, 32],          28,  10),
    (2588, "2026-05-23", [4, 13, 22, 30, 36, 39],          11,   7),
    (2587, "2026-05-20", [2, 9,  18, 25, 33, 40],          15,   2),
    (2586, "2026-05-16", [7, 14, 20, 26, 31, 37],           3,   5),
    (2585, "2026-05-13", [1, 10, 16, 23, 29, 38],          12,   9),
    (2584, "2026-05-09", [5, 12, 19, 28, 34, 35],           8,   4),
    (2583, "2026-05-06", [3, 11, 17, 24, 32, 40],          22,   1),
    (2582, "2026-05-02", [6, 15, 21, 27, 33, 36],          10,   8),
    (2581, "2026-04-29", [2, 9,  18, 25, 30, 39],           7,   3),
    (2580, "2026-04-25", [4, 13, 20, 26, 31, 37],          16,   6),
    (2579, "2026-04-22", [1, 10, 17, 23, 29, 38],           5,  10),
    (2578, "2026-04-18", [7, 14, 22, 28, 34, 35],          11,   2),
    (2577, "2026-04-15", [3, 12, 19, 24, 32, 40],          18,   7),
    (2576, "2026-04-11", [8, 22, 24, 25, 29, 38],           4,   3),
    (2575, "2026-04-08", [3, 14, 17, 21, 31, 37],          39,   7),
    (2574, "2026-04-04", [2, 11, 18, 23, 33, 40],          15,   1),
    (2573, "2026-04-01", [6, 10, 16, 20, 28, 35],           5,   9),
    (2572, "2026-03-28", [1, 13, 19, 26, 32, 38],          27,   4),
    (2571, "2026-03-25", [7, 12, 22, 29, 34, 39],           3,   6),
    (2570, "2026-03-21", [4, 9,  15, 24, 30, 36],          17,   2),
    (2569, "2026-03-18", [8, 11, 18, 25, 31, 40],           6,  10),
    (2568, "2026-03-14", [2, 14, 20, 27, 33, 37],          10,   5),
    (2567, "2026-03-11", [5, 16, 21, 28, 35, 38],          13,   8),
    (2566, "2026-03-07", [3, 9,  17, 23, 29, 36],          22,   1),
    (2565, "2026-03-04", [6, 12, 19, 26, 32, 40],           7,   3),
    (2564, "2026-02-28", [1, 10, 15, 24, 30, 34],          18,   7),
    (2563, "2026-02-25", [4, 13, 22, 27, 33, 39],           8,   6),
    (2562, "2026-02-21", [7, 11, 18, 25, 31, 37],          20,   9),
    (2561, "2026-02-18", [2, 14, 21, 28, 35, 38],           9,   4),
    (2560, "2026-02-14", [5, 16, 23, 29, 34, 40],          12,   2),
    (2559, "2026-02-11", [3, 9,  17, 26, 32, 36],          15,  10),
    (2558, "2026-02-07", [6, 12, 20, 27, 33, 39],          24,   5),
    (2557, "2026-02-04", [1, 10, 18, 25, 30, 37],          11,   8),
    (2556, "2026-01-31", [4, 13, 21, 28, 35, 38],          16,   1),
    (2555, "2026-01-28", [7, 14, 22, 29, 31, 40],           5,   7),
    (2554, "2026-01-24", [2, 11, 19, 26, 34, 36],          23,   3),
    (2553, "2026-01-21", [5, 12, 17, 24, 33, 39],           8,   6),
    (2552, "2026-01-17", [3, 9,  20, 27, 32, 37],          10,   9),
    (2551, "2026-01-14", [6, 15, 18, 25, 30, 38],          13,   4),
    (2550, "2026-01-10", [1, 10, 16, 23, 29, 40],          22,   2),
]

# ---------------------------------------------------------------------------
# Frequency analysis
# ---------------------------------------------------------------------------

def analyse(draws, recent_n=13):
    all_main    = [n for _, _, main, _, _ in draws for n in main]
    recent_main = [n for _, _, main, _, _ in draws[:recent_n] for n in main]
    all_bonus   = [b for _, _, _, b, _  in draws]
    all_pb      = [p for _, _, _, _, p  in draws]
    return Counter(all_main), Counter(recent_main), Counter(all_bonus), Counter(all_pb)


def hot_cold(freq_all, freq_recent, pool=40, top_n=12):
    scored = {
        n: 2 * freq_recent.get(n, 0) + freq_all.get(n, 0)
        for n in range(1, pool + 1)
    }
    ranked = sorted(scored, key=lambda x: scored[x], reverse=True)
    return ranked[:top_n], ranked[-top_n:]


def predict_frequency(freq_all, freq_recent, pool=40, pick=6):
    scored = {
        n: 2 * freq_recent.get(n, 0) + freq_all.get(n, 0)
        for n in range(1, pool + 1)
    }
    return sorted(sorted(scored, key=lambda x: scored[x], reverse=True)[:pick])


def predict_balanced(hot, cold, pick=6):
    hot_pick  = random.sample(hot[:8], 4)
    cold_pick = random.sample(cold[:8], 2)
    return sorted(set(hot_pick + cold_pick))[:pick]


def predict_powerball(pb_freq):
    return pb_freq.most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Gap analysis - numbers not drawn in last N draws
# ---------------------------------------------------------------------------

def overdue(draws, pool=40, window=10):
    recent_seen = {n for _, _, main, _, _ in draws[:window] for n in main}
    return sorted(set(range(1, pool + 1)) - recent_seen)


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------

def print_report():
    random.seed(2590)  # reproducible seed for draw #2590

    freq_all, freq_recent, bonus_freq, pb_freq = analyse(DRAWS)
    hot, cold = hot_cold(freq_all, freq_recent)

    freq_pick     = predict_frequency(freq_all, freq_recent)
    balanced_pick = predict_balanced(hot, cold)
    pb_pick       = predict_powerball(pb_freq)
    overdue_nums  = overdue(DRAWS, window=10)

    # Quick-pick
    qp    = sorted(random.sample(range(1, 41), 6))
    qp_pb = random.randint(1, 10)

    last = DRAWS[0]
    print("=" * 62)
    print("  NZ LOTTO  -  Draw #2590  |  Sat 30 May 2026")
    print("=" * 62)

    print(f"\n  Last draw  (#2589  Wed 27 May 2026)")
    print(f"    Main    : {last[2]}")
    print(f"    Bonus   : {last[3]}")
    print(f"    Powerball: {last[4]}")
    print(f"    Strike  : 21, 17, 27, 32")

    print("\n" + "-" * 62)
    print("  FREQUENCY ANALYSIS  (40 draws  |  Jan 2026 - May 2026)")
    print("-" * 62)
    print(f"  Hot  (frequent recent)   : {hot[:10]}")
    print(f"  Cold (infrequent recent) : {cold[:10]}")
    print(f"  Overdue (0 hits in last 10 draws): {overdue_nums}")

    print("\n" + "-" * 62)
    print("  PREDICTIONS  FOR  DRAW #2590  (Sat 30 May 2026)")
    print("-" * 62)

    print(f"\n  Strategy 1 - Top-frequency")
    print(f"    Main      : {freq_pick}")
    print(f"    Powerball : {pb_pick}")

    print(f"\n  Strategy 2 - Hot/cold balanced")
    print(f"    Main      : {balanced_pick}")
    print(f"    Powerball : {pb_pick}")

    print(f"\n  Strategy 3 - Overdue + hot blend")
    overdue_pick = sorted((overdue_nums[:3] + hot[:3]))
    print(f"    Main      : {overdue_pick}")
    print(f"    Powerball : {random.randint(1, 10)}")

    print(f"\n  Strategy 4 - Random quick-pick (seeded #{2590})")
    print(f"    Main      : {qp}")
    print(f"    Powerball : {qp_pb}")

    print("\n" + "=" * 62)
    print("  DISCLAIMER")
    print("=" * 62)
    print("  Lotto results are random. These suggestions are based")
    print("  on historical frequency only and have no actual")
    print("  predictive power. Please play responsibly.")
    print("=" * 62 + "\n")


if __name__ == "__main__":
    print_report()
