let order_start = document.querySelector('#dateStart');
let order_end = document.querySelector('#dateEnd');

calculate_total();

order_start.addEventListener('change', calculate_total);
order_end.addEventListener('change', calculate_total);


function calculate_total() {
    let duration = new Date(order_end.value) - new Date(order_start.value);
    duration = Math.ceil(duration / 1000 / 60 / 60);
    console.log(duration);

    let per_price = parseInt(document.querySelector('#price').textContent);
    let total = duration * per_price;

    document.querySelector('#total').value = total;
}

