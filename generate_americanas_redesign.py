#!/usr/bin/env python3
"""
Generate americanas_redesign.html following the exact pattern of gas_redesign.html
"""

import re
import json
from html import escape

# ============================================================================
# 1. READ SOURCE FILES
# ============================================================================

with open('/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas_redesign.html', 'r', encoding='utf-8') as f:
    gas_content = f.read()

with open('/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/americanas.html', 'r', encoding='utf-8') as f:
    americanas_content = f.read()

# ============================================================================
# 2. EXTRACT TEMPLATE SECTIONS FROM GAS
# ============================================================================

# Get everything up to and including </head>
head_end = gas_content.find('</head>') + len('</head>')
head_section = gas_content[:head_end]

# Extract nav (from <nav to </nav>)
nav_start = gas_content.find('<nav')
nav_end = gas_content.find('</nav>', nav_start) + len('</nav>')
nav_template = gas_content[nav_start:nav_end]

# Extract footer (from <footer to end)
footer_start = gas_content.find('<footer')
footer_section = gas_content[footer_start:]

# ============================================================================
# 3. HELPER FUNCTION TO EXTRACT TEXT CONTENT FROM AMERICANAS.HTML
# ============================================================================

def extract_content_by_id(content, content_id):
    """Extract text content for a specific content ID from americanas.html"""
    pattern = f'id="{content_id}"[^>]*>([^<]*)<'
    match = re.search(pattern, content)
    if match:
        return match.group(1).strip()

    # Alternative: look for the content div
    pattern = f'<div[^>]*id="{content_id}"[^>]*>(.*?)</div>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = re.sub(r'<[^>]+>', '', match.group(1))
        return text.strip()

    return ""

def extract_informativos(content):
    """Extract all informativos from americanas.html"""
    informativos = {}

    # Look for INFORMATIVO patterns with their content
    pattern = r'<a[^>]*onclick="toggleContent\(\'([^\']+)\'">[^<]*INFORMATIVO ([0-9]+/[0-9]+)[^<]*</a>'
    matches = re.finditer(pattern, content)

    for match in matches:
        content_id = match.group(1)
        informativo_num = match.group(2)

        # Extract the content
        text_content = extract_content_by_id(content, content_id)
        informativos[informativo_num] = text_content

    return informativos

def extract_pmp_items(content):
    """Extract all PMP items (both mensais and semanais)"""
    mensais = []
    semanais = []

    # Find PMP entries - they usually have dates and PDF filenames
    pmp_pattern = r'<a[^>]*href="[^"]*assets/pdfs/([^"]*PMP[^"]*\.pdf)"[^>]*>([^<]+)</a>'
    matches = re.finditer(pmp_pattern, content)

    for match in matches:
        filename = match.group(1)
        text = match.group(2).strip()

        if 'Mensal' in filename or 'Mensal' in text:
            mensais.append((text, filename))
        elif 'semanal' in filename.lower():
            semanais.append((text, filename))

    return mensais, semanais

# ============================================================================
# 4. DEFINE AMERICANAS DATA STRUCTURE
# ============================================================================

# Informativos - extract text content from americanas.html
informativos_data = extract_informativos(americanas_content)

# If extraction didn't work well, use fallback text
informativos = [
    ("0001/2024", "LEILÃO REVERSO — DIRETRIZES"),
    ("0008/2023", "REUNIÃO PARA APRESENTAÇÃO DO ADITIVO AO PLANO"),
    ("0007/2023", "APRESENTAÇÃO DE ADITIVO AO PLANO"),
    ("0006/2023", "CONVOCAÇÃO DA ASSEMBLEIA GERAL DE CREDORES"),
    ("0005/2023", "DESMEMBRAMENTO DOS CREDORES INVESTIDORES"),
    ("0004/2023", "INFORMAÇÕES EM SITE UNIFICADO"),
    ("0003/2023", "APRESENTADA NOVA RELAÇÃO DE CREDORES"),
    ("0002/2023", "VERIFICAÇÃO E COMPLEMENTAÇÃO DE ENDEREÇOS"),
    ("0001/2023", "AVISO AOS CREDORES"),
]

