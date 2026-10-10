# Caboatan & Associados

Site institucional estático administrado pelo Tesseract.

## Estado atual

- URL temporária: `https://mobspot.github.io/caboataneassociados.com.br/`;
- hospedagem: GitHub Pages, branch `main`, diretório `/`;
- domínio definitivo: pendente;
- indexação: bloqueada intencionalmente por `robots.txt` e meta `noindex` enquanto a URL for temporária;
- backend: inexistente; contato somente por links diretos já publicados;
- analytics: a tag legada `G-ZNMTXCQML2` foi preservada, mas acesso e titularidade ainda precisam de auditoria.

## Validação local

```powershell
python -m unittest discover -s tests -v
python -m http.server 4173
```

Abra `http://localhost:4173/`. Como os caminhos são relativos, a navegação funciona localmente e no subcaminho do GitHub Pages.

## Publicação e rollback

Push em `main` publica automaticamente pelo GitHub Pages após a CI. Antes de publicar, registre o HEAD atual. Em caso de regressão, reverta por um novo commit e confirme home, páginas internas, recursos, `robots.txt` e 404; não reescreva o histórico.

## Gate do domínio definitivo

Antes de liberar indexação, confirme domínio e responsável, valide o conteúdo profissional, configure canonical, sitemap, Search Console, GA4/eventos, relatório semanal, DNS e HTTPS. Nunca adicione `CNAME` por suposição.
