# AGENTS.md — Caboatan & Associados

Este repositório é controlado pelo Tesseract. Responda em português do Brasil.

## Regras

- O site é estático: não introduza PHP, formulário ou coleta sem backend e autorização explícita.
- A URL do GitHub Pages é temporária. Preserve `noindex` e não crie `CNAME`, canonical, sitemap ou Search Console até o domínio definitivo ser aprovado.
- Não invente ou atualize qualificações, registros, anos de experiência, endereço, clientes, serviços ou alegações profissionais sem fonte autorizada.
- Preserve a tag GA4 existente até a propriedade ser auditada; não copie credenciais nem identificadores privados.
- Push em `main` publica em produção temporária. Exija testes, rollback e autorização explícita.
- Alterações de DNS, domínio, envio, exclusão ou hospedagem externa exigem autorização de Sidney.
- Nunca grave segredo, token, senha, `.env` ou destinatário privado.

## Validação

```powershell
python -m unittest discover -s tests -v
```
