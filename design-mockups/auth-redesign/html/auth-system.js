document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) window.lucide.createIcons();

  document.querySelectorAll('[data-password-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.passwordToggle);
      if (!input) return;
      const reveal = input.type === 'password';
      input.type = reveal ? 'text' : 'password';
      button.setAttribute('aria-label', reveal ? 'Hide password' : 'Show password');
      button.innerHTML = `<i data-lucide="${reveal ? 'eye-off' : 'eye'}" aria-hidden="true"></i>`;
      if (window.lucide) window.lucide.createIcons();
    });
  });

  const otpInputs = [...document.querySelectorAll('.otp-input')];
  otpInputs.forEach((input, index) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/\D/g, '').slice(-1);
      if (input.value && otpInputs[index + 1]) otpInputs[index + 1].focus();
    });
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Backspace' && !input.value && otpInputs[index - 1]) otpInputs[index - 1].focus();
      if (event.key === 'ArrowLeft' && otpInputs[index - 1]) otpInputs[index - 1].focus();
      if (event.key === 'ArrowRight' && otpInputs[index + 1]) otpInputs[index + 1].focus();
    });
    input.addEventListener('paste', (event) => {
      const code = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, otpInputs.length);
      if (!code) return;
      event.preventDefault();
      code.split('').forEach((digit, digitIndex) => { if (otpInputs[digitIndex]) otpInputs[digitIndex].value = digit; });
      (otpInputs[Math.min(code.length, otpInputs.length) - 1] || input).focus();
    });
  });

  document.querySelectorAll('[data-password-meter]').forEach((input) => {
    const meter = document.getElementById(input.dataset.passwordMeter);
    const requirements = document.querySelectorAll(`[data-requirement-for="${input.id}"]`);
    const evaluate = () => {
      const value = input.value;
      const tests = {
        length: value.length >= 12,
        upper: /[A-Z]/.test(value),
        number: /\d/.test(value),
        symbol: /[^A-Za-z0-9]/.test(value)
      };
      const strength = Object.values(tests).filter(Boolean).length;
      if (meter) meter.dataset.strength = String(strength);
      requirements.forEach((item) => {
        const met = tests[item.dataset.rule];
        item.classList.toggle('met', Boolean(met));
        item.innerHTML = `<i data-lucide="${met ? 'check' : 'circle'}" aria-hidden="true"></i>${item.dataset.label}`;
      });
      if (window.lucide) window.lucide.createIcons();
    };
    input.addEventListener('input', evaluate);
    evaluate();
  });

  document.querySelectorAll('form[data-mock-form]').forEach((form) => {
    form.addEventListener('submit', (event) => event.preventDefault());
  });

  const countdown = document.querySelector('[data-countdown]');
  if (countdown) {
    let remaining = Number(countdown.dataset.countdown || 30);
    const tick = () => {
      countdown.textContent = remaining > 0 ? `Resend in 0:${String(remaining).padStart(2, '0')}` : 'Resend code';
      if (remaining > 0) { remaining -= 1; setTimeout(tick, 1000); }
      else countdown.removeAttribute('aria-disabled');
    };
    tick();
  }
});
