import streamlit as st
import pymupdf
import io

st.set_page_config(page_title="Flipkart Label Cropper (6-Up)", layout="centered")

st.title("📦 Flipkart 6-Up Label Cropper")
st.write("Upload your Flipkart multi-page PDF to get a 6-per-page ready-to-print A4 sheet.")

uploaded_file = st.file_uploader("Upload Flipkart Label PDF", type="pdf")

if uploaded_file is not None:
    A4_WIDTH = 595.28
    A4_HEIGHT = 841.89

    COLS = 2
    ROWS = 3
    LABELS_PER_PAGE = COLS * ROWS

    MARGIN_X = 6
    MARGIN_Y = 6
    GAP_X = 4
    GAP_Y = 4

    CELL_WIDTH = (A4_WIDTH - (2 * MARGIN_X) - (GAP_X * (COLS - 1))) / COLS
    CELL_HEIGHT = (A4_HEIGHT - (2 * MARGIN_Y) - (GAP_Y * (ROWS - 1))) / ROWS

    src_doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    total_labels = len(src_doc)
    out_doc = pymupdf.open()
    current_out_page = None

    for idx, page in enumerate(src_doc):
        slot = idx % LABELS_PER_PAGE

        if slot == 0:
            current_out_page = out_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

        col = slot % COLS
        row = slot // COLS

        target_x0 = MARGIN_X + col * (CELL_WIDTH + GAP_X)
        target_y0 = MARGIN_Y + row * (CELL_HEIGHT + GAP_Y)
        target_x1 = target_x0 + CELL_WIDTH
        target_y1 = target_y0 + CELL_HEIGHT
        target_rect = pymupdf.Rect(target_x0, target_y0, target_x1, target_y1)

        src_width = page.rect.width
        src_height = page.rect.height

        # Tight crop
        crop_x0 = src_width * 0.180
        crop_y0 = src_height * 0.024
        crop_x1 = src_width * 0.820
        crop_y1 = src_height * 0.452

        crop_rect = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)

        current_out_page.show_pdf_page(
            target_rect,
            src_doc,
            page.number,
            clip=crop_rect,
            keep_proportion=False
        )

    output_buffer = io.BytesIO()
    out_doc.save(output_buffer)
    out_doc.close()
    src_doc.close()
    output_buffer.seek(0)

    st.success(f"Successfully processed {total_labels} labels!")
    st.download_button(
        label="📥 Download 6-Up Printable PDF",
        data=output_buffer,
        file_name="flipkart_labels_6up.pdf",
        mime="application/pdf"
    )
