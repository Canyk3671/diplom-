// Переключение вкладок
function switchTab(tab) {
    var buttons = document.querySelectorAll('.tab-button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active');
    }
    var contents = document.querySelectorAll('.tab-content');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }
    var activeBtn = document.querySelector('[onclick="switchTab(\'' + tab + '\')"]');
    if (activeBtn) activeBtn.classList.add('active');
    var activeTab = document.getElementById('tab-' + tab);
    if (activeTab) activeTab.style.display = 'block';
}

// Построение сетки с нулями
function buildMatrixGridDefault(player, prefix) {
    var rowsEl = document.getElementById(prefix + 'rows' + player);
    var colsEl = document.getElementById(prefix + 'cols' + player);
    var grid = document.getElementById(prefix + 'grid' + player);
    if (!rowsEl || !colsEl || !grid) return;

    var rows = parseInt(rowsEl.value) || 2;
    var cols = parseInt(colsEl.value) || 2;
    grid.innerHTML = '';

    for (var i = 0; i < rows; i++) {
        var rowDiv = document.createElement('div');
        rowDiv.style.display = 'flex';
        for (var j = 0; j < cols; j++) {
            var input = document.createElement('input');
            input.type = 'number';
            input.step = 'any';
            input.value = '0';
            input.setAttribute('data-row', i);
            input.setAttribute('data-col', j);
            input.style.cssText = 'width:60px;padding:8px;text-align:center;margin:2px;border:1px solid #ccc;border-radius:4px;';
            rowDiv.appendChild(input);
        }
        grid.appendChild(rowDiv);
    }
}

// Заполнение сетки из JSON-строки
function fillGridFromJson(player, prefix, jsonStr) {
    if (!jsonStr || jsonStr === '') return false;
    try {
        var data = JSON.parse(jsonStr);
        var rowsEl = document.getElementById(prefix + 'rows' + player);
        var colsEl = document.getElementById(prefix + 'cols' + player);
        var grid = document.getElementById(prefix + 'grid' + player);
        if (!rowsEl || !colsEl || !grid) return false;

        rowsEl.value = data.length;
        colsEl.value = data[0] ? data[0].length : 0;

        grid.innerHTML = '';
        for (var i = 0; i < data.length; i++) {
            var rowDiv = document.createElement('div');
            rowDiv.style.display = 'flex';
            for (var j = 0; j < data[i].length; j++) {
                var input = document.createElement('input');
                input.type = 'number';
                input.step = 'any';
                input.value = data[i][j];
                input.setAttribute('data-row', i);
                input.setAttribute('data-col', j);
                input.style.cssText = 'width:60px;padding:8px;text-align:center;margin:2px;border:1px solid #ccc;border-radius:4px;';
                rowDiv.appendChild(input);
            }
            grid.appendChild(rowDiv);
        }
        return true;
    } catch(e) {
        console.log('Error parsing JSON:', e);
        return false;
    }
}

function buildMainGrid() {
    var matrixA = document.getElementById('matrix_a');
    var matrixB = document.getElementById('matrix_b');

    var filledA = fillGridFromJson('A', '', matrixA ? matrixA.value : '');
    if (!filledA) buildMatrixGridDefault('A', '');

    var filledB = fillGridFromJson('B', '', matrixB ? matrixB.value : '');
    if (!filledB) buildMatrixGridDefault('B', '');
}

function buildCompareGrid() {
    var matrixA = document.getElementById('comp_matrix_a');
    var matrixB = document.getElementById('comp_matrix_b');

    var filledA = fillGridFromJson('A', 'comp_', matrixA ? matrixA.value : '');
    if (!filledA) buildMatrixGridDefault('A', 'comp_');

    var filledB = fillGridFromJson('B', 'comp_', matrixB ? matrixB.value : '');
    if (!filledB) buildMatrixGridDefault('B', 'comp_');
}

function collectMatrix(player, prefix) {
    var rowsEl = document.getElementById(prefix + 'rows' + player);
    var colsEl = document.getElementById(prefix + 'cols' + player);
    var grid = document.getElementById(prefix + 'grid' + player);
    if (!rowsEl || !colsEl || !grid) return [[0]];

    var rows = parseInt(rowsEl.value) || 2;
    var cols = parseInt(colsEl.value) || 2;
    var matrix = [];
    for (var i = 0; i < rows; i++) {
        var row = [];
        for (var j = 0; j < cols; j++) {
            var input = grid.querySelector('input[data-row="' + i + '"][data-col="' + j + '"]');
            row.push(input ? (parseFloat(input.value) || 0) : 0);
        }
        matrix.push(row);
    }
    return matrix;
}

function submitMainForm() {
    document.getElementById('matrix_a').value = JSON.stringify(collectMatrix('A', ''));
    document.getElementById('matrix_b').value = JSON.stringify(collectMatrix('B', ''));
    return true;
}

function submitCompareForm() {
    document.getElementById('comp_matrix_a').value = JSON.stringify(collectMatrix('A', 'comp_'));
    document.getElementById('comp_matrix_b').value = JSON.stringify(collectMatrix('B', 'comp_'));
    return true;
}

// Инициализация при загрузке страницы
(function() {
    // Ждём загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            buildMainGrid();
            buildCompareGrid();
        });
    } else {
        buildMainGrid();
        buildCompareGrid();
    }
})();