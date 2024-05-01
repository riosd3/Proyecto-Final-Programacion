import tkinter as tk
from tkinter import messagebox

def mostrar_bienvenida():
    messagebox.showinfo("Bienvenido", "¡Hola! Bienvenido al menu principal.")

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

    # Ejecutar el bucle principal
    ventana_inicio.mainloop()

if __name__ == "__main__":
    main()
