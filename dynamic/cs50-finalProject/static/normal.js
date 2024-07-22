// initialization
// initialize all blocks (3x3)
let row_max = col_max = 3;
let slope = parseFloat(row_max / col_max);
let player_count = 2;
let blocks = [];
let tableBlocks = document.querySelector('#blocks');

for (let i = 0; i < row_max; i++) {
    let tr = document.createElement('tr');
    blocks[i] = [];
    for (let j = 0; j < col_max; j++) {
        blocks[i][j] = null;
        let td = document.createElement('td');
        td.classList.add('available');
        td.id = 'b' + i + j;
        tr.append(td);
    }
    let tbody = document.createElement('tbody');
    tbody.append(tr);
    tableBlocks.append(tbody);
}
for (let i = 0; i < row_max; i++) {
    for (let j = 0; j < col_max; j++) {
        document.querySelector('#b' + i + j).addEventListener('click', blocksChoose);
    }
}

// block clicking promise
let resolveClick;
let clickPromise = new Promise(resolve => {
    resolveClick = resolve;
});

// get operator remind text box
let operatorMsg = document.querySelector('#operator');

// initialize game status
let game_over = false;
let game_status = null;
let remain_blocks = row_max * col_max;
let time;

// 0 is player; 1 is computer
// current operator is assigned by getRandomInt
let operator = getRandomInt(player_count);

// play
main()

// submit record
let hasSubmit = false;
let submitBtn = document.querySelector('#submit');
let submitForm = document.querySelector('#submitForm');

submitForm.addEventListener('submit', function (event) {
    if (hasSubmit === true) {
        // refuse submit the form before alert but after clicking
        event.preventDefault();
        alert('One round can only be submitted one time.');
        return
    }
    if (document.querySelector('#name').value.trim() !== '') {
        hasSubmit = true;
        alert('Submit success!');
    }
})

// show records
let seeRecordBtn = document.querySelector('#seeRecords');
seeRecordBtn.addEventListener('click', seeRecords);
function seeRecords() {
    const records = fetch('/recordNormal')
        .then((res) => { return res.json() })
        .then((datas) => {
            if (datas.length === 0) {
                document.querySelector('#records').classList.add('m-0');
                document.querySelector('#records').innerHTML = '<p class="m-0">No any records. Be the first player now! :D</p>';
                return
            }
            document.querySelector('#records').classList.remove('m-0');
            let list = '';
            for (let data in datas) {
                list += '<tr><td>' + datas[data]['name'] + '</td>' + '<td>' + datas[data]['status'] + '</td>' + '<td>' + datas[data]['time'] + '</td></tr>'
            }

            let html = '<thead>\
                <tr>\
                    <th>Name</th>\
                    <th>Status</th>\
                    <th>Time</th>\
                </tr>\
            </thead>\
            <tbody>' + list + '</tbody>';

            document.querySelector('#records').innerHTML = html;
        })
        .catch((err) => { return alert('Sorry. The server is busy now. Please try again.') })
}

// tic-tac-toe logics
async function playing() {
    let timeStart = Date.now();
    do {
        await computersRound(blocks, operatorMsg);
        result();
        if (game_over) {
            break;
        }
        await playersRound(operatorMsg);
        result()
        if (game_over) {
            break;
        }
    } while (!game_over)
    let timeEnd = Date.now();

    // wait 0.75 sec to let player review the blocks for a while
    await (thinking(750))

    timePast(timeStart, timeEnd)
}

function showModal() {
    // result button only shows after game over
    let resultModalBtn = '<button class="btn btn-primary mt-3"\
    data-bs-target="#resultModal" data-bs-toggle="modal" id ="resultModalBtn">Result</button>';
    let btnPlacement = document.querySelector('.main');
    btnPlacement.innerHTML += resultModalBtn;
    document.querySelector('#status').textContent = game_status;
    if (game_status === 'Lose') {
        document.querySelector('#status').classList.add('text-danger');
    }
    if (game_status === 'Win') {
        document.querySelector('#status').classList.add('text-primary');
    }
    if (game_status === 'Tie') {
        document.querySelector('#status').classList.add('text-success');
    }


    document.querySelector('#timeSpend').textContent = time.min + ':' + time.sec + ':' + time.ms;

    document.querySelector('#recordTime').value = time.min + ':' + time.sec + ':' + time.ms;
    document.querySelector('#recordStatus').value = game_status;

    resultModalBtn = document.querySelector('#resultModalBtn');
    resultModalBtn.click();
}

