"use strict";

document.addEventListener("DOMContentLoaded", () => {
  setCurrentYear();
  setupMenu();
  setupNavigation();
  void loadPageContent();
});

function setCurrentYear() {
  const year = document.getElementById("current-year");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }
}

function setupMenu() {
  const button = document.querySelector(".menu-toggle");
  const navigation = document.getElementById("site-navigation");
  if (!button || !navigation) return;

  const closeMenu = () => {
    navigation.classList.remove("is-open");
    button.setAttribute("aria-expanded", "false");
  };

  button.addEventListener("click", () => {
    const isOpen = navigation.classList.toggle("is-open");
    button.setAttribute("aria-expanded", String(isOpen));
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 801px)").matches) {
      closeMenu();
    }
  });
}

function setupNavigation() {
  const links = [...document.querySelectorAll(".sidebar a[href^='#']")];
  if (!links.length) return;

  links.forEach((link) => {
    link.addEventListener("click", (event) => {
      const id = link.getAttribute("href")?.slice(1);
      const target = id ? document.getElementById(id) : null;
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      window.history.replaceState(null, "", `#${id}`);
    });
  });

  const sections = [...document.querySelectorAll("main section")];
  const updateActiveLink = () => {
    const visible = sections
      .filter((section) => !section.hidden)
      .map((section) => ({
        id: section.id,
        distance: Math.abs(section.getBoundingClientRect().top - 80),
        aboveFold: section.getBoundingClientRect().top <= 160,
      }))
      .filter((section) => section.aboveFold)
      .sort((left, right) => left.distance - right.distance)[0];

    links.forEach((link) => {
      link.classList.toggle(
        "active",
        Boolean(visible && link.getAttribute("href") === `#${visible.id}`)
      );
    });
  };

  let framePending = false;
  window.addEventListener(
    "scroll",
    () => {
      if (framePending) return;
      framePending = true;
      window.requestAnimationFrame(() => {
        updateActiveLink();
        framePending = false;
      });
    },
    { passive: true }
  );
  updateActiveLink();
}

async function loadPageContent() {
  const containers = [...document.querySelectorAll("[data-source]")];
  await Promise.all(containers.map(loadMarkdown));
  await loadMetadata();
}

async function loadMarkdown(container) {
  const source = container.dataset.source;
  if (!source) return;

  try {
    const response = await fetch(new URL(source, document.baseURI), {
      cache: "no-cache",
    });
    if (!response.ok) {
      if (response.status === 404 && container.closest("[data-optional]")) {
        hideSection(container);
        return;
      }
      throw new Error(`HTTP ${response.status}`);
    }

    const html = (await response.text()).trim();
    if (!html) {
      hideSection(container);
      return;
    }
    container.innerHTML = html;
  } catch (error) {
    console.error(`Could not load ${source}:`, error);
    container.innerHTML = '<p class="load-error">Content could not be loaded.</p>';
  }
}

function hideSection(container) {
  const section = container.closest("section");
  if (!section) return;
  section.hidden = true;
  const link = document.querySelector(`.sidebar a[href="#${section.id}"]`);
  const listItem = link?.closest("li");
  if (listItem) {
    listItem.hidden = true;
  }
}

async function loadMetadata() {
  const display = document.getElementById("last-updated");
  if (!display) return;

  try {
    const response = await fetch(
      new URL("_auto_contents/metadata.yml", document.baseURI),
      { cache: "no-cache" }
    );
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const metadata = await response.text();
    const match = metadata.match(/^last_updated:\s*(.+)$/m);
    if (match) {
      display.textContent = match[1].trim();
    }
  } catch (error) {
    console.error("Could not load synchronization metadata:", error);
  }
}
