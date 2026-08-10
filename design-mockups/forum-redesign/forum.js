lucide.createIcons();

const sidebar = document.getElementById("sidebar");
const menuButton = document.getElementById("mobile-menu");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");
let toastTimer;

function showToast(message) {
  if (!toast || !toastMessage) return;
  clearTimeout(toastTimer);
  toastMessage.textContent = message;
  toast.classList.add("visible");
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 2400);
}

if (menuButton && sidebar) {
  menuButton.addEventListener("click", () => {
    const isOpen = sidebar.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    menuButton.innerHTML = `<i data-lucide="${isOpen ? "x" : "menu"}" aria-hidden="true"></i>`;
    lucide.createIcons();
  });
}

document.addEventListener("click", (event) => {
  const toastTrigger = event.target.closest("[data-toast]");
  if (toastTrigger) {
    event.preventDefault();
    showToast(toastTrigger.dataset.toast);
  }

  const chip = event.target.closest(".chip[data-filter]");
  if (chip) {
    const group = chip.closest("[data-filter-group]");
    if (group) {
      group.querySelectorAll(".chip").forEach((item) => item.classList.toggle("active", item === chip));
    }
    showToast(`${chip.textContent.trim()} filter selected`);
  }
});

document.querySelectorAll("[data-save-draft]").forEach((button) => {
  button.addEventListener("click", () => showToast("Draft saved to your forum drafts"));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && sidebar && sidebar.classList.contains("open") && menuButton) {
    menuButton.click();
  }
});
