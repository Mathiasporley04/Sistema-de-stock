# 📦 SISTEMA DE CONTROL DE STOCK V2

## 🎯 ¿Qué hace este programa?

Es un sistema para **gestionar el inventario** de tu negocio. Te permite:
- **Escanear códigos de barras** de productos
- **Ver el stock actual** de cada producto
- **Sumar o restar stock** fácilmente
- **Sincronizar automáticamente** con Google Sheets
- **Ver reportes** del inventario

---

## 🚀 FUNCIONES PRINCIPALES

### 📱 **Interfaz Simple**
- **Campo de escaneo**: Escribe o escanea códigos de productos
- **Botones +1 y -1**: Cambiar stock rápidamente
- **Tabla de productos**: Ver todos los productos organizados
- **Información detallada**: Stock, precios, stock mínimo

### 🔗 **Integración con Google Sheets**
- **Sincronización automática**: Los cambios se guardan en Google Sheets
- **Actualizar desde Google Sheets**: Traer productos desde tu hoja
- **Conexión segura**: Credenciales guardadas internamente

### 🛡️ **Sistema de Seguridad**
- **Modo de edición único**: Solo un cambio a la vez
- **Indicador visual**: Fondo amarillo durante edición
- **Reversión automática**: Si hay error, vuelve al estado anterior

---

## 📋 CÓMO USAR EL PROGRAMA

### 1️⃣ **Primera vez - Configurar Google Sheets**
1. Haz clic en **"🔑 Credenciales"**
2. Selecciona tu archivo `credentials.json` de Google
3. Haz clic en **"🔗 Conectar Hoja"**
4. Pega la URL de tu Google Sheets
5. ¡Listo! Ya está conectado

### 2️⃣ **Usar el sistema**
1. **Escanear código**: Escribe o escanea el código del producto
2. **Ver información**: Aparece el stock, precio, etc.
3. **Cambiar stock**: Usa **+1** o **-1** para modificar
4. **Confirmar**: El sistema actualiza automáticamente Google Sheets

### 3️⃣ **Actualizar productos desde Google Sheets**
- Haz clic en **"🔄 Actualizar Registro de Productos"**
- El sistema lee todos los productos de tu hoja
- Los muestra en la tabla

---

## 🔧 FUNCIONES ESPECIALES

### 📊 **Reporte de Inventario**
- **Total de productos**
- **Productos con stock bajo**
- **Valor total del inventario**
- **Lista de productos que necesitan reposición**

### 📈 **Acciones Múltiples**
- **"📈 Sumar Múltiples"**: Agregar varias unidades
- **"📉 Restar Múltiples"**: Quitar varias unidades

### 🔄 **Sincronización**
- **Automática**: Cada cambio se sincroniza con Google Sheets
- **Optimizada**: Solo actualiza productos que cambiaron
- **Rápida**: No consume tiempo innecesario

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
Proyecto gestor de stock V2/
├── Control_stock.py          # Programa principal
├── README.md                 # Esta documentación
├── CAMBIOS_V2.md            # Lista de cambios
└── INSTRUCCIONES_RAPIDAS.md # Guía rápida
```

---

## ⚠️ IMPORTANTE

### ✅ **Lo que SÍ hace:**
- Gestiona inventario local y en Google Sheets
- Sincroniza automáticamente
- Protege contra errores
- Es rápido y eficiente

### ❌ **Lo que NO hace:**
- No crea productos nuevos (solo lee desde Google Sheets)
- No borra productos
- No modifica precios (solo stock)

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### **No conecta a Google Sheets**
1. Verifica que el archivo `credentials.json` esté en la carpeta
2. Asegúrate de que las APIs estén habilitadas en Google Cloud
3. Revisa que la hoja esté compartida con la cuenta de servicio

### **No encuentra productos**
1. Haz clic en **"🔄 Actualizar Registro de Productos"**
2. Verifica que los códigos en Google Sheets coincidan
3. Revisa que la hoja tenga los encabezados correctos

### **Error de sincronización**
1. Verifica tu conexión a internet
2. Revisa que la hoja no esté siendo editada por otra persona
3. Intenta de nuevo en unos minutos

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa esta documentación
2. Verifica que Google Sheets esté configurado correctamente
3. Asegúrate de que las credenciales sean válidas

---

**¡El sistema está listo para usar! 🎉** 