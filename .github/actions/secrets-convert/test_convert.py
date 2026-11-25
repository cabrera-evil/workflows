#!/usr/bin/env python3
"""Run: python3 .github/actions/secrets-convert/test_convert.py"""
import json, os, tempfile
import convert

# Infisical's exact output shape: KEY='value' joined by \n, raw values.
sample = (
    "PLAIN='abc'\n"
    "URL='postgres://u:p@h/db?x=a=b&y=1'\n"
    "QUOTED='he said \"hi\" and it\\'s fine'\n"
    "MULTI='line1\nline2\n# not a comment\nline3'\n"
    "ESCAPED='a\\nb'\n"
    "EMPTY=''\n"
    "WITH_SPACE='  padded  '"
)
d = convert.parse(sample)
assert d["PLAIN"] == "abc"
assert d["URL"] == "postgres://u:p@h/db?x=a=b&y=1"
assert d["QUOTED"] == "he said \"hi\" and it\\'s fine"
assert d["MULTI"] == "line1\nline2\n# not a comment\nline3"
assert d["ESCAPED"] == "a\\nb"          # literal backslash-n stays literal
assert d["EMPTY"] == "" and d["WITH_SPACE"] == "  padded  "
assert len(d) == 7
assert convert.parse("A='x'\n") == {"A": "x"}
for bad in ("", "garbage", "A='unterminated"):
    try:
        convert.parse(bad); raise SystemExit(f"accepted {bad!r}")
    except ValueError:
        pass

with tempfile.TemporaryDirectory() as tmp:
    for fmt, extra in (("helm-values", []), ("k8s-secret", ["--name", "api-secret"])):
        src, dst = os.path.join(tmp, "in.env"), os.path.join(tmp, "out.yaml")
        open(src, "w").write(sample)
        assert convert.main([fmt, src, dst, *extra]) == 0
        assert not os.path.exists(src) and oct(os.stat(dst).st_mode & 0o777) == "0o600"
        doc = json.load(open(dst))
        data = doc["secret"]["stringData"] if fmt == "helm-values" else doc["stringData"]
        assert data == d
        if fmt == "helm-values":
            assert doc["secret"]["enabled"] is True
        else:
            assert doc["metadata"]["name"] == "api-secret" and doc["kind"] == "Secret"
    open(src, "w").write(sample)
    assert convert.main(["k8s-secret", src, dst]) == 1 and os.path.exists(src)  # missing --name keeps input
print("ok")
