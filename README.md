# CryptoRacers: Juego de Carreras Cifrado de Extremo a Extremo

## Descripción del Proyecto
CryptoRacers es una aplicación de escritorio desarrollada en Python que simula un juego de carreras de vehículos. El propósito central del proyecto es implementar conceptos avanzados de criptografía, protegiendo tanto los datos locales del jugador como las interacciones y desafíos enviados entre distintos usuarios del sistema.

## Arquitectura de Seguridad y Criptografía
El núcleo de la aplicación radica en su infraestructura criptográfica, que garantiza la confidencialidad, integridad, autenticidad y no repudio en cada proceso:

*   **Almacenamiento Local Seguro (AES-256 GCM):** Los perfiles de usuario, incluyendo su garaje y puntos, se cifran localmente utilizando cifrado simétrico AES en modo GCM. La clave de cifrado se deriva de la contraseña del usuario aplicando 200.000 iteraciones de la función hash SHA-256 junto con un *salt*.
*   **Autenticación:** Las contraseñas no se almacenan en texto plano. El inicio de sesión se valida comparando un hash SHA-256 (también procesado con 200.000 iteraciones y un *salt* específico). El sistema impone validaciones mediante expresiones regulares para garantizar contraseñas robustas (requiriendo mayúsculas, números, símbolos y una longitud mínima de 12 caracteres).
*   **Infraestructura de Clave Pública (PKI) y Certificados X.509:** En el momento del registro, se generan dos pares de claves RSA de 2048 bits para cada usuario: un par para operaciones de cifrado ("cod") y otro para firma digital ("sign"). El sistema utiliza comandos de sistema hacia `openssl` para generar solicitudes de firma de certificados (CSR) y emitir certificados X.509 validados por una jerarquía de Autoridades de Certificación (alternando la asignación entre AC2 y AC3 subordinadas).
*   **Comunicaciones Seguras (Cifrado Híbrido):** Cuando un usuario propone una carrera a otro, los detalles del vehículo elegido se cifran con una clave simétrica temporal. A continuación, esta clave temporal se cifra utilizando la clave pública (RSA-OAEP) del destinatario, tras haber verificado la validez de su certificado X.509.
*   **Firmas Digitales (RSASSA-PSS):** Para asegurar la autenticidad de los desafíos, los datos de la carrera se firman digitalmente utilizando el algoritmo RSASSA-PSS junto con la clave privada de firma del emisor. El destinatario verifica esta firma antes de descifrar y visualizar el desafío.

## Funcionalidades del Juego
*   **Tienda y Mejoras:** Los jugadores comienzan con un saldo inicial de 200 puntos, los cuales pueden invertir en la compra de nuevos vehículos y en mejoras mecánicas que alteran las estadísticas base (velocidad, manejo, aceleración y frenada).
*   **Desafíos Multijugador asíncronos:** Los usuarios pueden proponer carreras a cualquier otro jugador registrado ingresando su nombre de usuario y seleccionando un vehículo de su garaje.
*   **Resolución de Carreras:** Al aceptar un desafío, el sistema compara la suma total de las estadísticas del vehículo del emisor frente a las del receptor. La lógica de la carrera incluye un componente de aleatoriedad (representando adelantamientos o accidentes en curvas) para determinar el ganador. El vencedor suma 200 puntos a su cuenta, mientras que el perdedor los resta.
*   **Interfaz Gráfica y Terminal Virtual:** Toda la interacción se gestiona a través de ventanas gráficas que incluyen un componente visual de consola de texto. Esta terminal informa en tiempo real sobre los procesos criptográficos subyacentes, la generación de firmas y el transcurso narrativo de las carreras.

## Stack Tecnológico
*   **Lenguaje:** Python.
*   **Interfaz Gráfica:** `tkinter` para la construcción de vistas y navegación.
*   **Criptografía:** Módulos de `Crypto` (incluyendo `Cipher`, `PublicKey`, `Signature` y `Hash`) para la implementación de algoritmos estándar (AES, RSA, SHA256).
*   **Certificación:** Integración directa con `openssl` a través de la librería `subprocess` para gestionar la infraestructura PKI.
