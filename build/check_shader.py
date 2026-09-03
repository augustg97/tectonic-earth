"""Validate the shader sources in web/shaders/ and write web/shaders.js from them.

Three separate times this project has shipped -- or nearly shipped -- a
fragment shader that would not compile, and every time the symptom was the
same: the page loads, the panels and labels render, the console shows nothing
useful, and the globe is simply black. The causes were all mechanical and all
findable by reading the source:

  * a GLSL RESERVED WORD used as a variable name. "patch" cost an afternoon,
    then "flat" -- an interpolation qualifier -- cost another. The compiler
    says `'flat' : syntax error` and nothing else.
  * a BACKTICK inside a shader comment. The shaders travel to the browser as
    JS template literals (shaders.js), so one backtick closes the literal
    early and the page dies with a JS SyntaxError.
  * a DOUBLED comment terminator, which drops the prose after the first `*/`
    into the shader as code.
  * a FUNCTION CALLED ABOVE ITS DEFINITION -- GLSL has no hoisting.

None of these need a browser to detect. Run this after any shader edit: it
is also the build step that turns web/shaders/*.glsl into web/shaders.js,
which index.html loads and build_site.py inlines (WP-10, D5).

    python3 check_shader.py            # exits non-zero on any problem

The two noise variants (VN_OLD/VN_NEW for the terrain, CN_OLD/CN_NEW for the
clouds) live in app.js and are spliced in at run time where the sources
carry the markers /*@vnoise*/ and /*@cnoise*/; the checks see the NEW ones.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
APP = os.path.join(WEB, "app.js")
SOURCES = {"FRAG": "index__FRAG.frag.glsl", "LFRAG": "index__LFRAG.frag.glsl", "VERT": "index__VERT.vert.glsl",
           "CFRAG": "index__CFRAG.frag.glsl", "CVERT": "index__CVERT.vert.glsl"}
MARKERS = {"/*@vnoise*/": "VN_NEW", "/*@cnoise*/": "CN_NEW"}

# GLSL ES 1.00/3.00 keywords and reserved-for-future-use words that are legal
# English and so plausible as variable names. Not the whole list -- the point
# is the ones a person would actually type by accident.
RESERVED = {
    "flat", "smooth", "noperspective", "patch", "sample", "shared", "buffer",
    "layout", "input", "output", "active", "common", "partition", "resource",
    "subroutine", "filter", "namespace", "using", "cast", "sizeof", "typedef",
    "template", "this", "packed", "goto", "switch", "default", "inline",
    "noinline", "volatile", "public", "static", "extern", "external",
    "interface", "long", "short", "double", "half", "fixed", "unsigned",
    "superp", "asm", "union", "enum", "row_major",
}
DECL = re.compile(r"\b(?:float|int|bool|vec2|vec3|vec4|mat2|mat3|mat4|"
                  r"ivec2|ivec3|ivec4|bvec2|bvec3|bvec4)\s+([A-Za-z_]\w*)")
# MAX_TEXTURE_IMAGE_UNITS on the hardware the site is viewed on (Apple silicon
# through ANGLE/Metal reports 16; so do most desktop GPUs; WebGL2 guarantees it).
MAX_TEXTURE_UNITS = 16


def _strip_comments(body):
    """Blank block and line comments, keeping newlines so line numbers hold."""
    code = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), body, flags=re.S)
    return re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), code)


def _js_literal(src, name):
    m = re.search(r"\bconst\s+" + name + r"\s*=\s*`", src)
    return src[m.end():src.index("`", m.end())] if m else ""


def shader_blocks(raw=False):
    """(name, body) for each shader source; the noise markers are replaced by
    the NEW variants from app.js unless raw is asked for."""
    app = open(APP).read() if os.path.exists(APP) else ""
    for name, fn in SOURCES.items():
        p = os.path.join(WEB, "shaders", fn)
        if not os.path.exists(p):
            continue
        body = open(p).read()
        if not raw:
            for mark, var in MARKERS.items():
                body = body.replace(mark, _js_literal(app, var))
        yield name, body


def main():
    bad = []
    for name, body in shader_blocks():
        # 1. reserved words as identifiers
        for m in DECL.finditer(body):
            if m.group(1) in RESERVED:
                ln = body[:m.start()].count("\n") + 1
                bad.append(f"{name} line {ln}: '{m.group(1)}' is a GLSL reserved "
                           f"word used as a variable name")
        # 2. unbalanced block comments
        d = i = stray = 0
        while i < len(body) - 1:
            if body[i:i + 2] == "/*":
                d += 1; i += 2; continue
            if body[i:i + 2] == "*/":
                d -= 1
                if d < 0:
                    ln = body[:i].count("\n") + 1
                    bad.append(f"{name} line {ln}: stray '*/' -- the prose after "
                               f"it becomes code")
                    stray += 1; d = 0
                i += 2; continue
            i += 1
        if d:
            bad.append(f"{name}: {d} unclosed block comment(s)")
        # 3. braces
        if body.count("{") != body.count("}"):
            bad.append(f"{name}: braces {body.count('{')}/{body.count('}')}")
        # duplicate variable declaration at the SAME brace depth. GLSL allows a
        # nested block (a for-loop body, an if) to shadow, so only a collision
        # at the same scope level is the "redefinition" error -- which, like the
        # others, shows only as a black globe. `valley` declared twice in the
        # main function body was one; loop counters reused in separate loops are
        # not. Track depth and only compare within a depth level; exclude
        # for-headers, whose counter lives in its own scope.
        depth = 0
        seen = [{}]
        declared_at = {}
        i = 0
        while i < len(body):
            ch = body[i]
            if ch == "{":
                depth += 1
                if len(seen) <= depth:
                    seen.append({})
                else:
                    seen[depth] = {}
            elif ch == "}":
                depth = max(0, depth - 1)
            else:
                m = DECL.match(body, i)
                # A real variable definition is followed by "=" or ";". A
                # function PARAMETER is followed by "," or ")", and a for-header
                # counter lives in its own scope -- exclude both, or every
                # `float rug` parameter collides with the body variable of the
                # same name in a different function.
                tail = body[m.end():m.end() + 1] if m else ""
                head = body[max(0, i - 5):i]
                if m and tail in "=;" and "for" not in head:
                    v = m.group(1)
                    ln = body[:i].count("\n") + 1
                    if v in seen[depth]:
                        bad.append(f"{name} line {ln}: '{v}' redeclared at the "
                                   f"same scope (first at line {seen[depth][v]})")
                    else:
                        seen[depth][v] = ln
                        declared_at.setdefault(v, ln)
            i += 1

        # 3a. A BACKTICK ANYWHERE IN THE SHADER SOURCE. The blocks are JS
        # template literals, so one backtick -- most often a variable name
        # quoted in a comment -- closes the literal early and the globe goes
        # black. The truncation shows up downstream as "unclosed block comment"
        # and a brace mismatch, which does not name the cause; say it plainly,
        # because this is the single most-repeated mistake in this file.
        for m in re.finditer("`", body):
            ln = body[:m.start()].count("\n") + 1
            ctx = body[max(0, m.start() - 46):m.start() + 14].replace("\n", " ")
            bad.append(f"{name} line {ln}: BACKTICK in shader source -- it closes "
                       f"the JS template literal. Near: ...{ctx}")

        # 3b. USE BEFORE DECLARATION. GLSL requires a variable to be declared
        # above its first use, and getting this wrong is another silent black
        # globe -- it cost a full rebuild cycle when a fracture-zone block was
        # inserted above the `rough` it depended on. Only flag names this shader
        # actually declares somewhere (so uniforms, varyings, built-ins and
        # function names are all ignored), and only when the first USE is on an
        # earlier line than the declaration.
        # Comments must be blanked first (keeping newlines so line numbers hold),
        # or every mention of a variable in the prose above it reads as a use.
        code = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                      body, flags=re.S)
        code = re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), code)
        # Scoped to main(): a name declared inside one helper and used inside
        # another is perfectly legal, so comparing across the whole block would
        # be all false positives. main() is where the long straight-line code
        # lives and where this mistake actually happens.
        mstart = code.find("void main")
        if mstart >= 0:
            mline = code[:mstart].count("\n") + 1
            for v, dln in declared_at.items():
                if dln < mline:
                    continue
                for m2 in re.finditer(rf"\b{re.escape(v)}\b", code[mstart:]):
                    uln = code[:mstart + m2.start()].count("\n") + 1
                    if uln < dln:
                        bad.append(f"{name} line {uln}: '{v}' used before it is "
                                   f"declared (declaration is at line {dln})")
                    break
        # 3c. A FUNCTION CALLED ABOVE ITS DEFINITION. GLSL has no hoisting and
        # no forward references without a prototype, and the failure is the
        # same silent black globe. basinEnv() calling vnoise3() from above the
        # injected definition cost a full render sweep.
        fdefs = {}
        for m in re.finditer(r"^(?:float|int|bool|vec[234]|mat[234]|void)\s+([A-Za-z_]\w*)\s*\(", code, flags=re.M):
            fdefs.setdefault(m.group(1), code[:m.start()].count("\n") + 1)
        for fn, dln in fdefs.items():
            if fn == "main":
                continue
            for m2 in re.finditer(rf"\b{re.escape(fn)}\s*\(", code):
                uln = code[:m2.start()].count("\n") + 1
                if uln < dln:
                    # skip the definition's own prototype-like appearance on its line
                    bad.append(f"{name} line {uln}: '{fn}()' is called above its definition (line {dln})")
                    break
        print(f"{name}: {len(body)} chars, {body.count('{')} blocks, ok"
              if not stray and not d else f"{name}: PROBLEMS")

    # 4. TEXTURE UNITS. A fragment shader gets MAX_TEXTURE_IMAGE_UNITS
    # samplers: 16 on Apple/ANGLE Metal and most desktop GL, and the WebGL2
    # minimum. The software GL the WP-10 rounds were reviewed on allows 32, so
    # a shader can link there and fail on the M1 -- "texture image units count
    # exceeds MAX_TEXTURE_IMAGE_UNITS(16)", one console line and a black globe
    # (README 7.17). Count the samplers each shader actually READS (a declared
    # sampler nothing reads is not a unit) and refuse above the real limit.
    for name, body in shader_blocks():
        code = _strip_comments(body)
        decls = re.findall(r"uniform\s+sampler2D\s+([^;]+);", code)
        names = [n.strip() for d in decls for n in d.split(",") if n.strip()]
        rest = re.sub(r"uniform\s+sampler2D\s+[^;]+;", " ", code)
        used = [n for n in names if re.search(rf"\b{re.escape(n)}\b", rest)]
        print(f"{name}: {len(used)} texture units read of {len(names)} declared (limit {MAX_TEXTURE_UNITS})")
        if len(used) > MAX_TEXTURE_UNITS:
            bad.append(f"{name}: reads {len(used)} samplers, over the {MAX_TEXTURE_UNITS} texture "
                       f"units a real GPU has -- links on software GL, black globe on the M1: "
                       f"{', '.join(used)}")

    # 5. the sources that must exist
    lens = {n: len(b) for n, b in shader_blocks()}
    for n in SOURCES:
        if n not in lens:
            bad.append(f"{n}: web/shaders/{SOURCES[n]} is missing")
    if lens.get("FRAG", 0) < 8000:
        bad.append(f"FRAG is only {lens.get('FRAG')} chars")

    if bad:
        print("\nPROBLEMS FOUND:")
        for b in bad:
            print("  !", b)
        return 1
    print("\nshader source clean")
    write_shaders_js()
    return 0


def write_shaders_js():
    """web/shaders.js: the sources as JS template literals on window.SHADERS,
    markers intact (app.js splices the noise variant it wants at run time).
    Generated -- edit web/shaders/*.glsl and run this."""
    parts = []
    for name, body in shader_blocks(raw=True):
        assert "`" not in body and "${" not in body, name
        parts.append("%s:`%s`" % (name, body))
    out = os.path.join(WEB, "shaders.js")
    with open(out, "w") as f:
        f.write("/* GENERATED by build/check_shader.py from web/shaders/*.glsl -- do not edit. */\n")
        f.write("window.SHADERS={" + ",\n".join(parts) + "};\n")
    print("web/shaders.js written (%d shaders)" % len(parts))


if __name__ == "__main__":
    sys.exit(main())
