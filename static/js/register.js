/* Page « Enregistrer votre hôtel » : parcours en 2 étapes, aide sur le mot de passe */
(function () {
  var form = document.getElementById('registerForm');
  if (!form) return;
  var panels = form.querySelectorAll('[data-panel]');
  var steps = document.querySelectorAll('#steps .step');
  var nom = document.getElementById('id_nom_etablissement');
  var username = document.getElementById('id_username');
  var pwd1 = document.getElementById('id_password1');
  var pwd2 = document.getElementById('id_password2');
  var meter = document.getElementById('pwdMeter');
  var rules = document.getElementById('pwdRules');
  var match = document.getElementById('pwdMatch');
  var courants = ['12345678', '123456789', 'azertyuiop', 'motdepasse', 'password', 'qwertyuiop', 'abcdefgh'];

  /* ---------- Étapes ---------- */
  function afficher(n) {
    panels.forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== String(n); });
    steps.forEach(function (s) {
      var i = Number(s.getAttribute('data-step'));
      s.classList.toggle('is-current', i === n);
      s.classList.toggle('is-done', i < n);
    });
    var premier = form.querySelector('[data-panel="' + n + '"] input:not([type=hidden])');
    if (premier) premier.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  form.querySelector('[data-next]').addEventListener('click', function () {
    if (!nom.value.trim()) {
      nom.classList.add('is-invalid');
      nom.focus();
      setTimeout(function () { nom.classList.remove('is-invalid'); }, 1500);
      return;
    }
    proposerIdentifiant();
    afficher(2);
  });
  form.querySelector('[data-prev]').addEventListener('click', function () { afficher(1); });
  steps.forEach(function (s) {
    s.addEventListener('click', function () {
      var n = Number(s.getAttribute('data-step'));
      if (n === 1 || nom.value.trim()) afficher(n);
    });
  });
  /* Formulaire renvoyé avec des erreurs : ouvrir l'étape concernée */
  if (form.querySelector('[data-panel="2"] .field-error')) afficher(2);

  /* ---------- Identifiant proposé d'après le nom de l'hôtel ---------- */
  var identifiantModifie = username.value !== '';
  username.addEventListener('input', function () { identifiantModifie = true; });
  function proposerIdentifiant() {
    if (identifiantModifie || !nom.value.trim()) return;
    username.value = nom.value
      .normalize('NFD').replace(/[̀-ͯ]/g, '')   // enlève les accents
      .toLowerCase().replace(/[^a-z0-9]+/g, '')
      .slice(0, 30);
  }

  /* ---------- Afficher / masquer les mots de passe ---------- */
  document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
    var champ = document.getElementById(btn.getAttribute('data-toggle-password'));
    btn.addEventListener('click', function () {
      var visible = champ.type === 'password';
      champ.type = visible ? 'text' : 'password';
      btn.querySelector('[data-eye]').hidden = visible;
      btn.querySelector('[data-eye-off]').hidden = !visible;
      btn.setAttribute('aria-label', visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe');
    });
  });

  /* ---------- Force du mot de passe (mêmes règles que le serveur) ---------- */
  function verifier() {
    var v = pwd1.value;
    var ok = {
      len: v.length >= 8,
      digit: !/^\d+$/.test(v),
      common: courants.indexOf(v.toLowerCase()) === -1 && v.length >= 8
    };
    rules.hidden = meter.hidden = v === '';
    rules.querySelectorAll('[data-rule]').forEach(function (li) {
      li.classList.toggle('is-ok', !!ok[li.getAttribute('data-rule')] && v !== '');
    });
    var score = (ok.len ? 1 : 0) + (ok.digit ? 1 : 0) + (ok.common ? 1 : 0) +
                (/[A-Z]/.test(v) && /[a-z]/.test(v) ? 1 : 0) + (v.length >= 12 ? 1 : 0);
    meter.className = 'pwd-meter niveau-' + Math.min(score, 4);
    meter.firstElementChild.style.width = Math.min(score, 4) * 25 + '%';
    comparer();
  }
  function comparer() {
    match.hidden = !(pwd2.value && pwd1.value === pwd2.value);
    pwd2.classList.toggle('is-invalid', !!pwd2.value && pwd1.value !== pwd2.value);
  }
  pwd1.addEventListener('input', verifier);
  pwd2.addEventListener('input', comparer);
})();
