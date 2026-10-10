from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "index.html",
    ROOT / "servicos.html",
    ROOT / "quemsomos.html",
    ROOT / "clientes.html",
    ROOT / "contato.html",
]


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: list[tuple[str, dict[str, str | None]]] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.attrs.append((tag, values))
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def parse(page: Path) -> tuple[str, DocumentParser]:
    text = page.read_text(encoding="utf-8")
    parser = DocumentParser()
    parser.feed(text)
    return text, parser


class SiteTests(unittest.TestCase):
    def test_required_public_files_exist(self) -> None:
        for path in PAGES + [ROOT / "404.html", ROOT / "robots.txt", ROOT / ".nojekyll"]:
            self.assertTrue(path.exists(), path)

    def test_public_site_is_static(self) -> None:
        self.assertEqual([], list(ROOT.rglob("*.php")))
        self.assertEqual([], list(ROOT.glob(".user.ini*")))
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("<?php", text, page)
            self.assertNotRegex(text, r"\.php(?:[?#\"'])", page)
            self.assertNotIn("<form", text.lower(), page)

    def test_temporary_indexing_is_blocked(self) -> None:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertRegex(robots, r"(?im)^User-agent:\s*\*$")
        self.assertRegex(robots, r"(?im)^Disallow:\s*/$")
        self.assertFalse((ROOT / "sitemap.xml").exists())
        self.assertFalse((ROOT / "CNAME").exists())
        for page in PAGES + [ROOT / "404.html"]:
            text = page.read_text(encoding="utf-8")
            self.assertRegex(text, r'<meta name="robots" content="noindex, nofollow">')
            self.assertNotRegex(text, r"<link[^>]+rel=[\"']canonical[\"']")

    def test_metadata_is_unique_and_portuguese(self) -> None:
        titles: set[str] = set()
        descriptions: set[str] = set()
        for page in PAGES:
            _, parser = parse(page)
            html = next(attrs for tag, attrs in parser.attrs if tag == "html")
            self.assertEqual("pt-BR", html.get("lang"), page)
            title = "".join(parser.title_parts).strip()
            self.assertTrue(title, page)
            titles.add(title)
            description = next(
                attrs.get("content", "")
                for tag, attrs in parser.attrs
                if tag == "meta" and attrs.get("name") == "description"
            )
            self.assertGreaterEqual(len(description), 50, page)
            descriptions.add(description)
        self.assertEqual(len(PAGES), len(titles))
        self.assertEqual(len(PAGES), len(descriptions))

    def test_accessibility_baseline(self) -> None:
        for page in PAGES:
            text, parser = parse(page)
            self.assertIn('class="skip-link"', text, page)
            mains = [attrs for tag, attrs in parser.attrs if tag == "main"]
            self.assertEqual(1, len(mains), page)
            self.assertEqual("conteudo", mains[0].get("id"), page)
            for tag, attrs in parser.attrs:
                if tag == "img":
                    self.assertIn("alt", attrs, f"{page}: {attrs.get('src')}")
                if tag == "a" and attrs.get("target") == "_blank":
                    self.assertEqual("noopener noreferrer", attrs.get("rel"), page)

    def test_local_references_resolve(self) -> None:
        for page in PAGES:
            _, parser = parse(page)
            for tag, attrs in parser.attrs:
                name = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script"} else None
                if not name or not attrs.get(name):
                    continue
                value = attrs[name] or ""
                parsed = urlsplit(value)
                if parsed.scheme or parsed.netloc or value.startswith(("#", "mailto:", "tel:", "data:")):
                    continue
                target = unquote(parsed.path)
                if not target or target.startswith("/"):
                    continue
                self.assertTrue((page.parent / target).exists(), f"{page.name}: {value}")

    def test_legacy_domain_and_ftp_are_not_runtime_dependencies(self) -> None:
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            self.assertNotIn("www.caboataneassociados.com.br", text, page)
        workflows = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / ".github/workflows").glob("*.yml"))
        self.assertNotIn("FTP-Deploy", workflows)
        self.assertNotIn("ftp.diferencialandaimes.com.br", workflows)

    def test_ga4_legacy_tag_is_preserved_without_fake_property_data(self) -> None:
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            self.assertIn("G-ZNMTXCQML2", text, page)

    def test_no_obvious_secret_formats(self) -> None:
        patterns = [
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        ]
        for path in ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in patterns:
                self.assertIsNone(pattern.search(text), path)


if __name__ == "__main__":
    unittest.main()
