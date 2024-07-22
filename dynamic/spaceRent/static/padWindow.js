padWindow();

window.addEventListener('resize', padWindow);

function padWindow() {
    let footer = document.querySelector('footer');
    let footerHeight = getComputedStyle(footer).getPropertyValue('height');
    let navbar = document.querySelector('#topMenu');
    let navbarHeight = getComputedStyle(navbar).getPropertyValue('height');

    let main = document.querySelector('main');
    main.style.minHeight = 'calc(100vh - ' + footerHeight + ' - ' + navbarHeight + ')';
}