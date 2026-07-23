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
    for name in ("FRAG", "CFRAG", "VERT", "CVERT"):
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
