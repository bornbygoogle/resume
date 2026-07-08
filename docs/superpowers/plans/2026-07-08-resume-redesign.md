# Refonte du CV en ligne — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformer `/en/` et `/fr/` en landing "tech/développeur" sombre orientée conversion recruteur, en déplaçant le CV classique actuel (ATS, imprimé par pdf.co) vers `/en/print/` et `/fr/print/`.

**Architecture:** Hugo bilingue piloté par `config.toml`. Le markup actuel du CV (partials + `devresume.css`) devient la vue `/print/` (noindex, hors sitemap) que `get_pdf.py` imprime. La landing est un nouveau template `layouts/index.html` + `assets/css/landing.css`, sans Bootstrap ni FontAwesome, fonts self-hosted, icônes SVG inline. Les deux vues lisent les mêmes données `languages.<lang>.params.*`.

**Tech Stack:** Hugo 0.163.3 (binaire `./hugo.exe` à la racine du repo), CSS vanilla, JS vanilla, Netlify, pdf.co.

**Spec:** `docs/superpowers/specs/2026-07-08-resume-redesign-design.md`

## Global Constraints

- Hugo 0.163.3 ; build de référence : `./hugo.exe --minify` (Git Bash, racine du repo).
- Toute chaîne visible existe en EN **et** FR (via `i18n/*.yaml` ou `languages.<lang>.params`).
- La landing n'importe ni Bootstrap, ni FontAwesome, ni Google Fonts distantes ; fonts en `static/fonts/*.woff2`.
- La vue `/print/` garde son rendu actuel à l'identique (mêmes partials, même `devresume.css`, mêmes liens Google Fonts + FontAwesome).
- Les noms de fichiers PDF ne changent pas : `resume.{en,fr}.{a4,letter}.pdf`.
- Accent unique de la landing : vert menthe `#6ee7b7` (thème sombre) / `#047857` (thème clair) — contraste AA.
- Thème : sombre par défaut ; clair uniquement si `localStorage.theme === "light"`.
- Convention de thème : classe `dark` sur `<html>` (partagée avec la vue print).
- Aucun fait ni chiffre inventé dans le contenu ; uniquement les textes fournis verbatim dans ce plan.
- Commits fréquents, un par tâche minimum, messages en français comme l'historique du repo (ex. `Refonte : ...`).

---

### Task 1: Vue `/print/` — déplacer le CV actuel, noindex, `get_pdf.py`

Le markup du CV vit aujourd'hui **en dur dans `layouts/_default/baseof.html`** (pas dans un block). On le déplace dans un partial, on transforme `baseof.html` en squelette à blocks, on crée les pages `/en/print/` et `/fr/print/`, et la home continue de rendre l'ancien CV (la landing arrive en Task 3 — chaque commit reste shippable).

**Files:**
- Create: `layouts/partials/print-resume.html`
- Create: `layouts/print/list.html`
- Create: `content/print/_index.en.md`
- Create: `content/print/_index.fr.md`
- Modify: `layouts/_default/baseof.html` (remplacement complet)
- Modify: `layouts/index.html` (remplacement complet)
- Modify: `layouts/partials/head.html` (ajout meta noindex)
- Modify: `get_pdf.py:119` (URL imprimée)

**Interfaces:**
- Consumes: partials existants (`header.html`, `profile.html`, `contact.html`, `summary.html`, `experience.html`, `skills.html`, `projects.html`, `sidebar.html`, `footer.html`, `scripts.html`) — inchangés.
- Produces: `baseof.html` expose `{{ block "main" . }}` ; les pages de type `print` ont `.Type == "print"` (test utilisé par `head.html` dans les tâches suivantes) ; partial `print-resume.html` rend le CV complet.

- [ ] **Step 1: Vérifier l'état de départ (le « test qui échoue »)**

Run: `./hugo.exe --quiet && ls public/en/print/index.html`
Expected: `ls: cannot access 'public/en/print/index.html': No such file or directory`

- [ ] **Step 2: Créer `layouts/partials/print-resume.html`**

Contenu = le corps actuel de `baseof.html` (lignes 6–35), verbatim :

```html
<a class="visually-hidden" href="#main">{{ i18n "skip_to_content" }}</a>

<main class="resume" id="main">
  <div class="resume__page">
    {{ partial "header.html" . }}

    <article class="resume__card">
      <header class="resume__header">
        {{ if .Site.Params.profile.enable }}{{ partial "profile.html" . }}{{ end }}
        {{ if .Site.Params.contact.enable }}{{ partial "contact.html" . }}{{ end }}
      </header>

      {{ if .Site.Params.summary.enable }}{{ partial "summary.html" . }}{{ end }}

      <div class="resume__grid">
        <div class="resume__main">
          {{ if .Site.Params.experience.enable }}{{ partial "experience.html" . }}{{ end }}
          {{ if .Site.Params.skills.enable }}{{ partial "skills.html" . }}{{ end }}
          {{ if .Site.Params.projects.enable }}{{ partial "projects.html" . }}{{ end }}
        </div>

        <aside class="resume__aside">
          {{ partial "sidebar.html" . }}
        </aside>
      </div>

      {{ partial "footer.html" . }}
    </article>
  </div>
</main>
```

- [ ] **Step 3: Réécrire `layouts/_default/baseof.html` en squelette à blocks**

Remplacement complet du fichier :

```html
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
  {{ partial "head.html" . }}

  <body>
    {{ block "main" . }}{{ end }}
    {{ partial "scripts.html" . }}
  </body>
</html>
```

- [ ] **Step 4: Réécrire `layouts/index.html` (home = ancien CV, temporairement)**

Remplacement complet du fichier :

```html
{{ define "main" }}
{{ partial "print-resume.html" . }}
{{ end }}
```

- [ ] **Step 5: Créer `layouts/print/list.html`**

