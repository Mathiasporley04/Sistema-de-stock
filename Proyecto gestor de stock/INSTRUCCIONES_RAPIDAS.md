# 🚀 INSTRUCCIONES RÁPIDAS - Sistema de Control de Stock

## ¡EMPIEZA AHORA!

### 1. Ejecutar el Sistema
```bash
python Control_stock.py
```

### 2. Usar con Pistola de Código de Barras
1. **Conecta** tu pistola de código de barras a la computadora
2. **Haz clic** en el campo "Código" en la interfaz
3. **Escanea** cualquier código de barras
4. El sistema automáticamente:
   - ✅ **Buscará** el producto en la base de datos
   - ✅ **Mostrará** su información con colores (verde=nivel bueno, naranja=medio, rojo=bajo)
   - ✅ **Limpiará** el campo para el siguiente escaneo
   - ✅ **Resaltará** el producto en la tabla
   - ✅ **Preguntará** si agregarlo si es nuevo (ventana no intrusiva)

### 3. Funciones Principales

#### 🎯 **Botones Principales (Uso Rápido):**
| Botón | Función | Atajo |
|-------|---------|-------|
| ➕ **+1** | Suma 1 unidad (venta) | Ctrl + (+) |
| ➖ **-1** | Resta 1 unidad (devolución) | Ctrl + (-) |

#### 🔧 **Botones Secundarios (Casos Especiales):**
| Botón | Función |
|-------|---------|
| 📈 **Sumar Múltiples** | Aumenta stock (cantidad personalizada) |
| 📉 **Restar Múltiples** | Reduce stock (cantidad personalizada) |
| 🔍 **Buscar Producto** | Búsqueda manual por código |
| ➕ **Agregar Producto** | Agrega nuevo producto al inventario |
| 📊 **Ver Reporte** | Muestra estadísticas del inventario |

### 4. Flujo de Trabajo Típico

#### Primera vez:
1. Escanea códigos de barras de tus productos
2. El sistema preguntará si quieres agregarlos
3. Completa: nombre, precio, stock mínimo

#### Uso diario:
1. **Ventas**: Usa botón "-1" o Ctrl + (-) para ventas rápidas
2. **Devoluciones**: Usa botón "+1" o Ctrl + (+) para devoluciones
3. **Recepción**: Usa "Sumar Múltiples" para cantidades grandes
4. **Control**: Revisa reportes para stock bajo

### 5. Datos de Ejemplo Incluidos

El sistema viene con 5 productos de ejemplo:
- Laptop HP Pavilion (Stock: 5)
- Mouse Inalámbrico Logitech (Stock: 15)
- Teclado Mecánico RGB (Stock: 8)
- Monitor 24" Samsung (Stock: 3)
- Cable HDMI 2m (Stock: 25)

**Puedes probar escaneando estos códigos:**
- 123456789
- 987654321
- 456789123
- 789123456
- 321654987

### 6. Configurar Google Sheets (Opcional)

Si quieres sincronizar en la nube:
```bash
python configurar_google_sheets.py
```

### 7. Verificar Sistema

Para asegurarte de que todo funciona:
```bash
python test_sistema.py
```

---

## 🎯 ¡LISTO PARA USAR!

**El sistema está completamente funcional y listo para tu negocio.**

- ✅ Interfaz gráfica intuitiva
- ✅ Compatible con pistolas de código de barras
- ✅ Datos de ejemplo incluidos
- ✅ Funciona sin internet (modo local)
- ✅ Opción de sincronización en la nube

**¡Comienza escaneando tu primer producto!** 