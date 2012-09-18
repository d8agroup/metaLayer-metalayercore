"""Report output option used for saving visualizations into a customizable
report.
"""

from metalayercore.outputs.classes import BaseOutput


class Output(BaseOutput):
    def get_unconfigured_config(self):
        """Return the base configuration data."""
        return {
            'name': 'reportoutput',
            'display_name_short': 'Report',
            'display_name_long': 'Report',
            'type': 'render',
            'modal': True,
            'instructions': 'Create a custom report with this datapoint.'
        }

    def generate_html(self, config, search_results):
        """Since this is a modal dialog the template resides with the other
        modals, static/html/thedashboard/modals
        """
        return ""
