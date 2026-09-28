/* HotelManagment — interactions de l'interface (menu mobile, fenêtres modales, messages) */
(function () {
  'use strict';

  /* ---------- Menu latéral (mobile) ---------- */
  var sidebar = document.getElementById('sidebar');
  var backdrop = document.getElementById('sidebarBackdrop');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('is-open');
    if (backdrop) backdrop.classList.add('is-open');
  }
  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('is-open');
    if (backdrop) backdrop.classList.remove('is-open');
  }

  /* ---------- Fenêtres modales ---------- */
  function openModal(modal) {
    if (!modal) return;
    modal.classList.add('is-open');
    document.body.classList.add('modal-open');
    var focusable = modal.querySelector('input:not([type=hidden]), select, textarea, button');
    if (focusable) setTimeout(function () { focusable.focus(); }, 30);
  }
  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove('is-open');
    if (!document.querySelector('.modal.is-open')) document.body.classList.remove('modal-open');
  }
  function targetOf(el) {
    var sel = el.getAttribute('data-modal-open') || el.getAttribute('data-bs-target');
    if (!sel) return null;
    return document.querySelector(sel.charAt(0) === '#' ? sel : '#' + sel);
  }

  document.addEventListener('click', function (e) {
    var el;

    if ((el = e.target.closest('[data-sidebar-open]'))) { openSidebar(); return; }
    if ((el = e.target.closest('[data-sidebar-close]'))) { closeSidebar(); return; }

    if ((el = e.target.closest('[data-modal-open], [data-bs-toggle="modal"]'))) {
      e.preventDefault();
      var current = el.closest('.modal');
      if (current && el.hasAttribute('data-modal-swap')) closeModal(current);
      openModal(targetOf(el));
      return;
    }
    if ((el = e.target.closest('[data-modal-close], [data-bs-dismiss="modal"]'))) {
      e.preventDefault();
      closeModal(el.closest('.modal'));
      return;
    }
    if (e.target.classList && e.target.classList.contains('modal')) {
      closeModal(e.target);
      return;
    }
    if ((el = e.target.closest('[data-alert-close], [data-bs-dismiss="alert"]'))) {
      var alert = el.closest('.alert');
      if (alert) alert.remove();
    }
  });

  /* Les messages de succès / info disparaissent seuls ; les erreurs restent jusqu'au clic */
  function dismissAlert(alert) {
    alert.classList.add('is-leaving');
    setTimeout(function () { alert.remove(); }, 400);
  }
  document.querySelectorAll('.alert-success, .alert-info').forEach(function (alert) {
    var timer = setTimeout(function () { dismissAlert(alert); }, 4000);
    alert.addEventListener('mouseenter', function () { clearTimeout(timer); alert.classList.add('is-paused'); });
    alert.addEventListener('mouseleave', function () {
      alert.classList.remove('is-paused');
      timer = setTimeout(function () { dismissAlert(alert); }, 2000);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelectorAll('.modal.is-open');
    if (open.length) closeModal(open[open.length - 1]);
    else closeSidebar();
  });

  /* Confirmation avant envoi (ex. check-out, annulation) */
  document.addEventListener('submit', function (e) {
    var msg = e.target.getAttribute('data-confirm');
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  /* Ouvre automatiquement une modale (ex. formulaire renvoyé avec erreurs) */
  document.querySelectorAll('.modal[data-auto-open]').forEach(openModal);

  window.addEventListener('resize', function () {
    if (window.innerWidth >= 768) closeSidebar();
  });

  /* ---------- Listes avec recherche (même rendu que la démo) ----------
     <div class="hm-combo" data-combo> : input caché [data-combo-value], champ [data-combo-input],
     menu [data-combo-menu] avec des <li data-value data-label>, message [data-combo-empty].
     Déclenche l'événement « combo-change » sur la boîte à chaque choix. */
  function setupCombo(box) {
    if (box.hmCombo) return box.hmCombo;
    var hidden = box.querySelector('[data-combo-value]');
    var input = box.querySelector('[data-combo-input]');
    var menu = box.querySelector('[data-combo-menu]');
    var empty = box.querySelector('[data-combo-empty]');
    var chevron = box.querySelector('.hm-combo-chevron');
    var items = Array.prototype.slice.call(box.querySelectorAll('li[data-value]'));
    var active = -1;

    function visible() { return items.filter(function (li) { return !li.hidden; }); }
    function notify() { box.dispatchEvent(new Event('combo-change', { bubbles: true })); }
    function open() { menu.hidden = false; box.classList.add('is-open'); }
    function close() { menu.hidden = true; box.classList.remove('is-open'); setActive(-1); }
    function setActive(i) {
      var vis = visible();
      items.forEach(function (li) { li.classList.remove('is-active'); });
      active = i;
      if (vis[i]) { vis[i].classList.add('is-active'); vis[i].scrollIntoView({ block: 'nearest' }); }
    }
    function filter() {
      var q = hidden.value ? '' : input.value.trim().toLowerCase();
      items.forEach(function (li) { li.hidden = !!q && li.textContent.toLowerCase().indexOf(q) === -1; });
      if (empty) empty.hidden = visible().length > 0;
      setActive(-1);
    }
    function choose(li) {
      hidden.value = li.getAttribute('data-value');
      hidden.setAttribute('data-prix', li.getAttribute('data-prix') || '');
      input.value = li.getAttribute('data-label');
      items.forEach(function (x) { x.classList.toggle('is-selected', x === li); });
      close();
      notify();
    }
    function select(value) {
      var li = items.filter(function (x) { return x.getAttribute('data-value') === String(value); })[0];
      if (li) choose(li); else reset();
    }
    function reset() {
      hidden.value = ''; hidden.removeAttribute('data-prix'); input.value = '';
      items.forEach(function (x) { x.classList.remove('is-selected'); x.hidden = false; });
      if (empty) empty.hidden = items.length > 0;
      close();
    }

    input.addEventListener('focus', function () { filter(); open(); });
    input.addEventListener('click', open);
    input.addEventListener('input', function () {
      if (hidden.value) { hidden.value = ''; hidden.removeAttribute('data-prix'); notify(); }
      filter(); open();
    });
    input.addEventListener('keydown', function (e) {
      var vis = visible();
      if (e.key === 'ArrowDown') { e.preventDefault(); open(); setActive(Math.min(active + 1, vis.length - 1)); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(Math.max(active - 1, 0)); }
      else if (e.key === 'Enter' && !menu.hidden) { e.preventDefault(); if (vis[Math.max(active, 0)]) choose(vis[Math.max(active, 0)]); }
      else if (e.key === 'Escape' && !menu.hidden) { e.stopPropagation(); close(); }
      else if (e.key === 'Tab') close();
    });
    if (chevron) chevron.addEventListener('mousedown', function (e) {
      e.preventDefault();
      if (menu.hidden) { input.focus(); open(); } else close();
    });
    items.forEach(function (li) {
      li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(li); });
    });
    document.addEventListener('mousedown', function (e) { if (!box.contains(e.target)) close(); });

    /* Un choix dans la liste est obligatoire si la boîte porte data-combo-required */
    var form = box.closest('form');
    if (form && box.hasAttribute('data-combo-required')) {
      form.addEventListener('submit', function (e) {
        if (hidden.value || input.disabled) return;
        e.preventDefault();
        e.stopImmediatePropagation();
        box.classList.add('is-invalid');
        input.focus();
        setTimeout(function () { box.classList.remove('is-invalid'); }, 1500);
      }, true);
    }

    if (hidden.value) select(hidden.value);
    box.hmCombo = { box: box, hidden: hidden, input: input, reset: reset, close: close, select: select };
    return box.hmCombo;
  }
  document.querySelectorAll('[data-combo]').forEach(setupCombo);

  window.HM = { openModal: openModal, closeModal: closeModal, combo: setupCombo };
})();