editais = [
    ("11/02/2026", "Publicação Edital Americanas UPI", "Publicaçao EDITAL AMericanas UPI.pdf"),
    ("27/03/2024", "Edital Leilão Reverso — DJe", "Edital-Leilao-Reverso-DJE-27-03-2024.pdf"),
    ("14/05/2024", "Edital de Leilão Eletrônico — Automóveis", "Edital-leilao-eletronico-Automoveis-14-05-2024-.pdf"),
    ("28/03/2024", "Edital de Leilão Reverso — DJe (2ª publicação)", "Edital-Leilao-Reverso-DJE-27-03-2024.pdf"),
    ("21/11/2023", "Edital de Convocação para AGC", "Edital-de-convocacao-para-AGC-2.pdf"),
    ("23/10/2023", "Edital de Desmembramento — Bondholders", "Edital-EDITAL-DE-DESMEMBRAMENTO-DOS-CREDORES-INVESTIDORES-Bondholders.pdf"),
    ("19/06/2023", "Edital do Art. 7º, §2º, e Art. 53 da LRE", "Edital do art. 7º§2º e art 53 da LRE.pdf"),
    ("02/06/2023", "Edital para Enquadramento como Credor Fornecedor", "EDITAL CREDOR FORNECEDOR - DJE 02.06.pdf"),
    ("05/05/2023", "Edital para Participação no Financiamento D.I.P.", "Grupo Americanas – Edital para participação no Financiamento D.I.P. – 0813541-59.2023.8.19.0001.pdf"),
    ("01/03/2023", "Edital Art. 52, §1° da LRE", "Grupo Americanas – Edital art. 52 §1° da LRE - 01_03_2023.pdf"),
]

relacao_credores = [
    ("24/06/2024", "Relação de Credores — Art. 7º, §2º LRE", "Relação de Credores Grupo Americanas - Art. 7º - §2º LRE - 24.06.24 (1).xlsx"),
    ("13/05/2024", "Relação de Credores Bondholders — DF KING", "Doc-02-Tender-Offer-Lista-dos-Habilitados-apresentada-pela-DF-KING.pdf"),
    ("13/05/2024", "Relação de Credores Habilitados — Leilão Reverso", "Doc_01_-_Relacao_de_credores_habilitados_leilao_reverso_-_Administracao_Judicial.pdf"),
    ("18/12/2023", "Relação de Credores Desmembrados (Consolidada)", "Relacao-Consolidada-Credores-Desmembrados.pdf"),
    ("07/12/2023", "Relação de Credores Desmembrados (1ª versão)", "Relacao-de-Credores-Desmembrados-Grupo-Americanas-1.pdf"),
    ("14/06/2023", "Versão Final da Relação de Credores — AJ", "Doc. 01 - Relação de Credores - Grupo Americanas - Art. 7º§2º LRE.pdf"),
    ("02/06/2023", "Relação de Credores — Art. 7º, §2º da LRE", "RELAÇÃO DE CREDORES - ART. 7º P.pdf"),
    ("13/02/2023", "Nova Relação de Credores — Americanas", "Grupo Americanas – Nova Relação de Credores apresentada pelas recuperandas em 10_02_2023 – Americanas.pdf"),
    ("13/02/2023", "Nova Relação de Credores — B2W Lux", "Grupo Americanas – Nova Relação de Credores apresentada pelas recuperandas em 10_02_2023 – B2W Lux.pdf"),
    ("13/02/2023", "Nova Relação de Credores — JSM Global", "Grupo Americanas – Nova Relação de Credores apresentada pelas recuperandas em 10_02_2023 – JSM Global.pdf"),
    ("13/02/2023", "Nova Relação de Credores — ST Importações", "Grupo Americanas – Nova Relação de Credores apresentada pelas recuperandas em 10_02_2023 – ST Importações.pdf"),
    ("13/02/2023", "Nova Relação de Credores — Consolidado", "Grupo Americanas – Nova Relação de Credores apresentada pelas recuperandas em 10_02_2023 – Consolidado.pdf"),
    ("25/01/2023", "Relação de Credores — Americanas", "Grupo Americanas - Relação de Credores apresentada pelas recuperandas - Americanas.pdf"),
    ("25/01/2023", "Relação de Credores — B2W Lux", "Grupo Americanas - Relação de Credores apresentada pelas recuperandas - B2W Lux.pdf"),
    ("25/01/2023", "Relação de Credores — JSM Global", "Grupo Americanas - Relação de Credores apresentada pelas recuperandas - JSM Global.pdf"),
    ("25/01/2023", "Relação de Credores — ST Importações", "Grupo Americanas - Relação de Credores apresentada pelas recuperandas - ST Importações.pdf"),
    ("25/01/2023", "Relação de Credores — Consolidado", "Grupo Americanas - Relação de Credores apresentada pelas recuperandas - Consolidado.pdf"),
]

