// only in index.html
let cmModalOpenBtn = document.querySelector('#cmModalOpenBtn');
let cmModalCloseCmBtn = document.querySelector('#cmModalCloseBtn');

if (cmModalOpenBtn && cmModalCloseCmBtn) {
    cmModalOpenBtn.click();

    cmModalCloseCmBtn.addEventListener('click', function () {
        let cmModal = document.querySelector('.cover-cm');
        cmModal.remove();
    });
}
