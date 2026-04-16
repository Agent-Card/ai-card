#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PAGES_BRANCH = "gh-pages"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the gh-pages branch with canonical or PR preview content."
    )
    parser.add_argument("mode", choices=("root", "preview", "cleanup"))
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root that has the authenticated origin remote",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Directory to publish into gh-pages",
    )
    parser.add_argument(
        "--remote-url",
        help="Authenticated remote URL to use for pushing gh-pages updates",
    )
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument(
        "--commit-message",
        required=True,
        help="Commit message for the gh-pages update",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Maximum push attempts before failing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apply the changes locally without committing or pushing",
    )
    return parser.parse_args()


def run_command(
    command: list[str],
    cwd: Path,
    *,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True,
    )


def remote_branch_exists(repo_root: Path) -> bool:
    result = run_command(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", PAGES_BRANCH],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    return result.returncode == 0


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def copy_tree_contents(source_dir: Path, destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for child in source_dir.iterdir():
        target = destination_dir / child.name
        if child.is_dir():
            shutil.copytree(child, target)
            continue
        shutil.copy2(child, target)


def clear_root(checkout_dir: Path, preserve_names: set[str]) -> None:
    for child in checkout_dir.iterdir():
        if child.name == ".git" or child.name in preserve_names:
            continue
        remove_path(child)


def stage_root_publish(checkout_dir: Path, source_dir: Path) -> None:
    clear_root(checkout_dir, {"pr"})
    copy_tree_contents(source_dir, checkout_dir)
    (checkout_dir / ".nojekyll").touch()


def stage_preview_publish(checkout_dir: Path, source_dir: Path, pr_number: int) -> None:
    preview_dir = checkout_dir / "pr" / str(pr_number)
    remove_path(preview_dir)
    preview_dir.mkdir(parents=True, exist_ok=True)
    copy_tree_contents(source_dir, preview_dir)
    (checkout_dir / ".nojekyll").touch()


def stage_preview_cleanup(checkout_dir: Path, pr_number: int) -> None:
    preview_dir = checkout_dir / "pr" / str(pr_number)
    remove_path(preview_dir)
    pr_root = checkout_dir / "pr"
    if pr_root.exists() and not any(pr_root.iterdir()):
        pr_root.rmdir()


def has_staged_changes(checkout_dir: Path) -> bool:
    result = run_command(
        ["git", "diff", "--cached", "--quiet"],
        cwd=checkout_dir,
        check=False,
    )
    return result.returncode != 0


def prepare_checkout(
    repo_root: Path,
    checkout_dir: Path,
    branch_exists: bool,
    remote_url: str | None,
) -> None:
    if not remote_url:
        remote_url = run_command(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_root,
            capture_output=True,
        ).stdout.strip()

    run_command(["git", "init"], cwd=checkout_dir)
    run_command(["git", "remote", "add", "origin", remote_url], cwd=checkout_dir)
    run_command(
        [
            "git",
            "config",
            "user.name",
            os.getenv("GIT_AUTHOR_NAME", "github-actions[bot]"),
        ],
        cwd=checkout_dir,
    )
    run_command(
        [
            "git",
            "config",
            "user.email",
            os.getenv(
                "GIT_AUTHOR_EMAIL", "41898282+github-actions[bot]@users.noreply.github.com"
            ),
        ],
        cwd=checkout_dir,
    )

    if branch_exists:
        run_command(["git", "fetch", "--depth", "1", "origin", PAGES_BRANCH], cwd=checkout_dir)
        run_command(["git", "checkout", "-B", PAGES_BRANCH, "FETCH_HEAD"], cwd=checkout_dir)
        return

    run_command(["git", "checkout", "--orphan", PAGES_BRANCH], cwd=checkout_dir)


def apply_mode(args: argparse.Namespace, checkout_dir: Path) -> None:
    if args.mode == "root":
        stage_root_publish(checkout_dir, args.source_dir.resolve())
        return
    if args.mode == "preview":
        stage_preview_publish(checkout_dir, args.source_dir.resolve(), args.pr_number)
        return
    stage_preview_cleanup(checkout_dir, args.pr_number)


def publish_once(args: argparse.Namespace, branch_exists: bool) -> bool:
    with tempfile.TemporaryDirectory(prefix="gh-pages-") as temp_dir:
        checkout_dir = Path(temp_dir)
        prepare_checkout(
            args.repo_root.resolve(),
            checkout_dir,
            branch_exists,
            args.remote_url,
        )
        apply_mode(args, checkout_dir)
        run_command(["git", "add", "-A"], cwd=checkout_dir)

        if not has_staged_changes(checkout_dir):
            print("No gh-pages changes to publish.")
            return True

        if args.dry_run:
            print("Dry run: gh-pages changes staged successfully.")
            return True

        run_command(["git", "commit", "-m", args.commit_message], cwd=checkout_dir)
        push_result = run_command(
            ["git", "push", "origin", PAGES_BRANCH],
            cwd=checkout_dir,
            check=False,
        )
        return push_result.returncode == 0


def validate_args(args: argparse.Namespace) -> None:
    if args.mode in {"root", "preview"} and not args.source_dir:
        raise SystemExit("--source-dir is required for root and preview modes")
    if args.mode in {"preview", "cleanup"} and args.pr_number is None:
        raise SystemExit("--pr-number is required for preview and cleanup modes")


def main() -> None:
    args = parse_args()
    validate_args(args)

    branch_exists = remote_branch_exists(args.repo_root.resolve())
    if args.mode == "cleanup" and not branch_exists:
        print("gh-pages branch does not exist; nothing to clean up.")
        return

    for attempt in range(1, args.max_attempts + 1):
        if publish_once(args, branch_exists):
            return
        branch_exists = True
        print(f"Retrying gh-pages push ({attempt}/{args.max_attempts})...")

    raise SystemExit("Failed to update the gh-pages branch after multiple attempts")


if __name__ == "__main__":
    main()