// initialization
// initialize all blocks (3x3)
let row_max = col_max = 3;
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
        document.querySelector('#b' + i + j).addEventListener('click', clickEvent);
    }
}


// get operator remind text box
let operatorMsg = document.querySelector('#operator');

// initialize game status
let game_over = false;
let game_status = null;
let remain_blocks = row_max * col_max;

// game starts and plays
// determine who goes first
// 0 is player; 1 is computer
let operator = getRandomInt(player_count);
// operator = 1;
console.log('first operator: ' + operator)

// A and B takes turns
playing();

async function playing() {
    do {
        await computersRound(blocks, operatorMsg);
        result();
        if (game_over) {
            break;
        }
        await playersRound(blocks, operatorMsg);
        result()
        if (game_over) {
            break;
        }
    } while (!game_over)
    console.log(game_over)
    console.log(game_status)
}








// submit record

// show records



function getRandomInt(max) {
    return Math.floor(Math.random() * max)
}

function clickEvent() {
    this.classList.remove('available');
    if (this.classList.length === 0) {
        this.removeAttribute('class');
    }
    this.removeEventListener('click', clickEvent);

    // switch operator
    if (!game_over) {
        if (operator === 1) {
            operator = 0;
        }
        else {
            operator = 1;
        }
        remain_blocks--;
    }
    console.log('operator: ' + operator)
    console.log('remain blocks: ' + remain_blocks)
}

async function computersRound(blocks, operatorMsg) {
    if (operator === 1) {
        operatorMsg.classList.remove('text-primary');
        operatorMsg.classList.add('text-danger');
        operatorMsg.textContent = "Computer is thinking."

        await thinking(2000);

        let i;
        let j;

        do {
            i = getRandomInt(row_max);
            j = getRandomInt(col_max);
            console.log('not sure computer: ' + i + ',' + j);
        } while (blocks[i][j] !== null)

        console.log('computer: ' + i + ',' + j);


        if (blocks[i][j] === null) {

            blocks[i][j] = 'X';

            let chosen_block = document.querySelector('#b' + i + j);
            chosen_block.textContent = 'X';
            chosen_block.classList.remove('available');
            chosen_block.classList.add('text-danger');
            chosen_block.removeEventListener('click', clickEvent);

            operator = switch_operator(operator);
            remain_blocks--;

        }
    }
    else {
        return
    }
}

async function playersRound(blocks, operatorMsg) {
    if (operator === 0) {
        operatorMsg.classList.remove('text-danger');
        operatorMsg.classList.add('text-primary');
        operatorMsg.textContent = "Your round."

        await thinking(2000)

        let i;
        let j;

        do {
            i = getRandomInt(row_max);
            j = getRandomInt(col_max);
            console.log('not sure player: ' + i + ',' + j);
        } while (blocks[i][j] !== null)

        console.log('player: ' + i + ',' + j);


        if (blocks[i][j] === null) {
            blocks[i][j] = 'O';

            let chosen_block = document.querySelector('#b' + i + j);
            chosen_block.textContent = 'O';
            chosen_block.classList.remove('available');
            chosen_block.classList.add('text-primary');

            operator = switch_operator(operator);
            remain_blocks--;
        }
    }
    else {
        return
    }
}

function thinking(delayTime) {
    return new Promise(resolve => setTimeout(resolve, delayTime));
}

function switch_operator(operator) {
    return operator === 1 ? 0 : 1;
}

function result() {
    for (let i = 0; i < row_max; i++) {
        // row
        if (blocks[i][col_max - 3] === 'X' && blocks[i][col_max - 2] === 'X' && blocks[i][col_max - 1] === 'X') {
            game_status = 'Lose';
            game_over = true;
        }
        if (blocks[i][col_max - 3] === 'O' && blocks[i][col_max - 2] === 'O' && blocks[i][col_max - 1] === 'O') {
            game_status = 'Win';
            game_over = true;
        }

        // col
        if (blocks[row_max - 3][i] === 'X' && blocks[row_max - 2][i] === 'X' && blocks[row_max - 1][i] === 'X') {
            game_status = 'Lose';
            game_over = true;
        }
        if (blocks[row_max - 3][i] === 'O' && blocks[row_max - 2][i] === 'O' && blocks[row_max - 1][i] === 'O') {
            game_status = 'Win';
            game_over = true;
        }
    }
    // diagonal (left-top to right-bottom)
    if (blocks[0][0] === 'X' && blocks[1][1] === 'X' && blocks[2][2] === 'X') {
        game_status = 'Lose';
        game_over = true;
    }
    if (blocks[0][0] === 'O' && blocks[1][1] === 'O' && blocks[2][2] === 'O') {
        game_status = 'Win';
        game_over = true;
    }

    // diagonal (right-top to left-bottom)
    if (blocks[0][2] === 'X' && blocks[1][1] === 'X' && blocks[2][0] === 'X') {
        game_status = 'Lose';
        game_over = true;
    }
    if (blocks[0][2] === 'O' && blocks[1][1] === 'O' && blocks[2][0] === 'O') {
        game_status = 'Win';
        game_over = true;
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
}
