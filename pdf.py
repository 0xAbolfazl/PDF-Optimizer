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
        self.window.geometry("600x700")
        self.window.minsize(500, 600)
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Variables
        self.input_file = ""
        self.output_file = ""
        self.is_processing = False
        self.is_fullscreen = False
        
        # Configure window
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.window, corner_radius=20, fg_color="#2b2b2b")
        self.main_container.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.show_main_ui()
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes("-fullscreen", self.is_fullscreen)
        
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.window.attributes("-fullscreen", False)
    
    def show_main_ui(self):
        """Show the main UI with file selection and settings"""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Header frame
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(pady=(20, 10), fill="x")
        
        # Title with icon
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack()
        
        ctk.CTkLabel(
            title_frame, 
            text="📄 PDF Resizer Pro", 
            font=ctk.CTkFont(size=28, weight="bold", family="Arial")
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Resize and optimize your PDF files for printing",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(5, 20))
        
        # File selection card
        file_card = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="#3a3a3a")
        file_card.pack(pady=10, padx=30, fill="x")
        
        ctk.CTkLabel(
            file_card, 
            text="📁 Select PDF File", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 5))
        
        self.file_label = ctk.CTkLabel(
            file_card, 
            text="No file selected", 
            text_color="#888888",
            wraplength=400,
            font=ctk.CTkFont(size=11)
        )
        self.file_label.pack(pady=5)
        
        self.select_btn = ctk.CTkButton(
            file_card,
            text="Browse Files",
            command=self.select_file,
            corner_radius=10,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        self.select_btn.pack(pady=(5, 15), padx=20)
        
        # Settings card
        settings_card = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="#3a3a3a")
        settings_card.pack(pady=10, padx=30, fill="x")
        
        ctk.CTkLabel(
            settings_card, 
            text="⚙️ Processing Settings", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Scale factor setting
        scale_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        scale_frame.pack(pady=8, padx=20, fill="x")
        
        ctk.CTkLabel(scale_frame, text="📏 Scale Factor:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        scale_value_frame = ctk.CTkFrame(scale_frame, fg_color="transparent")
        scale_value_frame.pack(fill="x", pady=5)
        
        self.scale_var = ctk.StringVar(value="90%")
        self.scale_value_label = ctk.CTkLabel(scale_value_frame, textvariable=self.scale_var, font=ctk.CTkFont(weight="bold"))
        self.scale_value_label.pack(side="right")
        
        self.scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=50,
            to=100,
            number_of_steps=50,
            command=self.update_scale_label,
            progress_color="#FF6B35",
            button_color="#FF6B35",
            button_hover_color="#E55A2B"
        )
        self.scale_slider.set(90)
        self.scale_slider.pack(fill="x", pady=5)
        
        # DPI setting
        dpi_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        dpi_frame.pack(pady=8, padx=20, fill="x")
        
        ctk.CTkLabel(dpi_frame, text="🖨️ Resolution (DPI):", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        self.dpi_var = ctk.StringVar(value="300")
        self.dpi_combo = ctk.CTkComboBox(
            dpi_frame,
            values=["150", "200", "300", "400", "600"],
            variable=self.dpi_var,
            state="readonly",
            dropdown_fg_color="#3a3a3a",
            dropdown_hover_color="#4a4a4a",
            button_color="#FF6B35",
            button_hover_color="#E55A2B"
        )
        self.dpi_combo.set("300")
        self.dpi_combo.pack(fill="x", pady=8)
        
        # Start button section
        button_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        button_frame.pack(pady=20, fill="x")
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Start Processing",
            command=self.start_processing,
            corner_radius=12,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#FF6B35",
            hover_color="#E55A2B",
            border_width=0
        )
        self.start_btn.pack(pady=10, padx=80)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_container, 
            text="✅ Ready to process", 
            text_color="#4CAF50",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Fullscreen hint
        fullscreen_label = ctk.CTkLabel(
            self.main_container,
            text="Press F11 for fullscreen • Esc to exit",
            text_color="#666666",
            font=ctk.CTkFont(size=9)
        )
        fullscreen_label.pack(pady=(0, 10))
    
    def show_processing_ui(self):
        """Show processing UI with progress bar"""
        # Clear container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Processing header
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(pady=(30, 20), fill="x")
        
        ctk.CTkLabel(
            header_frame, 
            text="⏳ Processing PDF...", 
            font=ctk.CTkFont(size=24, weight="bold", family="Arial")
        ).pack()
        
        # Progress card
        progress_card = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="#3a3a3a")
        progress_card.pack(pady=20, padx=40, fill="both", expand=True)
        
        ctk.CTkLabel(
            progress_card, 
            text="📊 Processing Progress", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Circular progress frame
        circular_frame = ctk.CTkFrame(progress_card, fg_color="transparent")
        circular_frame.pack(pady=10)
        
        # Progress percentage (big)
        self.progress_percent = ctk.CTkLabel(
            circular_frame, 
            text="0%", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FF6B35"
        )
        self.progress_percent.pack()
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_card, 
            mode="determinate", 
            height=20,
            progress_color="#FF6B35",
            corner_radius=10
        )
        self.progress_bar.pack(pady=15, padx=30, fill="x")
        self.progress_bar.set(0)
        
        # Page counter
        self.page_counter = ctk.CTkLabel(
            progress_card, 
            text="📄 Pages: 0/0", 
            text_color="#CCCCCC",
            font=ctk.CTkFont(size=12)
        )
        self.page_counter.pack(pady=5)
        
        # Status message
        self.processing_status = ctk.CTkLabel(
            progress_card, 
            text="🔄 Starting processing...", 
            text_color="#FFD700",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.processing_status.pack(pady=10)
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            progress_card,
            text="❌ Cancel Processing",
            command=self.cancel_processing,
            corner_radius=10,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#DC143C",
            hover_color="#B22222",
            border_width=0
        )
        self.cancel_btn.pack(pady=20, padx=50, fill="x")
    
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
            self.status_label.configure(text="✅ File selected - Ready to process", text_color="#4CAF50")
    
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
            self.status_label.configure(text="⏹️ Processing cancelled", text_color="#FF6B35")
    
    def update_progress(self, current, total, percentage):
        """Update progress from thread"""
        self.window.after(0, lambda: self._update_progress_ui(current, total, percentage))
    
    def _update_progress_ui(self, current, total, percentage):
        """Update UI elements from main thread"""
        if not self.is_processing:
            return
            
        self.progress_bar.set(percentage / 100)
        self.progress_percent.configure(text=f"{percentage:.1f}%")
        self.page_counter.configure(text=f"📄 Pages: {current}/{total}")
        
        if percentage < 25:
            self.processing_status.configure(text="🔍 Loading document...", text_color="#FFD700")
        elif percentage < 50:
            self.processing_status.configure(text="📝 Processing pages...", text_color="#FFA500")
        elif percentage < 75:
            self.processing_status.configure(text="🖼️ Optimizing images...", text_color="#FF6B35")
        else:
            self.processing_status.configure(text="✨ Finalizing...", text_color="#4CAF50")
    
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
                
                time.sleep(0.02)
            
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
            self.status_label.configure(text="✅ Processing completed successfully!", text_color="#4CAF50")
            
            input_size = os.path.getsize(input_path) / 1024 / 1024
            output_size = os.path.getsize(output_path) / 1024 / 1024
            
            messagebox.showinfo(
                "Success", 
                f"PDF processed successfully!\n\n"
                f"📦 Input: {input_size:.1f} MB\n"
                f"📤 Output: {output_size:.1f} MB\n"
                f"💾 Saved as: {os.path.basename(output_path)}"
            )
        else:
            self.status_label.configure(text="ℹ️ Processing completed", text_color="#FF6B35")
    
    def on_processing_error(self, error_msg):
        """Handle processing errors"""
        self.is_processing = False
        self.show_main_ui()
        self.status_label.configure(text="❌ Error occurred!", text_color="#DC143C")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PDFResizerApp()
    app.run()