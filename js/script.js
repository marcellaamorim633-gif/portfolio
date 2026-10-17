// Interações leves da página inicial.
document.querySelectorAll('a[href="#trabalhos"]').forEach((link) => {
  link.addEventListener('click', () => {
    document.querySelector('#trabalhos')?.classList.add('section-visited');
  });
});