```html
{{ define "main" }}
{{ partial "print-resume.html" . }}
{{ end }}
```

- [ ] **Step 6: Créer les pages de contenu print**

`content/print/_index.en.md` :

```yaml
---
title: "Print"
sitemap:
  disable: true
---
```

`content/print/_index.fr.md` :

```yaml
---
title: "Print"
sitemap:
  disable: true
---
```

- [ ] **Step 7: Ajouter le meta noindex dans `layouts/partials/head.html`**

Juste après la ligne `<meta name="referrer" content="no-referrer-when-downgrade" />`, insérer :

```html
{{ if eq .Type "print" }}<meta name="robots" content="noindex" />{{ end }}
```

- [ ] **Step 8: Pointer `get_pdf.py` sur `/print/`**

Ligne 119, remplacer :

```python
            page_url = f"{SITE_URL}/{lang}/"
```

par :

```python
            page_url = f"{SITE_URL}/{lang}/print/"
```

- [ ] **Step 9: Vérifier**

Run:
```bash
./hugo.exe --quiet \
  && grep -c 'resume__card' public/en/print/index.html \
  && grep -c 'resume__card' public/fr/print/index.html \
  && grep -c 'resume__card' public/en/index.html \
  && grep -c 'name="robots" content="noindex"' public/en/print/index.html \
  && (grep -l 'print' public/en/sitemap.xml public/fr/sitemap.xml || echo "sitemap OK: no print")
```
Expected: quatre `1` (ou plus) puis `sitemap OK: no print`. Le build ne doit émettre aucun warning de template.

- [ ] **Step 10: Commit**

```bash
git add layouts content get_pdf.py
git commit -m "Refonte : vue /print/ dédiée pour le PDF, baseof à blocks"
```

---

### Task 2: Fonts self-hosted + `landing.css` (tokens, base, thème) + head conditionnel

**Files:**
- Create: `static/fonts/inter-400.woff2`, `static/fonts/inter-500.woff2`, `static/fonts/inter-600.woff2`, `static/fonts/inter-700.woff2`, `static/fonts/jetbrains-mono-400.woff2`, `static/fonts/jetbrains-mono-500.woff2`
- Create: `assets/css/landing.css`
- Modify: `layouts/partials/head.html` (CSS/fonts conditionnels par vue)
- Modify: `assets/js/darkmode.js` (défaut sombre)

**Interfaces:**
- Consumes: `.Type == "print"` (Task 1).
- Produces: classes CSS utilisées par les Tasks 3–6 : `landing`, `topbar`, `hero`, `badge-available`, `btn btn--primary`, `btn btn--ghost`, `stats`, `section`, `section__title`, `chip`, `timeline`, `term-card`, `edu`, `footer-cta`, `icon`, `notfound`. Thème : tokens `--bg --surface --surface-2 --text --muted --accent --accent-ink --border`.

- [ ] **Step 1: Télécharger les fonts (woff2, latin)**

```bash
mkdir -p static/fonts/tmp
curl -L -o static/fonts/tmp/inter.zip "https://gwfh.mranftl.com/api/fonts/inter?download=zip&subsets=latin&variants=regular,500,600,700&formats=woff2"
curl -L -o static/fonts/tmp/jbm.zip "https://gwfh.mranftl.com/api/fonts/jetbrains-mono?download=zip&subsets=latin&variants=regular,500&formats=woff2"
unzip -o static/fonts/tmp/inter.zip -d static/fonts/tmp
unzip -o static/fonts/tmp/jbm.zip -d static/fonts/tmp
mv static/fonts/tmp/inter-*-latin-regular.woff2 static/fonts/inter-400.woff2
mv static/fonts/tmp/inter-*-latin-500.woff2     static/fonts/inter-500.woff2
mv static/fonts/tmp/inter-*-latin-600.woff2     static/fonts/inter-600.woff2
mv static/fonts/tmp/inter-*-latin-700.woff2     static/fonts/inter-700.woff2
mv static/fonts/tmp/jetbrains-mono-*-latin-regular.woff2 static/fonts/jetbrains-mono-400.woff2
mv static/fonts/tmp/jetbrains-mono-*-latin-500.woff2     static/fonts/jetbrains-mono-500.woff2
rm -rf static/fonts/tmp
ls -la static/fonts/
```
Expected: 6 fichiers `.woff2` (20–50 Ko chacun).
Fallback si l'API gwfh est indisponible : garder les liens Google Fonts pour la landing aussi (supprimer les `@font-face` du Step 2 et conserver le `<link>` fonts dans la branche landing du head au Step 3) — noter la déviation dans le commit.

- [ ] **Step 2: Créer `assets/css/landing.css`**

Fichier complet :

