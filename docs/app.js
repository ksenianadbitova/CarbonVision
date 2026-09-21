// Плавное появление секций при скролле
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = "1";
            entry.target.style.transform = "translateY(0)";
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll("section, .card, .step").forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
    observer.observe(el);
});

// Кнопка «Наверх»
const btnUp = document.createElement("button");
btnUp.innerHTML = "↑";
btnUp.setAttribute("aria-label", "Наверх");
btnUp.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #52b788, #95d5b2);
    color: #081c15;
    border: none;
    font-size: 1.5rem;
    font-weight: 800;
    cursor: pointer;
    box-shadow: 0 6px 20px rgba(82,183,136,0.5);
    opacity: 0;
    transition: opacity 0.3s ease, transform 0.3s ease;
    z-index: 999;
`;
document.body.appendChild(btnUp);

window.addEventListener("scroll", () => {
    if (window.scrollY > 400) {
        btnUp.style.opacity = "1";
        btnUp.style.transform = "translateY(0)";
    } else {
        btnUp.style.opacity = "0";
        btnUp.style.transform = "translateY(20px)";
    }
});

btnUp.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});