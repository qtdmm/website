// Client-side filter for the supported-meters table. The table is complete
// without JavaScript; this only hides rows.
(function () {
  var q = document.getElementById('meter-filter');
  var v = document.getElementById('vendor-filter');
  var count = document.getElementById('meter-count');
  var rows = Array.prototype.slice.call(document.querySelectorAll('#meters tbody tr'));
  function apply() {
    var text = q.value.trim().toLowerCase();
    var vendor = v.value;
    var shown = 0;
    rows.forEach(function (tr) {
      var ok = (!vendor || tr.getAttribute('data-vendor') === vendor) &&
               (!text || tr.textContent.toLowerCase().indexOf(text) !== -1);
      tr.style.display = ok ? '' : 'none';
      if (ok) shown++;
    });
    count.textContent = shown + ' of ' + rows.length;
  }
  // ?vendor=Fluke (from the vendor cloud on the home page) preselects a vendor
  var want = new URLSearchParams(location.search).get('vendor');
  if (want) {
    for (var i = 0; i < v.options.length; i++) if (v.options[i].value === want) { v.value = want; break; }
  }
  q.addEventListener('input', apply);
  v.addEventListener('change', apply);
  apply();
})();