```css
/*!
 * Landing stylesheet — vue écran /en/ et /fr/.
 * Terminal élégant : sombre par défaut, accent menthe, Inter + JetBrains Mono
 * self-hosted, zéro dépendance externe. La vue /print/ garde devresume.css.
 */

/* ============ 0. Fonts (self-hosted) ============ */
@font-face { font-family: "Inter"; font-style: normal; font-weight: 400; font-display: swap; src: url("/fonts/inter-400.woff2") format("woff2"); }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 500; font-display: swap; src: url("/fonts/inter-500.woff2") format("woff2"); }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 600; font-display: swap; src: url("/fonts/inter-600.woff2") format("woff2"); }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 700; font-display: swap; src: url("/fonts/inter-700.woff2") format("woff2"); }
@font-face { font-family: "JetBrains Mono"; font-style: normal; font-weight: 400; font-display: swap; src: url("/fonts/jetbrains-mono-400.woff2") format("woff2"); }
@font-face { font-family: "JetBrains Mono"; font-style: normal; font-weight: 500; font-display: swap; src: url("/fonts/jetbrains-mono-500.woff2") format("woff2"); }

/* ============ 1. Tokens ============ */
/* Clair (appliqué seulement sans .dark ; le script head met .dark par défaut) */
:root {
  --bg: #f5f7f6;
  --surface: #ffffff;
  --surface-2: #eef2f0;
  --text: #10201a;
  --muted: #52645c;
  --accent: #047857;          /* emerald-700 — AA sur fond clair */
  --accent-soft: rgba(4, 120, 87, 0.12);
  --accent-ink: #ffffff;      /* texte posé sur un fond accent */
  --border: #dce4e0;
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
  --radius: 12px;
  --maxw: 960px;
  color-scheme: light;
}

html.dark {
  --bg: #0b0f14;
  --surface: #111821;
  --surface-2: #0e141b;
  --text: #e6edf3;
  --muted: #94a3ae;
  --accent: #6ee7b7;          /* menthe — AA sur #0b0f14 */
  --accent-soft: rgba(110, 231, 183, 0.12);
  --accent-ink: #06281b;
  --border: #1f2a35;
  color-scheme: dark;
}

/* ============ 2. Reset & base ============ */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.65;
}
img { max-width: 100%; display: block; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
h1, h2, h3 { line-height: 1.2; margin: 0; }
p { margin: 0; }
ul { margin: 0; padding: 0; list-style: none; }

.visually-hidden {
  position: absolute; width: 1px; height: 1px; margin: -1px;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap;
}
.visually-hidden:focus {
  position: fixed; top: 8px; left: 8px; width: auto; height: auto;
  padding: 8px 12px; background: var(--surface); clip: auto; z-index: 100;
}

.mono { font-family: var(--font-mono); }

/* ============ 3. Layout ============ */
.landing { max-width: var(--maxw); margin: 0 auto; padding: 0 20px 48px; }
.section { margin-top: 72px; }
.section__title {
  font-size: 1.35rem; font-weight: 700; letter-spacing: -0.01em;
  margin-bottom: 24px;
}
.section__hash { font-family: var(--font-mono); color: var(--accent); margin-right: 8px; }

/* ============ 4. Topbar ============ */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 0; gap: 12px;
}
.lang-switch { display: flex; gap: 4px; font-family: var(--font-mono); font-size: 0.85rem; }
.lang-switch__link { padding: 4px 8px; border-radius: 6px; color: var(--muted); }
.lang-switch__link[aria-current="true"] { color: var(--accent); background: var(--accent-soft); }
.lang-switch__link:hover { text-decoration: none; color: var(--text); }

.theme-toggle { display: inline-flex; cursor: pointer; }
.theme-toggle input { position: absolute; opacity: 0; }
.theme-toggle__track {
  width: 40px; height: 22px; border-radius: 11px; background: var(--surface-2);
  border: 1px solid var(--border); display: inline-block; position: relative;
  transition: background 0.15s;
}
.theme-toggle__thumb {
  position: absolute; top: 2px; left: 2px; width: 16px; height: 16px;
  border-radius: 50%; background: var(--accent); transition: transform 0.15s;
}
.theme-toggle input:checked + .theme-toggle__track .theme-toggle__thumb { transform: translateX(18px); }
.theme-toggle input:focus-visible + .theme-toggle__track { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ============ 5. Hero ============ */
.hero { margin-top: 48px; display: grid; grid-template-columns: 1fr auto; gap: 32px; align-items: start; }
.hero__prompt { font-family: var(--font-mono); color: var(--muted); font-size: 0.95rem; margin-bottom: 12px; }
.hero__prompt .prompt-sign { color: var(--accent); margin-right: 8px; }
.cursor {
  display: inline-block; width: 9px; height: 1.1em; margin-left: 6px;
  background: var(--accent); vertical-align: text-bottom;
  animation: blink 1.1s steps(1) infinite;
}
@keyframes blink { 50% { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .cursor { animation: none; }
  html { scroll-behavior: auto; }
}
.hero__name { font-size: clamp(2.2rem, 6vw, 3.4rem); font-weight: 700; letter-spacing: -0.02em; }
.hero__headline { font-size: 1.15rem; color: var(--muted); margin-top: 8px; }
.hero__summary { margin-top: 20px; max-width: 58ch; color: var(--text); }
.hero__avatar { width: 96px; height: 96px; border-radius: 50%; border: 2px solid var(--border); object-fit: cover; }

.badge-available {
  display: inline-flex; align-items: center; gap: 8px; margin-top: 16px;
  font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent);
  background: var(--accent-soft); border: 1px solid var(--border);
  border-radius: 999px; padding: 5px 12px;
}
.badge-available .dot {
  width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
  animation: blink 2.2s steps(1) infinite;
}

.hero__cta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-mono); font-size: 0.9rem; font-weight: 500;
  padding: 10px 18px; border-radius: var(--radius); border: 1px solid var(--border);
  color: var(--text); background: var(--surface); cursor: pointer;
}
.btn:hover { text-decoration: none; border-color: var(--accent); }
.btn--primary { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.btn--primary:hover { filter: brightness(1.08); }
.btn--ghost { background: transparent; }

/* ============ 6. Stats ============ */
.stats {
  margin-top: 56px; display: grid; gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.stat {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 18px 20px;
}
.stat__value { font-family: var(--font-mono); font-size: 1.6rem; font-weight: 500; color: var(--accent); }
.stat__label { color: var(--muted); font-size: 0.9rem; margin-top: 4px; }

/* ============ 7. Timeline (expérience) ============ */
.timeline { border-left: 2px solid var(--border); padding-left: 24px; display: grid; gap: 40px; }
.timeline__item { position: relative; }
.timeline__item::before {
  content: ""; position: absolute; left: -31px; top: 6px;
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--accent); border: 2px solid var(--bg);
}
.timeline__dates { font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent); }
.timeline__role { font-size: 1.1rem; font-weight: 600; margin-top: 4px; }
.timeline__org { color: var(--muted); font-size: 0.95rem; }
.timeline__details { margin-top: 10px; color: var(--text); }
.timeline__bullets { margin-top: 10px; display: grid; gap: 6px; }
.timeline__bullets li { padding-left: 18px; position: relative; color: var(--text); }
.timeline__bullets li::before { content: ">"; position: absolute; left: 0; color: var(--accent); font-family: var(--font-mono); }

.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.chip {
  font-family: var(--font-mono); font-size: 0.78rem; color: var(--text);
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 6px; padding: 3px 9px;
}

/* ============ 8. Projets (cards terminal) ============ */
.projects { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.term-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden;
  transition: border-color 0.15s, transform 0.15s;
}
.term-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.term-card__bar {
  display: flex; align-items: center; gap: 6px;
  background: var(--surface-2); border-bottom: 1px solid var(--border);
  padding: 8px 14px;
}
.term-card__dot { width: 10px; height: 10px; border-radius: 50%; background: var(--border); }
.term-card__title { font-family: var(--font-mono); font-size: 0.8rem; color: var(--muted); margin-left: 6px; }
.term-card__body { padding: 18px 20px 22px; }
.term-card__name { font-size: 1.05rem; font-weight: 600; }
.term-card__name a { color: var(--text); }
.term-card__name a:hover { color: var(--accent); text-decoration: none; }
.term-card__meta { font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent); margin-top: 2px; }
.term-card__tagline { color: var(--muted); font-size: 0.95rem; margin-top: 10px; }

/* ============ 9. Skills ============ */
.skills-group { margin-bottom: 20px; }
.skills-group__name { font-family: var(--font-mono); font-size: 0.85rem; color: var(--muted); margin-bottom: 8px; }

/* ============ 10. Formation + Langues ============ */
.edu { display: grid; gap: 32px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
.edu__item + .edu__item { margin-top: 16px; }
.edu__degree { font-weight: 600; }
.edu__sub { color: var(--muted); font-size: 0.9rem; }
.lang-list li { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed var(--border); }
.lang-list .level { color: var(--muted); font-family: var(--font-mono); font-size: 0.85rem; }

/* ============ 11. Footer CTA ============ */
.footer-cta {
  margin-top: 88px; text-align: center;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 48px 24px;
}
.footer-cta__title { font-size: 1.6rem; font-weight: 700; }
.footer-cta__text { color: var(--muted); margin-top: 8px; }
.footer-cta .btn { margin-top: 24px; }
.footer-cta__social { display: flex; justify-content: center; gap: 16px; margin-top: 28px; }
.footer-cta__social a { color: var(--muted); }
.footer-cta__social a:hover { color: var(--accent); }
.footer-note { text-align: center; color: var(--muted); font-size: 0.8rem; font-family: var(--font-mono); margin-top: 28px; }
.footer-note a { color: var(--muted); text-decoration: underline; }

/* ============ 12. Icônes SVG ============ */
.icon { width: 20px; height: 20px; fill: currentColor; vertical-align: middle; }
.icon--sm { width: 16px; height: 16px; }

/* ============ 13. 404 ============ */
.notfound { text-align: center; padding: 96px 20px; }
.notfound__code { font-family: var(--font-mono); font-size: 5rem; color: var(--accent); }
.notfound__title { font-size: 1.4rem; margin-top: 8px; }
.notfound__text { color: var(--muted); margin: 12px 0 24px; }

/* ============ 14. Responsive ============ */
@media (max-width: 640px) {
  .hero { grid-template-columns: 1fr; }
  .hero__avatar { order: -1; }
  .section { margin-top: 56px; }
}
```

