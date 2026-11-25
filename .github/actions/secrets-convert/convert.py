#!/usr/bin/env python3
"""Convert an Infisical dotenv export to Helm values or a Kubernetes Secret manifest.

Infisical's `export-type: file` (secrets-action v1.0.18) writes `KEY='value'` joined by
newlines. Values are raw: no escaping, and they may span lines or contain quotes.
A new entry therefore starts only at `KEY='` at the beginning of the file or right after
a `'` + newline. ponytail: a value containing `'` + newline + `OTHER='` would be split.
"""
import argparse
import json
import os
import re
import sys

ENTRY = re.compile(r"(?:\A|(?<='\n))([^\s='#]+)='")


def parse(text):
    text = text.removesuffix("\n")  # Infisical writes none; tolerate one
    marks = list(ENTRY.finditer(text))
    if not marks or marks[0].start() != 0:
        raise ValueError("unrecognised Infisical export format")
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() - 1 if i + 1 < len(marks) else len(text)  # drop "\n" separator
        chunk = text[m.end():end]
        if not chunk.endswith("'"):
            raise ValueError(f"unterminated value for {m.group(1)}")
        out[m.group(1)] = chunk[:-1]
    return out


def render(fmt, data, name, helm_key):
    if fmt == "helm-values":
        return {helm_key: {"enabled": True, "stringData": data}}
    if fmt == "k8s-secret":
        if not name:
            raise ValueError("k8s-secret needs --name")
        return {"apiVersion": "v1", "kind": "Secret", "metadata": {"name": name},
                "type": "Opaque", "stringData": data}
    raise ValueError(f"unknown format {fmt!r}")


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("format")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--name", default="")
    p.add_argument("--helm-key", default="secret")
    a = p.parse_args(argv)
    try:
        with open(a.input, encoding="utf-8") as f:
            text = f.read()
        data = parse(text)
        doc = render(a.format, data, a.name, a.helm_key)
    except (OSError, ValueError) as e:
        print(f"::error title=secrets-convert::{e}")
        return 1
    fd = os.open(a.output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(doc, f)
    os.remove(a.input)
    print(f"Converted {len(data)} secrets to {a.format}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
