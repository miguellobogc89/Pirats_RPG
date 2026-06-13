from dataclasses import dataclass

from game.cartography.cartography_states import EXPLORED, HIDDEN, SEEN, SETTLED
from game.cartography.cartography_manager import STARTING_REGION_ID
from game.cartography.data.port_database import PORT_DATABASE
from game.cartography.data.region_database import REGION_DATABASE
from game.cartography.data.world_map import WORLD_MAP


ERROR = "error"
WARNING = "warning"
VALID_REGION_STATES = {HIDDEN, SEEN, EXPLORED, SETTLED}


@dataclass(frozen=True)
class CartographyValidationIssue:
    severity: str
    code: str
    message: str


def validate_cartography_data(
    region_database=None,
    port_database=None,
    world_map=None,
    starting_region_id=STARTING_REGION_ID,
):
    regions = region_database if region_database is not None else REGION_DATABASE
    ports = port_database if port_database is not None else PORT_DATABASE
    map_data = world_map if world_map is not None else WORLD_MAP

    issues = []

    issues.extend(validate_regions(regions, map_data))
    issues.extend(validate_connections(regions))
    issues.extend(validate_world_map(regions, map_data))
    issues.extend(validate_ports(regions, ports, starting_region_id))
    issues.extend(validate_resource_tables(regions))

    return issues


def validate_regions(regions, world_map):
    issues = []
    seen_region_ids = set()
    seen_declared_ids = set()
    map_height = len(world_map)
    map_width = max((len(row) for row in world_map), default=0)

    for region_id, region_data in regions.items():
        if region_id in seen_region_ids:
            issues.append(error(
                "duplicate_region_key",
                f"Region key duplicated: {region_id}",
            ))

        seen_region_ids.add(region_id)
        declared_id = region_data.get("id")

        if declared_id is None:
            issues.append(error(
                "missing_region_id",
                f"Region {region_id} has no internal id.",
            ))
        elif declared_id != region_id:
            issues.append(error(
                "region_id_mismatch",
                f"Region {region_id} declares id {declared_id}.",
            ))

        if declared_id in seen_declared_ids:
            issues.append(error(
                "duplicate_region_id",
                f"Region id duplicated in region data: {declared_id}",
            ))

        seen_declared_ids.add(declared_id)

        row = region_data.get("row")
        col = region_data.get("col")

        if row is None or col is None:
            issues.append(error(
                "missing_region_position",
                f"Region {region_id} has no row/col position.",
            ))
            continue

        if not isinstance(row, int) or not isinstance(col, int):
            issues.append(error(
                "invalid_region_position_type",
                f"Region {region_id} position must be integer row/col.",
            ))
            continue

        if row < 0 or col < 0 or row >= map_height or col >= map_width:
            issues.append(error(
                "region_position_out_of_map",
                f"Region {region_id} position ({row}, {col}) is outside WORLD_MAP.",
            ))

        issues.extend(validate_region_progress_fields(region_id, region_data))

    return issues


def validate_region_progress_fields(region_id, region_data):
    issues = []
    state = region_data.get("state")
    hidden = region_data.get("hidden")
    cartography_percent = region_data.get("cartography_percent")
    visits = region_data.get("visits")

    if state not in VALID_REGION_STATES:
        issues.append(error(
            "invalid_region_state",
            f"Region {region_id} has invalid state {state}.",
        ))

    if hidden is not None and not isinstance(hidden, bool):
        issues.append(error(
            "invalid_hidden_flag",
            f"Region {region_id} hidden flag must be boolean.",
        ))

    if hidden is True and state != HIDDEN:
        issues.append(warning(
            "hidden_state_mismatch",
            f"Region {region_id} is hidden but state is {state}.",
        ))

    if hidden is False and state == HIDDEN:
        issues.append(warning(
            "visible_state_mismatch",
            f"Region {region_id} is visible but state is hidden.",
        ))

    if not isinstance(cartography_percent, int) or not 0 <= cartography_percent <= 100:
        issues.append(error(
            "invalid_cartography_percent",
            f"Region {region_id} cartography_percent must be between 0 and 100.",
        ))

    if not isinstance(visits, int) or visits < 0:
        issues.append(error(
            "invalid_visit_count",
            f"Region {region_id} visits must be a non-negative integer.",
        ))

    for numeric_field in ("danger", "travel_days", "base_days"):
        value = region_data.get(numeric_field)

        if not isinstance(value, int) or value < 0:
            issues.append(error(
                "invalid_region_numeric_field",
                f"Region {region_id} {numeric_field} must be a non-negative integer.",
            ))

    return issues


