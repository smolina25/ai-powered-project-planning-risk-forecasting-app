# V3 Manual Build Guide

## Version
`v3` lovable-style multi-page site in `web/lovable-style-site/`

## What this version is for

This version is the polished product-facing website.

Use it when you want to present the capstone as:
- a shareable product website
- a complete multi-page experience
- a polished external-facing surface

## How two teammates could do this manually

### Teammate A
- study the Lovable reference site and video
- extract the structure and visual rhythm
- rewrite the content for `certAIn Project Intelligence`
- remove anything that would exaggerate the capstone

### Teammate B
- build the shared CSS design system
- implement the page set and internal routing
- create reusable navigation and footer logic
- test responsiveness and route integrity

### Shared review
- confirm the site is structurally close to the reference
- confirm the content remains honest to the project
- test the site as an external visitor would

## Manual workflow

1. Inspect the reference.
   Break it into:
   - navigation
   - hero
   - feature sections
   - pricing
   - dashboard page
   - footer

2. Define the page architecture.
   Final route set:
   - `index.html`
   - `product.html`
   - `ai-forecasting.html`
   - `monte-carlo.html`
   - `pricing.html`
   - `dashboard.html`
   - `about.html`
   - `login.html`

3. Create the shared system.
   Use one CSS file and one JavaScript file for:
   - visual identity
   - reusable layout rules
   - header/footer rendering
   - active nav state

4. Build the home page first.
   The home page controls the overall tone and determines whether the site feels polished.

5. Build the secondary pages.
   Suggested order:
   - product
   - AI forecasting
   - Monte Carlo
   - dashboard
   - pricing
   - about
   - login

6. Fix all internal links.
   Every CTA and every nav item must lead to a real page.

7. Test as a full site.
   Confirm:
   - no broken routes
   - mobile menu works
   - pages feel cohesive
   - the site is presentable publicly

## What to say in the presentation

\"We analyzed the Lovable reference structurally and rebuilt a similar multi-page experience manually for our own capstone. One teammate focused on reference analysis and truthful content adaptation, while the other implemented the shared frontend system, internal routes, and responsive behavior. The result is a polished marketing-style site that still stays grounded in our actual product and evidence.\"

## Human quality checklist

- Every page route works.
- The design language is consistent across pages.
- The home page matches the reference rhythm closely.
- The content is still defendable as part of the capstone.
- The site feels complete enough to share externally.
