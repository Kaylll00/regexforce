export type RegexToken = {
  kind: "symbol" | "union" | "star" | "plus" | "qmark" | "lparen" | "rparen" | "epsilon" | "empty" | "error";
  value: string;
  start: number;
  end: number;
};

export function regexTokens(text: string, textbook = false): RegexToken[] {
  const tokens: RegexToken[] = [];
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (char === " " || char === "\t") continue;
    if (char === "\\") {
      if (index + 1 >= text.length) {
        tokens.push({ kind: "error", value: char, start: index, end: index + 1 });
      } else {
        tokens.push({ kind: "symbol", value: text[index + 1], start: index, end: index + 2 });
        index += 1;
      }
      continue;
    }
    const kinds: Record<string, RegexToken["kind"]> = {
      "|": "union", "*": "star", "+": textbook ? "union" : "plus", "?": "qmark",
      "(": "lparen", ")": "rparen", "ε": "epsilon", "∅": "empty",
    };
    tokens.push({
      kind: kinds[char] ?? (".[]{}^$".includes(char) ? "error" : "symbol"),
      value: char,
      start: index,
      end: index + 1,
    });
  }
  return tokens;
}
