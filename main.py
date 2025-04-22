"""
GENERADOR Y ADMINISTRADOR DE CONTRASEÑAS MEJORADO
Versión con todas las funcionalidades implementadas:
- Generación de contraseñas seguras
- Almacenamiento en base de datos
- Gestión CRUD completa
- Reset de base de datos
- Reinicio de IDs automático
"""

import random
import string
import sqlite3
import os
from colorama import Fore, Back, Style, init

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================

# Inicializar colorama para los colores en consola
init()

# Nombre del archivo de base de datos
DB_NAME = "password_manager.db"

# =============================================
# FUNCIONES DE BASE DE DATOS
# =============================================

def inicializar_base_datos():
    """Crea la base de datos y la tabla si no existen"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            username TEXT,
            password TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_contrasena(service, username, password, notes=""):
    """Guarda una contraseña en la base de datos"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO passwords (service, username, password, notes)
        VALUES (?, ?, ?, ?)
    ''', (service, username, password, notes))
    conn.commit()
    conn.close()

def mostrar_contrasenas():
    """Muestra todas las contraseñas guardadas"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, service, username, password, notes FROM passwords ORDER BY service')
    passwords = cursor.fetchall()
    conn.close()

    if not passwords:
        print(Fore.YELLOW + "\nNo hay contraseñas guardadas en la base de datos." + Style.RESET_ALL)
        return

    print(Fore.CYAN + "\n" + "=" * 80)
    print("🔐 CONTRASEÑAS GUARDADAS".center(80))
    print("=" * 80 + Style.RESET_ALL)

    for pwd in passwords:
        print(Fore.GREEN + f"\nID: {pwd[0]}")
        print(Fore.WHITE + f"Servicio: {pwd[1]}")
        print(f"Usuario: {pwd[2] or 'N/A'}")
        print(Fore.YELLOW + f"Contraseña: {pwd[3]}")
        print(Fore.BLUE + f"Notas: {pwd[4] or 'Sin notas'}")
        print(Style.RESET_ALL + "-" * 50)

def editar_contrasena():
    """Permite editar una contraseña existente"""
    mostrar_contrasenas()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        id_pwd = int(input(Fore.WHITE + "\nIngrese el ID de la contraseña a editar (0 para cancelar): " + Style.RESET_ALL))
        if id_pwd == 0:
            return

        cursor.execute('SELECT service, username, password, notes FROM passwords WHERE id = ?', (id_pwd,))
        pwd = cursor.fetchone()

        if not pwd:
            print(Fore.RED + "\n❌ No se encontró una contraseña con ese ID." + Style.RESET_ALL)
            return

        print(Fore.CYAN + "\nDeje en blanco los campos que no desea cambiar:" + Style.RESET_ALL)
        new_service = input(f"Nuevo servicio [{pwd[0]}]: ") or pwd[0]
        new_username = input(f"Nuevo usuario [{pwd[1] or ''}]: ") or pwd[1]
        new_password = input(f"Nueva contraseña [{pwd[2]}]: ") or pwd[2]
        new_notes = input(f"Nuevas notas [{pwd[3] or ''}]: ") or pwd[3]

        cursor.execute('''
            UPDATE passwords 
            SET service = ?, username = ?, password = ?, notes = ?
            WHERE id = ?
        ''', (new_service, new_username, new_password, new_notes, id_pwd))

        conn.commit()
        print(Fore.GREEN + "\n✅ Contraseña actualizada correctamente!" + Style.RESET_ALL)

    except ValueError:
        print(Fore.RED + "\n❌ ID inválido. Debe ser un número." + Style.RESET_ALL)
    finally:
        conn.close()

def reiniciar_secuencia_ids():
    """
    Reinicia la secuencia de IDs para que comiencen desde 1 nuevamente.
    Se ejecuta automáticamente cuando se borran todas las contraseñas.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Verificar si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM passwords")
    count = cursor.fetchone()[0]

    if count == 0:
        try:
            # Reiniciar la secuencia de IDs
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='passwords'")
            conn.commit()
            print(Fore.BLUE + "\nℹ️ Secuencia de IDs reiniciada (comenzarán desde 1)." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.YELLOW + f"\n⚠️ No se pudo reiniciar la secuencia de IDs: {e}" + Style.RESET_ALL)

    conn.close()

def eliminar_contrasena():
    """Elimina una contraseña de la base de datos"""
    mostrar_contrasenas()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        id_pwd = int(input(Fore.WHITE + "\nIngrese el ID de la contraseña a eliminar (0 para cancelar): " + Style.RESET_ALL))
        if id_pwd == 0:
            return

        cursor.execute('DELETE FROM passwords WHERE id = ?', (id_pwd,))
        conn.commit()

        if cursor.rowcount > 0:
            print(Fore.GREEN + "\n✅ Contraseña eliminada correctamente!" + Style.RESET_ALL)
            # Verificar si quedan contraseñas
            cursor.execute("SELECT COUNT(*) FROM passwords")
            if cursor.fetchone()[0] == 0:
                reiniciar_secuencia_ids()
        else:
            print(Fore.RED + "\n❌ No se encontró una contraseña con ese ID." + Style.RESET_ALL)

    except ValueError:
        print(Fore.RED + "\n❌ ID inválido. Debe ser un número." + Style.RESET_ALL)
    finally:
        conn.close()

def resetear_base_datos():
    """
    Borra completamente la base de datos y la reinicializa desde cero.
    Pide confirmación al usuario antes de proceder.
    """
    print(Fore.RED + "\n⚠️ ADVERTENCIA: Esto borrará TODAS las contraseñas almacenadas." + Style.RESET_ALL)
    confirmacion = input("¿Estás seguro que deseas resetear la base de datos? (s/n): ").lower()

    if confirmacion == 's':
        try:
            # Eliminar el archivo de base de datos existente
            if os.path.exists(DB_NAME):
                os.remove(DB_NAME)
                print(Fore.YELLOW + "\nBase de datos eliminada..." + Style.RESET_ALL)

            # Crear una nueva base de datos vacía
            inicializar_base_datos()
            print(Fore.GREEN + "✅ Base de datos reseteada correctamente. Ahora está vacía." + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"\n❌ Error al resetear la base de datos: {e}" + Style.RESET_ALL)
    else:
        print(Fore.BLUE + "\nOperación cancelada. La base de datos no fue modificada." + Style.RESET_ALL)

# =============================================
# FUNCIONES DE GENERACIÓN DE CONTRASEÑAS
# =============================================

def generar_contrasena(longitud, cant_mayusculas, cant_numeros, cant_simbolos):
    """
    Genera una contraseña aleatoria según los parámetros especificados.

    Parámetros:
    - longitud: Longitud total de la contraseña
    - cant_mayusculas: Cantidad de letras mayúsculas
    - cant_numeros: Cantidad de números
    - cant_simbolos: Cantidad de símbolos

    Retorna:
    - La contraseña generada como string
    """
    contrasena = []

    # Añadir caracteres según cantidades solicitadas
    contrasena += random.choices(string.ascii_uppercase, k=cant_mayusculas)
    contrasena += random.choices(string.digits, k=cant_numeros)
    contrasena += random.choices(string.punctuation, k=cant_simbolos)

    # Rellenar con minúsculas el resto
    restante = longitud - len(contrasena)
    contrasena += random.choices(string.ascii_lowercase, k=restante)

    # Mezclar el orden de los caracteres
    random.shuffle(contrasena)

    return ''.join(contrasena)

def pedir_entero(mensaje, minimo=0):
    """
    Solicita al usuario un número entero validando que sea correcto.

    Parámetros:
    - mensaje: Texto a mostrar al usuario
    - minimo: Valor mínimo aceptado (por defecto 0)

    Retorna:
    - El número entero válido ingresado por el usuario
    """
    while True:
        try:
            valor = int(input(mensaje))
            if valor < minimo:
                print(Fore.RED + f"❗ El valor no puede ser menor que {minimo}. Intenta de nuevo." + Style.RESET_ALL)
            else:
                return valor
        except ValueError:
            print(Fore.RED + "❗ Entrada no válida. Ingresa un número entero." + Style.RESET_ALL)

# =============================================
# INTERFAZ DE USUARIO
# =============================================

def generar_y_guardar_contrasenas():
    """Genera contraseñas y pregunta si desea guardarlas"""
    print(Fore.CYAN + "=" * 60)
    print("🔐 GENERAR CONTRASEÑAS".center(60))
    print("=" * 60 + Style.RESET_ALL)

    while True:
        cantidad_contrasenas = pedir_entero("👉 ¿Cuántas contraseñas deseas generar?: ", minimo=1)
        longitud = pedir_entero("👉 Longitud total de la contraseña (mínimo 4): ", minimo=4)
        cant_mayusculas = pedir_entero("👉 ¿Cuántas letras mayúsculas?: ")
        cant_numeros = pedir_entero("👉 ¿Cuántos números?: ")
        cant_simbolos = pedir_entero("👉 ¿Cuántos símbolos?: ")

        total_especificado = cant_mayusculas + cant_numeros + cant_simbolos
        if total_especificado > longitud:
            print(Fore.RED + f"\n❌ La suma de mayúsculas, números y símbolos ({total_especificado}) excede la longitud total ({longitud}). Intenta de nuevo.\n" + Style.RESET_ALL)
        else:
            break

    # Mostrar contraseñas en formato llamativo con colores
    print(Fore.CYAN + "\n" + "*" * 60)
    print("🔒 TUS CONTRASEÑAS GENERADAS 🔒".center(60))
    print("*" * 60 + Style.RESET_ALL)

    contrasenas_generadas = []
    for i in range(1, cantidad_contrasenas + 1):
        contrasena = generar_contrasena(longitud, cant_mayusculas, cant_numeros, cant_simbolos)
        contrasenas_generadas.append(contrasena)
        print(Fore.GREEN + f"🔹 {i:02d}. {contrasena}" + Style.RESET_ALL)

    print(Fore.CYAN + "*" * 60)
    print(Fore.YELLOW + "✅ ¡Recuerda guardarlas en un lugar seguro!".center(60))
    print("*" * 60 + Style.RESET_ALL)

    # Preguntar si desea guardar alguna contraseña
    guardar = input(Fore.WHITE + "\n¿Deseas guardar alguna contraseña en la base de datos? (s/n): " + Style.RESET_ALL).lower()
    if guardar == 's':
        for i, contrasena in enumerate(contrasenas_generadas, 1):
            guardar_esta = input(Fore.WHITE + f"\n¿Guardar la contraseña {i}? (s/n): " + Style.RESET_ALL).lower()
            if guardar_esta == 's':
                service = input("Para qué servicio es esta contraseña: ")
                username = input("Nombre de usuario (opcional): ")
                notes = input("Notas adicionales (opcional): ")
                guardar_contrasena(service, username, contrasena, notes)
                print(Fore.GREEN + f"✅ Contraseña para {service} guardada correctamente!" + Style.RESET_ALL)

def menu_principal():
    """Muestra el menú principal con opciones coloreadas"""
    print(Fore.CYAN + "\n" + "=" * 60)
    print("🔐 MENÚ PRINCIPAL".center(60))
    print("=" * 60)
    print(Fore.GREEN + "1. Generar nuevas contraseñas")
    print(Fore.YELLOW + "2. Ver contraseñas guardadas")
    print(Fore.BLUE + "3. Editar contraseña existente")
    print(Fore.MAGENTA + "4. Eliminar contraseña")
    print(Fore.RED + "5. RESETEAR BASE DE DATOS (¡Cuidado!)")
    print(Fore.CYAN + "6. Salir")
    print(Style.RESET_ALL + "=" * 60)

def menu_gestion_base_datos():
    """Controla el flujo principal del programa"""
    # Inicializar la base de datos al iniciar
    inicializar_base_datos()

    while True:
        menu_principal()
        opcion = input(Fore.WHITE + "👉 Seleccione una opción: " + Style.RESET_ALL)

        if opcion == "1":
            generar_y_guardar_contrasenas()
        elif opcion == "2":
            mostrar_contrasenas()
        elif opcion == "3":
            editar_contrasena()
        elif opcion == "4":
            eliminar_contrasena()
        elif opcion == "5":
            resetear_base_datos()
        elif opcion == "6":
            print(Fore.CYAN + "\n¡Hasta pronto! 👋" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "\n❌ Opción inválida. Intente de nuevo." + Style.RESET_ALL)

# =============================================
# INICIO DEL PROGRAMA
# =============================================

if __name__ == "__main__":
    menu_gestion_base_datos()