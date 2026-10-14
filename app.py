import streamlit as st
import pymupdf
import io

st.set_page_config(page_title="Flipkart Multi-PDF Cropper (6-Up)", layout="centered")

st.title("📦 Flipkart Batch Label Cropper")
st.write("Select and upload all your separate Flipkart PDF labels at once.")

# Enabled multiple file selection
uploaded_files = st.file_uploader(
    "Select one or multiple Flipkart PDF files",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    A4_WIDTH = 595.28
    A4_HEIGHT = 841.89

    # 2 columns x 3 rows = 6 labels per Portrait sheet
    COLS = 2
    ROWS = 3
    LABELS_PER_PAGE = COLS * ROWS

    # Margins and spacing to fill the printable area
    MARGIN_X = 6
    MARGIN_Y = 6
    GAP_X = 4
    GAP_Y = 4

    CELL_WIDTH = (A4_WIDTH - (2 * MARGIN_X) - (GAP_X * (COLS - 1))) / COLS
    CELL_HEIGHT = (A4_HEIGHT - (2 * MARGIN_Y) - (GAP_Y * (ROWS - 1))) / ROWS

    out_doc = pymupdf.open()
    current_out_page = None
    label_counter = 0

    # Process every uploaded PDF file in order
    for uploaded_file in uploaded_files:
        src_doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")

        for page in src_doc:
            slot = label_counter % LABELS_PER_PAGE

            # Add a new A4 page every 6 labels
            if slot == 0:
                current_out_page = out_doc.new_page(width=A4_WIDTH, height=A4_HEIGHT)

            col = slot % COLS
            row = slot // COLS

            # Target position
            target_x0 = MARGIN_X + col * (CELL_WIDTH + GAP_X)
            target_y0 = MARGIN_Y + row * (CELL_HEIGHT + GAP_Y)
            target_x1 = target_x0 + CELL_WIDTH
            target_y1 = target_y0 + CELL_HEIGHT
            target_rect = pymupdf.Rect(target_x0, target_y0, target_x1, target_y1)

            src_width = page.rect.width
            src_height = page.rect.height

            # Exact crop bounds for Flipkart shipping label
            crop_x0 = src_width * 0.180
            crop_y0 = src_height * 0.024
            crop_x1 = src_width * 0.820
            crop_y1 = src_height * 0.452
            crop_rect = pymupdf.Rect(crop_x0, crop_y0, crop_x1, crop_y1)

            # Draw label stretched edge-to-edge
            current_out_page.show_pdf_page(
                target_rect,
                src_doc,
                page.number,
                clip=crop_rect,
                keep_proportion=False
            )

            label_counter += 1

        src_doc.close()

    output_buffer = io.BytesIO()
    out_doc.save(output_buffer)
    out_doc.close()
    output_buffer.seek(0)

    st.success(f"Successfully merged & processed {label_counter} labels from {len(uploaded_files)} PDF files!")
    st.download_button(
        label="📥 Download Merged 6-Up Printable PDF",
        data=output_buffer,
        file_name="flipkart_all_labels_6up.pdf",
        mime="application/pdf"
    )
