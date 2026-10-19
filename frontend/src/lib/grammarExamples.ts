export const grammarExamples = {
  "Right-linear": "S -> aA | bS | ε\nA -> aA | b",
  "Left-linear": "S -> Aa | b\nA -> Aa | ε",
  "With epsilon": "S -> aS | ε",
  "Multi-terminal bodies": "S -> abA | c\nA -> aB | ε\nB -> b",
} as const;
