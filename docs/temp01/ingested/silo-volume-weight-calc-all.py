"""Ignition Gateway timer script for multi-silo volume/weight calculations."""


from contextlib import suppress

import system  # type: ignore[import]
from java.util import Date  # type: ignore[import]
from silo_config import DEFAULT_ACTIVE_SILOS, get_silo_definition
from silo_math import SiloCalculator, sanitize_inputs

Geometry = dict[str, float]
DynamicInputs = tuple[float, float, float, float, list[str]]

LOGGER = system.util.getLogger('SiloCalculator')


def _read_geometry_from_udt(base_tag_path: str, fallback_geometry: Geometry) -> Geometry:
    """Read geometry overrides from the UDT if good quality tags exist."""
    try:
        tag_paths = [
            base_tag_path + '/H_TOT',
            base_tag_path + '/H_CONE',
            base_tag_path + '/R_B',
            base_tag_path + '/R_T',
            base_tag_path + '/D_CYL',
        ]
        tag_values = system.tag.readAll(tag_paths)
        if all(tv.quality.isGood() for tv in tag_values):
            return {
                'H_TOT': float(tag_values[0].value),
                'H_CONE': float(tag_values[1].value),
                'R_B': float(tag_values[2].value),
                'R_T': float(tag_values[3].value),
                'D_CYL': float(tag_values[4].value),
            }
    except Exception:
        pass
    return fallback_geometry


def _read_dynamic_inputs(base_tag_path: str, defaults: dict[str, float]) -> DynamicInputs:
    paths = [
        f'{base_tag_path}/P_percent',
        f'{base_tag_path}/dead_vol_ft',
        f'{base_tag_path}/safety_factor_ft',
        f'{base_tag_path}/density/latest',
    ]
    values = system.tag.readAll(paths)

    level_value = values[0]
    if not level_value.quality.isGood():
        raise ValueError(f'Bad quality for tag: {paths[0]}')

    p_percent = float(values[0].value)

    dead_vol = defaults['dead_vol_ft']
    warnings: list[str] = []
    if values[1].quality.isGood():
        dead_vol = float(values[1].value)
    else:
        warnings.append('dead_vol_ft using default due to bad tag quality')

    safety_factor = defaults['safety_factor_ft']
    if values[2].quality.isGood():
        safety_factor = float(values[2].value)
    else:
        warnings.append('safety_factor_ft using default due to bad tag quality')

    density = defaults.get('default_density_lb_per_bushel', 59.0)
    if values[3].quality.isGood():
        density = float(values[3].value)
    else:
        warnings.append('density using default due to bad tag quality')

    return p_percent, dead_vol, safety_factor, density, warnings


def process_silo(silo_num: int, definition: dict[str, dict[str, float]]) -> dict[str, object]:
    base_tag_path = f'[default]Silo{silo_num}'
    result = {
        'silo_num': silo_num,
        'success': False,
        'volume_ft3': 0.0,
        'weight_lb': 0.0,
        'warnings': [],
        'error': None,
    }

    try:
        silo_tag = system.tag.read(f'{base_tag_path}/Silo')
        if not silo_tag.quality.isGood():
            raise ValueError(f'Missing or bad-quality UDT for {base_tag_path}')

        geometry = _read_geometry_from_udt(base_tag_path, definition['geometry'])
        calculator = SiloCalculator(
            silo_num,
            geometry,
            definition['defaults']['additional_cone_volume_ft3'],
        )

        (
            p_percent,
            dead_vol_ft,
            safety_factor_ft,
            density,
            quality_warnings,
        ) = _read_dynamic_inputs(
            base_tag_path, definition['defaults']
        )

        sanitized, sanitize_warnings = sanitize_inputs(
            calculator,
            definition['defaults'],
            p_percent,
            dead_vol_ft,
            safety_factor_ft,
            density,
        )

        warnings = quality_warnings[:]
        warnings.extend(sanitize_warnings)

        volume, weight = calculator.calculate(
            sanitized['p_percent'],
            sanitized['dead_vol_ft'],
            sanitized['safety_factor_ft'],
            sanitized['density'],
        )

        # Read previous values before overwriting
        prev_tags = [
            f'{base_tag_path}/silo{silo_num}_volume_current',
            f'{base_tag_path}/silo{silo_num}_weight_current',
        ]
        prev_values = system.tag.readAll(prev_tags)
        prev_volume = float(prev_values[0].value) if prev_values[0].quality.isGood() else 0.0
        prev_weight = float(prev_values[1].value) if prev_values[1].quality.isGood() else 0.0

        status_message = 'OK - Calculated successfully'
        if warnings:
            status_message += f" ({'; '.join(warnings)})"

        system.tag.writeAll(
            [
                f'{base_tag_path}/silo{silo_num}_volume_current',
                f'{base_tag_path}/silo{silo_num}_weight_current',
                f'{base_tag_path}/silo{silo_num}_volume_previous',
                f'{base_tag_path}/silo{silo_num}_weight_previous',
                f'{base_tag_path}/LastCalcTime',
                f'{base_tag_path}/CalcStatus',
            ],
            [
                volume,
                weight,
                prev_volume,
                prev_weight,
                Date(),
                status_message,
            ],
        )

        result.update({
            'success': True,
            'volume_ft3': volume,
            'weight_lb': weight,
            'warnings': warnings,
        })
        return result

    except Exception as exc:
        result['error'] = f'ERROR - Silo {silo_num}: {exc}'
        with suppress(Exception):
            system.tag.writeAll(
                [f'{base_tag_path}/CalcStatus', f'{base_tag_path}/LastCalcTime'],
                [result['error'], Date()],
            )
        return result


def main() -> list[dict[str, object]]:
    results = []
    processed_count = 0
    error_count = 0

    for silo_num in DEFAULT_ACTIVE_SILOS:
        definition = get_silo_definition(silo_num)
        result = process_silo(silo_num, definition)
        results.append(result)
        if result['success']:
            processed_count += 1
        else:
            error_count += 1

    if processed_count or error_count:
        LOGGER.info(
            'Silo Calculator: processed %d silos successfully, %d errors',
            processed_count,
            error_count,
        )
    for result in results:
        if not result['success'] and result['error']:
            LOGGER.error(result['error'])
        elif result['warnings']:
            warning_values = result.get('warnings', [])
            if isinstance(warning_values, (list, tuple)):
                warning_text = '; '.join(str(warning) for warning in warning_values)
            else:
                warning_text = str(warning_values)
            LOGGER.warning(
                'Silo %s completed with warnings: %s',
                result['silo_num'],
                warning_text,
            )

    return results


if __name__ == '__main__':
    main()
