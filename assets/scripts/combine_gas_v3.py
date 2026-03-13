#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to combine gas_redesign.html (design) with complete content from gas.html
Version 3: Direct BeautifulSoup manipulation
"""

from bs4 import BeautifulSoup, NavigableString
import re
import os

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
                            informativos.append({
                                'title': title,
                                'content_div': content_div
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
                                'content_div': content_div
                            })
                if section_items:
                    sections[button_text] = section_items

    return sections

def create_doc_item(title, content_div, is_pdf_section=False):
    """Create a doc-item element"""
    # Get inner HTML
    inner_html = ''.join(str(child) for child in content_div.children)

    # Extract date if available
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', inner_html)
    date = date_match.group(1) if date_match else ''

    # Clean up title
    title_clean = title.replace('INFORMATIVO ', 'Informativo ')

    # Create new doc-item div
    doc_item = BeautifulSoup(
        f'''<div class="doc-item">
                        <div class="doc-item-header" onclick="toggleDoc(this)">
                            <span class="doc-date">{date}</span>
                            <span class="doc-name">{title_clean}</span>
                            <span class="doc-toggle">+</span>
                        </div>
                        <div class="doc-item-body">
                            {inner_html}
                        </div>
                    </div>''',
        'html.parser'
    )

    return doc_item

def combine_files(redesign_path, original_path, output_path):
    """Main function to combine files"""

    print("Reading files...")
    redesign_html = read_file(redesign_path)
    original_html = read_file(original_path)

    print("Parsing redesign file...")
    redesign_soup = BeautifulSoup(redesign_html, 'html.parser')

    print("Extracting informativos from original...")
    informativos = extract_all_informativos(original_html)
    print(f"Found {len(informativos)} informativos")

    print("Extracting other sections from original...")
    sections = extract_all_sections(original_html)
    print(f"Found sections: {list(sections.keys())}")

    # Find the page-content div in redesign
    page_content = redesign_soup.find('div', class_='page-content')
    if not page_content:
        print("ERROR: Could not find page-content div in redesign")
        return

    # Find and update the sidebar
    sidebar = page_content.find('aside', class_='doc-sidebar')
    if sidebar:
        print("Updating sidebar navigation...")
        sidebar_ul = sidebar.find('ul', class_='doc-nav')
        if sidebar_ul:
            sidebar_ul.clear()

            # Build new sidebar items
            nav_items_html = f'''<li class="nav-label">Processo</li>
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
                    </li>'''

            sidebar_ul.append(BeautifulSoup(nav_items_html, 'html.parser'))

    # Find and update the main content area
    main = page_content.find('div', class_='doc-main')
    if main:
        print("Building content panels...")
        main.clear()

        # Informativos panel
        print("  - Building informativos panel...")
        info_panel = BeautifulSoup(
            '''<div id="informativos-panel" class="doc-panel active">
                    <div class="panel-header">
                        <h2>Informativos</h2>
                        <p class="panel-subtitle">Comunicados da Administração Judicial</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        info_doc_list = info_panel.find('div', class_='doc-list')
        for info in informativos:
            doc_item = create_doc_item(info['title'], info['content_div'])
            info_doc_list.append(doc_item)
        main.append(info_panel)

        # Editais panel
        print("  - Building editais panel...")
        editais_panel = BeautifulSoup(
            '''<div id="editais-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Editais</h2>
                        <p class="panel-subtitle">Editais do processo falimentar</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        editais_doc_list = editais_panel.find('div', class_='doc-list')
        for item in sections.get('EDITAIS', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            editais_doc_list.append(doc_item)
        main.append(editais_panel)

        # Relação de Credores panel
        print("  - Building relação de credores panel...")
        relacao_panel = BeautifulSoup(
            '''<div id="relacao-credores-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Relação de Credores</h2>
                        <p class="panel-subtitle">Documentos e listas de credores</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        relacao_doc_list = relacao_panel.find('div', class_='doc-list')
        for item in sections.get('RELAÇÃO DE CREDORES', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            relacao_doc_list.append(doc_item)
        main.append(relacao_panel)

        # Avisos panel
        print("  - Building avisos panel...")
        avisos_panel = BeautifulSoup(
            '''<div id="avisos-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Avisos</h2>
                        <p class="panel-subtitle">Avisos e comunicações</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        avisos_doc_list = avisos_panel.find('div', class_='doc-list')
        for item in sections.get('AVISOS', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            avisos_doc_list.append(doc_item)
        main.append(avisos_panel)

        # Ação Civil Pública panel
        print("  - Building ação civil pública panel...")
        acao_panel = BeautifulSoup(
            '''<div id="acao-civil-publica-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Ação Civil Pública</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        acao_doc_list = acao_panel.find('div', class_='doc-list')
        for item in sections.get('AÇÃO CIVIL PÚBLICA', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            acao_doc_list.append(doc_item)
        main.append(acao_panel)

        # Tutela Cautelar panel
        print("  - Building tutela cautelar panel...")
        tutela_panel = BeautifulSoup(
            '''<div id="tutela-cautelar-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Tutela Cautelar Antecedente</h2>
                        <p class="panel-subtitle">Documentos e decisões</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        tutela_doc_list = tutela_panel.find('div', class_='doc-list')
        for item in sections.get('TUTELA CAUTELAR ANTECEDENTE À RECUPERAÇÃO JUDICIAL', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            tutela_doc_list.append(doc_item)
        main.append(tutela_panel)

        # Decisões Judiciais panel
        print("  - Building decisões judiciais panel...")
        decisoes_panel = BeautifulSoup(
            '''<div id="decisoes-panel" class="doc-panel">
                    <div class="panel-header">
                        <h2>Decisões Judiciais</h2>
                        <p class="panel-subtitle">Decisões e acórdãos</p>
                    </div>
                    <div class="doc-list">
                    </div>
                </div>''',
            'html.parser'
        )
        decisoes_doc_list = decisoes_panel.find('div', class_='doc-list')
        for item in sections.get('DECISÕES JUDICIAIS', []):
            doc_item = create_doc_item(item['title'], item['content_div'], True)
            decisoes_doc_list.append(doc_item)
        main.append(decisoes_panel)

    print("Fixing email link colors...")
    # Fix email links
    for a_tag in redesign_soup.find_all('a', href=re.compile(r'^mailto:')):
        a_tag['style'] = 'color:var(--gold-light);'

    print(f"Writing output to {output_path}...")
    output_html = str(redesign_soup)
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
    output_size = os.path.getsize(output_path)
    print(f"Output file size: {output_size / 1024:.1f} KB")

    # Check informativos
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
