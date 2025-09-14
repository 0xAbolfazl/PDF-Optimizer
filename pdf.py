import fitz  # PyMuPDF
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

class PDFResizerApp:
    def __init__(self):
        # Initialize the main window
        self.window = ctk.CTk()
        self.window.title("PDF Resizer Pro")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.input_file = ""
        self.output_file = ""
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="PDF Resizer Pro", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # File selection frame
        file_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        file_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            file_frame, 
            text="Select PDF File:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        self.file_label = ctk.CTkLabel(
            file_frame, 
            text="No file selected", 
            text_color="gray",
            wraplength=400
        )
        self.file_label.pack(pady=5)
        
        select_btn = ctk.CTkButton(
            file_frame,
            text="Browse PDF File",
            command=self.select_file,
            corner_radius=8
        )
        select_btn.pack(pady=10)
        
        # Settings frame
        settings_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            settings_frame, 
            text="Settings:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Scale factor slider
        scale_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        scale_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(scale_frame, text="Scale Factor:").pack(anchor="w")
        self.scale_var = ctk.StringVar(value="90%")
        
        scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=50,
            to=100,
            number_of_steps=50,
            command=self.update_scale_label
        )
        scale_slider.set(90)  # Default 90%
        scale_slider.pack(pady=5, fill="x")
        
        self.scale_label = ctk.CTkLabel(scale_frame, textvariable=self.scale_var)
        self.scale_label.pack()
        
        # DPI selection
        dpi_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dpi_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(dpi_frame, text="Resolution (DPI):").pack(anchor="w")
        
        self.dpi_var = ctk.StringVar(value="300")
        dpi_combo = ctk.CTkComboBox(
            dpi_frame,
            values=["150", "200", "300", "400", "600"],
            variable=self.dpi_var,
            state="readonly"
        )
        dpi_combo.set("300")  # Default 300 DPI
        dpi_combo.pack(pady=5, fill="x")
        
        # Process button
        process_btn = ctk.CTkButton(
            main_frame,
            text="Process PDF",
            command=self.process_pdf,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        process_btn.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="Ready to process", 
            text_color="green"
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress.pack(pady=5, padx=20, fill="x")
        self.progress.set(0)
    
    def update_scale_label(self, value):
        self.scale_var.set(f"{int(value)}%")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.input_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.configure(text=filename)
            
            # Generate output filename automatically
            base_name = os.path.splitext(filename)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = f"{base_name}_resized_{timestamp}.pdf"
    
    def process_pdf(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a PDF file first!")
            return
        
        try:
            self.status_label.configure(text="Processing...", text_color="yellow")
            self.progress.start()
            self.window.update()
            
            # Get settings values
            scale_factor = int(self.scale_var.get().replace('%', '')) / 100
            dpi = int(self.dpi_var.get())
            
            # Call the resize function
            self.resize_pdf_for_printing(self.input_file, self.output_file, scale_factor, dpi)
            
            self.progress.stop()
            self.status_label.configure(text="Processing completed successfully!", text_color="green")
            
            # Show success message with file info
            input_size = os.path.getsize(self.input_file) / 1024 / 1024
            output_size = os.path.getsize(self.output_file) / 1024 / 1024
            
            messagebox.showinfo(
                "Success", 
                f"PDF processed successfully!\n\n"
                f"Input: {input_size:.1f} MB\n"
                f"Output: {output_size:.1f} MB\n"
                f"Saved as: {self.output_file}"
            )
            
        except Exception as e:
            self.progress.stop()
            self.status_label.configure(text="Error occurred!", text_color="red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def resize_pdf_for_printing(self, input_pdf_path, output_pdf_path, scale_factor=0.9, dpi=300):
        """
        Resize PDF pages with high resolution for quality printing.
        """
        input_doc = fitz.open(input_pdf_path)
        output_doc = fitz.open()
        
        # Calculate zoom factor based on DPI
        zoom = dpi / 72
        
        total_pages = len(input_doc)
        
        for page_num in range(total_pages):
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
            target_rect = fitz.Rect(
                x_offset, y_offset, 
                x_offset + scaled_width, 
                y_offset + scaled_height
            )
            
            # Insert the high-resolution image
            new_page.insert_image(target_rect, pixmap=pix)
            
            # Update progress
            progress_value = (page_num + 1) / total_pages
            self.progress.set(progress_value)
            self.status_label.configure(text=f"Processing page {page_num + 1}/{total_pages}")
            self.window.update()
        
        # Save with compression
        output_doc.save(output_pdf_path, deflate=True)
        output_doc.close()
        input_doc.close()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PDFResizerApp()
    app.run()