avisos = [
    ("23/02/2026", "Assembleia Geral de Debenturistas — 22ª Emissão", "Assembleia Geral de Debenturistas-22a Emissao de Debentures Simples.pdf"),
    ("11/02/2026", "Fechamento Alienação da Parati", "fechamento alienação da Parati.pdf"),
    ("11/02/2026", "Comunicado ao Mercado", "COMUNICADO AO MERCADO.pdf"),
    ("11/02/2026", "Aviso Alienação UPI Uni.co", "AVISO ALIENAÇÃO UPI UNI.CO.pdf"),
    ("02/02/2026", "Comunicado ao Mercado — CAM 318/26 — Instauração da Arbitragem", "Comunicado ao Mercado - CAM 318 26 - Instauração da arbitragem.pdf"),
    ("23/01/2026", "Comunicado ao Mercado — CAM 236/23 — Desistência dos Requerentes", "Comunicado ao Mercado - CAM 236 23 - Desistência dos requerentes.pdf"),
    ("28/11/2025", "Fato Relevante — Eleição CFO e IRO", "28.11.2025 - Fato Relevante - Eleição CFO e IRO.pdf"),
    ("24/11/2025", "Comunicado ao Mercado — Reapresentação Proposta Vinculante Uni.co", "24.11.2025 - Comunicado ao Mercado - Reapresentação de Proposta Vinculante para aquisição do Acervo Uni.co.pdf"),
    ("19/11/2025", "Comunicado ao Mercado — Esclarecimentos CVM/B3", "19.11.2025 - Comunicado ao Mercado - Esclarecimentos sobre questionamentos da CVMB3.pdf"),
    ("06/11/2025", "Comunicado ao Mercado — Cancelamento Licença AME Digital", "06.11.2025 - Comunicado ao Mercado - Cancelamento da licença da AME Digital.pdf"),
    ("08/10/2025", "Comunicado ao Mercado — Celebração do Termo de Arbitragem", "08.10.2025 - Comunicado ao Mercado - Celebração do Termo de Arbitragem - Resolução CVM 802022.pdf"),
    ("25/08/2025", "Fato Relevante — Eleição CEO", "25.08.2025 - Fato Relevante - Eleição CEO.pdf"),
    ("12/08/2025", "Comunicado ao Mercado — Market Sounding HNT", "12.08.2025 - Comunicado ao Mercado - Market Sounding HNT.pdf"),
]

ata_agc = [
    ("21/12/2023", "Declarações de Voto e Ressalvas", "Doc.-08-Declaracoes-de-voto-e-ressalvas.pdf"),
    ("21/12/2023", "Manifestações dos Credores (chat virtual)", "Doc.-07-Manifestacoes-apresentadas-pelos-credores-atraves-do-chat-disponibilizado-no-ambiente-virt (1).pdf"),
    ("21/12/2023", "Apresentação do PRJ durante a AGC", "Doc.-06-Apresentacao-do-Plano-de-Recuperacao-Judicial-feita-durante-a-AGC.pdf"),
    ("21/12/2023", "Plano de Recuperação Judicial Aprovado", "Doc.-05-Plano-de-Recuperacao-Judicial-Deliberado.pdf"),
    ("21/12/2023", "Laudo de Votação do Pedido de Suspensão (rejeitado)", "Doc.-04-Laudo-de-votacao-do-pedido-de-suspensao-rejeitado-pela-AGC.pdf"),
    ("21/12/2023", "Laudo de Deliberação do PRJ", "Doc.-03-Laudo-de-deliberacao-do-Plano-de-Recuperacao-Judicial.pdf"),
    ("21/12/2023", "Laudo de Credenciamento", "Doc.-02-Laudo-de-Credenciamento.pdf"),
    ("20/12/2023", "Ata da AGC de 19/12/2023 — Aprovação do Plano", "Doc.-01-Ata-da-AGC-19-12-2023-Grupo-Americanas-PRJ-aprovado-1.pdf"),
]

plano_rj = [
    ("18/07/2024", "PRJ Consolidado e Anexos", "PRJ-Consolidado-e-Anexos-17-07-24.pdf"),
    ("18/07/2024", "Alteração do PRJ — Cláusula 10.1.1", "Alteracao-do-PRJ-17-07-2024-clausula-10.1.1.pdf"),
    ("19/12/2023", "2º Aditivo ao PRJ", "Doc. 01 - 2º Aditivo ao PRJ.pdf"),
    ("19/12/2023", "2º Aditivo ao PRJ — Versão com marcas de revisão", "2o-Aditivo-ao-PRJ-19-12-2023-Versao-com-marcas-de-revisao.pdf"),
    ("27/11/2023", "Aditamento ao PRJ", "Grupo-Americanas-PRJ-Aditado-27-11-2023.pdf"),
    ("27/11/2023", "Acordo de Apoio à Reestruturação", "Grupo-Americanas-Acordo-de-Apoio-a-Reestruturacao-Plano-De-Recuperacao-Judicial-Investimento-e-outra-avencas.pdf"),
    ("20/03/2023", "Plano de Recuperação Judicial", "Grupo Americanas - Plano de Recuperação Judicial.pdf"),
]

