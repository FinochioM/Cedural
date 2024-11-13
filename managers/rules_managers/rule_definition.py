from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


class RuleType(Enum):
    """Catálogo de todos los tipos de reglas posibles"""
    CONNECTIVITY = "connectivity"
    NEIGHBORS = "neighbors"
    PERCENTAGE = "percentage"
    PATTERN = "pattern"  # Para patrones específicos de tiles
    SYMMETRY = "symmetry"  # Para reglas de simetría
    FREQUENCY = "frequency"  # Para controlar frecuencia de aparición
    GROUPING = "grouping"  # Para reglas de agrupamiento
    SPACING = "spacing"  # Para reglas de espaciado entre tiles
    BORDER = "border"  # Para reglas específicas de bordes
    # Fácil de expandir añadiendo más tipos


@dataclass
class RuleDefinition:
    """Definición de una regla y su estructura"""
    type: RuleType
    template: Dict[str, Any]
    description: str


class RulesCatalog:
    """Catálogo central de reglas disponibles"""

    @staticmethod
    def get_all_rules() -> Dict[RuleType, RuleDefinition]:
        return {
            RuleType.CONNECTIVITY: RuleDefinition(
                type=RuleType.CONNECTIVITY,
                template={
                    "mustBeConnected": True,
                    "connectionType": "orthogonal"  # or "diagonal" or "both"
                },
                description="Define how tiles should be connected"
            ),
            RuleType.NEIGHBORS: RuleDefinition(
                type=RuleType.NEIGHBORS,
                template={
                    "allowedNeighbors": [],
                    "forbiddenNeighbors": [],
                    "positions": ["north", "south", "east", "west"]
                },
                description="Define which categories can be adjacent"
            ),
            RuleType.PERCENTAGE: RuleDefinition(
                type=RuleType.PERCENTAGE,
                template={
                    "min": 0,
                    "max": 100,
                    "target": 50,
                    "priority": 1
                },
                description="Define percentage constraints for the category"
            ),
            RuleType.PATTERN: RuleDefinition(
                type=RuleType.PATTERN,
                template={
                    "requiredPatterns": [],
                    "forbiddenPatterns": [],
                    "patternSize": {"width": 2, "height": 2}
                },
                description="Define specific tile patterns"
            ),
            RuleType.SYMMETRY: RuleDefinition(
                type=RuleType.SYMMETRY,
                template={
                    "type": "horizontal",  # or "vertical" or "both"
                    "strictness": 1.0
                },
                description="Define symmetry requirements"
            ),
            RuleType.FREQUENCY: RuleDefinition(
                type=RuleType.FREQUENCY,
                template={
                    "minOccurrences": 0,
                    "maxOccurrences": None,
                    "spacing": {"min": 1, "max": None}
                },
                description="Define how often tiles should appear"
            ),
            RuleType.GROUPING: RuleDefinition(
                type=RuleType.GROUPING,
                template={
                    "minGroupSize": 1,
                    "maxGroupSize": None,
                    "groupShape": "any"  # or "rectangular" or "circular"
                },
                description="Define how tiles should be grouped"
            ),
            RuleType.SPACING: RuleDefinition(
                type=RuleType.SPACING,
                template={
                    "minSpacing": 0,
                    "maxSpacing": None,
                    "relativeTo": []  # list of categories to space from
                },
                description="Define spacing requirements between tiles"
            ),
            RuleType.BORDER: RuleDefinition(
                type=RuleType.BORDER,
                template={
                    "mustBeBorder": False,
                    "borderSides": ["top", "bottom", "left", "right"],
                    "borderWidth": 1
                },
                description="Define border-specific rules_managers"
            )
        }

    @staticmethod
    def generate_template() -> Dict[str, Any]:
        """Genera un template JSON completo con todas las reglas disponibles"""
        template = {
            "type": "rule",
            "category": "",
            "rules_managers": {}
        }

        for rule_def in RulesCatalog.get_all_rules().values():
            template["rules_managers"][rule_def.type.value] = rule_def.template

        return template

    @staticmethod
    def validate_rule(rule_data: Dict[str, Any]) -> bool:
        """Valida que un JSON de reglas cumpla con la estructura requerida"""
        # Aquí iría la lógica de validación
        # Por ahora retorna True
        return True