# AGENTS.md — Caboatan & Associados

Este repositório é controlado pelo Tesseract. Responda em português do Brasil.

## Regras

- O site é estático: não introduza PHP, formulário ou coleta sem backend e autorização explícita.
- O domínio definitivo aprovado é `caboataneassociados.com.br`. Preserve seu `CNAME`; mantenha `noindex` e não crie canonical, sitemap ou Search Console até a validação factual do conteúdo.
- Não invente ou atualize qualificações, registros, anos de experiência, endereço, clientes, serviços ou alegações profissionais sem fonte autorizada.
- Preserve a tag GA4 existente até a propriedade ser auditada; não copie credenciais nem identificadores privados.
- Push em `main` publica o site oficial. Exija testes, rollback e autorização explícita.
- Alterações de DNS, domínio, envio, exclusão ou hospedagem externa exigem autorização de Sidney.
- Nunca grave segredo, token, senha, `.env` ou destinatário privado.

## Validação

```powershell
python -m unittest discover -s tests -v
```
