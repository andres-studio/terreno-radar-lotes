# Terreno · Radar de lotes

PWA para iPhone, con Jardín (Antioquia) como piloto. Sin dependencias de frontend ni claves para arrancar. Interfaz editorial con tipografía del sistema, tonos minerales, tarjetas, favoritos, comparación y asesor documental.

## Qué funciona

- Catálogo inicial: cuatro anuncios/proyectos observados el 2 de noviembre de 2026. Enlaces originales, precio, área y fecha; disponibilidad no confirmada.
- Filtros por precio, área y texto; orden por precio o $/m²; comparación de hasta tres anuncios.
- Municipio y departamento configurables. Guardados, notas, checklist e incorporación manual por enlace en el dispositivo.
- Exportación e importación de respaldo JSON. No hay cuenta ni sincronización entre dispositivos.
- Guía de compra: propiedad, norma territorial, ambiente, riesgo, tributos y financiación por destino.
- Simulador con tasa EA convertida a mensual, plazo, recursos propios, gastos de cierre cotizados y provisión anual; sin una tasa crediticia real asumida.
- Monitor Python, historial de precio **y área**, robots.txt, deduplicación por URL, errores conservados y GitHub Actions con publicación Pages.
- PWA con iconos, manifest y caché de última visita. La lectura del catálogo usa red primero; sin red puede mostrar una captura antigua con fecha.

## Alcance real del rastreo

No es un acceso universal a anuncios ni una API de Meta. Se vigilan cuatro fuentes configuradas en `sources.json`. El descubrimiento adicional usa Bing RSS sin clave, sujeto a disponibilidad y robots.txt; resultados sin precio COP y datos estructurados inequívocos se conservan como candidatos, no como lotes verificados. Facebook, contenido privado y portales que bloquean el acceso se consultan manualmente. El monitor no evita bloqueos ni inicia sesión.

Un fallo de consulta no cambia la fecha de observación, no borra un anuncio y no implica que se haya vendido. Nunca divide el precio mínimo de un proyecto entre un área mínima independiente. No se afirma que se hayan detectado todos los anuncios ni se identifica el mismo predio de portales diferentes automáticamente. El historial registra observaciones desde su incorporación; no reconstruye el pasado.

## Publicar en GitHub desde iPhone

1. Crea el repositorio `radar-lotes` en tu cuenta (por ejemplo `afherna1`). Un repositorio público facilita Pages con GitHub Free; su catálogo será público. No subas escrituras, documentos privados ni tus respaldos personales.
2. Extrae el ZIP y sube **el contenido** al repositorio en la raíz, preservando `dist`, `scripts`, `tests`, `sources.json` y `.github/workflows/monitor.yml`. GitHub no descomprime ZIPs automáticamente.
3. Si iOS no muestra `.github`, crea el archivo en GitHub → Add file → Create new file y escribe `.github/workflows/monitor.yml`. Copia el texto de `WORKFLOW_PARA_COPIAR.txt`, incluido en este paquete. Ese archivo es una copia exacta del workflow.
4. En Settings → Pages → Build and deployment selecciona **GitHub Actions**. En Settings → Actions → General permite los workflows y, si tu cuenta lo requiere, permisos de lectura y escritura para el workflow. No necesitas tokens personales ni claves de pago.
5. Actions → **Monitor y publicar Terreno** → Run workflow → Jardín / Antioquia. Revisa el resultado del monitor y la publicación; los errores de fuentes aparecen también en `dist/data/catalog.json`.
6. Abre la URL que devuelve Pages en Safari → Compartir → Añadir a pantalla de inicio → Abrir como app web. No se instala desde un HTML local en Archivos.

El workflow propone lunes a sábado a las 07:10 y 17:10 de Colombia (12:10 y 22:10 UTC); GitHub puede retrasarlo y pausar schedules en repositorios públicos inactivos. El horario comienza a funcionar cuando Actions esté habilitado y el workflow esté en la rama principal. Un push también valida, rastrea y publica. Los commits creados por GITHUB_TOKEN no crean un bucle de workflows de push.

