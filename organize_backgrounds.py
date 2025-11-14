import os
import sys
import cv2
import numpy as np
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime
from tqdm import tqdm
from sklearn.cluster import KMeans
import argparse

# Configuration
DEFAULT_CONFIG = {
    'sample_frames': 10,  # Number of frames to sample from each video
    'resize_width': 320,  # Width to resize frames for processing
    'min_color_percent': 8,  # Minimum percentage for a color to be considered
    'supported_formats': ('.mp4', '.mov', '.avi', '.m4v'),
    'color_ranges': {
        'red': [(0, 10), (170, 179)],
        'orange': [(11, 25)],
        'yellow': [(26, 35)],
        'green': [(36, 85)],
        'cyan': [(86, 100)],
        'blue': [(101, 140)],
        'violet': [(141, 160)],
        'pink': [(161, 170)],
    },
    'saturation_threshold': 30,  # Minimum saturation to be considered colored
    'value_threshold_white': 200,  # Minimum value to be considered white
    'saturation_threshold_white': 30,  # Maximum saturation to be considered white
    'value_threshold_black': 30,  # Maximum value to be considered black
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ColorInfo:
    name: str
    h_range: List[Tuple[int, int]]
    is_bw: bool = False

def get_color_ranges() -> Dict[str, ColorInfo]:
    """Return color range definitions."""
    return {
        'red': ColorInfo('red', [(0, 10), (170, 179)]),
        'orange': ColorInfo('orange', [(11, 25)]),
        'yellow': ColorInfo('yellow', [(26, 35)]),
        'green': ColorInfo('green', [(36, 85)]),
        'cyan': ColorInfo('cyan', [(86, 100)]),
        'blue': ColorInfo('blue', [(101, 140)]),
        'violet': ColorInfo('violet', [(141, 160)]),
        'pink': ColorInfo('pink', [(161, 170)]),
        'white': ColorInfo('white', [], is_bw=True),
        'black': ColorInfo('black', [], is_bw=True)
    }

def is_color_in_range(h: int, color_info: ColorInfo) -> bool:
    """Check if hue value falls within any of the color ranges."""
    if color_info.is_bw:
        return False
    for r in color_info.h_range:
        if r[0] <= h <= r[1]:
            return True
    return False

def get_dominant_colors(frame, k=5):
    """Get dominant colors using KMeans clustering."""
    # Reshape the image to be a list of pixels
    pixels = frame.reshape(-1, 3)
    
    # Convert to float32 for KMeans
    pixels = np.float32(pixels)
    
    # Define criteria and apply KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.2)
    _, labels, palette = cv2.kmeans(
        pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )
    
    # Get the count of each dominant color
    _, counts = np.unique(labels, return_counts=True)
    
    # Convert palette to uint8
    palette = np.uint8(palette)
    
    # Return colors sorted by frequency
    sorted_indices = np.argsort(counts)[::-1]
    return palette[sorted_indices], counts[sorted_indices] / counts.sum()

def analyze_frame_colors(frame, color_infos):
    """Analyze colors in a frame and return color percentages."""
    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Initialize color counts
    color_counts = {name: 0 for name in color_infos}
    total_pixels = h.size
    
    # Check each pixel
    for i in range(h.shape[0]):
        for j in range(h.shape[1]):
            h_val = h[i, j]
            s_val = s[i, j]
            v_val = v[i, j]
            
            # Check for black
            if v_val < DEFAULT_CONFIG['value_threshold_black']:
                color_counts['black'] += 1
                continue
                
            # Check for white
            if v_val > DEFAULT_CONFIG['value_threshold_white'] and s_val < DEFAULT_CONFIG['saturation_threshold_white']:
                color_counts['white'] += 1
                continue
                
            # Skip low saturation (grayscale)
            if s_val < DEFAULT_CONFIG['saturation_threshold']:
                continue
                
            # Check color ranges
            for name, color_info in color_infos.items():
                if color_info.is_bw:
                    continue
                if is_color_in_range(h_val, color_info):
                    color_counts[name] += 1
                    break
    
    # Convert counts to percentages
    return {name: (count / total_pixels) * 100 for name, count in color_counts.items()}

def process_video(video_path: Path, progress_callback=None):
    """Process a single video file and return dominant colors."""
    try:
        # Open video file
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logging.error(f"Could not open video: {video_path}")
            return None, []
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        # Determine frame sampling strategy
        sample_rate = max(1, total_frames // DEFAULT_CONFIG['sample_frames'])
        
        color_infos = get_color_ranges()
        color_totals = {name: 0.0 for name in color_infos}
        frames_processed = 0
        
        # Process frames
        for frame_idx in range(0, total_frames, sample_rate):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
                
            # Resize frame for faster processing
            height, width = frame.shape[:2]
            scale = DEFAULT_CONFIG['resize_width'] / width
            new_size = (DEFAULT_CONFIG['resize_width'], int(height * scale))
            frame = cv2.resize(frame, new_size, interpolation=cv2.INTER_AREA)
            
            # Analyze frame colors
            frame_colors = analyze_frame_colors(frame, color_infos)
            
            # Update totals
            for color, percent in frame_colors.items():
                color_totals[color] += percent
            
            frames_processed += 1
            
            # Update progress
            if progress_callback:
                progress_callback()
        
        cap.release()
        
        if frames_processed == 0:
            logging.warning(f"No frames processed for: {video_path}")
            return video_path, []
        
        # Calculate average percentages
        avg_percentages = {color: total / frames_processed for color, total in color_totals.items()}
        
        # Filter colors above threshold
        dominant_colors = [
            (color, percent) 
            for color, percent in avg_percentages.items() 
            if percent >= DEFAULT_CONFIG['min_color_percent']
        ]
        
        # Sort by percentage (descending)
        dominant_colors.sort(key=lambda x: x[1], reverse=True)
        
        return video_path, dominant_colors
        
    except Exception as e:
        logging.error(f"Error processing {video_path}: {str(e)}")
        return video_path, []

def get_destination_folder(colors: List[Tuple[str, float]], dest_dir: Path) -> Path:
    """Determine the destination folder based on dominant colors."""
    if not colors:
        return dest_dir / 'nao_identificado'
    
    color_names = [color[0] for color in colors]
    
    # If more than 3 colors or only one color
    if len(color_names) > 3:
        return dest_dir / 'colorido'
    elif len(color_names) == 1:
        return dest_dir / color_names[0]
    
    # For 2 or 3 colors, create a combination folder
    folder_name = '-'.join(sorted(color_names))
    return dest_dir / folder_name

def copy_video(src_path: Path, dest_dir: Path, overwrite=False) -> Path:
    """Copy video to destination with conflict resolution."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src_path.name
    
    if dest_path.exists() and not overwrite:
        # Add a number suffix to avoid overwriting
        counter = 1
        while True:
            new_name = f"{src_path.stem}({counter}){src_path.suffix}"
            new_dest = dest_dir / new_name
            if not new_dest.exists():
                dest_path = new_dest
                break
            counter += 1
    
    shutil.copy2(str(src_path), str(dest_path))
    return dest_path

class VideoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Fundos ProPresenter")
        self.root.geometry("800x600")
        
        # Variables
        self.src_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.overwrite = tk.BooleanVar(value=False)
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source directory
        ttk.Label(main_frame, text="Pasta de Origem:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.src_dir, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar...", command=self.browse_src).grid(row=0, column=2, padx=5, pady=5)
        
        # Destination directory
        ttk.Label(main_frame, text="Pasta de Destino:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_dir, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar...", command=self.browse_dest).grid(row=1, column=2, padx=5, pady=5)
        
        # Options
        ttk.Checkbutton(
            main_frame, 
            text="Sobrescrever arquivos existentes",
            variable=self.overwrite
        ).grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate',
            variable=self.progress_var
        )
        self.progress.grid(row=3, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_text = tk.Text(main_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky=tk.NS)
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Start button
        self.start_button = ttk.Button(
            main_frame, 
            text="Iniciar Organização", 
            command=self.start_processing
        )
        self.start_button.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Redirect stdout to log
        sys.stdout = TextRedirector(self.log_text, "stdout")
        sys.stderr = TextRedirector(self.log_text, "stderr")
    
    def browse_src(self):
        folder = filedialog.askdirectory()
        if folder:
            self.src_dir.set(folder)
    
    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_dir.set(folder)
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_processing(self):
        if self.processing:
            return
            
        src_dir = Path(self.src_dir.get())
        dest_dir = Path(self.dest_dir.get())
        
        if not src_dir.exists() or not src_dir.is_dir():
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de origem válida.")
            return
            
        if not dest_dir:
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino.")
            return
        
        # Create destination directory if it doesn't exist
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all video files
        video_files = []
        for ext in DEFAULT_CONFIG['supported_formats']:
            video_files.extend(list(src_dir.rglob(f"*{ext}")))
            video_files.extend(list(src_dir.rglob(f"*{ext.upper()}")))
        
        if not video_files:
            messagebox.showinfo("Aviso", f"Nenhum arquivo de vídeo encontrado em {src_dir}")
            return
        
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.log(f"Iniciando processamento de {len(video_files)} vídeos...")
        
        # Process videos in a separate thread to keep the UI responsive
        import threading
        threading.Thread(
            target=self.process_videos,
            args=(video_files, dest_dir, self.overwrite.get()),
            daemon=True
        ).start()
    
    def process_videos(self, video_files, dest_dir, overwrite):
        total_files = len(video_files)
        processed = 0
        
        # Create required directories
        required_dirs = [
            'branco', 'vermelho', 'laranja', 'amarelo', 'verde',
            'ciano', 'azul', 'violeta', 'preto', 'rosa',
            'colorido', 'nao_identificado'
        ]
        
        for dir_name in required_dirs:
            (dest_dir / dir_name).mkdir(exist_ok=True)
        
        # Process each video
        for video_path in video_files:
            try:
                self.log(f"Processando: {video_path.name}")
                
                # Update progress
                processed += 1
                progress = (processed / total_files) * 100
                self.progress_var.set(progress)
                self.root.title(f"Organizador de Fundos ProPresenter - {progress:.1f}%")
                
                # Process video
                _, dominant_colors = process_video(video_path)
                
                # Get destination folder
                dest_folder = get_destination_folder(dominant_colors, dest_dir)
                
                # Create combination folder if it doesn't exist
                dest_folder.mkdir(exist_ok=True)
                
                # Copy file
                dest_path = copy_video(video_path, dest_folder, overwrite)
                
                # Log results
                colors_str = ", ".join(f"{c[0]} ({c[1]:.1f}%)" for c in dominant_colors) if dominant_colors else "não identificado"
                self.log(f"  → {colors_str} → {dest_path.relative_to(dest_dir)}")
                
            except Exception as e:
                self.log(f"Erro ao processar {video_path.name}: {str(e)}")
                # Try to copy to nao_identificado on error
                try:
                    error_dest = dest_dir / 'nao_identificado'
                    error_dest.mkdir(exist_ok=True)
                    copy_video(video_path, error_dest, overwrite)
                    self.log(f"  → Copiado para: {error_dest.relative_to(dest_dir)}")
                except Exception as copy_error:
                    self.log(f"  → Falha ao copiar: {str(copy_error)}")
        
        # Update UI when done
        self.root.after(0, self.processing_complete)
    
    def processing_complete(self):
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.root.title("Organizador de Fundos ProPresenter - Concluído")
        messagebox.showinfo("Concluído", "Processamento finalizado!")

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
    
    def write(self, str_):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")
    
    def flush(self):
        pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='Organiza vídeos por cor predominante.')
    parser.add_argument('--src', type=str, help='Pasta de origem contendo os vídeos')
    parser.add_argument('--dst', type=str, help='Pasta de destino para os vídeos organizados')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescrever arquivos existentes')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if args.src and args.dst:
        # Command line mode
        src_dir = Path(args.src)
        dest_dir = Path(args.dst)
        
        if not src_dir.exists() or not src_dir.is_dir():
            print(f"Erro: A pasta de origem não existe: {src_dir}")
            return
            
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all video files
        video_files = []
        for ext in DEFAULT_CONFIG['supported_formats']:
            video_files.extend(list(src_dir.rglob(f"*{ext}")))
            video_files.extend(list(src_dir.rglob(f"*{ext.upper()}")))
        
        if not video_files:
            print(f"Nenhum arquivo de vídeo encontrado em {src_dir}")
            return
        
        print(f"Processando {len(video_files)} vídeos...")
        
        # Create required directories
        required_dirs = [
            'branco', 'vermelho', 'laranja', 'amarelo', 'verde',
            'ciano', 'azul', 'violeta', 'preto', 'rosa',
            'colorido', 'nao_identificado'
        ]
        
        for dir_name in required_dirs:
            (dest_dir / dir_name).mkdir(exist_ok=True)
        
        # Process each video
        for i, video_path in enumerate(video_files, 1):
            try:
                print(f"[{i}/{len(video_files)}] Processando: {video_path.name}")
                
                # Process video
                _, dominant_colors = process_video(video_path)
                
                # Get destination folder
                dest_folder = get_destination_folder(dominant_colors, dest_dir)
                
                # Create combination folder if it doesn't exist
                dest_folder.mkdir(exist_ok=True)
                
                # Copy file
                dest_path = copy_video(video_path, dest_folder, args.overwrite)
                
                # Print results
                colors_str = ", ".join(f"{c[0]} ({c[1]:.1f}%)" for c in dominant_colors) if dominant_colors else "não identificado"
                print(f"  → {colors_str} → {dest_path.relative_to(dest_dir)}")
                
            except Exception as e:
                print(f"Erro ao processar {video_path.name}: {str(e)}")
                # Try to copy to nao_identificado on error
                try:
                    error_dest = dest_dir / 'nao_identificado'
                    error_dest.mkdir(exist_ok=True)
                    copy_video(video_path, error_dest, args.overwrite)
                    print(f"  → Copiado para: {error_dest.relative_to(dest_dir)}")
                except Exception as copy_error:
                    print(f"  → Falha ao copiar: {str(copy_error)}")
        
        print("\nProcessamento concluído!")
    else:
        # GUI mode
        root = tk.Tk()
        app = VideoOrganizerApp(root)
        root.mainloop()

if __name__ == "__main__":
    main()
