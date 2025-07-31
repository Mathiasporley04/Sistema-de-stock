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
        
        # Variables para configuración de Google Sheets
        self.google_sheet_id = None  # ID de la hoja específica
        self.google_sheet_url = None  # URL de la hoja
        
        # Variables para caché de credenciales
        self.credentials_cache_file = 'google_credentials_cache.json'
        self.cached_credentials = None
        
        # Variables para caché de hoja conectada
        self.sheet_cache_file = 'google_sheet_cache.json'
        self.cached_sheet_id = None
        
        # Variables
        self.productos = {}
        self.codigo_actual = tk.StringVar()
        self.status_google_sheets = "⏳ Configurando..."
        
        # Sistema de defensa - modo de edición
        self.modo_edicion_activo = False
        self.producto_en_edicion = None
        self.stock_anterior = None
        
        self.cargar_credenciales_cache()
        self.cargar_hoja_cache()
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
            
            # Verificar si hay credenciales en caché
            if self.cached_credentials:
                try:
                    # Crear credenciales desde el caché
                    creds = Credentials.from_service_account_info(self.cached_credentials, scopes=scope)
                    self.gc = gspread.authorize(creds)
                    
                    # Intentar conectar con hoja en caché primero
                    if self.cached_sheet_id:
                        try:
                            self.google_sheet_id = self.cached_sheet_id
                            self.worksheet = self.gc.open_by_key(self.google_sheet_id).sheet1
                            self.status_google_sheets = "✅ Google Sheets conectado"
                            self.actualizar_estado_google_sheets()
                            return
                        except Exception as e:
                            print(f"Error abriendo hoja en caché: {e}")
                            # Si falla, limpiar caché de hoja
                            self.limpiar_hoja_cache()
                    
                    # Si no hay hoja en caché, solo configurar para lectura
                    self.status_google_sheets = "⚠️ Configurado (conecta una hoja)"
                    self.actualizar_estado_google_sheets()
                    return
                    
                except Exception as e:
                    print(f"Error con credenciales en caché: {e}")
                    # Si falla, limpiar caché y continuar
                    self.cached_credentials = None
                    if os.path.exists(self.credentials_cache_file):
                        os.remove(self.credentials_cache_file)
            
            # Verificar si existe el archivo de credenciales (método anterior)
            if os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                self.gc = gspread.authorize(creds)
                
                # Solo intentar abrir hojas existentes
                if hasattr(self, 'google_sheet_id') and self.google_sheet_id:
                    try:
                        self.worksheet = self.gc.open_by_key(self.google_sheet_id).sheet1
                        self.status_google_sheets = "✅ Google Sheets conectado"
                    except Exception as e:
                        self.status_google_sheets = "⚠️ Configurado (conecta una hoja)"
                else:
                    self.status_google_sheets = "⚠️ Configurado (conecta una hoja)"
                
                self.actualizar_estado_google_sheets()
            else:
                # No hay credenciales, configurar para modo local
                self.status_google_sheets = "⚠️ Modo local (sin Google Sheets)"
                self.gc = None
                self.actualizar_estado_google_sheets()
                
        except Exception as e:
            # Mostrar error
            self.status_google_sheets = f"❌ Error Google Sheets: {str(e)[:50]}..."
            self.gc = None
    
    def intentar_solucion_alternativa(self):
        """Intenta una solución alternativa para problemas de límites"""
        try:
            if not self.cached_credentials and not os.path.exists('credentials.json'):
                return False, "No hay credenciales disponibles"
            
            # Usar credenciales disponibles
            if self.cached_credentials:
                scope = ['https://spreadsheets.google.com/feeds']
                creds = Credentials.from_service_account_info(self.cached_credentials, scopes=scope)
            else:
                scope = ['https://spreadsheets.google.com/feeds']
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            
            gc_temp = gspread.authorize(creds)
            
            # Intentar solo leer (sin crear archivos)
            if hasattr(self, 'google_sheet_id') and self.google_sheet_id:
                worksheet = gc_temp.open_by_key(self.google_sheet_id).sheet1
                return True, "Modo solo lectura funcionando"
            else:
                return False, "Necesitas conectar una hoja específica primero"
                
        except Exception as e:
            return False, f"Error en solución alternativa: {str(e)}"
    
    def configurar_hoja_especifica(self, sheet_id=None, sheet_url=None):
        """Configura una hoja específica de Google Sheets"""
        if sheet_id:
            self.google_sheet_id = sheet_id
        elif sheet_url:
            # Extraer ID de la URL
            try:
                # Formato: https://docs.google.com/spreadsheets/d/SHEET_ID/edit
                self.google_sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            except:
                messagebox.showerror("Error", "URL de Google Sheets inválida")
                return False
        
        if self.google_sheet_id and self.gc:
            try:
                # SOLO abrir la hoja existente, NUNCA crear una nueva
                self.worksheet = self.gc.open_by_key(self.google_sheet_id).sheet1
                self.status_google_sheets = "✅ Hoja específica conectada"
                
                # Guardar hoja en caché
                self.guardar_hoja_cache(self.google_sheet_id)
                
                # Actualizar estado visual
                self.actualizar_estado_google_sheets()
                return True
            except gspread.SpreadsheetNotFound:
                messagebox.showerror("Error", "La hoja no existe o no tienes permisos para acceder a ella.\n\nAsegúrate de:\n1. Que la hoja exista\n2. Que esté compartida con tu cuenta de servicio\n3. Que tengas permisos de Editor")
                return False
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la hoja: {str(e)}")
                return False
        return False
    
    def cargar_credenciales_cache(self):
        """Carga las credenciales desde el caché interno"""
        try:
            if os.path.exists(self.credentials_cache_file):
                with open(self.credentials_cache_file, 'r') as f:
                    self.cached_credentials = json.load(f)
                return True
        except Exception as e:
            print(f"Error al cargar credenciales del caché: {e}")
        return False
    
    def guardar_credenciales_cache(self, credentials_data):
        """Guarda las credenciales en el caché interno"""
        try:
            with open(self.credentials_cache_file, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            self.cached_credentials = credentials_data
            return True
        except Exception as e:
            print(f"Error al guardar credenciales en caché: {e}")
            return False
    
    def solicitar_credenciales(self):
        """Solicita al usuario que seleccione el archivo de credenciales"""
        try:
            from tkinter import filedialog
            
            # Abrir diálogo para seleccionar archivo
            filename = filedialog.askopenfilename(
                title="Seleccionar archivo de credenciales de Google",
                filetypes=[
                    ("Archivos JSON", "*.json"),
                    ("Todos los archivos", "*.*")
                ],
                initialdir=os.getcwd()
            )
            
            if not filename:
                return False  # Usuario canceló
            
            # Leer y validar el archivo
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    credenciales = json.load(f)
                
                # Verificar formato básico
                if 'type' not in credenciales or credenciales['type'] != 'service_account':
                    messagebox.showerror("Error", "Formato de credenciales incorrecto.\n\nEl archivo debe ser de una cuenta de servicio de Google Cloud.")
                    return False
                
                if 'client_email' not in credenciales:
                    messagebox.showerror("Error", "Credenciales incompletas.\n\nFalta el campo 'client_email' en el archivo.")
                    return False
                
                # Guardar en caché
                if self.guardar_credenciales_cache(credenciales):
                    messagebox.showinfo("Éxito", 
                                      f"✅ Credenciales guardadas correctamente en caché interno\n\n"
                                      f"Cuenta de servicio: {credenciales['client_email']}\n"
                                      f"Proyecto: {credenciales.get('project_id', 'N/A')}")
                    return True
                else:
                    messagebox.showerror("Error", "No se pudieron guardar las credenciales en caché")
                    return False
                    
            except json.JSONDecodeError:
                messagebox.showerror("Error", "El archivo seleccionado no es un JSON válido.\n\nVerifica que sea el archivo correcto de credenciales de Google Cloud.")
                return False
            except UnicodeDecodeError:
                messagebox.showerror("Error", "Error al leer el archivo.\n\nVerifica que el archivo no esté corrupto.")
                return False
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado al procesar el archivo:\n{str(e)}")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el selector de archivos:\n{str(e)}")
            return False
    
    def limpiar_credenciales_cache(self):
        """Limpia las credenciales del caché"""
        try:
            if os.path.exists(self.credentials_cache_file):
                os.remove(self.credentials_cache_file)
            self.cached_credentials = None
            return True
        except Exception as e:
            print(f"Error al limpiar credenciales: {e}")
            return False
    
    def cargar_hoja_cache(self):
        """Carga la hoja conectada desde el caché interno"""
        try:
            if os.path.exists(self.sheet_cache_file):
                with open(self.sheet_cache_file, 'r') as f:
                    sheet_data = json.load(f)
                    self.cached_sheet_id = sheet_data.get('sheet_id')
                    print(f"Hoja cargada desde caché: {self.cached_sheet_id}")
            else:
                self.cached_sheet_id = None
        except Exception as e:
            print(f"Error cargando hoja desde caché: {e}")
            self.cached_sheet_id = None
    
    def guardar_hoja_cache(self, sheet_id):
        """Guarda la hoja conectada en el caché interno"""
        try:
            from datetime import datetime
            sheet_data = {
                'sheet_id': sheet_id,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.sheet_cache_file, 'w') as f:
                json.dump(sheet_data, f, indent=2)
            self.cached_sheet_id = sheet_id
            print(f"Hoja guardada en caché: {sheet_id}")
        except Exception as e:
            print(f"Error guardando hoja en caché: {e}")
    
    def limpiar_hoja_cache(self):
        """Limpia el caché de la hoja conectada"""
        try:
            if os.path.exists(self.sheet_cache_file):
                os.remove(self.sheet_cache_file)
            self.cached_sheet_id = None
            print("Caché de hoja limpiado")
        except Exception as e:
            print(f"Error limpiando caché de hoja: {e}")
    
    def mostrar_menu_credenciales(self, event):
        """Muestra menú contextual para las credenciales"""
        menu = tk.Menu(self.root, tearoff=0)
        
        if self.cached_credentials:
            menu.add_command(label="📧 Ver cuenta configurada", 
                           command=lambda: self.mostrar_info_credenciales())
            menu.add_separator()
            menu.add_command(label="🗑️ Limpiar credenciales", 
                           command=self.limpiar_credenciales_y_reiniciar)
        else:
            menu.add_command(label="🔑 Configurar credenciales", 
                           command=self.abrir_configurador_google_sheets)
        
        # Agregar información de hoja si está conectada
        if self.cached_sheet_id:
            menu.add_separator()
            menu.add_command(label="📊 Ver hoja conectada", 
                           command=lambda: self.mostrar_info_hoja())
            menu.add_command(label="🗑️ Limpiar hoja", 
                           command=self.limpiar_hoja_cache)
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def mostrar_info_credenciales(self):
        """Muestra información de las credenciales configuradas"""
        if self.cached_credentials:
            info = f"Cuenta de servicio: {self.cached_credentials['client_email']}\n"
            info += f"Proyecto: {self.cached_credentials.get('project_id', 'N/A')}\n"
            info += f"Tipo: {self.cached_credentials.get('type', 'N/A')}"
            
            messagebox.showinfo("Credenciales Configuradas", info)
    
    def mostrar_info_hoja(self):
        """Muestra información de la hoja conectada"""
        if self.cached_sheet_id:
            try:
                # Intentar obtener nombre de la hoja
                nombre_hoja = "Hoja conectada"
                if self.gc and self.worksheet:
                    nombre_hoja = self.worksheet.title
                
                info = f"📊 Nombre: {nombre_hoja}\n"
                info += f"🔗 ID: {self.cached_sheet_id}\n"
                info += f"✅ Estado: Conectada"
                messagebox.showinfo("Información de Hoja", info)
            except:
                info = f"🔗 ID: {self.cached_sheet_id}\n"
                info += f"⚠️ Estado: En caché (no conectada)"
                messagebox.showinfo("Información de Hoja", info)
        else:
            messagebox.showinfo("Información de Hoja", "No hay hoja conectada")
    
    def limpiar_credenciales_y_reiniciar(self):
        """Limpia las credenciales y reinicia la configuración"""
        if messagebox.askyesno("Limpiar Credenciales", 
                              "¿Estás seguro de que quieres limpiar las credenciales?\n\n"
                              "Esto desconectará Google Sheets hasta que configures nuevas credenciales."):
            if self.limpiar_credenciales_cache():
                self.setup_google_sheets()
                self.actualizar_estado_google_sheets()
                messagebox.showinfo("Éxito", "Credenciales limpiadas correctamente")
    
    def actualizar_estado_google_sheets(self):
        """Actualiza el ícono de estado de Google Sheets"""
        if hasattr(self, 'gs_status_label'):
            if self.gc and self.worksheet:
                self.gs_status_label.config(text="✅", foreground="green")
                self.crear_tooltip(self.gs_status_label, "Google Sheets conectado y funcionando")
            elif self.gc:
                self.gs_status_label.config(text="⚠️", foreground="orange")
                self.crear_tooltip(self.gs_status_label, "Google Sheets configurado pero no conectado a una hoja específica")
            else:
                self.gs_status_label.config(text="❌", foreground="red")
                self.crear_tooltip(self.gs_status_label, "Google Sheets no configurado. Haz clic en el botón para configurar")
    
    def crear_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                           font=("Arial", "8", "normal"))
            label.pack()
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', hide_tooltip)
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def abrir_configurador_google_sheets(self):
        """Abre el configurador de Google Sheets"""
        self.abrir_configurador()
    
    def abrir_configurador(self):
        """Configura Google Sheets seleccionando archivo de credenciales"""
        try:
            # Verificar si ya hay credenciales en caché
            if self.cached_credentials:
                respuesta = messagebox.askyesno("Google Sheets", 
                                              "Ya tienes credenciales configuradas.\n\n"
                                              "¿Quieres configurar nuevas credenciales?")
                if not respuesta:
                    return
            
            # Solicitar archivo de credenciales
            if self.solicitar_credenciales():
                # Reconfigurar Google Sheets con las nuevas credenciales
                self.setup_google_sheets()
                self.actualizar_estado_google_sheets()
                messagebox.showinfo("Éxito", "Google Sheets configurado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la configuración: {str(e)}")
    
    def abrir_hoja_google_sheets(self):
        """Abre la hoja de Google Sheets directamente en el navegador"""
        if self.google_sheet_id:
            try:
                import webbrowser
                sheet_url = f"https://docs.google.com/spreadsheets/d/{self.google_sheet_id}/edit"
                webbrowser.open(sheet_url)
                messagebox.showinfo("Éxito", "Hoja de Google Sheets abierta en tu navegador")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la hoja: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "No hay una hoja configurada. Configura Google Sheets primero.")
    
    def verificar_cambios_google_sheets(self):
        """Verifica si hay cambios en la configuración de Google Sheets"""
        try:
            # Ejecutar diagnóstico completo
            resultado = self.diagnosticar_google_sheets()
            
            # Mostrar resultado detallado
            self.mostrar_diagnostico(resultado)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar configuración: {str(e)}")
    
    def activar_solucion_alternativa(self):
        """Activa la solución alternativa para problemas de límites"""
        try:
            exito, mensaje = self.intentar_solucion_alternativa()
            if exito:
                messagebox.showinfo("Solución Alternativa", 
                                  f"✅ {mensaje}\n\nEl sistema ahora funciona en modo solo lectura.\n"
                                  "Puedes leer datos de Google Sheets pero no crear archivos nuevos.")
                self.status_google_sheets = "⚠️ Modo solo lectura"
                self.actualizar_estado_google_sheets()
            else:
                messagebox.showerror("Error", f"❌ No se pudo activar la solución alternativa:\n{mensaje}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al activar solución alternativa: {str(e)}")
    
    def diagnosticar_google_sheets(self):
        """Ejecuta un diagnóstico completo de Google Sheets"""
        diagnostico = {
            'credenciales_cache': False,
            'archivo_credenciales': False,
            'formato_credenciales': False,
            'api_habilitada': False,
            'conexion_google': False,
            'limites_ok': False,
            'hoja_compartida': False,
            'errores': []
        }
        
        # 1. Verificar credenciales en caché
        if self.cached_credentials:
            diagnostico['credenciales_cache'] = True
            diagnostico['formato_credenciales'] = True
        
        # 2. Verificar archivo credentials.json (método anterior)
        try:
            # Obtener ruta actual
            ruta_actual = os.getcwd()
            ruta_archivo = os.path.join(ruta_actual, 'credentials.json')
            
            # Verificar en directorio actual
            if not diagnostico['credenciales_cache'] and os.path.exists('credentials.json'):
                diagnostico['archivo_credenciales'] = True
                diagnostico['ruta_archivo'] = ruta_archivo
            # Verificar en directorio del script
            elif os.path.exists(os.path.join(os.path.dirname(__file__), 'credentials.json')):
                diagnostico['archivo_credenciales'] = True
                diagnostico['ruta_archivo'] = os.path.join(os.path.dirname(__file__), 'credentials.json')
                diagnostico['errores'].append("Archivo encontrado en directorio del script, pero no en directorio actual")
                
                # Verificar formato del archivo
                if not diagnostico['formato_credenciales']:
                    with open('credentials.json', 'r') as f:
                        creds = json.load(f)
                    
                    if 'type' in creds and creds['type'] == 'service_account':
                        diagnostico['formato_credenciales'] = True
                    else:
                        diagnostico['errores'].append("Formato de credenciales incorrecto")
                    
            else:
                diagnostico['errores'].append(f"Archivo credentials.json no encontrado")
                diagnostico['errores'].append(f"Buscando en: {ruta_archivo}")
                diagnostico['errores'].append(f"Directorio actual: {ruta_actual}")
        except json.JSONDecodeError:
            diagnostico['errores'].append("Error al leer credentials.json (formato JSON inválido)")
        except Exception as e:
            diagnostico['errores'].append(f"Error al verificar credenciales: {str(e)}")
        
        # 3. Verificar información de la cuenta de servicio
        if diagnostico['formato_credenciales']:
            # Verificar si las credenciales son del proyecto correcto
            if self.cached_credentials:
                diagnostico['info_cuenta'] = {
                    'email': self.cached_credentials.get('client_email', 'N/A'),
                    'project_id': self.cached_credentials.get('project_id', 'N/A'),
                    'type': self.cached_credentials.get('type', 'N/A')
                }
            elif os.path.exists('credentials.json'):
                try:
                    with open('credentials.json', 'r') as f:
                        creds = json.load(f)
                    diagnostico['info_cuenta'] = {
                        'email': creds.get('client_email', 'N/A'),
                        'project_id': creds.get('project_id', 'N/A'),
                        'type': creds.get('type', 'N/A')
                    }
                except:
                    pass
        
        # 4. Verificar conexión con Google
        if diagnostico['formato_credenciales']:
            try:
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
                gc_temp = gspread.authorize(creds)
                diagnostico['conexion_google'] = True
                
                # 3. Verificar API habilitada
                try:
                    # Intentar listar hojas (esto verifica si la API está habilitada)
                    gc_temp.list_spreadsheet_files()
                    diagnostico['api_habilitada'] = True
                except Exception as e:
                    error_msg = str(e)
                    if "API not enabled" in error_msg or "403" in error_msg:
                        if "drive.googleapis.com" in error_msg:
                            diagnostico['errores'].append("API de Google Drive no habilitada")
                        elif "sheets.googleapis.com" in error_msg:
                            diagnostico['errores'].append("API de Google Sheets no habilitada")
                        else:
                            diagnostico['errores'].append("API de Google no habilitada")
                    elif "quota" in error_msg.lower() or "storage" in error_msg.lower():
                        diagnostico['errores'].append("Problema de cuota o límites de Google Drive")
                        diagnostico['errores'].append("Detalles: " + error_msg)
                    else:
                        diagnostico['errores'].append(f"Error al verificar API: {error_msg}")
                
                # 4. Verificar límites de Google Drive
                try:
                    # Solo verificar que podemos listar hojas (sin crear nada)
                    gc_temp.list_spreadsheet_files()
                    diagnostico['limites_ok'] = True
                except Exception as e:
                    error_msg = str(e)
                    if "quota" in error_msg.lower() or "storage" in error_msg.lower():
                        diagnostico['errores'].append("🚨 PROBLEMA DE LÍMITES DETECTADO")
                        diagnostico['errores'].append("Google Drive tiene restricciones que impiden crear archivos")
                        diagnostico['errores'].append("Error específico: " + error_msg)
                        diagnostico['limites_ok'] = False
                        
                        # Intentar solución alternativa: usar solo lectura
                        try:
                            diagnostico['errores'].append("🔄 Intentando solución alternativa...")
                            # Intentar solo leer una hoja existente
                            if hasattr(self, 'google_sheet_id') and self.google_sheet_id:
                                worksheet_temp = gc_temp.open_by_key(self.google_sheet_id).sheet1
                                diagnostico['solucion_alternativa'] = True
                                diagnostico['errores'].append("✅ Solución alternativa: Modo solo lectura funcionando")
                            else:
                                diagnostico['errores'].append("⚠️ Para usar modo solo lectura, necesitas conectar una hoja específica")
                        except Exception as e2:
                            diagnostico['errores'].append(f"❌ Solución alternativa falló: {str(e2)}")
                    else:
                        diagnostico['errores'].append(f"Error al verificar límites: {error_msg}")
                
                # 5. Verificar hoja compartida (si hay una configurada)
                if hasattr(self, 'google_sheet_id') and self.google_sheet_id:
                    try:
                        worksheet_temp = gc_temp.open_by_key(self.google_sheet_id).sheet1
                        diagnostico['hoja_compartida'] = True
                    except Exception as e:
                        if "404" in str(e):
                            diagnostico['errores'].append("Hoja no encontrada o no compartida")
                        else:
                            diagnostico['errores'].append(f"Error al acceder a la hoja: {str(e)}")
                
            except Exception as e:
                diagnostico['errores'].append(f"Error de conexión con Google: {str(e)}")
        
        return diagnostico
    
    def mostrar_diagnostico(self, diagnostico):
        """Muestra el resultado del diagnóstico en una ventana detallada"""
        # Crear ventana de diagnóstico
        ventana_diagnostico = tk.Toplevel(self.root)
        ventana_diagnostico.title("Diagnóstico de Google Sheets")
        ventana_diagnostico.geometry("500x400")
        ventana_diagnostico.resizable(False, False)
        
        # Centrar ventana
        ventana_diagnostico.transient(self.root)
        ventana_diagnostico.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(ventana_diagnostico, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="🔍 DIAGNÓSTICO DE GOOGLE SHEETS", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Crear texto con scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generar reporte
        reporte = "ESTADO DE LA CONFIGURACIÓN:\n"
        reporte += "=" * 40 + "\n\n"
        
        # Verificar cada componente
        checks = [
            ("💾 Credenciales en caché", diagnostico['credenciales_cache']),
            ("📄 Archivo credentials.json", diagnostico['archivo_credenciales']),
            ("🔧 Formato de credenciales", diagnostico['formato_credenciales']),
            ("🌐 Conexión con Google", diagnostico['conexion_google']),
            ("⚙️ API habilitada", diagnostico['api_habilitada']),
            ("📊 Límites de Drive", diagnostico.get('limites_ok', False)),
            ("📊 Hoja compartida", diagnostico['hoja_compartida'])
        ]
        
        for check, status in checks:
            icono = "✅" if status else "❌"
            reporte += f"{icono} {check}\n"
        
        # Mostrar información de la cuenta si está disponible
        if 'info_cuenta' in diagnostico:
            reporte += "\n📧 INFORMACIÓN DE LA CUENTA:\n"
            reporte += "=" * 30 + "\n"
            reporte += f"Email: {diagnostico['info_cuenta']['email']}\n"
            reporte += f"Proyecto: {diagnostico['info_cuenta']['project_id']}\n"
            reporte += f"Tipo: {diagnostico['info_cuenta']['type']}\n"
        
        # Mostrar errores si los hay
        if diagnostico['errores']:
            reporte += "\n🚨 ERRORES ENCONTRADOS:\n"
            reporte += "=" * 30 + "\n"
            for error in diagnostico['errores']:
                reporte += f"• {error}\n"
        
        # Mostrar recomendaciones
        reporte += "\n💡 RECOMENDACIONES:\n"
        reporte += "=" * 25 + "\n"
        
        if not diagnostico['credenciales_cache'] and not diagnostico['archivo_credenciales']:
            reporte += "• Usa el nuevo sistema de caché interno (más seguro)\n"
            reporte += "• O crea el archivo credentials.json en la carpeta del proyecto\n"
        
        if not diagnostico['formato_credenciales']:
            reporte += "• Verifica que las credenciales tengan el formato correcto\n"
        
        if not diagnostico['api_habilitada']:
            reporte += "• Habilita la API de Google Sheets en Google Cloud Console\n"
        
        if not diagnostico.get('limites_ok', True):
            reporte += "• 🚨 PROBLEMA DE LÍMITES: Google Drive tiene restricciones\n"
            reporte += "• Soluciones posibles:\n"
            reporte += "  - Verifica que la cuenta de servicio tenga permisos de Editor\n"
            reporte += "  - Intenta con una cuenta de Google diferente\n"
            reporte += "  - Contacta soporte de Google si el problema persiste\n"
        
        if not diagnostico['hoja_compartida']:
            if 'info_cuenta' in diagnostico:
                reporte += f"• Comparte tu hoja con: {diagnostico['info_cuenta']['email']}\n"
            else:
                reporte += "• Comparte tu hoja con la cuenta de servicio\n"
        
        if all([diagnostico['formato_credenciales'], 
                diagnostico['conexion_google'], diagnostico['api_habilitada'], 
                diagnostico.get('limites_ok', False)]):
            reporte += "• ¡Todo está configurado correctamente! Solo necesitas conectar una hoja específica\n"
        
        # Insertar reporte en el widget
        text_widget.insert(tk.END, reporte)
        text_widget.config(state=tk.DISABLED)
        
        # Botón para cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=ventana_diagnostico.destroy).pack(pady=(20, 0))
    
    def configurar_google_sheets_dialog(self):
        """Diálogo para configurar Google Sheets"""
        if not self.gc:
            messagebox.showerror("Error", "Google Sheets no está configurado. Ejecuta configurar_google_sheets.py primero.")
            return
        
        # Crear ventana de configuración
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Google Sheets")
        config_window.geometry("500x300")
        config_window.resizable(False, False)
        
        # Centrar ventana
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Configurar Google Sheets", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Instrucciones
        instrucciones = """
Para conectar con tu hoja de Google Sheets:

1. Abre tu hoja de Google Sheets
2. Copia la URL completa de la hoja
3. Pega la URL en el campo de abajo
4. Haz clic en "Conectar"

La hoja debe tener:
• Columna E: Códigos de productos
• Columna F: Stock correspondiente
        """
        
        ttk.Label(main_frame, text=instrucciones, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Campo para URL
        ttk.Label(main_frame, text="URL de Google Sheets:").pack(anchor=tk.W)
        url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=url_var, width=60)
        url_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        def conectar():
            url = url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Por favor ingresa la URL de Google Sheets")
                return
            
            if self.configurar_hoja_especifica(sheet_url=url):
                messagebox.showinfo("Éxito", "Google Sheets conectado correctamente")
                config_window.destroy()
                self.cargar_datos()  # Recargar datos
            else:
                messagebox.showerror("Error", "No se pudo conectar con la hoja")
        
        ttk.Button(btn_frame, text="Conectar", command=conectar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Cancelar", command=config_window.destroy).pack(side=tk.LEFT)
    
    def conectar_hoja_dialog(self):
        """Diálogo simplificado para conectar una hoja específica"""
        # Verificar si ya hay una hoja conectada
        if hasattr(self, 'google_sheet_id') and self.google_sheet_id:
            # Obtener nombre de la hoja si es posible
            nombre_hoja = "Hoja conectada"
            try:
                if self.gc and self.worksheet:
                    nombre_hoja = self.worksheet.title
            except:
                pass
            
            # Crear diálogo personalizado con más opciones
            dialog_opciones = tk.Toplevel(self.root)
            dialog_opciones.title("Hoja ya conectada")
            dialog_opciones.geometry("400x200")
            dialog_opciones.transient(self.root)
            dialog_opciones.grab_set()
            
            # Centrar diálogo
            dialog_opciones.update_idletasks()
            x = (dialog_opciones.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog_opciones.winfo_screenheight() // 2) - (200 // 2)
            dialog_opciones.geometry(f"400x200+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(dialog_opciones, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(main_frame, text="Hoja ya conectada", 
                     font=('Arial', 12, 'bold')).pack(pady=(0, 15))
            
            # Información de la hoja actual
            ttk.Label(main_frame, text=f"📊 {nombre_hoja}", 
                     font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
            ttk.Label(main_frame, text=f"🔗 {self.google_sheet_id}", 
                     font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 15))
            
            # Botones
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X)
            
            def conectar_nueva():
                dialog_opciones.destroy()
                self._mostrar_dialog_conectar()
            
            def desconectar_actual():
                self.google_sheet_id = None
                self.worksheet = None
                self.status_google_sheets = "⚠️ Configurado (sin hoja)"
                self.limpiar_hoja_cache()  # Limpiar caché de hoja
                self.actualizar_estado_google_sheets()
                dialog_opciones.destroy()
                messagebox.showinfo("Desconectado", "Hoja desconectada correctamente")
            
            ttk.Button(btn_frame, text="🔗 Conectar Nueva", 
                      command=conectar_nueva).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="❌ Desconectar", 
                      command=desconectar_actual).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="✋ Cancelar", 
                      command=dialog_opciones.destroy).pack(side=tk.LEFT)
            
            return
        
        # Si no hay hoja conectada, mostrar diálogo normal
        self._mostrar_dialog_conectar()
    
    def _mostrar_dialog_conectar(self):
        """Muestra el diálogo para conectar una hoja"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Conectar Hoja de Google Sheets")
        dialog.geometry("450x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"450x250+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="🔗 Conectar Hoja", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        # Instrucciones simples
        ttk.Label(main_frame, text="Pega la URL de tu hoja de Google Sheets:", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 10))
        
        # Campo de entrada
        url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=url_var, width=50)
        url_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Ejemplo de URL
        ttk.Label(main_frame, text="Ejemplo: https://docs.google.com/spreadsheets/d/1234567890abcdef/edit", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W, pady=(0, 20))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def conectar():
            url = url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Por favor ingresa la URL de Google Sheets")
                return
            
            # Mostrar indicador de carga
            conectar_btn.config(text="Conectando...", state='disabled')
            dialog.update()
            
            if self.configurar_hoja_especifica(sheet_url=url):
                dialog.destroy()
                messagebox.showinfo("✅ Conectado", "Hoja de Google Sheets conectada correctamente")
            else:
                conectar_btn.config(text="🔗 Conectar", state='normal')
                messagebox.showerror("❌ Error", "No se pudo conectar la hoja.\n\nVerifica:\n• Que la URL sea correcta\n• Que la hoja esté compartida con tu cuenta de servicio\n• Que tengas permisos de Editor")
        
        conectar_btn = ttk.Button(button_frame, text="🔗 Conectar", command=conectar)
        conectar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=dialog.destroy).pack(side=tk.LEFT)
        
        # Enfocar en el campo de entrada
        url_entry.focus()
        
        # Permitir Enter para conectar
        url_entry.bind('<Return>', lambda e: conectar())
    
    def sincronizar_con_google_sheets(self):
        """Sincroniza los cambios con Google Sheets"""
        if self.gc and self.worksheet:
            try:
                print(f"\n=== MÉTODO DIRECTO DE LECTURA ===")
                
                # Leer directamente todas las celdas
                datos_raw = self.worksheet.get_all_values()
                print(f"Filas totales en hoja: {len(datos_raw)}")
                
                if len(datos_raw) < 3:
                    print("❌ La hoja tiene menos de 3 filas")
                    return False
                
                # Mostrar todas las filas para debug
                print(f"Fila 1: {datos_raw[0]}")
                print(f"Fila 2: {datos_raw[1]}")
                if len(datos_raw) > 2:
                    print(f"Fila 3: {datos_raw[2]}")
                
                # Intentar con diferentes filas como encabezados
                headers = None
                fila_inicio_datos = None
                
                # Buscar la fila que tiene encabezados válidos
                for i, fila in enumerate(datos_raw):
                    if any('codigo' in str(celda).lower() or 'stock' in str(celda).lower() for celda in fila):
                        headers = fila
                        fila_inicio_datos = i + 1
                        print(f"Encabezados encontrados en fila {i+1}: {headers}")
                        break
                
                if headers is None:
                    print("❌ No se encontraron encabezados válidos")
                    return False
                
                # Buscar las columnas correctas
                columna_codigo = None
                columna_stock = None
                
                for i, header in enumerate(headers):
                    header_clean = str(header).strip().lower()
                    if 'codigo' in header_clean or 'código' in header_clean:
                        columna_codigo = i
                        print(f"Columna código encontrada en posición {i}: '{header}'")
                    elif header_clean == 'stock' and 'min' not in header_clean:
                        columna_stock = i
                        print(f"Columna stock encontrada en posición {i}: '{header}'")
                
                if columna_codigo is None:
                    print("❌ No se encontró columna de código")
                    return False
                
                if columna_stock is None:
                    print("❌ No se encontró columna de stock")
                    return False
                
                # Crear diccionario de códigos -> fila para búsqueda rápida
                codigos_por_fila = {}
                for i, fila in enumerate(datos_raw[fila_inicio_datos:], start=fila_inicio_datos+1):
                    if len(fila) > columna_codigo:
                        codigo_hoja = str(fila[columna_codigo]).strip()
                        if codigo_hoja:
                            codigos_por_fila[codigo_hoja] = i
                
                print(f"Índice de códigos creado: {len(codigos_por_fila)} productos en hoja")
                
                # Procesar solo productos que han cambiado
                productos_actualizados = 0
                productos_no_encontrados = 0
                productos_sin_cambios = 0
                
                print(f"\n=== INICIO SINCRONIZACIÓN ===")
                print(f"Productos en memoria: {len(self.productos)}")
                
                for codigo, producto in self.productos.items():
                    # Buscar directamente en el índice
                    if codigo in codigos_por_fila:
                        fila_numero = codigos_por_fila[codigo]
                        fila = datos_raw[fila_numero - 1]  # Ajustar índice
                        
                        if len(fila) > columna_stock:
                            stock_hoja = str(fila[columna_stock]).strip()
                            nuevo_stock = producto['stock']
                            
                            # Solo actualizar si el stock cambió
                            if stock_hoja != str(nuevo_stock):
                                print(f"Actualizando {codigo}: {stock_hoja} -> {nuevo_stock}")
                                
                                try:
                                    # Actualizar stock en la columna correcta
                                    columna_letra = chr(ord('A') + columna_stock)
                                    celda = f'{columna_letra}{fila_numero}'
                                    self.worksheet.update(celda, [[nuevo_stock]])
                                    productos_actualizados += 1
                                    print(f"  ✅ Stock actualizado: {codigo} -> {nuevo_stock}")
                                except Exception as e:
                                    print(f"  ❌ Error actualizando stock de {codigo}: {e}")
                                    # Intentar método alternativo
                                    try:
                                        print(f"  🔄 Intentando método alternativo...")
                                        self.worksheet.update_acell(celda, nuevo_stock)
                                        productos_actualizados += 1
                                        print(f"  ✅ Stock actualizado (método alternativo): {codigo} -> {nuevo_stock}")
                                    except Exception as e2:
                                        print(f"  ❌ Error método alternativo: {e2}")
                            else:
                                productos_sin_cambios += 1
                    else:
                        productos_no_encontrados += 1
                        print(f"  ❌ Producto no encontrado en hoja: {codigo}")
                
                print(f"\nResumen:")
                print(f"  Productos actualizados: {productos_actualizados}")
                print(f"  Productos sin cambios: {productos_sin_cambios}")
                print(f"  Productos no encontrados: {productos_no_encontrados}")
                
                print(f"\n=== FIN SINCRONIZACIÓN ===")
                print(f"Sincronización completada: {productos_actualizados} stocks actualizados, {productos_no_encontrados} no encontrados")
                return True
            except Exception as e:
                print(f"Error al sincronizar: {e}")
                messagebox.showerror("Error de Sincronización", f"No se pudo sincronizar con Google Sheets:\n{str(e)}")
                return False
        return False
    
    def limpiar_encabezados_duplicados(self):
        """Limpia encabezados duplicados en la hoja de Google Sheets"""
        if self.gc and self.worksheet:
            try:
                # Obtener la primera fila (encabezados)
                headers = self.worksheet.row_values(1)
                
                # Limpiar encabezados duplicados y vacíos
                headers_limpios = []
                headers_vistos = set()
                
                for header in headers:
                    if header and header.strip() and header.strip() not in headers_vistos:
                        headers_limpios.append(header.strip())
                        headers_vistos.add(header.strip())
                    else:
                        headers_limpios.append("")  # Columna vacía para mantener estructura
                
                # Actualizar la primera fila con encabezados limpios
                self.worksheet.update('A1:Z1', [headers_limpios])
                
                messagebox.showinfo("Éxito", "Encabezados duplicados limpiados correctamente")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Error al limpiar encabezados: {str(e)}")
                return False
        return False
    
    def sincronizar_manual(self):
        """Sincronización manual con Google Sheets"""
        if self.gc and self.worksheet:
            try:
                # Mostrar indicador de carga
                self.btn_sincronizar.config(text="Sincronizando...", state='disabled')
                self.root.update()
                
                # Debug: mostrar información
                print(f"Productos en memoria: {len(self.productos)}")
                for codigo, producto in self.productos.items():
                    print(f"  {codigo}: stock {producto['stock']}")
                
                # Ejecutar sincronización
                if self.sincronizar_con_google_sheets():
                    messagebox.showinfo("✅ Sincronizado", "Datos sincronizados correctamente con Google Sheets")
                else:
                    messagebox.showerror("❌ Error", "No se pudo sincronizar con Google Sheets")
                
                # Restaurar botón
                self.btn_sincronizar.config(text="🔄 Sync", state='normal')
            except Exception as e:
                self.btn_sincronizar.config(text="🔄 Sync", state='normal')
                messagebox.showerror("Error", f"Error en sincronización manual: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "No hay Google Sheets conectado")
    
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
        
        # Frame para Google Sheets
        gs_frame = ttk.Frame(input_frame)
        gs_frame.grid(row=0, column=2, padx=(10, 0))
        
        # Estado de Google Sheets
        self.gs_status_label = ttk.Label(gs_frame, text="⏳", font=('Arial', 12))
        self.gs_status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Menú contextual para el ícono de estado
        self.gs_status_label.bind('<Button-3>', self.mostrar_menu_credenciales)
        
        # Botón para configurar Google Sheets
        ttk.Button(gs_frame, text="🔑 Credenciales", 
                  command=self.abrir_configurador_google_sheets).pack(side=tk.LEFT)
        
        # Botón para conectar hoja específica
        ttk.Button(gs_frame, text="🔗 Conectar Hoja", 
                  command=self.conectar_hoja_dialog).pack(side=tk.LEFT, padx=(5, 0))
        

        
        # Actualizar estado inicial
        self.actualizar_estado_google_sheets()
        
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
        ttk.Button(btn_secundarios, text="🔄 Actualizar Registro de Productos", 
                  command=self.actualizar_registro_productos).pack(side=tk.LEFT, padx=5)
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
        tabla_frame.rowconfigure(1, weight=1)  # Cambiar a row 1 para la tabla
        main_frame.rowconfigure(5, weight=1)
        
        # Frame para el título y última actualización
        titulo_frame = ttk.Frame(tabla_frame)
        titulo_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        titulo_frame.columnconfigure(1, weight=1)
        
        ttk.Label(titulo_frame, text="Inventario", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.label_ultima_actualizacion = ttk.Label(titulo_frame, text="", font=('Arial', 9))
        self.label_ultima_actualizacion.grid(row=0, column=1, sticky=tk.E)
        
        # Crear Treeview
        columns = ('Título', 'Código', 'Producto', 'Stock', 'Stock Mín', 'Precio Costo')
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        for col in columns:
            self.tabla.heading(col, text=col)
            if col == 'Precio Costo':
                self.tabla.column(col, width=100)
            elif col == 'Título':
                self.tabla.column(col, width=200)
            else:
                self.tabla.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # Cambiar a row 1
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))  # Cambiar a row 1
        
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
    
    def mostrar_producto(self, producto):
        """Muestra la información de un producto en la interfaz"""
        self.labels_info['Código:'].config(text=producto['codigo'])
        self.labels_info['Producto:'].config(text=producto.get('titulo', producto['producto']))
        
        # Mostrar stock con color según el nivel
        stock_actual = producto['stock']
        stock_minimo = producto.get('stock_min', producto.get('stock_minimo', 0))
        
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
        precio = producto.get('precio_costo', producto.get('precio', '$0.00'))
        self.labels_info['Precio Costo Unidad:'].config(text=precio)
        self.labels_info['Última Actualización:'].config(text=producto.get('ultima_actualizacion', ''))
    
    def limpiar_info_producto(self):
        """Limpia la información del producto mostrada"""
        for label in self.labels_info.values():
            label.config(text="", foreground='black')  # Resetear color
    

    

    
    def activar_modo_edicion(self, codigo, stock_anterior):
        """Activa el modo de edición para un producto específico"""
        if self.modo_edicion_activo:
            messagebox.showwarning("Modo de Edición Activo", 
                                 f"Ya hay una edición en curso para el producto {self.producto_en_edicion}.\n"
                                 "Complete la operación actual antes de hacer otro cambio.")
            return False
        
        self.modo_edicion_activo = True
        self.producto_en_edicion = codigo
        self.stock_anterior = stock_anterior
        
        # Cambiar color de fondo para indicar modo de edición
        self.root.configure(bg='#fff3cd')  # Amarillo claro
        self.status_var.set(f"🛡️ MODO EDICIÓN: {codigo} (Stock anterior: {stock_anterior})")
        
        return True
    
    def desactivar_modo_edicion(self):
        """Desactiva el modo de edición"""
        self.modo_edicion_activo = False
        self.producto_en_edicion = None
        self.stock_anterior = None
        
        # Restaurar color de fondo
        self.root.configure(bg='#f0f0f0')
        self.status_var.set(f"{self.status_google_sheets} | Listo para escanear")
    
    def verificar_modo_edicion(self, codigo=None):
        """Verifica si se puede realizar una operación en modo de edición"""
        if self.modo_edicion_activo:
            if codigo and codigo != self.producto_en_edicion:
                messagebox.showwarning("Modo de Edición Activo", 
                                     f"No puede modificar el producto {codigo} mientras hay una edición en curso para {self.producto_en_edicion}.")
                return False
            elif not codigo:
                messagebox.showwarning("Modo de Edición Activo", 
                                     f"No puede realizar esta operación mientras hay una edición en curso para {self.producto_en_edicion}.")
                return False
        return True
    

    
    def actualizar_registro_productos(self):
        """Actualiza el registro de productos desde Google Sheets"""
        if not self.gc or not self.worksheet:
            messagebox.showerror("Error", "No hay conexión con Google Sheets. Configure las credenciales primero.")
            return
        
        try:
            # Mostrar indicador de carga
            self.status_var.set("Actualizando registro de productos desde Google Sheets...")
            self.root.update()
            
            # Leer datos de Google Sheets
            datos_raw = self.worksheet.get_all_values()
            
            if len(datos_raw) < 2:
                messagebox.showwarning("Hoja Vacía", "La hoja de Google Sheets no tiene datos de productos.")
                return
            
            # Buscar encabezados válidos
            headers = None
            fila_inicio_datos = None
            
            for i, fila in enumerate(datos_raw):
                if any('codigo' in str(celda).lower() or 'stock' in str(celda).lower() for celda in fila):
                    headers = fila
                    fila_inicio_datos = i + 1
                    break
            
            if headers is None:
                messagebox.showerror("Error", "No se encontraron encabezados válidos en la hoja.")
                return
            
            # Buscar columnas
            columna_titulo = None
            columna_codigo = None
            columna_stock = None
            columna_stock_min = None
            columna_precio = None
            
            print(f"Buscando columnas en encabezados: {headers}")
            
            for i, header in enumerate(headers):
                header_clean = str(header).strip().lower()
                print(f"  Columna {i}: '{header}' -> '{header_clean}'")
                
                if 'título' in header_clean or 'titulo' in header_clean:
                    columna_titulo = i
                    print(f"    -> Columna título encontrada en posición {i}")
                elif 'codigo' in header_clean or 'código' in header_clean:
                    columna_codigo = i
                    print(f"    -> Columna código encontrada en posición {i}")
                elif header_clean == 'stock' and 'min' not in header_clean:
                    columna_stock = i
                    print(f"    -> Columna stock encontrada en posición {i}")
                elif 'stock min' in header_clean or 'stockmin' in header_clean or header_clean == 'stock min':
                    columna_stock_min = i
                    print(f"    -> Columna stock min encontrada en posición {i}")
                elif 'precio costo' in header_clean or 'preciocosto' in header_clean:
                    columna_precio = i
                    print(f"    -> Columna precio encontrada en posición {i}")
            
            print(f"Columnas encontradas:")
            print(f"  Título: {columna_titulo}")
            print(f"  Código: {columna_codigo}")
            print(f"  Stock: {columna_stock}")
            print(f"  Stock Min: {columna_stock_min}")
            print(f"  Precio: {columna_precio}")
            
            if columna_codigo is None:
                messagebox.showerror("Error", "No se encontró la columna de código en la hoja.")
                return
            
            # Limpiar productos existentes
            self.productos.clear()
            
            # Procesar cada fila de datos
            productos_agregados = 0
            
            for fila in datos_raw[fila_inicio_datos:]:
                if len(fila) > max(filter(None, [columna_titulo, columna_codigo, columna_stock, columna_stock_min, columna_precio])):
                    codigo = str(fila[columna_codigo]).strip()
                    
                    if codigo:  # Solo procesar si hay código
                        titulo = str(fila[columna_titulo]).strip() if columna_titulo is not None and len(fila) > columna_titulo else ""
                        stock = int(fila[columna_stock]) if columna_stock is not None and len(fila) > columna_stock and str(fila[columna_stock]).strip().isdigit() else 0
                        stock_min = int(fila[columna_stock_min]) if columna_stock_min is not None and len(fila) > columna_stock_min and str(fila[columna_stock_min]).strip().isdigit() else 0
                        precio = str(fila[columna_precio]).strip() if columna_precio is not None and len(fila) > columna_precio else ""
                        
                        print(f"Procesando producto {codigo}:")
                        print(f"  Título: '{titulo}'")
                        print(f"  Stock: {stock}")
                        print(f"  Stock Min: {stock_min}")
                        print(f"  Precio: '{precio}'")
                        
                        # Crear producto
                        producto = {
                            'codigo': codigo,
                            'titulo': titulo,
                            'producto': titulo,  # Usar título como nombre del producto
                            'stock': stock,
                            'stock_min': stock_min,
                            'precio_costo': precio,
                            'ultima_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        
                        self.productos[codigo] = producto
                        productos_agregados += 1
            
            # Actualizar tabla
            self.actualizar_tabla()
            
            # Actualizar última actualización
            self.label_ultima_actualizacion.config(text=f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Guardar datos localmente
            self.guardar_datos()
            
            messagebox.showinfo("Éxito", f"Se actualizaron {productos_agregados} productos desde Google Sheets.")
            self.status_var.set(f"{self.status_google_sheets} | Registro actualizado: {productos_agregados} productos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar registro de productos:\n{str(e)}")
            self.status_var.set(f"{self.status_google_sheets} | Error al actualizar registro")
    

    
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
                
                # Sincronizar con Google Sheets automáticamente
                self.sincronizar_con_google_sheets()
                
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
                
                # Sincronizar con Google Sheets automáticamente
                self.sincronizar_con_google_sheets()
                
                self.deseleccionar_producto()
                self.status_var.set(f"Stock actualizado: -{cantidad} unidades")
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def sumar_una_unidad(self):
        """Suma una unidad al stock del producto seleccionado"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            # Verificar modo de edición
            if not self.verificar_modo_edicion(codigo):
                return
            
            stock_anterior = self.productos[codigo]['stock']
            stock_nuevo = stock_anterior + 1
            
            # Mostrar confirmación
            if self.mostrar_confirmacion_stock(codigo, stock_anterior, stock_nuevo, "+1"):
                # Activar modo de edición
                if not self.activar_modo_edicion(codigo, stock_anterior):
                    return
                
                try:
                    # Aplicar cambio
                    self.productos[codigo]['stock'] = stock_nuevo
                    self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    self.actualizar_tabla()
                    self.guardar_datos()
                    
                    # Sincronizar con Google Sheets automáticamente
                    self.sincronizar_con_google_sheets()
                    
                    # Desactivar modo de edición
                    self.desactivar_modo_edicion()
                    self.deseleccionar_producto()
                    
                except Exception as e:
                    # En caso de error, revertir cambios
                    self.productos[codigo]['stock'] = stock_anterior
                    self.actualizar_tabla()
                    self.guardar_datos()
                    self.desactivar_modo_edicion()
                    messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}\nCambios revertidos.")
        else:
            messagebox.showwarning("Advertencia", "Primero seleccione un producto")
    
    def restar_una_unidad(self):
        """Resta una unidad al stock del producto seleccionado"""
        codigo = self.labels_info['Código:'].cget("text")
        if codigo and codigo in self.productos:
            # Verificar modo de edición
            if not self.verificar_modo_edicion(codigo):
                return
            
            if self.productos[codigo]['stock'] > 0:
                stock_anterior = self.productos[codigo]['stock']
                stock_nuevo = stock_anterior - 1
                
                # Mostrar confirmación
                if self.mostrar_confirmacion_stock(codigo, stock_anterior, stock_nuevo, "-1"):
                    # Activar modo de edición
                    if not self.activar_modo_edicion(codigo, stock_anterior):
                        return
                    
                    try:
                        # Aplicar cambio
                        self.productos[codigo]['stock'] = stock_nuevo
                        self.productos[codigo]['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        self.actualizar_tabla()
                        self.guardar_datos()
                        
                        # Sincronizar con Google Sheets automáticamente
                        self.sincronizar_con_google_sheets()
                        
                        # Desactivar modo de edición
                        self.desactivar_modo_edicion()
                        self.deseleccionar_producto()
                        
                    except Exception as e:
                        # En caso de error, revertir cambios
                        self.productos[codigo]['stock'] = stock_anterior
                        self.actualizar_tabla()
                        self.guardar_datos()
                        self.desactivar_modo_edicion()
                        messagebox.showerror("Error", f"Error al actualizar stock: {str(e)}\nCambios revertidos.")
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
            if self.tabla.item(item)['values'][1] == codigo:  # Ahora el código está en la posición 1
                self.tabla.selection_add(item)
                self.tabla.see(item)  # Hacer visible el item
                break
    

    
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
            codigo = item['values'][1]  # Ahora el código está en la posición 1 (segunda columna)
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
                producto.get('titulo', producto.get('producto', '')),
                producto['codigo'],
                producto['producto'],
                producto['stock'],
                producto.get('stock_min', producto.get('stock_minimo', 0)),
                producto.get('precio_costo', producto.get('precio', '$0.00'))
            ))
    
    def mostrar_reporte(self):
        """Muestra un reporte del inventario"""
        if not self.productos:
            messagebox.showinfo("Reporte", "No hay productos en el inventario")
            return
        
        # Calcular estadísticas
        total_productos = len(self.productos)
        stock_bajo = sum(1 for p in self.productos.values() 
                        if p['stock'] <= p.get('stock_min', p.get('stock_minimo', 0)))
        
        # Calcular valor total (usar precio_costo o precio)
        valor_total = 0
        for p in self.productos.values():
            precio = p.get('precio_costo', p.get('precio', 0))
            if isinstance(precio, str) and precio.startswith('$'):
                try:
                    precio = float(precio.replace('$', '').replace(',', ''))
                except:
                    precio = 0
            elif isinstance(precio, str):
                try:
                    precio = float(precio)
                except:
                    precio = 0
            valor_total += p['stock'] * precio
        
        reporte = f"""REPORTE DE INVENTARIO
        ========================
        
        Total de productos: {total_productos}
        Productos con stock bajo: {stock_bajo}
        Valor total del inventario: ${valor_total:.2f}
        
        Productos con stock bajo:
        """
        
        for producto in self.productos.values():
            stock_min = producto.get('stock_min', producto.get('stock_minimo', 0))
            if producto['stock'] <= stock_min:
                reporte += f"\n• {producto.get('titulo', producto['producto'])} (Stock: {producto['stock']}, Mínimo: {stock_min})"
        
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
                # Cargar desde Google Sheets con formato específico
                try:
                    datos = self.worksheet.get_all_records()
                except Exception as e:
                    if "duplicates" in str(e).lower():
                        # Si hay encabezados duplicados, usar método alternativo
                        datos_raw = self.worksheet.get_all_values()
                        if datos_raw:
                            # Usar la primera fila como headers y el resto como datos
                            headers = datos_raw[0]
                            datos = []
                            for fila in datos_raw[1:]:
                                if len(fila) >= len(headers):
                                    fila_dict = {}
                                    for i, header in enumerate(headers):
                                        if header:  # Solo usar headers no vacíos
                                            fila_dict[header] = fila[i] if i < len(fila) else ''
                                    datos.append(fila_dict)
                    else:
                        raise e
                
                productos_cargados = 0
                
                for fila in datos:
                    # Buscar en columna E (Código de producto)
                    codigo_producto = fila.get('Codigo de producto (seller custom field)', '')
                    stock = fila.get('Stock', '')
                    titulo = fila.get('TÍTULO', '')
                    
                    if codigo_producto and codigo_producto.strip():  # Ignorar filas vacías
                        try:
                            stock_int = int(stock) if stock else 0
                            self.productos[codigo_producto.strip()] = {
                                'codigo': codigo_producto.strip(),
                                'producto': titulo if titulo else f"Producto {codigo_producto}",
                                'stock': stock_int,
                                'stock_minimo': 5,  # Valor por defecto
                                'precio': 0.0,  # Valor por defecto
                                'ultima_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            productos_cargados += 1
                        except ValueError:
                            # Si el stock no es un número válido, usar 0
                            self.productos[codigo_producto.strip()] = {
                                'codigo': codigo_producto.strip(),
                                'producto': titulo if titulo else f"Producto {codigo_producto}",
                                'stock': 0,
                                'stock_minimo': 5,
                                'precio': 0.0,
                                'ultima_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            productos_cargados += 1
                
                self.status_var.set(f"Datos cargados desde Google Sheets: {productos_cargados} productos")
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
                # Obtener todos los datos actuales con manejo de encabezados duplicados
                try:
                    datos_actuales = self.worksheet.get_all_records()
                except Exception as e:
                    if "duplicates" in str(e).lower():
                        # Si hay encabezados duplicados, usar método alternativo
                        datos_actuales = self.worksheet.get_all_values()
                        if datos_actuales:
                            # Usar la primera fila como headers y el resto como datos
                            headers = datos_actuales[0]
                            datos_actuales = []
                            for fila in datos_actuales[1:]:
                                if len(fila) >= len(headers):
                                    fila_dict = {}
                                    for i, header in enumerate(headers):
                                        if header:  # Solo usar headers no vacíos
                                            fila_dict[header] = fila[i] if i < len(fila) else ''
                                    datos_actuales.append(fila_dict)
                    else:
                        raise e
                
                # Actualizar solo la columna E (Stock) para productos que existen
                productos_actualizados = 0
                for i, fila in enumerate(datos_actuales, start=2):  # Empezar desde fila 2 (después de headers)
                    codigo_producto = fila.get('Codigo de producto (seller custom field)', '').strip()
                    
                    if codigo_producto and codigo_producto in self.productos:
                        # Actualizar stock en columna E (Stock)
                        nuevo_stock = self.productos[codigo_producto]['stock']
                        self.worksheet.update(f'E{i}', nuevo_stock)
                        productos_actualizados += 1
                
                print(f"Stock actualizado en Google Sheets: {productos_actualizados} productos")
                
                self.status_var.set("Stock actualizado en Google Sheets")
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
