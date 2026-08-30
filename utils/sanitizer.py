#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ SiGI — Utilitário de Sanitização HTML e Proteção Contra XSS
Utiliza a biblioteca oficial Mozilla Bleach para garantir que qualquer
conteúdo de texto rico enviado pelo frontend seja higienizado antes de persistir no banco.
"""

import bleach
import re

# Tags HTML estritamente permitidas para o editor de texto rico
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike',
    'h1', 'h2', 'h3', 'h4', 'blockquote', 'ul', 'ol', 'li',
    'a', 'span', 'pre', 'code'
]

# Atributos permitidos por tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'span': ['class'],
    'p': ['class'],
    'li': ['class'],
    'h1': ['class'],
    'h2': ['class'],
    'h3': ['class'],
    'h4': ['class'],
    'blockquote': ['class']
}

# Protocolos de URL estritamente seguros
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']

# Classes CSS permitidas geradas pelo Quill.js
ALLOWED_CLASSES = {
    'ql-align-center',
    'ql-align-right',
    'ql-align-justify',
    'ql-indent-1',
    'ql-indent-2',
    'ql-indent-3'
}


def sanitizar_html(conteudo: str | None) -> str | None:
    """
    Sanitiza uma string HTML removendo scripts, iframes, atributos de eventos inline
    (onclick, onerror, onload, etc.) e protocolos inseguros (javascript:, data:).
    
    Retorna o HTML seguro ou None caso esteja vazio.
    """
    if not conteudo:
        return None

    texto_limpo = conteudo.strip()
    
    # Se o editor enviou apenas parágrafos vazios (<p><br></p> ou <p></p>)
    if re.fullmatch(r'<p>(\s*|<br\s*/?>)*</p>', texto_limpo, re.IGNORECASE) or not texto_limpo:
        return None

    # Remove completamente blocos inteiros de <script>...</script> e <style>...</style>
    texto_limpo = re.sub(r'<script\b[^>]*>[\s\S]*?<\/script>', '', texto_limpo, flags=re.IGNORECASE)
    texto_limpo = re.sub(r'<style\b[^>]*>[\s\S]*?<\/style>', '', texto_limpo, flags=re.IGNORECASE)

    # Sanitização profunda com Bleach
    sanitizado = bleach.clean(
        texto_limpo,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )

    # Adiciona rel="noopener noreferrer" e target="_blank" de forma segura aos links
    def _link_callback(attrs, new=False):
        href = attrs.get((None, 'href'), '')
        if href.startswith(('http://', 'https://')):
            attrs[(None, 'target')] = '_blank'
            attrs[(None, 'rel')] = 'noopener noreferrer'
        return attrs

    sanitizado = bleach.linkify(
        sanitizado,
        callbacks=[_link_callback],
        skip_tags=['pre', 'code']
    )

    return sanitizado.strip() if sanitizado.strip() else None
