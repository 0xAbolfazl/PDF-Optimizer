import fitz  # PyMuPDF
import os

def resize_pdf_for_printing(input_pdf_path, output_pdf_path, scale_factor=0.9, dpi=300):
    """
    Resize PDF pages with high resolution for quality printing.
    
    Parameters:
    input_pdf_path (str): Path to the input PDF file
    output_pdf_path (str): Path to save the output PDF file
    scale_factor (float): Scaling factor for content
    dpi (int): Resolution for output (300 for printing)
    """
    
    input_doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()
    
    # Calculate zoom factor based on DPI
    zoom = dpi / 72
    
    for page_num in range(len(input_doc)):
        page = input_doc.load_page(page_num)
        original_rect = page.rect
        
        # Create new page with original dimensions
        new_page = output_doc.new_page(width=original_rect.width, height=original_rect.height)
        
        # Calculate scaled dimensions
        scaled_width = original_rect.width * scale_factor
        scaled_height = original_rect.height * scale_factor
        
        # Calculate centering position
        x_offset = (original_rect.width - scaled_width) / 2
        y_offset = (original_rect.height - scaled_height) / 2
        
        # Create high-resolution matrix
        matrix = fitz.Matrix(zoom * scale_factor, zoom * scale_factor)
        
        # Get high-resolution pixmap
        pix = page.get_pixmap(matrix=matrix)
        
        # Create target rectangle
        target_rect = fitz.Rect(x_offset, y_offset, 
                               x_offset + scaled_width, 
                               y_offset + scaled_height)
        
        # Insert the high-resolution image
        new_page.insert_image(target_rect, pixmap=pix)
        
        print(f"Processed page {page_num + 1}/{len(input_doc)}")
    
    # Save with compression
    output_doc.save(output_pdf_path, deflate=True)
    output_doc.close()
    input_doc.close()
    
    # Print file info
    input_size = os.path.getsize(input_pdf_path) / 1024 / 1024
    output_size = os.path.getsize(output_pdf_path) / 1024 / 1024
    print(f"Input: {input_size:.1f}MB, Output: {output_size:.1f}MB")

def main():
    input_pdf = input("Enter input PDF path: ").strip()
    output_pdf = input("Enter output PDF path: ").strip()
    
    if not os.path.exists(input_pdf):
        print("Input file not found!")
        return
    
    try:
        resize_pdf_for_printing(input_pdf, output_pdf, scale_factor=0.9, dpi=300)
        print("PDF successfully created for printing!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()