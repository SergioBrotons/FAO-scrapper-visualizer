# Implementation Plan - DigitalCoa.ch Rebuild

Rebuild `digitalcoa.ch` as a premium, bilingual (EN/FR) corporate website using Next.js App Router, following a "Swiss Grid" design philosophy.

## User Review Required

> [!IMPORTANT]
> - **i18n Architecture**: We will use `next-intl` with the `/[locale]` routing pattern under `/en` and `/fr`.
> - **Content Delivery**: All content will be stored in `messages/en.json` and `messages/fr.json` for easy translation and OpenClaw editing.
> - **Technology Stack**: Next.js 14/15 (App Router), TypeScript, Tailwind CSS, Lucide React (icons).

## Proposed Changes

### 1. Project Core & i18n
- [NEW] `i18n.ts`: i18n configuration for `next-intl`.
- [NEW] `middleware.ts`: Locale routing middleware.
- [NEW] `navigation.ts`: Typed navigation utilities.
- [NEW] `messages/en.json`, `messages/fr.json`: Localized strings.

### 2. Design System & Global Styles
- [NEW] `app/globals.css`: Tailwind configuration with CSS variables for the Swiss Palette (Red, Blue, Green, Ochre, and premium Grayscale).
- [NEW] `tailwind.config.ts`: Customizing typography (Inter/Roboto) and spacing.

### 3. Shared Components
- [NEW] `components/layout/Header.tsx`: Premium navigation with language switcher.
- [NEW] `components/layout/Footer.tsx`: Structured footer with Swiss precision.
- [NEW] `components/ui/Container.tsx`: Standardized layout container.
- [NEW] `components/ui/Button.tsx`: High-polish button components.
- [NEW] `components/ui/Section.tsx`: Semantic section wrapper with variant spacing.
- [NEW] `components/common/SEO.tsx`: Centralized metadata handler.

### 4. Page Architecture (Localized)
- [NEW] `app/[locale]/page.tsx`: Home Page.
- [NEW] `app/[locale]/about/page.tsx`: About Page.
- [NEW] `app/[locale]/services/page.tsx`: Services Overview.
- [NEW] `app/[locale]/services/[slug]/page.tsx`: Service Detail Pages.
- [NEW] `app/[locale]/industries/page.tsx`: Who We Help.
- [NEW] `app/[locale]/insights/page.tsx`: Blog listing.
- [NEW] `app/[locale]/insights/[slug]/page.tsx`: Blog post template.
- [NEW] `app/[locale]/contact/page.tsx`: Contact Form with Server Action.

### 5. SEO & Generative Discovery
- [NEW] `app/sitemap.ts`: Dynamic sitemap generation.
- [NEW] `app/robots.ts`: standard robots rules.
- [NEW] `public/llms.txt`: Machine-readable content summary for LLMs.
- [NEW] `public/humans.txt`: Site credits and information.

## Verification Plan

### Automated Tests/Checks
- `npm run build` to ensure type safety and build correctness.
- `next-intl` validation of missing keys.

### Manual Verification
- **Responsiveness**: Verify on Mobile, Tablet, and Desktop.
- **i18n**: Toggle between EN/FR and verify route persistence and content translation.
- **SEO**: Check `<head>` tags (canonical, alternate, title, description) on any page.
- **Schema**: Validate JSON-LD outputs via Schema Markup Validator.
- **Forms**: Test contact form submission flow.
