# Horizontal Scroll Component - Usage Guide

**Created:** 2026-01-09
**Component:** `frontend/src/components/ui/HorizontalScroll.jsx`
**Status:** ✅ Ready to Use

---

## Problem

User feedback: "Company display lacks clear horizontal scrolling, giving the impression of incomplete content"

### Root Cause:
- Horizontal content without visible scroll indicators
- Users don't realize there's more content to the right
- No arrows or visual cues for scrolling
- Content appears cut off

---

## Solution

Created `HorizontalScroll.jsx` - A reusable component that adds:
- ✅ Visible left/right navigation arrows
- ✅ Gradient fade indicators at edges
- ✅ Smooth scroll behavior
- ✅ Auto-hide arrows when at start/end
- ✅ Optional progress dots
- ✅ Touch/swipe support
- ✅ Responsive design

---

## How to Use

### Basic Usage

```jsx
import HorizontalScroll from './ui/HorizontalScroll';

function MyComponent() {
  return (
    <HorizontalScroll>
      <div>Item 1</div>
      <div>Item 2</div>
      <div>Item 3</div>
      <div>Item 4</div>
      <div>Item 5</div>
    </HorizontalScroll>
  );
}
```

### With All Options

```jsx
<HorizontalScroll
  className="my-4"
  showArrows={true}      // Show navigation arrows (default: true)
  showDots={true}        // Show progress dots (default: false)
  scrollAmount={400}     // Pixels to scroll per click (default: 300)
>
  {/* Your content here */}
</HorizontalScroll>
```

---

## Where to Apply This Fix

Based on user feedback, look for these common patterns and wrap them with `HorizontalScroll`:

### 1. Company Logos / Brand Display

**Before:**
```jsx
<div className="flex gap-4 overflow-x-auto">
  {companies.map(company => (
    <img key={company.id} src={company.logo} />
  ))}
</div>
```

**After:**
```jsx
<HorizontalScroll showArrows={true}>
  {companies.map(company => (
    <img key={company.id} src={company.logo} />
  ))}
</HorizontalScroll>
```

### 2. Feature Cards

**Before:**
```jsx
<div className="flex gap-6 overflow-x-auto">
  {features.map(feature => (
    <FeatureCard key={feature.id} {...feature} />
  ))}
</div>
```

**After:**
```jsx
<HorizontalScroll showArrows={true} showDots={true}>
  {features.map(feature => (
    <FeatureCard key={feature.id} {...feature} />
  ))}
</HorizontalScroll>
```

### 3. Testimonials Carousel

**Before:**
```jsx
<div className="flex gap-4 overflow-x-scroll">
  {testimonials.map(testimonial => (
    <TestimonialCard key={testimonial.id} {...testimonial} />
  ))}
</div>
```

**After:**
```jsx
<HorizontalScroll showArrows={true} showDots={true}>
  {testimonials.map(testimonial => (
    <TestimonialCard key={testimonial.id} {...testimonial} />
  ))}
</HorizontalScroll>
```

### 4. Job Role Pills / Tags

**Before:**
```jsx
<div className="flex gap-2 overflow-x-auto flex-nowrap">
  {roles.map(role => (
    <span key={role} className="px-4 py-2 bg-blue-600 rounded-full whitespace-nowrap">
      {role}
    </span>
  ))}
</div>
```

**After:**
```jsx
<HorizontalScroll showArrows={true} scrollAmount={200}>
  {roles.map(role => (
    <span key={role} className="px-4 py-2 bg-blue-600 rounded-full whitespace-nowrap">
      {role}
    </span>
  ))}
</HorizontalScroll>
```

---

## Finding and Fixing All Instances

### Step 1: Search for Horizontal Scroll Patterns

```bash
# Search for overflow-x usage
grep -r "overflow-x" frontend/src/components/

# Search for flex layouts that might overflow
grep -r "flex.*gap" frontend/src/components/ | grep -v "flex-wrap"
```

### Step 2: Identify Problematic Areas

Look for:
- `overflow-x-auto` or `overflow-x-scroll`
- `flex` containers with many items
- Lists that extend beyond viewport
- Company logos, testimonials, feature cards

### Step 3: Wrap with HorizontalScroll

1. Import the component
2. Wrap the scrolling content
3. Remove `overflow-x-*` classes
4. Test on mobile and desktop

---

## Features Explained

### 1. Navigation Arrows
- Appear only when there's content to scroll
- Auto-hide when at start/end
- Gradient background for visibility
- Smooth hover effects