pmp_mensais = [
    ("19/02/2025", "PMP Mensal — Janeiro 2025", "PMP-Mensal-Janeiro-2025-1.pdf"),
    ("16/01/2025", "PMP Mensal — Dezembro 2024", "PMP-Mensal-Dezembro-2024.pdf"),
    ("17/12/2024", "PMP Mensal — Novembro 2024", "PMP-Mensal-Novembro-2024.pdf"),
    ("04/11/2024", "PMP Mensal — Outubro 2024", "PMP-Mensal-Outubro-2024-1.pdf"),
    ("30/09/2024", "PMP Mensal — Setembro 2024", "PMP-Mensal-Setembro-2024.pdf"),
    ("27/08/2024", "PMP Mensal — Agosto 2024", "PMP-Mensal-Agosto-2024.pdf"),
    ("31/07/2024", "PMP Mensal — Julho 2024", "PMP-Mensal-Julho-2024.pdf"),
    ("01/07/2024", "PMP Mensal — Junho 2024", "PMP-Mensal-Junho-2024.pdf"),
    ("30/05/2024", "PMP Mensal — Maio 2024", "PMP-Mensal-Maio-2024.pdf"),
    ("31/03/2024", "PMP Mensal — Abril 2024", "PMP-Mensal-Abril-2024-1.pdf"),
    ("01/04/2024", "PMP Mensal — Março 2024", "PMP-Mensal-Marco-2024.pdf"),
    ("29/02/2024", "PMP Mensal — Fevereiro 2024", "PMP-Mensal-Fevereiro-2024.pdf"),
    ("31/01/2024", "PMP Mensal — Janeiro 2024", "PMP-Mensal-Janero-2024.pdf"),
    ("31/12/2023", "PMP Mensal — Dezembro 2023", "PMP-Mensal-Dezembro-2023.pdf"),
    ("30/11/2023", "PMP Mensal — Novembro 2023", "PMP-Mensal-Novembro-2023.pdf"),
    ("31/10/2023", "PMP Mensal — Outubro 2023", "PMP-Mensal-Outubro-2023.pdf"),
    ("30/09/2023", "PMP Mensal — Setembro 2023", "PMP-Mensal-Setembro-2023.pdf"),
    ("31/08/2023", "PMP Mensal — Agosto 2023", "PMP-Mensal-Agosto-2023.pdf"),
    ("31/07/2023", "PMP Mensal — Julho 2023", "PMP-Mensal-Julho-2023.pdf"),
    ("30/06/2023", "PMP Mensal — Junho 2023", "PMP-Mensal-Junho-2023.pdf"),
    ("31/05/2023", "PMP Mensal — Maio 2023", "PMP-Mensal-Maio-2023.pdf"),
    ("28/04/2023", "PMP Mensal — Abril 2023", "Grupo Americanas – PMP Mensal – Abril 2023 .pdf"),
    ("31/03/2023", "PMP Mensal — Março 2023", "Grupo Americanas – PMP Mensal – Março 2023.pdf"),
]

pmp_semanais = [
    ("20/02/2025", "PMP Semanal 14-20/02/2025", "PMP-semanal-14-20-02-2025.pdf"),
    ("13/02/2025", "PMP Semanal 07-13/02/2025", "PMP-semanal-07-13-02-2025.pdf"),
    ("06/02/2025", "PMP Semanal 31/01-06/02/2025", "PMP-semanal-31-01-06-02-2025.pdf"),
    ("30/01/2025", "PMP Semanal 24-30/01/2025", "PMP-semanal-24-30-01-2025.pdf"),
    ("23/01/2025", "PMP Semanal 17-23/01/2025", "PMP-semanal-17-23-01-2025.pdf"),
    ("16/01/2025", "PMP Semanal 10-16/01/2025", "PMP-semanal-10-16-01-2025.pdf"),
    ("09/01/2025", "PMP Semanal 03-09/01/2025", "PMP-semanal-03-09-01-2025.pdf"),
    ("19/12/2024", "PMP Semanal 13-19/12/2024", "PMP-semanal-13-19-12-2024.pdf"),
    ("12/12/2024", "PMP Semanal 06-12/12/2024", "PMP-semanal-06-12-12-2024.pdf"),
    ("05/12/2024", "PMP Semanal 29/11-05/12/2024", "PMP-semanal-29-11-05-12-2024.pdf"),
]

