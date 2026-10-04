const menuToggle = document.getElementById("menuToggle");
const nav = document.querySelector(".nav");

if (menuToggle && nav) {

    menuToggle.addEventListener("click", () => {

        nav.classList.toggle("open");

        menuToggle.classList.toggle("active");

    });

}


/* =========================================================
   02. FECHAR MENU AO CLICAR EM UM LINK
   ========================================================= */

const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach(link => {

    link.addEventListener("click", () => {

        if (nav) {
            nav.classList.remove("open");
        }

        if (menuToggle) {
            menuToggle.classList.remove("active");
        }

    });

});


/* =========================================================
   03. HEADER AO ROLAR A PÁGINA
   ========================================================= */

const header = document.querySelector(".header");

window.addEventListener("scroll", () => {

    if (!header) return;

    if (window.scrollY > 50) {

        header.classList.add("scrolled");

    } else {

        header.classList.remove("scrolled");

    }

});


/* =========================================================
   04. ATUALIZAR LINK ATIVO DO MENU
   ========================================================= */

const sections = document.querySelectorAll("section[id]");

function updateActiveLink() {

    const scrollPosition = window.scrollY + 150;

    sections.forEach(section => {

        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute("id");

        if (
            scrollPosition >= sectionTop &&
            scrollPosition < sectionTop + sectionHeight
        ) {

            navLinks.forEach(link => {

                link.classList.remove("active");

                const href = link.getAttribute("href");

                if (href === `#${sectionId}`) {
                    link.classList.add("active");
                }

            });

        }

    });

}

window.addEventListener("scroll", updateActiveLink);


/* =========================================================
   05. ANIMAÇÃO DE ENTRADA DAS SEÇÕES
   ========================================================= */

const animatedElements = document.querySelectorAll(
    ".section-heading, .about-grid, .project-card, .tech-item, .timeline-item, .contact-content"
);

const observer = new IntersectionObserver(
    (entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.classList.add("visible");

                observer.unobserve(entry.target);

            }

        });

    },
    {
        threshold: 0.12
    }
);

animatedElements.forEach(element => {

    element.classList.add("animate-on-scroll");

    observer.observe(element);

});


/* =========================================================
   06. EFEITO SUAVE NO CARD DE CÓDIGO
   ========================================================= */

const codeCard = document.querySelector(".code-card");

if (codeCard) {

    document.addEventListener("mousemove", event => {

        const x = (window.innerWidth / 2 - event.clientX) / 60;
        const y = (window.innerHeight / 2 - event.clientY) / 60;

        if (window.innerWidth > 900) {

            codeCard.style.transform = `
                perspective(1000px)
                rotateY(${x}deg)
                rotateX(${-y}deg)
            `;

        }

    });

}


/* =========================================================
   07. ANO AUTOMÁTICO DO FOOTER
   ========================================================= */

const footerYear = document.querySelector(".footer-container > span");

if (footerYear) {

    footerYear.textContent =
        `© ${new Date().getFullYear()} Marcella Amorim`;

}


