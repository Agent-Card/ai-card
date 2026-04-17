#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import html
import json
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_PATH = Path("specification/ai-catalog.md")
DEFAULT_CONFIG_PATH = Path("specification/respec-config.json")
DEFAULT_BUILDER_PATH = Path("tools/build_spec.py")
DIFF2HTML_VERSION = "3.4.45"
BLOCK_TEXT_TAGS = {
  "address",
  "article",
  "aside",
  "blockquote",
  "br",
  "caption",
  "dd",
  "div",
  "dl",
  "dt",
  "figcaption",
  "figure",
  "footer",
  "form",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "header",
  "hr",
  "li",
  "main",
  "nav",
  "ol",
  "p",
  "pre",
  "section",
  "table",
  "td",
  "th",
  "tr",
  "ul",
}
IGNORED_TEXT_TAGS = {"script", "style", "noscript", "template"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a rendered PR preview site for the AI Catalog specification."
    )
    parser.add_argument("--base-sha", required=True, help="Base revision SHA")
    parser.add_argument("--head-sha", required=True, help="Head revision SHA")
    parser.add_argument("--base-branch", required=True, help="Base branch name")
    parser.add_argument("--head-branch", required=True, help="Head branch name")
    parser.add_argument("--pr-number", required=True, type=int, help="Pull request number")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory where the preview site should be written",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root containing the git history",
    )
    parser.add_argument(
        "--source-path",
        type=Path,
        default=DEFAULT_SOURCE_PATH,
        help="Specification source path relative to the repository root",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="ReSpec configuration path relative to the repository root",
    )
    parser.add_argument(
        "--builder-path",
        type=Path,
        default=DEFAULT_BUILDER_PATH,
        help="Specification builder path relative to the repository root",
    )
    return parser.parse_args()


def run_command(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def git_show(repo_root: Path, revision: str, relative_path: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative_path.as_posix()}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Unable to read {relative_path} at {revision}: {result.stderr.strip()}"
        )
    return result.stdout


def materialize_revision_tree(
    repo_root: Path,
    revision: str,
    work_root: Path,
    source_path: Path,
    config_path: Path,
    builder_path: Path,
) -> Path:
    tree_root = work_root / revision
    for relative_path in (source_path, config_path, builder_path):
        destination = tree_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            git_show(repo_root, revision, relative_path), encoding="utf-8"
        )
    return tree_root


def build_rendered_html(
    tree_root: Path,
    source_path: Path,
    config_path: Path,
    builder_path: Path,
    output_path: Path,
) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            sys.executable,
            str(tree_root / builder_path),
            str(tree_root / source_path),
            str(output_path),
            "--config",
            str(tree_root / config_path),
        ],
        cwd=tree_root,
    )
    return output_path.read_text(encoding="utf-8")


class RenderedTextExtractor(HTMLParser):
  def __init__(self) -> None:
    super().__init__(convert_charrefs=True)
    self.body_depth = 0
    self.ignored_depth = 0
    self.parts: list[str] = []

  def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
    if tag == "body":
      self.body_depth += 1
      return

    if not self.body_depth:
      return

    if tag in IGNORED_TEXT_TAGS:
      self.ignored_depth += 1
      return

    if tag in BLOCK_TEXT_TAGS:
      self.parts.append("\n")

  def handle_endtag(self, tag: str) -> None:
    if tag == "body":
      self.body_depth = max(0, self.body_depth - 1)
      self.parts.append("\n")
      return

    if not self.body_depth:
      return

    if tag in IGNORED_TEXT_TAGS:
      self.ignored_depth = max(0, self.ignored_depth - 1)
      return

    if tag in BLOCK_TEXT_TAGS:
      self.parts.append("\n")

  def handle_data(self, data: str) -> None:
    if self.body_depth and not self.ignored_depth:
      self.parts.append(data)

  def get_text(self) -> str:
    normalized_lines: list[str] = []
    previous_blank = True
    for raw_line in "".join(self.parts).splitlines():
      line = " ".join(raw_line.split())
      if not line:
        if not previous_blank:
          normalized_lines.append("")
        previous_blank = True
        continue
      normalized_lines.append(line)
      previous_blank = False
    return "\n".join(normalized_lines).strip() + "\n"


