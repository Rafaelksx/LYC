// Programa de Ejemplo 1 en MiniRust (Subconjunto de Rust)
// Demuestra declaración de variables inmutables y mutables, tipos, bucles e impresión

fn calcular_factorial(n: i32) -> i32 {
    let mut resultado: i32 = 1;
    let mut contador: i32 = 1;

    while contador <= n {
        resultado = resultado * contador;
        contador += 1;
    }

    return resultado;
}

fn main() {
    let numero: i32 = 5;
    let es_positivo: bool = true;

    if es_positivo && numero > 0 {
        let facto: i32 = calcular_factorial(numero);
        println!("El factorial es calculado con exito");
    } else {
        println!("Numero invalido");
    }
}
