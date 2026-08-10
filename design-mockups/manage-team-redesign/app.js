lucide.createIcons();

const params = new URLSearchParams(window.location.search);
const prototypeRole = params.get('role') === 'member' ? 'member' : 'admin';
document.body.dataset.role = prototypeRole;
document.documentElement.dataset.role = prototypeRole;

const sidebar = document.getElementById('sidebar');
const menu = document.getElementById('mobile-menu');
const toast = document.getElementById('toast');
const toastText = document.getElementById('toast-message');
let toastTimer;

function showToast(message) {
  if (!toast) return;
  clearTimeout(toastTimer);
  toastText.textContent = message;
  toast.classList.add('visible');
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 2600);
}

function roleUrl(path, role = prototypeRole) {
  const url = new URL(path, window.location.href);
  url.searchParams.set('role', role);
  return url.href;
}

function propagateRole() {
  document.querySelectorAll('a[href]').forEach(link => {
    const raw = link.getAttribute('href') || '';
    if (!raw || raw.startsWith('#') || raw.startsWith('mailto:') || raw.startsWith('http')) return;
    const target = new URL(raw, window.location.href);
    if (!target.pathname.includes('/manage-team-redesign/')) return;
    target.searchParams.set('role', prototypeRole);
    link.href = target.href;
  });
}

function addRolePreviewControl() {
  const actions = document.querySelector('.topbar-actions');
  if (!actions) return;
  const control = document.createElement('label');
  control.className = 'role-preview';
  control.innerHTML = `<span>Prototype role</span><select aria-label="Preview organization as role"><option value="admin">Administrator</option><option value="member">Member</option></select>`;
  const select = control.querySelector('select');
  select.value = prototypeRole;
  select.addEventListener('change', () => {
    const url = new URL(window.location.href);
    url.searchParams.set('role', select.value);
    window.location.href = url.href;
  });
  actions.prepend(control);
}

function updateRoleCopy() {
  document.querySelectorAll('[data-organization-label]').forEach(label => { label.textContent = 'IIoT Solutions'; });
  const profileRole = document.querySelector('.profile-role');
  if (profileRole) profileRole.textContent = prototypeRole === 'admin' ? 'CTO · Administrator' : 'AI Engineer · Member';
  const profileName = document.querySelector('.profile-name');
  if (profileName && prototypeRole === 'member') profileName.textContent = 'Hamza Feroze';
  const avatar = document.querySelector('.profile-rail .avatar');
  if (avatar && prototypeRole === 'member') avatar.textContent = 'HF';
  const roleDescription = document.querySelector('[data-role-description]');
  if (roleDescription) roleDescription.textContent = prototypeRole === 'admin'
    ? 'View the organization workspace and administer membership, invitations, roles and settings.'
    : 'View your organization profile, people, contacts, use cases and recent activity.';
  const rosterCopy = document.querySelector('[data-roster-copy]');
  if (rosterCopy) rosterCopy.textContent = prototypeRole === 'admin'
    ? 'Find members, open details and manage organization access.'
    : 'Find organization members and open basic member details.';
}

function accessDeniedMarkup() {
  return `<main class="page denied-page" id="main-content">
    <header class="page-heading"><div><p class="eyebrow">IIoT Solutions · Member access</p><h1>Administrator access required</h1><p class="lead">Your organization membership is active, but this action is reserved for IIoT Solutions administrators.</p></div></header>
    <section class="panel denied-panel">
      <div class="state-illustration"><i data-lucide="shield-alert"></i></div>
      <h2>This organization area is read-only for members</h2>
      <p>You can view the organization profile, member roster, administrators and contacts, published use cases, activity, and basic member details. Invitations, add/remove/suspend controls, role changes, permission editing, and organization settings are not available for the Member role.</p>
      <div class="button-row"><a class="button" href="${roleUrl('index.html', 'member')}"><i data-lucide="building-2"></i>Return to IIoT Solutions</a><a class="button secondary" href="mailto:aadil@iiotsolutions.sa"><i data-lucide="mail"></i>Contact administrator</a></div>
    </section>
  </main>`;
}

function enforceRoleBoundary() {
  const page = window.location.pathname.split('/').pop();
  const adminPages = new Set(['invitations.html', 'invite-member.html', 'permissions.html', 'settings.html']);
  if (prototypeRole !== 'member' || !adminPages.has(page)) return;
  const existing = document.querySelector('main');
  if (existing) existing.outerHTML = accessDeniedMarkup();
}

addRolePreviewControl();
updateRoleCopy();
enforceRoleBoundary();
propagateRole();
lucide.createIcons();

if (menu) {
  menu.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
    menu.innerHTML = `<i data-lucide="${open ? 'x' : 'menu'}"></i>`;
    lucide.createIcons();
  });
}

document.addEventListener('click', event => {
  const toastTrigger = event.target.closest('[data-toast]');
  if (toastTrigger) {
    event.preventDefault();
    showToast(toastTrigger.dataset.toast);
  }

  const open = event.target.closest('[data-modal-open]');
  if (open) document.getElementById(open.dataset.modalOpen)?.classList.add('open');

  const close = event.target.closest('[data-modal-close]');
  if (close) close.closest('.modal-backdrop')?.classList.remove('open');

  const toggle = event.target.closest('.toggle');
  if (toggle && prototypeRole === 'admin') {
    toggle.classList.toggle('on');
    toggle.setAttribute('aria-pressed', String(toggle.classList.contains('on')));
    showToast('Permission preference updated in this administrator mockup');
  }
});

document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  sidebar?.classList.remove('open');
  document.querySelectorAll('.modal-backdrop.open').forEach(modal => modal.classList.remove('open'));
});

const search = document.querySelector('[data-member-search]');
const role = document.querySelector('[data-role-filter]');
const status = document.querySelector('[data-status-filter]');
const rows = [...document.querySelectorAll('[data-member-row]')];
const count = document.querySelector('[data-result-count]');

function filterRows() {
  if (!rows.length) return;
  const query = (search?.value || '').toLowerCase();
  const roleValue = role?.value || 'all';
  const statusValue = status?.value || 'all';
  let visible = 0;
  rows.forEach(row => {
    const show = row.textContent.toLowerCase().includes(query)
      && (roleValue === 'all' || row.dataset.role === roleValue)
      && (statusValue === 'all' || row.dataset.status === statusValue);
    row.hidden = !show;
    if (show) visible += 1;
  });
  if (count) count.textContent = `Showing ${visible} of ${rows.length} organization members`;
}

[search, role, status].forEach(control => control?.addEventListener(control === search ? 'input' : 'change', filterRows));

document.querySelectorAll('[data-state]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-state]').forEach(item => item.classList.toggle('active', item === button));
  document.querySelectorAll('.state').forEach(item => item.classList.toggle('active', item.id === `state-${button.dataset.state}`));
  lucide.createIcons();
}));

document.querySelectorAll('[data-tab]').forEach(tab => tab.addEventListener('click', () => {
  document.querySelectorAll('[data-tab]').forEach(item => item.classList.toggle('active', item === tab));
  showToast(`${tab.textContent.trim()} section selected`);
}));

document.querySelectorAll('form[data-demo-form]').forEach(form => form.addEventListener('submit', event => {
  event.preventDefault();
  if (prototypeRole !== 'admin') {
    window.location.href = roleUrl(window.location.pathname.split('/').pop(), 'member');
    return;
  }
  const modal = form.closest('.modal-backdrop');
  if (modal) modal.classList.remove('open');
  showToast(form.dataset.success || 'Saved in this administrator mockup');
}));
