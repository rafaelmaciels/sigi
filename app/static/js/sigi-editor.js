/**
 * 🖋️ SiGI — Componente e Inicializador Reutilizável do Editor WYSIWYG (Quill.js)
 * Padronizado para toda a aplicação seguindo o modelo do módulo Dados do Membro.
 */

(function () {
  'use strict';

  // Toolbar completa padrão do SiGI (estilo WordPress)
  window.SIGI_TOOLBAR_OPTIONS = [
    [{ 'header': [2, 3, false] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
    [{ 'align': [] }],
    ['blockquote', 'link'],
    ['clean']
  ];

  /**
   * Inicializa um editor Quill em um container específico e vincula ao formulário.
   * 
   * @param {Object} options
   * @param {string} options.editorId - ID do elemento do editor (ex: 'editorContainer')
   * @param {string} options.inputId - ID do input hidden que armazenará o HTML (ex: 'corpo_input')
   * @param {string} [options.charCountId] - ID do span de contagem de caracteres
   * @param {string} [options.wordCountId] - ID do span de contagem de palavras
   * @param {string} [options.placeholder] - Texto placeholder do editor
   * @param {boolean} [options.readOnly=false] - Modo somente leitura
   * @param {number} [options.minHeight=180] - Altura mínima em pixels
   * @returns {Quill|null} Instância do Quill criada
   */
  window.initSigiEditor = function (options) {
    if (typeof Quill === 'undefined') {
      console.warn('Quill.js não foi carregado.');
      return null;
    }

    const editorEl = document.getElementById(options.editorId);
    const hiddenInput = document.getElementById(options.inputId);

    if (!editorEl || !hiddenInput) {
      return null;
    }

    const readOnly = options.readOnly || false;
    const placeholder = options.placeholder || 'Digite o conteúdo formatado aqui...';

    const quill = new Quill(editorEl, {
      theme: 'snow',
      readOnly: readOnly,
      placeholder: placeholder,
      modules: {
        toolbar: readOnly ? false : (options.toolbar || window.SIGI_TOOLBAR_OPTIONS),
        history: {
          delay: 1000,
          maxStack: 50,
          userOnly: true
        }
      }
    });

    if (options.minHeight) {
      const qlEditor = editorEl.querySelector('.ql-editor');
      if (qlEditor) {
        qlEditor.style.minHeight = options.minHeight + 'px';
      }
    }

    // Contadores de caracteres e palavras
    const charCountEl = options.charCountId ? document.getElementById(options.charCountId) : null;
    const wordCountEl = options.wordCountId ? document.getElementById(options.wordCountId) : null;

    function atualizarContadores() {
      const text = quill.getText().trim();
      const chars = text.length;
      const words = text ? text.split(/\s+/).length : 0;
      if (charCountEl) {
        charCountEl.textContent = chars + (chars === 1 ? ' caractere' : ' caracteres');
      }
      if (wordCountEl) {
        wordCountEl.textContent = words + (words === 1 ? ' palavra' : ' palavras');
      }
    }

    atualizarContadores();
    quill.on('text-change', atualizarContadores);

    // Sincronização no envio do formulário
    const form = hiddenInput.closest('form') || editorEl.closest('form');
    if (form) {
      form.addEventListener('submit', function () {
        const text = quill.getText().trim();
        if (!text) {
          hiddenInput.value = '';
        } else {
          hiddenInput.value = quill.root.innerHTML;
        }
      });
    }

    return quill;
  };
})();
