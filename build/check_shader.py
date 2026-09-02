"""Catch the shader traps that only show up as a black globe.

Three separate times this project has shipped -- or nearly shipped -- a
fragment shader that would not compile, and every time the symptom was the
same: the page loads, the panels and labels render, the console shows nothing
useful, and the globe is simply black. The causes were all mechanical and all
findable by reading the source:

  * a GLSL RESERVED WORD used as a variable name. "patch" cost an afternoon,
    then "flat" -- an interpolation qualifier -- cost another. The compiler
    says `'flat' : syntax error` and nothing else.
  * a BACKTICK inside a shader comment, which closes the JavaScript template
    literal early. The page then dies with a JS SyntaxError and APP never
    initialises at all.
  * a DOUBLED comment terminator, which drops the prose after the first `*/`
    into the shader as code.

None of these need a browser to detect. Run this before any shader edit ships.

    python3 check_shader.py            # exits non-zero on any problem
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "..", "web", "index.html")

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


def shader_blocks(src):
    for name in ("FRAG", "LFRAG", "CFRAG", "VERT", "CVERT"):
        m = re.search(r"\b(?:const|let|var)\s+" + name + r"\s*=\s*`", src)
        if not m:
            continue
        end = src.index("`", m.end())
        yield name, src[m.end():end], m.end()


def main():
    src = open(PAGE).read()
    bad = []
    for name, body, off in shader_blocks(src):
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
        print(f"{name}: {len(body)} chars, {body.count('{')} blocks, ok"
              if not stray and not d else f"{name}: PROBLEMS")

    # 4. a backtick anywhere between the FIRST shader's opening tick and the
    #    last one closes the template literal early. shader_blocks already
    #    stops at the first tick it finds, so a short block is the tell.
    lens = {n: len(b) for n, b, _ in shader_blocks(src)}
    if lens.get("FRAG", 0) < 8000:
        bad.append(f"FRAG is only {lens.get('FRAG')} chars -- a backtick inside "
                   f"it is closing the template literal early")

    if bad:
        print("\nPROBLEMS FOUND:")
        for b in bad:
            print("  !", b)
        return 1
    print("\nshader source clean")
    write_copies(src)
    return 0


# The plain-GLSL copies in web/shaders/ exist so the shaders can be read, diffed
# and syntax-highlighted outside the 8,000-line page. They were hand-kept and
# went stale: WP-10 found index__FRAG.frag.glsl 500 lines behind the shader
# that shipped, which is worse than no copy at all. They are now written here,
# from the same extraction the checks run on, every time the source is clean.
COPIES = {"FRAG": "index__FRAG.frag.glsl", "LFRAG": "index__LFRAG.frag.glsl", "VERT": "index__VERT.vert.glsl",
          "CFRAG": "index__CFRAG.frag.glsl", "CVERT": "index__CVERT.vert.glsl"}


def write_copies(src):
    out = os.path.join(HERE, "..", "web", "shaders")
    os.makedirs(out, exist_ok=True)
    for name, body, _ in shader_blocks(src):
        if name in COPIES:
            with open(os.path.join(out, COPIES[name]), "w") as f:
                f.write(body.strip("\n") + "\n")
    print("shader copies written to web/shaders/ (generated -- do not edit by hand)")


if __name__ == "__main__":
    sys.exit(main())
