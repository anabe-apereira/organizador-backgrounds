#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Organizador de Fundos ProPresenter
---------------------------------
Autor: Ana Beatriz Alves Pereira
Versão: 1.0.0
Descrição: Ferramenta para organização automática de vídeos de fundo por cores dominantes.
Licença: MIT
Site: https://github.com/anabe-apereira/organizador-backgrounds
"""

import os
import re
import sys
import time
import shutil
import tkinter as tk
import ctypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np
from PIL import Image, ImageTk
from sklearn.cluster import KMeans

def set_win_taskbar_icon(root, icon_path):
    """Set taskbar icon on Windows"""
    try:
        if os.name == 'nt':  # Only for Windows
            # Try different paths for the icon
            icon_paths = [
                icon_path,
                os.path.join(os.path.dirname(sys.executable), 'icon.ico'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico'),
                'icon.ico'  # Try relative path
            ]
            
            for path in icon_paths:
                if os.path.exists(path):
                    icon_path = os.path.abspath(path)
                    root.iconbitmap(default=icon_path)
                    
                    # Set taskbar icon (for Windows 7+)
                    if hasattr(ctypes, 'windll'):
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("OrganizadorDeFundos.ProPresenter")
                    print(f"Ícone carregado com sucesso: {icon_path}")
                    return
            
            print("Aviso: Ícone não encontrado em nenhum dos caminhos testados")
    except Exception as e:
        print(f"Erro ao definir o ícone da barra de tarefas: {e}")

import logging
from datetime import datetime
from tqdm import tqdm
from sklearn.cluster import KMeans
import argparse

# Configuration
DEFAULT_CONFIG = {
    'sample_frames': 10,  # Number of frames to sample from each video
    'resize_width': 320,  # Width to resize frames for processing
    'min_color_percent': 20,  # Minimum percentage for a color to be considered
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
def setup_logging():
    """Configura logging com arquivo timestamp."""
    # Primeiro, configura um logger básico para capturar erros iniciais
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    try:
        # Cria o diretório de logs se não existir
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Cria um nome de arquivo com timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = log_dir / f'logs_{timestamp}.txt'
        
        # Remove todos os handlers existentes
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configura o logging com arquivo e console
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)
        
        logging.info(f"Arquivo de log criado: {log_file}")
        return str(log_file.absolute())
    except Exception as e:
        logging.error(f"Erro ao configurar arquivo de log: {e}")
        return None

@dataclass
class ColorInfo:
    name: str
    h_range: List[Tuple[int, int]]
    is_bw: bool = False

def rgb_to_hsv_range(r_center: int, g_center: int, b_center: int, tolerance: int = 30) -> List[Tuple[int, int]]:
    """Converte um centro de cor RGB para uma faixa de matiz HSV com tolerância."""
    # Criar uma imagem 1x1 com a cor RGB
    rgb_color = np.uint8([[[b_center, g_center, r_center]]])  # OpenCV usa BGR
    hsv_color = cv2.cvtColor(rgb_color, cv2.COLOR_BGR2HSV)
    h_center = hsv_color[0, 0, 0]
    
    # Calcular faixa com tolerância
    h_min = max(0, h_center - tolerance)
    h_max = min(179, h_center + tolerance)
    
    # Tratar caso especial de vermelho que atravessa o 0/179
    if h_center < tolerance:
        # Vermelho próximo ao 0, retorna duas faixas
        return [(0, h_max), (179 - (tolerance - h_center), 179)]
    elif h_center > (179 - tolerance):
        # Vermelho próximo ao 179, retorna duas faixas
        return [(h_min, 179), (0, tolerance - (179 - h_center))]
    else:
        # Cor normal, retorna uma faixa
        return [(h_min, h_max)]

def get_color_ranges() -> Dict[str, ColorInfo]:
    """Return color range definitions from current config."""
    color_infos = {}
    
    # Add colors from DEFAULT_CONFIG['color_ranges']
    for color_name, ranges in DEFAULT_CONFIG.get('color_ranges', {}).items():
        color_infos[color_name] = ColorInfo(color_name, ranges, is_bw=False)
    
    # Add black/white
    color_infos['preto-branco'] = ColorInfo('preto-branco', [], is_bw=True)
    
    return color_infos

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
            
            # Check for black/white (preto-branco)
            if v_val < DEFAULT_CONFIG['value_threshold_black'] or (v_val > DEFAULT_CONFIG['value_threshold_white'] and s_val < DEFAULT_CONFIG['saturation_threshold_white']):
                color_counts['preto-branco'] += 1
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
        # Verificar se o arquivo existe antes de tentar abrir
        if not video_path.exists():
            print(f"Arquivo não encontrado: {video_path}")
            return None, []
        
        # Open video file
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"Não foi possível abrir o vídeo: {video_path}")
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
            print(f"Nenhum frame processado para: {video_path}")
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
        print(f"Erro ao processar {video_path}: {str(e)}")
        return video_path, []

def get_color_combinations():
    """Gera todas as combinações de duas cores em ordem alfabética."""
    # Não é mais necessário criar combinações, pois usamos apenas a cor majoritária
    return []

def get_destination_folder(colors: List[Tuple[str, float]], dest_dir: Path) -> Path:
    """Determine the destination folder based on dominant colors."""
    if not colors:
        return dest_dir / 'nao_identificado'
    
    # Se não houver cores predominantes claras (múltiplas cores sem predominância)
    if len(colors) > 1:
        # Verificar se a primeira cor tem uma predominância significativa (>50%)
        if colors[0][1] > 50:
            return dest_dir / colors[0][0]
        else:
            # Múltiplas cores sem predominância clara -> pasta colorido
            return dest_dir / 'colorido'
    
    # Apenas uma cor predominante
    return dest_dir / colors[0][0]

def copy_video(src_path: Path, dest_dir: Path, overwrite=False) -> Optional[Path]:
    """Copy video to destination with conflict resolution."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src_path.name
    
    # Verificar se o arquivo já existe no destino
    if dest_path.exists():
        if overwrite:
            try:
                dest_path.unlink()
            except Exception as e:
                print(f"Erro ao sobrescrever arquivo {dest_path}: {e}")
                return None
        else:
            # Arquivo já existe e não deve sobrescrever
            print(f"Arquivo já existe no destino, ignorando: {src_path.name}")
            return None
    
    try:
        shutil.copy2(str(src_path), str(dest_path))
        return dest_path
    except Exception as e:
        print(f"Erro ao copiar arquivo {src_path}: {e}")
        return None

