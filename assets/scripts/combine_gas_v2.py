#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to combine gas_redesign.html (design) with complete content from gas.html
Version 2: Better extraction and minimal prettification
"""

from bs4 import BeautifulSoup
import re

def read_file(filepath):
    """Read HTML file with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """Write HTML file with UTF-8 encoding"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_all_informativos(html_content):
    """Extract all informativos with their complete content from original"""
    soup = BeautifulSoup(html_content, 'html.parser')

    informativos = []

    # Find all dropdown items for INFORMATIVOS
    buttons = soup.find_all('button', class_='dropbtn')
    for button in buttons:
        if 'INFORMATIVOS' in button.get_text():
            dropdown = button.find_next('div', class_='dropdown-content')
            if dropdown:
                items = dropdown.find_all('a', class_='dropdown-item')
                for item in items:
                    title = item.get_text().strip()
                    onclick = item.get('onclick', '')
                    match = re.search(r"toggleContent\('([^']+)'\)", onclick)
                    if match:
                        content_id = match.group(1)
                        content_div = dropdown.find('div', id=content_id)
                        if content_div:
                            # Get all content inside the div
                            informativos.append({
                                'title': title,
                                'content': content_div
                            })
            break

    return informativos

def extract_all_sections(html_content):
    """Extract all other sections"""
    soup = BeautifulSoup(html_content, 'html.parser')

    sections = {}
    buttons = soup.find_all('button', class_='dropbtn')

    for button in buttons:
        button_text = button.get_text().strip()
        if button_text in ['EDITAIS', 'RELAÇÃO DE CREDORES', 'AVISOS', 'AÇÃO CIVIL PÚBLICA',
                           'TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', 'DECISÕES JUDICIAIS']:
            dropdown = button.find_next('div', class_='dropdown-content')
            if dropdown:
                items = dropdown.find_all('a', class_='dropdown-item')
                section_items = []
                for item in items:
                    title = item.get_text().strip()
                    onclick = item.get('onclick', '')
                    match = re.search(r"toggleContent\('([^']+)'\)", onclick)
                    if match:
                        content_id = match.group(1)
                        content_div = dropdown.find('div', id=content_id)
                        if content_div:
                            section_items.append({
                                'title': title,
                                'content': content_div
                            })
                if section_items:
                    sections[button_text] = section_items

    return sections

def get_inner_html(element):
    """Get inner HTML of an element"""
    return ''.join(str(child) for child in element.children)

def create_doc_item_html(title, content_element, is_pdf_section=False):
    """Create a doc-item HTML for an informativo or other item"""
    inner_html = get_inner_html(content_element)

    # Extract date if available
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', inner_html)
    date = date_match.group(1) if date_match else ''

    # Clean up title
    title_clean = title.replace('INFORMATIVO ', 'Informativo ')

    html = f'''                    <div class="doc-item">
                        <div class="doc-item-header" onclick="toggleDoc(this)">
                            <span class="doc-date">{date}</span>
                            <span class="doc-name">{title_clean}</span>
                            <span class="doc-toggle">+</span>
                        </div>
                        <div class="doc-item-body">
                            {inner_html}
'''
    if not is_pdf_section and 'ADMINISTRAÇÃO JUDICIAL' not in inner_html:
        html += '                            <strong>ADMINISTRAÇÃO JUDICIAL CONJUNTA DA GAS CONSULTORIA E TECNOLOGIA LTDA.</strong>\n'

    html += '''                        </div>
                    </div>
'''
    return html

def combine_files(redesign_path, original_path, output_path):
    """Main function to combine files"""

    print("Reading files...")
    redesign_html = read_file(redesign_path)
    original_html = read_file(original_path)

    print("Extracting informativos from original...")
    informativos = extract_all_informativos(original_html)
    print(f"Found {len(informativos)} informativos")

    print("Extracting other sections from original...")
    sections = extract_all_sections(original_html)
    print(f"Found sections: {list(sections.keys())}")

    # Build the informativos panel content
    print("Building informativos panel...")
    informativos_html = ''
    for info in informativos:
        informativos_html += create_doc_item_html(info['title'], info['content'])

    # Build other panels
    editais_html = ''
    for item in sections.get('EDITAIS', []):
        editais_html += create_doc_item_html(item['title'], item['content'], True)

    relacao_credores_html = ''
    for item in sections.get('RELAÇÃO DE CREDORES', []):
        relacao_credores_html += create_doc_item_html(item['title'], item['content'], True)

    avisos_html = ''
    for item in sections.get('AVISOS', []):
        avisos_html += create_doc_item_html(item['title'], item['content'], True)

    acao_civil_html = ''
    for item in sections.get('AÇÃO CIVIL PÚBLICA', []):
        acao_civil_html += create_doc_item_html(item['title'], item['content'], True)

    tutela_cautelar_html = ''
    for item in sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []):
        tutela_cautelar_html += create_doc_item_html(item['title'], item['content'], True)

    decisoes_html = ''
    for item in sections.get('DECISÕES JUDICIAIS', []):
        decisoes_html += create_doc_item_html(item['title'], item['content'], True)

    print("Building sidebar navigation...")
    sidebar_nav = f'''                <ul class="doc-nav">
                    <li class="nav-label">Processo</li>
                    <li>
                        <a href="#" onclick="showPanel('informativos', this); return false;">
                            Informativos
                            <span class="count">{len(informativos)}</span>
                        </a>
                    </li>
                    <li class="nav-label">Documentos</li>
                    <li>
                        <a href="#" onclick="showPanel('editais', this); return false;">
                            Editais
                            <span class="count">{len(sections.get('EDITAIS', []))}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('relacao-credores', this); return false;">
                            Relação de Credores
                            <span class="count">{len(sections.get('RELAÇÃO DE CREDORES', []))}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('avisos', this); return false;">
                            Avisos
                            <span class="count">{len(sections.get('AVISOS', []))}</span>
                        </a>
                    </li>
                    <li class="nav-label">Ações Judiciais</li>
                    <li>
                        <a href="#" onclick="showPanel('acao-civil-publica', this); return false;">
                            Ação Civil Pública
                            <span class="count">{len(sections.get('AÇÃO CIVIL PÚBLICA', []))}</span>
                        </a>
                    </li>
                    <li>
                        <a href="#" onclick="showPanel('tutela-cautelar', this); return false;">
                            Tutela Cautelar
                            <span class="count">{len(sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []))}</span>
                        </a>
                    </li>
                    <li class="nav-label">Decisões</li>
                    <li>
                        <a href="#" onclick="showPanel('decisoes', this); return false;">
                            Decisões Judiciais
                            <span class="count">{len(sections.get('DECISÕES JUDICIAIS', []))}</span>
                        </a>
                    </li>
                </ul>'''

    panels_html = f'''
                <!-- Informativos Panel -->
                <div id="informativos-panel" class="doc-panel active">
                    <div class="panel-header">
                        <h2>Informativos</h2>
                        <p class="panel-subtitle">Comunicados da Administração Judicial</p>
                    </div>
                    <div class="doc-list">
{informativos_html}
                    </div>
                </div>

                <!-- Editais Panel -->
                <div id="editais-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Editais</h2>
                        <p class="panel-subtitle">Editais do processo falimentar</p>
                    </div>
                    <div class="doc-list">
{editais_html}
                    </div>
                </div>

                <!-- Relação de Credores Panel -->
                <div id="relacao-credores-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Relação de Credores</h2>
                        <p class="panel-subtitle">Documentos e listas de credores</p>
                    </div>
                    <div class="doc-list">
{relacao_credores_html}
                    </div>
                </div>

                <!-- Avisos Panel -->
                <div id="avisos-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Avisos</h2>
                        <p class="panel-subtitle">Avisos e comunicações</p>
                    </div>
                    <div class="doc-list">
{avisos_html}
                    </div>
                </div>

                <!-- Ação Civil Pública Panel -->
                <div id="acao-civil-publica-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Ação Civil Pública</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
{acao_civil_html}
                    </div>
                </div>

                <!-- Tutela Cautelar Panel -->
                <div id="tutela-cautelar-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Tutela Cautelar Antecedente</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
{tutela_cautelar_html}
                    </div>
                </div>

                <!-- Decisões Judiciais Panel -->
                <div id="decisoes-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Decisões Judiciais</h2>
                        <p class="panel-subtitle">Decisões e acórdãos</p>
                    </div>
                    <div class="doc-list">
{decisoes_html}
                    </div>
                </div>
'''

    print("Replacing content sections...")
    # Use regex to find and replace the page-content div sections
    # Find the sidebar and replace its content
    sidebar_pattern = r'<aside class="doc-sidebar">.*?<ul class="doc-nav">.*?</ul>'
    output_html = re.sub(
        sidebar_pattern,
        f'<aside class="doc-sidebar">\n{sidebar_nav}',
        redesign_html,
        flags=re.DOTALL
    )

    # Find and replace the doc-panels sections
    panels_pattern = r'<div class="doc-main">.*?(?=<footer|$)'
    output_html = re.sub(
        panels_pattern,
        f'<div class="doc-main">{panels_html}\n            ',
        output_html,
        flags=re.DOTALL
    )

    # Fix email link colors
    output_html = re.sub(
        r'<a\s+href="mailto:([^"]+)"[^>]*style="color:#0066cc;"',
        r'<a href="mailto:\1" style="color:var(--gold-light);"',
        output_html
    )
    output_html = re.sub(
        r'<a\s+href="mailto:([^"]+)"[^>]*>',
        r'<a href="mailto:\1" style="color:var(--gold-light);">',
        output_html
    )

    # Save output
    print(f"Writing output to {output_path}...")
    write_file(output_path, output_html)

    # Verification
    doc_items = output_html.count('class="doc-item"')
    print(f"\nSuccess! Generated {output_path}")
    print(f"Total doc-items: {doc_items}")
    print(f"  - Informativos: {len(informativos)}")
    print(f"  - Editais: {len(sections.get('EDITAIS', []))}")
    print(f"  - Relação de Credores: {len(sections.get('RELAÇÃO DE CREDORES', []))}")
    print(f"  - Avisos: {len(sections.get('AVISOS', []))}")
    print(f"  - Ação Civil Pública: {len(sections.get('AÇÃO CIVIL PÚBLICA', []))}")
    print(f"  - Tutela Cautelar: {len(sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []))}")
    print(f"  - Decisões Judiciais: {len(sections.get('DECISÕES JUDICIAIS', []))}")

    # File size info
    import os
    output_size = os.path.getsize(output_path)
    print(f"Output file size: {output_size / 1024:.1f} KB")

    # Check that we have some informativos from the beginning
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'INFORMATIVO 0001/2022' in content:
            print("✓ Informativo 0001/2022 found")
        if 'INFORMATIVO 0065/2026' in content:
            print("✓ Informativo 0065/2026 found")

if __name__ == '__main__':
    redesign_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas_redesign.html'
    original_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas.html'
    output_path = '/sessions/blissful-friendly-maxwell/mnt/SiteZveiter/gas_redesign.html'

    combine_files(redesign_path, original_path, output_path)
