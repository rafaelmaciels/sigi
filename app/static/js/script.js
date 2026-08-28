/**
 * SiGI - Sistema Integrado de Gestão de Igreja
 * Frontend Utilities & Interactive Components
 */

document.addEventListener("DOMContentLoaded", function() {
  // 1. Mostrar/ocultar campo de cônjuge dinamicamente
  const estadoCivilEl = document.getElementById("estadoCivil");
  const conjugeField = document.getElementById("conjugeField");

  function atualizarCampoConjuge() {
    if (!estadoCivilEl || !conjugeField) return;
    if (estadoCivilEl.value === "Casado") {
      conjugeField.style.display = "block";
    } else {
      conjugeField.style.display = "none";
    }
  }

  if (estadoCivilEl) {
    estadoCivilEl.addEventListener("change", atualizarCampoConjuge);
    atualizarCampoConjuge();
  }

  // 2. Habilitar modo de edição em formulários de visualização
  const btnHabilitar = document.getElementById("habilitarEdicao");
  if (btnHabilitar) {
    btnHabilitar.addEventListener("click", function() {
      document.querySelectorAll("#formEditar input, #formEditar select, #formEditar textarea").forEach(function(el) {
        el.removeAttribute("readonly");
        el.removeAttribute("disabled");
      });
      const salvarBtn = document.getElementById("salvarBtn");
      if (salvarBtn) salvarBtn.classList.remove("d-none");
      this.style.display = "none";
    });
  }

  // 3. Aplicação de máscaras de input (compatível com jQuery Mask se presente)
  if (typeof $ !== "undefined" && typeof $.fn.mask !== "undefined") {
    $('#telefone, input[name="telefone"]').mask('(00) 00000-0000');
    $('#cpf, input[name="cpf"]').mask('000.000.000-00');
    $('#rg, input[name="rg"]').mask('00.000.000-0');
    $('#cep, input[name="cep"]').mask('00000-000');
    $('#cnpj, input[name="cnpj"]').mask('00.000.000/0000-00');
  }

  // 4. Inicializar Tooltips do Bootstrap se disponíveis
  if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
});
