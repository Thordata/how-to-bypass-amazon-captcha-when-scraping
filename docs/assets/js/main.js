/* amazon-captcha tutorial site — front-end behavior.
   Handles: theme toggle, TOC scroll-spy, code copy buttons, scroll reveal,
   mobile menu, back-to-top. No build step, no dependencies. */

(function () {
  "use strict";

  /* ---------- Theme toggle -------------------------------------------- */
  var STORAGE_KEY = "amazon-captcha-theme";

  function getPreferredTheme() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var toggle = document.querySelector(".theme-toggle");
    if (toggle) toggle.textContent = theme === "light" ? "☾" : "☀";
  }

  // Apply immediately to avoid flash.
  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getPreferredTheme());

    var toggle = document.querySelector(".theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        var current = document.documentElement.getAttribute("data-theme");
        var next = current === "light" ? "dark" : "light";
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
        // Notify the playground (if present) so its theme stays in sync.
        window.dispatchEvent(new CustomEvent("themechange", { detail: next }));
      });
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    /* ---------- Code copy buttons ------------------------------------ */
    document.querySelectorAll(".code-block").forEach(function (block) {
      var btn = block.querySelector(".code-block__copy");
      var code = block.querySelector("pre code");
      if (!btn || !code) return;
      btn.addEventListener("click", function () {
        var text = code.innerText;
        var done = function () {
          var original = btn.textContent;
          btn.textContent = "copied!";
          btn.classList.add("copied");
          setTimeout(function () {
            btn.textContent = original;
            btn.classList.remove("copied");
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done).catch(fallback);
        } else {
          fallback();
        }
        function fallback() {
          var ta = document.createElement("textarea");
          ta.value = text;
          ta.style.position = "fixed";
          ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand("copy"); } catch (e) {}
          document.body.removeChild(ta);
          done();
        }
      });
    });

    /* ---------- TOC scroll-spy --------------------------------------- */
    var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a[href^='#']"));
    var targets = tocLinks
      .map(function (a) {
        var id = a.getAttribute("href").slice(1);
        return document.getElementById(id);
      })
      .filter(Boolean);

    if (targets.length && "IntersectionObserver" in window) {
      var spy = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              var id = entry.target.id;
              tocLinks.forEach(function (a) {
                var match = a.getAttribute("href") === "#" + id;
                a.classList.toggle("is-active", match);
              });
            }
          });
        },
        { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
      );
      targets.forEach(function (t) { spy.observe(t); });
    }

    /* ---------- Scroll reveal ---------------------------------------- */
    var revealEls = document.querySelectorAll(".reveal");
    if (revealEls.length && "IntersectionObserver" in window) {
      var revealObs = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-in");
              revealObs.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.08 }
      );
      revealEls.forEach(function (el) { revealObs.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add("is-in"); });
    }

    /* ---------- Mobile menu ------------------------------------------ */
    var menuBtn = document.querySelector(".nav__menu-btn");
    var navLinks = document.querySelector(".nav__links");
    if (menuBtn && navLinks) {
      menuBtn.addEventListener("click", function () {
        navLinks.classList.toggle("is-open");
      });
      navLinks.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () { navLinks.classList.remove("is-open"); });
      });
    }

    /* ---------- Back to top ------------------------------------------ */
    var toTop = document.querySelector(".to-top");
    if (toTop) {
      var onScroll = function () {
        toTop.classList.toggle("is-visible", window.scrollY > 600);
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      toTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }

    /* ---------- Flow diagram animation ------------------------------- */
    var flow = document.querySelector(".flow__nodes");
    if (flow && "IntersectionObserver" in window) {
      var flowObs = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              var nodes = flow.querySelectorAll(".flow__node");
              nodes.forEach(function (node, i) {
                setTimeout(function () {
                  node.style.borderColor = "var(--accent)";
                  node.style.boxShadow = "0 0 0 1px var(--accent-line)";
                  setTimeout(function () {
                    node.style.borderColor = "";
                    node.style.boxShadow = "";
                  }, 600);
                }, i * 280);
              });
              flowObs.unobserve(flow);
            }
          });
        },
        { threshold: 0.3 }
      );
      flowObs.observe(flow);
    }
  });
})();
