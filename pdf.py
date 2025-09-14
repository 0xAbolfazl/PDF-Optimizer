import fitz  # PyMuPDF
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import time

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
        self.is_processing = False
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.window, corner_radius=15)
        self.main_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.show_main_ui()
    
    def show_main_ui(self):
        """Show the main UI with file selection and settings"""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_container, 
            text="PDF Resizer Pro", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # File selection frame
        file_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
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
        
        self.select_btn = ctk.CTkButton(
            file_frame,
            text="Browse PDF File",
            command=self.select_file,
            corner_radius=8
        )
        self.select_btn.pack(pady=10)
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
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
        
        self.scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=50,
            to=100,
            number_of_steps=50,
            command=self.update_scale_label
        )
        self.scale_slider.set(90)
        self.scale_slider.pack(pady=5, fill="x")
        
        self.scale_label = ctk.CTkLabel(scale_frame, textvariable=self.scale_var)
        self.scale_label.pack()
        
        # DPI selection
        dpi_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dpi_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(dpi_frame, text="Resolution (DPI):").pack(anchor="w")
        
        self.dpi_var = ctk.StringVar(value="300")
        self.dpi_combo = ctk.CTkComboBox(
            dpi_frame,
            values=["150", "200", "300", "400", "600"],
            variable=self.dpi_var,
            state="readonly"
        )
        self.dpi_combo.set("300")
        self.dpi_combo.pack(pady=5, fill="x")
        
        # Start button
        self.start_btn = ctk.CTkButton(
            self.main_container,
            text="Start Processing",
            command=self.start_processing,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        self.start_btn.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_container, 
            text="Ready to process", 
            text_color="green"
        )
        self.status_label.pack(pady=10)
    
    def show_processing_ui(self):
        """Show processing UI with progress bar"""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_container, 
            text="Processing PDF...", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        progress_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            progress_frame, 
            text="Processing Progress:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame, mode="determinate", height=20)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        
        # Progress percentage
        self.progress_percent = ctk.CTkLabel(
            progress_frame, 
            text="0%", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.progress_percent.pack(pady=5)
        
        # Page counter
        self.page_counter = ctk.CTkLabel(
            progress_frame, 
            text="Pages: 0/0", 
            text_color="gray"
        )
        self.page_counter.pack(pady=5)
        
        # Status message
        self.processing_status = ctk.CTkLabel(
            progress_frame, 
            text="Starting processing...", 
            text_color="yellow"
        )
        self.processing_status.pack(pady=10)
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            progress_frame,
            text="Cancel",
            command=self.cancel_processing,
            corner_radius=8,
            fg_color="#DC143C",
            hover_color="#B22222"
        )
        self.cancel_btn.pack(pady=10)
    
    def update_scale_label(self, value):
        self.scale_var.set(f"{int(value)}%")
    
    def select_file(self):
        if self.is_processing:
            return
            
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
    
    def start_processing(self):
        if not self.input_file:
            messagebox.showerror("Error", "Please select a PDF file first!")
            return
        
        if self.is_processing:
            return
        
        # Switch to processing UI
        self.show_processing_ui()
        self.is_processing = True
        
        # Get settings values
        scale_factor = int(self.scale_var.get().replace('%', '')) / 100
        dpi = int(self.dpi_var.get())
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(
            target=self.process_pdf_thread,
            args=(self.input_file, self.output_file, scale_factor, dpi),
            daemon=True
        )
        self.processing_thread.start()
    
    def cancel_processing(self):
        """Cancel the ongoing processing"""
        if self.is_processing:
            self.is_processing = False
            self.show_main_ui()
            self.status_label.configure(text="Processing cancelled", text_color="orange")
    
    def update_progress(self, current, total, percentage):
        """Update progress from thread"""
        self.window.after(0, lambda: self._update_progress_ui(current, total, percentage))
    
    def _update_progress_ui(self, current, total, percentage):
        """Update UI elements from main thread"""
        if not self.is_processing:
            return
            
        self.progress_bar.set(percentage / 100)
        self.progress_percent.configure(text=f"{percentage:.1f}%")
        self.page_counter.configure(text=f"Pages: {current}/{total}")
        
        if percentage < 25:
            self.processing_status.configure(text="Loading document...", text_color="yellow")
        elif percentage < 50:
            self.processing_status.configure(text="Processing pages...", text_color="orange")
        elif percentage < 75:
            self.processing_status.configure(text="Optimizing images...", text_color="blue")
        else:
            self.processing_status.configure(text="Finalizing...", text_color="green")
    
    def process_pdf_thread(self, input_path, output_path, scale_factor, dpi):
        """Process PDF in separate thread"""
        try:
            success = self.resize_pdf_for_printing(input_path, output_path, scale_factor, dpi)
            self.window.after(0, lambda: self.on_processing_complete(success, input_path, output_path))
            
        except Exception as e:
            self.window.after(0, lambda: self.on_processing_error(str(e)))
    
    def resize_pdf_for_printing(self, input_pdf_path, output_pdf_path, scale_factor, dpi):
        """Resize PDF pages with high resolution for quality printing."""
        try:
            input_doc = fitz.open(input_pdf_path)
            output_doc = fitz.open()
            
            zoom = dpi / 72
            total_pages = len(input_doc)
            
            for page_num in range(total_pages):
                if not self.is_processing:
                    return False
                    
                page = input_doc.load_page(page_num)
                original_rect = page.rect
                
                new_page = output_doc.new_page(width=original_rect.width, height=original_rect.height)
                
                scaled_width = original_rect.width * scale_factor
                scaled_height = original_rect.height * scale_factor
                
                x_offset = (original_rect.width - scaled_width) / 2
                y_offset = (original_rect.height - scaled_height) / 2
                
                matrix = fitz.Matrix(zoom * scale_factor, zoom * scale_factor)
                pix = page.get_pixmap(matrix=matrix)
                
                target_rect = fitz.Rect(x_offset, y_offset, x_offset + scaled_width, y_offset + scaled_height)
                new_page.insert_image(target_rect, pixmap=pix)
                
                progress_percentage = ((page_num + 1) / total_pages) * 100
                self.update_progress(page_num + 1, total_pages, progress_percentage)
                
                time.sleep(0.02)  # Small delay for UI updates
            
            if self.is_processing:
                output_doc.save(output_pdf_path, deflate=True)
                output_doc.close()
                input_doc.close()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error in processing: {e}")
            return False
    
    def on_processing_complete(self, success, input_path, output_path):
        """Handle processing completion"""
        self.is_processing = False
        self.show_main_ui()
        
        if success:
            self.status_label.configure(text="Processing completed successfully!", text_color="green")
            
            input_size = os.path.getsize(input_path) / 1024 / 1024
            output_size = os.path.getsize(output_path) / 1024 / 1024
            
            messagebox.showinfo(
                "Success", 
                f"PDF processed successfully!\n\n"
                f"Input: {input_size:.1f} MB\n"
                f"Output: {output_size:.1f} MB\n"
                f"Saved as: {os.path.basename(output_path)}"
            )
        else:
            self.status_label.configure(text="Processing completed", text_color="blue")
    
    def on_processing_error(self, error_msg):
        """Handle processing errors"""
        self.is_processing = False
        self.show_main_ui()
        self.status_label.configure(text="Error occurred!", text_color="red")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PDFResizerApp()
    app.run()