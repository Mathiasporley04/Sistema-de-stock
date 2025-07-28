import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

class SistemaControlStock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Control de Stock")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Configuración de Google Sheets
        self.sheet_name = "Control_Stock"
        self.gc = None
        self.worksheet = None
        
        # Variables
        self.productos = {}
        self.codigo_actual = tk.StringVar()
        self.status_google_sheets = "⏳ Configurando..."
        
        self.setup_google_sheets()
        self.crear_interfaz()
        self.cargar_datos()
        
    def setup_google_sheets(self):
        """Configura la conexión con Google Sheets"""
        try:
            # Scope para Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Verificar si existe el archivo de credenciales
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                self.gc = gspread.authorize(creds)
                
                # Intentar abrir la hoja existente o crear una nueva
                try:
                    self.worksheet = self.gc.open(self.sheet_name).sheet1
                except gspread.SpreadsheetNotFound:
                    # Crear nueva hoja
                    spreadsheet = self.gc.create(self.sheet_name)
                    self.worksheet = spreadsheet.sheet1
                    # Configurar encabezados
                    headers = ['Código', 'Producto', 'Stock Actual', 'Stock Mínimo', 'Última Actualización', 'Precio']
                    self.worksheet.append_row(headers)
                    
                # Mostrar mensaje de éxito en el status bar en lugar de messagebox
                self.status_google_sheets = "✅ Google Sheets conectado"
            else:
                # No mostrar messagebox, solo configurar para modo local
                self.status_google_sheets = "⚠️ Modo local (sin Google Sheets)"
                self.gc = None
                
        except Exception as e:
            # Mostrar error en el status bar en lugar de messagebox
            self.status_google_sheets = f"❌ Error Google Sheets: {str(e)[:50]}..."
            self.gc = None
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica del sistema"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="SISTEMA DE CONTROL DE STOCK", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame para entrada de código
        input_frame = ttk.LabelFrame(main_frame, text="Escaneo de Código de Barras", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Código:").grid(row=0, column=0, sticky=tk.W)
        self.entry_codigo = ttk.Entry(input_frame, textvariable=self.codigo_actual, font=('Arial', 12))
        self.entry_codigo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        self.entry_codigo.bind('<Return>', self.procesar_codigo)
        self.entry_codigo.bind('<KeyRelease>', self.on_key_release)  # Restaurar detección automática
        
        # Atajos de teclado globales
        self.root.bind('<Control-plus>', lambda e: self.sumar_una_unidad())
        self.root.bind('<Control-minus>', lambda e: self.restar_una_unidad())
        self.root.bind('<Control-Key-plus>', lambda e: self.sumar_una_unidad())
        self.root.bind('<Control-Key-minus>', lambda e: self.restar_una_unidad())
        
        # Botones principales (casos más comunes)
        btn_principales_frame = ttk.LabelFrame(main_frame, text="Acciones Principales", padding="10")
        btn_principales_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Botones principales grandes y destacados
        btn_principales = ttk.Frame(btn_principales_frame)
        btn_principales.pack(expand=True)
        
        # Estilo para botones principales grandes
        style = ttk.Style()
        style.configure('BotonesPrincipales.TButton', font=('Arial', 18, 'bold'))
        
        # Botón +1 (Sumar una unidad)
        btn_sumar_uno = ttk.Button(btn_principales, text="+1", 
                                  command=self.sumar_una_unidad, 
                                  style='BotonesPrincipales.TButton')
        btn_sumar_uno.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Botón -1 (Restar una unidad)
        btn_restar_uno = ttk.Button(btn_principales, text="-1", 
                                   command=self.restar_una_unidad, 
                                   style='BotonesPrincipales.TButton')
        btn_restar_uno.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Botones secundarios (casos especiales)
        btn_secundarios_frame = ttk.LabelFrame(main_frame, text="Acciones Secundarias", padding="10")
        btn_secundarios_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        
        btn_secundarios = ttk.Frame(btn_secundarios_frame)
        btn_secundarios.pack(expand=True)
        
        ttk.Button(btn_secundarios, text="📈 Sumar Múltiples", 
                  command=self.dar_alta_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_secundarios, text="📉 Restar Múltiples", 
                  command=self.dar_baja_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_secundarios, text="➕ Agregar Producto", 
                  command=self.agregar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_secundarios, text="📊 Ver Reporte", 
                  command=self.mostrar_reporte).pack(side=tk.LEFT, padx=5)
        
        # Frame para información del producto
        info_frame = ttk.LabelFrame(main_frame, text="Información del Producto", padding="10")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Labels para información
        self.labels_info = {}
        campos = ['Código:', 'Producto:', 'Stock Actual:', 'Stock Mínimo:', 'Precio Costo Unidad:', 'Última Actualización:']
        
        for i, campo in enumerate(campos):
            ttk.Label(info_frame, text=campo, font=('Arial', 10, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=2)
            label_valor = ttk.Label(info_frame, text="", font=('Arial', 10))
            label_valor.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            self.labels_info[campo] = label_valor
        
        # Tabla de productos
        tabla_frame = ttk.LabelFrame(main_frame, text="Inventario", padding="10")
        tabla_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        tabla_frame.columnconfigure(0, weight=1)
        tabla_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Crear Treeview
        columns = ('Código', 'Producto', 'Stock', 'Stock Mín', 'Precio Costo', 'Última Actualización')
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        for col in columns:
            self.tabla.heading(col, text=col)
            if col == 'Precio Costo':
                self.tabla.column(col, width=100)
            else:
                self.tabla.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Evento de selección
        self.tabla.bind('<<TreeviewSelect>>', self.seleccionar_producto)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"{self.status_google_sheets} | Listo para escanear")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Establecer foco en el campo de código inmediatamente
        self.entry_codigo.focus()
    
    def establecer_foco_campo(self):
        """Establece el foco en el campo de código y lo prepara para la entrada"""
        self.entry_codigo.focus()
        self.entry_codigo.select_range(0, tk.END)  # Seleccionar todo el texto si hay alguno
        self.status_var.set("Listo para escanear")
    

    
    def procesar_codigo(self, event=None):
        """Procesa el código escaneado automáticamente"""
        codigo = self.codigo_actual.get().strip()
        if codigo and len(codigo) > 0:
            # Procesar inmediatamente
            self.buscar_producto_por_codigo(codigo)
            # Limpiar campo automáticamente
            self.codigo_actual.set("")
            # Volver el foco al campo para el siguiente escaneo
            self.entry_codigo.focus()
            # Seleccionar todo el texto para facilitar el siguiente escaneo
            self.entry_codigo.select_range(0, tk.END)
    
    def buscar_producto_por_codigo(self, codigo):
        """Busca un producto por su código automáticamente"""
        if codigo in self.productos:
            # Producto encontrado - mostrar información inmediatamente
            self.mostrar_producto(self.productos[codigo])
            self.status_var.set(f"✅ {self.productos[codigo]['producto']} - Stock: {self.productos[codigo]['stock']}")
            # Resaltar el producto en la tabla
            self.resaltar_producto_en_tabla(codigo)
        else:
            # Producto no encontrado - limpiar y mostrar mensaje
            self.limpiar_info_producto()
            self.status_var.set(f"❌ Producto no encontrado: {codigo}")
            # Preguntar si agregar (pero de forma menos intrusiva)
            self.preguntar_agregar_producto(codigo)
    
    def mostrar_producto(self, producto):
        """Muestra la información de un producto en la interfaz"""
        self.labels_info['Código:'].config(text=producto['codigo'])
        self.labels_info['Producto:'].config(text=producto['producto'])
        
        # Mostrar stock con color según el nivel
        stock_actual = producto['stock']
        stock_minimo = producto['stock_minimo']
        
        if stock_actual <= stock_minimo:
            # Stock bajo - color rojo
            self.labels_info['Stock Actual:'].config(text=f"{stock_actual} ⚠️", foreground='red')
        elif stock_actual <= stock_minimo * 2:
            # Stock medio - color naranja
            self.labels_info['Stock Actual:'].config(text=f"{stock_actual} ⚡", foreground='orange')
        else:
            # Stock bueno - color verde
            self.labels_info['Stock Actual:'].config(text=f"{stock_actual} ✅", foreground='green')
        
        self.labels_info['Stock Mínimo:'].config(text=str(stock_minimo))
        self.labels_info['Precio Costo Unidad:'].config(text=f"${producto['precio']:.2f}")
        self.labels_info['Última Actualización:'].config(text=producto['ultima_actualizacion'])
    
    def limpiar_info_producto(self):
        """Limpia la información del producto mostrada"""
        for label in self.labels_info.values():
            label.config(text="", foreground='black')  # Resetear color
    
    def agregar_producto_nuevo(self, codigo):
        """Agrega un nuevo producto con el código escaneado"""
        producto = simpledialog.askstring("Nuevo Producto", "Nombre del producto:")
        if producto:
            precio = simpledialog.askfloat("Precio", "Precio del producto:")
            stock_minimo = simpledialog.askinteger("Stock Mínimo", "Stock mínimo:", minvalue=0)
            
            if precio is not None and stock_minimo is not None:
                nuevo_producto = {
                    'codigo': codigo,
                    'producto': producto,
                    'stock': 0,
                    'stock_minimo': stock_minimo,
                    'precio': precio,
                    'ultima_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                self.productos[codigo] = nuevo_producto
                self.actualizar_tabla()
                self.guardar_datos()
                self.mostrar_producto(nuevo_producto)
                self.status_var.set(f"Producto agregado: {producto}")
    

    
    def agregar_producto(self):
        """Abre diálogo para agregar producto manualmente"""
        codigo = simpledialog.askstring("Nuevo Producto", "Código del producto:")
        if codigo:
            self.agregar_producto_nuevo(codigo)
    
    def dar_alta_stock(self):
        """Da de alta stock a un producto"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            cantidad = simpledialog.askinteger("Dar de Alta", 
                                             f"Cantidad a agregar al stock de {self.productos[codigo]['producto']}:",
                                             minvalue=1)
            if cantidad:
                self.productos[codigo]['stock'] += cantidad
                self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.actualizar_tabla()
                self.guardar_datos()
                self.deseleccionar_producto()
                self.status_var.set(f"Stock actualizado: +{cantidad} unidades")
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def dar_baja_stock(self):
        """Da de baja stock a un producto"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            cantidad = simpledialog.askinteger("Dar de Baja", 
                                             f"Cantidad a quitar del stock de {self.productos[codigo]['producto']}:",
                                             minvalue=1, maxvalue=self.productos[codigo]['stock'])
            if cantidad:
                self.productos[codigo]['stock'] -= cantidad
                self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.actualizar_tabla()
                self.guardar_datos()
                self.deseleccionar_producto()
                self.status_var.set(f"Stock actualizado: -{cantidad} unidades")
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def sumar_una_unidad(self):
        """Suma una unidad al stock del producto seleccionado"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            stock_anterior = self.productos[codigo]['stock']
            stock_nuevo = stock_anterior + 1
            
            # Mostrar confirmación
            if self.mostrar_confirmacion_stock(codigo, stock_anterior, stock_nuevo, "+1"):
                # Aplicar cambio
                self.productos[codigo]['stock'] = stock_nuevo
                self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.actualizar_tabla()
                self.guardar_datos()
                self.deseleccionar_producto()
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def restar_una_unidad(self):
        """Resta una unidad al stock del producto seleccionado"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            if self.productos[codigo]['stock'] > 0:
                stock_anterior = self.productos[codigo]['stock']
                stock_nuevo = stock_anterior - 1
                
                # Mostrar confirmación
                if self.mostrar_confirmacion_stock(codigo, stock_anterior, stock_nuevo, "-1"):
                    # Aplicar cambio
                    self.productos[codigo]['stock'] = stock_nuevo
                    self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    self.actualizar_tabla()
                    self.guardar_datos()
                    self.deseleccionar_producto()
            else:
                messagebox.showwarning("Advertencia", f"No hay stock disponible de {self.productos[codigo]['producto']}")
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def mostrar_confirmacion_stock(self, codigo, stock_anterior, stock_nuevo, operacion):
        """Muestra una ventana de confirmación para cambios de stock"""
        producto = self.productos[codigo]['producto']
        
        # Crear ventana de confirmación
        ventana_confirmacion = tk.Toplevel(self.root)
        ventana_confirmacion.title("Confirmar Cambio de Stock")
        ventana_confirmacion.geometry("400x250")
        ventana_confirmacion.resizable(False, False)
        
        # Centrar la ventana
        ventana_confirmacion.transient(self.root)
        ventana_confirmacion.grab_set()
        
        # Contenido
        ttk.Label(ventana_confirmacion, text="¿Deseas confirmar esta acción?", 
                 font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        
        ttk.Label(ventana_confirmacion, text=f"Producto: {producto}", 
                 font=('Arial', 10, 'bold')).pack(pady=5)
        
        ttk.Label(ventana_confirmacion, text=f"Operación: {operacion}", 
                 font=('Arial', 10)).pack(pady=5)
        
        ttk.Label(ventana_confirmacion, text=f"Stock anterior: {stock_anterior}", 
                 font=('Arial', 10)).pack(pady=5)
        
        ttk.Label(ventana_confirmacion, text=f"Stock actualizado: {stock_nuevo}", 
                 font=('Arial', 10, 'bold'), foreground='green').pack(pady=5)
        
        # Variable para el resultado
        resultado = tk.BooleanVar()
        
        # Botones
        btn_frame = ttk.Frame(ventana_confirmacion)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="✅ Confirmar", 
                  command=lambda: [resultado.set(True), ventana_confirmacion.destroy()]).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=lambda: [resultado.set(False), ventana_confirmacion.destroy()]).pack(side=tk.LEFT, padx=10)
        
        # Esperar a que se cierre la ventana
        ventana_confirmacion.wait_window()
        
        return resultado.get()
    
    def deseleccionar_producto(self):
        """Deselecciona el producto actual y limpia la información"""
        # Limpiar información del producto
        self.limpiar_info_producto()
        
        # Deseleccionar en la tabla
        self.tabla.selection_remove(self.tabla.selection())
        
        # Limpiar campo de código
        self.codigo_actual.set("")
        
        # Actualizar status
        self.status_var.set(f"{self.status_google_sheets} | Listo para escanear")
        
        # Volver el foco al campo de código
        self.entry_codigo.focus()
    
    def resaltar_producto_en_tabla(self, codigo):
        """Resalta el producto en la tabla"""
        # Limpiar selección previa
        self.tabla.selection_remove(self.tabla.selection())
        
        # Buscar y seleccionar el producto
        for item in self.tabla.get_children():
            if self.tabla.item(item)['values'][0] == codigo:
                self.tabla.selection_add(item)
                self.tabla.see(item)  # Hacer visible el item
                break
    
    def preguntar_agregar_producto(self, codigo):
        """Pregunta si agregar un producto nuevo de forma menos intrusiva"""
        # Crear una ventana pequeña y no modal
        ventana_agregar = tk.Toplevel(self.root)
        ventana_agregar.title("Producto Nuevo")
        ventana_agregar.geometry("300x150")
        ventana_agregar.resizable(False, False)
        
        # Centrar la ventana
        ventana_agregar.transient(self.root)
        ventana_agregar.grab_set()
        
        # Contenido
        ttk.Label(ventana_agregar, text=f"El código {codigo} no existe", 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        ttk.Label(ventana_agregar, text="¿Desea agregarlo como nuevo producto?").pack(pady=5)
        
        # Botones
        btn_frame = ttk.Frame(ventana_agregar)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Sí, Agregar", 
                  command=lambda: [self.agregar_producto_nuevo(codigo), ventana_agregar.destroy()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="No", 
                  command=ventana_agregar.destroy).pack(side=tk.LEFT, padx=5)
        
                    # Auto-cerrar después de 10 segundos
        ventana_agregar.after(10000, ventana_agregar.destroy)
    
    def on_key_release(self, event):
        """Maneja la liberación de teclas para detectar escaneos automáticos"""
        codigo = self.codigo_actual.get().strip()
        
        # Si se presiona Enter, no hacer nada (ya se maneja en procesar_codigo)
        if event.keysym == 'Return':
            return
        
        # Si hay un código y tiene una longitud típica de código de barras (8-13 dígitos)
        if codigo and len(codigo) >= 8 and len(codigo) <= 13:
            # Verificar si es un código de barras válido (solo números)
            if codigo.isdigit():
                # Pequeño delay para asegurar que el escaneo esté completo
                self.root.after(200, self.verificar_y_procesar_codigo)
            else:
                # Código con letras, probablemente escritura manual
                self.status_var.set(f"{self.status_google_sheets} | Escribiendo código...")
        else:
            # Actualizar estado para escritura manual
            if codigo:
                self.status_var.set(f"{self.status_google_sheets} | Escribiendo código...")
            else:
                self.status_var.set(f"{self.status_google_sheets} | Listo para escanear")
    
    def verificar_y_procesar_codigo(self):
        """Verifica si el código actual es válido y lo procesa automáticamente"""
        codigo = self.codigo_actual.get().strip()
        
        # Solo procesar si el código sigue siendo válido
        if codigo and len(codigo) >= 8 and len(codigo) <= 13 and codigo.isdigit():
            # Verificar si el código existe en la base de datos
            if codigo in self.productos:
                # Procesar automáticamente
                self.procesar_codigo()
            else:
                # Código no encontrado, pero mantenerlo para que el usuario pueda presionar Enter
                self.status_var.set(f"{self.status_google_sheets} | ❌ Código no encontrado: {codigo}")
    
    def seleccionar_producto(self, event):
        """Maneja la selección de un producto en la tabla"""
        selection = self.tabla.selection()
        if selection:
            item = self.tabla.item(selection[0])
            codigo = item['values'][0]
            if codigo in self.productos:
                self.mostrar_producto(self.productos[codigo])
    
    def actualizar_tabla(self):
        """Actualiza la tabla de productos"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Agregar productos
        for producto in self.productos.values():
            self.tabla.insert('', 'end', values=(
                producto['codigo'],
                producto['producto'],
                producto['stock'],
                producto['stock_minimo'],
                f"${producto['precio']:.2f}",
                producto['ultima_actualizacion']
            ))
    
    def mostrar_reporte(self):
        """Muestra un reporte del inventario"""
        if not self.productos:
            messagebox.showinfo("Reporte", "No hay productos en el inventario")
            return
        
        # Calcular estadísticas
        total_productos = len(self.productos)
        stock_bajo = sum(1 for p in self.productos.values() if p['stock'] <= p['stock_minimo'])
        valor_total = sum(p['stock'] * p['precio'] for p in self.productos.values())
        
        reporte = f"""REPORTE DE INVENTARIO
        ========================
        
        Total de productos: {total_productos}
        Productos con stock bajo: {stock_bajo}
        Valor total del inventario: ${valor_total:.2f}
        
        Productos con stock bajo:
        """
        
        for producto in self.productos.values():
            if producto['stock'] <= producto['stock_minimo']:
                reporte += f"\n• {producto['producto']} (Stock: {producto['stock']}, Mínimo: {producto['stock_minimo']})"
        
        # Crear ventana de reporte
        ventana_reporte = tk.Toplevel(self.root)
        ventana_reporte.title("Reporte de Inventario")
        ventana_reporte.geometry("500x400")
        
        text_widget = tk.Text(ventana_reporte, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, reporte)
        text_widget.config(state=tk.DISABLED)
    
    def cargar_datos(self):
        """Carga los datos desde Google Sheets o archivo local"""
        if self.gc and self.worksheet:
            try:
                # Cargar desde Google Sheets
                datos = self.worksheet.get_all_records()
                for fila in datos:
                    if fila['Código']:  # Ignorar filas vacías
                        self.productos[fila['Código']] = {
                            'codigo': fila['Código'],
                            'producto': fila['Producto'],
                            'stock': int(fila['Stock Actual']),
                            'stock_minimo': int(fila['Stock Mínimo']),
                            'precio': float(fila['Precio']),
                            'ultima_actualizacion': fila['Última Actualización']
                        }
                self.status_var.set(f"Datos cargados desde Google Sheets: {len(self.productos)} productos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
        else:
            # Cargar desde archivo local
            try:
                if os.path.exists('stock_local.json'):
                    with open('stock_local.json', 'r', encoding='utf-8') as f:
                        self.productos = json.load(f)
                    self.status_var.set(f"Datos cargados localmente: {len(self.productos)} productos")
            except Exception as e:
                self.status_var.set("No se encontraron datos previos")
        
        self.actualizar_tabla()
    
    def guardar_datos(self):
        """Guarda los datos en Google Sheets o archivo local"""
        if self.gc and self.worksheet:
            try:
                # Limpiar hoja
                self.worksheet.clear()
                
                # Agregar encabezados
                headers = ['Código', 'Producto', 'Stock Actual', 'Stock Mínimo', 'Última Actualización', 'Precio']
                self.worksheet.append_row(headers)
                
                # Agregar datos
                for producto in self.productos.values():
                    self.worksheet.append_row([
                        producto['codigo'],
                        producto['producto'],
                        producto['stock'],
                        producto['stock_minimo'],
                        producto['ultima_actualizacion'],
                        producto['precio']
                    ])
                
                self.status_var.set("Datos guardados en Google Sheets")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar en Google Sheets: {str(e)}")
        else:
            # Guardar en archivo local
            try:
                with open('stock_local.json', 'w', encoding='utf-8') as f:
                    json.dump(self.productos, f, ensure_ascii=False, indent=2)
                self.status_var.set("Datos guardados localmente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SistemaControlStock()
    app.ejecutar()
