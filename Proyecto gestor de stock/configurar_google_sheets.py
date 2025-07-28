"""
Script auxiliar para configurar Google Sheets
Ejecuta este script si necesitas ayuda para configurar la integración con Google Sheets
"""

import os
import webbrowser
import json

def mostrar_instrucciones():
    print("=" * 60)
    print("CONFIGURACIÓN DE GOOGLE SHEETS")
    print("=" * 60)
    print()
    print("Este script te ayudará a configurar la integración con Google Sheets.")
    print("Sigue estos pasos:")
    print()
    
    pasos = [
        "1. Ve a Google Cloud Console",
        "2. Crea un nuevo proyecto",
        "3. Habilita la API de Google Sheets",
        "4. Crea una cuenta de servicio",
        "5. Descarga las credenciales",
        "6. Coloca el archivo en esta carpeta"
    ]
    
    for paso in pasos:
        print(f"   {paso}")
    
    print()
    print("¿Quieres que te abra Google Cloud Console? (s/n): ", end="")
    
    respuesta = input().lower().strip()
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        webbrowser.open("https://console.cloud.google.com/")
        print("\n✅ Google Cloud Console abierto en tu navegador")
    
    print("\n" + "=" * 60)
    print("PASOS DETALLADOS:")
    print("=" * 60)
    
    instrucciones_detalladas = """
1. CREAR PROYECTO:
   - En Google Cloud Console, haz clic en "Seleccionar proyecto"
   - Haz clic en "Nuevo proyecto"
   - Dale un nombre como "Control Stock"
   - Haz clic en "Crear"

2. HABILITAR API:
   - En el menú lateral, ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Sheets API"
   - Haz clic en "Google Sheets API"
   - Haz clic en "Habilitar"

3. CREAR CUENTA DE SERVICIO:
   - Ve a "APIs y servicios" > "Credenciales"
   - Haz clic en "Crear credenciales" > "Cuenta de servicio"
   - Nombre: "control-stock-app"
   - Descripción: "Cuenta de servicio para sistema de control de stock"
   - Haz clic en "Crear y continuar"
   - En "Otorgar acceso a esta cuenta de servicio", selecciona "Editor"
   - Haz clic en "Listo"

4. DESCARGAR CREDENCIALES:
   - En la lista de cuentas de servicio, haz clic en la que creaste
   - Ve a la pestaña "Claves"
   - Haz clic en "Agregar clave" > "Crear nueva clave"
   - Selecciona "JSON"
   - Haz clic en "Crear"
   - El archivo se descargará automáticamente

5. CONFIGURAR ARCHIVO:
   - Renombra el archivo descargado a "credentials.json"
   - Muévelo a la misma carpeta que Control_stock.py
   - ¡Listo! El sistema usará Google Sheets automáticamente
"""
    
    print(instrucciones_detalladas)

def verificar_configuracion():
    print("\n" + "=" * 60)
    print("VERIFICANDO CONFIGURACIÓN")
    print("=" * 60)
    
    if os.path.exists('credentials.json'):
        print("✅ Archivo credentials.json encontrado")
        
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            if 'type' in creds and creds['type'] == 'service_account':
                print("✅ Formato de credenciales correcto")
                print("✅ Configuración lista para usar")
                return True
            else:
                print("❌ Formato de credenciales incorrecto")
                return False
                
        except json.JSONDecodeError:
            print("❌ Error al leer el archivo credentials.json")
            return False
    else:
        print("❌ Archivo credentials.json no encontrado")
        print("   Coloca el archivo de credenciales en esta carpeta")
        return False

def crear_archivo_ejemplo():
    print("\n" + "=" * 60)
    print("ARCHIVO DE EJEMPLO")
    print("=" * 60)
    
    ejemplo = {
        "type": "service_account",
        "project_id": "tu-proyecto-id",
        "private_key_id": "tu-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nTU_CLAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n",
        "client_email": "tu-cuenta@tu-proyecto.iam.gserviceaccount.com",
        "client_id": "tu-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tu-cuenta%40tu-proyecto.iam.gserviceaccount.com"
    }
    
    print("Este es el formato que debe tener tu archivo credentials.json:")
    print(json.dumps(ejemplo, indent=2))
    print("\n⚠️  IMPORTANTE: Este es solo un ejemplo. NO uses estos valores reales.")

def main():
    print("🔧 CONFIGURADOR DE GOOGLE SHEETS")
    print("Para el Sistema de Control de Stock")
    print()
    
    while True:
        print("\nOpciones:")
        print("1. Mostrar instrucciones paso a paso")
        print("2. Verificar configuración actual")
        print("3. Mostrar formato del archivo credentials.json")
        print("4. Salir")
        print()
        
        opcion = input("Selecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            mostrar_instrucciones()
        elif opcion == "2":
            if verificar_configuracion():
                print("\n🎉 ¡Tu configuración está lista!")
                print("Puedes ejecutar Control_stock.py ahora")
            else:
                print("\n⚠️  Necesitas completar la configuración")
        elif opcion == "3":
            crear_archivo_ejemplo()
        elif opcion == "4":
            print("\n¡Hasta luego! 👋")
            break
        else:
            print("❌ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main() 