/* ============================================================
   ALUMNI MANAGEMENT SYSTEM — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss alerts after 5s ──
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transform = 'translateX(20px)';
      setTimeout(function () { el.remove(); }, 300);
    }, 5000);
  });

  // ── Active nav link highlighting ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link, .sidebar-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Animate stat values on scroll ──
  const statValues = document.querySelectorAll('.stat-value');
  if (statValues.length) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    statValues.forEach(function (el) { observer.observe(el); });
  }

  // ── Profile photo upload preview ──
  const photoInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
  photoInputs.forEach(function (input) {
    input.addEventListener('change', function (e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function (ev) {
        const preview = document.querySelector('[data-photo-preview]');
        if (preview) {
          preview.src = ev.target.result;
          preview.style.display = 'block';
        }
      };
      reader.readAsDataURL(file);
    });
  });

  // ── Tooltip initialisation ──
  document.querySelectorAll('[data-tooltip]').forEach(function (el) {
    el.addEventListener('mouseenter', function () {
      const tip = document.createElement('div');
      tip.className = 'tooltip-popup';
      tip.textContent = el.getAttribute('data-tooltip');
      tip.style.cssText = 'position:fixed;background:var(--navy);color:var(--ivory);padding:6px 12px;border-radius:6px;font-size:0.75rem;z-index:9999;pointer-events:none;white-space:nowrap;';
      document.body.appendChild(tip);
      const rect = el.getBoundingClientRect();
      tip.style.top = (rect.top - 36) + 'px';
      tip.style.left = (rect.left + rect.width / 2 - tip.offsetWidth / 2) + 'px';
      el._tooltip = tip;
    });
    el.addEventListener('mouseleave', function () {
      if (el._tooltip) { el._tooltip.remove(); el._tooltip = null; }
    });
  });

  // ── Confirm delete buttons ──
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm(btn.getAttribute('data-confirm') || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ── Form submission loading state ──
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      const submit = form.querySelector('[type="submit"]');
      if (submit && !submit.hasAttribute('data-no-loading')) {
        const orig = submit.innerHTML;
        submit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + (submit.getAttribute('data-loading-text') || 'Processing…');
        submit.disabled = true;
        // Re-enable after 10s as fallback
        setTimeout(function () { submit.innerHTML = orig; submit.disabled = false; }, 10000);
      }
    });
  });

  // ── Smooth scroll for anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Toggle password visibility ──
  window.togglePwd = function (inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const isText = input.type === 'text';
    input.type = isText ? 'password' : 'text';
    btn.innerHTML = isText
      ? '<i class="fas fa-eye"></i>'
      : '<i class="fas fa-eye-slash"></i>';
  };

  // ── Close dropdowns on outside click ──
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.dropdown-menu.open').forEach(function (menu) {
      if (!menu.previousElementSibling.contains(e.target)) {
        menu.classList.remove('open');
      }
    });
  });

  // ── Sidebar mobile toggle ──
  window.toggleSidebar = function () {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.toggle('open');
  };

  // ── Character counter for textareas ──
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const max = parseInt(ta.getAttribute('maxlength'));
    const counter = document.createElement('div');
    counter.style.cssText = 'font-size:0.75rem;color:var(--text-muted);text-align:right;margin-top:4px;';
    counter.textContent = '0 / ' + max;
    ta.parentNode.insertBefore(counter, ta.nextSibling);
    ta.addEventListener('input', function () {
      const len = ta.value.length;
      counter.textContent = len + ' / ' + max;
      counter.style.color = len >= max * 0.9 ? 'var(--crimson)' : 'var(--text-muted)';
    });
  });
});

// ── Animate numeric counters ──
function animateCounter(el) {
  const raw = el.textContent.replace(/[^0-9.]/g, '');
  const suffix = el.textContent.replace(/[0-9.,]/g, '');
  const target = parseFloat(raw);
  if (isNaN(target)) return;
  const duration = 1200;
  const start = performance.now();
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = target * ease;
    el.textContent = (current >= 1000
      ? (current >= 10000
        ? Math.round(current).toLocaleString()
        : (current / 1000).toFixed(1) + 'k')
      : Math.round(current)) + suffix;
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = raw.includes(',') ? parseInt(raw.replace(',', '')).toLocaleString() + suffix : raw + suffix;
  }
  requestAnimationFrame(step);
}

// ── Toast notification helper ──
window.showToast = function (message, type) {
  type = type || 'info';
  const toast = document.createElement('div');
  toast.className = 'alert alert-' + type;
  toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;max-width:360px;box-shadow:var(--shadow-md);animation:slideIn 0.3s ease;';
  const icons = { success: 'check-circle', error: 'exclamation-circle', warning: 'exclamation-triangle', info: 'info-circle' };
  toast.innerHTML = '<i class="fas fa-' + (icons[type] || 'info-circle') + '"></i><span>' + message + '</span>';
  document.body.appendChild(toast);
  setTimeout(function () {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = '0.3s ease';
    setTimeout(function () { toast.remove(); }, 300);
  }, 4000);
};

// ── Debounce utility ──
window.debounce = function (fn, delay) {
  let timer;
  return function () {
    clearTimeout(timer);
    timer = setTimeout(fn.apply.bind(fn, this, arguments), delay);
  };
};

// ── Live search with debounce ──
const globalSearch = document.getElementById('globalSearch');
if (globalSearch) {
  globalSearch.addEventListener('input', debounce(function () {
    const q = globalSearch.value.trim();
    if (q.length >= 2) {
      fetch('/api/search/?q=' + encodeURIComponent(q))
        .then(function (r) { return r.json(); })
        .then(function (data) {
          // Render quick search results if container exists
          const container = document.getElementById('quickSearchResults');
          if (container) {
            container.innerHTML = '';
            (data.results || []).forEach(function (item) {
              const div = document.createElement('a');
              div.href = item.url;
              div.className = 'quick-result-item';
              div.innerHTML = '<span class="qr-icon">' + item.icon + '</span><span class="qr-label">' + item.label + '</span>';
              container.appendChild(div);
            });
            container.style.display = data.results.length ? 'block' : 'none';
          }
        })
        .catch(function () { /* Silently fail */ });
    }
  }, 300));
}

// ── Copy to clipboard ──
window.copyToClipboard = function (text, btn) {
  navigator.clipboard.writeText(text).then(function () {
    const orig = btn ? btn.innerHTML : '';
    if (btn) btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    setTimeout(function () { if (btn) btn.innerHTML = orig; }, 2000);
  });
};

// ── Read more / less toggle ──
document.querySelectorAll('[data-read-more]').forEach(function (el) {
  const maxHeight = parseInt(el.getAttribute('data-read-more')) || 100;
  if (el.scrollHeight <= maxHeight) return;
  el.style.maxHeight = maxHeight + 'px';
  el.style.overflow = 'hidden';
  const btn = document.createElement('button');
  btn.className = 'btn btn-ghost btn-sm';
  btn.style.marginTop = '8px';
  btn.textContent = 'Read more';
  btn.addEventListener('click', function () {
    const isOpen = el.style.maxHeight === 'none';
    el.style.maxHeight = isOpen ? maxHeight + 'px' : 'none';
    btn.textContent = isOpen ? 'Read more' : 'Read less';
  });
  el.parentNode.insertBefore(btn, el.nextSibling);
});
