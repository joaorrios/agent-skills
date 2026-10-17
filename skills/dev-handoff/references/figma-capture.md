# Capture a build into Figma

The baseline is a running build or prototype, so the Figma file shows its real screens, captured from the build. A capture shows developers exactly what was approved; a redrawn frame drifts from it. Annotations sit on and beside the captures, which stay as captured.

## Prepare the build

Set the build to the baseline before capturing:

- Pick the baseline variant and set every prototype toggle and parameter to its baseline value. Each toggle, parameter, fallback, and workaround also gets a row in the drafts table, unless the design system or a decision fixes it.
- Turn off progressive-enhancement utilities that change measured values (for example a CSS `corner-shape` that the design system already applies through a token), so the capture measures the design-system scale. When one cannot be turned off, normalize the captured values back to the design-system scale and say so in the annotation.
- Load realistic content; sample data gets a row in the drafts table.

## Capture

Capture each screen and state in scope at each viewport the delivery targets, with Figma's capture tool (`generate_figma_design` in the Figma MCP server). A state the brief or a decision requires and the build lacks gets a row in the drafts table.

## Organize

- **Cover section**: delivery name, baseline (URL, branch or commit, capture date), platforms, the dev task link, and the drafts table (on the both route, a link to it in the HTML page).
- **Numbered sections**: one per screen or flow (`1 Menu closed`, `2 Menu open`), with frames in flow order named `1.1`, `1.2`.
- **Annotations**: numbered marks on each capture, each matched by a note beside the frame naming the element, its token or component, its behaviour, and the decision behind anything not visible. Use Figma's native annotations when the tool can write them, so they show in Dev Mode; otherwise use note cards.

## Checks

- Every state in scope is captured from the build at each target viewport.
- Measured values sit on the design-system scale or carry a normalization note.
- Every mark has a note, and every note cites a token, a component, or a decision.
- The cover's baseline link opens the captured version.
