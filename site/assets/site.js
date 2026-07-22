const body = document.body;
body.classList.add("js-ready");

const filter = document.querySelector(".js-filter");
if (filter) {
  const cards = [...document.querySelectorAll("[data-filter-grid] .record-card")];
  const empty = document.querySelector("[data-filter-empty]");
  filter.addEventListener("input", () => {
    const query = filter.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const matches = !query || card.dataset.search.includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    if (empty) empty.hidden = visible !== 0;
  });
}

const dialog = document.querySelector("[data-search-dialog]");
const globalInput = document.querySelector("[data-global-search]");
const results = document.querySelector("[data-search-results]");
let searchIndex;

async function loadSearchIndex() {
  if (!searchIndex) {
    const response = await fetch(body.dataset.searchIndex);
    searchIndex = await response.json();
  }
  return searchIndex;
}

function resultNode(item) {
  const link = document.createElement("a");
  link.href = item.url;
  const category = document.createElement("span");
  category.textContent = item.category;
  const title = document.createElement("strong");
  title.textContent = item.title;
  const description = document.createElement("small");
  description.textContent = item.description || item.keywords;
  link.append(category, title, description);
  return link;
}

async function performSearch(query) {
  const index = await loadSearchIndex();
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) {
    results.innerHTML = "<p>Start typing to explore the modeled records.</p>";
    return;
  }
  const matches = index
    .map((item) => {
      const title = item.title.toLowerCase();
      const haystack = `${item.title} ${item.description} ${item.keywords} ${item.category}`.toLowerCase();
      const matched = terms.every((term) => haystack.includes(term));
      const score = terms.reduce((total, term) => total + (title.includes(term) ? 4 : haystack.includes(term) ? 1 : 0), 0);
      return { item, matched, score };
    })
    .filter((entry) => entry.matched)
    .sort((a, b) => b.score - a.score || a.item.title.localeCompare(b.item.title))
    .slice(0, 12);
  results.replaceChildren();
  if (!matches.length) {
    const message = document.createElement("p");
    message.textContent = "No modeled records match that search.";
    results.append(message);
    return;
  }
  matches.forEach(({ item }) => results.append(resultNode(item)));
}

document.querySelectorAll("[data-open-search]").forEach((button) => {
  button.addEventListener("click", async () => {
    dialog.showModal();
    globalInput.focus();
    await loadSearchIndex();
  });
});

if (globalInput) {
  let timer;
  globalInput.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => performSearch(globalInput.value), 90);
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && document.activeElement?.tagName !== "INPUT") {
    event.preventDefault();
    dialog.showModal();
    globalInput.focus();
  }
});

const observer = new IntersectionObserver(
  (entries) => entries.forEach((entry) => entry.isIntersecting && entry.target.classList.add("is-visible")),
  { threshold: 0.08 },
);
document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));
