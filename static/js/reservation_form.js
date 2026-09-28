/* Fenêtre « Nouvelle réservation » : nouveau client, détail du calcul (listes avec recherche : app.js) */
(function () {
  var form = document.getElementById('reservationForm');
  if (!form) return;
  var newCheck = document.getElementById('nouveauClientCheck');
  var newFields = document.getElementById('nouveauClientFields');
  var requiredWhenNew = ['nouveau_nom', 'nouveau_prenom', 'nouveau_type_document', 'nouveau_numero_document'];
  var dateArr = form.querySelector('input[name="date_arrivee"]');
  var dateDep = form.querySelector('input[name="date_depart"]');
  var chambreValue = document.getElementById('chambreValue');
  var fmt = function (n) { return Math.round(n).toLocaleString('fr-FR') + ' FCFA'; };
  var num = function (v) { var n = parseFloat(String(v || '').replace(',', '.')); return isNaN(n) ? 0 : n; };
  var combos = Array.prototype.map.call(form.querySelectorAll('[data-combo]'), window.HM.combo);
  var clientCombo = combos[0];

  /* ---------- Nouveau client ---------- */
  function setNewClient(on) {
    newCheck.checked = on;
    newFields.hidden = !on;
    clientCombo.input.disabled = on;
    clientCombo.input.placeholder = on ? 'Nouveau client (voir ci-dessous)' : 'Rechercher un client...';
    if (on) clientCombo.reset();
    requiredWhenNew.forEach(function (name) {
      var el = form.querySelector('[name="' + name + '"]');
      if (el) el.required = on;
    });
    if (on) { var first = form.querySelector('[name="nouveau_prenom"]'); if (first) first.focus(); }
  }
  form.querySelector('[data-new-client]').addEventListener('mousedown', function (e) { e.preventDefault(); clientCombo.close(); setNewClient(true); });
  form.querySelector('[data-cancel-new-client]').addEventListener('click', function () { setNewClient(false); clientCombo.input.focus(); });

  /* ---------- Détail du calcul ---------- */
  function calc() {
    var prix = num(chambreValue.getAttribute('data-prix'));
    var nuits = 0;
    var a = new Date(dateArr.value), d = new Date(dateDep.value);
    if (!isNaN(a) && !isNaN(d)) nuits = Math.max(0, Math.round((d - a) / 86400000));
    var services = Array.prototype.reduce.call(form.querySelectorAll('.service-checkbox:checked'), function (s, c) { return s + num(c.getAttribute('data-prix')); }, 0);
    document.getElementById('apercuNuits').textContent = nuits;
    document.getElementById('apercuPrixNuit').textContent = fmt(prix);
    document.getElementById('apercuTotalChambres').textContent = fmt(nuits * prix);
    document.getElementById('apercuTotalServices').textContent = fmt(services);
    document.getElementById('apercuTotal').textContent = fmt(nuits * prix + services);
  }
  form.addEventListener('combo-change', calc);
  [dateArr, dateDep].forEach(function (el) { el.addEventListener('change', calc); el.addEventListener('input', calc); });
  form.querySelectorAll('.service-checkbox').forEach(function (c) { c.addEventListener('change', calc); });

  /* Remise à zéro à chaque ouverture */
  document.querySelectorAll('[data-modal-open="#reservationModal"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      form.reset();
      combos.forEach(function (c) { c.reset(); });
      setNewClient(false);
      calc();
    });
  });

  setNewClient(false);
  calc();
})();
