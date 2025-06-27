# Integración Inumet Uruguay para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Esta es una integración personalizada para Home Assistant que obtiene datos meteorológicos directamente de las fuentes de datos públicas del **Instituto Uruguayo de Meteorología (Inumet)**.

![image](https://github.com/user-attachments/assets/d2056e9a-b3e6-4bd8-9e50-7676776087bc)

Proporciona monitoreo de alertas meteorológicas, condiciones actuales de estaciones y el pronóstico extendido para todo el país, permitiendo una integración completa y detallada del tiempo de Uruguay en tu instancia de Home Assistant.

## Funcionalidades Principales

* **Configuración desde la Interfaz:** Se instala y configura fácilmente a través del flujo de configuración de Home Assistant.
* **Selección Dinámica de Estaciones:** Al configurar, la integración carga la lista completa de estaciones meteorológicas oficiales de Inumet y la presenta en un menú desplegable para una fácil selección.
* **Múltiples Estaciones:** Permite configurar **hasta 3 instancias diferentes** para monitorear 3 estaciones meteorológicas de forma simultánea.
* **Intervalo de Actualización Personalizable:** Permite al usuario definir la frecuencia de actualización (entre 30 y 240 minutos) durante la configuración y modificarla posteriormente desde las opciones de la integración.
* **Entidades Completas:** Crea un dispositivo por cada estación configurada, el cual agrupa:
    * Una entidad `weather` principal con el pronóstico de 7 días.
    * Sensores individuales para temperatura, humedad, presión y viento.
    * Un sensor binario para el estado de alertas.
    * Una entidad de imagen con el mapa oficial de alertas de Inumet.

## Instalación

### Método 1: HACS (Recomendado)

Si tienes [HACS (Home Assistant Community Store)](https://hacs.xyz/) instalado, esta es la forma más sencilla de instalar y mantener actualizada la integración.

1.  Abre HACS en tu Home Assistant.
2.  Ve a **Integraciones**.
3.  Haz clic en los tres puntos en la esquina superior derecha y selecciona **"Repositorios Personalizados"**.
4.  Pega la URL de este repositorio (`https://github.com/matbott/inumet-uruguay-ha`) en el campo, selecciona la categoría **"Integración"** y haz clic en **"Añadir"**.
5.  La integración aparecerá en la lista. Haz clic en **"Instalar"**.

### Método 2: Instalación Manual

1.  Ve a la sección de [Releases](https://github.com/matbott/inumet-uruguay-ha/releases) de este repositorio y descarga el archivo `.zip` de la última versión.
2.  Descomprime el archivo.
3.  Copia la carpeta `inumet_uruguay` que se encuentra dentro de `custom_components` en tu descarga.
4.  Pégala dentro de la carpeta `custom_components` de tu instalación de Home Assistant. (La ruta final debería ser `<config>/custom_components/inumet_uruguay`).
5.  Reinicia Home Assistant.

## Configuración

1.  Después de instalar (y reiniciar si lo hiciste manualmente), ve a **Ajustes > Dispositivos y Servicios**.
2.  Haz clic en el botón **"+ Añadir Integración"** en la esquina inferior derecha.
3.  Busca **"Inumet Uruguay"** en la lista y haz clic en ella.
4.  Aparecerá un formulario:
    * **Estación:** Selecciona la estación meteorológica que deseas monitorear de la lista desplegable.
    * **Intervalo de actualización:** Define cada cuántos minutos quieres que se actualicen los datos.
5.  Haz clic en **"Enviar"**.

¡Listo! La integración se configurará y creará un nuevo dispositivo con todas sus entidades. Puedes repetir este proceso hasta 3 veces para monitorear diferentes estaciones.

## Entidades Creadas

Por cada estación que configures, se creará un **Dispositivo** en Home Assistant llamado `Inumet Uruguay - [Nombre de la Estación]`. Dentro de este dispositivo, encontrarás las siguientes entidades:

* **`weather.[nombre_estacion]`**: La entidad principal del tiempo. Muestra la temperatura actual y el icono del tiempo. Al hacer clic, despliega el pronóstico detallado para los próximos 7 días.
* **`binary_sensor.alerta`**: Sensor que se enciende (estado: "Inseguro") cuando hay una o más alertas meteorológicas activas. Los detalles de la alerta (título, severidad, descripción) se encuentran en sus atributos.
* **`image.mapa_de_alertas`**: Muestra el mapa oficial de alertas de Inumet. Es ideal para mostrar en el panel de control usando una tarjeta de imagen.
* **Sensores individuales**:
    * `sensor.temperatura`
    * `sensor.humedad_relativa`
    * `sensor.presion`
    * `sensor.velocidad_del_viento`
    * `sensor.direccion_del_viento`

## Autor

Desarrollado por **@matbott**.

## Aviso

Esta es una integración no oficial y no está afiliada ni respaldada por Inumet. Depende de APIs públicas que podrían cambiar sin previo aviso, lo que podría causar que la integración deje de funcionar.
