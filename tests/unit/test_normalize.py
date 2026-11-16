"""Table-driven tests for app/domain/normalize.py (T6). Target: 100% branch coverage.

Run with coverage:
    uv run pytest tests/unit/test_normalize.py --cov=app.domain.normalize --cov-branch \
        --cov-report=term-missing
"""

# TODO(human): write the tests. Suggested shape (pytest.mark.parametrize):
#
#   1. Valid URLs -> expected normalized string. Ideas from tasks.md and beyond:
#        "HTTPS://EXAMPLE.com:443/A?b=C#d"  -> scheme/host lowercased, :443 dropped,
#                                               path/query/fragment untouched
#        "http://example.com:80/"            -> :80 dropped
#        "https://example.com:80/"           -> port kept (not the default for https)
#        "http://example.com:8080/x"         -> port kept
#        IDN host, e.g. "https://bücher.de/" -> see D19
#        path, query or fragment with uppercase or %-encoding -> unchanged
#
#   2. Invalid URLs -> InvalidUrlError:
#        "ftp://example.com/", "javascript:alert(1)", "data:text/html,x"
#        "https://", "https:///path"         -> no host
#        "https://example.com/" + "a" * N    -> 2,049 chars (and a 2,048 one that passes)
#        "https://rapid.codes/x", "https://RAPID.codes/x" -> blocked host
#        "https://example.com:abc/"          -> bad port
#        "https://user:pw@example.com/"      -> see D20
#        "", "not a url"
#
#   3. Hash: 32 bytes; equal URLs after normalization -> equal hash;
#      different URLs -> different hash.
#
# Tip: pass blocked_hosts explicitly in tests, e.g.
#      BLOCKED = frozenset({"rapid.codes", "rapid-codes.herokuapp.com"})