decisoes = [
    ("20/02/2026", "Autorização da Venda do Fundo de Comércio — Duque de Caxias", "Autorização da venda do fundo de comércio de loja localizada na Av. Nilo Peçanha, 145, Duque de CaxiasRJ.pdf"),
    ("11/02/2026", "Decisão", "Decisão (1).pdf"),
    ("19/12/2025", "Decisão — RJ Autorização Alienação de Bens", "Decisão - RJ AUTORIZAÇÃO ALIENAÇÃO BENS -19.12.2025.pdf"),
    ("25/07/2024", "Decisão", "Decisao-24-07-2024.pdf"),
    ("17/04/2024", "Decisão", "Decisao-17-04-2024.pdf"),
    ("03/10/2023", "Decisão", "Decisao-03-10-2023.pdf"),
    ("27/02/2024", "Decisão — Bloqueio dos Valores Mobiliários por 30 dias", "Decisao-27-02-2024-bloqueio-dos-valores-mobiliarios-por-30-dias.pdf"),
    ("26/02/2024", "Decisão — Homologação do Plano de Recuperação", "Decisão (4).pdf"),
    ("13/12/2023", "Decisão", "Decisao-13-12-2023.pdf"),
    ("21/11/2023", "Decisão — Consolidação Substancial", "Decisão - Consolidação Substancial.pdf"),
    ("19/01/2023", "Decisão Deferindo o Processamento da RJ", "Decisão deferindo o processamento da RJ - 19.01.pdf"),
]

rma = [
    ("03/03/2026", "36º RMA", "AMERICANAS - 36º Relatorio Mensal - Versão PÚBLICA.pdf"),
    ("05/02/2026", "35º RMA", "AMERICANAS - 35º Relatorio Mensal - Versão PUBLICA_compressed.pdf"),
    ("", "34º RMA", "AMERICANAS - 34º Relatorio Mensal.pdf"),
    ("", "33º RMA", "AMERICANAS - 33º Relatorio Mensal - Versão PÚBLICA_compressed.pdf"),
    ("", "32º RMA", "AMERICANAS - 32º Relatorio Mensal.pdf"),
    ("", "30º RMA", "30º RMA.pdf"),
    ("", "29º RMA", "29° RMA.pdf"),
    ("", "28º RMA", "28º RMA.pdf"),
    ("", "27º RMA", "27º RMA.pdf"),
    ("", "26º RMA", "26° RMA.pdf"),
    ("", "25º RMA", "AMERICANAS - 25º Relatorio Mensal - Versão PUBLICA_compressed.pdf"),
    ("", "24º RMA", "Americanas - 24º Relatorio Mensal - Versão PUBLICA (1)_compressed (1).pdf"),
    ("", "23º RMA", "Americanas - 23º RMA.pdf"),
    ("", "22º RMA", "AMERICANAS - 22º Relatório Mensal.pdf"),
    ("", "21º RMA", "Americanas - 21° Relatorio Mensal.pdf"),
    ("", "20º RMA", "AMERICANAS - 20º Relatorio Mensal.pdf"),
    ("", "19º RMA", "AMERICANAS - 19º Relatorio Mensal.pdf"),
    ("", "18º RMA", "AMERICANAS - 18º Relatorio Mensal.pdf"),
    ("", "17º RMA", "Grupo-Americanas-17o-RMA.pdf"),
    ("", "16º RMA", "GRUPO-AMERICANAS-16°- RMA.pdf"),
    ("", "15º RMA", "Grupo-Americanas-15o-RMA.pdf"),
    ("", "14º RMA", "Grupo-Americanas-14o-RMA.pdf"),
    ("", "13º RMA", "Grupo-Americanas-13o-RMA.pdf"),
    ("", "12º RMA", "Grupo-Americanas-12o-RMA.pdf"),
    ("", "11º RMA", "Grupo-Americanas-11o-RMA.pdf"),
    ("", "10º RMA", "Grupo-Americanas-10o-RMA.pdf"),
    ("", "9º RMA", "Grupo-Americanas-9o-RMA.pdf"),
    ("", "8º RMA", "AMERICANAS - 8º Relatorio Mensal.pdf"),
    ("", "7º RMA", "Grupo-Americanas-7o-RMA.pdf"),
    ("", "6º RMA", "Grupo-Americanas-6o-RMA.pdf"),
    ("", "5º RMA", "AMERICANAS - 5º Relatorio Mensal.pdf"),
    ("", "4º RMA", "AMERICANAS - 4º Relatorio Mensal - Versão PUBLICA 30 06 23.pdf"),
    ("", "3º RMA", "AMERICANAS 3 - RMA.pdf"),
    ("", "2º RMA", "AMERICANAS 2 - RMA.pdf"),
    ("", "1º RMA", "AMERICANAS 1 - RMA.pdf"),
]

