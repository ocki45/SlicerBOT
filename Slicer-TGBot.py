

# Укажите свой токен Telegram-бота
#TELEGRAM_BOT_TOKEN = "8062188431:AAF28CVPseI-FvfjFk5cXI4nusihZ232L9o"

import os
import math
from telegram import Bot
import logging
from pathlib import Path
import tempfile
import trimesh
import pyvista as pv
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, LineString, GeometryCollection, MultiLineString
from shapely.ops import unary_union
from shapely.validation import make_valid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import vtk
from shapely import affinity

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class SliceEngine:
    def __init__(self):
        self.settings = {
            'layer_height': 0.12,
            'nozzle_diameter': 0.4,
            'filament_diameter': 1.75,
            'print_temp': 210,
            'bed_temp': 60,
            'travel_speed': 200,
            'print_speed': 50,
            'outer_wall_speed': 30,
            'infill_speed': 80,
            'infill_density': 120,
            'retraction': 5,
            'retract_speed': 40,
            'z_hop': 0.3,
            'bottom_layers': 15,
            'top_layers': 15,
            'perimeters': 8,
            'small_feature': 0.0001,
            'solid_overlap': 0.3,
            'fill_angles': [45, 135, 90],
            'xy_compensation': 0.002,
            'simplify_tolerance': 0.0005
        }
        self.current_e = 0

    def process(self, stl_path: str, gcode_path: str) -> None:
        self.current_e = 0
        mesh = self._prepare_mesh(stl_path)
        layers = self._slice(mesh)
        self._export_gcode(layers, gcode_path)

    def _prepare_mesh(self, path: str) -> trimesh.Trimesh:
        mesh = trimesh.load(path)
        mesh.process()
        if not mesh.is_watertight:
            mesh.fill_holes()
        mesh.remove_degenerate_faces()
        return mesh

    def _slice(self, mesh: trimesh.Trimesh) -> list:
        layers = []
        z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2]
        layer_count = int(math.ceil((z_max - z_min) / self.settings['layer_height']))

        for i in range(layer_count):
            z = z_min + i * self.settings['layer_height']
            section = self._get_section(mesh, z)
            if section.is_empty:
                continue

            is_solid = i < self.settings['bottom_layers'] or i >= layer_count - self.settings['top_layers']

            layers.append({
                'z': z,
                'walls': self._generate_perimeters(section),
                'infill': self._generate_infill(section, is_solid)
            })

        return layers

    def _get_section(self, mesh: trimesh.Trimesh, z: float) -> MultiPolygon:
        section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if not section:
            return MultiPolygon()

        polygons = []
        for entity in section.entities:
            points = section.vertices[entity.points][:, :2]
            if len(points) < 3:
                continue

            poly = Polygon(points) \
                .buffer(
                self.settings['xy_compensation'],
                join_style=2,
                mitre_limit=10.0,
                single_sided=True
            ) \
                .simplify(self.settings['simplify_tolerance'])

            if poly.area > self.settings['small_feature']:
                polygons.append(poly)

        union = unary_union(polygons)
        return union if not union.is_empty else MultiPolygon()

    def _generate_perimeters(self, geometry: MultiPolygon) -> list:
        perimeters = []
        nozzle = self.settings['nozzle_diameter']
        offsets = np.linspace(0, nozzle * 0.7, self.settings['perimeters'])

        for offset in offsets:
            offset_geom = geometry.buffer(
                -offset,
                join_style=2,
                mitre_limit=5.0,
                single_sided=True
            )
            if offset_geom.is_empty:
                continue

            for p in self._iter_polygons(offset_geom):
                if p.area >= (nozzle * 0.5) ** 2:
                    coords = np.array(p.exterior.coords)
                    perimeters.append(coords)

        return perimeters

    def _generate_infill(self, geometry: MultiPolygon, is_solid: bool) -> list:
        patterns = []
        nozzle = self.settings['nozzle_diameter']
        density = 1.0 if is_solid else self.settings['infill_density'] / 100

        for poly in self._iter_polygons(geometry):
            expanded = poly.buffer(nozzle * self.settings['solid_overlap'])

            for angle in self.settings['fill_angles']:
                rotated = affinity.rotate(expanded, angle, origin='centroid')
                lines = self._generate_infill_lines(
                    rotated,
                    spacing=nozzle / density,
                    extension=nozzle * 4
                )
                for line in lines:
                    unrotated = affinity.rotate(line, -angle, origin='centroid')
                    if unrotated.length > nozzle * 0.5:
                        patterns.append(np.array(unrotated.coords.xy).T)

        return patterns

    def _generate_infill_lines(self, poly: Polygon, spacing: float, extension: float) -> list:
        bbox = poly.bounds
        lines = []

        for x in np.arange(
                bbox[0] - extension,
                bbox[2] + extension,
                spacing
        ):
            line = LineString([
                (x, bbox[1] - extension),
                (x, bbox[3] + extension)
            ])
            intersection = poly.intersection(line)
            if intersection.is_empty:
                continue

            if isinstance(intersection, LineString):
                lines.append(intersection)
            elif isinstance(intersection, MultiLineString):
                lines.extend(intersection.geoms)

        return [l for l in lines if l.length > self.settings['nozzle_diameter'] * 0.5]

    def _iter_polygons(self, geom):
        if isinstance(geom, MultiPolygon):
            yield from geom.geoms
        elif isinstance(geom, Polygon):
            yield geom

    def _export_gcode(self, layers: list, output_path: str) -> None:
        output = [
            "G28",
            f"M104 S{self.settings['print_temp']}",
            f"M140 S{self.settings['bed_temp']}",
            "G1 Z10 F5000"
        ]

        for layer in layers:
            output.append(f"\n;LAYER:{layer['z']:.2f}")
            output.append(f"G0 Z{layer['z'] + self.settings['z_hop']:.2f} F3000")
            output.append(f"G1 Z{layer['z']:.2f} F{self.settings['print_speed'] * 60}")

            for wall_path in layer['walls']:
                self._extrude(output, wall_path, self.settings['outer_wall_speed'], 1.1)

            for infill_path in layer['infill']:
                self._extrude(output, infill_path, self.settings['infill_speed'], 1.0)

        output.extend([
            "M104 S0",
            "M140 S0",
            "G28 X",
            "M84"
        ])

        with open(output_path, 'w') as f:
            f.write('\n'.join(output))

    def _extrude(self, gcode: list, path: np.ndarray, speed: int, flow: float) -> None:
        if len(path) < 2:
            return

        nozzle_area = math.pi * (self.settings['nozzle_diameter'] / 2) ** 2
        layer_height = self.settings['layer_height']

        for i in range(1, len(path)):
            x0, y0 = path[i - 1]
            x1, y1 = path[i]
            dx = x1 - x0
            dy = y1 - y0
            length = math.hypot(dx, dy)

            if length < 0.01:
                continue

            volume = layer_height * self.settings['nozzle_diameter'] * length
            e = (volume * flow) / nozzle_area

            if i == 1:
                gcode.append(f"G0 X{x0:.3f} Y{y0:.3f} F{self.settings['travel_speed'] * 60}")

            self.current_e += e
            gcode.append(f"G1 X{x1:.3f} Y{y1:.3f} E{self.current_e:.5f} F{speed * 60}")


class TelegramBot:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.slice_engine = SliceEngine()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(
            filters.Document.FileExtension("stl"),
            self.handle_file
        ))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Привет! Отправь мне STL файл для преобразования в G-код."
        )

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            file = await update.message.document.get_file()
            with tempfile.TemporaryDirectory() as tmp_dir:
                stl_path = str(Path(tmp_dir) / "model.stl")
                await file.download_to_drive(custom_path=stl_path)

                if not os.path.exists(stl_path):
                    raise ValueError("Файл не загружен")

                gcode_path = str(Path(tmp_dir) / "output.gcode")
                self.slice_engine.process(stl_path, gcode_path)

                with open(gcode_path, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        caption="Ваш G-код готов!"
                    )

        except Exception as e:
            logger.error(f"Ошибка: {type(e).__name__} - {str(e)}")
            await update.message.reply_text(f"Ошибка обработки: {str(e)}")

    def run(self) -> None:
        self.application.run_polling()


if __name__ == "__main__":
    TOKEN = "8062188431:AAF28CVPseI-FvfjFk5cXI4nusihZ232L9o"
    if not TOKEN:
        raise ValueError("Не задан TELEGRAM_BOT_TOKEN")

    bot = TelegramBot(TOKEN)
    bot.run()