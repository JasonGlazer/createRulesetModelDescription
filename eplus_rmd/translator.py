from pathlib import Path
from typing import Dict

from eplus_rmd.input_file import InputFile
from eplus_rmd.output_file import OutputFile


class Translator:
    """This class reads in the input files and does the heavy lifting to write output files"""

    def __init__(self, epjson_file_path: Path):
        print(f"Reading epJSON input file at {str(epjson_file_path)}")
        self.epjson_file = InputFile(epjson_file_path)
        self.epjson_object = self.epjson_file.epjson_object
        self.json_results_object = self.epjson_file.json_results_object

        self.rmd_file_path = OutputFile(epjson_file_path)
        print(f"Will write output file to {str(self.rmd_file_path)}")

        self.rmd = {}
        self.instance = {}
        self.building = {}
        self.building_segment = {}

    @staticmethod
    def validate_input_contents(input_json: Dict):
        if 'Version' not in input_json:
            raise Exception("Did not find Version key in input file epJSON contents, aborting")
        if 'Version 1' not in input_json['Version']:
            raise Exception("Did not find \"Version 1\" key in input epJSON Version value, aborting")
        if "version_identifier" not in input_json['Version']['Version 1']:
            raise Exception("Did not find \"version_identifier\" key in input epJSON Version value, aborting")

    def get_building_name(self):
        building_input = self.epjson_object['Building']
        return list(building_input.keys())[0]

    def create_skeleton(self):
        self.building_segment = {'id': 'segment 1'}

        self.building = {'id': self.get_building_name(),
                         'notes': 'this file contains only a single building',
                         'building_segments': [self.building_segment, ]}

        self.instance = {'id': 'Only instance',
                         'notes': 'this file contains only a single instance',
                         'buildings': [self.building, ]}

        self.rmd = {'id': 'rmd_root',
                    'notes': 'generated by createRulesetModelDescription from EnergyPlus',
                    'ruleset_model_instances': [self.instance, ]}

    def add_zones(self):
        tabular_reports = self.json_results_object['TabularReports']
        for tabular_report in tabular_reports:
            if tabular_report['ReportName'] == 'Input Verification and Results Summary':
                tables = tabular_report['Tables']
                for table in tables:
                    if table['TableName'] == 'Zone Summary':
                        rows = table['Rows']
                        zone_names = list(rows.keys())
                        zone_names.remove('Total')
                        zone_names.remove('Conditioned Total')
                        zone_names.remove('Unconditioned Total')
                        zone_names.remove('Not Part of Total')
                        print(zone_names)
                break
        zones = []
        for zone_name in zone_names:
            zone = {'id': zone_name}
            zones.append(zone)
        self.building_segment['zones'] = zones

    def process(self):
        epjson = self.epjson_object
        Translator.validate_input_contents(epjson)
        version_id = epjson['Version']['Version 1']['version_identifier']
        self.create_skeleton()
        self.add_zones()
        self.rmd_file_path.write(self.rmd)