## Otro municipio

En la app toca **Jardín, Antioquia** para cambiar territorio. El selector filtra el catálogo y permite guardar anuncios manuales: no ejecuta Actions desde el navegador. Para iniciar el rastreo: Actions → Run workflow → escribe municipio y departamento. Los territorios registrados en el catálogo o en las ejecuciones se vuelven a consultar en las corridas programadas siguientes. Fuentes específicas nuevas se agregan a `sources.json`; si no hay datos estructurados compatibles se necesita un adaptador. La revisión normativa municipal requiere fuentes propias; la app lo señala como pendiente y no hereda la norma de Jardín.

## Ejecutar y verificar

Python 3.10+ y Node para verificar JS (sin librerías externas):

```bash
python -m unittest discover -s tests -v
node --check dist/app.js
python scripts/monitor.py --municipio 'Jardín' --departamento 'Antioquia' --discover
python scripts/monitor.py --all
python -m http.server 8000 --directory dist
```

## Asesor y fuentes

Es un asistente documental basado en reglas, no un LLM conectado ni un dictamen de compra. No aprueba financiación, construcciones, títulos ni exenciones por municipio. No se ha confirmado un beneficio tributario específico para Jardín. Para cada predio se requiere soporte y revisión competente. Las condiciones del crédito se confirman con el intermediario y el programa vigente.

Fuentes de referencia, consultadas el 2 de noviembre de 2026:

