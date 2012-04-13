from metalayercore.actions.classes import BaseAction
from metalayercore.actions.controllers import ActionController

class Action(BaseAction):
    def get_unconfigured_config(self):
        return {
            'name':'trssbox3newsdata',
            'display_name_short':'News Data',
            'display_name_long':'TRSS Box3 Embedded Data',
            'image_small':'http://thomsonreuters.com/favicon.ico',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Story ID',
                        'name':'storyid',
                        'type':'string'
                    },
                    {
                        'display_name':'Language',
                        'name':'language',
                        'type':'string'
                    },
                    {
                        'display_name':'Number of Words',
                        'name':'numberofwords',
                        'type':'float'
                    },
                    {
                        'display_name':'Number of Characters',
                        'name':'numberofcharacters',
                        'type':'float'
                    },
                    {
                        'display_name':'Locations',
                        'name':'locations',
                        'type':'location_string'
                    },
                    {
                        'display_name':'Subjects',
                        'name':'subjects',
                        'type':'string'
                    },
                    {
                        'display_name':'Industries',
                        'name':'industries',
                        'type':'string'
                    },
                    {
                        'display_name':'Companies',
                        'name':'companies',
                        'type':'string'
                    },
                    {
                        'display_name':'People',
                        'name':'people',
                        'type':'string'
                    },
                ]
            }
        }

    def run(self, config, content):
        results = []
        for item in content:
            item_results = {}
            for prop in self.get_unconfigured_config()['content_properties']['added']:
                extension = 'f' if prop['type'] == 'float' else 's'
                key = 'extensions_%s_%s' % (prop['name'], extension)
                if key in item and item[key]:
                    item_results[prop['name']] = item[key]
            if item_results:
                item_results['id'] = item['id']
                results.append(item_results)
        return results

    def get_content_item_template(self):
        config = self.get_unconfigured_config()
        controller = ActionController(config)
        storyid = config['content_properties']['added'][0]
        language = config['content_properties']['added'][1]
        numberofwords = config['content_properties']['added'][2]
        numberofchars = config['content_properties']['added'][3]
        locations = config['content_properties']['added'][4]
        subjects = config['content_properties']['added'][5]
        industries = config['content_properties']['added'][6]
        companies = config['content_properties']['added'][7]
        people = config['content_properties']['added'][8]
        return "" \
            "<li class='action_values' style='padding-top:5px'><label>Language Code:</label> <b>${" + controller._search_encode_property(language) + "}</b></li> " \
            "<li class='action_values'><label>Character Count:</label> <b>${" + controller._search_encode_property(numberofchars) + "}</b></li> " \
            "{{if " + controller._search_encode_property(locations) + "}}"\
            "    <li class='action_values'>"\
            "        <label>locations:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>"\
            "            {{each(index, element) " + controller._search_encode_property(locations) + "}}"\
            "                {{if element != '_none' && index < 5}}${element}{{/if}} {{if index == 6}}...{{/if}}"\
            "            {{/each}}"\
            "        </span>"\
            "    </li>"\
            "{{/if}}"\
            "{{if " + controller._search_encode_property(subjects) + "}}"\
            "    <li class='action_values'>"\
            "        <label>subjects:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>"\
            "            {{each(index, element) " + controller._search_encode_property(subjects) + "}}"\
            "                {{if element != '_none' && index < 5}}${element}{{/if}} {{if index == 6}}...{{/if}}"\
            "            {{/each}}"\
            "        </span>"\
            "    </li>"\
            "{{/if}}"\
            "{{if " + controller._search_encode_property(industries) + "}}"\
            "    <li class='action_values'>"\
            "        <label>industries:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>"\
            "            {{each(index, element) " + controller._search_encode_property(industries) + "}}"\
            "                {{if element != '_none' && index < 5}}${element}{{/if}} {{if index == 6}}...{{/if}}"\
            "            {{/each}}"\
            "        </span>"\
            "    </li>"\
            "{{/if}}"\
            "{{if " + controller._search_encode_property(companies) + "}}"\
            "    <li class='action_values'>"\
            "        <label>companies:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>"\
            "            {{each(index, element) " + controller._search_encode_property(companies) + "}}"\
            "                {{if element != '_none' && index < 5}}${element}{{/if}} {{if index == 6}}...{{/if}}"\
            "            {{/each}}"\
            "        </span>"\
            "    </li>"\
            "{{/if}}"\
            "{{if " + controller._search_encode_property(people) + "}}"\
            "    <li class='action_values'>"\
            "        <label>people:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>"\
            "            {{each(index, element) " + controller._search_encode_property(people) + "}}"\
            "                {{if element != '_none' && index < 5}}${element}{{/if}} {{if index == 6}}...{{/if}}"\
            "            {{/each}}"\
            "        </span>"\
            "    </li>"\
            "{{/if}}"