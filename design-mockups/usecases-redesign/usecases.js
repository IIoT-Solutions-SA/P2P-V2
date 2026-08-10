(() => {
  const sidebar = document.getElementById("sidebar");
  const menu = document.getElementById("mobile-menu");
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toast-message");
  let toastTimer;

  if (window.lucide) window.lucide.createIcons();

  if (sidebar && menu) {
    menu.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      menu.setAttribute("aria-expanded", String(open));
    });
  }

  const showToast = message => {
    if (!toast || !toastMessage || !message) return;
    toastMessage.textContent = message;
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2400);
  };

  document.querySelectorAll("[data-toast]").forEach(el => {
    el.addEventListener("click", () => showToast(el.dataset.toast));
  });

  document.querySelectorAll("[data-state-target]").forEach(button => {
    button.addEventListener("click", () => {
      const target = button.dataset.stateTarget;
      document.querySelectorAll("[data-state-target]").forEach(item => {
        item.classList.toggle("active", item === button);
      });
      document.querySelectorAll("[data-state]").forEach(state => {
        state.classList.toggle("active", state.dataset.state === target);
      });
    });
  });
})();
