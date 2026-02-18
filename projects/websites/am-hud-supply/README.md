# AM HUD Supply Website
## Performance Supply Depot — Premium POS Supplies

**Status:** ✅ Complete  
**File:** `projects/websites/am-hud-supply/index.html` (21KB)  
**Tech:** Pure HTML/CSS (responsive, no frameworks)

---

## 🏢 About

Professional website for **AM HUD Supply** (also known as Performance Supply Depot), a B2B supplier of POS consumables for:
- Multifamily properties
- HUD housing
- Property management
- Commercial facilities

---

## 🎯 Products Offered

### 1. Thermal Receipt Paper Rolls
- 3 1/8" x 230' BPA-free
- Bright white, jam-resistant
- Compatible: Epson, Star, Citizen
- Bulk pricing: $0.20/roll (50+)

### 2. Bond Paper Rolls
- 1-Ply: 3" x 150' white
- 2-Ply: 3" x 90' carbonless
- Perfect for kitchen printers
- Durable, fade-resistant

### 3. Ink Ribbons & Cartridges
- ERC-30/34/38 compatible
- SP700 series
- TM-U220 compatible
- Boxes of 6+ for best pricing

---

## ✨ Website Features

### Design
- Modern gradient hero section
- Professional blue/orange color scheme
- Responsive layout (mobile-first)
- CSS animations (subtle)

### Sections
1. **Promo Banner** — Q1 2026 offer (10% off, free shipping)
2. **Hero** — Value proposition + CTA
3. **Products** — Three product cards with features
4. **Benefits** — Why choose AM HUD Supply (4 benefits)
5. **Quote Form** — Lead capture (Formspree-ready)
6. **Trust** — Testimonial + stats (500+ properties, 99.8% delivery)
7. **Footer** — Contact info, links

### Form Fields
- Name (required)
- Email (required)
- Phone (required)
- Company/Property (required)
- Volume range (dropdown)
- Specific needs (text)
- Additional details (textarea)

**Form Action:** Replace `YOUR_FORM_ID` with actual Formspree form ID

---

## 🚀 Deployment Options

### Option 1: Static Hosting
- GitHub Pages (free)
- Netlify (free tier)
- Vercel (free tier)
- AWS S3 + CloudFront

### Option 2: Traditional Hosting
- Upload via FTP/SFTP
- cPanel file manager
- Web host control panel

---

## 📱 Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| > 768px | Multi-column grid |
| ≤ 768px | Single column stack |
| ≤ 480px | Further optimized spacing |

---

## 🎨 Color Scheme

```css
Primary Blue:    #004080 / #003366 (dark)
Accent Orange:   #ff6600 / #e65c00 (hover)
Background Light: #f8f9fa
Background Blue:  #e9f2ff
Text Dark:        #333
Text Light:       #fff
```

---

## 📧 Business Contact Setup

**To activate form:**
1. Sign up at [formspree.io](https://formspree.io)
2. Create new form
3. Copy form ID
4. Replace `YOUR_FORM_ID` in HTML

**Email Integration:**
- Add `sales@amhudsupply.com` as notification email
- Set up auto-responder

---

## 🖼️ Images Needed

Replace placeholder images with actual product photos:

```
/images/thermal-paper-rolls.jpg
/images/bond-paper-rolls.jpg  
/images/ink-ribbons.jpg
```

**Recommended sizes:**
- 350x200px for product cards
- Compressed for web (80% quality JPG)

---

## 📊 Analytics Setup

Add Google Analytics or similar:

```html
<!-- Before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

---

## 🔍 SEO Optimized

**Meta Description:** High-quality thermal receipt paper, bond paper rolls, and ink ribbons for your POS printers. Fast delivery, bulk pricing for multifamily, HUD housing, and property management.

**Keywords:** thermal paper, bond paper, ink ribbons, POS supplies, receipt paper, property management, HUD housing, multifamily, bulk pricing

---

**Deployed:** February 18, 2026  
**Created by:** OpenClaw Engineer (Mortimer)  
**Version:** 1.0.0