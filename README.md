# BagualesPOS API Documentation

Documentación completa y precisa de todos los endpoints de la API REST de BagualesPOS.  
**Esta documentación está basada 100% en los serializers reales del backend.**

**Base URL**: `/api/`

---

## Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Productos](#productos)
3. [Clientes](#clientes)
4. [Inventario](#inventario)
5. [Ventas](#ventas)
6. [Caja](#caja)
7. [Dispositivos](#dispositivos)
8. [Usuarios](#usuarios)
9. [Registros](#registros)

---

## Autenticación

### Obtener Token de Acceso
**Método**: `POST`  
**Endpoint**: `/api/users/token/`  
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
**Endpoint**: `/api/users/token/refresh/`  
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
**Endpoint**: `/api/users/token/logout/`  
**Descripción**: Invalidar refresh token

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Productos

> **Nota**: Los productos usan diferentes serializers según la acción:
> - **Listado** (`GET /products/`): Usa `ProductListSerializer` (simplificado)
> - **Detalle** (`GET /products/{id}/`): Usa `ProductDetailSerializer` (completo)
> - **Crear/Actualizar** (`POST/PUT/PATCH`): Usa `ProductCreateUpdateSerializer`

### Listar Productos
**Método**: `GET`  
**Endpoint**: `/api/products/products/`  
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
**Endpoint**: `/api/products/products/<int:pk>/`  
**Ejemplo**: `/api/products/products/1/`  
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
**Endpoint**: `/api/products/products/`  
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
**Endpoint**: `/api/products/products/<int:pk>/`  
**Ejemplo**: `/api/products/products/1/`  
**Descripción**: Actualizar un producto

### Eliminar Producto (Soft Delete)
**Método**: `DELETE`  
**Endpoint**: `/api/products/products/<int:pk>/`  
**Ejemplo**: `/api/products/products/1/`  
**Descripción**: Eliminar lógicamente un producto

---

### Recursos de Productos

Todos estos recursos usan el patrón List/Write serializers:
- **Listado/Detalle**: Retorna `{ "id": 1, "name": "..." }`
- **Crear/Actualizar**: Acepta todos los campos del modelo

#### Marcas (Brands)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/brands/`

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
**Endpoint**: `/api/products/categories/`

#### Subcategorías
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/subcategories/`

#### Colores
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/colors/`

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
**Endpoint**: `/api/products/genders/`

#### Talles (Letter Sizes)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/letter-sizes/`

#### Materiales
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/materials/`

#### Temporadas (Seasons)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/seasons/`

#### Proveedores (Suppliers)
**Métodos**: `GET, POST, PUT, PATCH, DELETE`  
**Endpoint**: `/api/products/suppliers/`

---

## Clientes

### Listar Clientes
**Método**: `GET`  
**Endpoint**: `/api/clients/clients/`  
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
**Endpoint**: `/api/clients/clients/`  
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
**Endpoint**: `/api/clients/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/clients/1/`

### Actualizar Cliente
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/clients/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/clients/1/`

### Eliminar Cliente (Soft Delete)
**Método**: `DELETE`  
**Endpoint**: `/api/clients/clients/<int:pk>/`  
**Ejemplo**: `/api/clients/clients/1/`  
**Descripción**: Elimina lógicamente (is_deleted=true)

### Restaurar Cliente
**Método**: `POST`  
**Endpoint**: `/api/clients/clients/<int:pk>/restore/`  
**Ejemplo**: `/api/clients/clients/1/restore/`  
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
**Endpoint**: `/api/clients/customer-accounts/`

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
**Endpoint**: `/api/clients/customer-accounts/`

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
**Endpoint**: `/api/clients/customer-accounts/<int:pk>/deactivate/`  
**Ejemplo**: `/api/clients/customer-accounts/1/deactivate/`

**Response**:
```json
{
  "status": "account deactivated"
}
```

#### Resumen de Cuentas
**Método**: `GET`  
**Endpoint**: `/api/clients/customer-accounts/summary/`  
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
**Endpoint**: `/api/clients/balance-records/`

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
**Endpoint**: `/api/clients/balance-records/`  
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
**Endpoint**: `/api/inventory/inventory/`  
**Descripción**: Obtener stock de todos los productos

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
    "quantity": 50
  }
]
```

### Obtener Inventario
**Método**: `GET`  
**Endpoint**: `/api/inventory/inventory/<int:pk>/`  
**Ejemplo**: `/api/inventory/inventory/1/`

### Actualizar Inventario
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/inventory/inventory/<int:pk>/`  
**Ejemplo**: `/api/inventory/inventory/1/`

**Request**:
```json
{
  "quantity": 75
}
```

---

## Ventas

### Listar Ventas
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/`  
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
**Endpoint**: `/api/sales/sales/`  
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
**Endpoint**: `/api/sales/sales/<int:pk>/`  
**Ejemplo**: `/api/sales/sales/1/`

### Cerrar Venta
**Método**: `POST`  
**Endpoint**: `/api/sales/sales/<int:pk>/close/`  
**Ejemplo**: `/api/sales/sales/1/close/`  
**Descripción**: Cerrar y confirmar una venta (actualiza inventario, crea movimientos)

**Response**: Retorna la venta completa con `closed: true`

### Resumen de Ventas
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/summary/`  
**Descripción**: Métricas generales de ventas

**Response**:
```json
{
  "total_sales": "50000.00",
  "total_count": 150,
  "average_sale": "333.33",
  "today_sales": "5000.00",
  "today_count": 15
}
```

### Top Productos
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/top_products/`  
**Descripción**: Productos más vendidos

**Response**:
```json
[
  {
    "product_id": 1,
    "product_name": "Camisa Slim Fit",
    "total_quantity": 50,
    "total_revenue": "5000.00"
  }
]
```

### Ventas por Categoría
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/sales_by_category/`

**Response**:
```json
[
  {
    "category_id": 1,
    "category_name": "Ropa",
    "total": "25000.00",
    "count": 75
  }
]
```

### Ventas por Día
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/sales_by_day/`  
**Descripción**: Últimos 7 días

**Response**:
```json
[
  {
    "date": "2025-01-15",
    "total": "5000.00",
    "count": 15
  }
]
```

### Ventas por Mes
**Método**: `GET`  
**Endpoint**: `/api/sales/sales/sales_by_month/`  
**Descripción**: Últimos 6 meses

**Response**:
```json
[
  {
    "month": "2025-01",
    "total": "50000.00",
    "count": 150
  }
]
```

---

### Detalles de Venta (Sale Details)

#### Listar Detalles
**Método**: `GET`  
**Endpoint**: `/api/sales/sale-details/`

#### Crear Detalle
**Método**: `POST`  
**Endpoint**: `/api/sales/sale-details/`  
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
**Endpoint**: `/api/sales/pay-methods/`

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

## Caja

### Cajas Registradoras

> **Nota**: CashRegister ahora hereda de Device. Ver sección [Dispositivos](#dispositivos) para gestión completa.

#### Listar Cajas (desde devices)
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/cash_registers/`  
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
**Endpoint**: `/api/cash/cash-sessions/`  
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
**Endpoint**: `/api/cash/cash-sessions/<int:pk>/`  
**Ejemplo**: `/api/cash/cash-sessions/5/`

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
**Endpoint**: `/api/cash/cash-sessions/open/`  
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
**Endpoint**: `/api/cash/cash-sessions/<int:pk>/close/`  
**Ejemplo**: `/api/cash/cash-sessions/5/close/`  
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
**Endpoint**: `/api/cash/cash-sessions/my_active/`  
**Descripción**: Obtener sesión abierta del usuario actual

**Response**: Sesión completa o 404 si no tiene sesión abierta

#### Ventas de Sesión
**Método**: `GET`  
**Endpoint**: `/api/cash/cash-sessions/<int:pk>/sales/`  
**Ejemplo**: `/api/cash/cash-sessions/5/sales/`  
**Descripción**: Ventas cerradas y no canceladas de esta sesión

**Response**: Array de ventas (formato `SaleSerializer`)

#### Movimientos de Sesión
**Método**: `GET`  
**Endpoint**: `/api/cash/cash-sessions/<int:pk>/movements/`  
**Ejemplo**: `/api/cash/cash-sessions/5/movements/`

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
**Endpoint**: `/api/cash/cash-sessions/<int:pk>/summary/`  
**Ejemplo**: `/api/cash/cash-sessions/5/summary/`

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
**Endpoint**: `/api/cash/cash-movements/`  
**Filtros**: `?cash_session=5&type=CASH_IN`  
**Ordenamiento**: `?ordering=-created_at`

#### Crear Movimiento
**Método**: `POST`  
**Endpoint**: `/api/cash/cash-movements/`  
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
**Endpoint**: `/api/devices/devices/`  
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
**Endpoint**: `/api/devices/devices/`  
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
**Endpoint**: `/api/devices/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/devices/1/`  
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
**Endpoint**: `/api/devices/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/devices/1/`

### Eliminar Dispositivo
**Método**: `DELETE`  
**Endpoint**: `/api/devices/devices/<int:pk>/`  
**Ejemplo**: `/api/devices/devices/1/`

### Heartbeat (Check-in)
**Método**: `POST`  
**Endpoint**: `/api/devices/devices/<int:pk>/heartbeat/`  
**Ejemplo**: `/api/devices/devices/1/heartbeat/`  
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
**Endpoint**: `/api/devices/devices/<int:pk>/assign/`  
**Ejemplo**: `/api/devices/devices/1/assign/`  
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
**Endpoint**: `/api/devices/devices/<int:pk>/unassign/`  
**Ejemplo**: `/api/devices/devices/1/unassign/`

**Response**: Dispositivo completo con `assigned_user: null`

### Cajas Registradoras
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/cash_registers/`  
**Descripción**: Solo CashRegister activos

**Response**: Array de `CashRegisterSerializer` (con `current_session_id` y `has_open_session`)

### Terminales de Precio
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/price_checkers/`  
**Descripción**: Solo PriceChecker activos

**Response**: Array de `PriceCheckerSerializer` (con `display_promotions` y `timeout_seconds`)

### Terminales de Stock
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/stock_terminals/`  
**Descripción**: Solo StockTerminal activos

**Response**: Array de `StockTerminalSerializer` (con `can_receive_shipments` y `require_photo`)

### Dispositivos Online
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/online/`

**Response**: Array de `DeviceListSerializer` donde `is_online=true`

### Dispositivos Offline
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/offline/`

**Response**: Array de `DeviceListSerializer` donde `is_online=false`

### Resumen de Dispositivos
**Método**: `GET`  
**Endpoint**: `/api/devices/devices/summary/`

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

### Listar Usuarios
**Método**: `GET`  
**Endpoint**: `/api/users/users/`

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
    "is_staff": true,
    "date_joined": "2025-01-01T00:00:00Z",
    "profile": null
  }
]
```

### Crear Usuario
**Método**: `POST`  
**Endpoint**: `/api/users/users/`

**Request**:
```json
{
  "username": "nuevo_usuario",
  "email": "nuevo@example.com",
  "password": "contraseña123",
  "first_name": "Nuevo",
  "last_name": "Usuario",
  "is_active": true
}
```

### Obtener Usuario
**Método**: `GET`  
**Endpoint**: `/api/users/users/<int:pk>/`  
**Ejemplo**: `/api/users/users/1/`

### Actualizar Usuario
**Método**: `PUT/PATCH`  
**Endpoint**: `/api/users/users/<int:pk>/`  
**Ejemplo**: `/api/users/users/1/`

### Eliminar Usuario
**Método**: `DELETE`  
**Endpoint**: `/api/users/users/<int:pk>/`  
**Ejemplo**: `/api/users/users/1/`

---

## Registros

### Listar Registros
**Método**: `GET`  
**Endpoint**: `/api/records/records/`  
**Descripción**: Logs de acciones del sistema

### Obtener Registro
**Método**: `GET`  
**Endpoint**: `/api/records/records/<int:pk>/`  
**Ejemplo**: `/api/records/records/1/`

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

Estos campos **no** deben incluirse en requests POST/PUT/PATCH.

### Validaciones Frontend
Implementar estas validaciones antes de enviar requests:
- **Productos**: `sale_price > cost_price`
- **Caja**: `closing_balance >= 0`, `opening_balance >= 0`
- **Clientes**: Email válido, DNI numérico
- **Dispositivos**: MAC address formato `XX:XX:XX:XX:XX:XX`
