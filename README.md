# Integración Inumet Uruguay para Home Assistant

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=matbott&repository=ha-inumet-uruguay&category=integration)

Esta es una integración personalizada para Home Assistant que obtiene datos meteorológicos directamente de las fuentes de datos públicas del **Instituto Uruguayo de Meteorología (Inumet)**.

![image](https://github.com/user-attachments/assets/d903210a-4761-45eb-9c35-9c49e8fa47b6)

Proporciona monitoreo de alertas meteorológicas, condiciones actuales de estaciones y el pronóstico extendido para todo el país, permitiendo una integración completa y detallada del tiempo de Uruguay en tu instancia de Home Assistant.

## Funcionalidades Principales

* **Configuración desde la Interfaz:** Se instala y configura fácilmente a través del flujo de configuración de Home Assistant.
* **Selección Dinámica de Estaciones:** Al configurar, la integración carga la lista completa de estaciones meteorológicas oficiales de Inumet y la presenta en un menú desplegable para una fácil selección.
* **Múltiples Estaciones:** Permite configurar **hasta 3 instancias diferentes** para monitorear 3 estaciones meteorológicas de forma simultánea.
* **Intervalo de Actualización Personalizable:** Permite al usuario definir la frecuencia de actualización (entre 30 y 240 minutos) durante la configuración y modificarla posteriormente desde las opciones de la integración.
* **Entidades Completas:** Crea un dispositivo por cada estación configurada, el cual agrupa:
    * Una entidad `weather` principal con el pronóstico de varios días.
    * Sensores individuales para temperatura, humedad, presión y viento.
    * Un sensor binario para el estado de alertas.
    * Entidades de imagen para el mapa oficial de alertas de Inumet, el mapa de Índice de Peligro de Incendio (FWI) y el mapa de Índice UV.
    * Una entidad `camera` para las estaciones que cuentan con una cámara pública.

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

¡Listo! La integración se configurará y creará un nuevo dispositivo con todas sus entidades. Puedes repetir este proceso para monitorear diferentes estaciones.

## Entidades Creadas

Por cada estación que configures, se creará un **Dispositivo** en Home Assistant llamado `Inumet Uruguay - [Nombre de la Estación]`. Dentro de este dispositivo, encontrarás las siguientes entidades:

* **`weather.[nombre_estacion]`**: La entidad principal del tiempo. Muestra la temperatura actual, máxima/mínima del día y el icono del tiempo. Al hacer clic, despliega el pronóstico detallado para los próximos días.
* **`binary_sensor.alerta`**: Sensor que se enciende (estado: "Inseguro") cuando hay una o más alertas meteorológicas activas. Los detalles de la alerta se encuentran en sus atributos.
* **`image.mapa_de_alertas`**: Muestra el mapa oficial de alertas de Inumet.
* **`image.mapa_de_peligro_de_incendio_fwi`**: Muestra el mapa diario con el Índice de Peligro de Incendio.
* **`image.mapa_de_indice_uv`**: Muestra el último mapa disponible del Índice UV.
* **`camera.camara_estacion`**: Entidad de cámara que contiene la URL del video de la estación (si está disponible).
* **Sensores individuales**:
    * `sensor.temperatura`
    * `sensor.humedad_relativa`
    * `sensor.presion`
    * `sensor.velocidad_del_viento`
    * `sensor.direccion_del_viento`

## Configuración Avanzada: Visualizar Cámara con `button-card`

La entidad de la cámara no muestra el video directamente en una tarjeta estándar. La mejor manera de visualizarla es con un popup usando las integraciones de HACS **`browser_mod`** y **`button-card`**.

1.  Asegúrate de tener `browser_mod` y `button-card` instalados desde HACS.
2.  Añade una tarjeta **Manual** a tu panel y usa la siguiente configuración como plantilla:

```yaml
type: custom:button-card
name: Ver Cámara de [Nombre Estación]
icon: mdi:cctv
tap_action:
  action: call-service
  service: browser_mod.popup
  service_data:
    title: Cámara Estación [Nombre Estación]
    content:
      type: iframe
      url: >-
        [[[ return
        states['camera.inumet_uruguay_[entidad_de_tu_estacion]_camara_estacion'].attributes.direct_url;
        ]]]
styles:
  card:
    - padding: 4px
  icon:
    - height: 50px
  name:
    - font-size: 12px
```

**Importante:** Debes reemplazar [Nombre Estación] y camera.inumet_uruguay_[entidad_de_tu_estacion]_camara_estacion con los nombres y el entity_id correctos de tu entidad.

## Autor

Desarrollado por **@matbott & 🤖**.

## Aviso

Esta es una integración no oficial y no está afiliada ni respaldada por Inumet. Depende de APIs públicas que podrían cambiar sin previo aviso, lo que podría causar que la integración deje de funcionar.

## Agradecimiento:

Gracias a https://github.com/aronkahrs-us/inumet-weather-ha por la implementacion que dio lugar a este desarrollo.
