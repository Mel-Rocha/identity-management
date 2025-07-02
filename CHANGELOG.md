# Changelog

Todas as mudanças importantes neste projeto serão documentadas neste arquivo.

Este changelog segue as convenções de [Keep a Changelog](https://keepachangelog.com/) e [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Ambiente
- [ ] Develop
- [ ] Main

### Adicionado
- Funcionalidades ou melhorias novas.

### Corrigido
- Bugs corrigidos nesta versão.

### Alterado
- Comportamento ou implementação de funcionalidades existentes.

### Removido
- Funcionalidades, dependências ou código obsoleto removido.

---

### Notas
> Observações importantes sobre a versão, como alertas, limitações conhecidas ou instruções pós-deploy.

---

### Mudanças em Banco de Dados
> Rastreia alterações estruturais nas tabelas do banco.

- **Data:** `AAAA-MM-DD`
- **Tabela(s):** `nome_da_tabela`
- **Alteração:** ex: coluna `status` adicionada com tipo `ENUM`
- **Contexto de decisão:** Justificativa da alteração (ex: "Foi necessário registrar status do voucher para lógica de expiração.")
- **Script:** `20250612_add_status_to_voucher.sql`

---

### Mudanças em Variáveis de Ambiente
> Rastreia o histórico de variáveis utilizadas na configuração do ambiente.

- **Data:** `AAAA-MM-DD`
- **Adicionadas:** `NOME_VARIAVEL`, `NOME_VARIAVEL2`
- **Removidas:** `VAR_ANTIGA`
- **Contexto de decisão:** Justificativa da mudança (ex: "Nova integração exige token da API externa.")

---

### Mudanças em Infraestrutura
> Rastreia alterações que envolvem recursos de infraestrutura (ex: filas, workers, serviços externos, rede, monitoramento, etc.)

- **Data:** `AAAA-MM-DD`
- **Componente(s):** `Celery`, `Redis`, `Docker`, `Load Balancer`, etc.
- **Alteração:** ex: "Celery configurado com novo backend Redis"
- **Contexto de decisão:** Justificativa da mudança (ex: "Necessário suportar maior volume de tarefas assíncronas.")
- **Detalhes adicionais (opcional):** Arquivos afetados, comandos aplicados, links para PRs ou documentos.

---

### Compatibilidade de Versão
> Garante que as integrações com outros sistemas ou clientes estejam compatíveis com esta versão.

- **Projetos que consomem esta API:**
  - `App Mobile`: Compatível a partir da versão `v1.3.0`
  - `Painel Admin`: Compatível até `v2.0.5`
  - **Motivo**: Endpoint `/vouchers` agora requer `storeId`.

- **APIs externas consumidas por este projeto:**
  - `API Pagamentos`: Requer versão `>= v3.1.0`
  - `Auth Service`: Compatível com `v2.0.0`
  - **Motivo**: Mudança na assinatura da resposta `/validate-token`.

---

## [Develop Acumulado]

> Contém alterações já mergeadas na `develop` e ainda **não promovidas para `main`**. Detalhes completos estão nos changelogs das respectivas features.

---
### Adicionado
- N/A
---

### Corrigido
- N/A
---
### Alterado
- N/A

---
### Removido
- N/A
---

### Mudanças em Banco de Dados
- N/A
---
### Mudanças em Variáveis de Ambiente
- **Data:** - N/A
- **Adicionadas:** N/A
- **Removidas:** N/A  
- **Contexto de decisão:** N/A
- 
---
### Mudanças em Infraestrutura
- **Data:** N/A
- **Componente:** N/A
- **Alteração:** N/A
- **Contexto de decisão:** N/A
---
### Compatibilidade de Versão
- **Projetos que consomem esta API:**
  - `Painel Admin`: requer atualização para v2.0.6 (uso de novo endpoint `/excel-report`)
- **APIs externas consumidas por este projeto:**
  - `Auth Service`: requer suporte ao novo campo `token_expiry` na resposta de `/validate-token`

---

## [0.0.0] - 2025-07-02

### Ambiente
- [x] Develop  
- [ ] Main

### Adicionado
- N/A

### Corrigido
- N/A
- 
### Alterado
- N/A

### Removido
- N/A

---

### Notas
> - N/A

---

### Mudanças em Banco de Dados
- **Data:** N/A  
- **Tabela:** N/A  
- **Alteração:** N/A  
- **Contexto de decisão:** N/A  
- **Script:** N/A

---

### Mudanças em Variáveis de Ambiente
- **Data:** N/A
- **Adicionadas:** N/A
- **Removidas:** N/A  
- **Contexto de decisão:** N/A

---

### Mudanças em Infraestrutura
- **Data:** N/A
- **Componente:** N/A  
- **Alteração:** N/A
- **Contexto de decisão:** N/A

---

### Compatibilidade de Versão
- **Projetos consumidores:** N/A  
- **APIs externas:** N/A
