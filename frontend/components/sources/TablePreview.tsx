"use client";

/**
 * Parses a (possibly truncated) markdown table snippet and renders it as
 * an actual <table>. Citation snippets are truncated to ~160 chars by the
 * backend (see app/rag/context/builder.py), so the last row may be cut
 * off — rendered as-is rather than hidden, since partial data is still
 * more useful than nothing here.
 */
function parseMarkdownTable(markdown: string): string[][] | null {
  const lines = markdown
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.startsWith("|"));

  if (lines.length < 2) return null;

  const rows = lines
    .filter((line) => !/^\|[\s-|]+\|$/.test(line)) // drop the "|---|---|" separator row
    .map((line) =>
      line
        .split("|")
        .slice(1, -1)
        .map((cell) => cell.trim())
    );

  return rows.length > 0 ? rows : null;
}

export function TablePreview({ snippet }: { snippet: string }) {
  const rows = parseMarkdownTable(snippet);

  if (!rows) {
    return <p className="text-sm text-muted">{snippet}</p>;
  }

  const [header, ...body] = rows;

  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="w-full text-left text-xs">
        <thead className="bg-surface2">
          <tr>
            {header.map((cell, i) => (
              <th key={i} className="whitespace-nowrap px-2.5 py-1.5 font-medium text-ink">
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {body.map((row, i) => (
            <tr key={i} className="border-t border-border">
              {row.map((cell, j) => (
                <td key={j} className="whitespace-nowrap px-2.5 py-1.5 text-muted">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