def validate_connections(regions):
    issues = []

    for region_id, region_data in regions.items():
        connections = region_data.get("connections", [])

        if not isinstance(connections, list):
            issues.append(error(
                "invalid_connections_type",
                f"Region {region_id} connections must be a list.",
            ))
            continue

        for connected_region_id in connections:
            if connected_region_id not in regions:
                issues.append(error(
                    "unknown_connected_region",
                    f"Region {region_id} connects to missing region {connected_region_id}.",
                ))
                continue

            reverse_connections = regions[connected_region_id].get("connections", [])
            if region_id not in reverse_connections:
                issues.append(warning(
                    "one_way_connection",
                    f"Region {region_id} connects to {connected_region_id}, but not back.",
                ))

    return issues


def validate_world_map(regions, world_map):
    issues = []
    mapped_regions = {}

    for row_index, row in enumerate(world_map):
        for col_index, region_id in enumerate(row):
            if region_id is None:
                continue

            if region_id not in regions:
                issues.append(error(
                    "world_map_unknown_region",
                    f"WORLD_MAP cell ({row_index}, {col_index}) references missing region {region_id}.",
                ))
                continue

            if region_id in mapped_regions:
                issues.append(error(
                    "world_map_duplicate_region",
                    f"WORLD_MAP references region {region_id} more than once.",
                ))

            mapped_regions[region_id] = (row_index, col_index)
            expected_row = regions[region_id].get("row")
            expected_col = regions[region_id].get("col")

            if expected_row != row_index or expected_col != col_index:
                issues.append(warning(
                    "world_map_position_mismatch",
                    (
                        f"Region {region_id} declares position "
                        f"({expected_row}, {expected_col}) but WORLD_MAP places it "
                        f"at ({row_index}, {col_index})."
                    ),
                ))

    for region_id in regions:
        if region_id not in mapped_regions:
            issues.append(warning(
                "region_not_on_world_map",
                f"Region {region_id} is defined but not placed in WORLD_MAP.",
            ))

    return issues


def validate_ports(regions, ports, starting_region_id):
    issues = []
    starting_ports = []

    if starting_region_id not in regions:
        issues.append(error(
            "invalid_starting_region",
            f"Starting region {starting_region_id} does not exist.",
        ))

    for port_id, port_data in ports.items():
        declared_id = port_data.get("id")
        region_id = port_data.get("region_id")

        if declared_id != port_id:
            issues.append(error(
                "port_id_mismatch",
                f"Port {port_id} declares id {declared_id}.",
            ))

        if region_id not in regions:
            issues.append(error(
                "port_unknown_region",
                f"Port {port_id} points to missing region {region_id}.",
            ))
            continue

        if port_data.get("is_starting_port"):
            starting_ports.append(port_id)

        if not regions[region_id].get("has_port", False):
            issues.append(warning(
                "port_region_not_marked_as_port",
                f"Port {port_id} points to region {region_id}, but region has_port is false.",
            ))

    if not starting_ports:
        issues.append(error(
            "missing_starting_port",
            "No starting port is marked in PORT_DATABASE.",
        ))

    for port_id in starting_ports:
        if ports[port_id].get("region_id") != starting_region_id:
            issues.append(error(
                "starting_port_region_mismatch",
                (
                    f"Starting port {port_id} points to "
                    f"{ports[port_id].get('region_id')} instead of {starting_region_id}."
                ),
            ))

    return issues


def validate_resource_tables(regions):
    issues = []

    for region_id, region_data in regions.items():
        resources = set(region_data.get("resources", []))
        resource_table = region_data.get("resource_table", {})

        if not isinstance(resource_table, dict):
            issues.append(error(
                "invalid_resource_table_type",
                f"Region {region_id} resource_table must be a dict.",
            ))
            continue

        for resource_id, amount_range in resource_table.items():
            if resource_id not in resources:
                issues.append(warning(
                    "resource_table_resource_not_listed",
                    f"Region {region_id} resource_table contains {resource_id}, but resources does not list it.",
                ))

            if not is_valid_amount_range(amount_range):
                issues.append(error(
                    "invalid_resource_amount_range",
                    f"Region {region_id} resource {resource_id} has invalid amount range {amount_range}.",
                ))

        for resource_id in resources:
            if resource_id not in resource_table:
                issues.append(warning(
                    "listed_resource_missing_table_entry",
                    f"Region {region_id} lists resource {resource_id}, but resource_table has no entry.",
                ))

    return issues


def is_valid_amount_range(amount_range):
    if not isinstance(amount_range, (list, tuple)):
        return False

    if len(amount_range) != 2:
        return False

    min_amount, max_amount = amount_range

    if not isinstance(min_amount, int) or not isinstance(max_amount, int):
        return False

    if min_amount < 0 or max_amount < 0:
        return False

    return min_amount <= max_amount


def error(code, message):
    return CartographyValidationIssue(ERROR, code, message)


def warning(code, message):
    return CartographyValidationIssue(WARNING, code, message)


def format_validation_issue(issue):
    return f"[{issue.severity}] {issue.code}: {issue.message}"


if __name__ == "__main__":
    for validation_issue in validate_cartography_data():
        print(format_validation_issue(validation_issue))