- [ ] **Step 3: Rendre `layouts/partials/head.html` conditionnel par vue**

Remplacer le bloc fonts + FontAwesome + CSS (lignes 47–63 du fichier actuel, des commentaires `<!-- Fonts: ... -->` à la fin du `{{ with resources.Get "css/devresume.css" ... }}`) par :

```html
{{ if eq .Type "print" }}
<!-- Vue print : stack historique conservée à l'identique (pdf.co l'imprime) -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
/>
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v6.1.1/css/all.css" />
{{ with resources.Get "css/devresume.css" | minify | fingerprint }}
<style>
  {{ .Content | safeCSS }}
</style>
{{ end }}
{{ else }}
<!-- Vue landing : fonts self-hosted, zéro dépendance externe -->
<link rel="preload" href="/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/fonts/jetbrains-mono-400.woff2" as="font" type="font/woff2" crossorigin />
{{ with resources.Get "css/landing.css" | minify | fingerprint }}
<style>
  {{ .Content | safeCSS }}
</style>
{{ end }}
{{ end }}
```

Puis, dans le script inline de thème en haut du même fichier, remplacer :

```js
      var dark = t === "dark" || (t !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
```

par (sombre par défaut, spec §Design) :

```js
      var dark = t !== "light";
```

- [ ] **Step 4: Aligner `assets/js/darkmode.js` sur le défaut sombre**

Remplacement complet du fichier :

```js
// Theme toggle — wires the #darkSwitch checkbox to the `.dark` class on <html>.
// Dark is the default; light only applies when the user explicitly chose it.
// The initial class is applied by an inline script in <head> (no flash).
(function () {
  var toggle = document.getElementById("darkSwitch");
  if (!toggle) return; // pages without the toggle (e.g. 404) simply opt out

  var root = document.documentElement;

  function setTheme(on) {
    root.classList.toggle("dark", on);
    toggle.checked = on;
    try {
      localStorage.setItem("theme", on ? "dark" : "light");
    } catch (e) {}
  }

  // Sync the checkbox with whatever the head script already applied.
  toggle.checked = root.classList.contains("dark");

  toggle.addEventListener("change", function () {
    setTheme(toggle.checked);
  });
})();
```

- [ ] **Step 5: Vérifier**