- EOT: [Acuerdo 016 de 2018, estructura](https://www.antioquiadatos.gov.co/territorio_antioquia/wp-content/uploads/2023/02/Ordenamiento-Municipios/suroeste/jardin.pdf). Vigencia/modificaciones y planos por confirmar en Planeación.
- [Determinantes ambientales, Corantioquia](https://www.corantioquia.gov.co/ordenamiento-ambiental-del-territorio/).
- [SNR: tradición y libertad](https://www.supernotariado.gov.co/atencion-servicios-ciudadania/tramites-y-servicios/).
- [FINAGRO: crédito](https://www.finagro.com.co/atencion-servicios-ciudadania/tramites-opa-consulta-informacion/recursos-credito/credito-agropecuario-rural/credito).
- Anuncios en `sources.json`. Las afirmaciones comerciales no equivalen a una verificación del predio.

## Datos y privacidad

El catálogo y candidatos son públicos cuando se despliega con Pages. Favoritos, notas, checklist y anuncios manuales están en localStorage del origen; no se suben al repositorio ni se envían a un modelo. El borrado de datos del navegador los elimina. Los enlaces externos abren proveedores independientes. No se incorporan fotos ajenas: los paisajes de tarjetas son ilustraciones CSS identificadas como tales.

## Operación

Revisa periódicamente cambios en robots, estructura de portales, fuentes oficiales y condiciones crediticias. El script utiliza únicamente páginas públicas accesibles; restricciones de red pueden impedir validar el rastreo en algunos entornos. Una ejecución con errores conserva los últimos datos observados, con su fecha. No hay notificaciones push ni contacto automático al vendedor.

## Prototipo v2 · experiencia

Navegación inferior en móvil, paneles inferiores, controles segmentados, vistas tarjeta/lista, modo claro/oscuro, gráficos SVG interactivos y accesibles. Panorama compara exclusivamente anuncios individuales con precio y área conocidos (excluye mínimos independientes). La mediana describe esa muestra; no es un avalúo municipal. El simulador muestra el saldo de crédito y la distribución entre capital e intereses según valores introducidos. No se dibuja tendencia de precio cuando solo existe una observación.

## Actualización documental · 11 de noviembre de 2026

13 registros: los cuatro originales y nueve incorporaciones. Se conservan IDs e historial; las cuatro fuentes originales mantienen sus precios publicados. Las consultas se realizaron mediante recuperación web, a veces de páginas indexadas meses antes: no equivalen a disponibilidad comercial verificada. Se añadieron procedencia, consultas y fuentes coincidentes. Se excluyen del panorama de suelo los proyectos con mínimos independientes y dos anuncios con mejoras/cabaña/glamping. El catálogo ampliado no duplica las publicaciones coincidentes de Comfenalco o Estadio. Una ficha de Ciencuadras no accesible queda como candidata, sin precio incorporado. Ver `dist/data/revision-2026-11-11.json`. El rastreo programado en GitHub sigue pendiente de activación/verificación; esta revisión es documental.

## Fotos, enlaces, mapas y revisión documental · 11 noviembre

Se recuperaron directamente por HTTPS las 13 publicaciones (HTTP 200) y se conservaron 32 fotografías con sus URLs y créditos de origen. Se verificó el formato de las imágenes. Los enlaces y las fotos fueron accesibles en la fecha de consulta; no garantizan disponibilidad comercial futura. Las fichas contienen resúmenes fieles de los datos anunciados y fragmentos textuales breves, con enlace al contenido completo en el portal. No se republica la descripción íntegra.

Doce fichas incluyen un punto publicado por el portal. Dos puntos se repiten entre sectores y se advierte la precisión desconocida. No hay geocodificación que simule límites de un predio. Los mapas son referencias OpenStreetMap y enlaces a Apple Maps; requieren conexión. La ficha restante ofrece búsqueda por sector, sin marcador predial.

La revisión distingue afirmaciones del vendedor y soportes pendientes. No se identificaron documentos prediales suficientes para acreditar títulos o licencias: 0 documentos oficialmente verificados. El código comercial no se trata como matrícula inmobiliaria. Se enlazan SNR, Minvivienda y Corantioquia. Las casillas y notas personales no se convierten en certificados.

### Ampliación de fuentes · 11 de noviembre de 2026

El catálogo contiene 20 fichas: se conservaron las 13 anteriores y se añadieron siete. Se identifican ocho anunciantes comerciales; cinco fichas tienen identidad pendiente (cuatro del usuario 825391 de Ciencuadras y un clasificado local). Se agrupan las siete fichas de MIACTIVO aunque aparezcan en distintos portales: representan el 35 % del catálogo. No se ha certificado la identidad jurídica ni la reputación de los anunciantes.

Nuevas publicaciones: Inmobiliaria Selecta, Díaz Propiedades (dos lotes), El Búho Inmobiliaria, Emisa Soluciones, Jardín Colombia Real Estate y clasificados Jardín Antioquia. Las seis fichas nuevas con imágenes suman 21 fotografías; el clasificado La Esmeralda conserva el enlace al álbum del anunciante sin presentar imágenes no recuperadas como fotos del lote. La Esmeralda conserva la fecha de publicación de diciembre de 2025, sin confirmar disponibilidad actual. La oferta de El Búho reúne varios lotes y no participa en comparaciones de precio por metro cuadrado.

La sección **Fuentes y anunciantes** separa publicaciones, cinco contactos locales y seis canales sociales. Gold Plus, La 10, A.G. SAS, Gustavo Valencia y WM son contactos del directorio de Jardín; no se cuentan como lotes cargados. Los perfiles sociales provienen de enlaces de las propias inmobiliarias. La lectura pública de Facebook/Instagram estuvo limitada: no se incorporaron publicaciones sin verificar ni se promete rastreo automático de redes.

El monitor incorpora extracción etiquetada de Emisa/Espacio Urbano con comprobación del código de anuncio y conserva las ofertas que requieren consulta manual. Los metadatos de anunciante y las banderas de proyecto se mantienen durante las actualizaciones. El precio publicado no acredita disponibilidad ni licencias. Los pines municipales repetidos de las nuevas fichas de Díaz y Jardín Colombia Real Estate se descartaron, pendientes de ubicación predial.

Auditoría y procedencias: `dist/data/source-audit-2026-11-11.json`. Pruebas: `python -m unittest discover -s tests`.
