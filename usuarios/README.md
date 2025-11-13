# Módulo de Usuarios - Documentación de API

## Estructura del Módulo

```
usuarios/
├── models.py           # Modelos Rol y Usuario
├── serializers.py      # Serializers para validación y transformación de datos
├── views.py            # Vistas API (APIView)
├── urls.py             # Rutas del módulo
├── admin.py            # Configuración del panel admin
├── services/
│   ├── __init__.py
# Módulo de Usuarios - Documentación de API

## Estructura del Módulo

```
usuarios/
├── models.py           # Modelos Rol y Usuario
├── serializers.py      # Serializers para validación y transformación de datos
├── views.py            # Vistas API (APIView)
├── urls.py             # Rutas del módulo
├── admin.py            # Configuración del panel admin
├── services/
│   ├── __init__.py
│   ├── services_rol.py     # Lógica de negocio de Roles
│   └── services_usuario.py # Lógica de negocio de Usuarios
```

## Endpoints Disponibles

### Autenticación

#### Login

```http
POST /api/usuarios/login/
Content-Type: application/json

{
    "username": "tu_usuario",
    "password": "tu_contraseña"
}
```

**Respuesta exitosa (200):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "idUsuario": 1,
    "username": "tu_usuario",
    "email": "email@example.com",
    "fcmToken": null,
    "rol": {
      "idRol": 1,
      "nombre": "Admin",
      "descripcion": "Administrador del sistema"
    },
    "fecha_creacion": "2025-01-01T00:00:00Z",
    "fecha_actualizacion": "2025-01-01T00:00:00Z",
    "activo": true
  }
}
```

---

### Roles

#### Listar todos los roles

```http
GET /api/usuarios/roles/
Authorization: Bearer <access_token>
```

#### Crear un rol

```http
POST /api/usuarios/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "Admin",
    "descripcion": "Administrador del sistema"
}
```

#### Obtener un rol específico

```http
GET /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
```

#### Actualizar un rol

```http
PUT /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "SuperAdmin",
    "descripcion": "Super administrador"
}
```

#### Actualizar parcialmente un rol

```http
PATCH /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "descripcion": "Nueva descripción"
}
```

#### Eliminar un rol

```http
DELETE /api/usuarios/roles/<id_rol>/
Authorization: Bearer <access_token>
```

#### Buscar rol por nombre

```http
GET /api/usuarios/roles/buscar/?nombre=Admin
Authorization: Bearer <access_token>
```

---

### Usuarios

#### Listar todos los usuarios

```http
GET /api/usuarios/
Authorization: Bearer <access_token>
```

#### Crear un usuario

```http
POST /api/usuarios/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "rol": 1,
    "fcmToken": "token_opcional"
}
```

#### Obtener un usuario específico

```http
GET /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
```

#### Actualizar un usuario

```http
PUT /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "username": "usuario_actualizado",
    "email": "nuevo@example.com",
    "rol": 2,
    "activo": true
}
```

#### Actualizar parcialmente un usuario

```http
PATCH /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "email": "nuevo@example.com"
}
```

#### Desactivar un usuario (Soft Delete)

```http
DELETE /api/usuarios/<id_usuario>/
Authorization: Bearer <access_token>
```

#### Eliminar permanentemente un usuario

```http
DELETE /api/usuarios/<id_usuario>/permanente/
Authorization: Bearer <access_token>
```

#### Cambiar contraseña

```http
POST /api/usuarios/cambiar-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "id_usuario": 1,
    "password_actual": "contraseña_actual",
    "password_nueva": "nueva_contraseña"
}
```

#### Buscar usuarios

```http
GET /api/usuarios/buscar/?q=juan
Authorization: Bearer <access_token>
```

#### Actualizar FCM Token

```http
PATCH /api/usuarios/<id_usuario>/fcm-token/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "fcmToken": "nuevo_token_fcm"
}
```

---

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos inválidos o error de validación
- **401 Unauthorized**: No autenticado o credenciales inválidas
- **403 Forbidden**: Sin permisos o usuario inactivo
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

---

## Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "error": "Descripción del error"
}
```

### Ejemplos de errores comunes:

**Usuario no encontrado:**

```json
{
  "error": "Usuario no encontrado"
}
```

**Credenciales inválidas:**

```json
{
  "error": "Credenciales inválidas"
}
```

**Email duplicado:**

```json
{
  "error": "El email ya está registrado"
}
```

**Rol con usuarios asociados:**

```json
{
  "error": "No se puede eliminar el rol porque tiene usuarios asociados"
}
```

---

## Modelos de Datos

### Rol

```python
{
    "idRol": int,
    "nombre": string (max 100, único),
    "descripcion": string (max 255, opcional)
}
```

### Usuario

```python
{
    "idUsuario": int,
    "username": string (max 150, único),
    "email": string (max 255, único),
    "password": string (max 255, write-only),
    "fcmToken": string (max 255, opcional),
    "rol": int (foreign key),
    "rol_nombre": string (read-only),
    "fecha_creacion": datetime (auto),
    "fecha_actualizacion": datetime (auto),
    "activo": boolean (default: true)
}
```

---

## Migraciones

Para aplicar las migraciones y crear las tablas en la base de datos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Crear Superusuario

Para acceder al panel de administración:

```bash
python manage.py createsuperuser
```

---

## Notas Importantes

1. **Encriptación de contraseñas**: Las contraseñas se encriptan automáticamente usando el sistema de hashing de Django.

2. **Soft Delete**: Al eliminar un usuario con `DELETE /api/usuarios/<id>/`, solo se desactiva (campo `activo = False`). Para eliminación permanente, usar el endpoint `/permanente/`.

3. **Protección de Roles**: No se puede eliminar un rol que tenga usuarios asociados.

4. **Tokens JWT**: El access token expira en 120 minutos y el refresh token en 7 días.

5. **Búsqueda**: La búsqueda de usuarios busca coincidencias parciales (case-insensitive) en `username` y `email`.

---

## Módulo de Categorías - Documentación de API

Este módulo gestiona las categorías de productos. Las rutas principales están bajo `/api/categorias/`.

### Endpoints disponibles

Listar todas las categorias

```http
GET /api/categorias/
Authorization: Bearer <access_token>
```

Crear una categoría

```http
POST /api/categorias/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "Ropa",
    "descripcion": "Categoría de prendas"
}
```

Obtener una categoría específica

```http
GET /api/categorias/<id_categoria>/
Authorization: Bearer <access_token>
```

Actualizar una categoría

```http
PUT /api/categorias/<id_categoria>/
PATCH /api/categorias/<id_categoria>/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "Ropa Hombre",
    "descripcion": "Descripción actualizada",
    "activo": true
}
```

Eliminar (soft) una categoría

```http
DELETE /api/categorias/<id_categoria>/
Authorization: Bearer <access_token>
```

Buscar categoría por nombre

```http
GET /api/categorias/buscar/?nombre=Ropa
Authorization: Bearer <access_token>
```

### Modelos de Datos (Categoria)

```python
{
    "idCategoria": int,
    "nombre": string (max 150, único),
    "descripcion": string (max 255, opcional),
    "activo": boolean,
    "fecha_creacion": datetime,
    "fecha_actualizacion": datetime
}
```

Notas importantes sobre Categorías

- La eliminación de una categoría está protegida por la relación con `Product` (on_delete=PROTECT). No se podrá eliminar una categoría que tenga productos relacionados.
- Todas las operaciones requieren autenticación (según la implementación actual).

---

## Módulo de Productos - Documentación de API

Este módulo gestiona productos, variantes, imágenes e inventario. Las rutas principales están bajo `/api/productos/`.

### Endpoints disponibles

Listar y crear productos

```http
GET /api/productos/
Authorization: (GET is public in the implementation) - creación requiere token
```

```http
POST /api/productos/
Authorization: Bearer <access_token>
Content-Type: application/json
```

Ejemplo crear producto (se aceptan variantes e imágenes):

```json
{
  "name": "Remera Azul",
  "description": "Remera de algodón",
  "base_price": "25.00",
  "categoria_id": 1,
  "images": [ {"image_url": "https://.../img1.jpg"} ],
  "variants": [
    {"sku": "REM-AZ-XS", "size": "XS", "color": "Azul", "price": "25.00", "stock": 10},
    {"sku": "REM-AZ-M", "size": "M", "color": "Azul", "price": "26.00", "stock": 5}
  ],
  "active": true
}
```

Obtener / actualizar / eliminar un producto

```http
GET /api/productos/<id>/
PUT /api/productos/<id>/
PATCH /api/productos/<id>/
DELETE /api/productos/<id>/
```

Inventario de un producto

```http
GET /api/productos/<id>/inventory/
```

Actualizar stock de una variante (por id de variante)

```http
PATCH /api/productos/variants/<variant_id>/stock/
Authorization: Bearer <access_token>
Content-Type: application/json
```

Ejemplo body (partial update sobre la variante):

```json
{
  "stock": 12
}
```

Inventario global

```http
GET /api/productos/inventory/all/
Authorization: Bearer <access_token>
```

Ajustar inventario (registro de movimiento)

```http
POST /api/productos/inventory/adjust/
Authorization: Bearer <access_token> (permiso especial CanManageUsers requerido)
Content-Type: application/json
```

Body de ejemplo (dos formas):

```json
{
  "variant_id": 5,
  "delta": -2,
  "motivo": "Venta en tienda"
}
```

o

```json
{
  "variant_id": 5,
  "stock": 20,
  "motivo": "Ajuste inventario"
}
```

### Modelos de Datos (resumen)

Product

```python
{
  "id": int,
  "name": string (200),
  "description": string,
  "base_price": decimal,
  "categoria": { ... } (read-only),
  "categoria_id": int (write-only),
  "images": [ {"id": int, "image_url": string} ],
  "variants": [ {"id": int, "sku": string, "size": string, "color": string, "model_name": string, "price": decimal, "stock": int} ],
  "active": boolean,
  "created_at": datetime,
  "updated_at": datetime
}
```

ProductVariant

```python
{
  "id": int,
  "product_id": int,
  "sku": string,
  "size": string,
  "color": string,
  "model_name": string,
  "price": decimal (opcional),
  "stock": int (validación: mínimo 2 por serializer)
}
```

InventoryMovement (registro automático por servicios de inventario)

```python
{
  "id": int,
  "variant": int,
  "usuario": int | null,
  "previous_stock": int,
  "new_stock": int,
  "delta": int,
  "motivo": string,
  "fecha": datetime
}
```

Notas importantes sobre Productos e Inventario

- La lista pública de productos (GET /api/productos/) está permitida sin token según la implementación actual; creación/ediciones y operaciones de inventario requieren autenticación y permisos adecuados.
- El serializer fuerza un stock mínimo de 2 al crear/actualizar variantes si no se entrega un valor mayor; esto evita stock inferiores al umbral.
- Las imágenes de producto usan `image_url` (URLField). Si deseas usar almacenamiento local o cloud (ImageField) se deberá configurar storage.
- La relación `Product.categoria` usa on_delete=PROTECT: no se puede eliminar una categoría con productos asociados.
- Los movimientos de inventario se registran en `InventoryMovement` para auditoría.

---

## Códigos de Estado HTTP (resumen)

- 200 OK: Operación exitosa
- 201 Created: Recurso creado exitosamente
- 400 Bad Request: Datos inválidos o error de validación
- 401 Unauthorized: No autenticado o credenciales inválidas
- 403 Forbidden: Sin permisos o usuario inactivo
- 404 Not Found: Recurso no encontrado
- 500 Internal Server Error: Error del servidor

---

## Manejo de Errores (formato común)

Todas las respuestas de error siguen este formato:

```json
{
  "error": "Descripción del error"
}
```

Ejemplos de errores comunes adicionales:

"Categoria con productos asociados":
```json
{
  "error": "No se puede eliminar la categoria porque tiene productos asociados"
}
```

"Stock mínimo no cumplido":
```json
{
  "error": "El stock mínimo permitido es 2"
}
```

---

## Notas finales

Si quieres, puedo añadir ejemplos de request/response más detallados para endpoints concretos (por ejemplo, la respuesta de `GET /api/productos/` o el payload completo de `POST /api/productos/`), o generar una colección Postman usando `postmanJson.json` que ya está en el repo.

---
