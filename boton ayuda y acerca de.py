import tkinter as tk
from tkinter import messagebox

def mostrar_bienvenida():
    messagebox.showinfo("Bienvenido", "¡Hola! Bienvenido a mi aplicación.")

def mostrar_ayuda():
    messagebox.showinfo("Ayuda", "Enseguida se notificara tu mensaje de ayuda a nuestro servidor.")

def mostrar_acerca_de():
    messagebox.showinfo("Acerca de", "Versión 1.0\nAutor: Kevin Reyes. \nAño: 2024")

def main():
    # Crear la ventana principal
    ventana_inicio = tk.Tk()
    ventana_inicio.title("Ventana de Inicio")

    # Etiqueta de bienvenida
    etiqueta_bienvenida = tk.Label(ventana_inicio, text="Bienvenido a mi aplicación", font=("Helvetica", 16))
    etiqueta_bienvenida.pack(pady=20)

    # Botón de inicio
    boton_inicio = tk.Button(ventana_inicio, text="Iniciar", command=mostrar_bienvenida)
    boton_inicio.pack(pady=10)

    # Botón de ayuda
    boton_ayuda = tk.Button(ventana_inicio, text="Ayuda", command=mostrar_ayuda)
    boton_ayuda.pack(pady=5)

    # Botón de acerca de
    boton_acerca_de = tk.Button(ventana_inicio, text="Acerca de", command=mostrar_acerca_de)
    boton_acerca_de.pack(pady=5)

    # Ejecutar el bucle principal
    ventana_inicio.mainloop()

if __name__ == "__main__":
    main()
