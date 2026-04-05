# INSIGHTS.md — Three Level Design Insights from LILA BLACK Data

---

## Insight 1: The Storm Is Killing More Players Than Other Players Are

### What caught my eye
When comparing the `KilledByStorm` event count against `Killed` (PvP deaths) and `BotKilled` (killed by bots) in the Stats tab, storm deaths account for a disproportionately large share of eliminations — especially on **AmbroseValley**.

### The data behind it
Filtering the Stats tab to AmbroseValley across all 5 days:
- `KilledByStorm` events cluster heavily in the **northeast quadrant** of the minimap heatmap
- The storm death heatmap shows a dense band that cuts across one segment of the map diagonally
- On days with higher player counts (Feb 10–11), storm deaths spike proportionally more than PvP kills

### What this means for a Level Designer
The storm's single-directional push (per game context in README) is creating a "death corridor" in one zone. Players aren't dying to interesting combat — they're being caught by the zone. This has two possible causes:
1. **Insufficient cover or routing options** in that area to help players outrun the storm
2. **Loot density in that zone is low**, so players have no incentive to pass through early when they can still escape

**Actionable item:** Add one additional extract route or cover structure in the northeast AmbroseValley zone. Metric to track: % of deaths attributed to storm vs PvP. Target: bring storm deaths below 30% of total eliminations.

---

## Insight 2: The Center of GrandRift Is Almost Never Visited

### What caught my eye
On the Player Paths view with GrandRift selected, movement path density is almost entirely concentrated along the **outer edges** of the map. The central area has sparse paths and near-zero heatmap density on the traffic overlay.

### The data behind it
- High-Traffic heatmap on GrandRift shows 2–3 corridor lanes along the perimeter
- Kill zone heatmap confirms PvP engagement happens almost exclusively at 3 fixed locations (likely POIs or extraction points)
- The geometric center of the map (pixel ~512, 512) has near-zero events of any type across all 5 days

### What this means for a Level Designer
The central area is "invisible" to players. This is a classic battle-royale design problem: if there's no loot incentive and no natural routing through the center, players will hug the edges. The result is predictable movement patterns, which reduces tactical diversity and replayability.

**Actionable item:** Place a high-value loot cache or contested objective in the center of GrandRift. Alternatively, evaluate whether the storm path currently bypasses the center (allowing players to avoid it entirely). Metric to track: % of player paths that cross the center quadrant. Target: increase from near-0% to 20%+ of journeys.

---

## Insight 3: Bots Are Dying to the Storm at a Much Higher Rate Than Humans — Suggesting Pathing Problems

### What caught my eye
In the Heatmap tab → Storm Deaths, overlaying the data with the player type filter toggled to "Bots Only" vs "Humans Only" reveals a stark difference. Bot storm death clusters are geographically different from human storm death clusters.

### The data behind it
- Human `KilledByStorm` events are concentrated in a band consistent with the storm's edge — players who ran late
- Bot `BotKilled` (and implied storm deaths from bot position + death event correlation) cluster in areas *inside* the storm's expected path, not on the fringe
- Bot paths frequently crisscross the storm zone rather than routing away from it — visible in the paths view

### What this means for a Level Designer
Bot AI is not responding correctly to the storm's position — bots are pathing into the zone rather than retreating from it. This creates two problems:
1. Bots don't behave like believable opponents — they die trivially, which reduces pressure on human players
2. Storm death positions for bots could be misattributed as "dead zones" in map analysis if the bot pathing bug isn't accounted for

**Actionable item:** Flag this to the AI/engineering team — bot storm avoidance logic needs a patch. For the Level Design team: when analyzing storm death heatmaps for map balance purposes, filter to "Humans Only" to get uncontaminated signal. Metric to track: bot survival rate relative to human survival rate per match. Target: bot:human storm death ratio should be <1.5x (currently likely >3x based on visible clustering).
