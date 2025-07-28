let worldPopulation = 0;
let country = [];
let sortCountry = [];

const world = fetch('https://restcountries.com/v3.1/all?fields=name,population,flags')
    .then((res) => {
        console.log(res.ok);
        if (!res.ok) {
            console.log(res.status);
        }
        return res.json()
    })
    .catch((err) => {
        console.log(err);
        return alert('Sorry. The server is busy now. Please try again.')
    })
    .then((countries) => {
        console.log(countries)

        // calculate world population
        for (let index in countries) {
            worldPopulation = worldPopulation + parseInt(countries[index].population);
        }

        // calculate each country population percentage of the whole world's
        for (let index in countries) {
            let percent = parseFloat((countries[index].population / worldPopulation).toFixed(10));
            let eachCountry = {
                officialName: countries[index].name.official,
                commonName: countries[index].name.common,
                population: countries[index].population,
                percentage: percent, // * 100 + '%',
                flag: countries[index].flags.svg
            }
            country.push(eachCountry);
        }

        // sort by the population and from large to small
        sortCountry = country.sort((a, b) => {
            return b.population - a.population
        })
        console.log(sortCountry);

        // angle degree to each country
        let angle = 0;
        for (let index in sortCountry) {
            angle = angle + (sortCountry[index].percentage * 360);
            sortCountry[index].angle = angle;
        }

        // list chances
        let list = document.querySelector('.chance')
        for (let index in sortCountry) {
            let listItem = document.createElement('li');
            let country = document.createElement('span');
            let countryName = document.createElement('span');
            let flag = document.createElement('img');
            flag.setAttribute('src', sortCountry[index].flag);
            flag.setAttribute('width', '60px');
            flag.setAttribute('height', '40px');

            countryName.textContent = sortCountry[index].officialName;

            let chance = document.createElement('span');
            chance.textContent = (sortCountry[index].percentage * 100).toFixed(3) + '%';

            country.append(flag);
            country.append(countryName);
            listItem.append(country);
            listItem.append(chance);
            list.append(listItem);
        }


        // draw pie chart
        const ctx = document.getElementById('myChart');

        let labelCountryCommonName = [];
        let dataPopulation = [];
        let labelTop10Flag = [];

        for (let index in sortCountry) {
            dataPopulation.push(sortCountry[index].population);
            labelCountryCommonName.push(sortCountry[index].commonName);

            // flag & flag size
            if (index < 9) {
                let flag = {
                    src: `${sortCountry[index].flag}`,
                    width: 18,
                    height: 12
                };
                if (index < 4) {
                    flag.width = 30;
                    flag.height = 20;
                }
                if (index < 2) {
                    flag.width = 60;
                    flag.height = 40;
                }
                labelTop10Flag.push(flag);
            }
        }

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labelCountryCommonName,

                datasets: [{
                    label: 'population',
                    data: dataPopulation,
                    borderWidth: 0,
                },
                ]
            },
            options: {
                plugins: {
                    legend: {
                        display: false,
                    },
                    labels: [{
                        render: 'label',
                        position: 'inside',
                        fontSize: 20,
                        overlap: false,
                        fontColor: '#eee',
                    },
                    {
                        render: 'image',
                        images: labelTop10Flag,
                        position: 'border'
                    }
                    ],
                    tooltip: {
                        titleFont: {
                            size: 22
                        },
                    },
                },
                layout: {
                    padding: 0
                },

                maintainAspectRatio: false
            },

        });

    })

let counterclockwiseBtn = document.querySelector('#counterclockwise');
let clockwiseBtn = document.querySelector('#clockwise');
let chart = document.querySelector('#myChart');
let result = document.querySelector('.country-name')

// create random number from min(included) to max
// source code: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random#getting_a_random_number_between_two_values

function randomAngle(max, direction) {
    // at least max rounds

    if (direction === 'counterclockwise') {
        return -(360 * max) + (Math.random() * 360);
    }
    if (direction === 'clockwise') {
        return (360 * max) + (360 - (Math.random() * 360));
    }
}

let previousAngle = 0;

clockwiseBtn.addEventListener('click', function () {
    let angle = randomAngle(10, 'clockwise');

    // from counterclockwise click to clockwise
    if (previousAngle < 0) {
        previousAngle = 0;
    }

    // to make spin direction always the same
    angle = previousAngle + angle;

    previousAngle = angle;
    // HTML & CSS
    chart.style.transform = `rotate(${angle}deg)`;
    clockwiseBtn.style.cursor = 'not-allowed';
    clockwiseBtn.setAttribute('disabled', '');
    counterclockwiseBtn.style.cursor = 'not-allowed';
    counterclockwiseBtn.setAttribute('disabled', '');

    setTimeout(() => {
        let cycle;

        // clockwise
        if (angle > 0) {
            cycle = {
                name: "I'm spin cycle",
                angle: Math.abs(360 - (angle % 360))
            }
        }

        console.log(angle)
        console.log(cycle.angle)

        // HTML & CSS
        clockwiseBtn.removeAttribute('style');
        clockwiseBtn.removeAttribute('disabled');
        counterclockwiseBtn.removeAttribute('style');
        counterclockwiseBtn.removeAttribute('disabled');


        // check country
        for (let index in sortCountry) {
            if (cycle.angle < sortCountry[index].angle) {

                result.textContent = sortCountry[index].officialName;
                break;
            }
        }
    }, 5000)

});


counterclockwiseBtn.addEventListener('click', function () {
    let angle = randomAngle(10, 'counterclockwise');

    // from clockwise click to counterclockwise
    if (previousAngle > 0) {
        previousAngle = 0;
    }

    // to make spin direction always the same
    angle = previousAngle + angle;

    previousAngle = angle;

    // HTML & CSS
    chart.style.transform = `rotate(${angle}deg)`;
    counterclockwiseBtn.style.cursor = 'not-allowed';
    counterclockwiseBtn.setAttribute('disabled', '');
    clockwiseBtn.style.cursor = 'not-allowed';
    clockwiseBtn.setAttribute('disabled', '');

    setTimeout(() => {
        let cycle;

        // counterclockwise
        if (angle < 0) {
            cycle = {
                name: "I'm spin cycle",
                angle: Math.abs(0 - (angle / 360 % 1 * 360))
            }
        }

        console.log(angle)
        console.log(cycle.angle)

        // HTML & CSS
        counterclockwiseBtn.removeAttribute('style');
        counterclockwiseBtn.removeAttribute('disabled');
        clockwiseBtn.removeAttribute('style');
        clockwiseBtn.removeAttribute('disabled');


        // check country
        for (let index in sortCountry) {
            if (cycle.angle < sortCountry[index].angle) {

                result.textContent = sortCountry[index].officialName;
                break;
            }
        }
    }, 5000)

})
