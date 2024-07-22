/* for index.html events section css */
moveAndPad();

window.addEventListener('resize', moveAndPad);

function moveAndPad() {
    let square = document.querySelector('.events .square-background');
    if (square) {
        let squareSide = parseInt(getComputedStyle(square).getPropertyValue('height').replace('px', ''));
        let center = squareSide / 2;
        let diagonal = Math.ceil(Math.sqrt((squareSide ** 2) + (squareSide ** 2)));
        let outer = (diagonal - squareSide) / 2;

        let imgs = document.querySelectorAll('.events img');

        for (let i = 0; i < imgs.length; i++) {
            imgs[i].style.left = center + 'px';
            imgs[i].style.top = center + 'px';
        }

        let aS = document.querySelectorAll('.events .row a');

        for (let i = 0; i < aS.length; i++) {
            aS[i].style.paddingRight = center + 'px';
            aS[i].style.paddingBottom = center + 'px';
            aS[i].style.paddingLeft = outer + 'px';
            aS[i].style.paddingTop = outer + 'px';

            // console.log(aS[i].style.paddingRight)
            // console.log(aS[i].style.paddingBottom)
            // console.log(aS[i].style.paddingLeft)
            // console.log(aS[i].style.paddingTop)
        }
    }
}
