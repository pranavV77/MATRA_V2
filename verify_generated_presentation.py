import pptx
import sys

sys.stdout.reconfigure(encoding='utf-8')

prs = pptx.Presentation('MATRA_S7_Mid_Review_Presentation.pptx')
print(f'Total slides in generated presentation: {len(prs.slides)}')
assert len(prs.slides) == 12, f'Expected 12 slides, got {len(prs.slides)}'

for idx, slide in enumerate(prs.slides):
    title = slide.shapes.title.text if slide.shapes.title else "NO TITLE (Slide 1)"
    print(f"\n==================== SLIDE {idx+1}: {title} ====================")
    for s_idx, shape in enumerate(slide.shapes):
        if shape.has_text_frame:
            full_text = shape.text_frame.text.replace('\n', ' \\n ')
            print(f"  Shape {s_idx+1} ({shape.name}): {full_text[:140]}")
        elif shape.has_table:
            t = shape.table
            print(f"  Shape {s_idx+1} [TABLE {len(t.rows)}x{len(t.columns)}]: Header='{[c.text.replace(chr(10), ' ') for c in t.rows[0].cells]}'")
        else:
            print(f"  Shape {s_idx+1} ({shape.name}, type={shape.shape_type})")
