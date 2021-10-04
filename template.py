import re


class MailTemplate(object):
    pattern = r"{{([_a-zA-Z0-9]*)}}"

    def __init__(self, template='', data={}):
        self.template = template
        self.data = data

    def _replace(self, match):
        tag = match.group(1)
        return self.data.get(tag, match.group(0))

    def render(self):
        return re.sub(self.pattern, self._replace, self.template)


if __name__ == '__main__':
    from datetime import datetime
    data = {
        'TITLE': 'Mr',
        'FIRST_NAME': 'John',
        'LAST_NAME': 'Smith',
        'TODAY': datetime.now().strftime('%d %b %y'),
    }
    template = MailTemplate(
        '''
        Hi {{TITLE}} {{FIRST_NAME}} {{LAST_NAME}}.
        Today, {{TODAY}}, we would like to tell you that... {{NOTHING}}
        Sincerely,
        The Marketing Team
        ''', data)
    print(template.render())
