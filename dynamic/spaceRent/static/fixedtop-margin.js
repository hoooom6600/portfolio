createBuffer();

window.addEventListener('resize', createBuffer);

function createBuffer() {
    let navbar = document.querySelector('#topMenu');
    let height = getComputedStyle(navbar).getPropertyValue('height');
    // console.log(height);
    let fixTopBuffer = document.querySelector('#fixTopBuffer');
    fixTopBuffer.style.marginTop = height;
}