async function computersRound(blocks, operatorMsg) {
    if (operator === 1) {
        for (let i = 0; i < row_max; i++) {
            for (let j = 0; j < col_max; j++) {
                document.querySelector('#b' + i + j).removeEventListener('click', blocksChoose);
                document.querySelector('#b' + i + j).classList.remove('available');
                if (document.querySelector('#b' + i + j).classList.length === 0) {
                    document.querySelector('#b' + i + j).removeAttribute('class');
                }
            }
        }

        operatorMsg.classList.remove('text-primary');
        operatorMsg.classList.add('text-danger');
        operatorMsg.textContent = "Computer is thinking."

        await thinking(2000);

        let i;
        let j;

        do {
            i = getRandomInt(row_max);
            j = getRandomInt(col_max);
        } while (blocks[i][j] !== null)


        if (blocks[i][j] === null) {

            blocks[i][j] = 'X';

            let chosen_block = document.querySelector('#b' + i + j);
            chosen_block.textContent = 'X';
            chosen_block.classList.remove('available');
            chosen_block.classList.add('text-danger');
            chosen_block.removeEventListener('click', blocksChoose);

            operator = switch_operator(operator);
            remain_blocks--;
        }
    }
}

async function playersRound(operatorMsg) {
    if (operator === 0) {
        for (let i = 0; i < row_max; i++) {
            for (let j = 0; j < col_max; j++) {
                if (blocks[i][j] === null) {
                    document.querySelector('#b' + i + j).addEventListener('click', blocksChoose);
                    document.querySelector('#b' + i + j).classList.add('available');
                }
            }
        }
        operatorMsg.classList.remove('text-danger');
        operatorMsg.classList.add('text-primary');
        operatorMsg.textContent = "Your round.";

        await clickPromise;

        clickPromise = new Promise(resolve => {
            resolveClick = resolve;
        });

        for (let i = 0; i < row_max; i++) {
            for (let j = 0; j < col_max; j++) {
                document.querySelector('#b' + i + j).removeEventListener('click', blocksChoose);
                document.querySelector('#b' + i + j).classList.remove('available');
                if (document.querySelector('#b' + i + j).classList.length === 0) {
                    document.querySelector('#b' + i + j).removeAttribute('class');
                }
            }
        }
    }
}

