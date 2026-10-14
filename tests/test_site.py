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

    def test_domain_is_declared_and_indexing_remains_blocked(self) -> None:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertRegex(robots, r"(?im)^User-agent:\s*\*$")
        self.assertRegex(robots, r"(?im)^Disallow:\s*/$")
        self.assertFalse((ROOT / "sitemap.xml").exists())
        self.assertEqual(
            "caboataneassociados.com.br",
            (ROOT / "CNAME").read_text(encoding="utf-8").strip(),
        )
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

    def test_social_previews_use_public_banner(self) -> None:
        expected_image = "https://caboataneassociados.com.br/img/banner-1.jpg?v=20261012-2"
        expected_urls = {
            "index.html": "https://caboataneassociados.com.br/",
            "servicos.html": "https://caboataneassociados.com.br/servicos.html",
            "quemsomos.html": "https://caboataneassociados.com.br/quemsomos.html",
            "clientes.html": "https://caboataneassociados.com.br/clientes.html",
            "contato.html": "https://caboataneassociados.com.br/contato.html",
            "404.html": "https://caboataneassociados.com.br/",
        }
        self.assertTrue((ROOT / "img" / "banner-1.jpg").exists())
        for page in PAGES + [ROOT / "404.html"]:
            _, parser = parse(page)
            meta = {
                attrs.get("property") or attrs.get("name"): attrs.get("content")
                for tag, attrs in parser.attrs
                if tag == "meta" and (attrs.get("property") or attrs.get("name"))
            }
            self.assertEqual("website", meta.get("og:type"), page)
            self.assertEqual(expected_urls[page.name], meta.get("og:url"), page)
            self.assertEqual(expected_image, meta.get("og:image"), page)
            self.assertEqual(expected_image, meta.get("og:image:secure_url"), page)
            self.assertEqual("1920", meta.get("og:image:width"), page)
            self.assertEqual("1080", meta.get("og:image:height"), page)
            self.assertTrue(meta.get("og:image:alt"), page)
            self.assertEqual("summary_large_image", meta.get("twitter:card"), page)

    def test_reference_carousel_is_continuous_and_has_fallback(self) -> None:
        for name in ("index.html", "servicos.html", "quemsomos.html", "clientes.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('class="carousel reference-carousel"', text, name)
            self.assertIn('data-ride="false"', text, name)
            for image in range(1, 7):
                self.assertEqual(2, text.count(f'img/a{image}.jpg'), f"{name}: a{image}")
        css = (ROOT / "css" / "operational.css").read_text(encoding="utf-8")
        self.assertIn("@keyframes reference-scroll", css)
        self.assertIn("animation: reference-scroll 30s linear infinite", css)
        self.assertIn("animation-play-state: paused", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)

    def test_client_showcase_uses_large_images_and_unique_sections(self) -> None:
        text = (ROOT / "clientes.html").read_text(encoding="utf-8")
        _, parser = parse(ROOT / "clientes.html")
        ids = [attrs["id"] for _, attrs in parser.attrs if attrs.get("id")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn('alt="Post"', text)
        for section in ("industrias", "comercio", "servicos", "planosaude", "sorteios", "oss", "religiosas", "semlucro"):
            self.assertIn(f'id="{section}"', text)
            self.assertIn(f'href="#{section}"', text)
        css = (ROOT / "css" / "operational.css").read_text(encoding="utf-8")
        self.assertIn("grid-template-columns: minmax(30rem, 36rem) minmax(0, 1fr)", css)
        self.assertIn("min-height: 32rem", css)

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

    def test_contact_phone_and_whatsapp_are_current(self) -> None:
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            self.assertIn("tel:+5511911570039", text, page)
            self.assertIn("(11) 91157-0039", text, page)
            self.assertIn("phone=5511911570039", text, page)
            self.assertNotIn("11997329573", text, page)
            self.assertNotIn("5511997329573", text, page)
            self.assertNotIn("99732-9573", text, page)

    def test_authorized_institutional_content_and_aftal_links(self) -> None:
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        about = (ROOT / "quemsomos.html").read_text(encoding="utf-8")
        combined = home + about
        self.assertIn("mais de 30 anos", combined)
        self.assertIn("https://aftal-gsp.com/miembros-en-brasil/", home)
        self.assertIn("https://aftal-gsp.com/paises-miembros/", home)
        self.assertIn("https://aftal-gsp.com/miembros-en-brasil/", about)
        self.assertIn("https://aftal-gsp.com/paises-miembros/", about)
        self.assertNotRegex(combined, r"(?i)15\s+pa[ií]ses")
        self.assertNotIn("reginaldo.jpg", combined)
        self.assertFalse((ROOT / "img" / "reginaldo.jpg").exists())

    def test_modern_visual_layer_preserves_brand_and_responsiveness(self) -> None:
        css = (ROOT / "css" / "operational.css").read_text(encoding="utf-8")
        self.assertIn("--brand-blue: #005fa6", css)
        self.assertIn("--brand-gold: #f2a900", css)
        self.assertIn("overflow-x: hidden", css)
        self.assertIn("@media (max-width: 767px)", css)
        self.assertIn(".navbar-default .navbar-collapse.collapse.in", css)

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
