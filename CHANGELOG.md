# Changelog

La versión del paquete se deriva del tag de git (`vX.Y.Z`) mediante setuptools-scm.

## 1.0.0 — 2026-10-13

Correcciones de la auditoría de código del 2026-10-09 ([informe](docs/informe_2026-10-09_1420/README.md)) y verificación contra API MPMS 11.1 (2004).

### ⚠️ Cambios incompatibles

| Antes (0.1.0) | Ahora (1.0.0) |
|---|---|
| `correct_base_to_alternate(rho_60, t_f, p_psig, commodity_group=...)` | Todos los parámetros por nombre; `commodity_type=` |
| Resultados como tuplas de 5 o 6 valores | `NamedTuple` con `ctpl_rounded` (y `iterations` en 6.2) |
| `correct_observed_to_alternate_C(rho_t, t_a_c, p_a, t_b, ...)` (11.1.7.1) | `correct_metric_base_to_alternate(rho_base, t_base_c, t_c, p, pressure_unit, ...)` |
| `correct_observed_to_base_C(rho_o, t_o_c, p_o, t_b, ...)` (11.1.7.2) | `correct_metric_observed_to_base(rho_o, t_o_c, p_o, pressure_unit, t_base_c, ...)` |
| Presión de 7.x tomada como psig | Presión en kPa o bar (`pressure_unit` obligatorio); Fp en kPa⁻¹/bar⁻¹ |
| `t_b` con cualquier valor (20 por defecto) | `t_base_c` obligatorio, solo 15 o 20 °C |
| `table_5x_6x`, `table_23x_24x`, `table_53x_54x`, `table_59x_60x` | `ctl_from_observed_api`, `ctl_from_observed_relative_density`, `ctl_from_observed_density_15c`, `ctl_from_observed_density_20c` (sin redondeo intermedio; los resultados pueden variar en el 5.º decimal) |
| `table_54c(alpa_obs=...)`, `table_60c(alpa_obs=...)` | `alpha_obs=` |
| `API_to_rho`, `rho_to_API`, `celc_to_fahr`, `alphac_to_alphaf` | `api_to_rho`, `rho_to_api`, `celsius_to_fahrenheit`, `alpha_c_to_alpha_f` |
| `its90_to_ipts68(..., out_fahrenheit=True)` | Devuelve la temperatura en la unidad de entrada |
| Paquete `api_mpms.Tables` y `api_mpms.tests` | Eliminados: el generador está en `scripts/` y las pruebas en `tests/` |
| `constants.iteration_coefficients.da_coefficient` | `CommodityGroup.Da` |
| Densidades fuera de rango extrapoladas al grupo más cercano | `MPMSRangeError` |
| alpha_60 junto con tipo A/B/D | `MPMSValidationError` |

### Corregido

- `api_round` resolvía mal los empates en valores grandes y con incrementos no decimales.
- La tabla 23A del generador usaba la temperatura como densidad relativa.
- `rho_60 = 0` producía `ZeroDivisionError`; la presión se ignoraba en silencio con densidad nula.
- Presión `NaN` aceptada; `alpha_60_c = 0` tratado como ausente; `commodity_type=None` producía `AttributeError`.
- Las entradas fuera de rango se reportaban como error de convergencia.
- Tablas C: alpha sin redondear y sin validar.

### Añadido

- 11.1.6.3 `correct_observed_to_alternate`; `ctl_from_alpha`; tablas `table_5x`, `table_23x`, `table_53x`, `table_59x`.
- Generador de las 28 tablas de 11.1.8 con ejecución en paralelo.
- 493 pruebas (cobertura 99 %), entre ellas 105 ejemplos resueltos y 253 valores de tablas de la norma.
- Módulos públicos `api_mpms.conversions` y `api_mpms.tables` (también accesibles como atributos de `api_mpms`).
- Documentación para integradores en [`docs/api`](docs/api/README.md); sus ejemplos se ejecutan como pruebas (doctest).
- Mensajes de error en ASCII con unidades explícitas; las funciones métricas validan temperatura y presión en las unidades de entrada.
