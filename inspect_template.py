import pptx

prs = pptx.Presentation('Mid review PPT Template.pptx')
print(f'Total slides: {len(prs.slides)}')
print(f'Dimensions: {prs.slide_width/914400:.2f} x {prs.slide_height/914400:.2f} inches')

for idx, slide in enumerate(prs.slides):
    print(f'\n========================================')
    print(f'SLIDE {idx+1}: {slide.shapes.title.text if slide.shapes.title else "No Title"}')
    print(f'Layout: {slide.slide_layout.name}')
    for s_idx, shape in enumerate(slide.shapes):
        print(f'  Shape {s_idx+1}: {shape.name} (type={shape.shape_type}) at left={shape.left/914400:.2f}", top={shape.top/914400:.2f}", w={shape.width/914400:.2f}", h={shape.height/914400:.2f}"')
        if shape.has_text_frame:
            for p_idx, p in enumerate(shape.text_frame.paragraphs):
                p_align = p.alignment
                font_info = []
                for r in p.runs:
                    f_name = r.font.name
                    f_size = r.font.size.pt if r.font.size else None
                    f_bold = r.font.bold
                    f_color = str(r.font.color.rgb) if (r.font and r.font.color and hasattr(r.font.color, 'rgb') and r.font.color.type == pptx.enum.dml.MSO_COLOR_TYPE.RGB) else 'theme/none'
                    font_info.append(f'{r.text} [fn={f_name}, sz={f_size}, b={f_bold}, c={f_color}]')
                print(f'    P{p_idx+1} (align={p_align}): {" ".join(font_info) if font_info else p.text}')
