export type StepKind = "info" | "valid_argument" | "numeric_demonstration" | "warning";

export type Step = {
  title: string;
  description: string;
  data: Record<string, unknown>;
  kind: StepKind;
};

export type Transition = { from: string; symbol: string; to: string };

export type Automaton = {
  type: "nfa" | "dfa";
  alphabet: string[];
  states: string[];
  start: string;
  accepting: string[];
  transitions: Transition[];
  labels?: Record<string, string[]>;
};

export type TransitionTable = {
  alphabet: string[];
  has_epsilon: boolean;
  rows: Array<{
    state: string;
    start: boolean;
    accepting: boolean;
    cells: Record<string, string[]>;
  }>;
};

export type SimStep = {
  index: number;
  symbol: string | null;
  before: string[];
  after: string[];
  via_epsilon: string[];
  note: string;
};

export type SimulationResult = {
  string: string;
  accepted: boolean;
  steps: SimStep[];
  reason: string;
  rejected_at: number | null;
};

export type Rule = {
  kind: "regex" | "automaton" | "grammar";
  regex?: string;
  textbook?: boolean;
  automaton?: Automaton;
  grammar?: string;
};

export type ApiErrorBody = {
  error: { code: string; message: string; position: number | null };
};
