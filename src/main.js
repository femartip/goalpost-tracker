const $ = (id) => document.getElementById(id);

function uniq(arr) {
  return [...new Set(arr.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function badge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

function safe(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
}

function getTax(c) {
  const t = c.taxonomy || {};
  return {
    domain: t.domain || 'other',
    modality: t.modality || 'other',
    topic: Array.isArray(t.topic) ? t.topic : []
  };
}

function buildControls(state, options) {
  const controls = $('controls');
  controls.innerHTML = '';

  const makeSelect = (key, label, values) => {
    const el = document.createElement('div');
    el.className = 'control';
    el.innerHTML = `
      <label>${label}</label>
      <select id="sel-${key}">
        <option value="">All</option>
        ${values.map(v => `<option value="${safe(v)}" ${state[key]===v?'selected':''}>${safe(v)}</option>`).join('')}
      </select>
    `;
    controls.appendChild(el);
    el.querySelector('select').addEventListener('change', (e) => {
      state[key] = e.target.value || '';
      render();
    });
  };

  makeSelect('status', 'Status', options.status);
  makeSelect('domain', 'Domain', options.domain);
  makeSelect('modality', 'Modality', options.modality);
  makeSelect('author', 'Author', options.author);

  const search = document.createElement('div');
  search.className = 'control';
  search.innerHTML = `
    <label>Search</label>
    <input id="search" placeholder="text, topic, author..." value="${safe(state.q)}" />
  `;
  controls.appendChild(search);
  search.querySelector('input').addEventListener('input', (e) => {
    state.q = e.target.value;
    render();
  });
}

let claims = [];
const state = { status: '', domain: '', modality: '', author: '', q: '' };

function matches(c) {
  const t = getTax(c);
  if (state.status && c.status !== state.status) return false;
  if (state.domain && t.domain !== state.domain) return false;
  if (state.modality && t.modality !== state.modality) return false;
  if (state.author && c.author !== state.author) return false;

  const q = state.q.trim().toLowerCase();
  if (!q) return true;

  const blob = [
    c.author, c.claimText, c.claimType, c.status,
    c.tweetUrl,
    t.domain, t.modality,
    ...(t.topic || []),
    ...(c.evidence || []).flatMap(e => [e.title, e.url, e.notes])
  ].join(' ').toLowerCase();

  return blob.includes(q);
}

function renderGrid(items) {
  const grid = $('grid');
  grid.innerHTML = '';

  for (const c of items) {
    const t = getTax(c);
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="meta">
        <div>${safe(c.author)} · ${safe(c.date)}</div>
        <div>${badge(c.status)}</div>
      </div>
      <div class="quote">${safe(c.claimText)}</div>
      <div class="tags">
        <span class="tag">${safe(t.domain)}</span>
        <span class="tag">${safe(t.modality)}</span>
        ${(t.topic || []).slice(0, 4).map(x => `<span class="tag">${safe(x)}</span>`).join('')}
      </div>
    `;
    card.addEventListener('click', () => openDetail(c));
    grid.appendChild(card);
  }
}

function openDetail(c) {
  const t = getTax(c);
  const ev = Array.isArray(c.evidence) ? c.evidence : [];

  $('detail').innerHTML = `
    <h2>${safe(c.author)} · ${safe(c.date)} ${badge(c.status)}</h2>
    <p><strong>Claim type:</strong> ${safe(c.claimType)} · <strong>Domain:</strong> ${safe(t.domain)} · <strong>Modality:</strong> ${safe(t.modality)}</p>
    <p><strong>Topics:</strong> ${(t.topic || []).map(x => `<span class="tag">${safe(x)}</span>`).join(' ') || '<span class="tag">(none)</span>'}</p>
    <hr />
    <p><strong>Tweet:</strong> <a href="${safe(c.tweetUrl)}" target="_blank" rel="noreferrer">${safe(c.tweetUrl)}</a></p>
    <p><strong>Quote:</strong></p>
    <p class="quote">${safe(c.claimText)}</p>
    ${c.notes ? `<hr /><p><strong>Notes:</strong> ${safe(c.notes)}</p>` : ''}
    <hr />
    <h3>Evidence</h3>
    ${ev.length ? `
      ${ev.map(e => `
        <div style="margin: 10px 0;">
          <div><a href="${safe(e.url)}" target="_blank" rel="noreferrer">${safe(e.title || e.url)}</a>${e.date ? ` · ${safe(e.date)}` : ''}</div>
          ${e.notes ? `<div class="meta" style="margin-top:4px;">${safe(e.notes)}</div>` : ''}
        </div>
      `).join('')}
    ` : '<p class="meta">No evidence attached yet.</p>'}
  `;

  const dlg = $('dialog');
  dlg.showModal();
}

$('close').addEventListener('click', () => $('dialog').close());

function render() {
  const items = claims.filter(matches);
  renderGrid(items);
}

async function init() {
  const res = await fetch('./data/claims.json', { cache: 'no-cache' });
  claims = await res.json();

  const opts = {
    status: uniq(claims.map(c => c.status)),
    author: uniq(claims.map(c => c.author)),
    domain: uniq(claims.map(c => getTax(c).domain)),
    modality: uniq(claims.map(c => getTax(c).modality)),
  };

  buildControls(state, opts);
  render();
}

init();