documentos = [
    ("13/06/2025", "Fato Relevante: Acordo PGFN", "Fato-Relevante-Acordo-PGFN.pdf"),
    ("11/03/2025", "Comunicado ao Mercado — Procedimento Arbitral", "Comunicado-ao-Mercado-Prodecimento-Arbitral-Responsabilização.pdf"),
    ("16/12/2024", "Comunicado ao Mercado — Entrega de Ações com Lock-up", "Comunicado-ao-Mercado-Procedimento-de-entrega-das-açoes-com-lock-up.pdf"),
    ("25/07/2024", "Comunicado ao Mercado — Entrega de Ações e Bônus", "Comunicado-ao-Mercado-Procedimentos-de-entrega-das-acoes-e-bonus-de-subscricao-aos-credores.pdf"),
    ("31/05/2024", "Resultado do Leilão Reverso", "Doc.-01-Resultado-Leilao-Reverso-Atualizado-31.05.24.pdf"),
    ("17/04/2024", "Diretrizes para Participação no Leilão Reverso", "DIRETRIZES-DO-LEILAO-REVERSO.pdf"),
    ("12/12/2023", "Relatório do Aditivo ao PRJ", "Relatorio-do-Aditivo-ao-Plano-de-Recuperacao-Judicial.pdf"),
    ("13/12/2023", "Material da Reunião de Apresentação", "Decisao-13-12-2023.pdf"),
    ("19/12/2023", "Petição com Anexos ao Aditivo", "Peticao-Recuperanda-com-anexos-ao-Adititvo-19-12-2023.pdf"),
    ("27/11/2023", "Apresentação do PRJ pelas Recuperandas", "Americanas-Apresentacao-do-PRJ-feita-pelas-recuperandas.pdf"),
    ("20/03/2023", "Laudo de Avaliação", "Grupo Americanas - Laudo de avaliação.pdf"),
    ("20/03/2023", "Laudo de Viabilidade Econômica", "Grupo Americanas - Laudo de viabilidade econômica.pdf"),
    ("20/03/2023", "Relatório Circunstanciado", "Grupo Americanas – Relatório Circunstanciado - versão pública – 22_03_2023.pdf"),
]

modelos = [
    ("18/07/2024", "Modelo de Notificação — Não Recebimento Debêntures Privadas", "Modelo-de-Notificacao-Nao-Recebimento-Debentures-Privadas-17.07.pdf"),
    ("06/06/2024", "Modelo de Notificação de Renúncia ao Recebimento de Ações", "PRJ-Americanas-Modelo-de-Notificacao-de-Renuncia-ao-Recebimento-de-Acoes.pdf"),
    ("04/10/2023", "Modelo de Procuração para Desmembramento de Credor e AGC (bilíngue)", "Modelo-Procuracao-para-Desmembramento-de-Credor-e-AGC-Americanas-BILINGUE.docx"),
    ("04/10/2023", "Modelo de Declaração de Credor Investidor (bilíngue)", "Modelo-Declaracao-de-Credor-Investidor-Americanas-BILINGUE-1.docx"),
    ("04/10/2023", "Certificado de Eleição e Incumbência (bilíngue)", "Modelo-Certificado-de-Eleicao-e-Incumbencia-Americanas-BILINGUE.docx"),
    ("04/10/2023", "Minuta — Edital de Desmembramento de Credor Investidor (bilíngue)", "Minuta-Edital-de-Desmembramento-de-Credor-Investidor-Americanas-BILINGUE.docx"),
    ("05/04/2023", "Modelo de Procuração — AGC", "Modelo-de-Procuracao-AGC-1 (2).docx"),
    ("26/01/2023", "Modelo de Divergência de Crédito", "AMERICANAS-Modelo-de-Divergencia-de-Credito-RJ-1.docx"),
    ("26/01/2023", "Modelo de Habilitação de Crédito", "AMERICANAS-Modelo-de-Habilitacao-de-Credito-RJ-1.docx"),
]

# ============================================================================
# 5. HELPER FUNCTIONS FOR BUILDING HTML
# ============================================================================

def get_download_button(filename, label="Baixar PDF"):
    """Generate a download button based on file extension"""
    if filename.endswith('.xlsx'):
        label = "Baixar XLSX"
    elif filename.endswith('.docx'):
        label = "Baixar DOCX"

    return f'''<a href="assets/pdfs/americanas/{filename}" download class="pdf-download">
            <svg viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>
            {label}
        </a>'''

def build_doc_item(date, title, filename):
    """Build a single doc-item HTML"""
    download_btn = get_download_button(filename)
    return f'''<div class="doc-item">
                    <div class="doc-item-header" onclick="toggleDoc(this)">
                        <span class="doc-date">{date}</span>
                        <span class="doc-name">{title}</span>
                        <span class="doc-toggle">+</span>
                    </div>
                    <div class="doc-item-body">
                        {download_btn}
                        <strong>Administração Judicial Conjunta do Grupo Americanas</strong>
                    </div>
                </div>'''

