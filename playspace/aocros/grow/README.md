# Grow Directory

Knowledge base for AOCROS learning and pattern recognition.

## Structure

```
grow/
├── patterns/          ← Learned behavior patterns
│   ├── user_patterns/
│   ├── environment_patterns/
│   └── interaction_patterns/
├── identities/        ← Agent identity storage
│   ├── mylzeron/
│   ├── miles/
│   └── clawbot/
└── fractals/         ← Mylzeron's hobby
    └── mandelbrot/
```

## Pattern Format

Each pattern is a JSON file:
```json
{
  "pattern_id": "user_morning_routine",
  "created": "2026-02-18T07:00:00Z",
  "frequency": 0.87,
  "triggers": ["time:07:00", "location:home"],
  "actions": ["check_dusty", "health_report"]
}
```

## Learning

- Patterns extracted from unconscious memory
- Summarized by memory-summarizer agent
- Validated by CREAM compliance

## Identity Storage

Each agent stores:
- Core personality traits
- Learned preferences
- Decision weights
- Relationship mappings