# Sistema de Control de Stock con Código de Barras

Un sistema completo para gestionar inventario usando códigos de barras, con integración opcional a Google Sheets.

## Características

- ✅ **Escaneo de códigos de barras** - Compatible con pistolas de código de barras
- ✅ **Interfaz gráfica intuitiva** - Fácil de usar
- ✅ **Integración con Google Sheets** - Almacenamiento en la nube
- ✅ **Modo local** - Funciona sin conexión a internet
- ✅ **Gestión completa de stock** - Alta, baja y búsqueda de productos
- ✅ **Reportes automáticos** - Alertas de stock bajo
- ✅ **Búsqueda rápida** - Encuentra productos instantáneamente

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Google Sheets (Opcional)

Para usar Google Sheets como base de datos:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la API de Google Sheets
4. Crea una cuenta de servicio:
   - Ve a "IAM y administración" > "Cuentas de servicio"
   - Crea una nueva cuenta de servicio
   - Descarga el archivo JSON de credenciales
   - Renombra el archivo a `credentials.json`
   - Colócalo en la misma carpeta que el script

### 3. Ejecutar el sistema

```bash
python Control_stock.py
```

## Uso del Sistema

### Escaneo de Productos

1. **Conectar la pistola de código de barras** a tu computadora
2. **Hacer clic en el campo "Código"** o presionar Tab
3. **Escanear el código de barras** del producto
4. El sistema automáticamente:
   - Buscará el producto en la base de datos
   - Mostrará su información si existe
   - Preguntará si quieres agregarlo si es nuevo

### Funciones Principales

#### 🔍 **Buscar Producto**
- Busca productos por código manualmente
- Útil cuando no tienes la pistola conectada

#### ➕ **Agregar Producto**
- Agrega nuevos productos al inventario
- Solicita: código, nombre, precio y stock mínimo

#### 📈 **Dar de Alta**
- Aumenta el stock de un producto
- Selecciona el producto primero

#### 📉 **Dar de Baja**
- Reduce el stock de un producto
- No permite bajar más del stock disponible

#### 📊 **Ver Reporte**
- Muestra estadísticas del inventario
- Lista productos con stock bajo
- Calcula valor total del inventario

### Flujo de Trabajo Típico

1. **Primera vez**: Agregar productos escaneando códigos
2. **Recepción de mercancía**: Usar "Dar de Alta" para aumentar stock
3. **Ventas/Consumo**: Usar "Dar de Baja" para reducir stock
4. **Control diario**: Revisar reportes para detectar stock bajo

## Estructura de Datos

Cada producto contiene:
- **Código**: Código de barras único
- **Producto**: Nombre/descripción
- **Stock Actual**: Cantidad disponible
- **Stock Mínimo**: Nivel de alerta
- **Precio**: Precio unitario
- **Última Actualización**: Fecha y hora del último cambio

## Modos de Operación

### Modo Google Sheets
- Datos sincronizados en la nube
- Acceso desde cualquier dispositivo
- Backup automático
- Requiere configuración inicial

### Modo Local
- Datos guardados en `stock_local.json`
- Funciona sin internet
- Ideal para uso offline
- No requiere configuración

## Solución de Problemas

### La pistola no funciona
- Verifica que esté conectada como teclado
- Asegúrate de que el campo "Código" esté seleccionado
- Prueba escanear en cualquier editor de texto

### Error de Google Sheets
- Verifica que `credentials.json` esté en la carpeta correcta
- Asegúrate de que la API esté habilitada
- Revisa los permisos de la cuenta de servicio

### Datos no se guardan
- Verifica permisos de escritura en la carpeta
- En modo local, asegúrate de que `stock_local.json` no esté abierto en otro programa

## Personalización

### Cambiar nombre de la hoja de Google Sheets
Edita la línea en `Control_stock.py`:
```python
self.sheet_name = "Control_Stock"  # Cambia por tu nombre preferido
```

### Agregar campos adicionales
Modifica la lista de headers en la función `setup_google_sheets()`:
```python
headers = ['Código', 'Producto', 'Stock Actual', 'Stock Mínimo', 'Última Actualización', 'Precio', 'Nuevo Campo']
```

## Seguridad

- Las credenciales de Google Sheets se almacenan localmente
- No se envían datos a servidores externos (excepto Google Sheets)
- Los datos locales se guardan en formato JSON legible

## Soporte

Para problemas o mejoras:
1. Revisa la sección de solución de problemas
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de tener permisos de escritura en la carpeta

---

**¡Listo para usar!** 🚀

El sistema está diseñado para ser intuitivo y fácil de usar. Comienza escaneando tu primer producto y verás lo simple que es mantener tu inventario actualizado. 