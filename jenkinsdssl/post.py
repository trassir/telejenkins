import re

def error(x: str):
    raise ValueError(x)

RE_SEPARATORS = re.compile(r'[,;]')
def decode_notify(s: str):
    return re.sub(RE_SEPARATORS, ' ', s).split()

class PayloadUrlButton:
    def __init__(self, url, name):
        super().__init__()
        self.url = url
        self.name = name

class PostNotify:
    def arg(self, name, typename, nonemessage=None, optional=False, args=None):
        _args = args or self.kwargs
        value = _args.get(name)
        if not value:
            if optional:
                return None
            else:
                raise ValueError(nonemessage)
        if not isinstance(value, typename):
            raise ValueError(f'"{name}" must be a {typename} (got a {type(value)})')
        return value

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        notify = self.arg('notify', str, 'Parameters should include "notify"')
        self.notify = decode_notify(notify)
        self.type = self.arg('type', str, 'Parameters should include "type"')
        if self.type == 'simple':
            self.build_url    = self.arg('url',      str, '"simple" type supposed to include "url"')
            self.job_name     = self.arg('job_name', str, '"simple" type supposed to include "job_name"')
            self.build        = self.arg('build',    str, '"simple" type supposed to include "build"')
            self.build_result = self.arg('status',   str, '"simple" type supposed to include "status"')
            self.message      = self.arg('text',     str, optional=True) or ''
        elif self.type == 'markdown':
            self.markdown = self.arg('markdown', str, '"markdown" type supposed to include "markdown"')
        else:
            raise ValueError(f'Unknown request type "{self.type}"')
        payload = self.arg('payload', list, optional=True) or []
        self.payload = []
        for p in payload:
            tp = self.arg('type', str, 'Payload should include "type"', args=p)
            if tp == 'url_button':
                url  = self.arg('url', str, '"url_button" payload supposed to include "url"', args=p)
                name = self.arg('name', str, '"url_button" payload supposed to include "name"', args=p)
                # self.payload.append(dict(type=tp, url=url, name=name))
                self.payload.append(PayloadUrlButton(url, name))
            else:
                raise ValueError(f'Unknown payload type "{tp}"')
        del self.kwargs
