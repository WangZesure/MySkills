# Final Report Generation (Stage 7)

After Stage 6 delivery, produce a final report at `workspace/REPORT.md` structured like a short paper.

## Structure

1. **Abstract** — one paragraph: what was done, key results
2. **Problem Definition** — input/output tables, constraints, non-goals
3. **Design** — architecture ASCII diagram, module decomposition tree, data flow
4. **Results** — quantitative tables, ASCII visualizations (loss curves, speed bars), weight verification
5. **Test Point Verification** — P0/P1/P2 pass/fail table with actual values
6. **Conclusion** — verdict vs goal + agent collaboration reflection

## Visualization Requirements

- ASCII bar charts for performance comparisons (use Unicode blocks █▌▏)
- ASCII loss curves with epoch-by-epoch values
- Architecture diagram as PlantUML or ASCII box drawing
- Every table column traceable to a test point or goal.md entry

## Agent Collaboration Section

- Note which tasks were delegated to Claude Code and why
- Note cost (USD, turns, tokens) for delegated tasks
- Note which tasks were handled directly and why (simple enough)
- Reference the decision framework: "reference material exists → structured extraction, not knowledge-intensive"
