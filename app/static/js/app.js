// vision — keyboard shortcuts + search-as-you-type + sidebar toggles

(function () {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  const searchInput = $("#global-search");
  const dropdown = $("#search-dropdown");
  const app = $(".app");
  const modal = $("#shortcut-modal");

  // ---------- modal ----------
  function openModal() { modal.classList.remove("hidden"); }
  function closeModal() { modal.classList.add("hidden"); }
  modal?.addEventListener("click", (e) => {
    if (e.target === modal || e.target.hasAttribute("data-close-modal")) closeModal();
  });

  // ---------- search dropdown ----------
  let searchAbort = null;
  let searchTimer = null;
  let activeIdx = -1;
  let lastResults = [];

  async function runSearch(q) {
    if (searchAbort) searchAbort.abort();
    searchAbort = new AbortController();
    try {
      const r = await fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal: searchAbort.signal });
      const data = await r.json();
      renderDropdown(data.results || []);
    } catch (e) {
      if (e.name !== "AbortError") console.error(e);
    }
  }

  function renderDropdown(results) {
    lastResults = results;
    activeIdx = results.length ? 0 : -1;
    if (!results.length) {
      dropdown.innerHTML = `<div class="sd-empty">no matches</div>`;
    } else {
      dropdown.innerHTML = results.map((r, i) => `
        <a class="sd-item${i === 0 ? " active" : ""}" data-idx="${i}" href="/w/${r.slug}">
          <div class="sd-title">${escapeHtml(r.title)}</div>
          <div class="sd-folder">${escapeHtml(r.folder || "root")}/${escapeHtml(r.slug.split("/").pop())}</div>
          <div class="sd-snippet">${r.snippet || ""}</div>
        </a>
      `).join("");
    }
    dropdown.classList.remove("hidden");
  }
  function hideDropdown() { dropdown.classList.add("hidden"); }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
    }[c]));
  }

  searchInput?.addEventListener("input", (e) => {
    const q = e.target.value.trim();
    clearTimeout(searchTimer);
    if (!q) { hideDropdown(); return; }
    searchTimer = setTimeout(() => runSearch(q), 90);
  });
  searchInput?.addEventListener("focus", () => {
    if (searchInput.value.trim()) runSearch(searchInput.value.trim());
  });
  searchInput?.addEventListener("blur", () => {
    // give click a chance to land
    setTimeout(hideDropdown, 150);
  });
  searchInput?.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (lastResults.length) {
        activeIdx = (activeIdx + 1) % lastResults.length;
        updateActive();
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (lastResults.length) {
        activeIdx = (activeIdx - 1 + lastResults.length) % lastResults.length;
        updateActive();
      }
    } else if (e.key === "Enter") {
      if (activeIdx >= 0 && lastResults[activeIdx]) {
        e.preventDefault();
        window.location.href = `/w/${lastResults[activeIdx].slug}`;
      } else if (searchInput.value.trim()) {
        window.location.href = `/search?q=${encodeURIComponent(searchInput.value.trim())}`;
      }
    } else if (e.key === "Escape") {
      searchInput.blur();
      hideDropdown();
    }
  });

  function updateActive() {
    $$(".sd-item", dropdown).forEach((el, i) => {
      el.classList.toggle("active", i === activeIdx);
    });
    const el = $$(".sd-item", dropdown)[activeIdx];
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  // ---------- keyboard shortcuts ----------
  let pendingG = false;
  let pendingTimer = null;

  function isTyping(target) {
    return target && (
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable
    );
  }

  document.addEventListener("keydown", (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey) return;

    if (e.key === "Escape") {
      closeModal();
      if (document.activeElement === searchInput) searchInput.blur();
      return;
    }

    if (isTyping(e.target)) return;

    if (pendingG) {
      pendingG = false;
      clearTimeout(pendingTimer);
      const map = {
        "h": "/",
        "g": "/graph",
        "i": "/index",
        "t": "/tags",
        "l": "/log",
      };
      if (map[e.key]) {
        e.preventDefault();
        window.location.href = map[e.key];
      }
      return;
    }

    switch (e.key) {
      case "/":
        e.preventDefault();
        searchInput?.focus();
        searchInput?.select();
        break;
      case "g":
        pendingG = true;
        pendingTimer = setTimeout(() => { pendingG = false; }, 800);
        break;
      case "n":
        e.preventDefault();
        window.location.href = "/new";
        break;
      case "e":
        if (window.__VISION__ && window.__VISION__.currentSlug) {
          e.preventDefault();
          window.location.href = `/w/${window.__VISION__.currentSlug}/edit`;
        }
        break;
      case "?":
        e.preventDefault();
        openModal();
        break;
      case "[":
        e.preventDefault();
        app?.classList.toggle("left-collapsed");
        break;
      case "]":
        e.preventDefault();
        app?.classList.toggle("right-collapsed");
        break;
    }
  });
})();
