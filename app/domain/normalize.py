"""URL validation (FR4) and normalization (FR3), plus the hash used for dedup (D6).

Pure domain code: no I/O, no FastAPI, no settings import. Anything that depends on the
environment (like which hosts are ours) is passed in as an argument.
"""

from dataclasses import dataclass

MAX_URL_LENGTH = 2048


class InvalidUrlError(ValueError):
    """The URL breaks an FR4 rule. str(error) is shown to the API caller (422 detail)."""


@dataclass(frozen=True, slots=True)
class NormalizedUrl:
    url: str  # what gets stored in links.long_url and redirected to
    url_hash: bytes  # SHA-256 of `url`: exactly 32 bytes (links.url_hash CHECK)


def normalize_url(raw: str, blocked_hosts: frozenset[str]) -> NormalizedUrl:
    """Validate `raw` and return its normalized form and hash.

    `blocked_hosts` are our own hosts (e.g. {"rapid.codes", "<app>.herokuapp.com"}),
    lowercase. A short link to one of them could redirect to itself in a loop.

    Raises InvalidUrlError when a rule is broken.
    """
    # TODO(human): implement T6. What it has to do:
    #
    # FR4 validation (raise InvalidUrlError with a short, human-readable message):
    #   - at most MAX_URL_LENGTH characters. Decide: before or after normalizing?
    #     (links.long_url has CHECK (char_length(long_url) <= 2048), and that column
    #     stores the *normalized* URL.)
    #   - scheme is http or https, case-insensitive. `ftp:`, `javascript:`, `data:` fail.
    #   - a host is required (`https:///path` and `https://` fail).
    #   - the host is not in blocked_hosts. Compare after lowercasing.
    #
    # FR3 normalization:
    #   - lowercase the scheme and the host.
    #   - drop the port only when it's the default for the scheme: :80 for http,
    #     :443 for https. `https://x.com:80/` keeps its port.
    #   - keep path, query and #fragment exactly as given (case included).
    #
    # Then hash: hashlib.sha256(url.encode("utf-8")).digest() -> 32 bytes.
    #
    # Hints:
    #   - urllib.parse.urlsplit gives you scheme, netloc, path, query, fragment;
    #     .hostname is already lowercased, .port parses the port (and raises
    #     ValueError for junk like ":abc" or ":99999": catch it).
    #   - rebuild with urllib.parse.urlunsplit.
    #   - Proposed defaults, see docs/decisions.md: IDN hosts become punycode (D19),
    #     URLs with a user:password@ part are rejected (D20).
    raise NotImplementedError
