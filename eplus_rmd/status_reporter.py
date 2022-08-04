from yaml import safe_load, safe_dump
from pathlib import Path


class StatusReporter:
    def __init__(self, epjson_file_path: Path):
        parent_dir = Path(__file__).parent

        # the extra schema file includes extra tags on fields related to appendix G and energyplus
        extra_schema_file = 'ASHRAE229_extra.schema.yaml'
        extra_schema_path = Path(parent_dir).joinpath(extra_schema_file)
        if extra_schema_path.exists():
            with open(extra_schema_path) as schema_f:
                self.extra_schema = safe_load(schema_f)
        self.report_file_path = epjson_file_path.with_suffix('.report')

    def generate(self, rmd_dict):
        if self.extra_schema:
            with open(self.report_file_path, 'w') as f:
                f.write('============= Generated Report ==============\n')
                for data_group_name, node in self.extra_schema.items():
                    if 'Object Type' in node:
                        if node['Object Type'] == 'Data Group':
                            f.write(data_group_name)
                        if 'Data Elements' in node:
                            data_elements = node['Data Elements']
                            counter = {'inout ': 0, 'input ': 0, 'output': 0, 'note  ': 0, 'null  ': 0}
                            f.write('  #elements: ' + str(len(data_elements)) + '\n')
                            for data_element in data_elements:
                                fields = data_elements[data_element]
                                type = self.type_of_ep_field(fields)
                                f.write('  ' + type + '  ' + data_element + '\n')
                                counter[type] = counter[type] + 1
                            f.write('  Data element EP counts:  ' + str(counter) + '\n')

    def type_of_ep_field(self, fields):
        plus_in = False
        plus_out = False
        plus_note = False
        if 'EPin Object' in fields:
            if fields['EPin Object']:
                plus_in = True
        if 'EPin Field' in fields:
            if fields['EPin Field']:
                plus_in = True
        if 'EPout File' in fields:
            if fields['EPout File']:
                plus_out = True
        if 'EPout Report' in fields:
            if fields['EPout Report']:
                plus_out = True
        if 'EPout Table' in fields:
            if fields['EPout Table']:
                plus_out = True
        if 'EPout Column' in fields:
            if fields['EPout Column']:
                plus_out = True
        if 'EP Notes' in fields:
            if fields['EP Notes']:
                plus_note = True
        if plus_in and plus_out:
            return 'inout '
        elif plus_in:
            return 'input '
        elif plus_out:
            return 'output'
        elif plus_note:
            return 'note  '
        else:
            return 'null  '