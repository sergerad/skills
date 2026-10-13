// Colours the code in <pre><code class="language-…"> blocks: comments, strings, numbers, keywords,
// type names, constants and called functions. It is a small tokenizer, not a parser: enough to make
// a signature or an excerpt easy to scan. Without this script the code still reads as plain text.
(function () {
  const C_LIKE = { block: true, line: "//" };
  const LANGUAGES = {
    rust: {
      ...C_LIKE,
      chars: true,
      words:
        "as async await break const continue crate dyn else enum extern false fn for if impl in let loop match mod move mut pub ref return self Self static struct super trait true type unsafe use where while",
    },
    go: {
      ...C_LIKE,
      quotes: "\"'`",
      words:
        "break case chan const continue default defer else fallthrough false for func go goto if import interface map nil package range return select struct switch true type var",
    },
    typescript: {
      ...C_LIKE,
      quotes: "\"'`",
      words:
        "abstract as async await break case catch class const continue default delete do else enum export extends false finally for from function if implements import in instanceof interface let new null of private protected public readonly return static super switch this throw true try type typeof undefined var void while yield",
    },
    python: {
      line: "#",
      quotes: "\"'",
      words:
        "and as assert async await break class continue def del elif else except False finally for from global if import in is lambda None nonlocal not or pass raise return self True try while with yield",
    },
    solidity: {
      ...C_LIKE,
      quotes: "\"'",
      words:
        "abstract address bool bytes calldata constant constructor contract else emit enum error event external false for function if immutable import interface internal is library mapping memory modifier new override payable private public pure require return returns revert storage string struct true using view virtual while",
    },
    sql: {
      block: true,
      line: "--",
      quotes: "'\"",
      anyCase: true,
      words:
        "abort add after all alter and as autoincrement before begin between blob by case check commit conflict constraint create default delete distinct do drop else end exists foreign from group having if in index insert integer into is join key left limit not null on or order pragma primary references rollback select set strict table text then transaction trigger union unique update values when where",
    },
    shell: { line: "#", quotes: "\"'", words: "case do done elif else esac fi for function if in then while" },
    config: { line: "#", quotes: "\"'", words: "false null true" },
    json: { quotes: '"', words: "false null true" },
  };
  const ALIASES = {
    rs: "rust",
    ts: "typescript",
    js: "typescript",
    javascript: "typescript",
    py: "python",
    sol: "solidity",
    sh: "shell",
    bash: "shell",
    toml: "config",
    yaml: "config",
  };
  const NEVER = "(?!)";

  function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\\/-]/g, "\\$&");
  }

  function tokenizer(language) {
    const comments = [];
    if (language.block) comments.push("/\\*[\\s\\S]*?\\*/");
    if (language.line) comments.push(escapeRegExp(language.line) + "[^\\n]*");
    const strings = Array.from(language.quotes || '"').map((quote) => {
      const stop = quote === "`" ? quote : quote + "\\n";
      return quote + "(?:\\\\.|[^" + stop + "\\\\])*" + quote;
    });
    // A Rust character literal; a lifetime ('a) has no closing quote and is left alone.
    if (language.chars) strings.push("'(?:\\\\[^']+|[^'\\\\])'");
    const number = "\\b(?:0[xXbBoO][0-9a-fA-F_]+|\\d[\\d_]*(?:\\.\\d[\\d_]*)?(?:[eE][+-]?\\d+)?)[A-Za-z0-9_]*";
    const identifier = "[A-Za-z_$][A-Za-z0-9_$]*";
    return new RegExp(
      "(" + (comments.join("|") || NEVER) + ")|(" + strings.join("|") + ")|(" + number + ")|(" + identifier + ")",
      "g",
    );
  }

  function identifierClass(word, rest, language, words) {
    if (words.has(language.anyCase ? word.toLowerCase() : word)) return "kw";
    if (/^!?\(/.test(rest)) return "fn";
    if (/^[A-Z][A-Z0-9_]+$/.test(word)) return "const";
    if (/^[A-Z]/.test(word)) return "type";
    return "";
  }

  function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function highlight(code) {
    const named = Array.from(code.classList).find((name) => name.startsWith("language-"));
    const name = named ? named.slice("language-".length) : "";
    const language = LANGUAGES[ALIASES[name] || name];
    if (!language) return;
    const words = new Set(language.words.split(" "));
    const text = code.textContent;
    let html = "";
    let last = 0;
    for (const match of text.matchAll(tokenizer(language))) {
      const end = match.index + match[0].length;
      const kind = match[1]
        ? "com"
        : match[2]
          ? "str"
          : match[3]
            ? "num"
            : identifierClass(match[4], text.slice(end, end + 2), language, words);
      html += escapeHtml(text.slice(last, match.index));
      html += kind ? '<span class="tok-' + kind + '">' + escapeHtml(match[0]) + "</span>" : escapeHtml(match[0]);
      last = end;
    }
    code.innerHTML = html + escapeHtml(text.slice(last));
  }

  document.querySelectorAll("pre > code[class*='language-']").forEach(highlight);
})();
