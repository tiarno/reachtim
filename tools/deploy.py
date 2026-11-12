"""Upload dist/ to Porkbun static hosting over FTPS.

Credentials come from the environment — never from this file, and never from
anything committed. The repository is public.

    export FTP_HOST=pixie-ss1-ftp.porkbun.com
    export FTP_USER=reachtim.com
    export FTP_PASS=...
    .venv/bin/python tools/deploy.py            # upload
    .venv/bin/python tools/deploy.py --prune    # also delete remote files
                                                    # that dist/ no longer has
    .venv/bin/python tools/deploy.py --dry-run  # show the plan, change nothing

Porkbun requires TLS, so this connects with FTP_TLS and turns on protection for
the data channel as well as the control channel. Their per-file limit is 40 MB.

Run tools/check_build.py first; this does not validate, it only uploads.
"""

from __future__ import annotations

import argparse
import ftplib
import hashlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MAX_FILE_BYTES = 40 * 1024 * 1024  # Porkbun static hosting limit

# What is on the server, by content hash. FTP has no checksum command on this
# host, and size alone misses same-length edits (a typo swap never uploads), so
# each deploy records the sha256 of every file it knows is on the server and the
# next deploy skips a file only when its hash matches. Kept on the server, not
# locally, so it describes the server whichever machine deploys. Public, and
# harmless: it holds hashes of files that are already public.
MANIFEST = ".deploy-manifest.json"

# Never delete these during --prune, whatever the reason they exist.
PRUNE_KEEP = {".well-known", ".ftpquota", ".htaccess", MANIFEST}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(ftp: ftplib.FTP_TLS) -> dict[str, str]:
    """The server's last recorded {path: sha256}; empty if absent or unreadable,
    which makes every file count as changed."""
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {MANIFEST}", buf.write)
        data = json.loads(buf.getvalue().decode("utf-8"))
    except (ftplib.error_perm, ValueError, UnicodeDecodeError):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def write_manifest(ftp: ftplib.FTP_TLS, manifest: dict[str, str]) -> None:
    body = json.dumps(dict(sorted(manifest.items())), indent=0).encode("utf-8")
    ftp.storbinary(f"STOR {MANIFEST}", io.BytesIO(body))


def connect() -> ftplib.FTP_TLS:
    missing = [v for v in ("FTP_HOST", "FTP_USER", "FTP_PASS") if not os.environ.get(v)]
    if missing:
        raise SystemExit(f"missing environment variable(s): {', '.join(missing)}")
    ftp = ftplib.FTP_TLS(timeout=60)
    ftp.connect(os.environ["FTP_HOST"], 21)
    ftp.login(os.environ["FTP_USER"], os.environ["FTP_PASS"])
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def local_files() -> list[Path]:
    return sorted(p for p in DIST.rglob("*") if p.is_file())


def ensure_dir(ftp: ftplib.FTP_TLS, remote_dir: str, made: set[str]) -> None:
    """mkdir -p, remembering what already exists so we don't ask twice."""
    if remote_dir in ("", ".", "/") or remote_dir in made:
        return
    parent = str(Path(remote_dir).parent).replace("\\", "/")
    if parent not in ("", ".", "/"):
        ensure_dir(ftp, parent, made)
    try:
        ftp.mkd(remote_dir)
    except ftplib.error_perm as exc:
        # 550 here means "already exists", which is fine.
        if not str(exc).startswith("550"):
            raise
    made.add(remote_dir)