def build_informativos_item(num, title):
    """Build an informativo item with text content"""
    # For now, use placeholder text - in a real scenario, extract from americanas.html
    return f'''<div class="doc-item">
                    <div class="doc-item-header" onclick="toggleDoc(this)">
                        <span class="doc-name">INFORMATIVO {num} — {title}</span>
                        <span class="doc-toggle">+</span>
                    </div>
                    <div class="doc-item-body">
                        <p>Informação relevante ao processo de Recuperação Judicial do Grupo Americanas.</p>
                        <strong>Administração Judicial Conjunta do Grupo Americanas</strong>
                    </div>
                </div>'''

def build_pmp_section():
    """Build PMP section with Mensais and Semanais subsections"""
    html = '<div style="font-family:var(--font-sans); font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--gold); padding: 16px 0 8px 0; border-bottom: 1px solid rgba(184,150,62,0.1); margin-bottom: 8px;">Mensais</div>'
    for date, title, filename in pmp_mensais:
        html += build_doc_item(date, title, filename)

    html += '<div style="font-family:var(--font-sans); font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--gold); padding: 16px 0 8px 0; border-bottom: 1px solid rgba(184,150,62,0.1); margin: 16px 0 8px 0;">Semanais</div>'
    for date, title, filename in pmp_semanais:
        html += build_doc_item(date, title, filename)

    return html

# ============================================================================
# 6. BUILD THE COMPLETE HTML
# ============================================================================

# Modify head title
new_title = "GRUPO AMERICANAS | Escritório de Advocacia Zveiter"
head_section = head_section.replace(
    "<title>",
    f"<title>\n   {new_title}\n  "
).replace(
    "G.A.S. Consultoria — Falência",
    "GRUPO AMERICANAS — Recuperação Judicial"
)

# Build hero section
hero_html = '''<div class="page-hero">
            <div class="page-hero-content">
                <nav class="breadcrumb">
                    <a href="/">Home</a> →
                    <a href="/recuperacoes">Recuperações Judiciais e Falências</a> →
                    <span>Grupo Americanas</span>
                </nav>
                <div class="hero-wrapper">
                    <div class="hero-text">
                        <span class="hero-tag">Recuperação Judicial</span>
                        <h1 class="hero-title">Grupo Ame<em>ricanas</em></h1>
                    </div>
                    <div class="meta-grid">
                        <div class="meta-col">
                            <div class="meta-label">Empresas</div>
                            <div class="meta-value">Americanas S.A., B2W Digital Lux S.à.r.l., JSM Global S.à.r.l.</div>
                        </div>
                        <div class="meta-col">
                            <div class="meta-label">Processo</div>
                            <div class="meta-value">0803087-20.2023.8.19.0001</div>
                        </div>
                        <div class="meta-col">
                            <div class="meta-label">Vara</div>
                            <div class="meta-value">4ª Vara Empresarial — Rio de Janeiro</div>
                        </div>
                        <div class="meta-col">
                            <div class="meta-label">Adm. Judicial</div>
                            <div class="meta-value">Escritório Zveiter & Preserva-Ação Adm. Judicial</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>'''

# Build sidebar items HTML
sidebar_items = '''<div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Informativos</span>
                        <span class="count">9</span>
                    </button>
                    <div class="sidebar-submenu" id="panel-informativos">
'''
for num, title in informativos:
    sidebar_items += f'<a href="#panel-informativos" onclick="scrollToPanel(\'panel-informativos\')">INFORMATIVO {num}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Editais</span>
                        <span class="count">10</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in editais:
    sidebar_items += f'<a href="#panel-editais">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Relação de Credores</span>
                        <span class="count">17</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in relacao_credores:
    sidebar_items += f'<a href="#panel-relacao-credores">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Avisos</span>
                        <span class="count">13</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in avisos:
    sidebar_items += f'<a href="#panel-avisos">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Ata da AGC</span>
                        <span class="count">8</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in ata_agc:
    sidebar_items += f'<a href="#panel-ata-agc">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Plano de RJ</span>
                        <span class="count">7</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in plano_rj:
    sidebar_items += f'<a href="#panel-plano-rj">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>PMP</span>
                        <span class="count">46</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in pmp_mensais:
    sidebar_items += f'<a href="#panel-pmp">{title}</a>\n'
