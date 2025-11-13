# Ejemplos — Subida y uso de imágenes (Cloudinary)

Endpoints asumidos:
- POST /api/productos/images/upload/  (multipart/form-data)  
  Campos: product (id), image (archivo), alt_text (opcional), is_main (opcional)

1) Curl — subir imagen
```bash
curl -X POST \
  -F "product=1" \
  -F "image=@C:\ruta\a\foto.jpg" \
  http://localhost:8000/api/productos/images/upload/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Respuesta esperada (201):
```json
{
  "id": 42,
  "product": 1,
  "image": "https://res.cloudinary.com/dmlfvvfmf/image/upload/v.../foto.jpg",
  "alt_text": "Frente",
  "is_main": false,
  "order": 0,
  "created_at": "2025-11-11T00:00:00Z"
}
```

2) Fetch (frontend) — ejemplo
```javascript
const fd = new FormData();
fd.append('product', productId);
fd.append('image', fileInput.files[0]);
fetch('/api/productos/images/upload/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + token },
  body: fd
})
  .then(r => r.json())
  .then(data => {
    const url = data.image || data.image_url;
    if (url) document.getElementById('preview').src = url;
  });
```

3) Verificación en Django shell
```python
from productos.models import ProductImage
pi = ProductImage.objects.latest('id')
print(pi.image.url)  # URL pública en Cloudinary
```

4) Verificación en Cloudinary Dashboard
- Entrar a Cloudinary → Media Library → Assets. Si la subida fue correcta verás la imagen.

5) Notas y buenas prácticas
- URLs que empiezan con https://res.cloudinary.com/ indican que la imagen está en Cloudinary.
- No subas claves al repositorio; usa .env o variables de entorno.
- Para devolver la URL en la API, añade un campo image_url en el serializer que haga obj.image.url.
