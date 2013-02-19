from metalayercore.actions.classes import BaseAction
from metalayercore.actions.controllers import ActionController

tokenizer = None
tagger = None

class Action(BaseAction):
    def get_unconfigured_config(self):
        return {
            'name':'localtagging',
            'display_name_short':'Tagging',
            'display_name_long':'Tagging',
            'image_small':'/static/images/thedashboard/actions/tagging_small.png',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Tags',
                        'name':'tags',
                        'type':'string'
                    }
                ]
            }
        }

    def run(self, config, content):
        import nltk
        """
        from metalayercore.actions.controllers import ActionController
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
        tagger = ActionController.CacheGet('localtagging_tagger', -1)
        if tagger == -1:
            tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())
            ActionController.CacheAdd('localtagging_tagger', tagger)
        """
        global tagger, tokenizer
        if not tokenizer:
            tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+|[^\w\s]+')
        if not tagger:
            tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())
        results = [{'id':i['id'], 'tags':self._get_tags(config, i, tokenizer, tagger)} for i in content]
        return results

    def get_content_item_template(self):
        config = self.get_unconfigured_config()
        controller = ActionController(config)
        sentiment_property = config['content_properties']['added'][0]
        encoded_property = controller._search_encode_property(sentiment_property)
        return ""\
               "{{if typeof (" + encoded_property + ") !== 'undefined'}}"\
               "    {{if " + encoded_property + ".length > 0 && " + encoded_property + "[0] != '_none' }}"\
               "    <li class='action_values tags'>"\
               "        <label><img src='" + config['image_small'] + "' style='position:relative;top:5px;left:-2px;width:16px;height:16px;'/>&nbsp;Tags:</label>&nbsp;"\
               "        <span style='font-weight:bold;'>" \
               "            {{each(index, element) " + encoded_property + "}}" \
               "                {{if element != '_none' && index < 5}}"\
               "                    <a class='action_inline_filter' data-facet_name='" + encoded_property + "' data-facet_value='${element}'>${element}</a>"\
               "                {{/if}} "\
               "                {{if index == 6}}...{{/if}}" \
               "            {{/each}}" \
               "        </span>"\
               "    </li>"\
               "    {{/if}}"\
               "{{/if}}"

    def _get_tags(self, config, content_item, tokenizer, tagger):
        text = self._extract_text(config, content_item)
        tokenized = tokenizer.tokenize(text)
        tagged = tagger.tag(tokenized)
        results = [word.replace('#', '') for word in text.split() if word.startswith('#')]
        for pair in tagged:
            if len(pair) > 1:
                if pair[1] and pair[1].startswith('N'):
                    if pair[0].lower() not in results and len(pair[0]) > 3:
                        results.append(pair[0].lower())
        results = sorted(results, key=lambda r: len(r), reverse=True)
        return results

    def _extract_text(self, config, content_item):
        text = ''
        if 'title' in content_item:
            text += ' ' + content_item['title']
        if 'text' in content_item:
            for t in content_item['text']:
                text += ' ' + t
        return text.encode('ascii', 'ignore')
