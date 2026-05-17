import logging
import os
import requests
from backend.api_exceptions import ErrorCommunicatingWithExternalSourceError


class GuaraniClient:
    DEFAULT_VERSION = 'v2'
    LOG = logging.getLogger('GuaraniClient')

    def __init__(self, base_url=None, version=None, auth=None):
        self.base_url = (base_url or os.environ.get('GUARANI_API_URL') or '').rstrip('/')
        self.version = version or self.DEFAULT_VERSION
        if auth is None:
            user = os.environ.get('GUARANI_API_USER')
            password = os.environ.get('GUARANI_API_PASSWORD')
            auth = (user, password) if user and password else None
        self.auth = auth

    # --------------------------------------------------------------
    # alumnos
    # --------------------------------------------------------------
    def get_alumno(self, tipo_documento, numero_documento):
        return self._get(f'/{self.version}/alumnos', params={
            'tipo_documento': tipo_documento,
            'numero_documento': numero_documento,
        })

    def get_alumno_certificado(self, alumno, certificado):
        return self._get(f'/{self.version}/alumnos/{alumno}/certificados/{certificado}')

    # v2 only
    def list_alumnos_cambios_calidades(self, fecha_desde, fecha_hasta, persona=None,
                                       propuesta=None, plan=None, plan_cobrable=None,
                                       nro_transaccion=None, motivo_calidad=None):
        return self._get('/v2/alumnos-cambios-calidades', params=self._clean({
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'persona': persona,
            'propuesta': propuesta,
            'plan': plan,
            'plan_cobrable': plan_cobrable,
            'nro_transaccion': nro_transaccion,
            'motivo_calidad': motivo_calidad,
        }))

    # v2 only
    def list_alumnos_no_regulares(self, fecha_desde, fecha_hasta, persona=None,
                                  propuesta=None, plan=None, plan_cobrable=None,
                                  nro_transaccion=None):
        return self._get('/v2/alumnos-no-regulares', params=self._clean({
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'persona': persona,
            'propuesta': propuesta,
            'plan': plan,
            'plan_cobrable': plan_cobrable,
            'nro_transaccion': nro_transaccion,
        }))

    # v2 only
    def list_alumnos_pasivos(self, fecha_desde, fecha_hasta, persona=None,
                             propuesta=None, plan=None, plan_cobrable=None,
                             nro_transaccion=None, motivo_calidad=None):
        return self._get('/v2/alumnos-pasivos', params=self._clean({
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'persona': persona,
            'propuesta': propuesta,
            'plan': plan,
            'plan_cobrable': plan_cobrable,
            'nro_transaccion': nro_transaccion,
            'motivo_calidad': motivo_calidad,
        }))

    # --------------------------------------------------------------
    # comisiones
    # --------------------------------------------------------------
    def list_comisiones(self, nombre=None, actividad=None, actividad_codigo=None,
                        con_horarios=None, con_docentes=None, order=None,
                        limit=None, page=None):
        return self._get(f'/{self.version}/comisiones', params=self._clean({
            'nombre': nombre,
            'actividad': actividad,
            'actividad_codigo': actividad_codigo,
            'con_horarios': con_horarios,
            'con_docentes': con_docentes,
            'order': order,
            'limit': limit,
            'page': page,
        }))

    def get_comision(self, id_comision):
        return self._get(f'/{self.version}/comisiones/{id_comision}')

    def list_comision_docentes(self, id_comision):
        return self._get(f'/{self.version}/comisiones/{id_comision}/docentes')

    # --------------------------------------------------------------
    # convocatorias
    # --------------------------------------------------------------
    def list_convocatorias(self, titulo=None):
        return self._get(f'/{self.version}/convocatorias',
                         params=self._clean({'titulo': titulo}))

    def update_convocatoria(self, id_convocatoria, body):
        return self._put(f'/{self.version}/convocatorias/{id_convocatoria}', json=body)

    def list_convocatoria_aspirantes(self, id_convocatoria, cuil=None, con_reaperturas=None):
        return self._get(
            f'/{self.version}/convocatorias/{id_convocatoria}/aspirantes',
            params=self._clean({
                'cuil': cuil,
                'con_reaperturas': con_reaperturas,
            }),
        )

    def get_convocatoria_definicion(self, id_convocatoria):
        return self._get(f'/{self.version}/convocatorias/{id_convocatoria}/definicion')

    # --------------------------------------------------------------
    # cursos
    # --------------------------------------------------------------
    def list_cursos(self, plataforma=None, limit=None, page=None, order=None):
        return self._get(f'/{self.version}/cursos', params=self._clean({
            'plataforma': plataforma,
            'limit': limit,
            'page': page,
            'order': order,
        }))

    def create_curso(self, body):
        return self._post(f'/{self.version}/cursos', json=body)

    def get_curso(self, id_curso):
        return self._get(f'/{self.version}/cursos/{id_curso}')

    def update_curso(self, id_curso, body):
        return self._put(f'/{self.version}/cursos/{id_curso}', json=body)

    def delete_curso(self, id_curso):
        return self._delete(f'/{self.version}/cursos/{id_curso}')

    def list_curso_alumnos(self, id_curso):
        return self._get(f'/{self.version}/cursos/{id_curso}/alumnos')

    def link_curso_comision(self, id_curso, id_comision):
        return self._put(f'/{self.version}/cursos/{id_curso}/comisiones/{id_comision}')

    def unlink_curso_comision(self, id_curso, id_comision):
        return self._delete(f'/{self.version}/cursos/{id_curso}/comisiones/{id_comision}')

    # --------------------------------------------------------------
    # docentes
    # --------------------------------------------------------------
    def list_docentes(self, apellido=None, nombres=None, tipo_documento=None,
                      nro_documento=None, order=None, limit=None, page=None):
        return self._get(f'/{self.version}/docentes', params=self._clean({
            'apellido': apellido,
            'nombres': nombres,
            'tipo_documento': tipo_documento,
            'nro_documento': nro_documento,
            'order': order,
            'limit': limit,
            'page': page,
        }))

    def get_docente(self, id_docente):
        return self._get(f'/{self.version}/docentes/{id_docente}')

    def list_docente_comisiones(self, id_docente):
        return self._get(f'/{self.version}/docentes/{id_docente}/comisiones')

    def list_docente_mesas(self, id_docente):
        return self._get(f'/{self.version}/docentes/{id_docente}/mesas')

    # --------------------------------------------------------------
    # info / status
    # --------------------------------------------------------------
    def get_info(self):
        return self._get(f'/{self.version}/info')

    def get_status(self):
        return self._get(f'/{self.version}/status')

    # --------------------------------------------------------------
    # inscripciones (cursada)
    # --------------------------------------------------------------
    def list_inscripciones(self, comision=None, nro_transaccion=None,
                           historicas=None, estado_inscripcion=None):
        return self._get(f'/{self.version}/inscripciones', params=self._clean({
            'comision': comision,
            'nro_transaccion': nro_transaccion,
            'historicas': historicas,
            'estado_inscripcion': estado_inscripcion,
        }))

    def get_inscripcion(self, id_inscripcion):
        return self._get(f'/{self.version}/inscripciones/{id_inscripcion}')

    def list_inscripciones_mesas(self, llamado_mesa=None, nro_transaccion=None, historicas=None):
        return self._get(f'/{self.version}/inscripciones-mesas', params=self._clean({
            'llamado_mesa': llamado_mesa,
            'nro_transaccion': nro_transaccion,
            'historicas': historicas,
        }))

    # --------------------------------------------------------------
    # licencias estudiantiles (v2 only)
    # --------------------------------------------------------------
    def list_licencias_estudiantiles(self, persona=None, plan=None, fecha_desde=None,
                                     fecha_hasta=None, estado=None, plan_cobrable=None,
                                     licencia_financiera=None, permite_rendir_examen=None):
        return self._get('/v2/licencias-estudiantiles', params=self._clean({
            'persona': persona,
            'plan': plan,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'estado': estado,
            'plan_cobrable': plan_cobrable,
            'licencia_financiera': licencia_financiera,
            'permite_rendir_examen': permite_rendir_examen,
        }))

    # --------------------------------------------------------------
    # morosos / notificaciones de pagos
    # --------------------------------------------------------------
    def notify_morosos(self, body):
        return self._post(f'/{self.version}/morosos', json=body)

    def notify_pago(self, body):
        return self._post(f'/{self.version}/notificaciones-pagos', json=body)

    # --------------------------------------------------------------
    # oferta de cursos
    # --------------------------------------------------------------
    def list_oferta_cursos(self, inscripcion_vigente=None):
        return self._get(f'/{self.version}/oferta-cursos', params=self._clean({
            'inscripcion_vigente': inscripcion_vigente,
        }))

    # --------------------------------------------------------------
    # personas
    # --------------------------------------------------------------
    def list_personas(self, usuario=None, pais=None, tipo_documento=None, numero_documento=None):
        return self._get(f'/{self.version}/personas', params=self._clean({
            'usuario': usuario,
            'pais': pais,
            'tipo_documento': tipo_documento,
            'numero_documento': numero_documento,
        }))

    def get_persona_agenda(self, persona, fecha=None, modalidad=None):
        return self._get(f'/{self.version}/personas/{persona}/agenda', params=self._clean({
            'fecha': fecha,
            'modalidad': modalidad,
        }))

    def get_persona_datos_analitico(self, persona, codigo_titulo_araucano=None):
        return self._get(
            f'/{self.version}/personas/{persona}/datosanalitico',
            params=self._clean({'codigo_titulo_araucano': codigo_titulo_araucano}),
        )

    def get_persona_datos_personales(self, persona):
        return self._get(f'/{self.version}/personas/{persona}/datospersonales')

    # --------------------------------------------------------------
    # planes y versiones
    # --------------------------------------------------------------
    def list_planes_versiones(self, propuesta_nombre=None, propuesta_codigo=None,
                              plan_nombre=None, plan_codigo=None, version_nombre=None,
                              version_codigo=None, titulo_araucano=None):
        return self._get(f'/{self.version}/planes-versiones', params=self._clean({
            'propuesta_nombre': propuesta_nombre,
            'propuesta_codigo': propuesta_codigo,
            'plan_nombre': plan_nombre,
            'plan_codigo': plan_codigo,
            'version_nombre': version_nombre,
            'version_codigo': version_codigo,
            'titulo_araucano': titulo_araucano,
        }))

    def list_plan_version_actividades(self, id_plan_version):
        return self._get(f'/{self.version}/planes-versiones/{id_plan_version}/actividades')

    # --------------------------------------------------------------
    # preinscriptos
    # --------------------------------------------------------------
    def list_preinscriptos(self, usuario=None, pais=None, tipo_documento=None, numero_documento=None):
        return self._get(f'/{self.version}/preinscriptos', params=self._clean({
            'usuario': usuario,
            'pais': pais,
            'tipo_documento': tipo_documento,
            'numero_documento': numero_documento,
        }))

    def get_preinscripto_agenda(self, id_preinscripcion, fecha=None):
        return self._get(
            f'/{self.version}/preinscriptos/{id_preinscripcion}/agenda',
            params=self._clean({'fecha': fecha}),
        )

    # --------------------------------------------------------------
    # propuestas formativas
    # --------------------------------------------------------------
    def list_propuestas_formativas(self, propuesta_codigo=None, propuesta_nombre=None,
                                   ra_codigo=None, ra_nombre=None, order=None):
        return self._get(f'/{self.version}/propuestas-formativas', params=self._clean({
            'propuesta_codigo': propuesta_codigo,
            'propuesta_nombre': propuesta_nombre,
            'ra_codigo': ra_codigo,
            'ra_nombre': ra_nombre,
            'order': order,
        }))

    def get_propuesta_formativa(self, id_propuesta):
        return self._get(f'/{self.version}/propuestas-formativas/{id_propuesta}')

    # --------------------------------------------------------------
    # reaperturas a convocatorias (v2 only)
    # --------------------------------------------------------------
    def register_reapertura_convocatoria(self, body):
        return self._post('/v2/reaperturas-convocatorias', json=body)

    # ==============================================================
    # Internals
    # ==============================================================
    @staticmethod
    def _clean(params):
        return {k: v for k, v in params.items() if v is not None}

    def _get(self, path, params=None, headers=None):
        return self._request('GET', path, params=params, headers=headers)

    def _post(self, path, json=None, headers=None):
        return self._request('POST', path, json=json, headers=headers)

    def _put(self, path, json=None, headers=None):
        return self._request('PUT', path, json=json, headers=headers)

    def _delete(self, path, headers=None):
        return self._request('DELETE', path, headers=headers)

    def _request(self, method, path, params=None, json=None, headers=None):
        if not self.base_url:
            raise ErrorCommunicatingWithExternalSourceError(
                detail="GUARANI_API_URL is not configured."
            )
        url = f"{self.base_url}{path}"
        self.LOG.debug("Guarani %s %s params=%s json=%s", method, url, params, json)
        try:
            r = requests.request(
                method, url,
                params=params, json=json, headers=headers, auth=self.auth, verify=False,
                timeout=(5, 30),
            )
        except requests.exceptions.RequestException as e:
            self.LOG.error("Guarani request failed: %s", e)
            raise ErrorCommunicatingWithExternalSourceError(
                detail="Unexpected error when communicating with Guarani"
            )
        self.LOG.debug("Guarani response %s %s", r.status_code, r.text[:500])
        if not r.ok:
            self.LOG.error("Guarani error %s %s", r.status_code, r.text)
            raise ErrorCommunicatingWithExternalSourceError(
                detail=f"Guarani returned {r.status_code}"
            )
        if r.status_code == 204 or not r.content:
            return None
        try:
            return r.json()
        except ValueError:
            return r.text