Run:
```bash
./hugo.exe --quiet \
  && grep -c 'fontawesome' public/en/print/index.html \
  && (grep -q 'fontawesome' public/en/index.html && echo "FAIL: FA on landing" || echo "OK: no FA on landing") \
  && grep -c 'fonts/inter-400.woff2' public/en/index.html
```
Expected: `1` (print garde FontAwesome), `OK: no FA on landing`, puis `1` ou plus.
Note : à ce stade la home rend encore l'ancien markup avec le nouveau CSS — rendu cassé attendu et acceptable, la landing arrive en Task 3.

- [ ] **Step 6: Commit**

```bash
git add static/fonts assets/css/landing.css assets/js/darkmode.js layouts/partials/head.html
git commit -m "Refonte : fonts self-hosted, landing.css (tokens + base), défaut sombre"
```

---

### Task 3: Contenu enrichi (`config.toml` + i18n) — badge dispo, stats, bullets

Les textes ci-dessous sont **verbatim** — ne pas improviser.

**Files:**
- Modify: `config.toml` (ajouts sous `[languages.en.params]` et `[languages.fr.params]` + bullets d'expérience)
- Modify: `i18n/en.yaml`, `i18n/fr.yaml`

**Interfaces:**
- Produces: `params.hero.available` (bool), `params.hero.availability` (string), `params.stats.list[]` avec `value`/`label`, clés i18n `contact_me`, `footer_cta_title`, `footer_cta_text`, `open_source_note`. Consommés par Tasks 5–6.

- [ ] **Step 1: Ajouter les params hero + stats dans `config.toml`**

Sous `[languages.en.params]`, juste après le bloc `[languages.en.params.summary]` :

```toml
    [languages.en.params.hero]
        available = true
        availability = "Open to new opportunities"

    [languages.en.params.stats]
        enable = true

        [[languages.en.params.stats.list]]
        value = "5+"
        label = "years building backend services in production"

        [[languages.en.params.stats.list]]
        value = ".NET · Oracle · Azure"
        label = "core stack, from API design to CI/CD"

        [[languages.en.params.stats.list]]
        value = "FR · EN · VI"
        label = "working languages"
```

Sous `[languages.fr.params]`, juste après le bloc `[languages.fr.params.summary]` :

```toml
    [languages.fr.params.hero]
        available = true
        availability = "Disponible pour de nouvelles opportunités"

    [languages.fr.params.stats]
        enable = true

        [[languages.fr.params.stats.list]]
        value = "5+"
        label = "années de services backend en production"

        [[languages.fr.params.stats.list]]
        value = ".NET · Oracle · Azure"
        label = "stack principale, de l'API au CI/CD"

        [[languages.fr.params.stats.list]]
        value = "FR · EN · VI"
        label = "langues de travail"
```

- [ ] **Step 2: Reformuler les bullets d'expérience (orientés résultats, zéro fait inventé)**

Dans `config.toml`, remplacer les 4 `details` des `[[languages.en.params.experience.list.items]]` par, dans l'ordre :

1. `"Design and ship .NET Core backend services and REST APIs at the heart of AKANEA's customs software."`
2. `"Optimize PL/SQL routines on Oracle for high-volume transactional workloads, from profiling to query tuning."`
3. `"Run deployments on Azure — virtual machines and CI/CD pipelines — from build to production."`
4. `"Contribute across the full lifecycle in an Agile/Scrum team, from domain design to production support."`

Et les 4 `details` FR par :

1. `"Conception et livraison de services backend et d'API REST en .NET Core, au cœur des logiciels douaniers d'AKANEA."`
2. `"Optimisation de routines PL/SQL sur Oracle pour des charges transactionnelles à fort volume, du profilage au tuning de requêtes."`
3. `"Déploiements sur Azure — machines virtuelles et pipelines CI/CD — du build à la production."`
4. `"Contribution sur tout le cycle en équipe Agile/Scrum, de la conception du domaine au support en production."`

- [ ] **Step 3: Ajouter les clés i18n**

À la fin de `i18n/en.yaml` (avant le commentaire `# Legacy keys`) :

```yaml
- id: contact_me
  translation: Get in touch
- id: footer_cta_title
  translation: A role or a project in mind?
- id: footer_cta_text
  translation: "The fastest way to reach me is email."
- id: open_source_note
  translation: This resume is open source
```

À l'endroit équivalent de `i18n/fr.yaml` :

```yaml
- id: contact_me
  translation: Me contacter
- id: footer_cta_title
  translation: Un poste ou un projet en tête ?
- id: footer_cta_text
  translation: "Le plus simple pour me joindre : un email."
- id: open_source_note
  translation: Ce CV est open source
```

- [ ] **Step 4: Vérifier**

Run:
```bash
./hugo.exe --quiet \
  && grep -c "Disponible pour de nouvelles" public/fr/print/index.html || true
```
Expected: build sans erreur. (Le `grep` rend `0` — les nouveaux params ne sont consommés par aucun template encore ; l'important est l'absence d'erreur TOML/YAML.)
Vérifier aussi que la vue print reflète les nouveaux bullets :
```bash
grep -c "query tuning" public/en/print/index.html
```
Expected: `1`.

- [ ] **Step 5: Commit**

```bash
git add config.toml i18n
git commit -m "Refonte : contenu enrichi — badge dispo, stats, bullets orientés résultats"
```

---

### Task 4: Partial d'icônes SVG

**Files:**
- Create: `layouts/partials/icon.html`

**Interfaces:**
- Produces: `{{ partial "icon.html" "github" }}` → SVG inline (`class="icon"`). Noms supportés : `github`, `linkedin`, `twitter`, `mail`, `download`, `external`, `location`, `globe`, `phone`. Consommé par Tasks 5–6.

- [ ] **Step 1: Créer `layouts/partials/icon.html`**

```html
{{- $name := . -}}
{{- $icons := dict
  "github" "<path d=\"M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.15c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.76 2.7 1.25 3.35.96.1-.75.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.51-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.62 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.69 5.38-5.26 5.66.41.36.78 1.05.78 2.13v3.16c0 .3.2.66.8.55A11.52 11.52 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z\"/>"
  "linkedin" "<path d=\"M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45z\"/>"
  "twitter" "<path d=\"M23.95 4.57a10 10 0 0 1-2.83.78 4.93 4.93 0 0 0 2.16-2.72 9.86 9.86 0 0 1-3.13 1.2 4.92 4.92 0 0 0-8.39 4.49A13.98 13.98 0 0 1 1.64 3.16a4.92 4.92 0 0 0 1.52 6.57 4.9 4.9 0 0 1-2.23-.61v.06a4.93 4.93 0 0 0 3.95 4.83 4.94 4.94 0 0 1-2.22.08 4.93 4.93 0 0 0 4.6 3.42A9.88 9.88 0 0 1 0 19.54a13.94 13.94 0 0 0 7.55 2.21c9.06 0 14.01-7.5 14.01-14.01 0-.21 0-.42-.02-.63a10 10 0 0 0 2.41-2.54z\"/>"
  "mail" "<path d=\"M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4.24-8 5-8-5V6.47l8 5 8-5v1.77z\"/>"
  "download" "<path d=\"M12 16.5 5.5 10h4V3h5v7h4L12 16.5zM4 19h16v2H4v-2z\"/>"
  "external" "<path d=\"M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3zM5 5h6v2H7v10h10v-4h2v6H5V5z\"/>"
  "location" "<path d=\"M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z\"/>"
  "globe" "<path d=\"M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm7.93 9h-3.02a15.7 15.7 0 0 0-1.1-5.02A8.02 8.02 0 0 1 19.93 11zM12 4.04c.86 1.16 1.62 3.06 1.9 6.96h-3.8c.28-3.9 1.04-5.8 1.9-6.96zM4.07 13h3.02c.14 1.9.52 3.6 1.1 5.02A8.02 8.02 0 0 1 4.07 13zm3.02-2H4.07a8.02 8.02 0 0 1 4.12-5.02A15.7 15.7 0 0 0 7.09 11zM12 19.96c-.86-1.16-1.62-3.06-1.9-6.96h3.8c-.28 3.9-1.04 5.8-1.9 6.96zm3.81-1.94c.58-1.42.96-3.12 1.1-5.02h3.02a8.02 8.02 0 0 1-4.12 5.02z\"/>"
  "phone" "<path d=\"M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.02-.24c1.12.37 2.33.57 3.57.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1C10.61 21 3 13.39 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.24.2 2.45.57 3.57a1 1 0 0 1-.24 1.02l-2.21 2.2z\"/>"
-}}
<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{{ index $icons $name | safeHTML }}</svg>
```

- [ ] **Step 2: Vérifier**

Run: `./hugo.exe --quiet && echo BUILD_OK`
Expected: `BUILD_OK` (le partial n'est pas encore consommé ; on vérifie juste qu'il parse).

- [ ] **Step 3: Commit**

```bash
git add layouts/partials/icon.html
git commit -m "Refonte : partial d'icônes SVG inline"
```

---

### Task 5: Landing — markup complet (`layouts/index.html`)

**Files:**
- Modify: `layouts/index.html` (remplacement complet)

**Interfaces:**
- Consumes: classes CSS de Task 2, params de Task 3, `{{ partial "icon.html" ... }}` de Task 4, i18n keys existantes (`experiences`, `skills`, `projects`, `education`, `languages`, `download_pdf_a4`, `download_pdf_letter`, `language_switch_label`, `dark_mode`, `skip_to_content`) et nouvelles (Task 3).
- Produces: la page d'accueil finale ; l'id `#darkSwitch` requis par `darkmode.js`.

- [ ] **Step 1: Remplacer `layouts/index.html` en entier**

```html
{{ define "main" }}
{{- /* email extrait de contact.list (source unique de vérité) */ -}}
{{- $email := "" -}}
{{- range .Site.Params.contact.list -}}{{- if hasPrefix .url "mailto:" -}}{{- $email = strings.TrimPrefix "mailto:" .url -}}{{- end -}}{{- end -}}

<a class="visually-hidden" href="#main">{{ i18n "skip_to_content" }}</a>

<div class="landing" id="main">
  <header class="topbar">
    <nav class="lang-switch" aria-label="{{ i18n "language_switch_label" }}">
      {{ range .Sites }}
        {{ $lang := .Language.Lang }}
        <a class="lang-switch__link" href="{{ (printf "/%s/" $lang) | relURL }}" hreflang="{{ $lang }}" lang="{{ $lang }}"{{ if eq $lang $.Site.Language.Lang }} aria-current="true"{{ end }}>{{ $lang | upper }}</a>
      {{ end }}
    </nav>

    <label class="theme-toggle">
      <input type="checkbox" id="darkSwitch" />
      <span class="theme-toggle__track"><span class="theme-toggle__thumb"></span></span>
      <span class="visually-hidden">{{ i18n "dark_mode" }}</span>
    </label>
  </header>

  <section class="hero">
    <div>
      <p class="hero__prompt"><span class="prompt-sign">$</span>whoami<span class="cursor"></span></p>
      <h1 class="hero__name">{{ .Site.Params.profile.name }}</h1>
      <p class="hero__headline">{{ .Site.Params.profile.headline }}</p>

      {{ with .Site.Params.hero }}{{ if .available }}
      <p class="badge-available"><span class="dot"></span>{{ .availability }}</p>
      {{ end }}{{ end }}

      {{ with .Site.Params.summary }}{{ if .enable }}
      <p class="hero__summary">{{ .text }}</p>
      {{ end }}{{ end }}

      <div class="hero__cta">
        <a class="btn btn--primary" href="mailto:{{ $email }}">{{ partial "icon.html" "mail" }}{{ i18n "contact_me" }}</a>
        <a class="btn btn--ghost" href="{{ printf "/resume.%s.a4.pdf" .Site.Language.Lang | relURL }}">{{ partial "icon.html" "download" }}{{ i18n "download_pdf_a4" }}</a>
        <a class="btn btn--ghost" href="{{ printf "/resume.%s.letter.pdf" .Site.Language.Lang | relURL }}">{{ partial "icon.html" "download" }}{{ i18n "download_pdf_letter" }}</a>
      </div>
    </div>

    {{ with .Site.Params.profile.avatar }}
    <img class="hero__avatar" src="{{ printf "assets/images/%s" . | relURL }}" alt="{{ $.Site.Params.profile.name }}" width="96" height="96" />
    {{ end }}
  </section>

  {{ with .Site.Params.stats }}{{ if .enable }}
  <section class="stats" aria-label="Key facts">
    {{ range .list }}
    <div class="stat">
      <div class="stat__value">{{ .value }}</div>
      <div class="stat__label">{{ .label }}</div>
    </div>
    {{ end }}
  </section>
  {{ end }}{{ end }}

  {{ with .Site.Params.experience }}{{ if .enable }}
  <section class="section" id="experience">
    <h2 class="section__title"><span class="section__hash">##</span>{{ i18n "experiences" }}</h2>
    <div class="timeline">
      {{ range .list }}
      <div class="timeline__item">
        <p class="timeline__dates">{{ .dates }}</p>
        <h3 class="timeline__role">{{ .title }}</h3>
        <p class="timeline__org">{{ .company }} — {{ .location }}</p>
        {{ with .details }}<p class="timeline__details">{{ . }}</p>{{ end }}
        {{ with .items }}
        <ul class="timeline__bullets">
          {{ range . }}<li>{{ .details }}</li>{{ end }}
        </ul>
        {{ end }}
        {{ with .tech }}
        <div class="chips">
          {{ range . }}<span class="chip">{{ . }}</span>{{ end }}
        </div>
        {{ end }}
      </div>
      {{ end }}
    </div>
  </section>
  {{ end }}{{ end }}

  {{ with .Site.Params.projects }}{{ if .enable }}
  <section class="section" id="projects">
    <h2 class="section__title"><span class="section__hash">##</span>{{ i18n "projects" }}</h2>
    <div class="projects">
      {{ range .list }}
      <article class="term-card">
        <div class="term-card__bar">
          <span class="term-card__dot"></span><span class="term-card__dot"></span><span class="term-card__dot"></span>
          <span class="term-card__title">{{ .meta }}</span>
        </div>
        <div class="term-card__body">
          <h3 class="term-card__name">
            {{ if .url }}<a href="{{ .url }}" rel="noopener">{{ .title }} {{ partial "icon.html" "external" }}</a>{{ else }}{{ .title }}{{ end }}
          </h3>
          <p class="term-card__tagline">{{ .tagline }}</p>
        </div>
      </article>
      {{ end }}
    </div>
  </section>
  {{ end }}{{ end }}

  {{ with .Site.Params.skills }}{{ if .enable }}
  <section class="section" id="skills">
    <h2 class="section__title"><span class="section__hash">##</span>{{ i18n "skills" }}</h2>
    {{ range .list }}
    <div class="skills-group">
      <p class="skills-group__name">{{ .category }}</p>
      <div class="chips">
        {{ range .items }}<span class="chip">{{ . }}</span>{{ end }}
      </div>
    </div>
    {{ end }}
  </section>
  {{ end }}{{ end }}

  <section class="section edu" id="education">
    {{ with .Site.Params.education }}{{ if .enable }}
    <div>
      <h2 class="section__title"><span class="section__hash">##</span>{{ i18n "education" }}</h2>
      {{ range .list }}
      <div class="edu__item">
        <p class="edu__degree">{{ .degree }}</p>
        <p class="edu__sub">{{ .university }} · {{ .dates }}</p>
      </div>
      {{ end }}
    </div>
    {{ end }}{{ end }}

    {{ with .Site.Params.languages }}{{ if .enable }}
    <div>
      <h2 class="section__title"><span class="section__hash">##</span>{{ i18n "languages" }}</h2>
      <ul class="lang-list">
        {{ range .list }}
        <li><span>{{ .name }}</span><span class="level">{{ .level }}</span></li>
        {{ end }}
      </ul>
    </div>
    {{ end }}{{ end }}
  </section>

  <section class="footer-cta" id="contact">
    <h2 class="footer-cta__title">{{ i18n "footer_cta_title" }}</h2>
    <p class="footer-cta__text">{{ i18n "footer_cta_text" }}</p>
    <a class="btn btn--primary" href="mailto:{{ $email }}">{{ partial "icon.html" "mail" }}{{ $email }}</a>

    {{ with .Site.Params.social }}{{ if .enable }}
    <div class="footer-cta__social">
      {{ range .list }}
      <a href="{{ .url }}" rel="noopener" aria-label="{{ .title }}">{{ partial "icon.html" (lower .title) }}</a>
      {{ end }}
    </div>
    {{ end }}{{ end }}
  </section>

  <p class="footer-note">
    {{ i18n "open_source_note" }} — <a href="{{ .Site.Params.ghRepo }}resume" rel="noopener">github.com/bornbygoogle/resume</a>
  </p>
</div>
{{ end }}
```

- [ ] **Step 2: Vérifier le rendu généré**

Run:
```bash
./hugo.exe --quiet \
  && grep -c 'hero__name' public/en/index.html \
  && grep -c 'badge-available' public/fr/index.html \
  && grep -c 'term-card' public/en/index.html \
  && grep -c 'mailto:contact@minhan-tran.fr' public/en/index.html \
  && grep -c 'resume__card' public/en/print/index.html
```
Expected: chaque compte ≥ 1 (le HTML non minifié répète les classes sur plusieurs lignes ; seule l'absence de match, `0`, est un échec) — et zéro warning Hugo.

- [ ] **Step 3: Contrôle visuel local**

Run: `./hugo.exe server --port 1313` (en arrière-plan), puis ouvrir `http://localhost:1313/en/`, `http://localhost:1313/fr/`, `http://localhost:1313/en/print/`.
Vérifier : hero sombre avec curseur clignotant, badge « Disponible », CTA email + 2 PDF, stats, timeline, cards projets, chips skills, footer CTA ; toggle thème fonctionne ; `/print/` identique à l'ancien rendu. Arrêter le serveur.

- [ ] **Step 4: Commit**

```bash
git add layouts/index.html
git commit -m "Refonte : landing terminal sombre (hero, stats, timeline, projets, footer CTA)"
```

---

### Task 6: 404, robots, README — finitions

**Files:**
- Modify: `layouts/404.html`
- Modify: `README.md` (section architecture)

**Interfaces:**
- Consumes: classes `notfound`, `btn` de `landing.css` (la 404 tombe dans la branche landing du head, `.Type != "print"`).

- [ ] **Step 1: Adapter `layouts/404.html`**

Remplacement complet (mêmes contenus, classes landing) :

```html
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
  {{ partial "head.html" . }}

  <body>
    <main class="landing notfound" id="main">
      <div class="notfound__code">404</div>
      <h1 class="notfound__title">{{ i18n "not_found" }}</h1>
      <p class="notfound__text">{{ .Site.Params.profile.name }}</p>
      <a class="btn btn--primary" href="{{ (printf "/%s/" .Site.Language.Lang) | relURL }}">{{ i18n "back_home" }}</a>
    </main>
  </body>
</html>
```

- [ ] **Step 2: Ajouter la note d'architecture au README**

Ajouter à la fin de `README.md` :

```markdown
## Architecture

- `/en/` and `/fr/` — recruiter-facing landing page (dark, terminal-flavoured,
  self-hosted fonts, no external dependencies). Template: `layouts/index.html`,
  styles: `assets/css/landing.css`.
- `/en/print/` and `/fr/print/` — classic ATS-friendly resume layout
  (`layouts/print/list.html` + `assets/css/devresume.css`), `noindex`, excluded
  from the sitemap. This is the page `get_pdf.py` sends to pdf.co to produce
  `resume.{lang}.{a4,letter}.pdf`.
- All content for both views comes from `config.toml`
  (`languages.<lang>.params.*`) — single source of truth, bilingual.
```

- [ ] **Step 3: Vérifier**

Run:
```bash
./hugo.exe --quiet && grep -c 'notfound__code' public/404.html
```
Expected: `1`.

- [ ] **Step 4: Commit**

```bash
git add layouts/404.html README.md
git commit -m "Refonte : 404 landing, README architecture"
```

---

### Task 7: Vérification finale de bout en bout

**Files:** aucun nouveau — validation.

- [ ] **Step 1: Build propre complet**

```bash
rm -rf public && ./hugo.exe --minify
```
Expected: exit 0, aucun warning.

- [ ] **Step 2: Checklist des 4 pages + hygiène**

```bash
grep -c 'hero__name' public/en/index.html public/fr/index.html
grep -c 'resume__card' public/en/print/index.html public/fr/print/index.html
grep -c 'noindex' public/en/print/index.html public/fr/print/index.html
grep -o 'https://[a-z.]*fontawesome[^"]*' public/en/index.html || echo "OK no external CSS on landing"
grep -rl 'print' public/en/sitemap.xml public/fr/sitemap.xml || echo "OK sitemap"
grep -c 'darkSwitch' public/en/index.html
```
Expected: `1` partout où un compte est attendu, `OK no external CSS on landing`, `OK sitemap`, `1`.

- [ ] **Step 3: Contrôle print (proxy pdf.co)**

Lancer `./hugo.exe server`, ouvrir `http://localhost:1313/en/print/`, faire Ctrl+P (aperçu d'impression) et vérifier que le rendu A4 correspond au PDF actuel (2 colonnes, clair, sections complètes). Répéter pour `/fr/print/`.

- [ ] **Step 4: Accessibilité rapide**

Sur `/en/` : vérifier au clavier (Tab) que le skip-link, le lang-switch, les CTA et le toggle thème sont atteignables et focus-visibles ; vérifier le contraste du texte muted (`#94a3ae` sur `#0b0f14` ≈ 7:1, AA OK). Si Chrome est disponible, lancer un audit Lighthouse (DevTools → Lighthouse, Performance + Accessibility) sur `http://localhost:1313/en/` : viser ≥ 95 dans les deux catégories — la page n'a aucune dépendance externe, un score plus bas signale un problème à corriger.

- [ ] **Step 5: Commit final (si retouches) et push**

```bash
git status --short
# si retouches faites pendant la vérification :
git add -A && git commit -m "Refonte : ajustements de vérification finale"
```
Ne **pas** pousser sans accord explicite de l'utilisateur : le push sur `main` déclenche le workflow GitHub Actions (déploiement Netlify + génération des PDF via pdf.co, qui consomme des crédits API).
```

---

## Notes pour l'exécutant

- Le repo embarque son binaire Hugo : toujours `./hugo.exe`, pas un Hugo global.
- `defaultContentLanguageInSubdir = true` : les pages home sont `public/en/index.html` et `public/fr/index.html`, jamais `public/index.html` (qui contient la redirection alias).
- La vue `/print/` en navigateur peut s'afficher en sombre (défaut du thème) : sans importance, pdf.co imprime avec `mediaType: "print"` et le bloc `@media print` de `devresume.css` force le rendu papier.
- Si `hugo server` est déjà lancé sur 1313, utiliser `--port 1314`.
