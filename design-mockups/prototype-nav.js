/* PeerLink static prototype router: connects the independently-created mockup families. */
(() => {
  const script = document.currentScript;
  if (!script) return;
  const root = new URL('./', script.src);
  const route = path => new URL(path, root).href;
  const routes = {
    home: route('homepage-redesign/peerlink-homepage-network-workspace.html'),
    dashboard: route('dashboard-redesign/concept-c-network-workspace.html'),
    forum: route('forum-redesign/index.html'),
    forumComposer: route('forum-redesign/composer-drafts.html'),
    people: route('people-redesign/index.html'),
    usecases: route('usecases-redesign/library.html'),
    submitCase: route('usecases-redesign/submission.html'),
    manageTeam: route('manage-team-redesign/index.html'),
    login: route('auth-redesign/html/login.html'),
    signup: route('auth-redesign/html/signup.html'),
    verify: route('auth-redesign/html/email-verification.html'),
    forgot: route('auth-redesign/html/forgot-password.html'),
    forgotSent: route('auth-redesign/html/forgot-password-sent.html'),
    reset: route('auth-redesign/html/reset-password.html'),
    success: route('auth-redesign/html/auth-success.html'),
    mfa: route('auth-redesign/html/otp-mfa.html'),
    caseDetail: route('usecases-redesign/detail.html')
  };

  const normalize = value => (value || '').replace(/\s+/g, ' ').trim().toLowerCase().replace(/^[^a-z0-9]+/i, '');
  const destinationFor = text => {
    if (['dashboard', 'overview', 'view network workspace', 'open workspace'].includes(text)) return routes.dashboard;
    if (['forum', 'discussions'].includes(text)) return routes.forum;
    if (text.startsWith('ask a question')) return routes.forumComposer;
    if (['people', 'member directory'].includes(text)) return routes.people;
    if (['use cases', 'use case library', 'explore use cases', 'browse use cases', 'explore success stories'].includes(text)) return routes.usecases;
    if (['manage team', 'manage organization', 'iiot solutions', 'organization', 'organization profile', 'open organization'].includes(text)) return routes.manageTeam;
    if (['sign in', 'log in', 'login'].includes(text)) return routes.login;
    if (['join', 'join peerlink', 'join the network', 'create account', 'sign up', 'get started', 'get started free'].includes(text)) return routes.signup;
    if (['submit use case', 'submit a use case'].includes(text) || text.startsWith('share a use case')) return routes.submitCase;
    if (text.startsWith('find collaborators')) return routes.people;
    if (['read the use case', 'open use case'].includes(text)) return routes.caseDetail;
    if (['forgot password?', 'forgot your password?'].includes(text)) return routes.forgot;
    if (['home', 'back to home', 'peerlink'].includes(text)) return routes.home;
    return null;
  };

  document.querySelectorAll('a, button, [role="button"]').forEach(el => {
    const label = normalize(el.dataset?.label || el.getAttribute('aria-label') || el.textContent);
    const destination = destinationFor(label);
    if (!destination) return;
    if (el.tagName === 'A') {
      el.href = destination;
      el.addEventListener('click', event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        window.location.href = destination;
      }, true);
    } else el.addEventListener('click', event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      window.location.href = destination;
    }, true);
  });

  document.querySelectorAll('.brand, .logo, [class*="brand-mark"]').forEach(el => {
    if (el.closest('a')) return;
    el.style.cursor = 'pointer';
    el.setAttribute('title', 'PeerLink home');
    el.addEventListener('click', () => { window.location.href = routes.home; });
  });

  if (location.pathname.includes('homepage-redesign')) {
    document.querySelectorAll('a[href^="/usecases/"]').forEach(a => { a.href = routes.caseDetail; });
    document.querySelectorAll('a[href="/signup"]').forEach(a => { a.href = routes.signup; });
  }

  const page = location.pathname.split('/').pop();
  const formDestinations = {
    'login.html': routes.dashboard,
    'login-validation.html': routes.dashboard,
    'login-loading.html': routes.dashboard,
    'signup.html': routes.verify,
    'organization-registration.html': routes.verify,
    'email-verification.html': routes.mfa,
    'otp-mfa.html': routes.dashboard,
    'otp-mfa-error.html': routes.dashboard,
    'forgot-password.html': routes.forgotSent,
    'reset-password.html': routes.success
  };
  if (formDestinations[page]) {
    document.querySelectorAll('form').forEach(form => form.addEventListener('submit', event => {
      event.preventDefault();
      window.location.href = formDestinations[page];
    }));
  }

  window.PeerLinkPrototypeRoutes = routes;
})();
