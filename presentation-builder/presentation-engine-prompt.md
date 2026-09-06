# HTML presentation

## Goal
You are building a single-page, keyboard- and click-navigable HTML slide presentation player named `presentation.html`. The file generated must be downloadable. You will generate this presentation from `style.css`, and `content.json`.

## Input
- `content.json` holds **plain content only** — titles, body text, labels, list items, numbers.
- `style.css` holds **essential visual styling**, usually only color palette plus some additional config. You will need to complete the css to embbed into the final html to make it pretty and functional.

## Presentation properties
`mouseAdvance`: enables or disables the behaviour of the mouse to go forward with the slides.
`timerSeconds`: starting point of the  timer

## Timer, clickable slider and progression bar
Add an always visible progress bar and a timer in the page footer. The timer always gets backwards, is green when time > 00:00 and the turns red

**Navigation**
- `ArrowRight` / `PageDown` → next; `ArrowLeft` / `PageUp` → previous; wraps at both ends.
- Clicking empty stage background (not the slide card) advances one slide, unless `meta.mouseAdvance` is `false`.
- Prev/Next buttons call the same navigation function as the keyboard.
- `Ctrl`/`Cmd`+`R` is intercepted to reset the current slide's timer instead of reloading the page.

**Timer**
- Counts down from `meta.timerSeconds` (default `30`) on every slide change and manual reset.
- Past zero, switches to an "over time" visual state (`.timer.over`) and counts up with a `+` prefix.

**Auto-fit**
- If rendered slide content is taller than the stage area, scale it down (`transform: scale()`) so it never internally scrolls on desktop. Recalculate on resize and on every slide change.

## Slide types and their JSON shape

### **`title`** 
The deck cover. Renders full-bleed and centered, no header.
Fields: 
```json
    {
      "type": "title",
      "title": "",
      "subtitle": "",
      "presenter": "",
      "presenter_email": "",
      "logoImage": "",
      "logoText": ""
    }
```

### **`section`**
A section-divider slide between parts of the deck. No header. Minimal, large-type layout. Always number of sections and add for each section slide "Part {x}: {section_name}"
Fields:
```json
{
  "type": "section",
  "title": "Section title goes here",
  "body": "One optional sentence introducing this part of the deck."
}
```

### **`content`** 
A standard slide. Add a header with the slide title, slide subtitle, f"{page}/{total_pages}". Autoformat lists when fits

```json
    {
      "type": "content",
      "slide_title": "Project Title Here",
      "slide_subtitle": "Program / Course · Context",
      "content": [
        [
          "text1",
          "text2",
          "text3"
        ]
      ]
    }
```

### **`final`**
The closing/recommendation slide. No header, similar to Title, but with a big quote in the center, the place holder name, a "thank you" phrase, and a placeholder to point to `img/qr_code.png` Fields: `closing`, `title`, `body`, `recommendation` 

## Required behavior

**Layout & chrome**
- Fixed header: logo/initials mark, "deck label" eyebrow, title, subtitle — from `content.json > meta`.
- A centered "stage" holding exactly one visible slide at a time.
- Fixed footer control bar: Prev / Next / Reset-timer buttons, a progress bar (`(currentIndex + 1) / totalSlides`), a "current / total" counter, and a per-slide countdown timer.

## Class contract that `style.css` must style

`app-header`, `brand`, `logo`, `deck-label`, `subtitle` · `stage`, `slide`, `slide--title`, `slide--section`, `slide--content`, `slide--chart`, `slide--final`, `slide-content`, `kicker`, `lead` · `panel` (plus `.gold`/`.green`/`.red`/`.blue`/`.default` variants), `quote`, `answer` (with `question`/`answer`/`aside` children), `list`, `metric` (with nested `small`), `chart-svg` · `controls`, `progress > i`, `counter`, `timer` (plus `.over`), `mouse-note` · a `fade`-in keyframe animation for slide transitions · the two responsive breakpoints above.

## Before you start

If anything here is ambiguous for my specific deck — exact slide count and types, whether `style.css` should match a reference deck's theme or use a new palette, whether the demo CTA button is needed at all — ask me first instead of guessing.
