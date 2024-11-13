class RuleValidator:
    """Validar las reglas de manera exhaustiva"""

    @staticmethod
    def validate_rule_structure(rule_data):
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Verificar estructura básica
        required_fields = ["type", "category", "rules_managers"]
        for field in required_fields:
            if field not in rule_data:
                validation_results["is_valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")

        if "type" in rule_data and rule_data["type"] != "rule":
            validation_results["errors"].append("Invalid rule type - must be 'rule'")
            validation_results["is_valid"] = False

        # Validar reglas específicas
        if "rules_managers" in rule_data:
            rules = rule_data["rules_managers"]
            for rule_type, rule_content in rules.items():
                if not RuleValidator.validate_specific_rule(rule_type, rule_content, validation_results):
                    validation_results["is_valid"] = False

        # Verificar coherencia entre reglas
        RuleValidator.check_rules_coherence(rule_data, validation_results)

        return validation_results

    @staticmethod
    def validate_specific_rule(rule_type, content, results):
        """Validar una regla específica según su tipo"""
        validators = {
            "connectivity": RuleValidator._validate_connectivity_rule,
            "neighbors": RuleValidator._validate_neighbors_rule,
            "percentage": RuleValidator._validate_percentage_rule,
            "pattern": RuleValidator._validate_pattern_rule,
            "symmetry": RuleValidator._validate_symmetry_rule,
            "frequency": RuleValidator._validate_frequency_rule,
            "grouping": RuleValidator._validate_grouping_rule,
            "spacing": RuleValidator._validate_spacing_rule,
            "border": RuleValidator._validate_border_rule
        }

        if rule_type not in validators:
            results["errors"].append(f"Unknown rule type: {rule_type}")
            return False

        return validators[rule_type](content, results)

    @staticmethod
    def _validate_connectivity_rule(content, results):
        """Validar regla de conectividad"""
        if "mustBeConnected" not in content:
            results["errors"].append("Connectivity rule must specify 'mustBeConnected'")
            return False

        if not isinstance(content["mustBeConnected"], bool):
            results["errors"].append("'mustBeConnected' must be a boolean value")
            return False

        if "connectionType" in content:
            valid_types = ["orthogonal", "diagonal", "both"]
            if content["connectionType"] not in valid_types:
                results["errors"].append(
                    f"Invalid connection type. Must be one of: {', '.join(valid_types)}")
                return False

        return True

    @staticmethod
    def _validate_neighbors_rule(content, results):
        """Validar regla de vecinos"""
        if "allowedNeighbors" not in content and "forbiddenNeighbors" not in content:
            results["errors"].append("Neighbors rule must specify either 'allowedNeighbors' or 'forbiddenNeighbors'")
            return False

        if "allowedNeighbors" in content and not isinstance(content["allowedNeighbors"], list):
            results["errors"].append("'allowedNeighbors' must be a list")
            return False

        if "forbiddenNeighbors" in content and not isinstance(content["forbiddenNeighbors"], list):
            results["errors"].append("'forbiddenNeighbors' must be a list")
            return False

        if "positions" in content:
            valid_positions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
            for pos in content["positions"]:
                if pos not in valid_positions:
                    results["errors"].append(f"Invalid position: {pos}")
                    return False

        return True

    @staticmethod
    def _validate_percentage_rule(content, results):
        """Validar regla de porcentaje"""
        if "min" not in content and "max" not in content and "target" not in content:
            results["errors"].append("Percentage rule must specify at least one of: 'min', 'max', 'target'")
            return False

        for field in ["min", "max", "target"]:
            if field in content:
                if not isinstance(content[field], (int, float)):
                    results["errors"].append(f"'{field}' must be a number")
                    return False
                if content[field] < 0 or content[field] > 100:
                    results["errors"].append(f"'{field}' must be between 0 and 100")
                    return False

        if "min" in content and "max" in content:
            if content["min"] > content["max"]:
                results["errors"].append("'min' cannot be greater than 'max'")
                return False

        return True

    @staticmethod
    def _validate_pattern_rule(content, results):
        """Validar regla de patrón"""
        if "requiredPatterns" not in content and "forbiddenPatterns" not in content:
            results["errors"].append("Pattern rule must specify either 'requiredPatterns' or 'forbiddenPatterns'")
            return False

        if "patternSize" in content:
            if not isinstance(content["patternSize"], dict):
                results["errors"].append("'patternSize' must be an object")
                return False
            if "width" not in content["patternSize"] or "height" not in content["patternSize"]:
                results["errors"].append("'patternSize' must specify 'width' and 'height'")
                return False

        for pattern_type in ["requiredPatterns", "forbiddenPatterns"]:
            if pattern_type in content:
                if not isinstance(content[pattern_type], list):
                    results["errors"].append(f"'{pattern_type}' must be a list")
                    return False

        return True

    @staticmethod
    def _validate_symmetry_rule(content, results):
        """Validar regla de simetría"""
        if "type" not in content:
            results["errors"].append("Symmetry rule must specify 'type'")
            return False

        valid_types = ["horizontal", "vertical", "both", "rotational"]
        if content["type"] not in valid_types:
            results["errors"].append(f"Invalid symmetry type. Must be one of: {', '.join(valid_types)}")
            return False

        if "strictness" in content:
            if not isinstance(content["strictness"], (int, float)):
                results["errors"].append("'strictness' must be a number")
                return False
            if content["strictness"] < 0 or content["strictness"] > 1:
                results["errors"].append("'strictness' must be between 0 and 1")
                return False

        return True

    @staticmethod
    def _validate_frequency_rule(content, results):
        """Validar regla de frecuencia"""
        if "minOccurrences" not in content and "maxOccurrences" not in content:
            results["errors"].append("Frequency rule must specify at least one of: 'minOccurrences', 'maxOccurrences'")
            return False

        for field in ["minOccurrences", "maxOccurrences"]:
            if field in content:
                if not isinstance(content[field], (int, type(None))):
                    results["errors"].append(f"'{field}' must be an integer or null")
                    return False
                if content[field] is not None and content[field] < 0:
                    results["errors"].append(f"'{field}' must be non-negative")
                    return False

        if "spacing" in content:
            if not isinstance(content["spacing"], dict):
                results["errors"].append("'spacing' must be an object")
                return False
            if "min" not in content["spacing"]:
                results["errors"].append("'spacing' must specify 'min'")
                return False

        return True

    @staticmethod
    def _validate_grouping_rule(content, results):
        """Validar regla de agrupamiento"""
        if "minGroupSize" not in content:
            results["errors"].append("Grouping rule must specify 'minGroupSize'")
            return False

        if not isinstance(content["minGroupSize"], int) or content["minGroupSize"] < 1:
            results["errors"].append("'minGroupSize' must be a positive integer")
            return False

        if "maxGroupSize" in content:
            if content["maxGroupSize"] is not None:
                if not isinstance(content["maxGroupSize"], int):
                    results["errors"].append("'maxGroupSize' must be an integer or null")
                    return False
                if content["maxGroupSize"] < content["minGroupSize"]:
                    results["errors"].append("'maxGroupSize' cannot be less than 'minGroupSize'")
                    return False

        if "groupShape" in content:
            valid_shapes = ["any", "rectangular", "circular", "linear"]
            if content["groupShape"] not in valid_shapes:
                results["errors"].append(f"Invalid group shape. Must be one of: {', '.join(valid_shapes)}")
                return False

        return True

    @staticmethod
    def _validate_spacing_rule(content, results):
        """Validar regla de espaciado"""
        if "minSpacing" not in content:
            results["errors"].append("Spacing rule must specify 'minSpacing'")
            return False

        if not isinstance(content["minSpacing"], int) or content["minSpacing"] < 0:
            results["errors"].append("'minSpacing' must be a non-negative integer")
            return False

        if "maxSpacing" in content:
            if content["maxSpacing"] is not None:
                if not isinstance(content["maxSpacing"], int):
                    results["errors"].append("'maxSpacing' must be an integer or null")
                    return False
                if content["maxSpacing"] < content["minSpacing"]:
                    results["errors"].append("'maxSpacing' cannot be less than 'minSpacing'")
                    return False

        if "relativeTo" in content:
            if not isinstance(content["relativeTo"], list):
                results["errors"].append("'relativeTo' must be a list")
                return False

        return True

    @staticmethod
    def _validate_border_rule(content, results):
        """Validar regla de borde"""
        if "mustBeBorder" not in content:
            results["errors"].append("Border rule must specify 'mustBeBorder'")
            return False

        if not isinstance(content["mustBeBorder"], bool):
            results["errors"].append("'mustBeBorder' must be a boolean")
            return False

        if "borderSides" in content:
            valid_sides = ["top", "bottom", "left", "right"]
            if not isinstance(content["borderSides"], list):
                results["errors"].append("'borderSides' must be a list")
                return False
            for side in content["borderSides"]:
                if side not in valid_sides:
                    results["errors"].append(f"Invalid border side: {side}")
                    return False

        if "borderWidth" in content:
            if not isinstance(content["borderWidth"], int) or content["borderWidth"] < 1:
                results["errors"].append("'borderWidth' must be a positive integer")
                return False

        return True

    @staticmethod
    def check_rules_coherence(rule_data, results):
        """Verificar la coherencia entre diferentes reglas"""
        rules = rule_data.get("rules_managers", {})

        # Verificar coherencia entre conectividad y vecinos
        if "connectivity" in rules and "neighbors" in rules:
            if (rules["connectivity"].get("mustBeConnected") and
                not rules["neighbors"].get("allowedNeighbors")):
                results["warnings"].append(
                    "Connected tiles should have allowed neighbors specified")

        # Verificar coherencia entre porcentaje y frecuencia
        if "percentage" in rules and "frequency" in rules:
            if ("target" in rules["percentage"] and
                "maxOccurrences" in rules["frequency"]):
                results["warnings"].append(
                    "Percentage and frequency rules_managers might conflict")

        # Verificar coherencia entre agrupamiento y espaciado
        if "grouping" in rules and "spacing" in rules:
            if (rules["grouping"].get("minGroupSize", 1) > 1 and
                rules["spacing"].get("minSpacing", 0) > 0):
                results["warnings"].append(
                    "Grouping and spacing rules_managers might conflict")

        # Verificar coherencia con reglas de borde
        if "border" in rules and rules["border"].get("mustBeBorder"):
            if "pattern" in rules:
                results["warnings"].append(
                    "Border and pattern rules_managers might need special consideration")

        # Verificar coherencia con simetría
        if "symmetry" in rules:
            affected_rules = ["pattern", "grouping", "spacing"]
            for rule in affected_rules:
                if rule in rules:
                    results["warnings"].append(
                        f"Symmetry rule might affect {rule} rule behavior")