import argparse
import subprocess
import pkg_resources
from PIL import Image, ImageDraw, ImageFont


def get_package_dependencies(package_name, max_depth, current_depth=0, seen=None):
    if seen is None:
        seen = set()

    if package_name in seen or current_depth >= max_depth:
        return {}

    seen.add(package_name)

    # Получаем информацию о пакете с помощью pip
    try:
        dist = pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        print(f"Package '{package_name}' not found.")
        return {}

    dependencies = {package_name: []}
    for dep in dist.requires():
        dependencies[package_name].append(dep.project_name)
        # Рекурсивно собираем зависимости для текущего пакета
        dependencies.update(get_package_dependencies(dep.project_name, max_depth, current_depth + 1, seen))

    return dependencies


def draw_graph(dependencies, image_path):
    # Определяем размеры изображения
    img_width, img_height = 800, 600
    img = Image.new('RGB', (img_width, img_height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Задаём параметры для отрисовки графа
    font = ImageFont.load_default()

    # Определяем начальные координаты для пакета
    x, y = 100, 50
    step_y = 50

    # Рисуем пакет и его зависимости
    def draw_package(package, x, y):
        draw.text((x, y), package, font=font, fill=(0, 0, 0))
        return x + 100, y + step_y

    def recursive_draw(package, x, y, depth=0):
        if depth > 10:  # Лимитируем глубину рисования для предотвращения бесконечных циклов
            return
        # Рисуем текущий пакет
        new_x, new_y = draw_package(package, x, y)

        # Рисуем зависимости для текущего пакета
        if package in dependencies:
            for dep in dependencies[package]:
                # Соединяем линии зависимости
                draw.line([(new_x - 50, new_y - 10), (new_x + 50, new_y + 10)], fill=(0, 0, 0), width=1)
                new_y = recursive_draw(dep, new_x, new_y, depth + 1)

        return new_y

    # Рисуем основной пакет
    recursive_draw(list(dependencies.keys())[0], x, y)

    # Сохраняем изображение
    img.save(image_path)


def main():
    parser = argparse.ArgumentParser(description='Build and visualize package dependency graph without Graphviz.')
    parser.add_argument('--package_name', type=str, required=True, help='Name of the package to analyze')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output image file (PNG)')
    parser.add_argument('--max_depth', type=int, default=3, help='Maximum depth for dependency analysis')

    args = parser.parse_args()

    # Получаем зависимости пакета
    dependencies = get_package_dependencies(args.package_name, args.max_depth)

    # Визуализируем граф зависимостей в изображение
    draw_graph(dependencies, args.output_file)

    print(f"Dependency graph for {args.package_name} has been successfully saved to {args.output_file}")


if __name__ == '__main__':
    main()
