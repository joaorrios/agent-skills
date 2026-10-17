# HTML handoff page

One self-contained HTML page per delivery. When the user shared a reference handoff page, reuse its CSS and structure; otherwise use the structure and look below. On the both route, the page carries the header, motion, mobile, rules, drafts, and AI spec, and links each static state to its Figma section instead of rendering it.

## Values

Pull exact values from the Figma nodes (`get_design_context`, `get_variable_defs`, `get_metadata` in the Figma MCP server) and, for motion only the build carries, from the build's code with a link to it. Keep each state's node link, and cite the token wherever the design uses one. Export the design's real assets and ship them as supporting files, so live renders match the frames.

## Structure, in this order

1. **Header**: kicker `<Product> · Developer handoff`, H1 with the feature name, a one-paragraph lede (what it is, who sees it, what it does), chips (delivery date, platforms, two key rules), a card linking the Figma section, and callouts:
   - **Heads-up** when demo hover and press states are placeholders: "use the product's existing button states".
   - **Draft** whenever anything shown is a draft, linking to the drafts section.
2. **One section per screen or state**: a live render of the real UI (HTML and CSS rebuilt from the Figma values, scaled to fit) with a numbered rail, and a numbered list explaining each mark (element, copy in `code`, token or font, size, and color, behaviour). "Open in Figma ↗" with the state's node link.
3. **Motion** (if any): an interactive demo with a trigger button, a numbered explanation, a table `Element · Property · From → to · Duration · Delay`, and one note on the easing, which properties animate, and the `prefers-reduced-motion` behaviour.
4. **Mobile** (if different): a live demo, what changes and why, how to detect it, and its own motion table.
5. **Rules**: a grid of business rules (who sees it, when, how it ends, data and links, metrics), plus a keyboard table (Tab, Enter, Esc) when there is an overlay or modal.
6. **Drafts and placeholders**: the drafts table.
7. **Good to know**: a short list of gotchas, such as Figma effects without a CSS equivalent, assets to export and at what scale, and testing advice.
8. **Spec for your AI assistant**: a `<pre>` with a Copy button holding the page as plain text with exact values: Figma links, audience and frequency, links and data, each screen with its layers and values, motion, mobile, accessibility, button states, a `DRAFTS AND PLACEHOLDERS (NOT FINAL, DO NOT SHIP AS IS)` block, and an `INTENDED BEHAVIOUR, NOT BUGS` block.

## Look

- Geist and Geist Mono (Google Fonts), a light neutral page (#F0EFEC, cards #FFF, lines #DEDDD8) with full dark-mode tokens, max width 1280, sticky table of contents on desktop.
- Green round number marks, warm amber callouts for Heads-up and Draft, a dark stage (#0B0D12) behind live renders.
- Works at phone width; demos are keyboard-accessible (real buttons, focus trap, Esc).

## Publish

Publish the page where the team can open it (an artifact with its supporting files, a hosted page, or a file on the dev task), titled with the feature name.

## Checks

- Every value matches Figma, and every "Open in Figma" link opens the right node.
- The AI spec block says what the page says, drafts included.
- Demos open, close, replay, and respect reduced motion.
