#!/usr/bin/env python3
"""retarget-trapped.py — stage 2, item 7.

Five pages stranded at position 20+. Each was competing for a bare destination
name it cannot win, against its own destination hub. Now that the hubs exist and
absorb the head-term job, these are free to narrow onto the modifier query each
one actually answers.

Counts and prices below were read out of the pages themselves.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snippet_fix import apply as apply_meta  # noqa: E402

RETARGETS = {
 # 1,383 impr, pos 30.7 — competed with the El Valle hub for the destination
 # name. Narrowed onto the exhaustive list it actually is (33 named stops).
 "articles/things-to-do-el-valle-de-anton": (
   "33 Things to Do in El Valle de Antón (2026)",
   "Every hike, waterfall, hot spring, market and wildlife stop in the El Valle "
   "crater — 33 of them, with what each one costs and how long it takes."),
 # 1,337 impr, pos 40.4 — same problem, same fix (33 named stops).
 "articles/things-to-do-in-boquete-panama": (
   "33 Things to Do in Boquete, Panama (2026)",
   "Every coffee farm, trail, hot spring and adventure around Boquete — 33 of "
   "them, with prices, times, and which ones are worth the trip out of town."),
 # 1,022 impr, pos 21.2 — "boquete travel guide" is unwinnable; the page is
 # really a 3-day itinerary, which is a query it can hold.
 "articles/boquete-travel-guide": (
   "Boquete in 3 Days: A Tested Itinerary (2026)",
   "A day-by-day Boquete itinerary: town and coffee on day one, farms and the "
   "Caldera hot springs on day two, Lost Waterfalls or Barú on day three."),
 # 353 impr, pos 33.1 — transport intent, so lead with the two real numbers.
 "es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": (
   "Cómo Llegar a Bocas del Toro: Vuelo 1 h o Bus $35",
   "Vuelo de una hora desde Albrook o bus nocturno más lancha por unos $35. Las "
   "cuatro rutas comparadas — y la última lancha sale de Almirante a las 6 pm."),
 # 348 impr, pos 22.4 — narrowed from the bare head term to the ranked
 # comparison the page is built around.
 "articles/day-trips-from-panama-city": (
   "7 Day Trips from Panama City, Ranked by Travel Time",
   "El Valle, Taboga, Portobelo, San Blas, Monkey Island and the canal transit — "
   "seven day trips compared on cost, travel time and what the day looks like."),
}

def main():
    bad = [(k, len(t), len(d)) for k, (t, d) in RETARGETS.items() if len(t) > 60 or len(d) > 160]
    if bad:
        print("  REFUSING — copy too long:", bad); sys.exit(1)
    n = sum(apply_meta(p, title=t, desc=d) for p, (t, d) in RETARGETS.items())
    print(f"  retargeted {len(RETARGETS)} trapped pages ({n} files changed)")

if __name__ == "__main__":
    main()
