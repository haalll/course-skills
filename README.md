# course-skills

Lesson cards distilled from AI-agent courses, turned into Skills that agents on other
servers pull. Cards and code are in our own wording; no transcripts or notebooks are stored.

Layout:
- `<course-slug>/<lesson>/card.md`: when to use, patterns, do/don't, verified flag per gotcha
- `<course-slug>/<lesson>/reference/`: code and the framework mapping, kept out of the card
- `<course-slug>/<lesson>/lab/`: lab templates, not part of the card
- `skills/<name>/SKILL.md`: what an agent pulls
- `project-map.md`: where each card might apply (kept out of the cards)

Status: `main` holds the reviewed L04 and L05 cards (merged from `draft/r6`, round 7, Hal's approval). New work lands on `draft/rN` branches first. `.claude/` is ignored (tool state).

## Agentic Knowledge Graph Construction (DeepLearning.AI x Neo4j)
- [x] L04 Intro to ADK Part I: `agentic-kg-construction/L04-adk-part-1/card.md` (DRAFT)
- [x] L05 Intro to ADK Part II: `agentic-kg-construction/L05-adk-part-2/card.md` (DRAFT)
- [x] L06 Understanding user intent: `agentic-kg-construction/L06-user-intent/card.md` (DRAFT, branch draft/r7)
- [ ] L07 File suggestions
- [ ] L08 Schema proposal, structured
- [ ] L09 Schema proposal, unstructured
- [ ] L10-11 Knowledge graph construction I-II
- [ ] L01-03, L12 conceptual lessons (one combined card)
