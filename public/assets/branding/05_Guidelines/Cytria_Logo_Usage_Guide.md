# Cytria logo usage guide

Version 2.0 - approved smooth cubic vector master. Supersedes the polygon-traced version 1.0.

## Core palette

| Role | HEX | RGB |
|---|---:|---:|
| Cytria Ink | `#080D11` | 8, 13, 17 |
| Cytria Gold | `#C9A24D` | 201, 162, 77 |
| Cytria Canvas | `#FCFAF6` | 252, 250, 246 |
| White | `#FFFFFF` | 255, 255, 255 |

Gold scale: `#FBF7ED` `#F5EACF` `#EBD49A` `#DEBC69` `#D2AA4F` `#C9A24D` `#A77F22` `#805E0D` `#594107` `#332502`
Ink scale: `#080D11` `#0B1117` `#101820` `#17212A` `#25313B` `#3B4650`

There is no navy and no secondary accent colour. Gold is the only accent.

## Approved versions

- On light backgrounds: ink wordmark/C with gold segment.
- On dark backgrounds: white wordmark/C with gold segment.
- One-colour ink, black, or white when colour reproduction is unavailable.
- `-ink` is for pixels, `-black` is for print. They differ by 8/255 per channel. In both, the gold wedge matches the mark colour so the C reads closed. That is correct for one-colour output.
- Use the C symbol for social avatars, favicons, app icons, and very compact spaces.

## Clear space

Maintain clear space equal to the width of the main C stroke around every side. For the C-only symbol, retain the same minimum clear space. Social-media files already include generous crop-safe padding.

## Minimum size

- Full logo: 120 px digital or 30 mm print.
- C symbol: 24 px digital.
- Standard bicolour symbol: 32 px or larger when possible.
- Use the prepared favicon assets below 32 px.

## Do not

- Stretch, compress, rotate, skew, crop, outline, or add effects.
- Change the gold segment's position, scale, or colour.
- Recreate the wordmark with live text or a substitute font.
- Place the ink version on dark backgrounds or the white version on pale backgrounds.
- Use busy photography without a clean, high-contrast holding area.
- Rearrange the C and wordmark or alter their proportions.
- Use the original raster preview as a production logo.

## Website implementation

Use SVG for the header and footer. Use `cytria-logo-on-light.svg` on light surfaces and `cytria-logo-on-dark.svg` on dark surfaces. Keep the full SVG as one image rather than combining a C image with typed text.

```tsx
import Image from "next/image";

<Image
  src="/brand/cytria-logo-on-light.svg"
  alt="Cytria"
  width={190}
  height={70.45}
  style={{ height: "auto" }}
  priority
/>
```

Copy the files in `04_Web` to the Next.js `public` directory and configure metadata:

```tsx
export const metadata = {
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/icon-32x32.png", sizes: "32x32" },
      { url: "/icon-16x16.png", sizes: "16x16" },
    ],
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
};
```

The SVG favicon automatically changes the ink portion to white when the browser reports a dark colour scheme. The gold segment remains consistent.

## File selection

- `01_Master_SVG`: preferred production masters.
- `02_PNG`: transparent high-resolution fallbacks.
- `03_Social`: crop-safe square profile images.
- `04_Web`: favicon, touch icon, web-app icons, and manifest.

## Version 2.0 production rules

All variants derive from the user-approved smooth cubic paths. SVG masters contain paths only, with no fonts or embedded raster images. Use SVG when enlargement is needed; PNGs are finite-resolution exports. Do not enlarge PNGs beyond their intended display resolution.

The C-only files contain only the C and gold segment. Profile exports preserve the exact aspect ratio and include square crop-safe canvases. Favicons preserve the approved geometry on a high-contrast background.

Clear space x is the C stroke width, approximately 48 units in a 243-unit-high visible C. Keep at least x outside the visible artwork on all sides; intrinsic SVG margins alone do not provide this full clearance. In a 190 px wide full-logo display, use at least 12 px external padding.

Version 2.0 supersedes every version 1.0 asset, including icons and guide illustrations. Replace old copies as a complete set.