def walk_remote(ftp: ftplib.FTP_TLS, path: str = "") -> tuple[set[str], set[str]]:
    """Return (files, dirs) under `path`, as remote-relative posix paths.

    Porkbun runs vsFTPd, which does not implement MLSD — it is absent from FEAT
    and returns 500. So this parses the traditional unix LIST format instead,
    where the first character of the mode column distinguishes a directory.
    """
    files: set[str] = set()
    dirs: set[str] = set()
    rows: list[str] = []
    try:
        ftp.retrlines(f"LIST {path}" if path else "LIST", rows.append)
    except (ftplib.error_perm, ftplib.error_proto):
        return files, dirs

    for row in rows:
        parts = row.split(maxsplit=8)
        if len(parts) < 9:
            continue
        mode, name = parts[0], parts[8]
        if name in (".", "..") or mode.startswith("l"):  # skip symlinks
            continue
        full = f"{path}/{name}" if path else name
        if mode.startswith("d"):
            dirs.add(full)
            sub_f, sub_d = walk_remote(ftp, full)
            files |= sub_f
            dirs |= sub_d
        else:
            files.add(full)
    return files, dirs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prune", action="store_true",
                    help="delete remote files that are not in dist/")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not DIST.is_dir():
        raise SystemExit("dist/ not built — run build.py first")

    files = local_files()
    total = sum(f.stat().st_size for f in files)
    oversized = [f for f in files if f.stat().st_size > MAX_FILE_BYTES]
    if oversized:
        for f in oversized:
            print(f"too large for this host: {f.relative_to(DIST)}", file=sys.stderr)
        raise SystemExit(1)

    print(f"dist/: {len(files)} files, {total / 1024 / 1024:.1f} MB")
    if args.dry_run:
        print("(dry run — connecting to compare only)")

    ftp = connect()
    print(f"connected: {os.environ['FTP_HOST']} as {os.environ['FTP_USER']}")

    remote_files, remote_dirs = walk_remote(ftp)
    wanted = {f.relative_to(DIST).as_posix() for f in files}
    stale = {r for r in remote_files if r not in wanted}
    stale = {r for r in stale if r.split("/")[0] not in PRUNE_KEEP}

    print(f"remote: {len(remote_files)} files, {len(stale)} not in dist/")

    # A file is current only when the server has it at the same size AND the
    # manifest says the server's copy has the same hash. Size catches a file
    # changed or truncated behind the manifest's back; the hash catches
    # same-length edits. A file the manifest does not know is uploaded.
    manifest = read_manifest(ftp)
    remote_size: dict[str, int] = {}
    for r in remote_files:
        try:
            remote_size[r] = ftp.size(r) or -1
        except ftplib.error_perm:
            remote_size[r] = -1

    todo: list[tuple[Path, str, str]] = []
    for path in files:
        rel = path.relative_to(DIST).as_posix()
        digest = sha256(path)
        if remote_size.get(rel) == path.stat().st_size and manifest.get(rel) == digest:
            continue
        todo.append((path, rel, digest))
    skipped = len(files) - len(todo)
    if not manifest:
        print(f"  no {MANIFEST} on the server yet: every file counts as changed")
    print(f"to upload: {len(todo)} changed, {skipped} current")

    if args.dry_run:
        for _, rel, _ in todo[:40]:
            print(f"  upload: {rel}")
        if len(todo) > 40:
            print(f"  ... and {len(todo) - 40} more")
        for r in sorted(stale)[:40]:
            print(f"  stale: {r}")
        if len(stale) > 40:
            print(f"  ... and {len(stale) - 40} more")
        ftp.quit()
        return 0

    made: set[str] = set()
    sent = 0
    try:
        for i, (path, rel, digest) in enumerate(todo, 1):
            parent = str(Path(rel).parent).replace("\\", "/")
            for attempt in range(1, 5):
                try:
                    ensure_dir(ftp, parent, made)
                    with path.open("rb") as fh:
                        ftp.storbinary(f"STOR {rel}", fh, blocksize=32768)
                    break
                except ftplib.all_errors as exc:  # a tuple that already includes OSError
                    if attempt == 4:
                        raise
                    print(f"  retry {attempt} for {rel}: {type(exc).__name__}")
                    # The control connection is usually dead too; rebuild both.
                    try:
                        ftp.close()
                    except Exception:
                        pass
                    ftp = connect()
                    made.clear()
            manifest[rel] = digest
            sent += path.stat().st_size
            if i % 25 == 0 or i == len(todo):
                print(f"  {i:4}/{len(todo)}  {sent / 1024 / 1024:5.1f} MB sent  {rel}")
    finally:
        # Record what is on the server even after a failed run, so a re-run
        # resends only what did not make it.
        for p in list(manifest):
            if p not in wanted and p not in remote_files:
                del manifest[p]
        try:
            write_manifest(ftp, manifest)
        except ftplib.all_errors:
            try:
                ftp = connect()
                write_manifest(ftp, manifest)
            except ftplib.all_errors as exc:
                print(f"  could not write {MANIFEST} ({type(exc).__name__}); "
                      "the next deploy will resend everything", file=sys.stderr)

    if skipped:
        print(f"  skipped {skipped} already-current file(s)")

    if args.prune and stale:
        print(f"pruning {len(stale)} stale file(s)")
        for r in sorted(stale):
            try:
                ftp.delete(r)
            except ftplib.error_perm as exc:
                print(f"  could not delete {r}: {exc}")
        # Remove directories that are now empty, deepest first.
        for d in sorted(remote_dirs, key=lambda p: p.count("/"), reverse=True):
            if d.split("/")[0] in PRUNE_KEEP:
                continue
            try:
                ftp.rmd(d)
            except ftplib.error_perm:
                pass  # not empty, or still wanted

    ftp.quit()
    print(f"uploaded {len(todo)} of {len(files)} files, {sent / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