def extract_rendered_text(rendered_html: str) -> str:
  parser = RenderedTextExtractor()
  parser.feed(rendered_html)
  parser.close()
  return parser.get_text()


def build_named_unified_diff(
  base_text: str,
  head_text: str,
  fromfile: str,
  tofile: str,
) -> str:
  return "".join(
    difflib.unified_diff(
      base_text.splitlines(keepends=True),
      head_text.splitlines(keepends=True),
      fromfile=fromfile,
      tofile=tofile,
      n=3,
    )
  )


def js_string_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def write_preview_index(
    output_dir: Path,
    pr_number: int,
    base_branch: str,
    head_branch: str,
    base_sha: str,
    head_sha: str,
    fallback_diff_text: str,
    base_html: str,
    head_html: str,
) -> None:
    has_fallback_diff = bool(fallback_diff_text)
    fallback_diff_literal = js_string_literal(fallback_diff_text)
    base_html_literal = js_string_literal(base_html)
    head_html_literal = js_string_literal(head_html)
    title = f"PR #{pr_number} Rendered Specification Diff"

    document = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html.escape(title)}</title>
  <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/diff2html@{DIFF2HTML_VERSION}/bundles/css/diff2html.min.css\">
  <style>
    :root {{
      color-scheme: light;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
    }}

    body {{
      margin: 0;
      background: #f6f8fa;
      color: #1f2328;
    }}

    header {{
      padding: 2rem 2rem 1rem;
      background: white;
      border-bottom: 1px solid #d0d7de;
    }}

    h1, h2 {{
      margin: 0 0 0.75rem;
    }}

    p {{
      line-height: 1.5;
    }}

    main {{
      padding: 1.5rem 2rem 3rem;
    }}

    .links {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-top: 1rem;
    }}

    .links a {{
      color: #0969da;
      text-decoration: none;
      font-weight: 600;
    }}

    .links a:hover {{
      text-decoration: underline;
    }}

    .panel {{
      background: white;
      border: 1px solid #d0d7de;
      border-radius: 0.75rem;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 1px 2px rgba(31, 35, 40, 0.04);
    }}

    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
      gap: 1rem;
      margin: 0;
    }}

    .meta div {{
      min-width: 0;
    }}

    .meta dt {{
      font-size: 0.875rem;
      color: #59636e;
      margin-bottom: 0.25rem;
    }}

    .meta dd {{
      margin: 0;
      font-family: ui-monospace, SFMono-Regular, SFMono-Regular, Menlo, monospace;
      word-break: break-word;
    }}

    .empty {{
      padding: 1rem;
      border-radius: 0.5rem;
      background: #f6f8fa;
      border: 1px dashed #d0d7de;
    }}

    .status {{
      padding: 0.875rem 1rem;
      border-radius: 0.5rem;
      background: #eef6ff;
      border: 1px solid #b6d4fe;
      color: #0a3069;
      margin-bottom: 1rem;
    }}

    .status[data-state=\"error\"] {{
      background: #fff8c5;
      border-color: #d4a72c;
      color: #4d2d00;
    }}

    .status[data-state=\"success\"] {{
      background: #dafbe1;
      border-color: #4ac26b;
      color: #033a16;
    }}

    .status[data-state=\"warn\"] {{
      background: #fff8c5;
      border-color: #d4a72c;
      color: #4d2d00;
    }}

    .page-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(24rem, 1fr));
      gap: 1rem;
    }}

    .page-card {{
      border: 1px solid #d0d7de;
      border-radius: 0.75rem;
      overflow: hidden;
      background: #f6f8fa;
    }}

    .page-card h3 {{
      margin: 0;
      padding: 0.875rem 1rem;
      font-size: 1rem;
      background: white;
      border-bottom: 1px solid #d0d7de;
    }}

    .page-card iframe {{
      display: block;
      width: 100%;
      height: 75vh;
      border: 0;
      background: white;
    }}

    .diff-frame {{
      width: 100%;
      min-height: 78vh;
      border: 1px solid #d0d7de;
      border-radius: 0.75rem;
      background: white;
    }}

    #diff:empty {{
      display: none;
    }}

    details {{
      margin-top: 1rem;
    }}

    summary {{
      cursor: pointer;
      font-weight: 600;
      color: #1f2328;
    }}
  </style>
