const jsonServer = require('json-server')

const server = jsonServer.create()
const router = jsonServer.router('db.json')
const middlewares = jsonServer.defaults()

server.use(middlewares)
server.use(jsonServer.rewriter({
  "/v2/comisiones/:id": "/comisiones/:id",
  "/v2/comisiones": "/comisiones",
  "/v2/materias/:id": "/materias/:id",
  "/v2/materias": "/materias",
  "/v2/alumnos/:id": "/alumnos/:id",
  "/v2/alumnos": "/alumnos",
  "/v2/docentes/:id": "/docentes/:id",
  "/v2/docentes": "/docentes",
  "/v2/finales/:id": "/finales/:id",
  "/v2/finales": "/finales",
  "/v2/info": "/noop",
  "/v2/status": "/noop",
  "/docentes/:docente_id/finales/:final_id/subir_acta": "/docentes/:docente_id/actas",
  "/docentes/:docente_id/finales/:final_id/cargar_notas": "/noop",
}))
server.use(jsonServer.bodyParser)
server.use('/noop', (req, res, next) => {
  res.status(200).jsonp({})
})

// Use default router
server.use(router)
server.listen(process.env.PORT || 3000, () => {
  console.log('JSON Server is running')
})