### 2. Gradient Fade Indicators
- Subtle gradient on left edge (when can scroll left)
- Subtle gradient on right edge (when can scroll right)
- Indicates there's more content
- Non-intrusive visual cue

### 3. Progress Dots (Optional)
- Shows total number of "pages"
- Click to jump to specific section
- Active dot highlighted
- Good for image carousels

### 4. Touch Support
- Native touch scrolling on mobile
- Swipe gestures work automatically
- No custom touch handlers needed

---

## Customization

### Change Arrow Appearance

Edit `HorizontalScroll.jsx`:

```jsx
// Current
className="... bg-gradient-to-r from-blue-600 to-purple-600 ..."

// Change to solid color
className="... bg-blue-600 hover:bg-blue-700 ..."

// Change to outline style
className="... border-2 border-blue-600 bg-black/50 hover:bg-blue-600 ..."
```

### Change Scroll Amount

```jsx
<HorizontalScroll scrollAmount={500}>  // Scroll more
<HorizontalScroll scrollAmount={150}>  // Scroll less
```

### Hide Arrows on Desktop, Show on Mobile

```jsx
<HorizontalScroll showArrows={false} className="md:hidden-arrows">
```

Then add CSS:
```css
@media (min-width: 768px) {
  .hidden-arrows button {
    display: none;
  }
}
```

---

## Testing Checklist

After applying the fix:

- [ ] Desktop: Arrows visible and functional
- [ ] Desktop: Arrows hide when at start/end
- [ ] Desktop: Gradient fade indicators visible
- [ ] Desktop: Smooth scroll behavior
- [ ] Mobile: Touch scrolling works
- [ ] Mobile: Arrows visible (or hidden based on design)
- [ ] Tablet: Works in both orientations
- [ ] Content loads properly
- [ ] No layout shift on scroll
- [ ] Arrows don't cover content
- [ ] Accessible (keyboard navigation)

---

## Accessibility

The component includes:
- `aria-label` on arrow buttons
- Keyboard support (arrow keys work with native scroll)
- Focus indicators
- Semantic HTML

To improve:
- Add keyboard shortcuts (Left/Right arrow keys to scroll)
- Add ARIA live region for screen readers
- Add skip navigation option

---

## Performance

The component is optimized:
- Uses `useRef` for DOM access (no re-renders)
- Scroll event listener with cleanup
- Conditional rendering (arrows only when needed)
- CSS animations (GPU accelerated)
- No heavy dependencies

---

## Next Steps

1. **Find all horizontal scroll instances** in the codebase
2. **Wrap them** with `<HorizontalScroll>`
3. **Test** on all devices
4. **Deploy** and monitor user feedback

### Priority Areas to Fix:

1. **Landing Page** - Check for company logos, features
2. **Dashboard** - Check for analytics cards, stats
3. **Blog List** - Check for blog cards
4. **Job Matches** - Check for job cards
5. **Any carousel** - Replace with HorizontalScroll

---

## Example Implementation

```jsx
// Before (Landing Page Company Logos)
<div className="flex gap-6 overflow-x-auto py-8">
  <img src="/logos/google.png" className="h-12 grayscale hover:grayscale-0" />
  <img src="/logos/amazon.png" className="h-12 grayscale hover:grayscale-0" />
  <img src="/logos/microsoft.png" className="h-12 grayscale hover:grayscale-0" />
  <img src="/logos/apple.png" className="h-12 grayscale hover:grayscale-0" />
  <img src="/logos/meta.png" className="h-12 grayscale hover:grayscale-0" />
</div>

// After
<HorizontalScroll showArrows={true} scrollAmount={250}>
  <img src="/logos/google.png" className="h-12 grayscale hover:grayscale-0 transition" />
  <img src="/logos/amazon.png" className="h-12 grayscale hover:grayscale-0 transition" />
  <img src="/logos/microsoft.png" className="h-12 grayscale hover:grayscale-0 transition" />
  <img src="/logos/apple.png" className="h-12 grayscale hover:grayscale-0 transition" />
  <img src="/logos/meta.png" className="h-12 grayscale hover:grayscale-0 transition" />
</HorizontalScroll>
```

Result:
- Users see arrows on both sides
- Can click to scroll
- Gradient fade shows there's more content
- No confusion about incomplete content

---

## Support

If you encounter issues:
1. Check console for errors
2. Verify children are properly passed
3. Ensure Tailwind CSS classes are available
4. Test scroll behavior manually
5. Check z-index conflicts

---

**Status:** Component created and ready for implementation across the app.
