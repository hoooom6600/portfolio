let serverZone = -480; // server time is at Taiwan (UTC+8)
serverZone = -540; // take UTC+9 (like: jp, kr) for example
serverZone = -420; // take UTC+7 (like: th, vn) for example

let lag = document.querySelector('#lag');
if (lag) {
    // lag > 0 means user local time zone is later than server time zone
    lag.value = -(new Date().getTimezoneOffset() - serverZone) * 60 * 1000; // in milliseconds format
}

let tzoffset = (new Date()).getTimezoneOffset() * 60000; // offset in milliseconds
let localISOTime = (new Date(Date.now() - tzoffset)).toISOString();
let ISO0time = (new Date(Date.now())).toISOString();

let date = new Date(Date.now() - tzoffset - (Date.now() % (60 * 1000))); // unify in seconds
let minutes = date.getMinutes();

if (minutes >= 0 && minutes < 30) {
    date.setMinutes(30);
}
if (minutes > 30) {
    date.setMinutes(0);
    date.setHours(date.getHours() + 1);
}

let limit = date.toISOString();

console.log(limit)

/* index.html & result.html search */
let dateStart = document.querySelector('#dateStart');
let dateEnd = document.querySelector('#dateEnd');
if (dateStart && dateEnd) {
    dateStart.min = limit.slice(0, -8);
    dateEnd.min = limit.slice(0, -8);

    // check if need to change limit time every 1 minute pasts
    setInterval(function () {
        date = new Date(Date.now() - tzoffset - (Date.now() % (60 * 1000)));
        minutes = date.getMinutes();
        if (minutes >= 0 && minutes < 30) {
            date.setMinutes(30);
        }
        if (minutes > 30) {
            date.setMinutes(0);
            date.setHours(date.getHours() + 1);
        }

        limit = date.toISOString();
        dateStart.min = limit.slice(0, -8);
        dateEnd.min = limit.slice(0, -8);

        console.log(limit)
    }, 60000)
}


/* signup.html */
let birthday = document.querySelector('#floatingBirthday');
if (birthday) {
    birthday.max = localISOTime.split('T')[0];
}

