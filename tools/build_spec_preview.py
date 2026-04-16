#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_PATH = Path("specification/ai-catalog.md")
DEFAULT_CONFIG_PATH = Path("specification/respec-config.json")
DEFAULT_BUILDER_PATH = Path("tools/build_spec.py")
DIFF2HTML_VERSION = "3.4.45"


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


def build_unified_diff(base_html: str, head_html: str) -> str:
    return "".join(
        difflib.unified_diff(
            base_html.splitlines(keepends=True),
            head_html.splitlines(keepends=True),
            fromfile="a/base/index.html",
            tofile="b/head/index.html",
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
    diff_text: str,
) -> None:
    has_diff = bool(diff_text)
    diff_literal = js_string_literal(diff_text)
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
  </style>
</head>
<body>
  <header>
    <p>AI Catalog specification preview</p>
    <h1>{html.escape(title)}</h1>
    <p>
      This preview compares the rendered HTML generated from the base and head
      revisions of <code>{html.escape(DEFAULT_SOURCE_PATH.as_posix())}</code>.
    </p>
    <div class=\"links\">
      <a href=\"head/index.html\">Rendered head revision</a>
      <a href=\"base/index.html\">Rendered base revision</a>
      <a href=\"rendered.diff\">Raw rendered diff</a>
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
      <h2>Rendered HTML diff</h2>
      <p>
        The viewer below uses diff2html to show the unified diff between the
        generated base and head HTML pages.
      </p>
      {('<div id=\"diff\"></div>' if has_diff else '<p class=\"empty\">No rendered HTML differences were detected between these revisions.</p>')}
    </section>
  </main>
  <script src=\"https://cdn.jsdelivr.net/npm/diff2html@{DIFF2HTML_VERSION}/bundles/js/diff2html.min.js\"></script>
  {('<script>document.addEventListener(\"DOMContentLoaded\", function () { const diffString = ' + diff_literal + '; const diffHtml = Diff2Html.html(diffString, { drawFileList: false, matching: \"lines\", outputFormat: \"side-by-side\", renderNothingWhenEmpty: false }); document.getElementById(\"diff\").innerHTML = diffHtml; });</script>' if has_diff else '')}
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

        diff_text = build_unified_diff(base_html, head_html)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "rendered.diff").write_text(diff_text, encoding="utf-8")
        write_preview_index(
            output_dir,
            args.pr_number,
            args.base_branch,
            args.head_branch,
            args.base_sha,
            args.head_sha,
            diff_text,
        )

    print(output_dir / "index.html")


if __name__ == "__main__":
    main()