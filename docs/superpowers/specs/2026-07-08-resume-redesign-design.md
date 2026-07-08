# Refonte du CV en ligne — Design

**Date :** 2026-07-08
**Statut :** Validé par l'utilisateur

## Objectif

Moderniser le site CV (Hugo, bilingue EN/FR, hébergé sur Netlify) pour maximiser
les premiers contacts recruteurs. La page écran devient une landing "tech /
développeur" sombre et scannable ; le PDF ATS-friendly généré par pdf.co reste
un CV classique, inchangé visuellement.

## Décisions de cadrage

| Sujet | Décision |
|---|---|
| Ambition | Page perso moderne (landing recruteur), plus un « CV papier en ligne » |
| Style visuel écran | Tech / développeur : sombre par défaut, touches terminal, JetBrains Mono en accents |
| CTA principal | Email direct (`mailto:contact@minhan-tran.fr`) ; LinkedIn secondaire ; PDF en téléchargement |
| Contenu | Léger enrichissement orienté conversion (badge dispo, chiffres clés, bullets orientés résultats) — chaque reformulation validée par l'utilisateur, rien d'inventé |
| Architecture PDF | Page `/print/` dédiée par langue, layout actuel conservé, imprimée par pdf.co |

## Architecture des pages

- **`/en/` et `/fr/`** : nouvelle landing. Template `layouts/index.html` réécrit
  + nouveaux partials écran.
- **`/en/print/` et `/fr/print/`** : le layout actuel (2 colonnes, clair,
  ATS-friendly) déplacé tel quel. Meta `noindex` + exclusion sitemap.
- **`get_pdf.py`** : seule modification — `page_url = f"{SITE_URL}/{lang}/print/"`.
- **Source de contenu unique** : les deux vues lisent les mêmes données
  `config.toml` (`languages.<lang>.params.*`). Aucun contenu dupliqué.
- **Thème** : sombre par défaut, toggle clair persistant (localStorage),
  remplace `assets/js/darkmode.js`.
- Sélecteur de langue EN/FR conservé sur les deux vues.

## Design visuel de la landing (écran)

Ambiance terminal élégante, pas gadget :

- Fond sombre profond (pas noir pur), un accent unique : vert menthe néon doux.
- JetBrains Mono réservé aux détails techniques (labels, tags, prompt) ;
  Inter pour le corps. Fonts self-hosted (woff2 dans `static/fonts/`).
- Suppression de Bootstrap et FontAwesome → CSS vanilla + icônes SVG inline.
- Micro-interactions sobres : curseur clignotant du hero, hover discret sur les
  cards. Pas d'animation lourde ; objectif Lighthouse élevé (argument backend).

Structure de haut en bas :

1. **Hero** — intro monospace `$ whoami`, nom en très grand, headline
   « Développeur Backend — .NET Core / Azure », badge vert « Disponible »,
   CTA primaire `[ Me contacter ]` (mailto) et secondaire `[ CV PDF ↓ ]`
   (choix A4 / Letter). Avatar discret.
2. **Chiffres clés** — 3-4 stats dérivées du contenu existant
   (5+ ans, stack .NET/Oracle/Azure, EN · FR · VI).
3. **Expérience** — timeline verticale, bullets orientés résultats,
   chips tech en monospace.
4. **Projets** — cards style « fenêtre de terminal » (barre de titre à
   3 points) : bot de trading crypto, ce CV open-source. Liens externes.
5. **Skills** — groupes actuels rendus en chips scannables.
6. **Formation + Langues** — bloc compact deux colonnes.
7. **Footer CTA** — rappel « Un projet ? Un poste ? » → bouton email,
   liens GitHub/LinkedIn, mention du repo open-source.

## Enrichissement du contenu

- Badge disponibilité dans le hero (nouveau param `config.toml`, bilingue).
- Bullets d'expérience reformulés en résultats — aucun chiffre inventé,
  chaque reformulation proposée à l'utilisateur avant intégration.
- Bloc chiffres clés dérivé du contenu existant.
- Tout ajout existe en EN **et** FR dans `config.toml`.

## Print / PDF

- Les partials actuels deviennent le layout de `/print/` : rendu identique à
  aujourd'hui, donc PDF identique.
- `noindex` (meta robots) sur `/print/` ; pages exclues du sitemap.
- pdf.co continue d'imprimer avec `mediaType: "print"` — le CSS print existant
  (devresume.css) reste attaché à la vue `/print/` uniquement.

## Vérification

1. Build Hugo local sans erreur, deux langues.
2. Contrôle visuel des 4 pages : `/en/`, `/fr/`, `/en/print/`, `/fr/print/`.
3. Rendu print de `/print/` vérifié via l'aperçu d'impression navigateur
   (proxy fidèle de pdf.co `mediaType: print`).
4. `get_pdf.py` inchangé hormis l'URL ; testable en CI comme aujourd'hui.
5. Lighthouse sur la landing (performance + accessibilité), contraste AA sur
   le thème sombre.

## Hors périmètre

- Refonte profonde des textes (au-delà des reformulations validées).
- Formulaire de contact, analytics, blog.
- Changement d'hébergement ou de générateur (on reste sur Hugo + Netlify).
