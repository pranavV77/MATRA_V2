import pptx

prs = pptx.Presentation('Mid review PPT Template.pptx')
for idx, slide in enumerate(prs.slides):
    title_shape = slide.shapes.title
    title_text = title_shape.text if title_shape else "NO TITLE"
    print(f"Slide {idx+1}: Title='{title_text}', Shapes={len(slide.shapes)}")
    for s in slide.shapes:
        if s != title_shape and s.name != "Slide Number Placeholder 3":
            print(f"   Shape: {s.name}, Type={s.shape_type}, has_text={s.has_text_frame}, has_table={s.has_table}")
