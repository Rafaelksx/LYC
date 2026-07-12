// Programa de Ejemplo 2 en MiniRust con Errores Léxicos Intencionales
// Demuestra el comportamiento del analizador al encontrar caracteres fuera del alfabeto

fn procesar_datos() {
    let valor: f64 = 3.14159;
    
    // El símbolo @ y ¿ no pertenecen a la gramática léxica de MiniRust
    let tasa@anual: f64 = valor * 1.05;
    
    if valor > 0.0 {
        println!("Procesado correctamente");
    } ¿¿ error_sintactico ??
}
