
from flask import make_response
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
import os

# Setup Jinja2 environment to load HTML templates
# Assuming templates are in a 'templates' folder within the 'src' directory
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
if not os.path.exists(template_dir):
    os.makedirs(template_dir)

env = Environment(loader=FileSystemLoader(template_dir))

def generate_pdf_report(template_name, data, logo_path=None):
    """
    Generates a PDF report from an HTML template using WeasyPrint.

    Args:
        template_name (str): The filename of the Jinja2 HTML template (e.g., 'report_lateness.html').
        data (dict): Data to be rendered in the template.
        logo_path (str, optional): Absolute path to the logo image file.

    Returns:
        bytes: The generated PDF content as bytes.
        None: If template loading or PDF generation fails.
    """
    try:
        template = env.get_template(template_name)

        # Add logo path to data if provided
        if logo_path and os.path.exists(logo_path):
            # Convert to file URI for WeasyPrint
            data['logo_url'] = f'file://{logo_path}'
        else:
            data['logo_url'] = None
            if logo_path:
                print(f"Warning: Logo file not found at {logo_path}")

        html_content = template.render(data)

        # Basic CSS for styling (can be expanded or moved to a separate file)
        # Include basic styling for logo if present
        css_string = """
        @page { size: A4; margin: 2cm; }
        body { font-family: sans-serif; }
        h1 { text-align: center; color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .logo { max-width: 150px; max-height: 75px; display: block; margin-bottom: 20px; }
        """
        css = CSS(string=css_string)

        pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])
        return pdf_bytes

    except Exception as e:
        print(f"Error generating PDF report ({template_name}): {e}")
        return None

# Example HTML Template (save as src/templates/report_lateness.html)
"""
<!DOCTYPE html>
<html>
<head>
    <title>Relatório de Atrasos</title>
</head>
<body>
    {% if logo_url %}
        <img src="{{ logo_url }}" alt="Logo" class="logo">
    {% endif %}
    <h1>Relatório de Atrasos</h1>
    <p><strong>Período:</strong> {{ start_date }} a {{ end_date }}</p>
    <table>
        <thead>
            <tr>
                <th>Funcionário</th>
                <th>Data</th>
                <th>Hora Chegada</th>
                <th>Atraso (min)</th>
                <th>Horário Esperado</th>
            </tr>
        </thead>
        <tbody>
            {% for record in records %}
            <tr>
                <td>{{ record.employee_name }}</td>
                <td>{{ record.date }}</td>
                <td>{{ record.arrival_time }}</td>
                <td>{{ record.lateness_minutes }}</td>
                <td>{{ record.expected_arrival_time }}</td>
            </tr>
            {% else %}
            <tr>
                <td colspan="5" style="text-align: center;">Nenhum atraso registrado no período.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

