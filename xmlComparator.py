#!/usr/bin/env python3
#author: reycotallo98 akka redDev

import xml.etree.ElementTree as ET
import difflib
import argparse
import sys
from bs4 import BeautifulSoup

# Aumentar el límite de recursión
sys.setrecursionlimit(2000)

def parse_xml(file_path):
    """Convierte un archivo XML en una lista de líneas de texto bien formateadas."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    def elem_to_string(elem):
        """Convierte un elemento XML a una cadena con formato legible."""
        return ET.tostring(elem, encoding='unicode', method='xml')

    # Convertir el XML a una cadena y luego dividir en líneas
    xml_string = elem_to_string(root)
    return split_long_lines(xml_string.splitlines())

def split_long_lines(lines, max_length=80):
    """Divide líneas largas en múltiples líneas más cortas, respetando las etiquetas XML."""
    split_lines = []
    for line in lines:
        while len(line) > max_length:
            # Encuentra el último cierre de etiqueta antes del límite de longitud
            split_point = line.rfind('>', 0, max_length)
            if split_point == -1:  # No se encontró un cierre de etiqueta adecuado
                split_point = max_length
            split_lines.append(line[:split_point + 1])
            line = line[split_point + 1:].lstrip()
        split_lines.append(line)
    return split_lines

def compare_xml_lines(lines1, lines2, flag):
    """Compara dos listas de líneas y devuelve un HTML detallado de las diferencias con identificadores."""
    differ = difflib.HtmlDiff(wrapcolumn=80)
    diff_html = differ.make_file(lines1, lines2, context=False, numlines=0)

    # Parsear el HTML de diferencias para añadir identificadores únicos
    soup = BeautifulSoup(diff_html, 'html.parser')
    idx = 1
    if flag:
        for diff_row in soup.find_all('tr'):
            td_elements = diff_row.find_all('td', nowrap=True)
            

            # Verificar si hay un elemento con una clase que empiece con "diff"
            if td_elements:
                found_diff_class = any(td.find(class_=lambda c: c and c.startswith('diff')) for td in td_elements)

                if not found_diff_class:
                    print("No se encontró un <td nowrap> con una clase que empieza con 'diff'. Eliminando el <tr>.")
                    diff_row.decompose()
                    pass
        

        
                print(f"<tr> sin <td nowrap>.")
                if diff_row.get('class') and 'diff_add' in diff_row['class']:
                    diff_row['id'] = f'added_{idx}'
                    
                elif diff_row.get('class') and 'diff_sub' in diff_row['class']:
                    diff_row['id'] = f'removed_{idx}'
                    
                elif diff_row.get('class') and 'diff_chg' in diff_row['class']:
                    diff_row['id'] = f'changed_{idx}'
                    
                idx += 1
        

    else:
        for diff_row in soup.find_all('tr'):
            td_elements = diff_row.find_all('td', nowrap=True)
            if td_elements:
                print(f"<tr> sin <td nowrap>.")
                if diff_row.get('class') and 'diff_add' in diff_row['class']:
                    diff_row['id'] = f'added_{idx}'
                    
                elif diff_row.get('class') and 'diff_sub' in diff_row['class']:
                    diff_row['id'] = f'removed_{idx}'
                    
                elif diff_row.get('class') and 'diff_chg' in diff_row['class']:
                    diff_row['id'] = f'changed_{idx}'
                    
                idx += 1
            
    return str(soup)

def generate_html_diff(file1, file2, flag):
    """Genera el HTML completo para mostrar las diferencias con navegación."""
    lines1 = parse_xml(file1)
    lines2 = parse_xml(file2)

    html_diff = compare_xml_lines(lines1, lines2,flag)

    custom_css = '''
    <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f7f7f7; }
    .diff-wrapper { display: flex; flex-direction: column; }
    .diff-container { width: 100%; overflow: auto; flex: 1; }
    .diff_nav { position: fixed; bottom: 20px; right: 20px; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    .diff_nav button { margin: 0 5px; padding: 10px 20px; font-size: 14px; cursor: pointer; }
    table.diff { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .diff_header { background-color: #e6e6e6; text-align: left; padding: 8px; }
    .diff_next { background-color: #f2f2f2; }
    .diff_add { background-color: #ccffcc; }  /* Verde claro para adiciones */
    .diff_chg { background-color: #ffff99; }  /* Amarillo claro para cambios */
    .diff_sub { background-color: #ffcccc; }  /* Rojo claro para eliminaciones */
    td { word-wrap: break-word; white-space: pre-wrap; padding: 8px; vertical-align: top; }
    .legend { margin-bottom: 20px; }
    .legend span { display: inline-block; padding: 5px 10px; margin-right: 10px; }
    .legend .added { background-color: #ccffcc; }
    .legend .changed { background-color: #ffff99; }
    .legend .deleted { background-color: #ffcccc; }
    </style>
    '''

    custom_js = '''
    
    
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var currentIndex = 0;
        var ids = Array.from(document.querySelectorAll('tr td:first-child[id]')).map(el => el.id);
        console.log(ids)
        function goToIndex(index) {
            if (index >= 0 && index < ids.length) {
                console.log(ids[index]);
                window.location.hash = '#' + ids[index];
                currentIndex = index;
            }
        }
    
        // Hacemos que las funciones prev() y next() estén disponibles en el ámbito global
        window.next = function() {
            console.log('pa alante')
            if (currentIndex < ids.length - 1) {
                goToIndex(currentIndex + 1);
            }
        };
    
        window.prev = function() {
             console.log('pa atras')
            if (currentIndex > 0) {
                goToIndex(currentIndex - 1);
            }
        };
    
        // Inicializar el índice al primer cambio visible
        if (ids.length > 0) {
            goToIndex(0);
        }
    });
    </script>
    '''

    legend_html = '''
    <div class="legend">
        <span class="added">Added</span>
        <span class="changed">Changed</span>
        <span class="deleted">Deleted</span>
    </div>
    '''

    nav_html = '''
    <div class="diff_nav">
        <button id="prev" onclick="prev()">Previous</button>
        <button id="next" onclick="next()">Next</button>
    </div>
    '''

    full_html = f'''
    <html>
    <head>
    {custom_css}
    </head>
    <body>
    {legend_html}
    <div class="diff-wrapper">
        <div class="diff-container">
            {html_diff}
        </div>
    </div>
    {nav_html}
    {custom_js}
    </body>
    </html>
    '''
    return full_html

def save_html_diff(html_diff, output_file):
    """Guarda las diferencias en un archivo HTML."""
    with open(output_file, 'w') as file:
        file.write(html_diff)

def main():
    parser = argparse.ArgumentParser(description='Compara dos archivos XML y genera un informe de diferencias en HTML.')
    parser.add_argument('file1', help='Ruta del primer archivo XML')
    parser.add_argument('file2', help='Ruta del segundo archivo XML')
    parser.add_argument('output', help='Nombre del archivo de salida HTML')
    parser.add_argument(
    '-d','--deactivate', 
    action='store_true', 
    help="Hace que el script elimine de los documentos todos lo que no son cambios, mostrando solo los cambios"
)
    args = parser.parse_args()
    print(args.deactivate)
    html_diff = generate_html_diff(args.file1, args.file2, args.deactivate)
    save_html_diff(html_diff, args.output)
    print(f"Las diferencias se han guardado en {args.output}")

if __name__ == '__main__':
    main()
