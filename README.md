# Caboatan & Associados

Site institucional estático administrado pelo Tesseract.

## Estado atual

- URL oficial: `https://caboataneassociados.com.br/`;
- hospedagem: GitHub Pages, branch `main`, diretório `/`;
- domínio definitivo: `caboataneassociados.com.br`, aprovado por Sidney em 2026-10-12;
- indexação: bloqueada intencionalmente por `robots.txt` e meta `noindex` até a validação factual do conteúdo profissional;
- backend: inexistente; contato somente por links diretos já publicados;
- analytics: a tag legada `G-ZNMTXCQML2` foi preservada, mas acesso e titularidade ainda precisam de auditoria.

## Validação local

```powershell
python -m unittest discover -s tests -v
python -m http.server 4173
```

Abra `http://localhost:4173/`. Os caminhos públicos funcionam no domínio raiz configurado pelo `CNAME`.

## Publicação e rollback

Push em `main` publica automaticamente pelo GitHub Pages após a CI. Antes de publicar, registre o HEAD atual. Em caso de regressão, reverta por um novo commit, remova a associação do domínio no Pages se necessário e confirme home, páginas internas, recursos, `robots.txt` e 404; não reescreva o histórico.

## Gate de indexação e observabilidade

Antes de liberar indexação, confirme o responsável, valide o conteúdo profissional e então configure canonical, sitemap, Search Console, GA4/eventos e relatório semanal. O domínio e o HTTPS não eliminam esses gates.