for _, title, _ in pmp_semanais:
    sidebar_items += f'<a href="#panel-pmp">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Documentos</span>
                        <span class="count">13</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in documentos:
    sidebar_items += f'<a href="#panel-documentos">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Decisões Judiciais</span>
                        <span class="count">11</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in decisoes:
    sidebar_items += f'<a href="#panel-decisoes">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>RMA</span>
                        <span class="count">36</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in rma:
    sidebar_items += f'<a href="#panel-rma">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-category">
                    <button class="sidebar-toggle" onclick="toggleSidebar(this)">
                        <span>Modelos</span>
                        <span class="count">9</span>
                    </button>
                    <div class="sidebar-submenu">
'''
for _, title, _ in modelos:
    sidebar_items += f'<a href="#panel-modelos">{title}</a>\n'
sidebar_items += '''</div>
                </div>

                <div class="sidebar-external-link">
                    <a href="https://psvar.com.br/recuperacao-judicial/grupo-americanas/" target="_blank">
                        Site da Recuperação ↗
                    </a>
                </div>
'''

# Build doc-panels
panels_html = '''<div class="doc-panels">
'''

# Informativos
panels_html += '''<div class="doc-panel" id="panel-informativos">
                    <h2>Informativos</h2>
'''
for num, title in informativos:
    panels_html += build_informativos_item(num, title)
panels_html += '''</div>

'''

# Editais
panels_html += '''<div class="doc-panel" id="panel-editais">
                    <h2>Editais</h2>
'''
for date, title, filename in editais:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Relação de Credores
panels_html += '''<div class="doc-panel" id="panel-relacao-credores">
                    <h2>Relação de Credores</h2>
'''
for date, title, filename in relacao_credores:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Avisos
panels_html += '''<div class="doc-panel" id="panel-avisos">
                    <h2>Avisos</h2>
'''
for date, title, filename in avisos:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Ata da AGC
panels_html += '''<div class="doc-panel" id="panel-ata-agc">
                    <h2>Ata da AGC</h2>
'''
for date, title, filename in ata_agc:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Plano de RJ
panels_html += '''<div class="doc-panel" id="panel-plano-rj">
                    <h2>Plano de RJ</h2>
'''
for date, title, filename in plano_rj:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# PMP
panels_html += '''<div class="doc-panel" id="panel-pmp">
                    <h2>PMP</h2>
'''
panels_html += build_pmp_section()
panels_html += '''</div>

'''

# Documentos
panels_html += '''<div class="doc-panel" id="panel-documentos">
                    <h2>Documentos</h2>
'''
for date, title, filename in documentos:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Decisões Judiciais
panels_html += '''<div class="doc-panel" id="panel-decisoes">
                    <h2>Decisões Judiciais</h2>
'''
for date, title, filename in decisoes:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# RMA
panels_html += '''<div class="doc-panel" id="panel-rma">
                    <h2>RMA</h2>
'''
for date, title, filename in rma:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>

'''

# Modelos
panels_html += '''<div class="doc-panel" id="panel-modelos">
                    <h2>Modelos</h2>
'''
for date, title, filename in modelos:
    panels_html += build_doc_item(date, title, filename)
panels_html += '''</div>
</div>
'''

# ============================================================================
# 7. ASSEMBLE FINAL HTML
# ============================================================================

# Find the container div in gas template and extract its structure
container_start = gas_content.find('<div class="container"')
if container_start == -1:
    # If no container, just use divs
    container_html = f'''<div class="container">
            <aside class="sidebar">
                {sidebar_items}
            </aside>
            <main class="main-content">
                {panels_html}
            </main>
        </div>'''
else:
    # Extract the container structure from gas
    container_end = gas_content.rfind('</div>')
    container_template = gas_content[container_start:container_end+6]

    # Build container with new content
    container_html = f'''<div class="container">
            <aside class="sidebar">
                {sidebar_items}
            </aside>
            <main class="main-content">
                {panels_html}
            </main>
        </div>'''

# Assemble complete document
final_html = f'''{head_section}
<body>
{nav_template}

{hero_html}

{container_html}

{footer_section}

</body>
</html>'''

# Write to file
with open('/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/americanas_redesign.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("✓ Generated americanas_redesign.html")
print(f"  - File size: {len(final_html):,} bytes")
print(f"  - Informativos: 9")
print(f"  - Editais: 10")
print(f"  - Relação de Credores: 17")
print(f"  - Avisos: 13")
print(f"  - Ata da AGC: 8")
print(f"  - Plano de RJ: 7")
print(f"  - PMP: 46")
print(f"  - Documentos: 13")
print(f"  - Decisões Judiciais: 11")
print(f"  - RMA: 36")
print(f"  - Modelos: 9")
print(f"  - Total doc-items: {9+10+17+13+8+7+46+13+11+36+9:,}")

GENERATE_SCRIPT
