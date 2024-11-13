from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
import json
import shutil


class ProjectType(Enum):
    TOPDOWN = "topdown"
    SIDESCROLLER = "sidescroller"


@dataclass
class GridSettings:
    width: int
    height: int
    show_grid: bool = True
    snap_to_grid: bool = True
    grid_color: str = "#353535"


@dataclass
class RoomSettings:
    width: int
    height: int
    tileset: str
    rules: List[str]


class Project:
    def __init__(self, name: str, project_type: ProjectType):
        self.name = name
        self.type = project_type
        self.created = datetime.now()
        self.modified = datetime.now()
        self.version = "1.0"
        self.settings = {
            "grid": GridSettings(32, 32),
            "default_room": RoomSettings(30, 20, "", [])
        }
        self.workspaces: Dict[str, Workspace] = {}

    def create_workspace(self, name: str) -> 'Workspace':
        workspace = Workspace(name, self)
        self.workspaces[workspace.id] = workspace
        return workspace

    def save(self, path: Path):
        """Guarda el proyecto completo"""
        project_dir = path / self.name
        project_dir.mkdir(exist_ok=True)

        # Crear estructura de directorios
        (project_dir / "tilesets").mkdir(exist_ok=True)
        (project_dir / "rules").mkdir(exist_ok=True)
        (project_dir / "workspaces").mkdir(exist_ok=True)
        (project_dir / "backups").mkdir(exist_ok=True)

        # Guardar configuración principal
        config = self.to_dict()
        with open(project_dir / "project.json", "w") as f:
            json.dump(config, f, indent=2)

        # Guardar tilesets
        # Copiar los archivos de tileset a la carpeta tilesets
        for workspace in self.workspaces.values():
            if workspace.tileset:
                tileset_path = Path(workspace.tileset)
                if tileset_path.exists():
                    shutil.copy2(tileset_path, project_dir / "tilesets" / tileset_path.name)

        # Guardar rules
        # Copiar los archivos de reglas a la carpeta rules
        for workspace in self.workspaces.values():
            for room in workspace.rooms.values():
                for rule_file in room.rules:
                    rule_path = Path(rule_file)
                    if rule_path.exists():
                        shutil.copy2(rule_path, project_dir / "rules" / rule_path.name)


    @staticmethod
    def load(path: Path) -> 'Project':
        """Carga un proyecto existente"""
        with open(path / "project.json") as f:
            config = json.load(f)

        project = Project(
            name=config["metadata"]["name"],
            project_type=ProjectType(config["metadata"]["type"])
        )
        project.created = datetime.fromisoformat(config["metadata"]["created"])
        project.modified = datetime.fromisoformat(config["metadata"]["modified"])

        # Cargar configuraciones
        project.settings["grid"] = GridSettings(
            width=config["settings"]["grid"]["width"],
            height=config["settings"]["grid"]["height"],
            show_grid=config["settings"]["grid"]["show_grid"],
            snap_to_grid=config["settings"]["grid"]["snap_to_grid"],
            grid_color=config["settings"]["grid"]["grid_color"]
        )

        project.settings["default_room"] = RoomSettings(
            width=config["settings"]["default_room"]["width"],
            height=config["settings"]["default_room"]["height"],
            tileset=config["settings"]["default_room"]["tileset"],
            rules=config["settings"]["default_room"]["rules"]
        )

        # Cargar workspaces y rooms
        if "workspaces" in config:
            for workspace_id, workspace_data in config["workspaces"].items():
                workspace = Workspace(
                    name=workspace_data["name"],
                    project=project
                )
                workspace.id = workspace_data["id"]
                workspace.created = datetime.fromisoformat(workspace_data["created"])

                # Cargar rooms del workspace
                if "rooms" in workspace_data:
                    for room_id, room_data in workspace_data["rooms"].items():
                        room = Room(
                            name=room_data["name"],
                            workspace=workspace,
                            width=room_data["width"],
                            height=room_data["height"]
                        )
                        room.id = room_data["id"]
                        room.tileset = room_data["tileset"]
                        room.rules = room_data["rules"]
                        room.data = room_data["data"]
                        workspace.rooms[room.id] = room

                project.workspaces[workspace.id] = workspace

        return project

    def to_dict(self) -> dict:
        """Convierte el proyecto completo a un diccionario para guardarlo"""
        # Obtener la metadata básica
        data = {
            "metadata": {
                "name": self.name,
                "type": self.type.value,
                "version": self.version,
                "created": self.created.isoformat(),
                "modified": self.modified.isoformat()
            },
            "settings": {
                "grid": {
                    "width": self.settings["grid"].width,
                    "height": self.settings["grid"].height,
                    "show_grid": self.settings["grid"].show_grid,
                    "snap_to_grid": self.settings["grid"].snap_to_grid,
                    "grid_color": self.settings["grid"].grid_color
                },
                "default_room": {
                    "width": self.settings["default_room"].width,
                    "height": self.settings["default_room"].height,
                    "tileset": self.settings["default_room"].tileset,
                    "rules": self.settings["default_room"].rules
                }
            },
            # Agregar workspaces y su contenido
            "workspaces": {
                workspace_id: {
                    "id": workspace.id,
                    "name": workspace.name,
                    "created": workspace.created.isoformat(),
                    "rooms": {
                        room.id: {
                            "id": room.id,
                            "name": room.name,
                            "width": room.width,
                            "height": room.height,
                            "tileset": room.tileset,
                            "rules": room.rules,
                            "data": room.data
                        } for room in workspace.rooms.values()
                    }
                } for workspace_id, workspace in self.workspaces.items()
            }
        }
        return data


class Workspace:
    def __init__(self, name: str, project: Project):
        self.id = f"ws_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.project = project
        self.created = datetime.now()
        self.rooms: Dict[str, Room] = {}
        self.tileset = ""

    def create_room(self, name: str, width: Optional[int] = None,
                    height: Optional[int] = None) -> 'Room':
        room = Room(
            name=name,
            workspace=self,
            width=width or self.project.settings["default_room"].width,
            height=height or self.project.settings["default_room"].height
        )
        self.rooms[room.id] = room
        return room

    def save(self, workspaces_dir: Path):
        workspace_dir = workspaces_dir / self.id
        workspace_dir.mkdir(exist_ok=True)

        # Guardar configuración del workspace
        config = {
            "id": self.id,
            "name": self.name,
            "created": self.created.isoformat()
        }
        with open(workspace_dir / "workspace.json", "w") as f:
            json.dump(config, f, indent=2)

        # Guardar rooms
        for room in self.rooms.values():
            room.save(workspace_dir)


class Room:
    def __init__(self, name: str, workspace: Workspace, width: int, height: int):
        self.id = f"room_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.name = name
        self.workspace = workspace
        self.width = width
        self.height = height
        self.tileset = ""
        self.rules: List[str] = []
        self.data: List[List[int]] = [[0] * width for _ in range(height)]

    def save(self, workspace_dir: Path):
        """Guarda la configuración y datos de la room"""
        config = {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "tileset": self.tileset,
            "rules": self.rules,
            "data": self.data
        }
        with open(workspace_dir / f"{self.id}.json", "w") as f:
            json.dump(config, f, indent=2)