document.addEventListener('DOMContentLoaded', function () {
    var menuToggle = document.getElementById('menuToggle');
    var sidebar = document.getElementById('sidebar');
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
        document.addEventListener('click', function (e) {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuToggle) {
                sidebar.classList.remove('open');
            }
        });
    }
});

function cloneTemplateInto(templateId, containerId) {
    var tpl = document.getElementById(templateId);
    var container = document.getElementById(containerId);
    if (tpl && container) {
        container.appendChild(tpl.content.cloneNode(true));
    }
}

function addIngredientRow() {
    cloneTemplateInto('ingredientRowTemplate', 'ingredientRows');
}

function addStepRow() {
    cloneTemplateInto('stepRowTemplate', 'stepRows');
}

function addOrderRow() {
    cloneTemplateInto('orderRowTemplate', 'orderRows');
}

function removeRow(btn) {
    var row = btn.closest('.dynamic-row');
    if (row) {
        row.remove();
    }
}
