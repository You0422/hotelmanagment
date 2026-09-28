/* Dépenses : champ « Précisez la catégorie » quand « Autres » est choisi */
(function () {
  'use strict';
  document.querySelectorAll('.js-cat-select').forEach(function (select) {
    var form = select.closest('form');
    if (!form) return;
    var field = form.querySelector('.js-autre-field');
    var input = form.querySelector('.js-autre-input');
    if (!field || !input) return;

    // Catégorie personnalisée existante : on présélectionne « Autres » et on reprend son nom
    var current = select.getAttribute('data-current');
    if (current && !Array.prototype.some.call(select.options, function (o) { return o.value === current; })) {
      select.value = 'Autres';
      input.value = current;
    }

    function toggle() {
      var autre = select.value === 'Autres';
      field.hidden = !autre;
      input.required = autre;
      if (!autre) input.value = '';
    }
    select.addEventListener('change', toggle);
    toggle();
  });
})();
