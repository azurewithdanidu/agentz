# Verdict rules

Scores come from `search_catalog.py`, which uses the overlap coefficient on name and description words. CI warns on a new skill scoring 0.6 or higher against an existing one.

| Situation | Verdict |
| --- | --- |
| A match does the same job for the same users, and the brief adds nothing material | **Reuse** |
| A match does most of the job and the gap fits naturally inside it (a new rule, input type or output) | **Extend** |
| A match scores high but serves a different job, input or audience | **New**, with the difference stated |
| No match scores 0.4 or higher | **New** |
| A new plugin would trigger on the same prompts as an existing skill | **Extend**, or narrow the new skill's triggers until they don't collide |

Always prefer extending a plugin over publishing a near-copy. Two skills that trigger on the same prompt make both less reliable.
