// Dependent district dropdown: when a province <select> changes, load districts.
document.addEventListener("DOMContentLoaded", function () {
  const provinceSelects = document.querySelectorAll("select[name='province']");
  provinceSelects.forEach(function (sel) {
    const form = sel.closest("form");
    if (!form) return;
    const districtField = form.querySelector("[name='district']");
    if (!districtField) return;

    async function loadDistricts(keepValue) {
      const province = sel.value;
      if (!province || province === "ALL") return;
      try {
        const resp = await fetch(
          "/api/districts/?province=" + encodeURIComponent(province)
        );
        const data = await resp.json();
        if (!data.districts || data.districts.length === 0) return;
        // Convert text input into a datalist-backed input for suggestions.
        let listId = "district-list";
        let datalist = document.getElementById(listId);
        if (!datalist) {
          datalist = document.createElement("datalist");
          datalist.id = listId;
          document.body.appendChild(datalist);
        }
        datalist.innerHTML = "";
        data.districts.forEach(function (d) {
          const opt = document.createElement("option");
          opt.value = d;
          datalist.appendChild(opt);
        });
        districtField.setAttribute("list", listId);
        if (!keepValue) districtField.value = "";
      } catch (e) {
        console.warn("İlçe listesi yüklenemedi", e);
      }
    }

    sel.addEventListener("change", function () { loadDistricts(false); });
    loadDistricts(true);
  });
});
