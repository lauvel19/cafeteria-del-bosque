from apps.users.models import User
from apps.menu.models import Category, Product
from apps.kitchen.models import KitchenStation

print("Inicializando datos de prueba...\n")

# ----------------------------
# 1. USUARIOS
# ----------------------------
print("1. Creando usuarios...")

admin, _ = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@cafedelbosque.com",
        "role": "ADMIN",
        "is_staff": True,
        "is_superuser": True
    }
)
admin.set_password("admin123")
admin.save()
print("✓ Admin creado")

meseros = [
    ("maria_mesera", "María", "González", "maria@cafedelbosque.com"),
    ("juan_mesero", "Juan", "Pérez", "juan@cafedelbosque.com"),
]

for username, fn, ln, email in meseros:
    u, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "role": "MESERO",
            "first_name": fn,
            "last_name": ln
        }
    )
    u.set_password("mesero123")
    u.save()

print("✓ 2 Meseros creados")

cocinero, _ = User.objects.get_or_create(
    username="carlos_chef",
    defaults={
        "email": "carlos@cafedelbosque.com",
        "role": "COCINERO",
        "first_name": "Carlos",
        "last_name": "Rodríguez"
    }
)
cocinero.set_password("chef123")
cocinero.save()
print("✓ Cocinero creado")

clientes = [
    ("ana_cliente", "Ana", "Martínez", "ana@email.com"),
    ("pedro_cliente", "Pedro", "López", "pedro@email.com"),
]

for username, fn, ln, email in clientes:
    c, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "role": "CLIENTE",
            "first_name": fn,
            "last_name": ln
        }
    )
    c.set_password("cliente123")
    c.save()

print("✓ 2 Clientes creados")

# ----------------------------
# 2. CATEGORÍAS
# ----------------------------
print("\n2. Creando categorías...")

cat_bebidas, _ = Category.objects.get_or_create(
    name="Bebidas Calientes",
    defaults={"category_type": "BEBIDAS", "description": "Café, té y chocolate"}
)

cat_bebidas_frias, _ = Category.objects.get_or_create(
    name="Bebidas Frías",
    defaults={"category_type": "BEBIDAS", "description": "Jugos y batidos"}
)

cat_entradas, _ = Category.objects.get_or_create(
    name="Entradas",
    defaults={"category_type": "ENTRADAS", "description": "Panes y acompañamientos"}
)

cat_comidas, _ = Category.objects.get_or_create(
    name="Comidas",
    defaults={"category_type": "COMIDAS", "description": "Platos principales"}
)

cat_postres, _ = Category.objects.get_or_create(
    name="Postres",
    defaults={"category_type": "POSTRES", "description": "Dulces y postres"}
)

print("✓ 5 Categorías creadas")

# ----------------------------
# 3. PRODUCTOS
# ----------------------------
print("\n3. Creando productos...")

from apps.menu.models import Product, Category

def get_cat(nombre):
    return Category.objects.get(name=nombre)

products = [
    # Bebidas Calientes
    {"name": "Café Americano", "base_price": 3.50, "category": "Bebidas Calientes", "preparation_time": 3},
    {"name": "Cappuccino", "base_price": 4.50, "category": "Bebidas Calientes", "preparation_time": 4},
    {"name": "Latte", "base_price": 4.00, "category": "Bebidas Calientes", "preparation_time": 4},
    {"name": "Mocha", "base_price": 4.80, "category": "Bebidas Calientes", "preparation_time": 5},
    {"name": "Espresso", "base_price": 2.50, "category": "Bebidas Calientes", "preparation_time": 2},

    # Bebidas Frías
    {"name": "Frappuccino Vainilla", "base_price": 5.50, "category": "Bebidas Frías", "preparation_time": 6},
    {"name": "Smoothie de Fresa", "base_price": 5.00, "category": "Bebidas Frías", "preparation_time": 5},
    {"name": "Limonada Natural", "base_price": 3.00, "category": "Bebidas Frías", "preparation_time": 3},

    # Panadería
    {"name": "Croissant", "base_price": 2.80, "category": "Panadería", "preparation_time": 8},
    {"name": "Pan de Chocolate", "base_price": 3.20, "category": "Panadería", "preparation_time": 8},
    {"name": "Rollito de Canela", "base_price": 3.50, "category": "Panadería", "preparation_time": 10},

    # Postres
    {"name": "Cheesecake", "base_price": 4.50, "category": "Postres", "preparation_time": 12},
    {"name": "Brownie", "base_price": 3.80, "category": "Postres", "preparation_time": 7},
    {"name": "Galletas de Chispas", "base_price": 2.00, "category": "Postres", "preparation_time": 5},
]


for p in products:
    category = get_cat(p["category"])
    obj, created = Product.objects.get_or_create(
        name=p["name"],
        defaults={
            "base_price": p["base_price"],
            "category": category,
            "preparation_time": p["preparation_time"],
        }
    )
    print(obj, created)

print("✔ Productos creados\n")

# ----------------------------
# 4. ESTACIONES DE COCINA
# ----------------------------
print("\n4. Creando estaciones de cocina...")

KitchenStation.objects.get_or_create(
    name="Estación Bebidas Calientes",
    defaults={"station_type": "BEBIDAS_CALIENTES", "can_handle_categories": ["BEBIDAS"]}
)

KitchenStation.objects.get_or_create(
    name="Estación Bebidas Frías",
    defaults={"station_type": "BEBIDAS_FRIAS", "can_handle_categories": ["BEBIDAS"]}
)

KitchenStation.objects.get_or_create(
    name="Panadería",
    defaults={"station_type": "PANADERIA", "can_handle_categories": ["ENTRADAS"]}
)

KitchenStation.objects.get_or_create(
    name="Cocina Principal",
    defaults={"station_type": "COCINA", "can_handle_categories": ["COMIDAS"]}
)

KitchenStation.objects.get_or_create(
    name="Repostería",
    defaults={"station_type": "POSTRES", "can_handle_categories": ["POSTRES"]}
)

print("✓ 5 Estaciones creadas")

print("\n=========================================")
print("✓ Datos inicializados correctamente")
print("=========================================\n")
print("Credenciales creadas:")
print("- Admin: admin / admin123")
print("- Mesero: maria_mesera / mesero123")
print("- Chef: carlos_chef / chef123")
print("- Cliente: ana_cliente / cliente123")
