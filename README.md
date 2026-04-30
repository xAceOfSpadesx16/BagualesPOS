# BagualesPOS API Documentation

Documentación completa y precisa de todos los endpoints de la API REST de BagualesPOS.  
**Esta documentación está basada 100% en los serializers reales del backend.**

**Base URL**: `/api/`

---

## Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Perfil de Empresa](#perfil-de-empresa)
3. [Configuración de Empresa](#configuración-de-empresa)
4. [Sucursales](#sucursales)
5. [Productos](#productos)
6. [Historial de Precios](#historial-de-precios)
7. [Actualización Masiva de Precios](#actualización-masiva-de-precios)
8. [Clientes](#clientes)
9. [Inventario](#inventario)
10. [Transferencias de Stock](#transferencias-de-stock)
11. [Ventas](#ventas)
12. [Devoluciones](#devoluciones)
13. [Caja](#caja)
14. [Dispositivos](#dispositivos)
15. [Usuarios](#usuarios)
16. [Codigos de Autorizacion](#codigos-de-autorizacion)
17. [Registros de Auditoría](#registros-de-auditoría)

---

## Autenticación

### Obtener Token de Acceso
**Método**: `POST`  
**Endpoint**: `/api/token/`  
**Descripción**: Autenticarse y obtener tokens JWT (access y refresh)

**Request**:
```json
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "tu@email.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }
}
```

### Refrescar Token
**Método**: `POST`  
**Endpoint**: `/api/token/refresh/`  
**Descripción**: Renovar token de acceso usando refresh token

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Cerrar Sesión
**Método**: `POST`  
**Endpoint**: `/api/token/logout/`  
**Descripción**: Invalidar refresh token

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Perfil de Empresa

### Obtener Perfil
**Método**: `GET`
**Endpoint**: `/api/company/me/`
**Descripción**: Retorna los datos de la empresa del usuario autenticado

**Response**:
```json
{
  "id": 1,
  "name": "Mi Empresa S.A.",
  "legal_name": "Mi Empresa Sociedad Anónima",
  "tax_id": "30-12345678-9",
  "logo": "/media/companies/logos/logo.png",
  "address": "Av. San Martín 123",
  "phone": "+54 351 1234567",
  "email": "contacto@miempresa.com",
  "is_active": true
}
```

**Error 404**: Si el usuario no tiene empresa asociada.

---

## Configuración de Empresa

### Obtener Configuración
**Método**: `GET`
**Endpoint**: `/api/company/settings/`
**Descripción**: Retorna la configuración de la empresa. Si no existe, se crea con valores por defecto.

**Response**:
```json
{
  "id": 1,
  "company": 1,
  "tax_name": "IVA",
  "tax_rate": "21.00",
  "tax_enabled": true,
  "currency_code": "ARS",
  "currency_symbol": "$",
  "currency_decimals": 2,
  "receipt_header": "",
  "receipt_footer": "",
  "receipt_show_tax": true,
  "allow_negative_stock": false,
  "low_stock_threshold": 5
}
```

### Actualizar Configuración
**Método**: `PATCH`
**Endpoint**: `/api/company/settings/`
**Descripción**: Actualizar la configuración de la empresa (campos parciales)

**Request**:
```json
{
  "tax_rate": "10.50",
  "currency_code": "USD",
  "currency_symbol": "US$",
  "low_stock_threshold": 10,
  "receipt_footer": "Gracias por su compra"
}
```

**Response**: Objeto `CompanySettings` completo actualizado.

---

## Sucursales

### Listar Sucursales
**Método**: `GET`  
**Endpoint**: `/api/branches/`  
**Descripción**: Lista las sucursales de la empresa del usuario autenticado  
**Filtros**: `?is_active=true`  
**Búsqueda**: `?search=nombre`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Sucursal Centro",
    "code": "MAIN001",
    "address": "Av. San Martín 123",
    "is_active": true,
    "company": 1
  }
]
```

### Crear Sucursal
**Método**: `POST`  
**Endpoint**: `/api/branches/`  
**Descripción**: Crear nueva sucursal. La `company` se asigna automáticamente del usuario autenticado.

**Request**:
```json
{
  "name": "Sucursal Norte",
  "code": "NORTE01",
  "address": "Av. Colón 456"
}
```

**Response** `201`:
```json
{
  "id": 2,
  "name": "Sucursal Norte",
  "code": "NORTE01",
  "address": "Av. Colón 456",
  "is_active": true,
  "company": 1
}
```

**Errores comunes**:
- `400 Bad Request` – Si el usuario no tiene compañía asignada.
- `400 Bad Request` – Código de sucursal duplicado.

### Obtener Sucursal
**Método**: `GET`  
**Endpoint**: `/api/branches/<int:pk>/`  
**Ejemplo**: `/api/branches/1/`

### Actualizar Sucursal
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/branches/<int:pk>/`  
**Ejemplo**: `/api/branches/1/`

### Eliminar Sucursal
**Método**: `DELETE`  
**Endpoint**: `/api/branches/<int:pk>/`  
**Ejemplo**: `/api/branches/1/`

---

## Productos

> **Nota**: Los productos usan diferentes serializers según la acción:
> - **Listado** (`GET /products/`): Usa `ProductListSerializer` (simplificado)
> - **Detalle** (`GET /products/{id}/`): Usa `ProductDetailSerializer` (completo)
> - **Crear/Actualizar** (`POST/PUT/PATCH`): Usa `ProductCreateUpdateSerializer`

### Listar Productos
**Método**: `GET`  
**Endpoint**: `/api/products/`  
**Descripción**: Obtener lista simplificada de productos  
**Filtros**: `?category=1&brand=2&gender=1&season=1`  
**Búsqueda**: `?search=camisa`  
**Ordenamiento**: `?ordering=sale_price` o `?ordering=-sale_price`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Camisa Slim Fit",
    "brand": {
      "id": 2,
      "name": "Nike"
    },
    "category": {
      "id": 1,
      "name": "Ropa"
    },
    "sale_price": "$100.00",
    "is_active": true
  }
]
```

### Obtener Producto (Detalle)
**Método**: `GET`  
**Endpoint**: `/api/products/<int:pk>/`  
**Ejemplo**: `/api/products/1/`  
**Descripción**: Obtener detalles completos de un producto

**Response**:
```json
{
  "id": 1,
  "name": "Camisa Slim Fit",
  "numeric_size": 42,
  "cost_price": 50.00,
  "formatted_cost_price": "$50.00",
  "sale_price": 100.00,
  "formatted_sale_price": "$100.00",
  "internal_code": "PROD-00001",
  "details": "Camisa de algodón para hombre",
  "image": "/media/products/camisa.jpg",
  "is_active": true,
  "gender": {
    "id": 1,
    "name": "Masculino"
  },
  "letter_size": null,
  "material": {
    "id": 1,
    "name": "Algodón"
  },
  "color": {
    "id": 3,
    "name": "Azul",
    "code": "#0000FF"
  },
  "brand": {
    "id": 2,
    "name": "Nike"
  },
  "category": {
    "id": 1,
    "name": "Ropa"
  },
  "subcategories": [
    {
      "id": 1,
      "name": "Camisas"
    }
  ],
  "season": {
    "id": 2,
    "name": "Verano"
  },
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "is_deleted": false,
  "deleted_at": null
}
```

### Crear Producto
**Método**: `POST`  
**Endpoint**: `/api/products/`  
**Descripción**: Crear un nuevo producto

**Request**:
```json
{
  "name": "Pantalón Deportivo",
  "numeric_size": 40,
  "cost_price": "75.00",
  "sale_price": "150.00",
  "details": "Pantalón deportivo de poliéster",
  "image": null,
  "is_active": true,
  "gender": 1,
  "letter_size": null,
  "material": 2,
  "color": 1,
  "brand": 2,
  "category": 1,
  "subcategories": [1, 2],
  "season": 3
}
```

> **Validaciones**:
> - `sale_price` debe ser mayor que `cost_price`
> - Debe proporcionarse `numeric_size` O `letter_size`, no ambos
> - Campos requeridos: `brand`, `category`, `gender`, `color`, `season`

### Actualizar Producto
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/products/<int:pk>/`  
**Ejemplo**: `/api/products/1/`  
**Descripción**: Actualizar un producto

### Eliminar Producto (Soft Delete)
**Método**: `DELETE`
**Endpoint**: `/api/products/<int:pk>/`
**Ejemplo**: `/api/products/1/`
**Descripción**: Eliminar lógicamente un producto

---

## Historial de Precios

### Obtener Historial de Precios de un Producto
**Método**: `GET`
**Endpoint**: `/api/products/<int:pk>/price-history/`
**Ejemplo**: `/api/products/1/price-history/`
**Descripción**: Historial de cambios de precio de un producto (inmutable)
**Filtros**: `?date_from=2025-01-01&date_to=2025-03-01&limit=50`

**Response**:
```json
[
  {
    "id": 1,
    "product": 1,
    "field": "sale_price",
    "old_value": "100.00",
    "new_value": "110.00",
    "change_percentage": "10.00",
    "reason": "",
    "source": "MANUAL",
    "changed_by": 1,
    "changed_by_name": "Admin General",
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

> `field` puede ser `sale_price` o `cost_price`. `source` puede ser `MANUAL` o `BULK_UPDATE`.
> El historial se registra automáticamente vía signal al actualizar precios.

---

## Actualización Masiva de Precios

### Actualización Masiva
**Método**: `POST`
**Endpoint**: `/api/products/bulk-update-prices/`
**Descripción**: Aplica un ajuste de precios (porcentual o absoluto) a múltiples productos

**Request**:
```json
{
  "mode": "percentage",
  "adjustment": 10.0,
  "target_field": "sale_price",
  "product_ids": [1, 2, 3],
  "filters": {
    "category": 2,
    "brand": 1
  },
  "round_to": 2,
  "reason": "Actualización mensual"
}
```

> `mode`: `percentage` o `absolute`
> `target_field`: `sale_price`, `cost_price` o `both`
> `product_ids`: Array de IDs específicos (opcional)
> `filters`: Filtrar por categoría/marca (opcional, se combina con product_ids)
> `round_to`: Decimales de redondeo (default: 2)

**Response** `200`:
```json
{
  "updated_count": 5,
  "products": [
    {
      "id": 1,
      "name": "Camisa Slim Fit",
      "old_sale_price": "100.00",
      "new_sale_price": "110.00",
      "old_cost_price": "50.00",
      "new_cost_price": "50.00"
    }
  ]
}
```

> Se crea un `PriceHistory` por cada producto actualizado con `source: "BULK_UPDATE"`.

---

### Recursos de Productos

Todos estos recursos usan el patrón List/Write serializers:
- **Listado/Detalle**: Retorna `{ "id": 1, "name": "..." }`
- **Crear/Actualizar**: Acepta todos los campos del modelo

#### Marcas (Brands)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/brands/`

**Response (GET)**:
```json
[
  {
    "id": 1,
    "name": "Nike"
  }
]
```

#### Categorías
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/categories/`

#### Subcategorías
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/subcategories/`

#### Colores
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/colors/`

**Response (GET)**:
```json
[
  {
    "id": 1,
    "name": "Rojo",
    "code": "#FF0000"
  }
]
```

#### Géneros
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/genders/`

#### Talles (Letter Sizes)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/letter-sizes/`

#### Materiales
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/materials/`

#### Temporadas (Seasons)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/seasons/`

#### Proveedores (Suppliers)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/suppliers/`

---

## Clientes

### Listar Clientes
**Método**: `GET`  
**Endpoint**: `/api/clients/`  
**Descripción**: Obtener lista de clientes  
**Filtros**: `?is_deleted=false&chosen_billing_type=A`  
**Búsqueda**: `?search=Juan` (busca en name, last_name, dni, email, cuit)

**Response**:
```json
[
  {
    "id": 1,
    "name": "Juan",
    "last_name": "Pérez",
    "dni": "12345678",
    "email": "juan@email.com",
    "phone": "1234567890",
    "address": "Calle Falsa 123",
    "city": "Buenos Aires",
    "state": "Buenos Aires",
    "zip_code": "1000",
    "cuit": "20-12345678-9",
    "chosen_billing_type": "A",
    "is_deleted": false,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "deleted_at": null,
    "total_purchases": 5,
    "last_purchase": "2025-01-14T15:30:00Z",
    "customer_account": {
      "id": 1,
      "credit_limit": "10000.00",
      "active": true,
      "balance": "-2500.00"
    }
  }
]
```

### Crear Cliente
**Método**: `POST`  
**Endpoint**: `/api/clients/`  
**Descripción**: Crear un nuevo cliente

**Request**:
```json
{
  "name": "María",
  "last_name": "González",
  "dni": "87654321",
  "email": "maria@email.com",
  "phone": "0987654321",
  "address": "Av. Siempre Viva 742",
  "city": "Rosario",
  "state": "Santa Fe",
  "zip_code": "2000",
  "cuit": null,
  "chosen_billing_type": "B"
}
```

### Obtener Cliente
**Método**: `GET`  
**Endpoint**: `/api/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/1/`

### Actualizar Cliente
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/1/`

### Eliminar Cliente (Soft Delete)
**Método**: `DELETE`  
**Endpoint**: `/api/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/1/`  
**Descripción**: Elimina lógicamente (is_deleted=true)

### Restaurar Cliente
**Método**: `POST`  
**Endpoint**: `/api/clients/<int:pk>/restore/`  
**Ejemplo**: `/api/clients/1/restore/`  
**Descripción**: Restaurar un cliente eliminado

**Response**:
```json
{
  "status": "client restored"
}
```

---

### Cuentas Corrientes (Customer Accounts)

#### Listar Cuentas
**Método**: `GET`  
**Endpoint**: `/api/customer-accounts/`

**Response**:
```json
[
  {
    "id": 1,
    "client": {
      "id": 1,
      "name": "Juan",
      "last_name": "Pérez",
      "dni": "12345678"
    },
    "credit_limit": "10000.00",
    "active": true,
    "notes": "",
    "opening_date": "2025-01-01T00:00:00Z",
    "balance": "-2500.00"
  }
]
```

#### Crear Cuenta
**Método**: `POST`  
**Endpoint**: `/api/customer-accounts/`

**Request**:
```json
{
  "client_id": 1,
  "credit_limit": "10000.00",
  "active": true,
  "notes": "Cliente confiable"
}
```

#### Desactivar Cuenta
**Método**: `POST`  
**Endpoint**: `/api/customer-accounts/<int:pk>/deactivate/`  
**Ejemplo**: `/api/customer-accounts/1/deactivate/`

**Response**:
```json
{
  "status": "account deactivated"
}
```

#### Resumen de Cuentas
**Método**: `GET`  
**Endpoint**: `/api/customer-accounts/summary/`  
**Descripción**: Estadísticas de todas las cuentas corrientes

**Response**:
```json
{
  "credit_limit": "50000.00",
  "current_balance": "-15000.00",
  "available_credit": "35000.00",
  "total_debit": "25000.00",
  "total_credit": "10000.00"
}
```

---

### Registros de Balance (Balance Records)

#### Listar Registros
**Método**: `GET`  
**Endpoint**: `/api/balance-records/`

**Response**:
```json
[
  {
    "id": 1,
    "customer_account": 1,
    "type": "CREDIT",
    "amount": "5000.00",
    "payment_method": 1,
    "description": "Pago efectivo",
    "created_at": "2025-01-15T10:00:00Z",
    "created_by": "admin",
    "reconciled_at": null,
    "reconciled_by": null,
    "is_effective": true
  }
]
```

#### Crear Registro
**Método**: `POST`  
**Endpoint**: `/api/balance-records/`  
**Descripción**: Registrar pago o débito en cuenta corriente

**Request**:
```json
{
  "customer_account": 1,
  "type": "CREDIT",
  "amount": "5000.00",
  "payment_method": 1,
  "description": "Pago parcial factura 123"
}
```

---

## Inventario

### Listar Inventario
**Método**: `GET`  
**Endpoint**: `/api/inventory/`  
**Descripción**: Obtener stock de todos los productos  
**Filtros**: `?branch=1`

**Response**:
```json
[
  {
    "id": 1,
    "product": {
      "id": 1,
      "name": "Camisa Slim Fit",
      "brand": {
        "id": 2,
        "name": "Nike"
      },
      "category": {
        "id": 1,
        "name": "Ropa"
      },
      "sale_price": "$100.00",
      "is_active": true
    },
    "branch": 1,
    "quantity": 50
  }
]
```

### Obtener Inventario
**Método**: `GET`  
**Endpoint**: `/api/inventory/<int:pk>/`  
**Ejemplo**: `/api/inventory/1/`

### Actualizar Inventario
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/inventory/<int:pk>/`  
**Ejemplo**: `/api/inventory/1/`

**Request**:
```json
{
  "quantity": 75
}
```

### Disponibilidad en Otras Sucursales
**Método**: `GET`  
**Endpoint**: `/api/inventory/<int:pk>/other-branches/`  
**Ejemplo**: `/api/inventory/1/other-branches/`  
**Descripción**: Retorna la disponibilidad del mismo producto (asociado al registro de inventario solicitado) en todas las demás sucursales del sistema, excluyendo el inventario de la(s) sucursal(es) asignadas al cajero/usuario actual.

**Response**: Array de objetos de Inventario correspondientes a las dem\u00e1s sucursales.

### Actualizar Cantidad de Stock
**M\u00e9todo**: `POST`  
**Endpoint**: `/api/inventory/<int:pk>/update_quantity/`  
**Ejemplo**: `/api/inventory/1/update_quantity/`  
**Descripci\u00f3n**: Suma o resta unidades del stock de un item de inventario.

**Request**:
```json
{
  "operation": "addition",
  "quantity": 10
}
```

> `operation` puede ser `addition` (sumar) o `subtraction` (restar).  
> `quantity` debe ser un entero positivo mayor a 0.

**Errores comunes**:
- `400 Bad Request` &ndash; Cantidad inv\u00e1lida (no num\u00e9rica, negativa o cero).
- `400 Bad Request` &ndash; Operaci\u00f3n inv\u00e1lida (distinta a `addition` o `subtraction`).

**Response**: Objeto de Inventario actualizado.

### Stock Bajo
**M\u00e9todo**: `GET`  
**Endpoint**: `/api/inventory/low-stock/`  
**Filtro**: `?threshold=5` (por defecto: 5)  
**Descripci\u00f3n**: Lista items cuyo stock es menor o igual al umbral.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Camisa Slim Fit",
    "stock": 3,
    "min": 5
  }
]
```

### Resumen de Stock por Sucursal
**M\u00e9todo**: `GET`  
**Endpoint**: `/api/inventory/stock-breakdown/`  
**Descripci\u00f3n**: Resumen agregado de stock por producto entre sucursales. **Solo disponible para Administradores Generales.**  
**Filtros**: `?product=1&branch=1&low_stock=10`

**Response**:
```json
[
  {
    "product_id": 1,
    "product_name": "Camisa Slim Fit",
    "product_code": "PROD-00001",
    "sale_price": 100.0,
    "cost_price": 50.0,
    "total_stock": 150,
    "branches_count": 3,
    "branches": [
      { "branch__id": 1, "branch__name": "Centro", "branch__code": "MAIN01", "quantity": 50 },
      { "branch__id": 2, "branch__name": "Norte", "branch__code": "NORTE01", "quantity": 100 }
    ]
  }
]
```

**Error 403**: Si el usuario no es Administrador General.

---

## Solicitudes de Ajuste de Stock

### Listar Solicitudes
**M\u00e9todo**: `GET`  
**Endpoint**: `/api/stock-adjustments/`  
**Filtros**: `?status=PENDING&branch=1&adjustment_type=ADDITION`  
**Ordenamiento**: `?ordering=-created_at`

**Response**:
```json
[
  {
    "id": 1,
    "company": 1,
    "branch": 1,
    "branch_name": "Sucursal Centro",
    "product": 1,
    "product_data": {
      "id": 1,
      "name": "Camisa Slim Fit",
      "brand": { "id": 2, "name": "Nike" },
      "category": { "id": 1, "name": "Ropa" },
      "sale_price": "$100.00",
      "is_active": true
    },
    "adjustment_type": "ADDITION",
    "quantity": 10,
    "reason": "Ingreso de mercanc\u00eda",
    "status": "PENDING",
    "requested_by": 2,
    "requested_by_name": "Juan P\u00e9rez",
    "approved_by": null,
    "approved_by_name": "",
    "rejection_note": "",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
]
```

### Crear Solicitud de Ajuste
**M\u00e9todo**: `POST`  
**Endpoint**: `/api/stock-adjustments/`  
**Descripci\u00f3n**: Crea una solicitud PENDIENTE de ajuste de stock. El `company`, `branch`, `requested_by` y `status=PENDING` se asignan autom\u00e1ticamente.

**Request**:
```json
{
  "product": 1,
  "adjustment_type": "ADDITION",
  "quantity": 10,
  "reason": "Ingreso de mercanc\u00eda nueva"
}
```

> `adjustment_type` puede ser:
> - `ADDITION` &ndash; Suma al stock
> - `REDUCTION` &ndash; Resta del stock
> - `CORRECTION` &ndash; Corrige al valor exacto indicado

**Errores comunes**:
- `400 Bad Request` &ndash; Si el usuario no tiene sucursal asignada.

### Obtener Solicitud
**M\u00e9todo**: `GET`  
**Endpoint**: `/api/stock-adjustments/<int:pk>/`  
**Ejemplo**: `/api/stock-adjustments/1/`

### Aprobar Solicitud (Solo Admin General)
**M\u00e9todo**: `POST`  
**Endpoint**: `/api/stock-adjustments/<int:pk>/approve/`  
**Ejemplo**: `/api/stock-adjustments/1/approve/`  
**Descripci\u00f3n**: Aprueba la solicitud, aplica el ajuste al inventario y crea un `StockMovement` de auditor\u00eda.

**Errores comunes**:
- `403 Forbidden` &ndash; El usuario no es Administrador General.
- `400 Bad Request` &ndash; La solicitud no est\u00e1 en estado `PENDING`.
- `400 Bad Request` &ndash; No existe registro de inventario para ese producto y sucursal.
- `400 Bad Request` &ndash; Stock insuficiente para una reducci\u00f3n.

**Response**: Objeto `StockAdjustmentRequest` con `status: "APPROVED"`.

### Rechazar Solicitud (Solo Admin General)
**M\u00e9todo**: `POST`  
**Endpoint**: `/api/stock-adjustments/<int:pk>/reject/`  
**Ejemplo**: `/api/stock-adjustments/1/reject/`

**Request**:
```json
{
  "rejection_note": "El stock ya fue verificado manualmente."
}
```

**Response**: Objeto `StockAdjustmentRequest` con `status: "REJECTED"`.

---

## Movimientos de Stock (Auditor\u00eda)

### Listar Movimientos
**M\u00e9todo**: `GET`  
**Endpoint**: `/api/stock-movements/`  
**Descripci\u00f3n**: Solo lectura. Registro de auditor\u00eda de todos los cambios de stock.  
**Filtros**: `?branch=1&movement_type=ADJUSTMENT&product=1`  
**Ordenamiento**: `?ordering=-created_at`

**Response**:
```json
[
  {
    "id": 1,
    "company": 1,
    "branch": 1,
    "branch_name": "Sucursal Centro",
    "product": 1,
    "product_data": {
      "id": 1,
      "name": "Camisa Slim Fit",
      "brand": { "id": 2, "name": "Nike" },
      "category": { "id": 1, "name": "Ropa" },
      "sale_price": "$100.00",
      "is_active": true
    },
    "movement_type": "ADJUSTMENT",
    "previous_quantity": 40,
    "new_quantity": 50,
    "quantity_change": 10,
    "reference_id": 3,
    "reference_model": "StockAdjustmentRequest",
    "notes": "Approved adjustment: Ingreso de mercanc\u00eda",
    "created_by": 1,
    "created_by_name": "Admin General",
    "created_at": "2025-01-15T11:00:00Z"
  }
]
```

> Los tipos de movimiento (`movement_type`) son: `SALE`, `ADJUSTMENT`, `TRANSFER`, `RETURN`, `CORRECTION`.

### Obtener Movimiento
**M\u00e9todo**: `GET`
**Endpoint**: `/api/stock-movements/<int:pk>/`
**Ejemplo**: `/api/stock-movements/1/`

---

## Transferencias de Stock

### Listar Transferencias
**M\u00e9todo**: `GET`
**Endpoint**: `/api/stock-transfers/`
**Filtros**: `?status=PENDING&origin_branch=1&destination_branch=2&date_from=2025-01-01&date_to=2025-03-01`
**Ordenamiento**: `?ordering=-created_at`

**Response**:
```json
[
  {
    "id": 1,
    "company": 1,
    "origin_branch": 1,
    "origin_branch_name": "Sucursal Centro",
    "destination_branch": 2,
    "destination_branch_name": "Sucursal Norte",
    "status": "PENDING",
    "requested_by": 2,
    "requested_by_name": "Juan P\u00e9rez",
    "approved_by": null,
    "approved_by_name": "",
    "rejection_note": "",
    "notes": "Reposici\u00f3n de stock",
    "total_items": 3,
    "total_units": 15,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "details": [
      {
        "id": 1,
        "transfer": 1,
        "product": 1,
        "product_data": {
          "id": 1,
          "name": "Camisa Slim Fit",
          "brand": { "id": 2, "name": "Nike" },
          "category": { "id": 1, "name": "Ropa" },
          "sale_price": "$100.00",
          "is_active": true
        },
        "quantity": 5,
        "origin_stock_before": null,
        "origin_stock_after": null
      }
    ]
  }
]
```

> `status` puede ser: `PENDING`, `IN_TRANSIT`, `COMPLETED`, `REJECTED`

### Crear Transferencia
**M\u00e9todo**: `POST`
**Endpoint**: `/api/stock-transfers/`
**Descripci\u00f3n**: Crear solicitud de transferencia. `company` y `requested_by` se asignan autom\u00e1ticamente.

**Request**:
```json
{
  "origin_branch": 1,
  "destination_branch": 2,
  "notes": "Reposici\u00f3n de stock semanal",
  "details": [
    { "product": 1, "quantity": 5 },
    { "product": 3, "quantity": 10 }
  ]
}
```

> **Validaciones**: `origin_branch` y `destination_branch` deben ser diferentes. Al menos un `detail` requerido.

### Obtener Transferencia
**M\u00e9todo**: `GET`
**Endpoint**: `/api/stock-transfers/<int:pk>/`
**Ejemplo**: `/api/stock-transfers/1/`

### Aprobar Transferencia (Solo Admin)
**M\u00e9todo**: `POST`
**Endpoint**: `/api/stock-transfers/<int:pk>/approve/`
**Ejemplo**: `/api/stock-transfers/1/approve/`
**Descripci\u00f3n**: Aprueba la transferencia, descuenta stock de la sucursal origen y cambia estado a `IN_TRANSIT`.

**Validaciones**:
- Solo Administradores Generales pueden aprobar
- La transferencia debe estar en estado `PENDING`
- Stock suficiente en la sucursal origen para cada producto

**Response**: Objeto `StockTransfer` con `status: "IN_TRANSIT"`

**Errores**:
- `403 Forbidden` \u2013 El usuario no es Administrador General
- `400 Bad Request` \u2013 Estado incorrecto o stock insuficiente

### Rechazar Transferencia (Solo Admin)
**M\u00e9todo**: `POST`
**Endpoint**: `/api/stock-transfers/<int:pk>/reject/`
**Ejemplo**: `/api/stock-transfers/1/reject/`

**Request**:
```json
{
  "rejection_note": "Stock no disponible actualmente"
}
```

**Response**: Objeto `StockTransfer` con `status: "REJECTED"`

### Completar Transferencia
**M\u00e9todo**: `POST`
**Endpoint**: `/api/stock-transfers/<int:pk>/complete/`
**Ejemplo**: `/api/stock-transfers/1/complete/`
**Descripci\u00f3n**: Completa la transferencia sumando stock en la sucursal destino.

**Validaciones**:
- La transferencia debe estar en estado `IN_TRANSIT`

**Response**: Objeto `StockTransfer` con `status: "COMPLETED"`

---

## Ventas

### Listar Ventas
**Método**: `GET`  
**Endpoint**: `/api/sales/`  
**Filtros**: `?closed=true&pay_method=1&seller=2&payment_status=PAID&canceled=false`  
**Búsqueda**: `?search=Juan` (busca en nombre/apellido/dni del cliente)

**Response**:
```json
[
  {
    "id": 1,
    "seller": 2,
    "seller_name": "Juan Pérez",
    "client": 1,
    "client_data": {
      "id": 1,
      "name": "María",
      "last_name": "González",
      "dni": "87654321"
    },
    "total_amount": "150.00",
    "formatted_total_amount": "$150.00",
    "pay_method": 1,
    "payment_status": "PAID",
    "is_credit_sale": false,
    "account_record_id": null,
    "cash_session": 5,
    "cash_session_data": {
      "id": 5,
      "cash_register": "Caja Principal",
      "opening_date": "2025-01-15T08:00:00Z",
      "status": "OPEN"
    },
    "canceled": false,
    "closed": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:15:00Z",
    "details": [
      {
        "id": 1,
        "order": 1,
        "product": 1,
        "product_data": {
          "id": 1,
          "name": "Camisa Slim Fit"
        },
        "quantity": 2,
        "sale_price": "50.00",
        "cost_price": "25.00",
        "formatted_sale_price": "$50.00",
        "formatted_cost_price": "$25.00",
        "formatted_total_price": "$100.00",
        "profit": "50.00",
        "profit_margin": "50.00%",
        "created_at": "2025-01-15T10:00:00Z"
      }
    ]
  }
]
```

### Crear Venta
**Método**: `POST`  
**Endpoint**: `/api/sales/`  
**Descripción**: Crear nueva venta (automáticamente asigna seller=usuario actual)

**Request**:
```json
{
  "client": 1,
  "pay_method": 1
}
```

> **Nota**: Los detalles (items) se agregan con el endpoint `/sale-details/` después de crear la venta.

### Obtener Venta
**Método**: `GET`  
**Endpoint**: `/api/sales/<int:pk>/`  
**Ejemplo**: `/api/sales/1/`

### Cerrar Venta
**Método**: `POST`  
**Endpoint**: `/api/sales/<int:pk>/close/`  
**Ejemplo**: `/api/sales/1/close/`  
**Descripción**: Cerrar y confirmar una venta (actualiza inventario, crea movimientos)

**Response**: Retorna la venta completa con `closed: true`

### Cancelar Venta
**Método**: `POST`  
**Endpoint**: `/api/sales/<int:pk>/cancel/`  
**Ejemplo**: `/api/sales/1/cancel/`  
**Descripción**: Cancelar una venta y restaurar el stock al inventario de la sucursal correspondiente.

**Response**: Retorna la venta completa con `canceled: true`

### Resumen de Ventas
**Método**: `GET`  
**Endpoint**: `/api/sales/summary/`  
**Descripción**: Métricas generales de ventas  
**Filtros**: `?branch=1&date_from=2025-01-01&date_to=2025-03-01`

**Response**:
```json
{
  "total_sales": 15000.00,
  "total_transactions": 45,
  "average_ticket": 333.33,
  "total_products_sold": 120,
  "total_profit": 7500.00
}
```

### Resumen por Sucursal (Solo Admin General)
**Método**: `GET`  
**Endpoint**: `/api/sales/summary-by-branch/`  
**Descripción**: Métricas agrupadas por sucursal. Solo disponible para Administradores Generales.  
**Filtros**: `?date_from=2025-01-01&date_to=2025-03-01`

**Response**:
```json
[
  {
    "branch_id": 1,
    "branch_name": "Sucursal Centro",
    "branch_code": "MAIN01",
    "total_sales": 10000.00,
    "total_transactions": 30,
    "average_ticket": 333.33,
    "total_profit": 5000.00
  }
]
```

**Error 403**: Si el usuario no es Administrador General.

### Top Productos
**Método**: `GET`  
**Endpoint**: `/api/sales/top-products/`  
**Filtro**: `?limit=5` (por defecto: 5)  
**Descripción**: Productos más vendidos

**Response**:
```json
[
  {
    "product__name": "Camisa Slim Fit",
    "product_name": "Camisa Slim Fit",
    "total_quantity": 50,
    "total_revenue": "5000.00"
  }
]
```

### Ventas por Categoría
**Método**: `GET`  
**Endpoint**: `/api/sales/by-category/`

**Response**:
```json
[
  {
    "product__category__name": "Ropa",
    "name": "Ropa",
    "value": "25000.00"
  }
]
```

### Ventas por Día
**Método**: `GET`  
**Endpoint**: `/api/sales/by-day/`  
**Descripción**: Últimos 7 días

**Response**:
```json
[
  {
    "day": "Mon",
    "full_date": "2025-01-13",
    "ventas": "5000.00",
    "productos": 15
  }
]
```

### Ventas por Mes
**Método**: `GET`  
**Endpoint**: `/api/sales/by-month/`  
**Descripción**: Últimos 6 meses

**Response**:
```json
[
  {
    "month": "Jan",
    "full_date": "2025-01",
    "ventas": "50000.00",
    "transacciones": 150
  }
]
```

---

### Detalles de Venta (Sale Details)

#### Listar Detalles
**Método**: `GET`  
**Endpoint**: `/api/sale-details/`

#### Crear Detalle
**Método**: `POST`  
**Endpoint**: `/api/sale-details/`  
**Descripción**: Agregar producto a una venta

**Request**:
```json
{
  "order": 1,
  "product": 2,
  "quantity": 3
}
```

> **Nota**: Los campos `sale_price` y `cost_price` son read-only, se copian automáticamente del producto.

---

### Métodos de Pago

**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/pay-methods/`

**Response (GET)**:
```json
[
  {
    "id": 1,
    "name": "Efectivo",
    "description": "Pago en efectivo"
  }
]
```

---

## Devoluciones

> Los diferentes serializers según la acción:
> - **Listado** (`GET /returns/`): `ReturnListSerializer` (resumen)
> - **Detalle** (`GET /returns/{id}/`): `ReturnDetailResponseSerializer` (con details y refunds anidados)
> - **Crear** (`POST /returns/`): `ReturnCreateSerializer` (escritura con details/refunds inline)

### Listar Devoluciones
**Método**: `GET`
**Endpoint**: `/api/returns/`
**Filtros**: `?status=COMPLETED&branch=1&sale=5&reason_type=DEFECTIVE&cash_session=3&date_from=2025-01-01&date_to=2025-03-01`
**Búsqueda**: `?search=notas` (busca en reason_notes, nombre/apellido del cliente)
**Ordenamiento**: `?ordering=-created_at` o `?ordering=total_refund_amount`

**Response**:
```json
[
  {
    "id": 1,
    "sale": 5,
    "sale_client_name": "María González",
    "branch": 1,
    "branch_name": "Sucursal Centro",
    "cash_session": 3,
    "status": "COMPLETED",
    "reason_display": "Defective / Damaged",
    "reason_type": "DEFECTIVE",
    "reason_notes": "Producto con defecto de fábrica",
    "total_refund_amount": "150.00",
    "processed_by": 2,
    "processed_by_name": "Juan Pérez",
    "authorized_by": null,
    "authorized_by_name": "",
    "created_at": "2025-01-15T14:00:00Z",
    "updated_at": "2025-01-15T14:00:00Z"
  }
]
```

### Crear Devolución
**Método**: `POST`
**Endpoint**: `/api/returns/`
**Descripción**: Registrar una devolución sobre una venta cerrada. `company`, `branch`, `cash_session` y `processed_by` se asignan automáticamente.

**Request**:
```json
{
  "sale": 5,
  "reason_type": "DEFECTIVE",
  "reason_notes": "Producto con defecto de fábrica",
  "details": [
    {
      "sale_detail": 10,
      "product": 1,
      "quantity": 1,
      "unit_price": "100.00",
      "subtotal": "100.00",
      "condition": "DAMAGED",
      "restock": false
    }
  ],
  "refunds": [
    {
      "refund_method": "CASH",
      "amount": "100.00"
    }
  ]
}
```

> **Validaciones**:
> - La venta debe estar `closed=True` y `canceled=False`
> - Cada `quantity` en details no puede exceder lo disponible para devolver
> - La suma de `refunds[].amount` debe ser igual a la suma de `details[].subtotal`
> - `reason_type`: `DEFECTIVE`, `WRONG_ITEM`, `NOT_NEEDED`, `OTHER`
> - `condition`: `RESALEABLE`, `DAMAGED`
> - `refund_method`: `CASH`, `STORE_CREDIT`, `ORIGINAL_METHOD`

**Response** `201`: Objeto Return con `total_refund_amount` calculado.

### Obtener Devolución (Detalle)
**Método**: `GET`
**Endpoint**: `/api/returns/<int:pk>/`
**Ejemplo**: `/api/returns/1/`
**Descripción**: Retorna la devolución con `details` y `refunds` anidados.

**Response**:
```json
{
  "id": 1,
  "sale": 5,
  "sale_client_name": "María González",
  "branch": 1,
  "branch_name": "Sucursal Centro",
  "status": "COMPLETED",
  "reason_type": "DEFECTIVE",
  "reason_notes": "Producto con defecto de fábrica",
  "total_refund_amount": "100.00",
  "processed_by_name": "Juan Pérez",
  "details": [
    {
      "id": 1,
      "return_obj": 1,
      "sale_detail": 10,
      "product": 1,
      "product_name": "Camisa Slim Fit",
      "quantity": 1,
      "unit_price": "100.00",
      "subtotal": "100.00",
      "condition": "DAMAGED",
      "restock": false
    }
  ],
  "refunds": [
    {
      "id": 1,
      "return_obj": 1,
      "refund_method": "CASH",
      "pay_method": null,
      "pay_method_name": "",
      "amount": "100.00",
      "account_record": null
    }
  ],
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:00:00Z"
}
```

### Cancelar Devolución
**Método**: `POST`
**Endpoint**: `/api/returns/<int:pk>/cancel/`
**Ejemplo**: `/api/returns/1/cancel/`
**Descripción**: Revierte una devolución completada. Si los items tenían `restock=True`, se descuenta el stock restaurado.

**Response**: Objeto Return con `status: "CANCELED"`

**Errores**:
- `400 Bad Request` – Solo se pueden cancelar devoluciones con estado `COMPLETED`

### Resumen de Devoluciones
**Método**: `GET`
**Endpoint**: `/api/returns/summary/`
**Filtros**: `?date_from=2025-01-01&date_to=2025-03-01`

**Response**:
```json
{
  "total_returns": 12,
  "total_refund_amount": "3500.00",
  "total_items_returned": 25,
  "total_restocked": 20,
  "by_reason": [
    { "reason": "DEFECTIVE", "count": 5 },
    { "reason": "WRONG_ITEM", "count": 4 }
  ],
  "by_refund_method": [
    { "method": "CASH", "total": "2000.00" },
    { "method": "ORIGINAL_METHOD", "total": "1500.00" }
  ]
}
```

---

## Caja

### Cajas Registradoras

> **Nota**: CashRegister ahora hereda de Device. Ver sección [Dispositivos](#dispositivos) para gestión completa.

#### Listar Cajas (desde devices)
**Método**: `GET`  
**Endpoint**: `/api/devices/cash_registers/`  
**Descripción**: Obtener solo cajas registradoras activas

**Response**:
```json
[
  {
    "id": 1,
    "code": "CAJA-01",
    "name": "Caja Principal",
    "location": "Mostrador 1",
    "model": "HP EliteDesk",
    "serial_number": "SN123456",
    "ip_address": "192.168.1.10",
    "mac_address": "00:1B:44:11:3A:B7",
    "is_active": true,
    "is_online": true,
    "last_seen": "2025-01-15T10:00:00Z",
    "assigned_user": 2,
    "assigned_user_data": {
      "id": 2,
      "username": "juan",
      "first_name": "Juan",
      "last_name": "Pérez"
    },
    "assigned_date": "2025-01-15T08:00:00Z",
    "configurations": [],
    "notes": "",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "polymorphic_ctype": 15,
    "current_session_id": 5,
    "has_open_session": true
  }
]
```

---

### Sesiones de Caja

#### Listar Sesiones
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/`  
**Filtros**: `?status=OPEN&cash_register=1&user=2`  
**Ordenamiento**: `?ordering=-opening_date`

**Response (List - simplificado)**:
```json
[
  {
    "id": 5,
    "cash_register": 1,
    "cash_register_name": "Caja Principal",
    "user": 2,
    "user_name": "Juan Pérez",
    "status": "OPEN",
    "opening_date": "2025-01-15T08:00:00Z",
    "closing_date": null,
    "opening_balance": "1000.00",
    "closing_balance": null
  }
]
```

#### Obtener Sesión (Detalle completo)
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/<int:pk>/`  
**Ejemplo**: `/api/cash/sessions/5/`

**Response (Detail - completo)**:
```json
{
  "id": 5,
  "cash_register": 1,
  "cash_register_data": {
    "id": 1,
    "code": "CAJA-01",
    "name": "Caja Principal",
    "has_open_session": true,
    "current_session_id": 5
  },
  "user": 2,
  "user_data": {
    "id": 2,
    "username": "juan",
    "first_name": "Juan",
    "last_name": "Pérez"
  },
  "status": "OPEN",
  "opening_date": "2025-01-15T08:00:00Z",
  "closing_date": null,
  "opening_balance": "1000.00",
  "closing_balance": null,
  "total_cash_sales": "4000.00",
  "total_cash_in": "500.00",
  "total_cash_out": "100.00",
  "expected_balance": "5400.00",
  "difference": "0.00",
  "sales_count": 15,
  "notes": "",
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-01-15T08:00:00Z"
}
```

#### Abrir Sesión
**Método**: `POST`  
**Endpoint**: `/api/cash/sessions/open/`  
**Descripción**: Abrir nueva sesión (automáticamente asigna user=usuario actual)

**Request**:
```json
{
  "cash_register": 1,
  "opening_balance": "1000.00"
}
```

**Validaciones**:
- La caja debe estar activa (`is_active=true`)
- El usuario no puede tener otra sesión abierta
- La caja no puede tener otra sesión abierta

**Response**: Retorna sesión completa (formato Detail)

#### Cerrar Sesión
**Método**: `POST`  
**Endpoint**: `/api/cash/sessions/<int:pk>/close/`  
**Ejemplo**: `/api/cash/sessions/5/close/`  
**Descripción**: Cerrar sesión de caja

**Request**:
```json
{
  "closing_balance": "5500.00",
  "notes": "Cierre normal sin novedades"
}
```

**Validaciones**:
- La sesión debe estar abierta (`status=OPEN`)
- Solo el dueño de la sesión o admin puede cerrarla

**Response**: Retorna sesión completa con `difference` calculado

#### Mi Sesión Activa
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/my_active/`  
**Descripción**: Obtener sesión abierta del usuario actual

**Response**: Sesión completa o 404 si no tiene sesión abierta

#### Ventas de Sesión
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/<int:pk>/sales/`  
**Ejemplo**: `/api/cash/sessions/5/sales/`  
**Descripción**: Ventas cerradas y no canceladas de esta sesión

**Response**: Array de ventas (formato `SaleSerializer`)

#### Movimientos de Sesión
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/<int:pk>/movements/`  
**Ejemplo**: `/api/cash/sessions/5/movements/`

**Response**:
```json
[
  {
    "id": 1,
    "cash_session": 5,
    "type": "OPENING",
    "type_display": "Apertura",
    "amount": "1000.00",
    "reason": "Opening balance",
    "description": "",
    "created_by": 2,
    "created_by_name": "Juan Pérez",
    "created_at": "2025-01-15T08:00:00Z"
  },
  {
    "id": 2,
    "cash_session": 5,
    "type": "CASH_IN",
    "type_display": "Ingreso de efectivo",
    "amount": "500.00",
    "reason": "Cambio adicional",
    "description": "Cambio para el turno",
    "created_by": 2,
    "created_by_name": "Juan Pérez",
    "created_at": "2025-01-15T09:00:00Z"
  }
]
```

#### Resumen de Sesión
**Método**: `GET`  
**Endpoint**: `/api/cash/sessions/<int:pk>/summary/`  
**Ejemplo**: `/api/cash/sessions/5/summary/`

**Response**:
```json
{
  "session": {
    "id": 5,
    "cash_register": 1,
    "user": 2,
    "status": "OPEN"
  },
  "totals": {
    "opening_balance": "1000.00",
    "cash_sales": "4000.00",
    "cash_in": "500.00",
    "cash_out": "100.00",
    "expected_balance": "5400.00",
    "closing_balance": null,
    "difference": "0.00",
    "sales_count": 15
  }
}
```

---

### Movimientos de Efectivo

#### Listar Movimientos
**Método**: `GET`  
**Endpoint**: `/api/cash/movements/`  
**Filtros**: `?cash_session=5&type=CASH_IN`  
**Ordenamiento**: `?ordering=-created_at`

#### Crear Movimiento
**Método**: `POST`  
**Endpoint**: `/api/cash/movements/`  
**Descripción**: Registrar entrada/salida de efectivo (created_by se asigna automáticamente)

**Request**:
```json
{
  "cash_session": 5,
  "type": "CASH_IN",
  "amount": "500.00",
  "reason": "Cambio adicional",
  "description": "Cambio para operar en el turno"
}
```

**Tipos válidos**: `OPENING`, `CLOSING`, `CASH_IN`, `CASH_OUT`, `EXPENSE`

**Validación**: La sesión debe estar abierta (`status=OPEN`)

---

## Dispositivos

> **Sistema polimórfico**: Usa `django-polymorphic` para herencia type-safe.
> - **Device**: Clase base
> - **CashRegister**: Caja registradora (hereda de Device)
> - **PriceChecker**: Terminal de consulta de precios
> - **StockTerminal**: Terminal de gestión de stock

### Listar Dispositivos
**Método**: `GET`  
**Endpoint**: `/api/devices/`  
**Descripción**: Lista todos los dispositivos (polimórfico, retorna tipo correcto)  
**Filtros**: `?is_active=true&is_online=true&assigned_user=2`  
**Búsqueda**: `?search=CAJA` (busca en code, name, location, serial_number)  
**Ordenamiento**: `?ordering=name` o `?ordering=-last_seen`

**Response (List - simplificada)**:
```json
[
  {
    "id": 1,
    "code": "CAJA-01",
    "name": "Caja Principal",
    "device_type": "CashRegister",
    "location": "Mostrador 1",
    "is_active": true,
    "is_online": true,
    "assigned_user_name": "Juan Pérez",
    "last_seen": "2025-01-15T10:00:00Z"
  },
  {
    "id": 2,
    "code": "PC-01",
    "name": "Price Checker 1",
    "device_type": "PriceChecker",
    "location": "Pasillo A",
    "is_active": true,
    "is_online": false,
    "assigned_user_name": null,
    "last_seen": "2025-01-14T18:00:00Z"
  }
]
```

### Crear Dispositivo
**Método**: `POST`  
**Endpoint**: `/api/devices/`  
**Descripción**: Crear dispositivo (tipo determinado por `resourcetype`)

**Request (CashRegister)**:
```json
{
  "resourcetype": "CashRegister",
  "code": "CAJA-02",
  "name": "Caja Secundaria",
  "location": "Mostrador 2",
  "model": "Dell OptiPlex",
  "serial_number": "SN7890",
  "ip_address": "192.168.1.20",
  "mac_address": "00:1B:44:11:3A:B8",
  "is_active": true,
  "notes": ""
}
```

**Request (PriceChecker)**:
```json
{
  "resourcetype": "PriceChecker",
  "code": "PC-02",
  "name": "Price Checker 2",
  "location": "Pasillo B",
  "display_promotions": true,
  "timeout_seconds": 45,
  "is_active": true
}
```

**Request (StockTerminal)**:
```json
{
  "resourcetype": "StockTerminal",
  "code": "ST-01",
  "name": "Stock Terminal 1",
  "location": "Depósito",
  "can_receive_shipments": true,
  "require_photo": true,
  "is_active": true
}
```

### Obtener Dispositivo
**Método**: `GET`  
**Endpoint**: `/api/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/1/`  
**Descripción**: Retorna el serializer correcto según el tipo

**Response (CashRegister)**:
```json
{
  "id": 1,
  "code": "CAJA-01",
  "name": "Caja Principal",
  "location": "Mostrador 1",
  "model": "HP EliteDesk",
  "serial_number": "SN123456",
  "ip_address": "192.168.1.10",
  "mac_address": "00:1B:44:11:3A:B7",
  "is_active": true,
  "is_online": true,
  "last_seen": "2025-01-15T10:00:00Z",
  "assigned_user": 2,
  "assigned_user_data": {
    "id": 2,
    "username": "juan",
    "email": "juan@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-01-01T00:00:00Z",
    "profile": null
  },
  "assigned_date": "2025-01-15T08:00:00Z",
  "configurations": [],
  "notes": "",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "polymorphic_ctype": 15,
  "current_session_id": 5,
  "has_open_session": true
}
```

**Response (PriceChecker)**:
```json
{
  "id": 2,
  "code": "PC-01",
  "name": "Price Checker 1",
  "location": "Pasillo A",
  "model": null,
  "serial_number": null,
  "ip_address": "192.168.1.30",
  "mac_address": null,
  "is_active": true,
  "is_online": false,
  "last_seen": "2025-01-14T18:00:00Z",
  "assigned_user": null,
  "assigned_user_data": null,
  "assigned_date": null,
  "configurations": [
    {
      "id": 1,
      "key": "theme",
      "value": "dark",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "notes": "",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-14T18:00:00Z",
  "polymorphic_ctype": 16,
  "display_promotions": true,
  "timeout_seconds": 30
}
```

### Actualizar Dispositivo
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/1/`

### Eliminar Dispositivo
**Método**: `DELETE`  
**Endpoint**: `/api/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/1/`

### Heartbeat (Check-in)
**Método**: `POST`  
**Endpoint**: `/api/devices/<int:pk>/heartbeat/`  
**Ejemplo**: `/api/devices/1/heartbeat/`  
**Descripción**: Registrar que el dispositivo está activo (actualiza `last_seen` e `is_online`)

**Request**: Vacío

**Response**:
```json
{
  "timestamp": "2025-01-15T10:05:00Z",
  "message": "Heartbeat received from Caja Principal"
}
```

### Asignar Usuario
**Método**: `POST`  
**Endpoint**: `/api/devices/<int:pk>/assign/`  
**Ejemplo**: `/api/devices/1/assign/`  
**Descripción**: Asignar dispositivo a un usuario

**Request**:
```json
{
  "user_id": 2
}
```

**Response**: Dispositivo completo con usuario asignado

### Desasignar Usuario
**Método**: `POST`  
**Endpoint**: `/api/devices/<int:pk>/unassign/`  
**Ejemplo**: `/api/devices/1/unassign/`

**Response**: Dispositivo completo con `assigned_user: null`

### Cajas Registradoras
**Método**: `GET`  
**Endpoint**: `/api/devices/cash_registers/`  
**Descripción**: Solo CashRegister activos

**Response**: Array de `CashRegisterSerializer` (con `current_session_id` y `has_open_session`)

### Terminales de Precio
**Método**: `GET`  
**Endpoint**: `/api/devices/price_checkers/`  
**Descripción**: Solo PriceChecker activos

**Response**: Array de `PriceCheckerSerializer` (con `display_promotions` y `timeout_seconds`)

### Terminales de Stock
**Método**: `GET`  
**Endpoint**: `/api/devices/stock_terminals/`  
**Descripción**: Solo StockTerminal activos

**Response**: Array de `StockTerminalSerializer` (con `can_receive_shipments` y `require_photo`)

### Dispositivos Online
**Método**: `GET`  
**Endpoint**: `/api/devices/online/`

**Response**: Array de `DeviceListSerializer` donde `is_online=true`

### Dispositivos Offline
**Método**: `GET`  
**Endpoint**: `/api/devices/offline/`

**Response**: Array de `DeviceListSerializer` donde `is_online=false`

### Resumen de Dispositivos
**Método**: `GET`  
**Endpoint**: `/api/devices/summary/`

**Response**:
```json
{
  "total": 10,
  "active": 8,
  "online": 6,
  "offline": 2,
  "by_type": {
    "cash_registers": 4,
    "price_checkers": 3,
    "stock_terminals": 3
  }
}
```

---

## Usuarios

### Roles Existentes (Grupos)
**Método**: `GET`  
**Endpoint**: `/api/users/roles/`  
**Descripción**: Retorna la lista de roles (grupos) disponibles para asignar a un empleado (útil para llenar listas desplegables en el Frontend). Si el usuario autenticado no tiene rol `Administrador General`, se ocultará dicha opción de la lista para evitar que eleve privilegios.

**Response**:
```json
[
  {
    "id": 2,
    "name": "Gerente"
  },
  {
    "id": 3,
    "name": "Administrativo"
  },
  {
    "id": 4,
    "name": "Cajero"
  }
]
```

### Listar Usuarios
**Método**: `GET`  
**Endpoint**: `/api/users/`  
**Filtros**: `?search=nombre&ordering=date_joined`

**Response**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-01-01T00:00:00Z",
    "profile": {
      "id": 1,
      "user": 1,
      "phone_number": "+54 351 1234567",
      "dni": "12345678",
      "address": "Calle Falsa 123",
      "city": "Córdoba",
      "province": "Córdoba",
      "postal_code": "5000",
      "country": "Argentina",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    },
    "company": 1,
    "groups_names": ["Administrador General"],
    "branches_names": ["Sucursal Centro"]
  }
]
```

### Registrar Empresa y Administrador
**Método**: `POST`  
**Endpoint**: `/api/users/register/`  
**Autenticación**: No requerida  
**Descripción**: Crea un nuevo usuario Administrador General y su correspondiente Empresa (tenant).

**Request**:
```json
{
  "username": "admin_empresa",
  "email": "contacto@miempresa.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "company_name": "Mi Empresa S.A.",
  "company_tax_id": "30-12345678-9"
}
```

**Response** `201`:
```json
{
  "id": 1,
  "username": "admin_empresa",
  "email": "contacto@miempresa.com",
  "company_id": 1,
  "company_name": "Mi Empresa S.A.",
  "message": "User registered successfully"
}
```

**Errores comunes**:
- `400 Bad Request` – Las contraseñas no coinciden.
- `400 Bad Request` – El username o email ya está en uso.

### Crear Empleado (Usuario Dependiente)
**Método**: `POST`  
**Endpoint**: `/api/users/employees/`  
**Descripción**: Crea un empleado para la empresa actual. Asigna roles y sucursales.  
**Requiere rol**: `Administrador General` o `Gerente`

**Request**:
```json
{
  "username": "cajero_01",
  "email": "cajero@miempresa.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "Carlos",
  "last_name": "López",
  "groups_ids": [2],
  "branches_ids": [1]
}
```

**Response** `201`:
```json
{
  "id": 3,
  "username": "cajero_01",
  "email": "cajero@miempresa.com",
  "first_name": "Carlos",
  "last_name": "López",
  "company_id": 1,
  "groups": ["Gerente"],
  "branches": ["Sucursal Centro"],
  "message": "Employee created successfully"
}
```

**Errores comunes**:
- `400 Bad Request` – El usuario solicitante no tiene compañía asignada.
- `400 Bad Request` – `groups_ids` o `branches_ids` contienen IDs inválidos.
- `400 Bad Request` – Se intenta asignar el rol `Administrador General` sin tenerlo.

### Actualizar Empleado
**Método**: `PUT` / `PATCH`  
**Endpoint**: `/api/users/<int:pk>/employee/`  
**Ejemplo**: `/api/users/3/employee/`  
**Requiere rol**: `Administrador General` o `Gerente`

**Request**:
```json
{
  "first_name": "Carlos Andrés",
  "groups_ids": [2],
  "branches_ids": [1, 2]
}
```

**Response** `200`:
```json
{
  "id": 3,
  "username": "cajero_01",
  "email": "cajero@miempresa.com",
  "first_name": "Carlos Andrés",
  "last_name": "López",
  "groups": ["Gerente"],
  "branches": ["Sucursal Centro", "Sucursal Norte"],
  "message": "Employee updated successfully"
}
```

**Errores comunes**:
- `400 Bad Request` – El usuario solicitante no tiene compañía asignada.
- `403 Forbidden` – El empleado no pertenece a la misma compañía.

### Obtener Usuario
**Método**: `GET`  
**Endpoint**: `/api/users/<int:pk>/`  
**Ejemplo**: `/api/users/1/`

### Actualizar Usuario
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/users/<int:pk>/`  
**Ejemplo**: `/api/users/1/`

### Eliminar Usuario
**Método**: `DELETE`  
**Endpoint**: `/api/users/<int:pk>/`  
**Ejemplo**: `/api/users/1/`

---

## Codigos de Autorizacion

### Listar Codigos de Autorizacion
**Metodo**: `GET`
**Endpoint**: `/api/users/authorization-codes/`
**Descripcion**: Retorna todos los codigos de autorizacion de la empresa del usuario autenticado.
**Filtros**: `?is_active=true`
**Paginacion**: `?page=1&page_size=20`

**Response** `200`:
```json
[
  {
    "id": 1,
    "user": 2,
    "user_data": {
      "id": 2,
      "first_name": "Juan",
      "last_name": "Perez",
      "username": "jperez",
      "email": "juan@example.com"
    },
    "code": "SUP-001",
    "label": "Supervisor Turno Manana",
    "is_active": true,
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

### Crear Codigo de Autorizacion
**Metodo**: `POST`
**Endpoint**: `/api/users/authorization-codes/`
**Requiere rol**: `Administrador General` o `Gerente`

**Request**:
```json
{
  "user": 2,
  "code": "SUP-001",
  "label": "Supervisor Turno Manana",
  "is_active": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `user` | number | Si | ID del usuario supervisor |
| `code` | string | Si | Codigo de barras del supervisor |
| `label` | string | Si | Etiqueta descriptiva |
| `is_active` | boolean | No | Default `true` |

**Response** `201`: Mismo objeto que GET (con `id`, `user_data`, `created_at`, `updated_at`).

**Errores comunes**:
- `400 Bad Request` – Campos requeridos faltantes.
- `400 Bad Request` – Codigo duplicado dentro de la empresa.
- `400 Bad Request` – El usuario no pertenece a la misma empresa.

### Actualizar Codigo de Autorizacion
**Metodo**: `PATCH`
**Endpoint**: `/api/users/authorization-codes/<int:pk>/`
**Requiere rol**: `Administrador General` o `Gerente`

**Request** (todos opcionales):
```json
{
  "user": 2,
  "code": "SUP-002",
  "label": "Nuevo label",
  "is_active": false
}
```

**Response** `200`: Objeto completo del codigo actualizado.

### Eliminar Codigo de Autorizacion
**Metodo**: `DELETE`
**Endpoint**: `/api/users/authorization-codes/<int:pk>/`
**Requiere rol**: `Administrador General` o `Gerente`

**Response** `204`: Sin contenido.

### Validar Codigo de Autorizacion
**Metodo**: `POST`
**Endpoint**: `/api/users/authorization-codes/validate-code/`
**Descripcion**: Valida un codigo de autorizacion (escaneo de codigo de barras).

**Request**:
```json
{
  "code": "SUP-001"
}
```

**Response** `200` (codigo valido):
```json
{
  "valid": true,
  "user": {
    "id": 2,
    "first_name": "Juan",
    "last_name": "Perez",
    "username": "jperez",
    "email": "juan@example.com"
  },
  "role_display": "Gerente"
}
```

**Response** `200` (codigo invalido):
```json
{
  "valid": false,
  "user": null,
  "role_display": null,
  "error": "Codigo no encontrado o inactivo"
}
```

---

## Registros de Auditoría

### Listar Registros
**Método**: `GET`
**Endpoint**: `/api/records/`
**Descripción**: Registros inmutables de auditoría de todas las acciones del sistema
**Filtros**: `?action=SALE_CREATED&branch=1&user=2`
**Búsqueda**: `?search=descripción`
**Ordenamiento**: `?ordering=-created_at`

**Response**:
```json
[
  {
    "id": 1,
    "company": 1,
    "branch": 1,
    "branch_name": "Sucursal Centro",
    "user": 2,
    "user_name": "Juan Pérez",
    "action": "SALE_CREATED",
    "action_display": "Sale Created",
    "ip_address": "192.168.1.50",
    "description": "Venta #5 creada",
    "details": {},
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

> **Tipos de acción (`action`)**: `SALE_CREATED`, `SALE_CANCELED`, `ADJUSTMENT_CREATED`, `ADJUSTMENT_APPROVED`, `ADJUSTMENT_REJECTED`, `RETURN_PROCESSED`, `RETURN_CANCELED`, `TRANSFER_CREATED`, `TRANSFER_APPROVED`, `TRANSFER_COMPLETED`, `PRICE_CHANGED`, `PRICE_BULK_UPDATE`, `CASH_SESSION_OPENED`, `CASH_SESSION_CLOSED`, `INVENTORY_UPDATED`, `SETTINGS_UPDATED`

### Obtener Registro
**Método**: `GET`
**Endpoint**: `/api/records/<int:pk>/`
**Ejemplo**: `/api/records/1/`

### Resumen de Auditoría
**Método**: `GET`
**Endpoint**: `/api/records/summary/`
**Descripción**: Resumen agregado de registros de auditoría
**Filtros**: `?date_from=2025-01-01&date_to=2025-03-01`

**Response**:
```json
{
  "total_records": 450,
  "by_action": [
    { "action": "SALE_CREATED", "count": 120 },
    { "action": "INVENTORY_UPDATED", "count": 85 }
  ],
  "by_user": [
    { "user_id": 2, "user_name": "Juan Pérez", "count": 200 },
    { "user_id": 3, "user_name": "María González", "count": 150 }
  ],
  "most_active_hours": [
    { "hour": 10, "count": 75 },
    { "hour": 11, "count": 68 }
  ]
}
```

---

## Notas Importantes

### Autenticación
Todos los endpoints (excepto `/token/` y `/token/refresh/`) requieren autenticación JWT:

```
Authorization: Bearer <access_token>
```

### Paginación
Endpoints de listado soportan paginación:
```
?page=1&page_size=20
```

### Búsqueda
Usar el parámetro `search`:
```
?search=término
```

### Ordenamiento
Usar el parámetro `ordering` (prefijo `-` para descendente):
```
?ordering=-created_at
?ordering=name
```

### Filtrado
Usar nombres de campos como parámetros:
```
?is_active=true&location=Mostrador 1
```

### Campos Read-Only
Muchos serializers tienen campos calculados o automáticos que son read-only:
- **Cash**: `total_cash_sales`, `expected_balance`, `difference`, `sales_count`
- **Sales**: `total_amount`, `seller`, `payment_status`, `formatted_*`
- **Products**: `internal_code`, `formatted_cost_price`, `formatted_sale_price`
- **Devices**: `is_online`, `last_seen`, `assigned_date`, `polymorphic_ctype`
- **Returns**: `company`, `branch`, `cash_session`, `processed_by`, `total_refund_amount`
- **StockTransfers**: `company`, `status`, `requested_by`, `approved_by`
- **CompanySettings**: `company` (read-only, auto-asignado)
- **PriceHistory**: Todos los campos son read-only (registro inmutable)
- **AuditRecord**: Todos los campos son read-only (registro inmutable)

Estos campos **no** deben incluirse en requests POST/PUT/PATCH.

### Validaciones Frontend
Implementar estas validaciones antes de enviar requests:
- **Productos**: `sale_price > cost_price`
- **Caja**: `closing_balance >= 0`, `opening_balance >= 0`
- **Clientes**: Email válido, DNI numérico
- **Dispositivos**: MAC address formato `XX:XX:XX:XX:XX:XX`


## Tipos de Datos (Modelos y Tipado Frontend)

A continuación se documentan los campos y relaciones de los modelos del sistema para facilitar la integración y la creación de interfaces estáticas en el Frontend (ej. TypeScript).

### `Company` (App: `core`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `name` | `CharField` | `string` |  |
| `legal_name` | `CharField` | `string` | Nombre legal de la empresa |
| `address` | `CharField` | `string` | Dirección de la empresa |
| `phone` | `CharField` | `string` | Teléfono de la empresa |
| `email` | `EmailField` | `string` | Email de la empresa |
| `tax_id` | `CharField` | `string | null` |  (Opcional) |
| `logo` | `FileField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `owner` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `CompanySettings` (App: `core`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `OneToOne -> Company` | `number` | Read-only, auto-asignado |
| `tax_name` | `CharField` | `string` | Default: `"IVA"` |
| `tax_rate` | `DecimalField` | `string` | Default: `"21.00"` |
| `tax_enabled` | `BooleanField` | `boolean` | Default: `true` |
| `currency_code` | `CharField` | `string` | Default: `"ARS"`, código ISO |
| `currency_symbol` | `CharField` | `string` | Default: `"$"` |
| `currency_decimals` | `PositiveSmallIntegerField` | `number` | Default: `2` |
| `receipt_header` | `TextField` | `string` | Texto superior del ticket |
| `receipt_footer` | `TextField` | `string` | Texto inferior del ticket |
| `receipt_show_tax` | `BooleanField` | `boolean` | Default: `true` |
| `allow_negative_stock` | `BooleanField` | `boolean` | Default: `false` |
| `low_stock_threshold` | `PositiveIntegerField` | `number` | Default: `5` |

### `PriceHistory` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `product` | `FK -> Product` | `number` | Producto asociado |
| `field` | `CharField` | `string` | `"sale_price"` o `"cost_price"` |
| `old_value` | `DecimalField` | `string` | Precio anterior |
| `new_value` | `DecimalField` | `string` | Precio nuevo |
| `change_percentage` | `DecimalField` | `number | null` | Porcentaje de cambio (Opcional) |
| `reason` | `CharField` | `string` | Motivo del cambio |
| `source` | `CharField` | `string` | `"MANUAL"` o `"BULK_UPDATE"` |
| `changed_by` | `FK -> CustomUser` | `number | null` | Usuario que realizó el cambio (Opcional) |
| `created_at` | `DateTimeField` | `string` | Formato ISO 8601 |

### `Return` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `sale` | `FK -> Sale` | `number` | Venta asociada |
| `branch` | `FK -> Branch` | `number` | Auto-asignado |
| `cash_session` | `FK -> CashSession` | `number | null` | Auto-asignado (Opcional) |
| `status` | `CharField` | `string` | `"COMPLETED"` o `"CANCELED"` |
| `reason_type` | `CharField` | `string` | `"DEFECTIVE"`, `"WRONG_ITEM"`, `"NOT_NEEDED"`, `"OTHER"` |
| `reason_notes` | `TextField` | `string` | Notas del motivo |
| `total_refund_amount` | `DecimalField` | `string` | Calculado automáticamente |
| `processed_by` | `FK -> CustomUser` | `number | null` | Auto-asignado (Opcional) |
| `authorized_by` | `FK -> CustomUser` | `number | null` | (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `ReturnDetail` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `return_obj` | `FK -> Return` | `number` | Devolución asociada |
| `sale_detail` | `FK -> SaleDetail` | `number` | Línea de venta original |
| `product` | `FK -> Product` | `number` | Producto devuelto |
| `quantity` | `PositiveIntegerField` | `number` | Cantidad devuelta |
| `unit_price` | `DecimalField` | `string` | Precio unitario |
| `subtotal` | `DecimalField` | `string` | Subtotal |
| `condition` | `CharField` | `string` | `"RESALEABLE"` o `"DAMAGED"` |
| `restock` | `BooleanField` | `boolean` | Si se restaura al inventario |

### `ReturnRefund` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `return_obj` | `FK -> Return` | `number` | Devolución asociada |
| `refund_method` | `CharField` | `string` | `"CASH"`, `"STORE_CREDIT"`, `"ORIGINAL_METHOD"` |
| `pay_method` | `FK -> PayMethod` | `number | null` | (Opcional) |
| `amount` | `DecimalField` | `string` | Monto del reembolso |
| `account_record` | `FK -> CustomerBalanceRecord` | `number | null` | (Opcional) |

### `StockTransfer` (App: `inventory`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `origin_branch` | `FK -> Branch` | `number` | Sucursal de origen |
| `destination_branch` | `FK -> Branch` | `number` | Sucursal de destino |
| `status` | `CharField` | `string` | `"PENDING"`, `"IN_TRANSIT"`, `"COMPLETED"`, `"REJECTED"` |
| `requested_by` | `FK -> CustomUser` | `number | null` | Auto-asignado (Opcional) |
| `approved_by` | `FK -> CustomUser` | `number | null` | (Opcional) |
| `rejection_note` | `TextField` | `string` | Nota de rechazo |
| `notes` | `TextField` | `string` | Notas generales |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `StockTransferDetail` (App: `inventory`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Auto-asignado |
| `transfer` | `FK -> StockTransfer` | `number` | Transferencia asociada |
| `product` | `FK -> Product` | `number` | Producto a transferir |
| `quantity` | `PositiveIntegerField` | `number` | Cantidad |
| `origin_stock_before` | `IntegerField` | `number | null` | Stock antes de extraer (Opcional) |
| `origin_stock_after` | `IntegerField` | `number | null` | Stock después de extraer (Opcional) |

### `AuditRecord` (App: `records`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` | (Opcional) |
| `company` | `FK -> Company` | `number` | Empresa asociada |
| `branch` | `FK -> Branch` | `number | null` | Sucursal (Opcional) |
| `user` | `FK -> CustomUser` | `number | null` | Usuario que ejecutó la acción (Opcional) |
| `action` | `CharField` | `string` | Tipo de acción (ver lista en endpoint) |
| `ip_address` | `GenericIPAddressField` | `string | null` | IP desde donde se ejecutó (Opcional) |
| `description` | `TextField` | `string` | Descripción de la acción |
| `details` | `JSONField` | `object` | Datos adicionales de la acción |
| `created_at` | `DateTimeField` | `string` | Formato ISO 8601 |

### `Branch` (App: `core`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company` | Envía ID, recibe Entidad o ID |
| `name` | `CharField` | `string` |  |
| `code` | `CharField` | `string` |  |
| `address` | `CharField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Category` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Subcategory` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Season` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Color` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `code` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Gender` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `LetterSize` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `short_name` | `CharField` | `string` |  |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Materials` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Supplier` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `phone_number` | `CharField` | `string | null` |  (Opcional) |
| `email` | `CharField` | `string | null` |  (Opcional) |
| `address` | `CharField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Brand` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `supplier` | `FK -> Supplier` | `number | Supplier | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `logo` | `FileField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Product` (App: `products`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `numeric_size` | `IntegerField` | `number | null` |  (Opcional) |
| `cost_price` | `DecimalField` | `string` | DRF serializa decimales a string |
| `sale_price` | `DecimalField` | `string` | DRF serializa decimales a string |
| `internal_code` | `CharField` | `string | null` |  (Opcional) |
| `details` | `CharField` | `string | null` |  (Opcional) |
| `image` | `FileField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `gender` | `FK -> Gender` | `number | Gender | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `letter_size` | `FK -> LetterSize` | `number | LetterSize | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `material` | `FK -> Materials` | `number | Materials | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `color` | `FK -> Color` | `number | Color | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `brand` | `FK -> Brand` | `number | Brand | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `category` | `FK -> Category` | `number | Category | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `season` | `FK -> Season` | `number | Season | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `is_deleted` | `BooleanField` | `boolean` |  |
| `deleted_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `subcategories` | `M2M -> Subcategory` | `number[] | Subcategory[] | null` | Array de IDs o Entidades (Opcional) |

### `Inventory` (App: `inventory`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `product` | `FK -> Product` | `number | Product` | Envía ID, recibe Entidad o ID |
| `quantity` | `IntegerField` | `number` |  |

### `PayMethod` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Sale` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `seller` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `client` | `FK -> Client` | `number | Client | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `total_amount` | `DecimalField` | `string` | DRF serializa decimales a string |
| `pay_method` | `FK -> PayMethod` | `number | PayMethod | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `payment_status` | `CharField` | `string` |  |
| `account_record` | `FK -> CustomerBalanceRecord` | `number | CustomerBalanceRecord | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `cash_session` | `FK -> CashSession` | `number | CashSession | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `canceled` | `BooleanField` | `boolean` |  |
| `closed` | `BooleanField` | `boolean` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `SaleDetail` (App: `sales`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `order` | `FK -> Sale` | `number | Sale` | Envía ID, recibe Entidad o ID |
| `product` | `FK -> Product` | `number | Product | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `quantity` | `IntegerField` | `number` |  |
| `sale_price` | `DecimalField` | `string` | DRF serializa decimales a string |
| `cost_price` | `DecimalField` | `string` | DRF serializa decimales a string |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Client` (App: `clients`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `is_deleted` | `BooleanField` | `boolean` |  |
| `deleted_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `name` | `CharField` | `string` |  |
| `last_name` | `CharField` | `string` |  |
| `phone` | `CharField` | `string | null` |  (Opcional) |
| `dni` | `CharField` | `string` |  |
| `cuit` | `CharField` | `string | null` |  (Opcional) |
| `email` | `CharField` | `string` |  |
| `address` | `CharField` | `string` |  |
| `birth_date` | `DateField` | `string | null` | Formato ISO 8601 (Opcional) |
| `postal_code` | `CharField` | `string` |  |
| `chosen_billing_type` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `approved_customer_account` | `BooleanField` | `boolean` |  |

### `CustomerAccount` (App: `clients`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `client` | `FK -> Client` | `number | Client` | Envía ID, recibe Entidad o ID |
| `credit_limit` | `DecimalField` | `string | null` | DRF serializa decimales a string (Opcional) |
| `active` | `BooleanField` | `boolean` |  |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `opening_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `CustomerBalanceRecord` (App: `clients`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `customer_account` | `FK -> CustomerAccount` | `number | CustomerAccount` | Envía ID, recibe Entidad o ID |
| `sale` | `FK -> Sale` | `number | Sale | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `related_to` | `FK -> CustomerBalanceRecord` | `number | CustomerBalanceRecord | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `amount` | `DecimalField` | `string` | DRF serializa decimales a string |
| `movement_type` | `CharField` | `string` |  |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `reference` | `CharField` | `string | null` |  (Opcional) |
| `created_by` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `reconciled` | `BooleanField` | `boolean` |  |
| `reconciled_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `reconciled_by` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |

### `CashSession` (App: `cash`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `cash_register` | `FK -> CashRegister` | `number | CashRegister` | Envía ID, recibe Entidad o ID |
| `user` | `FK -> CustomUser` | `number | CustomUser` | Envía ID, recibe Entidad o ID |
| `status` | `CharField` | `string` |  |
| `opening_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `closing_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `opening_balance` | `DecimalField` | `string` | DRF serializa decimales a string |
| `closing_balance` | `DecimalField` | `string | null` | DRF serializa decimales a string (Opcional) |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `CashMovement` (App: `cash`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `cash_session` | `FK -> CashSession` | `number | CashSession` | Envía ID, recibe Entidad o ID |
| `type` | `CharField` | `string` |  |
| `amount` | `DecimalField` | `string` | DRF serializa decimales a string |
| `reason` | `CharField` | `string` |  |
| `description` | `TextField` | `string | null` |  (Opcional) |
| `created_by` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `Device` (App: `devices`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `polymorphic_ctype` | `FK -> ContentType` | `number | ContentType | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `code` | `CharField` | `string` |  |
| `name` | `CharField` | `string` |  |
| `location` | `CharField` | `string | null` |  (Opcional) |
| `model` | `CharField` | `string | null` |  (Opcional) |
| `serial_number` | `CharField` | `string | null` |  (Opcional) |
| `ip_address` | `GenericIPAddressField` | `string | null` |  (Opcional) |
| `mac_address` | `CharField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `is_online` | `BooleanField` | `boolean` |  |
| `last_seen` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_user` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `CashRegister` (App: `devices`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `polymorphic_ctype` | `FK -> ContentType` | `number | ContentType | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `code` | `CharField` | `string` |  |
| `name` | `CharField` | `string` |  |
| `location` | `CharField` | `string | null` |  (Opcional) |
| `model` | `CharField` | `string | null` |  (Opcional) |
| `serial_number` | `CharField` | `string | null` |  (Opcional) |
| `ip_address` | `GenericIPAddressField` | `string | null` |  (Opcional) |
| `mac_address` | `CharField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `is_online` | `BooleanField` | `boolean` |  |
| `last_seen` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_user` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `device_ptr` | `FK -> Device` | `number | Device` | Envía ID, recibe Entidad o ID |

### `PriceChecker` (App: `devices`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `polymorphic_ctype` | `FK -> ContentType` | `number | ContentType | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `code` | `CharField` | `string` |  |
| `name` | `CharField` | `string` |  |
| `location` | `CharField` | `string | null` |  (Opcional) |
| `model` | `CharField` | `string | null` |  (Opcional) |
| `serial_number` | `CharField` | `string | null` |  (Opcional) |
| `ip_address` | `GenericIPAddressField` | `string | null` |  (Opcional) |
| `mac_address` | `CharField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `is_online` | `BooleanField` | `boolean` |  |
| `last_seen` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_user` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `device_ptr` | `FK -> Device` | `number | Device` | Envía ID, recibe Entidad o ID |
| `display_promotions` | `BooleanField` | `boolean` |  |
| `timeout_seconds` | `IntegerField` | `number` |  |

### `StockTerminal` (App: `devices`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `polymorphic_ctype` | `FK -> ContentType` | `number | ContentType | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `code` | `CharField` | `string` |  |
| `name` | `CharField` | `string` |  |
| `location` | `CharField` | `string | null` |  (Opcional) |
| `model` | `CharField` | `string | null` |  (Opcional) |
| `serial_number` | `CharField` | `string | null` |  (Opcional) |
| `ip_address` | `GenericIPAddressField` | `string | null` |  (Opcional) |
| `mac_address` | `CharField` | `string | null` |  (Opcional) |
| `is_active` | `BooleanField` | `boolean` |  |
| `is_online` | `BooleanField` | `boolean` |  |
| `last_seen` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `branch` | `FK -> Branch` | `number | Branch | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_user` | `FK -> CustomUser` | `number | CustomUser | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `assigned_date` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `notes` | `TextField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `device_ptr` | `FK -> Device` | `number | Device` | Envía ID, recibe Entidad o ID |
| `can_receive_shipments` | `BooleanField` | `boolean` |  |
| `require_photo` | `BooleanField` | `boolean` |  |

### `DeviceConfig` (App: `devices`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `device` | `FK -> Device` | `number | Device` | Envía ID, recibe Entidad o ID |
| `key` | `CharField` | `string` |  |
| `value` | `CharField` | `string` |  |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

### `CustomUser` (App: `users`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `password` | `CharField` | `string` |  |
| `last_login` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `is_superuser` | `BooleanField` | `boolean` |  |
| `username` | `CharField` | `string` |  |
| `first_name` | `CharField` | `string | null` |  (Opcional) |
| `last_name` | `CharField` | `string | null` |  (Opcional) |
| `is_staff` | `BooleanField` | `boolean` |  |
| `is_active` | `BooleanField` | `boolean` |  |
| `date_joined` | `DateTimeField` | `string` | Formato ISO 8601 |
| `email` | `CharField` | `string | null` |  (Opcional) |
| `company` | `FK -> Company` | `number | Company | null` | Envía ID, recibe Entidad o ID (Opcional) |
| `branch` | `M2M -> Branch` | `number[] | Branch[] | null` | Array de IDs o Entidades (Opcional) |
| `groups` | `M2M -> Group` | `number[] | Group[] | null` | Array de IDs o Entidades (Opcional) |
| `user_permissions` | `M2M -> Permission` | `number[] | Permission[] | null` | Array de IDs o Entidades (Opcional) |

### `Profile` (App: `users`)
| Campo | Tipo Backend | Tipo Sugerido Frontend | Notas/Variaciones |
|-------|--------------|-----------------------|-------|
| `id` | `PrimaryKey` | `number | null` |  (Opcional) |
| `user` | `FK -> CustomUser` | `number | CustomUser` | Envía ID, recibe Entidad o ID |
| `phone_number` | `CharField` | `string | null` |  (Opcional) |
| `dni` | `CharField` | `string | null` |  (Opcional) |
| `address` | `CharField` | `string | null` |  (Opcional) |
| `city` | `CharField` | `string | null` |  (Opcional) |
| `province` | `CharField` | `string | null` |  (Opcional) |
| `postal_code` | `CharField` | `string | null` |  (Opcional) |
| `country` | `CharField` | `string | null` |  (Opcional) |
| `created_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |
| `updated_at` | `DateTimeField` | `string | null` | Formato ISO 8601 (Opcional) |

