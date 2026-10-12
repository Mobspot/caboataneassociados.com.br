# Changelog

## [Não publicado]

### Alterado

- domínio oficial definido como `caboataneassociados.com.br`, com caminhos da página 404 adaptados à raiz;
- documentação operacional separa disponibilidade do domínio e liberação futura da indexação;
- site convertido de PHP com includes para cinco páginas HTML estáticas compatíveis com GitHub Pages;
- navegação e recursos ajustados para o subcaminho temporário do repositório;
- dependência pública do domínio suspenso substituída pelo ativo local;
- deploy FTP automático substituído por validação contínua no GitHub.

### Adicionado

- arquivo `CNAME` versionado para associação reproduzível ao GitHub Pages;
- bloqueio temporário de indexação, página 404, skip link, foco visível, redução de movimento, documentação e testes.

### Removido

- handlers e páginas PHP, arquivos de configuração da hospedagem legada e formulário sem backend.
