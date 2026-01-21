//aqui se pone la base a trabajar
use('test');
//comando para llamar las colecciones
db.getCollectionNames();
• Documento (document): similar a un registro, en formato JSON.
• Campo (field): clave dentro de un documento.
Comandos Básicos
• use('test') → Selecciona una base de datos.
• show dbs → Lista todas las bases de datos.
• db.getCollectionNames() → Lista colecciones.
• db.coleccion.insertOne({...}) → Inserta un documento.
• db.coleccion.find() → Consulta documentos.
• db.coleccion.updateOne(filtro, {$set: {...}}) → Actualiza.
• db.coleccion.deleteOne(filtro) → Elimina.
Estructura de Ejemplo (Libro)
{ titulo, capitulos: [{ capitulo, parrafos: [{ parrafo, contenido }] }] }
Buenas Prácticas
• Usar nombres en minúsculas y en plural.
• Mantener consistencia en los tipos de datos.
• Evitar documentos excesivamente grandes.
• Agregar campos de fecha (created_at)


[]esta es la estructura para viajes en modulo personal
SQL SERVER (autoridad)
└── DAT_EVENTOS_PERSONAL
     └── ID (VIAJE_ID)
          │
          │ (INT)
          ▼
MongoDB
└── viajes
     └── viaje_id : 17
          └── secciones[]
               └── parrafos[]
                    └── frases[]

//ejemplo de consulta en MongoDB

use ('404webpagedb')

db.getCollection('viajes').aggregate([
  { $unwind: "$secciones" },
  { $unwind: "$secciones.parrafos" },
  { $unwind: "$secciones.parrafos.frases" },
  {
    $project: {
      _id: 0,
      frase: "$secciones.parrafos.frases"
    }
  }
])
// Resultado esperado:
// [
//   { frase: "Frase 1 del primer párrafo de la primera sección." },
//   { frase: "Frase 2 del primer párrafo de la primera sección." },
//   { frase: "Frase 1 del segundo párrafo de la primera sección." },
//   { frase: "Frase 2 del segundo párrafo de la primera sección." },
//   { frase: "Frase 1 del primer párrafo de la segunda sección." },
//   { frase: "Frase 2 del primer párrafo de la segunda sección." }
// ]