class VideoOrganizerApp:
    def __init__(self, root):
        self.root = root
        try:
            self.root.title("Organizador de Fundos ProPresenter")
            self.root.geometry("800x600")
            
            # Definir o ícone do aplicativo
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            set_win_taskbar_icon(self.root, icon_path)
            
            # Variables
            self.src_dir = tk.StringVar()
            self.dest_dir = tk.StringVar()
            self.overwrite = tk.BooleanVar(value=False)
            self.delete_source = tk.BooleanVar(value=False)
            self.processing = False
            self.inactivity_timer = None
            
            # Configuration variables
            self.config_vars = {
                'sample_frames': tk.IntVar(value=DEFAULT_CONFIG['sample_frames']),
                'resize_width': tk.IntVar(value=DEFAULT_CONFIG['resize_width']),
                'min_color_percent': tk.IntVar(value=DEFAULT_CONFIG['min_color_percent'])
            }
            
            # Color variables
            self.color_vars = {}
            self.setup_color_vars()
            
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", f"Erro ao iniciar aplicação: {str(e)}")
            self.root.destroy()
            raise
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log file info
        self.log_file = setup_logging()
        log_frame = ttk.LabelFrame(main_frame, text="Arquivo de Log", padding="5")
        log_frame.grid(row=0, column=0, columnspan=3, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(log_frame, text="Arquivo:", font=('TkDefaultFont', 8)).pack(anchor=tk.W)
        log_path_label = ttk.Label(log_frame, text=self.log_file or "Não foi possível criar arquivo de log", 
                                 foreground="blue", cursor="hand2", font=('TkDefaultFont', 8))
        log_path_label.pack(anchor=tk.W, fill=tk.X)
        
        if self.log_file:
            log_path_label.bind("<Button-1>", lambda e: os.startfile(os.path.dirname(self.log_file)))
        
        # Source directory
        ttk.Label(main_frame, text="Pasta de Origem:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.src_dir, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar...", command=self.browse_src).grid(row=1, column=2, padx=5, pady=5)
        
        # Destination directory
        ttk.Label(main_frame, text="Pasta de Destino:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dest_dir, width=50).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar...", command=self.browse_dest).grid(row=2, column=2, padx=5, pady=5)
        
        # Options - moved to separate frame for better organization
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=10)
        
        ttk.Checkbutton(
            options_frame, 
            text="Sobrescrever arquivos existentes",
            variable=self.overwrite
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame, 
            text="Excluir arquivos da pasta de origem após cópia",
            variable=self.delete_source
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate',
            variable=self.progress_var
        )
        self.progress.grid(row=4, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Logs de Processamento", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=tk.NSEW)
        log_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configuration and Start buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        config_button = ttk.Button(button_frame, text="⚙️ Configurações", command=self.open_config_window)
        config_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Iniciar Organização", 
            command=self.start_processing
        )
        self.start_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Redirect stdout to log
        self.text_redirector = TextRedirector(self.log_text, "stdout")
        sys.stdout = self.text_redirector
        sys.stderr = TextRedirector(self.log_text, "stderr")
        
        # Configurar arquivo de log para as saídas
        log_file = setup_logging()
        if log_file:
            self.text_redirector.set_log_file(log_file)
            sys.stderr.set_log_file(log_file)
    
    def setup_color_vars(self):
        """Initialize color variables with default RGB values."""
        default_colors_rgb = {
            'vermelho': (255, 0, 0),      # Vermelho puro
            'laranja': (255, 165, 0),     # Laranja
            'amarelo': (255, 255, 0),     # Amarelo
            'verde': (0, 255, 0),         # Verde puro
            'azul': (0, 0, 255),          # Azul puro
            'violeta': (128, 0, 128),     # Violeta
        }
        
        for color_name, (r, g, b) in default_colors_rgb.items():
            self.color_vars[color_name] = {
                'r': tk.IntVar(value=r),
                'g': tk.IntVar(value=g),
                'b': tk.IntVar(value=b),
                'enabled': tk.BooleanVar(value=True)
            }
    
    def open_config_window(self):
        """Open configuration window for parameters and colors."""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurações de Processamento")
        config_window.geometry("600x500")
        config_window.resizable(False, False)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(config_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Parameters tab
        params_frame = ttk.Frame(notebook)
        notebook.add(params_frame, text="Parâmetros")
        self.setup_params_tab(params_frame)
        
        # Colors tab
        colors_frame = ttk.Frame(notebook)
        notebook.add(colors_frame, text="Cores")
        self.setup_colors_tab(colors_frame)
        
        # Buttons
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Salvar", command=lambda: self.save_config(config_window)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=config_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Restaurar Padrão", command=lambda: self.restore_defaults(config_window)).pack(side=tk.LEFT, padx=5)
    
    def setup_params_tab(self, parent):
        """Setup parameters configuration tab."""
        # Sample frames
        ttk.Label(parent, text="Número de Quadros Amostrados:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        sample_spinbox = ttk.Spinbox(parent, from_=1, to=100, textvariable=self.config_vars['sample_frames'], width=15)
        sample_spinbox.grid(row=0, column=1, padx=10, pady=(10, 2), sticky=tk.W)
        ttk.Label(parent, text="Quantos quadros analisar de cada vídeo", font=('TkDefaultFont', 9), foreground='gray').grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(0, 10))
        
        # Resize width
        ttk.Label(parent, text="Largura de Redimensionamento:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        resize_spinbox = ttk.Spinbox(parent, from_=100, to=1920, increment=10, textvariable=self.config_vars['resize_width'], width=15)
        resize_spinbox.grid(row=2, column=1, padx=10, pady=(10, 2), sticky=tk.W)
        ttk.Label(parent, text="Largura para processamento (menor = mais rápido)", font=('TkDefaultFont', 9), foreground='gray').grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(0, 10))
        
        # Min color percent
        ttk.Label(parent, text="Percentual Mínimo de Cor:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=(10, 2))
        percent_spinbox = ttk.Spinbox(parent, from_=1, to=100, textvariable=self.config_vars['min_color_percent'], width=15)
        percent_spinbox.grid(row=4, column=1, padx=10, pady=(10, 2), sticky=tk.W)
        ttk.Label(parent, text="Percentual mínimo para considerar uma cor dominante", font=('TkDefaultFont', 9), foreground='gray').grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(0, 10))
    
    def setup_colors_tab(self, parent):
        """Setup colors configuration tab with RGB controls."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        ttk.Label(scrollable_frame, text="Cor", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(scrollable_frame, text="R", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="G", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="B", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Preview", font=('Arial', 10, 'bold')).grid(row=0, column=4, padx=10, pady=5)
        ttk.Label(scrollable_frame, text="Ativo", font=('Arial', 10, 'bold')).grid(row=0, column=5, padx=10, pady=5)
        
        row = 1
        self.color_previews = {}
        
        for color_name, vars_dict in self.color_vars.items():
            # Color name
            ttk.Label(scrollable_frame, text=color_name.capitalize()).grid(row=row, column=0, padx=10, pady=3, sticky=tk.W)
            
            # RGB controls
            r_spinbox = ttk.Spinbox(scrollable_frame, from_=0, to=255, textvariable=vars_dict['r'], width=6)
            r_spinbox.grid(row=row, column=1, padx=5, pady=3)
            
            g_spinbox = ttk.Spinbox(scrollable_frame, from_=0, to=255, textvariable=vars_dict['g'], width=6)
            g_spinbox.grid(row=row, column=2, padx=5, pady=3)
            
            b_spinbox = ttk.Spinbox(scrollable_frame, from_=0, to=255, textvariable=vars_dict['b'], width=6)
            b_spinbox.grid(row=row, column=3, padx=5, pady=3)
            
            # Color preview
            preview_label = tk.Label(scrollable_frame, width=8, height=1, relief=tk.RAISED, borderwidth=2)
            preview_label.grid(row=row, column=4, padx=10, pady=3)
            self.color_previews[color_name] = preview_label
            
            # Enable checkbox
            ttk.Checkbutton(scrollable_frame, variable=vars_dict['enabled']).grid(row=row, column=5, padx=10, pady=3)
            
            # Update preview when values change
            def update_preview(name=color_name, label=preview_label, r_var=vars_dict['r'], g_var=vars_dict['g'], b_var=vars_dict['b']):
                r = r_var.get()
                g = g_var.get()
                b = b_var.get()
                hex_color = f'#{r:02x}{g:02x}{b:02x}'
                label.configure(bg=hex_color)
            
            # Bind updates
            vars_dict['r'].trace('w', lambda *args, cn=color_name: update_preview())
            vars_dict['g'].trace('w', lambda *args, cn=color_name: update_preview())
            vars_dict['b'].trace('w', lambda *args, cn=color_name: update_preview())
            
            # Initial preview update
            update_preview()
            
            row += 1
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def save_config(self, window):
        """Save configuration and update global config."""
        # Update global config
        global DEFAULT_CONFIG
        DEFAULT_CONFIG['sample_frames'] = self.config_vars['sample_frames'].get()
        DEFAULT_CONFIG['resize_width'] = self.config_vars['resize_width'].get()
        DEFAULT_CONFIG['min_color_percent'] = self.config_vars['min_color_percent'].get()
        
        # Convert RGB to HSV and update color ranges
        new_color_ranges = {}
        for color_name, vars_dict in self.color_vars.items():
            if vars_dict['enabled'].get():
                r = vars_dict['r'].get()
                g = vars_dict['g'].get()
                b = vars_dict['b'].get()
                
                # Convert RGB to HSV range
                hsv_ranges = rgb_to_hsv_range(r, g, b)
                new_color_ranges[color_name] = hsv_ranges
        
        DEFAULT_CONFIG['color_ranges'] = new_color_ranges
        
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!\nCores RGB convertidas para HSV para processamento.")
        window.destroy()
    
    def restore_defaults(self, window):
        """Restore default configuration."""
        if messagebox.askyesno("Confirmar", "Deseja restaurar as configurações padrão?"):
            # Reset parameters
            self.config_vars['sample_frames'].set(10)
            self.config_vars['resize_width'].set(320)
            self.config_vars['min_color_percent'].set(20)
            
            # Reset colors
            self.setup_color_vars()
            
            # Refresh the colors tab
            for widget in window.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    # Recreate the colors tab
                    widget.forget(1)  # Remove the colors tab
                    colors_frame = ttk.Frame(widget)
                    widget.add(colors_frame, text="Cores")
                    self.setup_colors_tab(colors_frame)
                    break
    
    def browse_src(self):
        folder = filedialog.askdirectory()
        if folder:
            self.src_dir.set(folder)
    
    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_dir.set(folder)
    
    def log(self, message, log_to_file=True):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Escrever na tela
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, formatted_message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        
        # Escrever no arquivo de log apenas se solicitado
        if log_to_file:
            print(formatted_message)
        
        # Forçar atualização da interface
        self.root.update_idletasks()
    
    def start_processing(self):
        if self.inactivity_timer is not None:
            self.root.after_cancel(self.inactivity_timer)
            self.inactivity_timer = None
            
        src_dir = Path(self.src_dir.get())
        dest_dir = Path(self.dest_dir.get())
        
        if not src_dir.exists() or not src_dir.is_dir():
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de origem válida.")
            return
            
        if not dest_dir or not dest_dir.exists():
            messagebox.showerror("Erro", "Por favor, selecione uma pasta de destino válida.")
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
        # Criar pastas necessárias
        required_dirs = [
            'vermelho', 'laranja', 'amarelo', 'verde',
            'azul', 'violeta', 'preto-branco',
            'colorido', 'nao_identificado'
        ]
    
        # Criar todas as pastas necessárias
        for dir_name in required_dirs:
            (dest_dir / dir_name).mkdir(parents=True, exist_ok=True)
            
        total_files = len(video_files)
        processed = 0
       
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
                
                if dest_path is None:
                    # Arquivo não foi copiado (já existe ou erro)
                    self.log(f"  ⚠️ Arquivo não copiado: {video_path.name}")
                    continue
                
                # Delete source file if option is enabled
                if self.delete_source.get():
                    try:
                        video_path.unlink()
                        self.log(f"  ✅ Arquivo original excluído: {video_path.name}")
                    except Exception as delete_error:
                        self.log(f"  ⚠️ Erro ao excluir original: {str(delete_error)}")
                
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
        """Finaliza o processamento e inicia o temporizador para fechar a janela."""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.root.title("Organizador de Fundos ProPresenter - Concluído")
        messagebox.showinfo("Concluído", "Processamento finalizado com sucesso!")
        
        # Código de fechamento automático comentado para possível reativação futura
        # Configurar o temporizador para fechar após 30 segundos
        # self.inactivity_timer = self.root.after(30000, self.close_application)
        
        # Configurar eventos para resetar o temporizador quando houver interação
        # self.root.bind("<Button-1>", self.reset_inactivity_timer)
        # self.root.bind("<Key>", self.reset_inactivity_timer)
        # self.log_text.bind("<Button-1>", self.reset_inactivity_timer)

    def reset_inactivity_timer(self, event=None):
        """Reinicia o temporizador de inatividade."""
        # Código comentado - função desativada
        # if hasattr(self, 'inactivity_timer'):
        #     self.root.after_cancel(self.inactivity_timer)
        # self.inactivity_timer = self.root.after(30000, self.close_application)
        pass

    def close_application(self, event=None):
        """Fecha a aplicação de forma segura."""
        # Código comentado - função desativada
        # if hasattr(self, 'inactivity_timer'):
        #     self.root.after_cancel(self.inactivity_timer)
        # self.root.quit()
        # self.root.destroy()
        pass

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
        self.log_file = None
        self.skip_next = False  # Flag para controlar logs duplicados
        
    def write(self, str_):
        # Pular logs que já foram tratados pelo método log()
        if self.skip_next:
            self.skip_next = False
            return
            
        # Se a mensagem começa com timestamp, é do método log()
        if re.match(r'^\[\d{2}:\d{2}:\d{2}\]', str_):
            self.skip_next = True  # Marcar para pular a próxima mensagem
            
        # Escrever no widget da interface
        self.widget.configure(state="normal")
        self.widget.insert("end", str_, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")
        
        # Escrever no arquivo de log
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(str_)
            except Exception as e:
                # Usar stderr diretamente para evitar loop infinito
                import sys
                sys.stderr.write(f"Erro ao escrever no arquivo de log: {e}\n")
    
    def set_log_file(self, log_file):
        """Define o arquivo de log para salvar as saídas."""
        self.log_file = log_file
     
    def flush(self):
        pass

def parse_arguments():
    parser = argparse.ArgumentParser(description='Organiza vídeos por cor predominante.')
    parser.add_argument('--src', type=str, help='Pasta de origem dos vídeos')
    parser.add_argument('--dst', type=str, help='Pasta de destino para os vídeos organizados')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescrever arquivos existentes')
    parser.add_argument('--delete-source', action='store_true', help='Excluir arquivos da pasta de origem após cópia')
    return parser.parse_args()

def main():
    try:
        args = parse_arguments()
        
        # Configurar logging será feito na inicialização da UI para o modo GUI
        # ou aqui para o modo linha de comando
        if hasattr(args, 'src') and hasattr(args, 'dst') and args.src and args.dst:
            log_file = setup_logging()
            if log_file:
                print(f"Logs serão salvos em: {log_file}")
            
            # Verificar se os argumentos foram fornecidos
            if hasattr(args, 'src') and hasattr(args, 'dst') and args.src and args.dst:
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
                'vermelho', 'laranja', 'amarelo', 'verde',
                'azul', 'violeta', 'preto-branco',
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
                    
                    if dest_path is None:
                        # Arquivo não foi copiado (já existe ou erro)
                        print(f"  ⚠️ Arquivo não copiado: {video_path.name}")
                        continue
                    
                    # Delete source file if option is enabled
                    if args.delete_source:
                        try:
                            video_path.unlink()
                            print(f"  ✅ Arquivo original excluído: {video_path.name}")
                        except Exception as delete_error:
                            print(f"  ⚠️ Erro ao excluir original: {str(delete_error)}")
                    
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
            # GUI mode - sempre iniciar GUI se não houver argumentos
            try:
                root = tk.Tk()
                app = VideoOrganizerApp(root)
                root.mainloop()
            except Exception as e:
                import traceback
                traceback.print_exc()
                try:
                    messagebox.showerror("Erro", f"Erro fatal na aplicação: {str(e)}")
                except:
                    pass
                if 'root' in locals():
                    try:
                        root.destroy()
                    except:
                        pass
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