</head>
<body>
  <header>
    <p>AI Catalog specification preview</p>
    <h1>{html.escape(title)}</h1>
    <p>
      This preview compares the rendered page content generated from the base and head
      revisions of <code>{html.escape(DEFAULT_SOURCE_PATH.as_posix())}</code>.
    </p>
    <div class=\"links\">
      <a href=\"head/index.html\">Rendered head revision</a>
      <a href=\"base/index.html\">Rendered base revision</a>
      <a href=\"#rendered-diff\">Rendered HTML diff view</a>
      <a href=\"rendered.diff\">Fallback text diff</a>
      <a href=\"rendered-html.diff\">Raw HTML diff</a>
    </div>
  </header>
  <main>
    <section class=\"panel\">
      <h2>Comparison metadata</h2>
      <dl class=\"meta\">
        <div>
          <dt>Pull request</dt>
          <dd>#{pr_number}</dd>
        </div>
        <div>
          <dt>Base branch</dt>
          <dd>{html.escape(base_branch)}</dd>
        </div>
        <div>
          <dt>Base revision</dt>
          <dd>{html.escape(base_sha)}</dd>
        </div>
        <div>
          <dt>Head branch</dt>
          <dd>{html.escape(head_branch)}</dd>
        </div>
        <div>
          <dt>Head revision</dt>
          <dd>{html.escape(head_sha)}</dd>
        </div>
      </dl>
    </section>
    <section class=\"panel\">
      <h2>Rendered page snapshots</h2>
      <p>
        These panes load the actual generated HTML pages for the base and head
        revisions, so reviewers can compare the rendered specification directly.
      </p>
      <div class=\"page-grid\">
        <article class=\"page-card\">
          <h3>Base revision</h3>
          <iframe id=\"base-frame\" title=\"Base revision rendered specification\" loading=\"eager\"></iframe>
        </article>
        <article class=\"page-card\">
          <h3>Head revision</h3>
          <iframe id=\"head-frame\" title=\"Head revision rendered specification\" loading=\"eager\"></iframe>
        </article>
      </div>
    </section>
    <section class=\"panel\">
      <h2>Rendered page diff</h2>
      <p>
        This view renders a diff of the final browser DOM using the page's own
        HTML structure and styles, so the result stays close to the actual
        final specification format instead of a line-oriented patch.
      </p>
      <div id=\"diff-status\" class=\"status\" data-state=\"loading\">Loading browser-rendered page snapshots and computing diff...</div>
      <iframe id=\"rendered-diff\" class=\"diff-frame\" title=\"Rendered specification diff\" loading=\"eager\"></iframe>
      <details id=\"fallback-details\">
        <summary>Exact text diff for debugging</summary>
        <div id=\"diff\"></div>
      </details>
      <p id=\"diff-empty\" class=\"empty\" hidden>No rendered page-content differences were detected between these revisions.</p>
    </section>
  </main>
  <script type=\"module\">
    import HtmlDiff from \"https://cdn.jsdelivr.net/npm/htmldiff-js@1.0.5/+esm\";

    window.HtmlDiffModule = HtmlDiff && HtmlDiff.default ? HtmlDiff.default : HtmlDiff;
  </script>
  <script src=\"https://cdn.jsdelivr.net/npm/diff@7.0.0/dist/diff.min.js\"></script>
  <script src=\"https://cdn.jsdelivr.net/npm/diff2html@{DIFF2HTML_VERSION}/bundles/js/diff2html.min.js\"></script>
  <script>
    document.addEventListener(\"DOMContentLoaded\", function () {{
      const baseHtml = {base_html_literal};
      const headHtml = {head_html_literal};
      const fallbackDiffString = {fallback_diff_literal};
      const hasFallbackDiff = {str(has_fallback_diff).lower()};
      const baseFrame = document.getElementById(\"base-frame\");
      const headFrame = document.getElementById(\"head-frame\");
      const renderedDiffFrame = document.getElementById(\"rendered-diff\");
      const fallbackDetails = document.getElementById(\"fallback-details\");
      const diffContainer = document.getElementById(\"diff\");
      const diffStatus = document.getElementById(\"diff-status\");
      const diffEmpty = document.getElementById(\"diff-empty\");

      function waitForLoad(frame, htmlSource) {{
        return new Promise((resolve, reject) => {{
          const timeout = window.setTimeout(() => reject(new Error(\"Timed out waiting for preview frame to load\")), 45000);
          frame.addEventListener(\"load\", function onLoad() {{
            window.clearTimeout(timeout);
            resolve(frame);
          }}, {{ once: true }});
          frame.srcdoc = htmlSource;
        }});
      }}

      async function waitForRenderedDocument(frame, htmlSource) {{
        const loadedFrame = await waitForLoad(frame, htmlSource);
        const frameWindow = loadedFrame.contentWindow;
        const frameDocument = frameWindow && frameWindow.document;
        if (!frameDocument) {{
          throw new Error(\"Preview frame did not expose a document\");
        }}
        if (frameDocument.respec && frameDocument.respec.ready) {{
          await frameDocument.respec.ready;
        }}
        await new Promise((resolve) => frameWindow.requestAnimationFrame(() => resolve()));
        await new Promise((resolve) => frameWindow.requestAnimationFrame(() => resolve()));
        return frameDocument;
      }}

      function normalizeRenderedText(text) {{
        const normalizedLines = [];
        let previousBlank = true;
        for (const rawLine of text.replace(/\\r\\n/g, \"\\n\").split(\"\\n\")) {{
          const line = rawLine.replace(/\\s+/g, \" \" ).trim();
          if (!line) {{
            if (!previousBlank) {{
              normalizedLines.push(\"\");
            }}
            previousBlank = true;
            continue;
          }}
          normalizedLines.push(line);
          previousBlank = false;
        }}
        return normalizedLines.join(\"\\n\").trim() + \"\\n\";
      }}

      function getVisibleText(frameDocument) {{
        const source = frameDocument.body && typeof frameDocument.body.innerText === \"string\"
          ? frameDocument.body.innerText
          : frameDocument.documentElement && typeof frameDocument.documentElement.innerText === \"string\"
            ? frameDocument.documentElement.innerText
            : \"\";
        return normalizeRenderedText(source);
      }}

      function renderFallbackDiff(diffString) {{
        if (!diffString) {{
          diffContainer.innerHTML = \"\";
          return;
        }}
        diffContainer.innerHTML = Diff2Html.html(diffString, {{
          drawFileList: false,
          matching: \"lines\",
          outputFormat: \"side-by-side\",
          renderNothingWhenEmpty: false,
        }});
      }}

      function getDiffHeadMarkup(frameDocument) {{
        return Array.from(frameDocument.head.children)
          .filter((element) => element.tagName !== \"SCRIPT\")
          .map((element) => element.outerHTML)
          .join(\"\\n\");
      }}

      function buildRenderedDiffDocument(headMarkup, diffBodyMarkup) {{
        return `<!DOCTYPE html>
<html lang=\"en\">
<head>
${{headMarkup}}
<style>
  body {{
    padding: 0 1.5rem 3rem;
    box-sizing: border-box;
  }}

  ins.diffins {{
    background: #dafbe1;
    color: inherit;
    text-decoration: none;
    box-shadow: inset 0 -0.35em 0 rgba(74, 194, 107, 0.28);
  }}

  del.diffdel {{
    background: #ffebe9;
    color: #82071e;
    text-decoration: line-through;
    box-shadow: inset 0 -0.35em 0 rgba(248, 81, 73, 0.22);
  }}

  .diff-hint {{
    margin: 1rem 0 1.5rem;
    padding: 0.875rem 1rem;
    border: 1px solid #d0d7de;
    border-radius: 0.75rem;
    background: #f6f8fa;
    font: 600 0.95rem/1.4 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
    color: #1f2328;
  }}
</style>
</head>
<body>
  <div class=\"diff-hint\">Inserted content is highlighted in green and removed content in red, while the page keeps the rendered specification layout.</div>
  ${{diffBodyMarkup}}
</body>
</html>`;
      }}

      function renderRenderedDiffDocument(frameDocument, diffBodyMarkup) {{
        renderedDiffFrame.srcdoc = buildRenderedDiffDocument(getDiffHeadMarkup(frameDocument), diffBodyMarkup);
      }}

      Promise.all([
        waitForRenderedDocument(baseFrame, baseHtml),
        waitForRenderedDocument(headFrame, headHtml),
      ]).then(([baseDocument, headDocument]) => {{
        const htmlDiffModule = window.HtmlDiffModule;
        if (!htmlDiffModule || typeof htmlDiffModule.execute !== \"function\") {{
          throw new Error(\"Rendered HTML diff module did not load\");
        }}

        const baseText = getVisibleText(baseDocument);
        const headText = getVisibleText(headDocument);
        const hasRenderedChanges = baseText !== headText;
        if (!hasRenderedChanges) {{
          renderedDiffFrame.hidden = true;
          fallbackDetails.hidden = true;
          diffEmpty.hidden = false;
          diffStatus.textContent = \"No browser-rendered content differences were detected between these revisions.\";
          diffStatus.dataset.state = \"success\";
          return;
        }}

        const renderedBodyDiff = htmlDiffModule.execute(
          baseDocument.body ? baseDocument.body.innerHTML : \"\",
          headDocument.body ? headDocument.body.innerHTML : \"\",
        );
        renderRenderedDiffDocument(headDocument, renderedBodyDiff);

        const diffString = Diff.createTwoFilesPatch(
          \"a/base/rendered.txt\",
          \"b/head/rendered.txt\",
          baseText,
          headText,
          \"\",
          \"\",
          {{ context: 3 }}
        );
        renderFallbackDiff(diffString);
        diffStatus.textContent = \"Rendered diff view computed from the final browser DOM. Open the debug section below only if you need the exact text patch.\";
        diffStatus.dataset.state = \"warn\";
      }}).catch((error) => {{
        renderedDiffFrame.hidden = true;
        if (hasFallbackDiff) {{
          fallbackDetails.open = true;
          renderFallbackDiff(fallbackDiffString);
          diffStatus.textContent = \"Fell back to the static text diff because rendered HTML diff generation failed: \" + error.message;
          diffStatus.dataset.state = \"error\";
          return;
        }}
        fallbackDetails.hidden = true;
        diffStatus.textContent = \"Unable to compute the rendered diff: \" + error.message;
        diffStatus.dataset.state = \"error\";
        diffEmpty.hidden = false;
      }});
    }});
  </script>
</body>
</html>
"""

    (output_dir / "index.html").write_text(document, encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()

    with tempfile.TemporaryDirectory(prefix="spec-preview-") as temp_dir:
        work_root = Path(temp_dir)
        base_tree = materialize_revision_tree(
            repo_root,
            args.base_sha,
            work_root,
            args.source_path,
            args.config_path,
            args.builder_path,
        )
        head_tree = materialize_revision_tree(
            repo_root,
            args.head_sha,
            work_root,
            args.source_path,
            args.config_path,
            args.builder_path,
        )

        base_html = build_rendered_html(
            base_tree,
            args.source_path,
            args.config_path,
            args.builder_path,
            output_dir / "base/index.html",
        )
        head_html = build_rendered_html(
            head_tree,
            args.source_path,
            args.config_path,
            args.builder_path,
            output_dir / "head/index.html",
        )

        base_text = extract_rendered_text(base_html)
        head_text = extract_rendered_text(head_html)
        diff_text = build_named_unified_diff(
          base_text,
          head_text,
          "a/base/rendered.txt",
          "b/head/rendered.txt",
        )
        html_diff = build_named_unified_diff(
          base_html,
          head_html,
          "a/base/index.html",
          "b/head/index.html",
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "rendered.diff").write_text(diff_text, encoding="utf-8")
        (output_dir / "rendered-html.diff").write_text(html_diff, encoding="utf-8")
        write_preview_index(
            output_dir,
            args.pr_number,
            args.base_branch,
            args.head_branch,
            args.base_sha,
            args.head_sha,
            diff_text,
          base_html,
          head_html,
        )

    print(output_dir / "index.html")


if __name__ == "__main__":
    main()