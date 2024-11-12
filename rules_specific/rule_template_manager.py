import os
import json
from typing import Dict, List


class RuleTemplateManager:
    """Gestor de templates de reglas"""

    def __init__(self):
        self.templates_dir = "rule_templates"
        self.ensure_templates_directory()

    def ensure_templates_directory(self):
        """Asegura que existe el directorio de templates"""
        os.makedirs(self.templates_dir, exist_ok=True)

    def save_as_template(self, rule_data: Dict, template_name: str) -> bool:
        """Guarda una regla como template"""
        try:
            file_path = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(file_path, 'w') as f:
                json.dump(rule_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving template: {str(e)}")
            return False

    def load_template(self, template_name: str) -> Dict:
        """Carga un template existente"""
        try:
            file_path = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading template: {str(e)}")
            return None

    def get_available_templates(self) -> List[str]:
        """Obtiene lista de templates disponibles"""
        try:
            templates = [f[:-5] for f in os.listdir(self.templates_dir) if f.endswith('.json')]
            return templates
        except Exception:
            return []

    def apply_template(self, rule_data: Dict, template_name: str) -> Dict:
        """Aplica un template a una regla existente"""
        template = self.load_template(template_name)
        if template:
            # Preservar categoría original
            category = rule_data.get("category")
            # Aplicar template
            rule_data.update(template)
            # Restaurar categoría
            if category:
                rule_data["category"] = category
        return rule_data