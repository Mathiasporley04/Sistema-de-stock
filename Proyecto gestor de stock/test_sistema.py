"""
Script de prueba para verificar que el sistema de control de stock funcione correctamente
"""

import json
import os
import sys

def test_imports():
    """Prueba que todas las dependencias estén disponibles"""
    print("🔍 Probando importaciones...")
    
    try:
        import tkinter
        print("✅ Tkinter - OK")
    except ImportError:
        print("❌ Tkinter - FALLO")
        return False
    
    try:
        import gspread
        print("✅ gspread - OK")
    except ImportError:
        print("❌ gspread - FALLO")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google-auth - OK")
    except ImportError:
        print("❌ google-auth - FALLO")
        return False
    
    return True

def test_archivos():
    """Prueba que los archivos necesarios existan"""
    print("\n📁 Probando archivos...")
    
    archivos_requeridos = [
        "Control_stock.py",
        "requirements.txt",
        "README.md"
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - OK")
        else:
            print(f"❌ {archivo} - FALLO")
            return False
    
    # Verificar archivo de datos de ejemplo
    if os.path.exists("stock_local.json"):
        print("✅ stock_local.json - OK (datos de ejemplo encontrados)")
    else:
        print("⚠️  stock_local.json - No encontrado (se creará automáticamente)")
    
    return True

def test_datos_ejemplo():
    """Prueba que los datos de ejemplo sean válidos"""
    print("\n📊 Probando datos de ejemplo...")
    
    if not os.path.exists("stock_local.json"):
        print("⚠️  No hay datos de ejemplo para probar")
        return True
    
    try:
        with open("stock_local.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        print(f"✅ Datos cargados correctamente: {len(datos)} productos")
        
        # Verificar estructura de datos
        for codigo, producto in datos.items():
            campos_requeridos = ["codigo", "producto", "stock", "stock_minimo", "precio", "ultima_actualizacion"]
            for campo in campos_requeridos:
                if campo not in producto:
                    print(f"❌ Campo '{campo}' faltante en producto {codigo}")
                    return False
        
        print("✅ Estructura de datos válida")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_sistema_basico():
    """Prueba funcionalidades básicas del sistema"""
    print("\n⚙️  Probando sistema básico...")
    
    try:
        # Importar el sistema
        from Control_stock import SistemaControlStock
        
        # Crear instancia (sin mostrar ventana)
        sistema = SistemaControlStock()
        
        # Verificar que se creó correctamente
        if hasattr(sistema, 'productos') and hasattr(sistema, 'root'):
            print("✅ Sistema creado correctamente")
            
            # Verificar que cargó datos
            if sistema.productos:
                print(f"✅ Datos cargados: {len(sistema.productos)} productos")
            else:
                print("⚠️  No hay datos cargados")
            
            # Cerrar ventana sin mostrar
            sistema.root.destroy()
            return True
        else:
            print("❌ Sistema no se creó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error al crear sistema: {e}")
        return False

def mostrar_resumen():
    """Muestra un resumen de la configuración"""
    print("\n" + "=" * 60)
    print("RESUMEN DE CONFIGURACIÓN")
    print("=" * 60)
    
    print("\n📋 Estado del sistema:")
    
    # Verificar Google Sheets
    if os.path.exists("credentials.json"):
        print("✅ Google Sheets configurado")
        print("   - Los datos se sincronizarán en la nube")
    else:
        print("⚠️  Google Sheets no configurado")
        print("   - Los datos se guardarán localmente")
        print("   - Ejecuta 'python configurar_google_sheets.py' para configurar")
    
    # Verificar datos
    if os.path.exists("stock_local.json"):
        try:
            with open("stock_local.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
            print(f"✅ Datos de ejemplo disponibles: {len(datos)} productos")
        except:
            print("⚠️  Datos de ejemplo corruptos")
    else:
        print("⚠️  No hay datos de ejemplo")
    
    print("\n🚀 Próximos pasos:")
    print("1. Ejecuta 'python Control_stock.py' para usar el sistema")
    print("2. Conecta tu pistola de código de barras")
    print("3. Comienza escaneando productos")
    
    if not os.path.exists("credentials.json"):
        print("\n💡 Para usar Google Sheets:")
        print("   Ejecuta 'python configurar_google_sheets.py'")

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS DEL SISTEMA DE CONTROL DE STOCK")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    pruebas = [
        ("Importaciones", test_imports),
        ("Archivos", test_archivos),
        ("Datos de ejemplo", test_datos_ejemplo),
        ("Sistema básico", test_sistema_basico)
    ]
    
    resultados = []
    for nombre, prueba in pruebas:
        try:
            resultado = prueba()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en prueba '{nombre}': {e}")
            resultados.append((nombre, False))
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("RESULTADOS DE LAS PRUEBAS")
    print("=" * 60)
    
    exitos = 0
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{nombre}: {estado}")
        if resultado:
            exitos += 1
    
    print(f"\nTotal: {exitos}/{len(resultados)} pruebas exitosas")
    
    if exitos == len(resultados):
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    # Mostrar resumen
    mostrar_resumen()

if __name__ == "__main__":
    main() 