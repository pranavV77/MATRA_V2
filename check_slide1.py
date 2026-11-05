import pptx

prs = pptx.Presentation('Mid review PPT Template.pptx')
slide1 = prs.slides[0]
for s in slide1.shapes:
    print(f'Shape: {s.name}')
    if s.has_text_frame:
        for p in s.text_frame.paragraphs:
            print(f'  P: "{p.text}"')
            for r in p.runs:
                print(f'    Run: "{r.text}", font={r.font.name}, size={r.font.size.pt if r.font.size else None}, bold={r.font.bold}, color={r.font.color.rgb if r.font.color and hasattr(r.font.color, "rgb") else "no_rgb"}')
