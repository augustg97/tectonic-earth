"""Publish the field and sheet files somewhere other than the repository (WP-10, D4).

Two targets. A GitHub RELEASE, whose assets are flat files served from a CDN:

    python3 publish_assets.py --release fields-20260902          # needs gh, logged in
    python3 build_site.py --field-base https://github.com/OWNER/REPO/releases/download/fields-20260902 \\
                          --sheet-base https://github.com/OWNER/REPO/releases/download/fields-20260902

or a DIRECTORY -- another Pages repository, a bucket mount, a web root:

    python3 publish_assets.py --dir /path/to/tectonic-earth-assets
    python3 build_site.py --field-base https://OWNER.github.io/tectonic-earth-assets/fields \\
                          --sheet-base https://OWNER.github.io/tectonic-earth-assets/sheets

The manifests are copied too but the site always reads its own (they stay in
git; build_site.py copies them into docs/). The pages fetch the assets
cross-origin, so the host must answer with Access-Control-Allow-Origin: a
release's assets and GitHub Pages both do; check the browser console once.
History is a separate decision: this moves the files forward, it does not
rewrite what the repository already carries.
"""
import glob
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")


def files():
    out = sorted(glob.glob(os.path.join(WEB, "fields", "*")))
    out = [f for f in out if not f.endswith("_lite.webp")]
    sheets = os.path.join(WEB, "sheets")
    if os.path.exists(os.path.join(sheets, "manifest.json")):
        out += sorted(glob.glob(os.path.join(sheets, "*")))
    return out


def main():
    fs = files()
    if "--dir" in sys.argv:
        dst = sys.argv[sys.argv.index("--dir") + 1]
        for f in fs:
            sub = "sheets" if os.sep + "sheets" + os.sep in f else "fields"
            os.makedirs(os.path.join(dst, sub), exist_ok=True)
            shutil.copy2(f, os.path.join(dst, sub, os.path.basename(f)))
        print("copied %d files into %s/{fields,sheets}" % (len(fs), dst))
        return
    if "--release" in sys.argv:
        tag = sys.argv[sys.argv.index("--release") + 1]
        if subprocess.run(["gh", "release", "view", tag], capture_output=True).returncode != 0:
            subprocess.check_call(["gh", "release", "create", tag, "--title", tag,
                                   "--notes", "Field and sheet files for Tectonic Earth (%s)." % tag])
        # gh uploads in batches; a name clash is a re-upload
        for i in range(0, len(fs), 50):
            subprocess.check_call(["gh", "release", "upload", tag, "--clobber"] + fs[i:i + 50])
        print("uploaded %d files to release %s" % (len(fs), tag))
        return
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