function result() {
    // row
    for (let i = 0; i < row_max; i++) {
        let row_symbols = ''
        for (let j = 0; j < col_max; j++) {
            if (blocks[i][j]) {
                row_symbols += blocks[i][j];
            }
            if (row_symbols.includes('O') && !row_symbols.includes('X') && row_symbols.length === col_max) {
                game_status = 'Win';
                game_over = true;
                break;
            }
            if (row_symbols.includes('X') && !row_symbols.includes('O') && row_symbols.length === col_max) {
                game_status = 'Lose';
                game_over = true;
                break;
            }
        }
    }

    // col
    for (let i = 0; i < col_max; i++) {
        let col_symbols = '';
        for (let j = 0; j < row_max; j++) {
            col_symbols += blocks[j][i];
            if (col_symbols.includes('O') && !col_symbols.includes('X') && col_symbols.length === row_max) {
                game_status = 'Win';
                game_over = true;
                break;
            }
            if (col_symbols.includes('X') && !col_symbols.includes('O') && col_symbols.length === row_max) {
                game_status = 'Lose';
                game_over = true;
                break;
            }
        }
    }

    // diagonal (left-top to right-bottom)
    let slide1_symbols = '';

    for (let i = 0; i < row_max; i++) {
        for (let j = i; j < col_max; j++) {
            slide1_symbols += blocks[i][j];
            break;
        }
        if (slide1_symbols.includes('O') && !slide1_symbols.includes('X') && slope === 1 && slide1_symbols.length === row_max) {
            game_status = 'Win';
            game_over = true;
            break;
        }
        if (slide1_symbols.includes('X') && !slide1_symbols.includes('O') && slope === 1 && slide1_symbols.length === row_max) {
            game_status = 'Lose';
            game_over = true;
            break;
        }
    }

    // diagonal (right-top to left-bottom)
    let slide2_symbols = '';

    for (let i = 0; i < row_max; i++) {
        for (let j = col_max - i - 1; j < col_max; j++) {
            slide2_symbols += blocks[i][j];
            break;
        }
        if (slide2_symbols.includes('O') && !slide2_symbols.includes('X') && slope === 1 && slide2_symbols.length === row_max) {
            game_status = 'Win';
            game_over = true;
            break;
        }
        if (slide2_symbols.includes('X') && !slide2_symbols.includes('O') && slope === 1 && slide2_symbols.length === row_max) {
            game_status = 'Lose';
            game_over = true;
            break;
        }
    }

    // tie
    if (remain_blocks === 0 && !game_over && !game_status) {
        game_status = 'Tie';
        game_over = true;
        operatorMsg.textContent = 'Tie';
        operatorMsg.classList.remove("text-primary");
        operatorMsg.classList.remove("text-danger");
        operatorMsg.classList.add("text-success");
    }

    // lose
    if (game_status === 'Lose') {
        operatorMsg.textContent = "Lose";
        operatorMsg.classList.remove("text-primary");
        operatorMsg.classList.remove("text-success");
        operatorMsg.classList.add("text-danger");
    }

    // win
    if (game_status === 'Win') {
        operatorMsg.textContent = "Win";
        operatorMsg.classList.remove("text-success");
        operatorMsg.classList.remove("text-danger");
        operatorMsg.classList.add("text-primary");
    }

    if (game_over && game_status) {
        for (let i = 0; i < row_max; i++) {
            for (let j = 0; j < col_max; j++) {
                document.querySelector('#b' + i + j).removeEventListener('click', blocksChoose);
                document.querySelector('#b' + i + j).classList.remove('available');
                if (document.querySelector('#b' + i + j).classList.length === 0) {
                    document.querySelector('#b' + i + j).removeAttribute('class');
                }
            }
        }
    }
}


function thinking(delayTime) {
    return new Promise(resolve => setTimeout(resolve, delayTime));
}

function timePast(start, end) {
    let past = end - start;
    let ms = (Math.round(past % 1000 / 10)).toString().padStart(2, '0');
    let sec = (Math.floor(past / 1000 % 60)).toString().padStart(2, '0');
    let min = (Math.floor(past / 1000 / 60)).toString().padStart(2, '0');
    time = {
        past: past,
        ms: ms,
        sec: sec,
        min: min
    }
}

// click event listeners functions
// blocks choosing
function blocksChoose() {
    let self = this;
    let clickedId = self.id.replace('b', '');
    let isAvailable = self.classList.contains('available');
    if (blocks[clickedId[0]][clickedId[1]] !== null && !isAvailable) {
        alert('This block has been occupied. Please take another one.')
        return;
    }
    if (blocks[clickedId[0]][clickedId[1]] === null && isAvailable) {
        blocks[clickedId[0]][clickedId[1]] = 'O';
        self.classList.remove('available');
        if (self.classList.length === 0) {
            self.removeAttribute('class');
        }
        self.removeEventListener('click', blocksChoose);
        self.textContent = 'O';
        self.classList.remove('available');
        self.classList.add('text-primary');

        operator = switch_operator(operator);

        remain_blocks--;

        resolveClick();
    }
}

// to determine who go first and the computer picks his blocks choice
function getRandomInt(max) {
    return Math.floor(Math.random() * max)
}

// for player and computer take turns
function switch_operator(operator) {
    return operator === 1 ? 0 : 1;
}

async function main() {
    await playing();
    showModal();
}

// theme mode switch
let lightModeBtn = document.querySelector('#lightModeBtn');
let darkModeBtn = document.querySelector('#darkModeBtn');
let htmlTag = document.documentElement;

lightModeBtn.addEventListener('click', function () {
    htmlTag.removeAttribute('data-bs-theme');
    localStorage.setItem('colorMode', 'light');
})

darkModeBtn.addEventListener('click', function () {
    htmlTag.setAttribute('data-bs-theme', 'dark');
    localStorage.setItem('colorMode', 'dark');
})

let colorMode = localStorage.getItem('colorMode');
if (colorMode === 'light') {
    htmlTag.removeAttribute('data-bs-theme');
}
// default color mode is dark
else {
    htmlTag.setAttribute('data-bs-theme', 'dark');
}
